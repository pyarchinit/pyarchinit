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
# Per pyarchinit author (May 2026):
#   `>` and `>>` mean "the source COVERS the target" = source is above
#       in the stratigraphic matrix = source is_after target temporally.
#   `<` and `<<` mean "the source is COVERED by the target" = source is
#       below the target = target is_after source.
# The token A > B therefore produces edge `A is_after B` directly (no
# swap); A < B produces `B is_after A` (swap source/target).
# Single arrow `>` / `<` is used for Continuity (CON) and other
# stratigraphic-only relations; double arrow `>>` / `<<` is paradata
# data flow (DOC / Extractor / Combinar / property chains) and uses
# `generic_connection` because the writer filters extracted_from /
# combines as PARADATA_EDGE_TYPES (graphml_exporter.py:147).
_RAPPORTI_SHORTHAND = {
    ">":  ("is_after", False),           # A > B  ⇒  A is_after B
    "<":  ("is_after", True),            # A < B  ⇒  B is_after A
    ">>": ("generic_connection", False), # A >> B ⇒  A → B
    "<<": ("generic_connection", True),  # A << B ⇒  B → A
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


def _enrich_pyarchinit_graph(graph, db_path: Path,
                              sito_filter: Optional[str] = None) -> None:
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
            raw_rows = cursor.fetchall()
        except sqlite3.Error:
            raw_rows = []
        # Sort the periodizzazione rows by (periodo asc, fase asc) so
        # that when we add EpochNodes to the graph, ties on cron_iniziale
        # are broken by the natural phase numbering. The swimlane
        # generator at `epoch_generator.py:298` uses Python's stable
        # `sorted(..., reverse=True)`, so ties preserve insertion order:
        # phases inserted earlier here will end up above phases inserted
        # later in the rendered matrix when their cron_iniziale tie.
        def _sort_key(row):
            periodo, fase, *_ = row
            try:
                p_num = int(periodo) if periodo is not None else 0
            except (TypeError, ValueError):
                p_num = 0
            try:
                f_num = float(fase) if fase is not None else 0.0
            except (TypeError, ValueError):
                f_num = 0.0
            return (p_num, f_num)
        rows_sorted = sorted(raw_rows, key=_sort_key)

        try:
            for periodo, fase, cron_ini, cron_fin, descr in rows_sorted:
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
                # Stash periodo/fase on the EpochNode so the AI04
                # graphml round-trip can recover them via the
                # _embed_pyarchinit_data_keys post-processor (which
                # reads from `attributes` rather than parsing node_id —
                # node_id may be reassigned by GraphMLExporter).
                if not hasattr(ep, "attributes") or ep.attributes is None:
                    ep.attributes = {}
                ep.attributes["periodo"] = str(key[0])
                ep.attributes["fase"] = str(key[1])
                if cron_ini is not None:
                    ep.attributes["cron_iniziale"] = str(int(cron_ini))
                if cron_fin is not None:
                    ep.attributes["cron_finale"] = str(int(cron_fin))
                if descr:
                    ep.attributes["datazione_estesa"] = str(descr)
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
            if sito_filter is not None:
                cursor.execute(
                    "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                    "fase_iniziale, rapporti, d_stratigrafica "
                    "FROM us_table WHERE sito = ?",
                    (sito_filter,),
                )
            else:
                cursor.execute(
                    "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                    "fase_iniziale, rapporti, d_stratigrafica "
                    "FROM us_table"
                )
            rows = cursor.fetchall()
        except sqlite3.Error:
            rows = []

        for (us_val, sito, area, unita_tipo, periodo_ini, fase_ini,
             rapporti_raw, d_stratigrafica) in rows:
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
            # d_stratigrafica is the user-friendly description used as
            # the LABEL for property nodes (e.g. "Materiale").
            if d_stratigrafica is not None:
                us_node.attributes["d_stratigrafica"] = str(d_stratigrafica)

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
                # Stable ID keyed on (src, dst, edge_type): when both
                # endpoints declare the same relation in their rapporti
                # (e.g. 102 says "> 6" and 6 says "< 102", both
                # encoding "102 is_after 6"), only one edge is added.
                edge_id = (
                    f"rap_{src_node.node_id}_{dst_node.node_id}_"
                    f"{edge_type}")
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
    if unita_tipo in ("DOC", "EXT", "Extractor"):
        return f"D.{n}"
    if unita_tipo == "Combinar":
        return f"C.{n}"
    if unita_tipo == "property":
        return descrizione.strip() or f"property{n}"
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
        visual = _VISUAL_BY_UNITA_TIPO.get(unita_tipo)
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
    for edge_el in root.iter(f"{{{NS_GRAPHML}}}edge"):
        src = edge_el.get("source") or ""
        tgt = edge_el.get("target") or ""
        src_type = node_id_to_unita_tipo.get(src)
        tgt_type = node_id_to_unita_tipo.get(tgt)
        is_paradata = (
            src_type in _PARADATA_UNITA_TIPI
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
        for attr_name, kid in attrname_to_kid.items():
            val = attrs.get(attr_name)
            if val is None or val == "":
                continue
            d = etree.SubElement(node_el, f"{{{NS_GRAPHML}}}data")
            d.set("key", kid)
            d.text = str(val)

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
