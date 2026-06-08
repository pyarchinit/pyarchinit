# EM paradata export rendering — design

Date: 2026-06-08
Branch: `Stratigraph_00001`
Status: design approved, ready for implementation plan

## Problem

When a pyArchInit site is exported to GraphML (`export_graphml` →
`GraphProjector.populate_graph` → s3dgraphy `GraphMLExporter`) for yEd /
EM-tools, the Extended-Matrix paradata and contemporaneity relations do not
render the way the EM convention requires. Concretely, on the `Sito_Test_EM`
test database the exported `.graphml` shows:

1. **Paradata (DOC / Extractor / Combinar / property) appear disconnected.**
   The s3dgraphy `GraphMLExporter` excludes `PARADATA_EDGE_TYPES` from the drawn
   edges (`graphml_exporter.py` ~line 253: `export_edges = [e for e in
   self.graph.edges if e.edge_type not in TOPOLOGICAL_EDGE_TYPES and
   e.edge_type not in PARADATA_EDGE_TYPES]`) and renders paradata as group
   folders instead. The data-flow chain
   (`DOC → Extractor → Combinar → property → US/USV`) is invisible.
2. **Continuity (CON) nodes are missing.** Rows with `unita_tipo='CON'`
   (`ContinuityNode`, `node_type='BR'`) are not rendered as nodes in the export
   (`CON present: []`), so the user's explicitly-authored continuity is lost.
   (Separate from the *auto* `_synth_BR_*` diamonds, already suppressed in
   `[5.12.10-alpha]`.)
3. **Contemporaneity edges look like ordinary directed edges.**
   `is_physically_equal_to` ("Uguale a") and `is_bonded_to` ("Si lega a")
   currently render as a solid line **with** an arrowhead
   (`edge_generator.py`: `('line', 2.0)` + `Arrows target='standard'`). The EM
   convention is a **double line with no arrowhead**, and the two contemporary
   nodes must sit on the **same horizontal line**.
4. **Paradata node labels show the description, not the us code.** DOC /
   Combinar / Extractor / property render as `Documento` / `Combiner` /
   `Extractor` / `Proprieta` (from `d_stratigrafica`) instead of the `us` value
   (`D.1`, `C.1`, `D.1.1`, `prop1`). Source: `graphml_writer._resolve_display_label`
   returns `descrizione` for these unita_tipo.

These are rendering concerns in the s3dgraphy `GraphMLExporter` /
`edge_generator` plus one label concern in pyArchInit's `graphml_writer`. The
in-memory graph produced by `populate_graph` is already correct (paradata edges
typed by `paradata_edge_resolver`, USV/SF connected — `[5.12.9-alpha]`); the gap
is purely in how the GraphML is *written*.

## Goals

A pyArchInit → GraphML export whose paradata and contemporaneity render per the
EM/yEd convention:

- Paradata are **connected nodes** with the EM edges visible:
  `extracted_from`, `combines`, `has_property`, `has_documentation`,
  `has_data_provenance` (NOT folder-grouped, NOT filtered out).
- Paradata node labels are the **`us` value** (`D.1`, `D.1.1`, `C.1`, `prop1`).
- Contemporaneity edges (`is_physically_equal_to`, `is_bonded_to`, and the
  canonical `equals` / `bonded_to`) render as **double line, no arrowhead**;
  same-line alignment is delegated to yEd's layout (a non-directional edge).
- Explicit **CON** (`ContinuityNode`/BR) rows render as **diamond** nodes
  connected by `is_after` (the `>` / `<` shorthand).

Every fix is verified on the test DB via headless `export_graphml`, asserting on
the produced XML — not just on the in-memory graph.

## Approach (C — hybrid)

| # | Fix | Component | Location | Durability |
|---|-----|-----------|----------|------------|
| 4 | Paradata label = `us` | pyArchInit `graphml_writer._resolve_display_label` | `modules/s3dgraphy/sync/graphml_writer.py` | committed (durable) |
| 1 | Draw paradata edges | s3dgraphy `GraphMLExporter` | `ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py` | ext_libs live + fork PR |
| 3 | Contemporaneity double-line/no-arrow | s3dgraphy `edge_generator` | `ext_libs/s3dgraphy/exporter/graphml/edge_generator.py` | ext_libs live + fork PR |
| 2 | Render CON nodes | s3dgraphy `GraphMLExporter` | `ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py` | ext_libs live + fork PR |

The s3dgraphy-core fixes (1/2/3) are applied to `ext_libs` for the live result
and committed to the fork (branch `fix/pyarchinit-importer-node-type-by-unita-tipo`,
or a dedicated `fix/em-paradata-export-rendering` branch) for the upstream PR —
matching the established "live stop-gap + fork PR" pattern (dev9, #22/#23).
`ext_libs` is git-ignored: re-vendoring wipes the live patches until the PR is
merged and a dev release is pinned. pyArchInit-side callers must degrade
gracefully (no crash) if a re-vendored `ext_libs` lacks a change.

## Components

### Component 1 — Paradata label = `us` (fix #4)

`modules/s3dgraphy/sync/graphml_writer.py :: _resolve_display_label`.

Current: for `DOC` / `EXT` / `Extractor` / `Combinar` / `property` it returns
`descrizione.strip()` (the `d_stratigrafica` value) before falling back to a
`us`-derived form. Target: return the **`us` value** for these kinds:

- `DOC` → `us` (e.g. `D.1`)
- `Extractor` (and legacy `EXT`) → `us` (e.g. `D.1.1`)
- `Combinar` → `us` (e.g. `C.1`)
- `property` → `us` (e.g. `prop1`)

US / USM / USV* / SF / VSF / CON branches are unchanged (already correct after
the `[5.12.9-alpha]` / SF-VSF-naming test-data fix). Keep a sane fallback when
`us` is empty.

Test: headless export of the test DB → the DOC node's `NodeLabel` text == `D.1`
(and `D.1.1` / `C.1` / `prop1` for the others); no node labelled `Documento` /
`Combiner` / `Extractor` / `Proprieta`.

### Component 2 — Draw paradata edges (fix #1)

`ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py` (export-edge
selection, ~line 253) + the paradata-group rendering.

Current: `export_edges` excludes `PARADATA_EDGE_TYPES`; paradata are rendered as
`has_paradata_nodegroup` folders. Target: the paradata edges
(`extracted_from`, `combines`, `has_property`, `has_documentation`,
`has_data_provenance`) are **kept in `export_edges`** and drawn as visible
edges, and the folder grouping for these paradata is **not** applied (per the
approved "archi visibili" choice). `edge_generator` already styles
`extracted_from` as dashed; the remaining paradata edge types need a style entry
(default acceptable, dashed preferred for provenance-family).

Open sub-decision (resolve in the plan): whether to *remove* the paradata-group
code path or *gate* it behind a flag (`paradata_as_groups=False`) so other
consumers keep the folder behaviour. Recommendation: gate behind a flag, default
to edges for the pyArchInit export call, to stay non-destructive upstream.

Test: headless export → `extracted_from` / `combines` / `has_property` /
`has_documentation` present as `<edge>` elements; Combiner / Extractor / property
nodes are NOT isolated (degree ≥ 1).

### Component 3 — Contemporaneity edge style (fix #3)

`ext_libs/s3dgraphy/exporter/graphml/edge_generator.py`.

Current: `is_bonded_to` / `is_physically_equal_to` → `('line', 2.0)`, and
`generate_edge` always sets `Arrows target='standard'`. Target: for the
contemporaneity edge types (`is_physically_equal_to`, `is_bonded_to`, and the
canonical aliases `equals`, `bonded_to`, plus `has_same_time`):

- **No arrowhead**: `Arrows source='none' target='none'`.
- **Double line**: render the EM "contemporaneity" double stroke.

Same-line placement is **not** forced by the exporter — it is achieved when the
user applies the yEd layout, because a no-arrow edge is treated as
non-directional (same rank).

OPEN QUESTION (must be answered before implementing Component 3): yEd's native
`LineStyle` has no "double line". The exact representation EM-tools expects must
be confirmed with the user — candidates: (a) a yEd line style that reads as
double, (b) two parallel edges, (c) a custom EM marker. The arrowhead removal is
unambiguous and can ship regardless.

Test: headless export → these edge types have `Arrows source='none'
target='none'`; double-line marker present once its representation is fixed.

### Component 4 — Render CON nodes (fix #2)

`ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py` (node rendering).

Current: explicit `ContinuityNode` (`node_type='BR'`) rows are not emitted as
nodes (`CON present: []`). Target: render them as the EM **continuity diamond**
(the BR SVG already exists in `canvas_generator._get_continuity_svg`) and draw
their `is_after` edges (`>` / `<`). The drop point in the exporter's
node-rendering loop must be located in the plan and the BR type allowed through
for *non-synthetic* (user-authored, `injected_by` absent) continuity nodes. This
is distinct from the auto `_synth_BR_*` diamonds suppressed in `[5.12.10-alpha]`
— those stay suppressed; explicit CON rows are rendered.

Test: headless export → `CON1` / `CON2` nodes present (diamond shape) + their
`is_after` edges to `USM6` / `USM8`.

## Testing strategy

- A headless test (pattern of the existing `tests/sync` ones) that runs
  `export_graphml` on the `Sito_Test_EM` test DB (or a small hermetic fixture)
  and parses the produced `.graphml`, asserting the four outcomes above.
- For the s3dgraphy-core changes, add unit tests in the fork (the PR) covering:
  paradata edges drawn, contemporaneity no-arrow style, CON node emitted.
- Run the full `tests/sync` suite (baseline: 415 passed, 9 fail + 9 err
  pre-existing PG/Spatialite) — zero new regressions, AC-2 export baselines
  unchanged for fixtures without paradata/contemporaneity.

## Out of scope

- The 5 residual `generic_connection` edges (SF/VSF/USM ↔ USVs): no datamodel
  edge type applies — correct as-is.
- The s3dgraphy **importer** typing fix (fork branch
  `fix/pyarchinit-importer-node-type-by-unita-tipo`): a separate valid upstream
  improvement, not required for the pyArchInit export (which uses the bridge
  `StratigraphicUnit` + `unita_tipo` nodes).
- A pyArchInit config toggle to re-enable folder-based paradata / continuity
  diamonds — only add if a future user needs it.

## Risks / notes

- **ext_libs durability**: components 1–3 (and 4) live in `ext_libs` until the
  upstream PR lands; re-vendoring wipes them. pyArchInit callers stay defensive.
- **Double-line representation** (Component 3) is the one unresolved detail and
  gates only that component; the rest can proceed.
- **EM-tools round-trip**: switching paradata from folders to visible edges may
  affect how EM-tools (Blender) re-imports the GraphML. Validate with the user's
  EM-tools workflow before merging the upstream PR.
