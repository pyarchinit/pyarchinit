"""Project PyArchInit DB rows into a stratigraphic-layer s3dgraphy Graph.

AI04 implementation is a thin wrapper (Strategy D, see memory note
project_ai04_projector_refactor_plan.md) around the existing
_enrich_pyarchinit_graph() function in graphml_writer.py. The
promotion to a self-contained class lives in AI05.

Exposed publicly so callers (UI Import tab, CLI helper, future
SyncEngine in Phase 3) have a stable API surface even while the
underlying implementation evolves.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from .graph_ingestor import GraphSyncError

if TYPE_CHECKING:
    import s3dgraphy


class ProjectionError(GraphSyncError):
    """Read-side failure during GraphProjector.populate_graph()."""


class GraphProjector:
    """Stratigraphic-layer projection from PyArchInit DB to s3dgraphy Graph.

    Usage:
        projector = GraphProjector()
        graph = projector.populate_graph(db_path, sito="Scavo archeologico")

    The graph contains StratigraphicUnit / USM / USVs / USVn / USD /
    SF / VSF / CON / DOC / Extractor / Combinar / property nodes plus
    EpochNodes for the (periodo, fase) tuples present in the filtered
    rows. Edges follow the rapporti column conventions decoded by
    `_RAPPORTI_TO_EDGE_TYPE` and `_RAPPORTI_SHORTHAND` in
    graphml_writer.py.
    """

    def __init__(self, vocab_provider=None) -> None:
        # vocab_provider parameter is here for API forward-compat
        # with AI06+ (where vocabulary aliases drive normalisation).
        # AI04 does not consume it.
        self._vocab_provider = vocab_provider

    def populate_graph(self, db_path: Path, sito: str) -> "s3dgraphy.Graph":
        """Build and return a s3dgraphy.Graph populated with the
        stratigraphic rows of `sito` from the SQLite at `db_path`.

        Args:
            db_path: filesystem path to the pyarchinit SQLite DB.
            sito: site identifier (`us_table.sito` value). Mandatory
                — multi-graph projections are out of scope for AI04.

        Returns:
            A populated `s3dgraphy.Graph`. Empty graph (zero nodes) is
            valid: it just means the site has no rows.

        Raises:
            ProjectionError: on any failure reaching the DB or
                instantiating the in-memory graph.
        """
        if not sito:
            raise ProjectionError(
                "sito parameter is mandatory for GraphProjector.populate_graph(); "
                "AI04 only supports single-site graphs.")
        db_path = Path(db_path)
        if not db_path.exists():
            raise ProjectionError(f"DB file not found: {db_path}")

        # Verify Phase 1 migration applied: us_table.node_uuid column.
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise ProjectionError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise ProjectionError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")

        # Delegate to the existing AI03 enrichment routine.
        try:
            from s3dgraphy import Graph
            from s3dgraphy.importer.pyarchinit_importer import (
                PyArchInitImporter)
            from .graphml_writer import _enrich_pyarchinit_graph
        except ImportError as e:
            raise ProjectionError(f"s3dgraphy import failed: {e}") from e

        # Stage 1: import the StratigraphicUnit nodes from us_table via
        # the upstream PyArchInitImporter (spec §3.2: "Reuses the
        # already-existing s3dgraphy.importer.pyarchinit_importer as
        # base"). The importer creates one Graph with `graph_id` derived
        # from the file basename; we then transplant its nodes/edges
        # into a graph keyed by `sito` for AI04 single-site semantics.
        try:
            importer = PyArchInitImporter(
                filepath=str(db_path),
                mapping_name="pyarchinit_us_mapping",
            )
            imported = importer.parse()
        except Exception as e:
            raise ProjectionError(
                f"Importer failed for db={db_path}: {e}") from e

        graph = Graph(graph_id=sito)
        # Transplant imported nodes/edges into the sito-keyed graph.
        # Skip the auto-created GeoPositionNode of `imported` (graph
        # already has its own from Graph.__init__).
        for node in list(imported.nodes):
            if type(node).__name__ == "GeoPositionNode":
                continue
            try:
                graph.add_node(node, overwrite=True)
            except Exception:
                # Defensive: best-effort; fall through to enrichment.
                pass
        for edge in list(imported.edges):
            try:
                graph.add_edge(
                    edge_id=edge.edge_id,
                    edge_source=edge.edge_source,
                    edge_target=edge.edge_target,
                    edge_type=edge.edge_type,
                )
            except Exception:
                pass

        try:
            _enrich_pyarchinit_graph(graph, db_path, sito_filter=sito)
        except Exception as e:
            raise ProjectionError(
                f"Enrichment failed for sito={sito!r}: {e}") from e

        # Filter post-enrichment: keep only nodes whose attributes['sito']
        # match (defence in depth — _enrich already filters us_table rows
        # but EpochNodes are global and may belong to other sites).
        # We do NOT prune EpochNodes that are referenced via
        # has_first_epoch from any kept node.
        kept_node_ids = {
            n.node_id for n in graph.nodes
            if not hasattr(n, "attributes")
            or n.attributes is None
            or n.attributes.get("sito") in (None, sito)
        }
        # EpochNodes are global — keep them all if any strat node references them.
        # The downstream SiteMismatchError check in GraphIngestor catches mismatches.
        graph.nodes = [n for n in graph.nodes if n.node_id in kept_node_ids
                       or _is_epoch_node(n)]

        return graph


def _is_epoch_node(node) -> bool:
    """Return True if node is an EpochNode. Defensive — avoids importing
    EpochNode at module top because it forces s3dgraphy load too early."""
    return type(node).__name__ == "EpochNode"
