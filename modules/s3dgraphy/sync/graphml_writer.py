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

import ast
import re
import sqlite3
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


# PyArchInit `rapporti` strings (Italian + English) → s3dgraphy
# topological edge types. The s3dgraphy 0.1.40 PyArchInitImporter
# only handles the us_table column→property mapping; it does NOT
# parse the rapporti JSON column nor read periodizzazione_table.
# So the orchestrator below performs the missing enrichment by
# reading those tables directly and adding edges/EpochNodes that
# the GraphMLExporter + TemporalInferenceEngine then consume.
_RAPPORTI_TO_EDGE_TYPE = {
    # Italian
    "copre": "overlies",
    "coperto da": "is_overlain_by",
    "taglia": "cuts",
    "tagliato da": "is_cut_by",
    "riempie": "fills",
    "riempito da": "is_filled_by",
    "uguale a": "is_physically_equal_to",
    "si lega a": "is_bonded_to",
    "si appoggia a": "abuts",
    "gli si appoggia": "is_abutted_by",
    # English
    "covers": "overlies",
    "covered by": "is_overlain_by",
    "cuts": "cuts",
    "cut by": "is_cut_by",
    "fills": "fills",
    "filled by": "is_filled_by",
    "same as": "is_physically_equal_to",
    "bonds with": "is_bonded_to",
    "abuts": "abuts",
}


# pyarchinit-specific shorthand tokens for relations between non-US/USM
# units (USVs/USVn/SF/CON/Combinar/Extractor/property/DOC). The user
# enters these in the rapporti field as ">", ">>", "<", "<<".
#
# Convention (per the pyarchinit author, May 2026):
#  - single arrow ">" / "<" carries simple temporal precedence
#  - double arrow ">>" / "<<" carries paradata-style data flow
#    (Extractor/Combinar/property/DOC chains)
#
# Each entry returns (edge_type, swap) where swap=True means we emit
# the edge with source and target swapped relative to how the user
# wrote it. Rationale: ">" reads as "source is older than target",
# which in EM is encoded as `target is_after source` — so we swap.
# Similarly for ">>" → "target extracted_from source" (target depends
# on source's data).
_RAPPORTI_SHORTHAND = {
    ">":  ("is_after", True),            # A > B  ⇒  B is_after A
    "<":  ("is_after", False),           # A < B  ⇒  A is_after B
    # `>>` / `<<` are pyarchinit's data-flow shorthand. Semantically
    # this is `extracted_from` / `combines`, but those edge_types are
    # filtered out of the GraphMLExporter output (it expects paradata
    # edges to live inside a ParadataNodeGroup structure, which
    # pyarchinit-imported nodes do not produce). `generic_connection`
    # bypasses the filter and renders as a labelled edge in yEd —
    # users still see the relationship, just with a generic visual.
    ">>": ("generic_connection", True),  # A >> B  ⇒  B generic_connection A
    "<<": ("generic_connection", False), # A << B  ⇒  A generic_connection B
}


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


def _enrich_pyarchinit_graph(graph, db_path: Path) -> None:
    """Bake epoch swimlanes + topological rapporti edges into *graph*.

    The vendored s3dgraphy 0.1.40 PyArchInitImporter is incomplete:
    it imports only US columns mapped in the JSON mapping (us_table
    → StratigraphicNode + PropertyNodes), and does NOT:

      * read periodizzazione_table → create EpochNodes
      * add `has_first_epoch` edges from each US to its periodo
      * parse the `rapporti` JSON column → create topological edges

    Without those, the GraphMLExporter has no input for swimlanes
    and no input for the TemporalInferenceEngine — both AI03
    acceptance criteria fail. We perform the enrichment here, in
    the orchestrator's filter+enrich layer, so the bridge stays a
    one-call surface and so the test fixture remains pure
    pyArchInit-shaped data.

    Mutates the graph in place. No-op if the DB file lacks the
    expected tables.
    """
    from s3dgraphy.nodes.epoch_node import EpochNode

    # Build a name → StratigraphicNode index over the existing
    # importer-emitted nodes; rapporti reference US by their numeric
    # name, not by the importer-generated UUIDs.
    strat_by_name = {}
    for n in graph.nodes:
        # Importer emits `name = str(us_number)` for stratigraphic
        # rows. Skip PropertyNodes (they have a name like
        # "Interpretation" rather than the US id).
        nclass = type(n).__name__
        if nclass.startswith("Stratigraphic") or nclass == "USNode":
            strat_by_name[str(n.name)] = n

    if not strat_by_name:
        return  # nothing to enrich

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
    except sqlite3.Error:
        return

    try:
        # ---- 1. EpochNodes from periodizzazione_table -------------
        # Schema columns vary slightly across pyArchInit releases;
        # we read defensively. Each (periodo, fase) is one epoch.
        epoch_by_key = {}  # (periodo:int, fase:str) -> EpochNode
        try:
            cursor.execute(
                "SELECT periodo, fase, cron_iniziale, cron_finale, "
                "descrizione FROM periodizzazione_table"
            )
            for periodo, fase, cron_ini, cron_fin, descr in cursor.fetchall():
                if periodo is None:
                    continue
                key = (int(periodo), str(fase) if fase is not None else "")
                node_id = f"epoch_{key[0]}_{key[1]}"
                # Skip if already present (idempotent on repeat
                # invocation in single-graph mode).
                if graph.find_node_by_id(node_id) is not None:
                    epoch_by_key[key] = graph.find_node_by_id(node_id)
                    continue
                start = float(cron_ini) if cron_ini is not None else 0.0
                end = float(cron_fin) if cron_fin is not None else 0.0
                label = descr or f"Period {key[0]} Phase {key[1]}"
                # Cycle a pastel palette across epochs so each
                # swimlane row renders in a distinct background colour.
                # The s3dgraphy EpochSwimlanesGenerator
                # (`epoch_generator.py:360`) honours `epoch.color` when
                # it is not the default `#FFFFFF`; without an explicit
                # color it falls back to a single `#CCFFCC` for every
                # row, which is what the user reported as "tutti
                # verdino".
                row_color = _EPOCH_ROW_PALETTE[
                    len(epoch_by_key) % len(_EPOCH_ROW_PALETTE)]
                ep = EpochNode(
                    node_id=node_id,
                    name=str(label),
                    start_time=start,
                    end_time=end,
                    color=row_color,
                )
                graph.add_node(ep)
                epoch_by_key[key] = ep
        except sqlite3.Error:
            pass  # missing table is tolerated; epoch_count just stays 0

        # ---- 2. has_first_epoch edges and rapporti edges ----------
        # Also propagate `sito` and `area` to attributes so
        # _filter_by_site can match — the upstream PyArchInitImporter
        # mapping JSON only emits 5 columns and `sito` is not one of
        # them, leaving us_node.attributes empty post-import.
        try:
            cursor.execute(
                "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                "fase_iniziale, rapporti FROM us_table"
            )
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []

        edge_seq = 0
        for (us_val, sito, area, unita_tipo, periodo_ini, fase_ini,
             rapporti_raw) in rows:
            us_name = str(us_val) if us_val is not None else None
            if not us_name or us_name not in strat_by_name:
                continue
            us_node = strat_by_name[us_name]

            # Propagate identity attributes so site/area filters work
            # and so the post-processor can drive per-type styling.
            if sito is not None:
                us_node.attributes["sito"] = str(sito)
            if area is not None:
                us_node.attributes["area"] = str(area)
            if unita_tipo is not None:
                us_node.attributes["unita_tipo"] = str(unita_tipo)

            # 2a. has_first_epoch edge
            if periodo_ini is not None:
                try:
                    p_int = int(periodo_ini)
                except (TypeError, ValueError):
                    p_int = None
                if p_int is not None:
                    f_str = (str(fase_ini) if fase_ini is not None else "")
                    epoch = epoch_by_key.get((p_int, f_str))
                    # If exact (periodo, fase) not found, fall back to
                    # any epoch with the same periodo (some fixtures
                    # store fase as int, others as str).
                    if epoch is None:
                        for (p, _f), e in epoch_by_key.items():
                            if p == p_int:
                                epoch = e
                                break
                    if epoch is not None:
                        edge_id = f"hfe_{us_node.node_id}_{epoch.node_id}"
                        if graph.find_edge_by_id(edge_id) is None:
                            graph.add_edge(
                                edge_id=edge_id,
                                edge_source=us_node.node_id,
                                edge_target=epoch.node_id,
                                edge_type="has_first_epoch",
                            )

            # 2b. rapporti → topological edges
            if not rapporti_raw or rapporti_raw == "[]":
                continue
            try:
                rapporti = ast.literal_eval(rapporti_raw)
            except (ValueError, SyntaxError):
                continue
            if not isinstance(rapporti, list):
                continue
            for rapporto in rapporti:
                if not isinstance(rapporto, list) or len(rapporto) < 2:
                    continue
                # Preserve case for the shorthand tokens (>, >>, <, <<);
                # the named relations (copre/cuts/...) are case-folded.
                rel_raw = str(rapporto[0]).strip()
                rel_type_named = rel_raw.lower()
                target_us = str(rapporto[1]).strip()
                target_node = strat_by_name.get(target_us)
                if target_node is None:
                    continue

                # Try named-relation table first, then shorthand tokens.
                edge_type = _RAPPORTI_TO_EDGE_TYPE.get(rel_type_named)
                swap = False
                if edge_type is None:
                    shorthand = _RAPPORTI_SHORTHAND.get(rel_raw)
                    if shorthand is None:
                        continue
                    edge_type, swap = shorthand

                src_node, dst_node = (
                    (target_node, us_node) if swap
                    else (us_node, target_node)
                )
                edge_seq += 1
                edge_id = (f"rap_{src_node.node_id}_{dst_node.node_id}_"
                           f"{edge_type}_{edge_seq}")
                if graph.find_edge_by_id(edge_id) is None:
                    graph.add_edge(
                        edge_id=edge_id,
                        edge_source=src_node.node_id,
                        edge_target=dst_node.node_id,
                        edge_type=edge_type,
                    )
    finally:
        conn.close()


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

# Style table: per unita_tipo → (fill, border, border_width,
# border_style, shape). Calibrated against the canonical
# `Extended Matrix palette v.1.5dev1.graphml` published by the EM-tools
# project; pyarchinit-specific deviation: USM gets a grey fill so it
# is immediately distinguishable from US in the swimlane (the EM
# canonical palette uses identical fills for both).
_VISUAL_BY_UNITA_TIPO = {
    # Stratigraphic core (red border family — #9B3333)
    "US":   {"fill": "#FFFFFF", "border": "#9B3333", "width": "4.0",
             "style": "line", "shape": "rectangle"},
    "USM":  {"fill": "#C0C0C0", "border": "#9B3333", "width": "4.0",
             "style": "line", "shape": "rectangle"},
    "USN":  {"fill": "#FFFFFF", "border": "#9B3333", "width": "4.0",
             "style": "line", "shape": "ellipse"},  # negative SU
    "TSU":  {"fill": "#FFFFFF", "border": "#9B3333", "width": "4.0",
             "style": "dashed", "shape": "roundrectangle"},
    # Documentary (orange border)
    "USD":  {"fill": "#FFFFFF", "border": "#D86400", "width": "4.0",
             "style": "line", "shape": "roundrectangle"},
    # Structural Virtual (blue border, BLACK fill per EM canonical)
    "USVs": {"fill": "#000000", "border": "#248FE7", "width": "4.0",
             "style": "line", "shape": "parallelogram"},
    # Non-Structural Virtual (green border, BLACK fill per EM canonical)
    "USVn": {"fill": "#000000", "border": "#31792D", "width": "4.0",
             "style": "line", "shape": "hexagon"},
    # Special Find (yellow border)
    "SF":   {"fill": "#FFFFFF", "border": "#D8BD30", "width": "4.0",
             "style": "line", "shape": "octagon"},
    # Virtual Special Find (olive border, BLACK fill)
    "VSF":  {"fill": "#000000", "border": "#B19F61", "width": "4.0",
             "style": "line", "shape": "octagon"},
    # Working Unit (green border family)
    "UL":   {"fill": "#FFFFFF", "border": "#31792D", "width": "4.0",
             "style": "line", "shape": "octagon"},
    # Continuity (small dark dot)
    "CON":  {"fill": "#000000", "border": "#000000", "width": "2.0",
             "style": "line", "shape": "ellipse"},
    # Documents and paradata-tooling shapes — pyarchinit-specific
    # since these are not nodes in the canonical EM palette.
    "DOC":  {"fill": "#F0E68C", "border": "#806040", "width": "2.0",
             "style": "line", "shape": "roundrectangle"},
    "EXT":  {"fill": "#F0E68C", "border": "#806040", "width": "2.0",
             "style": "line", "shape": "roundrectangle"},
    "Extractor": {"fill": "#F0E68C", "border": "#806040", "width": "2.0",
                  "style": "line", "shape": "roundrectangle"},
    "Combinar":  {"fill": "#F0E68C", "border": "#806040", "width": "2.0",
                  "style": "line", "shape": "trapezoid"},
    "property":  {"fill": "#FFFFFF", "border": "#888888", "width": "2.0",
                  "style": "line", "shape": "ellipse"},
    "SUS":  {"fill": "#FFFFFF", "border": "#9B3333", "width": "4.0",
             "style": "line", "shape": "rectangle"},
}

# `_EPOCH_ROW_PALETTE` is defined earlier (above _enrich_pyarchinit_graph)
# so that the enrichment step can assign per-epoch colors before export.


def _resolve_display_abbrev(unita_tipo: str, language: str) -> str:
    """Return the language-aware display string for a unita_tipo.

    US/USM are localized via _LOCALIZED_US_USM. Every other EM type is
    canonical and returned verbatim.
    """
    if unita_tipo == "US":
        return _LOCALIZED_US_USM.get(language, ("US", "USM"))[0]
    if unita_tipo == "USM":
        return _LOCALIZED_US_USM.get(language, ("US", "USM"))[1]
    return unita_tipo


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
        unita_tipo = getattr(n, "attributes", {}).get("unita_tipo")
        meta_by_emid[emid] = {
            "unita_tipo": unita_tipo,
            "name": getattr(n, "name", ""),
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
    for node_el in root.iter(f"{{{NS_GRAPHML}}}node"):
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
        visual = _VISUAL_BY_UNITA_TIPO.get(unita_tipo)
        display_abbrev = _resolve_display_abbrev(unita_tipo, language)

        # Patch the ShapeNode block, if any
        for shape_el in node_el.iter(f"{{{NS_Y}}}ShapeNode"):
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
            # Prefix the label with the display abbreviation.
            # When the fill is dark (e.g. USVs/USVn/VSF black fill per
            # EM 1.5 canon), the label must use white text to stay
            # readable; otherwise stay with the default black.
            label_el = shape_el.find(f"{{{NS_Y}}}NodeLabel")
            if label_el is not None and label_el.text:
                bare = label_el.text.strip()
                if bare and not bare.startswith(display_abbrev):
                    label_el.text = f"{display_abbrev} {bare}"
                if visual and visual.get("fill") == "#000000":
                    label_el.set("textColor", "#FFFFFF")

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

    tree.write(str(xml_path), encoding="UTF-8", xml_declaration=True)


def export_graphml(
    db_path,
    mapping: str,
    output_path,
    *,
    site_filter: Optional[str] = None,
    persist_auxiliary: bool = False,
    language: str = "it",
) -> ExportResult:
    """Run PyArchInitImporter → optional site filter → GraphMLExporter.

    Args:
        db_path: filesystem path to the SQLite DB (str or Path).
        mapping: name of the s3dgraphy mapping to use, e.g. "pyarchinit".
        output_path: filesystem path where to write the GraphML.
        site_filter: optional `sito` value to restrict the export.
        persist_auxiliary: bake (True) vs volatile (False) auxiliary
            data policy. Default False (volatile) per Spec D6.
        language: 2-letter QGIS locale code used to localize US/USM
            display labels (Italian by default). EM-canonical types
            (USVs/USVn/SF/...) are language-neutral and unaffected.

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
        # Enrichment: bake epoch swimlanes + topological rapporti
        # edges that the upstream importer doesn't handle in 0.1.40.
        # Treated as part of the import stage for error attribution
        # because it's reading the same SQLite file the importer
        # opened.
        _enrich_pyarchinit_graph(graph, db_path)
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
