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
    # User-feedback 2026-05-15 (yed-fastfix): SF and VSF are PRIMARILY
    # us_table records (with unita_tipo='SF'/'VSF'). They can ALSO
    # populate inventario_materiali (see _DUAL_WRITE_INV_KINDS below),
    # but the us_table row is the canonical entry — the inventario row
    # joins back to it on (sito, us).
    ClassificationKind.SPECIAL_FIND,
    ClassificationKind.VIRTUAL_FIND,
    # User-feedback 2026-05-15 (yed-fastfix v2): paradata-family leaves
    # (DOCUMENT / COMBINER / EXTRACTOR / PROPERTY) are us_table records
    # too — the existing pyarchinit convention (verified against
    # production DB ``pyarchinit_db.sqlite``) stores them with
    # ``unita_tipo='DOC'`` / ``'Combinar'`` (sic — historical typo
    # preserved upstream) / ``'Extractor'`` / ``'property'``. They are
    # NOT written to a separate paradata.graphml file — the graphml
    # exporter picks them up from us_table along with the canonical
    # stratigraphic family.
    ClassificationKind.DOCUMENT,
    ClassificationKind.COMBINER,
    ClassificationKind.EXTRACTOR,
    ClassificationKind.PROPERTY,
})
# Kinds that are dual-written: primary insert into us_table, additional
# insert into inventario_materiali_table. SF / VSF / RSF per user
# feedback 2026-05-15. The us_table row is created first so its
# (sito, us) tuple is available for the inventario INSERT.
_DUAL_WRITE_INV_KINDS: frozenset = frozenset({
    ClassificationKind.SPECIAL_FIND,
    ClassificationKind.VIRTUAL_FIND,
    ClassificationKind.REUSED_SPECIAL_FIND,
})
# Empty after 2026-05-15 user feedback: AuthorNode / LicenseNode /
# EmbargoNode aren't classified by the yEd label-prefix classifier yet,
# so nothing reaches the paradata.graphml dispatch through this path.
# The ParadataStore add_document / add_combiner / add_extractor /
# add_property methods are kept as defensive code-paths for callers
# that override a leaf to paradata via the yE-E dialog.
_PARADATA_KINDS: frozenset = frozenset()

# Static map ClassifiedKind -> us_table.unita_tipo. USV_FORMAL is
# resolved label-by-label via ``_resolve_unita_tipo`` since the prefix
# (USVs / USVn / USVc) determines the value. Paradata values match
# the existing pyarchinit convention verified against
# ``pyarchinit_db.sqlite`` (DOC, Combinar, Extractor, property).
_CLASSIFIED_KIND_TO_UNITA_TIPO: dict = {
    ClassificationKind.US_REAL: "US",
    ClassificationKind.US_MASONRY: "USM",
    ClassificationKind.US_DOCUMENTARY: "USD",
    ClassificationKind.USV_VIRTUAL: "USV",
    ClassificationKind.REUSED_SPECIAL_FIND: "RSF",
    ClassificationKind.SPECIAL_FIND: "SF",
    ClassificationKind.VIRTUAL_FIND: "VSF",
    ClassificationKind.DOCUMENT: "DOC",
    ClassificationKind.COMBINER: "Combinar",
    ClassificationKind.EXTRACTOR: "Extractor",
    ClassificationKind.PROPERTY: "property",
}


def _strip_unita_tipo_prefix(label: str, unita_tipo: str | None) -> str:
    """Strip the unita_tipo prefix from a yEd label for us_table.us.

    pyArchInit's us_table.us stores the numeric portion only; the
    prefix is carried separately in us_table.unita_tipo. Examples:

      ('US100', 'US')     → '100'
      ('USV200', 'USV')   → '200'
      ('USVs5', 'USVs')   → '5'
      ('SF01', 'SF')      → '01'
      ('USM-15', 'USM')   → '15'  (separator dash trimmed)
      ('US', 'US')        → 'US'  (empty stripped → defensive fallback)

    Paradata-family labels carry an alphabetic-prefix-and-dot that
    doesn't match the unita_tipo string (DOC / Combinar / Extractor /
    property). Two sub-behaviors here:

    - **DocumentNode** (unita_tipo='DOC') reduces to the FIRST numeric
      run, which collapses identity variants (D.001, D.001-2,
      D.001bis all → '001') — the user-confirmed dedup behaviour.
    - **ExtractorNode** / CombinerNode / others preserve the FULL
      path after the alphabetic prefix so hierarchical labels
      (D.NN.MM identifies extractor MM of document NN) stay distinct:

      ('D.001', 'DOC')         → '001'
      ('D.001-2', 'DOC')       → '001'   (variant → DOC dedup)
      ('D.001bis', 'DOC')      → '001'   (variant → DOC dedup)
      ('D.01.03', 'Extractor') → '01.03' (hierarchy preserved)
      ('D.01.04', 'Extractor') → '01.04' (different extractor)
      ('C.42', 'Combinar')     → '42'
      ('E.005', 'Extractor')   → '005'
      ('material', 'property') → 'material'

    Case-insensitive prefix match. If neither path applies, returns
    the label unchanged.
    """
    import re as _re
    if not unita_tipo or not label:
        return label
    # Path 1: prefix matches the unita_tipo string verbatim (US/USM/USV/...).
    if label.upper().startswith(unita_tipo.upper()):
        stripped = label[len(unita_tipo):].lstrip(" -.").strip()
        return stripped or label
    # Path 2: paradata-family (alphabetic prefix + dot).
    m = _re.match(r"^[A-Za-z]+\.(.+)$", label)
    if m:
        body = m.group(1)
        # DocumentNode-only: reduce to first decimal run so identity
        # variants (D.001 / D.001-2 / D.001bis) collapse to '001'.
        # All other paradata types preserve the body verbatim so
        # multi-level hierarchies (D.NN.MM = extractor MM of doc NN)
        # remain distinct rows in us_table.
        if unita_tipo == "DOC":
            num = _re.match(r"^(\d+)", body)
            if num:
                return num.group(1)
        return body
    return label


def _build_member_to_period(periods: list) -> dict[str, tuple[str, str]]:
    """Build ``{yed_id → (periodo_str, fase_str)}`` from PeriodCandidates.

    Each PeriodCandidate has ``member_yed_ids`` (leaves whose Y-range
    falls inside the row) populated by ``yed_table_parser``. This
    inverts that into a per-leaf lookup so ``_write_us_rows`` can set
    ``periodo_iniziale`` / ``fase_iniziale`` on every member.
    """
    member_to_period: dict[str, tuple[str, str]] = {}
    for p in periods or []:
        periodo_val = (
            getattr(p, "user_periodo", None)
            or getattr(p, "auto_periodo", None)
        )
        fase_val = (
            getattr(p, "user_fase", None)
            or getattr(p, "auto_fase", None)
        )
        if periodo_val is None:
            continue
        periodo_str = str(periodo_val)
        fase_str = str(fase_val) if fase_val is not None else "1"
        for mid in getattr(p, "member_yed_ids", []) or []:
            if mid:
                member_to_period[mid] = (periodo_str, fase_str)
    return member_to_period


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


_PARADATA_NODEDUP_UTS: frozenset[str] = frozenset({
    "DOC", "Combinar", "Extractor", "property",
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
                  (SF / VSF / RSF, dual-written — same leaf also lives
                  in sql_us)
      - paradata: classified leaves that go into paradata.graphml
      - skipped:  anything outside the 3 buckets (UNKNOWN, SKIP, ...)

    User-feedback 2026-05-15: SF / VSF / RSF are dual-write — they are
    PRIMARILY us_table records (with unita_tipo='SF'/'VSF'/'RSF') and
    additionally populate inventario_materiali. So they appear in BOTH
    sql_us and sql_inv buckets; ``import_yed_raw`` writes us_table
    first (so node_uuid is assigned), then inventario reads the same
    leaves with the stripped numeric us value.
    """
    sql_us: list[ClassifiedNode] = []
    sql_inv: list[ClassifiedNode] = []
    paradata: list[ClassifiedNode] = []
    skipped: list[ClassifiedNode] = []
    for c in classified:
        kind = c.user_kind
        if kind in _SQL_US_KINDS:
            sql_us.append(c)
            if kind in _DUAL_WRITE_INV_KINDS:
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


def _resolve_folder_for_leaf(
    yed_id: str,
    folders: list[FolderCandidate],
) -> str | None:
    """Return the activity code of the folder containing ``yed_id``.

    Iterates ``folders``; the FIRST folder with
    ``auto_dimension == "attivita"`` (or user-overridden) whose
    flattened member set includes ``yed_id`` wins. Nested folders
    are walked recursively via ``_flatten_members``. Returns ``None``
    when the leaf is orphan (no parent folder) or the parent folder
    is of a non-activity dimension.

    Used by the yE-F fold branch in ``_write_us_rows`` to compute the
    primary or secondary activity for a paradata leaf.
    """
    for folder in folders:
        dim = getattr(folder, "user_dimension", None) or folder.auto_dimension
        if dim != "attivita":
            continue
        members = _flatten_members(folder, folders)
        if yed_id in members:
            return getattr(folder, "user_value", None) or folder.auto_value
    return None


# ---------------------------------------------------------------------------
# SQL writers
# ---------------------------------------------------------------------------

def _write_us_rows(
    conn,
    sql_us_classified: list[ClassifiedNode],
    sito: str,
    periods_map: dict | None = None,
    folders_map: dict | None = None,
    member_to_period: dict[str, tuple[str, str]] | None = None,
    us_by_yed_id_out: dict[str, str] | None = None,
) -> tuple[int, dict]:
    """INSERT one row into us_table per US-class leaf.

    Each row gets:
      - node_uuid: fresh uuid7().hex
      - sito:      caller-provided
      - area:      '1' (yE-D MVP default)
      - us:        ClassifiedNode.label stripped of its unita_tipo
                   prefix (e.g. 'US100' → '100', 'USV200' → '200',
                   'USVs5' → '5', 'SF01' → '01').
      - unita_tipo: US / USM / USD / USV / USVs / USVn / USVc / SF /
                   VSF / RSF per the kind / label.
      - periodo_iniziale / fase_iniziale / periodo_finale /
                   fase_finale: derived from member_to_period when
                   the leaf was found in a PeriodCandidate's Y-range
                   (yed_table_parser populates that). MVP: both
                   inizio/fine set to the same period (user can edit
                   in the Periodizzazione tab later).

    Returns ``(count, uuid_map)`` where ``uuid_map`` is a dict
    mapping ``yed_id -> node_uuid`` so downstream UPDATEs can target
    the row by uuid.

    ``periods_map`` and ``folders_map`` are reserved for future use
    (e.g., richer FK assignment to periodizzazione_table) — currently
    unused.
    """
    _ = periods_map  # reserved
    _ = folders_map  # reserved
    mtp = member_to_period or {}
    count = 0
    uuid_map: dict[str, str] = {}
    # Dedup index: (us, unita_tipo) tuple → node_uuid. Stratigraphic
    # leaves (US / USM / USV / SF / VSF / RSF / USD) dedup-by-identity
    # so multiple yed_ids referring to the same record collapse.
    #
    # yE-F (2026-05-16 spec §5): paradata kinds (DOC / Combinar /
    # Extractor / property) are FOLDED — N yEd occurrences of a
    # shared paradata label collapse to ONE us_table row whose
    # ``attivita`` carries the first folder in document order and
    # whose ``other_locations`` JSON list carries the secondary
    # folders. All sibling yEd ids share the same node_uuid; export
    # fans the single row back out to N nodes (render-time multi-
    # folder visibility) via _apply_yef_fan_out. This supersedes the
    # short-lived Bug R "no-dedup" branch which wrote one row per
    # occurrence with suffix-disambiguated us values.
    key_to_node_uuid: dict[tuple[str, str], str] = {}
    # yE-F fold index: (label, unita_tipo) → (primary_node_uuid,
    # primary_us, secondary_folders_list, primary_folder). First
    # encounter of a shared paradata label registers the primary row;
    # subsequent encounters append to ``secondary_folders_list`` (and
    # UPDATE other_locations on the primary row) when their folder
    # differs from the primary folder.
    paradata_primary_by_label: dict[
        tuple[str, str], tuple[str, str, list[str], str | None]
    ] = {}
    # Bug H (2026-05-15 user feedback): pre-load existing (us, unita_tipo)
    # rows for this sito so re-import is idempotent. New keys still get
    # INSERTed; existing keys are surfaced into uuid_map so rapporti /
    # folder dimensions continue to resolve correctly. Truly-unexpected
    # IntegrityErrors (data corruption, race) still bubble up and the
    # outer transaction rolls back atomically.
    #
    # yE-F idempotency for paradata (Task 6, 2026-05-16): the pre-load
    # also surfaces existing paradata-primary rows (DOC / Combinar /
    # Extractor / property) into ``paradata_primary_by_label`` so a
    # re-import against the same DB reuses the existing node_uuid +
    # appends only newly-seen folders to ``other_locations``. The
    # ``d_stratigrafica`` column carries the original (pre-strip)
    # paradata label and is the join key. ``other_locations`` is a
    # JSON list of secondary activity codes.
    #
    # Two-tier degradation: legacy DBs without the ``other_locations``
    # column fall back to the Task-5 short SELECT (key_to_node_uuid
    # only) so re-import idempotency for stratigraphic rows survives
    # on un-migrated schemas. Truly-broken DBs (no us_table at all)
    # land in the outer except and pre-load is skipped entirely.
    try:
        try:
            cursor = conn.execute(
                text(
                    "SELECT us, unita_tipo, node_uuid, d_stratigrafica, "
                    "attivita, other_locations "
                    "FROM us_table WHERE sito = :sito"
                ),
                {"sito": sito},
            )
            rows = list(cursor)
            yef_columns = True
        except Exception as exc_full:
            log.debug(
                "_write_us_rows: yE-F pre-load full SELECT failed "
                "(%s); falling back to legacy short SELECT", exc_full,
            )
            cursor = conn.execute(
                text(
                    "SELECT us, unita_tipo, node_uuid "
                    "FROM us_table WHERE sito = :sito"
                ),
                {"sito": sito},
            )
            rows = list(cursor)
            yef_columns = False
        for r in rows:
            if yef_columns:
                us_existing, ut_existing, nu_existing, d_existing, \
                    attiv_existing, ol_existing = (
                        r[0], r[1], r[2], r[3], r[4], r[5],
                    )
            else:
                us_existing, ut_existing, nu_existing = r[0], r[1], r[2]
                d_existing = attiv_existing = ol_existing = None
            if us_existing is None or ut_existing is None or nu_existing is None:
                continue
            key_to_node_uuid[(us_existing, ut_existing)] = nu_existing
            if (
                yef_columns
                and ut_existing in _PARADATA_NODEDUP_UTS
                and d_existing
            ):
                import json
                secondary: list[str] = []
                if ol_existing:
                    try:
                        parsed = json.loads(ol_existing)
                        if isinstance(parsed, list):
                            secondary = [str(x) for x in parsed]
                    except (ValueError, TypeError):
                        pass
                paradata_primary_by_label[
                    (str(d_existing), ut_existing)
                ] = (
                    nu_existing, str(us_existing), secondary,
                    attiv_existing,
                )
    except Exception as exc:
        log.debug(
            "_write_us_rows: yE-F pre-load failed (%s); "
            "falling back to insert-only mode", exc,
        )
    for c in sql_us_classified:
        unita_tipo = _resolve_unita_tipo(c)
        if unita_tipo is None:
            log.warning(
                "_write_us_rows: skipping %r (unmapped kind %s)",
                c.yed_id, c.user_kind,
            )
            continue
        us_value = _strip_unita_tipo_prefix(c.label, unita_tipo)
        if unita_tipo in _PARADATA_NODEDUP_UTS:
            # yE-F fold (2026-05-16 spec §5): each yEd occurrence of a
            # paradata label is folded to ONE us_table row + JSON list
            # of secondary activity codes. First-in-document-order
            # becomes primary; subsequent ones append to other_locations.
            label_key = (c.label, unita_tipo)
            current_folder = _resolve_folder_for_leaf(
                c.yed_id, list((folders_map or {}).values()),
            )
            existing = paradata_primary_by_label.get(label_key)
            if existing is None:
                node_uuid = uuid7().hex
                pi, fi = mtp.get(c.yed_id, (None, None))
                conn.execute(
                    text(
                        "INSERT INTO us_table "
                        "(sito, area, us, unita_tipo, node_uuid, "
                        " periodo_iniziale, fase_iniziale, "
                        " periodo_finale, fase_finale, "
                        " d_stratigrafica, attivita, other_locations) "
                        "VALUES (:sito, :area, :us, :unita_tipo, :nu, "
                        "        :pi, :fi, :pf, :ff, :d_strat, "
                        "        :attivita, :ol)"
                    ),
                    {
                        "sito": sito, "area": "1",
                        "us": us_value, "unita_tipo": unita_tipo,
                        "nu": node_uuid,
                        "pi": pi, "fi": fi, "pf": pi, "ff": fi,
                        "d_strat": c.label,
                        "attivita": current_folder,
                        "ol": None,
                    },
                )
                paradata_primary_by_label[label_key] = (
                    node_uuid, us_value, [], current_folder,
                )
                key_to_node_uuid[(us_value, unita_tipo)] = node_uuid
                uuid_map[c.yed_id] = node_uuid
                if us_by_yed_id_out is not None:
                    us_by_yed_id_out[c.yed_id] = us_value
                count += 1
            else:
                primary_uuid, primary_us, secondary, primary_folder = existing
                if (
                    current_folder
                    and current_folder != primary_folder
                    and current_folder not in secondary
                ):
                    secondary.append(current_folder)
                    import json
                    conn.execute(
                        text(
                            "UPDATE us_table SET other_locations = :ol "
                            "WHERE sito = :sito AND node_uuid = :nu"
                        ),
                        {
                            "ol": json.dumps(secondary),
                            "sito": sito, "nu": primary_uuid,
                        },
                    )
                uuid_map[c.yed_id] = primary_uuid
                if us_by_yed_id_out is not None:
                    us_by_yed_id_out[c.yed_id] = primary_us
            continue
        # Stratigraphic (US / USM / USV / SF / VSF / RSF / USD) — keep
        # dedup-by-identity: multiple yed_ids of the same record
        # collapse into one us_table row.
        dedup_key = (us_value, unita_tipo)
        if dedup_key in key_to_node_uuid:
            uuid_map[c.yed_id] = key_to_node_uuid[dedup_key]
            if us_by_yed_id_out is not None:
                us_by_yed_id_out[c.yed_id] = us_value
            continue
        node_uuid = uuid7().hex
        pi, fi = mtp.get(c.yed_id, (None, None))
        conn.execute(
            text(
                "INSERT INTO us_table "
                "(sito, area, us, unita_tipo, node_uuid, "
                " periodo_iniziale, fase_iniziale, "
                " periodo_finale, fase_finale) "
                "VALUES (:sito, :area, :us, :unita_tipo, :node_uuid, "
                "        :pi, :fi, :pf, :ff)"
            ),
            {
                "sito": sito,
                "area": "1",
                "us": us_value,
                "unita_tipo": unita_tipo,
                "node_uuid": node_uuid,
                "pi": pi,
                "fi": fi,
                "pf": pi,
                "ff": fi,
            },
        )
        key_to_node_uuid[dedup_key] = node_uuid
        uuid_map[c.yed_id] = node_uuid
        if us_by_yed_id_out is not None:
            us_by_yed_id_out[c.yed_id] = us_value
        count += 1
    return count, uuid_map


def _write_inventario_rows(
    conn,
    sql_inv_classified: list[ClassifiedNode],
    sito: str,
) -> int:
    """INSERT one row into inventario_materiali_table per SF/VSF/RSF.

    User-feedback 2026-05-15 (yed-fastfix):
    - tipo_reperto carries the resolved unita_tipo (SF / VSF / RSF)
      so downstream filters can distinguish the three families.
    - us is the STRIPPED numeric portion of the label (e.g. 'SF01' →
      '01'); this matches us_table.us so the (sito, us) join works
      for the dual-write linkage.
    - numero_inventario is derived from the same stripped numeric
      value (SF105 → 105) so the inventario row stays semantically
      aligned with the us_table entry and re-imports are idempotent.
      Falls back to `max(existing) + 1` when the label has no numeric
      portion.

    Bug H (2026-05-15 user feedback): pre-load existing
    numero_inventario values for the sito and SKIP collisions silently
    so re-import doesn't break with a UNIQUE violation. Unexpected
    integrity errors still trigger atomic rollback at the outer
    transaction.
    """
    existing_ninv: set[int] = set()
    try:
        for r in conn.execute(
            text(
                "SELECT numero_inventario FROM inventario_materiali_table "
                "WHERE sito = :sito"
            ),
            {"sito": sito},
        ):
            if r[0] is not None:
                try:
                    existing_ninv.add(int(r[0]))
                except (ValueError, TypeError):
                    continue
    except Exception as exc:
        log.debug(
            "_write_inventario_rows: skip-existing pre-load failed "
            "(%s); falling back to insert-only mode", exc,
        )

    def _next_fallback() -> int:
        return (max(existing_ninv) + 1) if existing_ninv else 1

    count = 0
    for c in sql_inv_classified:
        tipo = _resolve_unita_tipo(c) or "SF"
        us_value = _strip_unita_tipo_prefix(c.label, tipo)
        # Prefer the numeric portion of the label as numero_inventario
        # so SF105 → 105, VSF107 → 107. Non-numeric us values (e.g.
        # PROPERTY 'material', but those don't reach this function)
        # fall back to max+1.
        try:
            ninv = int(us_value)
        except (ValueError, TypeError):
            ninv = _next_fallback()
        if ninv in existing_ninv:
            log.info(
                "_write_inventario_rows: (%s, %s) already present — "
                "skipping (re-import idempotency)",
                sito, ninv,
            )
            continue
        conn.execute(
            text(
                "INSERT INTO inventario_materiali_table "
                "(sito, numero_inventario, tipo_reperto, definizione, "
                " area, us) "
                "VALUES (:sito, :ninv, :tipo, :defn, :area, :us)"
            ),
            {
                "sito": sito,
                "ninv": ninv,
                "tipo": tipo,
                "defn": c.label,
                "area": "1",
                "us": us_value,
            },
        )
        existing_ninv.add(ninv)
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

    User-feedback 2026-05-15 (yed-fastfix): the UI's "Codice periodo"
    is column ``cont_per`` (Integer). Populated with the same
    sequential integer as ``periodo`` so the form's read path resolves
    cleanly.

    Bug H (2026-05-15 user feedback): pre-load existing (periodo, fase)
    keys for this sito and SKIP collisions silently so re-import is
    idempotent.
    """
    existing_keys: set[tuple] = set()
    try:
        for r in conn.execute(
            text(
                "SELECT periodo, fase FROM periodizzazione_table "
                "WHERE sito = :sito"
            ),
            {"sito": sito},
        ):
            existing_keys.add((r[0], r[1]))
    except Exception as exc:
        log.debug(
            "_write_periodizzazione_rows: skip-existing pre-load failed "
            "(%s); falling back to insert-only mode", exc,
        )
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
        if (periodo_i, fase_str) in existing_keys:
            log.info(
                "_write_periodizzazione_rows: (%s, %s, %s) already "
                "present — skipping (re-import idempotency)",
                sito, periodo_i, fase_str,
            )
            continue
        conn.execute(
            text(
                "INSERT INTO periodizzazione_table "
                "(sito, periodo, fase, descrizione, datazione_estesa, "
                " cont_per) "
                "VALUES (:sito, :periodo, :fase, :descr, :datazione, "
                "        :cont_per)"
            ),
            {
                "sito": sito,
                "periodo": periodo_i,
                "fase": fase_str,
                "descr": label,
                "datazione": label,
                "cont_per": periodo_i,
            },
        )
        existing_keys.add((periodo_i, fase_str))
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
        # yE-F duplicate-primary fix (2026-05-16): for dim=='attivita',
        # exclude paradata fold rows. _write_us_rows has already set
        # attivita = first-folder-in-document-order; letting this UPDATE
        # run would overwrite it with the LAST iterated folder and also
        # duplicate the primary in other_locations on subsequent passes.
        if dim == "attivita" and node_uuids:
            check_placeholders: list[str] = []
            check_params: dict[str, Any] = {}
            for i, nu in enumerate(node_uuids):
                k = f"pu{i}"
                check_placeholders.append(f":{k}")
                check_params[k] = nu
            check_in = ", ".join(check_placeholders)
            paradata_uuids = {
                r[0] for r in conn.execute(
                    text(
                        f"SELECT node_uuid FROM us_table "
                        f"WHERE unita_tipo IN "
                        f"('DOC','Combinar','Extractor','property') "
                        f"AND node_uuid IN ({check_in})"
                    ),
                    check_params,
                )
            }
            node_uuids = [nu for nu in node_uuids if nu not in paradata_uuids]
            if not node_uuids:
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
    unita_tipo_by_yed_id: dict[str, str] | None = None,
) -> int:
    """Write us_table.rapporti for each leaf-to-leaf pair.

    SYNTHETIC pre-step: when ``expanded.synthetic_us_rows`` is
    non-empty, INSERT one us_table row per synthetic dict first;
    each carries ``node_uuid``, ``unita_tipo='VA'``, ``us=<label>``.
    The synthetic node_uuids are also folded into ``uuid_map`` so
    subsequent rapporti UPDATEs can target them; the synthetic
    label is folded into ``id_to_label`` so target resolution works.

    The pyarchinit ``rapporti`` column is a JSON list of
    ``[type, us_target, area, sito]`` tuples (one per outbound edge).
    Pos 1 is the target us value, pos 3 is sito — order verified
    against the canonical reader contract (graph_projector.py:721
    reads ``rapporto[1]`` as the target us; graph_ingestor's
    ``_rewrite_rapporti_sito`` updates ``item[3]`` as sito).
    yE-D MVP: ``type='covers'`` when ``edge_type`` is None,
    ``area='1'`` (matches the yE-D default in ``_write_us_rows``),
    ``us_target`` = the target's us value (already stripped of its
    unita_tipo prefix by the caller — ``id_to_label`` is built with
    ``_strip_unita_tipo_prefix``). When a rapporto target is NOT
    present in ``id_to_label`` (e.g. the target leaf was classified
    as paradata / inventario, not as a us_table row), the rapporto is
    SKIPPED with a debug log — pyarchinit's rapporti join requires
    the target to exist in us_table.

    Returns total count of UPDATE statements run (one per source
    that has at least one resolvable rapporto).
    """
    id_to_label = dict(id_to_label or {})  # local mutable copy
    unita_tipo_by_yed_id = dict(unita_tipo_by_yed_id or {})

    # Per-edge label dispatch (yed-fastfix 2026-05-15 user feedback):
    # US / USM ↔ US / USM             → verbose Italian (``Copre`` etc.)
    # CON (continuity) on either side → single arrow ``>`` / ``<``
    # All other unita_tipo (USV*, SF,
    #   VSF, RSF, USD, VA, …)         → double arrow ``>>`` / ``<<``
    # Default edge_type when yEd doesn't encode one is ``overlies``
    # (stratigraphic precedence default), which _select_rapporti_label
    # maps to ``Copre`` / ``>>`` / ``>`` respectively.
    from .graph_ingestor import _select_rapporti_label

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
        # the id_to_label map (for target resolution). The unita_tipo
        # is 'VA' (Virtual Activity) so the rapporti-token dispatch
        # picks the double-arrow shorthand for any rapporti through
        # synthetic anchors.
        if node_uuid:
            uuid_map[node_uuid] = node_uuid
            if us_label:
                id_to_label[node_uuid] = us_label
            unita_tipo_by_yed_id[node_uuid] = sr.get("unita_tipo", "VA")

    # ── Group rapporti per node (Bug T 2026-05-16 user feedback) ────
    # pyArchInit canonical model: BOTH endpoints of an edge carry the
    # rapporto in their us_table row — A says ``Copre B`` and B says
    # ``Coperto da A``. The graph reader (graph_projector.py:706+)
    # dedups redundant tuples via stable edge-id keyed on
    # (src, dst, edge_type), so writing both sides is safe and
    # restores DOC/Combinar/etc. visibility of inbound edges in the
    # Scheda US form. Inverse token map ensures the second side
    # carries the semantically-inverse token (>>↔<<, Copre↔Coperto
    # da, Taglia↔Tagliato da, etc.).
    _INVERSE_TOKEN: dict[str, str] = {
        ">>": "<<", "<<": ">>",
        ">":  "<",  "<":  ">",
        "Copre":           "Coperto da",
        "Coperto da":      "Copre",
        "Taglia":          "Tagliato da",
        "Tagliato da":     "Taglia",
        "Riempie":         "Riempito da",
        "Riempito da":     "Riempie",
        "Si appoggia a":   "Gli si appoggia",
        "Gli si appoggia": "Si appoggia a",
        # Symmetric tokens — inverse is identity.
        "Connesso a":             "Connesso a",
        "Uguale a":               "Uguale a",
        "Si lega a":              "Si lega a",
    }

    def _inverse_token(tok: str) -> str:
        return _INVERSE_TOKEN.get(tok, tok)

    _PARADATA_UNITA_TIPO: frozenset[str] = frozenset({
        "DOC", "Combinar", "Extractor", "property",
    })

    # Accumulate forward + inverse rapporti per yed_id, then UPDATE
    # each us_table row once. Each rapporto tuple is canonical:
    # ``[rel_type, us_target, area, sito]``.
    rapporti_by_node: dict[str, list[list]] = {}
    for src, tgt, edge_type in expanded.rapporti:
        src_label = id_to_label.get(src)
        tgt_label = id_to_label.get(tgt)
        if tgt_label is None and src_label is None:
            continue
        src_ut = unita_tipo_by_yed_id.get(src, "")
        tgt_ut = unita_tipo_by_yed_id.get(tgt, "")
        crosses_paradata = (
            src_ut in _PARADATA_UNITA_TIPO
            or tgt_ut in _PARADATA_UNITA_TIPO
        )
        effective_edge_type = edge_type or (
            "generic_connection" if crosses_paradata else "overlies"
        )
        fwd_token = _select_rapporti_label(
            effective_edge_type, src_ut, tgt_ut,
        )
        # Forward: on source's row (target_label needed).
        if src in uuid_map and tgt_label is not None:
            rapporti_by_node.setdefault(src, []).append(
                [fwd_token, tgt_label, "1", sito]
            )
        # Inverse: on target's row (src_label needed). Skip when the
        # target isn't us_table (paradata-bucket leftover, inventario,
        # etc.) or when the source isn't us_table.
        if tgt in uuid_map and src_label is not None:
            inv_token = _inverse_token(fwd_token)
            rapporti_by_node.setdefault(tgt, []).append(
                [inv_token, src_label, "1", sito]
            )

    update_count = 0
    for node_yed_id, rapporti_list in rapporti_by_node.items():
        if node_yed_id not in uuid_map:
            log.debug(
                "_write_rapporti: %r not in us_table uuid_map", node_yed_id,
            )
            continue
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
                "nu": uuid_map[node_yed_id],
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
    #
    # USV_VIRTUAL / USV_FORMAL / VIRTUAL_FIND entries are defensive —
    # after the 2026-05-15 fix they go to us_table (sql_us bucket), so
    # they don't normally reach this function. Kept here in case the
    # user overrides a USV/VSF to paradata via the yE-E dialog.
    dispatch: dict[ClassificationKind, tuple[str, str]] = {
        ClassificationKind.USV_VIRTUAL: ("add_virtual_us", "label"),
        ClassificationKind.USV_FORMAL: ("add_virtual_us", "label"),
        ClassificationKind.VIRTUAL_FIND: ("add_virtual_find", "label"),
        ClassificationKind.DOCUMENT: ("add_document", "label"),
        ClassificationKind.COMBINER: ("add_combiner", "label"),
        ClassificationKind.EXTRACTOR: ("add_extractor", "label"),
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

    member_to_period = _build_member_to_period(periods)

    try:
        with handle.engine.begin() as conn:
            # Bug S (2026-05-16 user feedback): collect the
            # per-yed_id us value actually written (e.g. ``material_2``
            # for the second occurrence of ``material``) so rapporti
            # target resolution picks the RIGHT us_table row when
            # multiple paradata rows share a label. Pre-Bug-R, every
            # ``material`` row mapped to us='material' (dedup), so the
            # stripped label was sufficient. After Bug R each occurrence
            # has its own us value and rapporti targets must point to
            # the specific one (the same yEd edge end-point).
            us_by_yed_id: dict[str, str] = {}
            us_count, uuid_map = _write_us_rows(
                conn, sql_us, sito,
                periods_map={p.yed_row_id: p for p in periods
                             if hasattr(p, "yed_row_id")},
                folders_map={f.yed_id: f for f in folders},
                member_to_period=member_to_period,
                us_by_yed_id_out=us_by_yed_id,
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
            # Prefer the actual written us value (from us_by_yed_id) so
            # paradata rapporti point to the SPECIFIC row, not the first
            # row with that label. Fall back to stripped-label for any
            # yed_id that didn't go through _write_us_rows (defensive).
            id_to_label = {
                c.yed_id: us_by_yed_id.get(
                    c.yed_id,
                    _strip_unita_tipo_prefix(
                        c.label, _resolve_unita_tipo(c),
                    ),
                )
                for c in sql_us
            }
            unita_tipo_by_yed_id = {
                c.yed_id: (_resolve_unita_tipo(c) or "")
                for c in sql_us
            }
            counts["rapporti_updated"] = _write_rapporti(
                conn, expanded, sito, uuid_map, id_to_label,
                unita_tipo_by_yed_id=unita_tipo_by_yed_id,
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
