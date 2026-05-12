# PG-UIFix — Design Spec (hotfix milestone)

**Date:** 2026-05-12
**Branch:** Stratigraph_00001
**Predecessor tag:** `yed-import-parsers-5.7.7-alpha` (commit `5d666c67`)
**Target tag:** `pg-uifix-5.7.8-alpha`

---

## 1. Goal

Hotfix milestone introduced **between yE-C and yE-D** to unblock PostgreSQL backend users. Removes 5 obsolete SQLite-only guards in UI and bridge code that should have been removed when Phase 3 PG-Compat shipped (Foundation + PG-A through PG-D, 2026-05-10/11) but were left in place by oversight.

**Without this fix, PG-backed pyarchinit users cannot:**
- Open the Paradata Manager dialog (Bug 1) — blocked with "Paradata management requires a SQLite-backed pyarchinit project"
- Export GraphML from the matrix viewer (Bug 2) — silently skipped with "GraphML skipped: postgresql backend not yet supported"
- Import GraphML files (Bug-1-like, lines 746+834 in s3dgraphy_dot_bridge) — blocked with same SQLite-only message

This is a **mechanical hotfix** — removes obsolete code paths, no new feature. ~225 LOC total.

## 2. Trigger

User reported (2026-05-12, after yE-C SHIPPED) three PG-backend bugs while testing the plugin on PostgreSQL. Diagnosis revealed:

- Phase 3 (PG-Compat) shipped backend support in `ParadataStore`, `GroupStore`, `export_graphml()`, `node_uuid migration` library — all PG-aware via `_resolve_db_handle` shim.
- BUT the calling UI code (dialogs, bridge wrappers) still had legacy guards `if not handle.is_postgres` / `if backend_is_postgres: skip` / `requires SQLite-backed` written pre-Phase-3 that block the user even though the underlying machinery now works.

The guards are **obsolete code**. This milestone removes them.

## 3. Decisions captured during brainstorming (2026-05-12)

Three delta questions resolved (user followed all my recommendations):

| Q | Decision | Rationale |
|---|---|---|
| Q1 Bug 3 inclusion | **β — Defer Bug 3** (media not loading in forms on PG) | Bug 3 needs diagnosis — root cause unknown; PG-UIFix focused on confirmed mechanical Bug 1+2. Media Manager works as workaround. |
| Q2 Test strategy | **γ — 2 L0 focused + manual** | Minimal test scaffold (mock db_manager with PG handle), plus manual QGIS verification gate at Group C |
| Q3 Scope of guard removal | **α — Fix the 5 confirmed spots** | All 5 found by initial grep are obsolete post-Phase-3. No full-codebase audit (would conflate legitimate branching with obsolete guards). |

## 4. Architecture

### Files modified (5 — 2 production + 3 docs)

| Path | Change | LOC delta |
|---|---|---|
| `gui/dialog_paradata_manager.py` | Remove 3 SQLite-only guards at lines 200-206, 208-217, 410-414. Replace `db_manager.get_sqlite_path() if self.db_manager else None` + null check with direct `ParadataStore(self.db_manager, self.sito)` / `GroupStore(...)` calls. The `_resolve_db_handle` shim accepts `Path | DbHandle | str` since Foundation. | ~−30 / +10 |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | Remove `if backend_is_postgres:` skip branch at lines 191-206 (graphml export). Remove "Import requires SQLite-backed" guards at lines 746 + 834 (PG-A imported the migration library + ingestor works on PG since 2026-05-10). | ~−40 / +5 |
| `metadata.txt` | Bump `version=5.7.7-alpha` → `version=5.7.8-alpha` | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.8-alpha] PG-UIFix` section | ~50 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Prepend PG-UIFix section ABOVE yE-C | ~30 |

### Files created (1 test file)

| Path | Responsibility |
|---|---|
| `tests/sync/test_pg_uifix.py` | 2 L0 regression tests pinning the absence of the SQLite-only guards | ~60 LOC |

### Files NOT touched

- **`tabs/US_USM.py`** — Bug 3 (media not loading) deferred to separate diagnosis
- Pyarchinit-projected branch of `populate_list()` and `_run()` — sacred (AC-2)
- yE-A/B/C modules (`yed_detector.py`, `yed_classifier.py`, `yed_table_parser.py`, `yed_group_walker.py`) — invariant
- DB schema, requirements.txt — no changes

### Total LOC

- Production: ~85 (deltas across 2 files)
- Test: ~60 (one new file)
- Docs: ~80
- **Grand total: ~225 LOC** — smallest milestone in the rollout

## 5. Fix details per spot

### Spot 1 — `gui/dialog_paradata_manager.py:198-206` (Bug 1 main)

**Current (obsolete):**
```python
def _store(self):
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    db_path = self.db_manager.get_sqlite_path() if self.db_manager else None
    if db_path is None:
        QMessageBox.critical(
            self, "No SQLite DB",
            "Paradata management requires a SQLite-backed pyarchinit project.")
        return None
    return ParadataStore(db_path, self.sito)
```

**Fix:**
```python
def _store(self):
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    if self.db_manager is None:
        QMessageBox.critical(
            self, "No DB",
            "Paradata management requires an active pyarchinit project.")
        return None
    return ParadataStore(self.db_manager, self.sito)
```

The null-check on `db_manager` itself is preserved (legit: dialog can be instantiated without DB context). The SQLite-only check is removed. `ParadataStore.__init__` uses `_resolve_db_handle` shim that accepts the manager (PG-D era).

### Spot 2 — `gui/dialog_paradata_manager.py:208-217` (Bug 1 — Group Store variant)

Same pattern as Spot 1 for `_group_store()`. Replace `get_sqlite_path()` + SQLite-only error with direct `GroupStore(self.db_manager, self.sito)`.

### Spot 3 — `gui/dialog_paradata_manager.py:410-414` (Bug 1 — US picker variant)

US picker uses the same SQLite-only block. Replace with PG-compatible call.

### Spot 4 — `modules/s3dgraphy/s3dgraphy_dot_bridge.py:191-206` (Bug 2 main)

**Current (obsolete):**
```python
if backend_is_postgres:
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
    # ... existing PG-aware export code ...
```

**Fix**: remove the `if backend_is_postgres:` branch entirely. The `else:` body becomes the unconditional path. `export_graphml()` from PG-B (2026-05-10) handles both SQLite and PG via `DbHandle`.

```python
# (was: backend-is-postgres-skip removed in PG-UIFix 5.7.8-alpha)
from .sync.graphml_writer import (
    export_graphml,
    EmptyGraphError,
    GraphMLExportError,
)
# ... existing PG-aware export code unchanged ...
```

### Spots 5 + 6 — `modules/s3dgraphy/s3dgraphy_dot_bridge.py:746, 834` (Bug-1-like — Import flow)

These two lines have the same `"Import requires a SQLite-backed pyarchinit project."` block. PG-A shipped node_uuid migration on PG; PG-C shipped GraphIngestor on PG. Both flows now work on PG. Remove the SQLite-only check.

## 6. Test strategy

### 2 L0 tests in `tests/sync/test_pg_uifix.py`

```python
"""PG-UIFix (5.7.8-alpha): regression tests pinning the absence of
SQLite-only guards in dialog_paradata_manager and s3dgraphy_dot_bridge.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def test_paradata_manager_does_not_block_on_pg_handle():
    """Bug 1 regression: dialog_paradata_manager._store() returns a
    ParadataStore instance when db_manager is a PG-backed db_manager
    (i.e., get_sqlite_path() would have returned None).

    Pre-PG-UIFix: blocked with "Paradata management requires a
    SQLite-backed pyarchinit project."
    """
    # Mock a db_manager that simulates PG backend
    mock_db_manager = MagicMock()
    mock_db_manager.get_sqlite_path = MagicMock(return_value=None)

    # Mock the dialog so we can call _store() without Qt rendering
    # (Use the actual dialog class but skip __init__; manually inject
    # db_manager + sito attributes)
    from gui.dialog_paradata_manager import (
        ParadataManagerDialog  # or similar class name
    )

    dialog = ParadataManagerDialog.__new__(ParadataManagerDialog)
    dialog.db_manager = mock_db_manager
    dialog.sito = "TestSite"

    # _store() should NOT show QMessageBox + return None
    with patch("gui.dialog_paradata_manager.QMessageBox") as mock_qmb:
        # Mock ParadataStore so we don't actually hit DB
        with patch("modules.s3dgraphy.sync.paradata_store.ParadataStore"
                   ) as mock_store:
            result = dialog._store()
            # Assert: no QMessageBox.critical was called with
            # "requires SQLite-backed"
            for call in mock_qmb.critical.call_args_list:
                args = call.args
                assert "SQLite-backed" not in str(args), \
                    f"Obsolete guard still fires: {args}"
            # Assert ParadataStore was instantiated with the db_manager
            mock_store.assert_called_once_with(mock_db_manager, "TestSite")


def test_graphml_export_runs_on_pg_backend(tmp_path):
    """Bug 2 regression: s3dgraphy_dot_bridge export flow does NOT
    set graphml_status='postgresql backend not yet supported' when
    backend_is_postgres=True.

    Pre-PG-UIFix: skipped graphml export branch.
    """
    # We test by inspecting that export_graphml is called even when
    # backend_is_postgres path would have triggered.
    # The function path under test is the matrix exporter in
    # s3dgraphy_dot_bridge. Build a minimal call context.

    # Mock the bridge's export function entry point.
    # Mock export_graphml to return a known dummy path.
    with patch(
        "modules.s3dgraphy.sync.graphml_writer.export_graphml"
    ) as mock_export:
        mock_export.return_value = {"nodes": 5, "edges": 3}

        # Mock backend_is_postgres = True via the helper used
        # internally (TBD per plan-time location).
        # Invoke the dot-bridge export function.
        # Assert export_graphml was called AND exported_files
        # contains 'graphml' key (not 'graphml_status' with
        # "not yet supported" reason).

        # Skeleton (full impl in Task A.4 of plan):
        from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge
        # Build minimal args + invoke export
        # Assert mock_export.called
        # Assert no exported_files['graphml_status'] with PG-skip reason
        pass  # Plan A.4 fills in the call site
```

NOTE: exact mock points (`gui.dialog_paradata_manager.QMessageBox` patch path, etc.) will be confirmed at plan-time by inspecting imports. The skeletons above show the test intent.

### Manual QGIS verification (Group C user gate)

1. **Paradata manager on PG**: open form US in PG-backed project → click "Manage paradata" → dialog opens WITHOUT "requires SQLite-backed" error → can add authors
2. **GraphML export on PG**: open matrix viewer → "Export Matrix" → see `✅ GraphML → /path/to/file.graphml` in the log (NOT `ℹ️ GraphML skipped`)
3. **SQLite still works**: switch to SQLite project → repeat both flows → verify identical behavior to pre-PG-UIFix (no regression)

### Regression gates after Group A

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py tests/sync/test_round_trip.py tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v   # AC-2 + 3 critical SQLite gates
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v   # 8 PG-D L2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_yed_*.py tests/sync/test_table_parser_integration.py tests/sync/test_group_walker_integration.py tests/sync/test_yed_parsers_orchestration.py -v   # 33 yE-A/B/C
PYTHONPATH="$PWD" python -m pytest tests/sync/test_pg_uifix.py -v   # 2 new
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

### Test count progression

| Milestone | Passed | Skipped |
|---|---|---|
| Pre PG-UIFix (post yE-C) | 289 | 33 |
| **Post PG-UIFix Group A (+2)** | **291** | 33 |
| Post Group B/C (docs) | 291 | 33 |
| PG online + psycopg2 | 299 | 12 |

## 7. Decomposition (5 Groups — small hotfix following established pattern)

| Group | Scope | Subagent | LOC est |
|---|---|---|---|
| Group 0 | Pre-flight + rollback tag `pre-pg-uifix` + baseline test counts | Controller | — |
| Group A | Fix 5 obsolete guards in 2 files + 2 L0 tests | 1 subagent | ~85 prod + ~60 test |
| Group B | Docs + version 5.7.7 → 5.7.8-alpha + bilingual CHANGELOG + dev-log PG-UIFix section ABOVE yE-C | 1 subagent | ~80 LOC docs |
| Group C | Annotated tag `pg-uifix-5.7.8-alpha` + USER APPROVAL GATE + push | 1 subagent (stops at C.4); controller pushes | — |
| Memory | Update memory: `project_pg_compat_progress.md` with PG-UIFix appendix; `project_yed_import_progress.md` with yE-D version shift note; `MEMORY.md` index. Plus update yE-D spec file (`2026-05-12-yed-import-pipeline-design.md`) target tag references from `5.7.8-alpha` to `5.7.9-alpha`. | Controller | ~30 |

### Effort estimate

~0.5-1 person-day dev + ~0.5 review = ~1-1.5 calendar days. The smallest milestone yet.

## 8. Acceptance criteria

### Per Group A

- 5 obsolete guards removed from `dialog_paradata_manager.py` (3 spots) + `s3dgraphy_dot_bridge.py` (2 spots — `imported requires SQLite` lines)
- `if backend_is_postgres:` skip branch removed from `s3dgraphy_dot_bridge.py:191-206` (Bug 2)
- 2 L0 tests pass with exact names from §6
- AC-2 byte-identical PRESERVED
- 3 critical SQLite regression gates PRESERVED
- 5 yE-A + 12 yE-B + 16 yE-C + 8 PG-D L2 tests PRESERVED
- Full suite: 291 passed, 33 skipped (PG offline)
- Strict trailer check returns 0

### Per Group B

- `metadata.txt` shows `version=5.7.8-alpha`
- Bilingual CHANGELOG entry prepended
- Dev-log PG-UIFix section above yE-C
- Strict trailer check returns 0

### Per Group C

- Annotated tag `pg-uifix-5.7.8-alpha` created locally
- Tag points to Group B commit
- Trailer check on tag message returns 0
- **STOP at Task C.4**: user manual test plan presented (3 manual checks per §6)
- Push after `approvato`

### Per Memory (Group D-equivalent)

- `project_pg_compat_progress.md` updated with PG-UIFix appendix
- `project_yed_import_progress.md` updated with yE-D version shift (5.7.8 → 5.7.9-alpha)
- `MEMORY.md` index updated to reflect PG-UIFix SHIPPED
- **yE-D spec file** (`docs/superpowers/specs/2026-05-12-yed-import-pipeline-design.md`) updated to reference target tag `yed-import-pipeline-5.7.9-alpha` instead of `5.7.8-alpha` (sed-style search/replace, ~5 occurrences)

## 9. Out of scope

### Deferred to separate milestone

- **Bug 3** (media not loading in US/Pottery/Artefact forms on PG) — needs diagnosis cycle with user-provided error logs from QGIS Python Console. Future tag candidates: `pg-media-fix-5.7.8.1-alpha` or accorpato in yE-Closure.

### Explicitly NEVER

- Full-codebase grep audit for obsolete `if backend_is_postgres` patterns (Q3=α explicitly chose narrow scope — the 5 confirmed spots)
- Refactoring of `dialog_paradata_manager.py` beyond removing the 3 guards
- Refactoring of `s3dgraphy_dot_bridge.py` beyond removing the 3 obsolete branches
- yE-D milestone work (this is preparatory only)
- DB schema migrations
- New features

### Deferred to yE-Closure

- Documentation pass updating tutorials to mention PG support consistently across all features

## 10. Plan-time investigation checklist

Before writing Group A code, the plan-writing phase must:

1. **Locate exact line numbers in current state**: re-read `dialog_paradata_manager.py:198-220, 408-417` and `s3dgraphy_dot_bridge.py:188-220, 740-760, 825-850` to confirm exact context (lines may shift slightly after PG-D and yE-C changes)
2. **Verify `_resolve_db_handle` import chain**: confirm `ParadataStore.__init__` and `GroupStore.__init__` correctly route `db_manager` through `_resolve_db_handle` (PG-D shipped this)
3. **Find the exact ParadataManagerDialog class name** in `dialog_paradata_manager.py` (for the L0 test mock target)
4. **Find the exact export entry point** in `s3dgraphy_dot_bridge.py` that wraps the matrix exporter (for the L0 test)

## 11. References

- **Parent spec**: `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md` (Phase 3 PG-Compat)
- **PG-A spec**: `docs/superpowers/specs/2026-05-10-pg-a-migration-design.md` (shipped node_uuid migration on PG)
- **PG-B spec**: `docs/superpowers/specs/2026-05-10-pg-b-export-design.md` (shipped graphml export on PG via `DbHandle`)
- **PG-D spec**: `docs/superpowers/specs/2026-05-11-pg-d-paradata-design.md` (shipped `ParadataStore` + `GroupStore` on PG)
- **yE-A + yE-B + yE-C specs**: `docs/superpowers/specs/2026-05-12-yed-import-*.md`
- **PG-Compat memory**: `~/.claude/projects/.../memory/project_pg_compat_progress.md`
- **yE memory**: `~/.claude/projects/.../memory/project_yed_import_progress.md`
- **Bug-fix locations**:
  - `gui/dialog_paradata_manager.py:200-217` (Bug 1 main + variant)
  - `gui/dialog_paradata_manager.py:414` (Bug 1 US picker variant)
  - `modules/s3dgraphy/s3dgraphy_dot_bridge.py:191-206` (Bug 2)
  - `modules/s3dgraphy/s3dgraphy_dot_bridge.py:746` + `834` (Bug-1-like)

## 12. Approval log

- Section 1 Architecture + files: approved 2026-05-12
- Section 2 Test strategy + decomposition: approved 2026-05-12
- **Spec final review**: pending user (this step)
