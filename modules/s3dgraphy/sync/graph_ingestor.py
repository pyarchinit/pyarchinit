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
)


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1)
# ---------------------------------------------------------------------------
class GraphSyncError(Exception):
    """Base class for all GraphProjector / GraphIngestor errors."""


class GraphIngestError(GraphSyncError):
    """Write-side failure. Always means DB rolled back to pre-call state."""


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
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from .conflict_resolver import ConflictResolver
from .ingest_result import (
    ConflictRecord, ConflictResolution, IngestResult)

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
        db_path: Path,
        sito: str,
        *,
        dry_run: bool = False,
        create_missing_epochs: bool = False,
    ) -> IngestResult:
        """See spec §3.2 docstring for full contract."""
        db_path = Path(db_path)
        # 1. Schema check
        self._verify_schema(db_path)
        # 2. Site-mismatch check
        self._verify_sito(graph, sito)
        # 3. Run the actual ingestion (Group C: dry-run only)
        return self._run(graph, db_path, sito,
                         dry_run=dry_run,
                         create_missing_epochs=create_missing_epochs)

    # ------------------------------------------------------------------ helpers
    def _verify_schema(self, db_path: Path) -> None:
        if not db_path.exists():
            raise GraphIngestError(f"DB file not found: {db_path}")
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

    def _verify_sito(self, graph, sito: str) -> None:
        if not sito:
            raise SiteMismatchError(
                "sito parameter is mandatory; AI04 only supports single-site graphs.")
        for n in graph.nodes:
            attrs = getattr(n, "attributes", None) or {}
            node_sito = attrs.get("sito")
            if node_sito is not None and node_sito != sito:
                raise SiteMismatchError(
                    f"Graph node {getattr(n, 'node_id', '?')!r} has "
                    f"sito={node_sito!r}, expected {sito!r}")

    def _run(self, graph, db_path, sito, *, dry_run, create_missing_epochs):
        inserted = updated = skipped = 0
        epochs_created = 0
        conflicts: list[ConflictRecord] = []
        errors: list[str] = []

        # Open the transaction (we always use BEGIN even in dry-run so
        # any side effects from other code paths get isolated and
        # ROLLBACK'd).
        conn = sqlite3.connect(str(db_path))
        conn.execute("BEGIN")
        try:
            cur = conn.cursor()
            for node in graph.nodes:
                # Skip non-stratigraphic / non-attribute nodes (e.g. EpochNode).
                attrs = getattr(node, "attributes", None) or {}
                if _is_epoch_node_local(node):
                    continue
                # Look up by node_uuid. Prefer the explicit attribute
                # (set by GraphProjector._propagate_node_uuid_and_us);
                # fall back to node_id when the graph was built outside
                # the projector and node_id IS the DB uuid.
                node_uuid = attrs.get("node_uuid") or getattr(
                    node, "node_id", None)
                if not node_uuid:
                    continue
                # Skip nodes that obviously aren't strat units (no `us`
                # attribute means the importer didn't tie this node to
                # us_table — e.g. PropertyNode, GeoPositionNode).
                if "us" not in attrs:
                    continue
                cur.execute(
                    "SELECT * FROM us_table WHERE node_uuid = ?",
                    (node_uuid,),
                )
                row = cur.fetchone()
                if row is None:
                    inserted += 1
                    continue
                # Build {col: db_val} dict from row + cursor.description
                col_names = [d[0] for d in cur.description]
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
            # Read all (periodo, fase) pairs already in periodizzazione_table.
            cur.execute(
                "SELECT CAST(periodo AS TEXT), CAST(fase AS TEXT) "
                "FROM periodizzazione_table")
            existing_epochs = {(r[0], r[1]) for r in cur.fetchall()}
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
            applied = 0
            if not dry_run:
                for node in graph.nodes:
                    if _is_epoch_node_local(node):
                        continue
                    attrs = getattr(node, "attributes", None) or {}
                    # Same priority as the detection loop above:
                    # explicit attrs.node_uuid wins (projector-built graphs),
                    # node_id is the fallback (graphs built outside the
                    # projector where node_id IS the DB uuid).
                    node_uuid = attrs.get("node_uuid") or getattr(
                        node, "node_id", None)
                    if not node_uuid:
                        continue
                    if "us" not in attrs:
                        continue
                    cur.execute(
                        "SELECT * FROM us_table WHERE node_uuid = ?",
                        (node_uuid,),
                    )
                    existing = cur.fetchone()
                    col_payload = {col: attrs.get(col)
                                   for col in MAPPED_COLUMNS
                                   if col in attrs}
                    col_payload["node_uuid"] = node_uuid
                    col_payload["sito"] = sito
                    if existing is None:
                        # INSERT
                        cols = list(col_payload.keys())
                        placeholders = ",".join("?" for _ in cols)
                        col_list = ",".join(cols)
                        cur.execute(
                            f"INSERT INTO us_table ({col_list}) VALUES "
                            f"({placeholders})",
                            [col_payload[c] for c in cols],
                        )
                        applied += 1
                    else:
                        # UPDATE selettivo: only the MAPPED_COLUMNS that
                        # actually differ. Any column not in attrs and
                        # any us_table column not in MAPPED_COLUMNS is
                        # left untouched (preserves descrizione, foto,
                        # etc.).
                        col_names = [d[0] for d in cur.description]
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
                                f"{c} = ?" for c in diff_cols)
                            cur.execute(
                                f"UPDATE us_table SET {set_clause} "
                                f"WHERE node_uuid = ?",
                                [*diff_vals, node_uuid],
                            )
                            applied += 1

                # Epoch INSERT (D5-B path, write mode only)
                if create_missing_epochs:
                    for node in graph.nodes:
                        if not _is_epoch_node_local(node):
                            continue
                        eattrs = getattr(node, "attributes", None) or {}
                        periodo = eattrs.get("periodo")
                        fase = eattrs.get("fase")
                        if periodo is None:
                            continue
                        ekey = (str(periodo),
                                str(fase) if fase is not None else "")
                        if ekey in existing_epochs:
                            continue
                        cur.execute(
                            "INSERT INTO periodizzazione_table "
                            "(periodo, fase, descrizione) VALUES (?, ?, ?)",
                            (periodo, fase,
                             getattr(node, "name", "") or ""),
                        )

            # Commit or rollback
            if dry_run:
                conn.rollback()
            else:
                conn.commit()
        except GraphSyncError:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise GraphIngestError(f"Ingest failed: {e}") from e
        finally:
            conn.close()

        return IngestResult(
            applied=applied,
            inserted=inserted, updated=updated, skipped=skipped,
            epochs_created=epochs_created,
            conflicts=tuple(conflicts), errors=tuple(errors),
            dry_run=dry_run,
        )


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
