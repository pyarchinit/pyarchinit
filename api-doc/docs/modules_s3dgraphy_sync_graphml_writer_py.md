# modules/s3dgraphy/sync/graphml_writer.py

## Overview

This file contains 19 documented elements.

## Functions

### _filter_by_site(graph, site_filter)

Return a new Graph containing only nodes/edges relevant to *site_filter*.

Retention rules (per spec §5 step 6.iv.2):
- Stratigraphic node kept iff its `attributes['sito']` equals site_filter.
- EpochNode kept iff at least one retained stratigraphic node points at
  it via a `has_first_epoch` edge.
- Edges kept iff BOTH endpoints are kept.

`site_filter=None` returns the original graph unchanged.

**Parameters:**
- `graph`
- `site_filter`

### _read_first_sito(db_path)

Return the first ``us_table.sito`` value found in *db_path*.

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

**Parameters:**
- `db_path`

### _count_temporal_input_edges(graph)

Count edges that the TemporalInferenceEngine would feed into
transitive_reduction(). Mirrors `extract_temporal_from_graph`'s
inclusion rules without instantiating the engine.

**Parameters:**
- `graph`

### _count_is_after_edges_in_xml(xml_text)

Count `is_after` edges present in a GraphML XML document.

GraphMLExporter emits the edge type via a `<data key="..."` /
`<y:EdgeLabel>` containing the literal "is_after". Each minimal
temporal edge produces one such occurrence on an <edge> element.

**Parameters:**
- `xml_text`

### _get_node_registry()

Return a singleton s3dgraphy NodeRegistry, or None if it can't
be loaded (e.g. older s3dgraphy version).

### _resolve_visual(unita_tipo)

Return the visual properties dict for *unita_tipo*, preferring
pyarchinit-specific overrides in `_VISUAL_BY_UNITA_TIPO` and
falling back to s3dgraphy's NodeRegistry palette for any type we
don't have an explicit override for.

Pyarchinit overrides cover legacy deviations the user expects:
border width 3.0 (vs canonical 4.0), USM grey background, CON
diamond, paradata BPMN/SVG icons. New EM types added to s3dgraphy
in future releases get sane visuals automatically via the
NodeRegistry path without changes here.

**Parameters:**
- `unita_tipo`

### _resolve_display_label(unita_tipo, us_number, language, descrizione)

Return the formatted display label for a node, per legacy
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

**Parameters:**
- `unita_tipo`
- `us_number`
- `language`
- `descrizione`

### _convert_shape_to_svg_node(shape_el, etree, NS_Y, refid, geometry)

Convert a ``<y:ShapeNode>`` element in place into a
``<y:SVGNode>`` referencing the legacy SVG resource id ``refid``.

Legacy dottoxml.py used SVGNodes with custom Inkscape SVGs to
render Continuity, Extractor and Combinar icons. We preserve the
Geometry/Fill/BorderStyle/NodeLabel children verbatim and just
change the parent tag and append <y:SVGNodeProperties> +
<y:SVGModel>/<y:SVGContent> instead of <y:Shape>.

**Parameters:**
- `shape_el`
- `etree`
- `NS_Y`
- `refid`
- `geometry`

### _convert_shape_to_bpmn_node(shape_el, etree, NS_Y, bpmn_type, geometry)

Convert a ``<y:ShapeNode>`` element in place into a
``<y:GenericNode>`` with BPMN artifact configuration matching
``bpmn_type`` (ARTIFACT_TYPE_DATA_OBJECT for DOC,
ARTIFACT_TYPE_ANNOTATION for property).

Legacy dottoxml.py used GenericNodes with the BPMN artifact
configuration to render DOC and property nodes. We preserve the
Geometry/Fill/BorderStyle/NodeLabel children verbatim and replace
the <y:Shape> child with the BPMN <y:StyleProperties> block.

**Parameters:**
- `shape_el`
- `etree`
- `NS_Y`
- `bpmn_type`
- `geometry`

### _ensure_resources_block(root, etree, NS_GRAPHML, NS_Y, needed_refids)

Make sure ``<graphml>`` has a ``<key yfiles.type="resources">``
declaration AND a matching ``<data>`` child carrying a
``<y:Resources>`` block with the requested SVG resource ids.

Idempotent: if the resources block already exists for the given
ids, do nothing. Otherwise create the missing pieces by appending
new elements; preserves any existing keys/data.

*needed_refids* is a set of strings like {"1", "2", "3"} matching
the keys of `_legacy_paradata_svgs.SVG_RESOURCES`.

**Parameters:**
- `root`
- `etree`
- `NS_GRAPHML`
- `NS_Y`
- `needed_refids`

### _apply_pyarchinit_visual_overrides(graph, xml_path, language)

Patch the GraphML produced by s3dgraphy GraphMLExporter so that
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

**Parameters:**
- `graph`
- `xml_path`
- `language`

### _embed_pyarchinit_data_keys(graph, xml_path)

Append custom <data> entries on each <node> in the produced
GraphML so AI04's import path can recover the pyarchinit columns
that s3dgraphy's GraphMLImporter would otherwise strip.

Each attribute gets its own <key for="node" attr.name="…"/> at
the document level, plus a per-node <data key="…">value</data>.

**Parameters:**
- `graph`
- `xml_path`

### _inject_isolated_paradata_nodes(paradata_nodes, xml_path)

Append AuthorNode / LicenseNode / EmbargoNode entries to the
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

**Parameters:**
- `paradata_nodes`
- `xml_path`

### _inject_group_folders(group_snapshot, members_map, xml_path)

Inject yEd folder nodes inside the TableNode for each group.

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

**Parameters:**
- `group_snapshot`
- `members_map`
- `xml_path`

### export_graphml(db_path, mapping, output_path, site_filter, persist_auxiliary, language, groups)

Run PyArchInitImporter → optional site filter → GraphMLExporter.

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

**Parameters:**
- `db_path`
- `mapping`
- `output_path`
- `site_filter`
- `persist_auxiliary`
- `language`
- `groups`

## Classes

### ExportResult

Metrics + warnings returned by a successful export_graphml() call.

### EmptyGraphError

Graph has no nodes after import + (optional) site filter.

**Inherits from**: ValueError

### GraphMLExportError

Wraps any failure during the GraphML export pipeline.

Attributes:
    stage: one of VALID_STAGES — categorises where the failure
        occurred so the bridge UI can present a useful message.
    original: the underlying exception, preserved for logging.

**Inherits from**: RuntimeError

#### Methods

##### __init__(self, stage, original)

*No description available.*
