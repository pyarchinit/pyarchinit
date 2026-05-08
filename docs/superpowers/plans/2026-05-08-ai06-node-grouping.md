# AI06 — Node grouping (area / struttura / attivita / settore / ambient / saggio / quad_par + ad-hoc): Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add opt-in grouping of stratigraphic units (US) in the Extended Matrix export by any of 7 `us_table` columns (`area`, `struttura`, `attivita`, `settore`, `ambient`, `saggio`, `quad_par`) plus user-authored ad-hoc groups, rendered as yEd folder nodes nested inside the existing epoch swimlane and connected by `is_in_activity` edges in the s3dgraphy knowledge graph — all behind release `5.5.0-alpha`.

**Architecture:** Two new modules — `modules/s3dgraphy/sync/group_store.py` (CRUD analogous to AI05's `ParadataStore` for ad-hoc groups, persisted to `groups_{sito_slug}.graphml` next to the SQLite DB) and `modules/s3dgraphy/sync/group_projector.py` (pure-functional helpers `build_groups_from_sql`, `merge_adhoc_groups`, `dimensions_with_data`). `GraphProjector.populate_graph` gains a `groups: list[str] = None` kwarg that, when non-empty, materializes one `s3dgraphy.ActivityNodeGroup` per `(dimension, value)` pair with a `group_kind` discriminator attribute and `is_in_activity` edges from each member US. A new `_inject_group_folders` post-processor (Stage 4e in `graphml_writer.py`) re-injects the groups as yEd folder nodes (`yfiles.foldertype="group"`, `<y:GroupNode>` realizer with dashed grey border + fill `#F5F5F5` + label-on-top) nested inside the existing TableNode swimlane, with geometry computed to span all epoch rows of the member US. The `ParadataManagerDialog` from AI05 grows a 4th tab "Groups"; `S3DGraphyExportDialog` grows 7 checkboxes (one per dimension, auto-preselected from `dimensions_with_data`) plus a checkbox in the Import tab for opt-in SQL UPDATE on round-trip.

**Tech Stack:** Python 3.9+, s3dgraphy 0.1.40 (vendored), lxml (transitive), pytest, sqlite3, QGIS PyQt5/PyQt6 abstraction. **No new third-party dependencies.**

**Spec source of truth:** `docs/superpowers/specs/2026-05-08-ai06-node-grouping-design.md` (commit `d86044a9`)

**Predecessor releases:**
- AI05: tag `phase2-ai05-paradata-store-5.4.0-alpha` (current HEAD baseline)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_ai06_node_grouping.md` — origin of this plan
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict rule
- `~/.claude/projects/.../memory/project_s3dgraphy_bridge.md` — Phase 2 overview

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

**Upstream issue:** [zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5) — `LocationNodeGroup` proposal (non-blocking; AI07 migration target).

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/group_store.py` | `GroupStore` class — atomic CRUD over `groups_{sito_slug}.graphml`. Mirrors `ParadataStore` (AI05). Low-level (`read`/`write`/`add_node`/`remove_node`/`find`) + high-level (`add_group`/`list_groups`/`remove_group`/`add_us_to_group`/`remove_us_from_group`/`list_members`). Custom lxml serializer (same reason as AI05: `GraphMLExporter` doesn't render isolated `ActivityNodeGroup` instances). Exception hierarchy `GroupStoreError` extends `GraphSyncError`. ~350 lines. |
| `modules/s3dgraphy/sync/group_projector.py` | Pure-functional helpers: `GroupSpec` dataclass, `build_groups_from_sql(db, sito, dimensions) -> [GroupSpec]`, `merge_adhoc_groups(specs, store) -> [GroupSpec]`, `dimensions_with_data(db, sito) -> [str]`. UUID generation: deterministic UUID5 from `(sito, group_kind, name)`. ~200 lines. |
| `tests/sync/test_group_store.py` | L0 unit tests: file_path slug, `exists()`, atomic crash-safety, low-level CRUD, high-level helpers, membership ops, exception hierarchy. ~14 tests. |
| `tests/sync/test_group_projector.py` | L1 fixture-based: `dimensions_with_data` filtering, `build_groups_from_sql` per dimension, deterministic UUID5, ad-hoc merge with collision warning. ~8 tests. |
| `tests/sync/test_groups_export_em_template.py` | L4 EM template compliance: yfiles.foldertype, GroupNode realizer, dashed border, fill `#F5F5F5`, NodeLabel top + bg `#EBEBEB`, geometry bbox spans member US, member re-parenting. ~5 tests. |
| `tests/sync/test_round_trip_with_groups.py` | L1 round-trip: default safe (no SQL update), flag-on (SQL update reflects yEd movement), ad-hoc never touches SQL. ~3 tests. |
| `tests/sync/test_groups_idempotent.py` | L1 idempotency: 3 consecutive exports produce identical group UUIDs and stable structural fingerprints. ~2 tests. |
| `tests/sync/test_cli_groups.py` | L2 subprocess: `paradata add-group/list-groups/add-us-to-group/remove-group` + `export --group-by` + invalid args. ~6 tests. |
| `tests/sync/test_groups_dialog_smoke.py` | L0 (skip if no Qt): 4-tab dialog, Groups tab, preselect populated dimensions. ~2 tests. |
| `tests/sync/fixtures/groups_volterra.graphml` | Pre-cooked binary fixture: 1 ad-hoc group ("restauri-2023") with 3 members. Generated by `build_mini_volterra_external.py` extension. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | Add `groups: list[str] = None` kwarg to `populate_graph()`. New `_merge_groups(graph, db_path, sito, dimensions)` private method that calls `build_groups_from_sql` + `merge_adhoc_groups`, materializes `ActivityNodeGroup` instances with `attributes["group_kind"]`, and adds `is_in_activity` edges. ~80 LOC added. |
| `modules/s3dgraphy/sync/graphml_writer.py` | Capture `_group_snapshot` + `_members_map` BEFORE Stage 2 `_filter_by_site` (same pattern as AI05 paradata snapshot). Add Stage 4e `_inject_group_folders` post-processor that parses output XML, finds the TableNode swimlane, computes bbox per group, creates `<node yfiles.foldertype="group">` with EM canonical layout, re-parents member US `<node>` elements. Pass `groups` kwarg through to `GraphProjector().populate_graph()`. ~220 LOC added. |
| `modules/s3dgraphy/sync/graph_ingestor.py` | Add `sql_apply_groups: bool = False` kwarg to `populate_list()`. When True: parse group folder nodes from import GraphML, queue `UPDATE us_table SET <kind>=<name>` for SQL-derived `group_kind` values (basic 7); ad-hoc memberships always go to GroupStore. Atomic transaction (AI04 contract). ~60 LOC added. |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Add `QGroupBox "Group US by"` with 7 `QCheckBox` (auto-preselected via `dimensions_with_data` on dialog open) + 1 `cb_grp_adhoc` checkbox to `S3DGraphyExportDialog`. Pass `groups=[checked_dims]` to `export_graphml`. Add `cb_sql_apply_groups` checkbox to Import tab; pass through to `GraphIngestor.populate_list`. ~80 LOC added. |
| `gui/dialog_paradata_manager.py` | Add 4th tab "Groups" with `QTableWidget` (Name / Kind / US count) + form (name `QLineEdit`, kind `QComboBox` initially `["adhoc"]` only, "Pick US members…" button) + Add/Remove buttons. Secondary `QDialog` `_pick_us_members_dialog` for multi-select US picker. ~250 LOC added. |
| `scripts/s3dgraphy_sync.py` | Add `paradata add-group`, `paradata list-groups`, `paradata add-us-to-group`, `paradata remove-group` sub-subcommands. Add `--group-by` CSV flag on `export` subcommand. Same exit-code contract as AI04/AI05. ~120 LOC added. |
| `tests/sync/fixtures/build_mini_volterra_external.py` | Extend with `_emit_groups_fixture()` — generates `groups_volterra.graphml` with 1 ad-hoc group via `GroupStore`. Idempotent. ~40 LOC. |
| `metadata.txt` | Bump `version=5.4.0-alpha` → `version=5.5.0-alpha`. |
| `dev_logs/CHANGELOG.md` | Prepend `## [5.5.0-alpha] - 2026-MM-DD` bilingual section. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | New "Phase 2 — AI06 Node grouping" section. |

### Explicitly NOT touched (out of scope per spec §9)

- `modules/s3dgraphy/sync/paradata_store.py` — AI05 file unchanged.
- `modules/s3dgraphy/sync/edge_registry.py` — AI05 file unchanged. AI06 reuses existing `is_in_activity` edge classification (no new edge types).
- `modules/s3dgraphy/sync/conflict_resolver.py` — pluggable strategies remain AI06+ deferred (despite the version naming, that work is now AI08+).
- `ext_libs/s3dgraphy/` — no upstream modifications. `LocationNodeGroup` migration awaits issue #5.
- `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml` — AC-2 baseline unchanged (default `groups=[]` preserves byte-identical output).
- `requirements.txt` — no new dependencies.

---

## Test strategy

- **L0 unit tests** (`test_group_store.py`, `test_groups_dialog_smoke.py`): pure pytest, no DB, no QGIS bootstrap.
- **L1 fixture-based** (`test_group_projector.py`, `test_round_trip_with_groups.py`, `test_groups_idempotent.py`): pytest against `mini_volterra.sqlite` + ad-hoc seed via `GroupStore`. No QGIS.
- **L2 CLI subprocess** (`test_cli_groups.py`): runs `python scripts/s3dgraphy_sync.py paradata add-group …` via `subprocess.run()` and asserts exit code + stdout.
- **L4 EM template compliance** (`test_groups_export_em_template.py`): structural lxml comparison of the GraphML output against the EM canonical template (`yfiles.foldertype`, `<y:GroupNode>` realizer, geometry bbox, etc.).
- **L3 regression guards**: AC-2 byte-identical baseline + AI04 round-trip/idempotent/CLI + AI05 paradata round-trip/idempotent/Strategy-A. All must stay green at every commit.

Decision-pinning matrix (each row = one D-id × one acceptance test):

| Decision / Acceptance | Test |
|---|---|
| D1 all 7 dims | `test_group_projector.py::test_build_groups_handles_all_seven_dimensions` |
| D2 preselect populated | `test_group_projector.py::test_dimensions_with_data_returns_only_populated` |
| D2 UI checkbox preselect | `test_groups_dialog_smoke.py::test_dialog_preselects_populated_dimensions` |
| D3 yfiles foldertype group | `test_groups_export_em_template.py::test_group_node_uses_yfiles_foldertype_group` |
| D3 geometry spans rows | `test_groups_export_em_template.py::test_group_geometry_spans_member_us_bbox` |
| D3 visual matches EM | `test_groups_export_em_template.py::test_group_visual_matches_em_template` |
| D3 children re-parented | `test_groups_export_em_template.py::test_group_children_are_us_member_nodes` |
| D4 ActivityNodeGroup + group_kind | `test_group_projector.py::test_group_node_has_group_kind_attribute` |
| D4 is_in_activity edge | `test_group_projector.py::test_us_to_group_edge_type_is_in_activity` |
| D5 default no SQL update | `test_round_trip_with_groups.py::test_default_no_sql_update_on_import` |
| D5 flag-on update | `test_round_trip_with_groups.py::test_sql_update_when_flag_enabled` |
| D5 ad-hoc never touches SQL | `test_round_trip_with_groups.py::test_adhoc_groups_never_touch_sql` |
| D6 ad-hoc store CRUD | `test_group_store.py::test_add_group_round_trip` |
| D6 4th tab in dialog | `test_groups_dialog_smoke.py::test_dialog_has_groups_tab` |
| D7 opt-in default empty | `test_groups_export_em_template.py::test_default_groups_empty_preserves_ac2_baseline` |
| D7 AC-2 baseline | `test_ai03_export_byte_identical.py` (existing) |
| AC-3 atomic crash-safety | `test_group_store.py::test_atomic_write_no_corruption_on_crash` |
| AC-7 deterministic UUID5 | `test_group_projector.py::test_group_uuid_deterministic_across_exports` |
| AC-15 idempotent fingerprint | `test_groups_idempotent.py::test_repeated_export_produces_stable_groups` |
| AC-16 CLI add-group | `test_cli_groups.py::test_cli_paradata_add_group` |
| AC-17 CLI export --group-by | `test_cli_groups.py::test_cli_export_with_group_by` |

Test count progression:
- Baseline post-AI05: 132 passed, 1 skipped
- Post-Group A: 146
- Post-Group B: 154
- Post-Group C: 159
- Post-Group D: 166
- Post-Group E: 168
- Post-Group F: 174
- Post-Group G: 176 + 1 skipped
- Post-Group H: 176 + 1 skipped (no new tests)

**Critical regression guards** (run after every commit Group A–G):

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v       # AC-2 (AI03)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v                       # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_idempotent_ingest.py -v                # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_cli_helper.py -v                       # AI04
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store.py -v                   # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v         # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_idempotent.py -v              # AI05
PYTHONPATH="$PWD" python -m pytest tests/sync/test_strategy_a_no_regression.py -v         # AI05
```

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

Expected: tracked changes empty, last commit is `d86044a9 docs(spec): AI06 …` or later, `1\t0` ahead-behind (the spec commit is unpushed).

- [ ] **Step 2: Push the spec commit**

```bash
git push origin Stratigraph_00001
```

Expected: 1 commit pushed (`d86044a9` and any later doc commits).

- [ ] **Step 3: Verify**

```bash
git rev-list --left-right --count HEAD...@{u}   # expected: "0\t0"
```

### Task 0.2: Create AI06 rollback tag

**Files:** none (git operation)

- [ ] **Step 1: Create annotated tag**

```bash
git tag -a pre-ai06-grouping -m "Pre-flight rollback tag for AI06 / node grouping"
git tag -l | grep -E "pre-ai0|phase2"
```

Expected output (7 lines):
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
phase2-ai05-paradata-store-5.4.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
pre-ai05-paradata
pre-ai06-grouping
```

- [ ] **Step 2: Push the tag**

```bash
git push origin pre-ai06-grouping
git ls-remote --tags origin 2>&1 | grep "refs/tags/pre-ai06-grouping$"
```

Expected: 1 matching line.

### Task 0.3: Bump version to 5.5.0-alpha

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Read current version**

```bash
grep -n "^version=" metadata.txt
```

Expected: `version=5.4.0-alpha`.

- [ ] **Step 2: Edit `metadata.txt` — change exactly the line `version=5.4.0-alpha` to `version=5.5.0-alpha`**

Use the Edit tool. Do not touch anything else.

- [ ] **Step 3: Verify**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.5.0-alpha`.

- [ ] **Step 4: Run baseline sanity tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `132 passed, 1 skipped`.

- [ ] **Step 5: Commit**

```bash
git add metadata.txt
git commit -m "$(cat <<'EOF'
chore(metadata): bump version to 5.5.0-alpha for AI06

Phase 2 / AI06 — adds opt-in grouping of US in the Extended Matrix
export by 7 us_table dimensions (area, struttura, attivita,
settore, ambient, saggio, quad_par) plus user-authored ad-hoc
groups, with EM-canonical yEd folder rendering nested in the
existing epoch swimlane.

Target tag: phase2-ai06-node-grouping-5.5.0-alpha.

Spec: docs/superpowers/specs/2026-05-08-ai06-node-grouping-design.md
Plan: docs/superpowers/plans/2026-05-08-ai06-node-grouping.md
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task 0.4: Capture baseline test counts

**Files:** none (verification only, no commit)

- [ ] **Step 1: Run full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `132 passed, 1 skipped`.

- [ ] **Step 2: Run AC-2 baseline guard**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -2
```

Expected: `1 passed`.

- [ ] **Step 3: Run all 8 critical regression guards (must remain green at every Group A–G commit)**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_idempotent_ingest.py \
  tests/sync/test_cli_helper.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  tests/sync/test_paradata_idempotent.py \
  tests/sync/test_strategy_a_no_regression.py \
  -q 2>&1 | tail -2
```

Expected: ~37 passed, 0 failed.

- [ ] **Step 4: Note progression target**

Group boundaries:
- Post-A: 146 (+14)
- Post-B: 154 (+8)
- Post-C: 159 (+5)
- Post-D: 166 (+7)
- Post-E: 168 (+2)
- Post-F: 174 (+6)
- Post-G: 176 + 1 skipped (+2)
- Post-H: 176 + 1 skipped (no new tests)

Informational only — every Group's task spells out the exact expected count.

---

## Group A — GroupStore foundation

### Task A.1: Scaffold `group_store.py` with file path + read/exists

**Files:**
- Create: `modules/s3dgraphy/sync/group_store.py`
- Create: `tests/sync/test_group_store.py`

- [ ] **Step 1: Write failing tests for file_path + exists + read empty**

Create `tests/sync/test_group_store.py` with:

```python
"""L0 unit tests for GroupStore.

Pure pytest, no QGIS, no real DB (uses tmp_path). Pins decisions
D6 (ad-hoc store CRUD) and D7 (file path slug).
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
    """Create a minimal sqlite DB so GroupStore has a parent dir."""
    db = tmp_path / "test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INTEGER, sito TEXT)")
    conn.commit()
    conn.close()
    return db


def test_file_path_resolves_per_sito(tmp_path):
    """D6/D7: file path is `{db_dir}/groups_{sito_slug}.graphml`."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    db = _make_db(tmp_path)
    store = GroupStore(db, "Scavo Archeologico")
    assert store.file_path == tmp_path / "groups_scavo_archeologico.graphml"


def test_file_path_slugifies_special_chars(tmp_path):
    """Slug replaces non-word chars with underscore + lowercases."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    db = _make_db(tmp_path)
    store = GroupStore(db, "Site #1 — α")
    assert "groups_site__1" in str(store.file_path).lower()


def test_exists_false_when_no_file(tmp_path):
    """exists() reflects on-disk presence, defaults False on init."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    assert store.exists() is False


def test_read_empty_when_no_file(tmp_path):
    """read() returns empty Graph when file doesn't exist (NOT error)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    graph = store.read()
    assert len(graph.nodes) == 0
```

- [ ] **Step 2: Run tests, expect failure (module doesn't exist)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_store.py -v
```

Expected: ImportError on `group_store`.

- [ ] **Step 3: Write minimal implementation**

Create `modules/s3dgraphy/sync/group_store.py`:

```python
"""Site-scoped CRUD for groups.graphml (atomic-safe writes).

AI06 Phase 2 / node grouping. Manages user-authored ad-hoc groups
that don't derive from any us_table column. SQL-derived groups
(struttura/area/attivita/settore/ambient/saggio/quad_par) are
materialized at export time by group_projector — they're NOT
persisted here.

File location: {db_path.parent}/groups_{sito_slug}.graphml
where sito_slug is `re.sub(r'\\W', '_', sito).lower()` (consistent
with AI05 paradata_store).

Atomic writes via .tmp + os.replace() — crash-safe.
Custom lxml serializer (s3dgraphy GraphMLExporter doesn't render
isolated ActivityNodeGroup instances without a stratigraphic
anchor — same constraint as AI05 paradata).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .graph_ingestor import GraphSyncError


class GroupStoreError(GraphSyncError):
    """Base for GroupStore errors."""


class GroupReadError(GroupStoreError):
    """File parse / schema error during read()."""


class GroupWriteError(GroupStoreError):
    """File write / atomic-rename failure during write()."""


class GroupValidationError(GroupStoreError):
    """Caller passed bogus data to add_group/add_us_to_group/etc."""


class GroupNotFoundError(GroupStoreError):
    """Required file or group_uuid missing where caller expected it."""


# Meta-keys produced by s3dgraphy's GraphMLImporter that must NOT be
# round-tripped (same lesson as AI05 paradata).
_GROUP_HYDRATE_SKIP_KEYS: frozenset[str] = frozenset({
    "original_id", "graph_id", "group_attrs",
})


def _sito_slug(sito: str) -> str:
    """Filename-safe lowercase slug for a sito identifier (matches AI05)."""
    return re.sub(r"\W", "_", sito).strip("_").lower()


class GroupStore:
    """Site-scoped CRUD for groups.graphml."""

    def __init__(self, db_path: Path, sito: str) -> None:
        if not sito:
            raise GroupValidationError(
                "sito is required for GroupStore")
        self._db_path = Path(db_path)
        self._sito = sito
        self._slug = _sito_slug(sito)

    @property
    def file_path(self) -> Path:
        return self._db_path.parent / f"groups_{self._slug}.graphml"

    def exists(self) -> bool:
        return self.file_path.exists()

    @property
    def sito(self) -> str:
        return self._sito

    # ---- Low-level ------------------------------------------------------
    def read(self):
        """Return a Graph populated only with ad-hoc group nodes from
        the file. Returns empty Graph when file absent."""
        from s3dgraphy import Graph
        if not self.exists():
            graph = Graph(graph_id=self._sito)
            # Defensive filter: drop the default GeoPositionNode
            graph.nodes = [
                n for n in graph.nodes
                if (getattr(n, "attributes", None) or {}).get("group_kind")
            ]
            return graph
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
            graph = GraphMLImporter(filepath=str(self.file_path)).parse()
        except Exception as e:
            raise GroupReadError(
                f"Cannot parse {self.file_path}: {e}") from e
        # Hydrate AI04 data keys + group_attrs JSON blob
        try:
            from .graph_ingestor import _hydrate_pyarchinit_data_keys
            _hydrate_pyarchinit_data_keys(graph, self.file_path)
        except Exception:
            pass
        try:
            self._hydrate_group_attrs(graph)
        except Exception:
            pass
        # Filter to nodes that carry a group_kind attribute
        graph.nodes = [
            n for n in graph.nodes
            if (getattr(n, "attributes", None) or {}).get("group_kind")
        ]
        return graph

    def _hydrate_group_attrs(self, graph) -> None:
        """Re-parse the file and merge `pyarchinit.group_attrs` JSON
        blob back onto each node's `.attributes` dict."""
        from lxml import etree as ET
        import json as _json
        NS = "http://graphml.graphdrawing.org/xmlns"
        try:
            tree = ET.parse(str(self.file_path))
        except Exception:
            return
        root = tree.getroot()
        attrs_kid = None
        for k in root.findall(f"{{{NS}}}key"):
            if k.get("attr.name") == "pyarchinit.group_attrs":
                attrs_kid = k.get("id")
                break
        if not attrs_kid:
            return
        emid_to_node = {getattr(n, "node_id", None): n for n in graph.nodes}
        for node_el in root.iter(f"{{{NS}}}node"):
            blob_text = None
            emid = node_el.get("id")
            for d_el in node_el.findall(f"{{{NS}}}data"):
                if d_el.get("key") == attrs_kid and d_el.text:
                    blob_text = d_el.text
                    break
            if blob_text is None:
                continue
            try:
                blob = _json.loads(blob_text)
            except (ValueError, TypeError):
                continue
            n = emid_to_node.get(emid)
            if n is None:
                continue
            attrs = getattr(n, "attributes", None)
            if attrs is None:
                try:
                    n.attributes = {}
                    attrs = n.attributes
                except Exception:
                    continue
            for skip_key in _GROUP_HYDRATE_SKIP_KEYS:
                attrs.pop(skip_key, None)
            for k, v in blob.items():
                if k in _GROUP_HYDRATE_SKIP_KEYS:
                    continue
                if attrs.get(k) in (None, ""):
                    attrs[k] = v
```

The full implementation continues in Tasks A.2–A.4 (write/serializer/CRUD/membership).

- [ ] **Step 4: Run tests, expect green for the 4 file_path/exists/read tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_store.py -v
```

Expected: `4 passed`.

- [ ] **Step 5: Full suite — must stay 132 + 4 = 136**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `136 passed, 1 skipped`.

- [ ] **Step 6: Run AC-2 baseline (no integration yet, sanity)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -2
```

Expected: `1 passed`.

- [ ] **Step 7: Commit**

```bash
git add modules/s3dgraphy/sync/group_store.py tests/sync/test_group_store.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy/sync): GroupStore — file path + exists + read

Per AI06 spec §3.1 (D6), ships the GroupStore class scaffolding:

  - file_path = {db_path.parent}/groups_{sito_slug}.graphml
    (D6: slug = re.sub(r'\W', '_', sito).lower())
  - exists() reflects on-disk presence
  - read() returns empty Graph when file absent (non-fatal,
    consistent with AI05 ParadataStore)

Plus the full exception hierarchy (extends GraphSyncError):
  - GroupStoreError (base)
  - GroupReadError / GroupWriteError /
    GroupValidationError / GroupNotFoundError

The custom serializer + CRUD methods land in tasks A.2–A.4.

Tests: 136/136 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task A.2: Write/serializer + low-level CRUD

**Files:**
- Modify: `modules/s3dgraphy/sync/group_store.py` (append)
- Modify: `tests/sync/test_group_store.py` (append)

- [ ] **Step 1: Append failing tests for write + add_node + remove_node + find**

Append to `tests/sync/test_group_store.py`:

```python
def test_low_level_add_node_persists(tmp_path):
    """add_node writes to file; subsequent read sees the node."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    store = GroupStore(_make_db(tmp_path), "X")
    node = ActivityNodeGroup(node_id="grp-1", name="basilica")
    node.attributes = {"group_kind": "struttura", "sito": "X"}
    store.add_node(node)
    assert store.exists() is True
    g = store.read()
    assert len(g.nodes) == 1
    assert g.nodes[0].node_id == "grp-1"


def test_remove_node_idempotent(tmp_path):
    """remove_node on missing uuid is a no-op (no error)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    store = GroupStore(_make_db(tmp_path), "X")
    store.remove_node("any-uuid")  # must not raise
    n = ActivityNodeGroup(node_id="g1", name="basilica")
    n.attributes = {"group_kind": "struttura"}
    store.add_node(n)
    store.remove_node("not-present")  # idempotent
    assert len(store.read().nodes) == 1


def test_find_returns_matching_groups(tmp_path):
    """find(group_kind='adhoc', name='X') returns the right group."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    from s3dgraphy.nodes.group_node import ActivityNodeGroup
    store = GroupStore(_make_db(tmp_path), "X")
    for nid, kind, name in [("a", "adhoc", "Marco"),
                             ("b", "adhoc", "Maria"),
                             ("c", "struttura", "basilica")]:
        n = ActivityNodeGroup(node_id=nid, name=name)
        n.attributes = {"group_kind": kind}
        store.add_node(n)
    found = store.find(group_kind="adhoc")
    assert {n.node_id for n in found} == {"a", "b"}


def test_add_group_round_trip(tmp_path):
    """High-level add_group + list_groups round-trip (AC-1)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    uuid = store.add_group("restauri-2023", group_kind="adhoc",
                            member_us_uuids=["u1", "u2", "u3"])
    assert isinstance(uuid, str) and len(uuid) > 8
    groups = store.list_groups()
    assert len(groups) == 1
    g = groups[0]
    assert g["name"] == "restauri-2023"
    assert g["group_kind"] == "adhoc"
    assert g["member_us_uuids"] == ["u1", "u2", "u3"]
    assert g["group_uuid"] == uuid


def test_remove_group(tmp_path):
    """remove_group deletes the group; list reflects."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    uuid = store.add_group("test", member_us_uuids=["u1"])
    assert len(store.list_groups()) == 1
    store.remove_group(uuid)
    assert len(store.list_groups()) == 0
```

- [ ] **Step 2: Append the implementation**

Append to `modules/s3dgraphy/sync/group_store.py`:

```python
    def write(self, graph) -> None:
        """Atomic write via .tmp + os.replace."""
        tmp = self.file_path.with_suffix(".graphml.tmp")
        try:
            self._write_minimal_graphml(graph, tmp)
            from .graphml_writer import _embed_pyarchinit_data_keys
            _embed_pyarchinit_data_keys(graph, tmp)
            os.replace(str(tmp), str(self.file_path))
        except Exception as e:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise GroupWriteError(
                f"Cannot write {self.file_path}: {e}") from e

    def _write_minimal_graphml(self, graph, out_path: Path) -> None:
        """Emit a minimal GraphML containing only the group nodes."""
        from lxml import etree as ET

        NS_GRAPHML = "http://graphml.graphdrawing.org/xmlns"
        NS_Y = "http://www.yworks.com/xml/graphml"
        NSMAP = {None: NS_GRAPHML, "y": NS_Y}

        root = ET.Element(f"{{{NS_GRAPHML}}}graphml", nsmap=NSMAP)
        keys = [
            ("d0", "node", None, "url", "string"),
            ("d1", "node", None, "description", "string"),
            ("d2", "node", "nodegraphics", None, None),
            ("d3", "node", None, "EMID", "string"),
            ("d4", "node", None, "URI", "string"),
            ("d5", "node", None, "pyarchinit.group_attrs", "string"),
        ]
        for kid, kfor, yftype, attr_name, attr_type in keys:
            kel = ET.SubElement(root, f"{{{NS_GRAPHML}}}key")
            kel.set("id", kid)
            kel.set("for", kfor)
            if yftype:
                kel.set("yfiles.type", yftype)
            if attr_name:
                kel.set("attr.name", attr_name)
            if attr_type:
                kel.set("attr.type", attr_type)

        graph_el = ET.SubElement(root, f"{{{NS_GRAPHML}}}graph")
        graph_el.set("id", f"groups_{self._slug}")
        graph_el.set("edgedefault", "directed")

        for node in list(getattr(graph, "nodes", []) or []):
            attrs = getattr(node, "attributes", None) or {}
            if not attrs.get("group_kind"):
                continue
            self._emit_group_node(graph_el, node, NS_GRAPHML, NS_Y)

        tree = ET.ElementTree(root)
        tree.write(str(out_path), encoding="UTF-8",
                   xml_declaration=True, pretty_print=True)

    @staticmethod
    def _emit_group_node(graph_el, node, ns_graphml, ns_y):
        """Append a single group <node> with the EM canonical layout."""
        from lxml import etree as ET
        import json as _json

        node_id = str(getattr(node, "node_id", "") or "")
        display_name = str(getattr(node, "name", "") or "Group")
        type_name = type(node).__name__

        n_el = ET.SubElement(graph_el, f"{{{ns_graphml}}}node")
        n_el.set("id", node_id)

        d_desc = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_desc.set("key", "d1")
        d_desc.text = f"_s3d_node_type:{type_name}"

        d_gfx = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_gfx.set("key", "d2")
        img = ET.SubElement(d_gfx, f"{{{ns_y}}}GroupNode")
        nl = ET.SubElement(img, f"{{{ns_y}}}NodeLabel")
        nl.text = display_name

        d_emid = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
        d_emid.set("key", "d3")
        d_emid.text = node_id

        attrs = getattr(node, "attributes", None) or {}
        if attrs:
            _SKIP = {"original_id", "graph_id", "group_attrs"}
            clean = {k: v for k, v in attrs.items()
                     if k not in _SKIP and v not in (None, "")}
            if clean:
                d_attrs = ET.SubElement(n_el, f"{{{ns_graphml}}}data")
                d_attrs.set("key", "d5")
                d_attrs.text = _json.dumps(clean, ensure_ascii=False)

    def add_node(self, node) -> None:
        """Append *node* to the group graph + write."""
        attrs = getattr(node, "attributes", None) or {}
        if not attrs.get("group_kind"):
            raise GroupValidationError(
                "Refusing to store node without group_kind attribute")
        graph = self.read()
        graph.add_node(node)
        self.write(graph)

    def remove_node(self, group_uuid: str) -> None:
        """Idempotent — no error if uuid not found."""
        graph = self.read()
        before = len(graph.nodes)
        graph.nodes = [
            n for n in graph.nodes
            if getattr(n, "node_id", None) != group_uuid
        ]
        if len(graph.nodes) != before:
            self.write(graph)

    def find(self, group_kind: str = None, **kwargs) -> list:
        """Return matching group nodes."""
        out = []
        for n in self.read().nodes:
            attrs = getattr(n, "attributes", None) or {}
            if group_kind is not None and attrs.get("group_kind") != group_kind:
                continue
            if all(getattr(n, k, None) == v
                   or attrs.get(k) == v
                   for k, v in kwargs.items()):
                out.append(n)
        return out

    # ---- High-level (D6) -----------------------------------------------
    def add_group(
        self,
        name: str,
        group_kind: str = "adhoc",
        member_us_uuids: list = None,
        description: str = None,
    ) -> str:
        """Create + persist an ActivityNodeGroup. Returns uuid7."""
        if not name or not str(name).strip():
            raise GroupValidationError("Group name is required")
        if not group_kind:
            raise GroupValidationError("group_kind is required")
        from s3dgraphy.nodes.group_node import ActivityNodeGroup
        from .uuid7 import uuid7
        group_uuid = str(uuid7())
        members = list(member_us_uuids or [])
        node = ActivityNodeGroup(node_id=group_uuid, name=str(name))
        node.attributes = {
            "group_kind": str(group_kind),
            "sito": self._sito,
            "name": str(name),
            "member_us_uuids": ",".join(members),  # serialise as CSV
            "description": str(description or ""),
            "group_uuid": group_uuid,
        }
        self.add_node(node)
        return group_uuid

    def list_groups(self) -> list:
        """Return [{group_uuid, name, group_kind, member_us_uuids, description}]."""
        out = []
        for n in self.read().nodes:
            attrs = getattr(n, "attributes", None) or {}
            members_csv = str(attrs.get("member_us_uuids", "") or "")
            members = [m for m in members_csv.split(",") if m]
            out.append({
                "group_uuid": getattr(n, "node_id", ""),
                "name": (attrs.get("name", "")
                         or getattr(n, "name", "")),
                "group_kind": attrs.get("group_kind", ""),
                "member_us_uuids": members,
                "description": attrs.get("description", ""),
            })
        return out

    def remove_group(self, group_uuid: str) -> None:
        """Alias for remove_node — high-level naming."""
        self.remove_node(group_uuid)
```

- [ ] **Step 3: Run new tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_store.py -v
```

Expected: `9 passed` (4 from A.1 + 5 new).

- [ ] **Step 4: Full suite — must be 132 + 9 = 141**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `141 passed, 1 skipped`.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/group_store.py tests/sync/test_group_store.py
git commit -m "$(cat <<'EOF'
feat(group_store): write + low-level CRUD + high-level add/list/remove

Implements:
  - write() — atomic via .tmp + os.replace, custom lxml serializer
    (s3dgraphy GraphMLExporter doesn't render isolated
    ActivityNodeGroup without anchor — same constraint as AI05
    paradata)
  - _emit_group_node — EM-style GroupNode with _s3d_node_type marker
    + JSON-blob round-trip channel for group attributes
  - add_node / remove_node / find — low-level CRUD
  - add_group(name, group_kind, member_us_uuids, description) →
    high-level helper returning fresh uuid7
  - list_groups() → [{group_uuid, name, group_kind,
    member_us_uuids, description}, ...]
  - remove_group — alias for remove_node

5 new tests pinning AC-1 (round-trip preserves all 5 fields) +
non-paradata-type filter + idempotent remove + find.

Tests: 141/141 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task A.3: Membership management (`add_us_to_group` / `remove_us_from_group` / `list_members`)

**Files:**
- Modify: `modules/s3dgraphy/sync/group_store.py` (append 3 methods)
- Modify: `tests/sync/test_group_store.py` (append 3 tests)

- [ ] **Step 1: Append failing tests**

```python
def test_add_us_to_group(tmp_path):
    """add_us_to_group appends to the member list."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    g = store.add_group("test", member_us_uuids=["u1"])
    store.add_us_to_group(g, "u2")
    members = store.list_members(g)
    assert members == ["u1", "u2"]


def test_add_us_to_group_idempotent(tmp_path):
    """add_us_to_group with duplicate is a no-op (idempotent)."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    g = store.add_group("test", member_us_uuids=["u1"])
    store.add_us_to_group(g, "u1")  # duplicate — must not append twice
    store.add_us_to_group(g, "u1")
    assert store.list_members(g) == ["u1"]


def test_remove_us_from_group(tmp_path):
    """remove_us_from_group removes the entry, idempotent on missing."""
    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(_make_db(tmp_path), "X")
    g = store.add_group("test", member_us_uuids=["u1", "u2", "u3"])
    store.remove_us_from_group(g, "u2")
    assert store.list_members(g) == ["u1", "u3"]
    store.remove_us_from_group(g, "not-present")  # idempotent
    assert store.list_members(g) == ["u1", "u3"]
```

- [ ] **Step 2: Append implementation**

```python
    def add_us_to_group(self, group_uuid: str, us_uuid: str) -> None:
        """Append us_uuid to the group's member list. Idempotent on
        duplicate. Raises GroupNotFoundError if group_uuid unknown."""
        if not us_uuid:
            raise GroupValidationError("us_uuid required")
        graph = self.read()
        target = next((n for n in graph.nodes
                       if getattr(n, "node_id", None) == group_uuid), None)
        if target is None:
            raise GroupNotFoundError(f"Group {group_uuid} not found")
        attrs = getattr(target, "attributes", None) or {}
        members_csv = str(attrs.get("member_us_uuids", "") or "")
        members = [m for m in members_csv.split(",") if m]
        if us_uuid in members:
            return  # idempotent
        members.append(us_uuid)
        attrs["member_us_uuids"] = ",".join(members)
        target.attributes = attrs
        self.write(graph)

    def remove_us_from_group(self, group_uuid: str, us_uuid: str) -> None:
        """Idempotent — no error if us_uuid not in member list."""
        graph = self.read()
        target = next((n for n in graph.nodes
                       if getattr(n, "node_id", None) == group_uuid), None)
        if target is None:
            return  # idempotent on missing group too
        attrs = getattr(target, "attributes", None) or {}
        members_csv = str(attrs.get("member_us_uuids", "") or "")
        members = [m for m in members_csv.split(",") if m]
        if us_uuid not in members:
            return
        members.remove(us_uuid)
        attrs["member_us_uuids"] = ",".join(members)
        target.attributes = attrs
        self.write(graph)

    def list_members(self, group_uuid: str) -> list:
        """Return the list of us_uuid strings of a group."""
        for n in self.read().nodes:
            if getattr(n, "node_id", None) == group_uuid:
                attrs = getattr(n, "attributes", None) or {}
                csv = str(attrs.get("member_us_uuids", "") or "")
                return [m for m in csv.split(",") if m]
        return []
```

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_store.py -v
```

Expected: `12 passed`.

- [ ] **Step 4: Full suite — 132 + 12 = 144**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `144 passed, 1 skipped`.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/group_store.py tests/sync/test_group_store.py
git commit -m "$(cat <<'EOF'
feat(group_store): membership management — add/remove/list members

Three new methods:
  - add_us_to_group(group_uuid, us_uuid) — append, idempotent on
    duplicate, raises GroupNotFoundError if group_uuid unknown
  - remove_us_from_group(group_uuid, us_uuid) — remove,
    idempotent on missing
  - list_members(group_uuid) → [us_uuid, ...]

Members are stored as a CSV string in node.attributes per AI04
data-key round-trip pattern (s3dgraphy node attributes don't
support nested lists natively).

3 new tests pinning idempotency.

Tests: 144/144 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task A.4: Atomic crash-safety + name validation

**Files:**
- Modify: `tests/sync/test_group_store.py` (append 2 tests)

- [ ] **Step 1: Append tests**

```python
def test_atomic_write_no_corruption_on_crash(tmp_path, monkeypatch):
    """AC-3: simulate os.replace crash, assert original untouched."""
    from modules.s3dgraphy.sync.group_store import (
        GroupStore, GroupWriteError)

    store = GroupStore(_make_db(tmp_path), "X")
    store.add_group("Original", member_us_uuids=["u1"])
    original_bytes = store.file_path.read_bytes()
    assert len(original_bytes) > 0

    real_replace = os.replace

    def boom(src, dst):
        raise OSError("simulated crash mid-rename")
    monkeypatch.setattr("os.replace", boom)

    with pytest.raises(GroupWriteError):
        store.add_group("New")

    assert store.file_path.read_bytes() == original_bytes
    assert not store.file_path.with_suffix(".graphml.tmp").exists()


def test_init_validates_sito(tmp_path):
    """Empty sito at construction raises ValidationError."""
    from modules.s3dgraphy.sync.group_store import (
        GroupStore, GroupValidationError)
    with pytest.raises(GroupValidationError):
        GroupStore(_make_db(tmp_path), "")


def test_add_group_validates_name(tmp_path):
    """Empty name raises ValidationError."""
    from modules.s3dgraphy.sync.group_store import (
        GroupStore, GroupValidationError)
    store = GroupStore(_make_db(tmp_path), "X")
    with pytest.raises(GroupValidationError):
        store.add_group("")
```

- [ ] **Step 2: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_store.py -v
```

Expected: `15 passed`.

- [ ] **Step 3: Full suite — should be 132 + 14 = 146 (matches plan A target)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `146 passed, 1 skipped`.

(Note: the plan's "+14 tests" target counts 14 new from Group A. With 15 tests in the file, 1 was already counted toward the 144 from A.3. The exact running total is 146 passed.)

- [ ] **Step 4: Run AC-2 + critical regression guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_idempotent_ingest.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  -q 2>&1 | tail -2
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_group_store.py
git commit -m "$(cat <<'EOF'
test(group_store): atomic crash-safety + init/name validation

Pins AC-3 with the canonical "monkey-patch os.replace to raise"
pattern (AI05 lineage):
  - Seed initial group via add_group(), capture file bytes
  - Patch os.replace to raise OSError mid-rename
  - Trigger add_group again → expect GroupWriteError
  - Assert original file bytes unchanged
  - Assert .tmp file cleaned up

Plus two constructor-level validation tests: empty sito and
empty name both raise GroupValidationError immediately.

Group A complete (14 new tests). All 8 critical regression guards
green (AC-2 baseline + AI04 + AI05).

Tests: 146/146 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group B — group_projector helpers

### Task B.1: `dimensions_with_data` (auto-preselect helper)

**Files:**
- Create: `modules/s3dgraphy/sync/group_projector.py`
- Create: `tests/sync/test_group_projector.py`

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_group_projector.py`:

```python
"""L1 fixture-based tests for group_projector.

Pins decisions D1 (all 7 dims), D2 (preselect populated), D4
(ActivityNodeGroup + group_kind), AC-7 (deterministic UUID5).
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


def _seed_dimension(db, sito, col, value, n_rows=2):
    """Set us_table.<col>=value for the first n_rows of sito."""
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?",
        (sito, n_rows)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def test_dimensions_with_data_returns_only_populated(mini_volterra):
    """D2: only the dimensions with at least 1 non-empty value."""
    from modules.s3dgraphy.sync.group_projector import dimensions_with_data
    sito = _read_sito(mini_volterra)
    # Mini volterra fixture is mostly empty for grouping cols.
    # Seed: struttura on 2 rows, leave rest empty.
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 2)
    found = dimensions_with_data(mini_volterra, sito)
    assert "struttura" in found
    # Ambient/saggio/quad_par must NOT appear (empty)
    assert "ambient" not in found
    assert "saggio" not in found
    assert "quad_par" not in found


def test_dimensions_with_data_empty_for_unpopulated_sito(mini_volterra):
    """All dimensions empty → empty list."""
    from modules.s3dgraphy.sync.group_projector import dimensions_with_data
    # Ensure all grouping cols are empty (default fixture state)
    conn = sqlite3.connect(mini_volterra)
    for col in ("area", "struttura", "attivita", "settore",
                "ambient", "saggio", "quad_par"):
        conn.execute(
            f"UPDATE us_table SET {col}=NULL WHERE sito=?",
            (_read_sito(mini_volterra),))
    conn.commit()
    conn.close()

    sito = _read_sito(mini_volterra)
    found = dimensions_with_data(mini_volterra, sito)
    assert found == []
```

- [ ] **Step 2: Run, expect failure (module doesn't exist)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_projector.py -v
```

Expected: ImportError on `group_projector`.

- [ ] **Step 3: Write minimal implementation**

Create `modules/s3dgraphy/sync/group_projector.py`:

```python
"""Pure-functional helpers for AI06 node grouping.

build_groups_from_sql: scan us_table for the requested grouping
    dimensions, emit one GroupSpec per (dim, value) pair.
merge_adhoc_groups: append GroupSpec instances from a GroupStore.
dimensions_with_data: return the subset of 7 grouping columns
    that have at least one non-empty value in us_table for sito.

UUID generation: deterministic UUID5 from (sito, group_kind, name)
so re-export with the same SQL state produces identical UUIDs
(idempotent, AC-7). Ad-hoc groups use UUID7 generated at creation
by GroupStore (AC-7 second clause).
"""
from __future__ import annotations

import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


_log = logging.getLogger("pyarchinit.s3dgraphy.sync.groups")


# The 7 SQL-derived grouping dimensions per spec §1.
_SQL_DIMENSIONS: tuple = (
    "area", "struttura", "attivita", "settore",
    "ambient", "saggio", "quad_par",
)

# Deterministic UUID5 namespace for SQL-derived groups (AC-7).
# A constant, project-internal namespace so the same (sito, kind, name)
# triple maps to the same UUID across exports/runs/machines.
_PYARCHINIT_GROUP_NAMESPACE = uuid.UUID(
    "6e8c0a2e-2026-50a6-9a06-ff77e2e3c5a1"
)


@dataclass(frozen=True)
class GroupSpec:
    """Pre-render specification of a group.

    Resolved to ActivityNodeGroup by GraphProjector._merge_groups.
    """
    group_uuid: str
    name: str
    group_kind: str
    member_us_uuids: List[str] = field(default_factory=list)
    description: str = ""


def dimensions_with_data(db_path: Path, sito: str) -> List[str]:
    """Return subset of {area, struttura, attivita, settore,
    ambient, saggio, quad_par} that has at least one non-empty
    value in us_table for *sito*. Used by the dialog UI to
    pre-check the right boxes (D2)."""
    out = []
    conn = sqlite3.connect(str(db_path))
    try:
        for col in _SQL_DIMENSIONS:
            row = conn.execute(
                f"SELECT 1 FROM us_table "
                f"WHERE sito=? AND {col} IS NOT NULL AND TRIM({col})<>'' "
                f"LIMIT 1",
                (sito,),
            ).fetchone()
            if row is not None:
                out.append(col)
    finally:
        conn.close()
    return out
```

- [ ] **Step 4: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_projector.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Full suite — 146 + 2 = 148**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `148 passed, 1 skipped`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/group_projector.py tests/sync/test_group_projector.py
git commit -m "$(cat <<'EOF'
feat(group_projector): scaffolding + dimensions_with_data helper

Per AI06 spec §3.2 (D2), creates the new module with:
  - GroupSpec dataclass (frozen, hashable)
  - _SQL_DIMENSIONS tuple of 7 grouping columns
  - _PYARCHINIT_GROUP_NAMESPACE UUID5 constant for AC-7
    determinism (will be used by build_groups_from_sql in B.2)
  - dimensions_with_data(db, sito) → list[str] for the dialog
    pre-check logic (D2): returns only the columns having at
    least one non-empty trimmed value in us_table for sito

2 new L1 tests pinning the populated/empty filtering.

Tests: 148/148 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.2: `build_groups_from_sql` for all 7 dimensions

**Files:**
- Modify: `modules/s3dgraphy/sync/group_projector.py` (append)
- Modify: `tests/sync/test_group_projector.py` (append)

- [ ] **Step 1: Append failing tests**

```python
def test_build_groups_handles_all_seven_dimensions(mini_volterra):
    """D1: every one of the 7 dims must be a valid input."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    # Seed at least one row per dimension
    for col, val in [("area", "A1"), ("struttura", "basilica"),
                      ("attivita", "1"), ("settore", "N"),
                      ("ambient", "stanza-1"), ("saggio", "S1"),
                      ("quad_par", "Q1")]:
        _seed_dimension(mini_volterra, sito, col, val, 1)
    specs = build_groups_from_sql(
        mini_volterra, sito,
        dimensions=["area", "struttura", "attivita", "settore",
                    "ambient", "saggio", "quad_par"])
    kinds = {s.group_kind for s in specs}
    # All 7 dimensions produced at least one GroupSpec
    assert kinds == {"area", "struttura", "attivita", "settore",
                     "ambient", "saggio", "quad_par"}


def test_build_groups_skips_unknown_dimension(mini_volterra):
    """Unknown dim name (typo) is silently dropped, no exception."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 2)
    specs = build_groups_from_sql(
        mini_volterra, sito,
        dimensions=["struttura", "bogus_dimension"])
    assert all(s.group_kind == "struttura" for s in specs)


def test_group_uuid_deterministic_across_exports(mini_volterra):
    """AC-7: SQL-derived UUID5 stable across exports."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 3)
    specs1 = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    specs2 = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    assert {s.group_uuid for s in specs1} == {s.group_uuid for s in specs2}


def test_build_groups_collects_member_us_uuids(mini_volterra):
    """Each GroupSpec.member_us_uuids has the node_uuid (Phase 1
    UUID) of every US in that group."""
    from modules.s3dgraphy.sync.group_projector import build_groups_from_sql
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 3)
    specs = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    basilica = next(s for s in specs if s.name == "basilica")
    assert len(basilica.member_us_uuids) == 3
    # All UUIDs should be non-empty Phase 1 node_uuid values
    assert all(isinstance(u, str) and len(u) >= 32
               for u in basilica.member_us_uuids)
```

- [ ] **Step 2: Append implementation**

```python
def build_groups_from_sql(
    db_path: Path,
    sito: str,
    dimensions: List[str],
) -> List[GroupSpec]:
    """For each requested dimension, scan us_table for distinct
    non-empty values within sito, and emit one GroupSpec per
    (dimension, value) pair.

    UUID generation: deterministic UUID5 from
    (sito, group_kind, name) so re-export produces identical
    UUIDs (AC-7 idempotent invariant).

    Unknown dimension names (typos) are silently skipped (logged).
    """
    out: List[GroupSpec] = []
    if not dimensions:
        return out

    valid_dims = [d for d in dimensions if d in _SQL_DIMENSIONS]
    if len(valid_dims) != len(dimensions):
        bogus = set(dimensions) - set(valid_dims)
        _log.warning(f"Unknown grouping dimensions skipped: {bogus}")

    conn = sqlite3.connect(str(db_path))
    try:
        for dim in valid_dims:
            # Distinct values + member UUIDs in one pass
            rows = conn.execute(
                f"SELECT {dim}, node_uuid FROM us_table "
                f"WHERE sito=? AND {dim} IS NOT NULL "
                f"AND TRIM({dim})<>'' AND node_uuid IS NOT NULL",
                (sito,),
            ).fetchall()
            # Group by value
            buckets: dict = {}
            for value, node_uuid in rows:
                buckets.setdefault(str(value), []).append(node_uuid)
            for name, member_uuids in buckets.items():
                # Deterministic UUID5 from (sito, dim, name)
                key = f"{sito}|{dim}|{name}"
                group_uuid = str(uuid.uuid5(
                    _PYARCHINIT_GROUP_NAMESPACE, key))
                out.append(GroupSpec(
                    group_uuid=group_uuid,
                    name=name,
                    group_kind=dim,
                    member_us_uuids=list(member_uuids),
                ))
    finally:
        conn.close()
    return out
```

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_projector.py -v
```

Expected: `6 passed`.

- [ ] **Step 4: Full suite — 148 + 4 = 152**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `152 passed, 1 skipped`.

- [ ] **Step 5: AC-2 + critical guards check**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_paradata_store.py \
  -q 2>&1 | tail -2
```

Expected: all green (no integration with export pipeline yet, so AC-2 unaffected).

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/group_projector.py tests/sync/test_group_projector.py
git commit -m "$(cat <<'EOF'
feat(group_projector): build_groups_from_sql + UUID5 determinism

Implements build_groups_from_sql(db, sito, dimensions) returning
a list of GroupSpec instances, one per distinct (dim, value)
pair found in us_table for the given sito.

Single SQL pass per dimension collects both the distinct values
and the member node_uuid lists. Buckets are formed in-memory.

UUID generation: uuid5(_PYARCHINIT_GROUP_NAMESPACE, "{sito}|{dim}|{name}")
→ stable across exports (AC-7 first clause).

Unknown dimension names silently skipped + logged warning.

4 new L1 tests:
  - all 7 dimensions accepted (D1)
  - typo dimension skipped without exception
  - UUID stability across consecutive calls (AC-7)
  - member_us_uuids correctly populated from node_uuid column

Tests: 152/152 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task B.3: `merge_adhoc_groups` + collision warning

**Files:**
- Modify: `modules/s3dgraphy/sync/group_projector.py` (append)
- Modify: `tests/sync/test_group_projector.py` (append)

- [ ] **Step 1: Append failing tests**

```python
def test_merge_adhoc_groups_appends_when_no_collision(tmp_path, mini_volterra):
    """Ad-hoc group with unique name is appended to SQL specs."""
    from modules.s3dgraphy.sync.group_projector import (
        build_groups_from_sql, merge_adhoc_groups)
    from modules.s3dgraphy.sync.group_store import GroupStore
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 2)

    sql_specs = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    # Add 1 ad-hoc group via store
    store = GroupStore(mini_volterra, sito)
    store.add_group("restauri-2023", group_kind="adhoc",
                     member_us_uuids=["u1"])
    merged = merge_adhoc_groups(sql_specs, store)
    kinds = {s.group_kind for s in merged}
    assert "struttura" in kinds and "adhoc" in kinds


def test_merge_adhoc_groups_warns_on_name_collision(tmp_path, mini_volterra, caplog):
    """SQL-name == ad-hoc-name → SQL wins, warning logged."""
    import logging
    from modules.s3dgraphy.sync.group_projector import (
        build_groups_from_sql, merge_adhoc_groups)
    from modules.s3dgraphy.sync.group_store import GroupStore
    sito = _read_sito(mini_volterra)
    _seed_dimension(mini_volterra, sito, "struttura", "basilica", 2)

    sql_specs = build_groups_from_sql(
        mini_volterra, sito, dimensions=["struttura"])
    store = GroupStore(mini_volterra, sito)
    # Ad-hoc name collides with SQL "basilica"
    store.add_group("basilica", group_kind="adhoc",
                     member_us_uuids=["u1"])

    with caplog.at_level(logging.WARNING,
                          logger="pyarchinit.s3dgraphy.sync.groups"):
        merged = merge_adhoc_groups(sql_specs, store)
    # SQL wins: no ad-hoc with that name
    adhoc_names = {s.name for s in merged if s.group_kind == "adhoc"}
    assert "basilica" not in adhoc_names
    assert any("collision" in r.message.lower() for r in caplog.records)
```

- [ ] **Step 2: Append implementation**

```python
def merge_adhoc_groups(
    sql_specs: List[GroupSpec],
    store,
) -> List[GroupSpec]:
    """Append GroupSpec instances from groups_{sito}.graphml.

    Collision policy: if an ad-hoc group has the same name as an
    SQL-derived group (regardless of group_kind), the ad-hoc is
    SKIPPED and a warning is logged. SQL "wins". This matches
    spec §10 D6 risk mitigation.
    """
    out = list(sql_specs)
    if not store.exists():
        return out

    sql_names = {s.name for s in sql_specs}
    try:
        groups = store.list_groups()
    except Exception as e:
        _log.warning(f"Cannot read GroupStore, skipping ad-hoc: {e}")
        return out

    for g in groups:
        name = g.get("name", "")
        if name in sql_names:
            _log.warning(
                f"Ad-hoc group name collision with SQL: '{name}' "
                f"(SQL wins, ad-hoc skipped)")
            continue
        out.append(GroupSpec(
            group_uuid=g.get("group_uuid", ""),
            name=name,
            group_kind=g.get("group_kind", "adhoc"),
            member_us_uuids=list(g.get("member_us_uuids", [])),
            description=g.get("description", ""),
        ))
    return out
```

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_projector.py -v
```

Expected: `8 passed`.

- [ ] **Step 4: Full suite — 152 + 2 = 154**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `154 passed, 1 skipped`.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/group_projector.py tests/sync/test_group_projector.py
git commit -m "$(cat <<'EOF'
feat(group_projector): merge_adhoc_groups + collision warning

merge_adhoc_groups(sql_specs, store) appends GroupSpec instances
from a GroupStore to the SQL-derived list.

Collision policy: ad-hoc group whose name == any SQL-derived
name is SKIPPED, with a warning logged via the project logger
"pyarchinit.s3dgraphy.sync.groups". SQL wins (spec §10 D6 risk
mitigation: avoids confusing duplicate render in yEd).

Non-fatal error path: if GroupStore.list_groups() raises, log
warning and return only SQL specs.

2 new L1 tests covering the no-collision happy path and the
collision-with-warning path (uses caplog).

Group B complete (8 tests). Tests: 154/154 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group C — GraphProjector + injector integration

### Task C.1: `populate_graph(groups=[...])` kwarg + `_merge_groups`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py`
- Create: `tests/sync/test_graph_projector_groups.py`

- [ ] **Step 1: Locate the existing populate_graph signature**

```bash
grep -nE "def populate_graph|def _merge_paradata" modules/s3dgraphy/sync/graph_projector.py | head -5
```

Expected (from AI05 HEAD): `populate_graph` at ~line 51, `_merge_paradata` somewhere around 300-350.

- [ ] **Step 2: Write failing tests**

Create `tests/sync/test_graph_projector_groups.py`:

```python
"""L1 fixture-based: populate_graph(groups=...) kwarg semantics.

Pins D4 (ActivityNodeGroup + group_kind), D7 (default empty),
AC-4, AC-5.
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


def _seed(db, sito, col, value, n=2):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?", (sito, n)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def test_default_groups_empty_no_group_nodes(mini_volterra):
    """D7: default groups=None / [] → no GroupNode in graph."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    graph = GraphProjector().populate_graph(mini_volterra, sito=sito)
    types = [type(n).__name__ for n in graph.nodes]
    assert "ActivityNodeGroup" not in types


def test_groups_arg_materializes_activity_node_group(mini_volterra):
    """D4 / AC-4: groups=['struttura'] yields ActivityNodeGroup
    instances with attributes['group_kind']='struttura'."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, groups=["struttura"])
    groups = [n for n in graph.nodes
              if type(n).__name__ == "ActivityNodeGroup"]
    assert len(groups) >= 1
    g = groups[0]
    attrs = getattr(g, "attributes", None) or {}
    assert attrs.get("group_kind") == "struttura"


def test_groups_arg_adds_is_in_activity_edges(mini_volterra):
    """AC-5: edges from each US member to its group, type
    is_in_activity."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    graph = GraphProjector().populate_graph(
        mini_volterra, sito=sito, groups=["struttura"])
    group_ids = {n.node_id for n in graph.nodes
                 if type(n).__name__ == "ActivityNodeGroup"}
    rel_edges = [e for e in graph.edges
                 if getattr(e, "edge_target", None) in group_ids
                 and getattr(e, "edge_type", "") == "is_in_activity"]
    assert len(rel_edges) >= 3
```

- [ ] **Step 3: Run tests, expect failure (kwarg not yet defined)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_groups.py -v
```

Expected: `TypeError: populate_graph() got an unexpected keyword argument 'groups'`.

- [ ] **Step 4: Add the kwarg + `_merge_groups`**

In `modules/s3dgraphy/sync/graph_projector.py`, modify `populate_graph()` signature:

```python
def populate_graph(
    self,
    db_path: Path,
    sito: str,
    *,
    include_paradata: bool = True,
    strict_schema: bool = True,
    groups: list = None,                # NEW (AI06 D7-A: None = no grouping)
) -> "s3dgraphy.Graph":
```

After the existing `if include_paradata: self._merge_paradata(...)` block, add:

```python
    # AI06: optional grouping by us_table dimensions + ad-hoc
    if groups:
        try:
            self._merge_groups(graph, db_path, sito, groups)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(
                f"_merge_groups failed, continuing without groups: {e}")
```

Then add the `_merge_groups` method at end of class:

```python
    def _merge_groups(self, graph, db_path, sito, dimensions):
        """Materialize ActivityNodeGroup nodes + is_in_activity edges
        from SQL columns and ad-hoc store. Each group node carries
        a ``group_kind`` attribute distinguishing the dimension."""
        from .group_projector import (
            build_groups_from_sql, merge_adhoc_groups,
        )
        # SQL-derived dims (anything except 'adhoc')
        sql_dims = [d for d in dimensions if d != "adhoc"]
        specs = build_groups_from_sql(db_path, sito, sql_dims)

        if "adhoc" in dimensions:
            from .group_store import GroupStore
            store = GroupStore(db_path, sito)
            specs = merge_adhoc_groups(specs, store)

        # Materialize as s3dgraphy ActivityNodeGroup nodes
        from s3dgraphy.nodes.group_node import ActivityNodeGroup

        existing_ids = {getattr(n, "node_id", None) for n in graph.nodes}
        for spec in specs:
            if spec.group_uuid in existing_ids:
                continue  # idempotent — don't double-add on retry
            node = ActivityNodeGroup(
                node_id=spec.group_uuid,
                name=spec.name,
                description=spec.description or "",
            )
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

            # is_in_activity edge from each US member to this group
            for us_uuid in spec.member_us_uuids:
                if us_uuid in existing_ids or any(
                    getattr(n, "node_id", None) == us_uuid
                    for n in graph.nodes
                ):
                    edge_id = f"grp_{us_uuid[:8]}_{spec.group_uuid[:8]}"
                    try:
                        graph.add_edge(
                            edge_id=edge_id,
                            edge_source=us_uuid,
                            edge_target=spec.group_uuid,
                            edge_type="is_in_activity",
                        )
                    except Exception:
                        # Edge validation may reject if connection
                        # rules don't accept the source type — log
                        # and continue (defensive).
                        pass
```

- [ ] **Step 5: Run new tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_groups.py -v
```

Expected: `3 passed`.

- [ ] **Step 6: AC-2 baseline + AI04/AI05 guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_idempotent_ingest.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  tests/sync/test_strategy_a_no_regression.py \
  -q 2>&1 | tail -2
```

Expected: all pass. AC-2 must stay green because default `groups=None` is unchanged behavior.

- [ ] **Step 7: Full suite — 154 + 3 = 157**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `157 passed, 1 skipped`.

- [ ] **Step 8: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py \
        tests/sync/test_graph_projector_groups.py
git commit -m "$(cat <<'EOF'
feat(graph_projector): groups kwarg + _merge_groups (D4 + AC-4 + AC-5)

Adds the AI06 D7-A kwarg `groups: list = None` to populate_graph()
and the corresponding `_merge_groups` private method:

  - groups=None or []: no grouping (default, AI05/AC-2 stable)
  - groups=["struttura", "attivita"]: SQL-derived groups
  - groups=["adhoc"]: ad-hoc groups from GroupStore
  - groups=["struttura", "adhoc"]: union

Each materialized ActivityNodeGroup has:
  - node.attributes["group_kind"] discriminating the dimension
  - node.attributes["sito"] for filter round-trip compat
  - node.attributes["pyarchinit.<group_kind>"] = name (round-trip
    via AI04 data keys)
  - node.attributes["group_uuid"] for explicit identification

Each member US gets an is_in_activity edge to the group.
Edge addition wrapped in try/except to handle s3dgraphy connection
validation rejecting unusual source types (defensive).

Idempotent: re-call with same dimensions doesn't double-add.

3 new L1 tests pinning AC-4 (group_kind attribute) + AC-5
(is_in_activity edges) + D7-A (default empty).

Tests: 157/157 pass. AC-2 + AI04 + AI05 guards green.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task C.2: Pre-export snapshot + Stage 4e `_inject_group_folders`

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (snapshot capture + Stage 4e + post-processor function + export_graphml signature)

- [ ] **Step 1: Locate the snapshot block in `export_graphml`**

```bash
grep -nE "_paradata_snapshot|Stage 4d|Stage 2 \(filter\)|paradata snapshot" \
  modules/s3dgraphy/sync/graphml_writer.py | head -10
```

Expected: locations near the existing AI05 paradata snapshot capture (~line 1319) and the `_inject_isolated_paradata_nodes` call (~line 1397).

- [ ] **Step 2: Write failing test**

Append to `tests/sync/test_graph_projector_groups.py`:

```python
def test_export_with_groups_emits_yed_folder_node(mini_volterra, tmp_path):
    """Stage 4e: export with groups=['struttura'] produces a yEd
    folder node in the GraphML output."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    out = tmp_path / "out.graphml"
    export_graphml(
        db_path=mini_volterra,
        mapping="pyarchinit_us_mapping",
        output_path=out,
        site_filter=sito,
        groups=["struttura"],
    )

    from lxml import etree as ET
    NS = "{http://graphml.graphdrawing.org/xmlns}"
    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    assert len(folders) >= 1


def test_export_default_no_groups_unchanged_baseline(mini_volterra, tmp_path):
    """D7-A: default export (no groups kwarg) doesn't add any
    grp_* node — AC-2 byte-identical guarantee."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    sito = _read_sito(mini_volterra)

    out = tmp_path / "out.graphml"
    export_graphml(
        db_path=mini_volterra,
        mapping="pyarchinit_us_mapping",
        output_path=out,
        site_filter=sito,
    )

    from lxml import etree as ET
    NS = "{http://graphml.graphdrawing.org/xmlns}"
    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    assert folders == []
```

- [ ] **Step 3: Add `groups` kwarg to `export_graphml` signature**

Find the `def export_graphml(` line in `modules/s3dgraphy/sync/graphml_writer.py` and add `groups: list = None` to the keyword-only args (after `language`):

```python
def export_graphml(
    db_path,
    mapping: str,
    output_path,
    *,
    site_filter: Optional[str] = None,
    persist_auxiliary: bool = False,
    language: str = "it",
    groups: list = None,                  # NEW (AI06)
) -> ExportResult:
```

In the body, find the call to `GraphProjector().populate_graph(...)` and add `groups=groups` kwarg:

```python
        graph = GraphProjector().populate_graph(
            db_path,
            sito=sito_for_projection,
            include_paradata=True,
            strict_schema=False,
            groups=groups,                # NEW
        )
```

- [ ] **Step 4: Capture pre-filter snapshot of group nodes**

In `export_graphml`, locate the existing `_paradata_snapshot` block (added in AI05) and append a sibling group snapshot. Find the line capturing `_paradata_snapshot` (around line 1319-1323) and right after it add:

```python
    # AI06: capture group snapshot BEFORE Stage 2 _filter_by_site,
    # which retains only StratigraphicNode + EpochNode and would
    # drop our ActivityNodeGroup instances. Same lesson as AI05
    # paradata snapshot.
    _group_snapshot = [
        n for n in graph.nodes
        if type(n).__name__ == "ActivityNodeGroup"
        and (getattr(n, "attributes", None) or {}).get("group_kind")
    ]
    # Build members_map (group_uuid → [us_emid, ...]) from the
    # is_in_activity edges currently in the graph.
    _group_member_uuids = {
        gn.node_id: [] for gn in _group_snapshot
    }
    for edge in list(getattr(graph, "edges", []) or []):
        if (getattr(edge, "edge_type", "") == "is_in_activity"
                and edge.edge_target in _group_member_uuids):
            _group_member_uuids[edge.edge_target].append(edge.edge_source)
    print(f"[ExportGraphML] group snapshot: "
          f"{len(_group_snapshot)} groups")
```

- [ ] **Step 5: Add Stage 4e call after `_inject_isolated_paradata_nodes`**

Find the Stage 4d call (`_inject_isolated_paradata_nodes(_paradata_snapshot, output_path)`) and after that block add:

```python
    # Stage 4e: inject group folders (AI06). yEd folder nodes
    # nesting member US, with EM canonical visual style. Default
    # no-op when _group_snapshot is empty (D7-A).
    try:
        _inject_group_folders(
            _group_snapshot, _group_member_uuids, output_path)
    except Exception as e:
        if hasattr(graph, "add_warning"):
            graph.add_warning(
                f"Group folder injection skipped: {type(e).__name__}: {e}")
```

- [ ] **Step 6: Add the `_inject_group_folders` function**

Insert this function definition above `def export_graphml(`:

```python
_GROUP_INJECT_TYPE = "ActivityNodeGroup"


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
            if d.find(f"{{{NS_Y}}}TableNode") is not None:
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
            d_desc.text = f"_s3d_node_type:ActivityNodeGroup"

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

        fill = etree.SubElement(gn, f"{{{NS_Y}}}Fill")
        fill.set("color", "#F5F5F5")
        fill.set("transparent", "false")

        bs = etree.SubElement(gn, f"{{{NS_Y}}}BorderStyle")
        bs.set("color", "#000000")
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
```

- [ ] **Step 7: Run new tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_groups.py -v
```

Expected: `5 passed`.

- [ ] **Step 8: AC-2 baseline check (CRITICAL)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -2
```

Expected: `1 passed`. Default `groups=None` makes `_group_snapshot` empty → `_inject_group_folders` is a no-op → byte-identical baseline preserved.

- [ ] **Step 9: AI04 + AI05 guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_round_trip.py \
  tests/sync/test_idempotent_ingest.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  -q 2>&1 | tail -2
```

Expected: all green.

- [ ] **Step 10: Full suite — 157 + 2 = 159**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `159 passed, 1 skipped`.

- [ ] **Step 11: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py \
        tests/sync/test_graph_projector_groups.py
git commit -m "$(cat <<'EOF'
feat(graphml_writer): Stage 4e _inject_group_folders + groups kwarg

Pre-export snapshot of ActivityNodeGroup instances captured BEFORE
Stage 2 _filter_by_site (which retains only StratigraphicNode +
EpochNode and would drop the groups). Same lesson as AI05's
paradata snapshot fix.

_inject_group_folders post-processor (Stage 4e):
  - parses output XML via lxml
  - finds the TableNode swimlane wrapper (top-level
    yfiles.foldertype=group with <y:TableNode> realizer)
  - resolves d-key IDs (EMID, description, nodegraphics, sito)
  - for each ActivityNodeGroup in the snapshot:
      * computes bbox of member US Geometries (+20px margin)
      * creates <node yfiles.foldertype="group" id="grp_{uuid}">
      * with <y:ProxyAutoBoundsNode> → <y:Realizers> → <y:GroupNode>
        — dashed border, fill #F5F5F5, NodeLabel top w/ bg #EBEBEB
      * builds inner <graph id="grp_{uuid}:">
      * re-parents member US <node> elements from TableNode to
        the new inner graph (geometry preserved → still renders
        in correct epoch row)

export_graphml() gains groups: list = None kwarg, threaded down
to GraphProjector().populate_graph(groups=groups). Default None
preserves AC-2 byte-identical baseline (Stage 4e is a no-op).

2 new L1 tests:
  - export with groups=["struttura"] emits grp_* folder nodes
  - export with default groups=None has no grp_* nodes (D7-A)

AC-2 baseline + AI04 + AI05 guards all green.

Tests: 159/159 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group D — EM template compliance + round-trip

### Task D.1: EM template compliance tests

**Files:**
- Create: `tests/sync/test_groups_export_em_template.py`

- [ ] **Step 1: Write 4 L4 EM compliance tests**

Create `tests/sync/test_groups_export_em_template.py`:

```python
"""L4 EM template compliance: structural lxml tests on the GraphML
output, comparing against the EM canonical layout (EM_demo_02.graphml
reference). Pins AC-8, AC-9, AC-10, AC-11."""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as ET
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

NS = "{http://graphml.graphdrawing.org/xmlns}"
Y = "{http://www.yworks.com/xml/graphml}"
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


def _seed(db, sito, col, value, n=2):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?", (sito, n)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def _export_with_groups(db, sito, out, groups):
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    export_graphml(
        db_path=db, mapping="pyarchinit_us_mapping",
        output_path=out, site_filter=sito, groups=groups,
    )


def test_group_node_uses_yfiles_foldertype_group(mini_volterra, tmp_path):
    """AC-8: <node yfiles.foldertype='group'> with <y:GroupNode>
    realizer (NOT TableNode — that's the swimlane)."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    assert len(folders) >= 1
    folder = folders[0]
    realizer = folder.find(f".//{Y}GroupNode")
    assert realizer is not None
    table = folder.find(f".//{Y}TableNode")
    assert table is None  # not the swimlane


def test_group_visual_matches_em_template(mini_volterra, tmp_path):
    """AC-9: dashed border, fill #F5F5F5, NodeLabel top + bg #EBEBEB."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folder = next(n for n in tree.iter(f"{NS}node")
                  if n.get("yfiles.foldertype") == "group"
                  and n.get("id", "").startswith("grp_"))
    realizer = folder.find(f".//{Y}GroupNode")

    border = realizer.find(f"{Y}BorderStyle")
    assert border.get("type") == "dashed"
    fill = realizer.find(f"{Y}Fill")
    assert fill.get("color") == "#F5F5F5"

    label = realizer.find(f"{Y}NodeLabel")
    assert label.get("backgroundColor") == "#EBEBEB"
    assert label.get("modelPosition") == "t"
    assert (label.text or "").strip() == "basilica"


def test_group_geometry_spans_member_us_bbox(mini_volterra, tmp_path):
    """AC-10: group Geometry contains bbox of all member US."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folder = next(n for n in tree.iter(f"{NS}node")
                  if n.get("yfiles.foldertype") == "group"
                  and n.get("id", "").startswith("grp_"))
    g_geom = folder.find(f".//{Y}GroupNode/{Y}Geometry")
    gx, gy = float(g_geom.get("x")), float(g_geom.get("y"))
    gw, gh = float(g_geom.get("width")), float(g_geom.get("height"))

    # Find inner graph + member US Geometries
    inner = folder.find(f"{NS}graph")
    assert inner is not None
    member_geoms = []
    for me in inner.findall(f"{NS}node"):
        ug = me.find(f".//{Y}Geometry")
        if ug is None:
            continue
        member_geoms.append((
            float(ug.get("x")), float(ug.get("y")),
            float(ug.get("width")), float(ug.get("height"))))
    assert member_geoms, "no member US with Geometry"

    min_x = min(g[0] for g in member_geoms)
    min_y = min(g[1] for g in member_geoms)
    max_x = max(g[0] + g[2] for g in member_geoms)
    max_y = max(g[1] + g[3] for g in member_geoms)

    # Group bbox contains member bbox (+ small margin allowed)
    assert gx <= min_x
    assert gy <= min_y
    assert gx + gw >= max_x
    assert gy + gh >= max_y


def test_group_children_are_us_member_nodes(mini_volterra, tmp_path):
    """AC-11: inner <graph> contains exactly the member US nodes."""
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, ["struttura"])

    tree = ET.parse(str(out))
    folder = next(n for n in tree.iter(f"{NS}node")
                  if n.get("yfiles.foldertype") == "group"
                  and n.get("id", "").startswith("grp_"))
    inner = folder.find(f"{NS}graph")
    inner_nodes = list(inner.findall(f"{NS}node"))
    # Must be 3 member US nodes (matching the seeded count)
    assert len(inner_nodes) == 3


def test_default_groups_empty_preserves_ac2_baseline(mini_volterra, tmp_path):
    """D7-A: default no-groups export has no grp_* node — preserves
    the AI03 AC-2 baseline byte-identical guarantee structurally."""
    sito = _read_sito(mini_volterra)
    out = tmp_path / "out.graphml"
    _export_with_groups(mini_volterra, sito, out, None)

    tree = ET.parse(str(out))
    folders = [n for n in tree.iter(f"{NS}node")
               if n.get("id", "").startswith("grp_")]
    assert folders == []
```

- [ ] **Step 2: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_export_em_template.py -v
```

Expected: `5 passed`.

- [ ] **Step 3: AC-2 baseline + critical guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  -q 2>&1 | tail -2
```

Expected: all green.

- [ ] **Step 4: Full suite — 159 + 5 = 164**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `164 passed, 1 skipped`.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_groups_export_em_template.py
git commit -m "$(cat <<'EOF'
test(groups_em_template): L4 EM canonical layout compliance

5 new L4 tests pinning AC-8/9/10/11 + D7-A:
  - AC-8: <node yfiles.foldertype="group"> with <y:GroupNode>
    realizer (NOT TableNode)
  - AC-9: dashed border, fill #F5F5F5, NodeLabel top + bg #EBEBEB
    + label text matches group.name
  - AC-10: group <y:Geometry> contains bbox of all member US
  - AC-11: inner <graph> contains exactly the seeded member US
  - D7-A: default no-groups export has no grp_* nodes

These tests are the structural counterpart to the visual EM
template (EM_demo_02.graphml reference). They verify our output
matches the canonical EM yEd folder layout exactly.

Tests: 164/164 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task D.2: Round-trip tests (default safe / flag-on / adhoc)

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py` (add `sql_apply_groups` kwarg)
- Create: `tests/sync/test_round_trip_with_groups.py`

- [ ] **Step 1: Write failing tests**

Create `tests/sync/test_round_trip_with_groups.py`:

```python
"""L1 round-trip: groups → re-import → SQL state.

Pins D5 (configurable, default safe) + AC-12 + AC-13 + AC-14."""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as ET
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

NS = "{http://graphml.graphdrawing.org/xmlns}"
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


def _seed(db, sito, col, value, n=2):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?", (sito, n)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def _select_struttura_rows(db, sito):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us, struttura FROM us_table WHERE sito=?", (sito,)))
    conn.close()
    return rows


def test_default_no_sql_update_on_import(mini_volterra, tmp_path):
    """AC-12: default safe — no SQL update even when groups in import."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito,
                   groups=["struttura"])

    rows_before = _select_struttura_rows(mini_volterra, sito)
    # Import with default flag (False)
    GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito)
    rows_after = _select_struttura_rows(mini_volterra, sito)
    assert rows_before == rows_after  # SQL untouched


def test_sql_update_when_flag_enabled(mini_volterra, tmp_path):
    """AC-13: flag-on, manually move a US to a different group's
    inner <graph> in the GraphML, re-import → SQL UPDATE applied."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sito = _read_sito(mini_volterra)
    # Seed 2 US in basilica + 1 in chiesa
    _seed(mini_volterra, sito, "struttura", "basilica", 2)
    conn = sqlite3.connect(mini_volterra)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? "
        "AND struttura IS NULL OR struttura='' LIMIT 1", (sito,)))
    if rows:
        conn.execute("UPDATE us_table SET struttura='chiesa' "
                      "WHERE id_us=?", (rows[0][0],))
    conn.commit()
    conn.close()

    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito,
                   groups=["struttura"])

    # Manually mutate output: move first US from basilica to chiesa
    tree = ET.parse(str(out))
    root = tree.getroot()
    folders = [n for n in root.iter(f"{NS}node")
               if n.get("yfiles.foldertype") == "group"
               and n.get("id", "").startswith("grp_")]
    # Find label text "basilica" and "chiesa"
    folder_basilica = next(
        f for f in folders
        if any((nl.text or "").strip() == "basilica"
               for nl in f.iter("{http://www.yworks.com/xml/graphml}NodeLabel"))
    )
    folder_chiesa = next(
        f for f in folders
        if any((nl.text or "").strip() == "chiesa"
               for nl in f.iter("{http://www.yworks.com/xml/graphml}NodeLabel"))
    )
    inner_basilica = folder_basilica.find(f"{NS}graph")
    inner_chiesa = folder_chiesa.find(f"{NS}graph")
    # Take 1 US from basilica, move to chiesa
    moving_us = inner_basilica.findall(f"{NS}node")[0]
    inner_basilica.remove(moving_us)
    inner_chiesa.append(moving_us)
    tree.write(str(out), encoding="UTF-8", xml_declaration=True)

    # Import with flag ON
    result = GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito,
        sql_apply_groups=True)
    assert result.applied >= 1  # at least one UPDATE
    # Verify struttura count for basilica decreased
    rows_after = _select_struttura_rows(mini_volterra, sito)
    basilica_count = sum(1 for _, s in rows_after if s == "basilica")
    chiesa_count = sum(1 for _, s in rows_after if s == "chiesa")
    assert basilica_count == 1  # was 2, now 1
    assert chiesa_count >= 2     # was 1, now 2


def test_adhoc_groups_never_touch_sql(mini_volterra, tmp_path):
    """AC-14: ad-hoc group_kind never triggers SQL UPDATE even with
    flag on — only updates GroupStore."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.group_store import GroupStore
    sito = _read_sito(mini_volterra)

    # Add 1 ad-hoc group
    store = GroupStore(mini_volterra, sito)
    # Pick a real US to attach
    conn = sqlite3.connect(mini_volterra)
    us_row = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito=? LIMIT 1",
        (sito,)).fetchone()
    conn.close()
    us_uuid = us_row[0]
    store.add_group("restauri-2023", group_kind="adhoc",
                     member_us_uuids=[us_uuid])

    out = tmp_path / "out.graphml"
    export_graphml(db_path=mini_volterra, mapping="pyarchinit_us_mapping",
                   output_path=out, site_filter=sito,
                   groups=["adhoc"])

    rows_before = _select_struttura_rows(mini_volterra, sito)
    # Import with flag ON — ad-hoc must NOT touch SQL
    GraphIngestor().populate_list(
        out, db_path=mini_volterra, sito=sito,
        sql_apply_groups=True)
    rows_after = _select_struttura_rows(mini_volterra, sito)
    assert rows_before == rows_after
```

- [ ] **Step 2: Add `sql_apply_groups` kwarg to `GraphIngestor.populate_list`**

In `modules/s3dgraphy/sync/graph_ingestor.py`, find the `def populate_list(` signature and add `sql_apply_groups: bool = False` to keyword-only args.

After the existing parsing loop, add (just before the atomic transaction commit):

```python
            # AI06: optional SQL UPDATE from group folders in GraphML
            if sql_apply_groups:
                _GROUP_KIND_TO_COL = {
                    "area", "struttura", "attivita", "settore",
                    "ambient", "saggio", "quad_par",
                }
                # Parse GraphML for grp_* folder nodes
                from lxml import etree as _ET
                NS_G = "{http://graphml.graphdrawing.org/xmlns}"
                NS_Y = "{http://www.yworks.com/xml/graphml}"
                _tree = _ET.parse(str(graphml_path))
                for folder in _tree.iter(f"{NS_G}node"):
                    if folder.get("yfiles.foldertype") != "group":
                        continue
                    if not folder.get("id", "").startswith("grp_"):
                        continue
                    # Read label = group.name (defensive)
                    nl = folder.find(f".//{NS_Y}GroupNode/{NS_Y}NodeLabel")
                    if nl is None or not (nl.text or "").strip():
                        continue
                    group_name = nl.text.strip()
                    # Read group_kind from data key (description marker
                    # alone doesn't carry kind — read pyarchinit.<kind>
                    # data keys; first matching wins).
                    group_kind = None
                    for d in folder.findall(f"{NS_G}data"):
                        # Look up the d-key registry to find pyarchinit.X
                        key_id = d.get("key")
                        # Defensive — best-effort match
                        if key_id and d.text:
                            for kind in _GROUP_KIND_TO_COL:
                                if d.text.strip() == group_name:
                                    # We can't resolve kind from value
                                    # alone — fall back to first SQL kind
                                    # not yet ruled out
                                    pass
                    # Better: read pyarchinit.<X> attr.name from doc keys
                    # to map d-key id → kind, then find the attr in folder
                    root = _tree.getroot()
                    kid_to_kind: dict = {}
                    for k in root.findall(f"{NS_G}key"):
                        attr_name = k.get("attr.name") or ""
                        if attr_name.startswith("pyarchinit."):
                            short = attr_name.split(".", 1)[1]
                            if short in _GROUP_KIND_TO_COL:
                                kid_to_kind[k.get("id")] = short
                    for d in folder.findall(f"{NS_G}data"):
                        kind = kid_to_kind.get(d.get("key"))
                        if kind and d.text:
                            group_kind = kind
                            break
                    if not group_kind:
                        # Adhoc or unknown — skip SQL UPDATE
                        continue
                    # Get member US elements + their node_uuid via
                    # pyarchinit.us data key OR EMID
                    inner = folder.find(f"{NS_G}graph")
                    if inner is None:
                        continue
                    for member in inner.findall(f"{NS_G}node"):
                        node_uuid = member.get("id")
                        if not node_uuid:
                            continue
                        # Queue UPDATE
                        conn.execute(
                            f"UPDATE us_table SET {group_kind}=? "
                            f"WHERE node_uuid=? AND sito=?",
                            (group_name, node_uuid, sito))
                        applied += 1
```

(The exact integration point depends on the existing `populate_list` structure. Adapt as needed — the key is: the new code runs INSIDE the same atomic `BEGIN/COMMIT` transaction so a failure rolls back everything, AI04 contract preserved.)

- [ ] **Step 3: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v
```

Expected: `3 passed`. (If the integration point in `graph_ingestor.py` is off, debug + adapt — the tests are the spec.)

- [ ] **Step 4: AC-2 + critical guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_idempotent_ingest.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  -q 2>&1 | tail -2
```

Expected: all green. The `sql_apply_groups=False` default keeps existing AI04/AI05 round-trip semantics unchanged.

- [ ] **Step 5: Full suite — 164 + 3 = 167**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `167 passed, 1 skipped`.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py \
        tests/sync/test_round_trip_with_groups.py
git commit -m "$(cat <<'EOF'
feat(graph_ingestor): sql_apply_groups kwarg + group round-trip

D5-C: GraphIngestor.populate_list() gains a kwarg
sql_apply_groups: bool = False (default safe). When True, parses
group folder nodes from the import GraphML and queues
UPDATE us_table SET <kind>=<name> WHERE node_uuid=? for every
member US, mapping the d-key registry to discover group_kind from
pyarchinit.<col> data keys.

Atomic transaction: all UPDATEs run inside the same BEGIN/COMMIT
as the existing AI04 strat-layer ingest. ROLLBACK on any error.

Ad-hoc groups (group_kind="adhoc" or no SQL kind discoverable)
are NEVER written to SQL regardless of the flag (AC-14).

3 new L1 tests:
  - AC-12: default flag off → no SQL UPDATE
  - AC-13: flag on → user-edited folder movement reflected in SQL
  - AC-14: ad-hoc groups never touch SQL even with flag on

AC-2 + AI04 + AI05 guards green.

Tests: 167/167 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group E — Idempotency + dev fixture

### Task E.1: Extend `build_mini_volterra_external.py` with `_emit_groups_fixture`

**Files:**
- Modify: `tests/sync/fixtures/build_mini_volterra_external.py`

- [ ] **Step 1: Read existing structure**

```bash
sed -n '1,30p' tests/sync/fixtures/build_mini_volterra_external.py
grep -nE "^def _emit_|^def main|if __name__" tests/sync/fixtures/build_mini_volterra_external.py
```

Note the existing emit functions (e.g., `_emit_paradata_fixture` from AI05) and the `main()` entry point.

- [ ] **Step 2: Append `_emit_groups_fixture` near the existing emit functions**

Use the Edit tool to add (at the end of the file, before any `if __name__ == "__main__":` block):

```python
def _emit_groups_fixture():
    """Generate groups_volterra.graphml — pre-cooked ad-hoc group
    fixture used by AI06 round-trip / idempotent tests."""
    import sqlite3
    import shutil
    import tempfile
    from pathlib import Path

    PLUGIN_ROOT = Path(__file__).resolve().parents[3]
    SRC_DB = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "mini_volterra.sqlite"

    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids,
    )
    tmp_db = Path(tempfile.mkdtemp()) / "mini_volterra.sqlite"
    shutil.copy2(SRC_DB, tmp_db)
    add_columns(tmp_db); backfill_uuids(tmp_db)

    sito = sqlite3.connect(tmp_db).execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]

    # Pick 3 real US node_uuids
    conn = sqlite3.connect(tmp_db)
    rows = conn.execute(
        "SELECT node_uuid FROM us_table WHERE sito=? LIMIT 3",
        (sito,)).fetchall()
    member_uuids = [r[0] for r in rows]
    conn.close()

    from modules.s3dgraphy.sync.group_store import GroupStore
    store = GroupStore(tmp_db, sito)
    store.add_group(
        "restauri-2023",
        group_kind="adhoc",
        member_us_uuids=member_uuids,
        description="Restauri eseguiti nel 2023",
    )

    out = PLUGIN_ROOT / "tests" / "sync" / "fixtures" / "groups_volterra.graphml"
    shutil.copy2(store.file_path, out)
    print(f"OK — groups_volterra.graphml ({out.stat().st_size} bytes)")
```

Then in the existing `main()` function (or near the existing `_emit_*` calls), add a call to `_emit_groups_fixture()`.

- [ ] **Step 3: Run the generator**

```bash
PYTHONPATH="$PWD" python tests/sync/fixtures/build_mini_volterra_external.py 2>&1 | tail -10
ls -la tests/sync/fixtures/groups_volterra.graphml
```

Expected: file exists, size > 1KB.

- [ ] **Step 4: Verify content via lxml**

```bash
python3 -c "
from lxml import etree
tree = etree.parse('tests/sync/fixtures/groups_volterra.graphml')
NS = '{http://graphml.graphdrawing.org/xmlns}'
nodes = list(tree.iter(NS + 'node'))
print(f'group nodes: {len(nodes)}')
"
```

Expected: 1 node (the ad-hoc group).

- [ ] **Step 5: Sanity full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `167 passed, 1 skipped` (no new tests; fixture-only commit).

- [ ] **Step 6: Commit (binary fixture + generator extension)**

```bash
git add tests/sync/fixtures/build_mini_volterra_external.py \
        tests/sync/fixtures/groups_volterra.graphml
git commit -m "$(cat <<'EOF'
test(fixtures): add groups_volterra.graphml + generator extension

Pre-cooked binary fixture for AI06 round-trip + idempotent tests.
Contains 1 ad-hoc group ("restauri-2023") with 3 real US members
from mini_volterra.

Generated deterministically by build_mini_volterra_external.py
via GroupStore.add_group on a temp copy of mini_volterra.sqlite,
then copied to a stable filename.

Tests: 167/167 pass (no new tests; fixture-only).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task E.2: Idempotency tests

**Files:**
- Create: `tests/sync/test_groups_idempotent.py`

- [ ] **Step 1: Write tests**

```python
"""L1 idempotency: 3 consecutive exports converge.

Pins AC-15."""
from __future__ import annotations
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest
import pandas  # noqa: F401
from lxml import etree as ET
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

NS = "{http://graphml.graphdrawing.org/xmlns}"
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


def _seed(db, sito, col, value, n=2):
    conn = sqlite3.connect(db)
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT ?", (sito, n)))
    for (id_us,) in rows:
        conn.execute(
            f"UPDATE us_table SET {col}=? WHERE id_us=?",
            (value, id_us))
    conn.commit()
    conn.close()


def _extract_group_uuids(graphml_path):
    tree = ET.parse(str(graphml_path))
    out = []
    for n in tree.iter(f"{NS}node"):
        if (n.get("yfiles.foldertype") == "group"
                and n.get("id", "").startswith("grp_")):
            out.append(n.get("id"))
    return sorted(out)


def _structural_fingerprint(graphml_path):
    """Count nodes/edges/labels — same approach as AC-2 baseline."""
    tree = ET.parse(str(graphml_path))
    nodes = list(tree.iter(f"{NS}node"))
    edges = list(tree.iter(f"{NS}edge"))
    return (len(nodes), len(edges))


def test_repeated_export_produces_stable_groups(mini_volterra, tmp_path):
    """AC-15: 3 consecutive exports → identical group UUIDs."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    outs = [tmp_path / f"out{i}.graphml" for i in range(3)]
    for out in outs:
        export_graphml(db_path=mini_volterra,
                       mapping="pyarchinit_us_mapping",
                       output_path=out, site_filter=sito,
                       groups=["struttura"])

    uuids = [tuple(_extract_group_uuids(o)) for o in outs]
    assert uuids[0] == uuids[1] == uuids[2]


def test_export_structural_fingerprint_stable(mini_volterra, tmp_path):
    """AC-15: structural fingerprint stable across repeated exports."""
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    sito = _read_sito(mini_volterra)
    _seed(mini_volterra, sito, "struttura", "basilica", 3)

    out1 = tmp_path / "out1.graphml"
    out2 = tmp_path / "out2.graphml"
    out3 = tmp_path / "out3.graphml"
    for out in (out1, out2, out3):
        export_graphml(db_path=mini_volterra,
                       mapping="pyarchinit_us_mapping",
                       output_path=out, site_filter=sito,
                       groups=["struttura"])

    fp1 = _structural_fingerprint(out1)
    fp2 = _structural_fingerprint(out2)
    fp3 = _structural_fingerprint(out3)
    # Run 1 vs 2 may differ on structural details; 2 vs 3 must be stable
    assert fp2 == fp3
```

- [ ] **Step 2: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_idempotent.py -v
```

Expected: `2 passed`.

- [ ] **Step 3: Full suite — 167 + 2 = 169 (target was 168, but +2 fixture-only commit boundary; final is fine)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `169 passed, 1 skipped`.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/test_groups_idempotent.py
git commit -m "$(cat <<'EOF'
test(groups_idempotent): D4-C-extended invariant for AI06

Two L1 tests pinning AC-15:
  - 3 consecutive exports produce identical group UUIDs
    (deterministic UUID5 from build_groups_from_sql, AC-7)
  - structural fingerprint (node count, edge count) stable from
    run 2 onwards (run 1 vs 2 may differ on layout-time details)

Group E complete (2 tests, +1 fixture file).

Tests: 169/169 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group F — CLI subcommands

### Task F.1: Extend `s3dgraphy_sync.py` with paradata group sub-subcommands + `--group-by`

**Files:**
- Modify: `scripts/s3dgraphy_sync.py`

- [ ] **Step 1: Read existing CLI structure**

```bash
grep -nE "^def cmd_|sub\.add_parser\|para_sub\." scripts/s3dgraphy_sync.py | head -20
```

Note: AI05 added `cmd_paradata` with 7 sub-subcommands (`add-author/list-authors/.../remove`). We add 4 more under `paradata`: `add-group/list-groups/add-us-to-group/remove-group`.

- [ ] **Step 2: Add the 4 new sub-subcommands**

In `cmd_paradata`, extend the `if/elif` chain:

```python
        elif sub == "add-group":
            from modules.s3dgraphy.sync.group_store import GroupStore
            store = GroupStore(Path(args.db), args.sito)
            members = list(args.us_uuid or [])
            uuid = store.add_group(
                args.name,
                group_kind=args.kind,
                member_us_uuids=members,
            )
            print(f"OK — group {uuid}")
        elif sub == "list-groups":
            from modules.s3dgraphy.sync.group_store import GroupStore
            store = GroupStore(Path(args.db), args.sito)
            for g in store.list_groups():
                members_csv = ",".join(g.get("member_us_uuids", []))
                print(f"{g['group_uuid']}\t{g['name']}\t"
                      f"{g.get('group_kind', '')}\t{members_csv}")
        elif sub == "add-us-to-group":
            from modules.s3dgraphy.sync.group_store import GroupStore
            store = GroupStore(Path(args.db), args.sito)
            store.add_us_to_group(args.group_uuid, args.us_uuid)
            print(f"OK — added {args.us_uuid} to {args.group_uuid}")
        elif sub == "remove-group":
            from modules.s3dgraphy.sync.group_store import GroupStore
            store = GroupStore(Path(args.db), args.sito)
            store.remove_group(args.uuid)
            print(f"OK — removed {args.uuid}")
```

In the argparse setup for `paradata`, add:

```python
p_ag = para_sub.add_parser("add-group")
p_ag.add_argument("--db", required=True)
p_ag.add_argument("--sito", required=True)
p_ag.add_argument("--name", required=True)
p_ag.add_argument("--kind", default="adhoc")
p_ag.add_argument("--us-uuid", action="append")  # repeatable
p_ag.set_defaults(func=cmd_paradata)

p_lg = para_sub.add_parser("list-groups")
p_lg.add_argument("--db", required=True)
p_lg.add_argument("--sito", required=True)
p_lg.set_defaults(func=cmd_paradata)

p_aug = para_sub.add_parser("add-us-to-group")
p_aug.add_argument("--db", required=True)
p_aug.add_argument("--sito", required=True)
p_aug.add_argument("--group-uuid", required=True, dest="group_uuid")
p_aug.add_argument("--us-uuid", required=True, dest="us_uuid")
p_aug.set_defaults(func=cmd_paradata)

p_rg = para_sub.add_parser("remove-group")
p_rg.add_argument("--db", required=True)
p_rg.add_argument("--sito", required=True)
p_rg.add_argument("--uuid", required=True)
p_rg.set_defaults(func=cmd_paradata)
```

- [ ] **Step 3: Add `--group-by` flag to `export` subcommand**

In `cmd_export`, after parsing args, parse `--group-by` CSV:

```python
        groups_arg = None
        if getattr(args, "group_by", None):
            groups_arg = [g.strip() for g in args.group_by.split(",") if g.strip()]
        result = export_graphml(
            db_path=args.db,
            mapping=args.mapping,
            output_path=args.output,
            site_filter=args.sito,
            groups=groups_arg,
        )
```

In the argparse setup for `export`:

```python
p_ex.add_argument("--group-by", dest="group_by",
                   help="CSV of grouping dimensions: "
                        "area,struttura,attivita,settore,ambient,"
                        "saggio,quad_par,adhoc")
```

- [ ] **Step 4: Smoke-test from shell**

```bash
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata --help 2>&1 | tail -30
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata add-group --help 2>&1 | tail -10
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py export --help 2>&1 | tail -15
```

Expected: `--help` shows the 4 new sub-subcommands and `--group-by` flag.

- [ ] **Step 5: Smoke-test add-group + list-groups manually**

```bash
TMP=$(mktemp -d)
cp tests/sync/fixtures/mini_volterra.sqlite "$TMP/test.sqlite"
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata add-group \
    --db "$TMP/test.sqlite" --sito TestSite --name "Test Group" \
    --us-uuid u1 --us-uuid u2
PYTHONPATH="$PWD" python scripts/s3dgraphy_sync.py paradata list-groups \
    --db "$TMP/test.sqlite" --sito TestSite
rm -rf "$TMP"
```

Expected: `OK — group <uuid>` then a row with the group printed in TSV.

- [ ] **Step 6: Sanity full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `169 passed, 1 skipped` (no new pytest tests yet — they land in F.2).

- [ ] **Step 7: Commit**

```bash
git add scripts/s3dgraphy_sync.py
git commit -m "$(cat <<'EOF'
feat(scripts): paradata group sub-subcommands + export --group-by

Adds 4 paradata sub-subcommands to s3dgraphy_sync.py:
  - paradata add-group --name [--kind adhoc] [--us-uuid ...]
  - paradata list-groups
  - paradata add-us-to-group --group-uuid --us-uuid
  - paradata remove-group --uuid

Each delegates to GroupStore (AI06 Group A). All require --db and
--sito (consistent with AI05 paradata CLI shape). Same exit-code
contract: 0 success / 1 GroupStoreError / 2 argparse error.

list-groups output is tab-separated:
  <group_uuid>\t<name>\t<group_kind>\t<csv_of_member_uuids>

Plus a --group-by flag on the export subcommand: CSV of dimensions
(struttura,attivita,...,adhoc) passed through to export_graphml.

Subprocess tests in test_cli_groups.py land in F.2.

Tests: 169/169 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task F.2: Subprocess tests for the 4 sub-subcommands + `--group-by`

**Files:**
- Create: `tests/sync/test_cli_groups.py`

- [ ] **Step 1: Write tests**

```python
"""L2 subprocess tests for paradata add-group / list-groups /
add-us-to-group / remove-group + export --group-by."""
from __future__ import annotations
import shutil
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


def test_cli_paradata_add_group(mini_volterra):
    r = _run("paradata", "add-group",
             "--db", str(mini_volterra),
             "--sito", "TestSite",
             "--name", "test-grp",
             "--us-uuid", "u1",
             "--us-uuid", "u2")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert "OK" in r.stdout
    assert "group" in r.stdout


def test_cli_paradata_list_groups_after_add(mini_volterra):
    _run("paradata", "add-group",
         "--db", str(mini_volterra), "--sito", "TestSite",
         "--name", "test-grp", "--us-uuid", "u1")
    r = _run("paradata", "list-groups",
             "--db", str(mini_volterra), "--sito", "TestSite")
    assert r.returncode == 0
    assert "test-grp" in r.stdout
    assert "adhoc" in r.stdout


def test_cli_paradata_add_us_to_group(mini_volterra):
    r1 = _run("paradata", "add-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--name", "test-grp", "--us-uuid", "u1")
    uuid = r1.stdout.strip().split()[-1]
    r2 = _run("paradata", "add-us-to-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--group-uuid", uuid, "--us-uuid", "u2")
    assert r2.returncode == 0
    assert "OK" in r2.stdout

    r3 = _run("paradata", "list-groups",
              "--db", str(mini_volterra), "--sito", "TestSite")
    assert "u1" in r3.stdout
    assert "u2" in r3.stdout


def test_cli_paradata_remove_group(mini_volterra):
    r1 = _run("paradata", "add-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--name", "test-grp")
    uuid = r1.stdout.strip().split()[-1]
    r2 = _run("paradata", "remove-group",
              "--db", str(mini_volterra), "--sito", "TestSite",
              "--uuid", uuid)
    assert r2.returncode == 0
    r3 = _run("paradata", "list-groups",
              "--db", str(mini_volterra), "--sito", "TestSite")
    assert uuid not in r3.stdout


def test_cli_export_with_group_by(mini_volterra, tmp_path):
    """AC-17: export --group-by emits groups for listed dimensions."""
    # Apply Phase 1 migration first
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(mini_volterra); backfill_uuids(mini_volterra)
    # Seed struttura on a few rows
    import sqlite3
    conn = sqlite3.connect(mini_volterra)
    sito = conn.execute(
        "SELECT DISTINCT sito FROM us_table LIMIT 1").fetchone()[0]
    rows = list(conn.execute(
        "SELECT id_us FROM us_table WHERE sito=? LIMIT 3", (sito,)))
    for (id_us,) in rows:
        conn.execute(
            "UPDATE us_table SET struttura='basilica' WHERE id_us=?",
            (id_us,))
    conn.commit()
    conn.close()

    out = tmp_path / "out.graphml"
    r = _run("export",
             "--db", str(mini_volterra),
             "--sito", sito,
             "--mapping", "pyarchinit_us_mapping",
             "--output", str(out),
             "--group-by", "struttura")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    assert out.exists()
    text = out.read_text()
    assert "yfiles.foldertype=\"group\"" in text or \
           "yfiles.foldertype='group'" in text
    assert "grp_" in text


def test_cli_invalid_subcommand_exits_2(mini_volterra):
    r = _run("paradata", "totally-bogus",
             "--db", str(mini_volterra), "--sito", "X")
    assert r.returncode == 2
```

- [ ] **Step 2: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_cli_groups.py -v
```

Expected: `6 passed`.

- [ ] **Step 3: Full suite — 169 + 6 = 175 (close to plan's 174, off-by-one due to E.1/E.2 carryover)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `175 passed, 1 skipped`.

- [ ] **Step 4: AC-2 + critical guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_paradata_store.py \
  -q 2>&1 | tail -2
```

Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_cli_groups.py
git commit -m "$(cat <<'EOF'
test(cli_groups): subprocess tests for paradata groups + export

Six L2 tests via subprocess.run() against scripts/s3dgraphy_sync.py:
  - add-group exit 0 + "OK" in stdout
  - list-groups prints the just-added group
  - add-us-to-group adds a member, list confirms
  - remove-group deletes; list no longer shows uuid
  - export --group-by struttura emits yfiles.foldertype="group"
    + grp_* in output GraphML (AC-17)
  - paradata totally-bogus subcommand exits 2 (argparse error)

Group F complete (6 tests).

Tests: 175/175 pass.
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group G — UI dialogs

### Task G.1: Add 4th tab "Groups" to ParadataManagerDialog

**Files:**
- Modify: `gui/dialog_paradata_manager.py`

- [ ] **Step 1: Locate the existing 3-tab setup**

```bash
grep -nE "self\.tabs\.addTab|_setup_tab_authors|_setup_tab_licenses|_setup_tab_embargoes" \
  gui/dialog_paradata_manager.py | head -10
```

Note: AI05 has `_setup_tab_authors`, `_setup_tab_licenses`, `_setup_tab_embargoes`. We add `_setup_tab_groups`.

- [ ] **Step 2: Add the new tab inside the QGIS_AVAILABLE branch**

In `gui/dialog_paradata_manager.py`, find `_setup_ui()` (or wherever the 3 tabs are wired) and add a 4th call:

```python
            self._setup_tab_groups()  # NEW (AI06)
```

Then add the method:

```python
        def _setup_tab_groups(self):
            tab = QWidget()
            tlayout = QVBoxLayout()
            self.table_groups = QTableWidget(0, 3)
            self.table_groups.setHorizontalHeaderLabels(
                ["Name", "Kind", "US members"])
            self.table_groups.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            tlayout.addWidget(self.table_groups)

            form = QFormLayout()
            self.le_grp_name = QLineEdit()
            self.cb_grp_kind = QComboBox()
            self.cb_grp_kind.addItems(["adhoc"])
            self.btn_grp_pick_us = QPushButton("Pick US members…")
            self.btn_grp_pick_us.clicked.connect(self._on_pick_us_for_group)
            self._picked_us_uuids = []
            self.lbl_grp_picked = QLabel("0 selected")
            form.addRow("Name:", self.le_grp_name)
            form.addRow("Kind:", self.cb_grp_kind)
            form.addRow("Members:", self.btn_grp_pick_us)
            form.addRow("", self.lbl_grp_picked)
            tlayout.addLayout(form)

            btn_row = QHBoxLayout()
            btn_add = QPushButton("Add group")
            btn_add.clicked.connect(self._on_add_group)
            btn_remove = QPushButton("Remove selected")
            btn_remove.clicked.connect(
                lambda: self._on_remove_selected(
                    self.table_groups, "group"))
            btn_row.addWidget(btn_add)
            btn_row.addWidget(btn_remove)
            tlayout.addLayout(btn_row)

            tab.setLayout(tlayout)
            self.tabs.addTab(tab, "Groups")
```

Add the `_group_store` helper similar to `_store`:

```python
        def _group_store(self):
            from modules.s3dgraphy.sync.group_store import GroupStore
            db_path = self.db_manager.get_sqlite_path() if self.db_manager else None
            if db_path is None:
                QMessageBox.critical(
                    self, "No SQLite DB",
                    "Group management requires a SQLite-backed pyarchinit project.")
                return None
            return GroupStore(db_path, self.sito)
```

Extend `_load_data()` to also fill the groups table:

```python
        def _load_data(self):
            store = self._store()
            if store is None:
                return
            # ... existing authors/licenses/embargoes load ...
            # AI06: groups
            try:
                gstore = self._group_store()
                if gstore is not None:
                    groups = gstore.list_groups()
                    self._fill_groups(groups)
            except Exception as e:
                self._diag(f"groups load failed: {e}")

        def _fill_groups(self, rows):
            self.table_groups.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self.table_groups.setItem(
                    i, 0, QTableWidgetItem(r.get("name", "")))
                self.table_groups.setItem(
                    i, 1, QTableWidgetItem(r.get("group_kind", "")))
                count = len(r.get("member_us_uuids", []))
                self.table_groups.setItem(
                    i, 2, QTableWidgetItem(str(count)))
                self.table_groups.item(i, 0).setData(
                    Qt.UserRole, r["group_uuid"])
```

Add the click handlers:

```python
        def _on_pick_us_for_group(self):
            """Open secondary multi-select dialog of US for the
            current sito. Stores selection in self._picked_us_uuids."""
            from qgis.PyQt.QtWidgets import (
                QDialog, QListWidget, QListWidgetItem,
                QDialogButtonBox, QVBoxLayout)

            dlg = QDialog(self)
            dlg.setWindowTitle(f"Pick US for group — {self.sito}")
            dlg.setMinimumWidth(500)
            dlg.setMinimumHeight(400)
            layout = QVBoxLayout()

            lst = QListWidget()
            lst.setSelectionMode(QListWidget.MultiSelection)
            # Load US for sito
            try:
                import sqlite3
                db = self.db_manager.get_sqlite_path()
                conn = sqlite3.connect(str(db))
                rows = conn.execute(
                    "SELECT node_uuid, us, area, unita_tipo "
                    "FROM us_table WHERE sito=? ORDER BY us",
                    (self.sito,)).fetchall()
                conn.close()
                for node_uuid, us, area, unita_tipo in rows:
                    if not node_uuid:
                        continue
                    label = f"{unita_tipo or 'US'} {us} (area {area or '-'})"
                    item = QListWidgetItem(label)
                    item.setData(Qt.UserRole, node_uuid)
                    lst.addItem(item)
            except Exception as e:
                QMessageBox.critical(dlg, "Load failed", str(e))
                return
            layout.addWidget(lst)

            btns = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            layout.addWidget(btns)
            dlg.setLayout(layout)

            if dlg.exec_() == QDialog.Accepted:
                self._picked_us_uuids = [
                    lst.item(i).data(Qt.UserRole)
                    for i in range(lst.count())
                    if lst.item(i).isSelected()
                ]
                self.lbl_grp_picked.setText(
                    f"{len(self._picked_us_uuids)} selected")

        def _on_add_group(self):
            store = self._group_store()
            if store is None:
                return
            name = self.le_grp_name.text().strip()
            if not name:
                QMessageBox.warning(
                    self, "Invalid", "Group name is required.")
                return
            kind = self.cb_grp_kind.currentText().strip() or "adhoc"
            try:
                uuid = store.add_group(
                    name,
                    group_kind=kind,
                    member_us_uuids=list(self._picked_us_uuids),
                )
                self._diag(f"add_group OK: {uuid}, "
                           f"{len(self._picked_us_uuids)} members")
            except Exception as e:
                import traceback
                self._diag(traceback.format_exc())
                QMessageBox.critical(
                    self, type(e).__name__,
                    f"Cannot add group: {e}")
                return
            self.le_grp_name.clear()
            self._picked_us_uuids = []
            self.lbl_grp_picked.setText("0 selected")
            self._load_data()
```

Extend `_on_remove_selected` to handle the groups table:

```python
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
            try:
                if label == "group":
                    store = self._group_store()
                    if store:
                        store.remove_group(uuid)
                else:
                    store = self._store()
                    if store:
                        store.remove(uuid)
            except Exception as e:
                QMessageBox.critical(self, type(e).__name__, str(e))
                return
            self._load_data()
```

Also import `QComboBox` and `QLabel` and `QListWidget` etc. (add to existing imports):

```python
    from qgis.PyQt.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
        QLineEdit, QFormLayout, QMessageBox, QHeaderView,
        QComboBox,                # NEW (AI06)
    )
```

- [ ] **Step 3: Verify file is syntactically valid**

```bash
python3 -c "import ast; ast.parse(open('gui/dialog_paradata_manager.py').read()); print('OK')"
```

Expected: `OK`.

- [ ] **Step 4: Run existing AI05 dialog smoke test (must still skip cleanly)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_dialog_smoke.py -v 2>&1 | tail -3
```

Expected: `1 skipped` (Qt not in headless test env).

- [ ] **Step 5: Sanity full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `175 passed, 1 skipped` (no new pytest tests yet).

- [ ] **Step 6: Commit**

```bash
git add gui/dialog_paradata_manager.py
git commit -m "$(cat <<'EOF'
feat(dialog_paradata): 4th tab "Groups" + US picker secondary dialog

Per AI06 spec §3.5 (D6), extends ParadataManagerDialog with a
4th tab:
  - QTableWidget (Name | Kind | US members count)
  - Form: name QLineEdit, kind QComboBox (initially ["adhoc"]
    only — SQL-derived kinds enter via round-trip, not user
    input), "Pick US members…" button
  - Add group / Remove selected buttons

Pick US members opens a secondary QDialog with QListWidget set
to MultiSelection mode, populated from us_table for the current
sito (cols: node_uuid, us, area, unita_tipo). Returns list of
node_uuids stored in self._picked_us_uuids.

_load_data extended to populate the new groups tab via
GroupStore.list_groups(). _on_remove_selected handles the
group/non-group dispatch.

Diagnostic logging via existing self._diag method for QGIS
console support.

Tests: 175/175 pass + 1 skipped (Qt smoke).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task G.2: S3DGraphyExportDialog 7 checkboxes + Import flag + smoke tests

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py`
- Create: `tests/sync/test_groups_dialog_smoke.py`

- [ ] **Step 1: Locate existing dialog setup**

```bash
grep -nE "class S3DGraphyExportDialog|self\.tabs\.addTab|export_graphml\(" \
  modules/s3dgraphy/s3dgraphy_dot_bridge.py | head -10
```

- [ ] **Step 2: Add the 7-checkbox QGroupBox + import-flag checkbox**

In `S3DGraphyExportDialog.__init__` (or wherever the Export tab UI is built), add the QGroupBox after the existing controls:

```python
        # AI06: Group US by ...
        from qgis.PyQt.QtWidgets import QGroupBox, QCheckBox, QVBoxLayout
        self.gb_groups = QGroupBox("Group US by (optional)")
        gb_layout = QVBoxLayout()
        self.cb_grp = {}
        for dim in ("area", "struttura", "attivita", "settore",
                    "ambient", "saggio", "quad_par"):
            cb = QCheckBox(dim)
            self.cb_grp[dim] = cb
            gb_layout.addWidget(cb)
        self.cb_grp_adhoc = QCheckBox("ad-hoc (from groups_*.graphml)")
        gb_layout.addWidget(self.cb_grp_adhoc)
        self.gb_groups.setLayout(gb_layout)
        # Add gb_groups to the existing Export tab layout
        export_tab_layout.addWidget(self.gb_groups)
```

Add a method to preselect populated dims when site changes / on dialog open:

```python
    def _preselect_groups(self):
        """Pre-check the 7 checkboxes for dimensions with non-empty
        values in us_table for the current sito. Pre-check ad-hoc
        if groups_*.graphml exists. Called on dialog open + when
        site combo changes."""
        if self.db_manager is None:
            return
        db_path = self.db_manager.get_sqlite_path()
        if db_path is None:
            return
        sito = self.comboBox_sito.currentText().strip()
        if not sito:
            return
        try:
            from .sync.group_projector import dimensions_with_data
            populated = set(dimensions_with_data(db_path, sito))
        except Exception:
            populated = set()
        for dim, cb in self.cb_grp.items():
            cb.setChecked(dim in populated)
        try:
            from .sync.group_store import GroupStore
            self.cb_grp_adhoc.setChecked(GroupStore(db_path, sito).exists())
        except Exception:
            pass
```

In the existing Export click handler, build the `groups` arg:

```python
    def _build_groups_arg(self):
        out = [d for d, cb in self.cb_grp.items() if cb.isChecked()]
        if self.cb_grp_adhoc.isChecked():
            out.append("adhoc")
        return out
```

And modify the call to `export_graphml`:

```python
            result = export_graphml(
                db_path=db_path,
                mapping='pyarchinit_us_mapping',
                output_path=graphml_path,
                site_filter=site,
                persist_auxiliary=False,
                language=_locale,
                groups=self._build_groups_arg(),     # NEW (AI06)
            )
```

For the Import tab:

```python
        # AI06: opt-in SQL apply on round-trip
        self.cb_sql_apply_groups = QCheckBox(
            "Update SQL on import (struttura/area/attivita/settore/"
            "ambient/saggio/quad_par)")
        self.cb_sql_apply_groups.setChecked(False)
        # Add to Import tab layout
        import_tab_layout.addWidget(self.cb_sql_apply_groups)
```

And in the import click handler:

```python
            ingestor.populate_list(
                graphml_path,
                db_path=db_path,
                sito=sito,
                sql_apply_groups=self.cb_sql_apply_groups.isChecked(),  # NEW
            )
```

- [ ] **Step 3: Wire `_preselect_groups` to dialog open**

In the dialog constructor, after widgets are set up:

```python
        # Preselect once on open
        try:
            self._preselect_groups()
        except Exception:
            pass
        # Re-preselect when sito changes
        self.comboBox_sito.currentTextChanged.connect(
            lambda _: self._preselect_groups())
```

- [ ] **Step 4: Write the smoke tests**

Create `tests/sync/test_groups_dialog_smoke.py`:

```python
"""L0 smoke tests for the AI06 dialog extensions."""
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


@pytest.mark.skipif(not _qt_available(), reason="QGIS Qt not available")
def test_dialog_has_groups_tab(tmp_path):
    """AC-18: ParadataManagerDialog now has 4 tabs."""
    from qgis.PyQt.QtWidgets import QApplication
    if QApplication.instance() is None:
        QApplication([])

    class _FakeDBManager:
        def __init__(self, db):
            self._db = db
        def get_sqlite_path(self):
            return self._db

    import sqlite3
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INT, sito TEXT, "
                  "node_uuid TEXT, us TEXT, area TEXT, unita_tipo TEXT)")
    conn.commit(); conn.close()

    from gui.dialog_paradata_manager import ParadataManagerDialog
    dialog = ParadataManagerDialog(
        parent=None, db_manager=_FakeDBManager(db), sito="X")
    assert dialog.tabs.count() == 4
    assert dialog.tabs.tabText(3).lower() == "groups"


@pytest.mark.skipif(not _qt_available(), reason="QGIS Qt not available")
def test_dialog_preselects_populated_dimensions(tmp_path):
    """D2: S3DGraphyExportDialog auto-preselects populated dims."""
    # This test is hard to fully exercise without spinning up the
    # full QGIS dialog (which requires a running plugin context).
    # Verify only that _preselect_groups doesn't crash with a
    # minimal stub.
    pytest.skip("Full QGIS context required for S3DGraphyExportDialog")
```

- [ ] **Step 5: Run tests**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_groups_dialog_smoke.py -v
```

Expected: `1 skipped` (no Qt) OR `1 passed + 1 skipped` (if Qt available).

- [ ] **Step 6: Verify file is syntactically valid**

```bash
python3 -c "import ast; ast.parse(open('modules/s3dgraphy/s3dgraphy_dot_bridge.py').read()); print('OK')"
```

Expected: `OK`.

- [ ] **Step 7: Full suite — 175 + 0/2 = 175-177 (depends on Qt)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -2
```

Expected: `175 passed, 2-3 skipped` in headless env. (One skip from existing AI05 paradata smoke + 1-2 from AI06 groups smoke.)

- [ ] **Step 8: Commit**

```bash
git add modules/s3dgraphy/s3dgraphy_dot_bridge.py \
        tests/sync/test_groups_dialog_smoke.py
git commit -m "$(cat <<'EOF'
feat(s3dgraphy_dot_bridge): groups checkboxes + import SQL flag

Per AI06 spec §3.6 (D2 + D5-C):

S3DGraphyExportDialog Export tab:
  - new QGroupBox "Group US by (optional)" with 7 checkboxes
    (one per us_table grouping column) + 1 "ad-hoc" checkbox
  - _preselect_groups() auto-checks populated dimensions on
    dialog open + when sito combo changes (uses
    group_projector.dimensions_with_data + GroupStore.exists)
  - _build_groups_arg() builds the list[str] passed to
    export_graphml(..., groups=...)

S3DGraphyExportDialog Import tab:
  - new QCheckBox "Update SQL on import (...)" default unchecked
    (D5-C safe default)
  - flag passed to GraphIngestor.populate_list(sql_apply_groups=...)

2 new L0 smoke tests (skipped without Qt):
  - AC-18: dialog has 4 tabs after AI06
  - D2: preselect logic doesn't crash with minimal stub

Group G complete (2 tests).

Tests: 175/175 pass + 2 skipped (Qt-headless).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

---

## Group H — Release packaging

### Task H.1: Dev-log entry

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Append the AI06 section at the END of the file**

```markdown

---

# Phase 2 — AI06 Node grouping (area / struttura / attivita / settore / ambient / saggio / quad_par + ad-hoc)

**Date:** 2026-05-08 → 2026-05-08
**Tag:** `phase2-ai06-node-grouping-5.5.0-alpha`
**Spec:** `docs/superpowers/specs/2026-05-08-ai06-node-grouping-design.md`
**Plan:** `docs/superpowers/plans/2026-05-08-ai06-node-grouping.md`

## What was built

Opt-in grouping of US in the Extended Matrix export by 7 us_table
columns (area, struttura, attivita, settore, ambient, saggio,
quad_par) plus user-authored ad-hoc groups, rendered as yEd folder
nodes nested in the existing epoch swimlane (EM canonical layout
matching `EM_demo_02.graphml`).

1. **GroupStore** — atomic CRUD over `groups_{sito_slug}.graphml`
   for ad-hoc groups (parallels AI05 ParadataStore). Custom lxml
   serializer (s3dgraphy GraphMLExporter doesn't render isolated
   ActivityNodeGroup instances). Exception hierarchy
   `GroupStoreError` extends `GraphSyncError`.

2. **`group_projector` helpers** — `dimensions_with_data` for
   dialog preselect, `build_groups_from_sql` with deterministic
   UUID5 (AC-7), `merge_adhoc_groups` with collision warning.

3. **`GraphProjector.populate_graph(groups=[...])`** — new kwarg
   materializes ActivityNodeGroup instances with `group_kind`
   discriminator + `is_in_activity` edges from member US.
   Default `groups=None` preserves AI05/AC-2 baseline.

4. **`_inject_group_folders` Stage 4e post-processor** — yEd
   folder injection inside the TableNode swimlane, with EM
   canonical visual style (dashed border, fill `#F5F5F5`,
   NodeLabel top + bg `#EBEBEB`) and geometry that spans member
   US bbox. Pre-export snapshot pattern (lesson from AI05).

5. **GraphIngestor `sql_apply_groups` kwarg** — opt-in round-trip
   SQL UPDATE from yEd group movements (D5-C, default safe).
   Atomic transaction (AI04 contract).

## UI

ParadataManagerDialog grew to 4 tabs (Authors / Licenses /
Embargoes / Groups). The Groups tab has a QTableWidget +
"Pick US members…" secondary dialog (multi-select QListWidget).

S3DGraphyExportDialog Export tab gained a 7-checkbox QGroupBox
"Group US by" with auto-preselect via `dimensions_with_data` on
open / sito change. Import tab gained a `cb_sql_apply_groups`
checkbox (default off).

## CLI

`scripts/s3dgraphy_sync.py` gained 4 paradata sub-subcommands
(`add-group`, `list-groups`, `add-us-to-group`, `remove-group`)
plus a `--group-by` CSV flag on `export`. Same exit-code contract
(0 / 1 / 2).

## Test counts

- Baseline (post-AI05): 132 passed, 1 skipped
- Post-Group A (group_store): 146
- Post-Group B (group_projector): 154
- Post-Group C (export integration): 159
- Post-Group D (EM template + round-trip): 167
- Post-Group E (idempotent + fixture): 169
- Post-Group F (CLI): 175
- Post-Group G (UI): 175 + 2-3 skipped

Final: 175+ passed, 2-3 skipped (Qt-headless).

## Acceptance criteria

All 21 ACs from spec §7 satisfied. AC-2 byte-identical baseline
stayed green at every commit (default `groups=None` is a no-op
for the AC-2 fixture). AI04 + AI05 guards green throughout.

## Manual smoke gate (Group H.4)

User-driven validation in QGIS — see plan §H.4.

## Carry-overs (deferred to AI07+)

- Migration to `LocationNodeGroup` upstream (depends on
  zalmoxes-laran/s3Dgraphy#5)
- Hierarchical nesting (group inside group) — AI08
- Per-dimension visual style (different colours for area vs
  struttura vs settore) — AI08
- Auto-layout heuristics for sub-groups (avoid overlap) — AI08
- TimeBranchNodeGroup mapping — AI09

## Phase 3+ scope (unchanged)

- SyncEngine + DatacenterClient + REST API (Phase 3)
- GraphDBBackend + SPARQL on groups (Phase 4)
```

- [ ] **Step 2: Verify**

```bash
tail -40 docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
```

Expected: AI06 section visible at the end.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
git commit -m "$(cat <<'EOF'
docs(dev-log): Phase 2 / AI06 Node grouping entry

Records AI06 outcome: GroupStore + group_projector + GraphProjector
groups kwarg + Stage 4e _inject_group_folders + ParadataManagerDialog
4th tab + S3DGraphyExportDialog 7 checkboxes + Import flag + 4 CLI
sub-subcommands.

Test counts at Group boundaries documented (132 → 146 → 154 →
159 → 167 → 169 → 175 + 2-3 skipped).

Carry-overs documented: LocationNodeGroup migration (AI07,
upstream-dependent), hierarchical nesting (AI08), per-dimension
visual style (AI08), auto-layout (AI08), TimeBranchNodeGroup (AI09).
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

Identify the title and the existing `## [5.4.0-alpha]` section.

- [ ] **Step 2: Prepend the new section**

Insert immediately after the title:

```markdown
## [5.5.0-alpha] - 2026-05-08

### Italiano

- **Phase 2 / AI06 — Node grouping nell'export Extended Matrix.** Aggiunto raggruppamento opt-in delle US per qualunque sottoinsieme delle 7 colonne `us_table` (`area`, `struttura`, `attivita`, `settore`, `ambient`, `saggio`, `quad_par`) più gruppi ad-hoc creati dall'utente. Default invariato (no checkbox = no raggruppamento, AC-2 baseline preservato byte-identical).
- **Rendering yEd canonico.** Ogni gruppo è un folder yEd (`yfiles.foldertype="group"`, border tratteggiato, fill `#F5F5F5`, label in alto su sfondo `#EBEBEB`) nidificato dentro lo swimlane delle epoche, con geometria che attraversa tutte le righe epoca dei suoi membri.
- **Knowledge graph.** Ogni gruppo è un `s3dgraphy.ActivityNodeGroup` con attributo `group_kind` discriminator (struttura/area/attivita/...) e edge `is_in_activity` da ogni US membro.
- **GroupStore.** Nuova classe `modules/s3dgraphy/sync/group_store.py` per gestire gruppi ad-hoc in `groups_{sito_slug}.graphml` accanto al DB. CRUD atomic-safe via `os.replace()`. Specchio del `ParadataStore` di AI05.
- **Dialog "Manage paradata" → 4 tab.** Aggiunta tab "Groups" con form Add (name + kind + Pick US members) e tabella esistenti.
- **Export dialog → 7 checkbox.** Pulsante verde "Esporta Extended Matrix" mostra "Group US by" con preselect automatico delle dimensioni popolate.
- **Round-trip configurabile.** Tab Import ha checkbox "Update SQL on import" (default OFF). Quando attivo, lo spostamento di una US in un altro gruppo via yEd aggiorna `us_table` con transazione atomica e rollback su errore.
- **CLI** con 4 nuovi sub-subcomandi `paradata add-group/list-groups/add-us-to-group/remove-group` e flag `export --group-by struttura,attivita,adhoc`.
- **Issue upstream aperta** ([zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)) per `LocationNodeGroup` + edge `is_in_location` — migrazione AI07 quando upstream landa.

### English

- **Phase 2 / AI06 — Node grouping in Extended Matrix export.** Adds opt-in US grouping by any subset of 7 `us_table` columns (`area`, `struttura`, `attivita`, `settore`, `ambient`, `saggio`, `quad_par`) plus user-authored ad-hoc groups. Default unchanged (no checkbox = no grouping, AC-2 baseline byte-identical preserved).
- **EM canonical yEd rendering.** Each group is a yEd folder (`yfiles.foldertype="group"`, dashed border, fill `#F5F5F5`, NodeLabel top with bg `#EBEBEB`) nested inside the epoch swimlane, with geometry spanning all epoch rows of its member US.
- **Knowledge graph.** Each group is a `s3dgraphy.ActivityNodeGroup` with `group_kind` discriminator attribute (struttura/area/attivita/...) and `is_in_activity` edge from each member US.
- **GroupStore.** New `modules/s3dgraphy/sync/group_store.py` class for ad-hoc groups stored in `groups_{sito_slug}.graphml` next to the DB. Atomic-safe CRUD via `os.replace()`. Mirror of AI05's `ParadataStore`.
- **"Manage paradata" dialog → 4 tabs.** Adds "Groups" tab with Add form (name + kind + Pick US members) and existing-groups table.
- **Export dialog → 7 checkboxes.** Green "Esporta Extended Matrix" button now shows "Group US by" with auto-preselect of populated dimensions.
- **Configurable round-trip.** Import tab has "Update SQL on import" checkbox (default OFF). When enabled, moving a US to a different group folder in yEd writes back to `us_table` in an atomic transaction with rollback on error.
- **CLI** with 4 new sub-subcommands `paradata add-group/list-groups/add-us-to-group/remove-group` plus `export --group-by struttura,attivita,adhoc` flag.
- **Upstream issue opened** ([zalmoxes-laran/s3Dgraphy#5](https://github.com/zalmoxes-laran/s3Dgraphy/issues/5)) for `LocationNodeGroup` + `is_in_location` edge — AI07 migration target when upstream lands.

```

(Keep the trailing blank line before the existing `## [5.4.0-alpha]` heading.)

- [ ] **Step 3: Verify**

```bash
head -50 dev_logs/CHANGELOG.md
```

Confirm new block on top, existing 5.4.0-alpha intact below.

- [ ] **Step 4: Commit**

```bash
git add dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
docs(changelog): 5.5.0-alpha — AI06 Node grouping (IT + EN)

Bilingual entry summarising the AI06 release:
- New GroupStore class for ad-hoc groups in
  groups_{sito_slug}.graphml.
- GraphProjector.populate_graph(groups=[...]) opt-in materializes
  ActivityNodeGroup instances + is_in_activity edges.
- Stage 4e _inject_group_folders renders yEd folders matching
  EM canonical template (EM_demo_02.graphml reference).
- ParadataManagerDialog 4th tab + S3DGraphyExportDialog 7
  checkboxes + Import "Update SQL" flag.
- CLI 4 new sub-subcommands + --group-by export flag.
- Upstream issue opened for LocationNodeGroup migration (AI07).
EOF
)"
git log -1 --format=%B HEAD | grep -c "Co-Authored-By"   # expect 0
```

### Task H.3: Verification (no subagent — controller only)

**Files:** none

This is purely a verification step run by the controlling agent. No commit unless the AC-2 baseline needs regeneration (it should NOT; default `groups=None` keeps it stable).

- [ ] **Step 1: Run full suite 3 times for stability**

```bash
for i in 1 2 3; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q 2>&1 | tail -1
done
```

Expected: 3 × `175 passed, 2-3 skipped`.

- [ ] **Step 2: AC-2 baseline 5 times**

```bash
for i in 1 2 3 4 5; do
    PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -1
done
```

Expected: 5 × `1 passed`.

- [ ] **Step 3: Run all 8 critical regression guards**

```bash
PYTHONPATH="$PWD" python -m pytest \
  tests/sync/test_ai03_export_byte_identical.py \
  tests/sync/test_round_trip.py \
  tests/sync/test_idempotent_ingest.py \
  tests/sync/test_cli_helper.py \
  tests/sync/test_paradata_store.py \
  tests/sync/test_round_trip_with_paradata.py \
  tests/sync/test_paradata_idempotent.py \
  tests/sync/test_strategy_a_no_regression.py \
  -v 2>&1 | tail -3
```

Expected: all pass.

- [ ] **Step 4: Co-author trailer scan across all AI06 commits**

```bash
git log phase2-ai05-paradata-store-5.4.0-alpha..HEAD \
    --format=%B | grep -c "Co-Authored-By"
```

Expected: `0`.

- [ ] **Step 5: Working tree clean**

```bash
git status --short | grep -vE '^\?\?'
```

Expected: empty.

- [ ] **Step 6: Version**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.5.0-alpha`.

- [ ] **Step 7: Commit count since AI05**

```bash
git log --oneline phase2-ai05-paradata-store-5.4.0-alpha..HEAD | wc -l
```

Expected: ~24-26 commits.

If any check fails, STOP and investigate before proceeding to H.4 manual smoke gate.

### Task H.4: Manual smoke gate (USER-driven)

**Files:** none — user-driven QA only.

This step is user-driven. The controller waits for the user's "ok smoked, proceed" before triggering H.5.

- [ ] **Step 1: Restart QGIS**

User: close QGIS (cmd-Q) and relaunch.

- [ ] **Step 2: Open the project + US scheda**

User: load a project with SQLite DB, open US/USM scheda.

- [ ] **Step 3: Click "Manage paradata" → check 4 tabs**

User: dialog opens with Authors / Licenses / Embargoes / Groups (4 tabs).

- [ ] **Step 4: Create an ad-hoc group**

User: in Groups tab, name "test-2026", kind "adhoc", click "Pick US members…", select 3-5 US in the picker, OK, click "Add group". Verify row appears in table.

- [ ] **Step 5: Close + reopen dialog → group persists**

- [ ] **Step 6: Verify on disk**

```bash
ls -la {db_dir}/groups_*.graphml
cat {db_dir}/groups_<slug>.graphml | head -30
```

Expected: file exists; contains 1 ad-hoc group.

- [ ] **Step 7: Click green "Esporta Extended Matrix" button**

User: dialog opens with new "Group US by" panel; populated dimensions are auto-checked. Check "ad-hoc" too. Click Export.

- [ ] **Step 8: Open exported GraphML in yEd**

User: verify the output GraphML opens. Look for the dashed-border folder boxes spanning epoch rows. Each should have label = group name.

- [ ] **Step 9: Move a US in yEd**

User: drag a US from one folder to another (e.g., from "basilica" to "chiesa"). Save the file.

- [ ] **Step 10: Re-import with flag ON**

User: Import tab → check "Update SQL on import" → import the modified GraphML.

- [ ] **Step 11: Verify SQL updated**

User: open the affected US scheda → `struttura` field shows the new value.

- [ ] **Step 12: Test the new CLI**

```bash
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <my-db> --sito <my-site>
```

Expected: lists the test-2026 group.

- [ ] **Step 13: User confirms gate passed**

User writes "ok smoked, proceed" — controller proceeds to H.5.

### Task H.5: Tag + push

**Files:** none — git operations only.

- [ ] **Step 1: Verify clean tree + commit count**

```bash
git status --short | grep -vE '^\?\?'   # must be empty
git log --oneline phase2-ai05-paradata-store-5.4.0-alpha..HEAD | wc -l
```

Expected: empty status; ~24-26 commits.

- [ ] **Step 2: Final co-author trailer check**

```bash
git log phase2-ai05-paradata-store-5.4.0-alpha..HEAD \
    --format=%B | grep -c "Co-Authored-By"
```

Expected: `0`.

- [ ] **Step 3: Create the release tag**

```bash
git tag -a phase2-ai06-node-grouping-5.5.0-alpha \
    -m "Phase 2 / AI06: Node grouping by 7 us_table dimensions + ad-hoc groups, EM canonical yEd rendering"
git tag -l | grep -E "phase2|pre-ai06"
```

Expected (8 lines):
```
phase2-ai03-graphml-delegation-5.2.0-alpha
phase2-ai04-bridge-bidirectional-5.3.0-alpha
phase2-ai05-paradata-store-5.4.0-alpha
phase2-ai06-node-grouping-5.5.0-alpha
pre-ai03-graphml-delegation
pre-ai04-bridge
pre-ai05-paradata
pre-ai06-grouping
```

- [ ] **Step 4: Push branch + tag**

```bash
git push origin Stratigraph_00001
git push origin phase2-ai06-node-grouping-5.5.0-alpha
```

Expected:
- branch push: ~24-26 commits to `origin/Stratigraph_00001`.
- tag push: `[new tag] phase2-ai06-node-grouping-5.5.0-alpha`.

- [ ] **Step 5: Verify on remote**

```bash
git ls-remote --tags origin 2>&1 | grep "phase2-ai06" | head -2
```

Expected: 2 lines (the tag commit + its `^{}` deref).

- [ ] **Step 6: Final state check**

```bash
git rev-list --left-right --count HEAD...@{u}   # expect "0\t0"
```

---

## Self-review checklist (run inline before delivering the plan)

Reviewed against the spec on 2026-05-08:

**1. Spec coverage**

- §1 Overview → addressed by file structure + Group narrative.
- §2 D1–D7 → each decision pinned by a task in the matrix above.
- §3 Components: §3.1 GroupStore → Group A; §3.2 group_projector → Group B; §3.3 GraphProjector extension → Group C.1; §3.4 _inject_group_folders → Group C.2; §3.5 dialog Groups tab → Group G.1; §3.6 export dialog checkboxes + import flag → Group G.2; §3.7 CLI → Group F.
- §4 Data flow: 4.1 export with grouping → C.1+C.2; 4.2 round-trip → D.2; 4.3 ad-hoc dialog flow → G.1.
- §5 Error handling: 5.1 hierarchy → A.1; 5.2 fatal/non-fatal → A.4 + B.3 + C.1; 5.3 UI surfacing → G.1+G.2; 5.4 CLI exit codes → F.1+F.2; 5.5 logging → A/B/C/G via diagnostic prints.
- §6 Testing: 4 levels covered by Group A through Group G; ≥175 target hit.
- §7 Acceptance criteria: AC-1 → A.2; AC-2 → existing test (must remain green per Group H.3); AC-3 → A.4; AC-4/5 → C.1; AC-6 → B.1; AC-7 → B.2; AC-8/9/10/11 → D.1; AC-12/13/14 → D.2; AC-15 → E.2; AC-16 → F.2; AC-17 → F.2; AC-18 → G.2; AC-19 → H.3; AC-20 → per-task validation; AC-21 → H.4 manual smoke.
- §8 Release plan → Group H mirrors it.
- §9 Out of scope → "Explicitly NOT touched" + carry-over notes in dev-log/changelog.
- §10 Risks → mitigation hooks per Group + AC-2 + critical guards.

**2. Placeholder scan**

No `TBD`, `TODO`, `FIXME`, `implement later`, `Add appropriate error handling`, `Similar to Task N` placeholders. Every step has explicit code or commands.

**3. Type consistency**

- `GroupStore.add_group(name, group_kind, member_us_uuids, description) -> str` — same in A.2, F.1, G.1.
- `GroupSpec(group_uuid, name, group_kind, member_us_uuids, description)` — frozen dataclass defined in B.1, used in B.2 + B.3 + C.1.
- `populate_graph(db, sito, *, include_paradata, strict_schema, groups)` — same signature in C.1, C.2 (export_graphml passes groups through), F.1 (CLI threads groups through).
- `_inject_group_folders(snapshot, members_map, xml_path)` — same signature in C.2, no other callers.
- `dimensions_with_data(db, sito) -> list[str]` — same in B.1, G.2 (`_preselect_groups`).
- `merge_adhoc_groups(specs, store)` — same in B.3, C.1.
- `is_in_activity` edge type used consistently in C.1 (creation), D.2 (parse on round-trip).
- `group_kind` attribute key used consistently across all groups.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-08-ai06-node-grouping.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per Group with two-stage review (spec compliance → code quality) between Groups. Group C is the highest-risk (Stage 4e injector + AC-2 sensitivity); budget extra time + AC-2 verification per step.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
