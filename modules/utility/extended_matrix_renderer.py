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
    """Walk the graphml and extract nodes / groups / edges."""
    tree = ET.parse(str(graphml_path))
    root = tree.getroot()
    scene = _Scene(title=graphml_path.stem)

    def _walk(parent_node: Optional[ET.Element], parent_group_id: Optional[str]):
        """Recurse into <graph> children under parent_node."""
        for graph in parent_node.findall(f"{{{_NS['g']}}}graph"):
            for n in graph.findall(f"{{{_NS['g']}}}node"):
                node_id = n.attrib.get("id", "")
                if not node_id:
                    continue
                label = _extract_label(n)
                is_group = n.attrib.get("yfiles.foldertype") in ("group", "folder")
                if is_group:
                    g = _GroupFolder(group_id=node_id, label=label)
                    scene.groups[node_id] = g
                    # Recurse into the group's nested <graph>
                    _walk(n, node_id)
                    # member_ids will be filled after the walk completes
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
    # Top-level nodes
    for n in top_graph.findall(f"{{{_NS['g']}}}node"):
        node_id = n.attrib.get("id", "")
        if not node_id:
            continue
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

    # Edges (top-level)
    for e in root.iter(f"{{{_NS['g']}}}edge"):
        src = e.attrib.get("source", "")
        tgt = e.attrib.get("target", "")
        if src and tgt:
            scene.edges.append(_Edge(src, tgt))

    return scene


# ----------------------------------------------------------------------
# Layout: layered per group + vertical stack
# ----------------------------------------------------------------------

def _topological_layers(member_ids: List[str], edges: List[_Edge],
                        member_set: Optional[set] = None) -> List[List[str]]:
    """Return ordered list of layers (roots first, leaves last).

    Uses SCC condensation to handle reciprocal edge cycles. Within
    each layer, nodes are returned in insertion order.
    """
    if not member_ids:
        return []
    try:
        import networkx as nx
    except ImportError:
        # Fall back: one layer with everything.
        return [list(member_ids)]

    mset = member_set if member_set is not None else set(member_ids)
    sub = nx.DiGraph()
    sub.add_nodes_from(member_ids)
    for e in edges:
        if e.source in mset and e.target in mset and e.source != e.target:
            sub.add_edge(e.source, e.target)

    if sub.number_of_edges() == 0:
        return [list(member_ids)]

    cond = nx.condensation(sub)
    members_attr = nx.get_node_attributes(cond, "members")

    if cond.number_of_edges() == 0:
        # Disconnected SCCs → one per layer, smaller first (top).
        sccs = [(scc_idx, members_attr.get(scc_idx, set()))
                for scc_idx in cond.nodes]
        sccs.sort(key=lambda kv: len(kv[1]))
        return [sorted(s) for _, s in sccs if s]

    out = []
    for gen in nx.topological_generations(cond):
        layer = []
        for scc_idx in gen:
            layer.extend(sorted(members_attr.get(scc_idx, set())))
        if layer:
            out.append(layer)
    return out


@dataclass
class _GroupLayout:
    group_id: str
    label: str
    layers: List[List[str]] = field(default_factory=list)
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
        layers = _topological_layers(g.member_ids, scene.edges, member_set)
        if not layers:
            continue
        max_w_cells = max(len(L) for L in layers)
        gl = _GroupLayout(
            group_id=g.group_id, label=g.label, layers=layers,
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

    # 2) Edges (under nodes)
    pos = positions
    for e in scene.edges:
        if e.source not in pos or e.target not in pos:
            continue
        x1, y1 = pos[e.source]
        x2, y2 = pos[e.target]
        ax.annotate(
            "",
            xy=(x2, y2), xycoords="data",
            xytext=(x1, y1), textcoords="data",
            arrowprops=dict(
                arrowstyle="->,head_width=0.4,head_length=0.6",
                color="#3a4d5c", linewidth=0.8, alpha=0.6,
                shrinkA=node_height * 0.55, shrinkB=node_height * 0.55,
            ),
            zorder=2,
        )

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
