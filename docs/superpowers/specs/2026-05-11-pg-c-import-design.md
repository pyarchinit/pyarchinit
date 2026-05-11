# PG-C — Import pipeline on PostgreSQL (5.7.2-alpha)

> **Spec source of truth.** Brainstormed 2026-05-11 after PG-B (5.7.1-alpha)
> shipped. This spec is the contract for the implementation plan that follows
> via `superpowers:writing-plans`.

**Status:** Approved 2026-05-11
**Predecessor:** `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
**Target tag:** `phase3-pgcompat-c-import-5.7.2-alpha`
**Parent spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.4

---

## 1. Goal

Make `GraphIngestor.populate_list` (the s3dgraphy bridge's IMPORT pipeline)
work on both SQLite and PostgreSQL backends, preserving atomic transaction
semantics, conflict resolution, and dry-run mode. The single `sqlite3.connect()`
site at `graph_ingestor.py:248` (which wraps the entire `_run` body in one
BEGIN/COMMIT/ROLLBACK transaction) becomes `with handle.engine.begin() as conn:`
— identical atomicity guarantee on both backends. All ~10 SELECT/INSERT/UPDATE
queries inside `_run` translate `?` placeholders → `:name` via SQLAlchemy
`text()`. Public `populate_list(graph, db_path, sito, ...)` keeps the `db_path`
keyword name (PG-A/B precedent) but accepts `Path | DbHandle | str` via
`_resolve_db_handle()` shim.

**PG-C is bounded.** Production code paths for paradata persistence
(`paradata_store.py`) and group store (`group_store.py`) stay SQLite-only and
ship in PG-D. ConflictResolver is already pure in-memory (no SQL queries) — no
refactoring needed.

## 2. Background

`GraphIngestor.populate_list` is the entry point of the s3dgraphy bridge's
import side. The QGIS "Apply changes" dialog invokes it after the user has
made edits in a graph viewer (yEd, EM-tools), to write the changes back into
pyarchinit's SQL tables.

Today the implementation is SQLite-only. The 1 `sqlite3.connect()` call site
at line 248 opens a single connection that wraps the entire `_run` body —
which includes ~10 distinct SELECT/INSERT/UPDATE queries against `site_table`,
`us_table`, and `periodizzazione_table`. The transaction is opened explicitly
with `conn.execute("BEGIN")`, committed at the end with `conn.commit()`, and
rolled back inside the outer `except` block.

The 8 known callers of `populate_list` are:

- `modules/s3dgraphy/s3dgraphy_dot_bridge.py` — 6 sites (dry-run + write-mode
  paths in the QGIS dialog, each with retry logic)
- `scripts/s3dgraphy_sync.py:94` — 1 CLI script invocation
- `tests/sync/test_round_trip.py:74` — 1 round-trip integration test

All callers currently pass a `Path` as `db_path`. With the PG-A/B shim
pattern, none of them need to change.

PG-A (5.7.0-alpha) flipped the migration script. PG-B (5.7.1-alpha) flipped
the export pipeline. PG-C is the third and largest production caller flip —
the import pipeline. After PG-C, the only remaining sqlite3 usage in
`modules/s3dgraphy/sync/` will be in `paradata_store.py` / `group_store.py`
(PG-D scope).

## 3. Architectural decisions (from brainstorming 2026-05-11)

### 3.1 Q1 — Signature change strategy

**Decision:** Approach (b) — shim continuity. Keep `db_path` keyword name on
`populate_list`, accept `Path | DbHandle | str` via `_resolve_db_handle()`
shim. Same pattern as PG-A and PG-B.

**Rationale:** The parent spec §4.4 originally specified a hard signature
flip (`db_path: Path` → `db_handle: DbHandle`). However, PG-A and PG-B both
adopted the shim-continuity pattern with great success (zero call-site
changes, AC-2 preserved trivially). For consistency across milestones and to
minimize breakage on 8 known caller sites (especially the 6 QGIS dialog
sites with retry logic), PG-C inherits the same pattern. The cosmetic rename
of public API parameters from `db_path` to `db_input` is deferred to
**Consolidation (5.7.4-alpha)** which will do all renames with a proper
deprecation cycle.

### 3.2 Decomposition approach

**Decision:** Approach 1 — single-file refactor + test groups (~6 commits).

- A: `graph_ingestor.py` `_run` body refactor in one commit (~150 LOC delta)
- B: `test_ingest_pg.py` (6 PG L2 cases)
- C: `test_round_trip_pg.py` (1-2 round-trip identity cases — AC-2 cousin
  for import)
- D: docs + version bump
- E: tag + push

**Rationale:** `_run` is a single atomic flow — splitting it into per-section
commits (Approach 2) would create intermediate commits with mixed sqlite3 +
SQLAlchemy patterns inside the same function, which is fragile. Extracting
sub-methods first (Approach 3) is scope creep — PG-C flips the backend, not
the architecture. Per-file groups are the right middle ground; the file is
1349 LOC but `_run` is one logical unit.

### 3.3 Atomic transaction strategy

**Decision:** Single `with handle.engine.begin() as conn:` wraps the entire
`_run` body. No per-table savepoints. Dry-run mode uses an internal
`_DryRunRollback` exception to force rollback at end-of-`with`.

**Rationale:** `engine.begin()` provides identical BEGIN/COMMIT/ROLLBACK
semantics to the current explicit pattern on both backends. The exception
auto-rollbacks on exit, the success path auto-commits. The only awkward
part is dry-run mode (which currently calls `conn.rollback()` at the end
of a successful execution), since `engine.begin()` has no "conditional
rollback". The clean solution is to raise an internal sentinel exception
at the very end of the `with` block:

```python
class _DryRunRollback(Exception):
    """Internal signal to force rollback at end of dry-run."""

try:
    with handle.engine.begin() as conn:
        # ... all the work ...
        if dry_run:
            raise _DryRunRollback()  # forces rollback
except _DryRunRollback:
    pass  # swallow, dry-run completed successfully
```

This preserves the original semantic (dry-run = no DB side effects) on both
backends.

### 3.4 ConflictResolver compatibility

**Decision:** No changes to `conflict_resolver.py`. Verified via grep:
zero `sqlite3` / `text(` / `conn.execute` references. Pure in-memory diff
resolver. The AI04 `ConflictResolution.GRAPH_WINS` policy works identically
on PG.

### 3.5 SQLAlchemy version constraint

Same as PG-B. Production `requirements.txt` mandates `SQLAlchemy>=2.0.0`.
The refactor MUST be SQLAlchemy 2.0-compliant:

- `text()` + named params (`:name` + dict)
- `engine.begin()` / `engine.connect()` context managers
- `conn.execute(text(...), params_dict)` — NOT legacy `engine.execute(...)`
- `result.keys()` for column names — NOT legacy `cur.description`
- `result.fetchone()`, `result.fetchall()` — same shape as sqlite3.Cursor

## 4. File-by-file change plan

### 4.1 Modified production files

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | **(1)** `populate_list(graph, db_path, sito, ...)` keyword `db_path` accepts `Path \| DbHandle \| str` via shim. Line 152 `db_path = Path(db_path)` coercion **REMOVED** (replaced by `handle = _resolve_db_handle(db_path)` early in the method). `_verify_schema(db_path)` continues to accept either form (already shim-compatible from PG-A). **(2)** `_run(graph, db_path, sito, ...)` internal signature renamed to `_run(graph, handle, sito, ...)` — private method, no shim needed. **(3)** Line 248 `conn = sqlite3.connect(...)` + line 249 `conn.execute("BEGIN")` → `with handle.engine.begin() as conn:`. Line 571 `conn.commit()` removed (context manager auto-commits). **(4)** All ~10 `cur = conn.cursor()` + `cur.execute(SQL, (params,))` with `?` placeholders → `conn.execute(text(SQL), {params})` with `:name` placeholders. **(5)** `cur.description` → `result.keys()` (1 site at ~line 322). **(6)** `_DryRunRollback` internal sentinel exception class for dry_run mode (since `engine.begin()` has no conditional rollback). **(7)** All `except sqlite3.Error` → `except Exception`. **(8)** `import sqlite3` REMOVED. | ~150 |

### 4.2 Modified test infrastructure

| Path | Change | LOC delta |
|---|---|---|
| `tests/sync/conftest_pg.py` | Optional: add `pg_with_volterra_seeded_for_ingest` fixture if the existing `pg_with_volterra` (from PG-B) isn't sufficient for ingest tests. Likely the existing fixture is enough — verify during implementation. Best case 0 LOC. | 0-30 |

### 4.3 New test files

| Path | Purpose | LOC |
|---|---|---|
| `tests/sync/test_ingest_pg.py` | 6 L2 PG cases for the ingest pipeline. Skip cleanly when PG offline. | ~150 |
| `tests/sync/test_round_trip_pg.py` | 1-2 cases: full round-trip identity on PG (seed PG → export → re-import → re-export → fingerprint match). AC-2 cousin for the IMPORT side. THE gate for PG-C. | ~100 |

### 4.4 Modified release-tracking files

| Path | Change | LOC delta |
|---|---|---|
| `metadata.txt` | Bump `5.7.1-alpha` → `5.7.2-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.2-alpha]` section. | ~40 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 — PG-C import section. | ~30 |

### 4.5 Files explicitly NOT touched (per parent spec §4.5 + 4.6)

- `modules/s3dgraphy/sync/paradata_store.py` (PG-D)
- `modules/s3dgraphy/sync/group_store.py` (PG-D)
- `modules/s3dgraphy/sync/_db_handle.py` (Foundation — no changes)
- `modules/s3dgraphy/sync/conflict_resolver.py` (pure in-memory, no SQL)
- `modules/s3dgraphy/sync/graph_projector.py` (PG-B — already refactored)
- `modules/s3dgraphy/sync/group_projector.py` (PG-B)
- `modules/s3dgraphy/sync/graphml_writer.py` (PG-B)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2 itself — must stay
  green untouched; technically PG-C doesn't touch export, but ping it
  anyway after Group A as a regression guard)
- `tests/sync/test_round_trip.py` (existing SQLite round-trip — must stay
  green via shim; this is the critical regression gate for PG-C)
- The 8 callers of `populate_list` (6 in bridge dialog, 1 CLI, 1 test) —
  all continue to pass `Path` and the shim resolves transparently

### 4.6 Total LOC

- Production code: ~150 modified
- Test code: ~250 (2 new files)
- Docs: ~70 (CHANGELOG + dev-log)
- **Grand total: ~470 LOC**

## 5. SQL dialect compatibility

### 5.1 Connection management

| SQLite (today) | Cross-backend (PG-C) |
|---|---|
| `conn = sqlite3.connect(str(db_path))` | `with handle.engine.begin() as conn:` |
| `conn.execute("BEGIN")` | (implicit in `engine.begin()`) |
| `cur = conn.cursor()` + `cur.execute(SQL, params)` | `result = conn.execute(text(SQL), params_dict)` |
| `cur.fetchone()` / `cur.fetchall()` | `result.fetchone()` / `result.fetchall()` |
| `cur.description` (column names) | `result.keys()` |
| `conn.commit()` | (implicit on `with` exit) |
| `conn.rollback()` on exception | (implicit on `with` exception) |
| `dry_run` → manual `conn.rollback()` at end | `_DryRunRollback` internal sentinel exception |

### 5.2 Query placeholder syntax

All `?` positional placeholders convert to `:name` named placeholders. The
actual SQL string content is unchanged (column lists, WHERE clauses, etc.).

Example (line 254):

```python
# Before
cur.execute("SELECT COUNT(*) FROM site_table WHERE sito = ?", (sito,))

# After
result = conn.execute(
    text("SELECT COUNT(*) FROM site_table WHERE sito = :sito"),
    {"sito": sito},
)
count = result.scalar()  # or result.fetchone()[0]
```

### 5.3 Query content unchanged

The ~10 SQL queries in `_run` retain their original column lists, WHERE
clauses, JOINs (if any). **No new `ORDER BY` clauses, no SQLite-specific
function calls.** If a query uses `CAST(... AS TEXT)` (line 351 does), that
works identically on both backends.

### 5.4 `_DryRunRollback` pattern

```python
class _DryRunRollback(Exception):
    """Internal signal to force rollback at end of dry-run.

    Required because SQLAlchemy's engine.begin() context manager has no
    conditional rollback — it commits on clean exit and rolls back on
    any exception. To preserve the original semantic where dry_run=True
    runs the whole block then rolls back, we raise this sentinel at the
    very end of a dry-run, and swallow it just outside the `with` block.
    """


def _run(self, graph, handle, sito, *, dry_run, ...):
    inserted = updated = skipped = 0
    # ... initialization ...

    try:
        with handle.engine.begin() as conn:
            # ... all the work ...
            # At the very end:
            if dry_run:
                raise _DryRunRollback()
    except _DryRunRollback:
        pass  # rollback happened; dry-run completed

    return IngestResult(inserted=inserted, ...)
```

### 5.5 Result row access

`cur.fetchall()` on sqlite3 returns list of tuples. SQLAlchemy 2.0 `Result`
returns list of `Row` objects. Positional access (`row[0]`, `row[1]`) works
identically. **Key access via `row[col_name]` ALSO works** on SQLAlchemy
`Row`. Most pyarchinit code uses positional access — no changes needed.

For the `db_row = dict(zip(col_names, row))` pattern at line 323:

```python
# Before
row = cur.fetchone()
if row is None: ...
col_names = [d[0] for d in cur.description]
db_row = dict(zip(col_names, row))

# After
result = conn.execute(text(...), {...})
row = result.fetchone()
if row is None: ...
col_names = list(result.keys())
db_row = dict(zip(col_names, row))
```

## 6. Data flow

### 6.1 Happy path (write mode, both backends)

```
populate_list(graph, db_path=Path|DbHandle|str, sito, dry_run=False, ...)
  → handle = _resolve_db_handle(db_path)
  → _verify_sito(graph, sito) — early validation
  → _hydrate_pyarchinit_data_keys(graph, graphml_path) if graphml_path
  → _promote_legacy_activitynodegroup(graph) — AI07
  → _verify_schema(handle) — uses _columns_of (PG-A)
  → _run(graph, handle, sito, dry_run=False, ...)
      → with handle.engine.begin() as conn:
          → SELECT COUNT FROM site_table WHERE sito=:sito
          → INSERT INTO site_table (if missing) — write mode
          → Loop over graph.nodes (conflict detection):
              → SELECT * FROM us_table WHERE node_uuid=:uuid
              → If exists, compare columns via ConflictResolver
          → Loop over graph.nodes (EpochNode detection):
              → SELECT periodo,fase FROM periodizzazione_table WHERE sito=:sito
              → Collect missing_epochs
          → if missing_epochs and not create_missing_epochs:
              → raise MissingEpochError → context manager rollback → propagate
          → Write block (if not dry_run):
              → INSERT INTO us_table for new rows
              → UPDATE us_table SET ... WHERE node_uuid=:uuid for changed rows
              → INSERT INTO periodizzazione_table if create_missing_epochs=True
              → UPDATE us_table SET <kind>=<group_name> if sql_apply_groups=True
          → (clean exit) → context manager commits
  → return IngestResult(inserted, updated, skipped, epochs_created, conflicts, ...)
```

### 6.2 Dry-run path

Identical to happy path until end of `with`:

```
          → if dry_run:
              → raise _DryRunRollback() → context manager rollback
  → except _DryRunRollback: pass (swallow)
  → return IngestResult (with detected conflicts but no SQL writes)
```

### 6.3 Error scenarios

| Trigger | Behavior |
|---|---|
| `db_path` passed as legacy `Path` | Shim resolves with DeprecationWarning. Behaviour identical to PG-A/B. |
| PG offline during populate_list | `engine.begin()` raises SQLAlchemy `OperationalError` → wrapped in `GraphSyncError` by the outer caller catch. |
| `MissingEpochError` raised | Context manager rolls back automatically. Exception propagates to caller. |
| ConflictResolver raises | Same as MissingEpochError — context manager rollback + propagate. |
| `INSERT INTO site_table` fails (UNIQUE conflict on PG?) | Rollback + propagate as `GraphSyncError`. |
| `dry_run=True` | `_DryRunRollback` internal sentinel forces rollback. No DB writes. Returns IngestResult with detected conflicts (read-only). |
| Concurrent QGIS session writing same sito | Default isolation (READ COMMITTED on PG, SERIALIZABLE on SQLite). Phase 4 concern. |

### 6.4 Concurrency — out of scope

PG-C introduces no `LOCK TABLE` or `pg_advisory_lock`. SyncEngine
multi-user concurrency is Phase 4 scope.

## 7. Test strategy

### 7.1 Test pyramid (PG-C delta over PG-B)

| Level | File | New cases | Skip semantics |
|---|---|---|---|
| L0 unit | none new | 0 | — |
| L1 SQLite | existing 250, **inc. `test_round_trip.py`** | 0 added, all stay green via shim | — |
| L2 PG | `tests/sync/test_ingest_pg.py` (NEW) | 6 | `pg_engine` skips when PG offline / psycopg2 missing |
| L2 PG | `tests/sync/test_round_trip_pg.py` (NEW) | 1-2 (AC-2 cousin for import) | Same |
| L3 regression guards | AC-2 + `test_round_trip.py` (existing) | 0 added, MUST stay green | — |

### 7.2 Six `test_ingest_pg.py` cases (pin the design)

| # | Test name | What it pins |
|---|---|---|
| 1 | `test_populate_list_accepts_dbhandle_on_pg` | Public API + shim acceptance + INSERT path on PG. Empty `pg_with_volterra`, build Graph with 3 StratigraphicNodes, run populate_list, assert `inserted=3`. |
| 2 | `test_populate_list_dry_run_no_changes_on_pg` | **`_DryRunRollback` pattern** — the critical test. dry_run=True returns IngestResult, but SELECT confirms 0 rows in us_table. |
| 3 | `test_populate_list_conflict_resolution_graph_wins_on_pg` | ConflictResolver works on PG. Seed PG with US (node_uuid X, d_stratigrafica="A"). Graph has same US with d_stratigrafica="B". populate_list updates row to "B", IngestResult.conflicts contains the diff. |
| 4 | `test_populate_list_missing_epoch_error_on_pg` | Rollback on exception. Graph contains EpochNode with periodo/fase not in periodizzazione_table on PG. populate_list(create_missing_epochs=False) raises MissingEpochError. SELECT confirms no partial writes. |
| 5 | `test_populate_list_creates_missing_epochs_on_pg` | INSERT INTO periodizzazione_table on PG. Same setup as #4 but create_missing_epochs=True → epoch inserted, IngestResult.epochs_created=1. |
| 6 | `test_populate_list_atomic_rollback_on_pg` | `engine.begin()` rollback semantics. Mock `text()` to raise RuntimeError after first INSERT. SELECT confirms 0 rows (no partial state committed). |

### 7.3 The AC-2 cousin (`test_round_trip_pg.py`)

Primary test:

```python
def test_round_trip_pg_identity(pg_with_volterra, tmp_path):
    """Full round-trip on PG: seed PG with mini_volterra → export →
    import the exported GraphML back into the SAME PG → re-export →
    compare structural fingerprints.

    AC-2 cousin for the IMPORT side. If import drops or mutates data,
    the second export will diverge from the first."""
    from tests.sync.test_ai03_export_byte_identical import _structure
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))

    out1 = tmp_path / "first.graphml"
    export_graphml(db_path=handle, mapping="pyarchinit_us_mapping",
                   output_path=out1, site_filter="Volterra")

    GraphIngestor().populate_list(
        graph=out1, db_path=handle, sito="Volterra",
        dry_run=False, graphml_path=out1,
    )

    out2 = tmp_path / "second.graphml"
    export_graphml(db_path=handle, mapping="pyarchinit_us_mapping",
                   output_path=out2, site_filter="Volterra")

    fp1 = _structure(out1.read_text(encoding="utf-8"))
    fp2 = _structure(out2.read_text(encoding="utf-8"))
    assert fp1 == fp2, f"Round-trip not idempotent:\nfp1={fp1!r}\nfp2={fp2!r}"
```

Optionally a second test that imports into a FRESH PG (DDL-only, no data)
to verify the import path is self-sufficient.

### 7.4 Decision-pinning matrix

| Decision | Test |
|---|---|
| Q1=b (`db_path` kwarg accepts DbHandle via shim) | Test #1 + existing SQLite tests (Path callers via shim) |
| Approach 1 (single-file refactor) | AC-2 + `test_round_trip.py` sanity ping after Group A |
| `engine.begin()` atomic transaction | Tests #2 (dry-run), #4 (MissingEpoch), #6 (forced rollback) |
| `_DryRunRollback` internal pattern | Test #2 (the critical test) |
| ConflictResolver works on PG | Test #3 |
| Round-trip identity on PG | `test_round_trip_pg_identity` (THE gate) |
| AC-2 export-side preservation | AC-2 existing (untouched) |
| Round-trip SQLite-side preservation | `test_round_trip.py` existing (Path → shim) |

### 7.5 Test count progression

- Pre PG-C (post PG-B): `250 passed, 18 skipped` (PG offline)
- Post Group A (refactor only, no new tests): unchanged
- Post Group B (`test_ingest_pg.py` 6 cases, PG offline all skip): `250 passed, 24 skipped`
- Post Group C (`test_round_trip_pg.py` 1-2 cases, PG offline all skip): `250 passed, 25-26 skipped`
- Post Group D (docs only): unchanged

Final:
- PG offline: **250 passed, 25-26 skipped**
- PG online + psycopg2 + local PG: **257-258 passed, 12 skipped**

## 8. Acceptance criteria

| AC | Description |
|---|---|
| **AC-2** (existing) | Byte-identical structural fingerprint on `mini_volterra.sqlite` — PG-C doesn't touch export, AC-2 should stay green by default. Verify after Group A. |
| **AC-15** (existing, AI07) | Toponym chain round-trip — unchanged |
| **PG-C-AC-1** NEW | `populate_list(graph, handle, sito)` works on PG (Test #1) |
| **PG-C-AC-2** NEW | `dry_run=True` on PG = no DB changes (Test #2 — the critical) |
| **PG-C-AC-3** NEW | ConflictResolver GRAPH_WINS works on PG (Test #3) |
| **PG-C-AC-4** NEW | MissingEpochError + rollback on PG (Test #4) |
| **PG-C-AC-5** NEW | `create_missing_epochs=True` + INSERT periodizzazione on PG (Test #5) |
| **PG-C-AC-6** NEW | Atomic rollback mid-transaction on PG (Test #6) |
| **PG-C-AC-7** NEW | **Round-trip identity on PG** (AC-2 cousin for import) — THE gate |
| **PG-C-AC-8** NEW | All 250 existing SQLite tests stay green via shim |
| **PG-C-AC-9** NEW | **`tests/sync/test_round_trip.py` (existing SQLite round-trip) stays green** — critical regression gate for PG-C |
| **PG-C-AC-10** NEW | Zero `Co-Authored-By: Claude` trailers |

## 9. Release plan

**Tag:** `phase3-pgcompat-c-import-5.7.2-alpha`
**Predecessor:** `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
**Rollback safety tag:** `pre-pg-c-import` (created in Group 0)

### 9.1 Commit structure (~6 commits)

| Group | Type | Commit |
|---|---|---|
| 0 | git | Pre-flight + rollback tag |
| A | refactor | `graph_ingestor.py` `_run` → `engine.begin()` + ~10 queries to `text()` + `_DryRunRollback` pattern + `populate_list` shim + `import sqlite3` removed |
| B | feature | `tests/sync/test_ingest_pg.py` (6 PG L2 cases) |
| C | feature | `tests/sync/test_round_trip_pg.py` (1-2 round-trip identity cases — AC-2 cousin for import) |
| D | release | Bump 5.7.1-alpha → 5.7.2-alpha + bilingual CHANGELOG + dev-log Phase 3 PG-C section |
| E | tag+push | Annotated tag + push |

### 9.2 AC-2 + round-trip sanity ping after Group A (CRITICAL)

Group A is the only Group touching production code. After commit:

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2 (export-side)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v                    # round-trip SQLite (import-side, critical)
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no            # full suite
```

If any fails → STOP, do NOT proceed.

The **existing SQLite round-trip test** is the critical gate for PG-C — it
exercises `populate_list` end-to-end. If it breaks after Group A, the
refactor has introduced a regression (most likely candidates: `dry_run`
handling, ConflictResolver compatibility, INSERT/UPDATE query translation).

### 9.3 Subagent batching for `subagent-driven-development`

- Group 0 → controller (no subagent)
- Group A → 1 subagent (large refactor ~150 LOC in single file)
- Group B → 1 subagent (6 PG L2 cases)
- Group C → 1 subagent (1-2 round-trip cases)
- Group D → 1 subagent (docs + version)
- Group E → 1 subagent (tag + push, gate for user approval)
- Memory snapshot → controller (no subagent) after E ships

### 9.4 Strict rules (inherited from Foundation + PG-A + PG-B)

- Zero `Co-Authored-By: Claude` trailers
- AC-2 byte-identical guard green after Group A (export-side regression check)
- **`tests/sync/test_round_trip.py` SQLite round-trip stays green after Group A** (critical import-side gate)
- All 250 pre-existing SQLite tests green at every Group
- HEREDOC commit messages
- No `git add -A` or `git add .`
- **SQLAlchemy 2.0-compliant** (no `.execute()` legacy on engines, no `bind=` legacy, `result.keys()` not `cur.description`)
- **NO SQL query content changes** — only connection wrapping + placeholder syntax (`?` → `:name`)
- **`db_path = Path(db_path)` coercion at line 152 MUST be removed** (the same trap caught in PG-B Group C — would break DbHandle callers)
- **`_DryRunRollback` internal exception pattern** for dry_run mode (required because `engine.begin()` has no conditional rollback)

### 9.5 Memory snapshot post-ship

Update `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move PG-C from PENDING to SHIPPED
- Annotate any lessons learned (especially around `_DryRunRollback`, any
  SQLAlchemy 2.0 `Result.keys()` API surprises, dialect-specific behaviors)

Update `MEMORY.md` index line for new CURRENT STATE.

### 9.6 Time estimate

Parent spec estimated ~3 weeks for PG-C (large scope). Via
subagent-driven-development: ~3-4h execution + ~1h review + memory update.
End-to-end from spec approval to tag pushed: 1 long session.

## 10. References

- Foundation spec: `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.4
- Foundation plan (shipped): `docs/superpowers/plans/2026-05-10-postgres-compat-foundation.md`
- Foundation tag: `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
- PG-A spec: `docs/superpowers/specs/2026-05-10-pg-a-migration-design.md`
- PG-A tag: `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- PG-B spec: `docs/superpowers/specs/2026-05-10-pg-b-export-design.md`
- PG-B tag: `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
- AC-2 test: `tests/sync/test_ai03_export_byte_identical.py`
- Existing SQLite round-trip: `tests/sync/test_round_trip.py`
- ConflictResolver: `modules/s3dgraphy/sync/conflict_resolver.py` (no SQL — verified)
- Memory: `project_pg_compat_progress.md` — current state of Phase 3
- Memory: `feedback_no_claude_coauthor.md` — strict commit rule
