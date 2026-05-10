# PG-B — Export pipeline on PostgreSQL (5.7.1-alpha)

> **Spec source of truth.** Brainstormed 2026-05-10 after PG-A (5.7.0-alpha)
> shipped. This spec is the contract for the implementation plan that follows
> via `superpowers:writing-plans`.

**Status:** Approved 2026-05-10
**Predecessor:** `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
**Target tag:** `phase3-pgcompat-b-export-5.7.1-alpha`
**Parent spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.3

---

## 1. Goal

Make the s3dgraphy bridge's **export pipeline** — `GraphProjector` (the
SQLite-to-Graph converter) + `GraphMLWriter` (the Graph-to-GraphML serializer)
+ `GroupProjector` (the spatial-dimensions side-projection) — work on both
SQLite and PostgreSQL backends. Reuses `DbHandle` + `_resolve_db_handle` +
`_columns_of` from Foundation, and the public-API-with-shim pattern from PG-A.
The 11 `sqlite3.connect()` call sites (8 in `graph_projector.py`, 2 in
`group_projector.py`, 1 in `graphml_writer.py`) are the only production code
touched.

**PG-B is bounded.** Production code paths for import (PG-C: `populate_list`),
paradata persistence (PG-D), and consolidation (5.7.4-alpha) stay SQLite-only
and ship in subsequent milestones.

## 2. Background

`GraphProjector` is the entry point of the export side of the bridge. It reads
pyarchinit's SQL tables, constructs an in-memory `s3dgraphy.Graph`, and hands
it to `GraphMLWriter` which serializes to disk as yEd-compatible GraphML.
`GroupProjector` is a side-projection invoked during `populate_graph` to build
spatial-dimension `LocationNodeGroup` folders (the AI07 feature).

Today the pipeline is SQLite-only. The 11 `sqlite3.connect()` call sites are
scattered across:

- `graph_projector.py:299, 366, 508, 756, 872` — read queries for US,
  site_table, periodizzazione, group folder lookups
- `graph_projector.py:_propagate_node_uuid_and_us` — UPDATEs node_uuid
  back into us_table after projection
- `group_projector.py:93` (`dimensions_with_data`) — reads which dimensions
  have populated US rows
- `group_projector.py:133` (`build_groups_from_sql`) — reads the per-dimension
  groupings for AI06/AI07 folders
- `graphml_writer.py:136` (`_read_first_sito`) — reads the first sito name
  for fallback when no `sito` is passed

Foundation (5.6.2-alpha) shipped the machinery; PG-A (5.7.0-alpha) flipped the
migration script as the first production caller. PG-B is the second production
caller flip — the export pipeline.

## 3. Architectural decisions (from brainstorming 2026-05-10)

### 3.1 Q1 — Public API signature strategy

**Decision:** Approach (a) — keep the `db_path` keyword name on public APIs,
accept `Path | DbHandle | str` via `_resolve_db_handle()` shim. PG-A precedent.

- `GraphProjector.populate_graph(db_path, sito, ...)` — `db_path` accepts shim
- `export_graphml(db_path, mapping, output_path, ...)` — `db_path` accepts shim
- `GroupProjector.dimensions_with_data(db_path, sito)` — `db_path` accepts shim
- `GroupProjector.build_groups_from_sql(db_path, sito, graph, ...)` — same

**Rationale:** Zero refactoring noise on AC-2 test, on round-trip CI fixture
suite (PR #6 with Emanuel), and on the QGIS-side bridge dialog callers. The
parameter name `db_path` becomes mildly misleading (now accepts more than a
Path) but the docstring will document the accepted types. Consolidation
(5.7.4-alpha) may rename to `db_input` at the end of Phase 3 with a clean
deprecation cycle.

### 3.2 Q2 — Test strategy for "PG export structural fingerprint"

**Decision:** Approach (a) — build a `load_sqlite_into_pg(sqlite_path, pg_engine)`
helper in `conftest_pg.py` that mirrors the SQLite schema and copies all rows
into PG. Used by a new `pg_with_volterra` fixture for the AC-2 cousin test.

**Rationale:** `mini_volterra.sqlite` (30KB committed fixture) is the source
of truth for the AC-2 structural baseline. To test that PG produces the same
fingerprint, PG must contain the same data. The helper is generic and reusable
across PG-C (import tests) and PG-D (paradata tests). Synthetic mini-datasets
would not pin the AC-2 cousin contract.

### 3.3 Decomposition approach

**Decision:** Approach 1 — per-file Groups (~8 commits).

- A: `graph_projector.py` (8 sites, ~150 LOC delta)
- B: `group_projector.py` (2 sites, ~40 LOC delta)
- C: `graphml_writer.py` (1 site + signature change, ~30 LOC delta)
- D: `conftest_pg.py` helper + fixture (~50 LOC new)
- E: `test_export_pg.py` (5 PG L2 cases, ~120 LOC new)
- F: `test_ai03_export_pg_structural.py` (AC-2 cousin, ~80 LOC new)
- G: docs + version bump
- H: tag + push

**Rationale:** File-cohesion. Per-method splitting inside `graph_projector.py`
would proliferate commits (boilerplate per AC-2 ping). Big-bang would
concentrate AC-2 risk. Per-file is the middle ground; if AC-2 breaks in Group
A, the bisect surface is one class, one commit, ~150 LOC.

### 3.4 SQLAlchemy version constraint

Production `requirements.txt` mandates `SQLAlchemy>=2.0.0`. The dev env may
have older versions (e.g., 1.4) installed for testing legacy paths. The
refactor MUST be SQLAlchemy 2.0-compliant; 1.4 backward compat is incidental.

- `text()` + named params (`:name` + dict) works identically on 2.0 and 1.4
- `engine.begin()` / `engine.connect()` API identical
- `Inspector.get_pk_constraint()` identical
- `engine.execute(...)` legacy API (removed in 2.0) **MUST NOT** be used
- `bind=` legacy param **MUST NOT** be used
- 2.0 future-mode "execution options" do not require pattern changes

## 4. File-by-file change plan

### 4.1 Modified production files

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | 8 `sqlite3.connect()` → `engine.connect()` (read-only) / `engine.begin()` (read+write). SQL queries: `?` placeholder → `:name` named params via `text()`. All `except sqlite3.Error` → `except Exception`. `populate_graph(db_path, ...)` and internal helpers accept `Path \| DbHandle \| str` via `_resolve_db_handle`. **No SQL query changes** — only connection wrapping + placeholder syntax. | ~150 |
| `modules/s3dgraphy/sync/group_projector.py` | 2 `sqlite3.connect()` sites (`dimensions_with_data`, `build_groups_from_sql`) → engine-based. Both public functions accept `DbHandle \| Path \| str` via shim. | ~40 |
| `modules/s3dgraphy/sync/graphml_writer.py` | 1 `sqlite3.connect()` (`_read_first_sito` at line 136) → engine-based. `export_graphml(db_path, mapping, output_path, ...)` accepts shim. Internal call at line ~1796-1800 (`GraphProjector().populate_graph(...)`) passes through `DbHandle` instead of `Path`. | ~30 |

### 4.2 Modified test infrastructure

| Path | Change | LOC delta |
|---|---|---|
| `tests/sync/conftest_pg.py` | Add `load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper (~50 LOC). Reflects SQLite schema via `sqlalchemy.inspect(sqlite_engine)`, emits `CREATE TABLE IF NOT EXISTS` on PG with TEXT/INTEGER type mapping, `TRUNCATE ... RESTART IDENTITY CASCADE`, then `executemany` INSERT. Idempotent. Add `pg_with_volterra` fixture wrapping it. | ~50 |

### 4.3 New test files

| Path | Purpose | LOC |
|---|---|---|
| `tests/sync/test_export_pg.py` | 4-5 L2 PG cases: `populate_graph` on PG returns valid Graph; `node_uuid` propagation; toponym chain emission; `dimensions_with_data`; `export_graphml` end-to-end. Skips cleanly when PG offline. | ~120 |
| `tests/sync/test_ai03_export_pg_structural.py` | 1 case: AC-2 cousin. PG export of mini_volterra produces same structural fingerprint as `mini_volterra_baseline_ai03.graphml`. Reuses `_structure()` from the existing AC-2 test. **THE gate for PG-B**. | ~80 |

### 4.4 Modified release-tracking files

| Path | Change | LOC delta |
|---|---|---|
| `metadata.txt` | Bump `5.7.0-alpha` → `5.7.1-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.1-alpha]` section. | ~40 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 — PG-B export section. | ~30 |

### 4.5 Files explicitly NOT touched (per spec §4.4 of parent)

- `modules/s3dgraphy/sync/graph_ingestor.py:populate_list` — main import flow (PG-C)
- `modules/s3dgraphy/sync/paradata_store.py` (PG-D)
- `modules/s3dgraphy/sync/group_store.py` (PG-D)
- `modules/s3dgraphy/sync/_db_handle.py` (Foundation — no changes)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2 itself — must stay
  green untouched; only its `_structure()` helper is imported by the PG cousin)
- All other 250 SQLite tests — must stay green via the backward-compat shim
- PR #6 round-trip fixture (Emanuel's repo) — no changes required

### 4.6 Total LOC

- Production code: ~220 modified
- Test code: ~250 (helper + 2 new files)
- Docs: ~70 (CHANGELOG + dev-log)
- **Grand total: ~540 LOC**

## 5. SQL dialect compatibility

### 5.1 Connection management

| SQLite (today) | Cross-backend (PG-B) |
|---|---|
| `conn = sqlite3.connect(str(db_path))` | `with handle.engine.connect() as conn:` (read-only) |
| `conn.commit()` (after INSERT/UPDATE) | `with handle.engine.begin() as conn:` (auto-commit on exit) |
| `cur.execute(sql, (params,))` | `conn.execute(text(sql_with_named_params), {"key": value})` |
| `try/except sqlite3.Error` | `try/except Exception` (broader; SQLAlchemy + psycopg2 raise OperationalError, DBAPIError, ProgrammingError) |
| `finally: conn.close()` | (context manager handles close) |

### 5.2 Query placeholder syntax

Current SQLite queries use `?` positional placeholders:

```python
cur.execute("SELECT ... WHERE sito = ?", (sito,))
```

PG-B replaces with SQLAlchemy `text()` named params:

```python
conn.execute(text("SELECT ... WHERE sito = :sito"), {"sito": sito})
```

**Safety:** Both backends parse `:name` parameters identically through
SQLAlchemy. No SQL injection vector — all values are bound, not interpolated.

### 5.3 Query content unchanged

The 11 sites' actual SQL strings (`SELECT ... FROM us_table WHERE ...`,
etc.) are NOT modified. Only the connection wrapping + placeholder syntax
changes. This is the single most important AC-2 risk-reduction rule:

- No new `ORDER BY` clauses
- No new `JOIN`s
- No new column selections
- No SQLite-specific function calls (`strftime`, `julianday`, `printf`)
  expected — would be flagged during refactor

If a SQLite-specific function is discovered → STOP that Group, surface to
brainstorming for cross-dialect equivalent. Not anticipated for pyarchinit's
simple SELECT/UPDATE pattern.

### 5.4 SELECT result row access

| SQLite (today) | Cross-backend (PG-B) |
|---|---|
| `cur.fetchall()` → list of tuples | `.fetchall()` → list of `Row` objects (SQLAlchemy 2.0) |
| `row[0]`, `row[1]` — positional | `row[0]`, `row[1]` — positional (Row supports this) |
| `cur.description` for column names | `result.keys()` for column names |

Most pyarchinit code accesses results positionally → no changes needed. If a
site uses `cur.description`, refactor to `.keys()`.

## 6. Data flow

### 6.1 Pattern A — Read-only query (most sites)

```
[before]                              [after PG-B]
conn = sqlite3.connect(str(db_path))  handle = _resolve_db_handle(db_path)
try:                                  try:
    cur = conn.cursor()                 with handle.engine.connect() as conn:
    cur.execute("SELECT ... ?",            rows = conn.execute(
                (sito,))                       text("SELECT ... :sito"),
    rows = cur.fetchall()                      {"sito": sito},
except sqlite3.Error as e:                 ).fetchall()
    raise GraphProjectorError(e)      except Exception as e:
finally:                                  raise GraphProjectorError(e)
    conn.close()
```

### 6.2 Pattern B — Read + write (e.g., _propagate_node_uuid_and_us)

```
with handle.engine.begin() as conn:
    rows = conn.execute(
        text("SELECT id_us FROM us_table WHERE sito=:sito"),
        {"sito": sito},
    ).fetchall()
    for (id_us,) in rows:
        conn.execute(
            text("UPDATE us_table SET node_uuid=:uuid WHERE id_us=:id"),
            {"uuid": str(uuid7()), "id": id_us},
        )
```

`engine.begin()` wraps the whole loop in a single transaction. Failure
rolls back DML (UPDATE) on both backends; SQLite DDL is auto-committed
(same caveat as PG-A; not relevant here since PG-B uses no DDL).

### 6.3 `load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper

```
def load_sqlite_into_pg(sqlite_path, pg_engine, tables=None):
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    sqlite_inspector = inspect(sqlite_engine)
    pg_inspector = inspect(pg_engine)

    tables = tables or [t for t in sqlite_inspector.get_table_names()
                        if not t.startswith("sqlite_")]
    counts = {}
    for table in tables:
        cols = sqlite_inspector.get_columns(table)
        col_defs = ", ".join(
            f"{c['name']} {_map_type(c['type'])}"
            for c in cols
        )
        with pg_engine.begin() as conn:
            conn.execute(text(
                f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})"
            ))
            conn.execute(text(
                f"TRUNCATE {table} RESTART IDENTITY CASCADE"
            ))
        with sqlite_engine.connect() as src:
            rows = src.execute(text(f"SELECT * FROM {table}")).mappings().all()
        if rows:
            col_names = list(rows[0].keys())
            placeholders = ", ".join(f":{c}" for c in col_names)
            with pg_engine.begin() as conn:
                conn.execute(
                    text(f"INSERT INTO {table} ({', '.join(col_names)}) "
                         f"VALUES ({placeholders})"),
                    [dict(r) for r in rows],
                )
        counts[table] = len(rows)
    return counts


def _map_type(sqlite_type):
    """Map SQLite column type to PostgreSQL-compatible type.

    pyarchinit uses only TEXT, INTEGER, REAL — trivially compatible with PG.
    """
    s = str(sqlite_type).upper()
    if "INT" in s:
        return "INTEGER"
    if "TEXT" in s or "CHAR" in s or "CLOB" in s:
        return "TEXT"
    if "REAL" in s or "FLOA" in s or "DOUB" in s:
        return "REAL"
    return "TEXT"  # fallback
```

### 6.4 Error scenarios

| Trigger | Behavior |
|---|---|
| `db_path` passed as legacy `Path` | Shim resolves with DeprecationWarning (Foundation §3.1) |
| `db_path` points to non-existent SQLite file | First `engine.connect()` raises SQLAlchemy `OperationalError` → wrapped in `GraphProjectorError` |
| PG offline during `populate_graph(handle, ...)` | First `engine.connect()` raises `OperationalError` from psycopg2 → wrapped in `GraphProjectorError` with clear message |
| SQLite-specific function discovered in query | STOP Group, surface to brainstorming for equivalent (not expected for pyarchinit) |
| `?` placeholder left in a `text()` call | SQLAlchemy 2.0 raises `CompileError` at execute time → fix during refactor by sweep grep |
| AC-2 breaks after Group A | RED FLAG. STOP. Diff `_structure()` actual vs baseline. 99% cosmetic (text() spacing). Re-baseline ONLY after verifying the diff is structurally equivalent. |

### 6.5 Concurrency — out of scope

PG-B introduces no `LOCK TABLE` or `pg_advisory_lock`. The export pipeline
is read-mostly. Concurrency export ↔ import = Phase 4 SyncEngine concern.

## 7. Test strategy

### 7.1 Test pyramid

| Level | File | New cases | Skip semantics |
|---|---|---|---|
| L0 unit | none new | 0 | — |
| L1 SQLite | existing 250 | 0 added, all stay green via shim | — |
| L2 PG | `tests/sync/test_export_pg.py` (NEW) | 4-5 | `pg_engine` fixture skips when PG offline / psycopg2 missing |
| L2 PG | `tests/sync/test_ai03_export_pg_structural.py` (NEW) | 1 (AC-2 cousin) | Same |
| L3 regression guards | AC-2 + round-trip (existing) | 0 added, MUST stay green | — |

### 7.2 Five `test_export_pg.py` cases (pin the design)

| # | Test name | What it pins |
|---|---|---|
| 1 | `test_populate_graph_accepts_dbhandle_on_pg` | `GraphProjector().populate_graph(handle, sito)` returns a Graph with N nodes matching SQLite expected count. Pins public API + shim acceptance. |
| 2 | `test_populate_graph_node_uuid_propagation_on_pg` | Every node in the returned Graph has `node_uuid` attribute (non-None). Pins `_propagate_node_uuid_and_us` PG path. |
| 3 | `test_populate_graph_toponym_chain_on_pg` | Graph contains `LocationNodeGroup` nodes with `kind="toponym"` + `is_in_location` edges. Pins `_emit_toponym_chain` PG path. |
| 4 | `test_group_projector_dimensions_with_data_on_pg` | `dimensions_with_data(handle, sito)` returns the expected dim_key set. Pins `group_projector.py` site #1. |
| 5 | `test_export_graphml_writes_file_on_pg` | `export_graphml(db_path=handle, mapping=..., output_path=...)` produces non-empty GraphML + `ExportResult.node_count > 0`. End-to-end pin. |

### 7.3 The AC-2 cousin (`test_ai03_export_pg_structural.py`)

Single test:

```python
def test_pg_export_structural_fingerprint_matches_sqlite_baseline(
        pg_with_volterra, tmp_path):
    """PG export of mini_volterra produces same structural fingerprint
    as the committed SQLite baseline. THE gate for PG-B."""
    from tests.sync.test_ai03_export_byte_identical import _structure, BASELINE
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync._db_handle import DbHandle

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    out = tmp_path / "out_pg.graphml"
    result = export_graphml(db_path=handle,
                            mapping="pyarchinit_us_mapping",
                            output_path=out)

    actual = _structure(out.read_text(encoding="utf-8"))
    baseline = _structure(BASELINE.read_text(encoding="utf-8"))

    assert actual == baseline, (
        f"PG export structural fingerprint != SQLite baseline.\n"
        f"  actual:   {actual!r}\n"
        f"  baseline: {baseline!r}"
    )
    assert result.node_count > 0
```

### 7.4 Decision-pinning matrix

| Decision | Test |
|---|---|
| Q1=a (shim accepts DbHandle in `db_path` kwarg) | Tests #1-5 + AC-2 (Path still works) |
| Q2=a (load_sqlite_into_pg helper) | Indirect via every test using `pg_with_volterra` |
| Approach 1 (per-file Groups) | AC-2 sanity ping after each Group with code changes |
| `_emit_toponym_chain` PG-compatible | Test #3 |
| `_propagate_node_uuid_and_us` PG-compatible | Test #2 |
| `_merge_groups` PG-compatible | Test #1 (group structures present) |
| `dimensions_with_data` PG-compatible | Test #4 |
| `export_graphml` PG-compatible end-to-end | Test #5 + AC-2 cousin |
| Structural equivalence PG ↔ SQLite | **AC-2 cousin** (the gate) |

### 7.5 Test count progression

- Pre PG-B (post PG-A): `250 passed, 12 skipped` (PG offline)
- Post Groups A/B/C (refactor only, no new tests): unchanged
- Post Group D (helper + fixture, no new tests): unchanged
- Post Group E (`test_export_pg.py` 5 cases): `250 passed, 17 skipped` (PG offline)
- Post Group F (AC-2 cousin): `250 passed, 18 skipped` (PG offline)
- PG online + psycopg2 + local PG: `256 passed, 6 skipped` after both E and F

## 8. Acceptance criteria

| AC | Description |
|---|---|
| **AC-2** (existing) | Byte-identical structural fingerprint on `mini_volterra.sqlite` — **MUST stay green at every Group with code changes** (A/B/C critical) |
| **AC-15** (existing, AI07) | Toponym chain round-trip — unchanged (PG-B doesn't touch import) |
| **PG-B-AC-1** NEW | `GraphProjector.populate_graph(handle, sito)` works on PG (test #1 + AC-2 existing) |
| **PG-B-AC-2** NEW | `node_uuid` propagation works on PG (test #2) |
| **PG-B-AC-3** NEW | Toponym chain emission works on PG (test #3) |
| **PG-B-AC-4** NEW | `dimensions_with_data` + `build_groups_from_sql` work on PG (test #4) |
| **PG-B-AC-5** NEW | `export_graphml(db_path=handle, ...)` produces valid GraphML on PG (test #5) |
| **PG-B-AC-6** NEW | **PG export structural fingerprint == SQLite baseline fingerprint** (AC-2 cousin) — **THE gate** |
| **PG-B-AC-7** NEW | All 250 existing SQLite tests stay green via shim |
| **PG-B-AC-8** NEW | Round-trip CI fixture suite (PR #6 with Emanuel) stays green |
| **PG-B-AC-9** NEW | Zero `Co-Authored-By: Claude` trailers in any commit |

## 9. Release plan

**Tag:** `phase3-pgcompat-b-export-5.7.1-alpha`
**Predecessor:** `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
**Rollback safety tag:** `pre-pg-b-export` (created in Group 0)

### 9.1 Commit structure (~8 commits)

| Group | Type | Commit |
|---|---|---|
| 0 | git | Pre-flight + rollback tag |
| A | refactor | `graph_projector.py` 8 sites → SQLAlchemy + populate_graph signature shim |
| B | refactor | `group_projector.py` 2 sites → SQLAlchemy + signatures shim |
| C | refactor | `graphml_writer.py` 1 site → SQLAlchemy + `export_graphml` signature shim |
| D | feature | `conftest_pg.py` `load_sqlite_into_pg` helper + `pg_with_volterra` fixture |
| E | feature | `tests/sync/test_export_pg.py` (5 PG L2 cases) |
| F | feature | `tests/sync/test_ai03_export_pg_structural.py` (AC-2 cousin) |
| G | release | Bump 5.7.0-alpha → 5.7.1-alpha + bilingual CHANGELOG + dev-log Phase 3 PG-B section |
| H | tag+push | Annotated tag + push |

### 9.2 AC-2 sanity ping after EVERY production-code Group

A/B/C all touch code AC-2 exercises. After each commit:

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
```

If AC-2 breaks → STOP, investigate `_structure()` diff, do NOT proceed to
next Group.

### 9.3 Subagent batching for `subagent-driven-development`

- Group 0 → controller (no subagent)
- Groups A–G → 1 subagent each
- Group H → 1 subagent (gate for user approval before push)
- Memory snapshot → controller (no subagent) after H ships

### 9.4 Strict rules (inherited from Foundation + PG-A)

- Zero `Co-Authored-By: Claude` trailers
- AC-2 byte-identical guard green at every Group A/B/C (production code)
- All 250 pre-existing SQLite tests green at every Group
- HEREDOC commit messages
- No `git add -A` or `git add .`
- **SQLAlchemy 2.0-compliant** (production version); 1.4 incidentally works
  but is not the target
- **No SQL query content changes** — only connection wrapping + placeholder
  syntax (`?` → `:name`)

### 9.5 Memory snapshot post-ship

Update `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move PG-B from PENDING to SHIPPED
- Annotate any lessons learned (especially if AC-2 needed re-baseline, or
  if a SQLite-specific function was discovered in any query)

Update `MEMORY.md` index line for new CURRENT STATE.

### 9.6 Time estimate

Parent spec estimated ~2 weeks for PG-B (medium scope). Via
subagent-driven-development: ~4-5h execution + ~1h review + memory update.
End-to-end from spec approval to tag pushed: 1 long session.

## 10. References

- Foundation spec: `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.3
- Foundation plan (shipped): `docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md`
- Foundation tag: `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
- PG-A spec: `docs/superpowers/specs/2026-05-10-pg-a-migration-design.md`
- PG-A plan (shipped): `docs/superpowers/plans/2026-05-10-pg-a-migration.md`
- PG-A tag: `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- AC-2 test: `tests/sync/test_ai03_export_byte_identical.py`
- AC-2 baseline: `tests/sync/fixtures/mini_volterra_baseline_ai03.graphml`
- Round-trip fixture (Emanuel's PR #6): `tests/sync/fixtures/toponym_volterra.sqlite`
- Memory: `project_pg_compat_progress.md` — current state of Phase 3
- Memory: `feedback_no_claude_coauthor.md` — strict commit rule
