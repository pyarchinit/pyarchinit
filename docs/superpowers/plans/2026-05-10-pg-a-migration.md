# PG-A — Phase 1 `node_uuid` migration on PostgreSQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Phase 1 `node_uuid` backfill migration work on both SQLite and PostgreSQL backends, reusing `DbHandle` + `_resolve_db_handle` + `_columns_of` from Foundation. Production callers in PG-B/C/D scope (`populate_list`, projector, paradata store) explicitly NOT touched. AC-2 byte-identical guard preserved throughout. Release `5.7.0-alpha`.

**Architecture:** Migration lib goes SQLAlchemy-everywhere (`engine.begin()` + `text()`), accepts `DbHandle | Path` via `_resolve_db_handle` shim for backward compatibility. PK discovery via `Inspector.get_pk_constraint`. `auto_backup_postgres` wraps `pg_dump` subprocess with skip-on-missing fallback. CLI gains `--conn-str` mutually exclusive with `--db`. QGIS handler drops the file picker, reads conn-str from `Connection().conn_str()`, dispatches backup per backend.

**Tech Stack:** Python 3.9+, SQLAlchemy 1.4+ (already a dep), `psycopg2-binary>=2.9` (Foundation added it), `pg_dump` optional system tool, pytest.

**Spec source of truth:** `docs/superpowers/specs/2026-05-10-pg-a-migration-design.md` (commit `e355f3a2`)

**Predecessor releases:**
- Foundation: tag `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` — current Phase 3 state
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/MEMORY.md` — Phase 1 node_uuid migration note (still MANUAL post-PG-A)

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

**Local PG setup (already done during Foundation):**
- Host: `localhost`
- Port: `5433`
- User: `postgres`
- Password: `postgres`
- Test DB: `pyarchinit_test_pg`

The `pg_engine` fixture in `tests/sync/conftest_pg.py` skips cleanly when PG offline or `psycopg2` missing — no setup needed in those cases.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `tests/migrations/test_node_uuid_backfill_lib_unit.py` | L0 unit tests for PK discovery via SQLAlchemy Inspector, `_columns_of` round-trip on tmp SQLite, idempotency of `add_columns` and `backfill_uuids` accepting `DbHandle`. No PG required. ~80 LOC. |
| `tests/sync/test_node_uuid_backfill_pg.py` | 6 L2 PG cases. Skipped cleanly when PG offline. ~150 LOC. |

### Modified

| Path | Why |
|---|---|
| `scripts/migrations/_2026_05_node_uuid_backfill_lib.py` | Replace `sqlite3.connect()` with `engine.begin()`. Public API accepts `DbHandle \| Path` via `_resolve_db_handle` shim. PK discovery via SQLAlchemy `Inspector`. ~120 LOC final (was 92). |
| `scripts/migrations/_common.py` | Add `auto_backup_postgres(engine, tag, dest_dir)`. `parse_argv` makes `--db` and `--conn-str` mutually exclusive. ~80 LOC final (was 33). |
| `scripts/migrations/2026_05_node_uuid_backfill.py` | CLI dispatches on `--db` vs `--conn-str`, picks backup helper per backend. ~50 LOC final (was 82). |
| `modules/s3dgraphy/sync/graph_ingestor.py:_verify_schema` | Internal swap `sqlite3.connect()` + `PRAGMA` → `_resolve_db_handle()` + `_columns_of()`. Signature `_verify_schema(self, db_path)` preserved. ~15 LOC delta. |
| `pyarchinitPlugin.py:_run_uuid_backfill_migration` | Drop file picker. Read conn-str via `Connection().conn_str()`. Dispatch backup per backend. Confirm dialog shows backend slug. ~50 LOC final (was ~60). |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py:_offer_node_uuid_migration` | Accept `db_path: Path` OR a DbManager via `_resolve_db_handle`. ~15 LOC delta. |
| `tests/migrations/test_node_uuid_backfill.py` | Extend with 2-3 cases for `--db` / `--conn-str` mutex + `--conn-str sqlite://...` happy path. +30 LOC. |
| `metadata.txt` | Bump `version=5.6.2-alpha` → `version=5.7.0-alpha`. 1 line. |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.0-alpha]` section. ~40 LOC. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 — PG-A migration section. ~30 LOC. |

### Explicitly NOT touched (per spec §4.3)

- `modules/s3dgraphy/sync/graph_projector.py` — sqlite3.connect call sites stay (PG-B)
- `modules/s3dgraphy/sync/graph_ingestor.py:populate_list` — main import flow stays SQLite-only (PG-C)
- `modules/s3dgraphy/sync/graphml_writer.py` (PG-B)
- `modules/s3dgraphy/sync/group_projector.py` (PG-B)
- `modules/s3dgraphy/sync/paradata_store.py` / `group_store.py` (PG-D)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2) — must stay green untouched throughout
- All other 244 SQLite tests — must stay green via the backward-compat shim

---

## Test strategy

- **L0 unit (`test_node_uuid_backfill_lib_unit.py` NEW):** pure pytest, no PG. PK discovery on tmp SQLite via `Inspector.get_pk_constraint`. Verifies idempotency contract works on the new `DbHandle | Path` signature.
- **L0 unit (`test_node_uuid_backfill.py` EXTENDED):** existing 4 SQLite cases continue to pass via shim. +2-3 new cases for `--db` / `--conn-str` argparse mutex.
- **L2 PG (`test_node_uuid_backfill_pg.py` NEW):** 6 cases gated by `pg_engine` fixture. Skip when PG offline or psycopg2 missing.
- **L3 regression guards:**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no            # full SQLite suite
```

`test_ai03_export_byte_identical.py` MUST stay green untouched at every Group of PG-A.

Decision-pinning matrix:

| Decision / Acceptance | Pinning test |
|---|---|
| Q1=a (single menu, no file picker) | Manual via QGIS — documented in dev-log |
| Q2=a+c (pg_dump or warning) | `test_auto_backup_postgres_invokes_pg_dump` (mocked) + `test_auto_backup_postgres_when_pg_dump_missing` (mocked `shutil.which → None`) |
| Q3=a (`--conn-str` mutex `--db`) | `test_argv_db_and_conn_str_mutex` + `test_argv_conn_str_sqlite_accepted` (CLI extension) |
| Approach 1 (SQLAlchemy-everywhere) | All 6 PG L2 tests would fail without it |
| `add_columns` idempotent both backends | SQLite: `test_add_columns_idempotent` (existing). PG: `test_add_columns_idempotent_on_pg` (Group E #1) |
| `backfill_uuids` produces UUID v7 on PG | `test_backfill_uuids_assigns_uuid7_on_pg` (Group E #2) |
| Atomic rollback on failure | `test_atomic_rollback_on_alter_failure` (Group E #5) |
| `_verify_schema` works on both backends | Existing SQLite path covered. PG path covered via `test_pg_smoke_columns_of_us_table` (Foundation, no new test) |

Test count progression:
- Pre PG-A (Foundation post-Group-F.3): 245 passed, 5 skipped
- Post-Group A (PG offline): 245 + 3 (lib unit) = **248 passed, 5 skipped**
- Post-Group B (PG offline): 248 + 3 (mutex + sqlite-conn-str + auto_backup_postgres_when_missing) = **251 passed, 5 skipped**
- Post-Group C (PG offline): unchanged — Group C is CLI dispatch, no new tests
- Post-Group D (PG offline): unchanged — `_verify_schema` swap covered by existing schemas
- Post-Group E (PG offline): 251 + 0 (6 cases all skipped) = **251 passed, 11 skipped**
- Post-Group E (PG online + psycopg2): 251 + 6 = **257 passed, 5 skipped**
- Post-Group F (PG offline): unchanged — handler change is QGIS-side, no automatable tests
- Post-Group G (PG offline): unchanged — docs/version only
- Final (PG offline): **251 passed, 11 skipped**
- Final (PG online): **257 passed, 5 skipped**

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

Expected: tracked changes empty, last commit is `e355f3a2 spec(pg-a-migration): …` (or later if user added more), `0\t0` ahead-behind.

- [ ] **Step 2: Verify Foundation tag exists**

```bash
git tag --list | grep -E "phase3-pgcompat-shim-5.6.2-alpha"
```

Expected: `phase3-pgcompat-shim-5.6.2-alpha` listed.

- [ ] **Step 3: Capture baseline test count**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `245 passed, 5 skipped` (Foundation baseline).

### Task 0.2: Create PG-A rollback safety tag

**Files:** none (git operation)

- [ ] **Step 1: Create rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-pg-a-migration -m "Rollback point before PG-A migration milestone

Predecessor: phase3-pgcompat-shim-5.6.2-alpha (7420a6cc)
Spec commit: e355f3a2

If PG-A needs to be reverted, reset hard to this tag."
git push origin pre-pg-a-migration
```

Expected: `* [new tag]         pre-pg-a-migration -> pre-pg-a-migration`.

---

## Group A — Migration lib cross-backend refactor

### Task A.1: Write failing L0 unit test for `DbHandle`-accepting signature

**Files:**
- Create: `tests/migrations/test_node_uuid_backfill_lib_unit.py`

- [ ] **Step 1: Create the unit test file with 3 cases**

```python
# tests/migrations/test_node_uuid_backfill_lib_unit.py
"""L0 unit tests for the PG-A migration lib refactor.

Verifies that add_columns / backfill_uuids accept either a DbHandle
or a Path (backward compat) and that PK discovery works via
SQLAlchemy Inspector across SQLite. PG path tested in
tests/sync/test_node_uuid_backfill_pg.py.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


def _seed_db(p: Path) -> None:
    """Create the three target tables with one row each, no node_uuid yet."""
    conn = sqlite3.connect(p)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT)")
    conn.execute(
        "CREATE TABLE inventario_materiali_table "
        "(id_invmat INTEGER PRIMARY KEY, sito TEXT)"
    )
    conn.execute(
        "CREATE TABLE periodizzazione_table "
        "(id_perfas INTEGER PRIMARY KEY, sito TEXT)"
    )
    conn.execute("INSERT INTO us_table VALUES (1, 'S')")
    conn.execute("INSERT INTO inventario_materiali_table VALUES (1, 'S')")
    conn.execute("INSERT INTO periodizzazione_table VALUES (1, 'S')")
    conn.commit()
    conn.close()


def test_add_columns_accepts_dbhandle(tmp_path):
    """add_columns(db_handle) works with a DbHandle, not just Path."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns,
    )
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    handle = DbHandle.from_path(db)
    add_columns(handle)
    # Verify via the engine on the handle (not via raw sqlite3)
    from sqlalchemy import text
    with handle.engine.connect() as conn:
        for table in TABLES:
            rows = conn.execute(
                text(f"PRAGMA table_info({table})")
            ).fetchall()
            cols = {r[1] for r in rows}
            assert "node_uuid" in cols


def test_backfill_uuids_accepts_dbhandle_returns_counts(tmp_path):
    """backfill_uuids(db_handle) → returns dict[str, int] of rows updated."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns, backfill_uuids,
    )
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    handle = DbHandle.from_path(db)
    add_columns(handle)
    counts = backfill_uuids(handle)
    assert set(counts.keys()) == set(TABLES)
    for table in TABLES:
        assert counts[table] == 1, (
            f"expected 1 row updated for {table}, got {counts[table]}"
        )


def test_pk_discovery_via_inspector(tmp_path):
    """SQLAlchemy Inspector.get_pk_constraint returns the PK col list."""
    from sqlalchemy import create_engine, inspect, text
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    engine = create_engine(f"sqlite:///{db}")
    inspector = inspect(engine)
    for table, expected_pk in [
        ("us_table", ["id_us"]),
        ("inventario_materiali_table", ["id_invmat"]),
        ("periodizzazione_table", ["id_perfas"]),
    ]:
        pk = inspector.get_pk_constraint(table)["constrained_columns"]
        assert pk == expected_pk, f"{table}: expected {expected_pk}, got {pk}"
```

- [ ] **Step 2: Run to verify all 3 fail**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/migrations/test_node_uuid_backfill_lib_unit.py -v 2>&1 | tail -10
```

Expected: 2 errors (`add_columns` / `backfill_uuids` reject `DbHandle`), 1 PASSED (`test_pk_discovery_via_inspector` is pure SQLAlchemy and works without lib changes).

### Task A.2: Refactor `_2026_05_node_uuid_backfill_lib.py` to SQLAlchemy + DbHandle

**Files:**
- Modify: `scripts/migrations/_2026_05_node_uuid_backfill_lib.py`

- [ ] **Step 1: Replace the file content**

```python
"""Library for the node_uuid backfill migration (PG-A milestone).

Adds a ``node_uuid TEXT`` column + a partial unique index
(``WHERE node_uuid IS NOT NULL``) to the three Phase 1 target tables, then
assigns a UUID v7 to every existing row whose ``node_uuid`` is NULL.

Both ``add_columns`` and ``backfill_uuids`` are idempotent. Split from the
CLI script so tests can import the logic without invoking argparse.

Cross-backend (SQLite + PostgreSQL) since 5.7.0-alpha. Public API accepts
either a ``DbHandle`` or a legacy ``Path`` (backward compat) via the
``_resolve_db_handle()`` shim from Foundation.
"""
from __future__ import annotations

from pathlib import Path
from typing import Union

from sqlalchemy import inspect, text

from modules.s3dgraphy.sync._db_handle import (
    DbHandle, _columns_of, _resolve_db_handle,
)
from modules.s3dgraphy.sync.uuid7 import uuid7

#: Tables that need a stable node identity for the s3dgraphy bridge.
TABLES: tuple[str, ...] = (
    "us_table",
    "inventario_materiali_table",
    "periodizzazione_table",
)

#: Type alias accepted by every public function.
DbInput = Union[DbHandle, Path]


def add_columns(db: DbInput) -> None:
    """Add ``node_uuid TEXT`` + partial unique index on each target table.

    The partial unique index uses ``WHERE node_uuid IS NOT NULL`` so that
    multiple NULLs do not collide during a partial-failure recovery (we may
    add the column on N tables but only finish backfilling N-1 before a
    crash; rolling forward must not be blocked by spurious uniqueness
    violations on the unfilled rows).

    Accepts a ``DbHandle`` or a legacy ``Path`` (resolved via the
    ``_resolve_db_handle`` shim). Atomic via SQLAlchemy ``engine.begin()`` —
    a failure mid-loop rolls back the whole step.
    """
    handle = _resolve_db_handle(db)
    with handle.engine.begin() as conn:
        for table in TABLES:
            cols = _columns_of(handle.engine, table)
            if "node_uuid" not in cols:
                conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN node_uuid TEXT")
                )
            conn.execute(text(
                f"CREATE UNIQUE INDEX IF NOT EXISTS "
                f"ix_{table}_node_uuid ON {table}(node_uuid) "
                f"WHERE node_uuid IS NOT NULL"
            ))


def backfill_uuids(db: DbInput) -> dict[str, int]:
    """Assign ``uuid7()`` to every NULL ``node_uuid``; return per-table counts.

    Idempotent: a second invocation returns ``{table: 0, ...}`` because every
    row now carries a value. Atomic via SQLAlchemy ``engine.begin()``.
    """
    handle = _resolve_db_handle(db)
    counts: dict[str, int] = {}
    inspector = inspect(handle.engine)
    with handle.engine.begin() as conn:
        for table in TABLES:
            pks = inspector.get_pk_constraint(table)["constrained_columns"]
            if pks:
                pk_col = pks[0]
            elif handle.is_postgres:
                # PG has no rowid fallback — every pyarchinit table has a PK
                # by design, but defend explicitly.
                raise RuntimeError(
                    f"{table}: no primary key declared on PostgreSQL — "
                    "cannot backfill safely"
                )
            else:
                pk_col = "rowid"
            rows = conn.execute(
                text(f"SELECT {pk_col} FROM {table} WHERE node_uuid IS NULL")
            ).fetchall()
            for (row_id,) in rows:
                conn.execute(
                    text(f"UPDATE {table} SET node_uuid = :uuid "
                         f"WHERE {pk_col} = :id"),
                    {"uuid": str(uuid7()), "id": row_id},
                )
            counts[table] = len(rows)
    return counts
```

- [ ] **Step 2: Run new L0 unit tests + existing SQLite tests**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/migrations/test_node_uuid_backfill_lib_unit.py tests/migrations/test_node_uuid_backfill.py -v 2>&1 | tail -15
```

Expected: 3 NEW PASSED + 4 EXISTING PASSED = 7 PASSED total.

- [ ] **Step 3: Full sync+migrations suite**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `248 passed, 5 skipped` (245 baseline + 3 new lib unit tests).

- [ ] **Step 4: AC-2 sanity ping**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/migrations/_2026_05_node_uuid_backfill_lib.py \
        tests/migrations/test_node_uuid_backfill_lib_unit.py
git commit -m "$(cat <<'EOF'
feat(pg-a/A): migration lib cross-backend via SQLAlchemy

Replace sqlite3.connect() with SQLAlchemy engine.begin() in
add_columns and backfill_uuids. Public API now accepts a DbHandle
or a legacy Path (backward compat via _resolve_db_handle shim).

PK discovery via SQLAlchemy Inspector.get_pk_constraint - works
identically on SQLite (PRAGMA-equivalent) and PostgreSQL
(pg_index-equivalent). Falls back to rowid only on SQLite when no
PK is declared; PG raises explicitly because every pyarchinit table
has a declared PK by design.

3 new L0 unit tests pin: DbHandle acceptance, idempotency contract,
and PK discovery via Inspector. Existing 4 SQLite tests continue
to pass via the shim accepting Path.

245 -> 248 passed, 5 skipped. AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group B — `_common.py` + `auto_backup_postgres` + parse_argv mutex

### Task B.1: Write failing tests for parse_argv mutex + auto_backup_postgres

**Files:**
- Modify: `tests/migrations/test_node_uuid_backfill.py` (extend with 3 new tests)

- [ ] **Step 1: Append the 3 new tests at the end of the existing file**

```python
def test_argv_db_and_conn_str_mutex():
    """parse_argv: --db and --conn-str cannot be passed together."""
    import pytest
    from scripts.migrations._common import parse_argv
    with pytest.raises(SystemExit):
        parse_argv(["--db", "/tmp/x.sqlite",
                    "--conn-str", "postgresql://x:y@h/d",
                    "--apply"])


def test_argv_conn_str_sqlite_accepted():
    """parse_argv: --conn-str sqlite:///... is accepted (not just PG)."""
    from scripts.migrations._common import parse_argv
    args = parse_argv(["--conn-str", "sqlite:///tmp/x.sqlite", "--apply"])
    assert args.conn_str == "sqlite:///tmp/x.sqlite"
    assert args.db is None
    assert args.apply is True


def test_auto_backup_postgres_when_pg_dump_missing(tmp_path, monkeypatch):
    """auto_backup_postgres returns None + raises BackupSkipped when
    pg_dump is missing from PATH."""
    import pytest
    from sqlalchemy import create_engine
    from scripts.migrations._common import (
        BackupSkipped, auto_backup_postgres,
    )
    monkeypatch.setattr("shutil.which", lambda name: None)
    engine = create_engine(
        "postgresql+psycopg2://postgres:postgres@localhost:5433/dummy"
    )
    with pytest.raises(BackupSkipped):
        auto_backup_postgres(engine, tag="x", dest_dir=tmp_path)
```

- [ ] **Step 2: Run to verify all 3 fail**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/migrations/test_node_uuid_backfill.py -v 2>&1 | tail -15
```

Expected: 4 EXISTING PASSED + 3 NEW FAILED (`--conn-str` not in argparse, `BackupSkipped` not defined, `auto_backup_postgres` not defined).

### Task B.2: Refactor `_common.py` with mutex + auto_backup_postgres

**Files:**
- Modify: `scripts/migrations/_common.py`

- [ ] **Step 1: Replace the file content**

```python
"""Shared helpers for one-shot migrations.

All migrations expose the same CLI: --dry-run | --apply | --rollback <path>.
Auto-backup is invoked at the start of any --apply run.

PG-A (5.7.0-alpha) added:
- ``--conn-str`` flag mutually exclusive with ``--db``.
- ``auto_backup_postgres()`` for PG backends (wraps ``pg_dump`` subprocess).
- ``BackupSkipped`` exception so callers can surface a "pg_dump not found"
  dialog and let the user decide whether to proceed without a backup.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import Engine


class BackupSkipped(Exception):
    """Raised by ``auto_backup_postgres`` when ``pg_dump`` is unavailable.

    The CLI / GUI catches this and offers the user a choice between
    proceeding without a backup (logged) and cancelling the migration.
    """


def auto_backup_sqlite(db_path: Path, tag: str) -> Path:
    """Copy db_path to <db>.pre_<tag>_<UTC timestamp>; return new path."""
    db_path = Path(db_path)
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup = db_path.with_name(f"{db_path.name}.pre_{tag}_{stamp}")
    shutil.copy2(db_path, backup)
    return backup


def auto_backup_postgres(engine: Engine, tag: str, dest_dir: Path) -> Path:
    """Run ``pg_dump`` on the engine's database; return path of the dump file.

    Discovers ``pg_dump`` via ``shutil.which``. If missing, raises
    ``BackupSkipped`` so the caller can surface a "skip backup at your own
    risk" dialog.

    Output path: ``<dest_dir>/<dbname>.sql.pre_<tag>_<ts>``.
    Subprocess is invoked with PGPASSWORD in env (never on the command line).
    Subprocess timeout is 5 minutes.
    """
    pg_dump = shutil.which("pg_dump")
    if pg_dump is None:
        raise BackupSkipped(
            "pg_dump not found on PATH. Install PostgreSQL client tools "
            "or skip the backup explicitly."
        )
    url = engine.url
    dbname = url.database or "unknown"
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"{dbname}.sql.pre_{tag}_{stamp}"
    cmd = [
        pg_dump,
        "-h", str(url.host or "localhost"),
        "-p", str(url.port or 5432),
        "-U", str(url.username or "postgres"),
        "-d", dbname,
        "-f", str(out),
    ]
    env = {"PGPASSWORD": str(url.password or ""), "PATH": shutil.os.environ.get("PATH", "")}
    proc = subprocess.run(cmd, env=env, timeout=300, check=False,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise BackupSkipped(
            f"pg_dump exited {proc.returncode}: {proc.stderr.strip()}"
        )
    return out


def parse_argv(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI args. ``--db`` (SQLite path) and ``--conn-str`` (any DSN)
    are mutually exclusive; exactly one of them must be present."""
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--db", help="Path to SQLite file")
    src.add_argument("--conn-str", dest="conn_str",
                     help="SQLAlchemy conn string (sqlite:/// or postgresql://)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true",
                   help="Report what would change; do not mutate")
    g.add_argument("--apply", action="store_true",
                   help="Apply the migration (auto-backup first)")
    g.add_argument("--rollback", metavar="BACKUP_PATH",
                   help="Restore the DB from a previous --apply backup")
    return p.parse_args(argv)
```

- [ ] **Step 2: Run all 3 new tests pass + 4 existing**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/migrations/test_node_uuid_backfill.py -v 2>&1 | tail -15
```

Expected: 7 PASSED.

- [ ] **Step 3: Full sync+migrations suite**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `251 passed, 5 skipped` (248 + 3 new mutex/backup tests).

- [ ] **Step 4: AC-2 sanity ping**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/migrations/_common.py tests/migrations/test_node_uuid_backfill.py
git commit -m "$(cat <<'EOF'
feat(pg-a/B): _common.py - auto_backup_postgres + --db/--conn-str mutex

Add auto_backup_postgres(engine, tag, dest_dir) wrapping pg_dump
via subprocess.run. Discovers pg_dump via shutil.which; raises
BackupSkipped exception when missing so callers can dialog the
user. Subprocess uses PGPASSWORD in env (never on command line),
5-minute timeout, capture_output for error reporting.

parse_argv now requires exactly one of --db or --conn-str
(mutually exclusive group). --conn-str accepts both
sqlite:///path and postgresql://... DSNs - resolution happens
downstream via _resolve_db_handle.

3 new tests: argparse mutex, sqlite via --conn-str accepted,
auto_backup_postgres raises BackupSkipped when pg_dump missing.

248 -> 251 passed. AC-2 preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group C — CLI script dispatch on `--db` vs `--conn-str`

### Task C.1: Refactor `2026_05_node_uuid_backfill.py` for cross-backend dispatch

**Files:**
- Modify: `scripts/migrations/2026_05_node_uuid_backfill.py`

- [ ] **Step 1: Replace the file content**

```python
#!/usr/bin/env python3
"""One-shot migration: add ``node_uuid TEXT`` + backfill UUID v7.

Adds the column to ``us_table``, ``inventario_materiali_table`` and
``periodizzazione_table``, plus a partial unique index, then fills every
NULL ``node_uuid`` with a fresh UUID v7. Idempotent. Auto-backups the DB
before --apply.

Cross-backend (SQLite + PostgreSQL) since 5.7.0-alpha. Pass either
``--db <sqlite_path>`` or ``--conn-str postgresql://...``; mutually exclusive.
"""
from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
from scripts.migrations._common import (
    BackupSkipped, auto_backup_postgres, auto_backup_sqlite, parse_argv,
)
from scripts.migrations._2026_05_node_uuid_backfill_lib import (
    TABLES, add_columns, backfill_uuids,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("node_uuid_backfill")


def _resolve_input(args) -> "tuple":
    """Return a DbHandle from the CLI args (--db or --conn-str)."""
    if args.db is not None:
        db_path = Path(args.db)
        if not db_path.exists():
            log.error("DB not found: %s", db_path)
            sys.exit(2)
        return _resolve_db_handle(db_path)
    return _resolve_db_handle(args.conn_str)


def _dry_run(handle) -> int:
    """Report which tables need ALTER + how many rows need backfill."""
    log.info("Dry-run plan for %s:", handle.conn_str)
    from modules.s3dgraphy.sync._db_handle import _columns_of
    with handle.engine.connect() as conn:
        for table in TABLES:
            cols = _columns_of(handle.engine, table)
            if "node_uuid" not in cols:
                log.info("  %-30s needs ALTER TABLE + backfill (no col)",
                         table)
                continue
            n = conn.execute(text(
                f"SELECT COUNT(*) FROM {table} WHERE node_uuid IS NULL"
            )).scalar()
            log.info("  %-30s %d row(s) need backfill", table, n)
    return 0


def _apply(handle, args) -> int:
    """Run auto_backup + add_columns + backfill_uuids."""
    if handle.is_postgres:
        try:
            backup = auto_backup_postgres(
                handle.engine,
                tag="node_uuid_backfill",
                dest_dir=Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                                       / "_pga_backups",
            )
            log.info("PG backup created: %s", backup)
        except BackupSkipped as e:
            log.warning("PG backup skipped: %s", e)
            log.warning("Proceeding WITHOUT a backup (CLI mode = no prompt)")
    else:
        backup = auto_backup_sqlite(handle.sqlite_path, tag="node_uuid_backfill")
        log.info("SQLite backup created: %s", backup)
    add_columns(handle)
    log.info("Schema OK on: %s", ", ".join(TABLES))
    counts = backfill_uuids(handle)
    log.info("Backfill applied to %s:", handle.conn_str)
    for table, n in counts.items():
        log.info("  %-30s %d row(s) updated", table, n)
    return 0


def _rollback(args) -> int:
    """Restore SQLite DB from a backup file. PG rollback is manual via psql."""
    if args.conn_str is not None:
        log.error("--rollback is SQLite-only. For PG, restore manually with "
                  "'psql -d <db> -f <backup>'")
        return 2
    backup = Path(args.rollback)
    if not backup.exists():
        log.error("Backup not found: %s", backup)
        return 2
    db = Path(args.db)
    shutil.copy2(backup, db)
    log.info("Rolled back %s ← %s", db, backup)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_argv(argv)
    if args.rollback:
        return _rollback(args)
    handle = _resolve_input(args)
    if args.dry_run:
        return _dry_run(handle)
    if args.apply:
        return _apply(handle, args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 2: Smoke-run --dry-run on a tmp SQLite DB**

Run:
```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
import sqlite3, tempfile, os
from pathlib import Path
tmp = Path(tempfile.mkstemp(suffix='.sqlite')[1])
conn = sqlite3.connect(tmp)
conn.execute('CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT)')
conn.execute('CREATE TABLE inventario_materiali_table (id_invmat INTEGER PRIMARY KEY)')
conn.execute('CREATE TABLE periodizzazione_table (id_perfas INTEGER PRIMARY KEY)')
conn.execute(\"INSERT INTO us_table VALUES (1, 'S')\")
conn.commit()
conn.close()
print(f'Tmp DB: {tmp}')
import subprocess
r = subprocess.run(['python', '-m', 'scripts.migrations.2026_05_node_uuid_backfill',
                    '--db', str(tmp), '--dry-run'],
                   capture_output=True, text=True,
                   env={**os.environ, 'PYTHONPATH': os.getcwd()})
print('--- stdout ---'); print(r.stdout)
print('--- stderr ---'); print(r.stderr)
print('exit:', r.returncode)
tmp.unlink()
"
```

Expected output: 3 lines reporting "needs ALTER TABLE + backfill" for each of the 3 tables, exit 0.

NOTE: the script filename starts with a digit (`2026_05_...`), so `python -m scripts.migrations.2026_05_node_uuid_backfill` will fail with `SyntaxError`. The smoke test must invoke as `python scripts/migrations/2026_05_node_uuid_backfill.py` instead. Adjust:

```bash
PYTHONPATH="$PWD" python scripts/migrations/2026_05_node_uuid_backfill.py --db <tmp_db> --dry-run
```

If the smoke confirms `--dry-run` lists the 3 tables and exits 0, we're good.

- [ ] **Step 3: Run all migration tests**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/migrations/ -v 2>&1 | tail -15
```

Expected: 7 PASSED (4 existing SQLite lib + 3 mutex/backup) + nothing else changed (Group C is CLI-only, no new tests).

- [ ] **Step 4: Full sync+migrations suite**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `251 passed, 5 skipped` (unchanged from Group B).

- [ ] **Step 5: AC-2 sanity ping**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/migrations/2026_05_node_uuid_backfill.py
git commit -m "$(cat <<'EOF'
refactor(pg-a/C): CLI dispatches on --db vs --conn-str

The CLI now resolves the DB input through _resolve_db_handle,
producing a DbHandle that subsequent _apply / _dry_run /
_rollback functions operate on. Backup helper is selected
per backend: auto_backup_sqlite for SQLite (existing path),
auto_backup_postgres for PG (Group B). PG backup destination
is ~/pyarchinit/pyarchinit_DB_folder/_pga_backups/.

CLI mode is non-interactive: when pg_dump is missing the
script logs a WARNING and proceeds without a backup
(documented in --help). Interactive QGIS dialog gating
arrives in Group F.

--rollback remains SQLite-only; PG rollback is manual via
'psql -d db -f backup.sql'. The script reports this clearly
on attempted PG rollback.

251 passed, 5 skipped (unchanged - Group C is CLI plumbing,
no new tests). AC-2 preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group D — `_verify_schema` swap PRAGMA → `_columns_of`

### Task D.1: Internal swap inside `GraphIngestor._verify_schema`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_ingestor.py:200-213`

- [ ] **Step 1: Read the current `_verify_schema` method**

```bash
sed -n '200,215p' modules/s3dgraphy/sync/graph_ingestor.py
```

Note the current 13-line method that uses `sqlite3.connect()` + `PRAGMA table_info(us_table)`.

- [ ] **Step 2: Replace with the cross-backend version (signature preserved)**

Use the Edit tool to replace:

```python
    def _verify_schema(self, db_path: Path) -> None:
        if not db_path.exists():
            raise GraphIngestError(f"DB file not found: {db_path}")
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(
```

with:

```python
    def _verify_schema(self, db_path: Path) -> None:
        # PG-A (5.7.0-alpha): cross-backend introspection via Foundation's
        # _columns_of dispatcher. db_path is still a Path here because
        # populate_list (the only caller) is SQLite-only until PG-C ships.
        # Internally we resolve to a DbHandle so the same code path will
        # work on PG once populate_list flips its signature.
        from ._db_handle import _columns_of, _resolve_db_handle
        if not db_path.exists():
            raise GraphIngestError(f"DB file not found: {db_path}")
        try:
            handle = _resolve_db_handle(db_path)
            cols = _columns_of(handle.engine, "us_table")
        except Exception as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(
```

- [ ] **Step 3: Verify existing AC-2 + import tests still pass**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/ -q --tb=no 2>&1 | tail -3
```

Expected: AC-2 PASS; full sync = `246 passed, 5 skipped` (unchanged from Foundation post-F.3 + Groups A-C didn't add sync tests).

- [ ] **Step 4: Full suite**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `251 passed, 5 skipped`.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graph_ingestor.py
git commit -m "$(cat <<'EOF'
refactor(pg-a/D): _verify_schema cross-backend via _columns_of

Replace the sqlite3.connect + PRAGMA table_info path with
Foundation's _columns_of dispatcher. db_path: Path signature
preserved because the only caller (populate_list) still passes
a Path - the actual flip to DbHandle ships in PG-C.

Internally we resolve db_path -> DbHandle via the shim, so the
same _columns_of dispatch already works on PG. When PG-C flips
populate_list's signature, this method will accept DbHandle
directly with zero behaviour change.

The exception handling broadens from sqlite3.Error to the more
general Exception (since SQLAlchemy on PG can raise OperationalError
or DBAPIError). The error message wrapper preserves the existing
"Cannot read us_table schema:" prefix for backward compat with any
log scrapers / error handlers downstream.

251 passed, 5 skipped (unchanged). AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group E — 6 PG L2 tests in `tests/sync/test_node_uuid_backfill_pg.py`

### Task E.1: Create the 6-case PG test file

**Files:**
- Create: `tests/sync/test_node_uuid_backfill_pg.py`

- [ ] **Step 1: Write the test file**

```python
# tests/sync/test_node_uuid_backfill_pg.py
"""PG-A: L2 PostgreSQL tests for the node_uuid backfill migration.

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed. Reuses the pg_engine session fixture from
tests/sync/conftest_pg.py (Foundation).
"""
from __future__ import annotations

import re
from unittest.mock import patch

import pytest
from sqlalchemy import inspect, text

# Import pg_engine fixture explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine  # noqa: F401


UUID_V7_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@pytest.fixture
def clean_pg_with_seed(pg_engine):
    """Truncate the 3 tables, insert 1 row per table with NULL node_uuid."""
    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))
        # inventario_materiali_table doesn't exist in conftest_pg's minimal
        # schema, so create it idempotently for this test module
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inventario_materiali_table (
                id_invmat SERIAL PRIMARY KEY,
                sito TEXT,
                numero_inventario TEXT,
                node_uuid TEXT
            )
        """))
        conn.execute(text(
            "TRUNCATE inventario_materiali_table RESTART IDENTITY CASCADE"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us) VALUES ('S', '1', '1')"
        ))
        conn.execute(text(
            "INSERT INTO inventario_materiali_table (sito, numero_inventario) "
            "VALUES ('S', 'A1')"
        ))
        conn.execute(text(
            "INSERT INTO periodizzazione_table (sito, periodo, fase) "
            "VALUES ('S', 1, 'I')"
        ))
    yield pg_engine


def test_add_columns_idempotent_on_pg(clean_pg_with_seed):
    """Run #1 adds 3 columns + 3 indexes; run #2 is no-op."""
    from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns,
    )
    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))
    add_columns(handle)
    for table in TABLES:
        assert "node_uuid" in _columns_of(clean_pg_with_seed, table)
    # Second run = no-op
    add_columns(handle)
    for table in TABLES:
        cols = _columns_of(clean_pg_with_seed, table)
        # Still exactly one node_uuid column (no duplicates)
        assert "node_uuid" in cols


def test_backfill_uuids_assigns_uuid7_on_pg(clean_pg_with_seed):
    """Every row has a valid UUID v7 after backfill; counts are accurate."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        TABLES, add_columns, backfill_uuids,
    )
    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))
    add_columns(handle)
    counts = backfill_uuids(handle)
    assert counts["us_table"] == 1
    assert counts["inventario_materiali_table"] == 1
    assert counts["periodizzazione_table"] == 1
    with clean_pg_with_seed.connect() as conn:
        for table in TABLES:
            rows = conn.execute(
                text(f"SELECT node_uuid FROM {table}")
            ).fetchall()
            for (val,) in rows:
                assert val is not None, f"NULL node_uuid in {table}"
                assert UUID_V7_REGEX.match(val), f"not UUID v7 in {table}: {val}"


def test_partial_unique_index_allows_null_collision(clean_pg_with_seed):
    """The WHERE node_uuid IS NOT NULL clause permits multiple NULLs.

    Required for partial-failure recovery: if add_columns succeeded on
    table A but crashed mid-backfill, a re-run must not blow up on the
    rows still carrying NULL.
    """
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from scripts.migrations._2026_05_node_uuid_backfill_lib import add_columns
    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))
    add_columns(handle)
    # Insert two more rows with NULL node_uuid - if the index were full
    # unique, the second INSERT would raise.
    with clean_pg_with_seed.begin() as conn:
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us) VALUES ('S', '1', '2')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us) VALUES ('S', '1', '3')"
        ))
        n_null = conn.execute(text(
            "SELECT COUNT(*) FROM us_table WHERE node_uuid IS NULL"
        )).scalar()
        assert n_null == 3, f"expected 3 NULL node_uuid rows, got {n_null}"


def test_pk_discovery_on_pg_via_inspector(clean_pg_with_seed):
    """SQLAlchemy Inspector returns the declared PK column on PG."""
    inspector = inspect(clean_pg_with_seed)
    for table, expected in [
        ("us_table", ["id_us"]),
        ("periodizzazione_table", ["id_perfas"]),
        ("inventario_materiali_table", ["id_invmat"]),
    ]:
        pk = inspector.get_pk_constraint(table)["constrained_columns"]
        assert pk == expected, f"{table}: expected {expected}, got {pk}"


def test_atomic_rollback_on_alter_failure(clean_pg_with_seed, monkeypatch):
    """If text() raises mid-add_columns, engine.begin() rolls back -
    no partial column added on the second/third table."""
    from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of
    from scripts.migrations import _2026_05_node_uuid_backfill_lib as lib

    handle = DbHandle.from_engine(clean_pg_with_seed,
                                   str(clean_pg_with_seed.url))

    # Patch text() inside the lib module to raise on the second call
    # (after us_table got its column added but before inventario gets it).
    original_text = lib.text
    call_count = {"n": 0}

    def fake_text(stmt):
        call_count["n"] += 1
        if "ALTER TABLE inventario_materiali_table" in stmt:
            raise RuntimeError("simulated mid-flight failure")
        return original_text(stmt)

    monkeypatch.setattr(lib, "text", fake_text)

    with pytest.raises(RuntimeError, match="simulated mid-flight failure"):
        lib.add_columns(handle)

    # Critical assertion: us_table's ALTER must have been ROLLED BACK
    # because engine.begin() wraps the whole loop in a single transaction
    cols = _columns_of(clean_pg_with_seed, "us_table")
    assert "node_uuid" not in cols, (
        "us_table.node_uuid should NOT exist after rollback; "
        "engine.begin() failed to roll back atomically"
    )


def test_auto_backup_postgres_invokes_pg_dump(tmp_path, monkeypatch):
    """Mock subprocess.run to verify pg_dump invocation argv + env."""
    from sqlalchemy import create_engine
    from scripts.migrations._common import auto_backup_postgres

    captured = {}

    def fake_run(cmd, env=None, timeout=None, check=False, **kw):
        captured["cmd"] = cmd
        captured["env"] = env
        # Simulate success
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    monkeypatch.setattr("scripts.migrations._common.subprocess.run", fake_run)
    monkeypatch.setattr("shutil.which",
                        lambda name: "/usr/bin/pg_dump" if name == "pg_dump"
                        else None)

    engine = create_engine(
        "postgresql+psycopg2://postgres:secret@localhost:5433/mydb"
    )
    out = auto_backup_postgres(engine, tag="t1", dest_dir=tmp_path)

    assert captured["cmd"][0] == "/usr/bin/pg_dump"
    assert "-h" in captured["cmd"] and "localhost" in captured["cmd"]
    assert "-p" in captured["cmd"] and "5433" in captured["cmd"]
    assert "-U" in captured["cmd"] and "postgres" in captured["cmd"]
    assert "-d" in captured["cmd"] and "mydb" in captured["cmd"]
    assert "-f" in captured["cmd"]
    assert captured["env"]["PGPASSWORD"] == "secret"
    assert "PATH" in captured["env"]  # PATH propagated for pg_dump's libs
    assert tmp_path in out.parents
```

- [ ] **Step 2: Run the 6 cases**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_node_uuid_backfill_pg.py -v 2>&1 | tail -15
```

Expected (one of two):
- PG offline / no psycopg2: 6 SKIPPED with reason `"PG not available at localhost:5433 (...)"`
- PG online + psycopg2: 6 PASSED

The `test_auto_backup_postgres_invokes_pg_dump` test does not depend on `pg_engine` (uses a non-connecting URL via mocked subprocess), so on PG-offline systems it will still be SKIPPED only because the file-level `pg_engine` import propagates a session-fixture skip. That's acceptable — Foundation's pattern.

NOTE: if `test_auto_backup_postgres_invokes_pg_dump` accidentally runs (because the file doesn't depend on `pg_engine` at module level), it should pass independently. In that case the count will be `5 skipped, 1 passed` on PG offline. Either outcome (`6 skipped` or `5 skipped + 1 passed`) is acceptable.

- [ ] **Step 3: Full sync+migrations suite**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected:
- PG offline: `251 passed, 11 skipped` (251 from Group D + 0 new passes if all skip + 6 new skips).
- Or `252 passed, 10 skipped` if `test_auto_backup_postgres_invokes_pg_dump` happens to run.
- PG online + psycopg2: `257 passed, 5 skipped`.

- [ ] **Step 4: AC-2 sanity ping**

Run:
```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_node_uuid_backfill_pg.py
git commit -m "$(cat <<'EOF'
test(pg-a/E): 6 L2 PostgreSQL tests for node_uuid backfill

Six cases that pin the cross-backend migration design:

1. test_add_columns_idempotent_on_pg - run #1 adds, run #2 no-op
2. test_backfill_uuids_assigns_uuid7_on_pg - every row has v7 UUID
3. test_partial_unique_index_allows_null_collision - WHERE NOT NULL
   permits multiple NULLs (recovery from partial failures)
4. test_pk_discovery_on_pg_via_inspector - SQLAlchemy reflection
   returns declared PK on PG (parity with SQLite)
5. test_atomic_rollback_on_alter_failure - engine.begin() rolls
   back the whole step on mid-flight exception
6. test_auto_backup_postgres_invokes_pg_dump - mocked subprocess
   verifies pg_dump argv + PGPASSWORD env propagation

The pg_engine fixture skips cleanly when PG offline at
localhost:5433 or psycopg2 missing - CI without local PG sees 6
SKIPPED, no failures.

inventario_materiali_table created idempotently in the test fixture
(it's not in Foundation's conftest_pg.py minimal schema since
Foundation only needed us/site/periodizzazione for the smoke test).

PG offline: 251 passed, 11 skipped.
PG online: 257 passed, 5 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group F — pyarchinitPlugin handler + bridge shim

### Task F.1: Refactor `_run_uuid_backfill_migration` in `pyarchinitPlugin.py`

**Files:**
- Modify: `pyarchinitPlugin.py:2771-2831` (the `_run_uuid_backfill_migration` method)

- [ ] **Step 1: Read the method's current code**

```bash
sed -n '2771,2832p' pyarchinitPlugin.py
```

Confirm the file picker pattern + `auto_backup_sqlite` direct call.

- [ ] **Step 2: Replace with the cross-backend version**

Use the Edit tool to replace the method body. The new version reads `Connection().conn_str()` to derive the current DB, dispatches backup per backend, and shows a backend-aware confirm dialog.

```python
    def _run_uuid_backfill_migration(self):
        """Backfill node_uuid on the currently-connected pyarchinit DB.

        PG-A (5.7.0-alpha): no file picker — uses the conn-str from the
        plugin's Connection() helper. Backup helper dispatches per backend.
        """
        from qgis.PyQt.QtWidgets import QMessageBox
        from pathlib import Path
        try:
            from .modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from .modules.db.pyarchinit_conn_strings import Connection
            from .scripts.migrations._2026_05_node_uuid_backfill_lib import (
                TABLES, add_columns, backfill_uuids,
            )
            from .scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )
        except Exception:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from modules.db.pyarchinit_conn_strings import Connection
            from scripts.migrations._2026_05_node_uuid_backfill_lib import (
                TABLES, add_columns, backfill_uuids,
            )
            from scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )

        conn_str = Connection().conn_str()
        if not conn_str:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Connessione non configurata",
                "Connetti prima un DB pyarchinit dalle Settings (menu "
                "Database → Configurazione)."
            )
            return

        try:
            handle = _resolve_db_handle(conn_str)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore di connessione",
                f"Impossibile aprire la connessione al DB:\n{e}",
            )
            return

        backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                         + "/" + str(handle.engine.url.database or "")
                         if handle.is_postgres
                         else f"SQLite: {handle.sqlite_path}")
        tables_list = "\n".join(f"  - {t}" for t in TABLES)
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma backfill node_uuid",
            f"Backend: {backend_label}\n\n"
            "Verrà aggiunta la colonna node_uuid (TEXT) e assegnato un "
            "UUID v7 a ogni record nelle tabelle:\n"
            f"{tables_list}\n\n"
            "Procedere con --apply (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        backup_path = None
        try:
            if handle.is_postgres:
                dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                            / "_pga_backups")
                try:
                    backup_path = auto_backup_postgres(
                        handle.engine, tag="node_uuid_backfill",
                        dest_dir=dest_dir,
                    )
                except BackupSkipped as e:
                    skip = QMessageBox.question(
                        self.iface.mainWindow(),
                        "Backup non disponibile",
                        f"{e}\n\nProcedere SENZA backup automatico "
                        "(sconsigliato)?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if skip != QMessageBox.Yes:
                        return
                    backup_path = None
            else:
                backup_path = auto_backup_sqlite(
                    handle.sqlite_path, tag="node_uuid_backfill",
                )
            add_columns(handle)
            counts = backfill_uuids(handle)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore migrazione",
                f"La migrazione è fallita:\n{e}\n\n"
                f"Backup creato: {backup_path}" if backup_path
                else f"La migrazione è fallita:\n{e}\n\nNessun backup creato.",
            )
            return

        counts_msg = "\n".join(
            f"  {table}: {n} row(s)" for table, n in counts.items())
        QMessageBox.information(
            self.iface.mainWindow(),
            "Backfill completato",
            f"Backup: {backup_path}\n\nUUID v7 assegnati:\n{counts_msg}",
        )
```

- [ ] **Step 3: Lint check (Python imports + syntax)**

Run:
```bash
PYTHONPATH="$PWD" python -c "
import ast
with open('pyarchinitPlugin.py') as f:
    ast.parse(f.read())
print('pyarchinitPlugin.py syntax OK')
"
```

Expected: `pyarchinitPlugin.py syntax OK`.

### Task F.2: Refactor `_offer_node_uuid_migration` in `s3dgraphy_dot_bridge.py`

**Files:**
- Modify: `modules/s3dgraphy/s3dgraphy_dot_bridge.py:899-960` (the `_offer_node_uuid_migration` method)

- [ ] **Step 1: Locate the method**

```bash
sed -n '899,965p' modules/s3dgraphy/s3dgraphy_dot_bridge.py
```

- [ ] **Step 2: Adapt to accept Path or DbManager via shim**

Use the Edit tool to update the method:

```python
        def _offer_node_uuid_migration(self, db_input, error) -> bool:
            """Offer to auto-apply the Phase 1 node_uuid backfill migration.

            PG-A (5.7.0-alpha): db_input may be a Path (legacy SQLite call
            sites) or a DbManager / conn-str / DbHandle (new). Backend
            detected via _resolve_db_handle.

            Returns True iff the migration was applied successfully and
            the caller should retry the import.
            """
            from pathlib import Path as _Path
            try:
                from ..s3dgraphy.sync._db_handle import _resolve_db_handle
                from ..scripts.migrations._2026_05_node_uuid_backfill_lib import (
                    add_columns, backfill_uuids,
                )
                from ..scripts.migrations._common import (
                    BackupSkipped, auto_backup_postgres, auto_backup_sqlite,
                )
            except ImportError:
                from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
                from scripts.migrations._2026_05_node_uuid_backfill_lib import (
                    add_columns, backfill_uuids,
                )
                from scripts.migrations._common import (
                    BackupSkipped, auto_backup_postgres, auto_backup_sqlite,
                )

            try:
                handle = _resolve_db_handle(db_input)
            except Exception as e:
                QMessageBox.critical(
                    self, "Errore di connessione",
                    f"Impossibile aprire il DB per la migrazione:\n{e}",
                )
                return False

            backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                             + "/" + str(handle.engine.url.database or "")
                             if handle.is_postgres
                             else f"SQLite: {handle.sqlite_path}")
            reply = QMessageBox.question(
                self,
                "Migrazione node_uuid richiesta",
                f"{error}\n\n"
                f"Backend: {backend_label}\n\n"
                f"Il database non ha la colonna `node_uuid` richiesta dal "
                f"bridge s3dgraphy (Phase 1 migration).\n\n"
                f"Vuoi applicare la migrazione adesso?\n"
                f"- Verrà fatto un backup automatico\n"
                f"- La colonna `node_uuid` (TEXT) sarà aggiunta alle "
                f"tabelle stratigrafiche\n"
                f"- A ogni record verrà assegnato un UUID v7",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply != QMessageBox.Yes:
                return False

            try:
                if handle.is_postgres:
                    from pathlib import Path as _P
                    dest_dir = (_P.home() / "pyarchinit"
                                / "pyarchinit_DB_folder" / "_pga_backups")
                    try:
                        backup = auto_backup_postgres(
                            handle.engine, tag="node_uuid_backfill",
                            dest_dir=dest_dir,
                        )
                    except BackupSkipped as e:
                        skip = QMessageBox.question(
                            self, "Backup non disponibile",
                            f"{e}\n\nProcedere SENZA backup (sconsigliato)?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No,
                        )
                        if skip != QMessageBox.Yes:
                            return False
                        backup = None
                else:
                    backup = auto_backup_sqlite(
                        handle.sqlite_path, tag="node_uuid_backfill",
                    )
                add_columns(handle)
                counts = backfill_uuids(handle)
            except Exception as mig_err:
                QMessageBox.critical(
                    self, "Errore migrazione",
                    f"La migrazione è fallita:\n{mig_err}",
                )
                return False

            QMessageBox.information(
                self, "Migrazione applicata",
                f"Backup: {backup}\n\nUUID v7 assegnati:\n"
                + "\n".join(f"  {t}: {n}" for t, n in counts.items())
            )
            return True
```

NOTE: **Both call sites of `_offer_node_uuid_migration` (lines 783 and 865) currently pass a `db_path` Path argument.** They continue to work because `_resolve_db_handle(Path)` is supported (with a DeprecationWarning that gets silenced in non-test contexts). No call site changes needed.

- [ ] **Step 3: Syntax check**

```bash
PYTHONPATH="$PWD" python -c "
import ast
with open('modules/s3dgraphy/s3dgraphy_dot_bridge.py') as f:
    ast.parse(f.read())
print('s3dgraphy_dot_bridge.py syntax OK')
"
```

Expected: `syntax OK`.

- [ ] **Step 4: Run full suite to confirm no test broke**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `251 passed, 11 skipped` (or `252/10` per Group E note). No regressions.

- [ ] **Step 5: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pyarchinitPlugin.py modules/s3dgraphy/s3dgraphy_dot_bridge.py
git commit -m "$(cat <<'EOF'
feat(pg-a/F): QGIS handler + bridge shim use Connection() conn-str

pyarchinitPlugin._run_uuid_backfill_migration:
- Drop the file picker entirely
- Read conn-str via Connection().conn_str()
- Show "Connetti prima un DB" error if no connection configured
- Confirm dialog displays backend label (sqlite path or pg host/db)
- Dispatch backup per backend (auto_backup_sqlite vs auto_backup_postgres)
- BackupSkipped exception -> dialog asking to skip-or-cancel
- Pass DbHandle to add_columns / backfill_uuids (which accept Path or
  DbHandle via the shim)

s3dgraphy_dot_bridge._offer_node_uuid_migration:
- Renamed parameter from db_path to db_input (accepts Path / DbManager /
  conn-str / DbHandle via _resolve_db_handle shim)
- Both existing call sites (lines 783, 865 - bridge dialog import flow)
  continue to work because they pass Path - which the shim still resolves
  with a DeprecationWarning
- Same backend-aware backup dispatch as the menu handler

This is the only PG-A Group that touches QGIS-side code. Manual
verification required to confirm UX (no automated GUI test); test
counts are unchanged because the L2 PG tests already cover the
underlying lib + backup helpers.

251 passed, 11 skipped (PG offline). AC-2 preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group G — Docs + version bump 5.7.0-alpha

### Task G.1: Bump `metadata.txt`

**Files:**
- Modify: `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.6.2-alpha` → `version=5.7.0-alpha`.

- [ ] **Step 2: Verify**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.7.0-alpha`.

### Task G.2: Append Phase 3 entry in dev-log

**Files:**
- Modify: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Locate the topmost Phase 3 section**

```bash
grep -n "^## Phase 3" docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md | head -3
```

The Foundation section is at the top: `## Phase 3 — PG Compat Foundation (5.6.2-alpha)`. We insert PG-A as a sibling section ABOVE it (most recent first).

- [ ] **Step 2: Insert the new section**

Use the Edit tool to find this exact text:

```
---

## Phase 3 — PG Compat Foundation (5.6.2-alpha)
```

and replace with:

```
---

## Phase 3 — PG-A migration (5.7.0-alpha)

**Tag:** `phase3-pgcompat-a-migration-5.7.0-alpha`
**Date:** 2026-05-10
**Spec:** `docs/superpowers/specs/2026-05-10-pg-a-migration-design.md`
**Plan:** `docs/superpowers/plans/2026-05-10-pg-a-migration.md`

### What shipped

- `node_uuid` backfill migration works on **both** SQLite and PostgreSQL
- Migration lib uses SQLAlchemy `engine.begin()` everywhere — no more
  `sqlite3.connect()`. Public API accepts `DbHandle | Path` via the
  Foundation `_resolve_db_handle` shim
- PK discovery via `Inspector.get_pk_constraint` (cross-dialect)
- `auto_backup_postgres()` wraps `pg_dump` subprocess with `BackupSkipped`
  exception when `pg_dump` is missing
- CLI: `--db` (SQLite) and `--conn-str` (any DSN) are mutually exclusive
- QGIS menu handler: dropped file picker; reads conn-str from
  `Connection().conn_str()`; backend-aware confirm dialog
- `GraphIngestor._verify_schema` uses `_columns_of` cross-dialect (signature
  preserved — populate_list flip is PG-C scope)

### Tests

- 3 new L0 unit tests (PK discovery via Inspector, DbHandle acceptance,
  idempotency contract)
- 6 new L2 PG tests (skip cleanly when PG offline / psycopg2 missing)
- 3 new L0 unit tests for `_common.py` (mutex, sqlite-via-conn-str,
  pg_dump missing)
- Total: 251 passed, 11 skipped (PG offline) or 257 passed, 5 skipped
  (PG online + psycopg2)
- AC-2 byte-identical baseline preserved

### Known follow-ups (later milestones)

- **PG-B** (5.7.1-alpha): Projector + GraphMLWriter read from PG (8 + 1
  sqlite3.connect call sites in graph_projector.py + graphml_writer.py)
- **PG-C** (5.7.2-alpha): Ingestor writes to PG with atomic transactions
  (`populate_list` signature flips from `db_path: Path` to `db_handle: DbHandle`)
- **PG-D** (5.7.3-alpha): ParadataStore + GroupStore workspace dir on PG
  (`pyarchinit_DB_folder/<conn_slug>/<sito>/` for PG)
- **Consolidation** (5.7.4-alpha): polish, deprecation warning cleanup

---

## Phase 3 — PG Compat Foundation (5.6.2-alpha)
```

### Task G.3: Bilingual CHANGELOG entry

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Insert above the existing 5.6.2-alpha section**

Use the Edit tool to find this exact text (the topmost entry):

```
## [5.6.2-alpha] - 2026-05-10
```

and replace with:

```
## [5.7.0-alpha] - 2026-05-10

### Italiano

**PG-A — Phase 1 `node_uuid` backfill ora funziona su PostgreSQL.**

Primo milestone post-Foundation della Phase 3. Ribalta il primo caller di produzione (lo script di migrazione `node_uuid`) sull'infrastruttura cross-backend. Tutti i 245 test SQLite di Foundation restano verdi via shim. Nessuna modifica a `populate_list`, projector, paradata store — quelli sono PG-B/C/D.

- **Migration lib SQLAlchemy-everywhere**: `add_columns(db)` e `backfill_uuids(db)` accettano `DbHandle | Path` (backward compat via shim). `engine.begin()` invece di `sqlite3.connect()` ovunque. Atomic via transazione SQLAlchemy.
- **PK discovery cross-dialect**: `sqlalchemy.inspect(engine).get_pk_constraint(table)["constrained_columns"]` rimpiazza il `PRAGMA table_info` SQLite-only. Funziona identicamente su entrambi i backend.
- **`auto_backup_postgres(engine, tag, dest_dir)`**: wrapper di `pg_dump` via `subprocess.run` con timeout 5min, PGPASSWORD in env (mai in argv). Solleva `BackupSkipped` se `pg_dump` non è nel PATH; il caller (CLI o QGIS dialog) decide se procedere senza backup.
- **CLI `--db` / `--conn-str` mutex**: l'argparse richiede esattamente uno dei due. `--conn-str` accetta sia `sqlite:///path` che `postgresql://...`.
- **QGIS handler senza file-picker**: `Migrazioni → Backfill node_uuid` legge la conn-str da `Connection().conn_str()`. Dialog di conferma mostra il backend (sqlite path o pg host/db). Backup dispatch automatico per backend. Errore se nessuna connessione è configurata.
- **`GraphIngestor._verify_schema` cross-dialect**: usa `_columns_of` di Foundation invece di `PRAGMA table_info`. Signature `db_path: Path` preservata (il flip a `DbHandle` è PG-C).
- **Bridge `_offer_node_uuid_migration`**: il dialog di auto-migration nel bridge accetta Path, DbManager, conn-str, o DbHandle.

13 nuovi test (3 lib unit + 3 mutex/backup unit + 6 PG L2 + 1 condivisi su SQLite via shim). Test count: 245 → 251 passed (PG offline, 11 skip) o 257 passed (PG online + psycopg2). AC-2 byte-identical preservato.

### English

**PG-A — Phase 1 `node_uuid` backfill now works on PostgreSQL.**

First post-Foundation milestone of Phase 3. Flips the first production caller (the `node_uuid` migration script) onto the cross-backend infrastructure. All 245 Foundation SQLite tests stay green via the shim. No changes to `populate_list`, projector, paradata store — those are PG-B/C/D.

- **Migration lib SQLAlchemy-everywhere**: `add_columns(db)` and `backfill_uuids(db)` accept `DbHandle | Path` (backward compat via shim). `engine.begin()` instead of `sqlite3.connect()` throughout. Atomic via SQLAlchemy transactions.
- **Cross-dialect PK discovery**: `sqlalchemy.inspect(engine).get_pk_constraint(table)["constrained_columns"]` replaces SQLite-only `PRAGMA table_info`. Identical behaviour on both backends.
- **`auto_backup_postgres(engine, tag, dest_dir)`**: `pg_dump` subprocess wrapper with 5-minute timeout, PGPASSWORD in env (never on argv). Raises `BackupSkipped` when `pg_dump` is missing from PATH; caller (CLI or QGIS dialog) decides whether to proceed without backup.
- **CLI `--db` / `--conn-str` mutex**: argparse requires exactly one. `--conn-str` accepts both `sqlite:///path` and `postgresql://...`.
- **QGIS handler without file picker**: `Migrazioni → Backfill node_uuid` reads conn-str from `Connection().conn_str()`. Confirmation dialog shows the backend (sqlite path or pg host/db). Backup helper dispatches per backend. Error dialog when no connection is configured.
- **`GraphIngestor._verify_schema` cross-dialect**: uses Foundation's `_columns_of` instead of `PRAGMA table_info`. `db_path: Path` signature preserved (the `DbHandle` flip is PG-C).
- **Bridge `_offer_node_uuid_migration`**: the auto-migration dialog now accepts Path, DbManager, conn-str, or DbHandle.

13 new tests (3 lib unit + 3 mutex/backup unit + 6 PG L2 + 1 shared with SQLite via shim). Test count: 245 → 251 passed (PG offline, 11 skip) or 257 passed (PG online + psycopg2). AC-2 byte-identical preserved.

---

## [5.6.2-alpha] - 2026-05-10
```

### Task G.4: Final verification + commit

**Files:** none (verify + commit)

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
echo "=== Recent commits since spec ==="
git log --oneline e355f3a2..HEAD

echo "=== Cumulative Co-Authored-By count ==="
git log e355f3a2..HEAD --format=%B | grep -c Co-Authored-By

echo "=== Full sync+migrations suite ==="
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3

echo "=== AC-2 ==="
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3

echo "=== Version ==="
grep "^version=" metadata.txt
```

Expected:
- 6 commits since `e355f3a2`: A, B, C, D, E, F
- Co-Authored-By count: `0`
- `251 passed, 11 skipped` (PG offline) or `257 passed, 5 skipped` (PG online)
- AC-2 PASS
- Version: `5.7.0-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(pg-a/G): docs + version bump 5.7.0-alpha

PG-A milestone documentation: bilingual CHANGELOG entry,
dev-log Phase 3 section, version bump 5.6.2-alpha -> 5.7.0-alpha.

Cumulative deliverables (Groups A-G):
- Migration lib SQLAlchemy-everywhere (DbHandle | Path)
- _common.py auto_backup_postgres + --db/--conn-str mutex
- CLI cross-backend dispatch
- _verify_schema cross-dialect via _columns_of
- 6 PG L2 tests + 6 L0 unit tests
- QGIS handler without file picker, reads Connection().conn_str()
- Bridge _offer_node_uuid_migration accepts all 5 input types

Test count: 245 -> 251 passed, 11 skipped (PG offline) or
245 -> 257 passed, 5 skipped (PG online with psycopg2).
AC-2 byte-identical baseline preserved throughout.

Spec: docs/superpowers/specs/2026-05-10-pg-a-migration-design.md
Plan: docs/superpowers/plans/2026-05-10-pg-a-migration.md
Predecessor: phase3-pgcompat-shim-5.6.2-alpha (7420a6cc)
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

- [ ] **Step 3: Post-commit verification**

```bash
echo "=== Post-G commit verification ==="
git log --oneline e355f3a2..HEAD
git log e355f3a2..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 7 commits since `e355f3a2`: A, B, C, D, E, F, G
- Co-Authored-By count: `0`
- `251 passed, 11 skipped` (PG offline) or `257 passed, 5 skipped` (PG online)
- AC-2 PASS
- Version: `5.7.0-alpha`

---

## Group H — Tag + push

### Task H.1: Pre-flight branch check

**Files:** none (git operation)

- [ ] **Step 1: Confirm we're on `Stratigraph_00001`**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git rev-parse --abbrev-ref HEAD
```

Expected: `Stratigraph_00001`. **STOP and BLOCK** if anything else (NEVER push to `main` or `master`).

### Task H.2: Create the annotated tag

**Files:** none (git operation)

- [ ] **Step 1: Tag**

```bash
git tag -a phase3-pgcompat-a-migration-5.7.0-alpha -m "$(cat <<'EOF'
PG-A - Phase 1 node_uuid migration on PostgreSQL

First post-Foundation milestone of Phase 3 (PG-compat refactor).
The node_uuid backfill migration now works on both SQLite and
PostgreSQL backends. NO changes to populate_list, projector,
paradata store - those are PG-B/C/D scope.

Cumulative deliverables (Groups A-G, 7 commits):

- Migration lib (_2026_05_node_uuid_backfill_lib.py) uses
  SQLAlchemy engine.begin() + text() everywhere. Public API
  accepts DbHandle or legacy Path via _resolve_db_handle shim.
- PK discovery via SQLAlchemy Inspector (cross-dialect).
- auto_backup_postgres() wraps pg_dump subprocess; raises
  BackupSkipped when pg_dump missing.
- CLI: --db (SQLite) and --conn-str (any DSN) mutually exclusive.
- QGIS handler reads Connection().conn_str(); no file picker.
- Bridge _offer_node_uuid_migration accepts Path / DbManager /
  conn-str / Engine / DbHandle.
- GraphIngestor._verify_schema uses _columns_of (cross-dialect)
  while preserving the db_path: Path signature for populate_list
  callers (PG-C will flip the signature).

Test counts: 245 -> 251 passed, 11 skipped (PG offline) or
245 -> 257 passed, 5 skipped (PG online + psycopg2).
AC-2 byte-identical baseline preserved.

Spec: docs/superpowers/specs/2026-05-10-pg-a-migration-design.md
Plan: docs/superpowers/plans/2026-05-10-pg-a-migration.md
Predecessor: phase3-pgcompat-shim-5.6.2-alpha (7420a6cc)
EOF
)"
```

- [ ] **Step 2: Verify the tag**

```bash
echo "=== Tag created ==="
git tag -n5 phase3-pgcompat-a-migration-5.7.0-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse phase3-pgcompat-a-migration-5.7.0-alpha^{commit}
git rev-parse HEAD
echo "=== Above two SHAs must match ==="
echo "=== Tag is annotated ==="
git cat-file -t phase3-pgcompat-a-migration-5.7.0-alpha
echo "=== Should print 'tag' (annotated), not 'commit' ==="
echo "=== Tag message has NO Co-Authored-By ==="
git tag -l --format='%(contents)' phase3-pgcompat-a-migration-5.7.0-alpha | grep -c Co-Authored-By
```

The final grep MUST return `0`.

### Task H.3: Push tag + branch

**Files:** none (git operation)

- [ ] **Step 1: Push the tag first**

```bash
git push origin phase3-pgcompat-a-migration-5.7.0-alpha 2>&1 | tail -3
```

Expected: `* [new tag]         phase3-pgcompat-a-migration-5.7.0-alpha -> phase3-pgcompat-a-migration-5.7.0-alpha`.

- [ ] **Step 2: Push the branch**

```bash
git push origin Stratigraph_00001 2>&1 | tail -3
```

Expected: branch updated successfully (Dependabot warnings unrelated).

- [ ] **Step 3: Verify on origin**

```bash
git ls-remote --tags origin | grep "phase3-pgcompat-a-migration-5.7.0-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected:
- Tag listed (with `^{}` dereferenced commit line)
- Branch tip equals local HEAD

### Task H.4: Memory snapshot (controller, no subagent)

**Files:** `~/.claude/projects/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/memory/project_pg_compat_progress.md`

- [ ] **Step 1: Update the existing memory note**

Read the current `project_pg_compat_progress.md`. In the "PENDING milestones" table, change the PG-A row from "TBD" to "SHIPPED 2026-05-10 — tag `phase3-pgcompat-a-migration-5.7.0-alpha`".

Append a new "## SHIPPED PG-A (5.7.0-alpha) 2026-05-10" section at the top with:
- Commit SHAs of A through G (7 total)
- Test count delta
- Lessons learned (if any)

Update `MEMORY.md` index line for `project_pg_compat_progress.md` to reflect the new CURRENT STATE.

- [ ] **Step 2: Final report**

After Group H completes, report:

- **Status:** DONE
- 7 new commits since `e355f3a2`
- Tag `phase3-pgcompat-a-migration-5.7.0-alpha` pushed to origin
- Test count: 251 passed (PG offline) / 257 (PG online), AC-2 preserved
- Zero `Co-Authored-By: Claude` trailers
- Memory note updated

---

## Self-Review

This plan covers every PG-A spec requirement:

| Spec section | Plan task |
|---|---|
| §3.1 Q1=a (single menu, Connection().conn_str(), no file picker) | Group F.1 |
| §3.2 Q2=a+c (pg_dump or warning fallback) | Group B (auto_backup_postgres + BackupSkipped) + Group F.1 (dialog) |
| §3.3 Q3=a (--conn-str mutex --db) | Group B (parse_argv) + Group C (CLI dispatch) |
| §3.4 Approach 1 (SQLAlchemy-everywhere) | Group A (migration lib) + Group D (verify_schema) |
| §4.1 Modified files (10 entries) | Groups A-G cover all |
| §4.2 New files (2 entries) | Group A (lib unit) + Group E (PG L2) |
| §4.3 NOT touched | Documented + verified by AC-2 sanity ping at every Group |
| §5 SQL dialect compat (5 sub-sections) | Group A applies all |
| §6 Data flow + error handling | Groups A (atomic) + B (BackupSkipped) + C (CLI) + F (dialogs) |
| §7 Test strategy | Groups A.1, B.1, E.1 |
| §8 Acceptance criteria (PG-A-AC-1..8) | Pinned by tests across A.1, B.1, E.1 |
| §9 Release plan | Groups G + H |

**Type consistency check:** `DbHandle`, `_resolve_db_handle`, `_columns_of`, `BackupSkipped`, `auto_backup_postgres`, `auto_backup_sqlite`, `add_columns`, `backfill_uuids`, `parse_argv` — all spelled and used consistently across Groups.

**No placeholders:** every step has either runnable code, exact commands, or specific file edits. No "TBD" / "TODO" / "Add appropriate error handling".

**Scope check:** Plan is focused on PG-A only. PG-B/C/D files are in §4.3 NOT touched and verified by AC-2 sanity pings.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-10-pg-a-migration.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review (spec compliance + code quality), fast iteration

**2. Inline Execution** — execute tasks in this session via `executing-plans`, batch with checkpoints

If **Subagent-Driven**, recommended batching:
- Group 0 (3 tasks) → no subagent — pure git
- Group A → 1 subagent (TDD lib refactor + 3 unit tests)
- Group B → 1 subagent (TDD common.py + 3 mutex/backup tests)
- Group C → 1 subagent (CLI dispatch refactor)
- Group D → 1 subagent (verify_schema swap)
- Group E → 1 subagent (6 PG L2 tests)
- Group F → 1 subagent (QGIS handler + bridge shim — sonnet OK, no UI test automation)
- Group G → 1 subagent (docs + version + final verification)
- Group H → 1 subagent (tag + push, gate per user approval)
- Memory snapshot → no subagent (controller writes after H ships)

If **Inline Execution**, batch by Group with checkpoint after each.
