# Consolidation 5.7.4-alpha Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Phase 3 with the deferred QSettings UI override for the workspace dir (deferred from PG-D Q1=b) + docs cleanup. Add a 3-tier fallback chain in `_workspace.py` so the workspace root can be configured via env var > QSettings > default. Add a "Paradata Workspace" section to `gui/pyarchinitConfigDialog.py`. Bump version to `5.7.4-alpha`. Write a Phase 3 closure summary in CHANGELOG + dev-log.

**Architecture:** Minimal-scope final milestone. ~310 LOC total (~120 prod + ~80 test + ~110 docs). The helper `_resolve_workspace_root() -> Path` does the 3-tier lookup; the PG branch of the existing `_resolve_workspace_dir()` delegates to it (SQLite branch UNCHANGED). UI section is additive Qt code in a 10241-line dialog file. 4 new L0 unit tests pin the env var precedence + default fallback + tilde expansion. QSettings layer is manually-verified in QGIS (no automated test). After Consolidation ships, Phase 3 is officially complete.

**Tech Stack:** Python 3.9+, SQLAlchemy 2.0+ (already a dep), PyQt5/QtCore (lazy import for `_workspace.py`, explicit for the dialog UI), pytest.

**Spec source of truth:** `docs/superpowers/specs/2026-05-11-consolidation-design.md` (commit `fdb20de4`)

**Predecessor releases:**
- PG-D: tag `phase3-pgcompat-d-paradata-5.7.3-alpha` (`b8d73058`)
- PG-C: tag `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`)
- PG-B: tag `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
- PG-A: tag `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- Foundation: tag `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` — Phase 3 state
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule

**Commit-message rule:** Never include trailers identifying Claude as a co-author. After each commit run `git log -1 --format=%B HEAD | grep -cE '^Co-Authored-By:' ` — must return `0`. **Note:** use the regex-anchored check (the `^Co-Authored-By:` form) — a simple `grep -c Co-Authored-By` can be fooled by body prose mentioning the rule. Avoid the literal hyphenated phrase in commit body text where possible.

**Local PG:** `postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg` (USER pre-created during Foundation). In dev env psycopg2 NOT installed → PG-D's 8 L2 tests skip cleanly. New L0 tests in this milestone don't need PG.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `tests/sync/test_workspace_root.py` | 4 L0 unit tests for `_resolve_workspace_root()` covering env var precedence, default fallback, empty env var skip-through, tilde expansion. Pure pytest, no Qt. ~80 LOC. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/_workspace.py` | Add `_resolve_workspace_root() -> Path` helper (3-tier fallback). Update `_resolve_workspace_dir()` PG branch to delegate to `_resolve_workspace_root()` instead of hardcoding `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"`. SQLite branch UNCHANGED. QSettings import lazy + fail-soft. | ~40 LOC delta |
| `gui/pyarchinitConfigDialog.py` | New "Paradata Workspace" QGroupBox (QLabel + QLineEdit + Browse + Reset buttons), reads/writes QSettings key `pyarchinit/paradata_workspace`. Inserted into the existing "DB Sync" tab content area (near line ~1149 where the existing "Synchronization Operations" buttons group sits). | ~80 LOC additive |
| `metadata.txt` | Bump `5.7.3-alpha` → `5.7.4-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.4-alpha]` section + Phase 3 closure summary prose. | ~60 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add "Phase 3 — Consolidation (5.7.4-alpha)" section + closing Phase 3 summary paragraph. | ~50 |

### Explicitly NOT touched

- Public API signatures of `populate_graph`, `populate_list`, `export_graphml`, `dimensions_with_data`, `build_groups_from_sql`, `ParadataStore.__init__`, `GroupStore.__init__` — `db_path` keyword preserved (rename deferred per Q1=(2))
- `paradata_store.py` and `group_store.py` — unchanged from PG-D
- `_db_handle.py` (Foundation — no changes)
- All SQL query content (covered by PG-A/B/C/D)
- `scripts/migrations/_common.py` (no DRY-up adoption — deferred)
- AC-2 + 3 SQLite regression gates + 8 PG-D L2 tests — must stay green untouched

### Total LOC

- Production: ~120 modified (~40 in `_workspace.py` + ~80 UI additive)
- Test: ~80 (1 new L0 file)
- Docs: ~110
- **Grand total: ~310 LOC** (smallest milestone in Phase 3)

---

## Test strategy

- **L0 unit (NEW):** `test_workspace_root.py` with 4 cases covering `_resolve_workspace_root()`. Pure pytest with `monkeypatch.setenv`. No Qt dependencies. Always runs (no skip).
- **L1 SQLite (existing 250):** Stay green. The SQLite branch of `_resolve_workspace_dir()` is UNCHANGED.
- **L2 PG (existing 8 from PG-D in `test_paradata_store_pg.py` + `test_group_store_pg.py`):** Stay green. They use `monkeypatch.setattr(Path, "home", lambda: tmp_path)`. The new helper's default branch still calls `Path.home()` — so the monkeypatch reaches it transparently.
- **L3 regression guards (existing, MUST stay green):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v    # critical gate
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v      # critical gate
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v    # critical gate
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v  # PG-D L2
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

After Group A, all of these must PASS (or SKIP for the PG L2 ones if PG offline). If any breaks, STOP and investigate.

Decision-pinning matrix:

| Decision / Acceptance | Pinning test |
|---|---|
| Q1=(2) minimal scope (no rename, no parametrized) | Plan structure: no rename tests added; no parametrize attribute added to existing tests |
| Q2=(b) 3-tier fallback (env > QSettings > default) | Tests #1, #2, #3, #4 in `test_workspace_root.py` |
| Approach 1 (helper + UI) | Tests #1-4 cover helper. UI verified manually in QGIS. |
| `_resolve_workspace_root()` deterministic | Each of the 4 tests asserts a specific resolution result |
| SQLite path preserved | Existing 3 critical SQLite regression gates stay green untouched |
| PG-D 8 L2 tests preserved | They use `monkeypatch.setattr(Path, "home", ...)` → `_resolve_workspace_root()` default branch calls `Path.home()` → monkeypatch reaches it |
| QSettings UI read/write | Manual verification in QGIS (no automated Qt test) |
| AC-2 preservation | AC-2 existing (untouched — only PG branch of `_resolve_workspace_dir` modified) |

Test count progression:

- Pre Consolidation (post PG-D): `250 passed, 33 skipped` (PG offline)
- Post Group A (helper + 4 new L0 tests): `254 passed, 33 skipped`
- Post Group B (UI only, no test): unchanged
- Post Group C (docs only): unchanged

Final:
- PG offline: **254 passed, 33 skipped**
- PG online + psycopg2: **262 passed, 12 skipped**

---

## Group 0 — Pre-flight & rollback safety

### Task 0.1: Verify clean starting point

**Files:** none (git operation)

- [ ] **Step 1: Confirm starting point**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git status --short | grep -vE '^\?\?'
git log --oneline -3
git rev-list --left-right --count HEAD...@{u}
```

Expected: tracked changes empty, last commit `fdb20de4 spec(consolidation): ...`, `0\t0` ahead-behind.

- [ ] **Step 2: Verify predecessor tag**

```bash
git tag --list | grep -E "phase3-pgcompat-d-paradata-5.7.3-alpha"
```

Expected: `phase3-pgcompat-d-paradata-5.7.3-alpha` listed.

- [ ] **Step 3: Capture baselines (regression gates)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
```

Expected: `250 passed, 33 skipped`. AC-2 + SQLite round-trip + 3 critical SQLite gates + 8 PG-D L2 tests all PASS (PG-D L2 skip when PG offline — acceptable).

### Task 0.2: Create rollback safety tag

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-consolidation-5.7.4 -m "Rollback point before Consolidation 5.7.4 milestone

Predecessor: phase3-pgcompat-d-paradata-5.7.3-alpha (b8d73058)
Spec commit: fdb20de4

If Consolidation needs to be reverted, reset hard to this tag."
git push origin pre-consolidation-5.7.4
```

Expected: `* [new tag]         pre-consolidation-5.7.4 -> pre-consolidation-5.7.4`.

---

## Group A — `_workspace.py` helper + 4 L0 unit tests

The only production-code Group. ~120 LOC total. Adds `_resolve_workspace_root()` and updates `_resolve_workspace_dir()` PG branch to use it. SQLite branch UNCHANGED.

**CRITICAL RULES (surface in subagent prompt):**
- `_resolve_workspace_root()` body matches spec §5.1 EXACTLY
- SQLite branch of `_resolve_workspace_dir()` UNCHANGED
- QSettings import lazy with try/except ImportError
- `Path.home()` still called in default branch (PG-D's monkeypatch tests rely on this)
- 4 new L0 unit tests with `monkeypatch.setenv()` for env var cases
- **AC-2 + 3 critical SQLite regression gates + 8 PG-D L2 tests sanity ping IMMEDIATELY after the commit** — if any breaks, STOP

### Task A.1: Refactor + add 4 L0 tests

**Files:**
- Modify: `modules/s3dgraphy/sync/_workspace.py`
- Create: `tests/sync/test_workspace_root.py`

#### Step 1: Update `_workspace.py`

Use the Read tool to confirm the current state of `_workspace.py`. The current file (post-PG-D) has:
- Module docstring (lines 1-11)
- Imports: `from __future__ import annotations`, `import re`, `from pathlib import Path`, `from ._db_handle import DbHandle`
- `_conn_slug(handle)` function
- `_resolve_workspace_dir(handle, sito)` function with PG branch hardcoding `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"`

Use the Edit tool to replace the ENTIRE current content with:

```python
"""Workspace path resolution for ParadataStore + GroupStore.

For SQLite: workspace = parent dir of the .sqlite file (legacy behaviour).
For PostgreSQL: workspace = <root> / <conn_slug> / <sito>/
  where <root> is resolved via _resolve_workspace_root() (env var, QSettings,
  or default ~/pyarchinit/pyarchinit_DB_folder).

Created on-demand via mkdir(parents=True, exist_ok=True).

_conn_slug() is the single source of truth for the PG connection slug
used as a filesystem-safe directory name.

_resolve_workspace_root() (added in Consolidation 5.7.4-alpha) does
3-tier fallback:
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. QSettings 'pyarchinit/paradata_workspace' (UI override)
  3. Default: ~/pyarchinit/pyarchinit_DB_folder
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from ._db_handle import DbHandle


def _conn_slug(handle: DbHandle) -> str:
    """Produce a deterministic filesystem-safe slug from a PG handle's URL.

    Format: <host>_<port>_<dbname>, with non-[a-zA-Z0-9_-] chars replaced
    by underscores. Always returns a non-empty string.

    Raises ValueError for non-PG handles.
    """
    if not handle.is_postgres:
        raise ValueError("_conn_slug only applies to PostgreSQL handles")
    url = handle.engine.url
    host = url.host or "unknown_host"
    port = str(url.port or "5432")
    dbname = url.database or "unknown_db"
    raw = f"{host}_{port}_{dbname}"
    return re.sub(r"[^a-zA-Z0-9_-]", "_", raw)


def _resolve_workspace_root() -> Path:
    """Resolve the workspace root directory using 3-tier fallback.

    1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
    2. QSettings 'pyarchinit/paradata_workspace' (UI override)
    3. Default: ~/pyarchinit/pyarchinit_DB_folder

    Returns a Path (existence not guaranteed; caller must mkdir if needed).

    Added in Consolidation 5.7.4-alpha to support the
    `pyarchinitConfigDialog.py` UI override deferred from PG-D Q1=b.
    Empty values (env var or QSettings) are treated as unset and fall
    through to the next layer.
    """
    env_override = os.environ.get("PYARCHINIT_WORKSPACE_DIR")
    if env_override:
        return Path(env_override).expanduser()
    try:
        from qgis.PyQt.QtCore import QSettings
        qs_value = QSettings().value("pyarchinit/paradata_workspace", "")
        if qs_value:
            return Path(str(qs_value)).expanduser()
    except ImportError:
        # Not in QGIS env (e.g., pytest): skip QSettings layer transparently
        pass
    return Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def _resolve_workspace_dir(handle: DbHandle, sito: str) -> Path:
    """Resolve the per-site workspace directory for paradata/group files.

    SQLite: parent dir of the .sqlite file (legacy behaviour, byte-identical
    to the pre-PG-D `self._db_path.parent` access).

    PostgreSQL: `<root>/<conn_slug>/<sito>/`, created via
    `mkdir(parents=True, exist_ok=True)`. <root> is resolved via
    `_resolve_workspace_root()` which honours env var + QSettings overrides.

    Raises:
        ValueError: SQLite handle with no `sqlite_path` (e.g., `:memory:`).
    """
    if not handle.is_postgres:
        if handle.sqlite_path is None:
            raise ValueError(
                "In-memory SQLite has no parent dir for workspace; "
                "ParadataStore / GroupStore require a file-backed DB"
            )
        return handle.sqlite_path.parent

    slug = _conn_slug(handle)
    # Sanitize sito for directory use (same pattern as conn_slug)
    sito_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", sito)
    workspace = _resolve_workspace_root() / slug / sito_safe
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
```

Verify the file imports cleanly:

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync._workspace import (
    _conn_slug, _resolve_workspace_dir, _resolve_workspace_root,
)
print('imports OK')
print('_resolve_workspace_root:', _resolve_workspace_root)
print('default (no env var):', _resolve_workspace_root())
"
```

Expected output: `imports OK` + paths printed. The "default (no env var)" should be `<home>/pyarchinit/pyarchinit_DB_folder` for the current user.

#### Step 2: Create `tests/sync/test_workspace_root.py`

Use the Write tool to create with EXACTLY this content:

```python
# tests/sync/test_workspace_root.py
"""Consolidation 5.7.4-alpha: L0 unit tests for _resolve_workspace_root().

Verifies the 3-tier fallback chain:
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. QSettings 'pyarchinit/paradata_workspace' (UI override) — NOT
     unit-tested here (would require Qt); manual verification in QGIS.
  3. Default: ~/pyarchinit/pyarchinit_DB_folder

All tests use monkeypatch.delenv/setenv for the env var layer and
do not depend on PG or Qt.
"""
from __future__ import annotations

from pathlib import Path


def test_default_when_env_and_qsettings_unset(monkeypatch):
    """With env var unset + QSettings unavailable (non-Qt env),
    _resolve_workspace_root() returns ~/pyarchinit/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    # In a pytest env, qgis.PyQt is not importable → QSettings layer
    # skipped via try/except ImportError. The default branch fires.
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_override_takes_precedence(monkeypatch, tmp_path):
    """Setting PYARCHINIT_WORKSPACE_DIR routes the root to that path."""
    custom = tmp_path / "custom_workspace"
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(custom))
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == custom


def test_empty_env_var_falls_through_to_default(monkeypatch):
    """An empty env var is treated as unset and the function falls
    through to the QSettings/default layers."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    # Empty env var skipped → QSettings unavailable in pytest → default
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_with_tilde_expanded(monkeypatch):
    """Tilde-prefixed env var values are expanded via Path.expanduser()."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace_consol")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "test_workspace_consol"
    # Sanity: the tilde was actually expanded (not literal)
    assert "~" not in str(root)
```

#### Step 3: Run the 4 new L0 tests

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -m pytest tests/sync/test_workspace_root.py -v 2>&1 | tail -10
```

Expected: `4 passed`. All 4 tests pass on any env (no Qt, no PG required).

#### Step 4: Run the full sync+migrations suite

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `254 passed, 33 skipped` (250 + 4 new L0 passes).

#### Step 5: Run AC-2 + 3 critical SQLite regression gates

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
```

Expected: ALL PASS.

#### Step 6: Run 8 PG-D L2 tests (must skip cleanly when PG offline)

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
```

Expected (PG offline): `8 skipped`. If PG online: `8 passed`.

**If any of the regression gates (Step 5) fail → STOP. Do not commit. Report BLOCKED.**

Likely causes if a gate breaks:
- `_resolve_workspace_root()` default branch produces a different path than the old hardcoded `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"` (e.g., typo in the path components)
- PG branch of `_resolve_workspace_dir` no longer constructs `<root>/<slug>/<sito>` correctly
- Monkeypatch on `Path.home()` in PG-D tests doesn't reach the new helper

#### Step 7: Commit Group A

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/_workspace.py tests/sync/test_workspace_root.py
git commit -m "$(cat <<'EOF'
refactor(consol/A): _resolve_workspace_root + 4 L0 unit tests

Add _resolve_workspace_root() helper to modules/s3dgraphy/sync/_workspace.py
with 3-tier fallback:

1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
2. QSettings pyarchinit/paradata_workspace (UI override; lazy import
   with try/except ImportError so non-Qt environments fall through)
3. Default: ~/pyarchinit/pyarchinit_DB_folder

_resolve_workspace_dir() PG branch now delegates to
_resolve_workspace_root() instead of hardcoding the default path.
SQLite branch UNCHANGED (still returns handle.sqlite_path.parent).

The default branch still calls Path.home(), so PG-D L2 tests that
use monkeypatch.setattr(Path, "home", ...) continue to work.

4 new L0 unit tests in tests/sync/test_workspace_root.py:
- default_when_env_and_qsettings_unset
- env_var_override_takes_precedence
- empty_env_var_falls_through_to_default
- env_var_with_tilde_expanded

All 4 use monkeypatch.delenv/setenv. No Qt, no PG dependency.

QSettings layer manually verified in QGIS (Group B adds the UI).

250 -> 254 passed, 33 skipped (PG offline). AC-2 byte-identical
preserved. 3 SQLite regression gates green. 8 PG-D L2 tests
preserved (still skip cleanly or pass when PG online).
EOF
)"
git log -1 --format=%B HEAD | grep -cE "^Co-Authored-By:"
```

The strict regex check MUST return `0`.

## Self-review checklist before reporting back

- [ ] `_resolve_workspace_root()` added with code matching spec §5.1 EXACTLY
- [ ] `_resolve_workspace_dir()` PG branch delegates to `_resolve_workspace_root()`
- [ ] `_resolve_workspace_dir()` SQLite branch UNCHANGED (`handle.sqlite_path.parent`)
- [ ] QSettings import lazy via try/except ImportError
- [ ] Empty env var falls through to next layer
- [ ] `Path.expanduser()` applied to env var values
- [ ] Module docstring updated to reference 3-tier fallback
- [ ] 4 new L0 tests created with exact names matching spec §7.2
- [ ] `import os` added at module level (for `os.environ.get`)
- [ ] All 4 new tests pass
- [ ] Full suite: 254 passed, 33 skipped
- [ ] AC-2 PASS
- [ ] 3 critical SQLite regression gates PASS
- [ ] 8 PG-D L2 tests SKIP cleanly (or PASS if PG online)
- [ ] Strict trailer check (`grep -cE '^Co-Authored-By:'`) returns 0
- [ ] No leftover changes after commit

## Report back format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commit SHA
- Test count (full suite + AC-2 + 3 SQLite gates + 8 PG-D L2)
- Strict trailer check result (must be 0)
- Files changed (should be 2: _workspace.py + test_workspace_root.py)
- Any concerns

If a gate breaks → BLOCKED with full test output + diagnostic next step.

If you find yourself wanting to refactor anything beyond the plan (e.g., re-organize `_resolve_workspace_dir` body, add caching, modify SQLite branch), STOP and report DONE_WITH_CONCERNS describing what you wanted to do.

---

## Group B — `pyarchinitConfigDialog.py` "Paradata Workspace" section

Additive Qt UI code in a 10241-line dialog file. ~80 LOC. **NO automated tests** — manual verification in QGIS.

**CRITICAL RULES (surface in subagent prompt):**
- Find the right insertion point — DO NOT refactor unrelated code
- New QGroupBox styled consistently with existing groups (`font-weight: bold; border: 2px solid <color>; border-radius: 5px;`)
- Read/write QSettings key `pyarchinit/paradata_workspace`
- Browse button uses `QFileDialog.getExistingDirectory()`
- Reset button clears the QSettings value
- If scope creep tempts (e.g., refactoring nearby sections, adding unrelated features), flag as DONE_WITH_CONCERNS

### Task B.1: Add "Paradata Workspace" section

**File:** `gui/pyarchinitConfigDialog.py`

#### Step 1: Locate the insertion point

The dialog has multiple QGroupBox sections in the "DB Sync" tab (added around line 1223 via `self.tabWidget.addTab(scroll_area, self.tr("DB Sync"))`). The existing groups in that tab include:
- `profiles_group = QGroupBox(self.tr("Connection Profiles"))` (~line 951)
- `local_group = QGroupBox(self.tr("Local Database"))` (~line 991)
- `remote_group = QGroupBox(self.tr("Remote Database"))` (~line 1059)
- `buttons_group = QGroupBox(self.tr("Synchronization Operations"))` (~line 1149)

The right insertion point is **just before `buttons_group`** (so it sits between the Remote Database config and the Sync Operations buttons), or **at the end of the DB Sync tab content** (after `buttons_group`). Both are valid; pick the location that flows visually.

Confirm the existing pattern by reading lines ~951-1170 of the file:

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
sed -n '1059,1080p' gui/pyarchinitConfigDialog.py  # remote_group declaration
sed -n '1149,1170p' gui/pyarchinitConfigDialog.py  # buttons_group declaration
```

#### Step 2: Add the new QGroupBox + widgets

Use the Edit tool. Find the existing `buttons_group = QGroupBox(self.tr("Synchronization Operations"))` line (around line 1149) and INSERT the following BEFORE it (preserving indentation — the surrounding code is inside a method, probably indented 12 spaces):

```python
            # ----- Paradata Workspace section (Consolidation 5.7.4-alpha) -----
            # Lets the user override the workspace directory where PG
            # paradata + groups .graphml files are stored. The override
            # is written to QSettings 'pyarchinit/paradata_workspace'
            # and picked up by modules.s3dgraphy.sync._workspace
            # ._resolve_workspace_root() on each ParadataStore /
            # GroupStore .file_path access. Empty = use default
            # (~/pyarchinit/pyarchinit_DB_folder).
            from qgis.PyQt.QtCore import QSettings as _QSettings
            workspace_group = QGroupBox(self.tr("Paradata Workspace"))
            workspace_group.setStyleSheet("""
                QGroupBox { font-weight: bold; border: 2px solid #607D8B; border-radius: 5px; margin-top: 8px; padding-top: 8px; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            """)
            workspace_layout = QVBoxLayout(workspace_group)

            workspace_info_label = QLabel(self.tr(
                "Override the workspace directory where PostgreSQL paradata "
                "and group files are stored. SQLite continues to store these "
                "files next to the .sqlite database (this setting does not "
                "affect SQLite). Leave blank to use the default "
                "(~/pyarchinit/pyarchinit_DB_folder)."
            ))
            workspace_info_label.setWordWrap(True)
            workspace_layout.addWidget(workspace_info_label)

            workspace_path_row = QHBoxLayout()
            workspace_path_label = QLabel(self.tr("Workspace dir:"))
            workspace_path_row.addWidget(workspace_path_label)

            self._workspace_lineedit = QLineEdit()
            _current_ws = _QSettings().value(
                "pyarchinit/paradata_workspace", "") or ""
            self._workspace_lineedit.setText(str(_current_ws))
            self._workspace_lineedit.setPlaceholderText(self.tr(
                "(default: ~/pyarchinit/pyarchinit_DB_folder)"
            ))
            workspace_path_row.addWidget(self._workspace_lineedit, stretch=1)

            workspace_browse_btn = QPushButton(self.tr("Browse..."))

            def _on_workspace_browse():
                _dir = QFileDialog.getExistingDirectory(
                    self, self.tr("Select Paradata Workspace Directory"),
                    self._workspace_lineedit.text() or str(Path.home()),
                )
                if _dir:
                    self._workspace_lineedit.setText(_dir)
                    # Persist immediately so Save isn't required
                    _QSettings().setValue(
                        "pyarchinit/paradata_workspace", _dir)

            workspace_browse_btn.clicked.connect(_on_workspace_browse)
            workspace_path_row.addWidget(workspace_browse_btn)

            workspace_reset_btn = QPushButton(self.tr("Reset"))

            def _on_workspace_reset():
                self._workspace_lineedit.clear()
                _QSettings().remove("pyarchinit/paradata_workspace")

            workspace_reset_btn.clicked.connect(_on_workspace_reset)
            workspace_path_row.addWidget(workspace_reset_btn)

            workspace_layout.addLayout(workspace_path_row)
            scroll_layout.addWidget(workspace_group)
            # ----- end Paradata Workspace section -----

```

NOTE on imports: `QGroupBox`, `QVBoxLayout`, `QHBoxLayout`, `QPushButton`, `QFormLayout` are already imported in the surrounding section (line ~911). `QLabel`, `QFileDialog`, `QLineEdit` are also imported (`QFileDialog,QLineEdit` at line 44). `Path` is imported from `pathlib` elsewhere — if not in scope at the insertion point, add a local `from pathlib import Path` inside the section block.

Verify imports actually in scope at the insertion location:

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
sed -n '910,915p' gui/pyarchinitConfigDialog.py
```

If `Path` is not imported in the surrounding scope, add `from pathlib import Path` as the first line inside the new section, just below the existing `from qgis.PyQt.QtCore import QSettings as _QSettings` line.

#### Step 3: Syntax check the modified file

```bash
PYTHONPATH="$PWD" python -c "
import ast
with open('gui/pyarchinitConfigDialog.py') as f:
    ast.parse(f.read())
print('pyarchinitConfigDialog.py syntax OK')
"
```

Expected: `pyarchinitConfigDialog.py syntax OK`.

#### Step 4: Run full suite + AC-2 + gates (sanity)

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: `254 passed, 33 skipped`. AC-2 PASS.

These run pytest in a non-Qt context, so the new dialog code is not loaded — the test suite is unaffected. The UI section only activates when QGIS opens the config dialog.

#### Step 5: Commit Group B

```bash
git add gui/pyarchinitConfigDialog.py
git commit -m "$(cat <<'EOF'
feat(consol/B): paradata workspace UI section in config dialog

Add "Paradata Workspace" QGroupBox to the DB Sync tab of
pyarchinitConfigDialog.py. Inserted before the existing
"Synchronization Operations" buttons group, around line 1149.

Contents:
- QLabel info text explaining the PG-only nature of the setting
- QLineEdit pre-populated from QSettings pyarchinit/paradata_workspace
  with placeholder text showing the default fallback
- Browse button (QFileDialog.getExistingDirectory) writes the chosen
  path into QSettings immediately (no separate Save click required)
- Reset button clears the QLineEdit and removes the QSettings key

The UI delegates to the pre-existing 3-tier fallback chain in
_workspace.py (added in Group A). Whenever ParadataStore or
GroupStore on a PG handle accesses .file_path, _resolve_workspace_root
re-reads the QSettings value, so changes take effect immediately
without restart.

No automated tests for this section (Qt UI). Manual verification:
open QGIS plugin config dialog -> DB Sync tab -> Paradata Workspace
group -> set/Browse/Reset and confirm a PG-handle ParadataStore picks
up the new path.

QGroupBox styled consistently with existing dialog groups
(border #607D8B, slate-blue, distinct from the surrounding green /
cyan / orange groups).

254 passed, 33 skipped (unchanged - UI is additive, no test impact).
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -cE "^Co-Authored-By:"
```

The strict regex check MUST return `0`.

## Self-review checklist

- [ ] New QGroupBox inserted in the DB Sync tab, BEFORE the existing `buttons_group`
- [ ] QGroupBox styled consistently with the dialog's existing groups (`font-weight: bold; border: 2px solid <color>; border-radius: 5px; ...`)
- [ ] QLineEdit pre-populated from QSettings + placeholder shows default
- [ ] Browse button uses `QFileDialog.getExistingDirectory()` + persists to QSettings on selection
- [ ] Reset button clears QLineEdit + removes the QSettings key
- [ ] `QSettings` imported locally inside the new section (lazy)
- [ ] `Path` accessible (already imported in scope or added as local import)
- [ ] No refactoring of unrelated code (other groups in DB Sync tab unchanged)
- [ ] Syntax check passes (ast.parse OK)
- [ ] Full suite: 254 passed, 33 skipped (unchanged from Group A)
- [ ] AC-2 PASS
- [ ] Strict trailer check returns 0

## Report back format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commit SHA
- Files changed (should be 1: pyarchinitConfigDialog.py)
- Strict trailer check result
- Any concerns about the insertion point (e.g., if the surrounding scope made the planned location awkward and the implementer chose differently)

If you find an existing section that already does similar workspace config, STOP and report DONE_WITH_CONCERNS describing what you found (would change the design).

---

## Group C — Docs + version 5.7.4-alpha + Phase 3 closure

### Task C.1: Bump `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.7.3-alpha` → `version=5.7.4-alpha`.

Verify:
```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep "^version=" metadata.txt
```
Expected: `version=5.7.4-alpha`.

### Task C.2: Insert Phase 3 Consolidation section to dev-log

**File:** `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Use the Edit tool to find this exact text:

```
---

## Phase 3 — PG-D paradata workspace (5.7.3-alpha)
```

Replace with:

```
---

## Phase 3 — Consolidation (5.7.4-alpha) — Phase 3 CLOSURE

**Tag:** `phase3-pgcompat-consolidation-5.7.4-alpha`
**Date:** 2026-05-11
**Spec:** `docs/superpowers/specs/2026-05-11-consolidation-design.md`
**Plan:** `docs/superpowers/plans/2026-05-11-consolidation.md`

### What shipped

- `_resolve_workspace_root()` helper in `modules/s3dgraphy/sync/_workspace.py`
  with 3-tier fallback: env var `PYARCHINIT_WORKSPACE_DIR` > QSettings
  `pyarchinit/paradata_workspace` > default `~/pyarchinit/pyarchinit_DB_folder`
- `_resolve_workspace_dir()` PG branch delegates to the new helper;
  SQLite branch UNCHANGED
- New "Paradata Workspace" section in `gui/pyarchinitConfigDialog.py`
  (DB Sync tab): QLineEdit + Browse + Reset, persists to QSettings
- 4 new L0 unit tests in `tests/sync/test_workspace_root.py`
  covering env var precedence + default fallback + tilde expansion
- Bilingual CHANGELOG entry + this dev-log section + Phase 3 closure
  summary

### Tests

- 4 new L0 tests (always run, no Qt, no PG dependency)
- All 250 SQLite tests + AC-2 + 3 critical SQLite regression gates
  preserved
- All 8 PG-D L2 tests preserved (monkeypatch on Path.home() reaches
  the helper's default branch)
- Total: 254 passed, 33 skipped (PG offline) or 262 passed,
  12 skipped (PG online + psycopg2)

### Deferred items (will ride along Phase 4 / 5.8.x)

- Rename `db_path` to `db_input` on 5 public APIs with a
  DeprecationWarning cycle
- Parametrized SQLite + PG tests (low ROI — PG-offline envs already
  skip cleanly)
- Optional `_common.py` adopt `_conn_slug` (small DRY improvement)

---

## Phase 3 closure

Phase 3 (PostgreSQL compatibility for the s3dgraphy bridge) is
officially complete with the Consolidation 5.7.4-alpha tag.

**6 tags shipped over 2 days (2026-05-10 to 2026-05-11):**

| Milestone | Tag | Commit |
|---|---|---|
| Foundation | `phase3-pgcompat-shim-5.6.2-alpha` | `7420a6cc` |
| PG-A | `phase3-pgcompat-a-migration-5.7.0-alpha` | `45803d83` |
| PG-B | `phase3-pgcompat-b-export-5.7.1-alpha` | `2121369e` |
| PG-C | `phase3-pgcompat-c-import-5.7.2-alpha` | `cf6ed26e` |
| PG-D | `phase3-pgcompat-d-paradata-5.7.3-alpha` | `b8d73058` |
| Consolidation | `phase3-pgcompat-consolidation-5.7.4-alpha` | (this tag) |

**Cumulative stats:**
- ~2500 LOC across the entire phase
- ~36+ commits (spec + plan + Group A-N per milestone + tags)
- 254 passed / 33 skipped (PG offline) / 262 passed / 12 skipped (PG online)
- AC-2 byte-identical guard preserved across every milestone
- Zero commits with Claude as co-author trailer (per project rule)
- All production `sqlite3.connect()` flipped to SQLAlchemy + `DbHandle`
  shim. Zero residual in `modules/s3dgraphy/sync/`.

**Phase 4** (SyncEngine + REST API for multi-user concurrency) is
ready to brainstorm when desired. The deferred polish items from
Phase 3 will ride along Phase 4's API churn.

---

## Phase 3 — PG-D paradata workspace (5.7.3-alpha)
```

### Task C.3: Prepend bilingual CHANGELOG entry

**File:** `dev_logs/CHANGELOG.md`

Use the Edit tool to find this exact text:

```
## [5.7.3-alpha] - 2026-05-11
```

Replace with:

```
## [5.7.4-alpha] - 2026-05-11

### Italiano

**Consolidation — chiusura ufficiale di Phase 3.**

Sesto e ultimo milestone di Phase 3. Aggiunge l'override UI del workspace dir (deferito da PG-D Q1=b) e il docs pass di chiusura. Scope minimale (~310 LOC) per chiudere la fase senza churn API.

- **`_resolve_workspace_root()` helper** in `modules/s3dgraphy/sync/_workspace.py`: 3-tier fallback chain.
  1. `PYARCHINIT_WORKSPACE_DIR` env var (priorità massima — utile per CI/test)
  2. QSettings `pyarchinit/paradata_workspace` (UI override persistente)
  3. Default `~/pyarchinit/pyarchinit_DB_folder/`
  Import QSettings lazy con try/except ImportError, quindi i non-Qt env (es. pytest) saltano trasparentemente il layer QSettings.
- **`_resolve_workspace_dir()` PG branch** ora chiama il nuovo helper invece di hardcodare il default. SQLite branch INVARIATO (`handle.sqlite_path.parent`).
- **Sezione UI "Paradata Workspace"** in `gui/pyarchinitConfigDialog.py` (tab DB Sync). QLineEdit + Browse + Reset. Read/write QSettings. Persistente tra sessioni QGIS. NON influenza SQLite users (il loro path resta accanto al `.sqlite`).
- **4 nuovi test L0** in `tests/sync/test_workspace_root.py`: env var precedence, default fallback, empty env var skip-through, tilde expansion. Pure pytest, no Qt, no PG dependency.
- **Phase 3 closure summary** nel dev-log: tutti i 6 tag + statistiche cumulative + items deferred.

**Items deferred** (saranno gestiti in Phase 4 / 5.8.x):
- Rename `db_path → db_input` su 5 API pubbliche con DeprecationWarning cycle
- Test parametrizzati SQLite + PG (low ROI — gli env PG-offline già skippano puliti)
- Adozione opzionale di `_conn_slug` in `_common.py:auto_backup_postgres`

**Phase 3 chiusura ufficiale**: 6 tag (Foundation + PG-A + PG-B + PG-C + PG-D + Consolidation), ~2500 LOC totali, ~36+ commit, AC-2 byte-identical preservato dall'inizio alla fine, zero residui `sqlite3.connect()` in `modules/s3dgraphy/sync/`. Phase 4 (SyncEngine + REST API) può essere brainstormata quando l'utente è pronto.

Test count: 250 → 254 passed, 33 skipped (PG offline) o 262 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato.

### English

**Consolidation — official Phase 3 closure.**

Sixth and final Phase 3 milestone. Adds the deferred UI override for the workspace dir (from PG-D Q1=b) and the closure docs pass. Minimal scope (~310 LOC) to close the phase without API churn.

- **`_resolve_workspace_root()` helper** in `modules/s3dgraphy/sync/_workspace.py`: 3-tier fallback chain.
  1. `PYARCHINIT_WORKSPACE_DIR` env var (highest priority — useful for CI/tests)
  2. QSettings `pyarchinit/paradata_workspace` (persistent UI override)
  3. Default `~/pyarchinit/pyarchinit_DB_folder/`
  QSettings import is lazy with try/except ImportError, so non-Qt environments (e.g., pytest) skip the QSettings layer transparently.
- **`_resolve_workspace_dir()` PG branch** now calls the new helper instead of hardcoding the default. SQLite branch UNCHANGED (`handle.sqlite_path.parent`).
- **UI "Paradata Workspace" section** in `gui/pyarchinitConfigDialog.py` (DB Sync tab). QLineEdit + Browse + Reset. Read/write QSettings. Persists across QGIS sessions. Does NOT affect SQLite users (their path stays next to the `.sqlite`).
- **4 new L0 tests** in `tests/sync/test_workspace_root.py`: env var precedence, default fallback, empty env var skip-through, tilde expansion. Pure pytest, no Qt, no PG dependency.
- **Phase 3 closure summary** in the dev-log: all 6 tags + cumulative stats + deferred items.

**Deferred items** (will be handled in Phase 4 / 5.8.x):
- Rename `db_path → db_input` on 5 public APIs with DeprecationWarning cycle
- Parametrized SQLite + PG tests (low ROI — PG-offline environments already skip cleanly)
- Optional adoption of `_conn_slug` in `_common.py:auto_backup_postgres`

**Phase 3 official closure**: 6 tags (Foundation + PG-A + PG-B + PG-C + PG-D + Consolidation), ~2500 LOC total, ~36+ commits, AC-2 byte-identical preserved from start to finish, zero residual `sqlite3.connect()` in `modules/s3dgraphy/sync/`. Phase 4 (SyncEngine + REST API) can be brainstormed when the user is ready.

Test count: 250 → 254 passed, 33 skipped (PG offline) or 262 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved.

---

## [5.7.3-alpha] - 2026-05-11
```

### Task C.4: Commit + final verification

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git log --oneline fdb20de4..HEAD
git log fdb20de4..HEAD --format=%B | grep -cE "^Co-Authored-By:"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 2 commits since `fdb20de4`: A, B
- Strict trailer count: `0`
- Test suite: `254 passed, 33 skipped` (PG offline)
- AC-2 PASS
- Version: `5.7.4-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(consol/C): docs + version 5.7.4-alpha + Phase 3 closure

Consolidation milestone documentation: bilingual CHANGELOG entry,
dev-log Consolidation section, version bump 5.7.3-alpha -> 5.7.4-alpha,
and a Phase 3 closure summary listing all 6 tags + cumulative stats.

Cumulative deliverables (Groups A-C):
- _resolve_workspace_root() helper with 3-tier fallback (env var,
  QSettings, default)
- _resolve_workspace_dir() PG branch delegates to helper; SQLite
  branch unchanged
- "Paradata Workspace" UI section in pyarchinitConfigDialog.py
  (DB Sync tab) with QLineEdit + Browse + Reset
- 4 new L0 unit tests for the helper

After this commit, Phase 3 is OFFICIALLY COMPLETE: 6 tags, ~2500 LOC,
zero residual sqlite3.connect() in sync/. Phase 4 (SyncEngine +
REST API) can be brainstormed when ready.

Test count: 250 -> 254 passed, 33 skipped (PG offline) or
250 -> 262 passed, 12 skipped (PG online with psycopg2).
AC-2 byte-identical baseline preserved.

Spec: docs/superpowers/specs/2026-05-11-consolidation-design.md
Plan: docs/superpowers/plans/2026-05-11-consolidation.md
Predecessor: phase3-pgcompat-d-paradata-5.7.3-alpha (b8d73058)
EOF
)"
git log -1 --format=%B HEAD | grep -cE "^Co-Authored-By:"
```

The strict regex check MUST return `0`.

- [ ] **Step 3: Post-commit verification**

```bash
git log --oneline fdb20de4..HEAD
git log fdb20de4..HEAD --format=%B | grep -cE "^Co-Authored-By:"
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 3 commits since `fdb20de4`: A, B, C
- Strict trailer count: `0`
- `254 passed, 33 skipped`
- Version: `5.7.4-alpha`

---

## Group D — Tag + push

### Task D.1: Pre-flight branch check

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
```

Expected: `Stratigraph_00001`. **STOP and BLOCK** if anything else.

### Task D.2: Create annotated tag

```bash
git tag -a phase3-pgcompat-consolidation-5.7.4-alpha -m "$(cat <<'EOF'
Consolidation - Phase 3 closure on PostgreSQL compat refactor

Sixth and final Phase 3 milestone. Adds the QSettings UI workspace
override (deferred from PG-D Q1=b) and the closure docs pass.

Cumulative deliverables (Groups A-C, 3 commits):

- _resolve_workspace_root() helper in
  modules/s3dgraphy/sync/_workspace.py with 3-tier fallback:
    1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
    2. QSettings pyarchinit/paradata_workspace (UI override)
    3. Default: ~/pyarchinit/pyarchinit_DB_folder
- _resolve_workspace_dir() PG branch delegates to the helper;
  SQLite branch UNCHANGED (byte-identical to pre-Consolidation).
- New "Paradata Workspace" QGroupBox section in
  gui/pyarchinitConfigDialog.py (DB Sync tab) with QLineEdit +
  Browse + Reset. Read/write QSettings, persists across sessions.
- 4 new L0 unit tests in tests/sync/test_workspace_root.py
  covering env var precedence + default fallback + tilde expansion.
- Bilingual CHANGELOG entry + dev-log Consolidation section + a
  Phase 3 closure summary section listing all 6 tags.

Test counts: 250 -> 254 passed, 33 skipped (PG offline) or
250 -> 262 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical preserved.
All 3 critical SQLite regression gates preserved.
All 8 PG-D L2 tests preserved.

Phase 3 status after Consolidation: OFFICIALLY COMPLETE.

6 tags shipped 2026-05-10 to 2026-05-11:
- Foundation 5.6.2-alpha
- PG-A migration 5.7.0-alpha
- PG-B export 5.7.1-alpha
- PG-C import 5.7.2-alpha
- PG-D paradata 5.7.3-alpha
- Consolidation 5.7.4-alpha

~2500 LOC across the entire phase. Zero residual sqlite3.connect()
in modules/s3dgraphy/sync/.

Items deferred to Phase 4 / 5.8.x:
- Rename db_path -> db_input on 5 public APIs
- Parametrized SQLite + PG tests
- Optional adoption of _conn_slug in _common.py

Spec: docs/superpowers/specs/2026-05-11-consolidation-design.md
Plan: docs/superpowers/plans/2026-05-11-consolidation.md
Predecessor: phase3-pgcompat-d-paradata-5.7.3-alpha (b8d73058)
EOF
)"
```

### Task D.3: Verify the tag

```bash
echo "=== Tag created locally ==="
git tag -n5 phase3-pgcompat-consolidation-5.7.4-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse phase3-pgcompat-consolidation-5.7.4-alpha^{commit}
git rev-parse HEAD
echo "=== Tag is annotated ==="
git cat-file -t phase3-pgcompat-consolidation-5.7.4-alpha
echo "=== Strict trailer check on tag message ==="
git tag -l --format='%(contents)' phase3-pgcompat-consolidation-5.7.4-alpha | grep -cE "^Co-Authored-By:"
```

The final grep MUST return `0`.

### Task D.4: Push tag + branch

```bash
git push origin phase3-pgcompat-consolidation-5.7.4-alpha 2>&1 | tail -3
git push origin Stratigraph_00001 2>&1 | tail -3
```

### Task D.5: Verify on origin

```bash
git ls-remote --tags origin | grep "phase3-pgcompat-consolidation-5.7.4-alpha"
git ls-remote --heads origin Stratigraph_00001
echo "=== All 6 Phase 3 tags ==="
git ls-remote --tags origin | grep -E "phase3-pgcompat-" | sort
```

Expected: tag listed (with `^{}` dereferenced commit line), branch tip equals local HEAD, all 6 Phase 3 tags visible.

### Task D.6: Memory snapshot (controller, no subagent)

After Group D ships, the controller updates `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move Consolidation from PENDING to SHIPPED with all SHAs
- **Add "🎉 PHASE 3 OFFICIALLY COMPLETE" closure section** with cumulative stats
- Document deferred items (rename + parametrized tests) for Phase 4 brainstorming
- Update `MEMORY.md` index line for new "Phase 3 COMPLETE" CURRENT STATE
- Optionally add a Phase 4 placeholder line

---

## Self-Review

This plan covers every Consolidation spec requirement:

| Spec section | Plan task |
|---|---|
| §3.1 Q1=(2) minimal scope (no rename, no parametrized) | Plan: no rename tasks; no parametrize tasks. Documented in "Explicitly NOT touched" |
| §3.2 Q2=(b) 3-tier fallback | Group A Step 1 |
| §3.3 Approach 1 (helper + UI section) | Group A + Group B |
| §3.4 Phase 3 closure | Group C Phase 3 closure section in dev-log + CHANGELOG |
| §4.1 Modified files | Groups A-C |
| §4.2 New files | Group A Step 2 |
| §4.3 NOT touched | Documented in Plan "Explicitly NOT touched" |
| §5 `_workspace.py` extension | Group A Step 1 exact code |
| §6 UI specification | Group B Step 2 |
| §7 Test strategy | Group A Step 2 (4 L0 cases) |
| §8 Acceptance criteria | Pinned by Group A's 4 L0 tests + existing gates |
| §9 Release plan | Groups C + D |

**Type consistency check:** `_resolve_workspace_root`, `_resolve_workspace_dir`, `_conn_slug`, `DbHandle`, `Path.home`, `os.environ.get`, `QSettings`, `QGroupBox`, `QLineEdit`, `QFileDialog`, `QPushButton`, `QHBoxLayout`, `QVBoxLayout`, `QLabel` — all used consistently across Groups.

**No placeholders:** every step has runnable code, exact commands, or specific file edits.

**Scope check:** Plan focused on Consolidation only. No rename of public APIs, no parametrized test promotion.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-consolidation.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review, fast iteration

**2. Inline Execution** — execute tasks in this session via `executing-plans`, batch with checkpoints

If **Subagent-Driven**, recommended batching:
- Group 0 (2 tasks) → no subagent — pure git
- Group A → 1 subagent (helper refactor + 4 L0 tests; ~120 LOC; sonnet OK)
- Group B → 1 subagent (Qt UI in 10K-line dialog; ~80 LOC; explicit "find insertion point, don't refactor" instruction)
- Group C → 1 subagent (docs + version + Phase 3 closure prose)
- Group D → 1 subagent (tag + push, gate for user approval)
- Memory snapshot → no subagent (controller writes Phase 3 closure)

If **Inline Execution**, batch by Group with checkpoint after each.
