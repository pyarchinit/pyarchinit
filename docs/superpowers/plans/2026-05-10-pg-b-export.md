# PG-B — Export pipeline on PostgreSQL Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the s3dgraphy bridge's export pipeline (GraphProjector + GraphMLWriter + GroupProjector) cross-backend. All 11 `sqlite3.connect()` call sites swap to SQLAlchemy `engine.connect()` / `engine.begin()`. Public APIs keep the legacy `db_path` keyword name and accept `Path | DbHandle | str` via Foundation's `_resolve_db_handle` shim. **NO SQL query content changes** — only connection wrapping + placeholder syntax (`?` → `:name`). Release `5.7.1-alpha`.

**Architecture:** Per-file Groups (8 Groups, ~8 commits). Production refactor (Groups A/B/C) precedes test infrastructure (D) precedes new PG L2 tests (E/F) precedes docs (G) precedes tag (H). AC-2 byte-identical guard MUST stay green at every Group with code changes — sanity ping after each commit in A/B/C is critical.

**Tech Stack:** Python 3.9+, SQLAlchemy 2.0+ (production version, 1.4 compatible incidentally), psycopg2-binary>=2.9 (Foundation), Foundation + PG-A helpers reused.

**Spec source of truth:** `docs/superpowers/specs/2026-05-10-pg-b-export-design.md` (commit `069d8c14`)

**Predecessor releases:**
- PG-A: tag `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- Foundation: tag `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)

**Memory notes (consult before refactoring):**
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` — current Phase 3 state
- `~/.claude/projects/.../memory/feedback_no_claude_coauthor.md` — strict commit-author rule
- `~/.claude/projects/.../memory/MEMORY.md` — Phase 1 node_uuid migration is MANUAL

**Commit-message rule:** Never include `Co-Authored-By: Claude …` trailers. Sole author is Enzo Cocca. Every HEREDOC in this plan is already trailer-free; do not re-add it. After each commit run `git log -1 --format=%B HEAD | grep -c Co-Authored-By` — must return `0`.

**Local PG (already set up during Foundation):** `postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg`. The `pg_engine` fixture skips cleanly when PG offline or psycopg2 missing — no setup needed in those cases.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `tests/sync/test_export_pg.py` | 5 L2 PG cases for the export pipeline. Skip cleanly when PG offline. ~120 LOC. |
| `tests/sync/test_ai03_export_pg_structural.py` | 1 L2 PG case = AC-2 cousin. PG export of mini_volterra produces same structural fingerprint as `mini_volterra_baseline_ai03.graphml`. ~80 LOC. |

### Modified

| Path | Why |
|---|---|
| `modules/s3dgraphy/sync/graph_projector.py` | 5 distinct `sqlite3.connect()` sites swap to `engine.connect()` / `engine.begin()`. SQL queries: `?` placeholder → `:name` via `text()`. `except sqlite3.Error` → `except Exception`. Public `populate_graph(db_path, sito, ...)` accepts `Path \| DbHandle \| str` via shim. Internal helpers (`_verify_node_uuid_column`, `_propagate_node_uuid_and_us`, `_enrich_into`, `_merge_groups`, `_emit_toponym_chain`) accept DbHandle internally. ~150 LOC delta. |
| `modules/s3dgraphy/sync/group_projector.py` | 2 `sqlite3.connect()` sites (`dimensions_with_data`, `build_groups_from_sql`) swap to engine-based. Both functions accept `DbHandle \| Path \| str` via shim. ~40 LOC delta. |
| `modules/s3dgraphy/sync/graphml_writer.py` | 1 `sqlite3.connect()` site (`_read_first_sito` at line 136) swaps to engine-based. `export_graphml(db_path, mapping, output_path, ...)` accepts shim. Internal call at line 1800 (`GraphProjector().populate_graph(...)`) passes the resolved handle. ~30 LOC delta. |
| `tests/sync/conftest_pg.py` | Add `load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper (~50 LOC). Reflects SQLite schema via SQLAlchemy `inspect()`, emits CREATE TABLE IF NOT EXISTS on PG, TRUNCATE, executemany INSERT. Add `pg_with_volterra` fixture wrapping the helper for the AC-2 cousin. |
| `metadata.txt` | Bump `version=5.7.0-alpha` → `version=5.7.1-alpha`. 1 line. |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.1-alpha]` section. ~40 LOC. |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 — PG-B export section. ~30 LOC. |

### Explicitly NOT touched (per spec §4.5)

- `modules/s3dgraphy/sync/graph_ingestor.py:populate_list` — main import flow (PG-C)
- `modules/s3dgraphy/sync/paradata_store.py` (PG-D)
- `modules/s3dgraphy/sync/group_store.py` (PG-D)
- `modules/s3dgraphy/sync/_db_handle.py` (Foundation — no changes)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2 itself — must stay
  green untouched; only its `_structure()` helper is imported by the PG cousin)
- All other 250 SQLite tests — must stay green via the backward-compat shim
- PR #6 round-trip fixture (Emanuel's repo) — no changes required

---

## Test strategy

- **L0 unit (none new):** Foundation + PG-A already cover the shim, `_columns_of`, and Inspector pattern. PG-B reuses these patterns without adding L0 tests.
- **L1 SQLite (existing 250):** Continue to pass via the backward-compat shim accepting `Path` legacy callers.
- **L2 PG (NEW):** 5 cases in `test_export_pg.py` + 1 AC-2 cousin in `test_ai03_export_pg_structural.py`. All skip cleanly when PG offline / psycopg2 missing.
- **L3 regression guards (existing, MUST stay green):**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v   # AC-2
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no            # full SQLite suite
```

**AC-2 is critical for PG-B.** Groups A/B/C touch code AC-2 exercises. After each Group commit, AC-2 sanity ping is mandatory. If AC-2 breaks → STOP, do not proceed.

Decision-pinning matrix (PG-B):

| Decision / Acceptance | Pinning test |
|---|---|
| Q1=a (`db_path` kwarg accepts DbHandle via shim) | Test #1 + AC-2 (Path still works) |
| Q2=a (`load_sqlite_into_pg` helper) | Indirect via every test using `pg_with_volterra` fixture |
| Approach 1 (per-file Groups) | AC-2 sanity ping after each production-code Group |
| `_verify_node_uuid_column` cross-dialect | Existing AC-2 (it calls populate_graph which calls this) |
| `_emit_toponym_chain` PG-compatible | Test #3 |
| `_propagate_node_uuid_and_us` PG-compatible | Test #2 |
| `_merge_groups` PG-compatible | Test #1 (group structures appear correctly) |
| `_enrich_into` PG-compatible | AC-2 cousin (fingerprint match) |
| `dimensions_with_data` PG-compatible | Test #4 |
| `export_graphml` end-to-end PG-compatible | Test #5 + AC-2 cousin |
| AC-2 stays green (regression guard) | `test_ai03_export_byte_identical.py` (existing, untouched) |

Test count progression:
- Pre PG-B (post PG-A baseline): `250 passed, 12 skipped` (PG offline) or `256 passed, 6 skipped` (PG online)
- Post Groups A/B/C (refactor only, no new tests): unchanged (250 passed, 12 skipped)
- Post Group D (helper + fixture, no new tests): unchanged
- Post Group E (5 PG L2 in `test_export_pg.py`): PG offline `250 passed, 17 skipped`; PG online `255 passed, 6 skipped`
- Post Group F (AC-2 cousin): PG offline `250 passed, 18 skipped`; PG online `256 passed, 6 skipped`
- Post Group G (docs only): unchanged

Final:
- PG offline: **250 passed, 18 skipped**
- PG online + psycopg2 + local PG: **256 passed, 6 skipped**

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

Expected: tracked changes empty, last commit is `069d8c14 spec(pg-b-export): ...`, `0\t0` ahead-behind.

- [ ] **Step 2: Verify predecessor tag exists**

```bash
git tag --list | grep -E "phase3-pgcompat-a-migration-5.7.0-alpha"
```

Expected: `phase3-pgcompat-a-migration-5.7.0-alpha` listed.

- [ ] **Step 3: Capture baseline test count**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 12 skipped` (PG-A baseline).

- [ ] **Step 4: Baseline AC-2 PASS**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

### Task 0.2: Create PG-B rollback safety tag

**Files:** none (git operation)

- [ ] **Step 1: Create rollback tag**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git tag -a pre-pg-b-export -m "Rollback point before PG-B export milestone

Predecessor: phase3-pgcompat-a-migration-5.7.0-alpha (45803d83)
Spec commit: 069d8c14

If PG-B needs to be reverted, reset hard to this tag."
git push origin pre-pg-b-export
```

Expected: `* [new tag]         pre-pg-b-export -> pre-pg-b-export`.

---

## Group A — `graph_projector.py` refactor (5 sites)

The most complex Group. 5 distinct `sqlite3.connect()` call sites in 5 methods, plus the public `populate_graph` signature shim.

**CRITICAL RULES for Group A:**
- NO SQL query content changes — only connection wrapping + placeholder syntax (`?` → `:name`)
- All `except sqlite3.Error` → `except Exception`
- SQLAlchemy 2.0-compliant (no `.execute()` legacy, no `bind=` legacy)
- AC-2 sanity ping IMMEDIATELY after the commit. If broken, STOP.

### Task A.1: Refactor `graph_projector.py` to SQLAlchemy

**File:** `modules/s3dgraphy/sync/graph_projector.py`

- [ ] **Step 1: Add import for `_resolve_db_handle` + `text`**

Use the Edit tool. Find the import block near the top:

```python
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING
```

Replace with:

```python
import sqlite3  # kept for legacy except sqlite3.Error catches in any remaining code; will be removed in Consolidation if unused after this commit
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import text

from ._db_handle import DbHandle, _columns_of, _resolve_db_handle
```

NOTE: keep the `import sqlite3` line for now (some `except sqlite3.Error` clauses elsewhere in the file may still reference it — Python doesn't require the module to be imported just because the exception type is named; but if grep shows zero remaining uses after this commit, remove it in Step 7 cleanup). Verify after the refactor with `grep -n sqlite3 graph_projector.py`.

- [ ] **Step 2: Refactor site #1 — `_verify_node_uuid_column` (~line 290-309)**

Find this exact block:

```python
    def _verify_node_uuid_column(self, db_path: Path) -> None:
        """Ensure the Phase-1 migration that added ``us_table.node_uuid``
        has been applied. Raises :class:`ProjectionError` otherwise.

        Extracted from ``populate_graph`` in AI05 Group C step 2 so the
        schema-check is testable in isolation and reusable by any future
        method that touches strat tables.
        """
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(us_table)")
            cols = {row[1] for row in cur.fetchall()}
            conn.close()
        except sqlite3.Error as e:
            raise ProjectionError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise ProjectionError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")
```

Replace with:

```python
    def _verify_node_uuid_column(self, db_path) -> None:
        """Ensure the Phase-1 migration that added ``us_table.node_uuid``
        has been applied. Raises :class:`ProjectionError` otherwise.

        PG-B (5.7.1-alpha): accepts ``Path | DbHandle | str`` via shim.
        Cross-backend introspection via Foundation's ``_columns_of``.
        """
        try:
            handle = _resolve_db_handle(db_path)
            cols = _columns_of(handle.engine, "us_table")
        except Exception as e:
            raise ProjectionError(f"Cannot read us_table schema: {e}") from e
        if "node_uuid" not in cols:
            raise ProjectionError(
                "us_table.node_uuid column missing — run "
                "scripts/migrations/2026_05_node_uuid_backfill.py --apply")
```

- [ ] **Step 3: Refactor site #2 — `_propagate_node_uuid_and_us` (~line 366)**

Find this exact block (the open of the sqlite3 connection at line 366 and the long body that ends at line 396):

```python
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT us, node_uuid, sito, area, unita_tipo, "
                "periodo_iniziale, fase_iniziale, rapporti, "
                "d_stratigrafica, d_interpretativa, attivita, struttura, "
                "settore, ambient, saggio, quad_par, documentazione "
                "FROM us_table WHERE sito = ?",
                (sito,),
            )
            rows = cur.fetchall()

            # AI08-F2 hotfix: lookup datazione_estesa per (periodo, fase)
            # from periodizzazione_table so each US can carry its
            # period's full date string.
            period_datazione: dict = {}
            try:
                for p_per, p_fase, p_dat in cur.execute(
                    "SELECT periodo, fase, datazione_estesa "
                    "FROM periodizzazione_table WHERE sito = ?",
                    (sito,),
                ).fetchall():
                    if p_dat:
                        period_datazione[
                            (str(p_per), str(p_fase))
                        ] = str(p_dat)
            except Exception:
                period_datazione = {}
        finally:
            conn.close()
```

Replace with:

```python
        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT us, node_uuid, sito, area, unita_tipo, "
                    "periodo_iniziale, fase_iniziale, rapporti, "
                    "d_stratigrafica, d_interpretativa, attivita, struttura, "
                    "settore, ambient, saggio, quad_par, documentazione "
                    "FROM us_table WHERE sito = :sito"
                ),
                {"sito": sito},
            ).fetchall()

            # AI08-F2 hotfix: lookup datazione_estesa per (periodo, fase)
            # from periodizzazione_table so each US can carry its
            # period's full date string.
            period_datazione: dict = {}
            try:
                for p_per, p_fase, p_dat in conn.execute(
                    text(
                        "SELECT periodo, fase, datazione_estesa "
                        "FROM periodizzazione_table WHERE sito = :sito"
                    ),
                    {"sito": sito},
                ).fetchall():
                    if p_dat:
                        period_datazione[
                            (str(p_per), str(p_fase))
                        ] = str(p_dat)
            except Exception:
                period_datazione = {}
```

NOTE: the `finally: conn.close()` is removed because the `with` context manager handles it automatically. The inner `try/except Exception` was already broad (it wasn't `except sqlite3.Error`), so it stays unchanged.

- [ ] **Step 4: Refactor site #3 — `_enrich_into` (~line 508 + 4 nested except blocks)**

Find this block opening the connection at line 508:

```python
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
        except sqlite3.Error:
            return

        try:
```

Replace with:

```python
        try:
            handle = _resolve_db_handle(db_path)
            conn = handle.engine.connect()
        except Exception:
            return

        try:
```

NOTE: we use `engine.connect()` (manual context) instead of `with engine.connect() as conn:` because the original method has a `try/finally: conn.close()` structure with multiple nested `try/except` blocks for individual queries. Preserving the structure minimizes diff risk. Add a `conn.close()` at the end.

Now find this exact inner block (the first nested except at line 519-525):

```python
            try:
                cursor.execute(
                    "SELECT periodo, fase, cron_iniziale, cron_finale, "
                    "descrizione FROM periodizzazione_table"
                )
                raw_rows = cursor.fetchall()
            except sqlite3.Error:
                raw_rows = []
```

Replace with:

```python
            try:
                raw_rows = conn.execute(
                    text(
                        "SELECT periodo, fase, cron_iniziale, cron_finale, "
                        "descrizione FROM periodizzazione_table"
                    )
                ).fetchall()
            except Exception:
                raw_rows = []
```

Find the second nested except (around line 593-595):

```python
            except sqlite3.Error:
                pass  # missing table is tolerated; epoch_count just stays 0
```

Replace with:

```python
            except Exception:
                pass  # missing table is tolerated; epoch_count just stays 0
```

Find the third nested try/except block (around line 602-618):

```python
            try:
                if sito_filter is not None:
                    cursor.execute(
                        "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                        "fase_iniziale, rapporti, d_stratigrafica "
                        "FROM us_table WHERE sito = ?",
                        (sito_filter,),
                    )
                else:
                    cursor.execute(
                        "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                        "fase_iniziale, rapporti, d_stratigrafica "
                        "FROM us_table"
                    )
                rows = cursor.fetchall()
            except sqlite3.Error:
                rows = []
```

Replace with:

```python
            try:
                if sito_filter is not None:
                    rows = conn.execute(
                        text(
                            "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                            "fase_iniziale, rapporti, d_stratigrafica "
                            "FROM us_table WHERE sito = :sito"
                        ),
                        {"sito": sito_filter},
                    ).fetchall()
                else:
                    rows = conn.execute(
                        text(
                            "SELECT us, sito, area, unita_tipo, periodo_iniziale, "
                            "fase_iniziale, rapporti, d_stratigrafica "
                            "FROM us_table"
                        )
                    ).fetchall()
            except Exception:
                rows = []
```

Find the closing `finally: cursor.close(); conn.close()` block (search for the end of the outer try in `_enrich_into`). Replace any remaining `cursor.close()` or `conn.close()` calls so that ONLY `conn.close()` remains at the very end of the try block (cursor is no longer a separate object — `conn.execute()` returns a Result directly).

If the original has:
```python
        finally:
            cursor.close()
            conn.close()
```
Replace with:
```python
        finally:
            conn.close()
```

If the original has:
```python
        finally:
            conn.close()
```
Leave unchanged (no cursor to close).

- [ ] **Step 5: Refactor site #4 — `_merge_groups` (~line 756)**

Find this exact block:

```python
        if strat_by_name and not node_uuid_to_id:
            try:
                conn = sqlite3.connect(str(db_path))
                try:
                    cur = conn.execute(
                        "SELECT node_uuid, us FROM us_table "
                        "WHERE sito=? AND node_uuid IS NOT NULL",
                        (sito,),
                    )
                    for nu, us_val in cur.fetchall():
                        if nu is None or us_val is None:
                            continue
                        node = strat_by_name.get(str(us_val))
                        if node is not None:
                            node_uuid_to_id[str(nu)] = node.node_id
                finally:
                    conn.close()
            except sqlite3.Error:
                pass
```

Replace with:

```python
        if strat_by_name and not node_uuid_to_id:
            try:
                handle = _resolve_db_handle(db_path)
                with handle.engine.connect() as conn:
                    rows = conn.execute(
                        text(
                            "SELECT node_uuid, us FROM us_table "
                            "WHERE sito=:sito AND node_uuid IS NOT NULL"
                        ),
                        {"sito": sito},
                    ).fetchall()
                    for nu, us_val in rows:
                        if nu is None or us_val is None:
                            continue
                        node = strat_by_name.get(str(us_val))
                        if node is not None:
                            node_uuid_to_id[str(nu)] = node.node_id
            except Exception:
                pass
```

- [ ] **Step 6: Refactor site #5 — `_emit_toponym_chain` (~line 872)**

Find this exact block:

```python
        import hashlib
        try:
            conn = sqlite3.connect(str(db_path))
            try:
                cur = conn.execute(
                    "SELECT nazione, regione, provincia, comune "
                    "FROM site_table WHERE sito=?",
                    (sito,),
                )
                row = cur.fetchone()
            finally:
                conn.close()
        except sqlite3.Error as e:
            logging.getLogger(__name__).info(
                "_emit_toponym_chain: site_table not accessible (%s); "
                "skipping toponym chain",
                e,
            )
            return
```

Replace with:

```python
        import hashlib
        try:
            handle = _resolve_db_handle(db_path)
            with handle.engine.connect() as conn:
                row = conn.execute(
                    text(
                        "SELECT nazione, regione, provincia, comune "
                        "FROM site_table WHERE sito=:sito"
                    ),
                    {"sito": sito},
                ).fetchone()
        except Exception as e:
            logging.getLogger(__name__).info(
                "_emit_toponym_chain: site_table not accessible (%s); "
                "skipping toponym chain",
                e,
            )
            return
```

- [ ] **Step 7: Cleanup unused `import sqlite3` if applicable**

After Steps 2-6, run:

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
grep -n sqlite3 modules/s3dgraphy/sync/graph_projector.py
```

If the only remaining mention is the `import sqlite3` line (no `sqlite3.connect`, no `sqlite3.Error`), remove the import. Otherwise leave the import in place.

- [ ] **Step 8: Update `populate_graph` signature docstring**

The `populate_graph` method signature (around line ~117-130) currently looks like:

```python
    def populate_graph(
        self,
        db_path: Path,
        sito: str,
        ...
```

The TYPE annotation `db_path: Path` is now misleading since the function accepts more. Update via the Edit tool to:

```python
    def populate_graph(
        self,
        db_path,  # Path | DbHandle | str — resolved via _resolve_db_handle shim
        sito: str,
        ...
```

(Remove the `: Path` annotation, add inline comment. Or use `db_path: "Path | DbHandle | str"` as a string forward ref. The plain removal is simpler.)

Find the `populate_graph` docstring and add a one-line note:

```python
        """Drive the AI03 export pipeline on a pyarchinit DB.

        PG-B (5.7.1-alpha): ``db_path`` accepts ``Path | DbHandle | str``
        via the ``_resolve_db_handle`` shim from Foundation. Backward
        compat preserved for legacy callers passing a Path.
        ...
        """
```

(Use the Edit tool to find the existing docstring opening line and insert the PG-B note after it.)

- [ ] **Step 9: Run SQLite suite to confirm no regression**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 12 skipped` (unchanged — Group A is refactor only, no new tests, no behaviour changes on SQLite path).

- [ ] **Step 10: AC-2 sanity ping (CRITICAL)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

**If AC-2 FAILS:** STOP. Do not commit. Investigate `_structure()` diff:

```bash
PYTHONPATH="$PWD" python -c "
from tests.sync.test_ai03_export_byte_identical import _structure, FIXTURE_DB, BASELINE
import shutil, tempfile
from pathlib import Path
tmp_dir = Path(tempfile.mkdtemp())
db = tmp_dir / 'mini_volterra.sqlite'
shutil.copy2(FIXTURE_DB, db)
from modules.s3dgraphy.sync.graphml_writer import export_graphml
out = tmp_dir / 'actual.graphml'
export_graphml(db_path=db, mapping='pyarchinit_us_mapping', output_path=out)
actual = _structure(out.read_text(encoding='utf-8'))
baseline = _structure(BASELINE.read_text(encoding='utf-8'))
print('actual:  ', actual)
print('baseline:', baseline)
print('diff:    ', {k: (actual[k], baseline[k]) for k in actual if actual[k] != baseline[k]})
"
```

Compare keys: `node_count`, `edge_count`, `labels`, `row_count`, `table_count`. If the diff is structural (different node/edge counts) → refactor regression, investigate which Step introduced it. If the diff is cosmetic (label string with extra space) → may indicate SQLAlchemy quoting issue, surface to user. **Do NOT re-baseline without explicit user approval.**

- [ ] **Step 11: Commit Group A**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git add modules/s3dgraphy/sync/graph_projector.py
git commit -m "$(cat <<'EOF'
refactor(pg-b/A): graph_projector cross-backend via SQLAlchemy

5 distinct sqlite3.connect() sites swapped to engine.connect()
via Foundation's _resolve_db_handle shim:

1. _verify_node_uuid_column - uses _columns_of dispatcher
2. _propagate_node_uuid_and_us - single engine.connect() wraps both
   us_table and periodizzazione_table SELECTs
3. _enrich_into - manual conn lifecycle (handle.engine.connect() +
   conn.close()) preserves the multi-nested-try structure with
   minimal diff
4. _merge_groups - single engine.connect() for the node_uuid_to_id
   lookup
5. _emit_toponym_chain - single engine.connect() for site_table read

All SQL queries unchanged in content - only ? -> :name placeholder
syntax via SQLAlchemy text(). All except sqlite3.Error -> except
Exception (broader, for SQLAlchemy + psycopg2 raises).

Public populate_graph(db_path, sito, ...) accepts Path | DbHandle |
str via the shim - existing call sites (graphml_writer.py:1800, QGIS
bridge dialog) continue to work passing Path.

NO query content changes. NO behaviour changes on SQLite path.
AC-2 byte-identical structural fingerprint preserved.
250 passed, 12 skipped (unchanged).
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group B — `group_projector.py` refactor (2 sites)

### Task B.1: Refactor `group_projector.py` to SQLAlchemy

**File:** `modules/s3dgraphy/sync/group_projector.py`

- [ ] **Step 1: Update imports**

Use the Edit tool. Find:

```python
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
```

Replace with:

```python
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
```

(Remove `import sqlite3` since both sites in this file use it and they all get refactored.)

- [ ] **Step 2: Refactor `dimensions_with_data` (~line 87-106)**

Find this exact block:

```python
def dimensions_with_data(db_path: Path, sito: str) -> List[str]:
    """Return subset of {area, struttura, attivita, settore,
    ambient, saggio, quad_par} that has at least one non-empty
    value in us_table for *sito*. Used by the dialog UI to
    pre-check the right boxes (D2)."""
    out = []
    conn = sqlite3.connect(str(db_path))
    try:
        for col in _SQL_DIMENSIONS:
            row = conn.execute(
                f"SELECT 1 FROM us_table "
                f"WHERE sito=? AND {col} IS NOT NULL AND TRIM({col})<>'' "
                f"LIMIT 1",
                (sito,),
            ).fetchone()
            if row is not None:
                out.append(col)
    finally:
        conn.close()
    return out
```

Replace with:

```python
def dimensions_with_data(db_path, sito: str) -> List[str]:
    """Return subset of {area, struttura, attivita, settore,
    ambient, saggio, quad_par} that has at least one non-empty
    value in us_table for *sito*. Used by the dialog UI to
    pre-check the right boxes (D2).

    PG-B (5.7.1-alpha): ``db_path`` accepts ``Path | DbHandle | str``
    via the ``_resolve_db_handle`` shim from Foundation.
    """
    out = []
    handle = _resolve_db_handle(db_path)
    with handle.engine.connect() as conn:
        for col in _SQL_DIMENSIONS:
            row = conn.execute(
                text(
                    f"SELECT 1 FROM us_table "
                    f"WHERE sito=:sito AND {col} IS NOT NULL "
                    f"AND TRIM({col})<>'' LIMIT 1"
                ),
                {"sito": sito},
            ).fetchone()
            if row is not None:
                out.append(col)
    return out
```

NOTE: f-string interpolation of `{col}` is preserved — `col` comes from the hardcoded `_SQL_DIMENSIONS` tuple, NOT user input. No SQL injection risk. Only the `?` → `:sito` placeholder changes.

- [ ] **Step 3: Refactor `build_groups_from_sql` (~line 109-163)**

Find this exact block:

```python
    conn = sqlite3.connect(str(db_path))
    try:
        for dim in valid_dims:
            # Distinct values + member UUIDs in one pass
            rows = conn.execute(
                f"SELECT {dim}, node_uuid FROM us_table "
                f"WHERE sito=? AND {dim} IS NOT NULL "
                f"AND TRIM({dim})<>'' AND node_uuid IS NOT NULL",
                (sito,),
            ).fetchall()
            # Group by value
            buckets: dict = {}
            for value, node_uuid in rows:
                buckets.setdefault(str(value), []).append(node_uuid)
            node_class, kind_enum = _resolve_node_class_and_kind(dim)
            for name, member_uuids in buckets.items():
                # Deterministic UUID5 from (sito, dim, name)
                key = f"{sito}|{dim}|{name}"
                group_uuid = str(uuid.uuid5(
                    _PYARCHINIT_GROUP_NAMESPACE, key))
                out.append(GroupSpec(
                    group_uuid=group_uuid,
                    name=name,
                    group_kind=dim,
                    member_us_uuids=list(member_uuids),
                    node_class=node_class,
                    kind=kind_enum,
                ))
    finally:
        conn.close()
    return out
```

Replace with:

```python
    handle = _resolve_db_handle(db_path)
    with handle.engine.connect() as conn:
        for dim in valid_dims:
            # Distinct values + member UUIDs in one pass
            rows = conn.execute(
                text(
                    f"SELECT {dim}, node_uuid FROM us_table "
                    f"WHERE sito=:sito AND {dim} IS NOT NULL "
                    f"AND TRIM({dim})<>'' AND node_uuid IS NOT NULL"
                ),
                {"sito": sito},
            ).fetchall()
            # Group by value
            buckets: dict = {}
            for value, node_uuid in rows:
                buckets.setdefault(str(value), []).append(node_uuid)
            node_class, kind_enum = _resolve_node_class_and_kind(dim)
            for name, member_uuids in buckets.items():
                # Deterministic UUID5 from (sito, dim, name)
                key = f"{sito}|{dim}|{name}"
                group_uuid = str(uuid.uuid5(
                    _PYARCHINIT_GROUP_NAMESPACE, key))
                out.append(GroupSpec(
                    group_uuid=group_uuid,
                    name=name,
                    group_kind=dim,
                    member_us_uuids=list(member_uuids),
                    node_class=node_class,
                    kind=kind_enum,
                ))
    return out
```

Also update the signature docstring. Find:

```python
def build_groups_from_sql(
    db_path: Path,
    sito: str,
    dimensions: List[str],
) -> List[GroupSpec]:
    """For each requested dimension, scan us_table for distinct
```

Replace with:

```python
def build_groups_from_sql(
    db_path,
    sito: str,
    dimensions: List[str],
) -> List[GroupSpec]:
    """For each requested dimension, scan us_table for distinct
    non-empty values within sito, and emit one GroupSpec per
    (dimension, value) pair.

    PG-B (5.7.1-alpha): ``db_path`` accepts ``Path | DbHandle | str``
    via the ``_resolve_db_handle`` shim from Foundation.

```

(Insert the PG-B note + keep the rest of the docstring as-is.)

- [ ] **Step 4: Run SQLite suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 12 skipped`.

- [ ] **Step 5: AC-2 sanity ping (CRITICAL)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

If AC-2 FAILS → STOP. Same diff investigation procedure as Group A Step 10.

- [ ] **Step 6: Commit Group B**

```bash
git add modules/s3dgraphy/sync/group_projector.py
git commit -m "$(cat <<'EOF'
refactor(pg-b/B): group_projector cross-backend via SQLAlchemy

2 sqlite3.connect() sites swapped:

1. dimensions_with_data(db_path, sito) - single engine.connect()
   wraps the 7-dimension probe loop
2. build_groups_from_sql(db_path, sito, dimensions) - single
   engine.connect() wraps the per-dimension scan

Both functions accept Path | DbHandle | str via the shim. The
{col}/{dim} f-string interpolation is preserved because the
identifiers come from the hardcoded _SQL_DIMENSIONS tuple (not
user input) - SQLAlchemy text() does not parameterize column names
and this is the standard pattern.

NO query content changes. AC-2 byte-identical preserved.
250 passed, 12 skipped (unchanged).
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group C — `graphml_writer.py` refactor (1 site + internal caller)

### Task C.1: Refactor `_read_first_sito` + update internal call to `populate_graph`

**File:** `modules/s3dgraphy/sync/graphml_writer.py`

- [ ] **Step 1: Add imports for shim**

Find the imports block at the top of the file. Look for the existing `import sqlite3` line. Add the shim imports near it:

```python
import sqlite3
```

After it (or near the other SQLAlchemy imports if any exist), add:

```python
from sqlalchemy import text

from ._db_handle import _resolve_db_handle
```

Verify with:

```bash
grep -n "from \._db_handle\|from sqlalchemy" modules/s3dgraphy/sync/graphml_writer.py | head -5
```

- [ ] **Step 2: Refactor `_read_first_sito` (~line 120-160)**

Find this exact block:

```python
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT sito FROM us_table "
                "WHERE sito IS NOT NULL AND sito <> '' "
                "ORDER BY sito LIMIT 1"
            ).fetchone()
        finally:
            conn.close()
    except sqlite3.Error as e:
        raise GraphMLExportError(
            "import",
            RuntimeError(f"Cannot read us_table.sito: {e}"),
        ) from e
```

Replace with:

```python
    try:
        handle = _resolve_db_handle(db_path)
        with handle.engine.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT sito FROM us_table "
                    "WHERE sito IS NOT NULL AND sito <> '' "
                    "ORDER BY sito LIMIT 1"
                )
            ).fetchone()
    except Exception as e:
        raise GraphMLExportError(
            "import",
            RuntimeError(f"Cannot read us_table.sito: {e}"),
        ) from e
```

NOTE: `_read_first_sito` is a module-level function. Its signature `_read_first_sito(db_path)` does NOT need to be updated (Path-only callers continue to work via shim).

- [ ] **Step 3: Update internal call to `populate_graph` (~line 1796-1808)**

The current code at line 1796-1808 reads:

```python
        from .graph_projector import GraphProjector
        sito_for_projection = site_filter or _read_first_sito(db_path)
        print(f"[ExportGraphML] populate_graph(sito={sito_for_projection!r}, "
              f"include_paradata=True) — AI05 fix b2af31f4")
        graph = GraphProjector().populate_graph(
            db_path,
            sito=sito_for_projection,
            include_paradata=True,
            strict_schema=False,
            groups=groups,                # NEW (AI06)
            primary_priority=primary_priority,   # NEW (AI07)
        )
```

This already passes `db_path` (which from PG-B onwards may be `Path | DbHandle | str` since `export_graphml`'s `db_path` keyword accepts the shim). `populate_graph` (refactored in Group A) accepts the same shim. So **NO CHANGE NEEDED** at line 1796-1808.

The shim chain is: caller passes Path → `export_graphml(db_path=Path)` → `_read_first_sito(db_path)` resolves internally → `GraphProjector().populate_graph(db_path)` resolves internally again. Each call site is independent. The single Path travels through 3 method boundaries, each resolves separately. This is fine for PG-B since each resolution is cheap (just `DbHandle.from_path(Path)`).

If you want to avoid 3x resolution, the optimization is to resolve once at the top of `export_graphml` and pass the resulting `DbHandle` down. But that's an optimization not a correctness fix. **Skip the optimization for PG-B** — premature.

- [ ] **Step 4: Verify `export_graphml` signature accepts shim**

The current signature of `export_graphml` is at ~line 1700-ish. Find it. Look for the parameter list:

```python
def export_graphml(
    *,
    db_path,  # currently: Path
    mapping,
    output_path,
    site_filter=None,
    ...
):
```

If the current signature has `db_path: Path` annotation, update to `db_path` (no annotation) or add a comment:

```python
def export_graphml(
    *,
    db_path,  # Path | DbHandle | str — resolved by _resolve_db_handle shim
    mapping,
    output_path,
    site_filter=None,
    ...
):
```

If the signature already has no type annotation, leave unchanged.

Update the docstring near the top of `export_graphml` to mention the shim:

```python
    """Export the s3dgraphy Graph of *db_path* to *output_path*.

    PG-B (5.7.1-alpha): ``db_path`` accepts ``Path | DbHandle | str``
    via the ``_resolve_db_handle`` shim from Foundation. Backward
    compat preserved for legacy callers passing a Path.
    ...
    """
```

(Insert the PG-B note after the first line of the existing docstring.)

- [ ] **Step 5: Verify no remaining `import sqlite3` if unused**

```bash
grep -n sqlite3 modules/s3dgraphy/sync/graphml_writer.py
```

If only `import sqlite3` remains (no `.connect`, no `.Error`), the import is dead. Remove via Edit. If other `sqlite3.X` usages remain (unlikely but possible — graphml_writer.py is 2039 LOC), leave the import.

- [ ] **Step 6: Run SQLite suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 12 skipped`.

- [ ] **Step 7: AC-2 sanity ping (CRITICAL)**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

If AC-2 FAILS → STOP. Same diff investigation procedure as Group A.

- [ ] **Step 8: Commit Group C**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py
git commit -m "$(cat <<'EOF'
refactor(pg-b/C): graphml_writer cross-backend via SQLAlchemy

1 sqlite3.connect() site swapped:

- _read_first_sito(db_path) - single engine.connect() reads the
  fallback sito name when caller passes no site_filter. Accepts
  Path | DbHandle | str via shim.

export_graphml(db_path=..., mapping=..., output_path=...) public
API accepts the shim transparently - the same db_path travels
through _read_first_sito + GraphProjector().populate_graph(), each
of which resolves the shim independently (acceptable: resolution
is cheap, optimization to single-resolve deferred).

NO query content changes. AC-2 byte-identical preserved.
250 passed, 12 skipped (unchanged).
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group D — `load_sqlite_into_pg` helper + `pg_with_volterra` fixture

### Task D.1: Add helper + fixture to `tests/sync/conftest_pg.py`

**File:** `tests/sync/conftest_pg.py`

- [ ] **Step 1: Read the current file state**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
cat tests/sync/conftest_pg.py
```

Confirm the existing exports: `PG_CONN_STR`, `_apply_pyarchinit_schema`, `pg_engine` (session), `clean_pg` (function).

- [ ] **Step 2: Append `load_sqlite_into_pg` helper + `pg_with_volterra` fixture**

APPEND (do not replace) the following content at the END of `tests/sync/conftest_pg.py`:

```python


# ---------------------------------------------------------------------------
# PG-B (5.7.1-alpha): load_sqlite_into_pg helper + pg_with_volterra fixture
#
# Used by the AC-2 cousin test (test_ai03_export_pg_structural.py) and by
# test_export_pg.py. Mirrors a SQLite fixture's schema + data into PG so
# end-to-end export tests can compare PG output against the SQLite baseline.
# ---------------------------------------------------------------------------
def _sqlite_type_to_pg(sqlite_type) -> str:
    """Map a SQLite column type to a PG-compatible declaration.

    pyarchinit uses only TEXT, INTEGER, REAL — trivially compatible with PG.
    Anything else falls back to TEXT for safety.
    """
    s = str(sqlite_type).upper()
    if "INT" in s:
        return "INTEGER"
    if "TEXT" in s or "CHAR" in s or "CLOB" in s:
        return "TEXT"
    if "REAL" in s or "FLOA" in s or "DOUB" in s:
        return "REAL"
    return "TEXT"


def load_sqlite_into_pg(sqlite_path, pg_engine, tables=None):
    """Mirror a SQLite fixture's schema + data into PG.

    For each user table in *sqlite_path*:
      1. Reflect columns via SQLAlchemy Inspector
      2. CREATE TABLE IF NOT EXISTS on PG with TEXT/INTEGER/REAL types
      3. TRUNCATE ... RESTART IDENTITY CASCADE
      4. INSERT every SQLite row via executemany

    Idempotent. Returns a dict {table: rows_loaded}.

    Args:
        sqlite_path: Path to the SQLite fixture file.
        pg_engine: SQLAlchemy Engine connected to PG.
        tables: Optional list of table names to limit the load.
                None (default) = all user tables (excludes sqlite_*).
    """
    from pathlib import Path
    from sqlalchemy import create_engine, inspect

    sqlite_engine = create_engine(f"sqlite:///{Path(sqlite_path)}")
    sqlite_inspector = inspect(sqlite_engine)
    all_tables = [
        t for t in sqlite_inspector.get_table_names()
        if not t.startswith("sqlite_")
    ]
    tables = list(tables) if tables else all_tables
    counts: dict = {}

    for table in tables:
        cols = sqlite_inspector.get_columns(table)
        if not cols:
            counts[table] = 0
            continue
        col_defs = ", ".join(
            f"{c['name']} {_sqlite_type_to_pg(c['type'])}"
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
            rows = src.execute(
                text(f"SELECT * FROM {table}")
            ).mappings().all()
        if rows:
            col_names = list(rows[0].keys())
            placeholders = ", ".join(f":{c}" for c in col_names)
            with pg_engine.begin() as conn:
                conn.execute(
                    text(
                        f"INSERT INTO {table} ({', '.join(col_names)}) "
                        f"VALUES ({placeholders})"
                    ),
                    [dict(r) for r in rows],
                )
        counts[table] = len(rows)

    sqlite_engine.dispose()
    return counts


@pytest.fixture
def pg_with_volterra(pg_engine):
    """PG seeded with the mini_volterra.sqlite fixture data.

    Used by tests that need a populated PG to compare against the
    SQLite baseline (AC-2 cousin, export_pg tests).
    """
    from pathlib import Path
    fixture = Path(__file__).parent / "fixtures" / "mini_volterra.sqlite"
    if not fixture.exists():
        pytest.skip(f"Fixture missing: {fixture}")
    load_sqlite_into_pg(fixture, pg_engine)
    yield pg_engine
```

- [ ] **Step 3: Verify the file imports cleanly**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
PYTHONPATH="$PWD" python -c "
import sys
sys.path.insert(0, 'tests/sync')
import conftest_pg
print('conftest_pg imports OK')
print('load_sqlite_into_pg:', conftest_pg.load_sqlite_into_pg)
print('pg_with_volterra:', conftest_pg.pg_with_volterra)
"
```

Expected: `conftest_pg imports OK` + the function and fixture references printed.

- [ ] **Step 4: Run full suite to confirm no regression**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 12 skipped` (unchanged — Group D adds fixture infrastructure but no tests use it yet).

- [ ] **Step 5: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 6: Commit Group D**

```bash
git add tests/sync/conftest_pg.py
git commit -m "$(cat <<'EOF'
test(pg-b/D): load_sqlite_into_pg helper + pg_with_volterra fixture

Add infrastructure for PG-B's end-to-end tests:

- _sqlite_type_to_pg: trivial type mapping (TEXT/INTEGER/REAL ->
  PG-compatible declarations). pyarchinit uses only these 3 SQLite
  types.
- load_sqlite_into_pg(sqlite_path, pg_engine, tables=None): reflects
  schema via SQLAlchemy Inspector, CREATE TABLE IF NOT EXISTS,
  TRUNCATE, executemany INSERT. Idempotent. Returns dict of row
  counts per table.
- pg_with_volterra fixture: seeds PG with mini_volterra.sqlite
  (the AC-2 baseline fixture). Skips cleanly if fixture missing.

Used by tests/sync/test_export_pg.py (Group E) and
tests/sync/test_ai03_export_pg_structural.py (Group F).

250 passed, 12 skipped (unchanged - Group D is fixture
infrastructure, no tests use it yet).
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group E — `test_export_pg.py` (5 PG L2 cases)

### Task E.1: Create `tests/sync/test_export_pg.py`

**File:** `tests/sync/test_export_pg.py`

- [ ] **Step 1: Write the file with 5 test cases**

Create with this content:

```python
# tests/sync/test_export_pg.py
"""PG-B: L2 PostgreSQL tests for the export pipeline.

Verifies that GraphProjector + GraphMLWriter + GroupProjector work
on PG when seeded with the same data as mini_volterra.sqlite.

Skipped cleanly when PG is unreachable at localhost:5433 or when
psycopg2 is not installed. Uses the pg_with_volterra fixture
from conftest_pg.py (Group D).
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def test_populate_graph_accepts_dbhandle_on_pg(pg_with_volterra):
    """GraphProjector.populate_graph(handle, sito) works on PG and
    returns a Graph with the same node count as on SQLite."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    projector = GraphProjector()
    graph = projector.populate_graph(
        handle,
        sito="Volterra",
        include_paradata=False,
        strict_schema=False,
    )
    assert graph is not None
    assert len(graph.nodes) > 0, "Graph has no nodes — projection failed"


def test_populate_graph_node_uuid_propagation_on_pg(pg_with_volterra):
    """Every StratigraphicNode-family node in the projected graph
    carries a non-None node_uuid attribute."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    graph = GraphProjector().populate_graph(
        handle, sito="Volterra", include_paradata=False,
        strict_schema=False,
    )
    strat_nodes = [
        n for n in graph.nodes
        if type(n).__name__.startswith("Stratigraphic")
        or type(n).__name__ == "USNode"
    ]
    if not strat_nodes:
        pytest.skip("mini_volterra has no stratigraphic units — "
                    "fixture-specific")
    for n in strat_nodes:
        attrs = getattr(n, "attributes", None) or {}
        nu = attrs.get("node_uuid")
        assert nu is not None, (
            f"Node {getattr(n, 'name', '?')} missing node_uuid attribute"
        )
        assert len(str(nu)) == 36, (
            f"node_uuid {nu!r} is not a 36-char UUID"
        )


def test_populate_graph_toponym_chain_on_pg(pg_with_volterra):
    """If mini_volterra has site_table populated with toponym fields,
    the projected graph contains LocationNodeGroup nodes with
    kind='toponym' + is_in_location edges from US nodes."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from sqlalchemy import text

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    # Verify the fixture has populated toponym data; skip otherwise
    with pg_with_volterra.connect() as conn:
        row = conn.execute(text(
            "SELECT nazione, regione, provincia, comune "
            "FROM site_table WHERE sito=:sito"
        ), {"sito": "Volterra"}).fetchone()
    if row is None or not any(v for v in row):
        pytest.skip("mini_volterra site_table not populated with "
                    "toponym fields — fixture-specific")

    graph = GraphProjector().populate_graph(
        handle, sito="Volterra", include_paradata=False,
        strict_schema=False,
    )
    toponym_nodes = [
        n for n in graph.nodes
        if type(n).__name__ == "LocationNodeGroup"
        and (getattr(n, "kind", None) == "toponym"
             or (getattr(n, "attributes", {}) or {}).get("kind") == "toponym")
    ]
    assert len(toponym_nodes) > 0, (
        "No LocationNodeGroup(kind='toponym') nodes emitted — "
        "_emit_toponym_chain may have failed on PG"
    )


def test_group_projector_dimensions_with_data_on_pg(pg_with_volterra):
    """dimensions_with_data(handle, sito) returns the same set of
    dimension names on PG as it would on SQLite."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.group_projector import dimensions_with_data

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    dims = dimensions_with_data(handle, "Volterra")
    # dims is a list of column names that have at least one non-empty
    # value. mini_volterra is expected to have at least area or
    # struttura populated.
    assert isinstance(dims, list)
    valid_dim_set = {"area", "struttura", "attivita", "settore",
                     "ambient", "saggio", "quad_par"}
    assert all(d in valid_dim_set for d in dims), (
        f"dimensions_with_data returned unexpected entries: {dims}"
    )


def test_export_graphml_writes_file_on_pg(pg_with_volterra, tmp_path):
    """End-to-end: export_graphml(db_path=handle, ...) produces a
    non-empty GraphML file on disk + ExportResult.node_count > 0."""
    from modules.s3dgraphy.sync._db_handle import DbHandle
    from modules.s3dgraphy.sync.graphml_writer import export_graphml

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    out = tmp_path / "out_pg.graphml"
    result = export_graphml(
        db_path=handle,
        mapping="pyarchinit_us_mapping",
        output_path=out,
        site_filter="Volterra",
    )
    assert out.exists(), "GraphML output file not created"
    assert out.stat().st_size > 0, "GraphML output file is empty"
    assert result.node_count > 0, "ExportResult.node_count is 0"
```

- [ ] **Step 2: Run the 5 cases**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_export_pg.py -v 2>&1 | tail -15
```

Expected (PG offline, in this dev env): ALL 5 SKIPPED with reason "PG not available at localhost:5433 (...)".

If PG is online: 5 PASSED.

- [ ] **Step 3: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected: `250 passed, 17 skipped` (PG offline; 12 + 5 new skips) OR `255 passed, 12 skipped` (PG online; 250 + 5 new passes).

- [ ] **Step 4: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit Group E**

```bash
git add tests/sync/test_export_pg.py
git commit -m "$(cat <<'EOF'
test(pg-b/E): 5 L2 PostgreSQL tests for the export pipeline

Five cases that pin the PG-B design:

1. test_populate_graph_accepts_dbhandle_on_pg - public API
   accepts DbHandle, projects a non-empty Graph
2. test_populate_graph_node_uuid_propagation_on_pg - every
   StratigraphicNode has node_uuid attribute (pins
   _propagate_node_uuid_and_us on PG)
3. test_populate_graph_toponym_chain_on_pg - if site_table is
   populated, LocationNodeGroup(kind='toponym') nodes are emitted
   (pins _emit_toponym_chain on PG)
4. test_group_projector_dimensions_with_data_on_pg - returns
   subset of the 7 valid dimensions (pins dimensions_with_data)
5. test_export_graphml_writes_file_on_pg - end-to-end:
   non-empty GraphML on disk + ExportResult.node_count > 0
   (pins _read_first_sito + the whole export pipeline)

The pg_with_volterra fixture (Group D) seeds PG with
mini_volterra.sqlite via load_sqlite_into_pg. All 5 tests skip
cleanly when PG offline at localhost:5433 or psycopg2 missing.

Tests #3 and #4 self-skip when the fixture doesn't have the
required data populated (toponym fields, grouping columns) -
defensive, mini_volterra schema may vary.

PG offline: 250 passed, 17 skipped.
PG online: 255 passed, 12 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group F — `test_ai03_export_pg_structural.py` (AC-2 cousin)

### Task F.1: Create the AC-2 cousin test

**File:** `tests/sync/test_ai03_export_pg_structural.py`

- [ ] **Step 1: Write the file**

Create with this content:

```python
# tests/sync/test_ai03_export_pg_structural.py
"""PG-B AC-2 cousin: PG export structural fingerprint == SQLite baseline.

This is THE gate for PG-B. If it passes, PG produces structurally
equivalent GraphML to SQLite for the mini_volterra fixture. If it
fails, PG-B has a regression in the export pipeline.

Reuses the _structure() helper from test_ai03_export_byte_identical.py
(the existing AC-2 test) to ensure both sides apply the SAME
fingerprint definition.

Skipped cleanly when PG offline / psycopg2 missing.
"""
from __future__ import annotations

import pytest

# Import fixtures explicitly - conftest_pg.py is not auto-discovered
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


def test_pg_export_structural_fingerprint_matches_sqlite_baseline(
        pg_with_volterra, tmp_path):
    """The PG export of mini_volterra produces the same structural
    fingerprint as the committed SQLite baseline GraphML.

    Uses _structure() from test_ai03_export_byte_identical.py so the
    fingerprint definition is identical to AC-2.
    """
    from tests.sync.test_ai03_export_byte_identical import (
        _structure, BASELINE,
    )
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    from modules.s3dgraphy.sync._db_handle import DbHandle

    handle = DbHandle.from_engine(pg_with_volterra,
                                   str(pg_with_volterra.url))
    out = tmp_path / "out_pg.graphml"
    result = export_graphml(
        db_path=handle,
        mapping="pyarchinit_us_mapping",
        output_path=out,
        site_filter="Volterra",
    )

    actual = _structure(out.read_text(encoding="utf-8"))
    baseline = _structure(BASELINE.read_text(encoding="utf-8"))

    assert actual == baseline, (
        f"PG export structural fingerprint != SQLite baseline.\n"
        f"  actual:   {actual!r}\n"
        f"  baseline: {baseline!r}\n\n"
        f"This is THE PG-B gate. If this fails, the export pipeline "
        f"has regressed on PG. Compare each key (node_count, "
        f"edge_count, labels, row_count, table_count) to find which "
        f"part of the pipeline diverged."
    )
    assert result.node_count > 0
```

- [ ] **Step 2: Run the test**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_pg_structural.py -v 2>&1 | tail -10
```

Expected:
- PG offline: 1 SKIPPED
- PG online + psycopg2: 1 PASSED. If PASS — PG produces equivalent GraphML to SQLite.
- PG online + psycopg2 + the test FAILS — STOP. The fingerprint diff is reported in the assertion message. Investigate which key differs (`node_count`, `edge_count`, `labels`, `row_count`, `table_count`).

- [ ] **Step 3: Full suite**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
```

Expected:
- PG offline: `250 passed, 18 skipped` (250 + 1 new skip)
- PG online: `256 passed, 12 skipped`

- [ ] **Step 4: AC-2 sanity ping**

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
```

Expected: PASS.

- [ ] **Step 5: Commit Group F**

```bash
git add tests/sync/test_ai03_export_pg_structural.py
git commit -m "$(cat <<'EOF'
test(pg-b/F): AC-2 cousin - PG export fingerprint == SQLite baseline

THE gate for PG-B. Single test:

- test_pg_export_structural_fingerprint_matches_sqlite_baseline
  - seeds PG with mini_volterra.sqlite (via pg_with_volterra)
  - runs export_graphml(db_path=handle, ...) end-to-end on PG
  - computes structural fingerprint via _structure() imported
    from the existing AC-2 test
  - asserts equality to the committed SQLite baseline
  - assertion message diffs the fingerprint keys for fast
    triage if it ever fails

Reuses _structure() and BASELINE from
test_ai03_export_byte_identical.py to guarantee the fingerprint
definition is identical to AC-2 itself.

Skipped cleanly when PG offline / psycopg2 missing.

PG offline: 250 passed, 18 skipped.
PG online: 256 passed, 12 skipped.
AC-2 byte-identical preserved.
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

---

## Group G — Docs + version 5.7.1-alpha

### Task G.1: Bump `metadata.txt`

**Files:** `metadata.txt`

- [ ] **Step 1: Bump version**

Use the Edit tool to change `version=5.7.0-alpha` → `version=5.7.1-alpha`.

- [ ] **Step 2: Verify**

```bash
grep "^version=" metadata.txt
```

Expected: `version=5.7.1-alpha`.

### Task G.2: Insert Phase 3 PG-B section to dev-log

**Files:** `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

- [ ] **Step 1: Locate the topmost Phase 3 section**

```bash
grep -n "^## Phase 3" docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md | head -3
```

The topmost is now `## Phase 3 — PG-A migration (5.7.0-alpha)`. We insert PG-B BEFORE it.

- [ ] **Step 2: Use Edit to insert the new section**

Find this exact text:

```
---

## Phase 3 — PG-A migration (5.7.0-alpha)
```

Replace with:

```
---

## Phase 3 — PG-B export pipeline (5.7.1-alpha)

**Tag:** `phase3-pgcompat-b-export-5.7.1-alpha`
**Date:** 2026-05-10
**Spec:** `docs/superpowers/specs/2026-05-10-pg-b-export-design.md`
**Plan:** `docs/superpowers/plans/2026-05-10-pg-b-export.md`

### What shipped

- GraphProjector + GraphMLWriter + GroupProjector work on both
  SQLite and PostgreSQL backends
- 11 sqlite3.connect() call sites swapped to SQLAlchemy
  engine.connect() / engine.begin(): 5 in graph_projector.py,
  2 in group_projector.py, 1 in graphml_writer.py (counted
  per-method site; total raw sqlite3 mentions higher due to
  nested except blocks)
- Public APIs `populate_graph(db_path, sito, ...)`,
  `export_graphml(db_path=..., ...)`, `dimensions_with_data(db_path, sito)`,
  `build_groups_from_sql(db_path, sito, dimensions)` all accept
  `Path | DbHandle | str` via Foundation's `_resolve_db_handle` shim
- NO SQL query content changes - only connection wrapping and
  placeholder syntax (`?` → `:name` via SQLAlchemy `text()`)
- All `except sqlite3.Error` → `except Exception` (broader, for
  SQLAlchemy + psycopg2 exceptions)
- `load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper
  in `conftest_pg.py` mirrors SQLite fixtures into PG via schema
  reflection. Reusable for PG-C/D.

### Tests

- 5 new L2 PG cases in `test_export_pg.py` (populate_graph,
  node_uuid propagation, toponym chain, dimensions_with_data,
  export_graphml end-to-end)
- 1 new AC-2 cousin in `test_ai03_export_pg_structural.py` -
  the PG-B gate, verifies PG export fingerprint == SQLite baseline
- All 6 skip cleanly when PG offline or psycopg2 missing
- Total: 250 passed, 18 skipped (PG offline) or 256 passed,
  12 skipped (PG online + psycopg2)
- AC-2 byte-identical structural fingerprint preserved throughout
  (sanity ping after every Group A/B/C commit)
- Round-trip CI fixture suite (PR #6 with Emanuel) stays green

### Known follow-ups (later milestones)

- **PG-C** (5.7.2-alpha): GraphIngestor.populate_list flips
  `db_path: Path` → `db_handle: DbHandle`; writes to PG with
  atomic transactions
- **PG-D** (5.7.3-alpha): ParadataStore + GroupStore workspace dir
  on PG (`pyarchinit_DB_folder/<conn_slug>/<sito>/` model)
- **Consolidation** (5.7.4-alpha): rename `db_path` → `db_input` on
  public APIs with proper deprecation cycle; remove any stale
  `import sqlite3` if all dialect-specific paths are gone

---

## Phase 3 — PG-A migration (5.7.0-alpha)
```

### Task G.3: Prepend bilingual CHANGELOG entry

**Files:** `dev_logs/CHANGELOG.md`

- [ ] **Step 1: Find the topmost entry**

```bash
grep -n "^## \[" dev_logs/CHANGELOG.md | head -3
```

The topmost is `## [5.7.0-alpha] - 2026-05-10`. We insert PG-B BEFORE it.

- [ ] **Step 2: Use Edit to insert the new section**

Find this exact text:

```
## [5.7.0-alpha] - 2026-05-10
```

Replace with:

```
## [5.7.1-alpha] - 2026-05-10

### Italiano

**PG-B — La pipeline di export ora funziona su PostgreSQL.**

Secondo milestone post-Foundation della Phase 3. Ribalta il secondo gruppo di caller di produzione (GraphProjector + GraphMLWriter + GroupProjector — il lato export del bridge s3dgraphy) sull'infrastruttura cross-backend. Tutti i 250 test SQLite di PG-A restano verdi via shim. Round-trip CI fixture suite (PR #6) intatta. AC-2 byte-identical preservato.

- **11 `sqlite3.connect()` siti swappati a SQLAlchemy**: 5 in `graph_projector.py` (`_verify_node_uuid_column`, `_propagate_node_uuid_and_us`, `_enrich_into`, `_merge_groups`, `_emit_toponym_chain`), 2 in `group_projector.py` (`dimensions_with_data`, `build_groups_from_sql`), 1 in `graphml_writer.py` (`_read_first_sito`).
- **Pattern uniforme**: ogni site usa `with handle.engine.connect() as conn:` (read-only) o `engine.begin()` (read+write). Tutte le query usano `text("... :name")` con named params. Tutti gli `except sqlite3.Error` → `except Exception`.
- **NESSUNA modifica al contenuto delle query SQL** — solo wrap della connessione e sintassi placeholder. Il rischio AC-2 è quindi minimo per design.
- **Public API senza breaking change**: `populate_graph(db_path, sito, ...)`, `export_graphml(db_path=..., ...)`, `dimensions_with_data(db_path, sito)`, `build_groups_from_sql(db_path, sito, dimensions)` mantengono il nome `db_path` ma accettano `Path | DbHandle | str` via shim Foundation. Esistenti call site (AC-2 test, PR #6, QGIS dialog) restano invariati.
- **`load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper** in `conftest_pg.py`: riflette lo schema SQLite via SQLAlchemy `Inspector`, esegue `CREATE TABLE IF NOT EXISTS` su PG, `TRUNCATE`, e `executemany INSERT`. Idempotente. Riusabile per PG-C/D.
- **6 nuovi test L2 PG**: 5 in `test_export_pg.py` + 1 AC-2 cousin in `test_ai03_export_pg_structural.py` (il gate del milestone: verifica che il fingerprint strutturale PG corrisponda alla baseline SQLite). Tutti skippano puliti quando PG offline o psycopg2 mancante.

Test count: 250 → 250 passed, 18 skipped (PG offline) o 256 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preservato dopo ogni Group A/B/C.

### English

**PG-B — Export pipeline now works on PostgreSQL.**

Second post-Foundation milestone of Phase 3. Flips the second batch of production callers (GraphProjector + GraphMLWriter + GroupProjector — the export side of the s3dgraphy bridge) onto the cross-backend infrastructure. All 250 PG-A SQLite tests stay green via shim. Round-trip CI fixture suite (PR #6) intact. AC-2 byte-identical preserved.

- **11 `sqlite3.connect()` sites swapped to SQLAlchemy**: 5 in `graph_projector.py` (`_verify_node_uuid_column`, `_propagate_node_uuid_and_us`, `_enrich_into`, `_merge_groups`, `_emit_toponym_chain`), 2 in `group_projector.py` (`dimensions_with_data`, `build_groups_from_sql`), 1 in `graphml_writer.py` (`_read_first_sito`).
- **Uniform pattern**: each site uses `with handle.engine.connect() as conn:` (read-only) or `engine.begin()` (read+write). All queries use `text("... :name")` named params. All `except sqlite3.Error` → `except Exception`.
- **NO SQL query content changes** — only connection wrapping + placeholder syntax. AC-2 risk minimized by design.
- **Public API zero-breaking-change**: `populate_graph(db_path, sito, ...)`, `export_graphml(db_path=..., ...)`, `dimensions_with_data(db_path, sito)`, `build_groups_from_sql(db_path, sito, dimensions)` keep the `db_path` keyword but accept `Path | DbHandle | str` via the Foundation shim. Existing call sites (AC-2 test, PR #6, QGIS dialog) unchanged.
- **`load_sqlite_into_pg(sqlite_path, pg_engine, tables=None)` helper** in `conftest_pg.py`: reflects SQLite schema via SQLAlchemy `Inspector`, emits `CREATE TABLE IF NOT EXISTS` on PG, `TRUNCATE`, and `executemany INSERT`. Idempotent. Reusable for PG-C/D.
- **6 new L2 PG tests**: 5 in `test_export_pg.py` + 1 AC-2 cousin in `test_ai03_export_pg_structural.py` (the milestone gate: verifies PG structural fingerprint matches SQLite baseline). All skip cleanly when PG offline or psycopg2 missing.

Test count: 250 → 250 passed, 18 skipped (PG offline) or 256 passed, 12 skipped (PG online + psycopg2). AC-2 byte-identical preserved after every Group A/B/C.

---

## [5.7.0-alpha] - 2026-05-10
```

### Task G.4: Final verification + commit

**Files:** none (verify + commit)

- [ ] **Step 1: Pre-commit verification**

```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
echo "=== Recent commits since spec ==="
git log --oneline 069d8c14..HEAD

echo "=== Cumulative Co-Authored-By count ==="
git log 069d8c14..HEAD --format=%B | grep -c Co-Authored-By

echo "=== Full sync+migrations suite ==="
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3

echo "=== AC-2 ==="
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3

echo "=== Version ==="
grep "^version=" metadata.txt
```

Expected:
- 6 commits since `069d8c14`: A, B, C, D, E, F
- Co-Authored-By count: `0`
- Test suite: `250 passed, 18 skipped` (PG offline) or `256 passed, 12 skipped` (PG online)
- AC-2: PASS
- Version: `5.7.1-alpha`

- [ ] **Step 2: Commit docs + version**

```bash
git add metadata.txt \
        docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md \
        dev_logs/CHANGELOG.md
git commit -m "$(cat <<'EOF'
release(pg-b/G): docs + version bump 5.7.1-alpha

PG-B milestone documentation: bilingual CHANGELOG entry,
dev-log Phase 3 PG-B section, version bump 5.7.0-alpha -> 5.7.1-alpha.

Cumulative deliverables (Groups A-G):
- graph_projector.py: 5 sqlite3 sites → SQLAlchemy
- group_projector.py: 2 sqlite3 sites → SQLAlchemy
- graphml_writer.py: 1 sqlite3 site → SQLAlchemy + signature shim
- conftest_pg.py: load_sqlite_into_pg helper + pg_with_volterra fixture
- 5 new L2 PG tests in test_export_pg.py
- 1 AC-2 cousin in test_ai03_export_pg_structural.py (the gate)

Test count: 250 -> 250 passed, 18 skipped (PG offline) or
250 -> 256 passed, 12 skipped (PG online with psycopg2).
AC-2 byte-identical baseline preserved throughout.

Spec: docs/superpowers/specs/2026-05-10-pg-b-export-design.md
Plan: docs/superpowers/plans/2026-05-10-pg-b-export.md
Predecessor: phase3-pgcompat-a-migration-5.7.0-alpha (45803d83)
EOF
)"
git log -1 --format=%B HEAD | grep -c Co-Authored-By
```

The grep MUST return `0`.

- [ ] **Step 3: Post-commit verification**

```bash
echo "=== Post-G verification ==="
git log --oneline 069d8c14..HEAD
git log 069d8c14..HEAD --format=%B | grep -c Co-Authored-By
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no 2>&1 | tail -3
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v 2>&1 | tail -3
grep "^version=" metadata.txt
```

Expected:
- 7 commits since `069d8c14`: A, B, C, D, E, F, G
- Co-Authored-By count: `0`
- `250 passed, 18 skipped` (PG offline)
- AC-2 PASS
- Version: `5.7.1-alpha`

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

- [ ] **Step 1: Tag**

```bash
git tag -a phase3-pgcompat-b-export-5.7.1-alpha -m "$(cat <<'EOF'
PG-B - Export pipeline on PostgreSQL

Second post-Foundation milestone of Phase 3 (PG-compat refactor).
GraphProjector + GraphMLWriter + GroupProjector now work on both
SQLite and PostgreSQL backends. NO changes to populate_list,
paradata_store, group_store - those are PG-C/D scope.

Cumulative deliverables (Groups A-G, 7 commits):

- graph_projector.py: 5 distinct sqlite3.connect() sites swapped to
  SQLAlchemy engine.connect() / engine.begin() via the
  _resolve_db_handle shim. Methods refactored: _verify_node_uuid_column,
  _propagate_node_uuid_and_us, _enrich_into, _merge_groups,
  _emit_toponym_chain.
- group_projector.py: 2 sqlite3.connect() sites swapped. Both
  dimensions_with_data and build_groups_from_sql accept DbHandle
  or legacy Path via shim.
- graphml_writer.py: 1 sqlite3.connect() site swapped (_read_first_sito).
  export_graphml(db_path=..., ...) public API accepts shim.
- conftest_pg.py: load_sqlite_into_pg helper + pg_with_volterra
  fixture. Reflects SQLite schema, mirrors data to PG. Reusable
  for PG-C/D.
- NO SQL query content changes - only connection wrapping and
  placeholder syntax (? -> :name via text()). All except
  sqlite3.Error -> except Exception.

Tests: 5 new PG L2 tests in test_export_pg.py + 1 AC-2 cousin in
test_ai03_export_pg_structural.py (the milestone gate). All skip
cleanly when PG offline / psycopg2 missing.

Test counts: 250 -> 250 passed, 18 skipped (PG offline) or
250 -> 256 passed, 12 skipped (PG online + psycopg2).
AC-2 byte-identical baseline preserved.

Spec: docs/superpowers/specs/2026-05-10-pg-b-export-design.md
Plan: docs/superpowers/plans/2026-05-10-pg-b-export.md
Predecessor: phase3-pgcompat-a-migration-5.7.0-alpha (45803d83)
EOF
)"
```

- [ ] **Step 2: Verify the tag**

```bash
echo "=== Tag created ==="
git tag -n5 phase3-pgcompat-b-export-5.7.1-alpha | head -10
echo "=== Tag points to HEAD ==="
git rev-parse phase3-pgcompat-b-export-5.7.1-alpha^{commit}
git rev-parse HEAD
echo "=== Above two SHAs must match ==="
echo "=== Tag is annotated ==="
git cat-file -t phase3-pgcompat-b-export-5.7.1-alpha
echo "=== Should print 'tag' (annotated), not 'commit' ==="
echo "=== Tag message has NO Co-Authored-By ==="
git tag -l --format='%(contents)' phase3-pgcompat-b-export-5.7.1-alpha | grep -c Co-Authored-By
```

The final grep MUST return `0`.

### Task H.3: Push tag + branch

- [ ] **Step 1: Push the tag**

```bash
git push origin phase3-pgcompat-b-export-5.7.1-alpha 2>&1 | tail -3
```

Expected: `* [new tag]         phase3-pgcompat-b-export-5.7.1-alpha -> phase3-pgcompat-b-export-5.7.1-alpha`.

- [ ] **Step 2: Push the branch**

```bash
git push origin Stratigraph_00001 2>&1 | tail -3
```

Expected: branch updated successfully (Dependabot warnings unrelated).

- [ ] **Step 3: Verify on origin**

```bash
git ls-remote --tags origin | grep "phase3-pgcompat-b-export-5.7.1-alpha"
git ls-remote --heads origin Stratigraph_00001
```

Expected:
- Tag listed (with `^{}` dereferenced commit line)
- Branch tip equals local HEAD

### Task H.4: Memory snapshot (controller, no subagent)

**Files:** `~/.claude/projects/.../memory/project_pg_compat_progress.md` + `MEMORY.md`

- [ ] **Step 1: Update progress memory**

Update the existing `project_pg_compat_progress.md`:
- Move PG-B from PENDING to SHIPPED with the 7 commit SHAs (A-G), tag SHA, test counts, lessons learned
- Update the milestone table (PG-B row → ✅ SHIPPED 2026-05-10)
- Update the "How to apply" section: branchpoint is now HEAD of PG-B (whichever commit G lands)

Update `MEMORY.md` index line for new CURRENT STATE: shift PG-A out of CURRENT and add PG-B as CURRENT STATE.

- [ ] **Step 2: Final report**

After Group H completes, report:

- **Status:** DONE
- 7 new commits since `069d8c14`
- Tag `phase3-pgcompat-b-export-5.7.1-alpha` pushed to origin
- Test count: 250 passed (PG offline) / 256 (PG online), AC-2 preserved
- Zero `Co-Authored-By: Claude` trailers
- Memory note updated

---

## Self-Review

This plan covers every PG-B spec requirement:

| Spec section | Plan task |
|---|---|
| §3.1 Q1=a (db_path kwarg accepts DbHandle) | Group A Step 8 (populate_graph), Group B Step 2 (dimensions_with_data) + Step 3 (build_groups_from_sql), Group C Step 4 (export_graphml) |
| §3.2 Q2=a (load_sqlite_into_pg helper) | Group D |
| §3.3 Approach 1 (per-file Groups) | Groups A-H decomposition |
| §3.4 SQLAlchemy 2.0-compliant | Every Group's commit message references the rule; the refactor uses only 2.0-compatible patterns |
| §4.1 Modified production files (3) | Groups A/B/C |
| §4.2 Modified test infrastructure (1) | Group D |
| §4.3 New test files (2) | Groups E/F |
| §4.4 Modified release-tracking files (3) | Group G |
| §4.5 NOT touched | Documented + verified by AC-2 sanity ping at every A/B/C |
| §5 SQL dialect compat (5 sub-sections) | Group A/B/C apply the patterns |
| §6 Data flow + error handling | Group A Step 10 (AC-2 diff procedure) |
| §7 Test strategy | Groups E/F |
| §8 Acceptance criteria (PG-B-AC-1..9) | Pinned by tests in Groups E/F |
| §9 Release plan | Groups G + H |

**Type consistency check:** `DbHandle`, `_resolve_db_handle`, `_columns_of`, `text`, `_sqlite_type_to_pg`, `load_sqlite_into_pg`, `pg_with_volterra`, `_structure`, `BASELINE` — all spelled and used consistently across Groups.

**No placeholders:** every step has either runnable code, exact commands, or specific file edits. No "TBD" / "TODO" / "Add appropriate error handling".

**Scope check:** Plan is focused on PG-B only. PG-C/D files are in §4.5 NOT touched and verified by AC-2 sanity pings.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-10-pg-b-export.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, two-stage review (spec compliance + code quality), fast iteration

**2. Inline Execution** — execute tasks in this session via `executing-plans`, batch with checkpoints

If **Subagent-Driven**, recommended batching:
- Group 0 (2 tasks) → no subagent — pure git
- Group A → 1 subagent (TDD-style refactor of 5 sites in graph_projector.py; biggest, ~150 LOC delta; AC-2 risk concentrated here)
- Group B → 1 subagent (group_projector.py 2 sites)
- Group C → 1 subagent (graphml_writer.py 1 site + caller path)
- Group D → 1 subagent (load_sqlite_into_pg helper + pg_with_volterra fixture)
- Group E → 1 subagent (5 PG L2 tests)
- Group F → 1 subagent (1 AC-2 cousin test)
- Group G → 1 subagent (docs + version + final verification)
- Group H → 1 subagent (tag + push, gate per user approval)
- Memory snapshot → no subagent (controller writes after H ships)

If **Inline Execution**, batch by Group with checkpoint after each.
