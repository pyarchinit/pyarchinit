# PG-D — ParadataStore + GroupStore workspace on PostgreSQL (5.7.3-alpha)

> **Spec source of truth.** Brainstormed 2026-05-11 after PG-C (5.7.2-alpha)
> shipped. This spec is the contract for the implementation plan that
> follows via `superpowers:writing-plans`.

**Status:** Approved 2026-05-11
**Predecessor:** `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`)
**Target tag:** `phase3-pgcompat-d-paradata-5.7.3-alpha`
**Parent spec:** `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.5

---

## 1. Goal

Make `ParadataStore` and `GroupStore` cross-backend for filesystem path
resolution. The single path-resolution site in each file
(`self._db_path.parent / f"<prefix>_<slug>.graphml"`) becomes a dispatch
via a new `modules/s3dgraphy/sync/_workspace.py` helper. On SQLite, the
path stays "alongside the .sqlite file" (legacy behaviour preserved
byte-identical). On PostgreSQL, the path lives in a per-connection /
per-site workspace dir: `~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/<prefix>_<sito>.graphml`.
Public constructor `Store(db_path, sito)` keeps the `db_path` keyword
name and accepts `Path | DbHandle | str` via `_resolve_db_handle()` shim
(PG-A/B/C pattern).

**PG-D is path-resolution-only.** Neither `paradata_store.py` nor
`group_store.py` contain SQL queries — they are filesystem-only helpers
that read/write `.graphml` files. The cross-backend concern is the
DIRECTORY of the file, not the contents.

**PG-D is bounded.** No QSettings UI override (deferred to
**Consolidation 5.7.4-alpha**), no auto-migration of existing
SQLite-side paradata files, no concurrency/locking. After PG-D ships,
zero residual `import sqlite3` in `modules/s3dgraphy/sync/` and Phase 3
is complete modulo Consolidation.

## 2. Background

`ParadataStore` and `GroupStore` are site-scoped CRUD helpers that
persist `.graphml` artefacts adjacent to a pyarchinit database. They
predate the cross-backend refactor and assumed a single deployment
model: SQLite file on disk, paradata `.graphml` next to it.

- `ParadataStore.file_path` (line 96): `return self._db_path.parent / f"paradata_{self._slug}.graphml"`
- `GroupStore.file_path` (line 84): `return self._db_path.parent / f"groups_{self._slug}.graphml"`

That single `.parent` access is the entire SQLite-only assumption.

The 15 known callers — 1 in `s3dgraphy_dot_bridge.py:543`, 2 in
`graph_projector.py:329,741`, 11 in `scripts/s3dgraphy_sync.py:131-179`,
and 6 in 3 test files — all pass a `Path`. With the PG-A/B/C shim
pattern, none of them change.

PG-A (5.7.0-alpha) flipped the migration script. PG-B (5.7.1-alpha)
flipped the export pipeline. PG-C (5.7.2-alpha) flipped the import
pipeline. PG-D flips the last filesystem boundary — and after it ships,
Phase 3's only remaining work is Consolidation 5.7.4-alpha (renames +
QSettings UI + final cleanup).

## 3. Architectural decisions (from brainstorming 2026-05-11)

### 3.1 Q1 — QSettings UI scope

**Decision:** Approach (b) — hardcoded default in PG-D, QSettings UI
override deferred to **Consolidation 5.7.4-alpha**.

**Rationale:** PG-D stays focused on the core path-resolution refactor
(2 small files + 1 new helper module). Consolidation 5.7.4-alpha already
plans to touch `gui/pyarchinitConfigDialog.py` for the
`db_path → db_input` rename deprecation cycle, so bundling the
"Paradata Workspace" QSettings section there is natural. Power users
who need a workspace override in PG-D can wait for Consolidation; the
hardcoded default (`~/pyarchinit/pyarchinit_DB_folder/`) matches the
PG-A `auto_backup_postgres` destination and is consistent across Phase
3 milestones.

### 3.2 Decomposition approach

**Decision:** Approach 1 — single workspace helper (~6 commits, A-E).

- A: NEW `_workspace.py` + `paradata_store.py` + `group_store.py`
  refactor + DRY-up `_conn_slug` in `scripts/migrations/_common.py`
- B: `test_paradata_store_pg.py` (3-4 PG L2 cases)
- C: `test_group_store_pg.py` (3-4 PG L2 cases)
- D: docs + version bump
- E: tag + push

**Rationale:** A single `_workspace.py` module is DRY and matches the
parent spec's §4.5 layout. Per-store helpers would duplicate the
SQLite/PG dispatch logic in two places, and in-store dispatch (skipping
the new module) would violate the parent spec's structure.

### 3.3 Public API signature strategy

**Decision:** Shim continuity (PG-A/B/C pattern). Keep the `db_path`
keyword name on `ParadataStore.__init__` and `GroupStore.__init__`,
accept `Path | DbHandle | str` via `_resolve_db_handle()`.

**Rationale:** Zero refactoring noise on the 15 known caller sites.
The rename of public APIs from `db_path` to `db_input` is deferred to
**Consolidation 5.7.4-alpha** which will do it across all Phase 3
public surfaces with a proper deprecation cycle.

### 3.4 `_conn_slug` DRY-up

**Decision:** Extract `_conn_slug(handle: DbHandle) -> str` into the
new `_workspace.py` as the single source of truth. PG-A's
`scripts/migrations/_common.py:auto_backup_postgres` updates to import
this function instead of inlining the slugify logic.

**Rationale:** Single source of truth for the conn-slug formula.
Cross-tree import (`scripts/` importing from `modules/s3dgraphy/sync/`)
is an accepted pattern in PG-A (see
`_2026_05_node_uuid_backfill_lib.py` which already imports
`_resolve_db_handle` cross-tree).

### 3.5 SQLite preservation

**Decision:** SQLite branch of `_resolve_workspace_dir` returns
`handle.sqlite_path.parent` (byte-identical to the current
`self._db_path.parent`). No behaviour change for SQLite users.

**Rationale:** Zero migration risk for existing SQLite installs. The 6
existing tests that exercise ParadataStore + GroupStore on SQLite
(test_round_trip_with_paradata, test_round_trip_with_groups,
test_graph_projector_paradata) must stay green without modification —
they are the critical regression gates for PG-D.

## 4. File-by-file change plan

### 4.1 New files

| Path | Purpose | LOC |
|---|---|---|
| `modules/s3dgraphy/sync/_workspace.py` | `_resolve_workspace_dir(handle, sito) -> Path` + `_conn_slug(handle) -> str`. SQLite branch: `handle.sqlite_path.parent`. PG branch: `Path.home() / "pyarchinit" / "pyarchinit_DB_folder" / _conn_slug(handle) / sito` with `mkdir(parents=True, exist_ok=True)`. Type-annotated, docstring-clean. | ~80 |

### 4.2 Modified production files

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/paradata_store.py` | `__init__(self, db_path, sito)`: keep keyword name, accept `Path \| DbHandle \| str` via `_resolve_db_handle()`. Store `self._handle = _resolve_db_handle(db_path)`. Property `file_path` (line 96): use `_resolve_workspace_dir(self._handle, self._sito) / f"paradata_{self._slug}.graphml"`. | ~30 |
| `modules/s3dgraphy/sync/group_store.py` | Same pattern. Property `file_path` (line 84): use `_resolve_workspace_dir(self._handle, self._sito) / f"groups_{self._slug}.graphml"`. | ~30 |
| `scripts/migrations/_common.py` | `auto_backup_postgres`: replace the inline slugify(host_port_dbname) with `from modules.s3dgraphy.sync._workspace import _conn_slug` + `_conn_slug(handle)`. Mantiene single source of truth. | ~5 (net delta) |

### 4.3 New test files

| Path | Purpose | LOC |
|---|---|---|
| `tests/sync/test_paradata_store_pg.py` | 3-4 PG L2 cases: workspace_dir resolution, write+read round-trip, conn_slug determinism, multi-site isolation. Skip cleanly when PG offline. | ~80 |
| `tests/sync/test_group_store_pg.py` | 3-4 PG L2 cases: workspace_dir resolution, write+read round-trip, conn_slug determinism, shares workspace dir with paradata. Skip cleanly when PG offline. | ~80 |

### 4.4 Modified release-tracking files

| Path | Change | LOC delta |
|---|---|---|
| `metadata.txt` | Bump `5.7.2-alpha` → `5.7.3-alpha`. | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.7.3-alpha]` section. | ~40 |
| `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md` | Add Phase 3 PG-D section. | ~30 |

### 4.5 Files explicitly NOT touched

- `gui/pyarchinitConfigDialog.py` (QSettings UI deferred to Consolidation 5.7.4 per Q1=b)
- `modules/s3dgraphy/sync/_db_handle.py` (Foundation — no changes)
- `modules/s3dgraphy/sync/conflict_resolver.py`, `graph_projector.py`,
  `group_projector.py`, `graphml_writer.py`, `graph_ingestor.py` (all
  PG-A/B/C scope — already refactored)
- `tests/sync/test_ai03_export_byte_identical.py` (AC-2 — must stay green untouched)
- `tests/sync/test_round_trip.py`, `test_round_trip_with_paradata.py`,
  `test_round_trip_with_groups.py`, `test_graph_projector_paradata.py`
  (existing SQLite tests — must stay green via shim, the critical
  regression gates for PG-D)
- The 15 callers of ParadataStore / GroupStore (6 in bridge + graph_projector,
  11 in scripts + tests) — all unchanged via shim

### 4.6 Total LOC

- Production code: ~145 modified/new
- Test code: ~160 (2 new files)
- Docs: ~70
- **Grand total: ~375 LOC** (smaller than PG-A/B/C as expected — no SQL refactor, no transactions, no `_DryRunRollback` complexity)

## 5. `_workspace.py` helper specification

```python
"""PG-D Workspace path resolution for ParadataStore + GroupStore.

For SQLite: workspace = parent dir of the .sqlite file (legacy behaviour).
For PostgreSQL: workspace = ~/pyarchinit/pyarchinit_DB_folder/<conn_slug>/<sito>/

Created on-demand via mkdir(parents=True, exist_ok=True).

_conn_slug() is the single source of truth for the PG connection slug
used as a filesystem-safe directory name. PG-A's auto_backup_postgres
also imports from here (DRY-up).
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
    # Sanitize sito for directory use (slugify same as conn_slug pattern)
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

## 6. Data flow

### 6.1 SQLite path (preserved byte-identical)

```
ParadataStore(db_path=Path("/data/pyarchinit.sqlite"), sito="Volterra")
  → handle = _resolve_db_handle(Path) → DbHandle(is_postgres=False,
                                                  sqlite_path=Path("/data/pyarchinit.sqlite"))
  → file_path property:
      → _resolve_workspace_dir(handle, "Volterra") → Path("/data/")
      → return Path("/data/paradata_Volterra.graphml")
```

Identico al comportamento pre-PG-D. No mkdir (parent already exists).

### 6.2 PostgreSQL path (new)

```
ParadataStore(db_path="postgresql+psycopg2://postgres:postgres@localhost:5433/pyarchinit_test_pg",
              sito="Volterra")
  → handle = _resolve_db_handle(str) → DbHandle(is_postgres=True, conn_str=...)
  → file_path property:
      → _resolve_workspace_dir(handle, "Volterra"):
          → conn_slug = "localhost_5433_pyarchinit_test_pg"
          → workspace = Path.home() / "pyarchinit/pyarchinit_DB_folder" /
                        "localhost_5433_pyarchinit_test_pg" / "Volterra"
          → workspace.mkdir(parents=True, exist_ok=True)
          → return workspace
      → return workspace / "paradata_Volterra.graphml"
```

### 6.3 `_conn_slug(handle)` examples

| URL | Conn slug |
|---|---|
| `postgresql+psycopg2://user:pass@localhost:5433/pyarchinit_test_pg` | `localhost_5433_pyarchinit_test_pg` |
| `postgresql://user@db.example.com:5432/prod` | `db_example_com_5432_prod` |
| `postgresql://user@192.168.1.10/test` | `192_168_1_10_5432_test` (port defaults to 5432) |
| `postgresql://user@localhost/db with space` | `localhost_5432_db_with_space` (spaces → `_`) |

### 6.4 Error scenarios

| Trigger | Behavior |
|---|---|
| `db_path` passed as legacy `Path` | Shim resolves with `DeprecationWarning`. SQLite path identical to pre-PG-D behaviour. |
| PG `DbHandle` with malformed URL (host=None) | `_conn_slug` defaults to `"unknown_host_unknown_db"`-ish slug. Workspace dir still created. Defensive. |
| Workspace dir not writable (permission, disk full) | `Path.mkdir()` raises `OSError` → propagates to caller. Same behaviour as a write-failure to SQLite path today. |
| Sito name contains filesystem-unsafe chars (`/`, `\`, ...) | Sanitized via the same regex as `_conn_slug`. Filename retains the original `self._slug` (already site-slugified by the store's existing code). |
| SQLite `handle.sqlite_path is None` (e.g., `:memory:`) | `_resolve_workspace_dir` raises `ValueError("In-memory SQLite has no parent dir for workspace")`. Documented. |
| Conn-slug collision (same host+port+db, different hosts) | By design: `~/pyarchinit/...` is already per-user. Cross-machine collisions only when both machines target the SAME PG server with the SAME database — which IS the desired behaviour (one PG db = one logical workspace, shareable via NFS if user wants). |

### 6.5 Migration considerations

**SQLite users**: zero impact. `handle.sqlite_path.parent` produces the
same path as `_db_path.parent` does today. All existing
`paradata_<sito>.graphml` and `groups_<sito>.graphml` files adjacent to
`.sqlite` files remain accessible.

**Fresh PG users**: greenfield. Workspace dir created on first
ParadataStore/GroupStore write.

**Mixed users** (SQLite + then switch to PG): existing SQLite-side
paradata file stays in its original location and is NOT auto-migrated
to the new PG workspace. Documented in CHANGELOG. User can manually
copy if desired.

### 6.6 Concurrency — out of scope

Same as PG-A/B/C: no file locking, no advisory locking. Phase 4
SyncEngine concern.

## 7. Test strategy

### 7.1 Test pyramid

| Level | File | New cases | Skip semantics |
|---|---|---|---|
| L0 unit | none new | 0 | — |
| L1 SQLite | existing tests (especially `test_round_trip_with_paradata.py`, `test_round_trip_with_groups.py`, `test_graph_projector_paradata.py`) | 0 added, all stay green via shim | — |
| L2 PG | `tests/sync/test_paradata_store_pg.py` (NEW) | 3-4 | `pg_engine` fixture skips when PG offline / psycopg2 missing |
| L2 PG | `tests/sync/test_group_store_pg.py` (NEW) | 3-4 | Same |
| L3 regression guards | AC-2 + SQLite round-trip suite | 0 added, MUST stay green | — |

### 7.2 Four `test_paradata_store_pg.py` cases

| # | Test name | What it pins |
|---|---|---|
| 1 | `test_paradata_store_workspace_dir_on_pg` | `ParadataStore(handle, sito).file_path` resolves to `<workspace>/<conn_slug>/<sito>/paradata_<sito>.graphml` on PG. Directory created via `mkdir(parents=True, exist_ok=True)`. |
| 2 | `test_paradata_store_write_read_roundtrip_on_pg` | Construct paradata Graph, `store.write(graph)`, `store.read()` returns the same. Exercises atomic write (`.tmp` → rename) on PG-side filesystem. |
| 3 | `test_paradata_store_conn_slug_deterministic_on_pg` | Two ParadataStores with the same DbHandle URL produce the same `file_path`. `_conn_slug` is deterministic. |
| 4 | `test_paradata_store_multiple_sites_isolated_on_pg` | Two sites on the same PG → two separate subdirs under the same `<conn_slug>` dir. |

### 7.3 Four `test_group_store_pg.py` cases

| # | Test name | What it pins |
|---|---|---|
| 1 | `test_group_store_workspace_dir_on_pg` | Same as paradata #1 but for GroupStore. |
| 2 | `test_group_store_write_read_roundtrip_on_pg` | Add ad-hoc groups, write+read. |
| 3 | `test_group_store_conn_slug_deterministic_on_pg` | Same as paradata #3 but for GroupStore. |
| 4 | `test_group_store_uses_same_workspace_as_paradata_on_pg` | ParadataStore + GroupStore with the same `(handle, sito)` produce file paths in the SAME `<conn_slug>/<sito>/` dir. Verifies DRY of `_resolve_workspace_dir`. |

### 7.4 Decision-pinning matrix

| Decision | Test |
|---|---|
| Q1=b (QSettings UI deferred) | Manual — not automatable (UI deferred) |
| Approach 1 (single workspace helper) | Test #4 in `test_group_store_pg.py` (shared workspace verified) |
| Shim continuity (db_path kwarg accepts Path/DbHandle/str) | Test #1 + existing SQLite tests (Path callers via shim) |
| SQLite preservation | Existing `test_round_trip_with_paradata.py` + `test_round_trip_with_groups.py` — must stay PASS untouched |
| PG workspace dir path formula | Test #1 (both files) |
| `_conn_slug` deterministic | Test #3 (both files) |
| AC-2 export-side preservation | AC-2 existing (untouched) |

### 7.5 Test count progression

- Pre PG-D (post PG-C): `250 passed, 25 skipped` (PG offline)
- Post Group A (refactor only, no new tests): unchanged
- Post Group B (test_paradata_store_pg.py 4 cases, PG offline all skip): `250 passed, 29 skipped`
- Post Group C (test_group_store_pg.py 4 cases, PG offline all skip): `250 passed, 33 skipped`
- Post Group D (docs only): unchanged

Final:
- PG offline: **250 passed, 33 skipped**
- PG online + psycopg2: **258 passed, 12 skipped**

## 8. Acceptance criteria

| AC | Description |
|---|---|
| **AC-2** (existing) | Byte-identical structural fingerprint on `mini_volterra.sqlite` — preserved (PG-D doesn't touch export) |
| **AC-15** (existing, AI07) | Toponym chain round-trip — unchanged |
| **PG-D-AC-1** NEW | `ParadataStore(handle, sito).file_path` points to `<workspace>/<conn_slug>/<sito>/paradata_<sito>.graphml` on PG |
| **PG-D-AC-2** NEW | `GroupStore(handle, sito).file_path` points to `<workspace>/<conn_slug>/<sito>/groups_<sito>.graphml` on PG |
| **PG-D-AC-3** NEW | Write+read round-trip works on PG for ParadataStore |
| **PG-D-AC-4** NEW | Write+read round-trip works on PG for GroupStore |
| **PG-D-AC-5** NEW | `_conn_slug(handle)` is deterministic for identical URLs |
| **PG-D-AC-6** NEW | ParadataStore + GroupStore share the same `<conn_slug>/<sito>/` dir on PG |
| **PG-D-AC-7** NEW | SQLite path remains byte-identical to PG-C behaviour (verified by passing existing SQLite tests via shim) |
| **PG-D-AC-8** NEW | All 250 existing SQLite tests stay green via shim |
| **PG-D-AC-9** NEW | `test_round_trip_with_paradata.py` + `test_round_trip_with_groups.py` + `test_graph_projector_paradata.py` stay green — the critical PG-D regression gates |
| **PG-D-AC-10** NEW | Zero `Co-Authored-By: Claude` trailers |

## 9. Release plan

**Tag:** `phase3-pgcompat-d-paradata-5.7.3-alpha`
**Predecessor:** `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`)
**Rollback safety tag:** `pre-pg-d-paradata` (created in Group 0)

### 9.1 Commit structure (~6 commits)

| Group | Type | Commit |
|---|---|---|
| 0 | git | Pre-flight + rollback tag |
| A | refactor | NEW `_workspace.py` + `paradata_store.py` + `group_store.py` refactor + `_conn_slug` DRY-up in `scripts/migrations/_common.py` |
| B | feature | `tests/sync/test_paradata_store_pg.py` (3-4 PG L2 cases) |
| C | feature | `tests/sync/test_group_store_pg.py` (3-4 PG L2 cases) |
| D | release | Bump 5.7.2-alpha → 5.7.3-alpha + bilingual CHANGELOG + dev-log Phase 3 PG-D section |
| E | tag+push | Annotated tag + push |

### 9.2 Critical sanity ping after Group A

Group A is the only Group touching production code. After commit:

```bash
PYTHONPATH="$PWD" python -m pytest tests/sync/test_ai03_export_byte_identical.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_paradata.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_round_trip_with_groups.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/test_graph_projector_paradata.py -v
PYTHONPATH="$PWD" python -m pytest tests/sync/ tests/migrations/ -q --tb=no
```

If anything fails → STOP. The main risk: `_resolve_workspace_dir`
SQLite branch produces a different path than `_db_path.parent`. The 3
gate tests (round_trip_with_paradata, round_trip_with_groups,
graph_projector_paradata) exercise ParadataStore/GroupStore end-to-end
on SQLite — they are the critical regression gates for PG-D.

### 9.3 Subagent batching for `subagent-driven-development`

- Group 0 → controller (no subagent)
- Group A → 1 subagent (NEW `_workspace.py` + 2 store refactors + `_common.py` DRY-up; ~145 LOC; sonnet OK with explicit "NO behaviour changes for SQLite" instruction)
- Group B → 1 subagent (3-4 PG L2 paradata tests)
- Group C → 1 subagent (3-4 PG L2 group_store tests)
- Group D → 1 subagent (docs + version)
- Group E → 1 subagent (tag + push, gate for user approval)
- Memory snapshot → controller (no subagent) after E ships

### 9.4 Strict rules (inherited from Foundation + PG-A/B/C)

- Zero `Co-Authored-By: Claude` trailers
- AC-2 byte-identical guard green after Group A (export-side regression check)
- **`test_round_trip_with_paradata.py` + `test_round_trip_with_groups.py` + `test_graph_projector_paradata.py` SQLite stay green after Group A** (critical PG-D regression gates)
- All 250 pre-existing SQLite tests green at every Group
- HEREDOC commit messages
- No `git add -A` or `git add .`
- **SQLite path remains byte-identical** to PG-C behaviour
- **NO QSettings UI / `pyarchinitConfigDialog.py` changes** — deferred to Consolidation 5.7.4

### 9.5 Memory snapshot post-ship

Update `~/.claude/projects/.../memory/project_pg_compat_progress.md`:
- Move PG-D from PENDING to SHIPPED
- Annotate lessons learned (especially any cross-tree import quirks
  for `_conn_slug` DRY-up, or PG filesystem path creation surprises)
- **Add note**: Phase 3 is now complete modulo Consolidation 5.7.4
  (rename `db_path` → `db_input` + QSettings UI override + deprecation
  cleanup)

Update `MEMORY.md` index line for new CURRENT STATE.

### 9.6 Time estimate

Parent spec estimated ~1 week for PG-D (medium scope). Via
subagent-driven-development: ~2-3h execution + ~1h review + memory
update. Faster than PG-A/B/C because there's no SQL refactor, no
transaction handling, no `_DryRunRollback` complexity. End-to-end from
spec approval to tag pushed: 1 session.

### 9.7 Phase 3 completion outlook

After PG-D ships, the only Phase 3 milestone remaining is:

**Consolidation 5.7.4-alpha**:
- Rename `db_path` → `db_input` on all public APIs (`populate_list`,
  `populate_graph`, `export_graphml`, `dimensions_with_data`,
  `build_groups_from_sql`, `add_columns`, `backfill_uuids`,
  `ParadataStore.__init__`, `GroupStore.__init__`) with
  `DeprecationWarning` cycle
- QSettings UI "Paradata Workspace" override in
  `gui/pyarchinitConfigDialog.py`
- Remove any residual `import sqlite3` if completely unused
- Documentation cleanup
- Promote parametrized tests where it makes sense

Phase 3 officially complete with Consolidation. Phase 4 (SyncEngine +
REST API for multi-user concurrency) is future scope.

## 10. References

- Foundation spec: `docs/superpowers/specs/2026-05-10-postgres-compat-design.md` §4.5
- Foundation tag: `phase3-pgcompat-shim-5.6.2-alpha` (`7420a6cc`)
- PG-A spec: `docs/superpowers/specs/2026-05-10-pg-a-migration-design.md`
- PG-A tag: `phase3-pgcompat-a-migration-5.7.0-alpha` (`45803d83`)
- PG-B spec: `docs/superpowers/specs/2026-05-10-pg-b-export-design.md`
- PG-B tag: `phase3-pgcompat-b-export-5.7.1-alpha` (`2121369e`)
- PG-C spec: `docs/superpowers/specs/2026-05-11-pg-c-import-design.md`
- PG-C tag: `phase3-pgcompat-c-import-5.7.2-alpha` (`cf6ed26e`)
- AC-2 test: `tests/sync/test_ai03_export_byte_identical.py`
- SQLite regression gates: `tests/sync/test_round_trip_with_paradata.py`, `test_round_trip_with_groups.py`, `test_graph_projector_paradata.py`
- Memory: `project_pg_compat_progress.md` — current state of Phase 3
- Memory: `feedback_no_claude_coauthor.md` — strict commit rule
