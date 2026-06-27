# pyArchInit data-home rename (`pyarchinit_5`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `Stratigraph_00001` branch store all runtime data under `~/pyarchinit_5/` (env-overridable) so the legacy `master` keeps `~/pyarchinit/` intact, via a single home-path resolver that every site derives from.

**Architecture:** New dependency-free resolver module `modules/utility/pyarchinit_home.py` is the single source of truth (`PYARCHINIT_HOME` env var → default `~/pyarchinit_5`). `__init__.py` sets the env var at import as the earliest authority; all ~40 hardcoded `~/pyarchinit` literals are replaced by resolver calls. `modules/s3dgraphy/sync/_workspace.py` stays import-clean and reads the env var directly. First QGIS launch offers to copy the legacy `pyarchinit_DB_folder`.

**Tech Stack:** Python 3, QGIS PyQt (QMessageBox), pytest, `shutil`/`os`/`pathlib`.

## Global Constraints

- Plugin folder name stays `pyarchinit`. Do NOT rename it.
- Do NOT touch the QSettings namespace `pyarchinit/` (339 refs) — out of scope.
- Do NOT touch subfolder/file/package names containing `pyarchinit_*` (`pyarchinit_DB_folder`, `pyarchinit_db_manager`, `pyarchinit_EXCEL_folder`, …). Only the top home segment changes.
- Default home name literal is exactly `pyarchinit_5`. Legacy is exactly `pyarchinit`.
- An empty `PYARCHINIT_HOME` env var counts as unset → default.
- No destructive ops on the legacy home (copy only; never move/delete).
- Commits: `git -c commit.gpgsign=false commit --no-verify`. NO `Co-Authored-By`, NO AI-attribution.
- Out of scope (do not edit): `scripts/analyze_correct_db.py`, `scripts/analyze_tma_areas.py`, `scripts/show_all_thesaurus_areas.py`, `scripts/verify_mapping.py`, `scripts/check_table_names.py`; pure docstrings/comments mentioning `~/pyarchinit` (update only opportunistically when already editing that exact line).
- Run tests from the plugin root with the repo's pytest setup (`conftest.py` adds the plugin dir to `sys.path`, so bare `from modules…` imports resolve).

---

### Task 1: Home resolver module + unit tests

**Files:**
- Create: `modules/utility/pyarchinit_home.py`
- Test: `tests/utility/test_pyarchinit_home.py`

**Interfaces:**
- Produces:
  - `pyarchinit_home() -> str` — resolved base dir.
  - `pyarchinit_home_bin() -> str` — `<home>/bin`.
  - `legacy_pyarchinit_home() -> str` — `~/pyarchinit` (migration only).
  - `migrate_db_folder(src_home: str, dst_home: str) -> bool` — copy `<src_home>/pyarchinit_DB_folder` into `<dst_home>/pyarchinit_DB_folder` (non-clobbering via `dirs_exist_ok=True`); returns True if the source DB folder existed and was copied.
  - `DEFAULT_HOME_NAME = "pyarchinit_5"`, `LEGACY_HOME_NAME = "pyarchinit"`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/utility/test_pyarchinit_home.py
"""L0 unit tests for the data-home resolver (pyarchinit_5 rename)."""
import os
from pathlib import Path

from modules.utility.pyarchinit_home import (
    pyarchinit_home, pyarchinit_home_bin, legacy_pyarchinit_home,
    migrate_db_folder, DEFAULT_HOME_NAME,
)


def test_default_when_env_unset(monkeypatch):
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    assert pyarchinit_home() == os.path.join(os.path.expanduser("~"), "pyarchinit_5")
    assert DEFAULT_HOME_NAME == "pyarchinit_5"


def test_env_var_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "custom_home"))
    assert pyarchinit_home() == str(tmp_path / "custom_home")


def test_empty_env_falls_through_to_default(monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", "")
    assert pyarchinit_home() == os.path.join(os.path.expanduser("~"), "pyarchinit_5")


def test_bin_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "h"))
    assert pyarchinit_home_bin() == str(tmp_path / "h" / "bin")


def test_legacy_home():
    assert legacy_pyarchinit_home() == os.path.join(os.path.expanduser("~"), "pyarchinit")


def test_migrate_db_folder_copies(tmp_path):
    src = tmp_path / "pyarchinit"
    (src / "pyarchinit_DB_folder").mkdir(parents=True)
    (src / "pyarchinit_DB_folder" / "config.cfg").write_text("X")
    dst = tmp_path / "pyarchinit_5"
    assert migrate_db_folder(str(src), str(dst)) is True
    assert (dst / "pyarchinit_DB_folder" / "config.cfg").read_text() == "X"


def test_migrate_db_folder_no_source(tmp_path):
    src = tmp_path / "pyarchinit"   # no pyarchinit_DB_folder inside
    src.mkdir()
    dst = tmp_path / "pyarchinit_5"
    assert migrate_db_folder(str(src), str(dst)) is False


def test_migrate_db_folder_source_wins_on_conflict(tmp_path):
    # Documents behaviour for the (real-flow-impossible) case where dst already
    # has the file: copytree(dirs_exist_ok=True) overwrites with the source.
    # In production migrate runs only when the new home is absent, so no
    # destination file pre-exists — this just pins the overwrite semantics.
    src = tmp_path / "pyarchinit"
    (src / "pyarchinit_DB_folder").mkdir(parents=True)
    (src / "pyarchinit_DB_folder" / "config.cfg").write_text("NEW")
    dst = tmp_path / "pyarchinit_5"
    (dst / "pyarchinit_DB_folder").mkdir(parents=True)
    (dst / "pyarchinit_DB_folder" / "config.cfg").write_text("KEEP")
    migrate_db_folder(str(src), str(dst))
    assert (dst / "pyarchinit_DB_folder" / "config.cfg").read_text() == "NEW"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/utility/test_pyarchinit_home.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'modules.utility.pyarchinit_home'`

- [ ] **Step 3: Write the resolver module**

```python
# modules/utility/pyarchinit_home.py
"""Single source of truth for the pyArchInit data-home directory.

The data home holds config.cfg, SQLite DBs, exports, backups, paradata and
the bin/ AI tooling. The branch defaults to ~/pyarchinit_5 so the legacy
master keeps ~/pyarchinit intact. Resolution: PYARCHINIT_HOME env var wins
(empty == unset), else the default. Dependency-free (os/shutil only) so it
imports at the very start of __init__.py and from standalone scripts.
"""
import os
import shutil

DEFAULT_HOME_NAME = "pyarchinit_5"
LEGACY_HOME_NAME = "pyarchinit"


def pyarchinit_home() -> str:
    """Resolved data-home base dir. Env var PYARCHINIT_HOME wins; else default."""
    env = os.environ.get("PYARCHINIT_HOME")
    if env:
        return env
    return os.path.join(os.path.expanduser("~"), DEFAULT_HOME_NAME)


def pyarchinit_home_bin() -> str:
    """`<home>/bin` — venvs, models, indexes, API keys."""
    return os.path.join(pyarchinit_home(), "bin")


def legacy_pyarchinit_home() -> str:
    """`~/pyarchinit` — the legacy master home (migration source only)."""
    return os.path.join(os.path.expanduser("~"), LEGACY_HOME_NAME)


def migrate_db_folder(src_home: str, dst_home: str) -> bool:
    """Copy `<src_home>/pyarchinit_DB_folder` into `<dst_home>/`.

    Returns True if the source DB folder existed and was copied. Uses
    dirs_exist_ok=True so a partially-created dst is tolerated. bin/ is NOT
    copied (heavy AI assets are reinstalled separately).
    """
    src_db = os.path.join(src_home, "pyarchinit_DB_folder")
    if not os.path.isdir(src_db):
        return False
    dst_db = os.path.join(dst_home, "pyarchinit_DB_folder")
    shutil.copytree(src_db, dst_db, dirs_exist_ok=True)
    return True
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/utility/test_pyarchinit_home.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git -c commit.gpgsign=false add modules/utility/pyarchinit_home.py tests/utility/test_pyarchinit_home.py
git -c commit.gpgsign=false commit --no-verify -m "feat(home): add pyarchinit_home resolver (default ~/pyarchinit_5)"
```

---

### Task 2: Wire `__init__.py` + `folder_installation.py` to the resolver + first-run migration

**Files:**
- Modify: `__init__.py` (line 49 source #1; `initialize_environment` around lines 818-841)
- Modify: `modules/utility/pyarchinit_folder_installation.py:28-30`

**Interfaces:**
- Consumes: `pyarchinit_home`, `legacy_pyarchinit_home`, `migrate_db_folder` from Task 1.
- Produces: `os.environ['PYARCHINIT_HOME']` set to the resolved home at import time (relied on by `pyarchinitPlugin.py:46` `HOME = os.environ['PYARCHINIT_HOME']`).

- [ ] **Step 1: Point `folder_installation` at the resolver (stop hardcoding/overwriting env)**

In `modules/utility/pyarchinit_folder_installation.py`, change the import block (line 24 area) and the class-body lines 28-30.

Add to imports (after line 24 `from .pyarchinit_OS_utility import Pyarchinit_OS_Utility`):
```python
from .pyarchinit_home import pyarchinit_home
```
Replace lines 28-30:
```python
    HOME = expanduser("~")
    HOME += os.sep + 'pyarchinit'
    os.environ['PYARCHINIT_HOME'] = HOME
```
with:
```python
    HOME = pyarchinit_home()
```
(The `from os.path import expanduser` at line 22 may now be unused — leave it; it is harmless and other code may rely on the module-level import. Do NOT remove unless grep proves it unused in this file.)

- [ ] **Step 2: Make `__init__.py` source #1 resolver-driven and set env at import**

In `__init__.py`, replace line 49:
```python
PYARCHINIT_HOME = os.path.expanduser("~") + os.sep + 'pyarchinit'
```
with:
```python
from .modules.utility.pyarchinit_home import (
    pyarchinit_home, legacy_pyarchinit_home, migrate_db_folder)

PYARCHINIT_HOME = pyarchinit_home()
# Earliest authority: every later pyarchinit_home() / os.environ read resolves
# to the same value (default ~/pyarchinit_5, or an external override).
os.environ['PYARCHINIT_HOME'] = PYARCHINIT_HOME
```

- [ ] **Step 3: Ensure `shutil` is importable in `__init__.py`**

Run: `grep -n "^import shutil\|^from shutil" "__init__.py"`
If no match, add `import shutil` near the other stdlib imports (top of file, after `import os`). (Not strictly needed since migration uses `migrate_db_folder`, but the migration helper below uses no shutil directly — skip if unused.)

- [ ] **Step 4: Add the first-run migration helper + rewire the install flow**

In `__init__.py`, locate the block (currently lines ~818-833):
```python
    fi = pyarchinit_Folder_installation()
    if not os.path.exists(PYARCHINIT_HOME):
        fi.install_dir()
    else:
        os.environ['PYARCHINIT_HOME'] = PYARCHINIT_HOME
        # Even on existing installs, refresh bundled maintenance
        # files (dot.py, dottoxml.py, …) when the plugin shipped a
        # newer version. Without this, fixes inside the plugin's
        # resources/dbfiles/ never reach ~/pyarchinit/bin/ where
        # they actually run.
        try:
            fi.install_or_update_maintenance_files()
        except Exception as _exc:
            # Never block plugin startup on a maintenance refresh.
            print(f"[pyArchInit] maintenance refresh skipped: {_exc}")
    _step()
```
Replace it with:
```python
    fi = pyarchinit_Folder_installation()

    # First-run migration: if the new home is absent but a legacy
    # ~/pyarchinit exists, offer to copy its DB folder (config + DBs).
    migrated = False
    if not os.path.exists(PYARCHINIT_HOME):
        legacy = legacy_pyarchinit_home()
        if os.path.isdir(os.path.join(legacy, "pyarchinit_DB_folder")):
            try:
                reply = QMessageBox.question(
                    None, "pyArchInit",
                    "Trovata un'installazione pyArchInit esistente in:\n"
                    f"{legacy}\n\n"
                    "Vuoi copiare configurazione e database nella nuova "
                    "cartella?\n"
                    f"{PYARCHINIT_HOME}\n\n"
                    "(Gli strumenti AI in bin/ NON vengono copiati: vanno "
                    "reinstallati o copiati manualmente.)",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.Yes:
                    migrated = migrate_db_folder(legacy, PYARCHINIT_HOME)
            except Exception as _exc:
                print(f"[pyArchInit] home migration skipped: {_exc}")

    if not os.path.exists(PYARCHINIT_HOME):
        fi.install_dir()
    else:
        os.environ['PYARCHINIT_HOME'] = PYARCHINIT_HOME
        if migrated:
            # Migration created only pyarchinit_DB_folder; create the rest
            # of the tree (bin/, exports, …). create_dir + copy_file are
            # idempotent and non-clobbering, so migrated files survive.
            fi.install_dir()
        # Refresh bundled maintenance files (dot.py, dottoxml.py, …) when the
        # plugin shipped a newer version, so fixes reach <home>/bin/.
        try:
            fi.install_or_update_maintenance_files()
        except Exception as _exc:
            # Never block plugin startup on a maintenance refresh.
            print(f"[pyArchInit] maintenance refresh skipped: {_exc}")
    _step()
```

- [ ] **Step 5: Import sanity check**

Run: `python -c "import ast; ast.parse(open('__init__.py').read()); ast.parse(open('modules/utility/pyarchinit_folder_installation.py').read()); print('syntax ok')"`
Expected: `syntax ok`

Run: `python -c "import os; os.environ.pop('PYARCHINIT_HOME', None); import sys; sys.path.insert(0,'.'); from modules.utility.pyarchinit_home import pyarchinit_home; print(pyarchinit_home())"`
Expected: ends with `/pyarchinit_5`

- [ ] **Step 6: Commit**

```bash
git -c commit.gpgsign=false add __init__.py modules/utility/pyarchinit_folder_installation.py
git -c commit.gpgsign=false commit --no-verify -m "feat(home): resolver-driven PYARCHINIT_HOME + first-run DB-folder migration"
```

---

### Task 3: `_workspace.py` env-aware default + update its tests

**Files:**
- Modify: `modules/s3dgraphy/sync/_workspace.py:66-69`
- Test: `tests/sync/test_workspace_root.py`

**Interfaces:**
- Consumes: `PYARCHINIT_HOME` env var (NOT the resolver — this module must stay free of `qgis.*`/`pyarchinit` imports per s3dgraphy upstream policy).

- [ ] **Step 1: Update the failing tests first**

In `tests/sync/test_workspace_root.py`, replace the three default-path assertions and add `PYARCHINIT_HOME` cleanup. Replace `test_default_when_env_unset` and `test_empty_env_var_falls_through_to_default`:
```python
def test_default_when_env_unset(monkeypatch):
    """With both env vars unset, the root defaults to
    ~/pyarchinit_5/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit_5" / "pyarchinit_DB_folder"


def test_empty_env_var_falls_through_to_default(monkeypatch):
    """Empty workspace + home env vars fall through to the default."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit_5" / "pyarchinit_DB_folder"
```
Add a new test:
```python
def test_pyarchinit_home_env_drives_default(monkeypatch, tmp_path):
    """When PYARCHINIT_WORKSPACE_DIR is unset, PYARCHINIT_HOME drives the base."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "h"))
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == tmp_path / "h" / "pyarchinit_DB_folder"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/sync/test_workspace_root.py -v`
Expected: FAIL on the default assertions (still returns `pyarchinit`)

- [ ] **Step 3: Update the resolver default**

In `modules/s3dgraphy/sync/_workspace.py`, replace lines 66-69:
```python
    env_override = os.environ.get("PYARCHINIT_WORKSPACE_DIR")
    if env_override:
        return Path(env_override).expanduser()
    return Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
```
with:
```python
    env_override = os.environ.get("PYARCHINIT_WORKSPACE_DIR")
    if env_override:
        return Path(env_override).expanduser()
    # Default base follows the data-home (PYARCHINIT_HOME env var, set by the
    # host plugin); falls back to ~/pyarchinit_5. Kept as a bare env read so
    # this module stays free of qgis.*/pyarchinit imports (s3dgraphy policy).
    home = os.environ.get("PYARCHINIT_HOME")
    base = Path(home) if home else Path.home() / "pyarchinit_5"
    return base / "pyarchinit_DB_folder"
```
Also update the docstring line 50 `2. Default: ~/pyarchinit/pyarchinit_DB_folder` → `2. Default: $PYARCHINIT_HOME/pyarchinit_DB_folder (else ~/pyarchinit_5/...)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_workspace_root.py -v`
Expected: PASS (5 passed — the tilde and override tests are unchanged)

- [ ] **Step 5: Commit**

```bash
git -c commit.gpgsign=false add modules/s3dgraphy/sync/_workspace.py tests/sync/test_workspace_root.py
git -c commit.gpgsign=false commit --no-verify -m "feat(home): paradata workspace default follows PYARCHINIT_HOME (~/pyarchinit_5)"
```

---

### Task 4: Backup + paradata + migration-script literals → resolver

**Files (modify):**
- `pyarchinitPlugin.py` (lines 2946, 3065, 3183, 3326, 3508)
- `gui/rapporti_check_dialog.py:235`
- `scripts/migrations/2026_05_node_uuid_backfill.py:69`
- `scripts/migrations/2026_05_media_fk_cascade.py:143`
- `modules/s3dgraphy/s3dgraphy_dot_bridge.py:1064`

**Interfaces:**
- Consumes: `pyarchinit_home` from Task 1.

- [ ] **Step 1: Add the resolver import to each file**

For each file above, add near the top imports (use the import style already present in that file):
- `pyarchinitPlugin.py`, `gui/rapporti_check_dialog.py`, `modules/s3dgraphy/s3dgraphy_dot_bridge.py`: `from modules.utility.pyarchinit_home import pyarchinit_home`
- `scripts/migrations/2026_05_node_uuid_backfill.py`, `scripts/migrations/2026_05_media_fk_cascade.py`: these run standalone; add a sys.path-safe import. Check the file's existing import header first; add:
  ```python
  from modules.utility.pyarchinit_home import pyarchinit_home
  ```
  If the script does not already put the plugin root on `sys.path`, follow its existing pattern for locating the plugin (read the file header before editing).

- [ ] **Step 2: Replace each literal**

Pattern: `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"` → `Path(pyarchinit_home()) / "pyarchinit_DB_folder"`.

Exact sites (the surrounding multi-line expression keeps its other parts):
- `pyarchinitPlugin.py:2946` `dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"` → `dest_dir = (Path(pyarchinit_home()) / "pyarchinit_DB_folder"`
- `pyarchinitPlugin.py:3065`, `:3183`, `:3326` — identical replacement.
- `pyarchinitPlugin.py:3508` `dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"` → same.
- `gui/rapporti_check_dialog.py:235` `Path.home() / "pyarchinit" / "pyarchinit_DB_folder"` → `Path(pyarchinit_home()) / "pyarchinit_DB_folder"`.
- `scripts/migrations/2026_05_node_uuid_backfill.py:69` `dest_dir=Path.home() / "pyarchinit" / "pyarchinit_DB_folder"` → `dest_dir=Path(pyarchinit_home()) / "pyarchinit_DB_folder"`.
- `scripts/migrations/2026_05_media_fk_cascade.py:143` — same.
- `modules/s3dgraphy/s3dgraphy_dot_bridge.py:1064` `dest_dir = (_P.home() / "pyarchinit"` — this uses the alias `_P` for `Path` and the `pyarchinit_DB_folder` segment is on the next line. Read lines 1064-1066, then replace the `_P.home() / "pyarchinit" / "pyarchinit_DB_folder"` expression with `_P(pyarchinit_home()) / "pyarchinit_DB_folder"`.

- [ ] **Step 3: Verify no stale literals remain in these files**

Run:
```bash
grep -nE 'home\(\) */ *"pyarchinit"' pyarchinitPlugin.py gui/rapporti_check_dialog.py scripts/migrations/2026_05_node_uuid_backfill.py scripts/migrations/2026_05_media_fk_cascade.py modules/s3dgraphy/s3dgraphy_dot_bridge.py
```
Expected: no output.

- [ ] **Step 4: Syntax check**

Run:
```bash
for f in pyarchinitPlugin.py gui/rapporti_check_dialog.py scripts/migrations/2026_05_node_uuid_backfill.py scripts/migrations/2026_05_media_fk_cascade.py modules/s3dgraphy/s3dgraphy_dot_bridge.py; do python -c "import ast; ast.parse(open('$f').read())" && echo "ok $f"; done
```
Expected: `ok` for all five.

- [ ] **Step 5: Commit**

```bash
git -c commit.gpgsign=false add pyarchinitPlugin.py gui/rapporti_check_dialog.py scripts/migrations/2026_05_node_uuid_backfill.py scripts/migrations/2026_05_media_fk_cascade.py modules/s3dgraphy/s3dgraphy_dot_bridge.py
git -c commit.gpgsign=false commit --no-verify -m "refactor(home): backups + paradata + migration scripts use pyarchinit_home()"
```

---

### Task 5: Env-aware fallbacks → resolver

**Files (modify):**
- `modules/utility/em_palette_parser.py:242`
- `modules/utility/pyarchinit_dem_visualizer.py:54-55`
- `modules/utility/textTosql.py:251`

**Interfaces:**
- Consumes: `pyarchinit_home` from Task 1.

- [ ] **Step 1: em_palette_parser.py**

Add import (sibling): `from .pyarchinit_home import pyarchinit_home` (place with other imports; verify none already).
Replace line 242:
```python
    home = os.environ.get("PYARCHINIT_HOME") or str(Path.home() / "pyarchinit")
```
with:
```python
    home = pyarchinit_home()
```

- [ ] **Step 2: pyarchinit_dem_visualizer.py**

Add import: `from .pyarchinit_home import pyarchinit_home`.
Replace lines 54-55:
```python
    home = os.environ.get('PYARCHINIT_HOME') or os.path.join(
        os.path.expanduser('~'), 'pyarchinit')
```
with:
```python
    home = pyarchinit_home()
```
Update the docstring line 51 `~/pyarchinit/site_dashboard/<sito>` → `~/pyarchinit_5/site_dashboard/<sito>`.

- [ ] **Step 3: textTosql.py:251**

Read lines 245-255 first to see how `HOME` is defined above line 251. Add import `from modules.utility.pyarchinit_home import pyarchinit_home` (match the file's import style).
Replace line 251:
```python
        PYARCHINIT_HOME = os.path.join(HOME, "pyarchinit")
```
with:
```python
        PYARCHINIT_HOME = pyarchinit_home()
```

- [ ] **Step 4: Verify + syntax**

Run:
```bash
grep -nE 'os\.environ\.get\("PYARCHINIT_HOME"\) or str\(Path\.home\(\) / "pyarchinit"\)|join\(HOME, "pyarchinit"\)' modules/utility/em_palette_parser.py modules/utility/textTosql.py
for f in modules/utility/em_palette_parser.py modules/utility/pyarchinit_dem_visualizer.py modules/utility/textTosql.py; do python -c "import ast; ast.parse(open('$f').read())" && echo "ok $f"; done
```
Expected: no grep output; `ok` for all three.

- [ ] **Step 5: Commit**

```bash
git -c commit.gpgsign=false add modules/utility/em_palette_parser.py modules/utility/pyarchinit_dem_visualizer.py modules/utility/textTosql.py
git -c commit.gpgsign=false commit --no-verify -m "refactor(home): env-aware fallbacks use pyarchinit_home()"
```

---

### Task 6: `bin/` family literals → `pyarchinit_home_bin()`

**Files (modify):**
- `tabs/pyarchinit_Pottery_mainapp.py` (lines 5392, 7567, 7631, 7793-7796, 7866, 7932, 8097, 8165-8166, 8388)
- `tabs/Sam_Segmentation_Dialog.py` (lines 62-63, 125, 127, 130, 192-193, 543, 1195)
- `modules/utility/pottery_similarity/embedding_models.py` (lines 76, 84, 192, 199, 341, 479, 493, 538)
- `modules/utility/pottery_similarity/similarity_search.py` (lines 41, 350)
- `tabs/Pottery_tools.py` (lines 1984, 2075)

**Interfaces:**
- Consumes: `pyarchinit_home`, `pyarchinit_home_bin` from Task 1.

**Transformation rules:**
- `os.path.expanduser('~/pyarchinit/bin/REST')` → `os.path.join(pyarchinit_home_bin(), 'REST')` (split REST on `/` into join args, e.g. `'models/khutm_clip'` → `'models', 'khutm_clip'`).
- `os.path.join(os.path.expanduser("~/pyarchinit/bin"), "x.py")` → `os.path.join(pyarchinit_home_bin(), "x.py")`.
- `Path.home() / 'pyarchinit' / 'pyarchinit_DB_folder' / 'config.cfg'` (similarity_search.py:41) → `Path(pyarchinit_home()) / 'pyarchinit_DB_folder' / 'config.cfg'`.
- `os.path.expanduser('~/pyarchinit/pyarchinit_DB_folder/config.cfg')` (Sam_Segmentation_Dialog.py:543) → `os.path.join(pyarchinit_home(), 'pyarchinit_DB_folder', 'config.cfg')`.
- `os.path.expanduser('~/pyarchinit/pyarchinit_DB_folder')` (Sam_Segmentation_Dialog.py:1195) → `os.path.join(pyarchinit_home(), 'pyarchinit_DB_folder')`.

- [ ] **Step 1: Add imports**

Add to each of the 5 files (match existing import style):
- `tabs/*`: `from modules.utility.pyarchinit_home import pyarchinit_home, pyarchinit_home_bin`
- `modules/utility/pottery_similarity/embedding_models.py` and `similarity_search.py`: `from modules.utility.pyarchinit_home import pyarchinit_home, pyarchinit_home_bin` (these are under modules/utility/pottery_similarity/; a bare `from modules.utility...` import works because the plugin root is on sys.path at runtime — confirm the file already uses `from modules…` style; if it uses relative imports, use `from ...pyarchinit_home import ...`).

- [ ] **Step 2: Apply the transformation rule to every listed line**

Read each file's listed lines (the grep inventory in the spec gives the exact current text), then apply the matching rule above. Examples (verbatim before → after):
- `tabs/pyarchinit_Pottery_mainapp.py:7567` `index_dir = os.path.expanduser('~/pyarchinit/bin/pottery_similarity')` → `index_dir = os.path.join(pyarchinit_home_bin(), 'pottery_similarity')`
- `tabs/pyarchinit_Pottery_mainapp.py:7796` `model_dir = os.path.expanduser('~/pyarchinit/bin/models/khutm_clip')` → `model_dir = os.path.join(pyarchinit_home_bin(), 'models', 'khutm_clip')`
- `tabs/Sam_Segmentation_Dialog.py:62` `venv_python = os.path.expanduser('~/pyarchinit/bin/sam_venv/bin/python')` → `venv_python = os.path.join(pyarchinit_home_bin(), 'sam_venv', 'bin', 'python')`
- `tabs/Sam_Segmentation_Dialog.py:130` (message string) `"SAM virtual environment not found at ~/pyarchinit/bin/sam_venv/"` → keep human text but make it accurate: `f"SAM virtual environment not found at {os.path.join(pyarchinit_home_bin(), 'sam_venv')}"`
- `modules/utility/pottery_similarity/embedding_models.py:479` `MODEL_DIR = os.path.expanduser('~/pyarchinit/bin/models/khutm_clip')` → if this is a class/module constant evaluated at import, use `MODEL_DIR = os.path.join(pyarchinit_home_bin(), 'models', 'khutm_clip')`.
- `tabs/Pottery_tools.py:1984` `runner_script = os.path.join(os.path.expanduser("~/pyarchinit/bin"), "yolo_runner.py")` → `runner_script = os.path.join(pyarchinit_home_bin(), "yolo_runner.py")`; line 2075 is a docstring — update text `~/pyarchinit/bin` → `<home>/bin` only if editing nearby.
- `modules/utility/pottery_similarity/similarity_search.py:41` per the Path rule above; `:350` `api_key_path = os.path.expanduser("~/pyarchinit/bin/gpt_api_key.txt")` → `api_key_path = os.path.join(pyarchinit_home_bin(), "gpt_api_key.txt")`.

Apply to ALL lines listed in **Files** above using the rules; do not skip any.

- [ ] **Step 3: Verify no runtime `~/pyarchinit/bin` literals remain (comments/docstrings excluded)**

Run:
```bash
grep -nE "expanduser\('~/pyarchinit/bin|expanduser\(\"~/pyarchinit/bin|expanduser\('~/pyarchinit/pyarchinit_DB_folder|home\(\) / 'pyarchinit' /" tabs/pyarchinit_Pottery_mainapp.py tabs/Sam_Segmentation_Dialog.py modules/utility/pottery_similarity/embedding_models.py modules/utility/pottery_similarity/similarity_search.py tabs/Pottery_tools.py
```
Expected: no output (any remaining hit must be a comment/docstring; inspect and confirm).

- [ ] **Step 4: Syntax check**

Run:
```bash
for f in tabs/pyarchinit_Pottery_mainapp.py tabs/Sam_Segmentation_Dialog.py modules/utility/pottery_similarity/embedding_models.py modules/utility/pottery_similarity/similarity_search.py tabs/Pottery_tools.py; do python -c "import ast; ast.parse(open('$f').read())" && echo "ok $f"; done
```
Expected: `ok` for all five.

- [ ] **Step 5: Commit**

```bash
git -c commit.gpgsign=false add tabs/pyarchinit_Pottery_mainapp.py tabs/Sam_Segmentation_Dialog.py modules/utility/pottery_similarity/embedding_models.py modules/utility/pottery_similarity/similarity_search.py tabs/Pottery_tools.py
git -c commit.gpgsign=false commit --no-verify -m "refactor(home): bin/ AI tooling paths use pyarchinit_home_bin()"
```

---

### Task 7: All remaining home-path forms (gap) + user-facing strings + TMA script

> **Scope note:** Task 6's brief inventory (built from a grep of only the
> `expanduser("~/pyarchinit/...")` single-string form) MISSED several other
> forms the codebase uses for the SAME data home: split-component joins
> (`os.path.join(os.path.expanduser("~"), "pyarchinit", "bin", ...)`),
> `home_dir`-variable joins (`os.path.join(home_dir, "pyarchinit", "bin", ...)`),
> env-aware-with-default (`os.environ.get("PYARCHINIT_HOME", os.path.join(os.path.expanduser("~"), "pyarchinit"))`),
> and one Path-division (`os.path.expanduser('~/pyarchinit')` then `/'bin'`).
> This task converts ALL of them so the rename is consistent. **Method:
> grep each file to find every occurrence (line numbers below are indicative
> and WILL have drifted), then convert by content match.**

**Files (modify):**
- `tabs/Pottery_tools.py`
- `tabs/US_USM.py`
- `tabs/Inv_Materiali.py`
- `tabs/pyarchinit_Pottery_mainapp.py`
- `modules/utility/pottery_utilities.py`
- `modules/utility/llm_providers.py`
- `modules/utility/pottery_similarity/index_manager.py`
- `modules/utility/textTosql.py` (message strings only)
- `scripts/import_tma_excel.py`

**Interfaces:**
- Consumes: `pyarchinit_home`, `pyarchinit_home_bin` from Task 1.

**Transformation rules (same as Task 6, generalized to all forms):**
- Any path under `.../bin/...` → `os.path.join(pyarchinit_home_bin(), <segments after bin>)`.
- Any path that is the home base or under a non-bin subfolder (e.g. `pyarchinit_DB_folder`, `pottery_extracted`, `pottery_ink_output`) → `os.path.join(pyarchinit_home(), <segments after the home>)` (or `pyarchinit_home()` alone if it IS the base).
- The `/`-segments must be split into ordered `os.path.join` args, none dropped/reordered.
- env-aware-with-default forms (`os.environ.get("PYARCHINIT_HOME", <default>)`) collapse to just `pyarchinit_home()` (the resolver already does the env read) — e.g. `HOME = os.environ.get('PYARCHINIT_HOME', os.path.join(os.path.expanduser('~'), 'pyarchinit'))` → `HOME = pyarchinit_home()`.
- DO NOT touch `modules/s3dgraphy/sync/pyarchinit_pg_importer.py` line ~35 — its `/ "pyarchinit"` is a MAPPINGS subfolder under `ext_libs/s3dgraphy/mappings/pyarchinit/`, NOT the data home. Verify by reading the surrounding lines.

- [ ] **Step 1: Find every site per file**

Run, then convert each hit with the rules above:
```bash
grep -nE "expanduser\((['\"])~\1\)\s*,\s*(['\"])pyarchinit\2|[a-z_]*home[a-z_]*\s*,\s*(['\"])pyarchinit\3|expanduser\((['\"])~/pyarchinit|environ\.get\((['\"])PYARCHINIT_HOME\6\s*,|os\.sep\s*\+\s*(['\"])pyarchinit\7" tabs/Pottery_tools.py tabs/US_USM.py tabs/Inv_Materiali.py tabs/pyarchinit_Pottery_mainapp.py modules/utility/pottery_utilities.py modules/utility/llm_providers.py modules/utility/pottery_similarity/index_manager.py
```
Indicative sites to expect (verify by grep — DO NOT trust these line numbers):
- `Pottery_tools.py`: ~139 (bin/pottery_venv), 739 (pottery_extracted → home, NOT bin), 919 (bin/pottery_ink_model.pkl), 955 (bin/models), 1796 (bin), 1827 (bin), 3006 (pottery_ink_output → home, NOT bin), 3051 (bin/models). After converting, check whether `home_dir = os.path.expanduser('~')` (≈138, 1795, 1826) is now unused on that line's scope; remove only if it has no other use in the same function, else leave it.
- `US_USM.py`: ~4832 (home_dir,bin,gpt_api_key.txt → bin), 5956 (env-aware faiss_index → bin), 5957 (env-aware faiss_index_hash.txt → bin).
- `Inv_Materiali.py`: ~7688, 7909 (env-aware HOME default → `pyarchinit_home()`).
- `pyarchinit_Pottery_mainapp.py`: ~5361 (env-aware HOME default → `pyarchinit_home()`).
- `pottery_utilities.py`: ~201, 203, 211, 277 (home_dir,bin,... → bin), 1259 (expanduser,bin/models → bin).
- `llm_providers.py`: ~617 (bin/gpt_api_key.txt), ~620 (bin/claude_api_key.txt, multiline), ~635 (bin/anthropic_api_key.txt, multiline) — read the multiline join blocks before editing.
- `index_manager.py`: ~38 `INDEX_BASE_PATH = os.path.join(os.path.expanduser('~/pyarchinit'), 'bin', 'pottery_similarity')` → `os.path.join(pyarchinit_home_bin(), 'pottery_similarity')`.

- [ ] **Step 2: Add the resolver import to each file (check first; don't duplicate)**

- `tabs/*` (Pottery_tools, US_USM, Inv_Materiali, pyarchinit_Pottery_mainapp): some already gained the import in Task 6 (Pottery_tools, pyarchinit_Pottery_mainapp). For the others add `from modules.utility.pyarchinit_home import pyarchinit_home, pyarchinit_home_bin` matching the file's import style.
- `modules/utility/pottery_utilities.py`, `modules/utility/llm_providers.py`: siblings of the resolver → `from .pyarchinit_home import pyarchinit_home, pyarchinit_home_bin` (match the file's existing relative/bare style — read the import header first).
- `modules/utility/pottery_similarity/index_manager.py`: one level down → `from ..pyarchinit_home import pyarchinit_home_bin` (two dots) OR bare `from modules.utility.pyarchinit_home import pyarchinit_home_bin` — match the file's existing style.

- [ ] **Step 3: Make API-key prompt MESSAGE strings reflect the real path**

For each human-readable string mentioning a `~/pyarchinit/bin/...` path, interpolate the resolved path:
- `tabs/US_USM.py:~4840` `"Please set your OpenAI API key in ~/pyarchinit/bin/gpt_api_key.txt"` → `f"Please set your OpenAI API key in {os.path.join(pyarchinit_home_bin(), 'gpt_api_key.txt')}"`
- `tabs/Inv_Materiali.py:~7713-7715` (it/en ternary, both branches) and `tabs/pyarchinit_Pottery_mainapp.py:~5392` ("Verrà salvata in ~/pyarchinit/bin/gpt_api_key.txt") — interpolate the bin path.
- `modules/utility/textTosql.py:~377 & ~540` (gpt_api_key.txt / claude_api_key.txt messages), `modules/utility/pottery_utilities.py:~286` ("YOLO model not found in ~/pyarchinit/bin/") — interpolate. textTosql already imports `pyarchinit_home`; add `pyarchinit_home_bin` to that import.

- [ ] **Step 4: import_tma_excel.py default config path**

Read `scripts/import_tma_excel.py` around the default config path (`"~/pyarchinit/pyarchinit_DB_folder/config.cfg"`). Confirm whether the script puts the plugin root on `sys.path`. If it does, add `from modules.utility.pyarchinit_home import pyarchinit_home` and use `os.path.join(pyarchinit_home(), "pyarchinit_DB_folder", "config.cfg")`. If NOT, inline (no fragile import): `os.path.join(os.environ.get("PYARCHINIT_HOME") or os.path.join(os.path.expanduser("~"), "pyarchinit_5"), "pyarchinit_DB_folder", "config.cfg")`.

- [ ] **Step 5: Verify + syntax check**

Run the Step 1 grep again over ALL nine files — expect NO output except the deliberately-skipped `pg_importer.py` (not in the list) and any comment/docstring you consciously left. Then:
```bash
for f in tabs/Pottery_tools.py tabs/US_USM.py tabs/Inv_Materiali.py tabs/pyarchinit_Pottery_mainapp.py modules/utility/pottery_utilities.py modules/utility/llm_providers.py modules/utility/pottery_similarity/index_manager.py modules/utility/textTosql.py scripts/import_tma_excel.py; do python -c "import ast; ast.parse(open('$f').read())" && echo "ok $f"; done
```
Expected: `ok` for all nine.

- [ ] **Step 6: Commit**

```bash
git -c commit.gpgsign=false add tabs/Pottery_tools.py tabs/US_USM.py tabs/Inv_Materiali.py tabs/pyarchinit_Pottery_mainapp.py modules/utility/pottery_utilities.py modules/utility/llm_providers.py modules/utility/pottery_similarity/index_manager.py modules/utility/textTosql.py scripts/import_tma_excel.py
git -c commit.gpgsign=false commit --no-verify -m "refactor(home): remaining home-path forms + user-facing strings + TMA script use resolver"
```

---

### Task 8: Full verification sweep

**Files:** none (verification only)

- [ ] **Step 1: Run the home-related test suites**

Run: `python -m pytest tests/utility/test_pyarchinit_home.py tests/sync/test_workspace_root.py -v`
Expected: all PASS.

- [ ] **Step 2: Run the broader suite to catch regressions**

Run: `python -m pytest tests/ -q`
Expected: same pass/skip profile as before this work (PG-dependent skips are expected offline). Compare against a pre-change baseline if unsure: `git stash` is NOT needed — just confirm no NEW failures referencing home paths.

- [ ] **Step 3: Repo-wide residual scan (ALL forms)**

Run the comprehensive scan — this catches EVERY way the data home is spelled (single-string, split-join, `home_dir` var, env-aware default, `Path.home()/`, `os.sep +`):
```bash
grep -rnE "[\"']pyarchinit[\"']" --include='*.py' tabs modules gui __init__.py scripts \
  | grep -vE "pyarchinit_home|legacy_pyarchinit|import pyarchinit|from pyarchinit|\.pyarchinit" \
  | grep -vE "/analyze_correct_db\.py|/analyze_tma_areas\.py|/show_all_thesaurus_areas\.py|/verify_mapping\.py|/check_table_names\.py"
```
Triage every hit. Legitimate remaining matches are ONLY:
- comments / docstrings mentioning `~/pyarchinit`;
- `modules/s3dgraphy/sync/pyarchinit_pg_importer.py` — the `"pyarchinit"` MAPPINGS subfolder under `ext_libs/s3dgraphy/mappings/pyarchinit/` (NOT the data home);
- any string that is genuinely not a data-home path component.
If ANY hit is live runtime code building a data-home path (in any form), it was missed — fix it with the Task 4/6/7 rules and re-commit. Also re-run the bin-specific grep from Task 6 Step 3 and the Task 7 Step 1 grep and confirm both are clean.

- [ ] **Step 4: Confirm the env-set authority**

Run: `python -c "import os; os.environ.pop('PYARCHINIT_HOME',None); import ast; ast.parse(open('__init__.py').read()); print('init ok')"`
Expected: `init ok` (full QGIS import can't run headless; this confirms syntax + the resolver default path from Step 1 of Task 2).

- [ ] **Step 5: Final commit (if Step 3 required fixes)**

Add ONLY the specific files you fixed by name — do NOT use `git add -A` (the working tree has unrelated untracked files: `AGENTS.md`, `pyarchinitPlugin.py.bak_palimpsest`, and a mid-feature `dev_logs/CHANGELOG.md` edit that the controller reconciles separately).
```bash
git -c commit.gpgsign=false add <only the files you changed in this step>
git -c commit.gpgsign=false commit --no-verify -m "refactor(home): residual data-home literals → resolver"
```

---

## Post-implementation (NOT part of task execution — surface to user)

- **Autonomous agents** (per CLAUDE.md): after code changes, invoke `stratigraph-changelog` (bilingual CHANGELOG). `tutorial-updater` only if user-facing behaviour changed — here the migration dialog is new user-facing behaviour, so a short tutorial note on first-run migration / `~/pyarchinit_5` is warranted.
- **Manual QGIS verification** (cannot be automated headless): fresh launch with no `~/pyarchinit_5` but existing `~/pyarchinit` → migration dialog appears → Yes copies `pyarchinit_DB_folder` → plugin runs against `~/pyarchinit_5`; `~/pyarchinit` untouched.
- **Tag/release**: only on explicit user request.

## Self-Review notes (author)

- Spec coverage: resolver (T1), source #1 + migration + idempotent flow (T2), source #3 textTosql (T5), `_workspace` policy-safe env read (T3), bin/ family (T6), backups/paradata/migration-scripts (T4), user strings + TMA (T7), tests + residual sweep (T8). All spec §sections mapped.
- Migration safety note: `copy_file` skips existing, `create_dir` swallows exists, `shutil.copytree(dirs_exist_ok=True)` overwrites same-named files from source (real flow never hits this — migrate runs only when the new home is absent) — pinned by T1 test `test_migrate_db_folder_source_wins_on_conflict`.
- Type consistency: resolver returns `str` everywhere; sites wrap with `Path(...)` where they need a Path (T4 backups, T6 similarity_search:41). `pyarchinit_home_bin()` returns `str` for `os.path.join`.
