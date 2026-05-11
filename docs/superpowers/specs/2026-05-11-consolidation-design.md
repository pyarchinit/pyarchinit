# Consolidation 5.7.4-alpha — Phase 3 closure

> **Spec source of truth.** Brainstormed 2026-05-11 after PG-D
> (5.7.3-alpha) shipped. The final Phase 3 milestone. After Consolidation
> ships, Phase 3 is officially complete and Phase 4 (SyncEngine + REST
> API) can be brainstormed.

**Status:** Approved 2026-05-11
**Predecessor:** `phase3-pgcompat-d-paradata-5.7.3-alpha` (`b8d73058`)
**Target tag:** `phase3-pgcompat-consolidation-5.7.4-alpha`
**Parent spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.6

---

## 1. Goal

Close Phase 3 with the deferred UI override of the workspace dir
(deferred from PG-D Q1=b) + docs cleanup. Add a 3-tier fallback chain
in `_workspace.py` so the workspace root can be configured via env var
(highest priority), QSettings (UI override), or default
(`~/pyarchinit/pyarchinit_DB_folder`, current behaviour). UI section in
`pyarchinitConfigDialog.py` lets users override via QSettings.

**Consolidation is bounded.** No rename of `db_path → db_input` on
public APIs (deferred to 5.8.x or Phase 4 where API churn can ride
along with other changes). No parametrized tests (low ROI — PG-offline
envs already skip cleanly). Only the QSettings UI feature + docs +
small `_workspace.py` extension are in scope.

## 2. Background

Phase 3 (PostgreSQL compatibility for the s3dgraphy bridge) shipped
its 5 core milestones across May 10-11, 2026:

| Milestone | Tag | Scope |
|---|---|---|
| Foundation | `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`) | DbHandle + shim + helpers (machinery only) |
| PG-A | `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`) | Migration script + CLI + handler + verify_schema |
| PG-B | `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`) | Export pipeline (graph_projector + group_projector + graphml_writer) |
| PG-C | `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`) | Import pipeline (GraphIngestor.populate_list + _DryRunRollback) |
| PG-D | `phase3-pgcompat-d-paradata-5.7.3-alpha` (`b8d73058`) | Paradata + group workspace (_workspace.py + 2 stores) |

After PG-D, all 5 deferred items from individual milestone brainstorms
were targeted to Consolidation:

1. Rename `db_path → db_input` on public APIs with DeprecationWarning cycle
2. QSettings UI for workspace dir override (deferred from PG-D Q1=b)
3. Documentation cleanup
4. Promote parametrized tests for SQLite + PG consistency
5. Optional `_common.py` adopt `_conn_slug`

The Consolidation brainstorming (2026-05-11) settled on **minimal
scope: items (2) + (3) only**. Items (1) and (4) deferred — see §3.1.

## 3. Architectural decisions (from brainstorming 2026-05-11)

### 3.1 Q1 — Scope of Consolidation

**Decision:** Approach (2) — minimal scope. **(B) QSettings UI** for
workspace override + **(D) Docs pass**. Skip **(A) rename** and **(C)
parametrized tests**.

**Rationale:**
- **(A) Rename `db_path → db_input`**: cosmetic improvement. `db_path`
  keyword still works fine via shim. Renaming touches 5 public APIs and
  ~20 call sites for marginal benefit. **Deferred** to 5.8.x or
  Phase 4 where it can ride along with other API churn.
- **(B) QSettings UI**: only user-facing feature. PG-D Q1=b explicitly
  deferred this to Consolidation. **In scope**.
- **(C) Parametrized tests**: unclear risk/reward. PG offline envs
  already skip PG tests cleanly. Parametrizing existing SQLite tests
  would double the skip noise in CI. **Deferred** indefinitely.
- **(D) Docs pass**: low risk, high value. Includes Phase 3 closure
  summary in dev-log + CHANGELOG. **In scope**.

### 3.2 Q2 — Override layering strategy

**Decision:** Approach (b) — 3-tier fallback (env var > QSettings >
default).

**Rationale:** Layered config is the classic pattern (e.g., Git
config: env > config file > defaults). Each layer serves a use case:
- Env var (`PYARCHINIT_WORKSPACE_DIR`): CI/tests escape hatch,
  power-user "force override" during debugging, easy to test via
  pytest monkeypatch
- QSettings (`pyarchinit/paradata_workspace`): user-facing override
  via QGIS dialog, persists across sessions
- Default (`~/pyarchinit/pyarchinit_DB_folder/`): backward-compat with
  PG-D behaviour, zero migration for existing users

### 3.3 Approach — helper function + UI section

**Decision:** Approach 1 — `_workspace.py` gets a new
`_resolve_workspace_root() -> Path` helper that does the 3-tier
resolution. `_resolve_workspace_dir()` PG branch delegates to it
instead of hardcoding `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"`.
UI section in `pyarchinitConfigDialog.py` reads/writes the QSettings
value via QLineEdit + Browse + Reset buttons.

**Rationale:**
- `_workspace.py` has no Qt dependency (lazy import + fail-soft for
  non-Qt envs like pytest)
- UI is isolated and testable manually in QGIS
- The 3-tier resolution is testable via monkeypatch on env var (the
  QSettings layer is manually-verified)
- Pure additive change — no refactor of existing PG-D logic

### 3.4 Phase 3 closure

After Consolidation ships, Phase 3 is officially complete. The 6 tags
+ cumulative stats are documented in:
- `dev_logs/CHANGELOG.md` `[5.7.4-alpha]` section + closure prose
- `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` "Phase 3 —
  Consolidation" section + closing summary paragraph
- `~/.claude/projects/.../memory/project_pg_compat_progress.md` (memory
  snapshot)

## 4. File-by-file change plan

### 4.1 Modified files

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/_workspace.py` | Add `_resolve_workspace_root() -> Path` helper (3-tier fallback). Modify `_resolve_workspace_dir()` PG branch to delegate to `_resolve_workspace_root()` instead of hardcoding `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"`. SQLite branch UNCHANGED. QSettings import lazy + fail-soft (try/except ImportError). | ~40 |
| `gui/pyarchinitConfigDialog.py` | New section "Paradata Workspace" (find right insertion point in 10241-line dialog — probably near existing DB settings). QLabel + QLineEdit (workspace path) + Browse button (QFileDialog.getExistingDirectory) + Reset button. Read/write QSettings `pyarchinit/paradata_workspace`. On dialog open, populate QLineEdit from current QSettings value (empty = default fallback). | ~80 |
| `metadata.txt` | Bump `5.7.3-alpha` → `5.7.4-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.4-alpha]` section + add a "Phase 3 closure summary" prose paragraph below the version block. | ~60 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add "Phase 3 — Consolidation (5.7.4-alpha)" section + closing **"Phase 3 closure"** summary paragraph mentioning all 6 tags + zero residual `sqlite3.connect()` + Consolidation deferred items (rename + parametrized tests). | ~50 |

### 4.2 New files

| Path | Purpose | LOC |
|---|---|---|
| `tests/sync/test_workspace_root.py` | 4 L0 unit tests for `_resolve_workspace_root()` (env var precedence, default fallback, `.expanduser()` handling, empty env var). Pure pytest, no Qt. | ~80 |

### 4.3 Explicitly NOT touched

- Public API signatures (`populate_graph`, `populate_list`,
  `export_graphml`, `dimensions_with_data`, `build_groups_from_sql`,
  `ParadataStore.__init__`, `GroupStore.__init__`) — `db_path` keyword
  preserved. Rename deferred per Q1=(2).
- `paradata_store.py` and `group_store.py` — unchanged from PG-D
- `_db_handle.py` (Foundation)
- All SQL query content (already covered by PG-A/B/C/D)
- `scripts/migrations/_common.py:auto_backup_postgres` — optional
  `_conn_slug` adoption (deferred indefinitely)
- AC-2 + 3 critical SQLite regression gates + 8 PG-D L2 tests — must
  stay green untouched

### 4.4 Total LOC

- Production: ~120 modified
- Test: ~80 (1 new file, 4 L0 cases)
- Docs: ~110
- **Grand total: ~310 LOC** (smallest milestone in Phase 3, even
  smaller than PG-D)

## 5. `_workspace.py` extension specification

### 5.1 New helper

```python
def _resolve_workspace_root() -> Path:
    """Resolve the workspace root directory using 3-tier fallback.

    1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
    2. QSettings 'pyarchinit/paradata_workspace' (UI override)
    3. Default: ~/pyarchinit/pyarchinit_DB_folder

    Returns a Path (existence not guaranteed; caller must mkdir if needed).

    Phase 3 Consolidation (5.7.4-alpha): added to support the
    `pyarchinitConfigDialog.py` UI override deferred from PG-D Q1=b.
    """
    import os
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
```

### 5.2 Updated `_resolve_workspace_dir()` (PG branch only)

```python
def _resolve_workspace_dir(handle: DbHandle, sito: str) -> Path:
    if not handle.is_postgres:
        # SQLite branch UNCHANGED from PG-D
        if handle.sqlite_path is None:
            raise ValueError(
                "In-memory SQLite has no parent dir for workspace; "
                "ParadataStore / GroupStore require a file-backed DB"
            )
        return handle.sqlite_path.parent

    # PG branch: was hardcoded, now uses _resolve_workspace_root()
    slug = _conn_slug(handle)
    sito_safe = re.sub(r"[^a-zA-Z0-9_-]", "_", sito)
    workspace = _resolve_workspace_root() / slug / sito_safe
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace
```

### 5.3 Resolution semantics

| Env var | QSettings | Final root |
|---|---|---|
| unset / empty | unset / empty | `~/pyarchinit/pyarchinit_DB_folder/` (default) |
| unset | `/data/workspace` | `/data/workspace/` |
| `/tmp/test` | (any) | `/tmp/test/` (env var wins) |
| `~/custom` | unset | `/Users/<user>/custom/` (`~` expanded) |

## 6. UI specification (`pyarchinitConfigDialog.py`)

### 6.1 Section "Paradata Workspace"

A new QGroupBox containing:
- **QLabel "Workspace directory (PostgreSQL only)"**: explanatory text
  mentioning that this affects only PG paradata/group `.graphml`
  files. SQLite continues to store files alongside the `.sqlite`.
- **QLineEdit** populated from `QSettings().value("pyarchinit/paradata_workspace", "")`.
  Placeholder text shows the current default
  (`~/pyarchinit/pyarchinit_DB_folder/`).
- **Browse button**: opens `QFileDialog.getExistingDirectory()` → writes
  the chosen path into QLineEdit.
- **Reset button**: clears QLineEdit + calls
  `QSettings().remove("pyarchinit/paradata_workspace")` on dialog save.

### 6.2 Save logic

When the dialog's OK button is clicked:
- If QLineEdit is non-empty and whitespace-stripped, write to QSettings.
- If QLineEdit is empty, call `QSettings().remove("pyarchinit/paradata_workspace")`.

### 6.3 Hint label (optional, low priority)

Display the current effective workspace root (computed via
`_resolve_workspace_root()`) as a read-only hint below the QLineEdit:
"Effective root: <path>". Helps user verify the layering result.

### 6.4 UI placement

`pyarchinitConfigDialog.py` is 10241 lines with no existing QSettings
patterns. The implementer locates the right insertion point during
Group B — probably near existing "Database settings" or "Paths"
sections, otherwise creates a new QGroupBox at the end of the
configuration tabs.

## 7. Test strategy

### 7.1 Pyramid (Consolidation delta over PG-D)

| Level | File | New cases | Skip semantics |
|---|---|---|---|
| L0 unit (NEW) | `tests/sync/test_workspace_root.py` | 4 | No skip — pure pytest, no Qt |
| L1 SQLite | 250 existing tests | 0 modified | All stay green (SQLite branch unchanged) |
| L2 PG | 8 existing tests in test_paradata_store_pg.py + test_group_store_pg.py | 0 modified | Stay green/skip (PG path now uses `_resolve_workspace_root()` but with unset env/QSettings, default fallback is byte-identical to PG-D) |
| L3 regression guards | AC-2 + 3 critical SQLite gates | 0 modified | MUST stay green |

### 7.2 Four `test_workspace_root.py` cases

| # | Test name | What it pins |
|---|---|---|
| 1 | `test_default_when_env_and_qsettings_unset` | Without env var + QSettings unavailable (non-Qt env) → returns `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"`. Verifies default path. |
| 2 | `test_env_var_override_takes_precedence` | `monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "/tmp/custom")` → returns `Path("/tmp/custom")`. Verifies env var path handling. |
| 3 | `test_empty_env_var_falls_through_to_default` | `monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")` → returns default (empty env var treated as unset). |
| 4 | `test_env_var_with_tilde_expanded` | `monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace")` → returns `Path.home() / "test_workspace"`. Verifies `.expanduser()`. |

**QSettings layer NOT unit-tested** (would require Qt). Manual
verification in QGIS during Group B.

### 7.3 Decision-pinning matrix

| Decision | Test |
|---|---|
| Q1=(2) minimal scope (no rename, no parametrized) | NO rename tests, NO parametrize attribute on existing tests (verified by plan) |
| Q2=(b) 3-tier fallback | Tests #1, #2, #3, #4 |
| Approach 1 (helper + UI) | Tests #1-4 cover helper; UI manual verification |
| `_resolve_workspace_root()` deterministic | Each test asserts specific resolution |
| SQLite path preserved | Existing 3 critical SQLite regression gates stay green |
| PG-D 8 L2 tests preserved | They use `monkeypatch.setattr(Path, "home", ...)` — `_resolve_workspace_root()` default branch calls `Path.home()`, so monkeypatch still works |

### 7.4 Test count progression

- Pre Consolidation (post PG-D): `250 passed, 33 skipped` (PG offline)
- Post Group A (refactor + 4 new L0 tests): `254 passed, 33 skipped`
- Post Group B (UI only, no test): unchanged
- Post Group C (docs only): unchanged

Final:
- PG offline: **254 passed, 33 skipped**
- PG online + psycopg2: **262 passed, 12 skipped**

## 8. Acceptance criteria

| AC | Description |
|---|---|
| **AC-2** (existing) | Byte-identical structural fingerprint on `mini_volterra.sqlite` — preserved |
| **AC-15** (existing, AI07) | Toponym chain round-trip — unchanged |
| **PG-D-AC-1..10** (existing) | All PG-D criteria preserved |
| **CONSOL-AC-1** NEW | `_resolve_workspace_root()` returns env var path when `PYARCHINIT_WORKSPACE_DIR` is set (Test #2) |
| **CONSOL-AC-2** NEW | Falls through to default when env var unset/empty AND QSettings unavailable (Tests #1, #3) |
| **CONSOL-AC-3** NEW | Applies `.expanduser()` to env var values (Test #4) |
| **CONSOL-AC-4** NEW | `_resolve_workspace_dir()` PG branch uses `_resolve_workspace_root()` instead of hardcoded path |
| **CONSOL-AC-5** NEW | `_resolve_workspace_dir()` SQLite branch UNCHANGED |
| **CONSOL-AC-6** NEW | QSettings UI section reads/writes `pyarchinit/paradata_workspace` (manual verification in QGIS) |
| **CONSOL-AC-7** NEW | PG-D's 8 PG L2 tests continue to pass (monkeypatch on `Path.home()` still works) |
| **CONSOL-AC-8** NEW | All 250 SQLite tests stay green |
| **CONSOL-AC-9** NEW | 3 critical SQLite regression gates stay green |
| **CONSOL-AC-10** NEW | Zero `Co-Authored-By: Claude` trailers |
| **PHASE-3-AC** | Phase 3 officially complete: all 6 tags shipped (Foundation + PG-A + PG-B + PG-C + PG-D + Consolidation) |

## 9. Release plan

**Tag:** `phase3-pgcompat-consolidation-5.7.4-alpha`
**Predecessor:** `phase3-pgcompat-d-paradata-5.7.3-alpha` (`b8d73058`)
**Rollback safety tag:** `pre-consolidation-5.7.4` (created in Group 0)

### 9.1 Commit structure (~4 commits)

| Group | Type | Commit |
|---|---|---|
| 0 | git | Pre-flight + rollback tag |
| A | refactor | `_workspace.py` add `_resolve_workspace_root()` + update `_resolve_workspace_dir()` PG branch + NEW `tests/sync/test_workspace_root.py` with 4 L0 cases |
| B | feature | `gui/pyarchinitConfigDialog.py` new "Paradata Workspace" section (QLineEdit + Browse + Reset) |
| C | release | Bump 5.7.3-alpha → 5.7.4-alpha + bilingual CHANGELOG + dev-log "Phase 3 — Consolidation" section + Phase 3 closure summary |
| D | tag+push | Annotated tag + push |

### 9.2 Critical sanity ping after Group A

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_workspace_root.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py tests/sync/test_round_trip_with_groups.py tests/sync/test_graph_projector_paradata.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_paradata_store_pg.py tests/sync/test_group_store_pg.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

If anything fails → STOP. Main risk: the new layer breaks PG-D's
8 L2 tests if monkeypatch on `Path.home()` no longer reaches the
default path. Mitigated by `_resolve_workspace_root()` still calling
`Path.home()` in the default branch.

### 9.3 Subagent batching

- Group 0 → controller (no subagent)
- Group A → 1 subagent (helper + 4 L0 tests; ~120 LOC; sonnet OK)
- Group B → 1 subagent (Qt UI in 10K-line dialog; ~80 LOC; **explicit
  instruction: find right insertion point, don't refactor**)
- Group C → 1 subagent (docs + version + Phase 3 closure prose)
- Group D → 1 subagent (tag + push, gate per user approval)
- Memory snapshot → controller (Phase 3 closure)

### 9.4 Strict rules (inherited)

- Zero `Co-Authored-By: Claude` trailers
- AC-2 byte-identical guard green after Group A
- 3 critical SQLite regression gates green after Group A
- 8 PG-D L2 tests green after Group A (monkeypatch compatibility)
- All 250 pre-existing SQLite tests green at every Group
- HEREDOC commit messages
- No `git add -A` or `git add .`
- **NO rename `db_path → db_input`** (deferred per Q1=(2))
- **NO parametrized tests** (deferred per Q1=(2))
- Group B: find right insertion point in 10K-line dialog, don't
  refactor unrelated code (PG-B Group C lesson)

### 9.5 Memory snapshot post-ship

Update `project_pg_compat_progress.md`:
- Move Consolidation from PENDING to SHIPPED
- **Add "Phase 3 OFFICIALLY COMPLETE" section** with all 6 tags +
  cumulative stats (LOC, tests, commits, days)
- Document deferred items (rename + parametrized tests) for future
  Phase 4 brainstorming
- Annotate QSettings UI integration as the only user-facing change in
  Consolidation

Update `MEMORY.md` index for new "Phase 3 COMPLETE" CURRENT STATE.

### 9.6 Time estimate

Parent spec estimated ~1 week. Via subagent-driven-development: ~2h
execution + ~30min review + memory update. Faster than PG-D because
the helper refactor is surgical and the UI section is additive (no
existing code to refactor).

### 9.7 Phase 3 closure outlook

After Consolidation ships, Phase 3 is officially CLOSED:

- 6 tags: Foundation + PG-A + PG-B + PG-C + PG-D + Consolidation
- ~2500 LOC across all 6 milestones
- ~36+ commits across the whole phase
- 254 passed / 33 skipped (PG offline) / ~262 / 12 (PG online)
- AC-2 byte-identical preserved throughout
- Zero `Co-Authored-By: Claude` trailers across the entire phase
- All production `sqlite3.connect()` flipped to SQLAlchemy + DbHandle shim

**Phase 4** (SyncEngine + REST API for multi-user concurrency) can be
brainstormed when ready. Deferred items from Phase 3 (rename
`db_path → db_input` + parametrized tests + optional `_common.py` adopt
`_conn_slug`) can ride along with Phase 4 API changes.

## 10. References

- Parent spec: `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.6
- Foundation tag: `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
- PG-A tag: `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- PG-B tag: `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
- PG-C tag: `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`)
- PG-D tag: `phase3-pgcompat-d-paradata-5.7.3-alpha` (`b8d73058`)
- PG-D spec: `docs/superpowers/specs/2026-05-11-pg-d-paradata-design.md`
  (the Q1=b decision that deferred QSettings UI to here)
- AC-2 test: `tests/sync/test_ai03_export_byte_identical.py`
- 3 SQLite critical gates: `tests/sync/test_round_trip_with_paradata.py`,
  `test_round_trip_with_groups.py`, `test_graph_projector_paradata.py`
- 8 PG-D L2 tests: `tests/sync/test_paradata_store_pg.py`,
  `test_group_store_pg.py`
- Memory: `project_pg_compat_progress.md` — current state of Phase 3
- Memory: `feedback_no_claude_coauthor.md` — strict commit rule
