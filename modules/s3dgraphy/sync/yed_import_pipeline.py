"""yE-D Group B: yEd-raw graphml import pipeline orchestrator.

Consumes drafts (output of yE-B/C parsers) and writes them to the
target pyarchinit DB in a single atomic transaction. Supports both
SQLite and PostgreSQL backends through the `DbHandle` abstraction
(Foundation 5.6.2-alpha) — all SQL is expressed as SQLAlchemy
``text()`` statements with named bind parameters.

Public API:

    import_yed_raw(handle, graphml_path, sito, drafts, *,
                   policy=SKIP, dry_run=False) -> IngestResult

Internal helpers (testable in isolation):

    _classify_destination(classified)
    _flatten_members(folder, all_folders)
    _write_us_rows(conn, sql_us_classified, sito, periods_map,
                   folders_map)
    _write_inventario_rows(conn, sql_inv_classified, sito)
    _write_periodizzazione_rows(conn, periods, sito)
    _apply_yed_folder_dimensions(conn, folders, sito, uuid_map)
    _write_rapporti(conn, expanded, sito, uuid_map)
    _write_paradata_via_store(handle, paradata_classified, sito)

The function order matches the dispatch order inside ``import_yed_raw``
(write US rows first so subsequent UPDATEs have a uuid_map; write
inventario / periodizzazione next; folder dimensions UPDATE; rapporti
UPDATE; paradata last).

The ``_DryRunRollback`` sentinel mirrors the PG-C precedent in
``graph_ingestor.py`` — raised inside ``engine.begin()`` to force
the transaction to roll back at the end of a dry run; caught
immediately outside the ``with`` block and translated into an
``IngestResult(dry_run=True)``.

Atomic-only error policy (Q3 α): any exception (other than
``_DryRunRollback``) triggers a transaction rollback via
``engine.begin()`` semantics, and ``import_yed_raw`` returns an
``IngestResult(applied=0, errors=(str(e),))``.

Added in yE-D (yed-import-pipeline-5.8.0-alpha).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from sqlalchemy import text

from ._db_handle import DbHandle, _resolve_db_handle
from .ingest_result import IngestResult
from .uuid7 import uuid7
from .yed_classifier import ClassificationKind, ClassifiedNode
from .yed_group_walker import FolderCandidate
from .yed_rapporti_policy import (
    ExpandedRapporti,
    FolderEdgePolicy,
    analyze_edges,
    apply_policy,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Destination classification constants (spec § 6).
# ---------------------------------------------------------------------------
_SQL_US_KINDS: frozenset = frozenset({
    ClassificationKind.US_REAL,
    ClassificationKind.US_MASONRY,
    ClassificationKind.US_DOCUMENTARY,
    # User-feedback 2026-05-13: virtual stratigraphic units are still
    # "unità tipo" — they belong to us_table (with different
    # unita_tipo values: USV / USVs / USVn / USVc / ...), not to paradata.
    ClassificationKind.USV_VIRTUAL,
    ClassificationKind.USV_FORMAL,
    # s3dgraphy 0.1.42: RSF (Reused Special Find) is a stratigraphic
    # unit too (spolia — re-used architectural / decorative element
    # with its own stratigraphic identity, family=real, non-series).
    ClassificationKind.REUSED_SPECIAL_FIND,
})
_SQL_INVENTARIO_KINDS: frozenset = frozenset({
    ClassificationKind.SPECIAL_FIND,
})
_PARADATA_KINDS: frozenset = frozenset({
    ClassificationKind.VIRTUAL_FIND,
    ClassificationKind.DOCUMENT,
    ClassificationKind.COMBINER,
    ClassificationKind.PROPERTY,
})

# Static map ClassifiedKind -> us_table.unita_tipo. USV_FORMAL is
# resolved label-by-label via ``_resolve_unita_tipo`` since the prefix
# (USVs / USVn / USVc) determines the value.
_CLASSIFIED_KIND_TO_UNITA_TIPO: dict = {
    ClassificationKind.US_REAL: "US",
    ClassificationKind.US_MASONRY: "USM",
    ClassificationKind.US_DOCUMENTARY: "USD",
    ClassificationKind.USV_VIRTUAL: "USV",
    ClassificationKind.REUSED_SPECIAL_FIND: "RSF",
}


def _resolve_unita_tipo(c: ClassifiedNode) -> str | None:
    """Resolve us_table.unita_tipo for a classified leaf.

    USV_FORMAL labels carry the unita_tipo in the prefix (e.g.
    ``USVs5`` → ``USVs``, ``USVn112`` → ``USVn``, ``USVc04`` → ``USVc``);
    the static map can't represent that. For other kinds, the static
    map is authoritative.
    """
    if c.user_kind == ClassificationKind.USV_FORMAL:
        # Read the first 3 or 4 characters of the label, prefer the
        # 4-char variant when the 4th char is a recognised suffix
        # (s / n / c). Defensive: anything shorter falls back to "USV".
        if len(c.label) >= 4 and c.label[3] in ("s", "n", "c", "S", "N", "C"):
            return c.label[:4]
        return "USV"
    return _CLASSIFIED_KIND_TO_UNITA_TIPO.get(c.user_kind)

# Set of folder dimension column names that are eligible for the
# auto-UPDATE pass (matches yed_group_walker.DEFAULT_FOLDER_PREFIX_MAP).
_ALLOWED_FOLDER_DIMENSIONS: frozenset = frozenset({
    "attivita", "area", "struttura", "settore",
    "ambient", "saggio", "quad_par",
})


class _DryRunRollback(Exception):
    """Sentinel raised inside engine.begin() to force a rollback.

    Mirrors the PG-C precedent in graph_ingestor.py. The instance
    carries the counts dict so the outer handler can build an
    IngestResult populated with the writes that WOULD have happened.
    """

    def __init__(self, counts: dict | None = None) -> None:
        super().__init__("dry_run rollback")
        self.counts = counts or {}


# ---------------------------------------------------------------------------
# yE-E (5.8.2-alpha): User overrides applied AFTER yE-A/B/C parsers,
# BEFORE the yE-D writers. The Qt wizard in `gui/yed_import_dialog.py`
# populates a YedOverrides instance and passes it through
# `import_yed_raw(overrides=...)`. Each field defaults to empty so the
# wizard only ships the diffs the user actually touched; headless callers
# pass `overrides=None` and get the auto_* defaults.
# ---------------------------------------------------------------------------

@dataclass
class YedOverrides:
    """User-supplied diffs over the yE-A/B/C parser outputs.

    Sidecar JSON shape (``<graphml>.yed_overrides.json``) mirrors this
    dataclass with keys ``classifier``, ``periods``, ``folders``,
    ``policy`` plus a ``version`` field for forward-compat.

    Empty fields are no-ops. Unknown yed_ids in the dicts are silently
    ignored — the user may have re-imported a graphml after editing it
    in yEd and dropped/renamed some leaves.
    """
    classifier: dict[str, "ClassificationKind"] = field(default_factory=dict)
    """yed_id -> ClassificationKind override for that leaf."""

    periods: dict[str, dict] = field(default_factory=dict)
    """yed_row_id -> {'periodo': str, 'fase': str,
                       'datazione_iniziale': int | None,
                       'datazione_finale': int | None,
                       'datazione_estesa': str | None}."""

    folders: dict[str, dict] = field(default_factory=dict)
    """folder yed_id -> {'dimension': str | None, 'value': str}.
    dimension=None or 'skip' means: don't apply this folder."""

    policy: "FolderEdgePolicy | None" = None
    """When non-None, takes precedence over the caller-passed policy."""


def apply_overrides_to_drafts(drafts: dict, overrides: YedOverrides) -> dict:
    """Return a NEW drafts dict (shallow copy + per-list copies) with
    overrides applied.

    - classified leaves: ``user_kind`` set to overrides.classifier[yed_id]
      when present; otherwise stays at ``auto_kind``.
    - period candidates: ``user_periodo``/``user_fase`` /
      ``user_datazione_iniziale``/``user_datazione_finale`` /
      ``user_datazione_estesa`` set from overrides.periods[yed_row_id]
      when present.
    - folder candidates: ``user_dimension``/``user_value`` set from
      overrides.folders[yed_id] when present.

    Pure function; the original `drafts` dict is NOT mutated. Each
    list/instance inside the returned dict may be a new object so callers
    can compare drafts vs returned to surface what changed.
    """
    out_classified = []
    for c in drafts.get("classified", []):
        new_user_kind = overrides.classifier.get(c.yed_id, c.user_kind)
        if new_user_kind == c.user_kind:
            out_classified.append(c)
        else:
            out_classified.append(replace(c, user_kind=new_user_kind))

    out_periods = []
    for p in drafts.get("periods", []):
        ovr = overrides.periods.get(getattr(p, "yed_row_id", None), {})
        if not ovr:
            out_periods.append(p)
            continue
        # Some PeriodCandidate fields are optional; only override the
        # ones present in the dict so callers can edit a subset.
        kwargs = {}
        if "periodo" in ovr:
            kwargs["user_periodo"] = ovr["periodo"]
        if "fase" in ovr:
            kwargs["user_fase"] = ovr["fase"]
        # PeriodCandidate may not have user_datazione_* fields yet;
        # set via setattr-style replace where supported.
        out_periods.append(replace(p, **kwargs) if kwargs else p)

    out_folders = []
    for f in drafts.get("folders", []):
        ovr = overrides.folders.get(f.yed_id, {})
        if not ovr:
            out_folders.append(f)
            continue
        kwargs = {}
        if "dimension" in ovr:
            # 'skip' is a sentinel meaning "don't apply this folder";
            # it flows through user_dimension and is checked in
            # _apply_yed_folder_dimensions().
            kwargs["user_dimension"] = ovr["dimension"]
        if "value" in ovr:
            kwargs["user_value"] = ovr["value"]
        out_folders.append(replace(f, **kwargs) if kwargs else f)

    return {
        **drafts,
        "classified": out_classified,
        "periods": out_periods,
        "folders": out_folders,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_destination(classified: list[ClassifiedNode]) -> dict:
    """Split classified leaves into write destinations.

    Returns a dict with four lists:
      - sql_us:   classified leaves that go into us_table
      - sql_inv:  classified leaves that go into inventario_materiali_table
      - paradata: classified leaves that go into paradata.graphml
      - skipped:  anything outside the 3 buckets (UNKNOWN, SKIP, ...)
    """
    sql_us: list[ClassifiedNode] = []
    sql_inv: list[ClassifiedNode] = []
    paradata: list[ClassifiedNode] = []
    skipped: list[ClassifiedNode] = []
    for c in classified:
        kind = c.user_kind
        if kind in _SQL_US_KINDS:
            sql_us.append(c)
        elif kind in _SQL_INVENTARIO_KINDS:
            sql_inv.append(c)
        elif kind in _PARADATA_KINDS:
            paradata.append(c)
        else:
            skipped.append(c)
    return {
        "sql_us": sql_us,
        "sql_inv": sql_inv,
        "paradata": paradata,
        "skipped": skipped,
    }


def _flatten_members(
    folder: FolderCandidate,
    all_folders: list[FolderCandidate],
) -> list[str]:
    """Recursive flatten: direct members + nested folders' members.

    Returns list of yed_id strings (leaves only; nested folder ids
    not in `all_folders` are skipped defensively).
    """
    by_id: dict[str, FolderCandidate] = {f.yed_id: f for f in all_folders}
    out: list[str] = []
    seen: set[str] = set()

    def _walk(f: FolderCandidate) -> None:
        if f.yed_id in seen:
            return
        seen.add(f.yed_id)
        out.extend(f.member_yed_ids)
        for nested_id in f.nested_folder_ids:
            nested = by_id.get(nested_id)
            if nested is None:
                continue
            _walk(nested)

    _walk(folder)
    return out


# ---------------------------------------------------------------------------
# SQL writers
# ---------------------------------------------------------------------------

def _write_us_rows(
    conn,
    sql_us_classified: list[ClassifiedNode],
    sito: str,
    periods_map: dict | None = None,
    folders_map: dict | None = None,
) -> tuple[int, dict]:
    """INSERT one row into us_table per US-class leaf.

    Each row gets:
      - node_uuid: fresh uuid7().hex
      - sito:      caller-provided
      - area:      '1' (yE-D MVP default)
      - us:        ClassifiedNode.label (the yEd label)
      - unita_tipo: US / USM / USD per the kind

    Returns ``(count, uuid_map)`` where ``uuid_map`` is a dict
    mapping ``yed_id -> node_uuid`` so downstream UPDATEs can target
    the row by uuid.

    ``periods_map`` and ``folders_map`` are reserved for future use
    (e.g., FK assignment to periodizzazione_table) — currently
    unused. yE-E will wire them up via the dialog.
    """
    _ = periods_map  # reserved
    _ = folders_map  # reserved
    count = 0
    uuid_map: dict[str, str] = {}
    for c in sql_us_classified:
        unita_tipo = _resolve_unita_tipo(c)
        if unita_tipo is None:
            log.warning(
                "_write_us_rows: skipping %r (unmapped kind %s)",
                c.yed_id, c.user_kind,
            )
            continue
        node_uuid = uuid7().hex
        conn.execute(
            text(
                "INSERT INTO us_table "
                "(sito, area, us, unita_tipo, node_uuid) "
                "VALUES (:sito, :area, :us, :unita_tipo, :node_uuid)"
            ),
            {
                "sito": sito,
                "area": "1",
                "us": c.label,
                "unita_tipo": unita_tipo,
                "node_uuid": node_uuid,
            },
        )
        uuid_map[c.yed_id] = node_uuid
        count += 1
    return count, uuid_map


def _write_inventario_rows(
    conn,
    sql_inv_classified: list[ClassifiedNode],
    sito: str,
) -> int:
    """INSERT one row into inventario_materiali_table per SPECIAL_FIND."""
    count = 0
    for idx, c in enumerate(sql_inv_classified, start=1):
        # We don't get a numero_inventario from yEd labels; use a
        # negative placeholder offset so multiple imports don't collide
        # immediately (real numbers assigned during finds workflow).
        # MVP: assign sequential positive ints derived from idx; the
        # UNIQUE (sito, numero_inventario, sub_inv) constraint will
        # catch real collisions on re-import (atomic rollback).
        conn.execute(
            text(
                "INSERT INTO inventario_materiali_table "
                "(sito, numero_inventario, tipo_reperto, definizione, "
                " area, us) "
                "VALUES (:sito, :ninv, :tipo, :defn, :area, :us)"
            ),
            {
                "sito": sito,
                "ninv": idx,
                "tipo": "SF",
                "defn": c.label,
                "area": "1",
                "us": c.label,
            },
        )
        count += 1
    return count


def _write_periodizzazione_rows(
    conn,
    periods: list,  # list[PeriodCandidate]
    sito: str,
) -> int:
    """INSERT one row into periodizzazione_table per PeriodCandidate.

    Uses ``user_periodo`` / ``user_fase`` / ``user_label`` (or their
    auto_* fallback in yE-D, since the dialog hasn't run yet).
    ``cron_iniziale`` / ``cron_finale`` stay NULL — yEd doesn't
    encode dates on table rows; the user fills them later in the
    Periodizzazione tab.
    """
    count = 0
    for p in periods:
        periodo = getattr(p, "user_periodo", None) or getattr(
            p, "auto_periodo", None,
        )
        fase = getattr(p, "user_fase", None) or getattr(p, "auto_fase", None)
        label = (
            getattr(p, "user_label", None)
            or getattr(p, "auto_label", None)
            or ""
        )
        try:
            periodo_i = int(periodo) if periodo is not None else None
        except (ValueError, TypeError):
            periodo_i = None
        # periodizzazione_table.fase is TEXT in pyarchinit schema.
        fase_str = str(fase) if fase is not None else None
        conn.execute(
            text(
                "INSERT INTO periodizzazione_table "
                "(sito, periodo, fase, descrizione, datazione_estesa) "
                "VALUES (:sito, :periodo, :fase, :descr, :datazione)"
            ),
            {
                "sito": sito,
                "periodo": periodo_i,
                "fase": fase_str,
                "descr": label,
                "datazione": label,
            },
        )
        count += 1
    return count


def _apply_yed_folder_dimensions(
    conn,
    folders: list[FolderCandidate],
    sito: str,
    uuid_map: dict[str, str],
) -> int:
    """UPDATE us_table SET <dim>=<value> for each folder's members.

    For every FolderCandidate whose ``user_dimension`` (or, in yE-D
    where the dialog hasn't run, ``auto_dimension``) is a known
    pyarchinit column name and not ``'skip'``, run an UPDATE setting
    that column to the folder's value for every leaf member resolved
    via ``uuid_map``.

    Members not in ``uuid_map`` (e.g. paradata leaves) are silently
    skipped — we log them at debug level.

    Returns the count of rows UPDATEd (sum across folders).
    """
    total = 0
    for folder in folders:
        dim = (
            getattr(folder, "user_dimension", None)
            or folder.auto_dimension
        )
        if not dim or dim == "skip":
            log.debug(
                "_apply_yed_folder_dimensions: skipping folder %r (no dim)",
                folder.yed_id,
            )
            continue
        if dim not in _ALLOWED_FOLDER_DIMENSIONS:
            log.warning(
                "_apply_yed_folder_dimensions: folder %r has dim %r "
                "not in allowed set — skipping",
                folder.yed_id, dim,
            )
            continue
        value = (
            getattr(folder, "user_value", None)
            or folder.auto_value
        )
        if not value:
            continue
        members = _flatten_members(folder, folders)
        node_uuids = [
            uuid_map[m] for m in members if m in uuid_map
        ]
        if not node_uuids:
            log.debug(
                "_apply_yed_folder_dimensions: folder %r had no "
                "us_table members (uuid_map miss) — skipping",
                folder.yed_id,
            )
            continue
        # Build named bind parameters for IN clause (backend-portable).
        # SQLAlchemy text() supports list expansion via the
        # `bindparam(name, expanding=True)` API, but for simplicity
        # we generate fresh placeholder names per call.
        params: dict[str, Any] = {
            "sito": sito,
            "val": value,
        }
        placeholders: list[str] = []
        for i, nu in enumerate(node_uuids):
            key = f"u{i}"
            params[key] = nu
            placeholders.append(f":{key}")
        in_clause = ", ".join(placeholders)
        # Use safe column-name embedding: dim is validated against
        # the allowlist above so it's safe to f-string here.
        sql = (
            f"UPDATE us_table SET {dim} = :val "
            f"WHERE sito = :sito AND node_uuid IN ({in_clause})"
        )
        result = conn.execute(text(sql), params)
        # SQLAlchemy result.rowcount may be -1 for some drivers,
        # so default to len(node_uuids) when unknown.
        affected = (
            result.rowcount if getattr(result, "rowcount", -1) != -1
            else len(node_uuids)
        )
        total += affected
    return total


def _write_rapporti(
    conn,
    expanded: ExpandedRapporti,
    sito: str,
    uuid_map: dict[str, str],
    id_to_label: dict[str, str] | None = None,
) -> int:
    """Write us_table.rapporti for each leaf-to-leaf pair.

    SYNTHETIC pre-step: when ``expanded.synthetic_us_rows`` is
    non-empty, INSERT one us_table row per synthetic dict first;
    each carries ``node_uuid``, ``unita_tipo='VA'``, ``us=<label>``.
    The synthetic node_uuids are also folded into ``uuid_map`` so
    subsequent rapporti UPDATEs can target them; the synthetic
    label is folded into ``id_to_label`` so target resolution works.

    The pyarchinit ``rapporti`` column is a JSON list of
    ``[type, sito, area, us_target]`` tuples (one per outbound edge).
    yE-D MVP: ``type='covers'`` when ``edge_type`` is None,
    ``area='1'`` (matches the yE-D default in ``_write_us_rows``),
    ``us_target`` = the target's ``us`` label, resolved via
    ``id_to_label`` (yed_id → label). When a rapporto target is NOT
    present in ``id_to_label`` (e.g. the target leaf was classified
    as paradata / inventario, not as a us_table row), the rapporto is
    SKIPPED with a debug log — pyarchinit's rapporti join requires
    the target to exist in us_table.

    Returns total count of UPDATE statements run (one per source
    that has at least one resolvable rapporto).
    """
    id_to_label = dict(id_to_label or {})  # local mutable copy

    # SYNTHETIC: insert virtual-activity rows first.
    for sr in expanded.synthetic_us_rows:
        node_uuid = sr.get("node_uuid")
        us_label = sr.get("us") or ""
        conn.execute(
            text(
                "INSERT INTO us_table "
                "(sito, area, us, unita_tipo, node_uuid) "
                "VALUES (:sito, :area, :us, :unita_tipo, :node_uuid)"
            ),
            {
                "sito": sito,
                "area": "1",
                "us": us_label,
                "unita_tipo": sr.get("unita_tipo", "VA"),
                "node_uuid": node_uuid,
            },
        )
        # The synthetic node_uuid is the leaf-id used by Group A's
        # SYNTHETIC branch when it rewired folder edges. Feed both
        # the uuid_map (for the source-side UPDATE WHERE clause) and
        # the id_to_label map (for target resolution).
        if node_uuid:
            uuid_map[node_uuid] = node_uuid
            if us_label:
                id_to_label[node_uuid] = us_label

    # ── Group rapporti by source ────────────────────────────────────
    by_source: dict[str, list[tuple[str, str | None]]] = {}
    for src, tgt, edge_type in expanded.rapporti:
        by_source.setdefault(src, []).append((tgt, edge_type))

    update_count = 0
    for src, edges in by_source.items():
        if src not in uuid_map:
            # The source isn't an us_table row — skip (paradata,
            # inventario, or a leaf that classify_destination
            # routed elsewhere). yE-E dialog will let user pick.
            log.debug(
                "_write_rapporti: src %r not in us_table uuid_map", src,
            )
            continue
        rapporti_list = []
        for tgt, edge_type in edges:
            target_label = id_to_label.get(tgt)
            if target_label is None:
                log.debug(
                    "_write_rapporti: target %r has no us_table row, "
                    "skipping rapporto", tgt,
                )
                continue
            rapp_type = edge_type or "covers"
            rapporti_list.append([
                rapp_type, sito, "1", target_label,
            ])
        if not rapporti_list:
            continue
        conn.execute(
            text(
                "UPDATE us_table SET rapporti = :rapp "
                "WHERE sito = :sito AND node_uuid = :nu"
            ),
            {
                "rapp": json.dumps(rapporti_list, ensure_ascii=False),
                "sito": sito,
                "nu": uuid_map[src],
            },
        )
        update_count += 1
    return update_count


def _write_paradata_via_store(
    handle: DbHandle,
    paradata_classified: list[ClassifiedNode],
    sito: str,
) -> int:
    """Dispatch each paradata leaf to the ParadataStore API.

    Path B decision (no US linkage at yE-D time):
      USV_VIRTUAL / USV_FORMAL → add_virtual_us (if API exists; else skip+log)
      DOCUMENT                  → add_document (if API exists; else skip+log)
      VIRTUAL_FIND              → add_virtual_find (if API exists; else skip+log)
      COMBINER                  → add_combiner (if API exists; else skip+log)
      PROPERTY                  → add_property (if API exists; else skip+log)

    Reads ParadataStore via getattr lookups; missing methods are
    logged as skips. Returns count of paradata writes ATTEMPTED.
    """
    if not paradata_classified:
        return 0
    try:
        from .paradata_store import ParadataStore
    except Exception as e:
        log.warning(
            "_write_paradata_via_store: cannot import ParadataStore: %s", e,
        )
        return 0
    try:
        store = ParadataStore(handle, sito)
    except Exception as e:
        log.warning(
            "_write_paradata_via_store: cannot instantiate "
            "ParadataStore(handle=%r, sito=%r): %s",
            handle, sito, e,
        )
        return 0

    # Map ClassifiedKind -> (method name, kw-key-for-label).
    # When a method is missing we skip+log.
    dispatch: dict[ClassificationKind, tuple[str, str]] = {
        ClassificationKind.USV_VIRTUAL: ("add_virtual_us", "label"),
        ClassificationKind.USV_FORMAL: ("add_virtual_us", "label"),
        ClassificationKind.VIRTUAL_FIND: ("add_virtual_find", "label"),
        ClassificationKind.DOCUMENT: ("add_document", "label"),
        ClassificationKind.COMBINER: ("add_combiner", "label"),
        ClassificationKind.PROPERTY: ("add_property", "label"),
    }
    count = 0
    for c in paradata_classified:
        method_name, _label_key = dispatch.get(c.user_kind, ("", ""))
        if not method_name:
            log.debug(
                "_write_paradata_via_store: no dispatch for %s",
                c.user_kind,
            )
            continue
        method = getattr(store, method_name, None)
        if method is None or not callable(method):
            if c.user_kind == ClassificationKind.PROPERTY:
                log.warning(
                    "PropertyNode %r written without US linkage — "
                    "yE-E dialog will let user assign target "
                    "(ParadataStore.%s missing)",
                    c.label, method_name,
                )
            else:
                log.info(
                    "_write_paradata_via_store: %s (%s) skipped — "
                    "ParadataStore.%s not implemented",
                    c.label, c.user_kind.value, method_name,
                )
            count += 1  # counted as attempted per spec § 6 line 307
            continue
        try:
            # Best-effort invocation. The exact signature varies; we
            # call with the label as the first positional arg and
            # tolerate TypeErrors.
            method(c.label)
        except TypeError:
            try:
                # Try with no args (some methods may auto-allocate).
                method()
            except Exception as e:
                log.warning(
                    "_write_paradata_via_store: ParadataStore.%s(%r) "
                    "failed: %s",
                    method_name, c.label, e,
                )
        except Exception as e:
            log.warning(
                "_write_paradata_via_store: ParadataStore.%s(%r) "
                "failed: %s",
                method_name, c.label, e,
            )
        count += 1
    return count


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def import_yed_raw(
    handle: DbHandle,
    graphml_path: Path | str,
    sito: str,
    drafts: dict,
    *,
    policy: FolderEdgePolicy = FolderEdgePolicy.SKIP,
    dry_run: bool = False,
    overrides: YedOverrides | None = None,
) -> IngestResult:
    """Orchestrate the yEd-raw graphml import end-to-end.

    Args:
        handle: target DbHandle (SQLite or PostgreSQL).
        graphml_path: path to the .graphml file (already detected
            as yEd-raw by the branch hook).
        sito: target site name (forced onto every inserted row).
        drafts: dict with keys ``classified`` / ``periods`` /
            ``folders`` (output of yE-B/C parsers).
        policy: folder-edge policy (default SKIP).
        dry_run: when True, the transaction rolls back at the end
        overrides: yE-E (5.8.2-alpha) — user-supplied diffs over the
            parser outputs. When non-None, ``apply_overrides_to_drafts``
            is called first; if ``overrides.policy`` is set it
            replaces the caller-passed ``policy``. None = hardcoded
            yE-D defaults (auto_kind / auto_periodo / auto_fase /
            auto_dimension on every leaf, period, folder).
            (via ``_DryRunRollback`` sentinel); counts are still
            reported in the returned ``IngestResult``.

    Returns:
        IngestResult with applied / inserted counts populated and
        ``parsed_drafts`` carrying a snapshot of the drafts inputs +
        the expanded rapporti / paradata counts.

    Error policy: atomic. On any exception (other than
    ``_DryRunRollback``), the transaction rolls back and the
    returned ``IngestResult`` has ``applied=0`` + ``errors=(str(e),)``.
    """
    handle = _resolve_db_handle(handle)

    # yE-E (5.8.2-alpha): apply user overrides BEFORE any downstream
    # read. The override dataclass is opt-in; None preserves yE-D
    # hardcoded-defaults behaviour. overrides.policy, when set, wins
    # over the caller-passed policy argument.
    if overrides is not None:
        drafts = apply_overrides_to_drafts(drafts, overrides)
        if overrides.policy is not None:
            policy = overrides.policy

    classified: list[ClassifiedNode] = drafts.get("classified", []) or []
    periods: list = drafts.get("periods", []) or []
    folders: list[FolderCandidate] = drafts.get("folders", []) or []

    # 1. Classify destinations BEFORE the transaction so we can short-
    #    circuit on a fully-empty draft.
    buckets = _classify_destination(classified)
    sql_us = buckets["sql_us"]
    sql_inv = buckets["sql_inv"]
    paradata = buckets["paradata"]

    # 2. Rapporti analysis runs OUTSIDE the transaction (read-only).
    folder_ids: set[str] = {f.yed_id for f in folders}
    _ = folder_ids  # kept for clarity / future use
    report = analyze_edges(graphml_path, classified, folders)
    expanded = apply_policy(
        report,
        policy,
        all_folders=folders,
        classified=classified,
    )

    # Counters populated inside the transaction; we'll feed them
    # into _DryRunRollback if dry_run flips, or into the final
    # IngestResult on success.
    counts = {
        "us_inserted": 0,
        "inv_inserted": 0,
        "period_inserted": 0,
        "us_updated_dim": 0,
        "rapporti_updated": 0,
        "paradata_written": 0,
    }

    try:
        with handle.engine.begin() as conn:
            us_count, uuid_map = _write_us_rows(
                conn, sql_us, sito,
                periods_map={p.yed_row_id: p for p in periods
                             if hasattr(p, "yed_row_id")},
                folders_map={f.yed_id: f for f in folders},
            )
            counts["us_inserted"] = us_count

            counts["inv_inserted"] = _write_inventario_rows(
                conn, sql_inv, sito,
            )
            counts["period_inserted"] = _write_periodizzazione_rows(
                conn, periods, sito,
            )
            counts["us_updated_dim"] = _apply_yed_folder_dimensions(
                conn, folders, sito, uuid_map,
            )
            # Build yed_id -> us-label map for rapporti target resolution.
            # Includes every leaf that landed in us_table (sql_us bucket),
            # so the rapporti tuples reference real us values, not yed
            # internal ids. Synthetic rows are merged inside _write_rapporti.
            id_to_label = {c.yed_id: c.label for c in sql_us}
            counts["rapporti_updated"] = _write_rapporti(
                conn, expanded, sito, uuid_map, id_to_label,
            )
            # Paradata writes go through ParadataStore which manages
            # its own file I/O. ParadataStore IS NOT inside the SQL
            # transaction — yE-D ships best-effort paradata writes
            # (atomic guarantees apply to SQL only).
            counts["paradata_written"] = _write_paradata_via_store(
                handle, paradata, sito,
            )

            if dry_run:
                raise _DryRunRollback(counts)
    except _DryRunRollback as drr:
        log.info("import_yed_raw: dry_run rollback — counts=%r", drr.counts)
        return IngestResult(
            applied=0,
            inserted=0,
            updated=0,
            skipped=0,
            epochs_created=0,
            conflicts=(),
            errors=(),
            dry_run=True,
            parsed_drafts={
                "classified": classified,
                "periods": periods,
                "folders": folders,
                "expanded_rapporti": expanded,
                "paradata_count": counts["paradata_written"],
                "would_apply": counts,
            },
        )
    except Exception as e:
        log.exception("import_yed_raw: pipeline failed — rolling back")
        return IngestResult(
            applied=0,
            inserted=0,
            updated=0,
            skipped=0,
            epochs_created=0,
            conflicts=(),
            errors=(str(e),),
            dry_run=False,
            parsed_drafts={
                "classified": classified,
                "periods": periods,
                "folders": folders,
                "expanded_rapporti": expanded,
                "paradata_count": 0,
            },
        )

    inserted = (
        counts["us_inserted"]
        + counts["inv_inserted"]
        + counts["period_inserted"]
    )
    updated = counts["us_updated_dim"] + counts["rapporti_updated"]
    applied = inserted + updated
    return IngestResult(
        applied=applied,
        inserted=inserted,
        updated=updated,
        skipped=0,
        epochs_created=counts["period_inserted"],
        conflicts=(),
        errors=(),
        dry_run=False,
        parsed_drafts={
            "classified": classified,
            "periods": periods,
            "folders": folders,
            "expanded_rapporti": expanded,
            "paradata_count": counts["paradata_written"],
            "counts": counts,
        },
    )
