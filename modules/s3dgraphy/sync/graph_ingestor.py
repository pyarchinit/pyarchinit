"""Bridge from a s3dgraphy Graph back to the PyArchInit SQL tables.

This module hosts the public `GraphIngestor` class (Group C onwards)
and the full exception hierarchy used by both the projector and the
ingestor. All ingestion is atomic (single BEGIN/COMMIT/ROLLBACK).
"""
from __future__ import annotations

from typing import Iterable

# ---------------------------------------------------------------------------
# Mapped columns — the subset of us_table columns the s3dgraphy bridge
# round-trips. Composed of the columns covered by
# pyarchinit_us_mapping.json (5) + the columns added by
# `_enrich_pyarchinit_graph` in graphml_writer.py (7). Anything else
# in us_table (descrizione, foto, profondita, …) is preserved by
# UPDATE selettivo and never overwritten.
# ---------------------------------------------------------------------------
MAPPED_COLUMNS: tuple[str, ...] = (
    # From pyarchinit_us_mapping.json
    "us",
    "d_stratigrafica",
    "d_interpretativa",
    "attivita",
    "struttura",
    # Added by _enrich_pyarchinit_graph
    "sito",
    "area",
    "unita_tipo",
    "periodo_iniziale",
    "fase_iniziale",
    "rapporti",
    "node_uuid",
    # AI04.1: DOC nodes carry a URL/path in s3dgraphy DocumentNode.url
    # → us_table.documentazione (#6 H.4 fix).
    "documentazione",
)


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1)
# ---------------------------------------------------------------------------
class GraphSyncError(Exception):
    """Base class for all GraphProjector / GraphIngestor errors."""


class GraphIngestError(GraphSyncError):
    """Write-side failure. Always means DB rolled back to pre-call state."""


class CycleDetectedError(GraphIngestError):
    """AI07: recursive walker detected a cycle in yEd folder nesting."""


class SchemaMismatchError(GraphIngestError):
    """us_table.node_uuid column missing (Phase 1 migration not applied).

    Hint: run scripts/migrations/2026_05_node_uuid_backfill.py --apply.
    """


class UnknownUnitaTipoError(GraphIngestError):
    """Graph node has unita_tipo not in the vocabulary.

    Hint: run scripts/migrations/2026_05_us_vocabulary_alignment.py --apply.
    """


class SiteMismatchError(GraphIngestError):
    """Graph contains a node whose attributes['sito'] != populate_list(sito=...)."""


class MissingEpochError(GraphIngestError):
    """One or more EpochNodes reference (periodo, fase) not present in
    periodizzazione_table while create_missing_epochs=False.

    The exception carries `missing: list[tuple[int, str]]` so callers
    can show all the missing keys at once instead of one per call.
    """
    def __init__(self, missing: Iterable[tuple]) -> None:
        self.missing = list(missing)
        super().__init__(
            f"Missing periodizzazione_table rows for: {self.missing}. "
            f"Run with create_missing_epochs=True to auto-create."
        )


# ---------------------------------------------------------------------------
# GraphIngestor (Groups C–D)
# ---------------------------------------------------------------------------
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

from sqlalchemy import text

from .conflict_resolver import ConflictResolver
from .ingest_result import (
    ConflictRecord, ConflictResolution, IngestResult)
from .yed_rapporti_policy import FolderEdgePolicy


# ---------------------------------------------------------------------------
# yEd-raw override hook (s3dgraphy #10 decoupling)
#
# The yEd-raw import branch historically opened a Qt dialog to collect
# user overrides + folder-edge policy. To keep this module free of
# `qgis.*` / `PyQt*` / `pyarchinit.*` imports (s3dgraphy policy +
# precondition for moving GraphIngestor into the s3dgraphy package),
# the GUI logic is registered from outside via `register_yed_override_hook`.
#
# When no hook is registered (CLI, tests, headless), populate_list()
# uses yE-D defaults: no overrides, FolderEdgePolicy.SKIP.
# ---------------------------------------------------------------------------
@dataclass
class YedOverrideResult:
    """Outcome of the yEd-raw override prompt.

    cancelled=True signals the caller chose to abort the import; the
    other fields are ignored in that case.
    """
    overrides: Optional[dict[str, Any]] = None
    policy: FolderEdgePolicy = FolderEdgePolicy.SKIP
    cancelled: bool = False


YedOverrideHook = Callable[
    [dict, Path, Any, str],  # drafts, graphml_path, handle, sito
    YedOverrideResult,
]

_yed_override_hook: Optional[YedOverrideHook] = None


def register_yed_override_hook(hook: YedOverrideHook) -> None:
    """Install the yEd-raw override hook. Called by host applications
    (e.g. pyArchInit plugin at initGui) to plug in a GUI prompt.
    """
    global _yed_override_hook
    _yed_override_hook = hook


def clear_yed_override_hook() -> None:
    """Remove any registered yEd-raw override hook. Mostly for tests."""
    global _yed_override_hook
    _yed_override_hook = None


class _DryRunRollback(Exception):
    """Internal sentinel to force rollback at end of dry-run.

    PG-C (5.7.2-alpha): required because SQLAlchemy's engine.begin()
    context manager has no conditional rollback — it commits on clean
    exit and rolls back on any exception. To preserve the original
    dry_run semantic (run the whole block then roll back), we raise
    this sentinel at the very end of a dry-run, and swallow it just
    outside the `with` block.
    """

if TYPE_CHECKING:
    import s3dgraphy

log = logging.getLogger("modules.s3dgraphy.sync.graph_ingestor")


class GraphIngestor:
    """Persist a s3dgraphy Graph back to the PyArchInit SQL tables.

    Single atomic transaction (BEGIN/COMMIT/ROLLBACK). Idempotent on
    re-runs against the same input. AI04 always uses
    ConflictResolution.GRAPH_WINS for value diffs.
    """

    def __init__(self, conflict_resolver: ConflictResolver | None = None) -> None:
        self._resolver = conflict_resolver or ConflictResolver()

    def populate_list(
        self,
        graph: "s3dgraphy.Graph",
        db_path,  # Path | DbHandle | str — resolved via _resolve_db_handle shim
        sito: str,
        *,
        dry_run: bool = False,
        create_missing_epochs: bool = False,
        graphml_path: Path | str | None = None,
        sql_apply_groups: bool = False,
    ) -> IngestResult:
        """See spec §3.2 docstring for full contract.

        When *graphml_path* is provided, AI04's custom data-keys
        (`pyarchinit.us`, `pyarchinit.area`, etc. — see
        graphml_writer._embed_pyarchinit_data_keys) are parsed from
        the file and merged into graph node attributes, so the
        round-trip preserves columns that s3dgraphy's own importer
        would otherwise drop.

        AI06 D.2: when *sql_apply_groups* is True (default False), the
        importer parses group folder nodes (``yfiles.foldertype="group"``
        with ``id="grp_..."``) from the GraphML at *graphml_path* (or
        *graph* if it is itself a path-like) and queues
        ``UPDATE us_table SET <kind>=<group_name>`` for every member
        US whose folder maps to a SQL-derived ``group_kind`` (the
        basic 7: area / struttura / attivita / settore / ambient /
        saggio / quad_par). Ad-hoc groups (group_kind not in this set)
        never touch SQL — they always live in the GroupStore (AC-14).

        Convenience: when *graph* is a Path-like (str or Path) instead
        of a Graph, the importer auto-loads it as a Graph via
        s3dgraphy's GraphMLImporter and uses the same path for
        graphml_path. This lets callers pass just the .graphml file.

        PG-C (5.7.2-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        """
        # yE-A + yE-B + yE-C + yE-D: yEd-raw detection -> dedicated
        # pipeline dispatch. When graphml_path is provided AND it's a
        # yEd-raw file (no pyarchinit.* keys), classify leaves +
        # extract periods + walk folders, then dispatch to
        # `import_yed_raw()` and RETURN its IngestResult — the legacy
        # `_run()` path is NOT executed for yEd-raw graphmls.
        #
        # yE-D (5.8.0-alpha): branch hook is now a dispatcher. The
        # pyarchinit-projected branch (after this block) is UNCHANGED
        # and remains sacred for AC-2 byte-identical contract.
        _yed_parsed_drafts = None  # legacy carry-over; remains None
        if graphml_path is not None:
            try:
                from .yed_detector import detect_flavor
                if detect_flavor(graphml_path) == "yed-raw":
                    from .yed_classifier import classify_leaves
                    from .yed_table_parser import extract_periods
                    from .yed_group_walker import walk_folders
                    from .yed_import_pipeline import import_yed_raw
                    drafts = {
                        "classified": classify_leaves(graphml_path),
                        "periods":    extract_periods(graphml_path),
                        "folders":    walk_folders(graphml_path),
                    }
                    # Resolve handle just-in-time so import_yed_raw
                    # receives a DbHandle regardless of how the caller
                    # passed db_path (Path / str / DbHandle).
                    from ._db_handle import _resolve_db_handle
                    _yed_handle = _resolve_db_handle(db_path)

                    # yE-E (5.8.2-alpha): when a yEd-raw override hook
                    # is registered (interactive QGIS session via
                    # `register_yed_override_hook`), call it to collect
                    # user overrides + policy. CLI / headless callers
                    # (tests, scripts) leave the hook unset and skip
                    # straight to yE-D defaults.
                    _yed_overrides = None
                    _yed_policy = FolderEdgePolicy.SKIP
                    if _yed_override_hook is not None:
                        _res = _yed_override_hook(
                            drafts, graphml_path,
                            _yed_handle, sito,
                        )
                        if _res.cancelled:
                            return IngestResult(
                                applied=0,
                                inserted=0,
                                updated=0,
                                skipped=0,
                                epochs_created=0,
                                errors=("Import cancelled by user",),
                            )
                        _yed_overrides = _res.overrides
                        _yed_policy = _res.policy

                    # yE-D dispatch + return; NO fall-through to legacy.
                    return import_yed_raw(
                        _yed_handle, graphml_path, sito, drafts,
                        policy=_yed_policy,
                        dry_run=dry_run,
                        overrides=_yed_overrides,
                    )
            except Exception as _e:
                # Defensive fallback: if yEd-raw detection / parsing
                # / dispatch throws unexpectedly (e.g. corrupted
                # graphml), fall through to the legacy path so the
                # existing pyarchinit-projected importers keep
                # working. A normal IngestResult-with-errors return
                # value from import_yed_raw is NOT routed here — it
                # propagates out of the `return` above.
                log.warning(
                    "yEd-raw dispatch failed, falling back to legacy: %s",
                    _e,
                )
        # -- existing pyarchinit-projected path UNCHANGED below --
        # AI06: graph may be a Path-like (graphml file). Auto-load.
        from pathlib import Path as _P
        if isinstance(graph, (str, _P)):
            gpath = _P(graph)
            if graphml_path is None:
                graphml_path = gpath
            try:
                from s3dgraphy.importer.import_graphml import (
                    GraphMLImporter)
            except ImportError:
                from s3dgraphy.importer.graphml_importer import (
                    GraphMLImporter)
            graph = GraphMLImporter(filepath=str(gpath)).parse()
        # 1. Sito parameter must be non-empty (cheap check, do first
        # so we fail fast even when db_path is invalid).
        self._verify_sito(graph, sito)
        # PG-C: resolve shim once at entry, propagate handle to _run/_verify_schema
        # Lazy import to avoid circular: _db_handle imports GraphSyncError from us.
        from ._db_handle import _resolve_db_handle
        handle = _resolve_db_handle(db_path)
        if graphml_path is not None:
            try:
                _hydrate_pyarchinit_data_keys(graph, Path(graphml_path))
            except Exception:
                # Defensive: if hydration fails, the graph still has
                # whatever attributes the s3dgraphy importer preserved.
                pass
        # AI07 Stage B: promote legacy 5.5.x ActivityNodeGroup nodes
        # with spatial group_kind to LocationNodeGroup (in-memory only;
        # emits DeprecationWarning if any). Run after the hydrator so
        # `pyarchinit.<dim>` data keys are visible on node attrs for
        # the fallback detection path.
        try:
            _promote_legacy_activitynodegroup(graph)
        except Exception as _e:
            # Defensive: never block ingestion on a promotion failure.
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "_promote_legacy_activitynodegroup failed, continuing: %s",
                _e,
            )
        # 2. Schema check (accepts handle directly — PG-A shim)
        self._verify_schema(handle)
        # 3. Run the actual ingestion
        return self._run(graph, handle, sito,
                         dry_run=dry_run,
                         create_missing_epochs=create_missing_epochs,
                         graphml_path=graphml_path,
                         sql_apply_groups=sql_apply_groups,
                         _yed_parsed_drafts=_yed_parsed_drafts)

    # ------------------------------------------------------------------ helpers
    def _verify_schema(self, handle) -> None:
        # PG-C (5.7.2-alpha): accepts DbHandle directly from populate_list.
        # The file-existence check is gone (PG has no file); we rely on
        # _columns_of returning empty set on connection / missing-table
        # failure to surface as SchemaMismatchError below.
        from ._db_handle import _columns_of
        try:
            cols = _columns_of(handle.engine, "us_table")
        except Exception as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

    def _verify_sito(self, graph, sito: str) -> None:
        """Validate the sito parameter.

        Note: AI04.1 changed semantics — we no longer raise on graph
        nodes carrying a different sito. The user's workflow is "load
        this graph and ingest into MY sito X", so we treat the
        parameter as authoritative. The per-node loop overrides each
        node's sito attribute to *sito* before INSERT/UPDATE.
        """
        if not sito:
            raise SiteMismatchError(
                "sito parameter is mandatory; AI04 only supports "
                "single-site graphs.")

    def _run(self, graph, handle, sito, *, dry_run, create_missing_epochs,
             graphml_path=None, sql_apply_groups=False,
             _yed_parsed_drafts=None):
        inserted = updated = skipped = 0
        epochs_created = 0
        sito_created = False
        applied = 0
        conflicts: list[ConflictRecord] = []
        errors: list[str] = []

        # Pre-compute per-source rapporti from graph edges so the write
        # path can populate us_table.rapporti as JSON-list-of-lists.
        rapporti_by_source = _build_rapporti_from_edges(graph, sito)

        # PG-C (5.7.2-alpha): engine.begin() opens an atomic transaction
        # that commits on clean exit / rolls back on exception. Identical
        # semantics to the old sqlite3 BEGIN/COMMIT/ROLLBACK pattern on
        # both SQLite and PostgreSQL backends. dry_run uses the
        # _DryRunRollback sentinel to force rollback at the end.
        try:
            with handle.engine.begin() as conn:
                # Ensure site_table has a row for `sito` — create if missing.
                count_row = conn.execute(
                    text("SELECT COUNT(*) FROM site_table WHERE sito = :sito"),
                    {"sito": sito},
                ).fetchone()
                if count_row[0] == 0:
                    if not dry_run:
                        conn.execute(
                            text(
                                "INSERT INTO site_table (sito, nazione, regione, "
                                "definizione_sito) VALUES (:sito, '', '', "
                                "'auto-created by AI04 import')"
                            ),
                            {"sito": sito},
                        )
                    sito_created = True
                for node in graph.nodes:
                    # Skip wrapper / metadata node types that have no SQL
                    # counterpart in us_table (PropertyNode etc. land in
                    # paradata.graphml under AI05; GeoPositionNode and
                    # ParadataNodeGroup are layout-only; EpochNode is
                    # handled in its own loop below).
                    type_name = type(node).__name__
                    if type_name in _NON_STRAT_TYPES:
                        continue
                    attrs = dict(getattr(node, "attributes", None) or {})
                    # Look up by node_uuid. Prefer the explicit attribute
                    # (set by GraphProjector._propagate_node_uuid_and_us);
                    # fall back to node_id when the graph was built outside
                    # the projector and node_id IS the DB uuid.
                    node_uuid = attrs.get("node_uuid") or getattr(
                        node, "node_id", None)
                    if not node_uuid:
                        continue
                    # Make sure the node carries a `us` value. Priority:
                    #   1. attrs["us"] (set by GraphProjector)
                    #   2. node.name with prefix stripped (graphml-imported)
                    # Examples of stripping:
                    #   "USM6"   → "6"
                    #   "USV102" → "102"
                    #   "US103a" → "103a"  (us column is TEXT)
                    if "us" not in attrs or attrs["us"] is None:
                        fallback_us = getattr(node, "name", None)
                        if not fallback_us:
                            continue
                        attrs["us"] = _strip_us_prefix(str(fallback_us))
                    # Always force sito to the populate_list parameter so
                    # the user can import a graph (made for ANY sito) into
                    # the chosen target sito (#3 H.4 fix).
                    attrs["sito"] = sito
                    # unita_tipo is best resolved from the s3dgraphy class
                    # name when attrs has lost it via round-trip.
                    if "unita_tipo" not in attrs or attrs["unita_tipo"] is None:
                        resolved_tipo = _resolve_unita_tipo(node, attrs)
                        if resolved_tipo:
                            attrs["unita_tipo"] = resolved_tipo
                    # DocumentNode: stash its `url` field into the
                    # documentazione column (#6 H.4 fix). Path is typically
                    # relative, e.g. "documents/scheda_1.pdf".
                    if (type_name == "DocumentNode"
                            and not attrs.get("documentazione")):
                        doc_url = (getattr(node, "url", None)
                                   or attrs.get("url"))
                        if doc_url:
                            attrs["documentazione"] = str(doc_url)
                    result = conn.execute(
                        text("SELECT * FROM us_table WHERE node_uuid = :uuid"),
                        {"uuid": node_uuid},
                    )
                    row = result.fetchone()
                    if row is None:
                        inserted += 1
                        continue
                    # Build {col: db_val} dict from row + result.keys()
                    col_names = list(result.keys())
                    db_row = dict(zip(col_names, row))
                    row_changed = False
                    for col in MAPPED_COLUMNS:
                        if col not in attrs:
                            continue
                        db_val = db_row.get(col)
                        graph_val = attrs.get(col)
                        if _values_equal(col, db_val, graph_val):
                            continue
                        row_changed = True
                        self._resolver.resolve(
                            db_row=db_row, graph_value=graph_val, field=col)
                        conflicts.append(ConflictRecord(
                            node_uuid=node_uuid, field=col,
                            db_value=db_val, graph_value=graph_val,
                            resolution=ConflictResolution.GRAPH_WINS.value,
                        ))
                    if row_changed:
                        updated += 1
                    else:
                        skipped += 1

                # ---- EpochNode loop ----
                # Read existing (periodo, fase) pairs FOR THIS SITO. The
                # UNIQUE constraint on periodizzazione_table is
                # (sito, periodo, fase) so the same period/phase combo
                # can legitimately exist for a different site.
                existing_epochs = {
                    (r[0], r[1])
                    for r in conn.execute(
                        text(
                            "SELECT CAST(periodo AS TEXT), CAST(fase AS TEXT) "
                            "FROM periodizzazione_table WHERE sito = :sito"
                        ),
                        {"sito": sito},
                    ).fetchall()
                }
                missing_epochs: list[tuple] = []
                for node in graph.nodes:
                    if not _is_epoch_node_local(node):
                        continue
                    attrs = getattr(node, "attributes", None) or {}
                    periodo = attrs.get("periodo")
                    fase = attrs.get("fase")
                    if periodo is None:
                        continue
                    key = (str(periodo), str(fase) if fase is not None else "")
                    if key in existing_epochs:
                        continue
                    if create_missing_epochs:
                        epochs_created += 1
                        # Group D writes the actual INSERT here. For dry-run, just count.
                    else:
                        # Coerce periodo back to int for the error payload
                        try:
                            p_int = int(periodo)
                        except (TypeError, ValueError):
                            p_int = periodo
                        missing_epochs.append((p_int, str(fase)))
                if missing_epochs:
                    # rollback now and let the outer except GraphSyncError
                    # branch re-raise (it also calls rollback, which is a
                    # no-op once the transaction is already rolled back).
                    raise MissingEpochError(missing=missing_epochs)

                # ---- Write block (Group D): INSERT new rows + UPDATE existing ----
                # In dry-run mode, this loop is skipped entirely and the
                # transaction is rolled back below. In write mode, we re-walk
                # graph.nodes to replay the same decisions made in the
                # detection loop above, this time issuing actual SQL writes.
                if not dry_run:
                    for node in graph.nodes:
                        type_name = type(node).__name__
                        if type_name in _NON_STRAT_TYPES:
                            continue
                        attrs = dict(getattr(node, "attributes", None) or {})
                        # Same priority as the detection loop above:
                        # explicit attrs.node_uuid wins (projector-built graphs),
                        # node_id is the fallback (graphs built outside the
                        # projector where node_id IS the DB uuid).
                        node_uuid = attrs.get("node_uuid") or getattr(
                            node, "node_id", None)
                        if not node_uuid:
                            continue
                        if "us" not in attrs or attrs["us"] is None:
                            fallback_us = getattr(node, "name", None)
                            if not fallback_us:
                                continue
                            attrs["us"] = _strip_us_prefix(str(fallback_us))
                        # Force sito to parameter (override anything the
                        # graph carried — the user's choice is authoritative).
                        attrs["sito"] = sito
                        if ("unita_tipo" not in attrs
                                or attrs["unita_tipo"] is None):
                            resolved_tipo = _resolve_unita_tipo(node, attrs)
                            if resolved_tipo:
                                attrs["unita_tipo"] = resolved_tipo
                        if (type_name == "DocumentNode"
                                and not attrs.get("documentazione")):
                            doc_url = (getattr(node, "url", None)
                                       or attrs.get("url"))
                            if doc_url:
                                attrs["documentazione"] = str(doc_url)
                        # area is part of the UNIQUE constraint
                        # (sito, area, us, unita_tipo) — default to "1"
                        # if the graph doesn't carry it.
                        if "area" not in attrs or attrs["area"] is None:
                            attrs["area"] = "1"
                        # rapporti from edges (#4): walk graph edges grouped
                        # by source node_id and serialise as the pyarchinit
                        # list-of-lists format. Edges-derived takes priority
                        # over a graphml-hydrated rapporti string because
                        # the latter may carry the SOURCE sito (e.g.
                        # "TestSite") which we want overridden to the
                        # target sito.
                        if node_uuid in rapporti_by_source:
                            attrs["rapporti"] = str(
                                rapporti_by_source[node_uuid])
                        elif "rapporti" in attrs and attrs["rapporti"]:
                            # Hydrated string — rewrite the sito in each
                            # rapporto to the target sito.
                            attrs["rapporti"] = _rewrite_rapporti_sito(
                                attrs["rapporti"], sito)
                        # periodizzazione from has_first_epoch edges (#5).
                        p_iniz, f_iniz = _find_first_epoch(
                            graph, node_uuid)
                        if p_iniz is not None and (
                                "periodo_iniziale" not in attrs
                                or not attrs["periodo_iniziale"]):
                            attrs["periodo_iniziale"] = str(p_iniz)
                        if f_iniz is not None and (
                                "fase_iniziale" not in attrs
                                or not attrs["fase_iniziale"]):
                            attrs["fase_iniziale"] = str(f_iniz)
                        result = conn.execute(
                            text("SELECT * FROM us_table WHERE node_uuid = :uuid"),
                            {"uuid": node_uuid},
                        )
                        existing = result.fetchone()
                        col_payload = {col: attrs.get(col)
                                       for col in MAPPED_COLUMNS
                                       if col in attrs}
                        col_payload["node_uuid"] = node_uuid
                        col_payload["sito"] = sito
                        if existing is None:
                            # INSERT
                            cols = list(col_payload.keys())
                            placeholders = ",".join(f":{c}" for c in cols)
                            col_list = ",".join(cols)
                            conn.execute(
                                text(
                                    f"INSERT INTO us_table ({col_list}) VALUES "
                                    f"({placeholders})"
                                ),
                                {c: col_payload[c] for c in cols},
                            )
                            applied += 1
                        else:
                            # UPDATE selettivo: only the MAPPED_COLUMNS that
                            # actually differ. Any column not in attrs and
                            # any us_table column not in MAPPED_COLUMNS is
                            # left untouched (preserves descrizione, foto,
                            # etc.).
                            col_names = list(result.keys())
                            db_row = dict(zip(col_names, existing))
                            diff_cols = []
                            diff_vals = []
                            for col in MAPPED_COLUMNS:
                                if col not in attrs:
                                    continue
                                if _values_equal(col, db_row.get(col),
                                                  attrs.get(col)):
                                    continue
                                diff_cols.append(col)
                                diff_vals.append(attrs.get(col))
                            if diff_cols:
                                set_clause = ", ".join(
                                    f"{c} = :{c}" for c in diff_cols)
                                params = {c: v for c, v in zip(diff_cols, diff_vals)}
                                params["__node_uuid"] = node_uuid
                                conn.execute(
                                    text(
                                        f"UPDATE us_table SET {set_clause} "
                                        f"WHERE node_uuid = :__node_uuid"
                                    ),
                                    params,
                                )
                                applied += 1

                    # Epoch INSERT (D5-B path, write mode only).
                    # Populate cron_iniziale/cron_finale and datazione when
                    # the EpochNode carries them. start_time/end_time are
                    # numeric (year), datazione is the human label.
                    if create_missing_epochs:
                        for node in graph.nodes:
                            if not _is_epoch_node_local(node):
                                continue
                            eattrs = getattr(node, "attributes", None) or {}
                            periodo = eattrs.get("periodo")
                            fase = eattrs.get("fase")
                            # Fall back to parsing from node_id when attrs
                            # are stripped by the importer.
                            if periodo is None:
                                tid = getattr(node, "node_id", "") or ""
                                m = _re.match(
                                    r"^epoch_([^_]+)_(.+?)(_synthetic)?$",
                                    str(tid))
                                if m:
                                    periodo, fase = m.group(1), m.group(2)
                            if periodo is None:
                                continue
                            ekey = (str(periodo),
                                    str(fase) if fase is not None else "")
                            if ekey in existing_epochs:
                                continue
                            descrizione = getattr(node, "name", "") or ""
                            cron_ini = getattr(node, "start_time", None)
                            cron_fin = getattr(node, "end_time", None)
                            # cron columns are INTEGER in pyarchinit
                            cron_ini_i = (int(cron_ini)
                                          if cron_ini not in (None, 0, 0.0)
                                          else None)
                            cron_fin_i = (int(cron_fin)
                                          if cron_fin not in (None, 0, 0.0)
                                          else None)
                            # datazione_estesa: free-text human label,
                            # often the epoch name for external graphs.
                            datazione = (eattrs.get("datazione")
                                         or eattrs.get("datazione_estesa")
                                         or descrizione)
                            # The UNIQUE constraint on periodizzazione_table
                            # is (sito, periodo, fase), so populate sito.
                            try:
                                periodo_i = int(periodo)
                            except (TypeError, ValueError):
                                periodo_i = None
                            conn.execute(
                                text(
                                    "INSERT INTO periodizzazione_table "
                                    "(sito, periodo, fase, descrizione, "
                                    " cron_iniziale, cron_finale, "
                                    " datazione_estesa) "
                                    "VALUES (:sito, :periodo, :fase, :descrizione, "
                                    " :cron_ini, :cron_fin, :datazione)"
                                ),
                                {
                                    "sito": sito, "periodo": periodo_i, "fase": fase,
                                    "descrizione": descrizione,
                                    "cron_ini": cron_ini_i, "cron_fin": cron_fin_i,
                                    "datazione": datazione,
                                },
                            )

                # AI06 D.2: optional SQL UPDATE from group folders in the
                # source GraphML. Runs INSIDE the same atomic transaction
                # so a failure here rolls back everything (AI04 contract
                # preserved). Default safe — gated by sql_apply_groups=True.
                if sql_apply_groups and not dry_run and graphml_path:
                    applied += _apply_group_folders_to_sql(
                        conn, Path(graphml_path), sito)

                # PG-C: at the very end of a dry-run, raise the
                # internal sentinel to force engine.begin() to roll
                # back. Clean exit (success path) auto-commits.
                if dry_run:
                    raise _DryRunRollback()
        except _DryRunRollback:
            pass  # dry-run completed; rollback already happened
        except GraphSyncError:
            # engine.begin() already rolled back on the exception path;
            # just re-raise so the caller sees the same error type.
            raise
        except Exception as e:
            raise GraphIngestError(f"Ingest failed: {e}") from e

        return IngestResult(
            applied=applied,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
            parsed_drafts=_yed_parsed_drafts,
        )


# AI06 D.2: SQL columns that map 1:1 to a SQL-derived group_kind.
# Ad-hoc groups (any other kind) NEVER touch SQL — they live in the
# GroupStore graphml file (AC-14).
_GROUP_KIND_TO_COL: frozenset = frozenset({
    "area", "struttura", "attivita", "settore",
    "ambient", "saggio", "quad_par",
})


# AI07: subset of SQL-backed kinds that map to LocationNodeGroup.
# Excludes "attivita" (Q1 — stays as ActivityNodeGroup) and "adhoc"
# (already LocationNodeGroup at projection time).
SQL_BACKED_KINDS_SPATIAL: frozenset = frozenset({
    "area", "struttura", "settore", "ambient", "saggio", "quad_par",
})


# AI07: dimension → s3dgraphy LocationNodeGroup.kind enum value
_DIM_TO_KIND: dict = {
    "area":      "study",
    "settore":   "study",
    "saggio":    "study",
    "quad_par":  "study",
    "struttura": "functional",
    "ambient":   "functional",
}


def _promote_legacy_activitynodegroup(graph) -> int:
    """AI07 Stage B: scan *graph* for ActivityNodeGroup nodes whose
    attributes carry ``group_kind`` ∈ ``SQL_BACKED_KINDS_SPATIAL``, and
    promote them in-memory to ``LocationNodeGroup`` with ``kind`` set
    per :data:`_DIM_TO_KIND`. Also rewires incoming ``is_in_activity``
    edges to ``is_in_location``.

    Detection: looks at ``node.attributes`` for either:

    - direct key ``'group_kind'`` (newer AI07 exports), or
    - any ``'pyarchinit.<dim>'`` key where ``<dim>`` is in
      ``SQL_BACKED_KINDS_SPATIAL`` (legacy 5.5.x exports that retained
      the data attributes through the importer).

    Emits exactly one ``DeprecationWarning`` per call (not per node) if
    any promotion happens. The warning references AI07 / pyarchinit
    5.6.0+ and instructs the user to re-export to migrate the on-disk
    representation.

    Returns: number of nodes promoted.
    """
    import warnings as _warnings
    from s3dgraphy.nodes.group_node import LocationNodeGroup

    promotions: list = []  # list of (old_node, new_node, group_kind)
    for n in list(graph.nodes):
        if type(n).__name__ != "ActivityNodeGroup":
            continue
        attrs = getattr(n, "attributes", None) or {}
        # Try direct group_kind attribute first
        gk = attrs.get("group_kind")
        if not gk:
            # Fallback: find pyarchinit.<dim> key in attributes
            for key in attrs:
                if isinstance(key, str) and key.startswith("pyarchinit."):
                    candidate = key.split(".", 1)[1]
                    if candidate in SQL_BACKED_KINDS_SPATIAL:
                        gk = candidate
                        break
        if gk not in SQL_BACKED_KINDS_SPATIAL:
            continue  # attivita / adhoc / unknown — leave alone
        kind_enum = _DIM_TO_KIND.get(gk, "functional")
        new_node = LocationNodeGroup(
            node_id=n.node_id,
            name=n.name,
            kind=kind_enum,
            description=getattr(n, "description", "") or "",
        )
        new_node.attributes = dict(attrs)
        # Ensure group_kind is also set as a direct attribute
        new_node.attributes["group_kind"] = gk
        # Re-stamp kind/propagation onto attributes (LocationNodeGroup
        # constructor sets these but we just clobbered the dict)
        new_node.attributes["kind"] = kind_enum
        new_node.attributes.setdefault("propagation", "additive")
        promotions.append((n, new_node, gk))

    if not promotions:
        return 0

    # Replace in-place: Graph.nodes is a list — find indices.
    nodes_list = graph.nodes
    for old, new, _gk in promotions:
        try:
            idx = nodes_list.index(old)
            nodes_list[idx] = new
        except ValueError:
            graph.add_node(new)

    # Rewire is_in_activity → is_in_location for promoted targets.
    promoted_ids = {old.node_id for old, _, _ in promotions}
    for e in getattr(graph, "edges", []):
        target = getattr(e, "edge_target", None)
        etype = getattr(e, "edge_type", None)
        if target in promoted_ids and etype == "is_in_activity":
            try:
                e.edge_type = "is_in_location"
            except (AttributeError, TypeError):
                # Edge may freeze edge_type; skip silently.
                pass

    n_count = len(promotions)
    _warnings.warn(
        f"Found {n_count} legacy ActivityNodeGroup nodes with "
        f"group_kind in {{area, struttura, settore, ambient, saggio, "
        f"quad_par}}. Promoting in-memory to LocationNodeGroup + kind. "
        f"Re-export the file via 'Esporta Extended Matrix' to migrate "
        f"the on-disk representation. AI07 / pyarchinit 5.6.0+.",
        DeprecationWarning,
        stacklevel=2,
    )
    return n_count


def _apply_group_folders_to_sql(conn, graphml_path: Path, sito: str) -> int:
    """AI07: recursive walker — descend yEd folder-in-folder structures
    and apply ``UPDATE us_table SET <kind>=<group_name>`` per
    SQL-backed folder.

    Toponym / unknown / ad-hoc kinds are skipped (AC-14 unchanged).

    Cycle detection: a `visited` set guards against malformed GraphML
    where folder A contains folder B contains folder A.

    Member US identification: prefer ``pyarchinit.node_uuid`` (when
    available, byte-identical match to the DB row); fall back to
    ``(pyarchinit.us, pyarchinit.area, sito)`` (always available
    because the AI03 enrichment writes those onto every strat node
    regardless of strict_schema).
    """
    try:
        from lxml import etree as _ET
    except ImportError:
        return 0

    NS_G = "{http://graphml.graphdrawing.org/xmlns}"
    NS_Y = "{http://www.yworks.com/xml/graphml}"
    try:
        _tree = _ET.parse(str(graphml_path))
    except Exception:
        return 0
    root = _tree.getroot()

    # Build d-key id → group_kind map (for the basic 7 kinds).
    kid_to_kind: dict = {}
    # Resolve other key ids we may need to identify members.
    node_uuid_kid = None
    us_kid = None
    area_kid = None
    sito_kid = None
    for k in root.findall(f"{NS_G}key"):
        attr_name = k.get("attr.name") or ""
        if not attr_name.startswith("pyarchinit."):
            continue
        short = attr_name.split(".", 1)[1]
        if short in _GROUP_KIND_TO_COL:
            kid_to_kind[k.get("id")] = short
        if short == "node_uuid":
            node_uuid_kid = k.get("id")
        elif short == "us":
            us_kid = k.get("id")
        elif short == "area":
            area_kid = k.get("id")
        elif short == "sito":
            sito_kid = k.get("id")

    visited: set = set()

    def _visit_folder(folder_elem) -> int:
        fid = folder_elem.get("id") or ""
        if fid and fid in visited:
            raise CycleDetectedError(
                f"Cycle detected: folder {fid!r} visited twice"
            )
        if fid:
            visited.add(fid)

        # Discover this folder's group_kind + group_name from data
        # entries. Prefer the explicit pyarchinit.<kind> data key; fall
        # back to NodeLabel text if data key has no text (preserves
        # backwards-compat with AI06 writer where the label IS the
        # canonical name and data text mirrors it).
        group_kind = None
        group_name = None
        for d in folder_elem.findall(f"{NS_G}data"):
            kind = kid_to_kind.get(d.get("key"))
            if kind:
                group_kind = kind
                group_name = (d.text or "").strip() or None
                break
        if group_name is None and group_kind is not None:
            nl = folder_elem.find(f".//{NS_Y}GroupNode/{NS_Y}NodeLabel")
            if nl is not None and (nl.text or "").strip():
                group_name = nl.text.strip()

        inner = folder_elem.find(f"{NS_G}graph")
        if inner is None:
            return 0

        local_applied = 0
        # Apply SQL UPDATE for direct US members of this folder
        # (only if group_kind is SQL-backed — toponym/adhoc skipped).
        if group_kind in _GROUP_KIND_TO_COL and group_name:
            for member in inner.findall(f"{NS_G}node"):
                # Skip nested folders — they get walked recursively below
                if member.get("yfiles.foldertype") == "group":
                    continue
                # Identify US member (prefer node_uuid, fall back to
                # us+area).
                node_uuid = None
                us_val = None
                area_val = None
                for md in member.findall(f"{NS_G}data"):
                    kid = md.get("key")
                    txt = (md.text or "").strip()
                    if not txt:
                        continue
                    if kid == node_uuid_kid:
                        node_uuid = txt
                    elif kid == us_kid:
                        us_val = txt
                    elif kid == area_kid:
                        area_val = txt
                if node_uuid:
                    upd_result = conn.execute(
                        text(
                            f"UPDATE us_table SET {group_kind}=:group_name "
                            f"WHERE node_uuid=:node_uuid AND sito=:sito"
                        ),
                        {"group_name": group_name, "node_uuid": node_uuid, "sito": sito},
                    )
                    local_applied += (
                        upd_result.rowcount
                        if upd_result.rowcount and upd_result.rowcount > 0
                        else 0)
                elif us_val:
                    # Fall back to (us, area, sito) match.
                    area_val = area_val or "1"
                    upd_result = conn.execute(
                        text(
                            f"UPDATE us_table SET {group_kind}=:group_name "
                            f"WHERE us=:us AND area=:area AND sito=:sito"
                        ),
                        {"group_name": group_name, "us": us_val,
                         "area": area_val, "sito": sito},
                    )
                    local_applied += (
                        upd_result.rowcount
                        if upd_result.rowcount and upd_result.rowcount > 0
                        else 0)

        # Recurse into nested folders
        for child in inner.findall(f"{NS_G}node"):
            if child.get("yfiles.foldertype") == "group":
                local_applied += _visit_folder(child)

        return local_applied

    applied = 0
    # Walk top-level folders only (nested ones are visited via
    # recursion). A folder is "top-level" if its parent <graph>'s
    # parent is NOT a <node> (i.e. it lives directly under the root
    # <graph>, not inside another folder's inner <graph>).
    for folder in root.iter(f"{NS_G}node"):
        if folder.get("yfiles.foldertype") != "group":
            continue
        parent = folder.getparent()
        if parent is not None and parent.tag == f"{NS_G}graph":
            grandparent = parent.getparent()
            if grandparent is not None and grandparent.tag == f"{NS_G}node":
                # this folder is nested — skip; it'll be visited by its
                # parent
                continue
        applied += _visit_folder(folder)

    return applied


def _values_equal(col: str, a, b) -> bool:
    """Loose equality matching the conventions in graphml_writer
    enrichment. JSON-serialised columns (rapporti) get parse-then-compare."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if col == "rapporti":
        try:
            import ast
            return ast.literal_eval(str(a)) == ast.literal_eval(str(b))
        except (ValueError, SyntaxError):
            return str(a) == str(b)
    return str(a) == str(b)


def _is_epoch_node_local(node) -> bool:
    return type(node).__name__ == "EpochNode"


# The Italian-rapporti / unit-type / direction tables previously
# defined inline here moved to `s3dgraphy.sync.rapporti` in v1.6
# (single home for the pyArchInit ↔ canonical-edge translation,
# consumed by graph_ingestor, graphml_writer, graph_projector and
# the yEd-import pipeline alike). The names below are kept as
# private re-export aliases so call sites in this file and in
# `yed_import_pipeline.py` (which already imports
# `_select_rapporti_label` from here) keep working unchanged.
#
# AI07/H.5 follow-up: the verbose-Italian / single-arrow /
# double-arrow dispatch is implemented by `_select_rapporti_label`
# (still defined later in this module — that function moves to
# `s3dgraphy.sync.rapporti` in a follow-up commit). It looks at the
# unita_tipo of BOTH source and target nodes:
#   - both ∈ _CANONICAL_UNIT_TYPES → verbose Italian
#   - either ∈ _CONTINUITY_UNIT_TYPES → single arrow `>` / `<`
#   - otherwise (any other non-canonical) → double arrow `>>` / `<<`
from .rapporti import (
    EDGE_TYPE_TO_RAPPORTI_IT as _EDGE_TYPE_TO_RAPPORTI_IT,
    CANONICAL_UNIT_TYPES as _CANONICAL_UNIT_TYPES,
    CONTINUITY_UNIT_TYPES as _CONTINUITY_UNIT_TYPES,
    EDGE_TYPE_DIRECTION_FORWARD as _EDGE_TYPE_DIRECTION_FORWARD,
)


def _hydrate_pyarchinit_data_keys(graph, graphml_path: Path) -> None:
    """Re-parse the GraphML at *graphml_path* via lxml and merge the
    pyarchinit-specific data keys (`pyarchinit.us`, `pyarchinit.area`,
    `pyarchinit.unita_tipo`, etc.) into graph node attributes.

    This is the IMPORT-side counterpart of
    graphml_writer._embed_pyarchinit_data_keys. s3dgraphy's
    GraphMLImporter strips unknown attributes; we recover the
    pyarchinit-specific ones by reading the same XML directly.

    No-op if the GraphML doesn't contain our custom data keys (older
    files / files from non-pyarchinit producers).
    """
    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    parser = etree.XMLParser(remove_blank_text=False)
    try:
        tree = etree.parse(str(graphml_path), parser)
    except Exception:
        return
    root = tree.getroot()

    # Build keyid → attr_name index for any key whose attr.name
    # starts with 'pyarchinit.'.
    key_id_to_attr: dict[str, str] = {}
    epochs_meta_kid = None
    for k in root.findall(f"{{{NS_GRAPHML}}}key"):
        attr_named = k.get("attr.name") or ""
        if not attr_named.startswith("pyarchinit."):
            continue
        kid = k.get("id")
        if not kid:
            continue
        if attr_named == "pyarchinit.epochs_meta":
            epochs_meta_kid = kid
            continue
        key_id_to_attr[kid] = attr_named[len("pyarchinit."):]

    # Hydrate EpochNodes from the graph-level JSON blob (#5 H.4 fix).
    if epochs_meta_kid:
        graph_el = root.find(f"{{{NS_GRAPHML}}}graph")
        if graph_el is not None:
            for d_el in graph_el.findall(f"{{{NS_GRAPHML}}}data"):
                if d_el.get("key") != epochs_meta_kid:
                    continue
                try:
                    import json as _json
                    epoch_meta_list = _json.loads(d_el.text or "[]")
                except (ValueError, TypeError):
                    epoch_meta_list = []
                for meta in epoch_meta_list:
                    name = meta.get("name", "")
                    if not name:
                        continue
                    # Find the EpochNode in graph.nodes with same name
                    for n in graph.nodes:
                        if (type(n).__name__ == "EpochNode"
                                and getattr(n, "name", "") == name):
                            attrs = getattr(n, "attributes", None)
                            if attrs is None:
                                try:
                                    n.attributes = {}
                                    attrs = n.attributes
                                except Exception:
                                    continue
                            for key in ("periodo", "fase", "cron_iniziale",
                                        "cron_finale", "datazione_estesa"):
                                if (key in meta
                                        and not attrs.get(key)):
                                    attrs[key] = meta[key]
                            break
                break

    if not key_id_to_attr:
        return

    # Build EMID → graph node lookup
    emid_to_node = {}
    for n in graph.nodes:
        emid = getattr(n, "node_id", None)
        if emid:
            emid_to_node[emid] = n
    known_emids = set(emid_to_node.keys())

    for node_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        emid = None
        for d_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            txt = (d_el.text or "").strip()
            if txt and txt in known_emids:
                emid = txt
                break
        if emid is None:
            continue
        n = emid_to_node[emid]
        attrs = getattr(n, "attributes", None)
        if attrs is None:
            try:
                n.attributes = {}
                attrs = n.attributes
            except Exception:
                continue
        for d_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            kid = d_el.get("key")
            if kid not in key_id_to_attr:
                continue
            val = (d_el.text or "").strip()
            if val == "":
                continue
            attr_name = key_id_to_attr[kid]
            # Don't overwrite existing attr unless empty
            if attrs.get(attr_name) in (None, ""):
                attrs[attr_name] = val


def _find_first_epoch(graph, node_uuid: str) -> tuple:
    """Walk has_first_epoch edges from *node_uuid* and return the
    `(periodo, fase)` tuple of the linked EpochNode, or `(None, None)`.

    s3dgraphy's GraphMLImporter strips most attributes but preserves
    edge `edge_type`. The EpochNode keeps `node.name` (e.g. "XV secolo")
    and any `attributes['periodo']` / `attributes['fase']` set by the
    projector. When attrs are stripped, fall back to parsing from
    EpochNode.node_id (which the projector formats as
    `epoch_<periodo>_<fase>`).
    """
    by_id = {}
    for n in graph.nodes:
        nid = getattr(n, "node_id", None)
        if nid:
            by_id[nid] = n
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) != "has_first_epoch":
            continue
        if getattr(e, "edge_source", None) != node_uuid:
            continue
        target = by_id.get(getattr(e, "edge_target", None))
        if target is None or not _is_epoch_node_local(target):
            continue
        attrs = getattr(target, "attributes", None) or {}
        periodo = attrs.get("periodo")
        fase = attrs.get("fase")
        if periodo is None:
            # Fall back to parsing the node_id format
            tid = getattr(target, "node_id", "") or ""
            m = _re.match(r"^epoch_([^_]+)_(.+?)(_synthetic)?$", str(tid))
            if m:
                periodo, fase = m.group(1), m.group(2)
        return periodo, fase
    return None, None


def _rewrite_rapporti_sito(rapporti_str: str, target_sito: str) -> str:
    """Parse a pyarchinit rapporti list-of-lists string and rewrite
    the sito (4th element of each rapporto) to *target_sito*. Returns
    the re-serialised string. Defensive — returns the input unchanged
    if parsing fails."""
    if not rapporti_str:
        return rapporti_str
    try:
        import ast
        data = ast.literal_eval(str(rapporti_str))
    except (ValueError, SyntaxError):
        return rapporti_str
    if not isinstance(data, list):
        return rapporti_str
    out = []
    for item in data:
        if isinstance(item, list) and len(item) >= 4:
            new_item = list(item)
            new_item[3] = target_sito
            out.append(new_item)
        else:
            out.append(item)
    return str(out)


# The verbose-vs-shorthand dispatch function, the multilingual
# prefix-strip helper, the class-name → unita_tipo table, the
# rapporti serialiser — all moved into the canonical home
# `s3dgraphy.sync.rapporti` in v1.6 (commit 2 of the canonical-edges
# refactor). The names below are kept as private re-export aliases so
# call sites that still import them from `graph_ingestor` keep
# working unchanged — notably the in-file users below and the
# `from .graph_ingestor import _select_rapporti_label` line in
# `yed_import_pipeline.py:1073`.
from .rapporti import (
    S3DGRAPHY_TYPE_TO_UNITA_TIPO as _S3DGRAPHY_TYPE_TO_UNITA_TIPO,
    strip_us_prefix as _strip_us_prefix,
    resolve_unita_tipo_for_dispatch as _resolve_unita_tipo_for_dispatch,
    select_rapporti_label as _select_rapporti_label,
    serialize_rapporti_from_edges as _build_rapporti_from_edges,
)

# The `re` module was historically imported here as `_re` (right above
# the now-extracted `_strip_us_prefix` regex). Two unrelated call
# sites in this file (the epoch-id parser at ~line 673 and the
# periodizzazione-row matcher at ~line 1233) still reach for `_re`,
# so we keep the local alias to avoid name-error regressions.
import re as _re


def _resolve_unita_tipo(node, attrs: dict) -> str | None:
    """Return the unita_tipo for *node*, prefering attrs (set by
    GraphProjector) over s3dgraphy class name (when graphml round-trip
    has stripped attrs)."""
    if attrs.get("unita_tipo"):
        return str(attrs["unita_tipo"])
    type_name = type(node).__name__
    return _S3DGRAPHY_TYPE_TO_UNITA_TIPO.get(type_name)


# Node types that have no us_table counterpart and must be skipped by
# the per-node loop. EpochNode is in its own loop and intentionally
# excluded from this set so the EpochNode branch can still see it.
# Note: DocumentNode is INCLUDED in the per-node loop (us_table.unita_tipo
# = 'DOC' is supported) — see #6 H.4 fix. The DocumentNode.url value is
# written to us_table.documentazione during INSERT/UPDATE.
_NON_STRAT_TYPES: frozenset[str] = frozenset({
    "EpochNode",
    "GeoPositionNode",
    "PropertyNode",
    "ParadataNodeGroup",
    "AuthorNode",
    "LicenseNode",
    "EmbargoNode",
    "ExtractorNode",
    "CombinerNode",
    "VirtualSpecialFindUnit",  # paradata-only, AI05 territory
    # AI06: Group folder nodes — never written to us_table.
    "GroupNode",
    "ActivityNodeGroup",
    "LocationNodeGroup",       # AI07: new spatial group node class
    "TimeBranchNodeGroup",
})
