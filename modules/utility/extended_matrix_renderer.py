"""Render an Extended Matrix GraphML to PNG via Graphviz `dot`.

This is the THIRD-generation renderer (the first two — matrix_swimlane
and graphml_to_png — are kept as fallbacks). The matplotlib-based
Sugiyama implementation was rejected by the user as not faithful
enough to the yEd Swimlane Layout output. This implementation hands
the hard work off to Graphviz's `dot` binary, which is the standard
tool for hierarchical+orthogonal graph layout:

- Per-group ``subgraph cluster_X`` blocks → automatic group folders
  drawn as sage-green containers, sized to their content.
- ``splines=ortho`` → real Manhattan edges with right-angle bends.
- ``rankdir=TB`` → top-to-bottom hierarchy (parents above children).
- 2-D cluster bin-packing → small groups (VA04, VA06) can sit
  side-by-side with the bigger ones (VA05).
- Transitive edges are kept short and clean via dot's longest-path
  layering.

Per-node fill/border/shape are extracted from the yEd graphml graphics
and translated to DOT attributes so the EM palette appearance is
preserved without needing a separate palette parser at render time.

Per-edge styles (color / linestyle / penwidth) come from the
``pyarchinit.rapporti`` field on each source node (Copre/Taglia/...).

Public API:

    >>> render_extended_matrix("/path/file.graphml",
    ...                        "/path/out.png", format="png")

If `dot` is not installed (or fails), the function raises
RuntimeError — the caller in s3dgraphy_dot_bridge handles the
fallback to the matplotlib-based flat swimlane renderer.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from xml.etree import ElementTree as ET


_NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}


# yEd shape → Graphviz shape mapping.
# Graphviz natively supports box / ellipse / hexagon / octagon /
# parallelogram. roundrectangle becomes box+rounded.
_YED_TO_GV_SHAPE = {
    "rectangle":      "box",
    "ellipse":        "ellipse",
    "hexagon":        "hexagon",
    "octagon":        "octagon",
    "parallelogram":  "parallelogram",
    "roundrectangle": "box",          # + style="rounded"
    "generic":        "box",
    "svg":            "box",
    "group":          "box",
}


# EM relation vocabulary → DOT edge styling.
# Convention (EM standard):
#   - Stratigraphic positive (Copre/Coperto da, Riempie/Riempito da,
#     Si appoggia/Gli si appoggia) → solid black arrowed line
#   - Stratigraphic NEGATIVE (Taglia/Tagliato da) → RED DASHED line
#     with arrow (cuts are destructive relations).
#   - Continuity (Uguale a, Si lega a) → black DOUBLE line, NO arrows,
#     same rank (units are at the same stratigraphic level / time).
#   - Paradata (DOC/Combiner/Extractor/property → US via << / >>) →
#     grey DASHED line (these aren't stratigraphic relations, they're
#     documentation/inference links).
_REL_DOT_STYLES = {
    "Copre":           {"color": "#1a2d4a", "penwidth": 1.2, "style": "solid",
                        "arrowhead": "normal"},
    "Coperto da":      {"color": "#1a2d4a", "penwidth": 1.2, "style": "solid",
                        "arrowhead": "normal"},
    # NEGATIVE: red dashed with arrow.
    "Taglia":          {"color": "#C0392B", "penwidth": 1.3, "style": "dashed",
                        "arrowhead": "normal"},
    "Tagliato da":     {"color": "#C0392B", "penwidth": 1.3, "style": "dashed",
                        "arrowhead": "normal"},
    "Riempie":         {"color": "#1f4e8a", "penwidth": 1.2, "style": "solid",
                        "arrowhead": "normal"},
    "Riempito da":     {"color": "#1f4e8a", "penwidth": 1.2, "style": "solid",
                        "arrowhead": "normal"},
    "Si appoggia a":   {"color": "#1a2d4a", "penwidth": 1.0, "style": "solid",
                        "arrowhead": "normal"},
    "Gli si appoggia": {"color": "#1a2d4a", "penwidth": 1.0, "style": "solid",
                        "arrowhead": "normal"},
    # CONTINUITY: double black line, no arrows, same rank (horizontal).
    "Si lega a":       {"color": "#1a2d4a", "penwidth": 1.0, "style": "solid",
                        "arrowhead": "none", "double": True, "samerank": True},
    "Uguale a":        {"color": "#1a2d4a", "penwidth": 1.0, "style": "solid",
                        "arrowhead": "none", "double": True, "samerank": True},
    # PARADATA membership / inference: dashed grey, with normal arrow.
    ">>":              {"color": "#7a8a99", "penwidth": 0.7, "style": "dashed",
                        "arrowhead": "normal"},
    "<<":              {"color": "#7a8a99", "penwidth": 0.7, "style": "dashed",
                        "arrowhead": "normal"},
}
_REL_DOT_DEFAULT = {"color": "#3a4d5c", "penwidth": 0.8, "style": "solid",
                    "arrowhead": "normal"}

# Relations that should be REVERSED when reading from rapporti so the
# edge points from parent → child consistently in the DAG.
_REVERSED_RELATIONS = {"<<", "Coperto da", "Tagliato da",
                       "Riempito da", "Gli si appoggia"}

# Symmetric relations: should be drawn only ONCE per (A, B) unordered
# pair, never two arrows for A→B and B→A.
_SYMMETRIC_RELATIONS = {"Uguale a", "Si lega a"}


# ----------------------------------------------------------------------
# DOT binary discovery
# ----------------------------------------------------------------------

def _find_dot_binary() -> Optional[str]:
    """Locate the Graphviz ``dot`` binary.

    Checks (in order):
    1. ``which dot`` (PATH)
    2. Standard Homebrew/Linux/macOS locations: ``/opt/homebrew/bin/dot``,
       ``/usr/local/bin/dot``, ``/usr/bin/dot``.

    Returns the absolute path, or None if dot isn't installed.
    """
    found = shutil.which("dot")
    if found:
        return found
    for candidate in ("/opt/homebrew/bin/dot",
                      "/usr/local/bin/dot",
                      "/usr/bin/dot"):
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


# ----------------------------------------------------------------------
# GraphML parsing
# ----------------------------------------------------------------------

@dataclass
class _NodeData:
    node_id: str
    label: str
    fill: str = "#FFFFFF"
    border: str = "#000000"
    border_width: float = 1.0
    shape: str = "box"          # already in DOT vocabulary
    rounded: bool = False       # True for roundrectangle yEd nodes
    text_color: str = "#000000"
    group_id: Optional[str] = None


@dataclass
class _GroupData:
    group_id: str
    label: str
    member_ids: List[str] = field(default_factory=list)


@dataclass
class _EdgeData:
    source: str
    target: str
    relation: str = ""


@dataclass
class _Scene:
    nodes: Dict[str, _NodeData] = field(default_factory=dict)
    groups: Dict[str, _GroupData] = field(default_factory=dict)
    edges: List[_EdgeData] = field(default_factory=list)
    title: str = ""


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


def _extract_label(n_elem: ET.Element) -> str:
    for lbl in n_elem.iter(f"{{{_NS['y']}}}NodeLabel"):
        if (lbl.text or "").strip():
            return (lbl.text or "").strip()
    return ""


def _extract_style(n_elem: ET.Element) -> Tuple[str, str, float, str, bool]:
    """Return (fill, border, border_width, dot_shape, rounded)."""
    graphic = None
    for tag in ("GenericNode", "ShapeNode", "SVGNode", "ImageNode",
                "GenericGroupNode", "GroupNode", "ProxyAutoBoundsNode"):
        cand = n_elem.find(f".//{{{_NS['y']}}}{tag}")
        if cand is not None:
            graphic = cand
            break
    if graphic is None:
        return "#FFFFFF", "#000000", 1.0, "box", False

    if graphic.tag.endswith("ProxyAutoBoundsNode"):
        for tag in ("GroupNode", "GenericGroupNode", "ShapeNode", "GenericNode"):
            inner = graphic.find(f".//{{{_NS['y']}}}{tag}")
            if inner is not None:
                graphic = inner
                break

    fill_elem = graphic.find(f".//{{{_NS['y']}}}Fill")
    fill = _strip_hex(fill_elem.attrib.get("color", "#FFFFFF"))[:7] \
        if fill_elem is not None else "#FFFFFF"

    border_elem = graphic.find(f".//{{{_NS['y']}}}BorderStyle")
    border = _strip_hex(border_elem.attrib.get("color", "#000000"))[:7] \
        if border_elem is not None else "#000000"
    border_w = _safe_float(border_elem.attrib.get("width", "1"), 1.0) \
        if border_elem is not None else 1.0

    yed_shape = "rectangle"
    tag_local = graphic.tag.rsplit("}", 1)[-1]
    if tag_local == "ShapeNode":
        shape_elem = graphic.find(f"{{{_NS['y']}}}Shape")
        if shape_elem is not None:
            yed_shape = shape_elem.attrib.get("type", "rectangle")
    elif tag_local in ("SVGNode", "ImageNode"):
        yed_shape = "svg"
    else:
        yed_shape = "generic"

    rounded = (yed_shape == "roundrectangle")
    dot_shape = _YED_TO_GV_SHAPE.get(yed_shape, "box")
    return fill, border, border_w, dot_shape, rounded


def _resolve_data_keys(root: ET.Element) -> Dict[str, str]:
    """Build {attr_name: key_id} from the graphml <key> declarations.

    Different exports use different key id numbering (d0..d37 etc.)
    depending on which optional schema fields are emitted. Hard-coding
    id strings like 'd15' breaks silently when the order changes. This
    helper resolves the stable attr.name (e.g. 'pyarchinit.rapporti')
    to whatever id was assigned in THIS file.
    """
    out: Dict[str, str] = {}
    for k in root.iter(f"{{{_NS['g']}}}key"):
        name = k.attrib.get("attr.name")
        kid = k.attrib.get("id")
        if name and kid:
            out[name] = kid
    return out


def _parse_graphml(graphml_path: Path) -> _Scene:
    """Walk the graphml and build a _Scene."""
    tree = ET.parse(str(graphml_path))
    root = tree.getroot()
    scene = _Scene(title=graphml_path.stem)
    raw_data: Dict[str, Dict[str, str]] = {}

    # Resolve data-key ids from declarations (NOT hardcoded — varies
    # between exports based on optional field presence).
    name_to_key = _resolve_data_keys(root)
    K_US        = name_to_key.get("pyarchinit.us",         "")
    K_AREA      = name_to_key.get("pyarchinit.area",       "")
    K_SITO      = name_to_key.get("pyarchinit.sito",       "")
    K_UNITA     = name_to_key.get("pyarchinit.unita_tipo", "")
    K_RAPPORTI  = name_to_key.get("pyarchinit.rapporti",   "")

    def _collect_data(n_elem: ET.Element, nid: str) -> None:
        bag: Dict[str, str] = {}
        for d in n_elem.findall(f"{{{_NS['g']}}}data"):
            k = d.attrib.get("key", "")
            t = (d.text or "").strip()
            if k and t:
                bag[k] = t
        raw_data[nid] = bag

    def _walk(parent_elem: ET.Element, parent_grp: Optional[str]) -> None:
        for graph in parent_elem.findall(f"{{{_NS['g']}}}graph"):
            for n in graph.findall(f"{{{_NS['g']}}}node"):
                nid = n.attrib.get("id", "")
                if not nid:
                    continue
                _collect_data(n, nid)
                label = _extract_label(n)
                is_group = n.attrib.get("yfiles.foldertype") in ("group", "folder")
                if is_group:
                    scene.groups[nid] = _GroupData(group_id=nid, label=label)
                    _walk(n, nid)
                else:
                    fill, border, bw, shape, rounded = _extract_style(n)
                    scene.nodes[nid] = _NodeData(
                        node_id=nid, label=label, fill=fill, border=border,
                        border_width=bw, shape=shape, rounded=rounded,
                        text_color=_readable_text_color(fill),
                        group_id=parent_grp,
                    )

    top_graph = root.find(f"{{{_NS['g']}}}graph")
    if top_graph is None:
        return scene
    for n in top_graph.findall(f"{{{_NS['g']}}}node"):
        nid = n.attrib.get("id", "")
        if not nid:
            continue
        _collect_data(n, nid)
        label = _extract_label(n)
        is_group = n.attrib.get("yfiles.foldertype") in ("group", "folder")
        if is_group:
            scene.groups[nid] = _GroupData(group_id=nid, label=label)
            _walk(n, nid)
        else:
            fill, border, bw, shape, rounded = _extract_style(n)
            scene.nodes[nid] = _NodeData(
                node_id=nid, label=label, fill=fill, border=border,
                border_width=bw, shape=shape, rounded=rounded,
                text_color=_readable_text_color(fill),
                group_id=None,
            )

    for n in scene.nodes.values():
        if n.group_id and n.group_id in scene.groups:
            scene.groups[n.group_id].member_ids.append(n.node_id)

    # Build (us, area, sito) → node_id reverse index for rapporti.
    by_uas: Dict[Tuple[str, str, str], str] = {}
    for nid, bag in raw_data.items():
        if nid not in scene.nodes:
            continue
        us = bag.get(K_US, "").strip() if K_US else ""
        area = bag.get(K_AREA, "").strip() if K_AREA else ""
        sito = bag.get(K_SITO, "").strip() if K_SITO else ""
        if us:
            by_uas[(us.lower(), area.lower(), sito.lower())] = nid

    # Canonical-pair dedup: for ANY relation, we never want two arrows
    # between the same pair of nodes. Reciprocal rapporti (A says
    # 'Copre B', B says 'Coperto da A') describe the SAME edge and
    # would otherwise produce two arrows pointing both ways.
    # Strategy: normalize each edge to a canonical (parent, child) form
    # using _REVERSED_RELATIONS, then dedup by the unordered node pair
    # ALONE (not by relation type — the first relation wins, which
    # matters very little because reciprocal pairs share semantics).
    pair_seen: Set[frozenset] = set()
    edges_from_rapporti = 0
    if K_RAPPORTI:
        for nid, bag in raw_data.items():
            if nid not in scene.nodes:
                continue
            rap = bag.get(K_RAPPORTI, "")
            if not rap:
                continue
            try:
                rap_list = ast.literal_eval(rap)
            except (ValueError, SyntaxError):
                continue
            if not isinstance(rap_list, (list, tuple)):
                continue
            for entry in rap_list:
                if not isinstance(entry, (list, tuple)) or len(entry) < 4:
                    continue
                tipo = str(entry[0])
                target_us, target_area, target_sito = (
                    str(entry[1]), str(entry[2]), str(entry[3])
                )
                tnid = by_uas.get(
                    (target_us.lower(), target_area.lower(),
                     target_sito.lower())
                )
                if not tnid or tnid == nid:
                    continue
                if tipo in _REVERSED_RELATIONS:
                    src, tgt = tnid, nid
                else:
                    src, tgt = nid, tnid
                pair_key = frozenset((src, tgt))
                if pair_key in pair_seen:
                    continue
                pair_seen.add(pair_key)
                scene.edges.append(_EdgeData(
                    source=src, target=tgt, relation=tipo,
                ))
                edges_from_rapporti += 1

    # Fallback: top-level <edge> when rapporti absent.
    if edges_from_rapporti == 0:
        for e in root.iter(f"{{{_NS['g']}}}edge"):
            src = e.attrib.get("source", "")
            tgt = e.attrib.get("target", "")
            if not src or not tgt:
                continue
            pair_key = frozenset((src, tgt))
            if pair_key in pair_seen:
                continue
            pair_seen.add(pair_key)
            scene.edges.append(_EdgeData(source=src, target=tgt))

    return scene


# ----------------------------------------------------------------------
# DOT source generation
# ----------------------------------------------------------------------

_DOT_ID_SANITIZE = re.compile(r'[^A-Za-z0-9_]')


def _dot_id(raw_id: str) -> str:
    """Convert an arbitrary node id into a DOT-safe identifier."""
    s = _DOT_ID_SANITIZE.sub("_", raw_id)
    if not s or s[0].isdigit():
        s = "n_" + s
    return s


def _dot_escape(text: str) -> str:
    """Escape a string for inclusion inside DOT double-quotes."""
    return (text or "").replace("\\", "\\\\").replace("\"", "\\\"")


def _build_dot_source(scene: _Scene,
                      *,
                      rankdir: str = "TB",
                      ranksep: float = 0.35,
                      nodesep: float = 0.18,
                      fontsize: int = 8) -> str:
    """Generate a DOT source string from the parsed Scene.

    Node defaults: smaller default size (width=0.45, height=0.22,
    fontsize=8) so symbols don't dominate the canvas. Per-node
    declarations omit width/height — letting dot auto-fit to the label,
    which gives the "adaptive sizing" the user asked for.
    """
    lines: List[str] = []
    lines.append("digraph ExtendedMatrix {")
    lines.append(f'  graph [splines=ortho rankdir={rankdir} '
                 f'ranksep={ranksep} nodesep={nodesep} '
                 f'compound=true bgcolor="#eef2f7" '
                 f'fontname="Helvetica" fontsize={fontsize + 2}];')
    lines.append(f'  node  [shape=box style=filled fontname="Helvetica" '
                 f'fontsize={fontsize} margin="0.06,0.025"];')
    lines.append(f'  edge  [arrowsize=0.55 fontname="Helvetica" '
                 f'fontsize={fontsize - 1}];')

    # Title label at the top
    if scene.title:
        title = _dot_escape(scene.title)
        lines.append(f'  labelloc="t"; label="{title}";')

    # 1) Cluster subgraphs per group
    for gid, g in scene.groups.items():
        if not g.member_ids:
            continue
        cluster_id = _dot_id(gid)
        lines.append(f'  subgraph cluster_{cluster_id} {{')
        lines.append(f'    label="{_dot_escape(g.label)}";')
        lines.append('    style="filled,rounded";')
        lines.append('    fillcolor="#dde6d6";')
        lines.append('    color="#a3b2a1";')
        lines.append('    fontcolor="#1a2d4a";')
        lines.append(f'    fontsize={fontsize + 1}; labeljust="l";')
        for nid in g.member_ids:
            n = scene.nodes.get(nid)
            if n is None:
                continue
            lines.append(f'    {_format_node_decl(n)}')
        lines.append('  }')

    # 2) Top-level (orphan) nodes
    for nid, n in scene.nodes.items():
        if n.group_id is None:
            lines.append(f'  {_format_node_decl(n)}')

    # 3) Same-rank constraint blocks for continuity relations
    #    (Uguale a / Si lega a): pin pairs to the same horizontal
    #    level so the double line is drawn horizontally as required.
    same_rank_pairs: List[Tuple[str, str]] = []
    for e in scene.edges:
        if e.source not in scene.nodes or e.target not in scene.nodes:
            continue
        style = _REL_DOT_STYLES.get(e.relation, _REL_DOT_DEFAULT)
        if style.get("samerank"):
            same_rank_pairs.append((e.source, e.target))
    for src, tgt in same_rank_pairs:
        lines.append(
            f'  {{rank=same; {_dot_id(src)}; {_dot_id(tgt)};}}'
        )

    # 4) Edges (typed). Special-case for continuity relations:
    #    draw as DOUBLE line (style="solid" with high penwidth + a
    #    parallel undecorated line via xlabel trick is too fragile;
    #    instead we use the dot "doubled" trick: dir=none + style=
    #    "solid" with very thick black + an inner edge with white
    #    inset is also fragile. Simplest reliable: pair them with
    #    a constraint=false reverse edge AND use the
    #    arrowhead/arrowtail=none on a constraint=false second edge).
    #    Honestly: we emit a primary thick edge (penwidth 1.0) + a
    #    parallel constraint=false thin white edge through the
    #    middle — produces a visible "double line" effect at
    #    rendering time.
    for e in scene.edges:
        if e.source not in scene.nodes or e.target not in scene.nodes:
            continue
        style = _REL_DOT_STYLES.get(e.relation, _REL_DOT_DEFAULT)
        s = _dot_id(e.source)
        t = _dot_id(e.target)
        arrowhead = style.get("arrowhead", "normal")
        attr_parts = [
            f'color="{style["color"]}"',
            f'penwidth={style["penwidth"]}',
            f'style="{style["style"]}"',
            f'arrowhead={arrowhead}',
            f'arrowtail=none',
            f'dir={"none" if arrowhead == "none" else "forward"}',
        ]
        # Continuity relations: no arrows, drawn as a double line.
        # Graphviz trick: use color="c1:white:c1" to fake a double line
        # via a stacked-color edge (works with splines=ortho too).
        if style.get("double"):
            attr_parts[0] = f'color="{style["color"]}:white:{style["color"]}"'
            attr_parts[1] = f'penwidth=2.4'   # thicker so the white stripe is visible
            attr_parts[3] = 'arrowhead=none'
            attr_parts[5] = 'dir=none'
        # Same-rank edges should not push siblings into separate ranks.
        if style.get("samerank"):
            attr_parts.append('constraint=false')
        lines.append(f'  {s} -> {t} [{", ".join(attr_parts)}];')

    lines.append("}")
    return "\n".join(lines)


def _format_node_decl(n: _NodeData) -> str:
    """Format a single DOT node declaration.

    Adaptive size: don't fix width/height — dot auto-fits to the
    label text (user feedback: "le icone troppo grandi falle più
    piccole o comunque che si adattino").
    """
    label = _dot_escape(n.label or n.node_id[:8])
    style = "filled,rounded" if n.rounded else "filled"
    attrs = (f'label="{label}" '
             f'shape={n.shape} '
             f'fillcolor="{n.fill}" '
             f'color="{n.border}" '
             f'penwidth={n.border_width:.1f} '
             f'fontcolor="{n.text_color}" '
             f'style="{style}"')
    return f'{_dot_id(n.node_id)} [{attrs}];'


# ----------------------------------------------------------------------
# Public renderer
# ----------------------------------------------------------------------

def render_extended_matrix(graphml_path: Union[str, Path],
                           output_path: Union[str, Path],
                           *,
                           format: str = "png") -> Path:
    """Render the Extended Matrix to PNG/JPEG/SVG via Graphviz dot.

    Raises RuntimeError if `dot` is not installed — the caller in
    s3dgraphy_dot_bridge handles fallback to the matplotlib renderer.
    """
    dot_binary = _find_dot_binary()
    if dot_binary is None:
        raise RuntimeError(
            "Graphviz `dot` binary not found. "
            "Install via `brew install graphviz` (macOS) / "
            "`apt-get install graphviz` (Linux) / "
            "`choco install graphviz` (Windows), or rely on the "
            "matplotlib swimlane renderer fallback."
        )

    graphml_path = Path(graphml_path)
    output_path = Path(output_path)
    if not graphml_path.exists():
        raise FileNotFoundError(f"GraphML not found: {graphml_path}")

    scene = _parse_graphml(graphml_path)
    if not scene.nodes and not scene.groups:
        raise ValueError(f"No drawable nodes in {graphml_path}")

    dot_source = _build_dot_source(scene)

    fmt = format.lower().lstrip(".")
    if fmt == "jpg":
        fmt = "jpeg"
    if fmt not in ("png", "jpeg", "svg", "pdf"):
        fmt = "png"

    # Persist the dot source alongside the output, useful for debugging
    # and for power users who want to tweak it in yEd / xdot.
    dot_aux = output_path.with_suffix(".dot")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dot_aux.write_text(dot_source, encoding="utf-8")

    result = subprocess.run(
        [dot_binary, f"-T{fmt}", "-o", str(output_path), str(dot_aux)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Graphviz dot failed (exit {result.returncode}):\n"
            f"{result.stderr.strip()[:2000]}"
        )
    if not output_path.exists():
        raise RuntimeError(
            f"Graphviz dot returned 0 but {output_path} was not created"
        )
    return output_path
