# PG-A — Phase 1 `node_uuid` migration on PostgreSQL (5.7.0-alpha)

> **Spec source of truth.** Brainstormed 2026-05-10 after Foundation (5.6.2-alpha)
> shipped. This spec is the contract for the implementation plan that follows
> via `superpowers:writing-plans`.

**Status:** Approved 2026-05-10
**Predecessor:** `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
**Target tag:** `phase3-pgcompat-a-migration-5.7.0-alpha`
**Parent spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.2

---

## 1. Goal

Make the Phase 1 `node_uuid` backfill migration work on **both** SQLite and
PostgreSQL backends, reusing the `DbHandle` + `_columns_of` + `_resolve_db_handle`
machinery shipped in Foundation. PG-A is bounded: **only** the migration script,
its CLI, the QGIS menu handler, the bridge shim, and `GraphIngestor._verify_schema`
are touched. Production code paths for export (PG-B), import (PG-C), and paradata
storage (PG-D) stay SQLite-only and ship in subsequent milestones.

## 2. Background

The `node_uuid` migration adds a `node_uuid TEXT` column + a partial unique index
(`WHERE node_uuid IS NOT NULL`) to three pyarchinit tables (`us_table`,
`inventario_materiali_table`, `periodizzazione_table`) and assigns a UUID v7 to
every existing row. It is the **prerequisite** for any s3dgraphy bridge operation
because `GraphIngestor.populate_list` raises `SchemaMismatchError` if the column
is missing.

Today the migration is SQLite-only:

- Library uses `sqlite3.connect()` directly
- PK discovery uses `PRAGMA table_info(table)` + the `pk` flag
- Schema introspection is `PRAGMA table_info` again
- CLI takes `--db <sqlite_path>`
- QGIS handler opens a file picker
- Auto-backup is `shutil.copy2(file, file + ".pre_<tag>_<ts>")`

Foundation (5.6.2-alpha) shipped the cross-backend machinery (`DbHandle`,
`_resolve_db_handle`, `_columns_of`) without flipping any caller. PG-A is the
first milestone where production code starts using it.

## 3. Architectural decisions (from brainstorming 2026-05-10)

### 3.1 Q1 — Migration entry point UX

**Decision:** Single QGIS menu entry "Migrazioni → Backfill node_uuid (UUID v7
per record)" uses `self.DB_MANAGER` (current pyarchinit DB connection). **No
file picker.** If `self.DB_MANAGER is None`, show error dialog "Connetti prima
un DB pyarchinit dalle Settings".

**Rationale:** Aligns the migration with the user's actual working DB. The
file-picker path served legacy DBs not currently connected, but practically
users always migrate the DB they are using. Removing the file-picker eliminates
"wrong file picked" footguns.

### 3.2 Q2 — Backup mechanism on PG

**Decision:** `pg_dump` subprocess if available; warning fallback if missing.

- `auto_backup_postgres(engine, tag, dest_dir)` invokes
  `subprocess.run(["pg_dump", "-h", host, "-p", port, "-U", user, "-d", dbname, "-f", path], env={"PGPASSWORD": pwd}, timeout=300)`
  with `check=False`
- `pg_dump` discovery via `shutil.which("pg_dump")`
- If missing OR `subprocess` fails: dialog "pg_dump non disponibile o fallito.
  Procedi senza backup automatico (sconsigliato)? [Skip backup] [Cancel]"
- Backup destination: `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<dbname>.sql.backup_<ts>`
  where `<conn_slug>` is `slugify(f"{host}_{port}_{dbname}")`

**Rationale:** `pg_dump` is the standard, full-fidelity PG backup. SQL-level
COPY/SELECT dumps would require custom restore scripts; users typically have
`pg_dump` if they have PG installed locally. The warning fallback respects user
agency without forcing a hard dependency.

### 3.3 Q3 — CLI argument format

**Decision:** Add `--conn-str` flag, mutually exclusive with `--db`.

```bash
# SQLite (existing)
python scripts/migrations/2026_05_node_uuid_backfill.py --apply --db /path/to.sqlite

# PG (new)
python scripts/migrations/2026_05_node_uuid_backfill.py --apply --conn-str postgresql+psycopg2://postgres:postgres@localhost:5433/mydb
```

**Rationale:** Explicit dialect signal beats overloading `--db`. Reading conn-str
from QGIS settings was rejected because it makes the CLI brittle (needs QGIS
config files in expected locations) and surprising (no flag visible at
invocation time).

### 3.4 Approach 1 — SQLAlchemy-everywhere

**Decision:** Migration lib uses `engine.begin()` + `text()` exclusively. No more
`sqlite3.connect()`. PK discovery via `Inspector.get_pk_constraint(table)`.
Backup helper dispatches on backend.

**Rationale:** Foundation exists for this. A dual-path with sqlite3 preserved
would double the maintenance surface for negligible AC-2 risk gain (the migration
lib is fully covered by its own unit tests).

## 4. File-by-file change plan

### 4.1 Modified files

| Path | Change | LOC |
|---|---|---|
| `scripts/migrations/_2026_05_node_uuid_backfill_lib.py` | Replace `sqlite3.connect()` with `engine.begin()`. `add_columns(db_handle)` + `backfill_uuids(db_handle)` accept `DbHandle` (Path callers continue to work via shim for backward compat). `_has_column` removed (replaced by `_columns_of`). PK discovery via `Inspector.get_pk_constraint`. All statements via SQLAlchemy `text()`. | ~120 |
| `scripts/migrations/2026_05_node_uuid_backfill.py` | CLI dispatches on `--db` vs `--conn-str`. Help text updated. Backup helper selected per backend. | ~50 |
| `scripts/migrations/_common.py` | Add `auto_backup_postgres(engine, tag, dest_dir)`. Update `parse_argv` to make `--db` and `--conn-str` mutually exclusive. | ~80 |
| `modules/s3dgraphy/sync/graph_ingestor.py:_verify_schema` | Swap `sqlite3.connect()` + `PRAGMA table_info` for `_resolve_db_handle(db_path).engine` + `_columns_of`. Signature `_verify_schema(self, db_path)` preserved (PG-C will flip the populate_list caller later). | ~15 |
| `pyarchinitPlugin.py:_run_uuid_backfill_migration` | Drop file picker. Use `self.DB_MANAGER` (error dialog if `None`). Dispatch backup: `auto_backup_sqlite` for SQLite, `auto_backup_postgres` for PG. Confirm dialog displays the backend (path or conn slug). | ~50 |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py:_offer_node_uuid_migration` | Accept `db_path: Path` OR a DbManager via `_resolve_db_handle` shim. Backward-compat for SQLite call sites. | ~15 |
| `metadata.txt` | Bump `5.6.2-alpha` → `5.7.0-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.0-alpha]` section. | ~40 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 — PG-A migration section. | ~30 |
| `tests/migrations/test_node_uuid_backfill_cli.py` | Extend with 2-3 cases (mutex `--db` / `--conn-str`, `--conn-str sqlite://...` accepted). | +30 |

### 4.2 New files

| Path | Purpose | LOC |
|---|---|---|
| `tests/migrations/test_node_uuid_backfill_lib_unit.py` | L0 unit tests for PK discovery via SQLAlchemy Inspector, `_columns_of` round-trip, idempotency contract. No DB. | ~80 |
| `tests/sync/test_node_uuid_backfill_pg.py` | 6 L2 PG cases. Skipped cleanly when PG offline. | ~150 |

### 4.3 Files explicitly NOT touched (deferred to PG-B/C/D)

- `modules/s3dgraphy/sync/graph_projector.py` — sqlite3.connect call sites (PG-B)
- `modules/s3dgraphy/sync/graph_ingestor.py:populate_list` — main import flow stays SQLite-only (PG-C)
- `modules/s3dgraphy/sync/graphml_writer.py` (PG-B)
- `modules/s3dgraphy/sync/group_projector.py` (PG-B)
- `modules/s3dgraphy/sync/paradata_store.py` / `group_store.py` (PG-D)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2) — must stay green untouched throughout PG-A
- All other 244 SQLite tests — must stay green via the backward-compat shim

### 4.4 Total LOC

- Production code: ~330 (modified) + 0 (new) = **~330**
- Test code: ~30 (extended) + ~230 (new) = **~260**
- Docs: ~70 (CHANGELOG + dev-log)
- **Grand total: ~660 LOC**

## 5. SQL dialect compatibility

### 5.1 ALTER TABLE ADD COLUMN

| Dialect | Statement |
|---|---|
| SQLite | `ALTER TABLE us_table ADD COLUMN node_uuid TEXT` (no `IF NOT EXISTS` until SQLite 3.35; current code uses `_has_column` guard) |
| PostgreSQL | Same statement; PG also supports `IF NOT EXISTS` but we don't use it for parity |

**Approach:** Guard via `_columns_of(engine, table)` membership check before
ALTER. Identical statement on both backends.

### 5.2 Partial unique index

```sql
CREATE UNIQUE INDEX IF NOT EXISTS ix_<t>_node_uuid
    ON <t>(node_uuid) WHERE node_uuid IS NOT NULL
```

Both SQLite (since 3.8) and PostgreSQL support partial indexes with this exact
syntax. **No dialect dispatch needed.**

### 5.3 PK discovery

| Dialect | Approach |
|---|---|
| SQLite | `PRAGMA table_info(t)` + check `pk` flag (current code) |
| PostgreSQL | Query `pg_index` (low-level) |
| **Both (chosen)** | `sqlalchemy.inspect(engine).get_pk_constraint(t)["constrained_columns"]` |

**Approach:** Use SQLAlchemy reflection. Returns a list of column names; pyarchinit
tables have single-column PKs so `[0]` is the column name we need. Fall back to
`"rowid"` if the list is empty (preserves current SQLite fallback).

### 5.4 UPDATE with parameter binding

```python
# Current (sqlite3 ?-placeholder)
conn.execute(f"UPDATE {table} SET node_uuid = ? WHERE {pk_col} = ?", (uuid_str, row_id))

# New (SQLAlchemy text() with named params, works on both)
conn.execute(text(f"UPDATE {table} SET node_uuid = :uuid WHERE {pk_col} = :id"),
             {"uuid": uuid_str, "id": row_id})
```

`{table}` and `{pk_col}` are still f-string interpolated because SQLAlchemy
`text()` does not support identifier binding. **Safety:** `table` comes from the
hardcoded `TABLES` tuple, `pk_col` comes from SQLAlchemy Inspector — both are
trusted, no user input → no SQL injection vector.

### 5.5 Transactions

| Dialect | Today | Cross-backend |
|---|---|---|
| SQLite | `sqlite3.connect()` + `conn.commit()` (implicit transaction) | `engine.begin()` (explicit BEGIN..COMMIT) |
| PG | n/a | Same |

**Approach:** Wrap each step (`add_columns`, `backfill_uuids`) in
`with engine.begin() as conn:`. Failure auto-rollbacks. Migration becomes
atomic per step.

## 6. Data flow

### 6.1 Happy path (both backends)

```
QGIS menu "Migrazioni → Backfill node_uuid (UUID v7 per record)"
  → _run_uuid_backfill_migration() reads self.DB_MANAGER
  → if self.DB_MANAGER is None: error dialog → return
  → db_handle = _resolve_db_handle(self.DB_MANAGER)
  → confirm dialog: "Migrate <backend>: <path-or-slug>? Auto-backup will be
                     created at <backup_dest>"
  → user confirms
  → backup = auto_backup_sqlite(db_path, tag) if sqlite
             else auto_backup_postgres(engine, tag, dest_dir)
  → if backup is None and user chose Cancel: return
  → add_columns(db_handle):
      with engine.begin() as conn:
        for table in TABLES:  # us_table, inventario_materiali_table, periodizzazione_table
          if "node_uuid" not in _columns_of(engine, table):
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN node_uuid TEXT"))
          conn.execute(text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{table}_node_uuid "
                            f"ON {table}(node_uuid) WHERE node_uuid IS NOT NULL"))
  → backfill_uuids(db_handle) → counts dict:
      with engine.begin() as conn:
        for table in TABLES:
          pks = inspect(engine).get_pk_constraint(table)["constrained_columns"]
          pk_col = pks[0] if pks else "rowid"
          rows = conn.execute(text(f"SELECT {pk_col} FROM {table} "
                                    f"WHERE node_uuid IS NULL")).fetchall()
          for (row_id,) in rows:
            conn.execute(text(f"UPDATE {table} SET node_uuid = :uuid "
                               f"WHERE {pk_col} = :id"),
                         {"uuid": str(uuid7()), "id": row_id})
          counts[table] = len(rows)
  → success dialog: "Migrated <sum> rows across 3 tables"
```

### 6.2 Error scenarios

| Trigger | Behavior |
|---|---|
| Menu clicked, `self.DB_MANAGER is None` | `QMessageBox.warning("Connetti prima un DB pyarchinit dalle Settings")` |
| `pg_dump` not in PATH (PG only) | Dialog: "pg_dump not found. Proceed without auto-backup (not recommended)? [Skip backup] [Cancel]" |
| `pg_dump` invocation fails (auth, disk, etc.) | Log WARNING, show return code + stderr in dialog, options: "Proceed without backup" / "Cancel" |
| ALTER TABLE fails (lock, disk full) | Exception propagates; `engine.begin()` rolls back. Error dialog with truncated stack trace + path of backup if created |
| Backfill fails mid-table N | Tables 0..N-1 stay migrated (idempotent — partial unique index allows NULL co-existence). Rerun resumes at table N. Error dialog explains the idempotent restart |
| Concurrent QGIS session ingesting same DB | No explicit lock introduced. PG default isolation (READ COMMITTED) applies. Concurrency = DBA responsibility |
| CLI: both `--db` and `--conn-str` | argparse mutex error → exit 2 |
| CLI: neither | argparse required-arg error → exit 2 |
| CLI: `--conn-str sqlite://...` | Accepted (resolved via `_resolve_db_handle`) |

### 6.3 Concurrency — explicitly out of scope

PG-A introduces NO `LOCK TABLE` or `pg_advisory_lock`. Concurrency between
migration and ingest is a Phase 4 concern (SyncEngine + REST API for multi-user
access). The single-user case (~80% of pyarchinit deployments) does not benefit
from advisory locks while paying their rollback complexity cost.

## 7. Test strategy

### 7.1 Pyramid

| Level | File | New cases | Skip |
|---|---|---|---|
| L0 unit | `tests/migrations/test_node_uuid_backfill_cli.py` (extend) | 2-3 | None |
| L0 unit | `tests/migrations/test_node_uuid_backfill_lib_unit.py` (NEW) | 3 | None |
| L2 PG | `tests/sync/test_node_uuid_backfill_pg.py` (NEW) | 6 | `pg_engine` fixture skips when PG offline / psycopg2 missing |
| L1 SQLite | existing 245 tests | 0 added | All must stay green via backward-compat shim |

### 7.2 Six PG L2 test cases (pin the design)

| # | Test name | What it pins |
|---|---|---|
| 1 | `test_add_columns_idempotent_on_pg` | Run #1 adds 3 columns + 3 indexes; run #2 is no-op. Verifies via `_columns_of(engine, "us_table")`. |
| 2 | `test_backfill_uuids_assigns_uuid7_on_pg` | Inserts N rows with `node_uuid IS NULL`, runs backfill, verifies every row has a valid UUID v7 (regex + version byte). |
| 3 | `test_partial_unique_index_allows_null_collision` | Confirms `WHERE node_uuid IS NOT NULL` allows multiple NULLs (recovery from partial failures). |
| 4 | `test_pk_discovery_on_pg_via_inspector` | `Inspector.get_pk_constraint("us_table")["constrained_columns"]` returns `["id_us"]` (parity with SQLite). |
| 5 | `test_atomic_rollback_on_alter_failure` | Mocks `text()` to raise during ALTER. Verifies `engine.begin()` rolls back; no partial column added. |
| 6 | `test_auto_backup_postgres_invokes_pg_dump` | Mocks `subprocess.run`. Verifies argv (host, port, user, db, -f path), env contains `PGPASSWORD`, return path is in conn-slug dir. |

A 7th case (`test_auto_backup_postgres_when_pg_dump_missing`) lives in
`test_node_uuid_backfill_lib_unit.py` (mocks `shutil.which` → None, no DB
needed).

### 7.3 Decision-pinning matrix

| Decision | Test |
|---|---|
| Q1=a (single menu, no file picker) | Manual via QGIS — documented in dev-log |
| Q2=a+c (pg_dump or warning) | Test #6 (mocked pg_dump present) + L0 unit `test_auto_backup_postgres_when_pg_dump_missing` |
| Q3=a (`--conn-str` mutex `--db`) | CLI test extension `test_argv_db_and_conn_str_mutex` |
| Approach 1 (SQLAlchemy-everywhere) | All 6 PG L2 tests would fail without SQLAlchemy dispatch |
| Idempotency contract | Test #1 (`add_columns`) + test #2 (backfill skips already-UUID'd rows) |

### 7.4 Test count progression

- Pre PG-A (Foundation): 245 passed, 5 skipped
- Post PG-A, PG offline: **250-251 passed, 11 skipped** (5 Foundation skips + 6 PG-A L2 skips)
- Post PG-A, PG online + psycopg2: **256 passed, 5 skipped**

## 8. Acceptance criteria

| AC | Description |
|---|---|
| **AC-2** (existing) | Byte-identical export on `mini_volterra.sqlite` — preserved (no export-path changes) |
| **AC-15** (existing, AI07) | Toponym chain round-trip — preserved |
| **PG-A-AC-1** NEW | `add_columns(db_handle)` idempotent on both backends |
| **PG-A-AC-2** NEW | `backfill_uuids(db_handle)` assigns UUID v7 to all NULLs on PG |
| **PG-A-AC-3** NEW | Atomic rollback: failure mid-migration leaves DB in pre-migration state |
| **PG-A-AC-4** NEW | CLI `--db` / `--conn-str` mutex enforced via argparse |
| **PG-A-AC-5** NEW | `auto_backup_postgres` invokes `pg_dump` with correct argv when available |
| **PG-A-AC-6** NEW | `auto_backup_postgres` raises warning + exposes skip path if `pg_dump` missing |
| **PG-A-AC-7** NEW | All 245 existing SQLite tests stay green via backward-compat shim |
| **PG-A-AC-8** NEW | `GraphIngestor._verify_schema(db_path)` works on both backends via `_columns_of` |

## 9. Release plan

**Tag:** `phase3-pgcompat-a-migration-5.7.0-alpha`
**Predecessor:** `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
**Rollback safety tag:** `pre-pg-a-migration` (created in Group 0 of the plan)

### 9.1 Commit structure (proposed — ~9 commits)

| Group | Type | Commit |
|---|---|---|
| 0 | git | Pre-flight + rollback tag |
| A | refactor | `_2026_05_node_uuid_backfill_lib.py` cross-backend (lib + 3 L0 unit tests) |
| B | feature | `_common.py` + `auto_backup_postgres` + `parse_argv` mutex (+ extended CLI test) |
| C | refactor | `2026_05_node_uuid_backfill.py` CLI dispatch |
| D | refactor | `GraphIngestor._verify_schema` swap PRAGMA → `_columns_of` |
| E | feature | 6 PG L2 tests (`tests/sync/test_node_uuid_backfill_pg.py`) |
| F | feature | `pyarchinitPlugin.py:_run_uuid_backfill_migration` + `s3dgraphy_dot_bridge.py` shim |
| G | release | Bump 5.6.2-alpha → 5.7.0-alpha + bilingual CHANGELOG + dev-log Phase 3 entry |
| H | tag+push | Annotated tag + push |

### 9.2 Subagent batching for `subagent-driven-development`

- Group 0 → controller (no subagent)
- Groups A–G → 1 subagent each
- Group H → 1 subagent (gate for user approval before push)

### 9.3 Strict rules (inherited from Foundation)

- Zero `Co-Authored-By: Claude` trailers (memory feedback rule)
- AC-2 byte-identical guard green at every Group with code changes
- All 245 pre-existing SQLite tests green at every Group
- HEREDOC commit messages
- No `git add -A` or `git add .`

### 9.4 Memory snapshot post-ship

Update `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move PG-A from PENDING to SHIPPED
- Annotate any lessons learned (PK discovery via Inspector pattern, pg_dump
  cross-platform surprises, etc.)

Update `MEMORY.md` index line to reflect new CURRENT STATE.

### 9.5 Time estimate

Parent spec estimated ~1 week. Via subagent-driven-development: ~2-3h execution
+ ~1h review + memory update. End-to-end from spec approval to tag pushed
should be a single session.

## 10. References

- Foundation spec: `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.2
- Foundation plan (executed): `docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md`
- Foundation tag: `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
- Predecessor migration spec: parent design §4.5 (Phase 1 SQLite-only ship)
- Memory: `project_pg_compat_progress.md` — current state of Phase 3
- Memory: `feedback_no_claude_coauthor.md` — strict commit rule
