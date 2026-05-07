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

import re
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


# Topological edge types that map onto temporal `is_after` precedence
# (i.e. those for which the inference engine has a non-None entry in
# TOPOLOGICAL_TO_TEMPORAL). Mirrored here to compute the pre-export
# temporal-edge count without re-running the engine.
_TEMPORAL_INPUT_EDGE_TYPES = frozenset({
    "cuts", "is_cut_by",
    "overlies", "is_overlain_by",
    "fills", "is_filled_by",
    "is_after", "is_before",
})


def _count_temporal_input_edges(graph) -> int:
    """Count edges that the TemporalInferenceEngine would feed into
    transitive_reduction(). Mirrors `extract_temporal_from_graph`'s
    inclusion rules without instantiating the engine.
    """
    return sum(
        1 for e in graph.edges
        if e.edge_type in _TEMPORAL_INPUT_EDGE_TYPES
    )


def _count_is_after_edges_in_xml(xml_text: str) -> int:
    """Count `is_after` edges present in a GraphML XML document.

    GraphMLExporter emits the edge type via a `<data key="..."` /
    `<y:EdgeLabel>` containing the literal "is_after". Each minimal
    temporal edge produces one such occurrence on an <edge> element.
    """
    # Count occurrences within edge labels. yEd labels embed the
    # edge_type as text; an attribute-form fallback also exists for
    # robustness.
    return len(re.findall(r">is_after<", xml_text)) + \
        len(re.findall(r'edge_type="is_after"', xml_text))


def export_graphml(
    db_path,
    mapping: str,
    output_path,
    *,
    site_filter: Optional[str] = None,
    persist_auxiliary: bool = False,
) -> ExportResult:
    """Run PyArchInitImporter → optional site filter → GraphMLExporter.

    Args:
        db_path: filesystem path to the SQLite DB (str or Path).
        mapping: name of the s3dgraphy mapping to use, e.g. "pyarchinit".
        output_path: filesystem path where to write the GraphML.
        site_filter: optional `sito` value to restrict the export.
        persist_auxiliary: bake (True) vs volatile (False) auxiliary
            data policy. Default False (volatile) per Spec D6.

    Returns:
        ExportResult with metrics + warnings.

    Raises:
        EmptyGraphError: if the (filtered) graph has no nodes.
        GraphMLExportError(stage=...): wraps any failure in import,
            filter, export or write stages.
    """
    db_path = Path(db_path)
    output_path = Path(output_path)

    # Stage 1: import
    try:
        from s3dgraphy.importer.pyarchinit_importer import (
            PyArchInitImporter,
        )
        importer = PyArchInitImporter(
            filepath=str(db_path), mapping_name=mapping)
        graph = importer.parse()
    except Exception as e:
        raise GraphMLExportError("import", e) from e

    # Stage 2: filter
    try:
        graph = _filter_by_site(graph, site_filter)
    except Exception as e:
        raise GraphMLExportError("filter", e) from e

    if len(graph.nodes) == 0:
        raise EmptyGraphError(
            f"No nodes after filter site_filter={site_filter!r}")

    # Count temporal-input edges BEFORE export so we can compute
    # tred_removed_edges by arithmetic on the produced XML. The
    # TemporalInferenceEngine does not emit a "removed N edges"
    # warning to graph.warnings (it only prints a stdout report and
    # adds warnings on cycle detection), so the plan's regex over
    # graph.warnings can never resolve. We use the arithmetic
    # fallback the plan suggested.
    temporal_input_count = _count_temporal_input_edges(graph)

    # Stage 3: export (in-memory XML build)
    try:
        from s3dgraphy.exporter.graphml.graphml_exporter import (
            GraphMLExporter,
        )
        exporter = GraphMLExporter(graph)
    except Exception as e:
        raise GraphMLExportError("export", e) from e

    # Stage 4: write
    try:
        exporter.export(
            str(output_path), persist_auxiliary=persist_auxiliary)
    except Exception as e:
        raise GraphMLExportError("write", e) from e

    # Build the result. Counts come from the post-export graph.
    from s3dgraphy.nodes.epoch_node import EpochNode
    epoch_count = sum(
        1 for n in graph.nodes if isinstance(n, EpochNode))

    # tred_removed_edges via arithmetic fallback (see comment above):
    # number of temporal-input edges minus number of is_after edges
    # actually emitted by the exporter after transitive reduction.
    # Cap at 0 to defend against off-by-one or unforeseen exporter
    # heuristics — never report a negative reduction.
    try:
        emitted_xml = output_path.read_text(encoding="utf-8")
        is_after_emitted = _count_is_after_edges_in_xml(emitted_xml)
        tred_removed = max(0, temporal_input_count - is_after_emitted)
    except OSError:
        tred_removed = 0

    warnings = list(getattr(graph, "warnings", []))

    return ExportResult(
        output_path=str(output_path),
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        epoch_count=epoch_count,
        tred_removed_edges=tred_removed,
        warnings=warnings,
    )
