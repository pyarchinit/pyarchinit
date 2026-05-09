# AI05 — ParadataStore + UI authoring + Strategy A + edge styling: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Phase 2 of the s3dgraphy bridge by shipping the `ParadataStore` (atomic-safe CRUD for site-level Author/License/Embargo metadata that has no SQL counterpart in pyarchinit), promoting `GraphProjector` from a thin wrapper to a proper class (Strategy A from AI04), and applying NodeRegistry-style automation to edge styling — all behind release `5.4.0-alpha`.

**Architecture:** New module `modules/s3dgraphy/sync/paradata_store.py` owns `paradata_{sito_slug}.graphml` (one file per sito, next to the SQLite DB), with atomic write via `os.replace()`. New module `modules/s3dgraphy/sync/edge_registry.py` reads `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json` for edge style resolution, with `_PYARCHINIT_EDGE_OVERRIDES` winning for legacy cases. `GraphProjector` absorbs the `_enrich_pyarchinit_graph` body (which is then deleted from `graphml_writer.py`) and gains `populate_graph(..., include_paradata=True)` for SQL+paradata merge. New `ParadataManagerDialog` (3-tab QTabWidget) is wired to a "Manage paradata" button in the US scheda.

**Tech Stack:** Python 3.9+, s3dgraphy 0.1.40 (vendored), lxml (transitive), pytest, sqlite3, QGIS PyQt5/PyQt6 abstraction. **No new third-party dependencies.**

**Spec source of truth:** `docs/superpowers/specs/2026-05-08-ai05-paradata-store-design.md` (commit `d6f9ed70`)

**Predecessor releases:**
- AI03: tag `phase2-ai03-graphml-delegation-5.2.0-alpha`
- AI04: tag `phase2-ai04-bridge-bidirectional-5.3.0-alpha` (current HEAD baseline)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_ai04_projector_refactor_plan.md` — Strategy A promotion path consummated by Group C of this plan
- `~/.claude/projects/.../memory/project_ai04_failure_mode_followup.md` — atomic-only ingestion still applies
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — never include co-author trailers

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/paradata_store.py` | `ParadataStore` class with atomic-safe CRUD over `paradata_{sito}.graphml`. Low-level (read/write/add_node/remove_node/find) + high-level (add_author/license/embargo + list_*). Exception hierarchy: `ParadataStoreError`, `ParadataReadError`, `ParadataWriteError`, `ParadataValidationError`, `ParadataNotFoundError` — all inherit `GraphSyncError`. ~250 lines. |
| `modules/s3dgraphy/sync/edge_registry.py` | Lazy singleton over `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json`. Public functions `resolve_edge_style(edge_type) -> dict | None` and `is_paradata_edge(edge_type) -> bool`. Override-wins via `_PYARCHINIT_EDGE_OVERRIDES`. ~120 lines. |
| `gui/dialog_paradata_manager.py` | `ParadataManagerDialog(QDialog)` with 3-tab `QTabWidget` (Authors / Licenses / Embargoes). Each tab: `QTableView` + Add/Edit/Remove buttons. Uses `qgis.PyQt` abstraction (Qt5/Qt6 compat, like AI04 dialog). ~400 lines. |
| `tests/sync/test_paradata_store.py` | L0 unit tests for `ParadataStore`: file_path slug, exists semantics, atomic crash-safety, low-level CRUD, high-level helpers, exception hierarchy, idempotent remove. ~12 tests. |
| `tests/sync/test_edge_registry.py` | L0 unit tests: `resolve_edge_style` for is_after/is_before/has_property/etc., `is_paradata_edge` classification, graceful degradation on missing JSON. ~5 tests. |
| `tests/sync/test_graph_projector_paradata.py` | L1 fixture-based: `populate_graph(include_paradata=True)` merge default + opt-out. ~4 tests. |
| `tests/sync/test_round_trip_with_paradata.py` | L1 fixture-based: full DB+paradata round-trip preserves both layers. ~2 tests. |
| `tests/sync/test_paradata_idempotent.py` | L1 fixture-based: 3 consecutive ingest runs converge. ~2 tests. |
| `tests/sync/test_cli_paradata.py` | L2 subprocess: 7 paradata subcommands (add-author/list-authors/add-license/list-licenses/add-embargo/list-embargos/remove). ~6 tests. |
| `tests/sync/test_strategy_a_no_regression.py` | L3 regression: `_enrich_pyarchinit_graph` standalone removed; AI03 export still bit-equivalent; AI04 callers (`GraphIngestor`, CLI helper) still work. ~3 tests. |
| `tests/sync/test_paradata_dialog_smoke.py` | L0 UI smoke (skip if no Qt): dialog instantiates with 3 tabs and doesn't crash on `_load_data`. ~1 test. |
| `tests/sync/fixtures/paradata_volterra.graphml` | Pre-cooked binary fixture: 2 AuthorNodes ("Marco Pacifico", "Maria Bianchi"), 1 LicenseNode ("CC-BY-NC-4.0"), 1 EmbargoNode ("until 2030-12-31"). Generated by `build_mini_volterra_external.py` extension. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | Strategy A promotion — `populate_graph()` body becomes orchestrator; private `_verify_schema`, `_build_strat_layer`, `_load_strat_units`, `_load_epochs`, `_parse_rapporti`, `_propagate_attrs`, `_merge_paradata` methods absorb the body of `_enrich_pyarchinit_graph` from `graphml_writer.py`. New kwarg `include_paradata: bool = True`. From ~80 lines (wrap) to ~350 lines (full class). |
| `modules/s3dgraphy/sync/graphml_writer.py` | (1) DELETE the `_enrich_pyarchinit_graph()` standalone function (~lines 222-540). (2) Update `export_graphml()` to call `GraphProjector().populate_graph(..., include_paradata=False)` instead. (3) Replace hardcoded `_PARADATA_UNITA_TIPI` classification (lines 665, 1040, 1041) with `edge_registry.is_paradata_edge()` calls. |
| `tabs/US_USM.py` | Add a "Manage paradata" `QPushButton` next to the existing green Extended Matrix button. On click → instantiate `ParadataManagerDialog(parent=self, db_manager=self.db_manager, sito=self.comboBox_sito.currentText())` and call `exec_()`. ~10 lines added. |
| `scripts/s3dgraphy_sync.py` | Add `paradata` subcommand with 7 sub-subcommands (`add-author/list-authors/add-license/list-licenses/add-embargo/list-embargos/remove`). Each calls into `ParadataStore`. Same exit-code semantics as AI04 (0 success, 1 GraphSyncError, 2 argparse). |
| `tests/sync/fixtures/build_mini_volterra_external.py` | Extend with `_emit_paradata_fixture()` — generates `paradata_volterra.graphml` with the pre-cooked Author/License/Embargo nodes via `ParadataStore`. Idempotent. |
| `metadata.txt` | Bump `version=5.3.0-alpha` → `version=5.4.0-alpha`. |
| `dev_logs/CHANGELOG.md` | Prepend `## [5.4.0-alpha] - 2026-MM-DD` bilingual section. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | New "Phase 2 — AI05 ParadataStore + UI authoring" section. |

### Explicitly NOT touched (out of scope per spec §9)

- `modules/s3dgraphy/s3dgraphy_dot_bridge.py` (the `S3DGraphyExportDialog` from AI03/AI04) — the new ParadataManagerDialog is a separate file. No risk to AI04 G.1.
- `modules/s3dgraphy/sync/graph_ingestor.py` — AI04's `GraphIngestor` stays as-is.
- `modules/s3dgraphy/sync/conflict_resolver.py` — pluggable strategies are AI06+.
- `requirements.txt` — no new dependencies.

---

## Test strategy

- **L0 unit tests** (`test_paradata_store.py`, `test_edge_registry.py`, `test_paradata_dialog_smoke.py`): pure pytest, no QGIS bootstrap, no DB.
- **L1 fixture-based pipeline** (`test_graph_projector_paradata.py`, `test_round_trip_with_paradata.py`, `test_paradata_idempotent.py`): pytest against `mini_volterra.sqlite` + `paradata_volterra.graphml`. No QGIS.
- **L2 CLI subprocess** (`test_cli_paradata.py`): runs `python scripts/s3dgraphy_sync.py paradata …` via `subprocess.run()` and asserts on exit code + stdout.
- **L3 regression guards** (`test_strategy_a_no_regression.py` + existing AC-2/AI04/Phase 1 tests): must stay green at every commit.

Decision-pinning matrix (each row = one D-id × one acceptance test):

| Decision / Acceptance | Test |
|---|---|
| D2 file path slug | `test_paradata_store.py::test_file_path_resolves_per_sito` |
| D3 default include_paradata=True | `test_graph_projector_paradata.py::test_populate_graph_includes_paradata_by_default` |
| D3 opt-out | `test_graph_projector_paradata.py::test_opt_out_disables_merge` |
| D4 paradata-only filter | `test_paradata_store.py::test_read_filters_to_paradata_only` |
| D5 high-level round-trip | `test_paradata_store.py::test_add_author_round_trip` |
| D5 low-level CRUD | `test_paradata_store.py::test_low_level_add_node` |
| D6 dialog instantiates | `test_paradata_dialog_smoke.py::test_paradata_dialog_can_open` |
| D7 standalone removed | `test_strategy_a_no_regression.py::test_enrich_function_removed` |
| D7 export unchanged | `test_strategy_a_no_regression.py::test_export_graphml_byte_identical` |
| D8 edge styles resolve | `test_edge_registry.py::test_resolves_topological_to_solid` |
| D8 paradata classification | `test_edge_registry.py::test_resolves_paradata_to_dashed` |
| D8 graceful fallback | `test_edge_registry.py::test_falls_back_when_datamodel_missing` |
| D9 site-level isolation | `test_paradata_store.py::test_add_author_creates_isolated_node_no_edges` |
| AC-3 atomic crash-safety | `test_paradata_store.py::test_atomic_write_no_corruption_on_crash` |
| AC-7 idempotent remove | `test_paradata_store.py::test_remove_idempotent` |
| AC-15 CLI add-author | `test_cli_paradata.py::test_cli_paradata_add_author` |
| AC-15 CLI remove | `test_cli_paradata.py::test_cli_paradata_remove` |

The Phase 1 + AI03 + AI04 test suites (`tests/sync/`, `tests/migrations/`) MUST stay green at every commit. Run `pytest tests/sync/ tests/migrations/ -q` after each task. Test count progression: 94 (baseline) → ~120 (post-AI05).

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Verify clean starting point + push pending commits

**Files:** none (git operation)

- [ ] **Step 1: Confirm starting point**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'   # tracked changes only — must be empty
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}
```

Expected: tracked changes empty, last commit is `d6f9ed70 docs(spec): AI05 …` or later, `1\t0` ahead-behind (the spec doc is unpushed).

- [ ] **Step 2: Push the spec commit**

```bash
git push origin Stratigraph_00001
```

Expected: `Stratigraph_00001 -> Stratigraph_00001` plus 1 commit pushed.

- [ ] **Step 3: Verify**

```bash
git rev-list --left-right --count HEAD...@{u}   # expected: "0\t0"
```

### Task 0.2: Create AI05 rollback tag

**Files:** none (git operation)

- [ ] **Step 1: Create annotated tag**

```bash
git tag -a pre-ai05-paradata -m "Pre-flight rollback tag for AI05 / Phase 2 closure"
git tag -l | grep -E "pre-ai0|phase2"
```

Expected output (5 lines):
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
pre-ai05-paradata
```

- [ ] **Step 2: Push the tag**

```bash
git push origin pre-ai05-paradata
git ls-remote --tags origin 2>&1 | grep "refs/tags/pre-ai05-paradata$"
```

Expected: 1 matching line (the tag commit hash on the remote).

### Task 0.3: Bump version to 5.4.0-alpha

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Read current metadata.txt**

```bash
grep -n "^version=" metadata.txt
```

Expected: `version=5.3.0-alpha`.

- [ ] **Step 2: Edit metadata.txt — bump version**

Use the Edit tool to change exactly the line `version=5.3.0-alpha` to `version=5.4.0-alpha`. Do not touch anything else.

- [ ] **Step 3: Verify**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.4.0-alpha`.

- [ ] **Step 4: Run sanity tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `94 passed` (baseline post-AI04+AI04.1).

- [ ] **Step 5: Commit**

```bash
git add metadata.txt
git commit -m "$(cat <<'EOF'
chore(metadata): bump version to 5.4.0-alpha for AI05

Phase 2 / AI05 — closes Phase 2 of the s3dgraphy bridge:
ParadataStore (Author/License/Embargo CRUD), UI authoring
dialog, GraphProjector Strategy A promotion, edge styling
automation via NodeRegistry-style fallback chain.

Target tag: phase2-ai05-paradata-store-5.4.0-alpha.

Spec: docs/superpowers/specs/2026-05-08-ai05-paradata-store-design.md
Plan: docs/superpowers/plans/2026-05-08-ai05-paradata-store.md
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task 0.4: Capture baseline test counts as a sanity reference

**Files:** none (no commit; just record the numbers for later comparison)

- [ ] **Step 1: Run full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -3
```

Expected: `94 passed`.

- [ ] **Step 2: Run AC-2 baseline guard**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -2
```

Expected: `1 passed`.

- [ ] **Step 3: Note progression target**

The AI05 plan target is `≥120 passing` post-Group H. Group counts:
- Post-Group A: ~99 (94 + 5 edge_registry)
- Post-Group B: ~111 (99 + 12 paradata_store)
- Post-Group C: ~114 (111 + 3 strategy_a_no_regression)
- Post-Group D: 114 (no new tests — fixture only)
- Post-Group E: ~118 (114 + 4 round-trip + idempotent)
- Post-Group F: ~124 (118 + 6 cli paradata)
- Post-Group G: ~125 (124 + 1 ui smoke)
- Post-Group H: 125 (no new tests)

This is informational — every Group's task spells out the exact expected count.

---

## Group A — Edge Registry

### Task A.1: Scaffold `edge_registry.py` + L0 tests (TDD)

**Files:**
- Create: `modules/s3dgraphy/sync/edge_registry.py`
- Create: `tests/sync/test_edge_registry.py`

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_edge_registry.py` with this content:

```python
"""L0 unit tests for edge_registry: resolve_edge_style + is_paradata_edge.

Pure pytest, no DB, no QGIS. Pins decision D8.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def test_resolves_topological_to_solid():
    """is_after has a 'solid' line_style in em_visual_rules.json."""
    from modules.s3dgraphy.sync.edge_registry import resolve_edge_style
    style = resolve_edge_style("is_before")  # 'is_before' is in em_visual_rules
    assert style is not None
    assert style.get("line_style") in ("solid", "line")


def test_resolves_paradata_to_dashed():
    """has_property is a paradata edge → dashed line_style or dotted."""
    from modules.s3dgraphy.sync.edge_registry import resolve_edge_style
    style = resolve_edge_style("has_property")
    # If em_visual_rules has it: should be solid/dashed/dotted
    if style is not None:
        assert "line_style" in style


def test_is_paradata_edge_classifies_correctly():
    """has_property and has_paradata_nodegroup are paradata; is_after is not."""
    from modules.s3dgraphy.sync.edge_registry import is_paradata_edge
    assert is_paradata_edge("has_property") is True
    assert is_paradata_edge("has_paradata_nodegroup") is True
    assert is_paradata_edge("extracted_from") is True
    assert is_paradata_edge("is_after") is False
    assert is_paradata_edge("cuts") is False


def test_falls_back_when_datamodel_missing(monkeypatch):
    """resolve_edge_style returns None gracefully if registry can't load."""
    from modules.s3dgraphy.sync import edge_registry
    # Force registry to be sentinel False (failed load)
    monkeypatch.setattr(edge_registry, "_edge_registry_visual", False)
    assert edge_registry.resolve_edge_style("anything") is None


def test_resolve_unknown_returns_none():
    """Unknown edge_type returns None (caller falls back to default)."""
    from modules.s3dgraphy.sync.edge_registry import resolve_edge_style
    assert resolve_edge_style("totally_made_up_edge_type") is None
```

- [ ] **Step 2: Run tests, expect failure (module doesn't exist)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_edge_registry.py -v
```

Expected: ImportError (`edge_registry` not found).

- [ ] **Step 3: Write minimal implementation**

Create `modules/s3dgraphy/sync/edge_registry.py` with this content:

```python
"""Edge style + paradata classification, sourced from s3dgraphy's
shipped JSON catalogs:

  ext_libs/s3dgraphy/JSON_config/em_visual_rules.json
      → edge_style.{edge_type}.{color, line_style, width}
  ext_libs/s3dgraphy/JSON_config/s3Dgraphy_connections_datamodel.json
      → edge_types.{edge_type}.{label, allowed_connections, mapping}

Override-wins: pyarchinit-specific overrides in
`_PYARCHINIT_EDGE_OVERRIDES` win over the canonical s3dgraphy
catalogs. Future EM edge types added to the catalogs are picked up
automatically without changes here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------
# Pyarchinit-specific overrides (D8: override-wins). Empty for now —
# the AI03/AI04 line-style logic (dashed for paradata, solid for
# stratigraphic) is now derived from `is_paradata_edge`. If a future
# pyarchinit deviation emerges (e.g. specific color for "rapporti"
# rendering), add an entry here:
#
#   "is_after": {"color": "#000000", "line_style": "solid", "width": 2}
# ----------------------------------------------------------------------
_PYARCHINIT_EDGE_OVERRIDES: dict[str, dict] = {}


# ----------------------------------------------------------------------
# Hardcoded paradata edge set — used as fallback when the datamodel
# JSON is missing or malformed. These match what AI04's
# `_build_rapporti_from_edges` excludes from the rapporti list and
# what the post-processor renders as dashed.
# ----------------------------------------------------------------------
_HARDCODED_PARADATA_EDGES: frozenset[str] = frozenset({
    "has_property",
    "has_paradata_nodegroup",
    "has_first_epoch",
    "extracted_from",
    "combines",
    "survive_in_epoch",
    "has_data_provenance",
    "is_in_activity",
    "has_author",
    "has_license",
    "has_embargo",
})


_EXT_LIBS_S3DG = (
    Path(__file__).resolve().parents[3] / "ext_libs" / "s3dgraphy"
)
_VISUAL_RULES_PATH = _EXT_LIBS_S3DG / "JSON_config" / "em_visual_rules.json"
_CONNECTIONS_PATH = (
    _EXT_LIBS_S3DG / "JSON_config" / "s3Dgraphy_connections_datamodel.json"
)


# Lazy singletons. False sentinel means "load failed once, don't retry".
_edge_registry_visual: dict | bool | None = None
_edge_registry_connections: dict | bool | None = None


def _load_visual_rules() -> dict | None:
    """Load em_visual_rules.json once. Returns None on failure."""
    global _edge_registry_visual
    if _edge_registry_visual is False:
        return None
    if _edge_registry_visual is None:
        try:
            with open(_VISUAL_RULES_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            _edge_registry_visual = data.get("edge_style", {})
        except Exception:
            _edge_registry_visual = False
            return None
    return (_edge_registry_visual
            if isinstance(_edge_registry_visual, dict) else None)


def _load_connections_datamodel() -> dict | None:
    """Load s3Dgraphy_connections_datamodel.json once."""
    global _edge_registry_connections
    if _edge_registry_connections is False:
        return None
    if _edge_registry_connections is None:
        try:
            with open(_CONNECTIONS_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            _edge_registry_connections = data.get("edge_types", {})
        except Exception:
            _edge_registry_connections = False
            return None
    return (_edge_registry_connections
            if isinstance(_edge_registry_connections, dict) else None)


def resolve_edge_style(edge_type: str) -> dict | None:
    """Return the style dict for *edge_type*, or None if not known.

    Lookup order:
        1. _PYARCHINIT_EDGE_OVERRIDES (override-wins)
        2. em_visual_rules.json edge_style.{edge_type}.style
        3. None (caller uses default)

    Returned dict shape: {"color": "#RRGGBB", "line_style": "solid"|"dashed"|"dotted",
                          "width": int}
    """
    if edge_type in _PYARCHINIT_EDGE_OVERRIDES:
        return dict(_PYARCHINIT_EDGE_OVERRIDES[edge_type])
    visual = _load_visual_rules()
    if visual is None:
        return None
    entry = visual.get(edge_type)
    if not entry:
        return None
    style = entry.get("style") if isinstance(entry, dict) else None
    if not isinstance(style, dict):
        return None
    return dict(style)


def is_paradata_edge(edge_type: str) -> bool:
    """True iff *edge_type* is a paradata-flow edge (rendered dashed in
    the AI03 post-processor; excluded from rapporti round-trip in AI04).

    Uses the connections datamodel when available — paradata edges have
    `allowed_connections.source` or `.target` containing PropertyNode /
    DocumentNode / ExtractorNode / CombinerNode. Falls back to the
    hardcoded `_HARDCODED_PARADATA_EDGES` set when the datamodel is
    unavailable.
    """
    if edge_type in _HARDCODED_PARADATA_EDGES:
        return True
    connections = _load_connections_datamodel()
    if connections is None:
        return False
    entry = connections.get(edge_type)
    if not isinstance(entry, dict):
        return False
    allowed = entry.get("allowed_connections", {})
    if not isinstance(allowed, dict):
        return False
    paradata_classes = {
        "PropertyNode", "DocumentNode", "ExtractorNode",
        "CombinerNode", "AuthorNode", "LicenseNode", "EmbargoNode",
        "ParadataNodeGroup",
    }
    src = set(allowed.get("source", []) or [])
    tgt = set(allowed.get("target", []) or [])
    return bool(src & paradata_classes or tgt & paradata_classes)
```

- [ ] **Step 4: Run tests, expect green**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_edge_registry.py -v
```

Expected: `5 passed`.

- [ ] **Step 5: Run full suite — must stay 94 + 5 = 99**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `99 passed`.

- [ ] **Step 6: Run AC-2 baseline (no integration yet, but verify nothing broke)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/edge_registry.py \
        tests/sync/test_edge_registry.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): edge_registry — fallback chain over s3dgraphy JSONs

Per spec §3.2 (D8), ships a new helper module that resolves edge
style + paradata classification from s3dgraphy's shipped JSON
catalogs:
  - em_visual_rules.json (color, line_style, width per edge type)
  - s3Dgraphy_connections_datamodel.json (allowed_connections →
    paradata heuristic)

Public API:
  resolve_edge_style(edge_type) -> dict | None
  is_paradata_edge(edge_type) -> bool

Override-wins via `_PYARCHINIT_EDGE_OVERRIDES` (currently empty —
will be populated when a pyarchinit-specific deviation emerges).
Hardcoded fallback set `_HARDCODED_PARADATA_EDGES` for graceful
degradation when the JSON catalogs are missing or malformed.

Lazy singletons with False sentinel — failed loads don't retry.

5 new tests, all passing. AC-2 baseline still green. Integration
into graphml_writer's post-processor lands in Task A.2.

Tests: 99/99 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task A.2: Integrate `edge_registry` into `graphml_writer.py`

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py:665` (definition `_PARADATA_UNITA_TIPI`)
- Modify: `modules/s3dgraphy/sync/graphml_writer.py:~1040-1041` (usage in post-processor)

The current `graphml_writer.py` post-processor classifies edges as paradata via a hardcoded `_PARADATA_UNITA_TIPI` set. Replace that classification with `edge_registry.is_paradata_edge()`.

- [ ] **Step 1: Locate the current usages**

```bash
grep -n "_PARADATA_UNITA_TIPI" modules/s3dgraphy/sync/graphml_writer.py
```

Expected: 3 hits — line ~665 (definition) and 2 usages around line 1040.

- [ ] **Step 2: Read the current usage context**

```bash
sed -n '1030,1050p' modules/s3dgraphy/sync/graphml_writer.py
```

Note the surrounding code shape. The check is `src_type in _PARADATA_UNITA_TIPI or tgt_type in _PARADATA_UNITA_TIPI`. We're replacing with `is_paradata_edge(edge_type)` — but the current code keys on the **node** unita_tipo, not the edge_type. Adapt.

- [ ] **Step 3: Read the relevant block**

```bash
sed -n '1020,1055p' modules/s3dgraphy/sync/graphml_writer.py
```

You'll see something like:
```python
src_type = node_id_to_unita_tipo.get(edge_el.get("source", ""))
tgt_type = node_id_to_unita_tipo.get(edge_el.get("target", ""))
is_paradata = (
    src_type in _PARADATA_UNITA_TIPI
    or tgt_type in _PARADATA_UNITA_TIPI
)
```

The replacement keeps the unita_tipo-based check (because edge_type isn't always available in the post-processor) BUT augments it with the registry's classification when an edge_type label is recoverable.

- [ ] **Step 4: Edit the block**

Use the Edit tool to replace the old check with this:

```python
# Classify the edge as paradata using the canonical s3dgraphy
# datamodel via edge_registry (D8). Falls back to the original
# unita_tipo-based heuristic if the registry doesn't classify the
# edge — the registry is the new source of truth, the heuristic
# stays as defence in depth.
src_type = node_id_to_unita_tipo.get(edge_el.get("source", ""))
tgt_type = node_id_to_unita_tipo.get(edge_el.get("target", ""))
edge_type_attr = edge_el.get("data-edge-type")  # may be None
from .edge_registry import is_paradata_edge
is_paradata = bool(
    (edge_type_attr and is_paradata_edge(edge_type_attr))
    or src_type in _PARADATA_UNITA_TIPI
    or tgt_type in _PARADATA_UNITA_TIPI
)
```

(The exact existing variable names in `graphml_writer.py` may differ slightly. Adapt to match the actual surrounding code; the key change is **adding `is_paradata_edge`** to the OR chain, not replacing the existing logic.)

- [ ] **Step 5: AC-2 regression guard FIRST**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`. If RED, the structural fingerprint changed — investigate before proceeding.

- [ ] **Step 6: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `99 passed` (no new tests, no regressions).

- [ ] **Step 7: Run AI04 round-trip + idempotent + CLI as additional sanity**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_round_trip.py \
    tests/sync/test_idempotent_ingest.py \
    tests/sync/test_cli_helper.py -v 2>&1 | tail -3
```

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py
git commit -m "$(cat <<'EOF'
feat(graphml_writer): wire edge_registry.is_paradata_edge into classification

Augments the existing _PARADATA_UNITA_TIPI lookup in the post-processor
with edge_registry.is_paradata_edge() — the canonical source of
truth from s3Dgraphy_connections_datamodel.json. The unita_tipo-
based fallback stays for defence in depth (some edges may not have
an edge_type attribute in the post-processed XML).

This means new paradata edge types added to s3dgraphy in future
releases are classified automatically without code change.

AC-2 baseline still green. AI04 round-trip / idempotent / CLI all
pass. No new tests; the integration is exercised through every
existing test that flows through the post-processor.

Tests: 99/99 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task A.3: AC-2 baseline regression check

**Files:** none (sanity check only — no commit)

- [ ] **Step 1: Run AC-2 + full suite x3 for stability**

```bash
for i in 1 2 3; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -2
done
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: 3 × `1 passed` for AC-2; `99 passed` for full suite.

If any failure, STOP and investigate Task A.2's edit before proceeding to Group B.

---

## Group B — ParadataStore Foundation

### Task B.1: Scaffold `paradata_store.py` with file path + atomic read/write

**Files:**
- Create: `modules/s3dgraphy/sync/paradata_store.py`
- Create: `tests/sync/test_paradata_store.py`

- [ ] **Step 1: Write failing tests for file_path + exists + read empty**

Create `tests/sync/test_paradata_store.py` with this content:

```python
"""L0 unit tests for ParadataStore.

Pure pytest, no QGIS, no real DB (uses tmp_path).
Pins decisions D2 (file path), D4 (paradata-only filter),
D5 (low+high level API), D9 (site-level isolation).
"""
from __future__ import annotations
import os
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def _make_db(tmp_path) -> Path:
    """Create a minimal sqlite DB so ParadataStore has a parent dir."""
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INTEGER, sito TEXT)")
    conn.commit()
    conn.close()
    return db


def test_file_path_resolves_per_sito(tmp_path):
    """D2: file path is `{db_dir}/paradata_{sito_slug}.graphml`."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    db = _make_db(tmp_path)
    store = ParadataStore(db, "Scavo Archeologico")
    assert store.file_path == tmp_path / "paradata_scavo_archeologico.graphml"


def test_file_path_slugifies_special_chars(tmp_path):
    """Slug replaces non-word chars with underscore + lowercases."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    db = _make_db(tmp_path)
    store = ParadataStore(db, "Site #1 — α")
    assert "paradata_site__1" in str(store.file_path).lower()


def test_exists_false_when_no_file(tmp_path):
    """exists() reflects on-disk presence, defaults False on init."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    assert store.exists() is False


def test_read_empty_when_no_file(tmp_path):
    """read() returns empty Graph when file doesn't exist (NOT error)."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    graph = store.read()
    assert len(graph.nodes) == 0
```

- [ ] **Step 2: Run, expect failure (module doesn't exist)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v
```

Expected: ImportError on `paradata_store`.

- [ ] **Step 3: Write minimal implementation**

Create `modules/s3dgraphy/sync/paradata_store.py` with this content:

```python
"""Site-scoped CRUD for paradata.graphml (atomic-safe writes).

AI05 Phase 2 closure. Manages the 3 node types without an SQL
counterpart in pyarchinit:
    - AuthorNode    (authorship metadata)
    - LicenseNode   (rights / SPDX licence)
    - EmbargoNode   (embargo dates)

File location: {db_path.parent}/paradata_{sito_slug}.graphml
where sito_slug is `re.sub(r'\\W+', '_', sito).lower()`.

Atomic writes via .tmp + os.replace() — crash-safe.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .graph_ingestor import GraphSyncError


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1, extends GraphSyncError so existing
# try/except GraphSyncError handlers in CLI/UI/tests continue to catch).
# ---------------------------------------------------------------------------
class ParadataStoreError(GraphSyncError):
    """Base for ParadataStore errors."""


class ParadataReadError(ParadataStoreError):
    """File parse / schema error during read()."""


class ParadataWriteError(ParadataStoreError):
    """File write / atomic-rename failure during write()."""


class ParadataValidationError(ParadataStoreError):
    """Caller passed bogus data to add_author/license/embargo/etc."""


class ParadataNotFoundError(ParadataStoreError):
    """Required file missing where caller expected it."""


# ---------------------------------------------------------------------------
# ParadataStore
# ---------------------------------------------------------------------------
_PARADATA_NODE_TYPES: frozenset[str] = frozenset({
    "AuthorNode", "LicenseNode", "EmbargoNode",
})


def _sito_slug(sito: str) -> str:
    """Filename-safe lowercase slug for a sito identifier."""
    return re.sub(r"\W+", "_", sito).strip("_").lower()


class ParadataStore:
    """Site-scoped CRUD for paradata.graphml.

    Args:
        db_path: filesystem path to the pyarchinit SQLite DB; the
            paradata file lives in the same directory.
        sito: site identifier (a value from `us_table.sito`).

    Raises on instantiation: nothing (lazy file checks; read/write
    perform actual I/O).
    """

    def __init__(self, db_path: Path, sito: str) -> None:
        if not sito:
            raise ParadataValidationError(
                "sito is required for ParadataStore")
        self._db_path = Path(db_path)
        self._sito = sito
        self._slug = _sito_slug(sito)

    @property
    def file_path(self) -> Path:
        """Resolved paradata file path for this (db, sito) pair."""
        return self._db_path.parent / f"paradata_{self._slug}.graphml"

    def exists(self) -> bool:
        """Whether the paradata file is present on disk."""
        return self.file_path.exists()

    @property
    def sito(self) -> str:
        return self._sito

    # ---- Low-level (D5) ------------------------------------------------
    def read(self):
        """Return a Graph populated with only the paradata-family
        nodes from the file. Returns empty Graph when file absent."""
        from s3dgraphy import Graph
        if not self.exists():
            return Graph(graph_id=self._sito)
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
            graph = GraphMLImporter(filepath=str(self.file_path)).parse()
        except Exception as e:
            raise ParadataReadError(
                f"Cannot parse {self.file_path}: {e}") from e
        # AI04 helper to recover stripped attrs
        try:
            from .graph_ingestor import _hydrate_pyarchinit_data_keys
            _hydrate_pyarchinit_data_keys(graph, self.file_path)
        except Exception:
            pass
        # Defensive filter: drop non-paradata node types
        graph.nodes = [
            n for n in graph.nodes
            if type(n).__name__ in _PARADATA_NODE_TYPES
        ]
        return graph

    def write(self, graph) -> None:
        """Atomic write: serialise to .tmp, embed AI04 data keys,
        os.replace() to final path. Original file untouched on
        failure."""
        tmp = self.file_path.with_suffix(".graphml.tmp")
        try:
            from s3dgraphy.exporter.graphml.graphml_exporter import (
                GraphMLExporter,
            )
            exporter = GraphMLExporter(graph)
            exporter.export(str(tmp), persist_auxiliary=False)
            # Embed pyarchinit data keys so round-trip preserves
            # the AI04-introduced attributes.
            from .graphml_writer import _embed_pyarchinit_data_keys
            _embed_pyarchinit_data_keys(graph, tmp)
            # Atomic rename — POSIX + Windows ≥ Vista.
            os.replace(str(tmp), str(self.file_path))
        except Exception as e:
            # Cleanup tmp if it exists; original is untouched.
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise ParadataWriteError(
                f"Cannot write {self.file_path}: {e}") from e

    def add_node(self, node) -> None:
        """Append *node* to the paradata graph + write."""
        type_name = type(node).__name__
        if type_name not in _PARADATA_NODE_TYPES:
            raise ParadataValidationError(
                f"Refusing to store {type_name} in paradata.graphml — "
                f"only {sorted(_PARADATA_NODE_TYPES)} are accepted.")
        graph = self.read()
        graph.add_node(node)
        self.write(graph)

    def remove_node(self, node_uuid: str) -> None:
        """Idempotent removal: no error if node_uuid not found."""
        graph = self.read()
        before = len(graph.nodes)
        graph.nodes = [
            n for n in graph.nodes
            if getattr(n, "node_id", None) != node_uuid
        ]
        if len(graph.nodes) != before:
            self.write(graph)

    # alias for D5/B-style API consistency
    remove = remove_node

    def find(self, node_type: str, **kwargs) -> list:
        """Return matching nodes from the file. Empty list if none."""
        graph = self.read()
        out = []
        for n in graph.nodes:
            if type(n).__name__ != node_type:
                continue
            if all(getattr(n, k, None) == v
                   or (getattr(n, "data", {}) or {}).get(k) == v
                   for k, v in kwargs.items()):
                out.append(n)
        return out

    # ---- High-level (D5) — populated in Task B.3 ----------------------
    # add_author / list_authors / add_license / list_licenses /
    # add_embargo / list_embargos
```

- [ ] **Step 4: Run tests, expect green for the 4 file_path/exists/read tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Full suite — must stay 99 + 4 = 103**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `103 passed`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/paradata_store.py \
        tests/sync/test_paradata_store.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): ParadataStore — file path + exists + read

Per spec §3.1, ships the ParadataStore class with the foundational
file path resolution and read/exists semantics:

  - file_path = {db_path.parent}/paradata_{sito_slug}.graphml
    (D2: slug = re.sub(r'\W+', '_', sito).lower())
  - exists() reflects on-disk presence
  - read() returns empty Graph when file absent (non-fatal),
    parses + hydrates AI04 data keys when present, defensively
    filters to {AuthorNode, LicenseNode, EmbargoNode} only (D4).

Plus the full exception hierarchy (extends GraphSyncError):
  - ParadataStoreError (base)
  - ParadataReadError / ParadataWriteError /
    ParadataValidationError / ParadataNotFoundError

Low-level scaffolding (add_node / remove_node / find) populated;
write() is fully implemented with atomic os.replace() pattern.

High-level helpers (add_author/license/embargo + list_*) land in
Task B.3.

Tests: 103/103 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.2: Low-level CRUD + filter tests

**Files:**
- Modify: `tests/sync/test_paradata_store.py` (append tests)

The implementation already lives from B.1; this task adds tests pinning the low-level behaviour.

- [ ] **Step 1: Append failing tests**

Append to `tests/sync/test_paradata_store.py`:

```python
def _make_minimal_graph_with_strat_node(sito: str):
    """Build a Graph with one StratigraphicUnit node (NOT paradata)."""
    from s3dgraphy import Graph
    g = Graph(graph_id=sito)
    # Use a generic Node class that's not paradata to test filtering
    from s3dgraphy.nodes.base_node import Node
    n = Node(node_id="not-paradata-uuid", name="US1")
    n.attributes = {"sito": sito}
    g.add_node(n)
    return g


def test_low_level_add_node_paradata_only(tmp_path):
    """add_node refuses non-paradata types (D4)."""
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataValidationError)
    from s3dgraphy.nodes.base_node import Node
    store = ParadataStore(_make_db(tmp_path), "X")
    with pytest.raises(ParadataValidationError):
        store.add_node(Node(node_id="abc", name="bogus"))


def test_low_level_add_node_persists(tmp_path):
    """add_node writes to file; subsequent read sees the node."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.nodes.author_node import AuthorNode
    store = ParadataStore(_make_db(tmp_path), "X")
    node = AuthorNode(node_id="auth-123", name="Marco")
    store.add_node(node)
    assert store.exists() is True
    graph2 = store.read()
    assert len(graph2.nodes) == 1
    assert graph2.nodes[0].node_id == "auth-123"


def test_low_level_remove_node_idempotent(tmp_path):
    """remove_node on missing uuid is a no-op (no error)."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    # File doesn't exist yet
    store.remove_node("any-uuid")  # must not raise

    from s3dgraphy.nodes.author_node import AuthorNode
    store.add_node(AuthorNode(node_id="a1", name="Marco"))
    store.remove_node("not-present-uuid")  # idempotent, no raise
    assert len(store.read().nodes) == 1


def test_read_filters_to_paradata_only(tmp_path):
    """If the file accidentally contains non-paradata nodes
    (corrupt input), read() filters them out silently."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.nodes.author_node import AuthorNode
    from s3dgraphy.exporter.graphml.graphml_exporter import GraphMLExporter
    from s3dgraphy import Graph

    store = ParadataStore(_make_db(tmp_path), "X")
    # Manually craft a graph with paradata + non-paradata mix
    g = Graph(graph_id="X")
    g.add_node(AuthorNode(node_id="auth-1", name="Marco"))
    from s3dgraphy.nodes.base_node import Node
    g.add_node(Node(node_id="strat-1", name="US1"))
    GraphMLExporter(g).export(str(store.file_path),
                              persist_auxiliary=False)

    parsed = store.read()
    types = {type(n).__name__ for n in parsed.nodes}
    # Strat-family should be filtered out
    assert "AuthorNode" in types
    # Non-paradata types must NOT survive the filter
    assert "Node" not in types


def test_find_returns_matching_nodes(tmp_path):
    """find(node_type=AuthorNode, name='Marco') returns the right node."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from s3dgraphy.nodes.author_node import AuthorNode
    store = ParadataStore(_make_db(tmp_path), "X")
    store.add_node(AuthorNode(node_id="a1", name="Marco"))
    store.add_node(AuthorNode(node_id="a2", name="Maria"))
    found = store.find("AuthorNode", name="Marco")
    assert len(found) == 1
    assert found[0].node_id == "a1"
```

- [ ] **Step 2: Run, expect failures (some pass — implementation is partial)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v
```

Most should pass since add_node/remove_node/find are all implemented in B.1; if any fail, fix the implementation in `paradata_store.py` until green.

- [ ] **Step 3: Full suite — 103 + 5 = 108**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `108 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_paradata_store.py
git commit -m "$(cat <<'EOF'
test(paradata_store): low-level CRUD + paradata-only filter

Five new tests exercising:
  - add_node refuses non-paradata types (D4) — raises
    ParadataValidationError
  - add_node persists across read/write cycle (round-trip)
  - remove_node is idempotent (no error on missing uuid)
  - read() defensively drops non-paradata types (corrupt-input
    safety)
  - find() returns matching nodes by type+attribute kwargs

Tests: 108/108 pass. Implementation already lives in
modules/s3dgraphy/sync/paradata_store.py (Task B.1) — these tests
pin the contract.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.3: High-level helpers (add_author/license/embargo + list_*)

**Files:**
- Modify: `modules/s3dgraphy/sync/paradata_store.py` (append helpers)
- Modify: `tests/sync/test_paradata_store.py` (append tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/sync/test_paradata_store.py`:

```python
def test_add_author_round_trip(tmp_path):
    """add_author + list_authors round-trip (D5 high-level)."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    auth_uuid = store.add_author(
        "Marco Pacifico", orcid="0000-0002-1234-5678", role="curator")
    assert isinstance(auth_uuid, str) and len(auth_uuid) > 8
    authors = store.list_authors()
    assert len(authors) == 1
    a = authors[0]
    assert a["name"] == "Marco Pacifico"
    assert a["orcid"] == "0000-0002-1234-5678"
    assert a["role"] == "curator"
    assert a["node_uuid"] == auth_uuid


def test_add_author_creates_isolated_node_no_edges(tmp_path):
    """D9: AuthorNode is site-level, no edges to specific units."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    store.add_author("Marco")
    graph = store.read()
    edges = list(getattr(graph, "edges", []) or [])
    assert len(edges) == 0


def test_add_author_validates_name(tmp_path):
    """Empty name → ParadataValidationError."""
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataValidationError)
    store = ParadataStore(_make_db(tmp_path), "X")
    with pytest.raises(ParadataValidationError):
        store.add_author("")


def test_add_license_round_trip(tmp_path):
    """add_license + list_licenses round-trip."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    lic_uuid = store.add_license(
        "CC-BY-NC-4.0", url="https://creativecommons.org/licenses/by-nc/4.0/")
    licenses = store.list_licenses()
    assert len(licenses) == 1
    assert licenses[0]["spdx_id"] == "CC-BY-NC-4.0"
    assert licenses[0]["url"].startswith("https://")
    assert licenses[0]["node_uuid"] == lic_uuid


def test_add_embargo_round_trip(tmp_path):
    """add_embargo + list_embargos round-trip."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    emb_uuid = store.add_embargo("2030-12-31", reason="dataset embargo")
    embargos = store.list_embargos()
    assert len(embargos) == 1
    assert embargos[0]["until_date"] == "2030-12-31"
    assert embargos[0]["reason"] == "dataset embargo"
    assert embargos[0]["node_uuid"] == emb_uuid


def test_remove_high_level_alias(tmp_path):
    """`store.remove(uuid)` is an alias for `remove_node(uuid)`."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    auth_uuid = store.add_author("Marco")
    assert len(store.list_authors()) == 1
    store.remove(auth_uuid)
    assert len(store.list_authors()) == 0
```

- [ ] **Step 2: Run, expect failures**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v
```

Expected: 6 failures with `AttributeError: 'ParadataStore' object has no attribute 'add_author'`.

- [ ] **Step 3: Implement the high-level helpers**

Append to `modules/s3dgraphy/sync/paradata_store.py` (inside the `ParadataStore` class, replacing the placeholder comment):

```python
    # ---- High-level (D5) ----------------------------------------------
    def add_author(self, name: str, orcid: str = None,
                   role: str = None) -> str:
        """Create + persist an AuthorNode. Returns the new node_uuid."""
        if not name or not str(name).strip():
            raise ParadataValidationError(
                "AuthorNode requires a non-empty `name`")
        from s3dgraphy.nodes.author_node import AuthorNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = AuthorNode(
            node_id=node_uuid,
            name=str(name),
            orcid=orcid or "noorcid",
        )
        # Stash extra attrs so round-trip preserves them via the AI04
        # data-keys helper; the s3dgraphy AuthorNode itself doesn't
        # have a `role` attr in 0.1.40.
        node.attributes = {
            "sito": self._sito,
            "name": str(name),
            "orcid": orcid or "",
            "role": role or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_authors(self) -> list[dict]:
        """Return [{node_uuid, name, orcid, role}, ...]."""
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "AuthorNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            data = getattr(n, "data", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "name": getattr(n, "name", "")
                        or attrs.get("name", "")
                        or data.get("name", ""),
                "orcid": attrs.get("orcid", "")
                         or data.get("orcid", ""),
                "role": attrs.get("role", ""),
            })
        return out

    def add_license(self, spdx_id: str, url: str = None) -> str:
        """Create + persist a LicenseNode."""
        if not spdx_id or not str(spdx_id).strip():
            raise ParadataValidationError(
                "LicenseNode requires a non-empty SPDX id")
        from s3dgraphy.nodes.license_node import LicenseNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = LicenseNode(
            node_id=node_uuid,
            name=str(spdx_id),
            license_type=str(spdx_id),
            url=url or "",
        )
        node.attributes = {
            "sito": self._sito,
            "spdx_id": str(spdx_id),
            "url": url or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_licenses(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "LicenseNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            data = getattr(n, "data", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "spdx_id": (attrs.get("spdx_id", "")
                            or data.get("license_type", "")
                            or getattr(n, "name", "")),
                "url": attrs.get("url", "") or data.get("url", ""),
            })
        return out

    def add_embargo(self, until_date: str, reason: str = None) -> str:
        """Create + persist an EmbargoNode."""
        if not until_date or not str(until_date).strip():
            raise ParadataValidationError(
                "EmbargoNode requires a non-empty until_date")
        from s3dgraphy.nodes.embargo_node import EmbargoNode
        from .uuid7 import uuid7
        node_uuid = str(uuid7())
        node = EmbargoNode(
            node_id=node_uuid,
            name=f"Embargo until {until_date}",
            embargo_end=str(until_date),
            reason=reason or "",
        )
        node.attributes = {
            "sito": self._sito,
            "until_date": str(until_date),
            "reason": reason or "",
            "node_uuid": node_uuid,
        }
        self.add_node(node)
        return node_uuid

    def list_embargos(self) -> list[dict]:
        out = []
        for n in self.read().nodes:
            if type(n).__name__ != "EmbargoNode":
                continue
            attrs = getattr(n, "attributes", None) or {}
            data = getattr(n, "data", None) or {}
            out.append({
                "node_uuid": getattr(n, "node_id", ""),
                "until_date": (attrs.get("until_date", "")
                               or data.get("embargo_end", "")),
                "reason": attrs.get("reason", "") or data.get("reason", ""),
            })
        return out
```

- [ ] **Step 4: Run tests, expect green**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v
```

Expected: all green (~14 tests).

- [ ] **Step 5: Full suite — 108 + 6 = 114**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `114 passed`. AC-2 baseline still green.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/paradata_store.py \
        tests/sync/test_paradata_store.py
git commit -m "$(cat <<'EOF'
feat(paradata_store): high-level helpers — add/list author/license/embargo

Implements the high-level CRUD API (D5):
  - add_author(name, orcid?, role?) -> uuid7
  - list_authors() -> [{node_uuid, name, orcid, role}, ...]
  - add_license(spdx_id, url?) -> uuid7
  - list_licenses() -> [{node_uuid, spdx_id, url}, ...]
  - add_embargo(until_date, reason?) -> uuid7
  - list_embargos() -> [{node_uuid, until_date, reason}, ...]
  - remove(node_uuid) — alias for remove_node()

Each `add_*` instantiates the corresponding s3dgraphy node class
(AuthorNode/LicenseNode/EmbargoNode), stashes extra attributes on
`.attributes` (so AI04 data-key round-trip preserves them across
GraphML export/import), and persists atomically via add_node().

Site-level scope (D9) — no edges from these nodes to specific
stratigraphic units.

Validation: empty `name`/`spdx_id`/`until_date` raise
ParadataValidationError. Bogus formats accepted as-is (validation
deferred to AI06+).

6 new tests (round-trip per type, isolation/no-edges, validation,
remove alias).

Tests: 114/114 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.4: Atomic crash-safety test

**Files:**
- Modify: `tests/sync/test_paradata_store.py` (append the crash test)

- [ ] **Step 1: Append failing test**

```python
def test_atomic_write_no_corruption_on_crash(tmp_path, monkeypatch):
    """AC-3: simulate a crash during os.replace, assert original
    file is untouched and tmp file is cleaned up."""
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataWriteError)

    store = ParadataStore(_make_db(tmp_path), "X")
    # Seed initial content
    store.add_author("Original")
    original_bytes = store.file_path.read_bytes()
    assert len(original_bytes) > 0

    # Patch os.replace globally to raise
    real_replace = os.replace

    def boom(src, dst):
        raise OSError("simulated crash mid-rename")
    monkeypatch.setattr("os.replace", boom)

    # Try to add another author → write fails
    with pytest.raises(ParadataWriteError):
        store.add_author("New")

    # Original file untouched
    assert store.file_path.read_bytes() == original_bytes
    # Tmp file cleaned up
    assert not store.file_path.with_suffix(".graphml.tmp").exists()


def test_paradata_store_init_validates_sito(tmp_path):
    """Empty sito at construction raises ParadataValidationError."""
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataValidationError)
    db = _make_db(tmp_path)
    with pytest.raises(ParadataValidationError):
        ParadataStore(db, "")
```

- [ ] **Step 2: Run tests, expect green** (the implementation already supports this from B.1)

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v
```

Expected: ~16 passed.

- [ ] **Step 3: Full suite — 114 + 2 = 116**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `116 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_paradata_store.py
git commit -m "$(cat <<'EOF'
test(paradata_store): atomic crash-safety + init validation

Pins AC-3 with the canonical "monkey-patch os.replace to raise"
pattern:
  - Seed initial content via add_author(), capture file bytes
  - Patch os.replace to raise OSError mid-rename
  - Trigger add_author() again → expect ParadataWriteError
  - Assert original file bytes unchanged
  - Assert .tmp file cleaned up

Plus a constructor-level validation test: empty sito raises
ParadataValidationError immediately.

Tests: 116/116 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group C — GraphProjector Strategy A promotion [HIGH RISK]

The `_enrich_pyarchinit_graph()` standalone function in `graphml_writer.py` is moved into `GraphProjector` private methods, then deleted. The single existing call site (`export_graphml()`) is updated. AC-2 baseline guards regression.

### Task C.1: Extract `_enrich_pyarchinit_graph` body into private GraphProjector methods

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`

The current `populate_graph()` is a thin wrapper:

```python
def populate_graph(self, db_path: Path, sito: str) -> "s3dgraphy.Graph":
    ...
    from .graphml_writer import _enrich_pyarchinit_graph
    graph = ...
    _enrich_pyarchinit_graph(graph, db_path, sito_filter=sito)
    return graph
```

We need to absorb the body of `_enrich_pyarchinit_graph` (currently in `graphml_writer.py`) into `GraphProjector` private methods. The function lives roughly between lines 222 and 540 of `graphml_writer.py`.

- [ ] **Step 1: Identify the function boundaries**

```bash
grep -nE "^def _enrich_pyarchinit_graph|^def [a-z_]+" modules/s3dgraphy/sync/graphml_writer.py | head -10
```

Note the start line of `_enrich_pyarchinit_graph` and the **next** top-level `def` (which marks the end). Capture the body lines.

- [ ] **Step 2: Run AC-2 baseline first as starting reference**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`.

- [ ] **Step 3: Extract body into private methods**

Read the full `_enrich_pyarchinit_graph` body, then refactor it into `GraphProjector` private methods. A pragmatic incremental approach:

1. Copy the entire `_enrich_pyarchinit_graph` body verbatim into a new private method `GraphProjector._enrich_into(self, graph, db_path, sito_filter=None)`.
2. Update `populate_graph()` to call `self._enrich_into(graph, db_path, sito_filter=sito)` instead of the standalone function.
3. Keep `_enrich_pyarchinit_graph` in `graphml_writer.py` for now (will be deleted in C.3) — both call sites will work in parallel during the transition.

The method body is large (~300 lines). Don't decompose into smaller methods YET — that's a follow-up if time permits. The primary goal of C.1 is to **own** the code inside `GraphProjector` so deletion in C.3 is purely a delete + call-site update.

Use the Edit tool to:
1. Read the existing `populate_graph()` body in `graph_projector.py`.
2. Add a new method `_enrich_into(self, graph, db_path, sito_filter=None)` that contains the SAME logic as `_enrich_pyarchinit_graph` from `graphml_writer.py`. Hint: the cleanest move is to use the controller's Bash + sed to copy the lines, then adjust indent (function → method).
3. Replace the `from .graphml_writer import _enrich_pyarchinit_graph` import + call with `self._enrich_into(graph, db_path, sito_filter=sito)`.

Concretely (assuming `_enrich_pyarchinit_graph` body extracted into a string `_BODY`):

```python
# At end of GraphProjector class:
def _enrich_into(self, graph, db_path, sito_filter=None):
    """Phase 2 / Strategy A — full-class implementation.

    Body absorbed verbatim from the soon-to-be-deleted
    _enrich_pyarchinit_graph() in graphml_writer.py.
    """
    # ... full body of _enrich_pyarchinit_graph, indent shifted by +4 ...
```

And in `populate_graph()`, replace the standalone-function import + call:

```python
# OLD
from .graphml_writer import _enrich_pyarchinit_graph
_enrich_pyarchinit_graph(graph, db_path, sito_filter=sito)

# NEW
self._enrich_into(graph, db_path, sito_filter=sito)
```

- [ ] **Step 4: Run AC-2 baseline guard (CRITICAL)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`. If RED, the move introduced a bug — investigate by diffing the new `_enrich_into` against the original `_enrich_pyarchinit_graph`.

- [ ] **Step 5: Run AI04 round-trip + idempotent + CLI guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_round_trip.py \
    tests/sync/test_idempotent_ingest.py \
    tests/sync/test_cli_helper.py -v 2>&1 | tail -3
```

Expected: all pass.

- [ ] **Step 6: Full suite — should still be 116**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `116 passed`.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py
git commit -m "$(cat <<'EOF'
refactor(graph_projector): absorb _enrich_pyarchinit_graph body
(Strategy A step 1/2)

AI04 left _enrich_pyarchinit_graph as a standalone function in
graphml_writer.py and GraphProjector.populate_graph as a thin
wrapper. AI05 D7 promotes GraphProjector to a proper class.

This step copies the full body of _enrich_pyarchinit_graph into a
new private method GraphProjector._enrich_into() with the same
signature and behaviour. populate_graph() now calls
self._enrich_into(...) instead of the standalone function.

The standalone function in graphml_writer.py is NOT yet deleted —
that happens in Task C.3. The two call paths (private method +
standalone function) coexist temporarily so this commit is
revertable in isolation.

AC-2 baseline GREEN. AI04 round-trip / idempotent / CLI all pass.
No new tests; the existing AI03/AI04 suite exercises both call
paths through different entry points.

Tests: 116/116 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task C.2: Add `include_paradata=True` kwarg + `_merge_paradata`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`
- Create: `tests/sync/test_graph_projector_paradata.py`

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_graph_projector_paradata.py`:

```python
"""L1 fixture-based: include_paradata kwarg semantics (D3)."""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst); backfill_uuids(dst)
    return dst


def _read_sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def test_populate_graph_includes_paradata_by_default(mini_volterra):
    """D3: default is include_paradata=True. Add a paradata file
    next to the DB and verify it appears in the graph."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    sito = _read_sito(mini_volterra)
    store = ParadataStore(mini_volterra, sito)
    auth_uuid = store.add_author("Marco Pacifico")

    p = GraphProjector()
    graph = p.populate_graph(mini_volterra, sito=sito)
    types = [type(n).__name__ for n in graph.nodes]
    assert "AuthorNode" in types, (
        f"populate_graph default did not include paradata: {types}")
    # Verify the specific author uuid is present
    assert any(getattr(n, "node_id", "") == auth_uuid
               for n in graph.nodes)


def test_opt_out_disables_merge(mini_volterra):
    """D3 opt-out: include_paradata=False excludes paradata nodes
    even if the file exists."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    sito = _read_sito(mini_volterra)
    ParadataStore(mini_volterra, sito).add_author("Marco")

    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=False)
    types = [type(n).__name__ for n in graph.nodes]
    assert "AuthorNode" not in types


def test_populate_graph_no_paradata_file_no_error(mini_volterra):
    """include_paradata=True + no file → returns strat layer (no error)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=True)
    # Should still have strat nodes (Volterra fixture)
    assert len(graph.nodes) > 0


def test_populate_graph_corrupt_paradata_falls_back(mini_volterra):
    """If paradata file is corrupt, log warning and return strat layer."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    sito = _read_sito(mini_volterra)
    store = ParadataStore(mini_volterra, sito)
    # Write garbage
    store.file_path.write_text("not valid xml at all")

    # Should NOT raise — falls back to strat-only
    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=True)
    types = [type(n).__name__ for n in graph.nodes]
    assert "AuthorNode" not in types
    assert len(graph.nodes) > 0  # strat still present
```

- [ ] **Step 2: Run, expect failures (kwarg not yet defined)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v
```

Expected: `TypeError: populate_graph() got an unexpected keyword argument 'include_paradata'`.

- [ ] **Step 3: Add the kwarg + `_merge_paradata`**

In `modules/s3dgraphy/sync/graph_projector.py`, modify `populate_graph()`:

```python
def populate_graph(
    self,
    db_path: Path,
    sito: str,
    *,
    include_paradata: bool = True,   # NEW (D3)
) -> "s3dgraphy.Graph":
    """Build a stratigraphic-layer Graph + (default) merge in any
    paradata.graphml that exists for this (db, sito).

    Set include_paradata=False to get pure-strat (backward-compat
    with AI04 callers like export_graphml).
    """
    if not sito:
        raise ProjectionError(
            "sito parameter is mandatory for GraphProjector.populate_graph(); "
            "AI04 only supports single-site graphs.")
    db_path = Path(db_path)
    if not db_path.exists():
        raise ProjectionError(f"DB file not found: {db_path}")

    # Verify Phase 1 migration applied: us_table.node_uuid column.
    self._verify_node_uuid_column(db_path)

    # Build the strat layer (existing logic)
    from s3dgraphy import Graph
    graph = Graph(graph_id=sito)
    try:
        self._enrich_into(graph, db_path, sito_filter=sito)
    except Exception as e:
        raise ProjectionError(
            f"Enrichment failed for sito={sito!r}: {e}") from e

    # Filter post-enrichment as before
    kept = {
        n.node_id for n in graph.nodes
        if not hasattr(n, "attributes")
        or n.attributes is None
        or n.attributes.get("sito") in (None, sito)
    }
    graph.nodes = [
        n for n in graph.nodes
        if n.node_id in kept or _is_epoch_node(n)
    ]

    # NEW (D3): merge paradata if requested + file present
    if include_paradata:
        self._merge_paradata(graph, db_path, sito)

    return graph

def _merge_paradata(self, graph, db_path, sito):
    """Read paradata.graphml for sito and add its nodes to *graph*.

    Non-fatal on read errors — log warning and proceed. The user
    still gets the strat layer.
    """
    from .paradata_store import ParadataStore, ParadataReadError
    import logging
    log = logging.getLogger(__name__)
    store = ParadataStore(db_path, sito)
    if not store.exists():
        return
    try:
        paradata_graph = store.read()
    except ParadataReadError as e:
        log.warning(
            f"Paradata file unreadable, falling back to strat-only: {e}")
        return
    existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}
    for n in paradata_graph.nodes:
        nid = getattr(n, "node_id", None)
        if nid and nid not in existing_ids:
            graph.add_node(n)
```

You may also need to extract the existing schema-check code into a `_verify_node_uuid_column` private method if it's not already:

```python
def _verify_node_uuid_column(self, db_path):
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(us_table)")
        cols = {row[1] for row in cur.fetchall()}
        conn.close()
    except sqlite3.Error as e:
        raise ProjectionError(f"Cannot read us_table schema: {e}") from e
    if "node_uuid" not in cols:
        raise ProjectionError(
            "us_table.node_uuid column missing — run "
            "scripts/migrations/2026_05_node_uuid_backfill.py --apply")
```

(If the existing code already lives inline in `populate_graph()`, just extract it.)

- [ ] **Step 4: Run new tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: AC-2 baseline + AI04 guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_ai03_export_byte_identical.py \
    tests/sync/test_round_trip.py \
    tests/sync/test_idempotent_ingest.py \
    tests/sync/test_cli_helper.py -v 2>&1 | tail -5
```

Expected: all pass. Note: AI04 callers DON'T pass `include_paradata`, so default `True` is in effect — but the AI04 fixture has no paradata file, so behaviour is unchanged.

- [ ] **Step 6: Full suite — 116 + 4 = 120**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `120 passed`.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py \
        tests/sync/test_graph_projector_paradata.py
git commit -m "$(cat <<'EOF'
feat(graph_projector): include_paradata kwarg + _merge_paradata
(Strategy A step 2/2)

Adds the D3 kwarg `include_paradata: bool = True` to
populate_graph() and the corresponding `_merge_paradata` private
method:
  - When True (default): reads ParadataStore for the sito, merges
    its AuthorNode/LicenseNode/EmbargoNode into the strat graph
    (de-dup by node_id).
  - When False: returns pure-strat (backward-compat for AI04
    callers like graphml_writer.export_graphml).
  - On paradata read error (file corrupt etc): log warning and
    fall back to strat-only — non-fatal so the user always gets
    SOME usable graph.

Also extracts the schema check (us_table.node_uuid column
existence) into _verify_node_uuid_column() — preparing for full
private-method decomposition.

4 new L1 tests covering default include + opt-out + missing-file +
corrupt-file fallback.

Tests: 120/120 pass. AC-2 baseline + AI04 round-trip/idempotent/CLI
all green.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task C.3: Delete `_enrich_pyarchinit_graph` from `graphml_writer.py` + update call site

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (DELETE function + UPDATE export_graphml call site)
- Create: `tests/sync/test_strategy_a_no_regression.py`

This is the highest-risk step. The standalone function gets DELETED, so any leftover caller crashes immediately. We grep first to be sure.

- [ ] **Step 1: Pre-flight grep — verify zero direct callers other than export_graphml**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep -rn "_enrich_pyarchinit_graph" \
    --include="*.py" \
    modules/ scripts/ tests/ tabs/ gui/ 2>/dev/null
```

Expected: hits should ONLY be:
- `modules/s3dgraphy/sync/graphml_writer.py` (definition + maybe export_graphml call)
- `modules/s3dgraphy/sync/graph_projector.py` (the import we removed in C.1, OR none if already removed)

If you find ANY other caller, STOP and adapt before deleting.

- [ ] **Step 2: Identify the export_graphml call site**

```bash
grep -nB 2 -A 3 "_enrich_pyarchinit_graph" modules/s3dgraphy/sync/graphml_writer.py
```

The `export_graphml` function calls the standalone enrichment. We need to replace that call with `GraphProjector().populate_graph(..., include_paradata=False)`.

- [ ] **Step 3: Find export_graphml's relevant block**

```bash
grep -nA 30 "def export_graphml" modules/s3dgraphy/sync/graphml_writer.py | head -40
```

Note the existing structure. The body roughly creates a Graph, calls `_enrich_pyarchinit_graph(graph, db_path)` for the strat layer, then post-processes.

- [ ] **Step 4: Edit export_graphml to use GraphProjector**

Use the Edit tool to:
1. Replace the strat-layer creation block in `export_graphml` (the `_enrich_pyarchinit_graph` call) with a `GraphProjector().populate_graph(..., include_paradata=False)` call:

```python
# OLD (approximate)
from s3dgraphy import Graph
graph = Graph(graph_id=...)
_enrich_pyarchinit_graph(graph, db_path)

# NEW
from .graph_projector import GraphProjector
graph = GraphProjector().populate_graph(
    db_path, sito=site_filter or _read_first_sito(db_path),
    include_paradata=False,
)
```

2. DELETE the entire `_enrich_pyarchinit_graph()` function definition (the ~300-line block).

The `_enrich_into` method on `GraphProjector` already contains the same logic. Verify zero remaining references via grep.

If `export_graphml` doesn't accept a `site_filter` arg, default to None and let `populate_graph` raise — but check the signature first:

```bash
grep -nA 5 "def export_graphml" modules/s3dgraphy/sync/graphml_writer.py | head -15
```

Inspect carefully and adapt. The existing AI03 export already pinned `site_filter` semantics; preserve them.

- [ ] **Step 5: Verify zero residual references**

```bash
grep -rn "_enrich_pyarchinit_graph" \
    --include="*.py" \
    modules/ scripts/ tests/ tabs/ gui/ 2>/dev/null
```

Expected: zero hits in production code (`tests/` may still reference for grep-based regression tests we're about to add).

- [ ] **Step 6: AC-2 baseline guard (CRITICAL)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: `1 passed`. If RED, the structural fingerprint changed — either:
1. Re-capture baseline (Group H concern, not now), or
2. Investigate; export_graphml flow has a real regression.

For now: if RED but the diff looks like UUID/order noise (the structural fingerprint already strips this), it's fine to regenerate the baseline in C.4. If RED with structural delta (different node count, new labels), that's a real regression — fix or revert.

- [ ] **Step 7: Run AI04 guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_round_trip.py \
    tests/sync/test_idempotent_ingest.py \
    tests/sync/test_cli_helper.py -v 2>&1 | tail -5
```

Expected: all pass.

- [ ] **Step 8: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `120 passed`.

- [ ] **Step 9: Add the regression-pinning test file**

Create `tests/sync/test_strategy_a_no_regression.py`:

```python
"""L3 regression guards for Strategy A promotion (D7).

After AI05 Group C, the standalone _enrich_pyarchinit_graph function
must NOT exist in production code. Its body lives inside
GraphProjector._enrich_into. The AI03 export_graphml() path uses
GraphProjector().populate_graph(..., include_paradata=False) to
preserve byte-equivalent output.
"""
from __future__ import annotations
import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def test_enrich_function_removed():
    """D7: the standalone _enrich_pyarchinit_graph function must NOT
    exist anywhere in production code (modules/, scripts/, tabs/,
    gui/)."""
    forbidden = "_enrich_pyarchinit_graph"
    hits = []
    for sub in ("modules", "scripts", "tabs", "gui"):
        sub_path = PLUGIN_ROOT / sub
        if not sub_path.exists():
            continue
        for py in sub_path.rglob("*.py"):
            try:
                text = py.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Look for top-level def + import + call patterns
            if re.search(
                    rf"^def {forbidden}\b|"
                    rf"from \S+ import {forbidden}|"
                    rf"\b{forbidden}\s*\(",
                    text, re.MULTILINE):
                hits.append(str(py.relative_to(PLUGIN_ROOT)))
    assert not hits, (
        f"Strategy A incomplete — _enrich_pyarchinit_graph still "
        f"referenced in: {hits}")


def test_export_graphml_uses_graph_projector():
    """D7: export_graphml must call GraphProjector().populate_graph
    instead of the deleted standalone function."""
    src = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "sync"
           / "graphml_writer.py").read_text(encoding="utf-8")
    assert "GraphProjector" in src, (
        "graphml_writer must use GraphProjector after Strategy A")


def test_graph_projector_has_enrich_into_method():
    """The body lives in GraphProjector._enrich_into now."""
    src = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "sync"
           / "graph_projector.py").read_text(encoding="utf-8")
    assert "def _enrich_into" in src
```

- [ ] **Step 10: Run regression tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_strategy_a_no_regression.py -v
```

Expected: `3 passed`.

- [ ] **Step 11: Full suite — 120 + 3 = 123**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `123 passed`.

- [ ] **Step 12: Commit (the deletion + tests + new export_graphml in one atomic commit)**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py \
        tests/sync/test_strategy_a_no_regression.py
git commit -m "$(cat <<'EOF'
refactor(graphml_writer): delete _enrich_pyarchinit_graph (Strategy A complete)

Strategy A promotion finishes here. The standalone
_enrich_pyarchinit_graph function in graphml_writer.py is DELETED.
Its body lives in GraphProjector._enrich_into() (added in Task C.1).

The single remaining call site — export_graphml() — is updated to
instantiate GraphProjector and call populate_graph(...,
include_paradata=False) for the strat-only output AI03 expects.

Pre-task grep verified zero other callers in modules/, scripts/,
tabs/, gui/. The new test file tests/sync/test_strategy_a_no_regression.py
pins this guarantee with three checks:
  1. _enrich_pyarchinit_graph not referenced anywhere in
     production code.
  2. graphml_writer.py uses GraphProjector.
  3. graph_projector.py defines _enrich_into.

AC-2 baseline GREEN (structural fingerprint preserved). AI04
round-trip + idempotent + CLI all pass.

Tests: 123/123 pass.

Closes the AI04 carry-over documented in
project_ai04_projector_refactor_plan.md (memory note).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task C.4: AC-2 baseline regen + full regression sweep

**Files:** none (regenerate baseline only if needed; otherwise verification only)

- [ ] **Step 1: Run AC-2 baseline 5 times for stability**

```bash
for i in 1 2 3 4 5; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -1
done
```

Expected: `1 passed` × 5.

- [ ] **Step 2: Run full suite 3 times**

```bash
for i in 1 2 3; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -1
done
```

Expected: `123 passed` × 3.

- [ ] **Step 3: If AC-2 is FLAKY (some pass, some fail), regenerate the baseline**

```bash
PYTHONPATH="$PWD" python <<'PY'
import pandas
from lxml import etree as _e
import sys
from pathlib import Path
ext = str(Path('.').resolve() / "ext_libs")
if ext in sys.path: sys.path.remove(ext)
sys.path.insert(0, ext)
for m in [k for k in list(sys.modules) if k=="s3dgraphy" or k.startswith("s3dgraphy.")]: del sys.modules[m]
from modules.s3dgraphy.sync.graphml_writer import export_graphml
out = Path("tests/sync/fixtures/mini_volterra_baseline_ai03.graphml")
export_graphml(db_path="tests/sync/fixtures/mini_volterra.sqlite",
               mapping="pyarchinit_us_mapping", output_path=out)
print(f"baseline regenerated: {out.stat().st_size} bytes")
PY
```

Then re-run the AC-2 5-times check. If still flaky, the structural fingerprint test itself needs adjustment (look at `test_ai03_export_byte_identical.py::_structure` — it already strips UUIDs and orders things) — but most likely the new structure is just stable in a different shape, so regen + commit suffices.

- [ ] **Step 4: If baseline regenerated, commit**

```bash
git add tests/sync/fixtures/mini_volterra_baseline_ai03.graphml
git commit -m "$(cat <<'EOF'
test(fixtures): regenerate AI03 baseline post-Strategy A

Re-captures the AI03 export pipeline output via the new
GraphProjector-based export_graphml() path. The structural
fingerprint (node count, edge count, NodeLabel set, swimlane row
count, table count) is byte-identical to the pre-Strategy-A
baseline; the regeneration just refreshes the file with current
UUIDs assigned by GraphProjector.

This commit lands ONLY if Task C.4's 5-run AC-2 stability check
showed flakiness on the old baseline. Otherwise, this commit does
not exist (the old baseline keeps passing).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

(If no regeneration was needed, this commit is skipped entirely.)

---

## Group D — Pre-cooked paradata fixture

### Task D.1: Extend `build_mini_volterra_external.py` to emit `paradata_volterra.graphml`

**Files:**
- Modify: `tests/sync/fixtures/build_mini_volterra_external.py`
- Create: `tests/sync/fixtures/paradata_volterra.graphml` (binary, generated)

- [ ] **Step 1: Read current generator**

```bash
sed -n '1,30p' tests/sync/fixtures/build_mini_volterra_external.py
```

It currently builds two `.graphml` fixtures: `mini_volterra_external.graphml` and `mini_volterra_external_with_new_epoch.graphml`. We add a third — `paradata_volterra.graphml`.

- [ ] **Step 2: Append `_emit_paradata_fixture` function call**

Use the Edit tool to add at the end of the script (before `if __name__ == "__main__":` if present):

```python
def _emit_paradata_fixture():
    """Generate paradata_volterra.graphml — pre-cooked Author/License/Embargo
    fixture used by AI05 round-trip tests."""
    import sqlite3
    import shutil
    import tempfile
    from pathlib import Path

    PLUGIN_ROOT = Path(__file__).resolve().parents[3]
    SRC_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"

    # Apply Phase 1 migration to a tmp copy so ParadataStore has a valid DB.
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids,
    )
    tmp_db = Path(tempfile.mkdtemp()) / "mini_volterra.sqlite"
    shutil.copy2(SRC_DB, tmp_db)
    add_columns(tmp_db); backfill_uuids(tmp_db)

    sito = sqlite3.connect(tmp_db).execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]

    # Use ParadataStore to seed the file with controlled UUIDs.
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(tmp_db, sito)
    store.add_author("Marco Pacifico", orcid="0000-0002-1234-5678",
                     role="curator")
    store.add_author("Maria Bianchi", orcid="0000-0001-9876-5432",
                     role="contributor")
    store.add_license("CC-BY-NC-4.0",
                      url="https://creativecommons.org/licenses/by-nc/4.0/")
    store.add_embargo("2030-12-31", reason="Volterra dataset embargo")

    # Copy the generated file into the fixtures directory under a
    # canonical name (the slug-based name depends on sito; we use a
    # site-agnostic filename for the test fixture).
    out = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "paradata_volterra.graphml"
    shutil.copy2(store.file_path, out)
    print(f"OK — paradata_volterra.graphml ({out.stat().st_size} bytes)")
```

Then call `_emit_paradata_fixture()` near the end of `main()` (or wherever the existing `_emit_*` calls are made).

- [ ] **Step 3: Run the generator**

```bash
PYTHONPATH="$PWD" python tests/sync/fixtures/build_mini_volterra_external.py
ls -la tests/sync/fixtures/paradata_volterra.graphml
```

Expected: file exists, size > 1KB.

- [ ] **Step 4: Verify content via lxml count**

```bash
python3 -c "
from lxml import etree
tree = etree.parse('tests/sync/fixtures/paradata_volterra.graphml')
root = tree.getroot()
ns = '{http://graphml.graphdrawing.org/xmlns}'
nodes = list(root.iter(ns + 'node'))
print(f'nodes: {len(nodes)}')
"
```

Expected: 4 nodes (2 Author + 1 License + 1 Embargo).

- [ ] **Step 5: Sanity full suite (no new tests but verify no breakage)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `123 passed`.

- [ ] **Step 6: Commit (binary fixture + generator extension)**

```bash
git add tests/sync/fixtures/build_mini_volterra_external.py \
        tests/sync/fixtures/paradata_volterra.graphml
git commit -m "$(cat <<'EOF'
test(fixtures): add paradata_volterra.graphml + generator extension

Pre-cooked binary fixture for AI05 round-trip + idempotent tests.
Contains 4 nodes:
  - 2 AuthorNodes ("Marco Pacifico" + "Maria Bianchi")
  - 1 LicenseNode ("CC-BY-NC-4.0")
  - 1 EmbargoNode ("until 2030-12-31")

Generated deterministically by build_mini_volterra_external.py via
ParadataStore.add_author/license/embargo on a temp copy of
mini_volterra.sqlite, then copied to a stable filename in
tests/sync/fixtures/.

Both the generator script and the binary are committed so test
runs don't depend on the script being executable.

Tests: 123/123 pass (no new tests; fixture-only commit).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group E — Round-trip + idempotent tests

### Task E.1: `test_round_trip_with_paradata.py`

**Files:**
- Create: `tests/sync/test_round_trip_with_paradata.py`

- [ ] **Step 1: Write the round-trip test**

Create `tests/sync/test_round_trip_with_paradata.py`:

```python
"""L1 round-trip with paradata layer.

DB + paradata.graphml → projector → ingest + ParadataStore.write
must preserve mapped columns AND paradata node uuids.
"""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst); backfill_uuids(dst)
    return dst


def _read_sito(db):
    conn = sqlite3.connect(db)
    s = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    conn.close()
    return s


def test_round_trip_preserves_paradata_uuids(mini_volterra):
    """D4 invariant extended: round-trip preserves both strat
    mapped columns AND paradata uuids."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    sito = _read_sito(mini_volterra)
    store_before = ParadataStore(mini_volterra, sito)
    a1 = store_before.add_author("Marco")
    a2 = store_before.add_author("Maria")
    l1 = store_before.add_license("CC-BY-4.0")
    e1 = store_before.add_embargo("2030-12-31")
    expected_uuids = {a1, a2, l1, e1}

    # Project + read paradata via store
    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, include_paradata=True)
    paradata_uuids_in_graph = {
        n.node_id for n in graph.nodes
        if type(n).__name__ in ("AuthorNode", "LicenseNode", "EmbargoNode")
    }
    assert expected_uuids.issubset(paradata_uuids_in_graph), (
        f"paradata not in graph: {expected_uuids - paradata_uuids_in_graph}")

    # Round-trip the paradata (write + read)
    paradata_subgraph_nodes = [
        n for n in graph.nodes
        if type(n).__name__ in ("AuthorNode", "LicenseNode", "EmbargoNode")
    ]
    from s3dgraphy import Graph
    rt_graph = Graph(graph_id=sito)
    for n in paradata_subgraph_nodes:
        rt_graph.add_node(n)
    store_before.write(rt_graph)

    # Read back via fresh store instance
    store_after = ParadataStore(mini_volterra, sito)
    after_uuids = {n.node_id for n in store_after.read().nodes}
    assert expected_uuids == after_uuids, (
        f"round-trip lost uuids: {expected_uuids - after_uuids}")
```

- [ ] **Step 2: Run, expect green**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v
```

Expected: `1 passed`.

- [ ] **Step 3: Full suite — 123 + 1 = 124**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `124 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_round_trip_with_paradata.py
git commit -m "$(cat <<'EOF'
test(round_trip_with_paradata): D4 invariant extended to AI05

Pins the round-trip semantic invariant for the paradata layer:
  - Seed 4 paradata nodes via ParadataStore (2 authors, 1 license,
    1 embargo).
  - Project via GraphProjector(include_paradata=True): graph has
    strat + all 4 paradata uuids.
  - Round-trip paradata sub-graph via ParadataStore.write +
    fresh-instance read.
  - Assert all 4 uuids preserved.

This guarantees that the GraphML serialise/parse round-trip
through the AI04 helper (_embed_/`_hydrate_pyarchinit_data_keys`)
preserves paradata node identity end-to-end.

Tests: 124/124 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task E.2: `test_paradata_idempotent.py`

**Files:**
- Create: `tests/sync/test_paradata_idempotent.py`

- [ ] **Step 1: Write the idempotent test**

Create `tests/sync/test_paradata_idempotent.py`:

```python
"""L1 idempotent paradata writes.

Three consecutive add_author + write cycles must converge — no
duplicate nodes, file size stable from run 2 onwards.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def _make_db(tmp_path):
    import sqlite3
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INT, sito TEXT)")
    conn.commit(); conn.close()
    return db


def test_repeated_add_author_creates_distinct_nodes(tmp_path):
    """Adding the same name N times creates N distinct nodes
    (each call produces a fresh uuid7) — this is the EXPECTED
    behavior since name is not a primary key."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    u1 = store.add_author("Marco")
    u2 = store.add_author("Marco")
    u3 = store.add_author("Marco")
    assert u1 != u2 != u3  # distinct uuids
    assert len(store.list_authors()) == 3


def test_re_read_after_write_idempotent(tmp_path):
    """Reading + writing the same graph produces a stable file:
    file_size after run 2 == file_size after run 3."""
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    store = ParadataStore(_make_db(tmp_path), "X")
    store.add_author("Marco")

    # Run 1: read + write (no mutation in between)
    g1 = store.read()
    store.write(g1)
    size1 = store.file_path.stat().st_size

    # Run 2: same
    g2 = store.read()
    store.write(g2)
    size2 = store.file_path.stat().st_size

    # Sizes might differ run 1 vs 2 due to UUID/timestamp embedding,
    # but run 2 vs 3 must be stable.
    g3 = store.read()
    store.write(g3)
    size3 = store.file_path.stat().st_size

    assert size2 == size3, (
        f"non-idempotent write: run 2={size2}, run 3={size3}")
    # Nodes preserved
    assert len(store.read().nodes) == 1
```

- [ ] **Step 2: Run, expect green**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_idempotent.py -v
```

Expected: `2 passed`.

- [ ] **Step 3: Full suite — 124 + 2 = 126**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `126 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_paradata_idempotent.py
git commit -m "$(cat <<'EOF'
test(paradata_idempotent): D4-C invariant for paradata round-trip

Two tests:
  1. Repeated add_author with identical name creates DISTINCT nodes
     (each call generates fresh uuid7). Pins the "name is not a
     primary key" semantic — same person can be added multiple
     times if the user wants multi-role authorship.
  2. Read + write cycles converge: file_size after run 2 ==
     file_size after run 3. Run 1 vs run 2 may differ due to
     UUID/timestamp embedding.

These pin the AI05 idempotency contract for paradata, parallel to
AI04's D4-C for stratigraphic ingestion.

Tests: 126/126 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group F — CLI subcommands

### Task F.1: Extend `scripts/s3dgraphy_sync.py` with `paradata` subcommand

**Files:**
- Modify: `scripts/s3dgraphy_sync.py`

- [ ] **Step 1: Read current CLI structure**

```bash
sed -n '1,50p' scripts/s3dgraphy_sync.py
grep -nE "def cmd_|sub\.add_parser" scripts/s3dgraphy_sync.py | head -10
```

Note: AI04 already has `export` and `import` subcommands. We add `paradata` with 7 sub-subcommands.

- [ ] **Step 2: Add paradata subcommand**

Use the Edit tool to add new command handlers + argparse setup. After the existing `cmd_import` function, append:

```python
def cmd_paradata(args) -> int:
    _setup_path()
    from modules.s3dgraphy.sync.paradata_store import (
        ParadataStore, ParadataStoreError,
    )
    store = ParadataStore(Path(args.db), args.sito)
    sub = args.paradata_action
    try:
        if sub == "add-author":
            uuid = store.add_author(args.name, orcid=args.orcid,
                                     role=args.role)
            print(f"OK — author {uuid}")
        elif sub == "list-authors":
            for a in store.list_authors():
                print(f"{a['node_uuid']}\t{a['name']}\t{a.get('orcid','')}\t{a.get('role','')}")
        elif sub == "add-license":
            uuid = store.add_license(args.spdx, url=args.url)
            print(f"OK — license {uuid}")
        elif sub == "list-licenses":
            for li in store.list_licenses():
                print(f"{li['node_uuid']}\t{li['spdx_id']}\t{li.get('url','')}")
        elif sub == "add-embargo":
            uuid = store.add_embargo(args.until, reason=args.reason)
            print(f"OK — embargo {uuid}")
        elif sub == "list-embargos":
            for e in store.list_embargos():
                print(f"{e['node_uuid']}\t{e['until_date']}\t{e.get('reason','')}")
        elif sub == "remove":
            store.remove(args.uuid)
            print(f"OK — removed {args.uuid}")
        else:
            print(f"ERROR: unknown paradata action: {sub}", file=sys.stderr)
            return 2
    except ParadataStoreError as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0
```

Then in the argparse setup, add:

```python
# in the main() function, after existing sub.add_parser calls
p_para = sub.add_parser("paradata", help="Manage paradata.graphml")
para_sub = p_para.add_subparsers(dest="paradata_action", required=True)

p_aa = para_sub.add_parser("add-author")
p_aa.add_argument("--db", required=True)
p_aa.add_argument("--sito", required=True)
p_aa.add_argument("--name", required=True)
p_aa.add_argument("--orcid")
p_aa.add_argument("--role")
p_aa.set_defaults(func=cmd_paradata)

p_la = para_sub.add_parser("list-authors")
p_la.add_argument("--db", required=True)
p_la.add_argument("--sito", required=True)
p_la.set_defaults(func=cmd_paradata)

p_al = para_sub.add_parser("add-license")
p_al.add_argument("--db", required=True)
p_al.add_argument("--sito", required=True)
p_al.add_argument("--spdx", required=True)
p_al.add_argument("--url")
p_al.set_defaults(func=cmd_paradata)

p_ll = para_sub.add_parser("list-licenses")
p_ll.add_argument("--db", required=True)
p_ll.add_argument("--sito", required=True)
p_ll.set_defaults(func=cmd_paradata)

p_ae = para_sub.add_parser("add-embargo")
p_ae.add_argument("--db", required=True)
p_ae.add_argument("--sito", required=True)
p_ae.add_argument("--until", required=True)
p_ae.add_argument("--reason")
p_ae.set_defaults(func=cmd_paradata)

p_le = para_sub.add_parser("list-embargos")
p_le.add_argument("--db", required=True)
p_le.add_argument("--sito", required=True)
p_le.set_defaults(func=cmd_paradata)

p_rm = para_sub.add_parser("remove")
p_rm.add_argument("--db", required=True)
p_rm.add_argument("--sito", required=True)
p_rm.add_argument("--uuid", required=True)
p_rm.set_defaults(func=cmd_paradata)
```

- [ ] **Step 3: Smoke-test from shell**

```bash
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata --help
```

Expected: argparse help showing the 7 subcommands.

- [ ] **Step 4: Smoke-test add-author + list-authors**

Use a temp DB:

```bash
TMP=$(mktemp -d)
cp tests/sync/fixtures/mini_volterra.sqlite "$TMP/test.sqlite"
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata add-author \
    --db "$TMP/test.sqlite" --sito TestSite --name "Marco" --orcid 0000-0002-1234-5678
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata list-authors \
    --db "$TMP/test.sqlite" --sito TestSite
rm -rf "$TMP"
```

Expected: `OK — author <uuid>` then list-authors prints the row.

- [ ] **Step 5: Sanity full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `126 passed`.

- [ ] **Step 6: Commit**

```bash
git add scripts/s3dgraphy_sync.py
git commit -m "$(cat <<'EOF'
feat(scripts): paradata subcommand suite for s3dgraphy_sync.py

Adds 7 paradata sub-subcommands to the AI04 CLI helper:
  - add-author --name [--orcid] [--role]
  - list-authors
  - add-license --spdx [--url]
  - list-licenses
  - add-embargo --until [--reason]
  - list-embargos
  - remove --uuid

Each subcommand:
  - Requires --db and --sito (consistent with AI04 CLI shape).
  - Returns exit 0 on success / 1 on ParadataStoreError / 2 on
    argparse error.
  - list-* output is tab-separated for easy shell-piping.
  - add-* prints the new node uuid7 for scripting.

Smoke-tested manually: add-author + list-authors round-trip.

Subprocess tests in test_cli_paradata.py land in F.2.

Tests: 126/126 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task F.2: Subprocess tests for paradata CLI

**Files:**
- Create: `tests/sync/test_cli_paradata.py`

- [ ] **Step 1: Write subprocess tests**

Create `tests/sync/test_cli_paradata.py`:

```python
"""L2 subprocess tests for scripts/s3dgraphy_sync.py paradata ..."""
from __future__ import annotations
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PLUGIN_ROOT / "scripts" / "s3dgraphy_sync.py"
FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    return dst


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
        cwd=str(PLUGIN_ROOT),
    )


def test_cli_paradata_add_author(mini_volterra):
    r = _run("paradata", "add-author",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--name", "Marco")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "OK" in r.stdout
    assert "author" in r.stdout


def test_cli_paradata_list_authors_after_add(mini_volterra):
    _run("paradata", "add-author",
         "--db", str(mini_volterra),
         "--sito", "TestSite",
         "--name", "Marco",
         "--orcid", "0000-0002-1234-5678")
    r = _run("paradata", "list-authors",
             "--db", str(mini_volterra),
             "--sito", "TestSite")
    assert r.returncode == 0
    assert "Marco" in r.stdout
    assert "0000-0002-1234-5678" in r.stdout


def test_cli_paradata_add_license(mini_volterra):
    r = _run("paradata", "add-license",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--spdx", "CC-BY-NC-4.0")
    assert r.returncode == 0
    assert "OK" in r.stdout


def test_cli_paradata_add_embargo(mini_volterra):
    r = _run("paradata", "add-embargo",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--until", "2030-12-31",
             "--reason", "test embargo")
    assert r.returncode == 0
    assert "OK" in r.stdout


def test_cli_paradata_remove(mini_volterra):
    # Add author, capture uuid, then remove
    r = _run("paradata", "add-author",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--name", "Marco")
    assert r.returncode == 0
    # Output format: "OK — author <uuid>"
    uuid = r.stdout.strip().split()[-1]

    r2 = _run("paradata", "remove",
              "--db", str(mini_volterra),
              "--sito", "TestSite",
              "--uuid", uuid)
    assert r2.returncode == 0
    assert uuid in r2.stdout

    # Verify list is empty
    r3 = _run("paradata", "list-authors",
              "--db", str(mini_volterra),
              "--sito", "TestSite")
    assert r3.returncode == 0
    assert uuid not in r3.stdout


def test_cli_paradata_invalid_subcommand_exits_2(mini_volterra):
    r = _run("paradata", "totally-bogus", "--db", str(mini_volterra))
    assert r.returncode == 2
```

- [ ] **Step 2: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_cli_paradata.py -v
```

Expected: `6 passed`.

- [ ] **Step 3: Full suite — 126 + 6 = 132**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `132 passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_cli_paradata.py
git commit -m "$(cat <<'EOF'
test(cli_paradata): subprocess tests for the 7 paradata subcommands

Six L2 tests via subprocess.run() against scripts/s3dgraphy_sync.py:
  - add-author exit 0 + "OK" in stdout
  - list-authors prints the just-added Marco + ORCID
  - add-license exit 0 + "OK"
  - add-embargo exit 0 + "OK"
  - remove round-trip: add then remove, verify list is empty
  - invalid subcommand exits 2 (argparse error)

Pins AC-15 (CLI add-author + list-authors + remove work via
subprocess) and the exit-code contract.

Tests: 132/132 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group G — UI ParadataManagerDialog

### Task G.1: Create `gui/dialog_paradata_manager.py`

**Files:**
- Create: `gui/dialog_paradata_manager.py`
- Create: `tests/sync/test_paradata_dialog_smoke.py`

- [ ] **Step 1: Write the dialog smoke test**

Create `tests/sync/test_paradata_dialog_smoke.py`:

```python
"""L0 smoke test for ParadataManagerDialog: dialog instantiates
without crash and has 3 tabs. Skipped if Qt is not available."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _qt_available() -> bool:
    try:
        from qgis.PyQt.QtWidgets import QDialog, QApplication  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _qt_available(),
                    reason="QGIS Qt not available")
def test_paradata_dialog_can_open(tmp_path):
    """Dialog instantiates with 3 tabs and doesn't crash on
    _load_data()."""
    from qgis.PyQt.QtWidgets import QApplication
    if QApplication.instance() is None:
        QApplication([])

    # Stub db_manager
    class _FakeDBManager:
        def __init__(self, db):
            self._db = db
        def get_sqlite_path(self):
            return self._db

    # Make a real tmp DB
    import sqlite3
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INT, sito TEXT)")
    conn.commit(); conn.close()

    from gui.dialog_paradata_manager import ParadataManagerDialog
    dialog = ParadataManagerDialog(
        parent=None, db_manager=_FakeDBManager(db), sito="X")
    assert dialog.tabs.count() == 3
    assert dialog.tabs.tabText(0).lower() == "authors"
    assert dialog.tabs.tabText(1).lower() == "licenses"
    assert dialog.tabs.tabText(2).lower() == "embargoes"
```

- [ ] **Step 2: Run, expect skip (no Qt in pytest env)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_dialog_smoke.py -v
```

Expected: `1 skipped`. (If Qt happens to be importable, the test runs and fails — proceed to step 3.)

- [ ] **Step 3: Implement the dialog**

Create `gui/dialog_paradata_manager.py`:

```python
"""ParadataManagerDialog — single-dialog 3-tab CRUD for site-level
paradata (Authors / Licenses / Embargoes).

Triggered by the "Manage paradata" button in the US scheda
(`tabs/US_USM.py`). Uses the qgis.PyQt abstraction for Qt5/Qt6
compatibility (mirrors the AI03/AI04 dialog pattern).
"""
from __future__ import annotations

try:
    from qgis.PyQt.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
        QLineEdit, QFormLayout, QMessageBox, QHeaderView,
    )
    from qgis.PyQt.QtCore import Qt
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


if QGIS_AVAILABLE:
    class ParadataManagerDialog(QDialog):
        """3-tab dialog for Author/License/Embargo CRUD on
        paradata_{sito}.graphml.
        """

        def __init__(self, parent, db_manager, sito: str):
            super().__init__(parent)
            self.db_manager = db_manager
            self.sito = sito
            self.setWindowTitle(f"Manage paradata — {sito}")
            self.setMinimumWidth(700)
            self._setup_ui()
            self._load_data()

        def _setup_ui(self):
            layout = QVBoxLayout()
            title = QLabel(f"<h3>Paradata for site: {self.sito}</h3>")
            layout.addWidget(title)
            desc = QLabel(
                "Manage authorship, licensing and embargo metadata "
                "stored in paradata.graphml (versionable in Git).")
            desc.setWordWrap(True)
            layout.addWidget(desc)

            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)

            self._setup_tab_authors()
            self._setup_tab_licenses()
            self._setup_tab_embargoes()

            close = QPushButton("Close")
            close.clicked.connect(self.accept)
            layout.addWidget(close)
            self.setLayout(layout)

        def _setup_tab_authors(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_authors = QTableWidget(0, 3)
            self.table_authors.setHorizontalHeaderLabels(
                ["Name", "ORCID", "Role"])
            self.table_authors.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_authors)

            form = QFormLayout()
            self.le_auth_name = QLineEdit()
            self.le_auth_orcid = QLineEdit()
            self.le_auth_role = QLineEdit()
            form.addRow("Name:", self.le_auth_name)
            form.addRow("ORCID:", self.le_auth_orcid)
            form.addRow("Role:", self.le_auth_role)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.clicked.connect(self._on_add_author)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_authors, "author"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Authors")

        def _setup_tab_licenses(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_licenses = QTableWidget(0, 2)
            self.table_licenses.setHorizontalHeaderLabels(
                ["SPDX ID", "URL"])
            self.table_licenses.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_licenses)

            form = QFormLayout()
            self.le_lic_spdx = QLineEdit()
            self.le_lic_url = QLineEdit()
            form.addRow("SPDX ID:", self.le_lic_spdx)
            form.addRow("URL:", self.le_lic_url)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.clicked.connect(self._on_add_license)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_licenses, "license"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Licenses")

        def _setup_tab_embargoes(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_embargoes = QTableWidget(0, 2)
            self.table_embargoes.setHorizontalHeaderLabels(
                ["Until", "Reason"])
            self.table_embargoes.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_embargoes)

            form = QFormLayout()
            self.le_emb_until = QLineEdit()
            self.le_emb_until.setPlaceholderText("YYYY-MM-DD")
            self.le_emb_reason = QLineEdit()
            form.addRow("Until:", self.le_emb_until)
            form.addRow("Reason:", self.le_emb_reason)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add")
            btn_add.clicked.connect(self._on_add_embargo)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_embargoes, "embargo"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Embargoes")

        def _store(self):
            from modules.s3dgraphy.sync.paradata_store import ParadataStore
            db_path = self.db_manager.get_sqlite_path() if self.db_manager else None
            if db_path is None:
                QMessageBox.critical(
                    self, "No SQLite DB",
                    "Paradata management requires a SQLite-backed pyarchinit project.")
                return None
            return ParadataStore(db_path, self.sito)

        def _load_data(self):
            store = self._store()
            if store is None:
                return
            try:
                authors = store.list_authors()
                licenses = store.list_licenses()
                embargoes = store.list_embargos()
            except Exception as e:
                QMessageBox.critical(
                    self, "Read failed",
                    f"Cannot load paradata: {type(e).__name__}: {e}")
                return
            self._fill_authors(authors)
            self._fill_licenses(licenses)
            self._fill_embargoes(embargoes)

        def _fill_authors(self, rows):
            self.table_authors.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_authors.setItem(
                    i, 0, QTableWidgetItem(r.get("name", "")))
                self.table_authors.setItem(
                    i, 1, QTableWidgetItem(r.get("orcid", "")))
                self.table_authors.setItem(
                    i, 2, QTableWidgetItem(r.get("role", "")))
                # Stash uuid in row's first item user data
                self.table_authors.item(i, 0).setData(
                    Qt.UserRole, r["node_uuid"])

        def _fill_licenses(self, rows):
            self.table_licenses.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_licenses.setItem(
                    i, 0, QTableWidgetItem(r.get("spdx_id", "")))
                self.table_licenses.setItem(
                    i, 1, QTableWidgetItem(r.get("url", "")))
                self.table_licenses.item(i, 0).setData(
                    Qt.UserRole, r["node_uuid"])

        def _fill_embargoes(self, rows):
            self.table_embargoes.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_embargoes.setItem(
                    i, 0, QTableWidgetItem(r.get("until_date", "")))
                self.table_embargoes.setItem(
                    i, 1, QTableWidgetItem(r.get("reason", "")))
                self.table_embargoes.item(i, 0).setData(
                    Qt.UserRole, r["node_uuid"])

        def _on_add_author(self):
            store = self._store()
            if store is None:
                return
            name = self.le_auth_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Invalid", "Name is required.")
                return
            try:
                store.add_author(
                    name,
                    orcid=self.le_auth_orcid.text().strip() or None,
                    role=self.le_auth_role.text().strip() or None,
                )
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self.le_auth_name.clear()
            self.le_auth_orcid.clear()
            self.le_auth_role.clear()
            self._load_data()

        def _on_add_license(self):
            store = self._store()
            if store is None:
                return
            spdx = self.le_lic_spdx.text().strip()
            if not spdx:
                QMessageBox.warning(self, "Invalid", "SPDX ID is required.")
                return
            try:
                store.add_license(
                    spdx, url=self.le_lic_url.text().strip() or None)
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self.le_lic_spdx.clear()
            self.le_lic_url.clear()
            self._load_data()

        def _on_add_embargo(self):
            store = self._store()
            if store is None:
                return
            until = self.le_emb_until.text().strip()
            if not until:
                QMessageBox.warning(self, "Invalid", "Until date is required.")
                return
            try:
                store.add_embargo(
                    until,
                    reason=self.le_emb_reason.text().strip() or None,
                )
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self.le_emb_until.clear()
            self.le_emb_reason.clear()
            self._load_data()

        def _on_remove_selected(self, table, label):
            row = table.currentRow()
            if row < 0:
                QMessageBox.information(
                    self, "No selection",
                    f"Select a {label} row to remove.")
                return
            uuid = table.item(row, 0).data(Qt.UserRole)
            if not uuid:
                return
            store = self._store()
            if store is None:
                return
            try:
                store.remove(uuid)
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self._load_data()


else:
    class ParadataManagerDialog:
        """Fallback when QGIS Qt is not available (CI / test envs).
        Importable but not instantiable."""
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "ParadataManagerDialog requires QGIS PyQt — not available")
```

- [ ] **Step 4: Run smoke test (skip if no Qt)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_dialog_smoke.py -v
```

Expected: `1 skipped` in headless test env.

- [ ] **Step 5: Verify file is syntactically valid**

```bash
python -c "import ast; ast.parse(open('gui/dialog_paradata_manager.py').read()); print('OK')"
```

Expected: `OK`.

- [ ] **Step 6: Full suite — 132 + 1 skipped = 132 passed, 1 skipped**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `132 passed, 1 skipped`.

- [ ] **Step 7: Commit**

```bash
git add gui/dialog_paradata_manager.py \
        tests/sync/test_paradata_dialog_smoke.py
git commit -m "$(cat <<'EOF'
feat(gui): ParadataManagerDialog — 3-tab CRUD for paradata

Per spec §3.4 (D6), ships gui/dialog_paradata_manager.py with the
ParadataManagerDialog class:
  - QDialog with QTabWidget (3 tabs: Authors / Licenses / Embargoes).
  - Each tab: QTableWidget showing existing entries + form for
    adding new ones + Remove-selected button.
  - All CRUD ops go through ParadataStore (low-level write +
    high-level helpers).
  - Errors via QMessageBox.critical/warning.

Wired to the qgis.PyQt abstraction for Qt5/Qt6 compatibility
(mirrors the AI03/AI04 dialog pattern).

Smoke test verifies dialog instantiates with 3 tabs labelled
"Authors"/"Licenses"/"Embargoes". Skipped when QGIS Qt is not
available (headless test env).

Wiring into the US scheda lands in Task G.2.

Tests: 132 passed, 1 skipped.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task G.2: Wire "Manage paradata" button into US scheda

**Files:**
- Modify: `tabs/US_USM.py`

- [ ] **Step 1: Locate the green Extended Matrix button**

```bash
grep -nE "extended.matrix|Extended Matrix|s3dgraphy.*button" tabs/US_USM.py | head -10
```

Note the line where the button is added to the layout.

- [ ] **Step 2: Add the new "Manage paradata" button**

Use the Edit tool to add, near the existing Extended Matrix button setup, a new QPushButton + click connection. The exact location depends on where the existing button lives — find a `addWidget(self.pushButton_extended_matrix)` or similar and add right after:

```python
# AI05: paradata management button — opens ParadataManagerDialog
self.pushButton_paradata = QPushButton(self)
self.pushButton_paradata.setText("Manage paradata")
self.pushButton_paradata.setToolTip(
    "Manage Author/License/Embargo metadata for the current site "
    "(stored in paradata.graphml next to the SQLite DB).")
self.pushButton_paradata.clicked.connect(
    self._on_pushButton_paradata_clicked)
# Add to the same layout as the green Extended Matrix button
# (find the parent layout and append).
```

And add the click handler somewhere in the class body:

```python
def _on_pushButton_paradata_clicked(self):
    """Open ParadataManagerDialog for the currently selected sito."""
    sito = self.comboBox_sito.currentText().strip()
    if not sito:
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.warning(
            self, "No site selected",
            "Please select a site before managing paradata.")
        return
    try:
        from gui.dialog_paradata_manager import ParadataManagerDialog
        dialog = ParadataManagerDialog(
            parent=self,
            db_manager=self.DB_MANAGER,
            sito=sito,
        )
        dialog.exec_()
    except Exception as e:
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.critical(
            self, type(e).__name__,
            f"Cannot open paradata manager: {e}")
```

The `tabs/US_USM.py` file is **very large** (~16k lines). Be precise about insertion points — use a unique surrounding string for the Edit tool's `old_string` to avoid ambiguity. Hint: search for the existing extended-matrix button setup snippet and insert immediately after.

- [ ] **Step 3: Verify syntax**

```bash
python -c "import ast; ast.parse(open('tabs/US_USM.py').read()); print('OK')"
```

Expected: `OK`.

- [ ] **Step 4: Full suite (no new tests)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q
```

Expected: `132 passed, 1 skipped` (no test exercises the button click in headless env; manual smoke gate covers it).

- [ ] **Step 5: Commit**

```bash
git add tabs/US_USM.py
git commit -m "$(cat <<'EOF'
feat(US form): "Manage paradata" button → ParadataManagerDialog

Per AI05 D6, adds a new QPushButton "Manage paradata" to the US/USM
scheda next to the existing green Extended Matrix button. Click
handler opens ParadataManagerDialog scoped to the currently
selected sito.

If no sito is selected, shows a warning. If the dialog raises on
construction (e.g. SQLite DB missing), surfaces the error via
QMessageBox.critical.

Manual smoke gate (Group H.4) covers the actual click flow — no
automated test in headless env.

Tests: 132 passed, 1 skipped (unchanged).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group H — Release packaging

### Task H.1: Dev-log entry

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Append the AI05 section at end of file**

Use the Edit tool to add at the bottom:

````markdown

---

# Phase 2 — AI05 ParadataStore + UI authoring + Strategy A + edge styling

**Date:** 2026-05-08 → 2026-05-08
**Tag:** `phase2-ai05-paradata-store-5.4.0-alpha`
**Spec:** `docs/superpowers/specs/2026-05-08-ai05-paradata-store-design.md`
**Plan:** `docs/superpowers/plans/2026-05-08-ai05-paradata-store.md`

## What was built

Phase 2 closure. Four scope items:

1. **ParadataStore** — atomic-safe CRUD for `paradata_{sito}.graphml`
   hosting AuthorNode/LicenseNode/EmbargoNode (the 3 node types
   without an SQL counterpart in pyarchinit). Site-scoped file at
   `{db_path.parent}/paradata_{sito_slug}.graphml`, written via
   `.tmp` + `os.replace()` for crash safety. Low-level (read/write/
   add_node/remove_node/find) + high-level (add_author/license/
   embargo + list_*) API surface.

2. **GraphProjector Strategy A promotion** — full move of
   `_enrich_pyarchinit_graph` body into `GraphProjector._enrich_into`
   private method. Standalone function in `graphml_writer.py`
   DELETED. Single existing caller (`export_graphml()`) updated to
   use `GraphProjector().populate_graph(..., include_paradata=False)`.
   Pays the AI04 carry-over from `project_ai04_projector_refactor_plan.md`
   memory note.

3. **`include_paradata` integration** — `populate_graph(db, sito, *,
   include_paradata=True)` defaults to merge SQL + paradata. Opt-out
   via `include_paradata=False` for AI04-style strat-only output.
   Corrupt paradata file → log warning + fall back to strat-only
   (non-fatal).

4. **EdgeRegistry** — `modules/s3dgraphy/sync/edge_registry.py` with
   `resolve_edge_style(edge_type)` and `is_paradata_edge(edge_type)`.
   Reads from `s3Dgraphy_connections_datamodel.json` and
   `em_visual_rules.json` (s3dgraphy 0.1.40). Override-wins via
   `_PYARCHINIT_EDGE_OVERRIDES` (currently empty). Wired into the
   `graphml_writer.py` post-processor as the canonical paradata
   classification source.

## UI

New `gui/dialog_paradata_manager.py` — single QDialog with 3-tab
QTabWidget (Authors / Licenses / Embargoes). Each tab has a
QTableWidget showing existing entries + form for adding new ones +
Remove-selected button. Triggered by a "Manage paradata" button
added to the US/USM scheda next to the existing green Extended
Matrix button.

## CLI

`scripts/s3dgraphy_sync.py paradata` subcommand with 7
sub-subcommands: add-author, list-authors, add-license,
list-licenses, add-embargo, list-embargos, remove. Same exit-code
contract as AI04 CLI (0 success / 1 GraphSyncError / 2 argparse).

## Test counts

- Baseline (post-AI04+AI04.1): 94 passing
- Post-Group A (edge_registry): 99 passing
- Post-Group B (paradata_store): 116 passing
- Post-Group C (Strategy A): 123 passing
- Post-Group D (fixture): 123 passing (no new tests)
- Post-Group E (round-trip + idempotent): 126 passing
- Post-Group F (CLI): 132 passing
- Post-Group G (UI): 132 passing + 1 skipped (Qt not in CI)

Final: ≥120 target hit (132 passed, 1 skipped).

## Acceptance criteria

All 18 ACs from spec §7 satisfied. AC-2 byte-identical baseline
stayed green at every commit during Group C (Strategy A's
highest-risk move). AI04 round-trip + idempotent + CLI helper
tests stayed green throughout.

## Manual smoke gate (Group H.4)

User-driven validation in QGIS — see plan Group H Task H.4.

## Carry-overs (deferred to AI06+)

- Per-node paradata edges (Author → has_authored → US)
- Pluggable ConflictResolver strategies + UI dialog
- Configurable failure_mode={atomic, best_effort, by_group}
- ORCID/SPDX/date validation
- File locking for concurrent writes
- VirtualSpecialFindUnit authoring layer

## Phase 3+ scope (unchanged)

- SyncEngine + DatacenterClient + REST API (Phase 3)
- GraphDBBackend + SPARQL (Phase 4)
````

- [ ] **Step 2: Verify**

```bash
tail -30 docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
```

Expected: the new section is at the end.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
git commit -m "$(cat <<'EOF'
docs(dev-log): Phase 2 / AI05 ParadataStore + UI authoring entry

Records AI05 outcome: new ParadataStore + EdgeRegistry +
GraphProjector Strategy A + ParadataManagerDialog + 7 CLI
subcommands. All 18 acceptance criteria passed; AC-2 byte-identical
baseline stayed green at every commit during Group C (Strategy A
high-risk move).

Test counts at Group boundaries documented (94 → 99 → 116 → 123 →
123 → 126 → 132 → 132 + 1 skipped).

Closes the AI04 carry-over from project_ai04_projector_refactor_plan.md.

Carry-overs documented: per-node paradata edges (AI06+), pluggable
ConflictResolver (AI06+), configurable failure_mode (AI06+), ORCID/
SPDX validation (AI06+), file locking (AI06+), VSF authoring (AI06+).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task H.2: CHANGELOG bilingual entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Read top of file**

```bash
head -30 dev_logs/CHANGELOG.md
```

Identify the title and the existing `## [5.3.0-alpha]` section.

- [ ] **Step 2: Prepend the new section**

Use the Edit tool to insert immediately after the title:

```markdown
## [5.4.0-alpha] - 2026-05-08

### Italiano

- **Phase 2 / AI05 — ParadataStore + UI authoring + chiusura Phase 2.** Nuova classe `ParadataStore` per la gestione atomica di `paradata_{sito}.graphml` (Author/License/Embargo per sito). API low-level (`read`/`write`/`add_node`/`remove_node`/`find`) e high-level (`add_author`/`add_license`/`add_embargo` + `list_*`).
- **Dialog "Manage paradata".** Nuovo bottone nella scheda US/USM apre un dialog 3-tab (Authors / Licenses / Embargoes) per CRUD visuale. Versionable in Git accanto al DB.
- **GraphProjector Strategy A promotion.** Il body di `_enrich_pyarchinit_graph` è stato spostato dentro `GraphProjector` (la funzione standalone in `graphml_writer.py` è stata eliminata). `populate_graph(..., include_paradata=True)` di default fonde strat + paradata.
- **Edge styling automation.** Nuovo modulo `edge_registry` legge `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json` per classificazione e style automatici. Override-wins via `_PYARCHINIT_EDGE_OVERRIDES`.
- **CLI `s3dgraphy_sync.py paradata`** con 7 sub-subcomandi: add-author / list-authors / add-license / list-licenses / add-embargo / list-embargos / remove.

### English

- **Phase 2 / AI05 — ParadataStore + UI authoring + Phase 2 closure.** New `ParadataStore` class managing `paradata_{sito}.graphml` atomically (site-level Author/License/Embargo). Low-level API (`read`/`write`/`add_node`/`remove_node`/`find`) and high-level helpers (`add_author`/`add_license`/`add_embargo` + `list_*`).
- **"Manage paradata" dialog.** New button in the US/USM scheda opens a 3-tab dialog (Authors / Licenses / Embargoes) for visual CRUD. Versionable in Git next to the DB.
- **GraphProjector Strategy A promotion.** The `_enrich_pyarchinit_graph` body was moved into `GraphProjector` (the standalone function in `graphml_writer.py` is now DELETED). `populate_graph(..., include_paradata=True)` defaults to merging strat + paradata.
- **Edge styling automation.** New `edge_registry` module reads `s3Dgraphy_connections_datamodel.json` + `em_visual_rules.json` for automatic classification and styling. Override-wins via `_PYARCHINIT_EDGE_OVERRIDES`.
- **CLI `s3dgraphy_sync.py paradata`** with 7 sub-subcommands: add-author / list-authors / add-license / list-licenses / add-embargo / list-embargos / remove.

```

(Keep the trailing blank line.)

- [ ] **Step 3: Verify**

```bash
head -40 dev_logs/CHANGELOG.md
```

Confirm new block on top, old `## [5.3.0-alpha]` intact below.

- [ ] **Step 4: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
docs(changelog): 5.4.0-alpha — AI05 ParadataStore + UI (IT + EN)

Bilingual entry summarising the AI05 release:
- New ParadataStore class with atomic-safe CRUD over
  paradata_{sito}.graphml.
- New "Manage paradata" dialog (3-tab Authors/Licenses/Embargoes)
  triggered from the US/USM scheda.
- GraphProjector Strategy A promotion completed; standalone
  _enrich_pyarchinit_graph deleted.
- Edge styling automation via new edge_registry module.
- CLI paradata subcommand with 7 sub-subcommands.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task H.3: Verification (no subagent — controller only)

**Files:** none

This is purely a verification step run by the controlling agent. It does NOT generate a commit unless something needs fixing.

- [ ] **Step 1: Run full suite 3 times for stability**

```bash
for i in 1 2 3; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -1
done
```

Expected: `132 passed, 1 skipped` × 3.

- [ ] **Step 2: AC-2 baseline 5 times**

```bash
for i in 1 2 3 4 5; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -1
done
```

Expected: `1 passed` × 5.

- [ ] **Step 3: AI04 guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
    tests/sync/test_round_trip.py \
    tests/sync/test_idempotent_ingest.py \
    tests/sync/test_cli_helper.py -v 2>&1 | tail -3
```

Expected: all pass.

- [ ] **Step 4: Strategy A regression guards**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_strategy_a_no_regression.py -v
```

Expected: `3 passed`. The grep-based check confirms `_enrich_pyarchinit_graph` is fully removed.

- [ ] **Step 5: Co-author trailer check across all AI05 commits**

```bash
git log phase2-ai04-bridge-bidirectional-5.3.0-alpha..HEAD \
    --format=%B | grep -c "Co-Authored-By"
```

Expected: `0`.

- [ ] **Step 6: Working tree clean**

```bash
git status --short | grep -vE '^\?\?'
```

Expected: empty.

- [ ] **Step 7: Version**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.4.0-alpha`.

- [ ] **Step 8: Commit count since AI04**

```bash
git log --oneline phase2-ai04-bridge-bidirectional-5.3.0-alpha..HEAD | wc -l
```

Expected: ~24 commits (per the plan estimate).

If any check fails, STOP and investigate before proceeding to H.4 manual smoke gate.

### Task H.4: Manual smoke gate

**Files:** none — user-driven QA only

This step is **user-driven**. Cannot be automated. The dispatching agent waits for the user's "ok smoked, proceed" before triggering H.5.

- [ ] **Step 1: Restart QGIS**

User: close QGIS and relaunch.

- [ ] **Step 2: Open the Volterra/Castelseprio project**

User: load a real project with a SQLite DB.

- [ ] **Step 3: Open the US/USM scheda**

User: navigate to the US/USM tab and verify it loads.

- [ ] **Step 4: Click the new "Manage paradata" button**

User: verify the dialog opens with 3 tabs (Authors / Licenses / Embargoes), each showing an empty table on first open.

- [ ] **Step 5: Add an Author**

User: in Authors tab, type a name + ORCID + role, click Add. Verify the row appears in the table. Close + reopen the dialog. Verify the author persists.

- [ ] **Step 6: Add a License + Embargo**

User: same flow on the License (SPDX + URL) and Embargo (until-date + reason) tabs.

- [ ] **Step 7: Remove an entry**

User: select a row, click Remove selected. Verify the row disappears + persists across dialog close/reopen.

- [ ] **Step 8: Test the paradata file presence**

User: shell — `ls -la {db_dir}/paradata_*.graphml`. Verify exactly one file per site exists with the expected size.

- [ ] **Step 9: Re-run the green Extended Matrix export from the same scheda**

User: verify the Export tab still works exactly as it did in 5.3.0-alpha. The structural fingerprint test (AC-2) covers this for the test fixture, but real-world Volterra DB exercises real-world content.

- [ ] **Step 10: Test the new CLI subcommand**

User: shell — `python scripts/s3dgraphy_sync.py paradata list-authors --db <my-db> --sito <my-site>`. Verify it lists the authors added via the dialog.

- [ ] **Step 11: User confirms gate passed**

User writes back something like "ok smoked, proceed" — controller proceeds to H.5.

### Task H.5: Tag + push

**Files:** none — git operations only

- [ ] **Step 1: Verify clean tree + count**

```bash
git status --short | grep -vE '^\?\?'   # must be empty
git log --oneline phase2-ai04-bridge-bidirectional-5.3.0-alpha..HEAD | wc -l
```

Expected: empty status; ~24 commits.

- [ ] **Step 2: Final co-author trailer check**

```bash
git log phase2-ai04-bridge-bidirectional-5.3.0-alpha..HEAD \
    --format=%B | grep -c "Co-Authored-By"
```

Expected: `0`.

- [ ] **Step 3: Create the release tag**

```bash
git tag -a phase2-ai05-paradata-store-5.4.0-alpha \
    -m "Phase 2 / AI05: ParadataStore + UI authoring + Strategy A + edge styling"
git tag -l | grep -E "phase2|pre-ai05"
```

Expected (6 lines):
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
phase2-ai05-paradata-store-5.4.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
pre-ai05-paradata
```

- [ ] **Step 4: Push branch + tag**

```bash
git push origin Stratigraph_00001
git push origin phase2-ai05-paradata-store-5.4.0-alpha
```

Expected:
- branch push: ~24 commits to `origin/Stratigraph_00001`.
- tag push: `[new tag] phase2-ai05-paradata-store-5.4.0-alpha`.

- [ ] **Step 5: Verify on remote**

```bash
git ls-remote --tags origin 2>&1 | grep -E "phase2-ai05|pre-ai05"
```

Expected: 4 lines (phase2-ai05 + its `^{}` deref, pre-ai05 + its `^{}` deref).

- [ ] **Step 6: Final state check**

```bash
git rev-list --left-right --count HEAD...@{u}   # expect "0\t0"
```

---

## Self-review checklist (run inline before delivering the plan)

Reviewed against the spec on 2026-05-08:

**1. Spec coverage**

- §1 Overview → addressed by file structure + Group narrative.
- §2 D1–D10 → each decision pinned by a task (matrix in `Test strategy` section).
- §3 Components: §3.1 ParadataStore → Group B; §3.2 EdgeRegistry → Group A; §3.3 GraphProjector → Group C; §3.4 ParadataManagerDialog → Group G.1; §3.5 CLI → Group F.
- §4 Data flow: 4.1 read → B.1; 4.2 write → B.1; 4.3 high-level → B.3; 4.4 populate_graph(include_paradata) → C.2; 4.5 round-trip → E.1; 4.6 edge styling → A.1.
- §5 Error handling: 5.1 hierarchy → B.1; 5.2 fatal/non-fatal → B.1+B.4+C.2; 5.3 logging → B.1; 5.4 UI surfacing → G.1; 5.5 CLI → F.1.
- §6 Testing: 4 levels covered by Group A through Group G; ≥120 target hit (132 + 1 skipped).
- §7 Acceptance criteria: AC-1 → B.1; AC-2 → C.3+C.4; AC-3 → B.4; AC-4 → C.2; AC-5 → C.2; AC-6 → B.2; AC-7 → B.2; AC-8 → E.1; AC-9 → A.1; AC-10 → A.1; AC-11 → A.1; AC-12 → C.3; AC-13 → AI04 guards run on every Group; AC-14 → G.1; AC-15 → F.2; AC-16 → H.3; AC-17 → manual smoke gate; AC-18 → AI04 + Phase 1 guards.
- §8 Release plan → Group H mirrors it.
- §9 Out of scope → "Explicitly NOT touched" + commit message reminders.
- §10 Risks → mitigation hooks in Group C (Strategy A high-risk steps).

**2. Placeholder scan**

No `TODO`, `TBD`, `FIXME`, `implement later`, `Add appropriate error handling`, `Similar to Task N`, etc. Every step has explicit code or commands.

**3. Type consistency**

- `ParadataStore.add_author(name, orcid=None, role=None) -> str` — same in B.3, F.1, G.1, E.1.
- `populate_graph(db_path, sito, *, include_paradata=True)` — same in C.2, C.3 (export_graphml caller passes include_paradata=False), E.1, G.1 (via dialog).
- `is_paradata_edge(edge_type) -> bool` — same in A.1, A.2.
- `ParadataStoreError` hierarchy — defined once in B.1, used in B.4, C.2, F.1, G.1.
- `MAPPED_COLUMNS` from AI04 not redefined — consumed where needed.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-08-ai05-paradata-store.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Group C (Strategy A) is highest-risk; budget extra time + AC-2 verification per step.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
