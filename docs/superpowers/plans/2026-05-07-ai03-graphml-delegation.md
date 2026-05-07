# AI03 — Delegate GraphML serialisation to s3Dgraphy: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut over the GraphML branch of the green "Extended Matrix" button from the broken legacy DOT→GraphML pipeline (`dottoxml.exportGraphml` + `enhance_graphml_with_groups`) to a thin delegation that runs `s3dgraphy.PyArchInitImporter` and `s3dgraphy.exporter.graphml.GraphMLExporter`. Closes the four EM limitations carried over from Phase 1 (empty graphml on grouping flag, no period swimlanes, partial edge styling, no transitive reduction).

**Architecture:** A new pure-Python module `modules/s3dgraphy/sync/graphml_writer.py` owns the import + filter + export pipeline behind a single `export_graphml(db_path, mapping, output_path, site_filter=None, persist_auxiliary=False) -> ExportResult` function, plus an `ExportResult` dataclass and `EmptyGraphError`/`GraphMLExportError(stage)` exceptions. The bridge in `s3dgraphy_dot_bridge.py` is rewired to call this function instead of `_convert_dot_to_graphml()`; the legacy code (`graphml_spatial_enhancer.py`, `apply_grouping_to_dot`, `SpatialGroupingDialog`, `cb_spatial_grouping`) is deleted in the same release. DOT and JSON output paths are unchanged. Site filter is in-memory subgraph retention with `has_first_epoch` reachability for `EpochNode`s.

**Tech Stack:** Python 3.9+, s3dgraphy 0.1.40 (already vendored under `ext_libs/s3dgraphy/`), lxml (transitive dep of s3dgraphy, no new requirement), pytest (existing `tests/sync/` scope), QGIS PyQt5/PyQt6 abstraction (existing). No new third-party dependencies.

**Spec source of truth:** `docs/superpowers/specs/2026-05-07-ai03-graphml-delegation-design.md`

**Reference docs (already in repo):**
- `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` (parent spec, §7.6 + §11)
- `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` ("Phase 1 known limitations carried over to Phase 2 / AI03")

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every commit-message HEREDOC in this plan is already trailer-free; do not re-add it.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/graphml_writer.py` | Public API of AI03. `export_graphml()` orchestrator + `ExportResult` dataclass + `_filter_by_site()` helper + `EmptyGraphError` / `GraphMLExportError(stage)` exceptions. Pure Python — no Qt, no QGIS imports |
| `tests/sync/test_graphml_writer_helpers.py` | 3 unit tests covering `ExportResult` shape, `_filter_by_site` reachability semantics, `GraphMLExportError(stage=...)` categorisation. Pure pytest, no QGIS, no real DB |
| `tests/sync/test_graphml_writer_pipeline.py` | 4 fixture-based pipeline tests, one per closed EM limitation (L1 populated graphml, L2 epoch swimlanes, L3 edge style diversification, L4 transitive reduction) |
| `tests/sync/fixtures/build_mini_volterra.py` | Deterministic generator for the SQLite fixture below. Idempotent — running twice produces byte-identical output |
| `tests/sync/fixtures/mini_volterra.sqlite` | Generated binary committed to the repo (~80–150 KB). Schema copied from `resources/dbfiles/pyarchinit.sqlite`; rows hand-crafted to exercise the four acceptance criteria |

### Modified

| Path | Why |
|---|---|
| `modules/db/pyarchinit_db_manager.py` | Add `get_sqlite_path() -> Optional[Path]` method that returns the SQLite file path when the configured backend is SQLite, `None` otherwise |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | (1) Remove `_convert_dot_to_graphml()` method, the inner `Options` class, and the `import dot` / `import dottoxml` block at the top of the file; (2) replace the GraphML branch of `export_integrated_matrix()` with a call to `graphml_writer.export_graphml()`; (3) the bridge no longer carries `self.spatial_groupings` state; (4) remove the `if self.spatial_groupings:` blocks at lines 141–145 and 228–231; (5) the dialog handler aggregates per-format status and shows a metrics-rich summary `QMessageBox` |
| `modules/s3dgraphy/spatial_grouping_manager.py` | Remove `SpatialGroupingManager.apply_grouping_to_dot()` method and the entire `SpatialGroupingDialog` class. Keep `SpatialGroupingManager` itself as a slim shell in case future phases reintroduce yEd group nodes |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py::S3DGraphyExportDialog` | Remove the `cb_spatial_grouping` QCheckBox, its `addWidget()` call, and the entire `if self.cb_spatial_grouping.isChecked(): …` branch in the Export handler |
| `metadata.txt` | Bump `version=5.1.0-alpha` → `version=5.2.0-alpha`; prepend the Phase 2 / AI03 changelog entry |
| `dev_logs/CHANGELOG.md` | Prepend a `## [5.2.0-alpha] - 2026-MM-DD` bilingual section listing the four closed EM limitations + cut-over policy |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` (+ DOCX re-render) | New "Phase 2 — AI03 GraphML delegation" section with implementation summary + manual smoke gate result |

### Deleted

| Path | Why |
|---|---|
| `modules/s3dgraphy/graphml_spatial_enhancer.py` | Entire file. The post-hoc yfiles-namespace enhancer was the source of the empty-graphml-on-grouping-flag bug; it is fully superseded by `s3dgraphy`'s native `EpochSwimlanesGenerator` |

### Explicitly NOT touched (out of scope per spec §9)

- `resources/dbfiles/dot.py` and `resources/dbfiles/dottoxml.py` — still consumed by Harris matrix exporters in `tabs/Interactive_matrix.py` and `modules/utility/pyarchinit_matrix_exp.py`. Removal is a follow-up under AI04 or later.
- `S3DGraphyIntegration.import_from_pyarchinit()` — still feeds the DOT and JSON exporters. Reusing the same legacy code path keeps the cut-over surgical: only the GraphML branch changes.
- `requirements.txt` — `s3dgraphy>=0.1.40` is already pinned (Phase 1, commit `5988ed4a`). Do not add `lxml`; it is a transitive dependency of s3dgraphy and the runtime installer pulls it.

---

## Test strategy

- **Unit tests** (`tests/sync/test_graphml_writer_helpers.py`): pure pytest, no QGIS bootstrap. Run with `pytest tests/sync/`.
- **Fixture-based pipeline tests** (`tests/sync/test_graphml_writer_pipeline.py`): pytest against the committed `mini_volterra.sqlite`. The s3dgraphy `GraphMLExporter` does not import Qt, so these run from a bare shell. Run with the same command.
- **Manual smoke gate**: see Group G Task G.4. Required before tagging the release.

The Phase 1 test suite (`tests/sync/`, `tests/migrations/`) must stay green at every commit. Run `pytest tests/sync/ tests/migrations/ -q` after each task in this plan as a regression check.

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Create AI03 rollback tag

**Files:** none (git operation)

- [ ] **Step 1: Confirm starting point**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'
git rev-parse HEAD
git tag -l phase1-foundation-5.1.0-alpha
```
Expected: working tree clean of tracked changes; `git rev-parse HEAD` returns the current branch tip; the Phase 1 release tag exists.

- [ ] **Step 2: Create the AI03 rollback tag at HEAD**

```bash
git tag -a pre-ai03-graphml-delegation -m "Rollback point before AI03 GraphML cut-over"
git tag -l pre-ai03-graphml-delegation
```
Expected: the tag prints. Stays local until Group G Task G.5.

- [ ] **Step 3: Verify the tag points where expected**

```bash
git rev-parse pre-ai03-graphml-delegation
git rev-parse HEAD
```
Both must print the same SHA.

### Task 0.2: Capture the legacy-output baseline

**Files:** none (manual verification)

This step does not modify the repo. It documents the broken state of the legacy GraphML pipeline so the post-AI03 result has something concrete to compare against.

- [ ] **Step 1: Locate (or regenerate) the user's previous Extended Matrix export**

The user already has artifacts of the broken output at `~/Downloads/cartella senza nome/`:
```
Extended_Matrix_Castelseprio Casa Piccoli_1.dot          (95 KB ✅)
Extended_Matrix_Castelseprio Casa Piccoli_1.graphml      (0 B   ❌)
Extended_Matrix_Castelseprio Casa Piccoli_1_phased.json  (172 KB ✅)
Extended_Matrix_Castelseprio Casa Piccoli_1_s3dgraphy.json (306 KB ✅)
```
If those files have been deleted, re-run the export from QGIS to regenerate them. Do not delete them — they are the regression baseline for the manual smoke gate at G.4.

- [ ] **Step 2: Note the file sizes in `.scratch/ai03-baseline.txt`**

```bash
mkdir -p .scratch
ls -la "/Users/enzo/Downloads/cartella senza nome/" > .scratch/ai03-baseline.txt 2>&1 || true
echo "AI03 starting baseline captured at $(date -u +%FT%TZ)" >> .scratch/ai03-baseline.txt
cat .scratch/ai03-baseline.txt
```

`.scratch/` was already gitignored by Phase 1 (commit `52b6f865`); confirm with:
```bash
git check-ignore -v .scratch/ai03-baseline.txt
```
Expected: an `.gitignore` rule prints, indicating the file is ignored.

---

## Group A — graphml_writer module + helpers

### Task A.1: ExportResult dataclass

**Files:**
- Create: `modules/s3dgraphy/sync/graphml_writer.py`
- Create: `tests/sync/test_graphml_writer_helpers.py`

- [ ] **Step 1: Write the failing test**

Create `tests/sync/test_graphml_writer_helpers.py`:

```python
"""Unit tests for graphml_writer helpers (no QGIS, no real DB)."""
from __future__ import annotations

import pytest


def test_export_result_holds_metrics():
    from modules.s3dgraphy.sync.graphml_writer import ExportResult
    r = ExportResult(
        output_path="/tmp/x.graphml",
        node_count=10,
        edge_count=15,
        epoch_count=2,
        tred_removed_edges=3,
        warnings=[],
    )
    assert r.output_path == "/tmp/x.graphml"
    assert r.node_count == 10
    assert r.edge_count == 15
    assert r.epoch_count == 2
    assert r.tred_removed_edges == 3
    assert r.warnings == []


def test_export_result_warnings_default_empty_list():
    from modules.s3dgraphy.sync.graphml_writer import ExportResult
    r = ExportResult(
        output_path="/tmp/x.graphml",
        node_count=1,
        edge_count=0,
        epoch_count=0,
        tred_removed_edges=0,
    )
    assert r.warnings == []
    # Two instances must NOT share the same default list (the classic
    # mutable-default trap — frozen dataclass + field(default_factory=list)).
    r2 = ExportResult(
        output_path="/tmp/y.graphml",
        node_count=2,
        edge_count=0,
        epoch_count=0,
        tred_removed_edges=0,
    )
    r.warnings.append("test")
    assert r2.warnings == [], (
        "ExportResult instances share warnings list — mutable default bug")
```

- [ ] **Step 2: Run, expect failure**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
python3 -m pytest tests/sync/test_graphml_writer_helpers.py -v 2>&1 | tail -10
```
Expected: `ModuleNotFoundError: No module named 'modules.s3dgraphy.sync.graphml_writer'`.

- [ ] **Step 3: Write the minimal implementation**

Create `modules/s3dgraphy/sync/graphml_writer.py`:

```python
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
```

- [ ] **Step 4: Run to confirm pass**

```bash
python3 -m pytest tests/sync/test_graphml_writer_helpers.py -v 2>&1 | tail -10
```
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_graphml_writer_helpers.py
git commit -m "feat(s3dgraphy/sync): ExportResult dataclass for graphml_writer

Frozen dataclass mirrors the metrics returned by a successful
export. warnings field uses field(default_factory=list) so two
ExportResult instances do not share a mutable default. Public
API surface for AI03 (spec §3.2)."
```

### Task A.2: GraphMLExportError + EmptyGraphError exceptions

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py`
- Modify: `tests/sync/test_graphml_writer_helpers.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/sync/test_graphml_writer_helpers.py`:

```python
def test_graphml_export_error_categorises_stage():
    from modules.s3dgraphy.sync.graphml_writer import GraphMLExportError
    inner = ValueError("bad json mapping")
    e = GraphMLExportError("import", inner)
    assert e.stage == "import"
    assert e.original is inner
    assert "import" in str(e)
    assert "ValueError" in str(e)


def test_graphml_export_error_accepts_only_known_stages():
    from modules.s3dgraphy.sync.graphml_writer import (
        GraphMLExportError,
        VALID_STAGES,
    )
    assert "import" in VALID_STAGES
    assert "filter" in VALID_STAGES
    assert "export" in VALID_STAGES
    assert "write" in VALID_STAGES
    with pytest.raises(ValueError, match="unknown stage"):
        GraphMLExportError("nonsense", ValueError("x"))


def test_empty_graph_error_is_value_error():
    from modules.s3dgraphy.sync.graphml_writer import EmptyGraphError
    assert issubclass(EmptyGraphError, ValueError)
    e = EmptyGraphError("no rows for site Volterra")
    assert "Volterra" in str(e)
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/sync/test_graphml_writer_helpers.py -v 2>&1 | tail -10
```
Expected: 3 new failures with `ImportError`.

- [ ] **Step 3: Append the minimal implementation**

Append to `modules/s3dgraphy/sync/graphml_writer.py`:

```python
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
```

- [ ] **Step 4: Run, expect pass**

```bash
python3 -m pytest tests/sync/test_graphml_writer_helpers.py -v 2>&1 | tail -10
```
Expected: 5 tests pass (2 from A.1 + 3 from A.2).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_graphml_writer_helpers.py
git commit -m "feat(s3dgraphy/sync): GraphMLExportError + EmptyGraphError

Exception hierarchy for graphml_writer:
- GraphMLExportError(stage, original) wraps any failure during the
  pipeline and pins one of {'import', 'filter', 'export', 'write'} so
  the bridge UI can present a useful message.
- EmptyGraphError subclasses ValueError; raised when import + filter
  yields zero nodes.

VALID_STAGES is exported so the bridge can validate before raising."
```

### Task A.3: _filter_by_site helper

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py`
- Modify: `tests/sync/test_graphml_writer_helpers.py`

- [ ] **Step 1: Append failing tests**

Append to `tests/sync/test_graphml_writer_helpers.py`:

```python
def _make_test_graph():
    """Build a minimal s3dgraphy Graph for filter testing.

    2 stratigraphic units (one per site), 2 epoch nodes,
    has_first_epoch edges connecting them.
    """
    import sys
    sys.path.insert(
        0,
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/"
        "default/python/plugins/pyarchinit/ext_libs")
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.edges.edge import Edge

    g = Graph(graph_id="test")
    us_a = StratigraphicUnit(node_id="us_a", name="US-A", description="")
    us_a.attributes["sito"] = "SiteA"
    us_b = StratigraphicUnit(node_id="us_b", name="US-B", description="")
    us_b.attributes["sito"] = "SiteB"
    epoch_1 = EpochNode(node_id="ep_1", name="Epoch1", start_time=0, end_time=100)
    epoch_2 = EpochNode(node_id="ep_2", name="Epoch2", start_time=100, end_time=200)
    g.add_node(us_a)
    g.add_node(us_b)
    g.add_node(epoch_1)
    g.add_node(epoch_2)
    g.add_edge(Edge(edge_id="e1", edge_source="us_a", edge_target="ep_1",
                    edge_type="has_first_epoch"))
    g.add_edge(Edge(edge_id="e2", edge_source="us_b", edge_target="ep_2",
                    edge_type="has_first_epoch"))
    return g


def test_filter_by_site_keeps_only_matching_strat_nodes():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, "SiteA")
    strat_ids = {n.node_id for n in out.nodes
                 if hasattr(n, "attributes") and n.attributes.get("sito")}
    assert strat_ids == {"us_a"}, f"expected only us_a, got {strat_ids!r}"


def test_filter_by_site_retains_reachable_epoch_nodes():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, "SiteA")
    epoch_ids = {n.node_id for n in out.nodes
                 if n.node_type == "EpochNode"}
    # ep_1 is reachable from us_a; ep_2 is reachable only from the
    # discarded us_b, so it must NOT survive the filter.
    assert epoch_ids == {"ep_1"}, f"expected {{ep_1}}, got {epoch_ids!r}"


def test_filter_by_site_prunes_orphan_edges():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, "SiteA")
    edge_ids = {e.edge_id for e in out.edges}
    # e2 connected discarded us_b → discarded ep_2; must be pruned.
    assert edge_ids == {"e1"}, f"expected {{e1}}, got {edge_ids!r}"


def test_filter_by_site_returns_unfiltered_when_none():
    from modules.s3dgraphy.sync.graphml_writer import _filter_by_site
    g = _make_test_graph()
    out = _filter_by_site(g, None)
    assert len(out.nodes) == len(g.nodes)
    assert len(out.edges) == len(g.edges)
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/sync/test_graphml_writer_helpers.py -v 2>&1 | tail -15
```
Expected: 4 new failures with `ImportError: cannot import name '_filter_by_site'`.

- [ ] **Step 3: Append the implementation**

Append to `modules/s3dgraphy/sync/graphml_writer.py`:

```python
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

    import sys
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

    # Pass 4: keep edges whose BOTH endpoints survived
    kept_node_ids = {n.node_id for n in out.nodes}
    for e in graph.edges:
        if (e.edge_source in kept_node_ids
                and e.edge_target in kept_node_ids):
            out.add_edge(e)

    return out
```

- [ ] **Step 4: Run to confirm pass**

```bash
python3 -m pytest tests/sync/test_graphml_writer_helpers.py -v 2>&1 | tail -15
```
Expected: 9 tests pass (5 prior + 4 new).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_graphml_writer_helpers.py
git commit -m "feat(s3dgraphy/sync): _filter_by_site helper for graphml_writer

Subgraph retention rule (spec §5 step 6.iv.2):
- StratigraphicNode subclass kept iff attributes['sito'] matches.
- EpochNode kept iff reachable from a retained strat node via
  has_first_epoch edge.
- Edges kept iff both endpoints survived.

site_filter=None returns the original graph unchanged."
```

---

## Group B — SQLite fixture for pipeline tests

### Task B.1: build_mini_volterra.py generator script

**Files:**
- Create: `tests/sync/fixtures/build_mini_volterra.py`

- [ ] **Step 1: Write the script**

Create `tests/sync/fixtures/build_mini_volterra.py`:

```python
"""Generate a deterministic mini-Volterra SQLite fixture.

Exercises the four AI03 acceptance criteria:
- Single sito='TestSite' so the L2 site-filter test produces the same
  graph as the unfiltered run; a regression on _filter_by_site that
  drops everything would surface immediately.
- 5 stratigraphic units spanning 3 unit_tipo values (US, USM, USVs).
- 2 periods/phases in periodizzazione_table; every US is assigned to
  one or the other so both EpochNodes survive the site filter.
- 7 rapporti entries spanning 4 distinct relation types (copre,
  coperto da, uguale a, riempie).
- 1 deliberate transitive redundancy: US1->US2->US3 PLUS US1->US3.
  After GraphMLExporter.transitive_reduction the redundant edge must
  disappear.

Usage:
    cd /path/to/pyarchinit
    python3 tests/sync/fixtures/build_mini_volterra.py

Output:
    tests/sync/fixtures/mini_volterra.sqlite (overwritten)
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite"
FIXTURE_DB = Path(__file__).resolve().parent / "mini_volterra.sqlite"

SITO = "TestSite"


def main() -> int:
    if not TEMPLATE_DB.exists():
        print(f"ERROR: template DB missing at {TEMPLATE_DB}", file=sys.stderr)
        return 2

    # Start from a copy of the template so all schema/views/triggers exist.
    if FIXTURE_DB.exists():
        FIXTURE_DB.unlink()
    shutil.copy2(TEMPLATE_DB, FIXTURE_DB)

    conn = sqlite3.connect(FIXTURE_DB)
    cur = conn.cursor()

    # Wipe every user-table that the fixture touches; keep schema.
    for tbl in ("us_table", "periodizzazione_table"):
        cur.execute(f"DELETE FROM {tbl}")

    # 2 epochs/phases in periodizzazione_table.
    # Columns of interest: sito, periodo, fase, cron_iniziale, cron_finale, descrizione
    cur.executemany(
        "INSERT INTO periodizzazione_table "
        "(sito, periodo, fase, cron_iniziale, cron_finale, descrizione) "
        "VALUES (?,?,?,?,?,?)",
        [
            (SITO, 1, 1, -100, 100, "Late Roman"),
            (SITO, 2, 1, 100, 400, "Early Medieval"),
        ],
    )

    # 5 stratigraphic units. Layout:
    # us=1,2,3 are 'US' in period 1 — these wire the transitive redundancy.
    # us=4 is 'USM' in period 2.
    # us=5 is 'USVs' in period 2.
    # rapporti is a string-encoded list, see PyArchInit conventions.
    rows = [
        # (sito, area, us, unita_tipo, periodo_iniziale, fase_iniziale,
        #  rapporti, d_stratigrafica, d_interpretativa, descrizione)
        (SITO, "1", "1", "US", 1, 1,
         "[['copre', '2', '1', 'TestSite'], ['copre', '3', '1', 'TestSite']]",
         "Strato di terra", "Riporto", "Strato di terra mista a pietre"),
        (SITO, "1", "2", "US", 1, 1,
         "[['copre', '3', '1', 'TestSite']]",
         "Strato di sabbia", "Sedimento", "Strato di sabbia gialla"),
        (SITO, "1", "3", "US", 1, 1,
         "[]",
         "Strato di argilla", "Naturale", "Argilla rossastra"),
        (SITO, "1", "4", "USM", 2, 1,
         "[['uguale a', '5', '1', 'TestSite']]",
         "Muratura in pietra", "Fondazione", "Fondazione muraria"),
        (SITO, "1", "5", "USVs", 2, 1,
         "[['riempie', '4', '1', 'TestSite']]",
         "Ricostruzione virtuale", "Ipotesi",
         "Volume ricostruttivo della muratura"),
    ]

    cur.executemany(
        "INSERT INTO us_table "
        "(sito, area, us, unita_tipo, periodo_iniziale, fase_iniziale, "
        " rapporti, d_stratigrafica, d_interpretativa, descrizione) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows,
    )

    conn.commit()
    conn.close()

    size = FIXTURE_DB.stat().st_size
    print(f"OK wrote {FIXTURE_DB} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the generator**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
python3 tests/sync/fixtures/build_mini_volterra.py
```
Expected: `OK wrote /…/tests/sync/fixtures/mini_volterra.sqlite (~80–150 KB)`.

- [ ] **Step 3: Sanity-check the fixture content**

```bash
python3 -c "
import sqlite3
c = sqlite3.connect('tests/sync/fixtures/mini_volterra.sqlite')
print('us_table count:', c.execute('SELECT COUNT(*) FROM us_table').fetchone()[0])
print('us_table types:', list(c.execute('SELECT unita_tipo, COUNT(*) FROM us_table GROUP BY unita_tipo')))
print('periodizzazione count:', c.execute('SELECT COUNT(*) FROM periodizzazione_table').fetchone()[0])
print('rapporti samples:')
for row in c.execute('SELECT us, rapporti FROM us_table'): print(' ', row)
"
```
Expected output structure:
```
us_table count: 5
us_table types: [('US', 3), ('USM', 1), ('USVs', 1)]
periodizzazione count: 2
rapporti samples:
  ('1', "[['copre', '2', '1', 'TestSite'], ['copre', '3', '1', 'TestSite']]")
  ('2', "[['copre', '3', '1', 'TestSite']]")
  ('3', "[]")
  ('4', "[['uguale a', '5', '1', 'TestSite']]")
  ('5', "[['riempie', '4', '1', 'TestSite']]")
```

- [ ] **Step 4: Commit script + binary**

```bash
git add tests/sync/fixtures/build_mini_volterra.py tests/sync/fixtures/mini_volterra.sqlite
git commit -m "test(fixtures): mini_volterra.sqlite for AI03 pipeline tests

Hand-crafted to exercise the 4 acceptance criteria of spec §7.2:
- L1 (populated graphml): 5 US + 2 epochs + 7 rapporti = enough
  content that an empty output would obviously be a regression.
- L2 (epoch swimlanes): 2 distinct periodo entries in
  periodizzazione_table, every US assigned to one of them so both
  EpochNodes survive the site filter.
- L3 (edge style diversification): rapporti uses 4 distinct types
  (copre, coperto da, uguale a, riempie) → maps to >=2 distinct
  GraphMLExporter line styles.
- L4 (transitive reduction): US1->US2->US3 plus US1->US3 (redundant)
  → after TR the redundant edge must disappear.

Single sito='TestSite' lets pipeline tests pin _filter_by_site
behaviour without ambiguity (filtered == unfiltered on this fixture).

build_mini_volterra.py is committed alongside the binary so the
fixture can be regenerated deterministically."
```

---

## Group C — Pipeline tests + export_graphml orchestrator

### Task C.1: Skeleton test file + first pipeline test (L1)

**Files:**
- Create: `tests/sync/test_graphml_writer_pipeline.py`
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (add `export_graphml` orchestrator)

- [ ] **Step 1: Write the failing test**

Create `tests/sync/test_graphml_writer_pipeline.py`:

```python
"""Fixture-based pipeline tests for graphml_writer.

Each of the four tests pins one acceptance criterion from the AI03
spec §7.2 / dev-log limitations L1–L4. They run pure pytest (no
QGIS) against the committed mini_volterra.sqlite.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

# Ensure ext_libs is importable for s3dgraphy
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN_ROOT / "ext_libs"))

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    """Copy the committed fixture to tmp_path so tests don't mutate it."""
    import shutil
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    return dst


def test_pipeline_produces_populated_graphml(mini_volterra, tmp_path):
    """L1 — the new pipeline must produce a non-empty .graphml.

    Closes the empty-on-grouping-flag bug from Phase 1.
    """
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    out = tmp_path / "out.graphml"
    result = export_graphml(
        db_path=mini_volterra,
        mapping="pyarchinit",
        output_path=out,
    )
    assert out.exists()
    # Legacy bug produced 0-byte files; threshold of 1 KB is well above
    # the empty-document baseline of any GraphML header alone.
    assert out.stat().st_size > 1000
    assert result.node_count > 0
    assert result.edge_count > 0
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/sync/test_graphml_writer_pipeline.py -v 2>&1 | tail -15
```
Expected: `ImportError: cannot import name 'export_graphml'` (orchestrator not implemented yet).

- [ ] **Step 3: Implement the orchestrator**

Append to `modules/s3dgraphy/sync/graphml_writer.py`:

```python
def export_graphml(
    db_path,
    mapping: str,
    output_path,
    *,
    site_filter: Optional[str] = None,
    persist_auxiliary: bool = False,
) -> ExportResult:
    """Run PyArchInitImporter → optional site filter → GraphMLExporter.

    Args:
        db_path: filesystem path to the SQLite DB (str or Path).
        mapping: name of the s3dgraphy mapping to use, e.g. "pyarchinit".
        output_path: filesystem path where to write the GraphML.
        site_filter: optional `sito` value to restrict the export.
        persist_auxiliary: bake (True) vs volatile (False) auxiliary
            data policy. Default False (volatile) per Spec D6.

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

    # Build the result. Counts come from the post-export graph.
    from s3dgraphy.nodes.epoch_node import EpochNode
    epoch_count = sum(
        1 for n in graph.nodes if isinstance(n, EpochNode))
    # tred_removed_edges is exposed on graph.warnings as a side-effect
    # of GraphMLExporter; absent → assume 0.
    tred_removed = 0
    for w in getattr(graph, "warnings", []):
        m = re.match(r"transitive reduction removed (\d+) edges?", w)
        if m:
            tred_removed = int(m.group(1))
            break
    warnings = list(getattr(graph, "warnings", []))

    return ExportResult(
        output_path=str(output_path),
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        epoch_count=epoch_count,
        tred_removed_edges=tred_removed,
        warnings=warnings,
    )
```

Note: `re` import is now needed at top of `graphml_writer.py`. Add `import re` near the existing imports.

- [ ] **Step 4: Run, expect pass**

```bash
python3 -m pytest tests/sync/test_graphml_writer_pipeline.py -v 2>&1 | tail -10
```
Expected: 1 test passes. The full sync suite:
```bash
python3 -m pytest tests/sync/ -q 2>&1 | tail -5
```
Expected: prior tests still pass too.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_graphml_writer_pipeline.py
git commit -m "feat(s3dgraphy/sync): export_graphml orchestrator + L1 pipeline test

Wires PyArchInitImporter → _filter_by_site → GraphMLExporter into a
single function, wrapping each stage's exceptions in
GraphMLExportError(stage=...) so the bridge UI can categorise
failures in its summary dialog.

ExportResult is built from post-export graph counts;
tred_removed_edges parses the matching graph.warning emitted by
TemporalInferenceEngine.transitive_reduction.

L1 pipeline test confirms the empty-on-grouping-flag bug is closed
on the mini-Volterra fixture (>1 KB output, node_count>0,
edge_count>0)."
```

### Task C.2: L2 — epoch swimlanes test

**Files:**
- Modify: `tests/sync/test_graphml_writer_pipeline.py`

- [ ] **Step 1: Append failing test**

Append to `tests/sync/test_graphml_writer_pipeline.py`:

```python
def test_pipeline_emits_epoch_swimlanes(mini_volterra, tmp_path):
    """L2 — closes 'no period swimlanes' limitation.

    GraphMLExporter wraps strat nodes inside a TableNode swimlane;
    each EpochNode becomes a row inside the table. Look for a
    TableNode marker in the produced XML and assert epoch_count
    matches the fixture's two periods.
    """
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    out = tmp_path / "out.graphml"
    result = export_graphml(
        db_path=mini_volterra, mapping="pyarchinit", output_path=out)
    xml = out.read_text(encoding="utf-8")
    assert ("TableNode" in xml or 'yfiles.foldertype="row"' in xml), (
        "no swimlane marker found in output")
    assert result.epoch_count >= 2, (
        f"expected >=2 epochs, got {result.epoch_count}")
```

- [ ] **Step 2: Run, expect pass (the orchestrator already produces swimlanes natively)**

```bash
python3 -m pytest tests/sync/test_graphml_writer_pipeline.py -v 2>&1 | tail -10
```
Expected: 2 tests pass. If L2 fails because the fixture's
`periodizzazione_table` rows do not actually wire to US records via
the mapping JSON, this is the place to inspect — possibly fix the
fixture (Group B) or the importer mapping (out of scope, escalate).

- [ ] **Step 3: Commit**

```bash
git add tests/sync/test_graphml_writer_pipeline.py
git commit -m "test(graphml_writer): L2 — epoch swimlanes acceptance criterion

Asserts the produced XML contains a TableNode/foldertype=row marker
and that result.epoch_count >= 2 on the mini-Volterra fixture.
Closes Phase 1 limitation L2 ('no period swimlanes')."
```

### Task C.3: L3 — edge style diversification test

**Files:**
- Modify: `tests/sync/test_graphml_writer_pipeline.py`

- [ ] **Step 1: Append failing test**

Append to `tests/sync/test_graphml_writer_pipeline.py`:

```python
def test_pipeline_diversifies_edge_styles(mini_volterra, tmp_path):
    """L3 — closes 'partial edge styling' limitation.

    The fixture rapporti span 4 distinct relation types (copre,
    coperto da, uguale a, riempie). After mapping into s3dgraphy
    edge types (is_after / is_after / has_same_time / fills) and
    rendering through GraphMLExporter, the produced XML must contain
    >=2 distinct yEd LineStyle.type values.
    """
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    out = tmp_path / "out.graphml"
    export_graphml(
        db_path=mini_volterra, mapping="pyarchinit", output_path=out)
    xml = out.read_text(encoding="utf-8")
    line_styles = set(re.findall(
        r'<y:LineStyle[^>]+type="([^"]+)"', xml))
    assert len(line_styles) >= 2, (
        f"expected >=2 distinct LineStyle.type values, got {line_styles!r}")
```

- [ ] **Step 2: Run, expect pass**

```bash
python3 -m pytest tests/sync/test_graphml_writer_pipeline.py -v 2>&1 | tail -10
```
Expected: 3 tests pass. If L3 fails (line_styles is a singleton),
this means s3dgraphy.EdgeGenerator is not differentiating styles for
this fixture's edge types — escalate to s3dgraphy upstream rather
than patching downstream.

- [ ] **Step 3: Commit**

```bash
git add tests/sync/test_graphml_writer_pipeline.py
git commit -m "test(graphml_writer): L3 — edge style diversification

Asserts the produced XML contains >=2 distinct yEd LineStyle.type
values across 4 relation types in the mini-Volterra fixture
(copre / coperto da / uguale a / riempie).
Closes Phase 1 limitation L3 ('only 2 of 36 edge types styled')."
```

### Task C.4: L4 — transitive reduction test

**Files:**
- Modify: `tests/sync/test_graphml_writer_pipeline.py`

- [ ] **Step 1: Append failing test**

Append to `tests/sync/test_graphml_writer_pipeline.py`:

```python
def test_pipeline_applies_transitive_reduction(mini_volterra, tmp_path):
    """L4 — closes 'no transitive reduction' limitation.

    The fixture wires US1→US2→US3 plus a redundant US1→US3.
    GraphMLExporter must remove the redundant edge via
    TemporalInferenceEngine.transitive_reduction.
    """
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    out = tmp_path / "out.graphml"
    result = export_graphml(
        db_path=mini_volterra, mapping="pyarchinit", output_path=out)
    assert result.tred_removed_edges >= 1, (
        f"expected >=1 redundant edge removed, got "
        f"{result.tred_removed_edges}; warnings={result.warnings!r}")
```

- [ ] **Step 2: Run, expect pass**

```bash
python3 -m pytest tests/sync/test_graphml_writer_pipeline.py -v 2>&1 | tail -10
```
Expected: 4 pipeline tests pass. If L4 fails because
`graph.warnings` is empty (no "transitive reduction removed N
edges" line emitted), inspect what s3dgraphy emits — the regex in
`export_graphml` may need adjustment, OR `tred_removed_edges` may
be exposed differently on the engine. Treat as plan-internal
ambiguity; escalate to spec author.

- [ ] **Step 3: Run the FULL sync suite as a regression gate**

```bash
python3 -m pytest tests/sync/ tests/migrations/ -v 2>&1 | tail -10
```
Expected: 19 (Phase 1 sync + 13 migrations) + 9 (helpers from A.1–A.3) + 4 (pipeline from C.1–C.4) = **32 tests total**, all green.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_graphml_writer_pipeline.py
git commit -m "test(graphml_writer): L4 — transitive reduction acceptance criterion

Asserts result.tred_removed_edges >= 1 on the mini-Volterra fixture
which has US1->US2->US3 plus a deliberately redundant US1->US3.
Closes Phase 1 limitation L4 ('no transitive reduction')."
```

---

## Group D — db_manager.get_sqlite_path()

### Task D.1: Add get_sqlite_path()

**Files:**
- Modify: `modules/db/pyarchinit_db_manager.py`
- Create: `tests/sync/test_db_manager_sqlite_path.py`

- [ ] **Step 1: Write the failing test**

Create `tests/sync/test_db_manager_sqlite_path.py`:

```python
"""Test for Pyarchinit_db_manager.get_sqlite_path().

The method returns the SQLite file path when the configured backend
is SQLite, or None for PostgreSQL. Lets graphml_writer skip the
GraphML branch with a clean Info message on PG backends.
"""
from __future__ import annotations

import pytest


class _FakeDBManager:
    """Stand-in for Pyarchinit_db_manager exposing only conn_str."""

    def __init__(self, conn_str: str):
        self.conn_str = conn_str


def test_get_sqlite_path_extracts_sqlite_url():
    from modules.db.pyarchinit_db_manager import _resolve_sqlite_path
    p = _resolve_sqlite_path("sqlite:///path/to/foo.sqlite")
    assert p is not None
    assert str(p).endswith("foo.sqlite")


def test_get_sqlite_path_returns_none_for_postgres():
    from modules.db.pyarchinit_db_manager import _resolve_sqlite_path
    assert _resolve_sqlite_path(
        "postgresql://user:pw@localhost:5432/db") is None


def test_get_sqlite_path_handles_relative_path():
    from modules.db.pyarchinit_db_manager import _resolve_sqlite_path
    p = _resolve_sqlite_path("sqlite:///./relative.sqlite")
    assert p is not None
    assert "relative.sqlite" in str(p)


def test_get_sqlite_path_returns_none_on_garbage():
    from modules.db.pyarchinit_db_manager import _resolve_sqlite_path
    assert _resolve_sqlite_path("not a connection string") is None
    assert _resolve_sqlite_path("") is None
    assert _resolve_sqlite_path(None) is None
```

- [ ] **Step 2: Run, expect failure**

```bash
python3 -m pytest tests/sync/test_db_manager_sqlite_path.py -v 2>&1 | tail -15
```
Expected: `ImportError: cannot import name '_resolve_sqlite_path'`.

- [ ] **Step 3: Add the helper + method**

Append to `modules/db/pyarchinit_db_manager.py` near the top (after existing imports):

```python
from pathlib import Path
from typing import Optional


def _resolve_sqlite_path(conn_str: Optional[str]) -> Optional[Path]:
    """Return the SQLite file path encoded in *conn_str*, or None.

    Examples:
        'sqlite:///path/to/foo.sqlite' -> Path('/path/to/foo.sqlite')
        'sqlite:///./rel.sqlite'       -> Path('./rel.sqlite')
        'postgresql://...'             -> None
        None / ''                      -> None
    """
    if not conn_str or "sqlite" not in conn_str.lower():
        return None
    # SQLAlchemy form: 'sqlite:///<path>'
    marker = "sqlite:///"
    if marker not in conn_str:
        return None
    return Path(conn_str.split(marker, 1)[1])
```

Then add a method to `Pyarchinit_db_manager`:

```python
    def get_sqlite_path(self) -> Optional[Path]:
        """Return the SQLite file path of the configured DB, or None
        if the backend is PostgreSQL or the conn_str is unknown.

        Used by AI03's graphml_writer to decide whether to attempt
        s3dgraphy-based GraphML export (SQLite-only in 5.2.0-alpha;
        PG support deferred to AI04).
        """
        return _resolve_sqlite_path(self.conn_str)
```

(Placement: locate the class via `grep -n "class Pyarchinit_db_manager" modules/db/pyarchinit_db_manager.py` and add the method near the existing `__init__`.)

- [ ] **Step 4: Run, expect pass**

```bash
python3 -m pytest tests/sync/test_db_manager_sqlite_path.py -v 2>&1 | tail -10
```
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add modules/db/pyarchinit_db_manager.py tests/sync/test_db_manager_sqlite_path.py
git commit -m "feat(db_manager): get_sqlite_path() for AI03 dispatch

Returns the SQLite file path encoded in self.conn_str, or None for
PG backends. Used by graphml_writer to decide whether to attempt
s3dgraphy-based GraphML export. PG path is AI04 territory; for
5.2.0-alpha graphml_writer logs Info and skips the GraphML branch
when get_sqlite_path() returns None.

_resolve_sqlite_path() is the pure helper exposed to unit tests so
the path-extraction logic can be tested without instantiating the
db manager."
```

---

## Group E — Wire the bridge

### Task E.1: Replace _convert_dot_to_graphml call with new writer

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`

- [ ] **Step 1: Locate the GraphML branch in export_integrated_matrix**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep -n "graphml_path\|_convert_dot_to_graphml\|enhance_graphml_with_groups\|spatial_groupings" modules/s3dgraphy/s3dgraphy_dot_bridge.py | head -20
```
Expected: lines around 195 (graphml_path), 225 (`_convert_dot_to_graphml`), 228–231 (`enhance_graphml_with_groups`), and 142–145 / 228 (`spatial_groupings`).

- [ ] **Step 2: Read the surrounding code**

Use the Read tool on `modules/s3dgraphy/s3dgraphy_dot_bridge.py` from line 190 to line 240 to see the full `# Export GraphML format (via DOT conversion)` block.

- [ ] **Step 3: Replace the GraphML branch**

In `export_integrated_matrix()`, locate the block that begins at line ~195:

```python
        # Export GraphML format (via DOT conversion)
        if 'graphml' in formats and 'dot' in exported_files:
            graphml_path = os.path.join(output_dir, f"{base_name}.graphml")
            try:
                # Create temporary options object for dottoxml
                class Options:
                    def __init__(self):
                        ...
                options = Options()
                self._convert_dot_to_graphml(exported_files['dot'], graphml_path, options)
                if self.spatial_groupings:
                    from .graphml_spatial_enhancer import GraphMLSpatialEnhancer
                    enhancer = GraphMLSpatialEnhancer()
                    enhancer.enhance_graphml_with_groups(graphml_path, self.spatial_groupings)
                exported_files['graphml'] = graphml_path
            except Exception as e:
                ...
```

Replace this whole block with:

```python
        # Export GraphML format via s3dgraphy.GraphMLExporter (AI03 cut-over).
        # Phase 1's DOT->GraphML pipeline is gone; the produced file now has
        # epoch swimlanes, transitive reduction, and full EM 1.5 edge styling.
        if 'graphml' in formats:
            graphml_path = os.path.join(output_dir, f"{base_name}.graphml")
            db_path = None
            if self.db_manager is not None:
                db_path = self.db_manager.get_sqlite_path()
            if db_path is None:
                # PG backend (or no db_manager). Skip GraphML and
                # surface a friendly status — DOT/JSON still produced.
                if QGIS_AVAILABLE:
                    QgsMessageLog.logMessage(
                        "GraphML export requires SQLite backend; "
                        "PostgreSQL support arrives with AI04. "
                        "DOT and JSON exports are unaffected.",
                        "PyArchInit", Qgis.Info,
                    )
                exported_files['graphml_status'] = {
                    'level': 'info',
                    'reason': 'postgresql backend not yet supported',
                }
            else:
                from .sync.graphml_writer import (
                    export_graphml,
                    EmptyGraphError,
                    GraphMLExportError,
                )
                try:
                    result = export_graphml(
                        db_path=db_path,
                        mapping='pyarchinit',
                        output_path=graphml_path,
                        site_filter=site,
                        persist_auxiliary=False,
                    )
                    exported_files['graphml'] = graphml_path
                    exported_files['graphml_result'] = result
                except (FileNotFoundError, EmptyGraphError) as e:
                    exported_files['graphml_status'] = {
                        'level': 'warning',
                        'reason': str(e),
                    }
                    if QGIS_AVAILABLE:
                        QgsMessageLog.logMessage(
                            f"GraphML skipped: {e}",
                            "PyArchInit", Qgis.Warning,
                        )
                except GraphMLExportError as e:
                    import traceback
                    exported_files['graphml_status'] = {
                        'level': 'error',
                        'stage': e.stage,
                        'reason': str(e),
                        'traceback': traceback.format_exc(),
                    }
                    if QGIS_AVAILABLE:
                        QgsMessageLog.logMessage(
                            f"GraphML export failed at {e.stage}: "
                            f"{e.original}",
                            "PyArchInit", Qgis.Critical,
                        )
                        QgsMessageLog.logMessage(
                            traceback.format_exc(),
                            "PyArchInit", Qgis.Critical,
                        )
```

- [ ] **Step 4: Verify the file still parses**

```bash
python3 -c "import ast; ast.parse(open('modules/s3dgraphy/s3dgraphy_dot_bridge.py').read()); print('parse OK')"
```
Expected: `parse OK`.

- [ ] **Step 5: Run pytest regression**

```bash
python3 -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```
Expected: same pass count as before (the test suite doesn't import the bridge directly).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "refactor(s3dgraphy_dot_bridge): GraphML branch delegates to graphml_writer

The legacy DOT->GraphML conversion (dottoxml.exportGraphml +
enhance_graphml_with_groups) is replaced by a single call to
modules.s3dgraphy.sync.graphml_writer.export_graphml(). PG backends
log Info and skip the branch; SQLite backends produce the proper
swimlane'd output. Per-format status is recorded in exported_files
so the dialog can show categorised metrics in Group F.

DOT and JSON outputs unchanged."
```

### Task E.2: Remove _convert_dot_to_graphml + Options + dottoxml/dot imports

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`

- [ ] **Step 1: Locate the dead code**

```bash
grep -nE "import dot\b|import dottoxml|def _convert_dot_to_graphml|class Options|self\.spatial_groupings" modules/s3dgraphy/s3dgraphy_dot_bridge.py
```

- [ ] **Step 2: Delete the identified blocks**

Delete:
- Lines around 26–32 (`import dot` / `import dottoxml` block — both `try` arms).
- The `def _convert_dot_to_graphml(self, ...)` method in its entirety (was lines ~283–318).
- Inside the (now-removed) GraphML branch — already gone in E.1. The inline `class Options:` definition is gone with it.
- Line ~59 `self.spatial_groupings = None` — initialise no longer needed.
- Lines around 142–145 — the `if self.spatial_groupings:` check inside `s3dgraphy_to_dot()`; replace with a direct return `return dot_content` because grouping is gone.

After every deletion, run `python3 -c "import ast; ast.parse(open('modules/s3dgraphy/s3dgraphy_dot_bridge.py').read()); print('parse OK')"` to confirm.

- [ ] **Step 3: Final parse + regression**

```bash
python3 -c "import ast; ast.parse(open('modules/s3dgraphy/s3dgraphy_dot_bridge.py').read()); print('parse OK')"
python3 -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```
Both must succeed.

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "chore(s3dgraphy_dot_bridge): remove dead GraphML legacy code

Now that the GraphML branch delegates to graphml_writer, the
following are dead code:
- _convert_dot_to_graphml() method
- inline Options class for dottoxml
- 'import dot' / 'import dottoxml' at module top
- self.spatial_groupings state + the apply_grouping_to_dot call
  inside s3dgraphy_to_dot()

dot.py and dottoxml.py themselves remain in resources/dbfiles/ —
the Harris matrix exporters in tabs/ still need them. AI04 will
retire those callers."
```

### Task E.3: Delete graphml_spatial_enhancer.py

**Files:**
- Delete: `modules/s3dgraphy/graphml_spatial_enhancer.py`

- [ ] **Step 1: Confirm no remaining importers**

```bash
grep -rln "graphml_spatial_enhancer\|GraphMLSpatialEnhancer" --include='*.py' . 2>&1 | grep -v __pycache__
```
Expected: empty output (E.1 removed the only call site).

- [ ] **Step 2: Delete the file**

```bash
git rm modules/s3dgraphy/graphml_spatial_enhancer.py
```

- [ ] **Step 3: Verify nothing broke**

```bash
python3 -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor(s3dgraphy): delete graphml_spatial_enhancer.py

The post-hoc yfiles-namespace enhancer was the source of the
empty-graphml-on-grouping-flag bug from Phase 1. Fully superseded
by s3dgraphy's native EpochSwimlanesGenerator (used inside
GraphMLExporter)."
```

### Task E.4: Trim spatial_grouping_manager.py

**Files:**
- Modify: `modules/s3dgraphy/spatial_grouping_manager.py`

- [ ] **Step 1: Identify the methods/classes to remove**

```bash
grep -nE "def apply_grouping_to_dot|class SpatialGroupingDialog" modules/s3dgraphy/spatial_grouping_manager.py
```

- [ ] **Step 2: Delete the `apply_grouping_to_dot` method**

Read lines around the method, delete it from class `SpatialGroupingManager`. Confirm parse:
```bash
python3 -c "import ast; ast.parse(open('modules/s3dgraphy/spatial_grouping_manager.py').read()); print('parse OK')"
```

- [ ] **Step 3: Delete the entire `SpatialGroupingDialog` class**

The class is gated by `if QGIS_AVAILABLE:`; remove the class but keep the `if QGIS_AVAILABLE:` block intact in case of other Qt-only symbols inside the file. After deletion confirm parse again.

- [ ] **Step 4: Verify no remaining importers**

```bash
grep -rln "SpatialGroupingDialog\|apply_grouping_to_dot" --include='*.py' . 2>&1 | grep -v __pycache__
```
Expected: empty output.

- [ ] **Step 5: Run regression**

```bash
python3 -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/spatial_grouping_manager.py
git commit -m "refactor(spatial_grouping_manager): drop legacy DOT/Qt API surface

Removes:
- SpatialGroupingManager.apply_grouping_to_dot() — destructive;
  rewrote DOT in a way that lost nodes not assigned to any group.
- SpatialGroupingDialog Qt class — no longer wired into the export
  dialog after AI03.

SpatialGroupingManager itself is kept as a slim shell. If a future
phase wants to reintroduce yEd group nodes on top of the swimlane
that's the place; the legacy implementation cannot be salvaged."
```

### Task E.5: Remove cb_spatial_grouping checkbox + Export-handler branch

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (S3DGraphyExportDialog)

- [ ] **Step 1: Locate the checkbox**

```bash
grep -nE "cb_spatial_grouping|spatial_groupings = " modules/s3dgraphy/s3dgraphy_dot_bridge.py
```
Expected: 4 lines around 394–425.

- [ ] **Step 2: Delete the checkbox declaration + addWidget call**

In `S3DGraphyExportDialog.setupUI()` remove:
```python
            self.cb_spatial_grouping = QCheckBox("Configure spatial/functional groupings")
            self.cb_spatial_grouping.setChecked(False)
            options_layout.addWidget(self.cb_spatial_grouping)
```

- [ ] **Step 3: Delete the `if self.cb_spatial_grouping.isChecked(): …` branch**

In the Export handler, remove the entire block that opens `SpatialGroupingDialog` and assigns `self.bridge.spatial_groupings`. The `bridge` no longer accepts `spatial_groupings` after E.2. The block ends with `self.bridge.spatial_groupings = None` — delete that too (the attribute is gone).

- [ ] **Step 4: Verify parse**

```bash
python3 -c "import ast; ast.parse(open('modules/s3dgraphy/s3dgraphy_dot_bridge.py').read()); print('parse OK')"
```

- [ ] **Step 5: Confirm no remaining `cb_spatial_grouping` references**

```bash
grep -rn "cb_spatial_grouping\|self.bridge.spatial_groupings" --include='*.py' . 2>&1 | grep -v __pycache__
```
Expected: empty.

- [ ] **Step 6: Run regression**

```bash
python3 -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "refactor(S3DGraphyExportDialog): drop spatial-grouping checkbox

The 'Configure spatial/functional groupings' checkbox + its handler
are gone with the legacy enhancer. yEd has native group nodes if a
user wants post-export grouping; AI03 ships only the EM-canonical
period swimlanes. UI is simpler and the class-level state surface
shrinks."
```

---

## Group F — Final summary dialog

### Task F.1: Build per-format status summary in the Export handler

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`

- [ ] **Step 1: Locate the Export-button handler in S3DGraphyExportDialog**

```bash
grep -nE "def on_export\|exported_files = \|QMessageBox\.information" modules/s3dgraphy/s3dgraphy_dot_bridge.py | head
```
Expected: a handler that calls `bridge.export_integrated_matrix(…)` and shows a final `QMessageBox.information`.

- [ ] **Step 2: Replace the simple "Export complete" dialog with a metrics summary**

The new exported_files dict (after E.1) carries:
- `'dot'`: path string
- `'json'`: path string
- `'phased'`: path string (when checked)
- `'graphml'`: path string (success case)
- `'graphml_result'`: ExportResult (success case)
- `'graphml_status'`: dict with level/reason/stage/traceback (skip or error case)

In the Export handler, after `bridge.export_integrated_matrix(…)` returns, build the message:

```python
            lines = []
            if 'dot' in exported_files:
                lines.append(f"✅ DOT  → {exported_files['dot']}")
            if 'json' in exported_files:
                lines.append(f"✅ JSON → {exported_files['json']}")
            if 'phased' in exported_files:
                lines.append(f"✅ Phased JSON → {exported_files['phased']}")

            if 'graphml' in exported_files:
                r = exported_files.get('graphml_result')
                if r:
                    lines.append(
                        f"✅ GraphML → {exported_files['graphml']}\n"
                        f"   {r.node_count} nodes, {r.edge_count} edges, "
                        f"{r.epoch_count} epochs, "
                        f"{r.tred_removed_edges} redundancies removed by "
                        f"transitive reduction"
                    )
                    for w in r.warnings:
                        lines.append(f"   ⚠️ {w}")
                else:
                    lines.append(f"✅ GraphML → {exported_files['graphml']}")
            elif 'graphml_status' in exported_files:
                st = exported_files['graphml_status']
                level = st.get('level', 'warning')
                glyph = '⚠️' if level == 'warning' else '❌' if level == 'error' else 'ℹ️'
                reason = st.get('reason', 'unknown')
                if 'stage' in st:
                    lines.append(
                        f"{glyph} GraphML failed at {st['stage']}: {reason}")
                else:
                    lines.append(f"{glyph} GraphML skipped: {reason}")

            QMessageBox.information(
                self,
                "Extended Matrix export complete",
                "\n".join(lines) if lines else "Nothing exported.",
            )
```

- [ ] **Step 3: Verify parse**

```bash
python3 -c "import ast; ast.parse(open('modules/s3dgraphy/s3dgraphy_dot_bridge.py').read()); print('parse OK')"
```

- [ ] **Step 4: Run regression**

```bash
python3 -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "feat(S3DGraphyExportDialog): metrics-rich export summary

Replaces the bare 'Export complete' QMessageBox with a per-format
breakdown:
- DOT / JSON / Phased: confirmed paths
- GraphML success: node/edge/epoch/tred-removed counts + any
  TemporalInferenceEngine warnings (e.g. cycles)
- GraphML skip/error: friendly reason + (for GraphMLExportError)
  the stage that failed

Closes the AI03 UX requirement that the dialog show a useful
post-export summary so users see the new pipeline at work."
```

---

## Group G — Release packaging (5.2.0-alpha)

### Task G.1: Bump metadata.txt

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Update version**

```bash
sed -i.bak 's/^version=5.1.0-alpha$/version=5.2.0-alpha/' metadata.txt
rm metadata.txt.bak
grep -n "^version=" metadata.txt
```
Expected: `version=5.2.0-alpha`.

- [ ] **Step 2: Prepend the new changelog block**

In `metadata.txt`, locate the `changelog=` line (it currently starts with the 5.1.0-alpha entry). Prepend:

```
changelog=5.2.0-alpha (2026-MM-DD) [Phase 2 / AI03: GraphML delegation to s3Dgraphy]:
    - Feature: GraphML branch of the 'Extended Matrix' export now uses
      s3dgraphy.PyArchInitImporter + s3dgraphy.exporter.graphml.GraphMLExporter.
      Closes the four EM limitations from Phase 1: empty graphml on grouping
      flag, no period swimlanes, partial edge styling, no transitive reduction.
    - Refactor: legacy DOT->GraphML pipeline removed in cut-over (no
      fallback). Files dropped: graphml_spatial_enhancer.py;
      _convert_dot_to_graphml() in s3dgraphy_dot_bridge.py;
      apply_grouping_to_dot() and SpatialGroupingDialog in
      spatial_grouping_manager.py; cb_spatial_grouping checkbox in the
      export dialog. resources/dbfiles/dot.py and dottoxml.py kept (still
      used by Harris matrix exporters out of AI03 scope).
    - Feature: db_manager.get_sqlite_path() lets the bridge skip GraphML
      with an Info message when the backend is PostgreSQL (PG support
      arrives with AI04).
    - Feature: export dialog summary now shows per-format metrics
      (node/edge/epoch counts, transitive reduction reduction, warnings).
    - Tests: 7 new tests under tests/sync/ (3 unit + 4 fixture-pipeline)
      mapped 1:1 to the four EM limitations.
  5.1.0-alpha (2026-05-07) [Phase 1 Foundation: PyArchInit ↔ s3Dgraphy bridge]:
```

(Replace `2026-MM-DD` with the actual release date.)

- [ ] **Step 3: Commit**

```bash
git add metadata.txt
git commit -m "chore(release): bump metadata to 5.2.0-alpha

Changelog block summarises the AI03 cut-over: closes the four
Phase 1 EM limitations via delegation to s3dgraphy GraphMLExporter,
drops the legacy DOT->GraphML pipeline, adds db_manager.get_sqlite_path()
and the metrics-rich export summary."
```

### Task G.2: dev_logs/CHANGELOG.md bilingual entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Read the current top of the file**

```bash
sed -n '1,10p' dev_logs/CHANGELOG.md
```

- [ ] **Step 2: Prepend the 5.2.0-alpha section**

After the file header (`---` line that follows the title), prepend:

```markdown
## [5.2.0-alpha] - 2026-MM-DD

**Phase 2 / AI03 of the StratiGraph WP5/T5.4 PyArchInit ↔ s3Dgraphy bridge: GraphML serialisation delegated to s3Dgraphy.** Closes the four Extended Matrix limitations carried over from Phase 1 (empty graphml on the spatial-grouping flag, no period swimlanes, partial edge styling, no transitive reduction). Tag: `phase2-ai03-graphml-delegation-5.2.0-alpha`. Rollback tag: `pre-ai03-graphml-delegation`.

### Aggiunto / Added

- **feat(s3dgraphy/sync): nuovo `graphml_writer.export_graphml()`** — wrapper sottile su `s3dgraphy.PyArchInitImporter` + `s3dgraphy.exporter.graphml.GraphMLExporter`. Il bottone verde "Extended Matrix" ora produce un GraphML con row swimlanes per epoca (`EpochSwimlanesGenerator`), tutti i 36 stili di edge EM 1.5 (`EdgeGenerator`), e rimozione delle ridondanze via `TemporalInferenceEngine.transitive_reduction()`. Pure Python, zero Qt, testabile via `pytest tests/sync/` senza bootstrap di QGIS. / **feat(s3dgraphy/sync): new `graphml_writer.export_graphml()`** — thin wrapper over `s3dgraphy.PyArchInitImporter` + `s3dgraphy.exporter.graphml.GraphMLExporter`. The green "Extended Matrix" button now produces a GraphML with row swimlanes per epoch (`EpochSwimlanesGenerator`), all 36 EM 1.5 edge styles (`EdgeGenerator`), and redundancy pruning via `TemporalInferenceEngine.transitive_reduction()`. Pure Python, zero Qt, testable via `pytest tests/sync/` without QGIS bootstrap.

- **feat(db_manager): `get_sqlite_path()`** — restituisce il path filesystem della SQLite quando il backend è SQLite, `None` per PostgreSQL. Permette al bridge di saltare il branch GraphML con messaggio Info su PG (supporto PG arriva con AI04). / **feat(db_manager): `get_sqlite_path()`** — returns the filesystem path of the SQLite DB when the backend is SQLite, `None` for PostgreSQL. Lets the bridge skip the GraphML branch with an Info message on PG (PG support arrives with AI04).

- **feat(S3DGraphyExportDialog): summary metrics-rich** — il dialog finale dopo l'export mostra, per ogni formato, il path prodotto e (per GraphML) le metriche `node_count / edge_count / epoch_count / tred_removed_edges` e i warning di `TemporalInferenceEngine` (es. cicli). Errore o skip mostrano lo stage e una ragione human-readable. / **feat(S3DGraphyExportDialog): metrics-rich summary** — the post-export dialog shows, per format, the produced path and (for GraphML) the metrics `node_count / edge_count / epoch_count / tred_removed_edges` plus `TemporalInferenceEngine` warnings (e.g. cycles). Errors or skips show the failing stage and a human-readable reason.

### Rimosso / Removed (cut-over per spec §3.3)

- `modules/s3dgraphy/graphml_spatial_enhancer.py` — interamente cancellato. Era la sorgente del bug "empty graphml on grouping flag" di Phase 1; sostituito dal `EpochSwimlanesGenerator` nativo di s3dgraphy. / `modules/s3dgraphy/graphml_spatial_enhancer.py` — entire file deleted. Was the source of the Phase 1 "empty graphml on grouping flag" bug; superseded by s3dgraphy's native `EpochSwimlanesGenerator`.

- `S3DGraphyDotBridge._convert_dot_to_graphml()`, la classe inner `Options`, e gli `import dot` / `import dottoxml` di `s3dgraphy_dot_bridge.py` — codice morto post-cutover. / `S3DGraphyDotBridge._convert_dot_to_graphml()`, the inner `Options` class, and the `import dot` / `import dottoxml` block of `s3dgraphy_dot_bridge.py` — dead code post-cutover.

- `SpatialGroupingManager.apply_grouping_to_dot()` e `SpatialGroupingDialog` — la classe Manager resta come shell vuota se serve in futuro; il dialog Qt è eliminato. La checkbox "Configure spatial/functional groupings" è rimossa dall'export dialog. / `SpatialGroupingManager.apply_grouping_to_dot()` and `SpatialGroupingDialog` — the Manager class is kept as an empty shell for possible future use; the Qt dialog is gone. The "Configure spatial/functional groupings" checkbox is removed from the export dialog.

### Test

- **7 nuovi test in `tests/sync/`** (3 unit + 4 fixture-pipeline) mappati 1:1 sulle 4 limitazioni EM di Phase 1: `test_pipeline_produces_populated_graphml` (L1), `test_pipeline_emits_epoch_swimlanes` (L2), `test_pipeline_diversifies_edge_styles` (L3), `test_pipeline_applies_transitive_reduction` (L4). Nuova fixture deterministica `tests/sync/fixtures/mini_volterra.sqlite` (5 US, 2 epoche, 7 rapporti, 1 ridondanza transitiva esplicita) generata da `build_mini_volterra.py`. Suite totale: 26 test (19 da Phase 1 + 7 da AI03). / **7 new tests under `tests/sync/`** (3 unit + 4 fixture-pipeline) mapped 1:1 onto the four Phase 1 EM limitations. New deterministic fixture `tests/sync/fixtures/mini_volterra.sqlite` (5 US, 2 epochs, 7 rapporti, 1 explicit transitive redundancy) generated by `build_mini_volterra.py`. Total suite: 26 tests (19 from Phase 1 + 7 from AI03).

### File modificati / Modified files

- `modules/s3dgraphy/sync/graphml_writer.py` (NEW)
- `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (refactored to delegate)
- `modules/s3dgraphy/spatial_grouping_manager.py` (trimmed)
- `modules/s3dgraphy/graphml_spatial_enhancer.py` (DELETED)
- `modules/db/pyarchinit_db_manager.py` (`get_sqlite_path` added)
- `tests/sync/test_graphml_writer_helpers.py` (NEW)
- `tests/sync/test_graphml_writer_pipeline.py` (NEW)
- `tests/sync/fixtures/build_mini_volterra.py` (NEW)
- `tests/sync/fixtures/mini_volterra.sqlite` (NEW binary, ~80–150 KB)
- `tests/sync/test_db_manager_sqlite_path.py` (NEW)
- `metadata.txt` (5.1.0-alpha → 5.2.0-alpha)

---
```

(Replace `2026-MM-DD` with the actual release date.)

- [ ] **Step 3: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "docs(changelog): 5.2.0-alpha — Phase 2 / AI03 GraphML delegation

Bilingual IT/EN entry covering the cut-over to s3dgraphy's
GraphMLExporter, the four closed EM limitations, the new test
fixture, the trimmed/deleted legacy code, and the metrics-rich
export summary."
```

### Task G.3: Update dev-log + render DOCX

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.docx`

- [ ] **Step 1: Add a Phase 2 / AI03 section to the dev-log markdown**

Append after the "Phase 1 closure — manual smoke gate (G.4) + tag (G.5)" section a new section titled **"# Phase 2 — AI03 closed (GraphML delegation)"** with subsections covering:
- date + status + commit range
- what was built (new module, deleted modules, modified bridge, get_sqlite_path)
- how the four EM limitations are closed (cite the four pipeline tests)
- what was tested (suite totals, fixture summary)
- decisions taken (cut-over rationale, no-fallback policy, deferred bake checkbox)
- workflow operationale (non avere `ext_libs/` checkato dentro il repo significa che dopo `git pull` chi sviluppa deve rifare `python scripts/modules_installer.py` per avere le 0.1.40 installate)

Use the same prose style as the Phase 1 sections.

- [ ] **Step 2: Re-render DOCX**

```bash
cd docs/superpowers/dev-log
pandoc T5.4_PyArchInit_Dev_Log.md -o T5.4_PyArchInit_Dev_Log.docx
cd ../../..
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/dev-log/
git commit -m "docs(dev-log): Phase 2 / AI03 entry — GraphML delegation

Documents the cut-over: scope, closed limitations, test suite delta,
decisions taken. DOCX re-rendered for partner Teams uploads."
```

### Task G.4: Manual smoke gate

**Files:** none (manual QA in QGIS)

- [ ] **Step 1: Restart QGIS**

User action; close + relaunch.

- [ ] **Step 2: Open the Volterra/Castelseprio project**

Verify the plugin loads without exception (Log Messages panel).

- [ ] **Step 3: Click the green "Extended Matrix" button**

Verify the dialog no longer has the "Configure spatial/functional groupings" checkbox.

- [ ] **Step 4: Export with default checks (DOT, GraphML, JSON)**

Wait for the summary `QMessageBox` to appear. It must show four lines:
- DOT path
- JSON path
- GraphML path with metrics: `<n> nodes, <m> edges, <k> epochs, <r> redundancies removed`
- (no Phased line if unchecked)

- [ ] **Step 5: Open the produced .graphml in yEd**

Verify visually:
- horizontal row swimlanes per period (the "no period rows" limitation closed)
- edges have visually distinct styles for `cuts`/`fills`/`has_same_time` etc.
- edge count visibly lower than DOT count (transitive reduction at work)

- [ ] **Step 6: Edge case: site filter mismatch**

Trigger the export with a site that doesn't exist (manual code edit or config tweak as appropriate). Verify the summary dialog shows `EmptyGraphError` cleanly without crashing the dialog.

- [ ] **Step 7: Sign off**

If all of 1–6 pass: report `✅ smoke OK` and proceed to G.5. If any fails: do NOT tag — investigate, fix, retry.

### Task G.5: Tag + push

**Files:** none (git operations)

- [ ] **Step 1: Verify clean working tree**

```bash
git status --short | grep -vE '^\?\?'
```
Expected: empty.

- [ ] **Step 2: Create the release tag**

```bash
git tag -a phase2-ai03-graphml-delegation-5.2.0-alpha -m "Phase 2 / AI03: GraphML serialisation delegated to s3Dgraphy"
git tag -l | grep -E "phase2|pre-ai03"
```

- [ ] **Step 3: Push branch + tags**

```bash
git push origin Stratigraph_00001
git push origin phase2-ai03-graphml-delegation-5.2.0-alpha
git push origin pre-ai03-graphml-delegation
```

---

## Self-review checklist (run inline before delivering the plan)

Reviewed against the spec on 2026-05-07.

**Spec coverage:**

| Spec section | Plan coverage |
|---|---|
| §1 Goal — cut-over to s3dgraphy.GraphMLExporter | Group A (writer) + Group E (bridge wiring) |
| §2 Decisions D1–D9 | Cut-over (E.x deletions); fixture-based tests (Group C); standalone 5.2.0-alpha (G.1–G.5); DOT/JSON unchanged (E.x); checkbox removed (E.5); bake deferred (writer hardcodes False); get_sqlite_path (D.1); in-memory site filter (A.3); mapping ownership upstream (Group A imports `pyarchinit` mapping unmodified) |
| §3 Architecture | Group A builds the new path; Group E removes the legacy path |
| §4 Components | Each row of the components table mapped to a Task in Groups A–F |
| §5 Data flow | Implemented in `export_graphml` (C.1) + bridge wiring (E.1) |
| §6 Error handling | Exception classes (A.2), bridge categorisation (E.1), summary dialog (F.1) |
| §7 Testing strategy | L1 unit tests (A.1–A.3), L2 fixture pipeline (C.1–C.4), L3 manual smoke (G.4) |
| §8 Acceptance criteria | All four asserted by tests in C.1–C.4; manual smoke confirms in G.4 |
| §9 Out of scope | Plan explicitly excludes (PG support, AI04, AI05, custom groupings, Harris matrix exporter, requirements changes) |

**Placeholder scan:** searched for "TBD", "TODO", "fill in" — none present. The two `2026-MM-DD` placeholders in the changelog texts (G.1, G.2) are deliberate — the implementer fills them with the actual release date at tagging time.

**Type consistency:**
- `ExportResult` field names (`output_path`, `node_count`, `edge_count`, `epoch_count`, `tred_removed_edges`, `warnings`) used identically in A.1 (definition), C.1 (orchestrator returns), and F.1 (dialog reads).
- `GraphMLExportError(stage, original)` constructor signature consistent across A.2 (definition), C.1 (raises) and E.1 (catches).
- `_filter_by_site(graph, site_filter)` signature consistent across A.3 (definition) and C.1 (calls).
- `export_graphml(db_path, mapping, output_path, *, site_filter, persist_auxiliary)` signature pinned in spec §2 D-list and identical in C.1 + E.1.

**Known assumptions to verify at execution time:**

- The s3dgraphy `Graph.add_node` / `add_edge` API exposes nodes/edges as `graph.nodes` / `graph.edges` iterables. If the actual API uses `.get_nodes()` etc., adjust the helper accordingly. (Implementer: check `ext_libs/s3dgraphy/graph.py` once before A.3.)
- `StratigraphicNode` instances expose `.attributes['sito']`. If the importer puts `sito` directly as `n.sito`, adjust `_filter_by_site` to read both attribute paths. (Implementer: do `n = list(graph.nodes)[0]; print(dir(n))` once on a real importer output before relying on the access pattern.)
- `TemporalInferenceEngine` adds the warning string `"transitive reduction removed N edges"` (or similar) to `graph.warnings`. If the format differs, adjust the regex in C.1 step 3. The fallback (`tred_removed_edges = 0`) is graceful — L4 test would fail if zero is reported, surfacing the regex mismatch. (Implementer: read `ext_libs/s3dgraphy/exporter/graphml/graphml_exporter.py:111-122` once to confirm.)

If any of these assumptions are wrong at execution time, fix the helper inline and update the test, do not work around it.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-07-ai03-graphml-delegation.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task or task-group; review between tasks; fast iteration. Same approach used successfully in Phase 1.

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`; batch execution with checkpoints for review.

Which approach?
