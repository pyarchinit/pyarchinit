"""Render a Harris-matrix swimlane diagram to PNG/JPEG via matplotlib.

This is the top-level orchestrator that ties together the three
upstream helpers built in tasks 1-3:

    s3d_json_loader  (graph data)
    em_palette_parser (visual style per node kind)
    harris_swimlane_layout  (node positions + row metadata)

Then it draws everything with matplotlib:

- One horizontal band per epoch (background = epoch color at low alpha)
- Period label on the left margin of each band
- Stratigraphic node patches at their (x, y) positions, with EM palette
  fill colour, border colour, and shape (rectangle/ellipse/parallelogram/
  hexagon/octagon/roundrectangle/generic-fallback-rectangle)
- Node name as text inside each patch
- Edges drawn as arrows between node centres, with relation-specific
  styles (solid for overlies/abuts, dashed for cuts, dotted for fills,
  double-line for equals)

Public API:

    >>> from modules.utility.matrix_swimlane_renderer import render_to_file
    >>> render_to_file(
    ...     json_path="/path/to/site.json",
    ...     output_path="/path/to/matrix.png",
    ...     group_by="area",
    ... )

or for already-loaded data:

    >>> render_swimlane(data, layout, palette, output_path="...", format="png")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from .em_palette_parser import Palette, PaletteStyle, default_palette_path, load_palette
from .harris_swimlane_layout import SwimlaneLayout, compute_layout
from .s3d_json_loader import S3DGraphData, load_s3d_json


# Map s3dgraphy stratigraphic kind → canonical palette sample label.
# The palette uses sample labels (USM01, USV100, etc.) but for the
# renderer we need a 1-to-1 mapping from semantic kind to the visual
# style that should represent it. Keep this small and explicit.
KIND_TO_PALETTE_LABEL = {
    "US":      "USM01",      # Standard archaeological US — rectangle
    "USM":     "USM01",      # Masonry stratigraphic — rectangle (red border)
    "USV":     "USV100",     # Generic virtual SU (truncated form) — parallelogram
    "USVs":    "USV100",     # Virtual structural — parallelogram
    "USVn":    "USV102",     # Virtual non-structural — hexagon
    "USD":     "USD10",      # Documentary stratigraphic — roundrect orange
    "SF":      "SF01",       # Special finding — octagon
    "VSF":     "VSF01",      # Virtual special finding — octagon dark
    "TSU":     "TSU",        # Time Stratigraphic Unit — roundrect
    "RSF":     "RSF01",      # Reused special finding (spolia)
    "serSU":   "USM01",      # Serialised SU — fallback to rectangle
    "serUSVn": "USV102",     # Serialised non-struct virtual
    "serUSVs": "USV100",     # Serialised struct virtual
    "SE":      "USM01",      # Stratigraphic Element — generic rectangle
    "unknown": "USM01",      # Unknown stratigraphic — fallback rectangle
    # Paradata kinds (mostly drawn as overlays, not main nodes)
    "property":  "property",
    "document":  "D.",
    "combiner":  "C.",
    "extractor": "D.",
}


# Per-relation edge styling. Maps s3dgraphy edge_type to a matplotlib
# linestyle + arrow style. Values not in this table fall back to a
# solid thin grey line so the layout still shows the topology.
EDGE_STYLES = {
    "overlies":       {"linestyle": "-",  "color": "#222222", "linewidth": 1.2, "alpha": 0.85},
    "covers":         {"linestyle": "-",  "color": "#222222", "linewidth": 1.2, "alpha": 0.85},
    "cuts":           {"linestyle": "--", "color": "#9B3333", "linewidth": 1.5, "alpha": 0.95},
    "fills":          {"linestyle": ":",  "color": "#1f4e8a", "linewidth": 1.5, "alpha": 0.85},
    "abuts":          {"linestyle": "-.", "color": "#666666", "linewidth": 1.1, "alpha": 0.80},
    "is_bonded_to":   {"linestyle": "-",  "color": "#31792D", "linewidth": 1.5, "alpha": 0.85},
    "equals":         {"linestyle": "-",  "color": "#1a2d4a", "linewidth": 2.5, "alpha": 0.90},
}
DEFAULT_EDGE_STYLE = {"linestyle": "-", "color": "#999999", "linewidth": 0.7, "alpha": 0.55}


@dataclass
class RenderConfig:
    """Visual knobs the caller may want to tweak."""
    figure_dpi: int = 150
    node_width_pts: float = 0.85           # logical units of node visible width within its 1.0 slot
    node_height_pts: float = 0.55          # logical units of node visible height within its 1.0 row
    node_fontsize: float = 8.0
    row_label_fontsize: float = 11.0
    row_label_pad: float = 0.3             # extra logical units to the left for row labels
    show_edges: bool = True
    show_period_bands: bool = True
    period_band_alpha: float = 0.18
    background_color: str = "#fdfdfd"
    title: Optional[str] = None
    title_fontsize: float = 14.0


def _import_matplotlib():
    """Lazy import so this module loads cleanly outside QGIS even if
    matplotlib isn't on sys.path (the early failure happens in
    render_swimlane, not at module import time)."""
    import matplotlib
    matplotlib.use("Agg")  # headless backend, safe in QGIS + CLI
    import matplotlib.pyplot as plt
    from matplotlib.patches import (Ellipse, FancyBboxPatch, Polygon,
                                    Rectangle, RegularPolygon)
    return plt, Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch


def _draw_node_patch(ax, x: float, y: float, style: PaletteStyle,
                     w: float, h: float, patches_mod):
    """Draw the EM-styled shape for a single node centered at (x, y).

    ``w`` and ``h`` are the desired patch width/height in logical units
    (NOT the style.width/height which are yEd template units). Returns
    the matplotlib Patch so the caller can also add a label.
    """
    Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch = patches_mod
    fill = style.fill if len(style.fill) <= 7 else style.fill[:7]  # drop alpha for matplotlib
    edge = style.border
    lw = max(0.6, style.border_width)

    shape = style.shape
    if shape == "ellipse":
        patch = Ellipse((x, y), w, h, facecolor=fill, edgecolor=edge, linewidth=lw)
    elif shape == "parallelogram":
        skew = w * 0.18
        pts = [(x - w/2 + skew, y - h/2), (x + w/2, y - h/2),
               (x + w/2 - skew, y + h/2), (x - w/2, y + h/2)]
        patch = Polygon(pts, closed=True, facecolor=fill, edgecolor=edge, linewidth=lw)
    elif shape == "hexagon":
        patch = RegularPolygon((x, y), numVertices=6, radius=h/1.7, orientation=0,
                                facecolor=fill, edgecolor=edge, linewidth=lw)
    elif shape == "octagon":
        patch = RegularPolygon((x, y), numVertices=8, radius=h/1.85, orientation=0,
                                facecolor=fill, edgecolor=edge, linewidth=lw)
    elif shape == "roundrectangle":
        patch = FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=fill, edgecolor=edge, linewidth=lw,
        )
    elif shape == "rectangle" or shape == "generic" or shape == "svg":
        patch = Rectangle((x - w/2, y - h/2), w, h,
                          facecolor=fill, edgecolor=edge, linewidth=lw)
    else:
        # Unknown shape → neutral rectangle
        patch = Rectangle((x - w/2, y - h/2), w, h,
                          facecolor=fill, edgecolor=edge, linewidth=lw)
    ax.add_patch(patch)
    return patch


def _node_label_text(name: str, max_chars: int = 14) -> str:
    """Truncate long node labels to keep the box readable."""
    name = (name or "").strip()
    if len(name) <= max_chars:
        return name
    return name[:max_chars - 1] + "…"


def _readable_text_color(fill_hex: str) -> str:
    """Pick white or black text depending on the fill's luminance.

    Uses the WCAG-style relative luminance approximation: a fill with
    luminance < 0.5 (rough mid-grey threshold) gets white text;
    otherwise black. Strips alpha from RRGGBBAA inputs.
    """
    if not fill_hex or not fill_hex.startswith("#"):
        return "#000000"
    hex_part = fill_hex[1:7]  # drop '#' and any alpha
    if len(hex_part) < 6:
        return "#000000"
    try:
        r = int(hex_part[0:2], 16) / 255.0
        g = int(hex_part[2:4], 16) / 255.0
        b = int(hex_part[4:6], 16) / 255.0
    except ValueError:
        return "#000000"
    # Quick perceptual luminance (sRGB → linear approximation):
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#ffffff" if lum < 0.5 else "#000000"


def render_swimlane(data: S3DGraphData,
                    layout: SwimlaneLayout,
                    palette: Palette,
                    output_path: Union[str, Path],
                    format: str = "png",
                    config: Optional[RenderConfig] = None) -> Path:
    """Render the swimlane matrix to ``output_path``.

    :param format: ``"png"`` (default) or ``"jpeg"`` / ``"jpg"`` or ``"svg"``.
    :returns: the output path as a :class:`Path`.
    """
    if config is None:
        config = RenderConfig()

    plt, Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch = _import_matplotlib()
    patches_mod = (Rectangle, Ellipse, Polygon, RegularPolygon, FancyBboxPatch)

    if not layout.positions:
        raise ValueError("Layout has no positions — nothing to render. "
                         "Was the stratigraphic bucket empty?")

    # --- Figure size: tight to content, no excessive white space.
    width_lu = layout.max_row_width + config.row_label_pad + 1.0  # +1 for right margin
    height_lu = len(layout.rows) * 1.0 + 0.2                       # tight top margin (no title overflow)
    fig_w_in = max(8.0, min(40.0, width_lu * 0.7))
    fig_h_in = max(3.0, min(40.0, height_lu * 0.75))
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in),
                           dpi=config.figure_dpi,
                           facecolor=config.background_color)

    # X spans [-row_label_pad, max_row_width + 0.5]; Y spans [0, num_rows].
    ax.set_xlim(-config.row_label_pad - 0.3, layout.max_row_width + 0.5)
    ax.set_ylim(-0.1, len(layout.rows) + 0.1)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # --- Period bands (one per row) ---
    if config.show_period_bands:
        for row in layout.rows:
            color = row.epoch_color or "#cccccc"
            band = Rectangle(
                (-config.row_label_pad - 0.3, row.y_bottom),
                layout.max_row_width + config.row_label_pad + 0.8,
                row.y_top - row.y_bottom,
                facecolor=color,
                edgecolor=color,
                alpha=config.period_band_alpha,
                zorder=0,
            )
            ax.add_patch(band)
            # Thin horizontal divider on top of each band
            ax.plot(
                [-config.row_label_pad - 0.3, layout.max_row_width + 0.5],
                [row.y_top, row.y_top],
                color="#888888", linewidth=0.4, alpha=0.6, zorder=1,
            )

    # --- Row labels (left margin) ---
    for row in layout.rows:
        label = row.label
        if row.start_time is not None and row.end_time is not None:
            label = f"{label}\n({_fmt_year(row.start_time)} → {_fmt_year(row.end_time)})"
        ax.text(
            -config.row_label_pad, row.y_center,
            label,
            ha="right", va="center",
            fontsize=config.row_label_fontsize,
            fontweight="bold",
            color="#1a2d4a",
            zorder=3,
        )

    # --- Edges (under nodes) ---
    if config.show_edges:
        for src, tgt, edge_attrs in data.networkx.edges(data=True):
            if src not in layout.positions or tgt not in layout.positions:
                # Skip edges that touch non-stratigraphic nodes (properties,
                # epochs, paradata) — those aren't in the swimlane.
                continue
            relation = edge_attrs.get("relation", "")
            style = EDGE_STYLES.get(relation, DEFAULT_EDGE_STYLE)
            x1, y1 = layout.positions[src]
            x2, y2 = layout.positions[tgt]
            ax.annotate(
                "",
                xy=(x2, y2), xycoords="data",
                xytext=(x1, y1), textcoords="data",
                arrowprops=dict(
                    arrowstyle="->,head_width=0.5,head_length=0.7",
                    linestyle=style["linestyle"],
                    color=style["color"],
                    linewidth=max(0.9, style["linewidth"]),
                    alpha=style["alpha"],
                    shrinkA=8, shrinkB=8,  # don't touch node borders
                ),
                zorder=2,
            )

    # --- Nodes ---
    w = config.node_width_pts
    h = config.node_height_pts
    for node_id, (x, y) in layout.positions.items():
        attrs = data.networkx.nodes[node_id]
        kind = attrs.get("kind") or ""
        palette_label = KIND_TO_PALETTE_LABEL.get(kind, kind)
        style = palette.get(palette_label)
        _draw_node_patch(ax, x, y, style, w, h, patches_mod)
        # Auto-pick white or black text depending on fill luminance —
        # USV / VSF have black fills, default black text was invisible.
        text_color = _readable_text_color(style.fill)
        ax.text(
            x, y,
            _node_label_text(attrs.get("name") or node_id),
            ha="center", va="center",
            fontsize=config.node_fontsize,
            color=text_color,
            zorder=4,
            wrap=True,
        )

    # --- Title (inline, low overhead) ---
    title = config.title or (data.name and f"Matrix Harris — {data.name}")
    if title:
        # Place title close to top edge to avoid white-space gap.
        fig.suptitle(title, fontsize=config.title_fontsize,
                     color="#1a2d4a", y=0.985)
    # Tighter padding so the matrix doesn't float in white.
    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)

    # --- Save ---
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = format.lower().lstrip(".")
    if fmt in ("jpg", "jpeg"):
        plt.savefig(output_path, format="jpg", dpi=config.figure_dpi,
                    bbox_inches="tight", facecolor=config.background_color)
    elif fmt == "svg":
        plt.savefig(output_path, format="svg", bbox_inches="tight",
                    facecolor=config.background_color)
    else:
        plt.savefig(output_path, format="png", dpi=config.figure_dpi,
                    bbox_inches="tight", facecolor=config.background_color)
    plt.close(fig)
    return output_path


def _fmt_year(year: float) -> str:
    """Format a numeric year as 'BC' / 'AD' string."""
    y = int(year)
    if y < 0:
        return f"{-y} a.C."
    return f"{y} d.C."


def render_to_file(json_path: Union[str, Path],
                   output_path: Union[str, Path],
                   *,
                   format: str = "png",
                   group_by: Optional[str] = None,
                   palette_path: Optional[Union[str, Path]] = None,
                   graph_id: Optional[str] = None,
                   config: Optional[RenderConfig] = None) -> Path:
    """One-shot convenience: parse JSON + palette, compute layout, render.

    Used by the QGIS plugin and the CLI smoke tests. Returns the output
    path so callers can confirm where the file landed.
    """
    data = load_s3d_json(json_path, graph_id=graph_id)
    layout = compute_layout(data, group_by=group_by)
    palette = load_palette(palette_path or default_palette_path())
    return render_swimlane(data, layout, palette, output_path,
                            format=format, config=config)
