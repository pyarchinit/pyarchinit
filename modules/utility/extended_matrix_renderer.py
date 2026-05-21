"""Render an Extended Matrix GraphML to PNG/JPEG with yEd-style group folders.

This is the THIRD renderer in the matrix-image pipeline. It supersedes
:mod:`graphml_to_png_renderer` (which used stored — overlapping —
positions) and :mod:`matrix_swimlane_renderer` (which ignored the
group structure and produced a flat swimlane).

Reads the .graphml that ``S3DGraphyDotBridge.export_extended_matrix_multi_format``
already produces, extracts:

- Group folders (yEd ``yfiles.foldertype="group"`` nodes), e.g.
  ``VA01`` / ``VA02`` / ... — these are the *attività* (activities)
  computed by the AI06 group projector.
- Member nodes per group (yEd nests them inside the group's nested
  ``<graph>`` element).
- Edges (both intra-group and cross-group).

Recomputes a FRESH layered layout per group:

- ``_topological_layers()`` → BFS layering with SCC condensation.
- Roots at the TOP of the group, deepest leaves at the BOTTOM
  (Harris matrix convention: youngest above oldest within a unit).
- Groups stacked vertically on the page (single column) with a
  fixed margin between them. Each group's width is uniform (so
  groups align visually); height scales with internal content.

Draws with matplotlib + EM palette styles inherited from the graphml
itself (so colour/shape decisions are baked into the file, no extra
palette lookup needed).

Public API:

    >>> render_extended_matrix("/path/file.graphml",
    ...                        "/path/out.png", format="png")
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from xml.etree import ElementTree as ET


_NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}


# ----------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------

@dataclass
class _NodeStyle:
    """Visual style extracted from yEd graphics — purely cosmetic."""
    fill: str = "#FFFFFF"
    border: str = "#000000"
    border_width: float = 1.0
    shape: str = "rectangle"
    width: float = 50.0
    height: float = 30.0


@dataclass
class _Node:
    node_id: str
    label: str
    style: _NodeStyle = field(default_factory=_NodeStyle)
    group_id: Optional[str] = None    # None = top-level (rare)


@dataclass
class _GroupFolder:
    group_id: str
    label: str
    member_ids: List[str] = field(default_factory=list)


@dataclass
class _Edge:
    source: str
    target: str
    relation: str = ""           # "Copre" / "Taglia" / "<<" / ">>" / etc.
    color: str = "#3a4d5c"
    linewidth: float = 0.8
    linestyle: str = "-"
    alpha: float = 0.6


# Italian EM relation vocabulary → matplotlib styling. Pairs (forward,
# reverse) generally have the SAME visual style; the directionality
# of the arrow is what conveys the asymmetry.
_REL_STYLES = {
    # Stratigraphic primary relations
    "Copre":         {"color": "#1a2d4a", "linewidth": 1.2, "linestyle": "-",  "alpha": 0.85},
    "Coperto da":    {"color": "#1a2d4a", "linewidth": 1.2, "linestyle": "-",  "alpha": 0.85},
    "Taglia":        {"color": "#9B3333", "linewidth": 1.4, "linestyle": "--", "alpha": 0.90},
    "Tagliato da":   {"color": "#9B3333", "linewidth": 1.4, "linestyle": "--", "alpha": 0.90},
    "Riempie":       {"color": "#1f4e8a", "linewidth": 1.2, "linestyle": ":",  "alpha": 0.85},
    "Riempito da":   {"color": "#1f4e8a", "linewidth": 1.2, "linestyle": ":",  "alpha": 0.85},
    "Si appoggia a": {"color": "#666666", "linewidth": 1.0, "linestyle": "-.", "alpha": 0.75},
    "Gli si appoggia": {"color": "#666666", "linewidth": 1.0, "linestyle": "-.", "alpha": 0.75},
    "Si lega a":     {"color": "#31792D", "linewidth": 1.3, "linestyle": "-",  "alpha": 0.85},
    "Uguale a":      {"color": "#1a2d4a", "linewidth": 2.0, "linestyle": "-",  "alpha": 0.90},
    # Paradata / group-membership relations
    ">>":            {"color": "#9aa6b3", "linewidth": 0.6, "linestyle": "-",  "alpha": 0.55},
    "<<":            {"color": "#9aa6b3", "linewidth": 0.6, "linestyle": "-",  "alpha": 0.55},
}
_REL_DEFAULT_STYLE = {"color": "#3a4d5c", "linewidth": 0.8,
                      "linestyle": "-", "alpha": 0.6}


def _style_edge(e: "_Edge") -> "_Edge":
    """Apply colour/width/linestyle/alpha based on e.relation."""
    style = _REL_STYLES.get(e.relation, _REL_DEFAULT_STYLE)
    e.color = style["color"]
    e.linewidth = style["linewidth"]
    e.linestyle = style["linestyle"]
    e.alpha = style["alpha"]
    return e


@dataclass
class _Scene:
    nodes: Dict[str, _Node] = field(default_factory=dict)
    groups: Dict[str, _GroupFolder] = field(default_factory=dict)
    edges: List[_Edge] = field(default_factory=list)
    title: str = ""


# ----------------------------------------------------------------------
# Parsing helpers
# ----------------------------------------------------------------------

def _strip_hex(c: str) -> str:
    if not c:
        return "#000000"
    return c if c.startswith("#") else "#" + c


def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _readable_text_color(fill_hex: str) -> str:
    """Auto-pick white vs black text based on fill luminance."""
    if not fill_hex or not fill_hex.startswith("#") or len(fill_hex) < 7:
        return "#000000"
    try:
        r = int(fill_hex[1:3], 16) / 255.0
        g = int(fill_hex[3:5], 16) / 255.0
        b = int(fill_hex[5:7], 16) / 255.0
    except ValueError:
        return "#000000"
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#ffffff" if lum < 0.5 else "#000000"


def _extract_label(node_elem: ET.Element) -> str:
    for lbl in node_elem.iter(f"{{{_NS['y']}}}NodeLabel"):
        if (lbl.text or "").strip():
            return (lbl.text or "").strip()
    return ""


def _extract_style(node_elem: ET.Element) -> _NodeStyle:
    """Find the first graphics element and extract style."""
    style = _NodeStyle()
    graphic = None
    for tag in ("GenericNode", "ShapeNode", "SVGNode", "ImageNode",
                "GenericGroupNode", "GroupNode", "ProxyAutoBoundsNode"):
        cand = node_elem.find(f".//{{{_NS['y']}}}{tag}")
        if cand is not None:
            graphic = cand
            break
    if graphic is None:
        return style
    if graphic.tag.endswith("ProxyAutoBoundsNode"):
        for tag in ("GroupNode", "GenericGroupNode", "ShapeNode", "GenericNode"):
            inner = graphic.find(f".//{{{_NS['y']}}}{tag}")
            if inner is not None:
                graphic = inner
                break

    geom = graphic.find(f".//{{{_NS['y']}}}Geometry")
    if geom is not None:
        style.width = _safe_float(geom.attrib.get("width", "50"), 50.0)
        style.height = _safe_float(geom.attrib.get("height", "30"), 30.0)
    fill_elem = graphic.find(f".//{{{_NS['y']}}}Fill")
    if fill_elem is not None:
        style.fill = _strip_hex(fill_elem.attrib.get("color", "#FFFFFF"))[:7]
    border_elem = graphic.find(f".//{{{_NS['y']}}}BorderStyle")
    if border_elem is not None:
        style.border = _strip_hex(border_elem.attrib.get("color", "#000000"))[:7]
        style.border_width = _safe_float(border_elem.attrib.get("width", "1"), 1.0)

    # Shape
    tag_local = graphic.tag.rsplit("}", 1)[-1]
    if tag_local == "ShapeNode":
        shape_elem = graphic.find(f"{{{_NS['y']}}}Shape")
        style.shape = (shape_elem.attrib.get("type") if shape_elem is not None
                       else "rectangle")
    elif tag_local in ("SVGNode", "ImageNode"):
        style.shape = "svg"
    else:
        style.shape = "generic"
    return style


def _parse_graphml(graphml_path: Path) -> _Scene:
    """Walk the graphml and extract nodes / groups / edges.

    Edges are derived from the per-node ``pyarchinit.rapporti`` data
    field (key ``d15``) which carries the TYPED EM relations
    (``Copre`` / ``Taglia`` / ``Riempie`` / ``<<`` / ``>>`` / ...).
    The graphml's top-level ``<edge>`` elements are kept as a fallback
    for older exports that lack the rapporti field.

    Each node's rapporti looks like::

        [["Coperto da", "03", "1", "test"],
         ["Copre",      "01", "1", "test"],
         ["<<",         "101", "1", "test"]]

    Format: ``[tipo, us, area, sito]``. We resolve ``(us, area, sito)``
    back to a node_id via a reverse index built from d0/d1/d2 (us, area,
    sito) of each node.
    """
    tree = ET.parse(str(graphml_path))
    root = tree.getroot()
    scene = _Scene(title=graphml_path.stem)

    # Per-node raw data (collected during the walk; used for rapporti
    # post-processing). Keyed by graphml node id.
    raw_data: Dict[str, Dict[str, str]] = {}

    def _collect_data(n_elem: ET.Element, node_id: str):
        bag: Dict[str, str] = {}
        for d in n_elem.findall(f"{{{_NS['g']}}}data"):
            k = d.attrib.get("key", "")
            t = (d.text or "").strip()
            if k and t:
                bag[k] = t
        raw_data[node_id] = bag

    def _walk(parent_node: Optional[ET.Element], parent_group_id: Optional[str]):
        """Recurse into <graph> children under parent_node."""
        for graph in parent_node.findall(f"{{{_NS['g']}}}graph"):
            for n in graph.findall(f"{{{_NS['g']}}}node"):
                node_id = n.attrib.get("id", "")
                if not node_id:
                    continue
                _collect_data(n, node_id)
                label = _extract_label(n)
                is_group = n.attrib.get("yfiles.foldertype") in ("group", "folder")
                if is_group:
                    g = _GroupFolder(group_id=node_id, label=label)
                    scene.groups[node_id] = g
                    _walk(n, node_id)
                else:
                    style = _extract_style(n)
                    scene.nodes[node_id] = _Node(
                        node_id=node_id, label=label, style=style,
                        group_id=parent_group_id,
                    )

    # Top-level <graph>
    top_graph = root.find(f"{{{_NS['g']}}}graph")
    if top_graph is None:
        return scene
    for n in top_graph.findall(f"{{{_NS['g']}}}node"):
        node_id = n.attrib.get("id", "")
        if not node_id:
            continue
        _collect_data(n, node_id)
        label = _extract_label(n)
        is_group = n.attrib.get("yfiles.foldertype") in ("group", "folder")
        if is_group:
            g = _GroupFolder(group_id=node_id, label=label)
            scene.groups[node_id] = g
            _walk(n, node_id)
        else:
            style = _extract_style(n)
            scene.nodes[node_id] = _Node(
                node_id=node_id, label=label, style=style, group_id=None,
            )

    # Backfill group member_ids
    for n in scene.nodes.values():
        if n.group_id and n.group_id in scene.groups:
            scene.groups[n.group_id].member_ids.append(n.node_id)

    # --- Build (us, area, sito) -> node_id reverse index (case-insensitive
    # on us value, since pyarchinit stores both '02' and '2'-typed-string
    # forms in different code paths).
    by_uas: Dict[Tuple[str, str, str], str] = {}
    for nid, bag in raw_data.items():
        us = bag.get("d0", "").strip()
        area = bag.get("d1", "").strip()
        sito = bag.get("d2", "").strip()
        if us and nid in scene.nodes:
            by_uas[(us.lower(), area.lower(), sito.lower())] = nid

    # --- Derive typed edges from the rapporti field ---
    # Direction semantics: pyarchinit rapporti are stored on the
    # ORIGIN node (the row owner). For each [tipo, target_us, area, sito]:
    #
    #   ">>" means "I am the PARENT, listed target is my CHILD"
    #        → edge orientation: this_node → target  (keep as-is)
    #
    #   "<<" means "I am the CHILD, listed target is my PARENT"
    #        → edge orientation: target → this_node  (REVERSED)
    #
    # This matters for the layered layout: parents end up at the TOP
    # of the group, children at the bottom. Stratigraphic relations
    # follow EM convention: "Copre" means "I cover X" (I'm above),
    # "Coperto da" means "I am covered by X" (X is above me, REVERSED).
    import ast as _ast

    _REVERSED_RELATIONS = {"<<", "Coperto da", "Tagliato da", "Riempito da",
                           "Gli si appoggia"}
    edge_seen: set = set()  # dedup: (source, target, relation)
    edges_from_rapporti = 0
    for nid, bag in raw_data.items():
        if nid not in scene.nodes:
            continue
        rapporti_raw = bag.get("d15", "")
        if not rapporti_raw:
            continue
        try:
            rap_list = _ast.literal_eval(rapporti_raw)
        except (ValueError, SyntaxError):
            continue
        if not isinstance(rap_list, (list, tuple)):
            continue
        for entry in rap_list:
            if not isinstance(entry, (list, tuple)) or len(entry) < 4:
                continue
            tipo, target_us, target_area, target_sito = (
                str(entry[0]), str(entry[1]), str(entry[2]), str(entry[3])
            )
            key = (target_us.lower(), target_area.lower(), target_sito.lower())
            target_nid = by_uas.get(key)
            if target_nid is None or target_nid == nid:
                continue
            if tipo in _REVERSED_RELATIONS:
                src, tgt = target_nid, nid
            else:
                src, tgt = nid, target_nid
            dedup_key = (src, tgt, tipo)
            if dedup_key in edge_seen:
                continue
            edge_seen.add(dedup_key)
            scene.edges.append(_style_edge(_Edge(
                source=src, target=tgt, relation=tipo,
            )))
            edges_from_rapporti += 1

    # Fallback: if no rapporti-derived edges, fall back to graphml <edge>
    # elements (older exports lacking the d15 field).
    if edges_from_rapporti == 0:
        for e in root.iter(f"{{{_NS['g']}}}edge"):
            src = e.attrib.get("source", "")
            tgt = e.attrib.get("target", "")
            if src and tgt:
                scene.edges.append(_style_edge(_Edge(src, tgt)))

    return scene


# ----------------------------------------------------------------------
# Layout: layered per group + vertical stack
# ----------------------------------------------------------------------

def _topological_layers(member_ids: List[str], edges: List[_Edge],
                        member_set: Optional[set] = None
                        ) -> Tuple[List[List[str]], List[Tuple[str, str]]]:
    """Sugiyama-style layering with transitive reduction.

    Pipeline:
      1. Induce subgraph over ``member_ids``.
      2. Break cycles deterministically via SCC condensation
         (each SCC collapses to a representative node; intra-SCC
         edges dropped).
      3. ``nx.transitive_reduction`` → keep only the necessary edges
         (drops A→C when A→B→C also exists).
      4. Longest-path layering: layer[v] = max(layer[u]+1) over
         predecessors u in the reduced DAG.
      5. Barycenter ordering: iterate up/down passes to minimise edge
         crossings between adjacent layers.

    Returns ``(layers, reduced_edges)`` where:
      - ``layers`` is the ordered list of layers (top → bottom)
        with each layer being a list of node_ids in left→right order.
      - ``reduced_edges`` is the (src, tgt) edge list AFTER transitive
        reduction — the renderer should prefer drawing these (with
        styling carried from the original _Edge objects that match).
    """
    if not member_ids:
        return [], []
    try:
        import networkx as nx
    except ImportError:
        return [list(member_ids)], []

    mset = member_set if member_set is not None else set(member_ids)
    sub = nx.DiGraph()
    sub.add_nodes_from(member_ids)
    for e in edges:
        if e.source in mset and e.target in mset and e.source != e.target:
            sub.add_edge(e.source, e.target)

    if sub.number_of_edges() == 0:
        return [sorted(member_ids)], []

    # 1) Condense SCCs into a DAG. Within each SCC pick a "representative"
    # node (lexicographically smallest id). The other SCC members get
    # placed in the same layer as the representative.
    cond = nx.condensation(sub)
    members_attr = nx.get_node_attributes(cond, "members")
    # Map scc_idx → representative node_id
    rep_of: Dict[int, str] = {
        idx: sorted(members_attr.get(idx, []))[0]
        for idx in cond.nodes if members_attr.get(idx)
    }
    # Build a clean DAG over representatives only.
    dag = nx.DiGraph()
    dag.add_nodes_from(rep_of.values())
    for u, v in cond.edges:
        if u in rep_of and v in rep_of:
            dag.add_edge(rep_of[u], rep_of[v])

    # 2) Transitive reduction (removes redundant long-arrow edges).
    if dag.number_of_edges() > 0:
        try:
            reduced = nx.transitive_reduction(dag)
        except Exception:
            reduced = dag
    else:
        reduced = dag

    # 3) Longest-path layer assignment.
    layer_of: Dict[str, int] = {n: 0 for n in reduced.nodes}
    for n in nx.topological_sort(reduced):
        preds = list(reduced.predecessors(n))
        if preds:
            layer_of[n] = max(layer_of[p] for p in preds) + 1

    max_layer = max(layer_of.values()) if layer_of else 0
    layers_by_idx: List[List[str]] = [[] for _ in range(max_layer + 1)]
    for rep, lvl in layer_of.items():
        layers_by_idx[lvl].append(rep)

    # 4) Expand SCC members back into their representative's layer
    # (non-representative SCC siblings sit in the same layer).
    rep_to_scc_members: Dict[str, List[str]] = {}
    for idx, ms in members_attr.items():
        rep = rep_of.get(idx)
        if rep is None:
            continue
        siblings = sorted(ms)
        rep_to_scc_members[rep] = siblings  # rep is first in sorted list

    expanded_layers: List[List[str]] = []
    for layer in layers_by_idx:
        out_layer: List[str] = []
        for rep in layer:
            out_layer.extend(rep_to_scc_members.get(rep, [rep]))
        if out_layer:
            expanded_layers.append(out_layer)

    # 5) Barycenter ordering: minimise edge crossings between layers.
    #    A few iterations of alternating down/up passes converge.
    _barycenter_ordering(expanded_layers, sub)

    # Reduced edges to return (in the representative DAG; expand to
    # actual node pairs by SCC representative).
    reduced_edges = [(u, v) for u, v in reduced.edges]

    return expanded_layers, reduced_edges


def _barycenter_ordering(layers: List[List[str]], graph) -> None:
    """In-place barycenter heuristic to minimise inter-layer crossings.

    Two passes (down then up) usually achieve most of the reduction.
    Stable: nodes with no neighbours in the reference layer keep
    their original position.
    """
    if len(layers) < 2:
        return

    def _do_pass(direction: int):
        # direction = +1 means use PREVIOUS layer as reference (top→bottom)
        # direction = -1 means use NEXT layer as reference (bottom→up)
        if direction > 0:
            iterator = range(1, len(layers))
        else:
            iterator = range(len(layers) - 2, -1, -1)
        for idx in iterator:
            ref_layer = layers[idx - direction]
            ref_pos = {n: i for i, n in enumerate(ref_layer)}
            current = layers[idx]
            scores = []
            for i, n in enumerate(current):
                if direction > 0:
                    neighbours = list(graph.predecessors(n)) if n in graph else []
                else:
                    neighbours = list(graph.successors(n)) if n in graph else []
                ref_positions = [ref_pos[m] for m in neighbours if m in ref_pos]
                bary = (sum(ref_positions) / len(ref_positions)
                        if ref_positions else i)
                scores.append((bary, i, n))
            scores.sort()
            layers[idx] = [n for _bary, _i, n in scores]

    for _ in range(3):
        _do_pass(+1)
        _do_pass(-1)


@dataclass
class _GroupLayout:
    group_id: str
    label: str
    layers: List[List[str]] = field(default_factory=list)
    reduced_edges: set = field(default_factory=set)  # {(src, tgt)} kept after TR
    width: float = 0.0
    height: float = 0.0
    x: float = 0.0         # absolute origin (top-left)
    y: float = 0.0


def _compute_group_layouts(scene: _Scene,
                           node_w: float = 80.0,
                           node_h: float = 35.0,
                           cell_x_pad: float = 30.0,
                           cell_y_pad: float = 25.0,
                           group_margin: float = 35.0,
                           group_internal_pad: float = 25.0,
                           uniform_group_width: bool = True
                           ) -> Tuple[List[_GroupLayout], float, float]:
    """Compute per-group layered layout + global positions.

    Returns (group_layouts, total_width, total_height) all in
    matplotlib coordinate units (we use yEd-like units: pixels).
    """
    groups_out: List[_GroupLayout] = []
    cell_w = node_w + cell_x_pad
    cell_h = node_h + cell_y_pad

    # 1) Per-group layered layout + bbox.
    for g in scene.groups.values():
        if not g.member_ids:
            continue
        member_set = set(g.member_ids)
        layers, reduced_edges = _topological_layers(
            g.member_ids, scene.edges, member_set,
        )
        if not layers:
            continue
        max_w_cells = max(len(L) for L in layers)
        gl = _GroupLayout(
            group_id=g.group_id, label=g.label, layers=layers,
            reduced_edges=set(reduced_edges),
            width=max_w_cells * cell_w + 2 * group_internal_pad,
            height=len(layers) * cell_h + 2 * group_internal_pad + 40.0,  # +40 for header
        )
        groups_out.append(gl)

    if not groups_out:
        return [], 0.0, 0.0

    # 2) Uniform group width (so they align visually as a column).
    if uniform_group_width:
        max_w = max(g.width for g in groups_out)
        for g in groups_out:
            g.width = max_w

    # 3) Stack vertically, single column.
    y_cursor = 0.0
    for g in groups_out:
        g.x = 0.0
        g.y = y_cursor
        y_cursor += g.height + group_margin
    total_width = max(g.width for g in groups_out)
    total_height = y_cursor

    return groups_out, total_width, total_height


def _node_positions(scene: _Scene, group_layouts: List[_GroupLayout],
                    node_w: float = 80.0, node_h: float = 35.0,
                    cell_x_pad: float = 30.0, cell_y_pad: float = 25.0,
                    group_internal_pad: float = 25.0) -> Dict[str, Tuple[float, float]]:
    """Map each non-group node to its absolute (cx, cy) centre position."""
    positions: Dict[str, Tuple[float, float]] = {}
    cell_w = node_w + cell_x_pad
    cell_h = node_h + cell_y_pad
    for g in group_layouts:
        # Header eats top 40 px of group; layers start below it.
        inner_top = g.y + group_internal_pad + 40.0
        for layer_idx, layer in enumerate(g.layers):
            n_in_layer = len(layer)
            row_y = inner_top + layer_idx * cell_h + cell_h / 2.0
            # Centre the layer within group's width.
            total_layer_w = n_in_layer * cell_w
            start_x = g.x + (g.width - total_layer_w) / 2.0
            for col_idx, nid in enumerate(layer):
                cx = start_x + col_idx * cell_w + cell_w / 2.0
                positions[nid] = (cx, row_y)
    return positions


# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

def _import_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import (Ellipse, FancyBboxPatch, Polygon,
                                    Rectangle, RegularPolygon)
    return plt, Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch


def _draw_node(ax, n: _Node, cx: float, cy: float, w: float, h: float,
               patches_mod) -> None:
    """Draw a node patch + label at (cx, cy) with size (w, h)."""
    Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch = patches_mod
    s = n.style
    fill = s.fill if len(s.fill) <= 7 else s.fill[:7]
    lw = max(0.6, min(s.border_width, 2.5))

    if s.shape == "ellipse":
        p = Ellipse((cx, cy), w, h, facecolor=fill, edgecolor=s.border, linewidth=lw)
    elif s.shape == "parallelogram":
        skew = w * 0.18
        pts = [(cx - w/2 + skew, cy + h/2),  # top-left (yEd uses inverted y, but we already flipped)
               (cx + w/2, cy + h/2),
               (cx + w/2 - skew, cy - h/2),
               (cx - w/2, cy - h/2)]
        p = Polygon(pts, closed=True, facecolor=fill, edgecolor=s.border, linewidth=lw)
    elif s.shape == "hexagon":
        p = RegularPolygon((cx, cy), numVertices=6, radius=max(w, h)/1.8,
                           orientation=0, facecolor=fill, edgecolor=s.border, linewidth=lw)
    elif s.shape == "octagon":
        p = RegularPolygon((cx, cy), numVertices=8, radius=max(w, h)/1.85,
                           orientation=0, facecolor=fill, edgecolor=s.border, linewidth=lw)
    elif s.shape == "roundrectangle":
        p = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.02,rounding_size=4",
                           facecolor=fill, edgecolor=s.border, linewidth=lw)
    else:
        p = Rectangle((cx - w/2, cy - h/2), w, h,
                      facecolor=fill, edgecolor=s.border, linewidth=lw)
    ax.add_patch(p)
    if n.label:
        ax.text(cx, cy, n.label[:14],
                ha="center", va="center", fontsize=8,
                color=_readable_text_color(fill),
                zorder=4)


def render_extended_matrix(graphml_path: Union[str, Path],
                           output_path: Union[str, Path],
                           *,
                           format: str = "png",
                           dpi: int = 150,
                           node_width: float = 80.0,
                           node_height: float = 35.0,
                           background: str = "#eef2f7") -> Path:
    """Render the Extended Matrix to PNG/JPEG/SVG.

    The GraphML's group folders (AI06 activity groups) drive the
    high-level structure: each group is rendered as a sage-green
    rounded container with the activity name as header. Within each
    container, a fresh Harris layered layout is computed (roots top,
    leaves bottom). Groups are stacked vertically with uniform width.
    """
    graphml_path = Path(graphml_path)
    output_path = Path(output_path)
    if not graphml_path.exists():
        raise FileNotFoundError(f"GraphML not found: {graphml_path}")

    scene = _parse_graphml(graphml_path)
    if not scene.groups:
        raise ValueError(
            f"No group folders in {graphml_path}. The Extended Matrix "
            "renderer requires the GraphML to contain yEd group nodes "
            "(AI06 attivita groups). Was the pipeline export configured "
            "to inject groups?"
        )

    group_layouts, total_w, total_h = _compute_group_layouts(
        scene, node_w=node_width, node_h=node_height,
    )
    positions = _node_positions(
        scene, group_layouts, node_w=node_width, node_h=node_height,
    )

    if not positions:
        raise ValueError("No drawable positions computed.")

    plt, Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch = _import_mpl()
    patches_mod = (Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch)

    # Figure: 1 in per ~110 logical units, clamped.
    fig_w_in = max(8.0, min(40.0, total_w / 100.0))
    fig_h_in = max(6.0, min(80.0, total_h / 80.0))
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in),
                           dpi=dpi, facecolor=background)
    pad = 30.0
    ax.set_xlim(-pad, total_w + pad)
    ax.set_ylim(-pad, total_h + pad)
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # 1) Group containers
    for g in group_layouts:
        ax.add_patch(Rectangle(
            (g.x, g.y), g.width, g.height,
            facecolor="#dde6d6",       # sage-green background (yEd default)
            edgecolor="#a3b2a1",
            linewidth=1.0,
            zorder=0,
        ))
        # Group header pill at top-left
        if g.label:
            ax.add_patch(Rectangle(
                (g.x + 8, g.y + 6), 70.0, 22.0,
                facecolor="#1a2d4a", edgecolor="#1a2d4a", zorder=1,
            ))
            ax.text(g.x + 8 + 35, g.y + 6 + 11, g.label,
                    ha="center", va="center", fontsize=10,
                    color="#ffffff", fontweight="bold", zorder=2)

    # 2) Edges — typed + orthogonal routing + transitive-reduction filter
    # Build a node→group_id index so we can decide whether an edge is
    # within-group (subject to that group's reduced-edge filter) or
    # cross-group (always kept — those are the real stratigraphic
    # links between activities).
    node_to_group: Dict[str, str] = {}
    for g in group_layouts:
        for layer in g.layers:
            for nid in layer:
                node_to_group[nid] = g.group_id
    group_lookup = {g.group_id: g for g in group_layouts}

    from matplotlib.patches import FancyArrowPatch
    pos = positions
    for e in scene.edges:
        if e.source not in pos or e.target not in pos:
            continue
        src_grp = node_to_group.get(e.source)
        tgt_grp = node_to_group.get(e.target)
        # Within-group: skip if transitive reduction dropped this edge.
        if src_grp and src_grp == tgt_grp:
            grp = group_lookup.get(src_grp)
            if grp is not None and grp.reduced_edges and \
                    (e.source, e.target) not in grp.reduced_edges:
                continue
        x1, y1 = pos[e.source]
        x2, y2 = pos[e.target]
        # Orthogonal routing: angle3 produces a single 90° bend
        # between source and target. Pick the bend angles based on
        # the relative position (mostly-vertical → bend at top
        # going down then right; mostly-horizontal → bend at right
        # going across then down).
        dx = x2 - x1
        dy = y2 - y1
        if abs(dy) >= abs(dx):
            # Mostly vertical (parent→child): leave node downward (90),
            # arrive horizontally (180 or 0).
            angleA, angleB = 90, 180 if dx < 0 else 0
        else:
            # Mostly horizontal (sibling-ish): leave node sideways,
            # arrive top/bottom.
            angleA = 180 if dx < 0 else 0
            angleB = 90 if dy < 0 else 270
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"angle,angleA={angleA},angleB={angleB},rad=2",
            arrowstyle="->,head_width=4,head_length=6",
            color=e.color,
            linewidth=e.linewidth,
            linestyle=e.linestyle,
            alpha=e.alpha,
            shrinkA=node_height * 0.55, shrinkB=node_height * 0.55,
            mutation_scale=10,
        )
        ax.add_patch(arrow)

    # 3) Nodes (on top)
    for nid, (cx, cy) in positions.items():
        node = scene.nodes.get(nid)
        if node is None:
            continue
        _draw_node(ax, node, cx, cy, node_width, node_height, patches_mod)

    fig.suptitle(f"Extended Matrix — {scene.title}",
                 fontsize=14, color="#1a2d4a", y=0.995)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.02)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = format.lower().lstrip(".")
    save_kwargs = dict(dpi=dpi, bbox_inches="tight", facecolor=background)
    if fmt in ("jpg", "jpeg"):
        plt.savefig(output_path, format="jpg", **save_kwargs)
    elif fmt == "svg":
        plt.savefig(output_path, format="svg",
                    bbox_inches="tight", facecolor=background)
    else:
        plt.savefig(output_path, format="png", **save_kwargs)
    plt.close(fig)
    return output_path
