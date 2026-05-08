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
        """Group C minimal version: returns an empty IngestResult.
        Group C.2-C.4 fill in the actual logic."""
        return IngestResult(applied=0, inserted=0, updated=0, skipped=0,
                            epochs_created=0, dry_run=dry_run)
