# PG-Compat Foundation (5.6.2-alpha) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the foundation infrastructure for PostgreSQL compatibility — `DbHandle` value object, `_resolve_db_handle()` shim accepting Path/str/DbManager/Engine, dialect-aware `_columns_of()` introspection, `conftest_pg.py` test fixture skeleton — **without changing any caller**, so all 234 existing SQLite tests stay green and no production code path switches semantics. Release `5.6.2-alpha`.

**Architecture:** Two new files in `modules/s3dgraphy/sync/`: `_db_handle.py` (DbHandle dataclass + 3 exceptions + `_resolve_db_handle()` shim + `_columns_of()` helper) and the public re-export from `__init__.py`. Test infrastructure: `tests/sync/conftest_pg.py` with `pg_engine` session fixture (skip cleanly if PG unreachable at `localhost:5433`) and `_apply_pyarchinit_schema(engine)` DDL bootstrap. New unit tests in `test_db_handle_shim.py` (10 cases) + smoke test in `test_pg_smoke.py` (1 case, skipped if PG offline). Zero production caller changes — Foundation is preparatory machinery only.

**Tech Stack:** Python 3.9+, SQLAlchemy 2.0 (already a dep via pyarchinit_db_manager), psycopg2-binary 2.9+ (NEW), pytest, sqlite3 (stdlib). **No new third-party dependencies on the production runtime path** — psycopg2-binary is required only when the user actually connects to PG.

**Spec source of truth:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` (commit `9355bed1`)

**Predecessor releases:**
- AI07 hotfix: tag `phase2-ai07-hotfix-5.6.1-alpha` (`026199c2`)
- Struttura sigla fix: `24377960`

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_ai07_post_release.md` — current state of Phase 2 ship
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/MEMORY.md` — Phase 1 node_uuid migration is MANUAL (already noted)

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

**Local PG setup (USER pre-creates):**
- Host: `localhost`
- Port: `5433`
- User: `postgres`
- Password: `postgres`
- Test DB to create: `pyarchinit_test_pg`

```bash
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE pyarchinit_test_pg"
```

The `pg_engine` fixture in `conftest_pg.py` creates the schema (us_table, site_table, periodizzazione_table) on first connection. Subsequent test runs reuse the schema; `clean_pg` truncates between tests.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `modules/s3dgraphy/sync/_db_handle.py` | `DbHandle` frozen dataclass + 3 exceptions (`DbHandleError`, `UnsupportedBackendError`, `PgConnectionError`) + `_resolve_db_handle(arg) -> DbHandle` shim accepting Path \| str \| DbManager \| Engine \| DbHandle + `_columns_of(engine, table) -> set[str]` dialect-aware introspection. ~80 LOC. |
| `tests/sync/test_db_handle_shim.py` | L0 unit tests for `_resolve_db_handle` and `DbHandle` factory methods. 10 tests covering all 5 input types + 2 deprecation warning checks + 3 error paths. ~120 LOC. |
| `tests/sync/conftest_pg.py` | `pg_engine` session fixture (skip cleanly if PG unreachable), `clean_pg` function fixture (TRUNCATE before each test), `_apply_pyarchinit_schema(engine)` DDL bootstrap helper that uses existing `modules/db/structures/*.py` Table definitions. ~80 LOC. |
| `tests/sync/test_pg_smoke.py` | L2 smoke test: `pg_engine` fixture connects, schema is present, `_columns_of()` returns expected columns on PG. Skipped cleanly if PG offline. 1 test. ~30 LOC. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/__init__.py` | Re-export `DbHandle` for callers. ~5 LOC. |
| `requirements.txt` | Add `psycopg2-binary>=2.9` (was implicit dep via SQLAlchemy + pyarchinit_db_manager). 1 line. |
| `metadata.txt` | Bump `version=5.6.1-alpha` → `version=5.6.2-alpha`. 1 line. |
| `dev_logs/CHANGELOG.md` | Prepend `## [5.6.2-alpha] - 2026-05-10` bilingual section. ~30 LOC. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | New "Phase 3 — PG Compat Foundation" section. ~30 LOC. |

### Explicitly NOT touched (per spec §4.1 — Foundation introduces machinery without using it)

- `modules/s3dgraphy/sync/graph_projector.py` — 8 sqlite3.connect call sites stay untouched (PG-B refactor)
- `modules/s3dgraphy/sync/graph_ingestor.py` — 3 sqlite3.connect call sites stay untouched (PG-C refactor)
- `modules/s3dgraphy/sync/graphml_writer.py` — 1 sqlite3.connect call site stays untouched (PG-B refactor)
- `modules/s3dgraphy/sync/group_projector.py` — 2 sqlite3.connect call sites stay untouched (PG-B refactor)
- `modules/s3dgraphy/sync/paradata_store.py`, `group_store.py` — file-path resolution stays untouched (PG-D refactor)
- `scripts/migrations/_2026_05_node_uuid_backfill_lib.py` and `2026_05_node_uuid_backfill.py` — stay sqlite3-only (PG-A refactor)
- `modules/s3dgraphy/s3dgraphy_dot_bridge.py` — dialog handlers stay untouched (later milestones)
- `modules/db/pyarchinit_db_manager.py` — already has the SQLAlchemy `engine` attribute we need; no changes
- `tests/sync/test_ai03_export_byte_identical.py` — AC-2 baseline must stay byte-identical green
- All other 233 existing tests — must stay green via the no-caller-change invariant

---

## Test strategy

- **L0 unit tests** (`test_db_handle_shim.py`): pure pytest, no DB, no QGIS bootstrap. Fast — runs in CI on every push regardless of PG availability.
- **L2 PG smoke** (`test_pg_smoke.py`): requires PG online at `localhost:5433`. Skipped cleanly via `pg_engine` fixture if unreachable. Verifies the fixture machinery itself works end-to-end.
- **L3 regression guards** — must stay green at every commit:

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no            # full SQLite suite
```

`test_ai03_export_byte_identical.py` is allowed to **change** only in PG-B (re-baseline if structural fingerprint shifts due to `engine.connect()` ordering — unlikely but possible). Anywhere in Foundation it MUST stay green untouched.

Decision-pinning matrix (Foundation):

| Decision / Acceptance | Pinning test |
|---|---|
| Q2=A SQLAlchemy shim accepts Path | `test_db_handle_shim.py::test_resolve_from_path` |
| Q2=A shim accepts str (sqlite/postgresql conn_str) | `test_db_handle_shim.py::test_resolve_from_sqlite_conn_str` + `test_resolve_from_postgresql_conn_str` |
| Q2=A shim accepts DbManager | `test_db_handle_shim.py::test_resolve_from_db_manager` |
| Q2=A shim accepts Engine | `test_db_handle_shim.py::test_resolve_from_engine` |
| Q2=A shim is idempotent on DbHandle | `test_db_handle_shim.py::test_resolve_from_db_handle_passthrough` |
| Q2=A Path triggers DeprecationWarning | `test_db_handle_shim.py::test_path_emits_deprecation_warning` |
| `UnsupportedBackendError` raised on unknown conn str | `test_db_handle_shim.py::test_unknown_conn_str_raises` |
| `_columns_of()` works on SQLite | `test_db_handle_shim.py::test_columns_of_sqlite` |
| `_columns_of()` works on PG | `test_pg_smoke.py::test_columns_of_pg_us_table` |
| AC-2 stays green (regression guard) | `test_ai03_export_byte_identical.py` (existing, untouched) |

Test count progression:
- Baseline (post `5080af8b` STATUS_ITEMS fix + `24377960` sigla fix): 234 passed, 3 skipped
- Post-Group A: 234 + 3 (DbHandle dataclass tests) = 237 passed, 3 skipped
- Post-Group B: 237 + 7 (5 resolver paths + 1 deprecation + 1 error) = 244 passed, 3 skipped
- Post-Group C: 244 + 1 (`_columns_of` SQLite) = 245 passed, 3 skipped
- Post-Group D: 245 + 1 (`test_pg_smoke.py`) = 246 passed, 4 skipped (or 245 + 1 if PG offline at run time)
- Post-Group F (final): same — 246 passed, 4 skipped (3 pre-existing + 1 PG smoke if offline)

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

Expected: tracked changes empty, last commit is `9355bed1 spec(pg-compat): …` (or later if user added more), `0\t0` ahead-behind.

- [ ] **Step 2: Verify predecessor tag exists**

```bash
git tag --list | grep -E "phase2-ai07-hotfix-5.6.1-alpha"
```

Expected: `phase2-ai07-hotfix-5.6.1-alpha` listed.

- [ ] **Step 3: Capture baseline test count**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `234 passed, 3 skipped` (or higher if other recent commits added tests).

### Task 0.2: Create PG-Compat rollback safety tag

**Files:** none (git operation)

- [ ] **Step 1: Create rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-pg-compat-foundation -m "Rollback point before PG compat Foundation milestone

Predecessor: phase2-ai07-hotfix-5.6.1-alpha (026199c2)
Spec commit: 9355bed1
Sigla fix: 24377960

If PG-compat Foundation needs to be reverted, reset hard to this tag."
git push origin pre-pg-compat-foundation
```

Expected output: `* [new tag]         pre-pg-compat-foundation -> pre-pg-compat-foundation`.

### Task 0.3: USER pre-creates the PG test database

**Files:** none (user action)

- [ ] **Step 1 (USER action — agent waits):** Run from a terminal:

```bash
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE pyarchinit_test_pg" 2>&1
```

Expected: `CREATE DATABASE` (or `database "pyarchinit_test_pg" already exists` — both acceptable).

If PG is not running on `localhost:5433`, that is also acceptable for Foundation — the conftest fixture skips cleanly. The fixture only fails the test when the connection string format is invalid, not when the server is offline.

- [ ] **Step 2: Smoke-verify reachability from Python**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
from sqlalchemy import create_engine, text
try:
    engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg')
    with engine.connect() as conn:
        print('PG OK:', conn.execute(text('SELECT version()')).scalar())
except Exception as e:
    print(f'PG OFFLINE (expected if no local PG): {type(e).__name__}: {e}')
"
```

Expected output (one of two):
- PG online: `PG OK: PostgreSQL 16.x ...`
- PG offline: `PG OFFLINE (expected if no local PG): OperationalError: ...`

Both outcomes are acceptable. Foundation tests skip cleanly when PG is offline.

---

## Group A — `DbHandle` dataclass + new exceptions

### Task A.1: TDD — write failing test for DbHandle dataclass

**Files:**
- Create: `tests/sync/test_db_handle_shim.py`

- [ ] **Step 1: Create the test file with 3 dataclass tests**

```python
# tests/sync/test_db_handle_shim.py
"""PG-Compat Foundation: tests for DbHandle dataclass + _resolve_db_handle shim."""
from __future__ import annotations

from pathlib import Path

import pytest


def test_db_handle_is_frozen_dataclass():
    """DbHandle must be immutable (frozen=True)."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from sqlalchemy import create_engine
    eng = create_engine("sqlite:///:memory:")
    h = DbHandle(engine=eng, is_postgres=False, sqlite_path=None,
                 conn_str="sqlite:///:memory:")
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        h.engine = None  # type: ignore[misc]


def test_db_handle_from_path_creates_sqlite_engine(tmp_path):
    """from_path() builds a SQLite engine and records the Path."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "dummy.sqlite"
    p.touch()
    h = DbHandle.from_path(p)
    assert h.is_postgres is False
    assert h.sqlite_path == p
    assert h.conn_str == f"sqlite:///{p}"
    # Engine works
    from sqlalchemy import text
    with h.engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_db_handle_from_engine_detects_postgres():
    """from_engine() honours the dialect (sqlite vs postgresql)."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from sqlalchemy import create_engine
    sqlite_eng = create_engine("sqlite:///:memory:")
    h_sqlite = DbHandle.from_engine(sqlite_eng, "sqlite:///:memory:")
    assert h_sqlite.is_postgres is False
    assert h_sqlite.sqlite_path is None  # in-memory has no path
```

- [ ] **Step 2: Run to verify all 3 fail**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_db_handle_shim.py -v
```

Expected: 3 FAILs (or errors) — `ImportError: No module named '_db_handle'` for all three.

### Task A.2: Implement DbHandle dataclass + new exceptions

**Files:**
- Create: `modules/s3dgraphy/sync/_db_handle.py`

- [ ] **Step 1: Create the module with dataclass + exceptions**

```python
# modules/s3dgraphy/sync/_db_handle.py
"""PG-Compat Foundation: backend-agnostic DbHandle + resolver shim.

This module is the single entry point through which the s3dgraphy bridge
layer accesses the underlying database. It accepts any of the input
shapes used by existing callers (Path, str, DbManager, Engine) and
normalises them to a `DbHandle` value object that subsequent bridge
methods operate on.

Foundation milestone (5.6.2-alpha) introduces this machinery WITHOUT
changing any caller. PG-A through PG-D milestones progressively
replace direct `sqlite3.connect()` call sites in the bridge with
`DbHandle.engine` access.

Spec: docs/superpowers/specs/2026-05-10-postgres-compat-design.md
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .graph_ingestor import GraphSyncError


class DbHandleError(GraphSyncError):
    """Failure resolving a db_handle argument."""


class UnsupportedBackendError(DbHandleError):
    """Conn string dialect not in {sqlite, postgresql}."""


class PgConnectionError(DbHandleError):
    """PG engine constructed but TCP connection failed."""


@dataclass(frozen=True)
class DbHandle:
    """Backend-agnostic handle wrapping a SQLAlchemy engine.

    Use the factory classmethods (`from_path`, `from_engine`,
    `from_db_manager`) rather than constructing directly.
    """
    engine: Engine                      # Always set
    is_postgres: bool
    sqlite_path: Optional[Path]         # Set only when backend is SQLite + file-backed
    conn_str: str                       # Original conn string for slug derivation

    @classmethod
    def from_path(cls, p: Path) -> "DbHandle":
        """Build a DbHandle from a SQLite file path."""
        conn_str = f"sqlite:///{p}"
        engine = create_engine(conn_str)
        return cls(engine=engine, is_postgres=False, sqlite_path=p,
                   conn_str=conn_str)

    @classmethod
    def from_engine(cls, engine: Engine, conn_str: str) -> "DbHandle":
        """Wrap an existing SQLAlchemy engine. Detects backend from
        engine.dialect.name."""
        is_pg = engine.dialect.name == "postgresql"
        sqlite_path: Optional[Path] = None
        if conn_str.startswith("sqlite:///") and not conn_str.endswith(":memory:"):
            sqlite_path = Path(conn_str[len("sqlite:///"):])
        return cls(engine=engine, is_postgres=is_pg, sqlite_path=sqlite_path,
                   conn_str=conn_str)
```

- [ ] **Step 2: Run to verify the 3 dataclass tests pass**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_db_handle_shim.py -v 2>&1 | tail -10
```

Expected: 3 PASSED.

- [ ] **Step 3: Run full sync suite to confirm no regression**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: `237 passed, 3 skipped` (234 + 3 new). AC-2 still green.

- [ ] **Step 4: AC-2 sanity ping**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/_db_handle.py \
        tests/sync/test_db_handle_shim.py
git commit -m "feat(pg-compat/A): DbHandle dataclass + 3 exceptions

Foundation step 1 of PG-compat refactor: introduce a frozen
DbHandle dataclass that wraps a SQLAlchemy engine and tracks
whether the backend is PostgreSQL. Factory classmethods from_path
and from_engine handle the two primary construction paths.

Three new exceptions inherit from existing GraphSyncError:
- DbHandleError (base for shim failures)
- UnsupportedBackendError (conn str dialect not in {sqlite, postgresql})
- PgConnectionError (PG engine built but TCP connection failed)

3 unit tests pin the dataclass contract (frozen, factory methods,
backend detection from engine.dialect.name).

No caller changes — Foundation introduces machinery only."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group B — `_resolve_db_handle` shim

### Task B.1: TDD — write failing tests for all 5 input types

**Files:**
- Modify: `tests/sync/test_db_handle_shim.py` (append 7 new tests)

- [ ] **Step 1: Append the 7 resolver tests**

```python
# Append to tests/sync/test_db_handle_shim.py


def test_resolve_from_path(tmp_path):
    """Path → SQLite engine via shim, with DeprecationWarning."""
    from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
    p = tmp_path / "x.sqlite"
    p.touch()
    with pytest.warns(DeprecationWarning):
        h = _resolve_db_handle(p)
    assert h.is_postgres is False
    assert h.sqlite_path == p


def test_resolve_from_sqlite_conn_str(tmp_path):
    """str starting with 'sqlite:' → engine."""
    from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
    h = _resolve_db_handle("sqlite:///:memory:")
    assert h.is_postgres is False


def test_resolve_from_postgresql_conn_str():
    """str starting with 'postgresql:' → engine (PG dialect detected)."""
    from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
    h = _resolve_db_handle("postgresql+psycopg2://x:y@localhost/z")
    assert h.is_postgres is True
    assert h.sqlite_path is None


def test_resolve_from_db_manager():
    """DbManager → use existing .engine attribute."""
    from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
    from sqlalchemy import create_engine

    class FakeDbManager:
        engine = create_engine("sqlite:///:memory:")
        conn_str = "sqlite:///:memory:"

    h = _resolve_db_handle(FakeDbManager())
    assert h.is_postgres is False
    assert h.engine is FakeDbManager.engine


def test_resolve_from_engine():
    """SQLAlchemy Engine → wrap as DbHandle."""
    from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
    from sqlalchemy import create_engine
    eng = create_engine("sqlite:///:memory:")
    h = _resolve_db_handle(eng)
    assert h.is_postgres is False
    assert h.engine is eng


def test_resolve_from_db_handle_passthrough(tmp_path):
    """DbHandle → return as-is (idempotent)."""
    from modules.s3dgraphy.sync._db_handle import (
        DbHandle, _resolve_db_handle,
    )
    p = tmp_path / "y.sqlite"
    p.touch()
    original = DbHandle.from_path(p)
    h = _resolve_db_handle(original)
    assert h is original


def test_resolve_unknown_str_raises():
    """str with unknown dialect prefix → UnsupportedBackendError."""
    from modules.s3dgraphy.sync._db_handle import (
        _resolve_db_handle, UnsupportedBackendError,
    )
    with pytest.raises(UnsupportedBackendError):
        _resolve_db_handle("mysql://foo/bar")
```

- [ ] **Step 2: Run to verify all 7 fail**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_db_handle_shim.py -v 2>&1 | tail -15
```

Expected: 3 PASSED (existing) + 7 FAILed (new) — `_resolve_db_handle` not yet defined.

### Task B.2: Implement `_resolve_db_handle` shim

**Files:**
- Modify: `modules/s3dgraphy/sync/_db_handle.py` (append shim function)

- [ ] **Step 1: Append `_resolve_db_handle` to the module**

```python
# Append to modules/s3dgraphy/sync/_db_handle.py


def _resolve_db_handle(arg) -> DbHandle:
    """Backward-compat shim — accept any of:

      - Path: SQLite file path (emits DeprecationWarning)
      - str: SQLAlchemy conn string (sqlite:// or postgresql://)
      - DbManager: pyarchinit Pyarchinit_db_management instance
                   (uses existing .engine + .conn_str)
      - Engine: SQLAlchemy engine (constructs DbHandle around it)
      - DbHandle: passthrough (idempotent)

    Raises UnsupportedBackendError for str with unknown dialect prefix.
    """
    import warnings

    # Order matters: check DbHandle FIRST (it's a dataclass — could
    # accidentally match other branches via duck-typing).
    if isinstance(arg, DbHandle):
        return arg

    if isinstance(arg, Path):
        warnings.warn(
            "Passing db_path: Path to the s3dgraphy bridge is "
            "deprecated since 5.7.0 — pass db_manager (the "
            "Pyarchinit_db_management instance) instead. The Path "
            "argument will continue to work via this shim but will "
            "be removed in a future release. See "
            "docs/superpowers/specs/2026-05-10-postgres-compat-design.md",
            DeprecationWarning,
            stacklevel=3,
        )
        return DbHandle.from_path(arg)

    if isinstance(arg, str):
        if arg.startswith("sqlite:") or arg.startswith("postgresql"):
            engine = create_engine(arg)
            return DbHandle.from_engine(engine, arg)
        raise UnsupportedBackendError(
            f"unrecognised conn string dialect: {arg!r} "
            f"(expected 'sqlite://...' or 'postgresql://...')"
        )

    if isinstance(arg, Engine):
        # Best-effort conn_str reconstruction from engine URL
        return DbHandle.from_engine(arg, str(arg.url))

    # DbManager duck-typing: has .engine attribute (SQLAlchemy Engine)
    # and either .conn_str string or default to engine URL string
    if hasattr(arg, "engine") and isinstance(arg.engine, Engine):
        conn_str = getattr(arg, "conn_str", None) or str(arg.engine.url)
        return DbHandle.from_engine(arg.engine, conn_str)

    raise DbHandleError(
        f"cannot resolve db_handle from {type(arg).__name__}: {arg!r} "
        f"(expected Path, str, DbManager, Engine, or DbHandle)"
    )
```

- [ ] **Step 2: Run to verify all 7 new tests pass**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_db_handle_shim.py -v 2>&1 | tail -15
```

Expected: 10 PASSED (3 from Group A + 7 new).

- [ ] **Step 3: Full suite + AC-2**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: `244 passed, 3 skipped` (237 + 7) for full suite; AC-2 PASS.

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/sync/_db_handle.py \
        tests/sync/test_db_handle_shim.py
git commit -m "feat(pg-compat/B): _resolve_db_handle shim — 5 input types + DeprecationWarning

The shim accepts:
- Path: SQLite file path (emits DeprecationWarning per spec §3.1
  to nudge callers toward db_manager. Continues to work for the
  full lifetime of PG-A/B/C/D.)
- str: SQLAlchemy conn string ('sqlite://' or 'postgresql://')
- DbManager: pyarchinit Pyarchinit_db_management (uses .engine)
- Engine: SQLAlchemy Engine
- DbHandle: idempotent passthrough

UnsupportedBackendError raised for unrecognised dialects (mysql,
oracle, ...). DbHandleError for objects that don't match any branch.

7 new unit tests: 5 input-type paths + 1 deprecation check + 1
unsupported-backend error.

237 → 244 passed, 3 skipped. AC-2 byte-identical preserved."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group C — `_columns_of` dialect-aware introspection

### Task C.1: TDD — write failing test (SQLite path only — PG path tested in Group D)

**Files:**
- Modify: `tests/sync/test_db_handle_shim.py` (append 1 test)

- [ ] **Step 1: Append the SQLite test**

```python
# Append to tests/sync/test_db_handle_shim.py


def test_columns_of_sqlite(tmp_path):
    """_columns_of() returns column names from SQLite via PRAGMA."""
    from modules.s3dgraphy.sync._db_handle import _columns_of
    from sqlalchemy import create_engine, text
    p = tmp_path / "x.sqlite"
    engine = create_engine(f"sqlite:///{p}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE foo (id INTEGER PRIMARY KEY, "
            "name TEXT NOT NULL, node_uuid TEXT)"
        ))
    cols = _columns_of(engine, "foo")
    assert cols == {"id", "name", "node_uuid"}


def test_columns_of_returns_empty_for_missing_table(tmp_path):
    """_columns_of() on a non-existent table returns empty set (not raise)."""
    from modules.s3dgraphy.sync._db_handle import _columns_of
    from sqlalchemy import create_engine
    p = tmp_path / "y.sqlite"
    engine = create_engine(f"sqlite:///{p}")
    cols = _columns_of(engine, "nonexistent_table")
    assert cols == set()
```

- [ ] **Step 2: Run to verify both fail**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_db_handle_shim.py::test_columns_of_sqlite tests/sync/test_db_handle_shim.py::test_columns_of_returns_empty_for_missing_table -v
```

Expected: 2 FAILed — `_columns_of` not defined.

### Task C.2: Implement `_columns_of`

**Files:**
- Modify: `modules/s3dgraphy/sync/_db_handle.py` (append helper)

- [ ] **Step 1: Append `_columns_of` to the module**

```python
# Append to modules/s3dgraphy/sync/_db_handle.py


def _columns_of(engine: Engine, table: str) -> set[str]:
    """Backend-agnostic column-name introspection.

    Dispatches on engine.dialect.name:
      - sqlite → PRAGMA table_info(table)
      - postgresql → information_schema.columns
      - other → uses SQLAlchemy reflection as fallback

    Returns an empty set if the table does not exist (does not raise).
    """
    dialect = engine.dialect.name
    if dialect == "sqlite":
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(f"PRAGMA table_info({table})")
                ).fetchall()
                return {r[1] for r in rows}
        except Exception:
            return set()
    if dialect == "postgresql":
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = :t "
                        "AND table_schema = current_schema()"
                    ),
                    {"t": table},
                ).fetchall()
                return {r[0] for r in rows}
        except Exception:
            return set()
    # Other dialects: reflection fallback
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return {col["name"] for col in inspector.get_columns(table)}
    except Exception:
        return set()
```

- [ ] **Step 2: Run to verify both pass**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_db_handle_shim.py -v 2>&1 | tail -15
```

Expected: 12 PASSED (10 from B + 2 new).

- [ ] **Step 3: Full suite + AC-2**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: `246 passed, 3 skipped` (244 + 2) for full suite; AC-2 PASS.

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/sync/_db_handle.py \
        tests/sync/test_db_handle_shim.py
git commit -m "feat(pg-compat/C): _columns_of() dialect-aware introspection

PG-compat foundation step 3: replace the SQLite-specific
'PRAGMA table_info(t)' introspection used by GraphIngestor._verify_schema
with a backend-aware helper that dispatches on engine.dialect.name.

- sqlite → PRAGMA table_info(t) (existing behaviour preserved)
- postgresql → information_schema.columns WHERE table_name=:t AND
  table_schema=current_schema()
- other → SQLAlchemy reflection fallback (Inspector.get_columns)

Returns empty set on missing tables (does not raise) — caller
distinguishes 'no table' from 'no node_uuid column' via further
membership check.

2 new unit tests: SQLite happy path + missing-table-returns-empty.
PG path tested in Group D via test_pg_smoke.py.

244 → 246 passed. AC-2 preserved."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group D — `conftest_pg.py` + smoke

### Task D.1: Create `conftest_pg.py` with fixtures + schema bootstrap

**Files:**
- Create: `tests/sync/conftest_pg.py`

- [ ] **Step 1: Write the fixture file**

```python
# tests/sync/conftest_pg.py
"""PG-Compat Foundation: PostgreSQL test fixtures.

Shared fixtures used by every PG-aware test in tests/sync/. All
fixtures skip cleanly when PG is unreachable at localhost:5433, so
CI runs without a local PG see no failures.

Setup expected (USER pre-creates):
    psql -h localhost -p 5433 -U postgres \\
        -c "CREATE DATABASE pyarchinit_test_pg"

The pg_engine fixture creates the schema on first connection.
Subsequent test runs reuse it; clean_pg truncates between tests.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


PG_CONN_STR = (
    "postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg"
)


def _apply_pyarchinit_schema(engine: Engine) -> None:
    """Apply minimal pyarchinit DDL to a PG database for testing.

    Foundation milestone: only us_table, site_table, periodizzazione_table
    with the columns the bridge actually reads/writes. Future PG-A/B/C
    milestones may extend this as needed.

    Idempotent: uses CREATE TABLE IF NOT EXISTS.
    """
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS us_table (
                id_us SERIAL PRIMARY KEY,
                sito TEXT,
                area TEXT,
                us TEXT,
                d_stratigrafica TEXT,
                d_interpretativa TEXT,
                rapporti TEXT,
                periodo_iniziale TEXT,
                fase_iniziale TEXT,
                periodo_finale TEXT,
                fase_finale TEXT,
                struttura TEXT,
                attivita TEXT,
                settore TEXT,
                ambient TEXT,
                saggio TEXT,
                quad_par TEXT,
                unita_tipo TEXT DEFAULT 'US',
                node_uuid TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS site_table (
                id_sito SERIAL PRIMARY KEY,
                sito TEXT UNIQUE,
                nazione TEXT,
                regione TEXT,
                provincia TEXT,
                comune TEXT,
                descrizione TEXT,
                node_uuid TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS periodizzazione_table (
                id_perfas SERIAL PRIMARY KEY,
                sito TEXT,
                periodo INTEGER,
                fase TEXT,
                cron_iniziale INTEGER,
                cron_finale INTEGER,
                descrizione TEXT,
                datazione_estesa TEXT,
                node_uuid TEXT,
                CONSTRAINT pg_periodizzazione_unico UNIQUE (sito, periodo, fase)
            )
        """))


@pytest.fixture(scope="session")
def pg_engine():
    """Session-scoped PG engine. Skip cleanly if PG unreachable."""
    try:
        engine = create_engine(PG_CONN_STR)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(
            f"PG not available at localhost:5433 ({type(e).__name__}: {e})"
        )
    _apply_pyarchinit_schema(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def clean_pg(pg_engine):
    """Truncate all stratigraphic tables before each test.

    Provides isolation between tests without paying schema-creation
    cost (which is amortised by the session-scoped pg_engine).
    """
    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))
    yield pg_engine
```

- [ ] **Step 2: Verify the file imports without errors**

Run:
```bash
PYTHONPATH="$PWD" python -c "
import sys; sys.path.insert(0, 'tests/sync')
import conftest_pg
print('conftest_pg imports OK')
print('PG_CONN_STR:', conftest_pg.PG_CONN_STR)
"
```

Expected: `conftest_pg imports OK`.

### Task D.2: TDD — smoke test that uses pg_engine fixture

**Files:**
- Create: `tests/sync/test_pg_smoke.py`

- [ ] **Step 1: Write the smoke test**

```python
# tests/sync/test_pg_smoke.py
"""PG-Compat Foundation: smoke test for the pg_engine fixture.

Verifies:
  - pg_engine fixture connects (or skips cleanly if PG offline)
  - Schema bootstrap created the expected tables
  - _columns_of() works on PG via information_schema dispatch path

Skipped cleanly when PG is unreachable. CI without a local PG
sees no failures.
"""
from __future__ import annotations

import pytest


def test_pg_smoke_columns_of_us_table(pg_engine):
    """pg_engine connects + schema bootstrap created us_table +
    _columns_of() returns the expected columns via information_schema."""
    from modules.s3dgraphy.sync._db_handle import _columns_of
    cols = _columns_of(pg_engine, "us_table")
    # Foundation schema declares: id_us, sito, area, us, d_stratigrafica,
    # d_interpretativa, rapporti, periodo_iniziale, fase_iniziale,
    # periodo_finale, fase_finale, struttura, attivita, settore,
    # ambient, saggio, quad_par, unita_tipo, node_uuid
    expected = {
        "id_us", "sito", "area", "us", "d_stratigrafica",
        "d_interpretativa", "rapporti", "periodo_iniziale",
        "fase_iniziale", "periodo_finale", "fase_finale",
        "struttura", "attivita", "settore", "ambient", "saggio",
        "quad_par", "unita_tipo", "node_uuid",
    }
    assert cols == expected, (
        f"PG us_table columns mismatch.\n"
        f"  Expected: {sorted(expected)}\n"
        f"  Got:      {sorted(cols)}"
    )
```

- [ ] **Step 2: Run the smoke test**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_pg_smoke.py -v 2>&1 | tail -10
```

Expected (one of two outcomes):
- PG online + reachable: `1 passed`
- PG offline: `1 skipped` with reason `"PG not available at localhost:5433 (...)"`. **Both are acceptable.**

If PG is online but the test FAILS with column mismatch, the schema-bootstrap CREATE TABLE statements in `conftest_pg.py` need adjustment.

- [ ] **Step 3: Full suite + AC-2**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected:
- PG online: `247 passed, 3 skipped`
- PG offline: `246 passed, 4 skipped`
- AC-2 PASS in both cases.

- [ ] **Step 4: Commit**

```bash
git add tests/sync/conftest_pg.py tests/sync/test_pg_smoke.py
git commit -m "test(pg-compat/D): conftest_pg.py + pg_smoke fixture machinery

PG-compat foundation step 4: introduce the test infrastructure used
by every future PG-aware test (PG-A migration, PG-B export, PG-C
import, PG-D paradata).

- conftest_pg.py: pg_engine session fixture + clean_pg function
  fixture + _apply_pyarchinit_schema bootstrap. Uses
  postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg.
  Skips cleanly via pytest.skip() when PG is unreachable, so CI
  runs without a local PG see no failures.
- test_pg_smoke.py: 1 test verifies the fixture chain end-to-end —
  pg_engine connects, schema is present, _columns_of() returns the
  expected 19 us_table columns via the PG information_schema branch.

Schema bootstrap is intentionally minimal (us_table + site_table +
periodizzazione_table with the columns the bridge reads/writes).
Future milestones may extend if needed.

246 → 247 passed (PG online) or 246 + 1 skipped (PG offline).
AC-2 byte-identical preserved."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group E — Public API exports + requirements + version bump

### Task E.1: Re-export `DbHandle` from `__init__.py`

**Files:**
- Modify: `modules/s3dgraphy/sync/__init__.py`

- [ ] **Step 1: Read existing `__init__.py`**

Run:
```bash
cat modules/s3dgraphy/sync/__init__.py
```

Note the existing `__all__` block (currently exports `VocabProviderCore`, `EdgeType`, etc.).

- [ ] **Step 2: Edit to add `DbHandle` re-export**

Find the existing `from .vocab_provider_core import VocabProviderCore` line and add an import for `DbHandle` after the existing imports. Find the existing `__all__ = [...]` list and add `"DbHandle"` to it.

```python
# Add this import after existing imports
from ._db_handle import DbHandle, DbHandleError, UnsupportedBackendError, PgConnectionError

# Add these to __all__
__all__ = [
    # ... existing entries ...
    "DbHandle",
    "DbHandleError",
    "UnsupportedBackendError",
    "PgConnectionError",
]
```

(The exact insertion uses the Edit tool with the existing `__all__` block as `old_string`.)

- [ ] **Step 3: Verify the import works**

Run:
```bash
PYTHONPATH="$PWD" python -c "
import sys; sys.path.insert(0, 'tests/sync')
import conftest
from modules.s3dgraphy.sync import DbHandle, DbHandleError
print('DbHandle:', DbHandle)
print('DbHandleError:', DbHandleError)
"
```

Expected: prints class objects, no error.

### Task E.2: Add `psycopg2-binary` to requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Inspect current requirements**

Run:
```bash
grep -nE "psycopg2|sqlalchemy|^# Core DB" requirements.txt
```

Note the line numbers around the "Core DB packages" comment.

- [ ] **Step 2: Add `psycopg2-binary` after the SQLAlchemy block**

Edit `requirements.txt` to insert (after the `GeoAlchemy2>=0.14.0` line):

```
# PostgreSQL driver — only needed at runtime when connecting to a PG backend
# Was implicit dep via SQLAlchemy + pyarchinit_db_manager; now explicit
# for the s3dgraphy bridge PG-compat refactor (5.6.2-alpha foundation).
psycopg2-binary>=2.9
```

- [ ] **Step 3: Verify pip can read the file**

Run:
```bash
python3 -c "
with open('requirements.txt') as f:
    lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
print(f'{len(lines)} requirement lines')
print('psycopg2-binary present:',
      any(l.startswith('psycopg2-binary') for l in lines))
"
```

Expected: `psycopg2-binary present: True`.

### Task E.3: Bump `metadata.txt` version

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.6.1-alpha` → `version=5.6.2-alpha`.

- [ ] **Step 2: Verify**

Run:
```bash
grep "^version=" metadata.txt
```

Expected: `version=5.6.2-alpha`.

- [ ] **Step 3: Commit Group E together**

```bash
git add modules/s3dgraphy/sync/__init__.py \
        requirements.txt \
        metadata.txt
git commit -m "release(pg-compat/E): public API + requirements + version bump 5.6.2-alpha

Foundation step 5: expose DbHandle and 3 new exceptions via the
public sync.__init__ namespace for callers in PG-A through PG-D
milestones. Add psycopg2-binary>=2.9 to requirements.txt — was
already implicit via SQLAlchemy + pyarchinit_db_manager but now
explicit for the bridge layer.

Bump version 5.6.1-alpha → 5.6.2-alpha. This is the foundation
release: machinery is in place, no caller is using it yet. PG-A
through PG-D will progressively flip call sites in subsequent
tags 5.7.0/.1/.2/.3."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group F — Docs + tag + push + memory

### Task F.1: Dev-log entry

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Insert a new section at the top**

Read the current file:

```bash
head -30 docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md
```

Locate the existing topmost section (likely "Phase 2 — AI07 LocationNodeGroup migration"). Use Edit to insert BEFORE that section:

```markdown
## Phase 3 — PG Compat Foundation (5.6.2-alpha)

**Tag:** `phase3-pgcompat-shim-5.6.2-alpha`
**Date:** 2026-05-10
**Spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md`
**Plan:** `docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md`

### What shipped

- `DbHandle` frozen dataclass + factory classmethods (`from_path`,
  `from_engine`)
- `_resolve_db_handle()` shim accepting Path | str | DbManager |
  Engine | DbHandle, with DeprecationWarning for Path callers
- `_columns_of()` backend-agnostic introspection (sqlite PRAGMA →
  postgresql information_schema → SQLAlchemy reflection fallback)
- 3 new exceptions: `DbHandleError`, `UnsupportedBackendError`,
  `PgConnectionError` (all subclass of existing `GraphSyncError`)
- `tests/sync/conftest_pg.py` — pg_engine session fixture +
  clean_pg + schema bootstrap
- `tests/sync/test_pg_smoke.py` — 1 smoke test verifying the
  fixture chain
- `psycopg2-binary>=2.9` added to requirements.txt

### Tests

- 12 new unit tests in `test_db_handle_shim.py` (5 input types +
  deprecation warning + unsupported backend + 2 columns_of)
- 1 PG smoke (skipped cleanly when PG offline)
- Final count: 246 passed, 3 skipped (PG offline) or 247 passed,
  3 skipped (PG online)
- AC-2 byte-identical baseline preserved throughout

### Known follow-ups (later milestones)

- **PG-A** (5.7.0-alpha): Phase 1 node_uuid backfill works on PG
- **PG-B** (5.7.1-alpha): Projector + GraphMLWriter read from PG
- **PG-C** (5.7.2-alpha): Ingestor writes to PG with atomic
  transactions
- **PG-D** (5.7.3-alpha): ParadataStore + GroupStore workspace
  dir on PG
- **Consolidation** (5.7.4-alpha): polish, deprecation cleanup

```

### Task F.2: CHANGELOG bilingual entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Prepend the bilingual section**

Read the current file:

```bash
head -10 dev_logs/CHANGELOG.md
```

Locate the existing topmost `## [5.6.1-alpha]` section. Use Edit to insert BEFORE that:

```markdown
## [5.6.2-alpha] - 2026-05-10

### Italiano

**Foundation per PostgreSQL compat — machinery only, nessun caller cambiato.**

Primo step della Phase 3 (PG-compat refactor del bridge s3dgraphy). Rilascia l'infrastruttura `DbHandle` + shim resolver + dialect-aware introspection senza modificare alcun call site di produzione. Tutti i 234 test SQLite esistenti restano verdi.

- **`DbHandle` dataclass**: wrapper immutabile attorno a un `Engine` SQLAlchemy che traccia se il backend è PostgreSQL, conserva il path SQLite (quando applicabile) e la conn string originale per derivare slugs.
- **`_resolve_db_handle()` shim**: accetta 5 tipi di input (`Path`, `str`, `DbManager`, `Engine`, `DbHandle` passthrough) e li normalizza a `DbHandle`. I `Path` callers ricevono `DeprecationWarning` (continuano a funzionare per tutta la durata di PG-A/B/C/D).
- **`_columns_of()` introspection**: dispatch su `engine.dialect.name` — `PRAGMA table_info` su SQLite, `information_schema.columns` su PostgreSQL, fallback a SQLAlchemy reflection. Sostituisce il path SQLite-only in `GraphIngestor._verify_schema` (cambio caller deferito a PG-C).
- **3 nuove eccezioni**: `DbHandleError`, `UnsupportedBackendError`, `PgConnectionError` (tutte subclass di `GraphSyncError`).
- **Test infrastructure**: `tests/sync/conftest_pg.py` (`pg_engine` + `clean_pg` fixtures, schema bootstrap su `localhost:5433/pyarchinit_test_pg`) + `tests/sync/test_pg_smoke.py`. Skip puliti quando PG è offline — niente fallimenti CI senza PG locale.
- **`psycopg2-binary>=2.9`** aggiunto a `requirements.txt`.

13 nuovi test (12 unit + 1 PG smoke). Test count: 234 → 246 passed, 3 skipped (PG offline) o 247 (PG online). AC-2 byte-identical preservato.

### English

**Foundation for PostgreSQL compat — machinery only, no callers changed.**

First step of Phase 3 (PG-compat refactor of the s3dgraphy bridge). Lands the `DbHandle` + resolver shim + dialect-aware introspection infrastructure without changing any production call site. All 234 existing SQLite tests stay green.

- **`DbHandle` dataclass**: immutable wrapper around a SQLAlchemy `Engine` tracking whether the backend is PostgreSQL, the SQLite path (when applicable), and the original conn string for slug derivation.
- **`_resolve_db_handle()` shim**: accepts 5 input types (`Path`, `str`, `DbManager`, `Engine`, `DbHandle` passthrough) and normalises them to `DbHandle`. `Path` callers receive a `DeprecationWarning` (continue to work for the full lifetime of PG-A/B/C/D).
- **`_columns_of()` introspection**: dispatches on `engine.dialect.name` — `PRAGMA table_info` on SQLite, `information_schema.columns` on PostgreSQL, SQLAlchemy reflection fallback. Replaces the SQLite-only path in `GraphIngestor._verify_schema` (caller swap deferred to PG-C).
- **3 new exceptions**: `DbHandleError`, `UnsupportedBackendError`, `PgConnectionError` (all subclass of `GraphSyncError`).
- **Test infrastructure**: `tests/sync/conftest_pg.py` (`pg_engine` + `clean_pg` fixtures, schema bootstrap on `localhost:5433/pyarchinit_test_pg`) + `tests/sync/test_pg_smoke.py`. Skips cleanly when PG is offline — no CI failures without a local PG.
- **`psycopg2-binary>=2.9`** added to `requirements.txt`.

13 new tests (12 unit + 1 PG smoke). Test count: 234 → 246 passed, 3 skipped (PG offline) or 247 (PG online). AC-2 byte-identical preserved.

---

```

### Task F.3: Commit docs + final verification

**Files:** none (commit only)

- [ ] **Step 1: Commit dev-log + CHANGELOG**

```bash
git add docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "docs(pg-compat/F): dev-log + bilingual CHANGELOG for 5.6.2-alpha

Foundation milestone documentation. Plan reference at
docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md.

Spec reference at
docs/superpowers/specs/2026-05-10-postgres-compat-design.md."
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

- [ ] **Step 2: Final verification**

Run:
```bash
git log --oneline -10
git log b569bd51..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 7 new commits since `9355bed1`: A.2, B.2, C.2, D.2, E (combined), F.3
- Co-Authored-By count: `0`
- Total: `246 passed, 3 skipped` (PG offline) or `247 passed, 3 skipped` (PG online)
- AC-2: PASS
- Version: `5.6.2-alpha`

### Task F.4: Tag + push

**Files:** none (git operation)

- [ ] **Step 1: Tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a phase3-pgcompat-shim-5.6.2-alpha \
  -m "PG-compat Foundation — DbHandle + resolver shim + dialect introspection

Foundation milestone (machinery only, no caller changes):

- DbHandle frozen dataclass + factory methods (from_path, from_engine)
- _resolve_db_handle() shim accepting Path | str | DbManager | Engine
  | DbHandle, with DeprecationWarning for Path
- _columns_of() backend-agnostic column introspection (sqlite PRAGMA →
  postgresql information_schema → SQLAlchemy reflection fallback)
- 3 new exceptions: DbHandleError, UnsupportedBackendError,
  PgConnectionError (subclass of GraphSyncError)
- conftest_pg.py + test_pg_smoke.py — PG fixture machinery, skips
  cleanly when PG offline at localhost:5433

Spec: docs/superpowers/specs/2026-05-10-postgres-compat-design.md
Plan: docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md
Predecessor: phase2-ai07-hotfix-5.6.1-alpha (026199c2)

13 new tests (12 unit + 1 PG smoke). Total 246 passed, 3 skipped
(PG offline) or 247 (PG online). AC-2 byte-identical preserved."
git push origin phase3-pgcompat-shim-5.6.2-alpha
git push origin Stratigraph_00001
```

Expected: tag created and pushed; branch pushed.

- [ ] **Step 2: Verify GitHub remote**

Run:
```bash
git ls-remote --tags origin | grep "phase3-pgcompat-shim-5.6.2-alpha"
```

Expected: tag listed with the correct commit SHA.

### Task F.5: Memory snapshot

**Files:**
- Create: `~/.claude/projects/.../memory/project_pg_compat_progress.md`

- [ ] **Step 1: Write the progress note**

Path:
```
/Users/enzo/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/project_pg_compat_progress.md
```

Body:
```markdown
---
name: PG-Compat refactor — Foundation shipped 2026-05-10
description: Phase 3 PostgreSQL compatibility refactor of the s3dgraphy bridge. Foundation milestone (5.6.2-alpha) shipped — machinery in place, no callers flipped yet. PG-A/B/C/D and consolidation pending.
type: project
---

## SHIPPED Foundation (5.6.2-alpha) 2026-05-10

**Tag:** `phase3-pgcompat-shim-5.6.2-alpha`
**Spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md`
**Plan:** `docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md`

What landed:
- `DbHandle` dataclass + 3 exceptions in `modules/s3dgraphy/sync/_db_handle.py`
- `_resolve_db_handle()` shim accepting 5 input types
- `_columns_of()` dialect-aware introspection
- `tests/sync/conftest_pg.py` PG fixture infrastructure
- 12 unit tests + 1 PG smoke (skips when PG offline)
- 234 → 246 passed, 3 skipped (PG offline) or 247 (PG online)
- AC-2 byte-identical preserved

NO production caller changed. Foundation introduces machinery only.

## PENDING milestones

| Milestone | Tag | When |
|---|---|---|
| PG-A | `phase3-pgcompat-a-migration-5.7.0-alpha` | TBD — brainstorm + plan after Foundation review |
| PG-B | `phase3-pgcompat-b-export-5.7.1-alpha` | After PG-A ships |
| PG-C | `phase3-pgcompat-c-import-5.7.2-alpha` | After PG-B ships |
| PG-D | `phase3-pgcompat-d-paradata-5.7.3-alpha` | After PG-C ships |
| Consolidation | `phase3-pgcompat-consolidation-5.7.4-alpha` | After PG-D ships |

Each milestone gets its own brainstorming + plan + subagent-driven implementation cycle, similar to AI04→AI05→AI06→AI07.

## How to apply

When user wants to start the next milestone:
- "PG-A" / "next milestone" / "brainstorming PG-A" → invoke
  `superpowers:brainstorming` with the spec section §4.2 as scope
- The Foundation `_db_handle.py` is the single source of truth for
  shim semantics; PG-A reuses without modification
- The conftest_pg.py PG fixture is also reused as-is

The branchpoint is `Stratigraph_00001` HEAD post-Foundation.
```

- [ ] **Step 2: Update MEMORY.md index**

File: `/Users/enzo/.claude/projects/.../memory/MEMORY.md`. Find the existing AI07 line and add a new line below for PG-compat:

```markdown
- [PG-Compat Foundation shipped](project_pg_compat_progress.md) — **CURRENT STATE 2026-05-10**. Tag `phase3-pgcompat-shim-5.6.2-alpha` shipped: `DbHandle` + resolver shim + `_columns_of()` dialect introspection + PG fixture infrastructure. 246 passed, 3 skipped. PG-A/B/C/D and consolidation pending — each gets own brainstorm + plan cycle.
```

- [ ] **Step 3: Final report**

Once all 5 tasks of Group F complete, report:

- **Status:** DONE
- 7 new commits since `9355bed1`
- Tag `phase3-pgcompat-shim-5.6.2-alpha` pushed to origin
- Test count: 246 passed (PG offline) / 247 passed (PG online), 3 skipped, AC-2 preserved
- Zero `Co-Authored-By: Claude` trailers
- Memory note created at `project_pg_compat_progress.md`, MEMORY.md index updated

---

## Self-Review

This plan covers every Foundation requirement in the spec §4.1:

| Spec §4.1 entry | Plan task |
|---|---|
| `_db_handle.py` (NEW) — DbHandle + exceptions + resolver + columns_of | Group A (dataclass + exceptions) + Group B (resolver) + Group C (columns_of) |
| `__init__.py` re-export | Group E Task E.1 |
| `test_db_handle_shim.py` (NEW) | Group A.1 + B.1 + C.1 (TDD test files written before each impl) |
| `conftest_pg.py` (NEW) | Group D Task D.1 |
| `requirements.txt` psycopg2-binary | Group E Task E.2 |
| `metadata.txt` 5.6.1 → 5.6.2 | Group E Task E.3 |
| CHANGELOG bilingual | Group F Task F.2 |

Plus dev-log entry (F.1), tag + push (F.4), memory snapshot (F.5) — covered.

Type consistency: `DbHandle` (dataclass), `_resolve_db_handle` (function), `_columns_of` (function), `DbHandleError` / `UnsupportedBackendError` / `PgConnectionError` (exceptions), `pg_engine` / `clean_pg` (fixtures), `_apply_pyarchinit_schema` (helper) — all consistent across Groups.

No placeholders. Every step has either runnable code, exact commands, or specific file edits.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per Group, review between tasks, fast iteration, two-stage review (spec compliance + code quality)
2. **Inline Execution** — execute tasks in this session using `executing-plans`, batch execution with checkpoints for user review

**Which approach?**

If **Subagent-Driven** chosen, recommended subagent batching:
- Group 0 (3 tasks) → no subagent — pure git + USER action for PG DB pre-creation
- Group A (1 implementation task) → 1 subagent — TDD cycle for dataclass
- Group B (1 implementation task) → 1 subagent — TDD cycle for resolver shim
- Group C (1 implementation task) → 1 subagent — TDD cycle for columns_of
- Group D (1 task = fixture + smoke) → 1 subagent — fixture infrastructure
- Group E (3 tasks combined into 1 commit) → 1 subagent — public API + requirements + version
- Group F Tasks F.1–F.3 → 1 subagent — docs + final verification
- Group F Task F.4 → 1 subagent — tag + push (separate to gate user approval before tagging)
- Group F Task F.5 → no subagent — memory update by controller

If **Inline Execution** chosen, batch execution with checkpoint after each Group.
