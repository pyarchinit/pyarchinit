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

from sqlalchemy import text

from ._db_handle import _resolve_db_handle


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

    Bug P (2026-05-15 v2 user feedback): row-paradata nodes are now
    StratigraphicNode-class instances (with attributes['unita_tipo']
    distinguishing DOC/Combinar/Extractor/property), so the existing
    StratigraphicNode branch below handles them naturally — no
    paradata-specific filter logic needed here. Site-level paradata
    (Author/License/Embargo) is handled by ``_inject_isolated_paradata_nodes``
    via the ``_PARADATA_INJECT_TYPES`` snapshot/inject path.

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

    # Pass 1: keep stratigraphic nodes matching site_filter.
    # Bug P (2026-05-15 v2): row-paradata are StratigraphicNode subclasses
    # now (with attributes['unita_tipo'] set), so they're handled by the
    # ``isinstance(n, StratigraphicNode)`` check below — no separate
    # branch needed.
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


def _read_first_sito(db_path: Path) -> str:
    """Return the first ``us_table.sito`` value found in *db_path*.

    Used by :func:`export_graphml` when the caller did not pass a
    ``site_filter``: AI05's :class:`GraphProjector.populate_graph`
    requires a non-empty sito (single-site projection contract), but
    AI03's ``export_graphml`` historically accepted ``site_filter=None``
    and silently exported the whole DB. For backward compatibility we
    pick the first sito available — matching pre-AI05 behaviour on
    single-sito fixtures (the Volterra baseline AC-2 guards) and giving
    deterministic output on multi-sito DBs (caller must pass an
    explicit ``site_filter`` to disambiguate).

    Raises GraphMLExportError(stage="import") if us_table is empty
    or unreadable.
    """
    try:
        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT sito FROM us_table "
                    "WHERE sito IS NOT NULL AND sito <> '' "
                    "ORDER BY sito LIMIT 1"
                )
            ).fetchone()
    except Exception as e:
        raise GraphMLExportError(
            "import",
            RuntimeError(f"Cannot read us_table.sito: {e}"),
        ) from e
    if row is None:
        raise GraphMLExportError(
            "import",
            RuntimeError(
                "us_table contains no rows with a sito — pass an "
                "explicit site_filter or check the DB."),
        )
    return str(row[0])


# PyArchInit `rapporti` strings (Italian + English) → s3dgraphy
# topological edge types. The s3dgraphy 0.1.40 PyArchInitImporter
# only handles the us_table column→property mapping; it does NOT
# parse the rapporti JSON column nor read periodizzazione_table.
# So the orchestrator below performs the missing enrichment by
# reading those tables directly and adding edges/EpochNodes that
# the GraphMLExporter + TemporalInferenceEngine then consume.
#
# The canonical home for these constants is `s3dgraphy.sync.rapporti`
# (introduced in v1.6 as the public surface for pyArchInit rapporti
# ↔ canonical-edge translation across all sync code paths). The
# names below are kept as private re-export aliases so legacy
# imports `from s3dgraphy.sync.graphml_writer import _RAPPORTI_…`
# keep working unchanged.
from .rapporti import (
    RAPPORTI_TO_EDGE_TYPE as _RAPPORTI_TO_EDGE_TYPE,
    RAPPORTI_SHORTHAND as _RAPPORTI_SHORTHAND,
)


# Light-hue palette cycled across epoch swimlane rows so each period
# has a distinct background. Pastel shades chosen for readability.
# Defined here (early in the module) so `_enrich_pyarchinit_graph` can
# assign each EpochNode.color before export — the s3dgraphy
# EpochSwimlanesGenerator at `epoch_generator.py:360` honours
# `epoch.color` when set, otherwise falls back to `#CCFFCC` for every
# row (the green-ish default the user spotted).
_EPOCH_ROW_PALETTE = (
    "#FFE4E1",  # misty rose
    "#E0FFFF",  # light cyan
    "#F5F5DC",  # beige
    "#E6E6FA",  # lavender
    "#F0FFF0",  # honeydew
    "#FFF0F5",  # lavender blush
    "#FFFACD",  # lemon chiffon
    "#E0FFE4",  # mint
)


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


# ---------------------------------------------------------------------------
# Post-processor: pyarchinit-specific visual conventions on top of the
# s3dgraphy GraphMLExporter output. The exporter writes a GraphML where
# every node uses a single rectangle/white/dark-red style and every label
# is just the bare US number. The conventions below restore the EM 1.5
# look that yEd users (and EM-tools downstream) expect.
# ---------------------------------------------------------------------------

# Per-language US/USM display abbreviations — sourced from the Phase 1
# i18n module so QGIS locale is honoured. Other unita_tipo values
# (USVs/USVn/SF/etc.) are EM canonical and identical across languages.
_LOCALIZED_US_USM = {
    "it": ("US", "USM"),
    "en": ("SU", "WSU"),
    "de": ("SE", "MSE"),
    "fr": ("US", "USM"),
    "es": ("UE", "UEM"),
    "ar": ("SU", "WSU"),
    "ca": ("UE", "UEM"),
    "ro": ("US", "USZ"),
    "pt": ("UE", "UEM"),
    "el": ("ΣΜ", "ΤΣΜ"),
}

# Style table: per unita_tipo → visual properties. Calibrated to the
# legacy pyarchinit Harris-matrix output (resources/dbfiles/dottoxml
# pipeline) so users get the visual baseline they have always seen,
# with the EM 1.5dev1 palette's color values where they overlap.
#
# Keys:
#   fill         – fill color
#   border       – border color
#   width        – border width
#   style        – border line style (line / dashed / dotted)
#   shape        – yEd shape name
#   text_color   – NodeLabel textColor (defaults to #000000)
#   font_style   – NodeLabel fontStyle ("bold" / "plain"; default "bold")
#   underlined   – NodeLabel underlinedText flag (True / False)
# Lazy-initialised s3dgraphy NodeRegistry singleton. Reads
# em_palette_template.graphml + s3Dgraphy_node_datamodel.json so we
# don't have to hardcode visual rules for every EM type. Used as a
# FALLBACK by `_resolve_visual()` for any unita_tipo we don't have
# an explicit pyarchinit override for. See:
#   ext_libs/s3dgraphy/exporter/graphml/node_registry.py
#   ext_libs/s3dgraphy/JSON_config/em_visual_rules.json
#   ext_libs/s3dgraphy/templates/em_palette_template.graphml
_node_registry = None


def _get_node_registry():
    """Return a singleton s3dgraphy NodeRegistry, or None if it can't
    be loaded (e.g. older s3dgraphy version)."""
    global _node_registry
    if _node_registry is False:  # sentinel: previously failed to load
        return None
    if _node_registry is None:
        try:
            from s3dgraphy.exporter.graphml.node_registry import (
                NodeRegistry,
            )
            _node_registry = NodeRegistry()
        except Exception:
            _node_registry = False
            return None
    return _node_registry


def _resolve_visual(unita_tipo: str):
    """Return the visual properties dict for *unita_tipo*, preferring
    pyarchinit-specific overrides in `_VISUAL_BY_UNITA_TIPO` and
    falling back to s3dgraphy's NodeRegistry palette for any type we
    don't have an explicit override for.

    Pyarchinit overrides cover legacy deviations the user expects:
    border width 3.0 (vs canonical 4.0), USM grey background, CON
    diamond, paradata BPMN/SVG icons. New EM types added to s3dgraphy
    in future releases get sane visuals automatically via the
    NodeRegistry path without changes here.
    """
    if unita_tipo in _VISUAL_BY_UNITA_TIPO:
        return _VISUAL_BY_UNITA_TIPO[unita_tipo]
    registry = _get_node_registry()
    if registry is None:
        return None
    props = registry.get_visual_properties(unita_tipo)
    if props is None:
        return None
    # Translate the s3dgraphy NodeVisualProperties dataclass into the
    # dict shape the post-processor consumes (same keys as the entries
    # in `_VISUAL_BY_UNITA_TIPO`).
    return {
        "fill": props.fill_color,
        "border": props.border_color,
        "width": str(props.border_width),
        "style": props.border_type,
        "shape": props.shape,
        "text_color": props.text_color,
        "font_style": "plain",
    }


_VISUAL_BY_UNITA_TIPO = {
    # Stratigraphic core (red border #9B3333, width 3.0 per legacy)
    "US":   {"fill": "#FFFFFF", "border": "#9B3333", "width": "3.0",
             "style": "line", "shape": "rectangle"},
    "USM":  {"fill": "#C0C0C0", "border": "#9B3333", "width": "3.0",
             "style": "line", "shape": "rectangle"},
    "USN":  {"fill": "#FFFFFF", "border": "#9B3333", "width": "3.0",
             "style": "line", "shape": "ellipse"},
    "TSU":  {"fill": "#FFFFFF", "border": "#9B3333", "width": "3.0",
             "style": "dashed", "shape": "roundrectangle"},
    # Documentary stratigraphic (orange border, EM canonical)
    "USD":  {"fill": "#FFFFFF", "border": "#D86400", "width": "3.0",
             "style": "line", "shape": "roundrectangle"},
    # Structural Virtual SU — parallelogram, BLACK fill, blue border,
    # white plain (not bold) text per EM canon and legacy output
    "USVs": {"fill": "#000000", "border": "#248FE7", "width": "3.0",
             "style": "line", "shape": "parallelogram",
             "text_color": "#FFFFFF", "font_style": "plain"},
    # Non-Structural Virtual SU — hexagon, BLACK fill, green border
    "USVn": {"fill": "#000000", "border": "#31792D", "width": "3.0",
             "style": "line", "shape": "hexagon",
             "text_color": "#FFFFFF", "font_style": "plain"},
    # Bug Q (2026-05-15 user feedback): pyarchinit's UI uses ``USV``
    # as the canonical unita_tipo for generic virtual SU (the user
    # form's combobox value, not the EM-internal ``USVs``/``USVn``
    # distinction). Render with the same EM canonical shape as USVs
    # (blue parallelogram, black fill, white text) so the round-trip
    # to yEd matches the EM 1.5 palette.
    "USV":  {"fill": "#000000", "border": "#248FE7", "width": "3.0",
             "style": "line", "shape": "parallelogram",
             "text_color": "#FFFFFF", "font_style": "plain"},
    # Special Find (yellow border)
    "SF":   {"fill": "#FFFFFF", "border": "#D8BD30", "width": "3.0",
             "style": "line", "shape": "octagon"},
    "VSF":  {"fill": "#000000", "border": "#B19F61", "width": "3.0",
             "style": "line", "shape": "octagon",
             "text_color": "#FFFFFF", "font_style": "plain"},
    # Working Unit (green border)
    "UL":   {"fill": "#FFFFFF", "border": "#31792D", "width": "3.0",
             "style": "line", "shape": "octagon"},
    # Continuity — black diamond/rhombus per legacy pyarchinit
    # (Scavo archeologico.graphml uses an SVG square rotated 45°;
    # rendering the same as a yEd built-in "diamond" shape with
    # solid-black fill and border preserves the visual.)
    "CON":  {"fill": "#000000", "border": "#000000", "width": "3.0",
             "style": "line", "shape": "diamond",
             "font_style": "plain"},
    # Paradata tooling, calibrated against the EM 1.5dev1 palette and
    # the user's brief:
    #   - DOC: BPMN data-object look (yEd ShapeNode rectangle with
    #     fill #FFFFFFE6, thin black border 1.0). Label "D.<n>"
    #     centered, bold, NOT underlined.
    #   - Extractor: lavender rectangle (#CCCCFF), thin black border
    #     1.0. Label "D.<n>" UNDERLINED.
    #   - Combinar: lavender rectangle, label "C.<n>" NOT underlined.
    #   - property: BPMN annotation look, fill #FFFFFFE6, thin black
    #     border, label = d_stratigrafica (e.g. "Materiale"),
    #     plain (non-bold) text, NOT underlined.
    "DOC":       {"fill": "#FFFFFFE6", "border": "#000000", "width": "1.0",
                  "style": "line", "shape": "rectangle"},
    "EXT":       {"fill": "#CCCCFF", "border": "#000000", "width": "1.0",
                  "style": "line", "shape": "rectangle",
                  "underlined": True},
    "Extractor": {"fill": "#CCCCFF", "border": "#000000", "width": "1.0",
                  "style": "line", "shape": "rectangle",
                  "underlined": True},
    "Combinar":  {"fill": "#CCCCFF", "border": "#000000", "width": "1.0",
                  "style": "line", "shape": "rectangle"},
    "property":  {"fill": "#FFFFFFE6", "border": "#000000", "width": "1.0",
                  "style": "line", "shape": "rectangle",
                  "font_style": "plain"},
    "SUS":  {"fill": "#FFFFFF", "border": "#9B3333", "width": "3.0",
             "style": "line", "shape": "rectangle"},
}

# Unit types that render as paradata flow (dashed edges to/from them).
# When an edge has at least one endpoint of one of these types, the
# post-processor sets <y:LineStyle type="dashed">; otherwise it stays
# solid (the default for stratigraphic relations).
_PARADATA_UNITA_TIPI = frozenset({
    "DOC", "EXT", "Extractor", "Combinar", "property",
})

# Mapping from unita_tipo to the y:Resources/y:Resource refid that
# yEd should reference for the node icon. Refids match those used
# by the legacy dottoxml.py pipeline (id="1" Extractor, id="2"
# Combinar, id="3" Continuity).
_PARADATA_SVG_REFID = {
    "CON": "3",
    "Extractor": "1",
    "EXT": "1",
    "Combinar": "2",
}

# Mapping from unita_tipo to the BPMN type used by yEd's
# com.yworks.bpmn.Artifact.withShadow GenericNode configuration.
# DOC ↔ data-object (page with corner fold); property ↔ annotation
# (open bracket on the left).
_PARADATA_BPMN_TYPE = {
    "DOC": "ARTIFACT_TYPE_DATA_OBJECT",
    "property": "ARTIFACT_TYPE_ANNOTATION",
}

# Geometry overrides for paradata icons — the legacy dot.py used
# specific sizes per icon to keep the visual proportions reasonable.
_PARADATA_ICON_GEOMETRY = {
    "CON":       {"height": "26.0", "width": "26.0"},
    "Extractor": {"height": "25.0", "width": "25.0"},
    "EXT":       {"height": "25.0", "width": "25.0"},
    "Combinar":  {"height": "25.0", "width": "25.0"},
    "DOC":       {"height": "55.0", "width": "35.0"},
}

# `_EPOCH_ROW_PALETTE` is defined earlier (above _enrich_pyarchinit_graph)
# so that the enrichment step can assign per-epoch colors before export.


def _resolve_display_label(unita_tipo: str, us_number: str,
                           language: str, descrizione: str = "") -> str:
    """Return the formatted display label for a node, per legacy
    pyarchinit Harris-matrix conventions.

    Format rules:
      US        → "US<n>"        (concat, no space, language-aware US/SU/SE/...)
      USM       → "USM<n>"       (language-aware USM/WSU/MSE/...)
      USVs/USVn → "USV<n>"       (3 letters; legacy strips the
                                  s/n suffix in the LABEL, even
                                  though the type is preserved)
      SF, VSF   → "SF<n>" / "VSF<n>"
      CON       → "CON<n>"
      DOC       → "D.<n>"
      EXT/Extractor → "D.<n>"   (same shape; underline applied via
                                  visual table)
      Combinar  → "C.<n>"
      property  → descrizione   (e.g. "Materiale", "Pavimento"); falls
                                  back to "property<n>" if descrizione
                                  is empty
      anything else → "<unita_tipo><n>" (concat fallback)
    """
    n = us_number.strip()
    if unita_tipo == "US":
        return f"{_LOCALIZED_US_USM.get(language, ('US', 'USM'))[0]}{n}"
    if unita_tipo == "USM":
        return f"{_LOCALIZED_US_USM.get(language, ('US', 'USM'))[1]}{n}"
    if unita_tipo in ("USVs", "USVn"):
        return f"USV{n}"
    if unita_tipo in ("SF", "VSF"):
        return f"{unita_tipo}{n}"
    if unita_tipo == "CON":
        return f"CON{n}"
    # Bug R (2026-05-15 user feedback): paradata kinds are no longer
    # dedup'd at import — every yEd occurrence is its own row with a
    # synthesised us value (e.g. ``material_2``, ``01_3``). The
    # original label (``material``, ``D.01``, ``C.02``, ``E.005``)
    # lives in ``d_stratigrafica`` (passed in as ``descrizione``).
    # Prefer that for display so the rendered NodeLabel matches the
    # yEd-authored label, regardless of the us suffix.
    if unita_tipo in ("DOC", "EXT", "Extractor"):
        return descrizione.strip() or f"D.{n}"
    if unita_tipo == "Combinar":
        return descrizione.strip() or f"C.{n}"
    if unita_tipo == "property":
        if descrizione.strip():
            return descrizione.strip()
        # Legacy fallback (no descrizione): when imported from yEd
        # before Bug R, property NAME lived in us_table.us. Honour
        # that path for pre-Bug-R DBs.
        if n and not n.isdigit():
            return n
        return f"property{n}"
    return f"{unita_tipo}{n}"


def _convert_shape_to_svg_node(shape_el, etree, NS_Y, refid: str,
                                geometry: dict) -> None:
    """Convert a ``<y:ShapeNode>`` element in place into a
    ``<y:SVGNode>`` referencing the legacy SVG resource id ``refid``.

    Legacy dottoxml.py used SVGNodes with custom Inkscape SVGs to
    render Continuity, Extractor and Combinar icons. We preserve the
    Geometry/Fill/BorderStyle/NodeLabel children verbatim and just
    change the parent tag and append <y:SVGNodeProperties> +
    <y:SVGModel>/<y:SVGContent> instead of <y:Shape>.
    """
    shape_el.tag = f"{{{NS_Y}}}SVGNode"
    # Apply legacy icon geometry overrides.
    geom_el = shape_el.find(f"{{{NS_Y}}}Geometry")
    if geom_el is not None:
        if "height" in geometry:
            geom_el.set("height", geometry["height"])
        if "width" in geometry:
            geom_el.set("width", geometry["width"])
    # Drop the <y:Shape type="..."> child if present — SVGNode does
    # not accept it.
    inner_shape = shape_el.find(f"{{{NS_Y}}}Shape")
    if inner_shape is not None:
        shape_el.remove(inner_shape)
    # Append SVG plumbing.
    svg_props = etree.SubElement(shape_el, f"{{{NS_Y}}}SVGNodeProperties")
    svg_props.set("usingVisualBounds", "true")
    svg_model = etree.SubElement(shape_el, f"{{{NS_Y}}}SVGModel")
    svg_model.set("svgBoundsPolicy", "0")
    svg_content = etree.SubElement(svg_model, f"{{{NS_Y}}}SVGContent")
    svg_content.set("refid", refid)


def _convert_shape_to_bpmn_node(shape_el, etree, NS_Y, bpmn_type: str,
                                 geometry: dict) -> None:
    """Convert a ``<y:ShapeNode>`` element in place into a
    ``<y:GenericNode>`` with BPMN artifact configuration matching
    ``bpmn_type`` (ARTIFACT_TYPE_DATA_OBJECT for DOC,
    ARTIFACT_TYPE_ANNOTATION for property).

    Legacy dottoxml.py used GenericNodes with the BPMN artifact
    configuration to render DOC and property nodes. We preserve the
    Geometry/Fill/BorderStyle/NodeLabel children verbatim and replace
    the <y:Shape> child with the BPMN <y:StyleProperties> block.
    """
    shape_el.tag = f"{{{NS_Y}}}GenericNode"
    shape_el.set("configuration", "com.yworks.bpmn.Artifact.withShadow")
    geom_el = shape_el.find(f"{{{NS_Y}}}Geometry")
    if geom_el is not None:
        if "height" in geometry:
            geom_el.set("height", geometry["height"])
        if "width" in geometry:
            geom_el.set("width", geometry["width"])
    inner_shape = shape_el.find(f"{{{NS_Y}}}Shape")
    if inner_shape is not None:
        shape_el.remove(inner_shape)
    style_props = etree.SubElement(shape_el, f"{{{NS_Y}}}StyleProperties")
    for prop_name, prop_class, prop_value in (
        ("com.yworks.bpmn.icon.line.color", "java.awt.Color", "#000000"),
        ("com.yworks.bpmn.icon.fill2", "java.awt.Color", "#d4d4d4cc"),
        ("com.yworks.bpmn.icon.fill", "java.awt.Color", "#ffffffe6"),
        ("com.yworks.bpmn.type",
         "com.yworks.yfiles.bpmn.view.BPMNTypeEnum", bpmn_type),
    ):
        prop_el = etree.SubElement(style_props, f"{{{NS_Y}}}Property")
        prop_el.set("class", prop_class)
        prop_el.set("name", prop_name)
        prop_el.set("value", prop_value)


def _ensure_resources_block(root, etree, NS_GRAPHML, NS_Y,
                             needed_refids: set) -> None:
    """Make sure ``<graphml>`` has a ``<key yfiles.type="resources">``
    declaration AND a matching ``<data>`` child carrying a
    ``<y:Resources>`` block with the requested SVG resource ids.

    Idempotent: if the resources block already exists for the given
    ids, do nothing. Otherwise create the missing pieces by appending
    new elements; preserves any existing keys/data.

    *needed_refids* is a set of strings like {"1", "2", "3"} matching
    the keys of `_legacy_paradata_svgs.SVG_RESOURCES`.
    """
    if not needed_refids:
        return
    from . import _legacy_paradata_svgs as svgs

    # Find or allocate the resources <key>.
    res_key_id = None
    used_ids = set()
    for k_el in root.findall(f"{{{NS_GRAPHML}}}key"):
        kid = k_el.get("id")
        if kid:
            used_ids.add(kid)
        if k_el.get("yfiles.type") == "resources":
            res_key_id = kid
    if res_key_id is None:
        # Allocate a fresh "dN" id that doesn't clash.
        n = 0
        while f"d{n}" in used_ids:
            n += 1
        res_key_id = f"d{n}"
        key_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        key_el.set("for", "graphml")
        key_el.set("id", res_key_id)
        key_el.set("yfiles.type", "resources")
        # Insert after the last existing <key>, before <graph>.
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            last_key = existing_keys[-1]
            last_key.addnext(key_el)
        else:
            root.insert(0, key_el)

    # Find or create the matching <data> child of <graphml>.
    res_data_el = None
    for d_el in root.findall(f"{{{NS_GRAPHML}}}data"):
        if d_el.get("key") == res_key_id:
            res_data_el = d_el
            break
    if res_data_el is None:
        res_data_el = etree.SubElement(root, f"{{{NS_GRAPHML}}}data")
        res_data_el.set("key", res_key_id)

    # Find or create the <y:Resources> child.
    resources_el = res_data_el.find(f"{{{NS_Y}}}Resources")
    if resources_el is None:
        resources_el = etree.SubElement(res_data_el, f"{{{NS_Y}}}Resources")

    # Add only the resources that are not already present.
    existing_resource_ids = {
        r.get("id")
        for r in resources_el.findall(f"{{{NS_Y}}}Resource")
    }
    for refid in sorted(needed_refids):
        if refid in existing_resource_ids:
            continue
        if refid not in svgs.SVG_RESOURCES:
            continue
        r_el = etree.SubElement(resources_el, f"{{{NS_Y}}}Resource")
        r_el.set("id", refid)
        r_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r_el.text = svgs.SVG_RESOURCES[refid]


def _apply_pyarchinit_visual_overrides(
    graph,
    xml_path: Path,
    *,
    language: str = "it",
) -> None:
    """Patch the GraphML produced by s3dgraphy GraphMLExporter so that
    every pyarchinit visual convention surfaces correctly:

    1. Stratigraphic node labels are prefixed with the language-aware
       unit-type abbreviation ("US 36", "USM 3", "USVs 4", …).
    2. Node fill / border / shape come from `_VISUAL_BY_UNITA_TIPO`
       keyed on the `unita_tipo` attribute that
       `_enrich_pyarchinit_graph` populates from the DB.
    3. Each `<y:Row>` inside the swimlane TableNode gets a distinct
       background colour from `_EPOCH_ROW_PALETTE` so adjacent epochs
       are visually separable.

    The exporter emits the s3dgraphy `node_id` (UUID) under data key
    `d3` (the EMID slot). We use that to bridge in-memory graph nodes
    to their XML counterparts.

    Mutates *xml_path* in place. No-op if lxml is unavailable.
    """
    try:
        from lxml import etree
    except ImportError:
        return

    # Build EMID → metadata map from the in-memory graph.
    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    NS_Y = "http://www.yworks.com/xml/graphml"

    meta_by_emid = {}
    for n in graph.nodes:
        emid = getattr(n, "node_id", None)
        if not emid:
            continue
        attrs = getattr(n, "attributes", {}) or {}
        meta_by_emid[emid] = {
            "unita_tipo": attrs.get("unita_tipo"),
            "name": getattr(n, "name", ""),
            "descrizione": attrs.get("d_stratigrafica", ""),
        }

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # --- 1+2. Walk every <node> and patch label/fill/border/shape ----------
    # The EMID slot's data-key id varies across nested graphs in the
    # exporter output (sometimes d3, sometimes d7, etc. — depends on
    # how many nested keys are scoped at the parent <graph> level).
    # Walk all <data> children of the node and pick the one whose text
    # is a UUID we recognise from the in-memory graph.
    known_emids = set(meta_by_emid.keys())
    # Track which graphml node-id corresponds to which unita_tipo so we
    # can decide dashed-vs-solid edge style in the second pass.
    node_id_to_unita_tipo: dict[str, str] = {}
    # Track ParadataNodeGroup wrapper nodes — those are the targets of
    # the US→PD edges and need to drive dashed-edge selection too.
    paradata_group_node_ids: set[str] = set()
    # Collect SVG resource ids needed by paradata nodes we synthesize.
    needed_svg_refids: set[str] = set()
    for node_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        # ParadataNodeGroup wrappers carry a nested <graph> child
        # holding their paradata members. Mark them so we can later
        # decide their incident edges should be dashed.
        if node_el.find(f"{{{NS_GRAPHML}}}graph") is not None:
            xid = node_el.get("id")
            if xid:
                paradata_group_node_ids.add(xid)
        emid = None
        for data_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            txt = (data_el.text or "").strip()
            if txt and txt in known_emids:
                emid = txt
                break
        if emid is None:
            continue

        meta = meta_by_emid[emid]
        unita_tipo = meta["unita_tipo"]
        if not unita_tipo:
            continue
        node_xml_id = node_el.get("id")
        if node_xml_id:
            node_id_to_unita_tipo[node_xml_id] = unita_tipo
        visual = _resolve_visual(unita_tipo)
        us_number = (meta.get("name") or "").strip()
        descrizione = (meta.get("descrizione") or "").strip()
        display_label = _resolve_display_label(
            unita_tipo, us_number, language, descrizione)

        # Patch the ShapeNode block, if any
        shape_nodes = list(node_el.iter(f"{{{NS_Y}}}ShapeNode"))
        for shape_el in shape_nodes:
            if visual:
                fill_el = shape_el.find(f"{{{NS_Y}}}Fill")
                if fill_el is not None:
                    fill_el.set("color", visual["fill"])
                border_el = shape_el.find(f"{{{NS_Y}}}BorderStyle")
                if border_el is not None:
                    border_el.set("color", visual["border"])
                    if "width" in visual:
                        border_el.set("width", visual["width"])
                    if "style" in visual:
                        border_el.set("type", visual["style"])
                shape_inner = shape_el.find(f"{{{NS_Y}}}Shape")
                if shape_inner is not None:
                    shape_inner.set("type", visual["shape"])
            # Replace the label with the legacy-faithful display form
            # ("US36", "USV102", "D.4001", "C.900", "Materiale", …).
            label_el = shape_el.find(f"{{{NS_Y}}}NodeLabel")
            if label_el is not None:
                label_el.text = display_label
                if visual:
                    text_color = visual.get("text_color", "#000000")
                    label_el.set("textColor", text_color)
                    font_style = visual.get("font_style", "plain")
                    label_el.set("fontStyle", font_style)
                    if visual.get("underlined"):
                        label_el.set("underlinedText", "true")
                    else:
                        label_el.set("underlinedText", "false")

        # If this paradata type needs an SVG / BPMN icon (legacy
        # dottoxml.py convention), morph the ShapeNode in place into
        # the appropriate yEd container element.
        svg_refid = _PARADATA_SVG_REFID.get(unita_tipo)
        bpmn_type = _PARADATA_BPMN_TYPE.get(unita_tipo)
        icon_geom = _PARADATA_ICON_GEOMETRY.get(unita_tipo, {})
        if svg_refid and shape_nodes:
            _convert_shape_to_svg_node(
                shape_nodes[0], etree, NS_Y, svg_refid, icon_geom)
            needed_svg_refids.add(svg_refid)
        elif bpmn_type and shape_nodes:
            _convert_shape_to_bpmn_node(
                shape_nodes[0], etree, NS_Y, bpmn_type, icon_geom)

    # --- 2b. Patch edges: dashed when one endpoint is paradata --------------
    # pyarchinit-legacy convention: stratigraphic edges (US↔US, USM↔USM,
    # CON↔stratigraphic, …) are SOLID. Edges touching a paradata unit
    # (DOC, Extractor, Combinar, property) are DASHED.
    from .edge_registry import is_paradata_edge
    for edge_el in root.iter(f"{{{NS_GRAPHML}}}edge"):
        src = edge_el.get("source") or ""
        tgt = edge_el.get("target") or ""
        src_type = node_id_to_unita_tipo.get(src)
        tgt_type = node_id_to_unita_tipo.get(tgt)
        # Classify the edge as paradata using the canonical s3dgraphy
        # datamodel via edge_registry (D8). Falls back to the original
        # unita_tipo-based heuristic if the registry doesn't classify
        # the edge — the registry is the new source of truth, the
        # heuristic stays as defence in depth (and covers edges whose
        # edge_type attribute isn't recoverable from the post-processed
        # XML, which is the common case for AI03 output).
        edge_type_attr = edge_el.get("data-edge-type")  # may be None
        is_paradata = bool(
            (edge_type_attr and is_paradata_edge(edge_type_attr))
            or src_type in _PARADATA_UNITA_TIPI
            or tgt_type in _PARADATA_UNITA_TIPI
            or src in paradata_group_node_ids
            or tgt in paradata_group_node_ids
        )
        line_style = "dashed" if is_paradata else "line"
        for ls_el in edge_el.iter(f"{{{NS_Y}}}LineStyle"):
            ls_el.set("type", line_style)

    # --- 3. Cycle epoch row colors ----------------------------------------
    # Rows live inside <y:TableNode>/<y:Table>/<y:Rows>/<y:Row ...>.
    # Each row gets a background fill via <y:Property name="..."/>;
    # but yEd respects a default RowStyle on the TableNode. We attach
    # a per-row Style fragment with the palette colour.
    palette = _EPOCH_ROW_PALETTE
    rows = list(root.iter(f"{{{NS_Y}}}Row"))
    for i, row_el in enumerate(rows):
        color = palette[i % len(palette)]
        # Add or replace a Fill child on the Row element. yEd treats
        # the first <y:Fill> child of <y:Row> as the row background.
        existing_fill = row_el.find(f"{{{NS_Y}}}Fill")
        if existing_fill is not None:
            existing_fill.set("color", color)
            existing_fill.set("transparent", "false")
        else:
            fill_el = etree.SubElement(row_el, f"{{{NS_Y}}}Fill")
            fill_el.set("color", color)
            fill_el.set("transparent", "false")

    # --- 4. Embed legacy paradata SVG resources -------------------------
    # If we converted any ShapeNode → SVGNode in step 1+2, the produced
    # GraphML now references <y:SVGContent refid="N"/> for some N. yEd
    # resolves these against a sibling <y:Resources> block carried in a
    # <data key="..."> child of <graphml> with yfiles.type="resources".
    # Add the block (or extend an existing one) so the icons render.
    _ensure_resources_block(
        root, etree, NS_GRAPHML, NS_Y, needed_svg_refids)

    tree.write(str(xml_path), encoding="UTF-8", xml_declaration=True)


# Custom data-key names (must match the parser in graph_ingestor.py).
_PYARCHINIT_NODE_DATA_KEYS = (
    ("us", "pyarchinit.us"),
    ("area", "pyarchinit.area"),
    ("sito", "pyarchinit.sito"),
    ("unita_tipo", "pyarchinit.unita_tipo"),
    ("periodo_iniziale", "pyarchinit.periodo_iniziale"),
    ("fase_iniziale", "pyarchinit.fase_iniziale"),
    ("rapporti", "pyarchinit.rapporti"),
    ("d_stratigrafica", "pyarchinit.d_stratigrafica"),
    # AI08-F2 hotfix: also expose the interpretative description per US
    ("d_interpretativa", "pyarchinit.d_interpretativa"),
    ("documentazione", "pyarchinit.documentazione"),  # DOC URL/path
    # AI06: persist DB node_uuid so round-trip via GraphMLImporter
    # (which generates a fresh internal node_id) can still identify
    # the original us_table row for UPDATE selettivo.
    ("node_uuid", "pyarchinit.node_uuid"),
    # AI06 D.2: register the SQL-derived group_kind columns so
    # _inject_group_folders can emit a pyarchinit.<kind> data entry
    # on each group folder. The round-trip importer
    # (sql_apply_groups=True) reads these to discover which us_table
    # column to UPDATE.
    ("struttura", "pyarchinit.struttura"),
    ("attivita", "pyarchinit.attivita"),
    ("settore", "pyarchinit.settore"),
    ("ambient", "pyarchinit.ambient"),
    ("saggio", "pyarchinit.saggio"),
    ("quad_par", "pyarchinit.quad_par"),
    # AI08-F2 hotfix: per-US datazione_estesa resolved from
    # periodizzazione_table by (sito, periodo_iniziale, fase_iniziale).
    ("datazione_estesa", "pyarchinit.datazione_estesa"),
)
_PYARCHINIT_EPOCH_DATA_KEYS = (
    ("periodo", "pyarchinit.periodo"),
    ("fase", "pyarchinit.fase"),
    ("cron_iniziale", "pyarchinit.cron_iniziale"),
    ("cron_finale", "pyarchinit.cron_finale"),
    ("datazione_estesa", "pyarchinit.datazione_estesa"),
)


def _embed_pyarchinit_data_keys(graph, xml_path: Path) -> None:
    """Append custom <data> entries on each <node> in the produced
    GraphML so AI04's import path can recover the pyarchinit columns
    that s3dgraphy's GraphMLImporter would otherwise strip.

    Each attribute gets its own <key for="node" attr.name="…"/> at
    the document level, plus a per-node <data key="…">value</data>.
    """
    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # Build EMID → graph node lookup so we can pull attributes per node.
    emid_to_node = {}
    for n in graph.nodes:
        emid = getattr(n, "node_id", None)
        if emid:
            emid_to_node[emid] = n

    # Allocate fresh data-key ids that don't collide.
    used_ids = {k.get("id") for k in root.findall(f"{{{NS_GRAPHML}}}key")
                if k.get("id")}
    next_n = 0
    def _alloc_id() -> str:
        nonlocal next_n
        while f"d{next_n}" in used_ids:
            next_n += 1
        kid = f"d{next_n}"
        used_ids.add(kid)
        next_n += 1
        return kid

    # Register node-level keys
    node_attrname_to_keyid: dict[str, str] = {}
    for attr_name, attr_named in _PYARCHINIT_NODE_DATA_KEYS:
        kid = _alloc_id()
        node_attrname_to_keyid[attr_name] = kid
        key_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        key_el.set("for", "node")
        key_el.set("id", kid)
        key_el.set("attr.name", attr_named)
        key_el.set("attr.type", "string")
        # Insert after existing keys
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            existing_keys[-1].addnext(key_el)
        else:
            root.insert(0, key_el)

    # Register epoch-level keys (we'll write them on EpochNode shapes;
    # those are inside <y:Row> in the swimlane TableNode, but s3dgraphy
    # also emits them as separate <node> entries — we put data on both
    # via the same key set, applied conditionally below).
    epoch_attrname_to_keyid: dict[str, str] = {}
    for attr_name, attr_named in _PYARCHINIT_EPOCH_DATA_KEYS:
        kid = _alloc_id()
        epoch_attrname_to_keyid[attr_name] = kid
        key_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        key_el.set("for", "node")
        key_el.set("id", kid)
        key_el.set("attr.name", attr_named)
        key_el.set("attr.type", "string")
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            existing_keys[-1].addnext(key_el)
        else:
            root.insert(0, key_el)

    # ---- Epoch metadata block (#5 H.4 fix) ----
    # EpochNodes don't appear as separate <node> elements in s3dgraphy
    # output (they live inside the swimlane <y:TableNode>'s <y:Row>),
    # so per-node data keys can't reach them. Instead embed a single
    # JSON blob on the <graph> element listing every EpochNode's
    # periodo/fase/cron metadata, indexed by name. The AI04 hydrator
    # reads this and propagates back to graph.nodes by name match.
    import json as _json
    epoch_meta = []
    for n in graph.nodes:
        if type(n).__name__ != "EpochNode":
            continue
        nattrs = getattr(n, "attributes", None) or {}
        meta = {"name": getattr(n, "name", "")}
        for key in ("periodo", "fase", "cron_iniziale",
                    "cron_finale", "datazione_estesa"):
            if nattrs.get(key) is not None:
                meta[key] = str(nattrs[key])
        if getattr(n, "start_time", None) not in (None, 0, 0.0):
            meta.setdefault("cron_iniziale", str(int(n.start_time)))
        if getattr(n, "end_time", None) not in (None, 0, 0.0):
            meta.setdefault("cron_finale", str(int(n.end_time)))
        if len(meta) > 1:
            epoch_meta.append(meta)
    if epoch_meta:
        epochs_kid = _alloc_id()
        ekey_el = etree.Element(f"{{{NS_GRAPHML}}}key")
        ekey_el.set("for", "graph")
        ekey_el.set("id", epochs_kid)
        ekey_el.set("attr.name", "pyarchinit.epochs_meta")
        ekey_el.set("attr.type", "string")
        existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
        if existing_keys:
            existing_keys[-1].addnext(ekey_el)
        else:
            root.insert(0, ekey_el)
        # Find the top-level <graph> child to attach the data blob to
        graph_el = root.find(f"{{{NS_GRAPHML}}}graph")
        if graph_el is not None:
            ed = etree.SubElement(graph_el, f"{{{NS_GRAPHML}}}data")
            ed.set("key", epochs_kid)
            ed.text = _json.dumps(epoch_meta)

    # Walk every <node>, look up its EMID in emid_to_node, attach the
    # corresponding pyarchinit data values when present.
    known_emids = set(emid_to_node.keys())
    for node_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        emid = None
        for d_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            txt = (d_el.text or "").strip()
            if txt and txt in known_emids:
                emid = txt
                break
        if emid is None:
            continue
        n = emid_to_node[emid]
        attrs = getattr(n, "attributes", None) or {}
        # Choose the right attr-set based on node type
        is_epoch = type(n).__name__ == "EpochNode"
        if is_epoch:
            attrname_to_kid = epoch_attrname_to_keyid
            # Auto-derive periodo/fase from EpochNode.node_id when not
            # already in attrs (so our import side sees them).
            import re as _re_local
            tid = getattr(n, "node_id", "") or ""
            m = _re_local.match(
                r"^epoch_([^_]+)_(.+?)(_synthetic)?$", str(tid))
            if m:
                attrs = dict(attrs)
                attrs.setdefault("periodo", m.group(1))
                attrs.setdefault("fase", m.group(2))
            cron_ini = getattr(n, "start_time", None)
            cron_fin = getattr(n, "end_time", None)
            if cron_ini not in (None, 0, 0.0):
                attrs.setdefault("cron_iniziale", str(int(cron_ini)))
            if cron_fin not in (None, 0, 0.0):
                attrs.setdefault("cron_finale", str(int(cron_fin)))
            datazione = attrs.get("datazione_estesa") or getattr(n, "name", "")
            if datazione:
                attrs.setdefault("datazione_estesa", str(datazione))
        else:
            attrname_to_kid = node_attrname_to_keyid
            # DocumentNode: copy `url` field into a documentazione
            # attribute so the data-key emitter picks it up. AI04.1 #6.
            if type(n).__name__ == "DocumentNode":
                doc_url = (getattr(n, "url", None)
                           or attrs.get("url"))
                if doc_url and not attrs.get("documentazione"):
                    attrs = dict(attrs)
                    attrs["documentazione"] = str(doc_url)
        for attr_name, kid in attrname_to_kid.items():
            val = attrs.get(attr_name)
            if val is None or val == "":
                continue
            d = etree.SubElement(node_el, f"{{{NS_GRAPHML}}}data")
            d.set("key", kid)
            d.text = str(val)

    tree.write(str(xml_path), encoding="UTF-8", xml_declaration=True)


_PARADATA_INJECT_TYPES: frozenset[str] = frozenset({
    "AuthorNode", "LicenseNode", "EmbargoNode",
})
# Bug P (2026-05-15 v2 user feedback): DO NOT inject row-paradata
# (DocumentNode / CombinerNode / ExtractorNode / PropertyNode) via
# this post-processor — that appends them OUTSIDE the swimlane with
# no edges, which is the wrong UX for us_table records. Instead the
# projector creates them as StratigraphicNode-class instances with
# ``attributes['unita_tipo']`` set, so the GraphMLExporter renders
# them inside the swimlane like USV/SF/VSF and the rapporti edges
# get attached via the normal _enrich_into path.


def _clone_node_for_location(primary_node, location: str, idx: int,
                             canonical_uuid: str):
    """Return a deep-copy clone of ``primary_node`` placed in
    ``location`` folder.

    Used by ``_apply_yef_fan_out`` (yE-F design spec §6) to emit N
    visual yEd ``<node>`` copies per multi-folder paradata row.

    The clone:
      - Has node_id ``f"{canonical_uuid}_loc_{idx}"`` (unique within graph)
      - Inherits Python class (StratigraphicUnit subclass), name, description
      - Copies attributes dict with overrides:
          attivita = location
          _yef_canonical_uuid = canonical_uuid (for downstream resolver)
          _yef_is_copy = True (filter marker)
          node_uuid = canonical_uuid (round-trip identity in graphml output)

    Mutating the clone's attributes does NOT affect the primary
    (deep-copy semantics).
    """
    cls = type(primary_node)
    clone = cls(
        node_id=f"{canonical_uuid}_loc_{idx}",
        name=str(getattr(primary_node, "name", "")),
        description=str(getattr(primary_node, "description", "")),
    )
    base_attrs = getattr(primary_node, "attributes", None) or {}
    new_attrs = dict(base_attrs)
    new_attrs["attivita"] = location
    new_attrs["_yef_canonical_uuid"] = canonical_uuid
    new_attrs["_yef_is_copy"] = True
    new_attrs["node_uuid"] = canonical_uuid
    clone.attributes = new_attrs
    return clone


def _apply_yef_fan_out(graph) -> int:
    """yE-F render fan-out (design spec §6).

    For each StratigraphicUnit-class node with non-empty
    ``attributes['other_locations']``, emit N-1 visual copies via
    ``_clone_node_for_location``. The N copies (primary + secondaries)
    share the canonical ``pyarchinit.node_uuid`` data key for round-
    trip identity, but have distinct yEd ``<node>`` ids
    (``<canonical>_loc_<idx>``).

    Stashes ``graph.attributes['_yef_copies_by_canonical']`` =
    ``dict[canonical_uuid, list[primary_and_copies]]`` for the
    per-folder edge resolver (yE-F-D).

    Returns the number of copies created (0 if no yE-F rows in graph).
    Non-paradata rows and empty ``other_locations`` are ignored.
    """
    import json
    canonical_to_copies: dict[str, list] = {}
    copies_created = 0
    for n in list(graph.nodes):
        attrs = getattr(n, "attributes", None) or {}
        ol_raw = attrs.get("other_locations")
        if not ol_raw:
            continue
        try:
            secondary_locs = json.loads(ol_raw)
        except (ValueError, TypeError):
            continue
        if not isinstance(secondary_locs, list) or not secondary_locs:
            continue
        primary_uuid = n.node_id
        attrs["_yef_canonical_uuid"] = primary_uuid
        canonical_to_copies[primary_uuid] = [n]
        for idx, loc in enumerate(secondary_locs, start=1):
            copy = _clone_node_for_location(
                n, str(loc), idx, primary_uuid,
            )
            graph.add_node(copy)
            canonical_to_copies[primary_uuid].append(copy)
            copies_created += 1
    if not hasattr(graph, "attributes") or graph.attributes is None:
        graph.attributes = {}
    graph.attributes["_yef_copies_by_canonical"] = canonical_to_copies
    return copies_created


def _inject_isolated_paradata_nodes(paradata_nodes, xml_path: Path) -> None:
    """Append AuthorNode / LicenseNode / EmbargoNode entries to the
    GraphMLExporter output for site-level paradata that has no
    ParadataNodeGroup anchor.

    GraphMLExporter only renders paradata when it sits inside a
    ParadataNodeGroup attached to a stratigraphic unit. AI05's
    site-level paradata (D9 in spec — Author/License/Embargo apply
    to the site as a whole, not to specific US) gets silently
    dropped. This post-processor fixes that by re-injecting them
    post-export.

    Pass a snapshot of paradata nodes (list, not Graph) because the
    exporter mutates graph.nodes during export — by the time this
    runs, the original AuthorNode/LicenseNode/EmbargoNode entries
    are no longer in graph.nodes.

    Each injected node gets:
      - the existing EMID key for round-trip identity
      - the existing description key with `_s3d_node_type:<Type>`
        marker (so re-import recognises the subclass)
      - the existing nodegraphics key with a minimal yEd ImageNode
        + NodeLabel (display name)
      - the AI05 paradata_attrs JSON blob via key "pyarchinit.paradata_attrs"
    """
    # Defensive: also accept a Graph for backward compat.
    if hasattr(paradata_nodes, "nodes"):
        paradata_nodes = [
            n for n in paradata_nodes.nodes
            if type(n).__name__ in _PARADATA_INJECT_TYPES
        ]
    print(f"[ParadataInject] candidates: {len(paradata_nodes)}")
    if not paradata_nodes:
        return

    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    NS_Y = "http://www.yworks.com/xml/graphml"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # Resolve key IDs for the attr.names we need by scanning
    # registered <key> elements.
    attrname_to_kid: dict[str, str] = {}
    for k in root.findall(f"{{{NS_GRAPHML}}}key"):
        if k.get("for") != "node":
            continue
        attr_name = k.get("attr.name")
        yfiles_type = k.get("yfiles.type")
        if attr_name == "EMID":
            attrname_to_kid["EMID"] = k.get("id")
        elif attr_name == "description":
            attrname_to_kid["description"] = k.get("id")
        elif yfiles_type == "nodegraphics":
            attrname_to_kid["nodegraphics"] = k.get("id")
        elif attr_name == "pyarchinit.paradata_attrs":
            attrname_to_kid["paradata_attrs"] = k.get("id")
        elif attr_name == "pyarchinit.sito":
            attrname_to_kid["sito"] = k.get("id")
        elif attr_name == "pyarchinit.us":
            attrname_to_kid["us"] = k.get("id")
        elif attr_name == "pyarchinit.unita_tipo":
            attrname_to_kid["unita_tipo"] = k.get("id")
        elif attr_name == "pyarchinit.area":
            attrname_to_kid["area"] = k.get("id")

    # If essential keys are missing (shouldn't happen — they're
    # registered by GraphMLExporter + _embed_pyarchinit_data_keys),
    # bail out gracefully.
    if "EMID" not in attrname_to_kid or "nodegraphics" not in attrname_to_kid:
        return

    # Collect existing EMIDs in the output so we don't double-inject.
    existing_emids: set[str] = set()
    emid_kid = attrname_to_kid["EMID"]
    for node_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        for d_el in node_el.findall(f"{{{NS_GRAPHML}}}data"):
            if d_el.get("key") == emid_kid and d_el.text:
                existing_emids.add(d_el.text.strip())
                break

    # Find the <graph> element to append into.
    graph_el = root.find(f"{{{NS_GRAPHML}}}graph")
    if graph_el is None:
        return

    # Per-node-type yEd colour palette (matches em_visual_rules
    # paradata category by default — kept simple here).
    # Bug O (2026-05-15 user feedback): added row-paradata colours
    # roughly matching the EM 1.5 BPMN palette so they're visually
    # distinguishable in yEd after round-trip.
    type_colours = {
        "AuthorNode":    "#FFCCCC",
        "LicenseNode":   "#CCFFCC",
        "EmbargoNode":   "#CCCCFF",
        "DocumentNode":  "#FFFFCC",  # pale yellow — BPMN data object
        "CombinerNode":  "#FFE4B5",  # moccasin — combiner
        "ExtractorNode": "#E6E6FA",  # lavender — extractor
        "PropertyNode":  "#F0E68C",  # khaki — BPMN annotation
    }

    import json as _json
    injected = 0
    for node in paradata_nodes:
        emid = str(getattr(node, "node_id", "") or "")
        if not emid or emid in existing_emids:
            continue
        type_name = type(node).__name__
        display = str(getattr(node, "name", "") or type_name)

        n_el = etree.SubElement(graph_el, f"{{{NS_GRAPHML}}}node")
        n_el.set("id", emid)

        # EMID
        d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
        d.set("key", emid_kid)
        d.text = emid

        # description w/ round-trip marker
        if "description" in attrname_to_kid:
            d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
            d.set("key", attrname_to_kid["description"])
            d.text = f"_s3d_node_type:{type_name}"

        # nodegraphics — minimal yEd ImageNode w/ NodeLabel
        d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
        d.set("key", attrname_to_kid["nodegraphics"])
        img = etree.SubElement(d, f"{{{NS_Y}}}ImageNode")
        geom = etree.SubElement(img, f"{{{NS_Y}}}Geometry")
        geom.set("height", "30.0")
        geom.set("width", "30.0")
        geom.set("x", "0.0")
        geom.set("y", "0.0")
        fill = etree.SubElement(img, f"{{{NS_Y}}}Fill")
        fill.set("color", type_colours.get(type_name, "#CCCCCC"))
        fill.set("transparent", "false")
        bs = etree.SubElement(img, f"{{{NS_Y}}}BorderStyle")
        bs.set("color", "#000000")
        bs.set("type", "line")
        bs.set("width", "1.0")
        nl = etree.SubElement(img, f"{{{NS_Y}}}NodeLabel")
        nl.text = display

        # paradata_attrs JSON blob (AI05 round-trip channel)
        if "paradata_attrs" in attrname_to_kid:
            attrs = getattr(node, "attributes", None) or {}
            if attrs:
                _SKIP = {"original_id", "graph_id", "paradata_attrs"}
                clean = {k: v for k, v in attrs.items()
                         if k not in _SKIP and v not in (None, "")}
                if clean:
                    d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
                    d.set("key", attrname_to_kid["paradata_attrs"])
                    d.text = _json.dumps(clean, ensure_ascii=False)

        # sito for filter-on-import compat with AI04
        if "sito" in attrname_to_kid:
            attrs = getattr(node, "attributes", None) or {}
            sito = attrs.get("sito") if attrs else None
            if sito:
                d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
                d.set("key", attrname_to_kid["sito"])
                d.text = str(sito)

        # Bug O (2026-05-15 user feedback): row-paradata classes need
        # ``pyarchinit.us``, ``pyarchinit.unita_tipo``, ``pyarchinit.area``
        # data keys so re-import via GraphProjector picks them up by
        # composite (us, unita_tipo) key. Author/License/Embargo
        # nodes don't carry these (they're site-level metadata, not
        # us_table records), so we only emit when the attrs are
        # present.
        attrs = getattr(node, "attributes", None) or {}
        for extra_key in ("us", "unita_tipo", "area"):
            kid = attrname_to_kid.get(extra_key)
            val = attrs.get(extra_key)
            if kid and val not in (None, ""):
                d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
                d.set("key", kid)
                d.text = str(val)

        injected += 1

    print(f"[ParadataInject] injected {injected} paradata nodes "
          f"into {xml_path.name}")
    if injected:
        tree.write(str(xml_path), encoding="UTF-8",
                   xml_declaration=True, pretty_print=True)


_GROUP_INJECT_TYPE = "ActivityNodeGroup"


# AI06 dimension-keyed entries + AI07 kind-enum entries. Lookup order
# in _resolve_group_visual: try dimension first (e.g. "struttura"), then
# fall back to s3dgraphy LocationNodeGroup.kind enum value (e.g.
# "toponym"). The dimension-key entries match AI06+F2 exactly so
# AC-2 byte-identical regression stays green for all existing dims.
_GROUP_KIND_PALETTE: dict = {
    # AI06 + F2: pyarchinit dimension keys
    # group_kind     : (fill_rgba_50pct,    border_solid)
    "area":            ("#FFE0E680",         "#C84A5F"),
    "struttura":       ("#FFE6CC80",         "#C66B33"),
    "attivita":        ("#FFF5CC80",         "#A89A33"),
    "settore":         ("#E6FFCC80",         "#6BC633"),
    "ambient":         ("#CCFFE680",         "#33A86B"),
    "saggio":          ("#CCF5FF80",         "#3389A8"),
    "quad_par":        ("#E0CCFF80",         "#6633C6"),
    "adhoc":           ("#F5F5F580",         "#666666"),
    # AI07: s3dgraphy LocationNodeGroup.kind enum keys
    "toponym":         ("#E6E6FA80",         "#9370DB"),  # lavender / dark slate
    "study":           ("#FFFFE080",         "#888888"),  # ivory / mid grey
    "functional":      ("#E0FFFF80",         "#008B8B"),  # light cyan / dark cyan
}
_GROUP_DEFAULT_FILL = "#F5F5F580"
_GROUP_DEFAULT_BORDER = "#000000"


def _resolve_group_visual(
    group_kind: str | None = None,
    kind: str | None = None,
) -> tuple[str, str]:
    """Resolve fill + border for a group folder.

    Lookup order:
    1. dimension key (e.g. "struttura") — AI06 + F2 path, preserves
       byte-identical AC-2 baseline for all existing dimensions
    2. s3dgraphy LocationNodeGroup.kind enum (e.g. "toponym") — AI07
       fallback for nodes that have no dimension-key palette entry
    3. defaults (grey + black) — last resort
    """
    if group_kind and group_kind in _GROUP_KIND_PALETTE:
        return _GROUP_KIND_PALETTE[group_kind]
    if kind and kind in _GROUP_KIND_PALETTE:
        return _GROUP_KIND_PALETTE[kind]
    return (_GROUP_DEFAULT_FILL, _GROUP_DEFAULT_BORDER)


def _inject_other_locations_badges(
    us_other_locations: dict,
    xml_path: Path,
) -> None:
    """AI07/F1: render non-primary memberships as inline yEd NodeLabel
    badges below each US's main label, so the user can SEE the
    non-primary memberships in yEd directly without a custom Property
    Mapper.

    Format: a single sandwich-position NodeLabel reading
    ``also: <name> (<kind>), <name> (<kind>), ...``.

    yEd renders multiple NodeLabels per ShapeNode by stacking them
    according to ``modelName`` + ``modelPosition``. We use
    ``modelName="sandwich"`` ``modelPosition="s"`` to place the badge
    just below the existing main label.

    Args:
        us_other_locations: dict mapping us_emid → list of memberships
            (each: ``{"name", "kind", "group_uuid"}``).
        xml_path: path to the GraphML output to post-process.
    """
    if not us_other_locations:
        return

    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    NS_Y = "http://www.yworks.com/xml/graphml"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # EMID lookup (same pattern as _inject_other_locations_data)
    emid_kid = None
    for k in root.findall(f"{{{NS_GRAPHML}}}key"):
        if k.get("attr.name") == "EMID" and k.get("for") == "node":
            emid_kid = k.get("id")
            break
    if emid_kid is None:
        return

    emid_to_node_el: dict = {}
    for n_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        for d in n_el.findall(f"{{{NS_GRAPHML}}}data"):
            if d.get("key") == emid_kid and d.text:
                emid_to_node_el[d.text.strip()] = n_el

    badged = 0
    for us_emid, memberships in us_other_locations.items():
        n_el = emid_to_node_el.get(us_emid)
        if n_el is None:
            continue
        # Find the ShapeNode (US visual). May be inside a <data key=…>
        # block. Search any descendant ShapeNode.
        shape = n_el.find(f".//{{{NS_Y}}}ShapeNode")
        if shape is None:
            continue
        # Build the badge text
        parts = [
            f"{m.get('name','')} ({m.get('kind','')})"
            for m in memberships
            if m.get("name")
        ]
        if not parts:
            continue
        badge_text = "also: " + ", ".join(parts)
        # Append a NodeLabel under the existing one(s)
        label = etree.SubElement(shape, f"{{{NS_Y}}}NodeLabel")
        label.set("alignment", "center")
        label.set("autoSizePolicy", "content")
        label.set("fontFamily", "Dialog")
        label.set("fontSize", "9")
        label.set("fontStyle", "italic")
        label.set("hasBackgroundColor", "false")
        label.set("hasLineColor", "false")
        label.set("modelName", "sandwich")
        label.set("modelPosition", "s")
        label.set("textColor", "#666666")
        label.set("visible", "true")
        label.text = badge_text
        badged += 1
    print(f"[OtherLocationsBadges] rendered on {badged}/{len(us_other_locations)} US")

    tree.write(
        str(xml_path),
        encoding="UTF-8",
        xml_declaration=True,
        standalone=False,
    )


def _inject_other_locations_data(
    us_other_locations: dict,
    xml_path: Path,
) -> None:
    """AI07/F1 §5.4: emit `<data key="s3d:other_locations">` on US
    nodes for non-primary memberships.

    yEd folders can host a node under at most ONE parent (the primary
    membership). Other memberships are preserved on the US side as a
    JSON-serialised list under the ``s3d:other_locations`` data key,
    so downstream tools (yEd visual-rules badges, triplestore
    reconstruction) can recover them without folder re-parenting.

    Schema per entry: ``{"name": str, "kind": str, "group_uuid": str}``.

    Args:
        us_other_locations: dict mapping us_emid → list of memberships.
            Empty dict is a no-op.
        xml_path: path to the GraphML output to post-process.
    """
    if not us_other_locations:
        return

    try:
        from lxml import etree
    except ImportError:
        return

    import json as _json

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # Allocate a fresh data-key id and register it at document level.
    used_ids = {k.get("id") for k in root.findall(f"{{{NS_GRAPHML}}}key")
                if k.get("id")}
    next_n = 0
    while f"d{next_n}" in used_ids:
        next_n += 1
    other_kid = f"d{next_n}"

    key_el = etree.Element(f"{{{NS_GRAPHML}}}key")
    key_el.set("for", "node")
    key_el.set("id", other_kid)
    key_el.set("attr.name", "s3d:other_locations")
    key_el.set("attr.type", "string")
    # Insert after the last existing <key>
    existing_keys = root.findall(f"{{{NS_GRAPHML}}}key")
    if existing_keys:
        last = existing_keys[-1]
        last.addnext(key_el)
    else:
        root.insert(0, key_el)

    # Resolve EMID → node element (EMID is registered as a data key
    # by GraphMLExporter; iterate <data> children to find it).
    emid_kid = None
    for k in root.findall(f"{{{NS_GRAPHML}}}key"):
        if k.get("attr.name") == "EMID" and k.get("for") == "node":
            emid_kid = k.get("id")
            break

    if emid_kid is None:
        return  # GraphML doesn't carry EMID — can't anchor the data

    emid_to_node_el: dict = {}
    for n_el in root.iter(f"{{{NS_GRAPHML}}}node"):
        for d in n_el.findall(f"{{{NS_GRAPHML}}}data"):
            if d.get("key") == emid_kid and d.text:
                emid_to_node_el[d.text.strip()] = n_el

    injected = 0
    for us_emid, memberships in us_other_locations.items():
        n_el = emid_to_node_el.get(us_emid)
        if n_el is None:
            continue
        d = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
        d.set("key", other_kid)
        d.text = _json.dumps(memberships, ensure_ascii=False, sort_keys=True)
        injected += 1
    print(f"[OtherLocations] injected on {injected}/{len(us_other_locations)} US")

    tree.write(
        str(xml_path),
        encoding="UTF-8",
        xml_declaration=True,
        standalone=False,
    )


def _inject_group_folders(
    group_snapshot: list,
    members_map: dict,
    xml_path: Path,
) -> None:
    """Inject yEd folder nodes inside the TableNode for each group.

    Each ActivityNodeGroup with group_kind attribute becomes a
    <node yfiles.foldertype="group"> with a <y:GroupNode> realizer
    (dashed border, fill #F5F5F5, NodeLabel position=top with bg
    #EBEBEB) and a Geometry that spans the bounding box of all
    member US nodes.

    Member US <node> elements are RE-PARENTED from the TableNode
    swimlane to the new group folder's inner <graph>. Their
    original Geometry is preserved so they continue rendering in
    the correct epoch row.

    Pass a snapshot list (not a Graph) — by the time this runs,
    the exporter has mutated graph.nodes (same lesson as AI05
    _inject_isolated_paradata_nodes).
    """
    print(f"[GroupInject] candidates: {len(group_snapshot)}")
    if not group_snapshot:
        return

    try:
        from lxml import etree
    except ImportError:
        return

    NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
    NS_Y = "http://www.yworks.com/xml/graphml"
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    # Resolve key IDs needed for node re-creation
    attrname_to_kid: dict = {}
    # AI06 D.2: also map pyarchinit.<group_kind> keys so we can emit
    # a <data> entry on the folder identifying the SQL column group_kind
    # corresponds to. The round-trip importer (graph_ingestor with
    # sql_apply_groups=True) reads this back to know which us_table
    # column to UPDATE.
    _GROUP_KIND_COLS = frozenset({
        "area", "struttura", "attivita", "settore",
        "ambient", "saggio", "quad_par",
    })
    group_kind_to_kid: dict = {}
    for k in root.findall(f"{{{NS_GRAPHML}}}key"):
        if k.get("for") != "node":
            continue
        attr_name = k.get("attr.name")
        yfiles_type = k.get("yfiles.type")
        if attr_name == "EMID":
            attrname_to_kid["EMID"] = k.get("id")
        elif attr_name == "description":
            attrname_to_kid["description"] = k.get("id")
        elif yfiles_type == "nodegraphics":
            attrname_to_kid["nodegraphics"] = k.get("id")
        elif attr_name == "pyarchinit.sito":
            attrname_to_kid["sito"] = k.get("id")
        elif attr_name and attr_name.startswith("pyarchinit."):
            short = attr_name.split(".", 1)[1]
            if short in _GROUP_KIND_COLS:
                group_kind_to_kid[short] = k.get("id")

    if "nodegraphics" not in attrname_to_kid:
        return  # nothing we can do without nodegraphics key

    # Find the TableNode wrapper (epoch swimlane container).
    # In s3dgraphy GraphMLExporter output it's the top-level
    # yfiles.foldertype="group" containing <y:TableNode>.
    table_node_el = None
    table_inner_graph = None
    for n in root.iter(f"{{{NS_GRAPHML}}}node"):
        if n.get("yfiles.foldertype") != "group":
            continue
        # Look for TableNode realizer
        for d in n.findall(f"{{{NS_GRAPHML}}}data"):
            if d.find(f".//{{{NS_Y}}}TableNode") is not None:
                table_node_el = n
                table_inner_graph = n.find(f"{{{NS_GRAPHML}}}graph")
                break
        if table_node_el is not None:
            break

    if table_node_el is None or table_inner_graph is None:
        # No swimlane wrapper — fall back to root <graph>
        table_inner_graph = root.find(f"{{{NS_GRAPHML}}}graph")
        if table_inner_graph is None:
            return

    # Build EMID → element index for member lookup
    emid_kid = attrname_to_kid.get("EMID")
    emid_to_node_el: dict = {}
    if emid_kid:
        for n_el in table_inner_graph.iter(f"{{{NS_GRAPHML}}}node"):
            for d in n_el.findall(f"{{{NS_GRAPHML}}}data"):
                if d.get("key") == emid_kid and d.text:
                    emid_to_node_el[d.text.strip()] = n_el
                    break

    injected = 0
    for group_node in group_snapshot:
        group_uuid = getattr(group_node, "node_id", "")
        attrs = getattr(group_node, "attributes", None) or {}
        display_name = attrs.get("name") or getattr(group_node, "name", "")
        if not group_uuid or not display_name:
            continue

        # Find member US elements by EMID
        member_emids = members_map.get(group_uuid, [])
        member_els = [emid_to_node_el[e] for e in member_emids
                      if e in emid_to_node_el]
        if not member_els:
            continue  # nothing to render for this group

        # Compute bbox of member geometries (defensive: skip absent geom)
        xs, ys, x2s, y2s = [], [], [], []
        for me in member_els:
            geom = me.find(f".//{{{NS_Y}}}Geometry")
            if geom is None:
                continue
            try:
                gx = float(geom.get("x", "0"))
                gy = float(geom.get("y", "0"))
                gw = float(geom.get("width", "0"))
                gh = float(geom.get("height", "0"))
            except (TypeError, ValueError):
                continue
            xs.append(gx); ys.append(gy)
            x2s.append(gx + gw); y2s.append(gy + gh)
        if not xs:
            continue
        margin = 20.0
        bx = min(xs) - margin
        by = min(ys) - margin
        bw = (max(x2s) - min(xs)) + 2 * margin
        bh = (max(y2s) - min(ys)) + 2 * margin

        # Build the group folder element
        n_el = etree.SubElement(table_inner_graph, f"{{{NS_GRAPHML}}}node")
        n_el.set("id", f"grp_{group_uuid}")
        n_el.set("yfiles.foldertype", "group")

        # Description with round-trip marker
        if "description" in attrname_to_kid:
            d_desc = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
            d_desc.set("key", attrname_to_kid["description"])
            # AI07: use actual node class — LocationNodeGroup for the 6
            # spatial dims + toponym, ActivityNodeGroup for `attivita`.
            # Hardcoding it broke round-trip class detection on legacy
            # parsers (Group H smoke catch).
            d_desc.text = f"_s3d_node_type:{type(group_node).__name__}"

        # nodegraphics: ProxyAutoBoundsNode → Realizers → GroupNode
        d_gfx = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
        d_gfx.set("key", attrname_to_kid["nodegraphics"])
        proxy = etree.SubElement(d_gfx, f"{{{NS_Y}}}ProxyAutoBoundsNode")
        realizers = etree.SubElement(proxy, f"{{{NS_Y}}}Realizers")
        realizers.set("active", "0")
        gn = etree.SubElement(realizers, f"{{{NS_Y}}}GroupNode")

        geom = etree.SubElement(gn, f"{{{NS_Y}}}Geometry")
        geom.set("x", f"{bx:.4f}")
        geom.set("y", f"{by:.4f}")
        geom.set("width", f"{bw:.4f}")
        geom.set("height", f"{bh:.4f}")

        # AI08-F2: per-dimension palette lookup (D2-C). Default falls
        # back to AI06 grey + black for unknown group_kind values.
        group_kind = attrs.get("group_kind", "")
        fill_rgba, border_rgb = _GROUP_KIND_PALETTE.get(
            group_kind, (_GROUP_DEFAULT_FILL, _GROUP_DEFAULT_BORDER))

        fill = etree.SubElement(gn, f"{{{NS_Y}}}Fill")
        fill.set("color", fill_rgba)
        fill.set("transparent", "false")

        bs = etree.SubElement(gn, f"{{{NS_Y}}}BorderStyle")
        bs.set("color", border_rgb)
        bs.set("type", "dashed")
        bs.set("width", "1.0")

        nl = etree.SubElement(gn, f"{{{NS_Y}}}NodeLabel")
        nl.set("alignment", "right")
        nl.set("autoSizePolicy", "node_width")
        nl.set("backgroundColor", "#EBEBEB")
        nl.set("fontFamily", "Dialog")
        nl.set("fontSize", "15")
        nl.set("modelName", "internal")
        nl.set("modelPosition", "t")
        nl.set("verticalTextPosition", "bottom")
        nl.set("visible", "true")
        nl.text = display_name

        shape = etree.SubElement(gn, f"{{{NS_Y}}}Shape")
        shape.set("type", "roundrectangle")
        state = etree.SubElement(gn, f"{{{NS_Y}}}State")
        state.set("closed", "false")
        state.set("innerGraphDisplayEnabled", "false")

        # sito data key
        sito = attrs.get("sito", "")
        if sito and "sito" in attrname_to_kid:
            d_sito = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
            d_sito.set("key", attrname_to_kid["sito"])
            d_sito.text = str(sito)

        # AI06 D.2: emit pyarchinit.<group_kind> data so the round-trip
        # importer (sql_apply_groups=True) knows which us_table column
        # to UPDATE for the members. Only for the 7 SQL-derived basic
        # kinds; ad-hoc folders carry no kind data and are skipped on
        # import (see graph_ingestor populate_list).
        gkind = attrs.get("group_kind", "")
        if gkind and gkind in group_kind_to_kid:
            d_kind = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}data")
            d_kind.set("key", group_kind_to_kid[gkind])
            d_kind.text = str(display_name)

        # Inner <graph> element + re-parent member US elements
        inner = etree.SubElement(n_el, f"{{{NS_GRAPHML}}}graph")
        inner.set("id", f"grp_{group_uuid}:")
        inner.set("edgedefault", "directed")
        for me in member_els:
            # Detach from current parent and append to inner
            parent = me.getparent()
            if parent is not None:
                parent.remove(me)
            inner.append(me)

        injected += 1

    print(f"[GroupInject] injected {injected} group folders")
    if injected:
        tree.write(str(xml_path), encoding="UTF-8",
                   xml_declaration=True, pretty_print=True)


def export_graphml(
    db_path,
    mapping: str,
    output_path,
    *,
    site_filter: Optional[str] = None,
    persist_auxiliary: bool = False,
    language: str = "it",
    groups: list = None,                  # NEW (AI06)
    primary_priority: list = None,        # NEW (AI07)
) -> ExportResult:
    """Run PyArchInitImporter → optional site filter → GraphMLExporter.

    PG-B (5.7.1-alpha): ``db_path`` accepts ``Path | DbHandle | str``
    via the ``_resolve_db_handle`` shim from Foundation. Backward
    compat preserved for legacy callers passing a Path.

    Args:
        db_path: Path | DbHandle | str — resolved by _resolve_db_handle
            shim. Legacy callers passing a plain ``Path`` or ``str``
            file path continue to work unchanged.
        mapping: name of the s3dgraphy mapping to use, e.g. "pyarchinit".
        output_path: filesystem path where to write the GraphML.
        site_filter: optional `sito` value to restrict the export.
        persist_auxiliary: bake (True) vs volatile (False) auxiliary
            data policy. Default False (volatile) per Spec D6.
        language: 2-letter QGIS locale code used to localize US/USM
            display labels (Italian by default). EM-canonical types
            (USVs/USVn/SF/...) are language-neutral and unaffected.
        primary_priority: AI07 — optional list of dimension names
            ordered from highest to lowest priority for the
            ``is_primary`` selection on is_in_location edges. When
            None, ``DEFAULT_PRIMARY_PRIORITY`` is used (struttura first).
            Toponym is always excluded from primary.

    Returns:
        ExportResult with metrics + warnings.

    Raises:
        EmptyGraphError: if the (filtered) graph has no nodes.
        GraphMLExportError(stage=...): wraps any failure in import,
            filter, export or write stages.
    """
    output_path = Path(output_path)

    # Stage 1: import + enrichment via GraphProjector (Strategy A,
    # AI05 Group C). The standalone `_enrich_pyarchinit_graph` was
    # deleted; its body now lives inside
    # :py:meth:`GraphProjector._enrich_into`. We pass
    # ``include_paradata=True`` so the green Extended Matrix export
    # button merges any Author/License/Embargo nodes the user
    # authored via the "Manage paradata" dialog. The merge is a
    # no-op when no paradata.graphml exists next to the DB — so
    # AC-2 fixtures (which don't ship a paradata file) stay
    # byte-identical.
    # ``strict_schema=False`` is passed so AC-2 fixtures (pre-AI05
    # migration, no us_table.node_uuid column) keep round-tripping
    # without applying the migration; node_uuid is only needed by
    # AI04's GraphIngestor, never by AI03's GraphML export.
    try:
        from .graph_projector import GraphProjector
        sito_for_projection = site_filter or _read_first_sito(db_path)
        print(f"[ExportGraphML] populate_graph(sito={sito_for_projection!r}, "
              f"include_paradata=True) — AI05 fix b2af31f4")
        graph = GraphProjector().populate_graph(
            db_path,
            sito=sito_for_projection,
            include_paradata=True,
            strict_schema=False,
            groups=groups,                # NEW (AI06)
            primary_priority=primary_priority,   # NEW (AI07)
        )
        para_count = sum(1 for n in graph.nodes
                         if type(n).__name__ in
                         ("AuthorNode", "LicenseNode", "EmbargoNode"))
        print(f"[ExportGraphML] post-merge: {len(graph.nodes)} nodes, "
              f"{para_count} paradata")
    except Exception as e:
        raise GraphMLExportError("import", e) from e

    # yE-F fan-out (design spec §6): emit N visual copies per
    # multi-folder paradata row. Must run AFTER populate_graph
    # (which propagates other_locations into node.attributes) and
    # BEFORE _filter_by_site (so sito-filtering keeps the copies).
    try:
        copies_created = _apply_yef_fan_out(graph)
        if copies_created:
            print(
                f"[ExportGraphML] yE-F fan-out emitted {copies_created} "
                f"visual copies"
            )
    except Exception as exc:
        print(f"[ExportGraphML] yE-F fan-out skipped: {exc}")

    # Capture paradata snapshot BEFORE the site filter — the AI04
    # `_filter_by_site` only retains StratigraphicNode + EpochNode
    # (it doesn't know about AI05 paradata classes), so it drops
    # isolated AuthorNode/LicenseNode/EmbargoNode. Stage 4d below
    # re-injects from this snapshot. AI05 site-level paradata (D9)
    # applies to the whole site unconditionally — no per-node
    # filtering is appropriate for them.
    _paradata_snapshot = [
        n for n in graph.nodes
        if type(n).__name__ in _PARADATA_INJECT_TYPES
    ]
    print(f"[ExportGraphML] paradata snapshot: {len(_paradata_snapshot)}")

    # AI06: capture group snapshot BEFORE Stage 2 _filter_by_site,
    # which retains only StratigraphicNode + EpochNode and would
    # drop our ActivityNodeGroup instances. Same lesson as AI05
    # paradata snapshot.
    # AI07: also accept LocationNodeGroup (spatial dims dispatch)
    # and is_in_location edges. The downstream _inject_group_folders
    # is class-agnostic — it reads attrs["group_kind"] for palette
    # lookup, and Group C's _merge_groups stamps that attribute on
    # both classes uniformly.
    _GROUP_NODE_CLASSES = ("ActivityNodeGroup", "LocationNodeGroup")
    _GROUP_EDGE_TYPES = ("is_in_activity", "is_in_location")
    _group_snapshot = [
        n for n in graph.nodes
        if type(n).__name__ in _GROUP_NODE_CLASSES
        and (getattr(n, "attributes", None) or {}).get("group_kind")
    ]
    # Build members_map (group_uuid → [us_emid, ...]) from the
    # is_in_activity / is_in_location edges currently in the graph.
    # AI07/F1: only include edges with is_primary=True (or no is_primary
    # attribute, for AI06 backward compat). yEd folders can host a node
    # under at most ONE parent — non-primary memberships are tracked
    # separately for the upcoming `s3d:other_locations` US-side data
    # emission, NOT for folder re-parenting. This eliminates the empty
    # secondary folders ("area B with 0 children") that confused users
    # in 5.5.2-alpha multi-dim exports.
    _group_member_uuids = {
        gn.node_id: [] for gn in _group_snapshot
    }
    # AI07/F1 §5.4: non-primary memberships per US, surfaced via
    # `<data key="s3d:other_locations">` on the US node element so
    # downstream tools (yEd visual rules, triplestore reconstruction)
    # can recover them without folder re-parenting.
    # Map: us_emid → [{"name", "kind", "group_uuid"}, ...]
    _us_other_locations: dict[str, list[dict]] = {}
    _id_to_group_node = {gn.node_id: gn for gn in _group_snapshot}
    for edge in list(getattr(graph, "edges", []) or []):
        if (getattr(edge, "edge_type", "") in _GROUP_EDGE_TYPES
                and edge.edge_target in _group_member_uuids):
            edge_attrs = getattr(edge, "attributes", None) or {}
            if edge_attrs.get("is_primary", True) is True:
                _group_member_uuids[edge.edge_target].append(edge.edge_source)
            else:
                # Non-primary — record on the US side for s3d:other_locations.
                gn = _id_to_group_node.get(edge.edge_target)
                if gn is None:
                    continue
                gattrs = getattr(gn, "attributes", None) or {}
                _us_other_locations.setdefault(edge.edge_source, []).append({
                    "name": gattrs.get("name") or getattr(gn, "name", "") or "",
                    "kind": getattr(gn, "kind", None) or "activity",
                    "group_uuid": edge.edge_target,
                })
    print(f"[ExportGraphML] group snapshot: "
          f"{len(_group_snapshot)} groups; "
          f"non-primary US memberships: {len(_us_other_locations)}")

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

    # Stage 4b: pyarchinit-specific visual overrides on the produced
    # XML. The s3dgraphy GraphMLExporter writes a graph where every
    # node is a white rectangle with a dark-red border and the label
    # is just the bare US number; this post-processor restores the
    # EM 1.5 look (per-type fill/border/shape, language-aware
    # "US 36" / "USM 3" / "USVs 4" labels, distinct epoch row colors).
    # Treated as best-effort — failures here are logged through
    # graph.warnings but do NOT fail the export, since the file is
    # already structurally valid.
    try:
        _apply_pyarchinit_visual_overrides(
            graph, output_path, language=language)
    except Exception as e:  # pragma: no cover (defensive)
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"Visual post-processing skipped: {type(e).__name__}: {e}")

    # Stage 4c: embed pyarchinit-specific attributes as GraphML data
    # keys so AI04's GraphIngestor can recover them on round-trip.
    # s3dgraphy's GraphMLImporter strips any attribute it doesn't
    # recognise; emitting under our own data-key namespace lets us
    # parse them back via lxml directly in graph_ingestor.
    try:
        _embed_pyarchinit_data_keys(graph, output_path)
    except Exception as e:  # pragma: no cover (defensive)
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"Data-key embedding skipped: {type(e).__name__}: {e}")

    # Stage 4d: inject isolated paradata nodes (AuthorNode /
    # LicenseNode / EmbargoNode) that GraphMLExporter silently
    # drops when they're not anchored to a ParadataNodeGroup. AI05
    # site-level paradata (D9) lives on the graph with no edges to
    # specific stratigraphic units, so we append them post-export
    # via a dedicated post-processor. Use the pre-export snapshot
    # because the exporter mutates graph.nodes during export.
    try:
        _inject_isolated_paradata_nodes(
            _paradata_snapshot, output_path)
    except Exception as e:  # pragma: no cover (defensive)
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"Paradata injection skipped: {type(e).__name__}: {e}")

    # Stage 4e: inject group folders (AI06). yEd folder nodes
    # nesting member US, with EM canonical visual style. Default
    # no-op when _group_snapshot is empty (D7-A).
    try:
        _inject_group_folders(
            _group_snapshot, _group_member_uuids, output_path)
    except Exception as e:  # pragma: no cover (defensive)
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"Group folder injection skipped: "
                f"{type(e).__name__}: {e}")

    # Stage 4f (AI07/F1 §5.4): emit `<data key="s3d:other_locations">`
    # on US nodes for non-primary memberships. Default no-op when
    # _us_other_locations is empty (single-dim or AI06 baseline).
    try:
        _inject_other_locations_data(
            _us_other_locations, output_path)
    except Exception as e:  # pragma: no cover (defensive)
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"s3d:other_locations injection skipped: "
                f"{type(e).__name__}: {e}")

    # Stage 4g (AI07/F1): inline NodeLabel badges below each US's
    # main label so the user can SEE the non-primary memberships in
    # yEd directly without configuring a Property Mapper.
    try:
        _inject_other_locations_badges(
            _us_other_locations, output_path)
    except Exception as e:  # pragma: no cover (defensive)
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"s3d:other_locations badge rendering skipped: "
                f"{type(e).__name__}: {e}")

    # Build the result. Counts come from the post-export graph.
    from s3dgraphy.nodes.epoch_node import EpochNode
    epoch_count = sum(
        1 for n in graph.nodes if isinstance(n, EpochNode))

    warnings = list(getattr(graph, "warnings", []))

    # tred_removed_edges via arithmetic fallback (see comment above):
    # number of temporal-input edges minus number of is_after edges
    # actually emitted by the exporter after transitive reduction.
    # Cap at 0 to defend against off-by-one or unforeseen exporter
    # heuristics — never report a negative reduction.
    #
    # CYCLE FALLBACK: when the TemporalInferenceEngine detects a cycle,
    # it skips reduction and emits ALL input edges verbatim. The
    # arithmetic difference would then equal the number of edges the
    # engine derived from topological-only relations (cuts/fills/...)
    # which is misleading — no reduction actually happened. Detect
    # the cycle warning and report 0.
    cycle_detected = any(
        "cycle" in str(w).lower() for w in warnings
    )
    if cycle_detected:
        tred_removed = 0
    else:
        try:
            emitted_xml = output_path.read_text(encoding="utf-8")
            is_after_emitted = _count_is_after_edges_in_xml(emitted_xml)
            tred_removed = max(0, temporal_input_count - is_after_emitted)
        except OSError:
            tred_removed = 0

    return ExportResult(
        output_path=str(output_path),
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        epoch_count=epoch_count,
        tred_removed_edges=tred_removed,
        warnings=warnings,
    )
