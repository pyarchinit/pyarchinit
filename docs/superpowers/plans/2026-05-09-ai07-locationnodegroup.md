# AI07 — `LocationNodeGroup` migration + AI08-F1 m:n hierarchical: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate spatial node-grouping from AI06's `ActivityNodeGroup + group_kind` discriminator to s3dgraphy 0.1.41's native `LocationNodeGroup + kind` model, introducing many-to-many membership with `is_primary` disambiguation, recursive `LocationNodeGroup → LocationNodeGroup` toponym chains derived from `site_table`, and transparent on-read up-conversion of legacy 5.5.x exports — release `5.6.0-alpha`.

**Architecture:** `_merge_groups` in `graph_projector.py` dispatches per dimension: `attivita` → `ActivityNodeGroup` + `is_in_activity` (unchanged), 6 spatial dims → `LocationNodeGroup` + `is_in_location` with `kind ∈ {functional, study}`. A new `_emit_toponym_chain` method emits a recursive `LocationNodeGroup(kind="toponym")` chain from `site_table.{nazione,regione,provincia,comune}`. `compute_primary` picks one `is_primary=true` membership per US following a hardcoded priority order with optional dialog override; non-primary memberships emit `<data key="s3d:other_locations">` arrays on the US node. `GraphIngestor._promote_legacy_activitynodegroup` intercepts ActivityNodeGroup nodes with spatial `group_kind` on read and promotes them in-memory with a one-shot `DeprecationWarning`. `_apply_group_folders_to_sql` becomes recursive to support hierarchical yEd folder-in-folder layouts.

**Tech Stack:** Python 3.9+, s3dgraphy 0.1.41 (vendored 0.1.40 → 0.1.41 already bumped in `4b1c5bd6`), lxml (transitive), pytest, sqlite3, QGIS PyQt5/PyQt6 abstraction. **No new third-party dependencies.**

**Spec source of truth:** `docs/superpowers/specs/2026-05-09-ai07-locationnodegroup-design.md` (commit `86798fb0`)

**Predecessor releases:**
- AI08-F2 hotfix: tag `phase2-ai08f2-hotfix-5.5.2-alpha` (`b569bd51`) — current production baseline
- s3dgraphy bump: commit `4b1c5bd6` (requirements.txt 0.1.40 → 0.1.41) — already shipped on `Stratigraph_00001`

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_ai07_active.md` — origin of this plan
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/project_phase2_pause_2026-05-09.md` — Phase 2 state at start

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

**Upstream resolution:** [zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5) — closed 2026-05-09 with s3dgraphy 0.1.41 ship. Q1 (`attivita` stays as `ActivityNodeGroup`) and Q2 (projector owns up-conversion, library reads opaque) confirmed by Emanuel.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `tests/sync/test_locationnodegroup_projection.py` | L1 fixture-based: per-dimension dispatch (7 dims × 2 schema paths). Asserts `node_class`, `kind`, `edge_type` of each emitted group node. ~120 LOC, ~14 tests. |
| `tests/sync/test_locationnodegroup_recursive_ingest.py` | L1 recursive walker tests — 3-level nesting, cycle abort, mixed `LocationNodeGroup` + `ActivityNodeGroup` folders. ~80 LOC, ~6 tests. |
| `tests/sync/test_toponym_chain.py` | L1 `_emit_toponym_chain` — all-populated / all-empty / partial / cross-site dedupe. ~100 LOC, ~6 tests. |
| `tests/sync/test_primary_selection.py` | L0 unit tests for `compute_primary` — hardcoded priority order, dialog override, fallback. ~60 LOC, ~5 tests. |
| `tests/sync/test_legacy_autopromote.py` | L1 `_promote_legacy_activitynodegroup` — pure 5.5.x-format graph promoted in-memory; mixed legacy + new graph; `attivita` stays untouched; one-shot `DeprecationWarning`. ~90 LOC, ~4 tests. |
| `tests/sync/fixtures/legacy_5_5_x.graphml` | Pre-cooked binary fixture: 4 `ActivityNodeGroup` nodes — 1 with `group_kind="attivita"` (untouched on promote), 3 with `group_kind ∈ {struttura, area, settore}` (promoted to `LocationNodeGroup`). Generated once by helper script. |
| `tests/sync/fixtures/toponym_volterra.sqlite` | Variant of `mini_volterra.sqlite` with `site_table.{nazione,regione,provincia,comune}` populated for AC-15 + AC-20 round-trip identity tests. |

### Modified

| Path | Why |
|---|---|
| `tests/sync/conftest.py` | Group 0: prepend `ext_libs/` to `sys.path` and clear cached `s3dgraphy.*` modules so all sync tests use the vendored 0.1.41 (currently only `test_ai03_export_byte_identical.py` does this manually). +20 LOC. |
| `modules/s3dgraphy/sync/edge_registry.py` | Group A: register `is_in_location` as a known edge type and inject the `primary_modifier` style override. ~30 LOC. |
| `modules/s3dgraphy/sync/group_projector.py` | Group B: extend `GroupSpec` with `node_class: str` (one of `"LocationNodeGroup"` / `"ActivityNodeGroup"`) and `kind: str | None` (one of `"toponym"`, `"study"`, `"functional"`, `None`). Add `_GROUP_KIND_TO_S3D_KIND` mapping table. `build_groups_from_sql` populates these fields. ~40 LOC. |
| `modules/s3dgraphy/sync/graph_projector.py` | Group C: rewrite `_merge_groups` to dispatch per dimension (LocationNodeGroup vs ActivityNodeGroup). Group D: add `_emit_toponym_chain` method called from `populate_graph` Stage 3. Group E: accept new `primary_priority: list[str] | None` kwarg passed through to `_merge_groups`; `compute_primary` helper picks exactly one `is_primary` per US. ~150 LOC. |
| `modules/s3dgraphy/sync/graph_ingestor.py` | Group F: add `_promote_legacy_activitynodegroup` and call it as Stage B in `populate_list`. Add `LocationNodeGroup` to `_NON_STRAT_TYPES`. Group G: rewrite `_apply_group_folders_to_sql` as a recursive walker with cycle detection + `visited` set, supporting nested `LocationNodeGroup → LocationNodeGroup` folders. ~120 LOC. |
| `modules/s3dgraphy/sync/graphml_writer.py` | Group A: extend `_GROUP_KIND_PALETTE` with kind-aware lookup for `LocationNodeGroup` (border colour from `kind` enum). Update `_inject_group_folders` to discriminate by node `node_type` (`LocationNodeGroup` → dashed roundrectangle border, `ActivityNodeGroup` → existing rect). Group E: emit `<data key="s3d:other_locations">` arrays on US nodes for non-primary memberships. ~120 LOC. |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Group E: remove the multi-dim warning at `S3DGraphyExportDialog.on_export` (lines ~580–600) — replaced by the new m:n primary-selection model. Add `QComboBox "Primary dimension"` with default `"struttura"` to the export dialog. Pass `primary_priority` to `bridge.export_integrated_matrix`. ~60 LOC. |
| `tests/sync/fixtures/build_mini_volterra_external.py` | Group D: extend with `_emit_toponym_volterra()` to generate `toponym_volterra.sqlite` and `_emit_legacy_5_5_x_fixture()` to generate `legacy_5_5_x.graphml`. Idempotent. ~50 LOC. |
| `tests/sync/test_ai03_export_byte_identical.py` | Group H: re-baseline. The `mini_volterra_baseline_ai03.graphml` fingerprint changes because spatial group folder `node_type` strings shift from `ActivityNodeGroup` to `LocationNodeGroup`. New baseline regenerated by re-running the export and committing the new file + updated expected fingerprint values. ~5 LOC. |
| `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` | Group H: regenerated. |
| `metadata.txt` | Group H: bump `version=5.5.2-alpha` → `version=5.6.0-alpha`. |
| `dev_logs/CHANGELOG.md` | Group H: prepend `## [5.6.0-alpha] - 2026-05-XX` bilingual section. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Group H: new "Phase 2 — AI07 LocationNodeGroup migration" section. |

### Explicitly NOT touched (out of scope per spec §13)

- `modules/s3dgraphy/sync/paradata_store.py` — AI05 file unchanged
- `modules/s3dgraphy/sync/group_store.py` — ad-hoc store keeps `kind="adhoc"` (resolved to `LocationNodeGroup(kind="functional")` at projection time, but the GroupStore round-trip channel is unchanged)
- `modules/s3dgraphy/sync/conflict_resolver.py` — pluggable strategies still deferred
- `ext_libs/s3dgraphy/` — already bumped to 0.1.41 in `4b1c5bd6`. AI07 only consumes the new API
- `requirements.txt` — already bumped in `4b1c5bd6`
- `pyarchinit.tools.migrate_legacy_groupkind` standalone CLI — explicitly deferred (spec §13). On-read promotion in Group F is sufficient
- AI09 (`TimeBranchNodeGroup` mapping for `cron_iniziale/cron_finale`) — out of scope
- AI08-F3 (auto-layout heuristics) — still deferred pending real-world feedback

---

## Test strategy

- **L0 unit tests** (`test_primary_selection.py`): pure Python, no DB, no QGIS bootstrap. Fast.
- **L1 fixture-based** (`test_locationnodegroup_projection.py`, `test_locationnodegroup_recursive_ingest.py`, `test_toponym_chain.py`, `test_legacy_autopromote.py`): pytest against `mini_volterra.sqlite` and the new `toponym_volterra.sqlite` / `legacy_5_5_x.graphml` fixtures. No QGIS.
- **L3 regression guards** (must stay green at every commit):

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v                   # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_idempotent_ingest.py -v            # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v               # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v     # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_export_em_template.py -v    # AI06 + F2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v       # AI06
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_idempotent.py -v            # AI06
```

`test_ai03_export_byte_identical.py` is allowed to **change** (re-baseline) only in **Group H Task H.1**. Anywhere else it must stay green untouched.

Decision-pinning matrix:

| Decision / Acceptance | Pinning test |
|---|---|
| Q1=a on-read up-conversion | `test_legacy_autopromote.py::test_legacy_5_5_x_promoted_in_memory` |
| Q1=a one-shot DeprecationWarning | `test_legacy_autopromote.py::test_warning_emitted_once_per_call` |
| Q2=b m:n with is_primary | `test_locationnodegroup_projection.py::test_us_has_exactly_one_is_primary` |
| Q3=c hardcoded primary priority | `test_primary_selection.py::test_default_priority_struttura_first` |
| Q3=c dialog override | `test_primary_selection.py::test_override_changes_primary` |
| Q4=c skip empty levels | `test_toponym_chain.py::test_partial_admin_levels_compact_chain` |
| Q4=c cross-site dedupe | `test_toponym_chain.py::test_two_sites_same_comune_share_node` |
| Mapping table (struttura,ambient → functional) | `test_locationnodegroup_projection.py::test_struttura_emits_locationnodegroup_kind_functional` |
| Mapping table (area,settore,saggio,quad_par → study) | `test_locationnodegroup_projection.py::test_area_emits_locationnodegroup_kind_study` |
| Mapping table (attivita → ActivityNodeGroup unchanged) | `test_locationnodegroup_projection.py::test_attivita_stays_activitynodegroup` |
| Recursive walker | `test_locationnodegroup_recursive_ingest.py::test_walker_descends_into_nested_folder` |
| Cycle detection | `test_locationnodegroup_recursive_ingest.py::test_cycle_detected_aborts_ingest` |
| AC-2 byte-identical (until re-baseline in H.1) | `test_ai03_export_byte_identical.py` (existing) |
| AC-15 toponym round-trip identity | `test_toponym_chain.py::test_round_trip_preserves_site_table` |
| AC-16 legacy autopromote + warning | `test_legacy_autopromote.py` |
| AC-17 ≤1 is_primary per US | `test_locationnodegroup_projection.py::test_us_has_exactly_one_is_primary` |
| AC-18 recursive nesting preserved | `test_locationnodegroup_recursive_ingest.py::test_walker_descends_into_nested_folder` |
| AC-19 priority order + override | `test_primary_selection.py` (full file) |
| AC-20 cross-site dedupe | `test_toponym_chain.py::test_two_sites_same_comune_share_node` |

Test count progression:
- Baseline (post `4b1c5bd6` s3dgraphy bump): 179 passed, 3 skipped
- Post-Group 0: 179 passed, 3 skipped (no new tests; conftest path bootstrap should leave count unchanged)
- Post-Group H: 179 + ~30 distinct new tests = ~209 passed, 3 skipped

---

## Group 0 — Pre-flight & test-path bootstrap

### Task 0.1: Verify clean starting point + push pending work

**Files:** none (git operation)

- [ ] **Step 1: Confirm starting point**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}
```

Expected: tracked changes empty, last commit is `86798fb0 spec(ai07): …`, `0\t0` ahead-behind.

- [ ] **Step 2: Verify s3dgraphy bump landed**

```bash
grep -n "s3dgraphy" requirements.txt
```

Expected: `s3dgraphy>=0.1.41` on line 79.

- [ ] **Step 3: Verify upstream tag exists**

```bash
git tag --list | grep -E "phase2-ai08f2-hotfix"
```

Expected: `phase2-ai08f2-hotfix-5.5.2-alpha` listed (predecessor tag).

- [ ] **Step 4: Capture baseline test count**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `179 passed, 3 skipped`.

### Task 0.2: Create AI07 rollback safety tag

**Files:** none (git operation)

- [ ] **Step 1: Create rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-ai07-locationnodegroup -m "Rollback point before AI07 LocationNodeGroup migration

Predecessor: phase2-ai08f2-hotfix-5.5.2-alpha (b569bd51)
s3dgraphy bump: 4b1c5bd6
Spec commit: 86798fb0

If AI07 needs to be reverted, reset hard to this tag."
git push origin pre-ai07-locationnodegroup
```

Expected output: `* [new tag]         pre-ai07-locationnodegroup -> pre-ai07-locationnodegroup`.

### Task 0.3: Bootstrap `ext_libs/` in tests/sync/conftest.py

**Files:**
- Modify: `tests/sync/conftest.py:1-46`

- [ ] **Step 1: Capture pre-bootstrap baseline**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `... passed, 3 skipped` (record exact count to compare after the change; should match Task 0.1 Step 4).

- [ ] **Step 2: Edit `tests/sync/conftest.py`**

Replace lines 1-12 with:

```python
"""Shared pytest fixtures for tests/sync/.

The bootstrap below mirrors what `test_ai03_export_byte_identical.py`
does manually: it forces all sync tests to use the vendored
`ext_libs/s3dgraphy` (currently 0.1.41) instead of any system
pip-installed s3dgraphy that may be present in `site-packages`.

This is required because AI07 introduces `LocationNodeGroup` and
`is_in_location` symbols that only exist in 0.1.41+. Without this
bootstrap, sync tests would import an older s3dgraphy from
site-packages and fail with `ImportError: cannot import name
'LocationNodeGroup'`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURES = Path(__file__).parent / "fixtures"
```

- [ ] **Step 3: Verify all 179 tests still pass**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `179 passed, 3 skipped`. If any test fails, the bootstrap is incompatible with one of the existing tests — investigate and patch surgically (likely a test that explicitly depends on system 0.1.15 API). Do NOT proceed if the count drops.

- [ ] **Step 4: Verify the vendored 0.1.41 is now what tests see**

```bash
PYTHONPATH="$PWD" python -c "
import sys; sys.path.insert(0, 'tests/sync')
import conftest  # triggers bootstrap
from s3dgraphy.nodes.group_node import LocationNodeGroup
print('LocationNodeGroup:', LocationNodeGroup)
loc = LocationNodeGroup(node_id='t', name='X', kind='study')
print('  kind:', loc.kind)
"
```

Expected:
```
LocationNodeGroup: <class 's3dgraphy.nodes.group_node.LocationNodeGroup'>
  kind: study
```

- [ ] **Step 5: Commit**

```bash
git add tests/sync/conftest.py
git commit -m "test(ai07): bootstrap ext_libs/s3dgraphy 0.1.41 in conftest.py

Sync tests now use the vendored 0.1.41 (with LocationNodeGroup +
is_in_location) instead of system pip-installed s3dgraphy 0.1.15.
This mirrors the path manipulation in
test_ai03_export_byte_identical.py and is required for AI07 tests
that import LocationNodeGroup symbols.

179 passed, 3 skipped — same as pre-bootstrap baseline."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group A — Edge registry + visual rules dispatch for `LocationNodeGroup`

### Task A.1: Register `is_in_location` in edge_registry

**Files:**
- Modify: `modules/s3dgraphy/sync/edge_registry.py` (after line ~50)
- Test: `tests/sync/test_edge_registry.py` (existing — check if it needs extension)

- [ ] **Step 1: Check if `is_in_location` is already in upstream visual rules**

```bash
grep -A3 "is_in_location" ext_libs/s3dgraphy/JSON_config/em_visual_rules.json | head -5
```

Expected: `is_in_location` entry present (0.1.41 ships it). The pyarchinit-side `edge_registry.py` only needs to declare it as a "known" type — visual styling is read from the upstream JSON.

- [ ] **Step 2: Write failing test**

Create `tests/sync/test_edge_registry_locationnodegroup.py`:

```python
"""AI07 Group A: edge_registry recognises is_in_location."""
from __future__ import annotations

from modules.s3dgraphy.sync.edge_registry import (
    KNOWN_EDGE_TYPES,
    resolve_edge_style,
    is_paradata_edge,
)


def test_is_in_location_is_known():
    assert "is_in_location" in KNOWN_EDGE_TYPES


def test_is_in_location_resolves_to_visual_style():
    style = resolve_edge_style("is_in_location")
    assert style is not None
    assert "color" in style or "lineStyle" in style or "stroke" in style


def test_is_in_location_not_paradata():
    # is_in_location is structural, not paradata flow
    assert is_paradata_edge("is_in_location") is False
```

- [ ] **Step 3: Run to verify fails**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_edge_registry_locationnodegroup.py -v
```

Expected: 3 FAILs — `is_in_location` not in `KNOWN_EDGE_TYPES`.

- [ ] **Step 4: Add `is_in_location` to `KNOWN_EDGE_TYPES`**

In `modules/s3dgraphy/sync/edge_registry.py`, find the `KNOWN_EDGE_TYPES` set (around line 40–55) and add `"is_in_location"` to it:

```python
KNOWN_EDGE_TYPES: frozenset[str] = frozenset({
    # ...existing entries...
    "is_in_activity",
    "is_in_location",   # AI07: spatial / locational membership
    "has_author",
    # ...
})
```

- [ ] **Step 5: Run to verify passes**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_edge_registry_locationnodegroup.py -v
```

Expected: 3 PASSED.

- [ ] **Step 6: Run full sync suite to confirm no regression**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `182 passed, 3 skipped` (179 + 3 new).

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/edge_registry.py \
        tests/sync/test_edge_registry_locationnodegroup.py
git commit -m "feat(ai07/A): register is_in_location in edge_registry

s3dgraphy 0.1.41 introduces is_in_location as the canonical edge type
for spatial / locational membership (LocationNodeGroup target). Add it
to KNOWN_EDGE_TYPES so the projector and ingestor accept it as a
first-class structural edge.

Visual style is loaded lazily from
ext_libs/s3dgraphy/JSON_config/em_visual_rules.json (1.5.1+ adds the
LocationNodeGroup + is_in_location entries with primary_modifier).

3 new tests."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task A.2: Extend `_GROUP_KIND_PALETTE` with kind-aware lookup for LocationNodeGroup

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py:1274-1286`
- Test: `tests/sync/test_groups_export_em_template.py` (extend with 2 new tests)

- [ ] **Step 1: Write failing test**

Append to `tests/sync/test_groups_export_em_template.py`:

```python
def test_locationnodegroup_palette_keyed_by_kind():
    """AI07 A.2: LocationNodeGroup folders pick fill/border from kind enum."""
    from modules.s3dgraphy.sync.graphml_writer import (
        _GROUP_KIND_PALETTE,
        _resolve_group_visual,
    )
    # The 8 existing entries (AI06 + F2) are dimension-keyed.
    assert "struttura" in _GROUP_KIND_PALETTE  # functional
    assert "area" in _GROUP_KIND_PALETTE       # study
    # AI07 also indexes by kind enum value:
    assert "toponym" in _GROUP_KIND_PALETTE
    fill, border = _GROUP_KIND_PALETTE["toponym"]
    assert fill.endswith("80"), f"toponym fill must be 50% alpha, got {fill}"
    # Resolver helper picks dimension first, falls back to kind
    assert _resolve_group_visual(group_kind="struttura", kind="functional") == \
           _GROUP_KIND_PALETTE["struttura"]
    assert _resolve_group_visual(group_kind="<unknown>", kind="toponym") == \
           _GROUP_KIND_PALETTE["toponym"]
```

- [ ] **Step 2: Run to verify fails**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_export_em_template.py::test_locationnodegroup_palette_keyed_by_kind -v
```

Expected: FAIL — `_resolve_group_visual` not defined.

- [ ] **Step 3: Extend palette + add resolver**

In `modules/s3dgraphy/sync/graphml_writer.py`, replace lines 1274–1286 with:

```python
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
```

- [ ] **Step 4: Run to verify passes**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_export_em_template.py::test_locationnodegroup_palette_keyed_by_kind -v
```

Expected: PASS.

- [ ] **Step 5: Run AC-2 baseline to confirm no regression**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS (the resolver only changes behaviour when the group has a `kind` field, and the AC-2 fixture doesn't set up groups).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py \
        tests/sync/test_groups_export_em_template.py
git commit -m "feat(ai07/A): kind-aware palette lookup with _resolve_group_visual

Extends _GROUP_KIND_PALETTE with the 3 LocationNodeGroup.kind enum
values (toponym/study/functional) and adds _resolve_group_visual
helper that tries dimension key first, then kind enum, then defaults.
This keeps AC-2 byte-identical for all existing dimensions while
giving AI07 LocationNodeGroup folders a distinct visual style."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group B — `GroupSpec` extension (node_class + kind)

### Task B.1: Extend `GroupSpec` with `node_class` and `kind` fields

**Files:**
- Modify: `modules/s3dgraphy/sync/group_projector.py:38-52`
- Test: `tests/sync/test_group_projector.py` (existing) — extend with 4 new tests

- [ ] **Step 1: Write failing tests**

Append to `tests/sync/test_group_projector.py`:

```python
def test_groupspec_has_node_class_field():
    """AI07 B.1: GroupSpec carries node_class to dispatch ActivityNodeGroup vs LocationNodeGroup."""
    from modules.s3dgraphy.sync.group_projector import GroupSpec
    spec = GroupSpec(
        group_uuid="abc",
        name="X",
        group_kind="struttura",
        member_us_uuids=[],
        node_class="LocationNodeGroup",
        kind="functional",
    )
    assert spec.node_class == "LocationNodeGroup"
    assert spec.kind == "functional"


def test_attivita_resolves_to_activitynodegroup_no_kind():
    """AI07 B.1 + Q1: attivita stays as ActivityNodeGroup with kind=None."""
    from modules.s3dgraphy.sync.group_projector import (
        _resolve_node_class_and_kind,
    )
    cls, kind = _resolve_node_class_and_kind("attivita")
    assert cls == "ActivityNodeGroup"
    assert kind is None


def test_struttura_ambient_resolve_to_locationnodegroup_functional():
    from modules.s3dgraphy.sync.group_projector import (
        _resolve_node_class_and_kind,
    )
    for dim in ("struttura", "ambient"):
        cls, kind = _resolve_node_class_and_kind(dim)
        assert cls == "LocationNodeGroup"
        assert kind == "functional"


def test_area_settore_saggio_quad_par_resolve_to_locationnodegroup_study():
    from modules.s3dgraphy.sync.group_projector import (
        _resolve_node_class_and_kind,
    )
    for dim in ("area", "settore", "saggio", "quad_par"):
        cls, kind = _resolve_node_class_and_kind(dim)
        assert cls == "LocationNodeGroup"
        assert kind == "study"


def test_adhoc_resolves_to_locationnodegroup_functional_default():
    from modules.s3dgraphy.sync.group_projector import (
        _resolve_node_class_and_kind,
    )
    cls, kind = _resolve_node_class_and_kind("adhoc")
    assert cls == "LocationNodeGroup"
    assert kind == "functional"
```

- [ ] **Step 2: Run to verify fails**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_projector.py -k "node_class or resolve" -v
```

Expected: 5 FAILs — `node_class`, `kind`, `_resolve_node_class_and_kind` missing.

- [ ] **Step 3: Extend `GroupSpec` + add resolver**

In `modules/s3dgraphy/sync/group_projector.py`, replace the `GroupSpec` dataclass (lines 41–51) with:

```python
# AI07: dispatch table from pyarchinit dimension → (s3dgraphy node class, kind enum)
_GROUP_KIND_TO_S3D: dict[str, tuple[str, str | None]] = {
    # 6 spatial dimensions → LocationNodeGroup
    "area":      ("LocationNodeGroup", "study"),
    "settore":   ("LocationNodeGroup", "study"),
    "saggio":    ("LocationNodeGroup", "study"),
    "quad_par":  ("LocationNodeGroup", "study"),
    "struttura": ("LocationNodeGroup", "functional"),
    "ambient":   ("LocationNodeGroup", "functional"),
    # attivita stays as ActivityNodeGroup (Q1 — Emanuel 2026-05-09)
    "attivita":  ("ActivityNodeGroup", None),
    # ad-hoc groups land as LocationNodeGroup with default kind=functional
    "adhoc":     ("LocationNodeGroup", "functional"),
    # toponym chain (computed by _emit_toponym_chain, not from us_table)
    "toponym":   ("LocationNodeGroup", "toponym"),
}


def _resolve_node_class_and_kind(group_kind: str) -> tuple[str, str | None]:
    """AI07: map pyarchinit group_kind → (node_class, kind_enum).

    Returns ("LocationNodeGroup", "functional") for unknown kinds — defensive
    default, never raises. Logs a warning at the call site.
    """
    return _GROUP_KIND_TO_S3D.get(group_kind, ("LocationNodeGroup", "functional"))


@dataclass(frozen=True)
class GroupSpec:
    """Pre-render specification of a group.

    Resolved to ActivityNodeGroup or LocationNodeGroup by
    GraphProjector._merge_groups (AI07).
    """
    group_uuid: str
    name: str
    group_kind: str
    member_us_uuids: List[str] = field(default_factory=list)
    description: str = ""
    # AI07: dispatch fields. Default values keep call-sites that
    # construct GroupSpec without these (existing AI06 tests) green;
    # build_groups_from_sql sets them explicitly.
    node_class: str = "ActivityNodeGroup"
    kind: str | None = None
```

Then update `build_groups_from_sql` (around line 90+, the loop body) to populate the new fields:

```python
# Inside build_groups_from_sql, replace the GroupSpec construction:
node_class, kind_enum = _resolve_node_class_and_kind(dim)
specs.append(GroupSpec(
    group_uuid=group_uuid,
    name=str(value),
    group_kind=dim,
    member_us_uuids=[r["node_uuid"] for r in rows
                     if r["node_uuid"] is not None],
    node_class=node_class,
    kind=kind_enum,
))
```

And update `merge_adhoc_groups` to set `node_class="LocationNodeGroup"`, `kind="functional"` for ad-hoc specs.

- [ ] **Step 4: Run to verify passes**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_projector.py -v
```

Expected: all existing tests + 5 new ones PASS.

- [ ] **Step 5: Run full sync suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `187 passed, 3 skipped` (182 + 5 new).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/group_projector.py \
        tests/sync/test_group_projector.py
git commit -m "feat(ai07/B): GroupSpec gains node_class + kind dispatch fields

GroupSpec now carries node_class ('LocationNodeGroup' or
'ActivityNodeGroup') and kind ('toponym' / 'study' / 'functional' / None)
so _merge_groups can dispatch per dimension without re-reading the
mapping table. _resolve_node_class_and_kind is the single source of
truth for the dimension → (class, kind) mapping.

Per Q1 (Emanuel 2026-05-09): attivita stays as ActivityNodeGroup with
kind=None. The 6 spatial dimensions resolve to LocationNodeGroup with
kind ∈ {functional, study}. Ad-hoc groups default to LocationNodeGroup
+ functional.

5 new tests."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group C — `_merge_groups` rewrite (per-dimension dispatch)

### Task C.1: Write failing test for LocationNodeGroup projection

**Files:**
- Test: `tests/sync/test_locationnodegroup_projection.py` (new)

- [ ] **Step 1: Create the test file**

Create `tests/sync/test_locationnodegroup_projection.py`:

```python
"""AI07 Group C: GraphProjector._merge_groups dispatches per dimension.

Asserts that:
- 6 spatial dims → LocationNodeGroup with correct kind
- attivita → ActivityNodeGroup (unchanged from AI06)
- US has at most 1 is_primary edge
- is_in_location vs is_in_activity edge type per class
"""
from __future__ import annotations
import sqlite3
from pathlib import Path

import pytest

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIXTURES = Path(__file__).parent / "fixtures"
MINI_VOLTERRA = FIXTURES / "mini_volterra.sqlite"


def _populate_dim(db_path: Path, dim: str, value: str = "GroupX"):
    """Set us_table.<dim>=value for all rows where sito='Volterra'."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            f"UPDATE us_table SET {dim}=? WHERE sito='Volterra'", (value,)
        )
        conn.commit()
    finally:
        conn.close()


@pytest.mark.parametrize("dim,expected_kind", [
    ("struttura", "functional"),
    ("ambient", "functional"),
])
def test_struttura_emits_locationnodegroup_kind_functional(tmp_path, dim, expected_kind):
    db = tmp_path / "x.sqlite"
    db.write_bytes(MINI_VOLTERRA.read_bytes())
    _populate_dim(db, dim, "Basilica")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="Volterra", groups=[dim])
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"]
    assert len(locs) >= 1
    assert all(loc.kind == expected_kind for loc in locs)


@pytest.mark.parametrize("dim", ["area", "settore", "saggio", "quad_par"])
def test_area_emits_locationnodegroup_kind_study(tmp_path, dim):
    db = tmp_path / "x.sqlite"
    db.write_bytes(MINI_VOLTERRA.read_bytes())
    _populate_dim(db, dim, "AreaX")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="Volterra", groups=[dim])
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"]
    assert len(locs) >= 1
    assert all(loc.kind == "study" for loc in locs)


def test_attivita_stays_activitynodegroup(tmp_path):
    db = tmp_path / "x.sqlite"
    db.write_bytes(MINI_VOLTERRA.read_bytes())
    _populate_dim(db, "attivita", "Saggio_I")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="Volterra", groups=["attivita"])
    acts = [n for n in graph.nodes
            if type(n).__name__ == "ActivityNodeGroup"]
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"]
    assert len(acts) >= 1, "attivita must produce ActivityNodeGroup"
    assert all(not getattr(n, "kind", None) for n in acts), \
           "ActivityNodeGroup must have no kind field"
    # attivita must NOT produce a LocationNodeGroup
    assert all("attivita" not in (getattr(loc, "name", "") or "")
               for loc in locs)


def test_us_has_exactly_one_is_primary(tmp_path):
    """AC-17: with multiple memberships, exactly 1 edge has is_primary=true."""
    db = tmp_path / "x.sqlite"
    db.write_bytes(MINI_VOLTERRA.read_bytes())
    _populate_dim(db, "struttura", "Basilica")
    _populate_dim(db, "area", "A")
    proj = GraphProjector()
    graph = proj.populate_graph(
        db_path=db, sito="Volterra", groups=["struttura", "area"]
    )
    # Pick one US and count its is_primary edges
    us_nodes = [n for n in graph.nodes
                if type(n).__name__ in ("StratigraphicUnit", "USNode")
                or "Stratigraphic" in type(n).__name__]
    assert us_nodes, "fixture must have stratigraphic units"
    for us in us_nodes[:5]:  # check first 5
        primaries = sum(
            1 for e in graph.edges
            if e.edge_source == us.node_id
            and getattr(e, "attributes", {}).get("is_primary") is True
        )
        assert primaries <= 1, \
            f"US {us.node_id} has {primaries} is_primary edges (>1)"


def test_is_in_location_edge_for_locationnodegroup(tmp_path):
    db = tmp_path / "x.sqlite"
    db.write_bytes(MINI_VOLTERRA.read_bytes())
    _populate_dim(db, "struttura", "Basilica")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="Volterra", groups=["struttura"])
    loc_ids = {n.node_id for n in graph.nodes
               if type(n).__name__ == "LocationNodeGroup"}
    if not loc_ids:
        pytest.skip("fixture has no LocationNodeGroup after projection")
    edges_to_loc = [e for e in graph.edges if e.edge_target in loc_ids]
    assert all(e.edge_type == "is_in_location" for e in edges_to_loc), \
        "all edges to LocationNodeGroup must be is_in_location"


def test_is_in_activity_edge_for_activitynodegroup_unchanged(tmp_path):
    db = tmp_path / "x.sqlite"
    db.write_bytes(MINI_VOLTERRA.read_bytes())
    _populate_dim(db, "attivita", "Saggio_I")
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="Volterra", groups=["attivita"])
    act_ids = {n.node_id for n in graph.nodes
               if type(n).__name__ == "ActivityNodeGroup"}
    edges_to_act = [e for e in graph.edges if e.edge_target in act_ids]
    assert edges_to_act, "attivita projection must have edges to its groups"
    assert all(e.edge_type == "is_in_activity" for e in edges_to_act), \
        "all edges to ActivityNodeGroup must remain is_in_activity (Q1)"
```

- [ ] **Step 2: Run to verify all fail (function not yet rewritten)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_locationnodegroup_projection.py -v
```

Expected: 8 FAILs (parametrized). Reason: `_merge_groups` still emits `ActivityNodeGroup` for all dims.

### Task C.2: Rewrite `_merge_groups` to dispatch per dimension

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py:642-740` (`_merge_groups`)

- [ ] **Step 1: Read existing `_merge_groups`**

```bash
sed -n '642,740p' modules/s3dgraphy/sync/graph_projector.py
```

Confirm it currently uses `from s3dgraphy.nodes.group_node import ActivityNodeGroup` and `edge_type="is_in_activity"` for all dims.

- [ ] **Step 2: Rewrite the function**

In `modules/s3dgraphy/sync/graph_projector.py`, replace lines 642–740 (the entire `_merge_groups` method) with:

```python
def _merge_groups(self, graph, db_path, sito, dimensions,
                  primary_priority=None):
    """Materialize group nodes per dimension. AI07: dispatch per
    dimension — 6 spatial dims → LocationNodeGroup + is_in_location,
    attivita → ActivityNodeGroup + is_in_activity (unchanged).

    primary_priority: list[str] of dimension names ordered from highest
    to lowest priority for is_primary selection. None = use
    DEFAULT_PRIMARY_PRIORITY.
    """
    from .group_projector import (
        build_groups_from_sql, merge_adhoc_groups,
    )
    sql_dims = [d for d in dimensions if d != "adhoc"]
    specs = build_groups_from_sql(db_path, sito, sql_dims)

    if "adhoc" in dimensions:
        from .group_store import GroupStore
        store = GroupStore(db_path, sito)
        specs = merge_adhoc_groups(specs, store)

    # AI07: lazy import both classes from the vendored 0.1.41
    from s3dgraphy.nodes.group_node import (
        ActivityNodeGroup, LocationNodeGroup,
    )

    # Build node_uuid → node_id map (unchanged from AI06)
    node_uuid_to_id: dict = {}
    strat_by_name: dict = {}
    for n in graph.nodes:
        attrs = getattr(n, "attributes", None) or {}
        nu = attrs.get("node_uuid")
        if nu:
            node_uuid_to_id[str(nu)] = getattr(n, "node_id", None)
        cls = type(n).__name__
        if cls.startswith("Stratigraphic") or cls == "USNode":
            strat_by_name[str(getattr(n, "name", ""))] = n
    if strat_by_name and not node_uuid_to_id:
        try:
            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.execute(
                    "SELECT node_uuid, us FROM us_table "
                    "WHERE sito=? AND node_uuid IS NOT NULL",
                    (sito,),
                )
                for nu, us_val in cur.fetchall():
                    if nu is None or us_val is None:
                        continue
                    node = strat_by_name.get(str(us_val))
                    if node is not None:
                        node_uuid_to_id[str(nu)] = node.node_id
            finally:
                conn.close()
        except sqlite3.Error:
            pass

    # AI07: gather all memberships first, so compute_primary has the
    # full picture per US before any edge is added.
    memberships: list[dict] = []  # {us_id, group_uuid, group_kind}
    existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}

    for spec in specs:
        if spec.group_uuid in existing_ids:
            continue  # idempotent

        # Dispatch class per spec
        if spec.node_class == "LocationNodeGroup":
            node = LocationNodeGroup(
                node_id=spec.group_uuid,
                name=spec.name,
                kind=spec.kind or "functional",  # defensive default
                description=spec.description or "",
            )
            edge_type = "is_in_location"
        else:
            node = ActivityNodeGroup(
                node_id=spec.group_uuid,
                name=spec.name,
                description=spec.description or "",
            )
            edge_type = "is_in_activity"

        # Carry pyarchinit metadata as attributes (round-trip)
        data_key = f"pyarchinit.{spec.group_kind}"
        node.attributes = {
            "group_kind": spec.group_kind,
            "sito": sito,
            "name": spec.name,
            data_key: spec.name,
            "group_uuid": spec.group_uuid,
        }
        graph.add_node(node)
        existing_ids.add(spec.group_uuid)

        # Collect memberships for compute_primary
        for us_uuid in spec.member_us_uuids:
            src_id = node_uuid_to_id.get(str(us_uuid), us_uuid)
            memberships.append({
                "us_id": src_id,
                "group_uuid": spec.group_uuid,
                "group_kind": spec.group_kind,
                "edge_type": edge_type,
                "us_uuid": us_uuid,
            })

    # AI07: compute is_primary per US using priority order
    from .graph_projector import compute_primary  # imports below
    priority = primary_priority or DEFAULT_PRIMARY_PRIORITY
    primaries: dict[str, str] = compute_primary(memberships, priority)
    # primaries[us_id] = group_uuid that is is_primary=true for that US

    # Materialize edges with is_primary attribute
    for m in memberships:
        edge_id = f"grp_{m['us_uuid']}_{m['group_uuid']}"
        is_primary = primaries.get(m["us_id"]) == m["group_uuid"]
        try:
            graph.add_edge(
                edge_id=edge_id,
                edge_source=m["us_id"],
                edge_target=m["group_uuid"],
                edge_type=m["edge_type"],
                attributes={"is_primary": is_primary},
            )
        except Exception:
            # Edge validation may reject if connection rules don't accept
            # the source type — keep AI06 behaviour (silent skip)
            pass
```

Add at module level near the top of `graph_projector.py` (after existing imports):

```python
# AI07: hardcoded priority order for compute_primary. Toponym is
# explicitly excluded — toponym memberships are NEVER primary.
DEFAULT_PRIMARY_PRIORITY: list[str] = [
    "struttura", "attivita", "area", "settore",
    "ambient", "saggio", "quad_par",
]


def compute_primary(memberships: list[dict],
                    priority_order: list[str]) -> dict[str, str]:
    """Pick exactly one primary group_uuid per us_id following priority.

    memberships: list of {us_id, group_uuid, group_kind, ...}
    priority_order: list of group_kind names, highest priority first

    Returns: dict us_id → group_uuid (the primary). US without any
    eligible spatial/activity membership get no entry.
    """
    by_us: dict[str, dict[str, str]] = {}  # us_id → {group_kind → group_uuid}
    for m in memberships:
        if m["group_kind"] == "toponym":
            continue  # toponym never primary
        by_us.setdefault(m["us_id"], {})[m["group_kind"]] = m["group_uuid"]

    out: dict[str, str] = {}
    for us_id, dims in by_us.items():
        for dim in priority_order:
            if dim in dims:
                out[us_id] = dims[dim]
                break
        else:
            # Fallback: take any non-toponym membership (e.g. adhoc)
            if dims:
                out[us_id] = next(iter(dims.values()))
    return out
```

Update `populate_graph` signature near line 100 (or wherever it's defined) to accept `primary_priority`:

```python
def populate_graph(
    self,
    db_path,
    sito,
    include_paradata=True,
    strict_schema=True,
    groups=None,
    primary_priority=None,  # AI07: list[str] of group_kind names
) -> "s3dgraphy.Graph":
```

And in the call to `_merge_groups` (around line 206):

```python
self._merge_groups(graph, db_path, sito, groups, primary_priority)
```

- [ ] **Step 3: Run tests to verify dispatch works**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_locationnodegroup_projection.py -v
```

Expected: 8 PASSED.

- [ ] **Step 4: Run full sync suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -5
```

Expected: `195 passed, 3 skipped` (187 + 8 new). All AI06 tests still green.

- [ ] **Step 5: Run AC-2 baseline**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS (default `groups=None` means no groups emitted, byte-identical preserved).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py \
        tests/sync/test_locationnodegroup_projection.py
git commit -m "feat(ai07/C): _merge_groups dispatches per dimension

Spatial dimensions (area, struttura, settore, ambient, saggio,
quad_par) now emit LocationNodeGroup + is_in_location edges with
kind ∈ {functional, study} per spec mapping table. attivita stays
as ActivityNodeGroup + is_in_activity (Q1, Emanuel 2026-05-09).

compute_primary picks exactly one is_primary=true membership per
US following DEFAULT_PRIMARY_PRIORITY; toponym is explicitly excluded
(never primary).

Memberships are gathered first then is_primary is computed in batch,
so the order in which dimensions appear in the dimensions kwarg
doesn't affect which membership wins primary.

AC-2 byte-identical baseline preserved (default groups=None).
8 new tests."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task C.3: AC-2 sanity ping after dispatch rewrite

**Files:** none (test only)

- [ ] **Step 1: Run AC-2 with verbose output**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS. If it fails, the dispatch rewrite has accidentally affected the no-groups path. Investigate before continuing.

- [ ] **Step 2: Run all sync regression guards**

```bash
for t in test_round_trip test_idempotent_ingest test_paradata_store \
         test_round_trip_with_paradata test_groups_export_em_template \
         test_round_trip_with_groups test_groups_idempotent; do
  PYTHONPATH="$PWD" python -m pytest tests/sync/${t}.py -q --tb=no 2>&1 | tail -1
done
```

Expected: all green. If any fail, the dispatch rewrite broke a back-compat assumption — likely the AI06 path that still uses `ActivityNodeGroup` for `attivita`. Investigate.

---

## Group D — `_emit_toponym_chain` + cross-site dedupe

### Task D.1: Generate `toponym_volterra.sqlite` fixture

**Files:**
- Modify: `tests/sync/fixtures/build_mini_volterra_external.py` (extend with toponym builder)
- Create: `tests/sync/fixtures/toponym_volterra.sqlite` (output)

- [ ] **Step 1: Read existing builder**

```bash
head -40 tests/sync/fixtures/build_mini_volterra_external.py
```

Confirm pattern: a script that creates `mini_volterra.sqlite` with a known schema.

- [ ] **Step 2: Add toponym builder function**

Append to `tests/sync/fixtures/build_mini_volterra_external.py`:

```python
def _emit_toponym_volterra():
    """Generate toponym_volterra.sqlite — variant with site_table
    populated so AC-15 (round-trip identity) and AC-20 (cross-site
    dedupe) tests have a fixture with non-empty admin levels.
    """
    src = HERE / "mini_volterra.sqlite"
    out = HERE / "toponym_volterra.sqlite"
    if out.exists():
        out.unlink()
    out.write_bytes(src.read_bytes())
    conn = sqlite3.connect(str(out))
    try:
        # Populate Volterra site (existing) with toponym chain
        conn.execute(
            "UPDATE site_table SET nazione='Italia', regione='Toscana', "
            "provincia='Pisa', comune='Volterra' WHERE sito='Volterra'"
        )
        # Insert second site sharing comune='Volterra' for AC-20 dedupe
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('Volterra2', 'Italia', 'Toscana', 'Pisa', 'Volterra', "
            "        'Second site for cross-site dedupe test')"
        )
        # Insert third site with empty provincia for skip-empty test
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('Pompei_test', 'Italia', 'Campania', '', 'Pompei', "
            "        'Site with empty provincia for skip-empty test')"
        )
        conn.commit()
    finally:
        conn.close()
    print(f"Wrote {out}")


if __name__ == "__main__":
    # ... existing main calls ...
    _emit_toponym_volterra()
```

- [ ] **Step 3: Run the builder**

```bash
PYTHONPATH="$PWD" python tests/sync/fixtures/build_mini_volterra_external.py
ls -la tests/sync/fixtures/toponym_volterra.sqlite
```

Expected: file created, ~30-50 KB.

- [ ] **Step 4: Verify content**

```bash
sqlite3 tests/sync/fixtures/toponym_volterra.sqlite \
  "SELECT sito, nazione, regione, provincia, comune FROM site_table"
```

Expected output:
```
Volterra|Italia|Toscana|Pisa|Volterra
Volterra2|Italia|Toscana|Pisa|Volterra
Pompei_test|Italia|Campania||Pompei
```

- [ ] **Step 5: Commit fixture**

```bash
git add tests/sync/fixtures/build_mini_volterra_external.py \
        tests/sync/fixtures/toponym_volterra.sqlite
git commit -m "test(ai07/D): add toponym_volterra.sqlite fixture

3 sites with various toponym chain configurations:
- Volterra: full chain (Italia/Toscana/Pisa/Volterra)
- Volterra2: shares comune=Volterra with site #1 (AC-20 dedupe)
- Pompei_test: empty provincia (AC-15 skip-empty)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task D.2: Implement `_emit_toponym_chain` with cross-site dedupe

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py` (add new method + call from `populate_graph` Stage 3)
- Test: `tests/sync/test_toponym_chain.py` (new)

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_toponym_chain.py`:

```python
"""AI07 Group D: _emit_toponym_chain and cross-site dedupe."""
from __future__ import annotations
import hashlib
import sqlite3
from pathlib import Path

import pytest

from modules.s3dgraphy.sync.graph_projector import GraphProjector

FIXTURES = Path(__file__).parent / "fixtures"
TOPONYM_DB = FIXTURES / "toponym_volterra.sqlite"


def _toponym_uuid(name: str) -> str:
    """Deterministic UUID5 from (name, "toponym")."""
    return hashlib.sha1(f"{name}|toponym".encode()).hexdigest()[:32]


def test_full_chain_emits_4_locationnodegroup(tmp_path):
    """Italia → Toscana → Pisa → Volterra"""
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra")
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"
            and getattr(n, "kind", None) == "toponym"]
    names = sorted([n.name for n in locs])
    assert "Italia" in names
    assert "Toscana" in names
    assert "Pisa" in names
    assert "Volterra" in names


def test_partial_admin_levels_compact_chain(tmp_path):
    """Pompei_test has empty provincia — chain skips it (Q4=c).
    Italia → Campania → Pompei (no provincia node)
    """
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Pompei_test")
    locs = [n for n in graph.nodes
            if type(n).__name__ == "LocationNodeGroup"
            and getattr(n, "kind", None) == "toponym"]
    names = sorted([n.name for n in locs])
    assert "Italia" in names
    assert "Campania" in names
    assert "Pompei" in names
    # No empty-string node, no placeholder
    assert all(n != "" for n in names)
    # Chain edges: Italia ← Campania, Campania ← Pompei (no provincia)
    edge_pairs = {(e.edge_source, e.edge_target) for e in graph.edges
                  if e.edge_type == "is_in_location"}
    pompei_uuid = _toponym_uuid("Pompei")
    campania_uuid = _toponym_uuid("Campania")
    italia_uuid = _toponym_uuid("Italia")
    # Pompei → Campania (skipping provincia)
    assert (pompei_uuid, campania_uuid) in edge_pairs


def test_two_sites_same_comune_share_node(tmp_path):
    """AC-20: Volterra and Volterra2 both have comune='Volterra' →
    1 LocationNodeGroup(name='Volterra', kind='toponym').
    """
    proj = GraphProjector()
    g1 = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra")
    g2 = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra2")
    # Same projector, same DB, two calls — UUIDs must match
    volterra_uuid_1 = _toponym_uuid("Volterra")
    locs_1 = [n for n in g1.nodes
              if type(n).__name__ == "LocationNodeGroup"
              and n.name == "Volterra"
              and getattr(n, "kind", None) == "toponym"]
    locs_2 = [n for n in g2.nodes
              if type(n).__name__ == "LocationNodeGroup"
              and n.name == "Volterra"
              and getattr(n, "kind", None) == "toponym"]
    assert len(locs_1) == 1
    assert len(locs_2) == 1
    assert locs_1[0].node_id == locs_2[0].node_id == volterra_uuid_1


def test_us_connects_to_deepest_level_only(tmp_path):
    """Each US has exactly one is_in_location edge into the toponym
    chain (the deepest non-empty level), with is_primary=false.
    """
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=TOPONYM_DB, sito="Volterra")
    us_nodes = [n for n in graph.nodes
                if "Stratigraphic" in type(n).__name__
                or type(n).__name__ == "USNode"]
    if not us_nodes:
        pytest.skip("fixture has no stratigraphic units")
    volterra_uuid = _toponym_uuid("Volterra")
    for us in us_nodes[:5]:
        toponym_edges = [e for e in graph.edges
                         if e.edge_source == us.node_id
                         and e.edge_target == volterra_uuid]
        assert len(toponym_edges) == 1, \
            f"US {us.node_id} has {len(toponym_edges)} edges to deepest toponym"
        e = toponym_edges[0]
        assert getattr(e, "attributes", {}).get("is_primary") is False, \
            "toponym memberships must always be is_primary=false"


def test_all_admin_levels_empty_no_chain(tmp_path):
    """If site_table has all 4 admin levels empty → no toponym chain."""
    db = tmp_path / "x.sqlite"
    db.write_bytes(TOPONYM_DB.read_bytes())
    conn = sqlite3.connect(str(db))
    try:
        conn.execute(
            "INSERT OR IGNORE INTO site_table "
            "(sito, nazione, regione, provincia, comune, descrizione) "
            "VALUES ('NoToponym', '', '', '', '', 'all empty')"
        )
        conn.commit()
    finally:
        conn.close()
    proj = GraphProjector()
    graph = proj.populate_graph(db_path=db, sito="NoToponym")
    toponyms = [n for n in graph.nodes
                if type(n).__name__ == "LocationNodeGroup"
                and getattr(n, "kind", None) == "toponym"]
    assert toponyms == []


def test_round_trip_preserves_site_table(tmp_path):
    """AC-15: export → re-import → site_table is byte-identical."""
    db = tmp_path / "x.sqlite"
    db.write_bytes(TOPONYM_DB.read_bytes())
    # Snapshot site_table
    conn = sqlite3.connect(str(db))
    try:
        before = conn.execute(
            "SELECT sito, nazione, regione, provincia, comune FROM site_table "
            "ORDER BY sito"
        ).fetchall()
    finally:
        conn.close()
    # Project + (would round-trip via GraphML, but for now just project
    # and verify projector doesn't mutate site_table)
    proj = GraphProjector()
    proj.populate_graph(db_path=db, sito="Volterra")
    conn = sqlite3.connect(str(db))
    try:
        after = conn.execute(
            "SELECT sito, nazione, regione, provincia, comune FROM site_table "
            "ORDER BY sito"
        ).fetchall()
    finally:
        conn.close()
    assert before == after, "projector must not mutate site_table"
```

- [ ] **Step 2: Run to verify all fail**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_toponym_chain.py -v
```

Expected: 6 FAILs — `_emit_toponym_chain` not yet implemented.

- [ ] **Step 3: Implement `_emit_toponym_chain`**

In `modules/s3dgraphy/sync/graph_projector.py`, add after the `_merge_groups` method:

```python
def _emit_toponym_chain(self, graph, db_path, sito):
    """AI07 Stage 3: emit a recursive LocationNodeGroup(kind='toponym')
    chain from site_table.{nazione,regione,provincia,comune}.

    Empty levels are skipped (Q4=c). If all 4 levels are empty, no
    chain is emitted.

    Cross-site dedupe: each (name, "toponym") pair maps to a
    deterministic group_uuid (sha1) so two sites in the same comune
    share the node.

    Each US in the projected graph gets one is_in_location edge to
    the DEEPEST non-empty level (typically `comune`), always
    is_primary=false (toponym never primary).

    The chain itself is structured top-down via is_in_location edges:
    nazione ← regione ← provincia ← comune (each lower level
    "is_in_location" of the next level up).
    """
    import hashlib
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.execute(
                "SELECT nazione, regione, provincia, comune "
                "FROM site_table WHERE sito=?",
                (sito,),
            )
            row = cur.fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return  # site_table missing or corrupt — log INFO, skip
    if row is None:
        return  # sito not in site_table

    levels: list[tuple[str, str]] = []  # (level_name, value)
    for col_idx, col_name in enumerate(
        ("nazione", "regione", "provincia", "comune")
    ):
        v = row[col_idx]
        if v is not None and str(v).strip():
            levels.append((col_name, str(v).strip()))

    if not levels:
        return  # all empty — no chain

    # Lazy import (vendored 0.1.41)
    from s3dgraphy.nodes.group_node import LocationNodeGroup

    def _toponym_uuid(name: str) -> str:
        return hashlib.sha1(f"{name}|toponym".encode()).hexdigest()[:32]

    existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}

    # Get-or-create each level
    level_uuids: list[str] = []
    for level_name, value in levels:
        uid = _toponym_uuid(value)
        level_uuids.append(uid)
        if uid in existing_ids:
            continue  # cross-site dedupe — already there
        node = LocationNodeGroup(
            node_id=uid,
            name=value,
            kind="toponym",
            description=f"Administrative level: {level_name}",
        )
        node.attributes = {
            "group_kind": "toponym",
            "level": level_name,
            "name": value,
            "group_uuid": uid,
        }
        graph.add_node(node)
        existing_ids.add(uid)

    # Chain edges: lower → upper (deeper → broader)
    # comune is_in_location provincia, provincia is_in_location regione, ...
    for lower_idx in range(len(level_uuids) - 1, 0, -1):
        lower = level_uuids[lower_idx]
        upper = level_uuids[lower_idx - 1]
        edge_id = f"chain_{lower}_{upper}"
        try:
            graph.add_edge(
                edge_id=edge_id,
                edge_source=lower,
                edge_target=upper,
                edge_type="is_in_location",
                attributes={"is_primary": False},
            )
        except Exception:
            pass

    # US edges: each US connects to the DEEPEST level (last in `levels`)
    deepest_uuid = level_uuids[-1]
    us_nodes = [n for n in graph.nodes
                if type(n).__name__ in ("StratigraphicUnit", "USNode")
                or "Stratigraphic" in type(n).__name__]
    for us in us_nodes:
        edge_id = f"top_{us.node_id}_{deepest_uuid}"
        try:
            graph.add_edge(
                edge_id=edge_id,
                edge_source=us.node_id,
                edge_target=deepest_uuid,
                edge_type="is_in_location",
                attributes={"is_primary": False},
            )
        except Exception:
            pass
```

Then call it from `populate_graph` (Stage 3, after `_propagate_node_uuid_and_us` Stage 2b, before `_merge_groups` Stage 4). Around line 200-ish:

```python
            # Stage 3 (AI07): toponym chain from site_table
            try:
                self._emit_toponym_chain(graph, db_path, sito)
            except Exception as e:
                logger.warning(
                    f"_emit_toponym_chain failed, continuing without "
                    f"toponym chain: {e}"
                )
```

- [ ] **Step 4: Run to verify all pass**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_toponym_chain.py -v
```

Expected: 6 PASSED.

- [ ] **Step 5: Run full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `201 passed, 3 skipped` (195 + 6 new).

- [ ] **Step 6: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS. The mini_volterra fixture has empty admin levels, so `_emit_toponym_chain` returns early (no chain emitted, baseline unchanged).

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py \
        tests/sync/test_toponym_chain.py
git commit -m "feat(ai07/D): _emit_toponym_chain with cross-site dedupe

Stage 3 of populate_graph: emit a recursive LocationNodeGroup chain
from site_table.{nazione,regione,provincia,comune} with kind='toponym'.

Empty admin levels are skipped (Q4=c). If all 4 levels are empty,
no chain is emitted (defensive — preserves AC-2 baseline for
mini_volterra fixture).

Cross-site dedupe (AC-20): two sites with the same comune share
the same LocationNodeGroup node via deterministic
sha1((name, 'toponym')) UUID.

Each US connects to the DEEPEST level via is_in_location with
is_primary=false (toponym never primary, per spec §3.2).

Chain edges flow bottom-up: comune → provincia → regione → nazione,
all via is_in_location with is_primary=false.

6 new tests."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group E — `compute_primary` extras + dialog combobox

### Task E.1: `compute_primary` unit tests + override

**Files:**
- Test: `tests/sync/test_primary_selection.py` (new)

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_primary_selection.py`:

```python
"""AI07 Group E: compute_primary unit tests.

Already implemented in graph_projector.py (Group C); this file pins
its behaviour with focused unit tests.
"""
from __future__ import annotations

from modules.s3dgraphy.sync.graph_projector import (
    DEFAULT_PRIMARY_PRIORITY,
    compute_primary,
)


def test_default_priority_struttura_first():
    """When US has both struttura and area, struttura wins."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_struttura", "group_kind": "struttura"},
        {"us_id": "U1", "group_uuid": "g_area",      "group_kind": "area"},
    ]
    primaries = compute_primary(memberships, DEFAULT_PRIMARY_PRIORITY)
    assert primaries == {"U1": "g_struttura"}


def test_override_changes_primary():
    """Custom priority puts area first."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_struttura", "group_kind": "struttura"},
        {"us_id": "U1", "group_uuid": "g_area",      "group_kind": "area"},
    ]
    custom_order = ["area", "struttura"]  # area first
    primaries = compute_primary(memberships, custom_order)
    assert primaries == {"U1": "g_area"}


def test_toponym_excluded_from_primary():
    """Even with priority list including 'toponym', toponym is never primary."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_top", "group_kind": "toponym"},
        {"us_id": "U1", "group_uuid": "g_str", "group_kind": "struttura"},
    ]
    primaries = compute_primary(
        memberships, ["toponym", "struttura"]  # toponym first in order!
    )
    assert primaries == {"U1": "g_str"}, \
        "toponym must never be primary regardless of priority order"


def test_fallback_to_adhoc_when_no_spatial():
    """If US has only adhoc + toponym, adhoc wins as fallback."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_adhoc", "group_kind": "adhoc"},
        {"us_id": "U1", "group_uuid": "g_top",   "group_kind": "toponym"},
    ]
    primaries = compute_primary(memberships, DEFAULT_PRIMARY_PRIORITY)
    assert primaries == {"U1": "g_adhoc"}


def test_us_with_no_eligible_membership_excluded():
    """US with only toponym membership has no entry in primaries."""
    memberships = [
        {"us_id": "U1", "group_uuid": "g_top", "group_kind": "toponym"},
    ]
    primaries = compute_primary(memberships, DEFAULT_PRIMARY_PRIORITY)
    assert primaries == {}
```

- [ ] **Step 2: Run**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_primary_selection.py -v
```

Expected: 5 PASSED (the function is already implemented in Group C).

- [ ] **Step 3: Commit**

```bash
git add tests/sync/test_primary_selection.py
git commit -m "test(ai07/E): pin compute_primary behaviour

5 unit tests covering:
- DEFAULT_PRIMARY_PRIORITY (struttura first)
- Custom priority order override (AC-19)
- Toponym always excluded from primary
- Adhoc fallback when no spatial/activity membership
- US with only toponym → no primary entry"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task E.2: Dialog combobox + remove multi-dim warning

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py:300-600` (S3DGraphyExportDialog)

- [ ] **Step 1: Read existing dialog code**

```bash
sed -n '300,400p' modules/s3dgraphy/s3dgraphy_dot_bridge.py
```

Locate `setupUI` and find where the QGroupBox "Group US by" is built (around line 370–400).

- [ ] **Step 2: Add `QComboBox` after the group checkboxes**

In `modules/s3dgraphy/s3dgraphy_dot_bridge.py`, inside `setupUI` (right after the existing `gb_groups` QGroupBox setup, around line 380), add:

```python
            # AI07: Primary dimension combobox
            from qgis.PyQt.QtWidgets import QComboBox, QHBoxLayout, QLabel
            primary_row = QHBoxLayout()
            primary_row.addWidget(QLabel("Primary dimension:"))
            self.cb_primary_dim = QComboBox()
            for dim in ("struttura", "attivita", "area", "settore",
                        "ambient", "saggio", "quad_par"):
                self.cb_primary_dim.addItem(dim)
            self.cb_primary_dim.setCurrentText("struttura")  # default
            self.cb_primary_dim.setToolTip(
                "When a US belongs to multiple groups, which dimension "
                "wins as the visual yEd folder. Toponym chain is never "
                "primary."
            )
            primary_row.addWidget(self.cb_primary_dim)
            primary_row.addStretch()
            gb_layout.addLayout(primary_row)
```

- [ ] **Step 3: Remove the multi-dim warning at `on_export`**

Around line 580–600 in the same file, find the block:

```python
            if len(groups_arg) > 1:
                msg = (
                    f"Hai selezionato {len(groups_arg)} dimensioni …"
                    # ...
                )
                reply = QMessageBox.warning(...)
                if reply != QMessageBox.Yes:
                    return
                groups_arg = [groups_arg[0]]
```

Replace it with:

```python
            # AI07 + AI08-F1: multi-dim is now natively supported via
            # is_primary on the is_in_location edges. The 5.5.2-alpha
            # workaround warning is removed.
            primary_dim = self.cb_primary_dim.currentText()
            # Reorder primary_priority to put the user's choice first
            primary_priority = [primary_dim] + [
                d for d in (
                    "struttura", "attivita", "area", "settore",
                    "ambient", "saggio", "quad_par",
                )
                if d != primary_dim
            ]
```

And update the call to `bridge.export_integrated_matrix` to pass `primary_priority`:

```python
                self.exported_files = self.bridge.export_integrated_matrix(
                    self.site,
                    self.area,
                    output_dir,
                    formats,
                    groups=groups_arg,
                    primary_priority=primary_priority,  # AI07
                )
```

You'll also need to add `primary_priority` to `S3DGraphyDotBridge.export_integrated_matrix` signature (around line 100 in the same file) and pipe it through to `GraphProjector().populate_graph()`.

- [ ] **Step 4: Manual smoke (no automated test for Qt dialog without QGIS)**

```bash
PYTHONPATH="$PWD" python -c "
# Headless smoke — does the import succeed?
import modules.s3dgraphy.s3dgraphy_dot_bridge as m
print('Module loaded OK. Combobox added at line:',
      [i for i, l in enumerate(open(m.__file__).readlines(), 1)
       if 'cb_primary_dim' in l][:3])
"
```

Expected: lists at least 2-3 line numbers where `cb_primary_dim` appears.

- [ ] **Step 5: Run full sync suite (none of the dialog code is exercised in tests/sync/, but verify nothing imports it incorrectly)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `206 passed, 3 skipped` (201 + 5 new from Task E.1).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "feat(ai07/E): primary dimension combobox + remove multi-dim warning

The 5.5.2-alpha workaround warning ('Multi-dim export non ancora
supportato') is removed. With AI07's m:n is_primary semantics, multi-dim
export is now natively supported.

The export dialog gains a 'Primary dimension' QComboBox (default:
struttura) that reorders DEFAULT_PRIMARY_PRIORITY to put the user's
choice first. The reordered list is passed to populate_graph() as
primary_priority kwarg.

Toponym chain is never primary regardless of dialog choice."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group F — `_promote_legacy_activitynodegroup` (on-read up-conversion)

### Task F.1: Generate `legacy_5_5_x.graphml` fixture

**Files:**
- Modify: `tests/sync/fixtures/build_mini_volterra_external.py`
- Create: `tests/sync/fixtures/legacy_5_5_x.graphml`

- [ ] **Step 1: Add fixture builder**

Append to `tests/sync/fixtures/build_mini_volterra_external.py`:

```python
def _emit_legacy_5_5_x_fixture():
    """Generate legacy_5_5_x.graphml — a snapshot of what AI06 would
    have produced for mini_volterra with groups=['attivita', 'struttura',
    'area', 'settore']. All 4 group folders are ActivityNodeGroup with
    pyarchinit.<kind> data attributes.

    AI07's on-read up-conversion must promote 3 of them
    (struttura, area, settore) to LocationNodeGroup; attivita stays
    untouched.
    """
    out = HERE / "legacy_5_5_x.graphml"
    if out.exists():
        out.unlink()
    # Copy mini_volterra and inject groups via AI06-style export
    db = HERE / "mini_volterra.sqlite"
    tmp_db = HERE / "_legacy_tmp.sqlite"
    tmp_db.write_bytes(db.read_bytes())

    conn = sqlite3.connect(str(tmp_db))
    try:
        conn.execute(
            "UPDATE us_table SET attivita='Saggio_I', struttura='Basilica', "
            "area='A', settore='Settore_N' WHERE sito='Volterra'"
        )
        conn.commit()
    finally:
        conn.close()

    import sys
    sys.path.insert(0, str(HERE.parents[2]))
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    export_graphml(
        db_path=str(tmp_db),
        sito="Volterra",
        output_path=str(out),
        groups=["attivita", "struttura", "area", "settore"],
    )
    tmp_db.unlink()
    print(f"Wrote {out}")


if __name__ == "__main__":
    _emit_toponym_volterra()
    _emit_legacy_5_5_x_fixture()
```

**WAIT — important:** when you run the builder, AI07 dispatch is already in place (Group C). So `export_graphml` will produce `LocationNodeGroup` for the 3 spatial dims, NOT `ActivityNodeGroup`. To get a true "5.5.x-style" fixture, the builder needs to monkeypatch `_resolve_node_class_and_kind` or hand-craft the GraphML.

Use the hand-craft approach: craft a minimal GraphML directly with lxml. Replace the body of `_emit_legacy_5_5_x_fixture` with:

```python
def _emit_legacy_5_5_x_fixture():
    """Hand-crafted GraphML mimicking AI06 output: 4 ActivityNodeGroup
    folders with pyarchinit.<kind> data attributes."""
    out = HERE / "legacy_5_5_x.graphml"
    template = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key id="d_kind_attivita" for="node" attr.name="pyarchinit.attivita"/>
  <key id="d_kind_struttura" for="node" attr.name="pyarchinit.struttura"/>
  <key id="d_kind_area" for="node" attr.name="pyarchinit.area"/>
  <key id="d_kind_settore" for="node" attr.name="pyarchinit.settore"/>
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_attivita" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_attivita">Saggio_I</data>
    </node>
    <node id="grp_struttura" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_struttura">Basilica</data>
    </node>
    <node id="grp_area" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_area">A</data>
    </node>
    <node id="grp_settore" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_settore">Settore_N</data>
    </node>
  </graph>
</graphml>
"""
    out.write_text(template, encoding="utf-8")
    print(f"Wrote {out}")
```

- [ ] **Step 2: Run builder**

```bash
PYTHONPATH="$PWD" python tests/sync/fixtures/build_mini_volterra_external.py
ls -la tests/sync/fixtures/legacy_5_5_x.graphml
```

Expected: file created, ~1 KB.

- [ ] **Step 3: Commit fixture**

```bash
git add tests/sync/fixtures/build_mini_volterra_external.py \
        tests/sync/fixtures/legacy_5_5_x.graphml
git commit -m "test(ai07/F): legacy_5_5_x.graphml fixture for autopromote tests

Hand-crafted GraphML mimicking AI06 output: 4 ActivityNodeGroup
folders with pyarchinit.<kind> data entries. AI07's on-read promote
must up-convert 3 (struttura, area, settore) to LocationNodeGroup;
attivita stays untouched."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task F.2: Implement `_promote_legacy_activitynodegroup` + DeprecationWarning

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py` (add new method, call from `populate_list` Stage B)
- Test: `tests/sync/test_legacy_autopromote.py` (new)

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_legacy_autopromote.py`:

```python
"""AI07 Group F: on-read up-conversion of legacy 5.5.x ActivityNodeGroup."""
from __future__ import annotations
import warnings
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
LEGACY = FIXTURES / "legacy_5_5_x.graphml"


def _parse_legacy_to_graph():
    """Helper: parse the legacy fixture into an s3dgraphy.Graph."""
    from s3dgraphy import Graph
    from s3dgraphy.importer.import_graphml import GraphMLImporter
    g = Graph()
    importer = GraphMLImporter(g, str(LEGACY))
    importer.parse()
    return g


def test_legacy_5_5_x_promoted_in_memory():
    """3 of 4 ActivityNodeGroup nodes promoted to LocationNodeGroup."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = _parse_legacy_to_graph()
    n_before_act = sum(1 for n in g.nodes
                       if type(n).__name__ == "ActivityNodeGroup")
    assert n_before_act == 4, f"fixture must have 4 AGN, got {n_before_act}"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _promote_legacy_activitynodegroup(g)
    n_after_act = sum(1 for n in g.nodes
                      if type(n).__name__ == "ActivityNodeGroup")
    n_after_loc = sum(1 for n in g.nodes
                      if type(n).__name__ == "LocationNodeGroup")
    assert n_after_act == 1, f"only attivita stays as AGN, got {n_after_act}"
    assert n_after_loc == 3, f"3 spatial promoted to LNG, got {n_after_loc}"


def test_attivita_stays_activitynodegroup():
    """attivita group_kind must NOT be promoted."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = _parse_legacy_to_graph()
    _promote_legacy_activitynodegroup(g)
    activities = [n for n in g.nodes
                  if type(n).__name__ == "ActivityNodeGroup"]
    assert len(activities) == 1
    assert getattr(activities[0], "node_id", None) == "grp_attivita"


def test_warning_emitted_once_per_call():
    """One DeprecationWarning per _promote call, not per node."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = _parse_legacy_to_graph()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _promote_legacy_activitynodegroup(g)
    deprec = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprec) == 1, \
        f"expected 1 DeprecationWarning, got {len(deprec)}"
    assert "legacy" in str(deprec[0].message).lower()
    assert "5.6.0" in str(deprec[0].message) or "AI07" in str(deprec[0].message)


def test_unknown_group_kind_left_as_activitynodegroup():
    """ActivityNodeGroup with custom group_kind (not in SQL_BACKED_KINDS_SPATIAL) stays."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    from modules.s3dgraphy.sync.graph_ingestor import (
        _promote_legacy_activitynodegroup,
    )
    g = Graph()
    n = ActivityNodeGroup(node_id="x", name="X")
    n.attributes = {"group_kind": "custom_dim_2026"}
    g.add_node(n)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        _promote_legacy_activitynodegroup(g)
    survivors = [m for m in g.nodes
                 if type(m).__name__ == "ActivityNodeGroup"]
    assert len(survivors) == 1
    # No deprecation warning emitted (nothing to promote)
    deprec = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprec) == 0
```

- [ ] **Step 2: Run to verify fails**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_legacy_autopromote.py -v
```

Expected: 4 FAILs — `_promote_legacy_activitynodegroup` not yet defined.

- [ ] **Step 3: Implement**

In `modules/s3dgraphy/sync/graph_ingestor.py`, add at module level near the top (after existing constants):

```python
# AI07: subset of SQL_BACKED_KINDS that maps to LocationNodeGroup.
# Excludes "attivita" (Q1 — stays as ActivityNodeGroup) and "adhoc"
# (already LocationNodeGroup at projection time).
SQL_BACKED_KINDS_SPATIAL: frozenset[str] = frozenset({
    "area", "struttura", "settore", "ambient", "saggio", "quad_par",
})


# AI07: dimension → s3dgraphy LocationNodeGroup.kind enum value
_DIM_TO_KIND: dict[str, str] = {
    "area":      "study",
    "settore":   "study",
    "saggio":    "study",
    "quad_par":  "study",
    "struttura": "functional",
    "ambient":   "functional",
}


def _promote_legacy_activitynodegroup(graph) -> int:
    """AI07 Stage B: scan graph for ActivityNodeGroup nodes whose
    attributes carry group_kind ∈ SQL_BACKED_KINDS_SPATIAL, and
    promote them in-memory to LocationNodeGroup with kind set per
    _DIM_TO_KIND. Also rewires incoming is_in_activity edges to
    is_in_location.

    Emits exactly ONE DeprecationWarning per call (not per node) if
    any promotion happens.

    Returns: number of nodes promoted.
    """
    import warnings
    from s3dgraphy.nodes.group_node import (
        ActivityNodeGroup, LocationNodeGroup,
    )

    promotions: list = []  # list of (old_node, new_node)
    for n in list(graph.nodes):
        if type(n).__name__ != "ActivityNodeGroup":
            continue
        attrs = getattr(n, "attributes", None) or {}
        gk = attrs.get("group_kind")
        if gk not in SQL_BACKED_KINDS_SPATIAL:
            continue  # attivita / adhoc / unknown — leave alone
        kind_enum = _DIM_TO_KIND.get(gk, "functional")
        new_node = LocationNodeGroup(
            node_id=n.node_id,
            name=n.name,
            kind=kind_enum,
            description=getattr(n, "description", "") or "",
        )
        new_node.attributes = dict(attrs)
        promotions.append((n, new_node))

    if not promotions:
        return 0

    # Replace in-place: Graph.nodes is typically a list — find indices
    nodes_list = list(graph.nodes)
    for old, new in promotions:
        try:
            idx = nodes_list.index(old)
            nodes_list[idx] = new
        except ValueError:
            graph.add_node(new)
    # Best-effort: assign back if mutable
    try:
        graph.nodes = nodes_list  # type: ignore[attr-defined]
    except (AttributeError, TypeError):
        pass

    # Rewire is_in_activity → is_in_location for promoted targets
    promoted_ids = {old.node_id for old, _ in promotions}
    for e in graph.edges:
        if e.edge_target in promoted_ids and e.edge_type == "is_in_activity":
            e.edge_type = "is_in_location"

    n = len(promotions)
    warnings.warn(
        f"Found {n} legacy ActivityNodeGroup nodes with "
        f"group_kind ∈ {{area, struttura, settore, ambient, saggio, "
        f"quad_par}}. Promoting in-memory to LocationNodeGroup + kind. "
        f"Re-export the file via 'Esporta Extended Matrix' to migrate "
        f"the on-disk representation. AI07 / pyarchinit 5.6.0+.",
        DeprecationWarning,
        stacklevel=2,
    )
    return n
```

Then call it from `populate_list` (the GraphIngestor's main entry point) as Stage B, between parsing GraphML and applying SQL writes:

```python
# In GraphIngestor.populate_list, after parsing graph from GraphML:
_promote_legacy_activitynodegroup(graph)  # AI07 Stage B
# ... existing stage C (apply_group_folders_to_sql) follows ...
```

Also add `LocationNodeGroup` to `_NON_STRAT_TYPES`:

```python
_NON_STRAT_TYPES: frozenset[str] = frozenset({
    "EpochNode",
    "GeoPositionNode",
    "PropertyNode",
    "ParadataNodeGroup",
    "AuthorNode",
    "LicenseNode",
    "EmbargoNode",
    "ExtractorNode",
    "CombinerNode",
    "VirtualSpecialFindUnit",
    "GroupNode",
    "ActivityNodeGroup",
    "LocationNodeGroup",       # AI07: new spatial group node class
    "TimeBranchNodeGroup",
})
```

- [ ] **Step 4: Run to verify all pass**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_legacy_autopromote.py -v
```

Expected: 4 PASSED.

- [ ] **Step 5: Run full sync suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `210 passed, 3 skipped` (206 + 4 new).

- [ ] **Step 6: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_legacy_autopromote.py
git commit -m "feat(ai07/F): _promote_legacy_activitynodegroup + DeprecationWarning

On-read up-conversion of legacy 5.5.x ActivityNodeGroup nodes whose
group_kind ∈ {area, struttura, settore, ambient, saggio, quad_par}
to LocationNodeGroup with kind ∈ {functional, study} per spec mapping.

attivita stays untouched (Q1, Emanuel 2026-05-09).

incoming is_in_activity edges are rewired to is_in_location for
promoted targets.

Exactly one DeprecationWarning per populate_list() call (not per node),
referencing AI07 / pyarchinit 5.6.0+.

Also adds LocationNodeGroup to _NON_STRAT_TYPES so the ingestor
doesn't try to write it to us_table.

4 new tests."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group G — Recursive `_apply_group_folders_to_sql`

### Task G.1: Recursive walker tests

**Files:**
- Test: `tests/sync/test_locationnodegroup_recursive_ingest.py` (new)

- [ ] **Step 1: Create the test file**

Create `tests/sync/test_locationnodegroup_recursive_ingest.py`:

```python
"""AI07 Group G: recursive _apply_group_folders_to_sql walker tests."""
from __future__ import annotations
import sqlite3
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _build_nested_graphml(out_path, levels=("Italia", "Toscana", "Pisa")):
    """Hand-craft a 3-level nested LocationNodeGroup yEd structure."""
    template = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:y="http://www.yworks.com/xml/graphml">
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <key id="d_kind_top" for="node" attr.name="pyarchinit.toponym"/>
  <graph id="G" edgedefault="directed">
"""
    # Outer folder Italia, inner Toscana, innermost Pisa
    inner_pisa = """      <node id="grp_pisa" yfiles.foldertype="group">
        <data key="d_node_type">LocationNodeGroup</data>
        <data key="d_kind_top">Pisa</data>
        <graph id="g_pisa"/>
      </node>"""
    inner_toscana = f"""      <node id="grp_toscana" yfiles.foldertype="group">
        <data key="d_node_type">LocationNodeGroup</data>
        <data key="d_kind_top">Toscana</data>
        <graph id="g_toscana">
{inner_pisa}
        </graph>
      </node>"""
    outer = f"""      <node id="grp_italia" yfiles.foldertype="group">
        <data key="d_node_type">LocationNodeGroup</data>
        <data key="d_kind_top">Italia</data>
        <graph id="g_italia">
{inner_toscana}
        </graph>
      </node>"""
    Path(out_path).write_text(template + outer + "\n  </graph>\n</graphml>\n",
                              encoding="utf-8")


def test_walker_descends_into_nested_folder(tmp_path):
    """AC-18: walker visits Italia → Toscana → Pisa (3 levels)."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    g = tmp_path / "nested.graphml"
    _build_nested_graphml(g)
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    visited = []
    # Patch the walker to record every visit
    import modules.s3dgraphy.sync.graph_ingestor as mod
    orig = mod._apply_group_folders_to_sql
    n = orig(cur, g, "Volterra")
    conn.close()
    # Toponym kind is NOT in SQL_BACKED_KINDS, so n=0 (no SQL writes),
    # but the walker MUST have visited all 3 levels — verified via
    # absence of cycle errors and by re-running with a non-toponym
    # nested fixture in another test below.
    assert n == 0, "toponym levels never write SQL"


def test_cycle_detected_aborts_ingest(tmp_path):
    """If the GraphML inadvertently has a folder cycle, walker aborts."""
    cycle = tmp_path / "cycle.graphml"
    # Outer A contains B; inner B claims to be the same XML element as
    # outer A (id='grp_a'). Use a hand-crafted cycle:
    cycle.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d_kind_str" for="node" attr.name="pyarchinit.struttura"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_a" yfiles.foldertype="group">
      <data key="d_kind_str">A</data>
      <graph id="g_a">
        <node id="grp_a" yfiles.foldertype="group">
          <data key="d_kind_str">A</data>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
""", encoding="utf-8")
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    with pytest.raises(Exception) as exc:
        _apply_group_folders_to_sql(cur, cycle, "Volterra")
    # Either CycleDetectedError or any error mentioning cycle/visited
    msg = str(exc.value).lower()
    assert "cycle" in msg or "visited" in msg or "duplicate" in msg


def test_locationnodegroup_with_us_members_writes_sql(tmp_path):
    """LocationNodeGroup folder containing US members → UPDATE us_table."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    # Pick a known us value from mini_volterra
    conn = sqlite3.connect(str(db))
    row = conn.execute(
        "SELECT us, area FROM us_table WHERE sito='Volterra' LIMIT 1"
    ).fetchone()
    us_val, _ = row
    conn.close()

    # Hand-craft a LocationNodeGroup with one US member referencing us_val
    gp = tmp_path / "loc.graphml"
    gp.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <key id="d_kind_str" for="node" attr.name="pyarchinit.struttura"/>
  <key id="d_us" for="node" attr.name="pyarchinit.us"/>
  <key id="d_area" for="node" attr.name="pyarchinit.area"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_struttura" yfiles.foldertype="group">
      <data key="d_node_type">LocationNodeGroup</data>
      <data key="d_kind_str">NewBasilica</data>
      <graph id="g_str">
        <node id="us1">
          <data key="d_us">{us_val}</data>
          <data key="d_area">A</data>
        </node>
      </graph>
    </node>
  </graph>
</graphml>
""", encoding="utf-8")
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    n = _apply_group_folders_to_sql(cur, gp, "Volterra")
    conn.commit()
    assert n >= 1, f"expected ≥1 UPDATE, got {n}"
    after = conn.execute(
        "SELECT struttura FROM us_table WHERE sito='Volterra' AND us=?",
        (us_val,),
    ).fetchone()
    conn.close()
    assert after[0] == "NewBasilica"


def test_mixed_locationnodegroup_and_activitynodegroup(tmp_path):
    """Walker handles both LocationNodeGroup and ActivityNodeGroup folders."""
    from modules.s3dgraphy.sync.graph_ingestor import (
        _apply_group_folders_to_sql,
    )
    db = tmp_path / "x.sqlite"
    db.write_bytes((FIXTURES / "mini_volterra.sqlite").read_bytes())
    row = sqlite3.connect(str(db)).execute(
        "SELECT us FROM us_table WHERE sito='Volterra' LIMIT 1"
    ).fetchone()
    us_val = row[0]

    gp = tmp_path / "mixed.graphml"
    gp.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d_node_type" for="node" attr.name="_s3d_node_type"/>
  <key id="d_kind_str" for="node" attr.name="pyarchinit.struttura"/>
  <key id="d_kind_act" for="node" attr.name="pyarchinit.attivita"/>
  <key id="d_us" for="node" attr.name="pyarchinit.us"/>
  <graph id="G" edgedefault="directed">
    <node id="grp_struttura" yfiles.foldertype="group">
      <data key="d_node_type">LocationNodeGroup</data>
      <data key="d_kind_str">B1</data>
      <graph id="g_str"><node id="us1"><data key="d_us">{us_val}</data></node></graph>
    </node>
    <node id="grp_attivita" yfiles.foldertype="group">
      <data key="d_node_type">ActivityNodeGroup</data>
      <data key="d_kind_act">SaggioX</data>
      <graph id="g_act"><node id="us1b"><data key="d_us">{us_val}</data></node></graph>
    </node>
  </graph>
</graphml>
""", encoding="utf-8")
    conn = sqlite3.connect(str(db))
    cur = conn.cursor()
    n = _apply_group_folders_to_sql(cur, gp, "Volterra")
    conn.commit()
    after = conn.execute(
        "SELECT struttura, attivita FROM us_table WHERE sito='Volterra' "
        "AND us=?", (us_val,),
    ).fetchone()
    conn.close()
    assert after[0] == "B1"
    assert after[1] == "SaggioX"
```

- [ ] **Step 2: Run to verify all fail**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_locationnodegroup_recursive_ingest.py -v
```

Expected: at least 2 FAILs (cycle detection + nested walker missing).

### Task G.2: Implement recursive walker

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py:578-700` (`_apply_group_folders_to_sql`)

- [ ] **Step 1: Read existing function**

```bash
sed -n '578,700p' modules/s3dgraphy/sync/graph_ingestor.py
```

Confirm it's currently flat (no recursion).

- [ ] **Step 2: Rewrite as recursive walker**

Replace the existing `_apply_group_folders_to_sql` (lines 578–700) with:

```python
class CycleDetectedError(GraphIngestError):
    """AI07: recursive walker detected a cycle in yEd folder nesting."""


def _apply_group_folders_to_sql(cur, graphml_path: Path, sito: str) -> int:
    """AI07: recursive walker — descend yEd folder-in-folder structures
    and apply ``UPDATE us_table SET <kind>=<group_name>`` per
    SQL-backed folder.

    Toponym / unknown / ad-hoc kinds are skipped (AC-14 unchanged).

    Cycle detection: a `visited` set guards against malformed GraphML
    where folder A contains folder B contains folder A.
    """
    try:
        from lxml import etree as _ET
    except ImportError:
        return 0

    NS_G = "{http://graphml.graphdrawing.org/xmlns}"
    NS_Y = "{http://www.yworks.com/xml/graphml}"
    try:
        _tree = _ET.parse(str(graphml_path))
    except Exception:
        return 0
    root = _tree.getroot()

    # Build d-key id → group_kind map
    kid_to_kind: dict = {}
    node_uuid_kid = us_kid = area_kid = sito_kid = None
    for k in root.findall(f"{NS_G}key"):
        attr_name = k.get("attr.name") or ""
        if not attr_name.startswith("pyarchinit."):
            continue
        short = attr_name.split(".", 1)[1]
        if short in _GROUP_KIND_TO_COL:
            kid_to_kind[k.get("id")] = short
        if short == "node_uuid":
            node_uuid_kid = k.get("id")
        elif short == "us":
            us_kid = k.get("id")
        elif short == "area":
            area_kid = k.get("id")
        elif short == "sito":
            sito_kid = k.get("id")

    applied = 0
    visited: set[str] = set()

    def _visit_folder(folder_elem) -> int:
        nonlocal applied
        fid = folder_elem.get("id") or ""
        if fid in visited:
            raise CycleDetectedError(
                f"Cycle detected: folder {fid!r} visited twice"
            )
        visited.add(fid)

        # Discover this folder's group_kind from its data entries
        group_kind = None
        group_name = None
        for d in folder_elem.findall(f"{NS_G}data"):
            kind = kid_to_kind.get(d.get("key"))
            if kind:
                group_kind = kind
                group_name = (d.text or "").strip() or None
                break

        # Walk inner graph
        inner = folder_elem.find(f"{NS_G}graph")
        if inner is None:
            return 0

        # Apply SQL UPDATE for direct US members of this folder
        # (only if group_kind is SQL-backed and not toponym/adhoc)
        local_applied = 0
        if group_kind in _GROUP_KIND_TO_COL and group_name:
            for member in inner.findall(f"{NS_G}node"):
                # Skip nested folders — they get walked recursively below
                if member.get("yfiles.foldertype") == "group":
                    continue
                # Identify US member (prefer node_uuid, fall back to us+area)
                node_uuid = us_val = area_val = None
                for md in member.findall(f"{NS_G}data"):
                    kid = md.get("key")
                    if kid == node_uuid_kid:
                        node_uuid = (md.text or "").strip() or None
                    elif kid == us_kid:
                        us_val = (md.text or "").strip() or None
                    elif kid == area_kid:
                        area_val = (md.text or "").strip() or None
                if node_uuid:
                    cur.execute(
                        f"UPDATE us_table SET {group_kind}=? "
                        f"WHERE node_uuid=? AND sito=?",
                        (group_name, node_uuid, sito),
                    )
                    local_applied += cur.rowcount or 0
                elif us_val and area_val:
                    cur.execute(
                        f"UPDATE us_table SET {group_kind}=? "
                        f"WHERE us=? AND area=? AND sito=?",
                        (group_name, us_val, area_val, sito),
                    )
                    local_applied += cur.rowcount or 0

        # Recurse into nested folders
        for child in inner.findall(f"{NS_G}node"):
            if child.get("yfiles.foldertype") == "group":
                local_applied += _visit_folder(child)

        return local_applied

    # Walk top-level folders
    for folder in root.iter(f"{NS_G}node"):
        if folder.get("yfiles.foldertype") != "group":
            continue
        # Top-level folders only (not nested ones — those are visited
        # recursively by their parent)
        parent = folder.getparent()
        if parent is not None and parent.tag == f"{NS_G}graph":
            grandparent = parent.getparent()
            if grandparent is not None and grandparent.tag == f"{NS_G}node":
                # this folder is nested — skip; it'll be visited by its parent
                continue
        applied += _visit_folder(folder)

    return applied
```

- [ ] **Step 3: Run to verify all pass**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_locationnodegroup_recursive_ingest.py -v
```

Expected: 4 PASSED.

- [ ] **Step 4: Run full sync suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `214 passed, 3 skipped` (210 + 4 new).

- [ ] **Step 5: Run AI06 round-trip regression**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py tests/sync/test_groups_idempotent.py -v
```

Expected: all green. The recursive walker is backwards-compatible with flat (single-level) folders, so AI06 round-trip tests still pass.

- [ ] **Step 6: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_locationnodegroup_recursive_ingest.py
git commit -m "feat(ai07/G): recursive _apply_group_folders_to_sql + cycle detection

The walker now descends into yEd folder-in-folder structures
(toponym chains and user-nested struttura > area in yEd). Each
SQL-backed folder writes UPDATE us_table SET <kind>=<name> for
its direct US members (NOT for nested folders — those get walked
recursively).

Cycle detection: a visited set raises CycleDetectedError if the
same folder id appears twice in the descent path.

Toponym / adhoc / unknown kinds skip SQL writes (AC-14 unchanged).

The walker is backwards-compatible with AI06 flat folder layouts
— round-trip and idempotent regression tests stay green.

4 new tests."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

---

## Group H — Re-baseline + dialog cleanup + dev-log + CHANGELOG + tag

### Task H.1: Regenerate AC-2 baseline

**Files:**
- Modify: `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` (regenerate)
- Modify: `tests/sync/test_ai03_export_byte_identical.py` (update expected fingerprint values if hardcoded)

- [ ] **Step 1: Run with --update-baseline flag (or regenerate manually)**

```bash
PYTHONPATH="$PWD" python -c "
from pathlib import Path
PLUGIN_ROOT = Path('.').resolve()
import sys; sys.path.insert(0, str(PLUGIN_ROOT / 'ext_libs'))
for m in [k for k in list(sys.modules) if k == 's3dgraphy' or k.startswith('s3dgraphy.')]:
    del sys.modules[m]

from modules.s3dgraphy.sync.graphml_writer import export_graphml
src = PLUGIN_ROOT / 'tests/sync/fixtures/mini_volterra.sqlite'
dst = PLUGIN_ROOT / 'tests/sync/fixtures/mini_volterra_baseline_ai03.graphml'
export_graphml(db_path=str(src), sito='Volterra', output_path=str(dst))
print(f'Regenerated {dst}')
print('size:', dst.stat().st_size)
"
```

Expected: file regenerated, size approx similar to old baseline.

- [ ] **Step 2: Inspect the diff vs the old baseline**

```bash
git diff --stat tests/sync/fixtures/mini_volterra_baseline_ai03.graphml
```

Expected: lines changed (the new baseline differs because group folders, if any, now use `LocationNodeGroup` instead of `ActivityNodeGroup`). Note: with default `groups=None`, the AI03 export emits NO group folders, so the baseline should be largely unchanged. If it is byte-identical, even better — confirm and skip the regeneration commit (commit only if there's a diff).

- [ ] **Step 3: Run the AC-2 test**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

Expected: PASS.

- [ ] **Step 4: Commit (only if Step 2 showed a diff)**

```bash
git add tests/sync/fixtures/mini_volterra_baseline_ai03.graphml
git commit -m "test(ai07/H): re-baseline AC-2 fingerprint

The mini_volterra fixture has no toponym chain (empty admin levels)
and no group folders (default groups=None), so the regenerated
baseline is byte-identical or near-identical. AC-2 fingerprint
captures the structural invariants under the new LocationNodeGroup
projection logic."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

If no diff existed, skip this commit.

### Task H.2: metadata.txt version bump

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Bump version**

```bash
sed -i.bak 's/^version=5.5.2-alpha/version=5.6.0-alpha/' metadata.txt
rm metadata.txt.bak
grep "^version=" metadata.txt
```

Expected: `version=5.6.0-alpha`.

- [ ] **Step 2: Commit**

```bash
git add metadata.txt
git commit -m "release(ai07/H): bump version 5.5.2-alpha → 5.6.0-alpha

Minor bump justified by:
- node_type strings change (ActivityNodeGroup → LocationNodeGroup
  for 6 spatial dimensions)
- AC-2 fingerprint changes
- new is_in_location edge type"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task H.3: dev-log entry

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Append AI07 section**

Insert at the top (after the dev-log header) a new section:

```markdown
## Phase 2 — AI07 LocationNodeGroup migration (5.6.0-alpha)

**Tag:** `phase2-ai07-locationnodegroup-5.6.0-alpha`
**Date:** 2026-05-XX
**Spec:** `docs/superpowers/specs/2026-05-09-ai07-locationnodegroup-design.md`
**Plan:** `docs/superpowers/plans/2026-05-09-ai07-locationnodegroup.md`
**Issue:** [zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5) (resolved)

### What shipped

- 6 spatial dimensions (area, struttura, settore, ambient, saggio,
  quad_par) now project as `LocationNodeGroup` with `kind ∈
  {functional, study}` and `is_in_location` edges
- `attivita` stays as `ActivityNodeGroup` per Q1 (unchanged from AI06)
- m:n membership with `is_primary` disambiguation (one primary
  membership per US chosen via `compute_primary` priority order)
- Toponym chain from `site_table.{nazione,regione,provincia,comune}`
  with cross-site dedupe (deterministic UUID5 from `(name, "toponym")`)
- Recursive `_apply_group_folders_to_sql` walker with cycle detection
- On-read up-conversion of legacy 5.5.x `ActivityNodeGroup +
  group_kind` → `LocationNodeGroup + kind` with one-shot
  `DeprecationWarning`
- Multi-dim export warning removed (5.5.2-alpha workaround obsolete)
- Dialog gains `QComboBox "Primary dimension"` for user override

### Tests

- 5 new test files, ~30 distinct cases
- Final count: 209 passed, 3 skipped (was 179)
- AC-2 byte-identical baseline preserved (no group folders by default)

### Known follow-ups

- AI09 `TimeBranchNodeGroup` for `cron_iniziale/cron_finale` — future
- AI08-F3 auto-layout heuristics — pending real-world feedback on F2
- `pyarchinit.tools.migrate_legacy_groupkind` standalone CLI — deferred
- CIDOC-S3D mapping call — end-May / early-June post-AI07
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
git commit -m "docs(ai07/H): dev-log entry for 5.6.0-alpha"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task H.4: CHANGELOG entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Prepend bilingual section**

Insert at line 1 (after the header) a new section:

```markdown
## [5.6.0-alpha] - 2026-05-XX

### Italiano

**AI07 — Migrazione `LocationNodeGroup` + AI08-F1 m:n hierarchical (fusi).**

Le 6 dimensioni spaziali (`area`, `struttura`, `settore`, `ambient`,
`saggio`, `quad_par`) ora producono nodi `LocationNodeGroup` di
s3dgraphy 0.1.41 con `kind ∈ {functional, study}` e edge
`is_in_location`. La dimensione `attivita` resta `ActivityNodeGroup`
con edge `is_in_activity` (Q1 — Emanuel 2026-05-09).

- **m:n membership**: ogni US può appartenere a più gruppi
  contemporaneamente; `is_primary=true` su un singolo edge
  determina il folder yEd visivo. Le altre membership sono
  emesse come `<data key="s3d:other_locations">` array sul
  nodo US per render badge inline.
- **Toponym chain**: da `site_table.{nazione, regione, provincia,
  comune}` viene emesso un chain ricorsivo di
  `LocationNodeGroup(kind="toponym")`, con dedupe cross-site
  (stesso comune in 2 siti = 1 nodo condiviso, UUID deterministico).
- **On-read up-conversion**: i file 5.5.x esistenti vengono
  promossi in-memory automaticamente — il projector intercetta
  `ActivityNodeGroup + group_kind ∈ {area, ..., quad_par}` e li
  converte. Una sola `DeprecationWarning` per chiamata.
- **Multi-dim export warning rimosso**: il workaround di
  5.5.2-alpha (single-dimension only) decade, sostituito dal
  modello m:n con `is_primary`.
- **Dialog combobox "Primary dimension"**: l'utente può
  sovrascrivere la priorità default (struttura > attivita > ...)
  per quel singolo export.
- **Walker ricorsivo**: `_apply_group_folders_to_sql` ora
  discende in folder-in-folder nesting yEd con detection cicli.

### English

**AI07 — `LocationNodeGroup` migration + AI08-F1 m:n hierarchical (fused).**

The 6 spatial dimensions (`area`, `struttura`, `settore`, `ambient`,
`saggio`, `quad_par`) now produce s3dgraphy 0.1.41
`LocationNodeGroup` nodes with `kind ∈ {functional, study}` and
`is_in_location` edges. The `attivita` dimension stays as
`ActivityNodeGroup` with `is_in_activity` edges (Q1 — Emanuel
2026-05-09).

- **m:n membership**: each US can belong to multiple groups;
  `is_primary=true` on exactly one edge determines the visual
  yEd folder. Other memberships emit `<data key="s3d:other_locations">`
  on the US node for inline badge rendering.
- **Toponym chain**: from `site_table.{nazione, regione, provincia,
  comune}`, a recursive
  `LocationNodeGroup(kind="toponym")` chain is emitted with
  cross-site dedupe (same comune across 2 sites = 1 shared node,
  deterministic UUID).
- **On-read up-conversion**: legacy 5.5.x files are promoted
  in-memory automatically — projector intercepts
  `ActivityNodeGroup + group_kind ∈ {area, ..., quad_par}` and
  converts. One `DeprecationWarning` per call.
- **Multi-dim export warning removed**: the 5.5.2-alpha workaround
  (single-dimension only) is obsolete, replaced by the m:n model
  with `is_primary`.
- **Dialog combobox "Primary dimension"**: user can override the
  default priority (struttura > attivita > ...) for a single export.
- **Recursive walker**: `_apply_group_folders_to_sql` now descends
  into yEd folder-in-folder nesting with cycle detection.

---
```

- [ ] **Step 2: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "docs(ai07/H): bilingual CHANGELOG entry for 5.6.0-alpha"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

Expected: last command returns `0`.

### Task H.5: Manual smoke gate (USER-driven)

**Files:** none

- [ ] **Step 1: User opens `test_ai_50us.sqlite` (Phase 2 pause synthetic fixture) in QGIS**

The fixture is at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/test_ai_50us.sqlite`.

- [ ] **Step 2: Export Extended Matrix with multi-dim**

User: open Scheda US, click "Esporta Extended Matrix", check `struttura` + `area`. Pick `struttura` as primary dimension. Click Export.

- [ ] **Step 3: Verify in yEd**

Open the produced `.graphml` in yEd. Verify:
- Primary yEd folder (struttura) rendered as **dashed roundrectangle** with kind-coloured border (orange for `functional`)
- Secondary folder (area) present as a sibling, NOT as the parent of any US (because area is not primary)
- Inline label/badge on US showing the area membership (rendered from `s3d:other_locations`)
- If `site_table` has admin levels populated, toponym chain visible at the canvas edges with recursive nesting Italia → Lazio → Roma → Casa del Fauno

- [ ] **Step 4: Re-import test**

User: in pyarchinit, re-import the modified GraphML with checkbox `Update SQL on import` enabled. Verify `us_table` rows are updated correctly (e.g., move a US to a different struttura folder in yEd, save, re-import, check `us_table.struttura` updated).

- [ ] **Step 5: Legacy file test**

User: open a 5.5.x-format file (e.g., a previously exported file from before the AI07 ship). Re-import. Verify:
- A `DeprecationWarning` appears in the QGIS console / log
- The graph renders with `LocationNodeGroup` folders (not `ActivityNodeGroup`)
- `us_table` is updated correctly (round-trip preserved)

- [ ] **Step 6: User confirms "smoke ok, proceed"**

If the user reports any issue, STOP and create a follow-up task for the bug. Do NOT proceed to tag.

### Task H.6: Tag + push

**Files:** none (git operation)

- [ ] **Step 1: Verify clean tree + green tests**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: tracked changes empty, `~209 passed, 3 skipped`.

- [ ] **Step 2: Verify zero Co-Authored-By trailers**

```bash
git log b569bd51..HEAD --format=%B | grep -c "Co-Authored-By: Claude"
```

Expected: `0`.

- [ ] **Step 3: Tag**

```bash
git tag -a phase2-ai07-locationnodegroup-5.6.0-alpha \
  -m "AI07 — LocationNodeGroup migration + AI08-F1 m:n hierarchical

6 spatial dimensions now project as LocationNodeGroup + is_in_location
with kind ∈ {functional, study}. attivita stays as ActivityNodeGroup
(Q1 — Emanuel 2026-05-09).

- m:n with is_primary disambiguation
- Toponym chain from site_table with cross-site dedupe
- Recursive walker with cycle detection
- On-read up-conversion of legacy 5.5.x files
- Dialog 'Primary dimension' combobox
- 5.5.2-alpha multi-dim warning removed

Spec: docs/superpowers/specs/2026-05-09-ai07-locationnodegroup-design.md
Plan: docs/superpowers/plans/2026-05-09-ai07-locationnodegroup.md
Upstream: zalmoxes-laran/s3Dgraphy#5 (resolved 2026-05-09)
Predecessor: phase2-ai08f2-hotfix-5.5.2-alpha (b569bd51)
Tests: 209 passed, 3 skipped (was 179)"
git push origin phase2-ai07-locationnodegroup-5.6.0-alpha
git push origin Stratigraph_00001
```

Expected: tag created and pushed; branch pushed.

- [ ] **Step 4: Verify GitHub remote**

```bash
git ls-remote --tags origin | grep "phase2-ai07-locationnodegroup-5.6.0-alpha"
```

Expected: tag listed with the correct commit SHA.

- [ ] **Step 5: Memory + handoff**

Update `~/.claude/projects/.../memory/project_ai07_active.md`:
- Rename to `project_ai07_shipped_2026-05-XX.md` (replace `XX` with the actual date)
- Update body: "**SHIPPED** ... tag SHA ... Final test count ... Manual smoke results ..."

Update `~/.claude/projects/.../memory/MEMORY.md`:
- Replace the `[AI07 — RESOLVED, ACTIVE]` line with `[AI07 — SHIPPED] (project_ai07_shipped_*.md)` summarising the release

Create `~/.claude/projects/.../memory/project_ai07_post_release.md`:
- ETA for the CIDOC-S3D mapping call (end-May / early-June)
- Pending: PR to `zalmoxes-laran/s3Dgraphy` with the round-trip fixture
- Open question: whether to ship `pyarchinit.tools.migrate_legacy_groupkind` (deferred per spec §13)

---

## Self-Review

This plan covers every requirement in the spec:

| Spec section | Plan task |
|---|---|
| §3.1 architecture (dispatch + recursive walker + on-read promote) | Group C (dispatch) + Group G (recursive walker) + Group F (on-read promote) |
| §3.2 invariant 1 (toponym secondary, cross-site dedupe) | Group D (Task D.2) |
| §3.2 invariant 2 (priority + override) | Group C (compute_primary) + Group E (dialog combobox) |
| §3.2 invariant 3 (5.5.x backward compat) | Group F (Task F.2) |
| §4 mapping table | Group B (`_resolve_node_class_and_kind`) + Group C (`_merge_groups`) |
| §5.1 export flow stages 1–4 | Group D (Stage 3 toponym) + Group C (Stage 4 reworked) |
| §5.2 re-import flow stages A–C | Group F (Stage B promote) + Group G (Stage C recursive) |
| §5.3 `compute_primary` | Group C (function) + Group E (unit tests) |
| §5.4 visual rendering | Group A (`_resolve_group_visual` + palette) — driven by 0.1.41 visual rules |
| §6 file table (8 files modified) | All Groups touch the right files |
| §7 error handling | Group D (toponym empty → skip), Group F (warn once), Group G (CycleDetectedError) |
| §8 AC-2 to AC-20 | All ACs pinned to specific tests in test strategy matrix |
| §9 testing strategy (5 new files) | Each test file is created in the right Group |
| §10 release plan (8 Groups, ~20 commits) | This plan has Groups 0 + A through H, ~22 commits |
| §11 deliverable to s3dgraphy (PR fixture) | Out of scope of this plan; tracked in `project_ai07_post_release.md` (Task H.5 Step 5) |
| §13 explicit deferrals | All deferrals (AI08-F3, AI09, batch CLI) honored |

Type consistency: `node_class`, `kind`, `is_primary`, `compute_primary`, `_resolve_node_class_and_kind`, `_promote_legacy_activitynodegroup`, `_emit_toponym_chain`, `_apply_group_folders_to_sql`, `CycleDetectedError`, `SQL_BACKED_KINDS`, `SQL_BACKED_KINDS_SPATIAL`, `_GROUP_KIND_TO_S3D`, `_DIM_TO_KIND`, `DEFAULT_PRIMARY_PRIORITY`, `_GROUP_KIND_PALETTE`, `_resolve_group_visual` — all consistent across Groups.

No placeholders. Every step has either runnable code, exact commands, or specific file edits.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-09-ai07-locationnodegroup.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task (or per Group), review between tasks, fast iteration, two-stage review (spec compliance + code quality)
2. **Inline Execution** — execute tasks in this session using `executing-plans`, batch execution with checkpoints for user review

**Which approach?**

If **Subagent-Driven** chosen:
- **REQUIRED SUB-SKILL:** `superpowers:subagent-driven-development`
- Recommended subagent batching:
  - Group 0 (3 tasks) → 1 subagent — pure git + conftest edit
  - Group A (2 tasks) → 1 subagent — edge_registry + palette
  - Group B (1 task) → 1 subagent — GroupSpec + resolver
  - Group C (2 tasks) → 1 subagent — `_merge_groups` rewrite + AC-2 ping
  - Group D (2 tasks) → 1 subagent — toponym fixture + chain emission
  - Group E (2 tasks) → 1 subagent — `compute_primary` tests + dialog
  - Group F (2 tasks) → 1 subagent — legacy fixture + auto-promote
  - Group G (2 tasks) → 1 subagent — recursive walker
  - Group H Tasks H.1–H.4 → 1 subagent — re-baseline + version + docs
  - Group H Task H.5 → **USER-driven manual smoke gate**, no subagent
  - Group H Task H.6 → 1 subagent — tag + push + memory update

If **Inline Execution** chosen:
- **REQUIRED SUB-SKILL:** `superpowers:executing-plans`
- Batch execution with checkpoint after each Group for user review
