"""Load an s3dgraphy JSON export (v1.5) into a NetworkX DiGraph.

The s3dgraphy ``JSONExporter`` writes a hierarchical JSON document where
nodes are organised by category (stratigraphic, epochs, groups,
properties, documents, extractors, combiners, ...) and edges are
organised by relation type (``has_first_epoch``, ``overlies``, ``cuts``,
``fills``, ...). This module flattens that hierarchy into a single
``networkx.DiGraph`` annotated for downstream consumption by the
swimlane layout (:mod:`harris_swimlane_layout`) and the matplotlib
renderer (:mod:`matrix_swimlane_renderer`).

Each NetworkX node carries::

    {
      "kind": "US" | "USVs" | "USVn" | "SF" | "VSF" | "USD" |
              "TSU" | "SE" | "serSU" | "serUSVn" | "serUSVs" |
              "EpochNode" | "property" | "document" | "extractor" |
              "combiner" | "group" | ...,
      "name": str,
      "description": str,
      "data": dict,   # raw s3dgraphy node.data fields
      "bucket": str,  # JSON top-level key it came from ("stratigraphic", "epochs", ...)
    }

Each NetworkX edge carries::

    {
      "relation": str,   # edge_type from JSON (e.g. "overlies", "has_first_epoch")
      "id": str,         # edge_id from JSON
    }

The loader ALSO returns:

- :attr:`S3DGraphData.epochs`: ordered list of (epoch_id, name, start, end, color),
  sorted ascending by ``start_time`` so that index 0 is the OLDEST epoch.
- :attr:`S3DGraphData.node_to_epoch`: dict ``{node_id: epoch_id}`` built from
  ``has_first_epoch`` edges. Stratigraphic nodes without a first-epoch
  link get ``None`` (renderer puts them in a synthetic "unassigned" row).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "networkx is required for s3d_json_loader. "
        "Install via the plugin requirements.txt."
    ) from e


# Categories within ``nodes`` that contain {node_id: node_data} dicts.
# The stratigraphic bucket has ANOTHER level of nesting (per-kind dict)
# so it's handled separately.
_FLAT_NODE_BUCKETS = (
    "epochs", "groups", "properties", "documents",
    "extractors", "combiners", "authors", "licenses",
    "embargoes", "links", "geo", "semantic_shapes",
    "representation_models", "representation_model_doc",
    "representation_model_sf",
)

# Fallback bucket → kind mapping when the raw node dict lacks a "type"
# field (real s3dgraphy exports always include it; this matters only
# for synthetic test data and defensive parsing). Mirrors the
# canonical s3dgraphy node_type values seen in json_exporter.py:174-272.
_BUCKET_TO_KIND_FALLBACK = {
    "epochs": "EpochNode",
    "properties": "property",
    "documents": "document",
    "extractors": "extractor",
    "combiners": "combiner",
    "groups": "group",
    "authors": "author",
    "licenses": "license",
    "embargoes": "embargo",
    "links": "link",
    "geo": "geo_position",
    "semantic_shapes": "semantic_shape",
    "representation_models": "representation_model",
    "representation_model_doc": "representation_model_doc",
    "representation_model_sf": "representation_model_sf",
}


@dataclass
class EpochInfo:
    """One stratigraphic epoch (period) from the JSON."""
    epoch_id: str
    name: str
    start_time: Optional[float]  # negative for BC dates
    end_time: Optional[float]
    color: Optional[str]         # hex colour (palette accent for the row)


@dataclass
class S3DGraphData:
    """Parsed s3dgraphy JSON, ready to feed the swimlane layout."""
    graph_id: str
    name: str
    description: str
    networkx: "nx.DiGraph"
    epochs: List[EpochInfo] = field(default_factory=list)
    node_to_epoch: Dict[str, Optional[str]] = field(default_factory=dict)


def _coerce_time(v: Any) -> Optional[float]:
    """Convert a JSON time value to float (negative = BC). None if invalid."""
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _add_node(g: "nx.DiGraph", node_id: str, kind: str, bucket: str,
              raw: Dict[str, Any]) -> None:
    """Add one node to the graph with normalized attrs."""
    g.add_node(
        node_id,
        kind=kind,
        name=raw.get("name", "") or "",
        description=raw.get("description", "") or "",
        data=raw.get("data", {}) if isinstance(raw.get("data"), dict) else {},
        bucket=bucket,
    )


def _build_epochs(epochs_dict: Dict[str, Dict[str, Any]]) -> List[EpochInfo]:
    """Build the chronologically-ordered epoch list (oldest first)."""
    epochs: List[EpochInfo] = []
    for epoch_id, raw in epochs_dict.items():
        data = raw.get("data", {}) if isinstance(raw.get("data"), dict) else {}
        epochs.append(EpochInfo(
            epoch_id=epoch_id,
            name=raw.get("name", "") or "",
            start_time=_coerce_time(data.get("start_time")),
            end_time=_coerce_time(data.get("end_time")),
            color=(data.get("color") or "").strip() or None,
        ))
    # Sort: NULL start_time goes to the END (modern / unknown). Stable
    # otherwise so epoch insertion order is preserved within same start.
    epochs.sort(key=lambda e: (e.start_time is None, e.start_time or 0.0))
    return epochs


def _build_node_to_epoch(edges_dict: Dict[str, List[Dict[str, str]]]) -> Dict[str, str]:
    """Map each node → its first epoch via ``has_first_epoch`` edges.

    One node may have multiple ``has_first_epoch`` edges in theory; we
    keep the FIRST one encountered. Downstream (renderer) decides what
    to do for multi-epoch nodes; for now the simplest "primary epoch"
    suffices to assign a swimlane row.
    """
    mapping: Dict[str, str] = {}
    for edge in edges_dict.get("has_first_epoch", []):
        src = edge.get("from")
        tgt = edge.get("to")
        if src and tgt and src not in mapping:
            mapping[src] = tgt
    return mapping


def load_s3d_json(json_input: Union[str, Path, Dict[str, Any]],
                  graph_id: Optional[str] = None) -> S3DGraphData:
    """Parse an s3dgraphy JSON export into :class:`S3DGraphData`.

    Accepts either a file path (str / Path) or an already-loaded dict
    (useful for tests).

    If the export contains multiple graphs and ``graph_id`` is not
    specified, the FIRST graph in document order is used (s3dgraphy
    JSON v1.5 typically has one graph per file but supports multi).
    """
    # Load JSON
    if isinstance(json_input, dict):
        doc = json_input
    else:
        path = Path(json_input)
        if not path.exists():
            raise FileNotFoundError(f"s3dgraphy JSON not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            doc = json.load(f)

    graphs = doc.get("graphs", {})
    if not graphs:
        raise ValueError("No 'graphs' section in JSON export")
    if graph_id is None:
        graph_id = next(iter(graphs))
    if graph_id not in graphs:
        raise KeyError(f"graph_id {graph_id!r} not in export "
                       f"(available: {list(graphs.keys())})")

    g_data = graphs[graph_id]
    nodes_data = g_data.get("nodes", {})
    edges_data = g_data.get("edges", {})

    nx_graph = nx.DiGraph()

    # 1) Stratigraphic nodes (nested per-kind dict).
    stratigraphic = nodes_data.get("stratigraphic", {})
    if isinstance(stratigraphic, dict):
        for kind, id_map in stratigraphic.items():
            if not isinstance(id_map, dict):
                continue
            for node_id, raw in id_map.items():
                _add_node(nx_graph, node_id, kind, "stratigraphic", raw)

    # 2) Flat buckets (one level of nesting each).
    for bucket in _FLAT_NODE_BUCKETS:
        section = nodes_data.get(bucket, {})
        if not isinstance(section, dict):
            continue
        for node_id, raw in section.items():
            # Map bucket → semantic kind. Use the raw "type" field when
            # present (real exports always have it); otherwise fall
            # back to the canonical kind name via _BUCKET_TO_KIND_FALLBACK
            # (handles irregular plurals like properties→property, and
            # the special case epochs→EpochNode).
            kind = raw.get("type") if isinstance(raw, dict) else None
            if not kind:
                kind = _BUCKET_TO_KIND_FALLBACK.get(bucket, bucket)
            _add_node(nx_graph, node_id, kind, bucket, raw if isinstance(raw, dict) else {})

    # 3) Edges (all relation types).
    if isinstance(edges_data, dict):
        for relation, edge_list in edges_data.items():
            if not isinstance(edge_list, list):
                continue
            for edge in edge_list:
                src = edge.get("from")
                tgt = edge.get("to")
                if not src or not tgt:
                    continue
                # Skip edges to nodes not in the graph (defensive — happens
                # if the JSON references AuthorNodes etc. that were filtered).
                if src not in nx_graph or tgt not in nx_graph:
                    continue
                nx_graph.add_edge(src, tgt, relation=relation, id=edge.get("id"))

    # 4) Epoch registry + node→epoch mapping.
    epochs_list = _build_epochs(nodes_data.get("epochs", {}))
    node_to_epoch = _build_node_to_epoch(edges_data if isinstance(edges_data, dict) else {})

    # Backfill node_to_epoch with None for stratigraphic nodes without link
    for node_id, attrs in nx_graph.nodes(data=True):
        if attrs.get("bucket") == "stratigraphic":
            node_to_epoch.setdefault(node_id, None)

    return S3DGraphData(
        graph_id=graph_id,
        name=g_data.get("name", "") or "",
        description=g_data.get("description", "") or "",
        networkx=nx_graph,
        epochs=epochs_list,
        node_to_epoch=node_to_epoch,
    )
