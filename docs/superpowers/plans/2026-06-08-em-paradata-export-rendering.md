# EM paradata export rendering — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a pyArchInit → GraphML export render Extended-Matrix paradata as
connected nodes with us-value labels, render explicit CON as continuity
diamonds, and render contemporaneity relations as double (parallel) no-arrow
edges.

**Architecture:** Hybrid (spec approach C). The node label fix lives in
pyArchInit's `graphml_writer` (durable, committed to `Stratigraph_00001`). The
three rendering fixes live in the s3dgraphy core exporter — applied to the
git-ignored `ext_libs/s3dgraphy` for the live result AND to the fork
(`~/Downloads/s3Dgraphy_fork`) for the upstream PR. pyArchInit passes the new
exporter flags defensively via `inspect.signature` so a re-vendored `ext_libs`
never crashes.

**Tech Stack:** Python 3, pytest, ElementTree (GraphML XML), SQLite test DB
(`/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_test_em.sqlite`),
s3dgraphy 1.6.0.dev9 (vendored in `ext_libs/`).

**Spec:** `docs/superpowers/specs/2026-06-08-em-paradata-export-rendering-design.md`

---

## Conventions used by every task

- **PLUGIN** = `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit`
- **FORK** = `/Users/enzo/Downloads/s3Dgraphy_fork` (branch
  `fix/em-paradata-export-rendering`, created in Task 0)
- **TESTDB** = `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_test_em.sqlite`
- s3dgraphy-core edits are made in **both** `PLUGIN/ext_libs/s3dgraphy/...`
  (live) and `FORK/src/s3dgraphy/...` (PR). The two files are identical content;
  edit FORK then `cp` to ext_libs, or edit both — either is fine, but keep them
  in sync.
- Headless tests run from `PLUGIN` via `python3 -m pytest tests/sync/<file> -q`.
  Temporary probe tests are named `tests/sync/_tmp_*.py` and deleted after use;
  permanent tests are named `tests/sync/test_*.py`.
- Commit messages: NO `Co-Authored-By`, NO AI-attribution footer. Use
  `git -c commit.gpgsign=false commit`.

## File structure

| File | Responsibility | Change |
|------|----------------|--------|
| `PLUGIN/modules/s3dgraphy/sync/graphml_writer.py` | display label + defensive flag pass | modify `_resolve_display_label`; pass `paradata_as_groups=False` |
| `PLUGIN/tests/sync/test_em_export_rendering.py` | headless export assertions (all 4 fixes) | create |
| `FORK/src/s3dgraphy/exporter/graphml/edge_generator.py` (+ ext_libs copy) | contemporaneity style | modify `EDGE_TYPE_TO_LINE_STYLE` + `generate_edge` arrows |
| `FORK/src/s3dgraphy/exporter/graphml/graphml_exporter.py` (+ ext_libs copy) | `paradata_as_groups` flag + draw paradata edges + emit parallel contemporaneity edges + render CON | modify `export()` + edge/node emission |
| `FORK/tests/test_em_paradata_rendering.py` | s3dgraphy-core unit tests for the PR | create |

---

## Task 0: Create the fork branch

**Files:** none (git only)

- [ ] **Step 1: Create a clean branch off upstream**

```bash
cd /Users/enzo/Downloads/s3Dgraphy_fork
git fetch upstream s3dgraphy_v1.6dev
git checkout -q upstream/s3dgraphy_v1.6dev
git checkout -q -b fix/em-paradata-export-rendering
git branch --show-current   # => fix/em-paradata-export-rendering
```

Expected: branch `fix/em-paradata-export-rendering` created.

---

## Task 1: Paradata node label = `us` (spec Component 1, fix #6)

**Files:**
- Modify: `PLUGIN/modules/s3dgraphy/sync/graphml_writer.py` (`_resolve_display_label`, ~line 509-521)
- Test: `PLUGIN/tests/sync/test_em_export_rendering.py`

- [ ] **Step 1: Write the failing test** (create the file with a shared helper + this test)

```python
# PLUGIN/tests/sync/test_em_export_rendering.py
import sys, xml.etree.ElementTree as ET
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TESTDB = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_test_em.sqlite"
N = "{http://graphml.graphdrawing.org/xmlns}"


def _export(tmp_path):
    if not Path(TESTDB).exists():
        pytest.skip("EM test DB absent")
    out = str(tmp_path / "em.graphml")
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    export_graphml(TESTDB, "pyarchinit_us_mapping", out,
                   site_filter="Sito_Test_EM")
    return ET.parse(out).getroot()


def _node_labels(root):
    labels = set()
    for n in root.iter(N + "node"):
        for tx in n.iter():
            if tx.tag.endswith("}NodeLabel") and tx.text and tx.text.strip():
                labels.add(tx.text.strip())
                break
    return labels


def test_paradata_labels_are_us_values(tmp_path):
    labels = _node_labels(_export(tmp_path))
    # paradata labelled by us code, NOT by description
    assert "D.1" in labels, labels
    assert "D.1.1" in labels, labels      # extractor
    assert "C.1" in labels, labels        # combiner
    assert not any(l in ("Documento", "Combiner", "Extractor", "Proprieta")
                   for l in labels), labels
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_paradata_labels_are_us_values -q`
Expected: FAIL — labels contain `Documento`/`Combiner`/`Extractor`, not `D.1`.

- [ ] **Step 3: Edit `_resolve_display_label`**

In `graphml_writer.py`, replace the paradata branches so they return the `us`
value (`us_number`) instead of `descrizione`:

```python
    if unita_tipo in ("DOC", "EXT", "Extractor"):
        return n or descrizione.strip()
    if unita_tipo == "Combinar":
        return n or descrizione.strip()
    if unita_tipo == "property":
        return n or descrizione.strip()
```

(`n = us_number.strip()` is already defined at the top of the function. Keep the
`US`/`USM`/`USV*`/`SF`/`VSF`/`CON` branches above unchanged.)

- [ ] **Step 4: Run test to verify it passes**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_paradata_labels_are_us_values -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd "$PLUGIN"
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_em_export_rendering.py
git -c commit.gpgsign=false commit -m "fix(export): label paradata nodes by us value, not description"
```

---

## Task 2: Draw paradata edges via `paradata_as_groups` flag (spec Component 2, fix #1)

**Files:**
- Modify: `FORK/src/s3dgraphy/exporter/graphml/graphml_exporter.py` (`export()` signature + the `export_edges` filter ~line 253 + the paradata-group emission)
- Mirror: `PLUGIN/ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py`
- Modify: `PLUGIN/modules/s3dgraphy/sync/graphml_writer.py` (defensive flag pass)
- Test: `PLUGIN/tests/sync/test_em_export_rendering.py` (+ `FORK/tests/...`)

- [ ] **Step 1: Read the current code to locate exact lines**

Run: `cd "$PLUGIN" && grep -n "PARADATA_EDGE_TYPES\|export_edges =\|_build_paradata_groups\|def export(\|continuity_diamonds" ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py`
Note the line numbers of: (a) the `def export(...)` signature, (b) the
`export_edges = [...]` comprehension that excludes `PARADATA_EDGE_TYPES`, (c) the
`paradata_groups = self._build_paradata_groups(...)` call and its emission loop.

- [ ] **Step 2: Write the failing test**

```python
# add to PLUGIN/tests/sync/test_em_export_rendering.py
def _edges(root):
    return [(e.get("source"), e.get("target")) for e in root.iter(N + "edge")]

def _node_degrees(root):
    import collections
    deg = collections.Counter()
    for s, t in _edges(root):
        deg[s] += 1; deg[t] += 1
    # map id -> label
    id2lab = {}
    for nd in root.iter(N + "node"):
        for tx in nd.iter():
            if tx.tag.endswith("}NodeLabel") and tx.text and tx.text.strip():
                id2lab[nd.get("id")] = tx.text.strip(); break
    return {id2lab.get(k, k): v for k, v in deg.items()}

def test_paradata_nodes_are_connected(tmp_path):
    deg = _node_degrees(_export(tmp_path))
    # combiner / extractor / a document must have at least one edge
    assert deg.get("C.1", 0) >= 1, deg
    assert deg.get("D.1.1", 0) >= 1, deg     # extractor
    assert deg.get("D.1", 0) >= 1, deg       # document
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_paradata_nodes_are_connected -q`
Expected: FAIL — `C.1`/`D.1.1`/`D.1` have degree 0 (paradata filtered into folders).

- [ ] **Step 4: Add the `paradata_as_groups` flag to the exporter (FORK + ext_libs)**

In `graphml_exporter.py`, change the `export()` signature to add
`paradata_as_groups: bool = True` (after `continuity_diamonds`). Then:

1. In the `export_edges` comprehension (the one that excludes
   `PARADATA_EDGE_TYPES`), only apply the `PARADATA_EDGE_TYPES` exclusion when
   `paradata_as_groups` is True:

```python
        export_edges = [
            e for e in self.graph.edges
            if e.edge_type not in TOPOLOGICAL_EDGE_TYPES
            and (not paradata_as_groups
                 or e.edge_type not in PARADATA_EDGE_TYPES)
        ]
```

2. Guard the paradata-group build/emit block so it only runs when
   `paradata_as_groups` is True (wrap the `paradata_groups =
   self._build_paradata_groups(...)` call and its emission loop in
   `if paradata_as_groups:`).

Apply the SAME edit to `PLUGIN/ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py`
(or `cp FORK/src/.../graphml_exporter.py PLUGIN/ext_libs/.../graphml_exporter.py`).

- [ ] **Step 5: Ensure paradata edge types have a draw style (FORK + ext_libs)**

In `edge_generator.py` `EDGE_TYPE_TO_LINE_STYLE`, confirm/add entries (dashed for
provenance-family):

```python
    'extracted_from': ('dashed', 2.0),
    'combines': ('dashed', 2.0),
    'has_property': ('dashed', 2.0),
    'has_documentation': ('dashed', 2.0),
    'has_data_provenance': ('dashed', 2.0),
```

(Keep existing entries; add only the missing ones.)

- [ ] **Step 6: Pass `paradata_as_groups=False` defensively from graphml_writer**

In `PLUGIN/modules/s3dgraphy/sync/graphml_writer.py`, where it already builds
`_export_kw` via `inspect.signature` for `continuity_diamonds`, add the same
detection for `paradata_as_groups`:

```python
    sig_params = _inspect.signature(exporter.export).parameters
    if "continuity_diamonds" in sig_params:
        _export_kw["continuity_diamonds"] = False
    if "paradata_as_groups" in sig_params:
        _export_kw["paradata_as_groups"] = False
```

(Refactor the existing single-param check into this two-param form.)

- [ ] **Step 7: Run test to verify it passes**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_paradata_nodes_are_connected -q`
Expected: PASS.

- [ ] **Step 8: Commit (pyArchInit side) + stage fork**

```bash
cd "$PLUGIN"
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_em_export_rendering.py
git -c commit.gpgsign=false commit -m "fix(export): draw paradata edges (paradata_as_groups=False)"
cd "$FORK" && git add src/s3dgraphy/exporter/graphml/graphml_exporter.py src/s3dgraphy/exporter/graphml/edge_generator.py
git -c commit.gpgsign=false commit -m "feat(graphml): paradata_as_groups flag to draw paradata edges instead of folders"
```

---

## Task 3: Contemporaneity = double (parallel) no-arrow edges (spec Component 3, fix #3)

**Files:**
- Modify: `FORK/src/s3dgraphy/exporter/graphml/edge_generator.py` (`generate_edge` arrows) + `graphml_exporter.py` (emit two edges for contemporaneity types)
- Mirror: ext_libs copies
- Test: `PLUGIN/tests/sync/test_em_export_rendering.py`

Contemporaneity edge types: `is_physically_equal_to`, `is_bonded_to`, `equals`,
`bonded_to`, `has_same_time`.

- [ ] **Step 1: Write the failing test**

```python
# add to PLUGIN/tests/sync/test_em_export_rendering.py
def _edges_with_arrows(root):
    out = []
    for e in root.iter(N + "edge"):
        src_arrow = tgt_arrow = None
        for a in e.iter():
            if a.tag.endswith("}Arrows"):
                src_arrow = a.get("source"); tgt_arrow = a.get("target")
        out.append((e.get("source"), e.get("target"), src_arrow, tgt_arrow))
    return out

def test_contemporaneity_double_no_arrow(tmp_path):
    root = _export(tmp_path)
    # us 9 "Uguale a" 10 (is_physically_equal_to), us 6 "Si lega a" 8 (is_bonded_to)
    # find the two stratigraphic nodes' ids by label
    id2lab = {}
    for nd in root.iter(N + "node"):
        for tx in nd.iter():
            if tx.tag.endswith("}NodeLabel") and tx.text and tx.text.strip():
                id2lab[tx.text.strip()] = nd.get("id"); break
    eq_pair = {id2lab.get("US9"), id2lab.get("US10")}
    edges = [(s, t, sa, ta) for (s, t, sa, ta) in _edges_with_arrows(root)
             if {s, t} == eq_pair]
    # two parallel edges, both no-arrow
    assert len(edges) == 2, edges
    assert all(sa == "none" and ta == "none" for (_, _, sa, ta) in edges), edges
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_contemporaneity_double_no_arrow -q`
Expected: FAIL — only one edge, arrows target='standard'.

- [ ] **Step 3: No-arrow for contemporaneity in `generate_edge` (FORK + ext_libs)**

In `edge_generator.py` `generate_edge`, where it currently always sets
`arrows.set('target', 'standard')`, branch on the edge type:

```python
        _CONTEMP = {"is_physically_equal_to", "is_bonded_to", "equals",
                    "bonded_to", "has_same_time"}
        arrows = ET.SubElement(polyline, f'{{{self.ns_y}}}Arrows')
        if edge_type in _CONTEMP:
            arrows.set('source', 'none')
            arrows.set('target', 'none')
        else:
            arrows.set('source', 'none')
            arrows.set('target', 'standard')
```

- [ ] **Step 4: Emit two parallel edges for contemporaneity (FORK + ext_libs)**

In `graphml_exporter.py`, in the loop that emits `export_edges` via
`edge_generator.generate_edge(...)`, when `edge.edge_type` is in the
contemporaneity set, generate the edge TWICE with distinct edge ids and opposite
small bend offsets so yEd renders two parallel arcs. Locate the emission loop
(grep `generate_edge(` in the file) and wrap:

```python
        _CONTEMP = {"is_physically_equal_to", "is_bonded_to", "equals",
                    "bonded_to", "has_same_time"}
        # ... inside the per-edge loop:
        if edge.edge_type in _CONTEMP:
            for k in (0, 1):
                x = edge_gen.generate_edge(edge, edge_uuid=f"{edge_uuid}_{k}")
                # opposite bend so the two strokes are visibly parallel
                _apply_parallel_bend(x, offset=(6 if k == 0 else -6))
                parent.append(x)
        else:
            parent.append(edge_gen.generate_edge(edge, edge_uuid=edge_uuid))
```

Add a small helper near the edge emission (same module):

```python
    def _apply_parallel_bend(edge_xml, offset):
        """Insert a single bend Point on the edge's PolyLineEdge so two
        contemporaneity edges between the same nodes render as parallel
        strokes instead of overlapping into one line."""
        import xml.etree.ElementTree as _ET
        ple = edge_xml.find(f'.//{{{self.ns_y}}}PolyLineEdge')
        if ple is None:
            return
        path = ple.find(f'{{{self.ns_y}}}Path')
        if path is None:
            path = _ET.SubElement(ple, f'{{{self.ns_y}}}Path')
            path.set('sx', '0'); path.set('sy', '0')
            path.set('tx', '0'); path.set('ty', '0')
        pt = _ET.SubElement(path, f'{{{self.ns_y}}}Point')
        pt.set('x', str(offset)); pt.set('y', str(offset))
```

(If `generate_edge` does not accept `edge_uuid`, read its signature and adapt —
the goal is two `<edge>` elements with distinct `id`s between the same endpoints.)
Mirror all edits to ext_libs.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_contemporaneity_double_no_arrow -q`
Expected: PASS.

- [ ] **Step 6: Commit fork**

```bash
cd "$FORK"
git add src/s3dgraphy/exporter/graphml/edge_generator.py src/s3dgraphy/exporter/graphml/graphml_exporter.py
git -c commit.gpgsign=false commit -m "feat(graphml): contemporaneity edges as parallel no-arrow strokes"
```

---

## Task 4: Render explicit CON nodes (spec Component 4, fix #2)

**Files:**
- Modify: `FORK/src/s3dgraphy/exporter/graphml/graphml_exporter.py` (node emission — allow non-synthetic BR through)
- Mirror: ext_libs copy
- Test: `PLUGIN/tests/sync/test_em_export_rendering.py`

- [ ] **Step 1: Locate why CON nodes are dropped**

Run: `cd "$PLUGIN" && grep -n "node_type\|'BR'\|\"BR\"\|ContinuityNode\|PHYSICAL_STRATIGRAPHIC_TYPES\|for .* in .*nodes\|generate_stratigraphic_node\|_synth" ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py`
Identify the node-rendering loop and the predicate that currently excludes BR /
ContinuityNode nodes from emission.

- [ ] **Step 2: Write the failing test**

```python
# add to PLUGIN/tests/sync/test_em_export_rendering.py
def test_explicit_con_nodes_rendered(tmp_path):
    root = _export(tmp_path)
    labels = _node_labels(root)
    assert "CON1" in labels, labels
    assert "CON2" in labels, labels
    # no auto synthetic continuity diamonds
    assert not any(l.startswith("_synth_BR_") for l in labels), labels
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_explicit_con_nodes_rendered -q`
Expected: FAIL — `CON1`/`CON2` absent.

- [ ] **Step 4: Allow non-synthetic ContinuityNode through node emission (FORK + ext_libs)**

In the node-rendering predicate found in Step 1, allow `ContinuityNode`
(`node_type == 'BR'`) nodes to be emitted UNLESS they are synthetic
(`getattr(node, 'attributes', {}).get('injected_by') == 'materialize_continuity'`
or `str(node.name).startswith('_synth')`). Render them with the continuity SVG
(`canvas_generator._get_continuity_svg`, already used for the diamond shape).
The `is_after` edges (`>`/`<`) are already drawn (is_after is in
`EDGE_TYPE_TO_LINE_STYLE`). Mirror to ext_libs.

(Exact predicate edit depends on Step 1; the rule is: emit BR nodes whose name
does NOT start with `_synth` and that lack the `materialize_continuity`
`injected_by` tag.)

- [ ] **Step 5: Run test to verify it passes**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py::test_explicit_con_nodes_rendered -q`
Expected: PASS.

- [ ] **Step 6: Commit fork**

```bash
cd "$FORK"
git add src/s3dgraphy/exporter/graphml/graphml_exporter.py
git -c commit.gpgsign=false commit -m "feat(graphml): render explicit (non-synthetic) ContinuityNode diamonds"
```

---

## Task 5: Full regression + fork tests + finalize

**Files:**
- Test: `FORK/tests/test_em_paradata_rendering.py` (s3dgraphy-core unit tests for the PR)

- [ ] **Step 1: Run the full pyArchInit sync suite**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync -q 2>&1 | tail -3`
Expected: `4XX passed` with the SAME 9 failed + 9 errors as baseline
(PG/Spatialite pre-existing). No NEW failures. If a new failure appears, fix the
responsible task before continuing.

- [ ] **Step 2: Run the new EM export test file in full**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_em_export_rendering.py -q`
Expected: all 4 tests PASS.

- [ ] **Step 3: Add s3dgraphy-core unit tests in the fork**

Create `FORK/tests/test_em_paradata_rendering.py` with hermetic unit tests (build
a tiny `Graph` in memory with EpochNodes + a US + DOC/Extractor/Combiner +
is_physically_equal_to pair + an explicit ContinuityNode, call
`GraphMLExporter(graph).export(out, paradata_as_groups=False)`, parse the XML)
asserting: (a) paradata edges present, (b) contemporaneity = 2 no-arrow edges,
(c) explicit CON node emitted. Mirror the assertion helpers from
`test_em_export_rendering.py`.

- [ ] **Step 4: Run the fork test suite for regressions**

Run: `cd "$FORK" && python3 -m pytest tests/ -q --tb=no -p no:cacheprovider 2>&1 | tail -3`
Expected: same pre-existing failures as baseline (17 failed incl. lossless +
PG), NO new failures. Plus the new test file passing.

- [ ] **Step 5: Commit fork tests**

```bash
cd "$FORK"
git add tests/test_em_paradata_rendering.py
git -c commit.gpgsign=false commit -m "test(graphml): EM paradata/contemporaneity/CON rendering"
```

- [ ] **Step 6: Update CHANGELOG (pyArchInit)**

Add a `[5.12.11-alpha]` bilingual entry to `PLUGIN/dev_logs/CHANGELOG.md`
summarizing the 4 export-rendering fixes (label=us, paradata edges visible,
contemporaneity parallel no-arrow, explicit CON rendered). Commit.

- [ ] **Step 7: STOP — do not push / open PR without user approval**

The fork branch is ready. Per the user's standing instruction, opening/pushing
the s3dgraphy PR is an explicit, user-approved action. Report the fork diff and
wait. Also: validate the EM-tools (Blender) round-trip with the user before the
PR is merged (paradata folders → edges may affect re-import).

---

## Self-review

**Spec coverage:**
- Component 1 (label=us) → Task 1. ✓
- Component 2 (draw paradata edges, `paradata_as_groups` flag) → Task 2. ✓
- Component 3 (contemporaneity parallel no-arrow) → Task 3. ✓
- Component 4 (render CON) → Task 4. ✓
- Testing strategy (headless export assertions + fork unit tests + full suite) →
  Tasks 1–5. ✓
- Rollout (ext_libs live + fork PR + defensive flag pass) → Tasks 2/5, Step 6 of
  Task 2. ✓

**Placeholder scan:** Tasks 2/4 contain a "read the current code to locate exact
lines" first step because the s3dgraphy exporter's edge-emission loop and
node-rendering predicate were not line-mapped during brainstorming; the test
code, target behaviour, exact functions, and the change to make are all
specified. This is a locate-then-edit step, not a content gap. The
`_apply_parallel_bend` helper and the `generate_edge` arrow branch are given in
full.

**Type/name consistency:** `paradata_as_groups` and `continuity_diamonds` are
the two exporter kwargs, passed via `inspect.signature` in graphml_writer
(consistent across Tasks 2 and the existing `[5.12.10-alpha]` code). The
contemporaneity edge-type set `_CONTEMP` is identical in Tasks 3 Step 3 and
Step 4. Helper names (`_export`, `_node_labels`, `_edges`, `_node_degrees`,
`_edges_with_arrows`) are defined once in `test_em_export_rendering.py` and
reused.
