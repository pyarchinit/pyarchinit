# Design — Centralized data-home resolution + rename to `pyarchinit_5`

**Date:** 2026-06-27
**Branch:** `Stratigraph_00001` (the "pyArchInit 5" line)
**Status:** Approved (design); pending implementation plan

## Problem

The branch and the legacy `master` plugin both write their runtime data to the
same home directory `~/pyarchinit/` (config.cfg, SQLite DBs, exports, backups,
paradata, and the heavy `bin/` AI tooling). A user who installs the branch and
later reinstalls `master` finds the shared home already mutated by the branch.

Goal: the branch must use a **separate** data home (`~/pyarchinit_5/`) so that
`master` keeps `~/pyarchinit/` intact (old DBs usable). The **plugin folder**
stays named `pyarchinit` — only the *data* home changes.

### Why it is not a one-line change

The home name is currently defined in **two** independent places and bypassed by
~40 hardcoded literals:

| Kind | Location | Notes |
|---|---|---|
| Source #1 | `__init__.py:49` `PYARCHINIT_HOME = expanduser("~") + os.sep + 'pyarchinit'` | sets `os.environ['PYARCHINIT_HOME']`; drives config.cfg path |
| Source #2 | `modules/utility/pyarchinit_folder_installation.py:28-30` | `self.HOME`; physically **creates** the ~14 subfolders; also overwrites the env var |
| Source #3 (minor) | `modules/utility/textTosql.py:251` | `os.path.join(HOME, "pyarchinit")` |
| Bypass literals (~40) | see §4 | `~/pyarchinit/bin/...` family (~30) + `Path.home()/"pyarchinit"/...` backups + paradata defaults + env-aware fallbacks |

## Decisions (confirmed with user)

1. **Resolution:** env var `PYARCHINIT_HOME` if set, else default `~/pyarchinit_5`.
2. **`bin/`:** fully isolated in `~/pyarchinit_5/bin` (no sharing with legacy).
3. **First run:** if the new home is absent but `~/pyarchinit` exists, a dialog
   offers to copy `pyarchinit_DB_folder` (config.cfg + SQLite DBs). `bin/` is
   **not** auto-copied (heavy venvs/models); the dialog states it must be
   reinstalled or copied manually.
4. **Migration scripts** wired to the QGIS menu are aligned to the resolver
   (default `pyarchinit_5`).

## Architecture: single source of truth

New module **`modules/utility/pyarchinit_home.py`** (dependency-free, `os` only):

```python
DEFAULT_HOME_NAME = "pyarchinit_5"

def pyarchinit_home() -> str:
    """Resolved data-home base. Env var PYARCHINIT_HOME wins; else default."""
    env = os.environ.get("PYARCHINIT_HOME")
    return env if env else os.path.join(os.path.expanduser("~"), DEFAULT_HOME_NAME)

def pyarchinit_home_bin() -> str:        # ~/pyarchinit_5/bin
    return os.path.join(pyarchinit_home(), "bin")

def legacy_pyarchinit_home() -> str:     # ~/pyarchinit  (migration only)
    return os.path.join(os.path.expanduser("~"), "pyarchinit")
```

Rule: an **empty** `PYARCHINIT_HOME` counts as unset → default (matches the
existing `modules/s3dgraphy/sync/_workspace.py` "empty values skipped" pattern).

### Derivation chain

- `__init__.py:49` computes with the same env-or-default(`pyarchinit_5`) logic and
  **immediately** sets `os.environ['PYARCHINIT_HOME']`. It is the earliest
  authority (runs at import). Inside QGIS every later `pyarchinit_home()` call
  reads an already-fixed env var → consistent.
- `pyarchinit_folder_installation.py` stops hardcoding/overwriting and uses the
  resolver. Its ~14 subfolders already derive from `self.HOME`, so they follow.
- Standalone scripts (run outside QGIS, where `__init__.py` never executes) get
  the default `pyarchinit_5` directly from the resolver.

## §4 — Literal replacement scope

Mechanical replacement across ~12 files:

- **`~/pyarchinit/bin/...` family (~30)** → `os.path.join(pyarchinit_home_bin(), …)`
  in `tabs/pyarchinit_Pottery_mainapp.py`, `tabs/Sam_Segmentation_Dialog.py`,
  `modules/utility/pottery_similarity/embedding_models.py`, `modules/utility/textTosql.py`,
  `tabs/Pottery_tools.py`, `modules/utility/pottery_similarity/similarity_search.py`.
- **Backups** `Path.home()/"pyarchinit"/"pyarchinit_DB_folder"` → resolver:
  `pyarchinitPlugin.py` (lines 2946, 3065, 3183, 3326, 3508), `gui/rapporti_check_dialog.py:235`,
  `scripts/migrations/2026_05_node_uuid_backfill.py:69`, `scripts/migrations/2026_05_media_fk_cascade.py:143`.
- **Paradata** `modules/s3dgraphy/sync/_workspace.py:69` default + `modules/s3dgraphy/s3dgraphy_dot_bridge.py:1064` → resolver.
- **Env-aware fallbacks** (already read the env var, only default fixed):
  `modules/utility/em_palette_parser.py:242`, `modules/utility/pyarchinit_dem_visualizer.py:51`.
- **Source #3** `modules/utility/textTosql.py:251` → resolver.
- **User-facing strings** that name the path (API-key prompts in
  `tabs/US_USM.py`, `tabs/Inv_Materiali.py`, `tabs/pyarchinit_Pottery_mainapp.py`,
  `modules/utility/textTosql.py`) → interpolate the real resolved path so the
  message stays accurate.
- **`scripts/import_tma_excel.py:424`** default config path → resolver.

### Out of scope (deliberately not touched)

- Plugin folder name `pyarchinit`.
- QSettings namespace `pyarchinit/` (339 refs) — not isolated by this change;
  documented as a known shared resource (see Risks).
- Subfolder / file / package names containing `pyarchinit_*`
  (`pyarchinit_DB_folder`, `pyarchinit_db_manager`, `pyarchinit_EXCEL_folder`, …).
- Throwaway analysis scripts referencing specific old `.sqlite` files by name:
  `scripts/analyze_correct_db.py`, `scripts/analyze_tma_areas.py`,
  `scripts/show_all_thesaurus_areas.py`, `scripts/verify_mapping.py`,
  `scripts/check_table_names.py`.
- Pure docstrings/comments mentioning `~/pyarchinit` (cosmetic; updated
  opportunistically only when already editing the line).

## First-run migration (in `__init__.py::initialize_environment`)

```
if not os.path.exists(pyarchinit_home()) and os.path.isdir(legacy_pyarchinit_home()):
    ask QMessageBox Yes/No:
      "Found an existing pyArchInit installation at ~/pyarchinit.
       Copy configuration and databases into pyarchinit_5?
       (AI tools in bin/ are NOT copied — reinstall or copy manually.)"
    on Yes: copytree(legacy/pyarchinit_DB_folder -> new/pyarchinit_DB_folder)
```

- Runs **before** `fi.install_dir()` so the copied tree is respected.
- **Important — do not short-circuit `install_dir`:** copying `pyarchinit_DB_folder`
  creates the new home dir, which would make the existing `if not os.path.exists(
  PYARCHINIT_HOME): fi.install_dir()` guard skip creation of the *other* subfolders
  (`bin`, `pyarchinit_PDF_folder`, …). Fix: `fi.install_dir()` must be **idempotent**
  (create-missing-only, e.g. `os.makedirs(..., exist_ok=True)`) and be called
  unconditionally after the optional migration copy. The implementation plan must
  verify/adjust `install_dir` for idempotency.
- Whole block in `try/except` → log and continue; never block startup (mirrors
  the existing maintenance-refresh guard at `__init__.py:828-832`).
- Idempotent: if the new home already exists, no prompt, no copy.

## Error handling

- Migration copy failure → `print('[pyArchInit] home migration skipped: …')`, continue.
- Malformed / empty `PYARCHINIT_HOME` → default.
- No destructive operations on the legacy home (copy only, never move/delete).

## Testing

- **New** `tests/test_pyarchinit_home.py`: default == `~/pyarchinit_5`; env override
  wins; empty env → default.
- **Update** `tests/sync/test_workspace_root.py` (currently asserts `~/pyarchinit/…`)
  → `pyarchinit_5` (or derive from the resolver to stay rename-proof).
- **Import sanity**: plugin package imports without error.
- **Verification grep**: no remaining runtime `~/pyarchinit` / `Path.home()/"pyarchinit"`
  literals outside migration helpers, out-of-scope scripts, and comments.

## Risks / known limitations

- **QSettings stay shared** (`pyarchinit/` group) when branch and master run in the
  same QGIS profile + same plugin folder: stored paths (paradata-workspace
  override, remote-storage creds, graphviz/pg bin paths, last-used dirs) carry
  over from whichever version ran last. Usually benign; explicitly out of scope.
- First branch run on a machine with an existing `~/pyarchinit` requires the user
  to accept the copy dialog (or reconfigure), and to re-setup/copy `bin/` AI
  assets if they use SAM/pottery/Text2SQL.
- No effect on `master` ✓ — it keeps reading/writing `~/pyarchinit`.