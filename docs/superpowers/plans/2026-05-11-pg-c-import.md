# PG-C — Import pipeline on PostgreSQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `GraphIngestor.populate_list` (the s3dgraphy bridge IMPORT pipeline) work on both SQLite and PostgreSQL backends, preserving atomic transaction semantics, ConflictResolver behaviour, and dry-run mode. The single `sqlite3.connect()` site at `graph_ingestor.py:248` (wraps entire `_run` body in one BEGIN/COMMIT/ROLLBACK) becomes `with handle.engine.begin() as conn:`. All ~10 inner queries translate `?` placeholder → `:name` via SQLAlchemy `text()`. Public `populate_list` keeps `db_path` keyword via shim (PG-A/B pattern). Internal `_DryRunRollback` sentinel exception handles dry_run mode. Release `5.7.2-alpha`.

**Architecture:** Per-file single-commit refactor (Group A) + new test files (B/C) + docs (D) + tag (E). `_run` is one atomic flow; splitting it would create intermediate commits with mixed sqlite3 + SQLAlchemy patterns. AC-2 (export-side) should stay green by default since PG-C doesn't touch export; `test_round_trip.py` (SQLite import-side) is the **critical regression gate** after Group A.

**Tech Stack:** Python 3.9+, SQLAlchemy 2.0+ (production version), psycopg2-binary>=2.9 (Foundation), Foundation + PG-A + PG-B helpers reused.

**Spec source of truth:** `docs/superpowers/specs/2026-05-11-pg-c-import-design.md` (commit `2268463a`)

**Predecessor releases:**
- PG-B: tag `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
- PG-A: tag `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- Foundation: tag `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` — current Phase 3 state
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

**Local PG setup:** `postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg` (USER pre-created during Foundation, schema applied by `tests/sync/conftest_pg.py`). In dev env psycopg2 is NOT installed, so PG L2 tests skip cleanly. That's expected.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `tests/sync/test_ingest_pg.py` | 6 L2 PG cases for the import pipeline. Skip cleanly when PG offline. ~150 LOC. |
| `tests/sync/test_round_trip_pg.py` | 1-2 round-trip identity cases. AC-2 cousin for the import side — THE gate for PG-C. ~100 LOC. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/graph_ingestor.py` | (1) `populate_list` keyword `db_path` accepts `Path \| DbHandle \| str` via shim. Line 152 `db_path = Path(db_path)` coercion REMOVED. (2) `_run(graph, db_path, ...)` private signature renamed to accept handle internally. (3) Line 248 `conn = sqlite3.connect(...)` + `conn.execute("BEGIN")` → `with handle.engine.begin() as conn:`. Lines 568-579 `conn.commit()` / `conn.rollback()` / `conn.close()` removed (context manager). (4) All ~10 inner queries: `?` → `:name` via `text()`. (5) `cur.description` → `result.keys()` (2 sites at lines 322, 480). (6) `_DryRunRollback` internal sentinel exception class. (7) `except sqlite3.Error` → `except Exception`. (8) `_apply_group_folders_to_sql(cur, ...)` helper at line 712 also flips: signature `cur` → `conn`, 2 internal `cur.execute()` → `conn.execute(text())`. (9) `import sqlite3` REMOVED. | ~150 LOC delta |
| `metadata.txt` | Bump `5.7.1-alpha` → `5.7.2-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.2-alpha]` section. | ~40 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 PG-C section. | ~30 |

### Explicitly NOT touched (per spec §4.5)

- `modules/s3dgraphy/sync/paradata_store.py` (PG-D)
- `modules/s3dgraphy/sync/group_store.py` (PG-D)
- `modules/s3dgraphy/sync/_db_handle.py` (Foundation)
- `modules/s3dgraphy/sync/conflict_resolver.py` (pure in-memory, verified)
- `modules/s3dgraphy/sync/graph_projector.py` (PG-B, refactored)
- `modules/s3dgraphy/sync/group_projector.py` (PG-B)
- `modules/s3dgraphy/sync/graphml_writer.py` (PG-B)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2 — must stay green untouched)
- `tests/sync/test_round_trip.py` (SQLite round-trip — must stay green via shim; critical gate)
- The 8 callers of `populate_list` (6 in bridge, 1 CLI, 1 test) — all unchanged via shim

### Total LOC

- Production: ~150 modified
- Test code: ~250 (2 new files)
- Docs: ~70
- **Grand total: ~470 LOC**

---

## Test strategy

- **L0 unit (none new):** Foundation + PG-A/B unit tests cover shim, `_columns_of`, Inspector pattern.
- **L1 SQLite (existing 250):** All stay green via shim. Especially `test_round_trip.py` — the critical gate.
- **L2 PG (NEW):** 6 cases in `test_ingest_pg.py` + 1-2 round-trip cases in `test_round_trip_pg.py`. Skip cleanly when PG offline / psycopg2 missing.
- **L3 regression guards (existing, MUST stay green):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2 (export — should stay trivially green)
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v                    # SQLite round-trip (import — critical gate)
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no            # full SQLite suite
```

**AC-2 is critical for PG-C** because, even though it tests the export, a refactor of the import path could in theory corrupt data on first import call (rare, but possible if `_DryRunRollback` is mishandled). The `test_round_trip.py` SQLite gate is the primary import-side regression check.

Decision-pinning matrix:

| Decision / Acceptance | Pinning test |
|---|---|
| Q1=b (`db_path` kwarg accepts DbHandle via shim) | Test #1 (Group B) + existing SQLite tests (Path callers) |
| Approach 1 (single-file refactor) | AC-2 + `test_round_trip.py` after Group A |
| `engine.begin()` atomic transaction | Tests #2 (dry-run), #4 (MissingEpoch), #6 (forced rollback) |
| `_DryRunRollback` internal sentinel pattern | Test #2 (THE critical test for this pattern) |
| ConflictResolver works on PG | Test #3 |
| Round-trip identity on PG | `test_round_trip_pg_identity` (THE gate) |
| AC-2 preservation | AC-2 existing (untouched) |
| Round-trip SQLite preservation | `test_round_trip.py` existing (Path → shim) |

Test count progression:
- Pre PG-C (post PG-B): `250 passed, 18 skipped` (PG offline)
- Post Group A (refactor only, no new tests): unchanged
- Post Group B (`test_ingest_pg.py` 6 cases, PG offline all skip): `250 passed, 24 skipped`
- Post Group C (`test_round_trip_pg.py` 1 case, PG offline skip): `250 passed, 25 skipped`
- Post Group D (docs only): unchanged

Final:
- PG offline: **250 passed, 25 skipped**
- PG online + psycopg2: **257 passed, 12 skipped**

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

Expected: tracked changes empty, last commit `2268463a spec(pg-c-import): ...`, `0\t0` ahead-behind.

- [ ] **Step 2: Verify predecessor tag exists**

```bash
git tag --list | grep -E "phase3-pgcompat-b-export-5.7.1-alpha"
```

Expected: `phase3-pgcompat-b-export-5.7.1-alpha` listed.

- [ ] **Step 3: Capture baseline test count + AC-2 + SQLite round-trip**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -3
```

Expected: `250 passed, 18 skipped`. AC-2 PASS. `test_round_trip.py` ALL PASS.

### Task 0.2: Create rollback safety tag

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-pg-c-import -m "Rollback point before PG-C import milestone

Predecessor: phase3-pgcompat-b-export-5.7.1-alpha (2121369e)
Spec commit: 2268463a

If PG-C needs to be reverted, reset hard to this tag."
git push origin pre-pg-c-import
```

Expected: `* [new tag]         pre-pg-c-import -> pre-pg-c-import`.

---

## Group A — `graph_ingestor.py` `_run` refactor

The single production-code Group. ~150 LOC delta in one file. Single atomic flow — splitting would create mixed sqlite3 + SQLAlchemy intermediate commits.

**CRITICAL RULES (surface in subagent prompt):**
- NO SQL query content changes — only connection wrapping + placeholder syntax (`?` → `:name`)
- Line 152 `db_path = Path(db_path)` MUST be REMOVED (same trap as PG-B Group C — would break DbHandle callers)
- `_DryRunRollback` internal sentinel exception class is REQUIRED (engine.begin() has no conditional rollback)
- `cur.description` → `result.keys()` (SQLAlchemy 2.0)
- `except sqlite3.Error` → `except Exception`
- SQLAlchemy 2.0-compliant (no `.execute()` legacy on engines)
- **AC-2 + `test_round_trip.py` sanity ping after the commit** — if either breaks, STOP

### Task A.1: Refactor `graph_ingestor.py`

**File:** `modules/s3dgraphy/sync/graph_ingestor.py`

#### Step 1: Update imports + add `_DryRunRollback` class

Find the imports block near line 88-96:

```python
# ---------------------------------------------------------------------------
# GraphIngestor (Groups C–D)
# ---------------------------------------------------------------------------
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from .conflict_resolver import ConflictResolver
from .ingest_result import (
    ConflictRecord, ConflictResolution, IngestResult)
```

Replace with:

```python
# ---------------------------------------------------------------------------
# GraphIngestor (Groups C–D)
# ---------------------------------------------------------------------------
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import text

from ._db_handle import _resolve_db_handle
from .conflict_resolver import ConflictResolver
from .ingest_result import (
    ConflictRecord, ConflictResolution, IngestResult)


class _DryRunRollback(Exception):
    """Internal sentinel to force rollback at end of dry-run.

    PG-C (5.7.2-alpha): required because SQLAlchemy's engine.begin()
    context manager has no conditional rollback — it commits on clean
    exit and rolls back on any exception. To preserve the original
    dry_run semantic (run the whole block then roll back), we raise
    this sentinel at the very end of a dry-run, and swallow it just
    outside the `with` block.
    """
```

NOTE: `import sqlite3` is removed. Other classes in the file may still reference `sqlite3.Error` — verify with `grep -n sqlite3 graph_ingestor.py` after this step and fix if any remain. The plan expects zero `sqlite3` references after Group A.

#### Step 2: Refactor `populate_list` — remove Path coercion + accept shim

Find the `populate_list` method body opening (around line 117-152). The current code starts with:

```python
    def populate_list(
        self,
        graph: "s3dgraphy.Graph",
        db_path: Path,
        sito: str,
        *,
        dry_run: bool = False,
        create_missing_epochs: bool = False,
        graphml_path: Path | str | None = None,
        sql_apply_groups: bool = False,
    ) -> IngestResult:
        """..."""
        db_path = Path(db_path)
        # AI06: graph may be a Path-like (graphml file). Auto-load.
        from pathlib import Path as _P
        if isinstance(graph, (str, _P)):
```

Use the Edit tool to change the signature annotation `db_path: Path` to plain `db_path` (no annotation), add a PG-C note to docstring, and REMOVE the `db_path = Path(db_path)` line. The new opening becomes:

```python
    def populate_list(
        self,
        graph: "s3dgraphy.Graph",
        db_path,  # Path | DbHandle | str — resolved via _resolve_db_handle shim
        sito: str,
        *,
        dry_run: bool = False,
        create_missing_epochs: bool = False,
        graphml_path: Path | str | None = None,
        sql_apply_groups: bool = False,
    ) -> IngestResult:
        """...

        PG-C (5.7.2-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        """
        # PG-C: resolve shim once at entry, propagate handle to _run/_verify_schema
        handle = _resolve_db_handle(db_path)
        # AI06: graph may be a Path-like (graphml file). Auto-load.
        from pathlib import Path as _P
        if isinstance(graph, (str, _P)):
```

(Note: the `db_path = Path(db_path)` line at the old line 152 is GONE. The `handle = _resolve_db_handle(db_path)` line takes its place.)

#### Step 3: Pass handle to `_verify_schema` and `_run`

In the `populate_list` body, find the calls (around line 191-197):

```python
        # 2. Schema check
        self._verify_schema(db_path)
        # 3. Run the actual ingestion (Group C: dry-run only)
        return self._run(graph, db_path, sito,
                         dry_run=dry_run,
                         create_missing_epochs=create_missing_epochs,
                         graphml_path=graphml_path,
                         sql_apply_groups=sql_apply_groups)
```

Replace with:

```python
        # 2. Schema check (accepts handle directly — PG-A shim)
        self._verify_schema(handle)
        # 3. Run the actual ingestion
        return self._run(graph, handle, sito,
                         dry_run=dry_run,
                         create_missing_epochs=create_missing_epochs,
                         graphml_path=graphml_path,
                         sql_apply_groups=sql_apply_groups)
```

#### Step 4: Update `_verify_schema` signature

Find the `_verify_schema` method (around line 200-217). The current signature is:

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
            raise SchemaMismatchError(...)
```

Refactor to accept `handle` directly (no shim re-resolution). The `db_path.exists()` check no longer applies (no Path) — replace with engine-level connectivity check via `_columns_of` which already handles missing-table case:

```python
    def _verify_schema(self, handle) -> None:
        # PG-C (5.7.2-alpha): accepts DbHandle directly from populate_list.
        # The file-existence check is gone (PG has no file); we rely on
        # _columns_of returning empty set on connection / missing-table
        # failure to surface as SchemaMismatchError below.
        from ._db_handle import _columns_of
        try:
            cols = _columns_of(handle.engine, "us_table")
        except Exception as e:
            raise GraphIngestError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise SchemaMismatchError(...)
```

NOTE: this removes the old `if not db_path.exists()` early check. On SQLite, if the file doesn't exist, `create_engine(f"sqlite:///{path}")` returns a working engine but `_columns_of` returns empty set → `SchemaMismatchError` raised below. Same outcome, slightly different error path. Acceptable.

(If preserving the file-not-found error message verbatim is critical, restore the existence check using `handle.sqlite_path and not handle.sqlite_path.exists()`. Up to implementer judgment based on whether existing tests catch this specific error message.)

#### Step 5: Refactor `_run` signature + open the SQLAlchemy transaction

Find the `_run` method header (around line 233-249):

```python
    def _run(self, graph, db_path, sito, *, dry_run, create_missing_epochs,
             graphml_path=None, sql_apply_groups=False):
        inserted = updated = skipped = 0
        epochs_created = 0
        sito_created = False
        conflicts: list[ConflictRecord] = []
        errors: list[str] = []

        # Pre-compute per-source rapporti from graph edges so the write
        # path can populate us_table.rapporti as JSON-list-of-lists.
        rapporti_by_source = _build_rapporti_from_edges(graph, sito)

        # Open the transaction (we always use BEGIN even in dry-run so
        # any side effects from other code paths get isolated and
        # ROLLBACK'd).
        conn = sqlite3.connect(str(db_path))
        conn.execute("BEGIN")
        try:
            cur = conn.cursor()
```

Replace with:

```python
    def _run(self, graph, handle, sito, *, dry_run, create_missing_epochs,
             graphml_path=None, sql_apply_groups=False):
        inserted = updated = skipped = 0
        epochs_created = 0
        sito_created = False
        applied = 0
        conflicts: list[ConflictRecord] = []
        errors: list[str] = []

        # Pre-compute per-source rapporti from graph edges so the write
        # path can populate us_table.rapporti as JSON-list-of-lists.
        rapporti_by_source = _build_rapporti_from_edges(graph, sito)

        # PG-C (5.7.2-alpha): engine.begin() opens an atomic transaction
        # that commits on clean exit / rolls back on exception. Identical
        # semantics to the old sqlite3 BEGIN/COMMIT/ROLLBACK pattern on
        # both SQLite and PostgreSQL backends. dry_run uses the
        # _DryRunRollback sentinel to force rollback at the end.
        try:
            with handle.engine.begin() as conn:
```

NOTE: the `applied = 0` is hoisted from the inner write block (around line 388) to the top of `_run` so it's in scope when the `with` block exits — needed for the final `IngestResult(applied=applied, ...)` at line 581-587. Find the existing `applied = 0` line inside the write block and DELETE it (it's redundant after hoisting).

The entire current body of `_run` (from `cur = conn.cursor()` down to `finally: conn.close()` at line 579) needs to be indented one level INSIDE the new `with handle.engine.begin() as conn:` block. Use the Edit tool carefully — this is a large block move + indent shift. Recommend doing it in sub-steps via multiple Edit calls if necessary.

#### Step 6: Translate all inner queries (10 queries in `_run`)

Now refactor each `cur.execute(SQL, (params,))` to `conn.execute(text(SQL_with_named), {params_dict})`. Order them by line number in the original:

**Query 1 (line 253-254)** — `SELECT COUNT FROM site_table`:

```python
# Before
cur.execute(
    "SELECT COUNT(*) FROM site_table WHERE sito = ?", (sito,))
if cur.fetchone()[0] == 0:
```

```python
# After
count_row = conn.execute(
    text("SELECT COUNT(*) FROM site_table WHERE sito = :sito"),
    {"sito": sito},
).fetchone()
if count_row[0] == 0:
```

**Query 2 (line 257-262)** — `INSERT INTO site_table`:

```python
# Before
cur.execute(
    "INSERT INTO site_table (sito, nazione, regione, "
    "definizione_sito) VALUES (?, '', '', "
    "'auto-created by AI04 import')",
    (sito,),
)
```

```python
# After
conn.execute(
    text(
        "INSERT INTO site_table (sito, nazione, regione, "
        "definizione_sito) VALUES (:sito, '', '', "
        "'auto-created by AI04 import')"
    ),
    {"sito": sito},
)
```

**Query 3 (line 313-317)** — `SELECT * FROM us_table` (detection loop):

```python
# Before
cur.execute(
    "SELECT * FROM us_table WHERE node_uuid = ?",
    (node_uuid,),
)
row = cur.fetchone()
if row is None:
    inserted += 1
    continue
# Build {col: db_val} dict from row + cursor.description
col_names = [d[0] for d in cur.description]
db_row = dict(zip(col_names, row))
```

```python
# After
result = conn.execute(
    text("SELECT * FROM us_table WHERE node_uuid = :uuid"),
    {"uuid": node_uuid},
)
row = result.fetchone()
if row is None:
    inserted += 1
    continue
# Build {col: db_val} dict from row + result.keys()
col_names = list(result.keys())
db_row = dict(zip(col_names, row))
```

**Query 4 (line 350-353)** — `SELECT periodo, fase FROM periodizzazione_table`:

```python
# Before
cur.execute(
    "SELECT CAST(periodo AS TEXT), CAST(fase AS TEXT) "
    "FROM periodizzazione_table WHERE sito = ?",
    (sito,))
existing_epochs = {(r[0], r[1]) for r in cur.fetchall()}
```

```python
# After
existing_epochs = {
    (r[0], r[1])
    for r in conn.execute(
        text(
            "SELECT CAST(periodo AS TEXT), CAST(fase AS TEXT) "
            "FROM periodizzazione_table WHERE sito = :sito"
        ),
        {"sito": sito},
    ).fetchall()
}
```

**Query 5 (line 453-457)** — `SELECT * FROM us_table` (write loop):

```python
# Before
cur.execute(
    "SELECT * FROM us_table WHERE node_uuid = ?",
    (node_uuid,),
)
existing = cur.fetchone()
```

```python
# After
result = conn.execute(
    text("SELECT * FROM us_table WHERE node_uuid = :uuid"),
    {"uuid": node_uuid},
)
existing = result.fetchone()
```

**Query 6 (line 466-472)** — dynamic INSERT INTO us_table (write block):

```python
# Before
cols = list(col_payload.keys())
placeholders = ",".join("?" for _ in cols)
col_list = ",".join(cols)
cur.execute(
    f"INSERT INTO us_table ({col_list}) VALUES "
    f"({placeholders})",
    [col_payload[c] for c in cols],
)
applied += 1
```

```python
# After
cols = list(col_payload.keys())
placeholders = ",".join(f":{c}" for c in cols)
col_list = ",".join(cols)
conn.execute(
    text(
        f"INSERT INTO us_table ({col_list}) VALUES "
        f"({placeholders})"
    ),
    {c: col_payload[c] for c in cols},
)
applied += 1
```

**Query 7 (line 480-481)** — `cur.description` (second site, in the write block UPDATE path):

```python
# Before
col_names = [d[0] for d in cur.description]
db_row = dict(zip(col_names, existing))
```

The `cur.description` here refers to the cursor from Query 5 above. After refactor, `result` is the local variable from Query 5 — use `result.keys()` instead:

```python
# After
col_names = list(result.keys())
db_row = dict(zip(col_names, existing))
```

**Query 8 (line 492-499)** — dynamic UPDATE us_table:

```python
# Before
if diff_cols:
    set_clause = ", ".join(
        f"{c} = ?" for c in diff_cols)
    cur.execute(
        f"UPDATE us_table SET {set_clause} "
        f"WHERE node_uuid = ?",
        [*diff_vals, node_uuid],
    )
    applied += 1
```

```python
# After
if diff_cols:
    set_clause = ", ".join(
        f"{c} = :{c}" for c in diff_cols)
    params = {c: v for c, v in zip(diff_cols, diff_vals)}
    params["__node_uuid"] = node_uuid
    conn.execute(
        text(
            f"UPDATE us_table SET {set_clause} "
            f"WHERE node_uuid = :__node_uuid"
        ),
        params,
    )
    applied += 1
```

NOTE: `__node_uuid` (double underscore prefix) is used to avoid name collision with any MAPPED_COLUMN that might happen to be named `node_uuid`.

**Query 9 (line 549-557)** — INSERT INTO periodizzazione_table:

```python
# Before
cur.execute(
    "INSERT INTO periodizzazione_table "
    "(sito, periodo, fase, descrizione, "
    " cron_iniziale, cron_finale, "
    " datazione_estesa) "
    "VALUES (?, ?, ?, ?, ?, ?, ?)",
    (sito, periodo_i, fase, descrizione,
     cron_ini_i, cron_fin_i, datazione),
)
```

```python
# After
conn.execute(
    text(
        "INSERT INTO periodizzazione_table "
        "(sito, periodo, fase, descrizione, "
        " cron_iniziale, cron_finale, "
        " datazione_estesa) "
        "VALUES (:sito, :periodo, :fase, :descrizione, "
        " :cron_ini, :cron_fin, :datazione)"
    ),
    {
        "sito": sito, "periodo": periodo_i, "fase": fase,
        "descrizione": descrizione,
        "cron_ini": cron_ini_i, "cron_fin": cron_fin_i,
        "datazione": datazione,
    },
)
```

**Query 10** — `_apply_group_folders_to_sql(cur, ...)` call at line 563-565:

```python
# Before
if sql_apply_groups and not dry_run and graphml_path:
    applied += _apply_group_folders_to_sql(
        cur, Path(graphml_path), sito)
```

```python
# After
if sql_apply_groups and not dry_run and graphml_path:
    applied += _apply_group_folders_to_sql(
        conn, Path(graphml_path), sito)
```

The helper signature changes from `cur` → `conn` — see Step 7 for the helper refactor.

#### Step 7: Refactor `_apply_group_folders_to_sql` helper (line 712-866)

Find the signature:

```python
def _apply_group_folders_to_sql(cur, graphml_path: Path, sito: str) -> int:
```

Replace with:

```python
def _apply_group_folders_to_sql(conn, graphml_path: Path, sito: str) -> int:
```

Find the 2 internal `cur.execute()` calls (lines 822 and 833) and replace:

**Internal site 1 (line 822-826)**:

```python
# Before
cur.execute(
    f"UPDATE us_table SET {group_kind}=? "
    f"WHERE node_uuid=? AND sito=?",
    (group_name, node_uuid, sito),
)
local_applied += (
    cur.rowcount if cur.rowcount and cur.rowcount > 0
    else 0)
```

```python
# After
upd_result = conn.execute(
    text(
        f"UPDATE us_table SET {group_kind}=:group_name "
        f"WHERE node_uuid=:node_uuid AND sito=:sito"
    ),
    {"group_name": group_name, "node_uuid": node_uuid, "sito": sito},
)
local_applied += (
    upd_result.rowcount
    if upd_result.rowcount and upd_result.rowcount > 0
    else 0)
```

**Internal site 2 (line 833-840)**:

```python
# Before
cur.execute(
    f"UPDATE us_table SET {group_kind}=? "
    f"WHERE us=? AND area=? AND sito=?",
    (group_name, us_val, area_val, sito),
)
local_applied += (
    cur.rowcount if cur.rowcount and cur.rowcount > 0
    else 0)
```

```python
# After
upd_result = conn.execute(
    text(
        f"UPDATE us_table SET {group_kind}=:group_name "
        f"WHERE us=:us AND area=:area AND sito=:sito"
    ),
    {"group_name": group_name, "us": us_val,
     "area": area_val, "sito": sito},
)
local_applied += (
    upd_result.rowcount
    if upd_result.rowcount and upd_result.rowcount > 0
    else 0)
```

NOTE: `{group_kind}` f-string interpolation is preserved — `group_kind` comes from the hardcoded `_GROUP_KIND_TO_COL` set, not user input. Same pattern as PG-B Group B.

#### Step 8: Replace the commit/rollback/close block at end of `_run`

Find the block at lines 567-579:

```python
            # Commit or rollback
            if dry_run:
                conn.rollback()
            else:
                conn.commit()
        except GraphSyncError:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise GraphIngestError(f"Ingest failed: {e}") from e
        finally:
            conn.close()
```

Replace with:

```python
                # PG-C: at the very end of a dry-run, raise the
                # internal sentinel to force engine.begin() to roll
                # back. Clean exit (success path) auto-commits.
                if dry_run:
                    raise _DryRunRollback()
        except _DryRunRollback:
            pass  # dry-run completed; rollback already happened
        except GraphSyncError:
            # engine.begin() already rolled back on the exception path;
            # just re-raise so the caller sees the same error type.
            raise
        except Exception as e:
            raise GraphIngestError(f"Ingest failed: {e}") from e
```

NOTE: indentation is critical here. The `if dry_run: raise _DryRunRollback()` lives INSIDE the `with handle.engine.begin() as conn:` block (so the rollback fires correctly via the context manager). The `except` clauses live OUTSIDE the `with` but INSIDE the outer `try`. The `finally: conn.close()` is removed entirely (context manager handles close).

#### Step 9: Verify no remaining sqlite3 references

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep -n sqlite3 modules/s3dgraphy/sync/graph_ingestor.py
```

Expected: no output. If anything remains (e.g., docstring mention of "sqlite3" history), that's fine if it's just commentary — only `sqlite3.X` API usage must be gone.

#### Step 10: Run SQLite suite + AC-2 + round-trip (CRITICAL)

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 18 skipped`.

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -10
```

Expected: ALL PASS.

**If any of these fail → STOP. Do not commit.** Investigate:
- For AC-2 failure: structural fingerprint diff (same procedure as PG-B Group A Step 10).
- For `test_round_trip.py` failure: this is the critical PG-C regression. Likely candidates:
  - `_DryRunRollback` mishandled (look at test_round_trip dry_run flow)
  - Query parameter binding bug (typo in `:name` placeholder)
  - `cur.description` → `result.keys()` translation broken (some test uses `db_row[col_name]`)
  - `_apply_group_folders_to_sql` cur/conn confusion

Report the failure as BLOCKED with the test output.

#### Step 11: Commit Group A

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/graph_ingestor.py
git commit -m "$(cat <<'EOF'
refactor(pg-c/A): graph_ingestor cross-backend via SQLAlchemy

1 sqlite3.connect() site swapped to engine.begin() via Foundation
shim. The single transaction wrapping the whole _run body (currently
BEGIN/COMMIT/ROLLBACK on sqlite3) now uses
with handle.engine.begin() as conn: - identical atomicity semantics
on both SQLite and PostgreSQL.

~10 inner queries translated:
- SELECT COUNT FROM site_table
- INSERT INTO site_table (write mode, when missing)
- SELECT * FROM us_table (detection loop)
- SELECT periodo,fase FROM periodizzazione_table
- SELECT * FROM us_table (write loop)
- INSERT INTO us_table (dynamic column list, write block)
- cur.description -> result.keys() (2 sites)
- UPDATE us_table SET ... (dynamic column list)
- INSERT INTO periodizzazione_table
- _apply_group_folders_to_sql helper: signature cur -> conn,
  2 internal UPDATE us_table SET {group_kind}=... cur.execute
  -> conn.execute(text(...))

All ? placeholders -> :name named params via SQLAlchemy text().
All except sqlite3.Error -> except Exception.

populate_list(db_path, ...) public API now accepts
Path | DbHandle | str via _resolve_db_handle shim - line 152
db_path = Path(db_path) coercion REMOVED (would have broken
DbHandle callers - same trap caught in PG-B Group C).

_run(graph, handle, ...) private signature renamed; populate_list
resolves shim once at entry and passes handle down.

_DryRunRollback internal sentinel exception class added: raised at
end of with block when dry_run=True so engine.begin() rolls back.
Caught + swallowed outside the with. Preserves the original
'dry_run = no DB writes' semantic on both backends.

import sqlite3 REMOVED. No remaining sqlite3.X usage in the file.

NO SQL query content changes - only connection wrapping and
placeholder syntax (? -> :name). NO behaviour changes on SQLite
path.

AC-2 byte-identical structural fingerprint preserved.
tests/sync/test_round_trip.py (SQLite round-trip, the critical
PG-C regression gate) preserved.

250 passed, 18 skipped (unchanged).
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group B — `tests/sync/test_ingest_pg.py` (6 PG L2 cases)

### Task B.1: Create the 6-case PG ingest test file

**File:** `tests/sync/test_ingest_pg.py`

- [ ] **Step 1: Write the file with 6 test cases**

```python
# tests/sync/test_ingest_pg.py
"""PG-C: L2 PostgreSQL tests for the ingest pipeline.

Verifies that GraphIngestor.populate_list works on PG when seeded
via the pg_with_volterra fixture (from PG-B's conftest_pg.py).

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed.
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def _make_test_graph_with_us(sito="Volterra", us_count=3):
    """Build a minimal s3dgraphy Graph with us_count StratigraphicNodes.

    Each node has a fresh node_uuid, the requested sito, and a numeric
    'us' value (1, 2, 3, ...). Used as input for populate_list tests
    that don't need to round-trip a real GraphML file.
    """
    import uuid
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode

    graph = Graph(graph_id="test_graph")
    for i in range(1, us_count + 1):
        node_uuid = str(uuid.uuid4())
        node = StratigraphicNode(
            node_id=node_uuid,
            name=str(i),
            description="",
            data={},
        )
        if not hasattr(node, "attributes") or node.attributes is None:
            node.attributes = {}
        node.attributes["node_uuid"] = node_uuid
        node.attributes["us"] = str(i)
        node.attributes["sito"] = sito
        node.attributes["area"] = "1"
        node.attributes["unita_tipo"] = "US"
        graph.add_node(node)
    return graph


def test_populate_list_accepts_dbhandle_on_pg(pg_engine):
    """populate_list(graph, handle, sito) works on PG and inserts US rows.

    Uses a fresh PG (DDL-only, no data) so insertions are unambiguous.
    """
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from sqlalchemy import text

    # Truncate to start clean
    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = _make_test_graph_with_us(sito="TestSite", us_count=3)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite", dry_run=False,
    )
    # Newly inserted rows: 3
    assert result.inserted == 3, f"expected 3 inserted, got {result.inserted!r}"
    # Verify rows are actually present on PG
    with pg_engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM us_table WHERE sito=:s"),
            {"s": "TestSite"},
        ).scalar()
    assert count == 3, f"expected 3 us_table rows, got {count}"


def test_populate_list_dry_run_no_changes_on_pg(pg_engine):
    """dry_run=True returns IngestResult but commits NO changes.

    THE critical test for _DryRunRollback pattern."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = _make_test_graph_with_us(sito="TestSite", us_count=3)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite", dry_run=True,
    )
    # IngestResult still reports the would-be inserts (3) in detection
    assert result.inserted == 3, (
        f"dry_run should still detect 3 inserts, got {result.inserted!r}"
    )
    # But the DB has NO new rows because _DryRunRollback fired
    with pg_engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM us_table WHERE sito=:s"),
            {"s": "TestSite"},
        ).scalar()
    assert count == 0, (
        f"dry_run should have 0 us_table rows after rollback, got {count}"
    )


def test_populate_list_conflict_resolution_graph_wins_on_pg(pg_engine):
    """When DB has a US row and graph has the same US with different
    column values, populate_list updates the row (GRAPH_WINS policy)
    and IngestResult.conflicts captures the diff."""
    import uuid as _uuid
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))
        # Seed: one US row with node_uuid X and d_stratigrafica="OLD"
        my_uuid = str(_uuid.uuid4())
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo, "
            "d_stratigrafica, node_uuid) "
            "VALUES ('TestSite', '1', '1', 'US', 'OLD', :uuid)"
        ), {"uuid": my_uuid})

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = Graph(graph_id="g")
    node = StratigraphicNode(
        node_id=my_uuid, name="1", description="", data={}
    )
    node.attributes = {
        "node_uuid": my_uuid, "us": "1", "sito": "TestSite",
        "area": "1", "unita_tipo": "US",
        "d_stratigrafica": "NEW",  # the diff
    }
    graph.add_node(node)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite", dry_run=False,
    )
    assert result.updated == 1, (
        f"expected 1 update, got {result.updated!r}"
    )
    assert any(c.field == "d_stratigrafica" for c in result.conflicts), (
        f"conflicts should contain d_stratigrafica diff, got "
        f"{result.conflicts!r}"
    )
    # Verify the actual DB value is "NEW"
    with pg_engine.connect() as conn:
        val = conn.execute(
            text("SELECT d_stratigrafica FROM us_table WHERE node_uuid=:u"),
            {"u": my_uuid},
        ).scalar()
    assert val == "NEW", f"expected d_stratigrafica='NEW', got {val!r}"


def test_populate_list_missing_epoch_error_on_pg(pg_engine):
    """MissingEpochError raised + transaction rolled back when graph
    has EpochNode whose (periodo, fase) is not in periodizzazione_table
    and create_missing_epochs=False."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestor, MissingEpochError,
    )
    from s3dgraphy import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = Graph(graph_id="g")
    epoch = EpochNode(
        node_id="epoch_99_x",
        name="Period 99 Phase x",
        start_time=0.0, end_time=0.0,
    )
    if not hasattr(epoch, "attributes") or epoch.attributes is None:
        epoch.attributes = {}
    epoch.attributes["periodo"] = "99"
    epoch.attributes["fase"] = "x"
    graph.add_node(epoch)

    with pytest.raises(MissingEpochError):
        GraphIngestor().populate_list(
            graph=graph, db_path=handle, sito="TestSite",
            dry_run=False, create_missing_epochs=False,
        )

    # Atomic rollback: site_table should NOT have been written either
    with pg_engine.connect() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM site_table WHERE sito=:s"
        ), {"s": "TestSite"}).scalar()
    assert count == 0, (
        f"site_table should be empty (rolled back), got {count}"
    )


def test_populate_list_creates_missing_epochs_on_pg(pg_engine):
    """create_missing_epochs=True inserts the new epoch + returns
    IngestResult.epochs_created=1."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from s3dgraphy import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = Graph(graph_id="g")
    epoch = EpochNode(
        node_id="epoch_99_x",
        name="Period 99 Phase x",
        start_time=1500.0, end_time=1600.0,
    )
    epoch.attributes = {"periodo": "99", "fase": "x"}
    graph.add_node(epoch)

    result = GraphIngestor().populate_list(
        graph=graph, db_path=handle, sito="TestSite",
        dry_run=False, create_missing_epochs=True,
    )
    assert result.epochs_created == 1, (
        f"expected 1 epoch created, got {result.epochs_created!r}"
    )
    # Verify the row is in periodizzazione_table
    with pg_engine.connect() as conn:
        row = conn.execute(text(
            "SELECT periodo, fase FROM periodizzazione_table WHERE sito=:s"
        ), {"s": "TestSite"}).fetchone()
    assert row is not None
    assert str(row[0]) == "99"
    assert str(row[1]) == "x"


def test_populate_list_atomic_rollback_on_pg(pg_engine, monkeypatch):
    """Mock text() to raise RuntimeError mid-transaction. Verify that
    engine.begin() rolls back: no partial writes survive."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync import graph_ingestor as gi_mod
    from sqlalchemy import text

    with pg_engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE us_table, site_table, periodizzazione_table "
            "RESTART IDENTITY CASCADE"
        ))

    handle = DbHandle.from_engine(pg_engine, str(pg_engine.url))
    graph = _make_test_graph_with_us(sito="TestSite", us_count=3)

    # Patch text() inside graph_ingestor to raise on the INSERT INTO
    # us_table statement (after site_table INSERT, so we know SOMETHING
    # was attempted and the rollback has to clean it up).
    original_text = gi_mod.text
    call_count = {"n": 0}

    def fake_text(stmt):
        call_count["n"] += 1
        if "INSERT INTO us_table" in stmt:
            raise RuntimeError("simulated mid-transaction failure")
        return original_text(stmt)

    monkeypatch.setattr(gi_mod, "text", fake_text)

    with pytest.raises(Exception):
        from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
        GraphIngestor().populate_list(
            graph=graph, db_path=handle, sito="TestSite", dry_run=False,
        )

    # site_table INSERT must have been rolled back too
    with pg_engine.connect() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM site_table WHERE sito=:s"
        ), {"s": "TestSite"}).scalar()
    assert count == 0, (
        f"site_table.sito='TestSite' should be 0 after rollback, got {count}"
    )
```

- [ ] **Step 2: Run the 6 tests**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ingest_pg.py -v 2>&1 | tail -15
```

Expected (PG offline / no psycopg2 in dev env): ALL 6 SKIPPED with reason "PG not available at localhost:5433 (...)".

If PG online: 6 PASSED.

- [ ] **Step 3: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected (PG offline): `250 passed, 24 skipped` (250 + 6 new skips).

- [ ] **Step 4: AC-2 sanity**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_ingest_pg.py
git commit -m "$(cat <<'EOF'
test(pg-c/B): 6 L2 PostgreSQL tests for the ingest pipeline

Six cases that pin the PG-C design:

1. test_populate_list_accepts_dbhandle_on_pg - public API
   accepts DbHandle, inserts 3 US rows
2. test_populate_list_dry_run_no_changes_on_pg - THE critical
   test for _DryRunRollback pattern (engine.begin() conditional
   rollback). dry_run=True detects 3 inserts but commits 0.
3. test_populate_list_conflict_resolution_graph_wins_on_pg -
   ConflictResolver GRAPH_WINS works on PG: seed DB with US
   d_stratigrafica='OLD', graph has 'NEW' -> UPDATE applies +
   IngestResult.conflicts captures diff
4. test_populate_list_missing_epoch_error_on_pg - MissingEpochError
   raised + atomic rollback (site_table also rolled back)
5. test_populate_list_creates_missing_epochs_on_pg -
   create_missing_epochs=True INSERTs periodizzazione_table row
6. test_populate_list_atomic_rollback_on_pg - mocked text() raises
   on INSERT INTO us_table after site_table INSERT, verifying
   engine.begin() rolls back the WHOLE transaction (site_table
   stays empty).

All 6 skip cleanly when PG offline / psycopg2 missing.
Uses pg_engine fixture from PG-B's conftest_pg.py.

PG offline: 250 passed, 24 skipped.
PG online: 256 passed, 12 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group C — `tests/sync/test_round_trip_pg.py` (AC-2 cousin for import)

### Task C.1: Create the round-trip identity test

**File:** `tests/sync/test_round_trip_pg.py`

- [ ] **Step 1: Write the file**

```python
# tests/sync/test_round_trip_pg.py
"""PG-C AC-2 cousin: round-trip identity on PostgreSQL.

THE gate test for PG-C. Verifies that the import path on PG produces
a database state equivalent to a fresh export — i.e., the bridge is
idempotent end-to-end on PG.

Flow:
  1. Seed PG with mini_volterra.sqlite data (pg_with_volterra fixture)
  2. Export PG → first.graphml
  3. Import first.graphml back into the SAME PG (re-write)
  4. Re-export PG → second.graphml
  5. Compare structural fingerprints of first.graphml and second.graphml

If the import pipeline drops or mutates data, the second export will
diverge from the first. Reuses _structure() from the existing AC-2
test to ensure identical fingerprint definition.

Skipped cleanly when PG offline / psycopg2 missing.
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def test_round_trip_pg_identity(pg_with_volterra, tmp_path):
    """Full round-trip on PG: seed PG with mini_volterra → export →
    import the exported GraphML back into the SAME PG → re-export →
    compare structural fingerprints.

    THE gate for PG-C."""
    from tests.sync.test_ai03_export_byte_identical import _structure
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))

    out1 = tmp_path / "first.graphml"
    export_graphml(db_path=handle, mapping="pyarchinit_us_mapping",
                   output_path=out1, site_filter="Volterra")

    # Import first.graphml back into the same PG (re-write path).
    # This exercises the entire populate_list pipeline: SELECT, UPDATE
    # for existing rows, ConflictResolver, etc.
    GraphIngestor().populate_list(
        graph=out1, db_path=handle, sito="Volterra",
        dry_run=False, graphml_path=out1,
    )

    out2 = tmp_path / "second.graphml"
    export_graphml(db_path=handle, mapping="pyarchinit_us_mapping",
                   output_path=out2, site_filter="Volterra")

    fp1 = _structure(out1.read_text(encoding="utf-8"))
    fp2 = _structure(out2.read_text(encoding="utf-8"))

    assert fp1 == fp2, (
        f"PG round-trip not idempotent.\n"
        f"  fp1 (post-export):   {fp1!r}\n"
        f"  fp2 (post-reimport): {fp2!r}\n\n"
        f"This is THE PG-C gate. If this fails, the import pipeline "
        f"has regressed on PG. Compare each key (node_count, "
        f"edge_count, labels, row_count, table_count) to find which "
        f"part of the pipeline diverged."
    )
```

- [ ] **Step 2: Run the test**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_pg.py -v 2>&1 | tail -10
```

Expected:
- PG offline: 1 SKIPPED
- PG online + psycopg2: 1 PASSED. If PG export then import then export reproduces the same fingerprint, the import pipeline is structurally correct.
- PG online + test FAILS: STOP. Fingerprint diff is reported in the assertion message. Likely candidates: missing UPDATE on us_table, `_DryRunRollback` accidentally fired, ConflictResolver issue.

- [ ] **Step 3: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected:
- PG offline: `250 passed, 25 skipped` (250 + 1 new skip)
- PG online: `257 passed, 12 skipped`

- [ ] **Step 4: AC-2 sanity**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_round_trip_pg.py
git commit -m "$(cat <<'EOF'
test(pg-c/C): AC-2 cousin - round-trip identity on PostgreSQL

THE gate for PG-C. Single test:

- test_round_trip_pg_identity
  - seeds PG with mini_volterra.sqlite (via pg_with_volterra)
  - exports PG -> first.graphml
  - imports first.graphml back into the SAME PG via populate_list
    (exercises the full ingest pipeline: detection loop, UPDATE
    path, ConflictResolver, atomic transaction)
  - re-exports PG -> second.graphml
  - asserts structural fingerprint (from existing AC-2 _structure())
    is identical between first.graphml and second.graphml

If the import drops or mutates data, the second export diverges
from the first. The assertion message diffs each fingerprint key
for fast triage.

Skipped cleanly when PG offline / psycopg2 missing.

PG offline: 250 passed, 25 skipped.
PG online: 257 passed, 12 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group D — Docs + version 5.7.2-alpha

### Task D.1: Bump `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.7.1-alpha` → `version=5.7.2-alpha`.

Verify:
```bash
grep "^version=" metadata.txt
```
Expected: `version=5.7.2-alpha`.

### Task D.2: Insert Phase 3 PG-C section to dev-log

**File:** `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Insert above PG-B section**

Use the Edit tool to find:

```
---

## Phase 3 — PG-B export pipeline (5.7.1-alpha)
```

Replace with:

```
---

## Phase 3 — PG-C import pipeline (5.7.2-alpha)

**Tag:** `phase3-pgcompat-c-import-5.7.2-alpha`
**Date:** 2026-05-11
**Spec:** `docs/superpowers/specs/2026-05-11-pg-c-import-design.md`
**Plan:** `docs/superpowers/plans/2026-05-11-pg-c-import.md`

### What shipped

- `GraphIngestor.populate_list` works on both SQLite and PostgreSQL
- The single sqlite3.connect() site at graph_ingestor.py:248 (which
  wraps the entire _run body in one BEGIN/COMMIT/ROLLBACK) becomes
  `with handle.engine.begin() as conn:` — identical atomic semantics
  on both backends
- ~10 inner SELECT/INSERT/UPDATE queries translate `?` → `:name` via
  SQLAlchemy `text()`
- `_apply_group_folders_to_sql` helper signature `cur` → `conn`,
  2 internal UPDATEs also flipped
- Public `populate_list(graph, db_path, sito, ...)` keeps `db_path`
  keyword (PG-A/B precedent), accepts `Path | DbHandle | str` via
  Foundation shim. Line 152 `db_path = Path(db_path)` coercion
  REMOVED.
- Private `_run(graph, handle, ...)` accepts DbHandle directly
- `_DryRunRollback` internal sentinel exception class added: raised
  at end of `with` block when `dry_run=True` so engine.begin() rolls
  back. Caught + swallowed outside the `with`. Preserves the
  original "dry_run = no DB writes" semantic on both backends.
- `cur.description` → `result.keys()` (2 sites, SQLAlchemy 2.0
  pattern)
- All `except sqlite3.Error` → `except Exception`
- `import sqlite3` REMOVED from graph_ingestor.py
- ConflictResolver verified pure in-memory (no SQL); zero changes
  needed

### Tests

- 6 new L2 PG cases in test_ingest_pg.py (DbHandle acceptance,
  dry_run rollback — the critical test for _DryRunRollback,
  ConflictResolver, MissingEpochError, create_missing_epochs,
  atomic rollback on forced exception)
- 1 new round-trip identity test in test_round_trip_pg.py (THE
  PG-C gate: PG seeded → export → re-import → re-export →
  fingerprint match)
- All 7 skip cleanly when PG offline / psycopg2 missing
- Total: 250 passed, 25 skipped (PG offline) or 257 passed, 12
  skipped (PG online + psycopg2)
- AC-2 byte-identical preserved (PG-C doesn't touch export)
- tests/sync/test_round_trip.py SQLite stays green (critical
  import-side regression gate)

### Known follow-ups (later milestones)

- **PG-D** (5.7.3-alpha): ParadataStore + GroupStore workspace dir
  on PG (`pyarchinit_DB_folder/<conn_slug>/<sito>/` model). The
  only remaining sqlite3 usage in modules/s3dgraphy/sync/ after
  PG-C ships.
- **Consolidation** (5.7.4-alpha): rename `db_path` → `db_input` on
  all public APIs (populate_list, populate_graph, export_graphml,
  dimensions_with_data, build_groups_from_sql, add_columns,
  backfill_uuids) with proper deprecation cycle.

---

## Phase 3 — PG-B export pipeline (5.7.1-alpha)
```

### Task D.3: Prepend bilingual CHANGELOG entry

**File:** `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Insert above 5.7.1-alpha section**

Use the Edit tool to find:

```
## [5.7.1-alpha] - 2026-05-10
```

Replace with:

```
## [5.7.2-alpha] - 2026-05-11

### Italiano

**PG-C — Il pipeline di IMPORT ora funziona su PostgreSQL.**

Terzo milestone post-Foundation della Phase 3. Ribalta il pipeline di import (`GraphIngestor.populate_list`) sull'infrastruttura cross-backend. Tutti i 250 test SQLite di PG-B restano verdi via shim, INCLUSO il critical `test_round_trip.py` che esercita populate_list end-to-end su SQLite. AC-2 byte-identical preservato (PG-C non tocca export).

- **1 `sqlite3.connect()` sito swappato a `engine.begin()`**: il singolo punto di transazione atomica che wrappa l'intero `_run` body diventa `with handle.engine.begin() as conn:`. Semantica BEGIN/COMMIT/ROLLBACK identica su entrambi i backend.
- **~10 query interne tradotte**: SELECT COUNT/INSERT su site_table, SELECT */INSERT/UPDATE su us_table (loop di detection + write block, con `cur.description` → `result.keys()` per i nomi colonna), SELECT/INSERT su periodizzazione_table, 2 UPDATE in `_apply_group_folders_to_sql` (signature `cur` → `conn`). Tutte usano `text(":name")` con named params.
- **Public API senza breaking change**: `populate_list(graph, db_path, sito, ...)` mantiene il keyword `db_path` ma accetta `Path | DbHandle | str` via shim Foundation. Linea 152 `db_path = Path(db_path)` coercion **RIMOSSA** (avrebbe rotto i caller DbHandle — stessa trap catturata in PG-B Group C). Internal `_run(graph, handle, ...)` ricezione handle direttamente.
- **`_DryRunRollback` internal sentinel exception**: pattern necessario perché `engine.begin()` non ha "conditional rollback". In dry_run mode, alla fine del blocco `with` solleviamo `_DryRunRollback()` per forzare il rollback automatico del context manager, poi swallow l'eccezione fuori dal `with`. Preserva la semantica "dry_run = nessuna modifica DB" su entrambi i backend.
- **ConflictResolver verificato pure in-memory**: zero modifiche a `conflict_resolver.py`. Il policy GRAPH_WINS di AI04 funziona identicamente su PG.
- **`import sqlite3` rimosso da `graph_ingestor.py`**. Dopo PG-C, l'unico sqlite3 residuo in `modules/s3dgraphy/sync/` è in `paradata_store.py` / `group_store.py` (scope PG-D).
- **7 nuovi test L2 PG**: 6 in `test_ingest_pg.py` (DbHandle acceptance, dry_run rollback — il critical per `_DryRunRollback`, ConflictResolver, MissingEpochError, create_missing_epochs, atomic rollback su mock failure) + 1 round-trip identity in `test_round_trip_pg.py` (il gate del milestone). Tutti skippano puliti quando PG offline o psycopg2 mancante.

Test count: 250 → 250 passed, 25 skipped (PG offline) o 257 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato. SQLite round-trip preservato.

### English

**PG-C — Import pipeline now works on PostgreSQL.**

Third post-Foundation milestone of Phase 3. Flips the import pipeline (`GraphIngestor.populate_list`) onto the cross-backend infrastructure. All 250 PG-B SQLite tests stay green via shim, INCLUDING the critical `test_round_trip.py` that exercises populate_list end-to-end on SQLite. AC-2 byte-identical preserved (PG-C doesn't touch export).

- **1 `sqlite3.connect()` site swapped to `engine.begin()`**: the single atomic-transaction point wrapping the entire `_run` body becomes `with handle.engine.begin() as conn:`. BEGIN/COMMIT/ROLLBACK semantics identical on both backends.
- **~10 inner queries translated**: SELECT COUNT / INSERT on site_table, SELECT */INSERT/UPDATE on us_table (detection loop + write block, with `cur.description` → `result.keys()` for column names), SELECT/INSERT on periodizzazione_table, 2 UPDATEs in `_apply_group_folders_to_sql` (signature `cur` → `conn`). All use `text(":name")` with named params.
- **Public API zero-breaking-change**: `populate_list(graph, db_path, sito, ...)` keeps the `db_path` keyword but accepts `Path | DbHandle | str` via the Foundation shim. Line 152 `db_path = Path(db_path)` coercion **REMOVED** (would have broken DbHandle callers — same trap caught in PG-B Group C). Internal `_run(graph, handle, ...)` receives the handle directly.
- **`_DryRunRollback` internal sentinel exception**: pattern required because `engine.begin()` has no conditional rollback. In dry_run mode, at end of the `with` block we raise `_DryRunRollback()` to force the context manager to roll back, then swallow outside the `with`. Preserves the "dry_run = no DB writes" semantic on both backends.
- **ConflictResolver verified pure in-memory**: zero changes to `conflict_resolver.py`. AI04's GRAPH_WINS policy works identically on PG.
- **`import sqlite3` removed from `graph_ingestor.py`**. After PG-C, the only remaining sqlite3 usage in `modules/s3dgraphy/sync/` is in `paradata_store.py` / `group_store.py` (PG-D scope).
- **7 new L2 PG tests**: 6 in `test_ingest_pg.py` (DbHandle acceptance, dry_run rollback — the critical test for `_DryRunRollback`, ConflictResolver, MissingEpochError, create_missing_epochs, atomic rollback on mock failure) + 1 round-trip identity in `test_round_trip_pg.py` (the milestone gate). All skip cleanly when PG offline or psycopg2 missing.

Test count: 250 → 250 passed, 25 skipped (PG offline) or 257 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved. SQLite round-trip preserved.

---

## [5.7.1-alpha] - 2026-05-10
```

### Task D.4: Commit + final verification

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git log --oneline 2268463a..HEAD
git log 2268463a..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v 2>&1 | tail -5
grep "^version=" metadata.txt
```

Expected:
- 3 commits since `2268463a`: A, B, C
- Co-Authored-By count: `0`
- Test suite: `250 passed, 25 skipped` (PG offline)
- AC-2: PASS
- SQLite round-trip: ALL PASS
- Version: `5.7.2-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(pg-c/D): docs + version bump 5.7.2-alpha

PG-C milestone documentation: bilingual CHANGELOG entry,
dev-log Phase 3 PG-C section, version bump 5.7.1-alpha -> 5.7.2-alpha.

Cumulative deliverables (Groups A-D):
- graph_ingestor.py: 1 sqlite3 site + ~10 inner queries -> SQLAlchemy
  via Foundation shim. _DryRunRollback internal sentinel exception
  for dry_run mode. populate_list accepts shim. _run accepts handle.
  cur.description -> result.keys(). _apply_group_folders_to_sql
  signature cur -> conn. import sqlite3 removed.
- 6 new L2 PG tests in test_ingest_pg.py
- 1 round-trip identity test in test_round_trip_pg.py (PG-C gate)

Test count: 250 -> 250 passed, 25 skipped (PG offline) or
250 -> 257 passed, 12 skipped (PG online with psycopg2).
AC-2 byte-identical baseline preserved.
SQLite round-trip preserved (critical import-side regression gate).

Spec: docs/superpowers/specs/2026-05-11-pg-c-import-design.md
Plan: docs/superpowers/plans/2026-05-11-pg-c-import.md
Predecessor: phase3-pgcompat-b-export-5.7.1-alpha (2121369e)
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

- [ ] **Step 3: Post-commit verification**

```bash
git log --oneline 2268463a..HEAD
git log 2268463a..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 4 commits since `2268463a`: A, B, C, D
- Co-Authored-By count: `0`
- `250 passed, 25 skipped`
- Version: `5.7.2-alpha`

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
git tag -a phase3-pgcompat-c-import-5.7.2-alpha -m "$(cat <<'EOF'
PG-C - Import pipeline on PostgreSQL

Third post-Foundation milestone of Phase 3 (PG-compat refactor).
GraphIngestor.populate_list now works on both SQLite and
PostgreSQL backends. NO changes to paradata_store, group_store -
those are PG-D scope.

Cumulative deliverables (Groups A-D, 4 commits):

- graph_ingestor.py: 1 sqlite3.connect() site at line 248
  (wrapping entire _run body) swapped to `with engine.begin() as
  conn:` - identical BEGIN/COMMIT/ROLLBACK atomic semantics on
  both backends.
- ~10 inner SQL queries translated to text() + named params:
  SELECT/INSERT site_table, SELECT */INSERT/UPDATE us_table
  (detection + write loops), SELECT/INSERT periodizzazione_table,
  2 UPDATEs in _apply_group_folders_to_sql helper (signature
  cur -> conn).
- cur.description -> result.keys() (2 sites, SQLAlchemy 2.0).
- Public populate_list(graph, db_path, sito, ...) accepts
  Path | DbHandle | str via shim. Line 152 db_path = Path(db_path)
  coercion REMOVED. Internal _run accepts handle directly.
- _DryRunRollback internal sentinel exception class added:
  raised at end of with block when dry_run=True so
  engine.begin() rolls back. Caught + swallowed outside.
  Preserves the original dry_run semantic on both backends.
- All except sqlite3.Error -> except Exception.
- import sqlite3 REMOVED from graph_ingestor.py.
- ConflictResolver verified pure in-memory (no SQL refactor).

Tests: 6 new PG L2 tests in test_ingest_pg.py + 1 round-trip
identity test in test_round_trip_pg.py (THE PG-C gate). All
skip cleanly when PG offline / psycopg2 missing.

Test counts: 250 -> 250 passed, 25 skipped (PG offline) or
250 -> 257 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical preserved.
SQLite round-trip preserved (critical import-side regression gate).

Spec: docs/superpowers/specs/2026-05-11-pg-c-import-design.md
Plan: docs/superpowers/plans/2026-05-11-pg-c-import.md
Predecessor: phase3-pgcompat-b-export-5.7.1-alpha (2121369e)
EOF
)"
```

### Task E.3: Verify the tag

```bash
echo "=== Tag created locally ==="
git tag -n5 phase3-pgcompat-c-import-5.7.2-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse phase3-pgcompat-c-import-5.7.2-alpha^{commit}
git rev-parse HEAD
echo "=== Tag is annotated ==="
git cat-file -t phase3-pgcompat-c-import-5.7.2-alpha
echo "=== Tag message has NO Co-Authored-By ==="
git tag -l --format='%(contents)' phase3-pgcompat-c-import-5.7.2-alpha | grep -c Co-Authored-By
```

Final grep MUST return `0`.

### Task E.4: Push tag + branch

```bash
git push origin phase3-pgcompat-c-import-5.7.2-alpha 2>&1 | tail -3
git push origin Stratigraph_00001 2>&1 | tail -3
```

### Task E.5: Verify on origin

```bash
git ls-remote --tags origin | grep "phase3-pgcompat-c-import-5.7.2-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected: tag listed (with `^{}` dereferenced commit line), branch tip equals local HEAD.

### Task E.6: Memory snapshot (controller, no subagent)

After Group E ships, the controller updates `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move PG-C from PENDING to SHIPPED with all SHAs + lessons learned
- Update milestone table
- Update `MEMORY.md` index line

---

## Self-Review

This plan covers every PG-C spec requirement:

| Spec section | Plan task |
|---|---|
| §3.1 Q1=b (`db_path` kwarg accepts DbHandle via shim) | Group A Step 2 |
| §3.2 Approach 1 (single-file refactor) | Group A single commit |
| §3.3 Atomic transaction + `_DryRunRollback` | Group A Step 1 (class def) + Step 8 (usage) |
| §3.4 ConflictResolver compat | No code change (verified pure in-memory) |
| §3.5 SQLAlchemy 2.0 compliance | Group A throughout (text(), result.keys(), engine.begin()) |
| §4.1 Modified production files (1) | Group A |
| §4.3 New test files (2) | Groups B and C |
| §4.4 Modified release-tracking files (3) | Group D |
| §4.5 NOT touched | Documented + verified via AC-2 + SQLite round-trip sanity ping after Group A |
| §5 SQL dialect compat | Group A throughout |
| §6 Data flow + error handling | Group A Step 8 (`_DryRunRollback` + except blocks) |
| §7 Test strategy | Groups B and C |
| §8 Acceptance criteria | Pinned by Groups A (regression), B (6 PG L2), C (round-trip gate) |
| §9 Release plan | Groups D + E |

**Type consistency check:** `DbHandle`, `_resolve_db_handle`, `_columns_of`, `text`, `_DryRunRollback`, `pg_with_volterra` — all spelled and used consistently across Groups.

**No placeholders:** every step has runnable code, exact commands, or specific file edits.

**Scope check:** Plan is focused on PG-C only. PG-D files in §4.5 NOT touched.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-pg-c-import.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review (spec compliance + code quality), fast iteration

**2. Inline Execution** — execute tasks in this session via `executing-plans`, batch with checkpoints

If **Subagent-Driven**, recommended batching:
- Group 0 (2 tasks) → no subagent — pure git
- Group A → 1 subagent (large refactor ~150 LOC, critical AC-2 + SQLite round-trip ping after commit)
- Group B → 1 subagent (6 PG L2 tests)
- Group C → 1 subagent (1 round-trip identity test — the PG-C gate)
- Group D → 1 subagent (docs + version + final verification)
- Group E → 1 subagent (tag + push, gate per user approval)
- Memory snapshot → no subagent (controller writes after E ships)

If **Inline Execution**, batch by Group with checkpoint after each.
