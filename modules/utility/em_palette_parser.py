"""Parse EM_palette.graphml (yEd format) into a flat per-label style dict.

The Extended Matrix (EM) palette is the canonical visual reference for
archaeological stratigraphic unit types in pyArchInit / s3dgraphy.
This module reads the yEd GraphML palette file and produces a Python
dict keyed by the node label text (visible in yEd: e.g. "USM01", "D.",
"USV100", "property", "epoch") rather than by the d3 UUID (which is
opaque). The renderer (matrix_swimlane_renderer) looks up each
s3dgraphy node's kind in this dict to find the fill colour, border,
shape, and geometry to draw with.

Public API:

    >>> palette = load_palette("/Users/.../EM_palette.graphml")
    >>> palette.styles["USM01"]
    PaletteStyle(label='USM01', fill='#E6BFE6', border='#000000',
                 border_width=1.0, shape='parallelogram', width=60.0,
                 height=30.0)

When a node kind is not present, callers should use
``palette.fallback`` (a neutral grey rectangle) instead of crashing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Union
from xml.etree import ElementTree as ET


# yEd / GraphML namespace map (yEd uses these prefixes consistently)
_NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}


@dataclass
class PaletteStyle:
    """Visual properties for one EM palette node kind."""
    label: str
    fill: str = "#FFFFFF"          # hex RGB or RGBA (yEd uses RRGGBB or RRGGBBAA)
    border: str = "#000000"
    border_width: float = 1.0
    shape: str = "rectangle"       # rectangle | ellipse | parallelogram | hexagon |
                                   # octagon | roundrectangle | generic | svg
    width: float = 50.0
    height: float = 30.0
    description: str = ""          # palette tooltip / d6 description


@dataclass
class Palette:
    """A loaded EM palette: a dict of styles by label + a fallback."""
    styles: Dict[str, PaletteStyle] = field(default_factory=dict)
    fallback: PaletteStyle = field(default_factory=lambda: PaletteStyle(
        label="__fallback__",
        fill="#EEEEEE",
        border="#999999",
        border_width=1.0,
        shape="rectangle",
        width=50.0,
        height=30.0,
    ))

    def get(self, label: str) -> PaletteStyle:
        """Lookup a style by label with case-insensitive fallback to neutral."""
        if label in self.styles:
            return self.styles[label]
        # Case-insensitive second chance (USM vs usm)
        upper = label.upper()
        for k, v in self.styles.items():
            if k.upper() == upper:
                return v
        return self.fallback

    def __contains__(self, label: str) -> bool:
        return label in self.styles


def _strip_hex_alpha(color: str) -> str:
    """Normalise yEd colour strings.

    yEd writes both ``#RRGGBB`` and ``#RRGGBBAA``. Matplotlib accepts both
    when prefixed with ``#``, but we strip the alpha channel for the
    border (where alpha makes no visual sense) and keep it on the fill
    (where translucent overlays are sometimes desired). Returned strings
    always start with ``#``.
    """
    if not color:
        return "#000000"
    color = color.strip()
    if not color.startswith("#"):
        color = "#" + color
    return color


def _extract_node_label(node_elem: ET.Element) -> str:
    """Return the visible label text of the first <y:NodeLabel> with text.

    Falls back to an empty string if none is present (which happens for
    purely graphical palette entries like the ellipse separator).
    """
    for label_elem in node_elem.iter(f"{{{_NS['y']}}}NodeLabel"):
        text = (label_elem.text or "").strip()
        if text:
            return text
    return ""


def _extract_geometry(graphic_elem: ET.Element) -> tuple[float, float]:
    """Extract (width, height) from the first <y:Geometry> child."""
    geom = graphic_elem.find(f".//{{{_NS['y']}}}Geometry")
    if geom is None:
        return 50.0, 30.0
    try:
        w = float(geom.attrib.get("width", "50"))
        h = float(geom.attrib.get("height", "30"))
        return w, h
    except (TypeError, ValueError):
        return 50.0, 30.0


def _extract_fill_border(graphic_elem: ET.Element) -> tuple[str, str, float]:
    """Extract (fill_color, border_color, border_width) from a yEd graphic."""
    fill_elem = graphic_elem.find(f".//{{{_NS['y']}}}Fill")
    border_elem = graphic_elem.find(f".//{{{_NS['y']}}}BorderStyle")
    fill = _strip_hex_alpha(fill_elem.attrib.get("color", "#FFFFFF")) if fill_elem is not None else "#FFFFFF"
    border = _strip_hex_alpha(border_elem.attrib.get("color", "#000000")) if border_elem is not None else "#000000"
    try:
        width = float(border_elem.attrib.get("width", "1.0")) if border_elem is not None else 1.0
    except (TypeError, ValueError):
        width = 1.0
    return fill, border, width


def _extract_shape(graphic_elem: ET.Element) -> str:
    """Return the shape kind. For <y:ShapeNode> the shape type is explicit;
    for <y:GenericNode> we use 'generic'; for <y:SVGNode> we use 'svg'."""
    tag_local = graphic_elem.tag.rsplit("}", 1)[-1]
    if tag_local == "ShapeNode":
        shape_elem = graphic_elem.find(f"{{{_NS['y']}}}Shape")
        if shape_elem is not None:
            return shape_elem.attrib.get("type", "rectangle")
        return "rectangle"
    if tag_local == "SVGNode":
        return "svg"
    return "generic"  # GenericNode + anything else falls back to generic


def _extract_description(node_elem: ET.Element) -> str:
    """Extract the palette tooltip / description (d6 key)."""
    for data_elem in node_elem.findall(f"{{{_NS['g']}}}data"):
        key = data_elem.attrib.get("key", "")
        # In EM_palette.graphml d6 is the description key (assigned by yEd).
        # We don't hard-code 'd6' because some palettes rename the key id,
        # but the attr.name on the <key> declaration is always 'description'.
        if key == "d6":
            text = (data_elem.text or "").strip()
            if text.startswith("<![CDATA["):
                text = text[9:-3]
            return text
    return ""


def load_palette(graphml_path: Union[str, Path]) -> Palette:
    """Parse a yEd EM palette GraphML file into a :class:`Palette`.

    Empty-label nodes (graphical separators / unlabelled samples) are
    skipped. Duplicate labels keep the FIRST style encountered (yEd
    palettes have no enforced uniqueness, but typical EM palettes
    declare one entry per kind).
    """
    path = Path(graphml_path)
    if not path.exists():
        raise FileNotFoundError(f"EM palette not found: {path}")

    tree = ET.parse(str(path))
    root = tree.getroot()
    palette = Palette()

    for node_elem in root.iter(f"{{{_NS['g']}}}node"):
        label = _extract_node_label(node_elem)
        if not label or label in palette.styles:
            # Skip nameless or duplicate entries.
            continue
        # Find the graphic element (one of GenericNode / ShapeNode / SVGNode)
        graphic = None
        for tag in ("GenericNode", "ShapeNode", "SVGNode"):
            cand = node_elem.find(f".//{{{_NS['y']}}}{tag}")
            if cand is not None:
                graphic = cand
                break
        if graphic is None:
            continue
        fill, border, border_w = _extract_fill_border(graphic)
        width, height = _extract_geometry(graphic)
        shape = _extract_shape(graphic)
        description = _extract_description(node_elem)
        palette.styles[label] = PaletteStyle(
            label=label,
            fill=fill,
            border=border,
            border_width=border_w,
            shape=shape,
            width=width,
            height=height,
            description=description,
        )
    return palette


def default_palette_path() -> Path:
    """Resolve the EM palette template path.

    **Authoritative source**: the palette template SHIPPED with the
    s3dgraphy package (``ext_libs/s3dgraphy/templates/em_palette_template
    .graphml``). When s3dgraphy is updated (``pip install -U s3dgraphy``),
    the palette refreshes automatically — no code changes needed here.

    Uses :func:`importlib.util.find_spec` to LOCATE the package without
    executing its ``__init__.py``. The eager ``import s3dgraphy`` chain
    pulls in pandas/numpy/SQLAlchemy via the importer subpackage — a
    waste of import time when all we need is a static path.

    Fallback: legacy ``~/pyarchinit/bin/EM_palette.graphml`` (pre-1.5.0
    layout). Used only if find_spec returns None (s3dgraphy not on
    ``sys.path`` — never the case in a QGIS plugin environment).
    """
    try:
        from importlib.util import find_spec
        spec = find_spec("s3dgraphy")
        if spec is not None and spec.submodule_search_locations:
            pkg_dir = Path(next(iter(spec.submodule_search_locations)))
            path = pkg_dir / "templates" / "em_palette_template.graphml"
            if path.exists():
                return path
    except Exception:
        pass
    # Legacy fallback (pre-s3dgraphy-1.5.0 layout).
    import os
    home = os.environ.get("PYARCHINIT_HOME") or str(Path.home() / "pyarchinit")
    return Path(home) / "bin" / "EM_palette.graphml"
