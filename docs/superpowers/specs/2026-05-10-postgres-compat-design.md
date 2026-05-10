# PostgreSQL compatibility for the s3dgraphy bridge layer

**Status:** design approved (2026-05-10)
**Predecessor tag:** `phase2-ai07-hotfix-5.6.1-alpha` + commit `24377960` (Struttura sigla_estesa fix)
**Foundation tag (Settimana 0):** `phase3-pgcompat-shim-5.6.2-alpha`
**Milestone tags:**
- `phase3-pgcompat-a-migration-5.7.0-alpha`
- `phase3-pgcompat-b-export-5.7.1-alpha`
- `phase3-pgcompat-c-import-5.7.2-alpha`
- `phase3-pgcompat-d-paradata-5.7.3-alpha`
- `phase3-pgcompat-consolidation-5.7.4-alpha`

**Branch:** `Stratigraph_00001` (per-milestone feature branches off this)
**Working directory:** `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit`

## 1. Goal

Refactor the s3dgraphy bridge layer (`modules/s3dgraphy/sync/` + supporting migration scripts and dialog handlers) to support **both** SQLite/Spatialite **and** PostgreSQL/PostGIS backends with a single code path, while preserving:

- AC-2 byte-identical regression guard on `mini_volterra.sqlite`
- AI04/AI06/AI07 round-trip identity invariants (us_table preservation across export → re-import)
- The PR #6 round-trip integration suite (consumer of pyarchinit from the s3dgraphy fork)
- The Git-versionable file-based ParadataStore + GroupStore model from AI05/AI06
- All 234 existing tests post-5.6.1-alpha (no regression)

The bridge currently uses `sqlite3.connect()` directly throughout — it is SQLite-only by AI04 spec design choice. The pyarchinit "tab" controllers are already backend-agnostic via `pyarchinit_db_manager` (SQLAlchemy-based). This spec extends backend agnosticism to the bridge.

## 2. Background

### 2.1 Current state

- **Bridge files using `sqlite3` directly**: `graph_projector.py` (8 calls), `graph_ingestor.py` (3 calls), `graphml_writer.py` (1 call), `group_projector.py` (2 calls). Total: 14 sites across 4 files.
- **Migration scripts**: `scripts/migrations/2026_05_node_uuid_backfill.py` and its `_lib` use `sqlite3` directly. 5 sites.
- **Dialog gating**: `S3DGraphyExportDialog.on_export` checks `db_manager.get_sqlite_path()` — returns None on PG → bridge silently unavailable. Error message at `s3dgraphy_dot_bridge.py:205`: "postgresql backend not yet supported".
- **`pyarchinit_db_manager`** is already SQLAlchemy-based: uses `create_engine`, `engine.connect()`, `engine.begin()`, detects backend from `conn_str.startswith("sqlite")` / `conn_str.startswith("postgresql")`. The infrastructure to support PG is already there at the manager level — only the bridge has the gap.
- **No PostGIS / Spatialite calls in the bridge**: only plain SQL on text columns. PostGIS is not a concern for this refactor.
- **No SQLite-only SQL syntax** in the bridge: no `INSERT OR IGNORE`, no `PRAGMA` outside `_verify_schema`. Parameter binding (`?`) and `PRAGMA table_info` are the only dialect-specific call sites.

### 2.2 User feedback that triggered this work

> "assicurati che queste task che stiamo facendo siano funzionanti anche con postgres non solo con sqlite"

User confirmed (2026-05-10):
- Local PostgreSQL at `localhost:5433`, user `postgres`, password `postgres`
- Test database to be created: `pyarchinit_test_pg`
- Workspace dir for `groups_*.graphml` / `paradata_*.graphml` on PG: configurable (Q3=b), default to `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/`

### 2.3 Brainstorm decisions (this session)

- **Q1 scope = (b) incremental**: 4 milestones (A migration / B export / C import / D paradata) + foundation
- **Q2 approach = (A) SQLAlchemy with backward-compat shim**: signatures change from `db_path: Path` to `db_handle` argument that accepts Path | str | DbManager | Engine. Path → SQLite engine + DeprecationWarning.
- **Q3 file location = (b) workspace dir configurable**: `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/` as PG default, override via QSettings `pyarchinit/paradata_workspace`. SQLite path unchanged.
- **Q4 test strategy = local PG**: connect to existing `localhost:5433` PG with `postgres/postgres`, install `pyarchinit_test_pg` test DB, conftest fixture skips cleanly if PG offline.

## 3. Architecture

### 3.1 Compatibility shim

```
┌────────────────────────────────────────────────────────────────┐
│  CALLERS (dialog, CLI, tests, PR#6 fixture, future AI09 hooks) │
│   Pass: db_path: Path                                          │
│   OR    db_manager: DbMgr                                      │
│   OR    engine: Engine                                         │
│   OR    db_handle: DbHandle                                    │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   COMPATIBILITY SHIM                            │
│  _resolve_db_handle(arg) -> DbHandle                            │
│   - Path → SQLite engine via create_engine(f"sqlite:///{p}")    │
│           + DeprecationWarning                                  │
│   - str  → if starts with "sqlite:" or "postgresql:"            │
│           create_engine(arg). Otherwise raise ValueError        │
│   - DbManager → use existing .engine, detect backend            │
│   - Engine → wrap as-is                                         │
│   - DbHandle → idempotent passthrough                           │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BRIDGE LAYER (refactored)                      │
│   GraphProjector / GraphIngestor / GraphMLWriter / GroupStore   │
│                                                                 │
│   All SQL via SQLAlchemy text() + named params (:name)          │
│   Transactions via `with engine.begin() as conn: ...`           │
│   Backend-agnostic — same code runs on SQLite + PG              │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
        SQLAlchemy engine (sqlite:/// or postgresql+psycopg2://)
```

### 3.2 `DbHandle` value object

```python
# modules/s3dgraphy/sync/_db_handle.py
@dataclass(frozen=True)
class DbHandle:
    engine: Engine                      # Always set
    is_postgres: bool
    sqlite_path: Path | None            # Set only when backend is SQLite
    conn_str: str                       # Original conn string for slug derivation

    @classmethod
    def from_path(cls, p: Path) -> "DbHandle":
        engine = create_engine(f"sqlite:///{p}")
        return cls(engine=engine, is_postgres=False, sqlite_path=p,
                   conn_str=f"sqlite:///{p}")

    @classmethod
    def from_engine(cls, engine: Engine, conn_str: str) -> "DbHandle":
        is_pg = engine.dialect.name == "postgresql"
        sqlite_path = (Path(conn_str.replace("sqlite:///", ""))
                       if conn_str.startswith("sqlite:") else None)
        return cls(engine=engine, is_postgres=is_pg, sqlite_path=sqlite_path,
                   conn_str=conn_str)
```

### 3.3 Four-milestone progression

| Milestone | Tag | Scope | Effort |
|---|---|---|---|
| **Foundation** | `phase3-pgcompat-shim-5.6.2-alpha` | `_db_handle.py` + `_resolve_db_handle()` + new exceptions, no caller changes | small (~3 days) |
| **PG-A** | `phase3-pgcompat-a-migration-5.7.0-alpha` | Phase 1 `node_uuid` backfill works on PG | small (~1 week) |
| **PG-B** | `phase3-pgcompat-b-export-5.7.1-alpha` | Projector + GraphMLWriter read from PG | medium (~2 weeks) |
| **PG-C** | `phase3-pgcompat-c-import-5.7.2-alpha` | Ingestor writes to PG with atomic transactions | large (~3 weeks) |
| **PG-D** | `phase3-pgcompat-d-paradata-5.7.3-alpha` | ParadataStore + GroupStore workspace dir on PG | medium (~1 week) |
| **Consolidation** | `phase3-pgcompat-consolidation-5.7.4-alpha` | Polish, deprecation warnings cleanup, parametrized test promotion | small (~1 week) |

Each milestone is a single tag + PR locally on `Stratigraph_00001`. Foundation must ship first; milestones A-D can in principle ship in parallel after foundation, but recommended sequence is A → B → C → D for incremental risk reduction.

## 4. File-by-file change plan

### 4.1 Foundation (`5.6.2-alpha`) — shim + new exceptions

| Path | Change | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/_db_handle.py` | NEW — `DbHandle` dataclass, `_resolve_db_handle()`, `_columns_of()` helpers, exceptions | ~80 |
| `modules/s3dgraphy/sync/__init__.py` | Re-export `DbHandle` for callers | ~5 |
| `tests/sync/test_db_handle_shim.py` | NEW — unit tests for shim resolution paths (Path, str, DbManager, Engine) | ~80 |
| `tests/sync/conftest_pg.py` | NEW — `pg_engine` session fixture, `clean_pg` function fixture, schema bootstrap helper | ~80 |
| `requirements.txt` | Add `psycopg2-binary>=2.9` (was implicit dep via SQLAlchemy already) | 1 |
| `metadata.txt` | Bump `5.6.1-alpha` → `5.6.2-alpha` | 1 |
| `dev_logs/CHANGELOG.md` | New `[5.6.2-alpha]` bilingual entry | ~30 |

**No caller changes** — Foundation introduces machinery without using it. Test count: 234 → ~244 (10 new shim unit tests).

### 4.2 PG-A — Phase 1 migration (`5.7.0-alpha`)

| Path | Change | LOC |
|---|---|---|
| `scripts/migrations/_2026_05_node_uuid_backfill_lib.py` | Replace `sqlite3.connect(db_path)` with `db_handle.engine.begin()`. `add_columns` + `backfill_uuids` accept `DbHandle`. PG dialect: `ALTER TABLE x ADD COLUMN IF NOT EXISTS y` (works on both) | ~100 |
| `scripts/migrations/2026_05_node_uuid_backfill.py` | CLI script: accept `--db <sqlite_path>` OR `--conn-str postgresql://...` | ~30 |
| `scripts/migrations/_common.py` | Add `auto_backup_postgres(engine, tag)` wrapper for `pg_dump`. Keep existing `auto_backup_sqlite`. | ~40 |
| `pyarchinitPlugin.py` | `_run_uuid_backfill_migration` uses `self.DB_MANAGER` if set, falls back to file picker for SQLite. | ~20 |
| `modules/s3dgraphy/s3dgraphy_dot_bridge.py` | `_offer_node_uuid_migration` accepts both Path and DbManager via shim | ~15 |
| `tests/sync/test_node_uuid_backfill_pg.py` | NEW — verify migration on PG via `pg_engine` fixture | ~80 |

Test count: ~244 → ~250.

### 4.3 PG-B — Export pipeline (`5.7.1-alpha`)

| Path | Change | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | 8 `sqlite3.connect()` → `engine.connect()` / `engine.begin()`. SQL queries to use `text(":name")` params. Sites: `_emit_toponym_chain`, `_propagate_node_uuid_and_us`, `_merge_groups` (the `node_uuid_to_id` lookup), `populate_graph` signature change to accept `db_handle` (with shim) | ~150 |
| `modules/s3dgraphy/sync/group_projector.py` | 2 `sqlite3.connect()` (in `dimensions_with_data` + `build_groups_from_sql`) → engine-based; signatures change | ~40 |
| `modules/s3dgraphy/sync/graphml_writer.py` | 1 `sqlite3.connect()` (in `_read_first_sito`) → engine-based. `export_graphml` signature accepts `db_handle` | ~30 |
| `tests/sync/test_export_pg.py` | NEW — projector reads from PG, structural fingerprint matches SQLite version | ~120 |
| `tests/sync/test_ai03_export_pg_structural.py` | NEW — AC-2 cousin: PG export structural fingerprint == SQLite fingerprint | ~80 |

Test count: ~250 → ~265.

### 4.4 PG-C — Import pipeline (`5.7.2-alpha`)

| Path | Change | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | 3 `sqlite3.connect()` → engine-based. `populate_list` rewrite of: `_verify_schema`, `_apply_group_folders_to_sql`, atomic transaction via `with engine.begin()`. INSERT/UPDATE statements: param style `?` → `:name`. SchemaMismatchError detection: `_columns_of()` dispatches on dialect. | ~250 |
| `tests/sync/test_import_pg.py` | NEW — ingestor writes to PG, AC-15 round-trip identity verified | ~150 |
| `tests/sync/test_recursive_walker_pg.py` | NEW — recursive walker test on PG | ~80 |
| `tests/integration/pyarchinit_roundtrip_pg/` | NEW directory mirroring PR #6 structure but for PG (own pyarchinit-side, not pushed to s3dgraphy fork yet) | ~150 |

Test count: ~265 → ~285.

### 4.5 PG-D — ParadataStore + GroupStore (`5.7.3-alpha`)

| Path | Change | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/_workspace.py` | NEW — `_resolve_paradata_dir(db_handle, sito) -> Path` + `_conn_slug(db_handle)` | ~80 |
| `modules/s3dgraphy/sync/paradata_store.py` | Constructor accepts `db_handle`. `file_path` resolves via `_resolve_paradata_dir`. Backward-compat shim for `db_path: Path`. | ~60 |
| `modules/s3dgraphy/sync/group_store.py` | Same as above | ~50 |
| `gui/pyarchinitConfigDialog.py` | New section "Paradata Workspace" → QSettings `pyarchinit/paradata_workspace` | ~40 |
| `tests/sync/test_paradata_store_pg.py` | NEW | ~80 |
| `tests/sync/test_group_store_pg.py` | NEW | ~80 |

Test count: ~285 → ~300.

### 4.6 Consolidation (`5.7.4-alpha`)

- Promote parametrized backend tests (where useful) to cover SQLite + PG consistently
- Cleanup deprecation warnings in test config (after a grace period)
- Documentation passes (tutorials + API docs regen)

### 4.7 Total LOC + files

- Production LOC: ~930 (across 4 milestones + foundation)
- Test LOC: ~670
- Files touched: ~22 (11 new files)

### 4.8 Out of scope

- **PostGIS / Spatialite geometry**: bridge does not touch geometry. Deferred unless future requirement.
- **MySQL/MariaDB**: not requested.
- **Schema migration via Alembic**: current pyarchinit migration scripts use plain `ALTER TABLE`. Alembic adoption is a separate concern.
- **AI09 EM-import improvements**: independent track. Awaits 0.1.42/1.5.0 ship from Emanuel before brainstorming.
- **PR #6 fork integration of PG tests**: deferred until PG-D ships. The fork remains SQLite-only for now.

## 5. SQL dialect compatibility

### 5.1 Operations and portability

| Operation | SQLite | PostgreSQL | Strategy |
|---|---|---|---|
| Add column | `ALTER TABLE x ADD COLUMN y TEXT` | `ALTER TABLE x ADD COLUMN IF NOT EXISTS y TEXT` (PG ≥9.6) | Pre-check via `_columns_of()`, only ADD if missing |
| Schema introspection | `PRAGMA table_info(t)` | `SELECT column_name FROM information_schema.columns WHERE table_name=:t` | Dispatch on `engine.dialect.name` in `_columns_of()` |
| Last insert ID | `cur.lastrowid` | `RETURNING id_us` | Use SQLAlchemy `Insert.returning()` (portable from 1.4+) |
| Atomic transaction | `with conn:` (auto-commit) | `BEGIN ... COMMIT` | `with engine.begin() as conn:` (works on both) |
| Boolean column | INTEGER 0/1 | BOOLEAN true/false | Avoid bool in raw SQL — use INT |
| Insert + ignore conflict | `INSERT OR IGNORE` | `INSERT ... ON CONFLICT DO NOTHING` | Not currently used in bridge — skip |
| Substr / instr | `SUBSTR`, `INSTR` | `SUBSTRING`, `POSITION` | Not used in bridge — skip |
| Parameter binding | `?` (positional) | `%s` (psycopg2) or `:name` (SQLAlchemy) | Use SQLAlchemy `text(":name")` — portable |

### 5.2 Bridge SQL audit

Already audited: bridge uses `INSERT INTO us_table`, `INSERT INTO site_table`, `INSERT INTO periodizzazione_table`, `UPDATE us_table SET ... WHERE ...`, `SELECT ... FROM us_table WHERE ...`. **All portable.** Only the parameter style and the `PRAGMA` introspection are dialect-specific.

## 6. Error handling

### 6.1 New exceptions

```python
# modules/s3dgraphy/sync/_db_handle.py

class DbHandleError(GraphSyncError):
    """Failure resolving a db_handle argument."""

class UnsupportedBackendError(DbHandleError):
    """Conn string dialect not in {sqlite, postgresql}."""

class PgConnectionError(DbHandleError):
    """PG engine constructed but TCP connection failed."""
```

### 6.2 Error mapping per backend

| Error | SQLite | PostgreSQL | Uniform strategy |
|---|---|---|---|
| Table missing | `sqlite3.OperationalError("no such table: us_table")` | `psycopg2.errors.UndefinedTable` | Catch via SQLAlchemy `exc.OperationalError` / `exc.ProgrammingError`; uniform message |
| Column missing | `OperationalError("no such column: node_uuid")` | `UndefinedColumn` | Catch + raise existing `SchemaMismatchError` |
| Lock contention | `database is locked` | `LockNotAvailable` (rare) | Retry once with backoff, then raise |
| Constraint violation | `IntegrityError("UNIQUE constraint failed")` | `IntegrityError("duplicate key")` | Catch + classify into existing `IngestConflictError` |
| Connection refused | (irrelevant: SQLite file missing) | `OperationalError("could not connect")` | Caught by shim at `DbHandle` creation → `PgConnectionError` with friendly message |
| Permission denied | `PermissionError` (file system) | `OperationalError("permission denied for table")` | Friendly message at first `engine.connect()` |

### 6.3 Atomic transaction guarantee (AI04 contract)

```python
with engine.begin() as conn:    # auto-rollback on exception
    conn.execute(...)
    conn.execute(...)
# auto-COMMIT here if no exception
```

SQLite has autocommit by default; PG does not. Using `engine.begin()` (NOT `engine.connect()`) in **every write path** in the bridge guarantees identical semantics on both backends.

### 6.4 Migration backup safety (PG-A)

| Backend | Backup mechanism |
|---|---|
| SQLite | Existing `auto_backup_sqlite()` — copies `.sqlite` → `.sqlite.backup_<ts>` |
| PG | NEW `auto_backup_postgres(engine, tag)` — wrapper over `pg_dump`. Path: `<workspace>/<conn_slug>_<dbname>.sql.backup_<ts>` |

If `pg_dump` is not installed → warning dialog, user chooses to proceed without backup (logged) or cancel.

## 7. Test strategy

### 7.1 Test pyramid

| Level | Backend | When to use |
|---|---|---|
| L0 unit (no DB) | mock | Logic in `_resolve_db_handle()`, `_columns_of()`, `_resolve_paradata_dir()` |
| L1 SQLite | SQLite | Existing 234 tests via shim. No rewrites needed |
| L2 PG-only | PG fixture | Logic specific to PG: `information_schema`, `pg_dump`, `RETURNING` clauses |
| L3 parametrized | both | Critical invariants: round-trip identity, AC-15, atomic rollback |
| L4 integration | PG | End-to-end: migrate fresh PG → ingest → export → re-import → identity |

### 7.2 PG fixture lifecycle

```python
# tests/sync/conftest_pg.py

@pytest.fixture(scope="session")
def pg_engine():
    """Skip cleanly if PG unreachable."""
    conn_str = "postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg"
    try:
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"PG not available at localhost:5433 ({e})")
    _apply_pyarchinit_schema(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def clean_pg(pg_engine):
    with pg_engine.begin() as conn:
        conn.execute(text("TRUNCATE us_table, site_table, periodizzazione_table CASCADE"))
    yield pg_engine
```

### 7.3 Existing test backward compat

All 234 SQLite tests post-5.6.1 continue to pass via the shim. The path-based `db_path: Path` argument is accepted in every public bridge method and resolved through `_resolve_db_handle()`.

Deprecation warning for `db_path: Path` callers is silenced in test config to avoid flooding output.

### 7.4 AC-2 + round-trip preservation matrix

| Test | Pre-PG-A | Post-PG-A | Post-PG-B | Post-PG-C | Post-PG-D |
|---|---|---|---|---|---|
| `test_ai03_export_byte_identical.py` (AC-2) | ✓ | ✓ | ✓ | ✓ | ✓ |
| `test_round_trip_with_groups.py` | ✓ | ✓ | ✓ | ✓ | ✓ |
| Round-trip identity AI04 / AI06 / AI07 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 234 SQLite tests | ✓ | ✓ | ✓ | ✓ | ✓ |
| **NEW** PG migration test | — | ✓ | ✓ | ✓ | ✓ |
| **NEW** PG export structural fingerprint | — | — | ✓ | ✓ | ✓ |
| **NEW** PG round-trip identity | — | — | — | ✓ | ✓ |
| **NEW** PG paradata workspace | — | — | — | — | ✓ |

## 8. Acceptance criteria

| AC | Description |
|---|---|
| **AC-2** (existing, must stay green) | byte-identical fingerprint on `mini_volterra.sqlite` |
| **AC-15** (existing, AI07) | toponym chain round-trip identity |
| **PG-AC-1 NEW** | `_resolve_db_handle()` resolves all 5 input types correctly |
| **PG-AC-2 NEW** | UUID7 backfill migration runs to completion on a fresh PG DB |
| **PG-AC-3 NEW** | Export from PG with same data as SQLite produces structural fingerprint equality |
| **PG-AC-4 NEW** | Import to PG: us_table identity preserved after no-op re-import (PG round-trip) |
| **PG-AC-5 NEW** | Atomic rollback: forced exception mid-import leaves PG us_table unchanged |
| **PG-AC-6 NEW** | ParadataStore + GroupStore resolve workspace dir per Q3=b logic on both backends |
| **PG-AC-7 NEW** | All 234 existing SQLite tests pass post-foundation (no regression) |
| **PG-AC-8 NEW** | Deprecation warning emitted for `db_path: Path` callers (visible in pytest, silenced in actual user runs) |

## 9. Release plan

```
Settimana 0   →  Foundation (5.6.2-alpha): shim + DbHandle + tests + spec doc commit
Settimana 1-2 →  PG-A migration (5.7.0-alpha)
Settimana 3-5 →  PG-B export (5.7.1-alpha)
Settimana 6-8 →  PG-C import (5.7.2-alpha)  ← biggest
Settimana 9-10 →  PG-D paradata + workspace UI (5.7.3-alpha)
Settimana 11   →  consolidation (5.7.4-alpha)
```

Each milestone:
1. Foundation must ship first; PG-A through PG-D can in principle ship in parallel after, but recommended sequential A → B → C → D.
2. Each milestone is a single tag; AC-2 + 234 SQLite test suite must stay green at every milestone.
3. Manual smoke gate before each tag: open QGIS with a real PG DB at `localhost:5433`, exercise the milestone's user-facing code path, confirm.

## 10. Coordination with concurrent work

| Concurrent track | Strategy |
|---|---|
| **Emanuel PR #6 merge** (in pending review) | No file overlap. Continues independently |
| **s3dgraphy 0.1.42 → 1.5.0** (1-2 weeks Emanuel) | Bump `requirements.txt s3dgraphy>=1.5,<2` during foundation or PG-A. Verify AC-2 still green |
| **AI09 EM-import improvements** (deferred) | Independent. Can run pre or post PG-D depending on user priority |
| **RSF support** (post-0.1.42 deliverable) | Part of AI09. Independent from PG compat |

## 11. Memory snapshots

`project_pg_compat_progress.md` updated at each milestone tag with: tag SHA, test count delta, files modified, open carry-overs. At consolidation ship, archive as `project_pg_compat_shipped.md`.

## 12. References

- AI04 spec (parent): `docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md`
- AI07 spec (predecessor): `docs/superpowers/specs/2026-05-09-ai07-locationnodegroup-design.md`
- pyarchinit DB manager: `modules/db/pyarchinit_db_manager.py`
- Memory note: `~/.claude/projects/.../memory/project_ai07_post_release.md`
