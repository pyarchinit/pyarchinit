# PG-D — ParadataStore + GroupStore workspace on PostgreSQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ParadataStore` and `GroupStore` cross-backend for filesystem path resolution. The single path-resolution site in each file (`self._db_path.parent / f"<prefix>_<slug>.graphml"`) becomes a dispatch via NEW `modules/s3dgraphy/sync/_workspace.py` helper. SQLite preserves "alongside .sqlite" (byte-identical). PG uses `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/`. Public constructors keep `db_path` keyword via shim (PG-A/B/C pattern). Release `5.7.3-alpha`.

**Architecture:** Single-file refactor (Group A) adds new `_workspace.py` + minimal edits to 2 store files (~30 LOC delta each). Both stores call `_resolve_workspace_dir(handle, sito)` from the new helper. Then 2 new PG L2 test files (Groups B+C), docs (D), tag (E). Lowest-risk PG-X milestone: no SQL refactor, no transactions, no `_DryRunRollback` complexity.

**Tech Stack:** Python 3.9+, SQLAlchemy 2.0+ (for URL parsing in `_conn_slug`), psycopg2-binary>=2.9, Foundation + PG-A/B/C helpers reused.

**Spec source of truth:** `docs/superpowers/specs/2026-05-11-pg-d-paradata-design.md` (commit `88e5892f`)

**Predecessor releases:**
- PG-C: tag `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`)
- PG-B: tag `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
- PG-A: tag `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- Foundation: tag `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)

**Memory notes:**
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` — Phase 3 state
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Verify after each commit: `git log -1 --format=%B HEAD | grep -c Co-Authored-By` → `0`.

**Spec correction:** Spec §3.4 claimed `_conn_slug` would DRY-up an inline slugify in `auto_backup_postgres`. Verified during plan: `_common.py:auto_backup_postgres` has NO inline slugify — it uses `dbname` directly. There is **no existing duplication to DRY up**. `_conn_slug` is purely new code in `_workspace.py`. The `_common.py` is **NOT modified** in this plan. Any future adoption of `_conn_slug` by `auto_backup_postgres` is deferred (Consolidation 5.7.4 or later).

**Local PG setup:** `postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg` (USER pre-created during Foundation). In dev env psycopg2 NOT installed → PG L2 tests in Groups B/C skip cleanly.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/_workspace.py` | `_resolve_workspace_dir(handle, sito) -> Path` + `_conn_slug(handle) -> str`. SQLite branch: returns `handle.sqlite_path.parent`. PG branch: `Path.home() / "pyarchinit" / "pyarchinit_DB_folder" / _conn_slug(handle) / sito_safe` with `mkdir(parents=True, exist_ok=True)`. ~80 LOC. |
| `tests/sync/test_paradata_store_pg.py` | 4 PG L2 cases: workspace_dir resolution, write+read round-trip, conn_slug determinism, multi-site isolation. Skip cleanly when PG offline. ~80 LOC. |
| `tests/sync/test_group_store_pg.py` | 4 PG L2 cases: workspace_dir, round-trip, conn_slug determinism, shares workspace with paradata. Skip cleanly when PG offline. ~80 LOC. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/paradata_store.py` | `__init__(db_path, sito)` keeps keyword name, accepts `Path \| DbHandle \| str` via shim. Stores `self._handle = _resolve_db_handle(db_path)`. Preserves `self._db_path = Path(db_path)` for legacy attribute readers (Path callers only — graceful fallback). Property `file_path` (line 96): uses `_resolve_workspace_dir(self._handle, self._sito) / f"paradata_{self._slug}.graphml"`. | ~25 LOC delta |
| `modules/s3dgraphy/sync/group_store.py` | Same pattern. Property `file_path` (line 84): uses `_resolve_workspace_dir(self._handle, self._sito) / f"groups_{self._slug}.graphml"`. | ~25 LOC delta |
| `metadata.txt` | Bump `5.7.2-alpha` → `5.7.3-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.3-alpha]` section. | ~40 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 PG-D section. | ~30 |

### Explicitly NOT touched

- `scripts/migrations/_common.py` (spec §3.4 DRY-up dropped — see spec correction above)
- `gui/pyarchinitConfigDialog.py` (QSettings UI deferred to Consolidation 5.7.4)
- `modules/s3dgraphy/sync/_db_handle.py` (Foundation)
- `modules/s3dgraphy/sync/conflict_resolver.py`, `graph_projector.py`, `group_projector.py`, `graphml_writer.py`, `graph_ingestor.py` (all PG-A/B/C scope)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2)
- `tests/sync/test_round_trip.py`, `test_round_trip_with_paradata.py`, `test_round_trip_with_groups.py`, `test_graph_projector_paradata.py` (critical SQLite regression gates — must stay green untouched)
- The 15 callers of ParadataStore / GroupStore (1 bridge + 2 graph_projector + 11 scripts + tests) — unchanged via shim

### Total LOC

- Production: ~130 (80 new + 50 modified)
- Test: ~160 (2 new files)
- Docs: ~70
- **Grand total: ~360 LOC** (smallest PG-X milestone)

---

## Test strategy

- **L0 unit (none new):** Foundation + PG-A/B/C cover shim. PG-D inherits.
- **L1 SQLite (existing 250):** All stay green via shim. Especially `test_round_trip_with_paradata.py`, `test_round_trip_with_groups.py`, `test_graph_projector_paradata.py` — the critical gates.
- **L2 PG (NEW):** 4 paradata + 4 group_store cases. Skip cleanly when PG offline.
- **L3 regression guards (existing, MUST stay green):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

After Group A, all of these must PASS. If any breaks, the SQLite branch of `_resolve_workspace_dir` is producing a different path than `_db_path.parent` was. Investigate before proceeding.

Test count progression:
- Pre PG-D (post PG-C): `250 passed, 25 skipped` (PG offline)
- Post Group A (refactor only): unchanged
- Post Group B (test_paradata_store_pg.py 4 cases, PG offline all skip): `250 passed, 29 skipped`
- Post Group C (test_group_store_pg.py 4 cases, PG offline all skip): `250 passed, 33 skipped`
- Post Group D (docs only): unchanged

Final:
- PG offline: **250 passed, 33 skipped**
- PG online + psycopg2: **258 passed, 12 skipped**

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

Expected: tracked changes empty, last commit `88e5892f spec(pg-d-paradata): ...`, `0\t0` ahead-behind.

- [ ] **Step 2: Verify predecessor tag**

```bash
git tag --list | grep -E "phase3-pgcompat-c-import-5.7.2-alpha"
```

Expected: `phase3-pgcompat-c-import-5.7.2-alpha` listed.

- [ ] **Step 3: Capture baselines (5 regression gates)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v 2>&1 | tail -5
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v 2>&1 | tail -5
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
```

Expected: `250 passed, 25 skipped`. AC-2 PASS. All 4 gate tests PASS.

### Task 0.2: Create rollback safety tag

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-pg-d-paradata -m "Rollback point before PG-D paradata milestone

Predecessor: phase3-pgcompat-c-import-5.7.2-alpha (cf6ed26e)
Spec commit: 88e5892f

If PG-D needs to be reverted, reset hard to this tag."
git push origin pre-pg-d-paradata
```

Expected: `* [new tag]         pre-pg-d-paradata -> pre-pg-d-paradata`.

---

## Group A — `_workspace.py` + paradata_store.py + group_store.py refactor

The only production-code Group. NEW `_workspace.py` + minimal edits to 2 store files. ~130 LOC total.

**CRITICAL RULES (surface in subagent prompt):**
- NEW `_workspace.py` with code matching spec §5 exactly
- paradata_store.py + group_store.py: keep `db_path` keyword on constructor, shim via `_resolve_db_handle`
- SQLite path MUST stay byte-identical (`handle.sqlite_path.parent` == old `_db_path.parent`)
- Update only the `file_path` property — DO NOT modify any other store method/attribute
- **AC-2 + 4 round-trip/paradata gate tests sanity ping IMMEDIATELY after the commit** — if any breaks, STOP and report BLOCKED

### Task A.1: Refactor

**Files:**
- Create: `modules/s3dgraphy/sync/_workspace.py`
- Modify: `modules/s3dgraphy/sync/paradata_store.py`
- Modify: `modules/s3dgraphy/sync/group_store.py`

#### Step 1: Create `_workspace.py`

Create `modules/s3dgraphy/sync/_workspace.py` with EXACTLY this content:

```python
"""PG-D Workspace path resolution for ParadataStore + GroupStore.

For SQLite: workspace = parent dir of the .sqlite file (legacy behaviour).
For PostgreSQL: workspace = ~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/

Created on-demand via mkdir(parents=True, exist_ok=True).

_conn_slug() is the single source of truth for the PG connection slug
used as a filesystem-safe directory name. Future code (e.g.,
Consolidation 5.7.4) may adopt this helper for other paths.
"""
from __future__ import annotations

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


def _resolve_workspace_dir(handle: DbHandle, sito: str) -> Path:
    """Resolve the per-site workspace directory for paradata/group files.

    SQLite: parent dir of the .sqlite file (legacy behaviour, byte-identical
    to the pre-PG-D `self._db_path.parent` access).

    PostgreSQL: `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/`,
    created via `mkdir(parents=True, exist_ok=True)`.

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
    workspace = (
        Path.home()
        / "pyarchinit"
        / "pyarchinit_DB_folder"
        / slug
        / sito_safe
    )
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
```

Verify the file imports cleanly:

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
from modules.s3dgraphy.sync._workspace import _conn_slug, _resolve_workspace_dir
print('imports OK')
print('_conn_slug:', _conn_slug)
print('_resolve_workspace_dir:', _resolve_workspace_dir)
"
```

Expected: `imports OK` + the function references printed.

#### Step 2: Refactor `paradata_store.py`

Find the imports block at top:

```python
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .graph_ingestor import GraphSyncError
```

Use the Edit tool to add the new shim + workspace imports. Replace with:

```python
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ._db_handle import _resolve_db_handle
from ._workspace import _resolve_workspace_dir
from .graph_ingestor import GraphSyncError
```

Find the `__init__` method (around line 85-91):

```python
    def __init__(self, db_path: Path, sito: str) -> None:
        if not sito:
            raise ParadataValidationError(
                "sito is required for ParadataStore")
        self._db_path = Path(db_path)
        self._sito = sito
        self._slug = _sito_slug(sito)
```

Replace with:

```python
    def __init__(self, db_path, sito: str) -> None:
        """Construct a site-scoped paradata store.

        PG-D (5.7.3-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        """
        if not sito:
            raise ParadataValidationError(
                "sito is required for ParadataStore")
        self._handle = _resolve_db_handle(db_path)
        # Preserve self._db_path for any defensive code that reads it
        # directly (currently only used here for repr/debug, but keep
        # the attribute to avoid breaking subclasses).
        self._db_path = (
            self._handle.sqlite_path
            if self._handle.sqlite_path is not None
            else Path(self._handle.conn_str)
        )
        self._sito = sito
        self._slug = _sito_slug(sito)
```

Find the `file_path` property (around line 93-96):

```python
    @property
    def file_path(self) -> Path:
        """Resolved paradata file path for this (db, sito) pair."""
        return self._db_path.parent / f"paradata_{self._slug}.graphml"
```

Replace with:

```python
    @property
    def file_path(self) -> Path:
        """Resolved paradata file path for this (db, sito) pair.

        PG-D (5.7.3-alpha): SQLite returns `<sqlite_parent>/paradata_<sito>.graphml`
        (byte-identical to pre-PG-D). PG returns
        `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/paradata_<sito>.graphml`.
        """
        return (
            _resolve_workspace_dir(self._handle, self._sito)
            / f"paradata_{self._slug}.graphml"
        )
```

#### Step 3: Refactor `group_store.py`

Same pattern as Step 2. Find the imports block at top:

```python
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .graph_ingestor import GraphSyncError
```

Replace with:

```python
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ._db_handle import _resolve_db_handle
from ._workspace import _resolve_workspace_dir
from .graph_ingestor import GraphSyncError
```

Find the `__init__` method (around line 74-80):

```python
    def __init__(self, db_path: Path, sito: str) -> None:
        if not sito:
            raise GroupValidationError(
                "sito is required for GroupStore")
        self._db_path = Path(db_path)
        self._sito = sito
        self._slug = _sito_slug(sito)
```

Replace with:

```python
    def __init__(self, db_path, sito: str) -> None:
        """Construct a site-scoped group store.

        PG-D (5.7.3-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        """
        if not sito:
            raise GroupValidationError(
                "sito is required for GroupStore")
        self._handle = _resolve_db_handle(db_path)
        # Preserve self._db_path for any defensive code that reads it
        # directly. Same pattern as ParadataStore.
        self._db_path = (
            self._handle.sqlite_path
            if self._handle.sqlite_path is not None
            else Path(self._handle.conn_str)
        )
        self._sito = sito
        self._slug = _sito_slug(sito)
```

Find the `file_path` property (around line 82-84):

```python
    @property
    def file_path(self) -> Path:
        return self._db_path.parent / f"groups_{self._slug}.graphml"
```

Replace with:

```python
    @property
    def file_path(self) -> Path:
        """Resolved groups file path for this (db, sito) pair.

        PG-D (5.7.3-alpha): SQLite returns `<sqlite_parent>/groups_<sito>.graphml`
        (byte-identical to pre-PG-D). PG returns
        `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/groups_<sito>.graphml`.
        """
        return (
            _resolve_workspace_dir(self._handle, self._sito)
            / f"groups_{self._slug}.graphml"
        )
```

#### Step 4: Run SQLite suite + critical regression gates (CRITICAL)

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"

# Full suite
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 25 skipped`.

```bash
# AC-2 (export side, should be untouched)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

```bash
# SQLite round-trip (general)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
```

Expected: PASS.

```bash
# Paradata round-trip (CRITICAL GATE for PG-D)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v 2>&1 | tail -10
```

Expected: ALL PASS.

```bash
# Groups round-trip (CRITICAL GATE for PG-D)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v 2>&1 | tail -10
```

Expected: ALL PASS.

```bash
# ParadataStore via graph_projector (CRITICAL GATE for PG-D)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v 2>&1 | tail -10
```

Expected: ALL PASS.

**If any of these fail → STOP. Do not commit. Report BLOCKED with full test output.**

Likely causes if a gate test breaks:
- `handle.sqlite_path.parent` produces a different path than `_db_path.parent` (e.g., relative vs absolute path resolution)
- Shim resolves `Path("nonexistent.sqlite")` to a `DbHandle` that fails `_resolve_workspace_dir` (e.g., if `sqlite_path` ends up None)
- `_db_path` attribute consumers downstream see a different value after the refactor

#### Step 5: Commit Group A

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/_workspace.py \
        modules/s3dgraphy/sync/paradata_store.py \
        modules/s3dgraphy/sync/group_store.py
git commit -m "$(cat <<'EOF'
refactor(pg-d/A): workspace dir helper + paradata/group store shim

NEW modules/s3dgraphy/sync/_workspace.py: cross-backend filesystem
workspace path resolution.

- _conn_slug(handle): deterministic <host>_<port>_<dbname> slug for
  PG handles, with non-[a-zA-Z0-9_-] chars replaced by underscores.
  Raises ValueError on non-PG handles. Single source of truth for
  future code that needs a filesystem-safe PG identifier.
- _resolve_workspace_dir(handle, sito): SQLite returns
  handle.sqlite_path.parent (byte-identical to pre-PG-D behaviour).
  PG returns ~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/
  with mkdir(parents=True, exist_ok=True). Raises ValueError on
  in-memory SQLite (no parent dir).

paradata_store.py + group_store.py: __init__(db_path, sito) keeps
the db_path keyword name but accepts Path | DbHandle | str via the
Foundation _resolve_db_handle shim. self._handle stored internally.
self._db_path attribute preserved (best-effort: handle.sqlite_path
for SQLite, conn_str for PG) so any defensive consumer reading the
attribute directly doesn't break.

The file_path property in both stores now calls
_resolve_workspace_dir(self._handle, self._sito) and appends the
existing filename pattern (paradata_<sito>.graphml or
groups_<sito>.graphml). Filename pattern uniform across backends.

SQLite path remains byte-identical to PG-C behaviour. Critical
regression gates (test_round_trip_with_paradata.py,
test_round_trip_with_groups.py, test_graph_projector_paradata.py)
all pass without modification.

NO QSettings UI changes (deferred to Consolidation 5.7.4 per Q1=b).
NO scripts/migrations/_common.py changes (no existing duplication
to DRY up; _conn_slug is purely new).

250 passed, 25 skipped (unchanged). AC-2 + 3 PG-D gate tests PASS.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

## Self-review checklist before reporting back

- [ ] NEW `_workspace.py` created with code matching spec §5 exactly
- [ ] `paradata_store.py` __init__ accepts db_path via shim, stores self._handle, preserves self._db_path attribute
- [ ] `paradata_store.py` file_path uses `_resolve_workspace_dir(self._handle, self._sito) / f"paradata_{self._slug}.graphml"`
- [ ] `group_store.py` __init__ + file_path same pattern
- [ ] No `cur.execute` / SQL changes anywhere (these files have no SQL)
- [ ] No changes to `scripts/migrations/_common.py`
- [ ] No changes to `gui/pyarchinitConfigDialog.py`
- [ ] Full suite: 250 passed, 25 skipped (unchanged)
- [ ] **AC-2 PASS** (critical)
- [ ] **`test_round_trip.py` PASS** (general SQLite round-trip)
- [ ] **`test_round_trip_with_paradata.py` PASS** (CRITICAL gate)
- [ ] **`test_round_trip_with_groups.py` PASS** (CRITICAL gate)
- [ ] **`test_graph_projector_paradata.py` PASS** (CRITICAL gate)
- [ ] Co-Authored-By count is 0
- [ ] No leftover changes after commit

## Report back format

- **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
- Commit SHA
- Test count (full suite + AC-2 + 3 PG-D gate tests)
- Co-Authored-By count
- Files changed (should be 3: _workspace.py NEW + paradata_store.py + group_store.py)
- Any concerns or surprises

If any gate test breaks → BLOCKED with full test output + diagnostic next step.

If you find yourself wanting to make any change beyond the plan (e.g., adding QSettings code, modifying `_common.py`, refactoring any other store method), STOP and report DONE_WITH_CONCERNS describing what you wanted to do. Do NOT silently deviate.

---

## Group B — `tests/sync/test_paradata_store_pg.py` (4 PG L2 cases)

### Task B.1: Create the 4-case PG paradata test file

**File:** `tests/sync/test_paradata_store_pg.py`

- [ ] **Step 1: Write the file**

Create with this content:

```python
# tests/sync/test_paradata_store_pg.py
"""PG-D: L2 PostgreSQL tests for ParadataStore on the new workspace dir.

Verifies that ParadataStore.file_path resolves to
~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/paradata_<sito>.graphml
on PG, that write+read round-trip works, that _conn_slug is
deterministic, and that multiple sites are isolated.

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine  # noqa: F401


def test_paradata_store_workspace_dir_on_pg(pg_engine, monkeypatch, tmp_path):
    """ParadataStore.file_path on PG resolves to
    <home>/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/paradata_<sito>.graphml.

    Use monkeypatch on Path.home to redirect to tmp_path so the test
    doesn't pollute the real user home dir.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = ParadataStore(db_path=handle, sito="TestSite")
    fp = store.file_path

    # The path lives under tmp_path/pyarchinit/pyarchinit_DB_folder/
    assert tmp_path in fp.parents
    assert "pyarchinit" in str(fp)
    assert "pyarchinit_DB_folder" in str(fp)
    assert fp.name == "paradata_testsite.graphml"
    # Parent dir is the sito subdir under conn_slug
    assert fp.parent.name == "TestSite"
    assert fp.parent.parent.parent.name == "pyarchinit_DB_folder"
    # Workspace dir was created by mkdir(parents=True, exist_ok=True)
    assert fp.parent.exists()
    assert fp.parent.is_dir()


def test_paradata_store_write_read_roundtrip_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """Construct ParadataStore on PG, write a paradata graph, read it
    back. End-to-end I/O on the new workspace dir."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = ParadataStore(db_path=handle, sito="TestSite")
    assert not store.exists()

    # add_author writes the paradata file
    store.add_author("Test Author", role="creator")
    assert store.exists()

    # Read back
    graph = store.read()
    author_nodes = [
        n for n in graph.nodes
        if type(n).__name__ == "AuthorNode"
    ]
    assert len(author_nodes) == 1, (
        f"expected 1 author, got {len(author_nodes)}"
    )
    assert getattr(author_nodes[0], "name", None) == "Test Author"


def test_paradata_store_conn_slug_deterministic_on_pg(pg_engine):
    """Two ParadataStore instances with the same handle produce the
    same file_path. _conn_slug is deterministic."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store1 = ParadataStore(db_path=handle, sito="DeterministicSite")
    store2 = ParadataStore(db_path=handle, sito="DeterministicSite")
    assert store1.file_path == store2.file_path


def test_paradata_store_multiple_sites_isolated_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """Two different sites on the same PG produce file_paths in
    different sito subdirs (isolation under the same conn_slug)."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.paradata_store import ParadataStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store_a = ParadataStore(db_path=handle, sito="SiteAlpha")
    store_b = ParadataStore(db_path=handle, sito="SiteBeta")

    # Same conn_slug parent
    assert store_a.file_path.parent.parent == store_b.file_path.parent.parent
    # Different sito subdirs
    assert store_a.file_path.parent != store_b.file_path.parent
    assert store_a.file_path.parent.name == "SiteAlpha"
    assert store_b.file_path.parent.name == "SiteBeta"
```

- [ ] **Step 2: Run the 4 tests**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py -v 2>&1 | tail -10
```

Expected (PG offline / no psycopg2 in dev env): ALL 4 SKIPPED with reason "PG not available at localhost:5433 (...)".

If PG online: 4 PASSED.

- [ ] **Step 3: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected (PG offline): `250 passed, 29 skipped` (250 + 4 new skips).

- [ ] **Step 4: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit Group B**

```bash
git add tests/sync/test_paradata_store_pg.py
git commit -m "$(cat <<'EOF'
test(pg-d/B): 4 L2 PostgreSQL tests for ParadataStore workspace

Four cases that pin the PG-D paradata design:

1. test_paradata_store_workspace_dir_on_pg - file_path resolves
   to <home>/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/
   paradata_<sito>.graphml. Uses monkeypatch on Path.home to
   redirect to tmp_path (no pollution of real home dir).
2. test_paradata_store_write_read_roundtrip_on_pg - end-to-end
   I/O: add_author writes, read returns the AuthorNode. Pins
   atomic write (.tmp + os.replace) on PG-side filesystem.
3. test_paradata_store_conn_slug_deterministic_on_pg - two stores
   with the same handle produce the same file_path. _conn_slug
   is deterministic.
4. test_paradata_store_multiple_sites_isolated_on_pg - two sites
   on same PG produce file_paths in different sito subdirs under
   the same conn_slug parent.

All 4 skip cleanly when PG offline / psycopg2 missing.
Uses pg_engine fixture from PG-B's conftest_pg.py.

PG offline: 250 passed, 29 skipped.
PG online: 254 passed, 12 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group C — `tests/sync/test_group_store_pg.py` (4 PG L2 cases)

### Task C.1: Create the 4-case PG group_store test file

**File:** `tests/sync/test_group_store_pg.py`

- [ ] **Step 1: Write the file**

Create with this content:

```python
# tests/sync/test_group_store_pg.py
"""PG-D: L2 PostgreSQL tests for GroupStore on the new workspace dir.

Verifies that GroupStore.file_path resolves to
~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/groups_<sito>.graphml
on PG, that write+read round-trip works, that _conn_slug is
deterministic, and that GroupStore shares the workspace dir with
ParadataStore (DRY check on _resolve_workspace_dir).

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine  # noqa: F401


def test_group_store_workspace_dir_on_pg(pg_engine, monkeypatch, tmp_path):
    """GroupStore.file_path on PG resolves to
    <home>/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/groups_<sito>.graphml."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = GroupStore(db_path=handle, sito="TestSite")
    fp = store.file_path

    assert tmp_path in fp.parents
    assert "pyarchinit_DB_folder" in str(fp)
    assert fp.name == "groups_testsite.graphml"
    assert fp.parent.name == "TestSite"
    assert fp.parent.exists()
    assert fp.parent.is_dir()


def test_group_store_write_read_roundtrip_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """Construct GroupStore on PG, add an ad-hoc group, read it back."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store = GroupStore(db_path=handle, sito="TestSite")
    assert not store.exists()

    # add_group writes the file
    store.add_group(
        group_uuid="test-group-uuid-1",
        name="TestGroup",
        description="A test group",
        member_us_uuids=[],
    )
    assert store.exists()

    groups = store.list_groups()
    assert len(groups) == 1, f"expected 1 group, got {len(groups)}"
    assert groups[0].get("name") == "TestGroup"


def test_group_store_conn_slug_deterministic_on_pg(pg_engine):
    """Two GroupStore instances with the same handle produce the same
    file_path."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    store1 = GroupStore(db_path=handle, sito="DeterministicSite")
    store2 = GroupStore(db_path=handle, sito="DeterministicSite")
    assert store1.file_path == store2.file_path


def test_group_store_uses_same_workspace_as_paradata_on_pg(
        pg_engine, monkeypatch, tmp_path):
    """ParadataStore + GroupStore with the same (handle, sito) produce
    file_paths in the SAME <conn_slug>/<sito>/ dir. Verifies DRY of
    _resolve_workspace_dir."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.paradata_store import ParadataStore
    from modules.s3dgraphy.sync.group_store import GroupStore

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    pstore = ParadataStore(db_path=handle, sito="SharedSite")
    gstore = GroupStore(db_path=handle, sito="SharedSite")

    # Same parent dir (the <conn_slug>/<sito>/ subdir)
    assert pstore.file_path.parent == gstore.file_path.parent
    # Different filenames (paradata vs groups)
    assert pstore.file_path.name != gstore.file_path.name
    assert "paradata_" in pstore.file_path.name
    assert "groups_" in gstore.file_path.name
```

- [ ] **Step 2: Run the 4 tests**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -m pytest tests/sync/test_group_store_pg.py -v 2>&1 | tail -10
```

Expected (PG offline): 4 SKIPPED. If PG online: 4 PASSED.

- [ ] **Step 3: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected (PG offline): `250 passed, 33 skipped` (+4 new skips).

- [ ] **Step 4: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit Group C**

```bash
git add tests/sync/test_group_store_pg.py
git commit -m "$(cat <<'EOF'
test(pg-d/C): 4 L2 PostgreSQL tests for GroupStore workspace

Four cases that pin the PG-D group_store design:

1. test_group_store_workspace_dir_on_pg - file_path resolves to
   <home>/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/
   groups_<sito>.graphml.
2. test_group_store_write_read_roundtrip_on_pg - end-to-end:
   add_group writes, list_groups returns the entry.
3. test_group_store_conn_slug_deterministic_on_pg - same handle
   -> same file_path.
4. test_group_store_uses_same_workspace_as_paradata_on_pg -
   ParadataStore + GroupStore with the same (handle, sito)
   produce file_paths in the SAME conn_slug/sito/ dir (DRY
   check on _resolve_workspace_dir).

All 4 skip cleanly when PG offline / psycopg2 missing.

PG offline: 250 passed, 33 skipped.
PG online: 258 passed, 12 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group D — Docs + version 5.7.3-alpha

### Task D.1: Bump `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.7.2-alpha` → `version=5.7.3-alpha`.

Verify:
```bash
grep "^version=" metadata.txt
```
Expected: `version=5.7.3-alpha`.

### Task D.2: Insert Phase 3 PG-D section to dev-log

**File:** `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Insert above PG-C section**

Use the Edit tool to find:

```
---

## Phase 3 — PG-C import pipeline (5.7.2-alpha)
```

Replace with:

```
---

## Phase 3 — PG-D paradata workspace (5.7.3-alpha)

**Tag:** `phase3-pgcompat-d-paradata-5.7.3-alpha`
**Date:** 2026-05-11
**Spec:** `docs/superpowers/specs/2026-05-11-pg-d-paradata-design.md`
**Plan:** `docs/superpowers/plans/2026-05-11-pg-d-paradata.md`

### What shipped

- ParadataStore + GroupStore work on both SQLite and PostgreSQL
- NEW `modules/s3dgraphy/sync/_workspace.py` with
  `_resolve_workspace_dir(handle, sito) -> Path` and
  `_conn_slug(handle) -> str`
- SQLite path: `handle.sqlite_path.parent` (byte-identical to
  pre-PG-D — legacy "alongside .sqlite" behaviour preserved)
- PG path: `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/`
  with `mkdir(parents=True, exist_ok=True)`
- Public `ParadataStore.__init__(db_path, sito)` and
  `GroupStore.__init__(db_path, sito)` keep `db_path` keyword
  but accept `Path | DbHandle | str` via Foundation shim
- File `file_path` property in both stores now calls
  `_resolve_workspace_dir` and appends the existing filename
  pattern (`paradata_<sito>.graphml` / `groups_<sito>.graphml`)
- NO SQL refactor (these files have no SQL queries)
- NO QSettings UI changes (deferred to Consolidation 5.7.4 per
  Q1=b decision)
- NO changes to `scripts/migrations/_common.py` (no existing
  duplication to DRY up)

### Tests

- 4 new L2 PG cases in `test_paradata_store_pg.py` (workspace
  dir resolution, write+read round-trip, conn_slug determinism,
  multi-site isolation)
- 4 new L2 PG cases in `test_group_store_pg.py` (parallel to
  paradata, plus shared-workspace test verifying paradata +
  group_store share the same `<conn_slug>/<sito>/` dir)
- All 8 skip cleanly when PG offline / psycopg2 missing
- Total: 250 passed, 33 skipped (PG offline) or 258 passed,
  12 skipped (PG online + psycopg2)
- AC-2 byte-identical preserved (PG-D doesn't touch export)
- 3 critical SQLite regression gates stay green untouched:
  test_round_trip_with_paradata.py, test_round_trip_with_groups.py,
  test_graph_projector_paradata.py

### Phase 3 status

After PG-D ships, **Phase 3 is complete modulo Consolidation
5.7.4-alpha**:
- Foundation 5.6.2-alpha ✅
- PG-A migration 5.7.0-alpha ✅
- PG-B export 5.7.1-alpha ✅
- PG-C import 5.7.2-alpha ✅
- PG-D paradata 5.7.3-alpha ✅
- Consolidation 5.7.4-alpha pending

Zero residual `sqlite3.connect()` calls in
`modules/s3dgraphy/sync/`. All production code paths flipped to
SQLAlchemy + DbHandle shim.

### Known follow-ups (Consolidation 5.7.4-alpha)

- Rename `db_path` → `db_input` on all public APIs (populate_list,
  populate_graph, export_graphml, dimensions_with_data,
  build_groups_from_sql, add_columns, backfill_uuids,
  ParadataStore.__init__, GroupStore.__init__) with proper
  DeprecationWarning cycle
- QSettings UI "Paradata Workspace" override in
  `gui/pyarchinitConfigDialog.py` (deferred from PG-D Q1=b)
- Documentation cleanup
- Promote parametrized tests where it makes sense

---

## Phase 3 — PG-C import pipeline (5.7.2-alpha)
```

### Task D.3: Prepend bilingual CHANGELOG entry

**File:** `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Insert above 5.7.2-alpha section**

Use the Edit tool to find:

```
## [5.7.2-alpha] - 2026-05-11
```

Replace with:

```
## [5.7.3-alpha] - 2026-05-11

### Italiano

**PG-D — ParadataStore + GroupStore lavorano su PostgreSQL.**

Quarto e ultimo milestone "core" della Phase 3. Ribalta i due file system store (paradata + groups) sull'infrastruttura cross-backend. Tutti i 250 test SQLite di PG-C restano verdi via shim, INCLUSO i 3 critical gate (test_round_trip_with_paradata, test_round_trip_with_groups, test_graph_projector_paradata). AC-2 byte-identical preservato.

- **NEW `modules/s3dgraphy/sync/_workspace.py`**: helper module con `_resolve_workspace_dir(handle, sito) -> Path` e `_conn_slug(handle) -> str`. SQLite branch ritorna `handle.sqlite_path.parent` (byte-identical al comportamento pre-PG-D). PG branch ritorna `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/` con `mkdir(parents=True, exist_ok=True)`.
- **`_conn_slug`**: formula deterministica `slugify(f"{host}_{port}_{dbname}")` con regex `[^a-zA-Z0-9_-]` → `_`. Single source of truth per identificatori filesystem-safe basati su URL PG.
- **`paradata_store.py` + `group_store.py`**: constructor accetta `Path | DbHandle | str` via shim Foundation. Property `file_path` chiama `_resolve_workspace_dir` invece di `self._db_path.parent`. Filename pattern uniforme su entrambi i backend (`paradata_<sito>.graphml` / `groups_<sito>.graphml`).
- **Zero SQL refactor**: questi file non hanno query SQL. PG-D è il più piccolo milestone PG-X (~360 LOC vs PG-A/B/C ~470-660 LOC).
- **SQLite preservation**: i 15 caller esistenti (1 bridge, 2 graph_projector, 11 scripts/s3dgraphy_sync, 6 test) continuano a passare `Path` e funzionano invariati via shim. Comportamento file system byte-identical per SQLite users.
- **NO QSettings UI** (deferred to Consolidation 5.7.4 per Q1=b).
- **8 nuovi test L2 PG**: 4 in `test_paradata_store_pg.py` + 4 in `test_group_store_pg.py`. Tutti usano `monkeypatch` su `Path.home()` per non polluire il home dir reale. Skippano puliti quando PG offline o psycopg2 mancante.

**Phase 3 è ora completa modulo Consolidation 5.7.4-alpha** (rename `db_path → db_input` + QSettings UI + cleanup).

Test count: 250 → 250 passed, 33 skipped (PG offline) o 258 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato.

### English

**PG-D — ParadataStore + GroupStore work on PostgreSQL.**

Fourth and final "core" milestone of Phase 3. Flips the two filesystem stores (paradata + groups) onto the cross-backend infrastructure. All 250 PG-C SQLite tests stay green via shim, INCLUDING the 3 critical gates (test_round_trip_with_paradata, test_round_trip_with_groups, test_graph_projector_paradata). AC-2 byte-identical preserved.

- **NEW `modules/s3dgraphy/sync/_workspace.py`**: helper module with `_resolve_workspace_dir(handle, sito) -> Path` and `_conn_slug(handle) -> str`. SQLite branch returns `handle.sqlite_path.parent` (byte-identical to pre-PG-D behaviour). PG branch returns `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/` with `mkdir(parents=True, exist_ok=True)`.
- **`_conn_slug`**: deterministic formula `slugify(f"{host}_{port}_{dbname}")` with regex `[^a-zA-Z0-9_-]` → `_`. Single source of truth for filesystem-safe PG identifiers.
- **`paradata_store.py` + `group_store.py`**: constructor accepts `Path | DbHandle | str` via Foundation shim. `file_path` property calls `_resolve_workspace_dir` instead of `self._db_path.parent`. Filename pattern uniform across backends (`paradata_<sito>.graphml` / `groups_<sito>.graphml`).
- **Zero SQL refactor**: these files have no SQL queries. PG-D is the smallest PG-X milestone (~360 LOC vs PG-A/B/C ~470-660 LOC).
- **SQLite preservation**: the 15 existing callers (1 bridge, 2 graph_projector, 11 scripts/s3dgraphy_sync, 6 tests) continue to pass `Path` and work unchanged via shim. File-system behaviour byte-identical for SQLite users.
- **NO QSettings UI** (deferred to Consolidation 5.7.4 per Q1=b).
- **8 new L2 PG tests**: 4 in `test_paradata_store_pg.py` + 4 in `test_group_store_pg.py`. All use `monkeypatch` on `Path.home()` to avoid polluting the real home dir. Skip cleanly when PG offline or psycopg2 missing.

**Phase 3 is now complete modulo Consolidation 5.7.4-alpha** (rename `db_path → db_input` + QSettings UI + cleanup).

Test count: 250 → 250 passed, 33 skipped (PG offline) or 258 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved.

---

## [5.7.2-alpha] - 2026-05-11
```

### Task D.4: Commit + final verification

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git log --oneline 88e5892f..HEAD
git log 88e5892f..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v 2>&1 | tail -5
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v 2>&1 | tail -5
grep "^version=" metadata.txt
```

Expected:
- 3 commits since `88e5892f`: A, B, C
- Co-Authored-By count: `0`
- Test suite: `250 passed, 33 skipped` (PG offline)
- AC-2 PASS
- Round-trip gates ALL PASS
- Version: `5.7.3-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(pg-d/D): docs + version bump 5.7.3-alpha

PG-D milestone documentation: bilingual CHANGELOG entry, dev-log
Phase 3 PG-D section, version bump 5.7.2-alpha -> 5.7.3-alpha.

Cumulative deliverables (Groups A-D):
- NEW _workspace.py: cross-backend filesystem workspace helper
  (_resolve_workspace_dir + _conn_slug)
- paradata_store.py + group_store.py: shim continuity (db_path
  keyword accepts Path|DbHandle|str), file_path property uses
  _resolve_workspace_dir
- 4 new L2 PG tests in test_paradata_store_pg.py
- 4 new L2 PG tests in test_group_store_pg.py

Test count: 250 -> 250 passed, 33 skipped (PG offline) or
250 -> 258 passed, 12 skipped (PG online with psycopg2).
AC-2 byte-identical preserved.
3 critical SQLite regression gates preserved.

Phase 3 now complete modulo Consolidation 5.7.4-alpha (rename
db_path -> db_input + QSettings UI + cleanup).

Spec: docs/superpowers/specs/2026-05-11-pg-d-paradata-design.md
Plan: docs/superpowers/plans/2026-05-11-pg-d-paradata.md
Predecessor: phase3-pgcompat-c-import-5.7.2-alpha (cf6ed26e)
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

- [ ] **Step 3: Post-commit verification**

```bash
git log --oneline 88e5892f..HEAD
git log 88e5892f..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 4 commits since `88e5892f`: A, B, C, D
- Co-Authored-By count: `0`
- `250 passed, 33 skipped`
- Version: `5.7.3-alpha`

---

## Group E — Tag + push

### Task E.1: Pre-flight branch check

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
```

Expected: `Stratigraph_00001`. **STOP and BLOCK** if anything else.

### Task E.2: Create annotated tag

```bash
git tag -a phase3-pgcompat-d-paradata-5.7.3-alpha -m "$(cat <<'EOF'
PG-D - ParadataStore + GroupStore workspace on PostgreSQL

Fourth and final 'core' milestone of Phase 3 (PG-compat refactor).
ParadataStore + GroupStore now work on both SQLite and PostgreSQL
backends via the new _workspace.py helper. After PG-D ships,
Phase 3 is complete modulo Consolidation 5.7.4-alpha.

Cumulative deliverables (Groups A-D, 4 commits):

- NEW modules/s3dgraphy/sync/_workspace.py:
  - _conn_slug(handle): deterministic slugify(host_port_dbname)
    formula for PG handles. Single source of truth for filesystem-safe
    PG identifiers. Raises ValueError on non-PG handles.
  - _resolve_workspace_dir(handle, sito): SQLite returns
    handle.sqlite_path.parent (byte-identical to pre-PG-D). PG
    returns ~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/
    with mkdir(parents=True, exist_ok=True).
- paradata_store.py + group_store.py: constructor accepts
  Path | DbHandle | str via Foundation _resolve_db_handle shim.
  file_path property calls _resolve_workspace_dir. Filename pattern
  uniform across backends.
- NO SQL refactor (these files have no SQL queries).
- NO QSettings UI changes (deferred to Consolidation 5.7.4 per
  Q1=b decision).
- NO scripts/migrations/_common.py changes (no existing
  duplication to DRY up).

Tests: 4 new PG L2 tests in test_paradata_store_pg.py + 4 in
test_group_store_pg.py. All use monkeypatch on Path.home() to
avoid polluting the real home dir. Skip cleanly when PG offline /
psycopg2 missing.

Test counts: 250 -> 250 passed, 33 skipped (PG offline) or
250 -> 258 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical preserved.
3 critical SQLite regression gates preserved:
test_round_trip_with_paradata.py, test_round_trip_with_groups.py,
test_graph_projector_paradata.py.

Phase 3 status after PG-D:
- Foundation 5.6.2-alpha SHIPPED
- PG-A migration 5.7.0-alpha SHIPPED
- PG-B export 5.7.1-alpha SHIPPED
- PG-C import 5.7.2-alpha SHIPPED
- PG-D paradata 5.7.3-alpha SHIPPED
- Consolidation 5.7.4-alpha PENDING

Zero residual sqlite3.connect() in modules/s3dgraphy/sync/.

Spec: docs/superpowers/specs/2026-05-11-pg-d-paradata-design.md
Plan: docs/superpowers/plans/2026-05-11-pg-d-paradata.md
Predecessor: phase3-pgcompat-c-import-5.7.2-alpha (cf6ed26e)
EOF
)"
```

### Task E.3: Verify the tag

```bash
echo "=== Tag created locally ==="
git tag -n5 phase3-pgcompat-d-paradata-5.7.3-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse phase3-pgcompat-d-paradata-5.7.3-alpha^{commit}
git rev-parse HEAD
echo "=== Tag is annotated ==="
git cat-file -t phase3-pgcompat-d-paradata-5.7.3-alpha
echo "=== Tag message has NO Co-Authored-By ==="
git tag -l --format='%(contents)' phase3-pgcompat-d-paradata-5.7.3-alpha | grep -c Co-Authored-By
```

Final grep MUST return `0`.

### Task E.4: Push tag + branch

```bash
git push origin phase3-pgcompat-d-paradata-5.7.3-alpha 2>&1 | tail -3
git push origin Stratigraph_00001 2>&1 | tail -3
```

### Task E.5: Verify on origin

```bash
git ls-remote --tags origin | grep "phase3-pgcompat-d-paradata-5.7.3-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected: tag listed (with `^{}` line), branch tip equals local HEAD.

### Task E.6: Memory snapshot (controller, no subagent)

After Group E ships, the controller updates `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move PG-D from PENDING to SHIPPED with all SHAs + lessons learned
- Add note: **Phase 3 complete modulo Consolidation 5.7.4**
- Update `MEMORY.md` index line

---

## Self-Review

This plan covers every PG-D spec requirement:

| Spec section | Plan task |
|---|---|
| §3.1 Q1=b (QSettings UI deferred) | NO `pyarchinitConfigDialog.py` changes anywhere |
| §3.2 Approach 1 (single workspace helper) | Group A NEW `_workspace.py` |
| §3.3 Shim continuity | Group A Step 2/3 (constructor signatures) |
| §3.4 `_conn_slug` (corrected: no DRY-up, purely new) | Group A Step 1 |
| §3.5 SQLite preservation | Group A Step 4 (CRITICAL regression gates) |
| §4.1 NEW `_workspace.py` | Group A Step 1 |
| §4.2 paradata_store + group_store modifications | Group A Steps 2 + 3 |
| §4.5 NOT touched (`_common.py`, UI, etc.) | Documented in File Structure section |
| §5 `_workspace.py` helper spec | Group A Step 1 exact code |
| §6 Data flow + error handling | Group A Step 4 diagnostics + Step 5 commit |
| §7 Test strategy | Groups B + C |
| §8 Acceptance criteria | Pinned by Groups A (regression), B (paradata), C (group_store) |
| §9 Release plan | Groups D + E |

**Type consistency check:** `_workspace`, `_resolve_workspace_dir`, `_conn_slug`, `DbHandle`, `_resolve_db_handle`, `handle.sqlite_path`, `handle.is_postgres`, `handle.engine.url`, `pg_engine`, `monkeypatch`, `Path.home` — all used consistently across Groups.

**No placeholders:** every step has runnable code, exact commands, or specific file edits.

**Scope check:** Plan focused on PG-D only. `_common.py` NOT touched (spec correction documented in header). UI deferred to Consolidation.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-pg-d-paradata.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review, fast iteration

**2. Inline Execution** — execute tasks in this session via `executing-plans`, batch with checkpoints

If **Subagent-Driven**, recommended batching:
- Group 0 (2 tasks) → no subagent — pure git
- Group A → 1 subagent (NEW `_workspace.py` + 2 small store refactors; ~130 LOC; AC-2 + 3 gate tests sanity ping)
- Group B → 1 subagent (4 PG L2 paradata tests)
- Group C → 1 subagent (4 PG L2 group_store tests)
- Group D → 1 subagent (docs + version + final verification)
- Group E → 1 subagent (tag + push, gate for user approval)
- Memory snapshot → no subagent (controller writes after E ships)

If **Inline Execution**, batch by Group with checkpoint after each.
