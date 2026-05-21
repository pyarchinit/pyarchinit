"""Render a yEd GraphML file directly to PNG/JPEG via matplotlib.

This is the SECOND renderer path in the matrix-image pipeline (the
first being :mod:`matrix_swimlane_renderer`, which recomputes layout
from s3dgraphy JSON). This one is much simpler: it reads the node
positions and styles ALREADY computed by the s3dgraphy GraphML writer
(``modules.s3dgraphy.sync.graphml_writer.export_graphml``) and just
rasterises them — so the PNG looks identical to what yEd shows when
opening the same .graphml file.

Why two renderers? The swimlane renderer:
- works from the JSON (richer semantic info)
- can group/sort/wrap intelligently
- but has to MAKE UP a layout, which doesn't match the user's
  hand-tuned EM Matrix / yE-F group-folder layout.

The graphml renderer:
- works from the GraphML the pipeline already wrote
- uses the EXACT positions yEd would show
- draws all node types including paradata (Documents, Extractors,
  Properties, Combiners) — not just stratigraphic units
- ignores group folders' "fold" state — they're drawn as outlines

Public API:

    >>> render_graphml_to_png("/path/file.graphml",
    ...                       "/path/out.png", format="png")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from xml.etree import ElementTree as ET


_NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}


@dataclass
class _NodeBox:
    """Visual representation of one yEd node."""
    node_id: str
    label: str
    x: float          # yEd absolute X (top-left corner)
    y: float          # yEd absolute Y (top-left corner)
    width: float
    height: float
    fill: str         # #RRGGBB(AA)
    border: str
    border_width: float
    shape: str        # rectangle | ellipse | hexagon | octagon |
                      # parallelogram | roundrectangle | generic |
                      # svg | group
    is_group: bool = False
    text_color: str = "#000000"
    font_size: float = 10.0
    font_bold: bool = False


@dataclass
class _EdgeLine:
    source: str
    target: str
    relation: str = ""
    color: str = "#444444"
    width: float = 1.0
    style: str = "-"     # matplotlib linestyle


@dataclass
class _GraphmlScene:
    nodes: Dict[str, _NodeBox] = field(default_factory=dict)
    edges: List[_EdgeLine] = field(default_factory=list)
    title: str = ""


# -----------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------

def _strip_hex(c: str) -> str:
    if not c:
        return "#000000"
    c = c.strip()
    return c if c.startswith("#") else "#" + c


def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _parse_node_label(node_elem: ET.Element) -> Tuple[str, str, float, bool]:
    """Return (label_text, text_color, font_size, font_bold)."""
    label_elem = None
    for cand in node_elem.iter(f"{{{_NS['y']}}}NodeLabel"):
        if (cand.text or "").strip():
            label_elem = cand
            break
    if label_elem is None:
        return "", "#000000", 10.0, False
    text = (label_elem.text or "").strip()
    color = _strip_hex(label_elem.attrib.get("textColor", "#000000"))
    size = _safe_float(label_elem.attrib.get("fontSize", "10"), 10.0)
    bold = label_elem.attrib.get("fontStyle", "plain").lower() in ("bold", "boldItalic")
    return text, color, size, bold


def _parse_node_graphics(node_elem: ET.Element) -> Tuple[
    Optional[float], Optional[float], Optional[float], Optional[float],
    str, str, float, str, bool,
]:
    """Return (x, y, width, height, fill, border, border_width, shape, is_group).

    is_group is True for ProxyAutoBoundsNode / yEd group/folder nodes,
    which we render as outlined rectangles without fill.
    """
    folder_type = node_elem.attrib.get("yfiles.foldertype", "")
    is_group = folder_type in ("group", "folder")

    # GenericNode / ShapeNode / SVGNode / ImageNode / ProxyAutoBoundsNode
    graphic = None
    for tag in ("GenericNode", "ShapeNode", "SVGNode", "ImageNode",
                "GenericGroupNode", "ProxyAutoBoundsNode"):
        cand = node_elem.find(f".//{{{_NS['y']}}}{tag}")
        if cand is not None:
            graphic = cand
            break
    if graphic is None:
        return None, None, None, None, "#FFFFFF", "#000000", 1.0, "rectangle", is_group

    # ProxyAutoBoundsNode → look inside Realizers for the actual graphic
    if graphic.tag.endswith("ProxyAutoBoundsNode"):
        for tag in ("GroupNode", "GenericGroupNode", "ShapeNode", "GenericNode"):
            inner = graphic.find(f".//{{{_NS['y']}}}{tag}")
            if inner is not None:
                graphic = inner
                is_group = True
                break

    geom = graphic.find(f".//{{{_NS['y']}}}Geometry")
    x = _safe_float(geom.attrib.get("x")) if geom is not None else None
    y = _safe_float(geom.attrib.get("y")) if geom is not None else None
    w = _safe_float(geom.attrib.get("width"), 50.0) if geom is not None else 50.0
    h = _safe_float(geom.attrib.get("height"), 30.0) if geom is not None else 30.0

    fill_elem = graphic.find(f".//{{{_NS['y']}}}Fill")
    fill = _strip_hex(fill_elem.attrib.get("color", "#FFFFFF")) if fill_elem is not None else "#FFFFFF"

    border_elem = graphic.find(f".//{{{_NS['y']}}}BorderStyle")
    border = _strip_hex(border_elem.attrib.get("color", "#000000")) if border_elem is not None else "#000000"
    border_w = _safe_float(
        border_elem.attrib.get("width", "1") if border_elem is not None else "1", 1.0
    )

    shape = "generic"
    tag_local = graphic.tag.rsplit("}", 1)[-1]
    if tag_local == "ShapeNode":
        shape_elem = graphic.find(f"{{{_NS['y']}}}Shape")
        shape = (shape_elem.attrib.get("type") if shape_elem is not None
                 else "rectangle")
    elif tag_local in ("SVGNode", "ImageNode"):
        shape = "svg"
    elif is_group:
        shape = "group"
    else:
        shape = "generic"

    return x, y, w, h, fill, border, border_w, shape, is_group


def _parse_edge_style(edge_elem: ET.Element) -> Tuple[str, float, str, str]:
    """Return (color, width, linestyle, relation_hint)."""
    color = "#444444"
    width = 1.0
    linestyle = "-"
    # yEd <y:LineStyle color="..." type="line|dashed|dotted" width="..."/>
    for line_elem in edge_elem.iter(f"{{{_NS['y']}}}LineStyle"):
        color = _strip_hex(line_elem.attrib.get("color", "#444444"))
        width = _safe_float(line_elem.attrib.get("width", "1"), 1.0)
        ltype = line_elem.attrib.get("type", "line").lower()
        linestyle = {
            "line": "-",
            "dashed": "--",
            "dotted": ":",
            "dashed_dotted": "-.",
        }.get(ltype, "-")
        break
    # Relation hint from edge label (e.g. "overlies", "cuts")
    relation = ""
    for label_elem in edge_elem.iter(f"{{{_NS['y']}}}EdgeLabel"):
        if (label_elem.text or "").strip():
            relation = (label_elem.text or "").strip()
            break
    return color, width, linestyle, relation


def _parse_graphml(graphml_path: Path) -> _GraphmlScene:
    """Parse a GraphML file into a _GraphmlScene (positions + styles)."""
    tree = ET.parse(str(graphml_path))
    root = tree.getroot()
    scene = _GraphmlScene(title=graphml_path.stem)

    # ALL nodes (depth-first to also include nodes inside group nodes).
    for node_elem in root.iter(f"{{{_NS['g']}}}node"):
        node_id = node_elem.attrib.get("id")
        if not node_id:
            continue
        label, txt_color, font_size, font_bold = _parse_node_label(node_elem)
        x, y, w, h, fill, border, border_w, shape, is_group = _parse_node_graphics(node_elem)
        # Skip nodes without geometry (they're usually metadata / port placeholders).
        if x is None or y is None:
            continue
        scene.nodes[node_id] = _NodeBox(
            node_id=node_id,
            label=label,
            x=x, y=y, width=w, height=h,
            fill=fill, border=border, border_width=border_w,
            shape=shape, is_group=is_group,
            text_color=txt_color, font_size=font_size, font_bold=font_bold,
        )

    # Edges
    for edge_elem in root.iter(f"{{{_NS['g']}}}edge"):
        src = edge_elem.attrib.get("source")
        tgt = edge_elem.attrib.get("target")
        if not src or not tgt:
            continue
        color, width, linestyle, relation = _parse_edge_style(edge_elem)
        scene.edges.append(_EdgeLine(
            source=src, target=tgt, relation=relation,
            color=color, width=width, style=linestyle,
        ))

    return scene


# -----------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------

def _import_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import (Ellipse, FancyBboxPatch, Polygon,
                                    Rectangle, RegularPolygon)
    return plt, Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch


def _draw_shape(ax, node: _NodeBox, patches_mod):
    """Draw the shape patch for one node. yEd y-axis is INVERTED relative
    to matplotlib (positive y goes DOWN in yEd, UP in matplotlib), so the
    caller is expected to set ax.invert_yaxis() before drawing.
    """
    Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch = patches_mod
    cx = node.x + node.width / 2.0
    cy = node.y + node.height / 2.0
    fill = node.fill[:7] if len(node.fill) > 7 else node.fill  # strip alpha for mpl
    lw = max(0.4, min(node.border_width, 3.0))

    if node.is_group or node.shape == "group":
        # Group folder: outlined rectangle with NO fill (so children show).
        # Use a slightly transparent fill so the group is visible too.
        return ax.add_patch(Rectangle(
            (node.x, node.y), node.width, node.height,
            facecolor=fill if fill != "#FFFFFF" else "#f8f9fb",
            edgecolor=node.border,
            linewidth=lw,
            alpha=0.35,
            zorder=0,
        ))

    if node.shape == "ellipse":
        p = Ellipse((cx, cy), node.width, node.height,
                    facecolor=fill, edgecolor=node.border, linewidth=lw)
    elif node.shape == "parallelogram":
        skew = node.width * 0.18
        pts = [
            (node.x + skew, node.y),
            (node.x + node.width, node.y),
            (node.x + node.width - skew, node.y + node.height),
            (node.x, node.y + node.height),
        ]
        p = Polygon(pts, closed=True, facecolor=fill, edgecolor=node.border, linewidth=lw)
    elif node.shape == "hexagon":
        p = RegularPolygon((cx, cy), numVertices=6,
                           radius=max(node.width, node.height) / 1.8,
                           orientation=0,
                           facecolor=fill, edgecolor=node.border, linewidth=lw)
    elif node.shape == "octagon":
        p = RegularPolygon((cx, cy), numVertices=8,
                           radius=max(node.width, node.height) / 1.85,
                           orientation=0,
                           facecolor=fill, edgecolor=node.border, linewidth=lw)
    elif node.shape == "roundrectangle":
        p = FancyBboxPatch(
            (node.x, node.y), node.width, node.height,
            boxstyle="round,pad=0.02,rounding_size=6",
            facecolor=fill, edgecolor=node.border, linewidth=lw,
        )
    else:
        # rectangle / generic / svg fallback
        p = Rectangle((node.x, node.y), node.width, node.height,
                      facecolor=fill, edgecolor=node.border, linewidth=lw)
    return ax.add_patch(p)


def render_graphml_to_png(graphml_path: Union[str, Path],
                          output_path: Union[str, Path],
                          *,
                          format: str = "png",
                          dpi: int = 150,
                          padding_pct: float = 0.04,
                          background: str = "#fdfdfd") -> Path:
    """Render a yEd GraphML file to PNG / JPEG / SVG.

    Uses the positions and styles already baked into the file —
    visually equivalent to what yEd would display.
    """
    graphml_path = Path(graphml_path)
    output_path = Path(output_path)
    if not graphml_path.exists():
        raise FileNotFoundError(f"GraphML not found: {graphml_path}")

    scene = _parse_graphml(graphml_path)
    if not scene.nodes:
        raise ValueError(f"No drawable nodes in {graphml_path}")

    plt, Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch = _import_matplotlib()
    patches_mod = (Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch)

    # Compute bounding box in yEd coordinates.
    xs = [n.x for n in scene.nodes.values()]
    ys = [n.y for n in scene.nodes.values()]
    xe = [n.x + n.width for n in scene.nodes.values()]
    ye = [n.y + n.height for n in scene.nodes.values()]
    min_x, max_x = min(xs), max(xe)
    min_y, max_y = min(ys), max(ye)
    w_total = max_x - min_x
    h_total = max_y - min_y
    pad_x = max(w_total * padding_pct, 20.0)
    pad_y = max(h_total * padding_pct, 20.0)

    # Figure size: 1 inch per ~120 yEd units, clamped to sane bounds.
    fig_w_in = max(8.0, min(60.0, (w_total + 2 * pad_x) / 110.0))
    fig_h_in = max(5.0, min(60.0, (h_total + 2 * pad_y) / 110.0))
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in),
                           dpi=dpi, facecolor=background)
    ax.set_xlim(min_x - pad_x, max_x + pad_x)
    ax.set_ylim(min_y - pad_y, max_y + pad_y)
    ax.invert_yaxis()           # yEd: +y points DOWN
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # 1) Draw group/folder backgrounds FIRST (so children sit on top).
    group_nodes = [n for n in scene.nodes.values() if n.is_group]
    for g in sorted(group_nodes, key=lambda n: -(n.width * n.height)):
        _draw_shape(ax, g, patches_mod)
        # Group label at top-left
        if g.label:
            ax.text(g.x + 6, g.y + 14, g.label,
                    fontsize=max(8, g.font_size * 0.9),
                    color="#1a2d4a", fontweight="bold",
                    zorder=1)

    # 2) Draw edges (under nodes).
    for e in scene.edges:
        src = scene.nodes.get(e.source)
        tgt = scene.nodes.get(e.target)
        if src is None or tgt is None:
            continue
        x1 = src.x + src.width / 2.0
        y1 = src.y + src.height / 2.0
        x2 = tgt.x + tgt.width / 2.0
        y2 = tgt.y + tgt.height / 2.0
        ax.annotate(
            "",
            xy=(x2, y2), xycoords="data",
            xytext=(x1, y1), textcoords="data",
            arrowprops=dict(
                arrowstyle="->,head_width=0.18,head_length=0.28",
                color=e.color, linewidth=max(0.5, min(e.width, 2.5)),
                linestyle=e.style, alpha=0.7,
                shrinkA=4, shrinkB=4,
            ),
            zorder=2,
        )

    # 3) Draw non-group nodes (on top of edges + group backgrounds).
    for n in scene.nodes.values():
        if n.is_group:
            continue
        _draw_shape(ax, n, patches_mod)
        if n.label:
            ax.text(
                n.x + n.width / 2.0,
                n.y + n.height / 2.0,
                n.label,
                ha="center", va="center",
                fontsize=max(6, min(n.font_size, 11)),
                color=n.text_color,
                fontweight="bold" if n.font_bold else "normal",
                zorder=4,
            )

    # 4) Title (filename minus extension).
    fig.suptitle(f"Extended Matrix — {scene.title}",
                 fontsize=14, color="#1a2d4a", y=0.997)

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
