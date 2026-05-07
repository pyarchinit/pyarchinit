"""Pure-Python wrapper over s3dgraphy.PyArchInitImporter +
s3dgraphy.exporter.graphml.GraphMLExporter.

Public API:
    export_graphml(db_path, mapping, output_path,
                   *, site_filter=None, persist_auxiliary=False) -> ExportResult

This is the AI03 cut-over surface (per spec §3.2). Replaces the
legacy DOT→GraphML pipeline that lived in s3dgraphy_dot_bridge.py
+ graphml_spatial_enhancer.py + dottoxml.exportGraphml.

No Qt imports — runnable from bare pytest.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ExportResult:
    """Metrics + warnings returned by a successful export_graphml() call."""
    output_path: str
    node_count: int
    edge_count: int
    epoch_count: int
    tred_removed_edges: int
    warnings: list = field(default_factory=list)


VALID_STAGES = frozenset({"import", "filter", "export", "write"})


class EmptyGraphError(ValueError):
    """Graph has no nodes after import + (optional) site filter."""


class GraphMLExportError(RuntimeError):
    """Wraps any failure during the GraphML export pipeline.

    Attributes:
        stage: one of VALID_STAGES — categorises where the failure
            occurred so the bridge UI can present a useful message.
        original: the underlying exception, preserved for logging.
    """

    def __init__(self, stage: str, original: Exception):
        if stage not in VALID_STAGES:
            raise ValueError(
                f"unknown stage {stage!r}; valid: {sorted(VALID_STAGES)}")
        self.stage = stage
        self.original = original
        super().__init__(
            f"GraphML {stage} failed: {type(original).__name__}: {original}")


def _filter_by_site(graph, site_filter: Optional[str]):
    """Return a new Graph containing only nodes/edges relevant to *site_filter*.

    Retention rules (per spec §5 step 6.iv.2):
    - Stratigraphic node kept iff its `attributes['sito']` equals site_filter.
    - EpochNode kept iff at least one retained stratigraphic node points at
      it via a `has_first_epoch` edge.
    - Edges kept iff BOTH endpoints are kept.

    `site_filter=None` returns the original graph unchanged.
    """
    if site_filter is None:
        return graph

    # ext_libs must be importable; this module is also imported from the bridge
    # which already adds it to sys.path during plugin initialisation.
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

    out = Graph(
        graph_id=getattr(graph, "graph_id", "filtered"),
        name=getattr(graph, "name", "filtered"),
        description=getattr(graph, "description", ""),
    )

    # Pass 1: keep stratigraphic nodes matching site_filter
    kept_strat_ids = set()
    for n in graph.nodes:
        if isinstance(n, StratigraphicNode):
            if n.attributes.get("sito") == site_filter:
                out.add_node(n)
                kept_strat_ids.add(n.node_id)

    # Pass 2: walk has_first_epoch edges from kept strat nodes;
    # collect epoch ids reachable that way.
    reachable_epoch_ids = set()
    for e in graph.edges:
        if (e.edge_type == "has_first_epoch"
                and e.edge_source in kept_strat_ids):
            reachable_epoch_ids.add(e.edge_target)

    # Pass 3: keep EpochNodes whose ids are in reachable_epoch_ids
    for n in graph.nodes:
        if isinstance(n, EpochNode) and n.node_id in reachable_epoch_ids:
            out.add_node(n)

    # Pass 4: keep edges whose BOTH endpoints survived. Note: Graph.add_edge
    # takes 4 positional strings (edge_id, edge_source, edge_target,
    # edge_type), not an Edge instance.
    kept_node_ids = {n.node_id for n in out.nodes}
    for e in graph.edges:
        if (e.edge_source in kept_node_ids
                and e.edge_target in kept_node_ids):
            out.add_edge(e.edge_id, e.edge_source, e.edge_target, e.edge_type)

    return out
