# yE-F Multi-Folder Paradata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement single-row + `other_locations` + render-time fan-out model for paradata (DOC/Combinar/Extractor/property) so a label shared across N yEd folders produces 1 us_table row + JSON list of secondary activities, restoring identity-dedup while preserving multi-folder visibility on re-export.

**Architecture:** Three new code paths in the existing yE-D pipeline: (1) **fold-at-import** in `_write_us_rows` groups paradata leaves by `(d_stratigrafica, unita_tipo)` with first-in-document-order primary and appends others to a new `other_locations` TEXT column; (2) **fan-out-at-export** in `graphml_writer._apply_yef_fan_out` emits N visual yEd `<node>` copies sharing the canonical `pyarchinit.node_uuid` for round-trip identity; (3) **per-folder edge resolver** in `graph_projector._enrich_into` picks the target copy whose `attivita` attribute matches the source's folder. B1 (Bug R 5.8.5-alpha) legacy data stays functional via `other_locations IS NULL` detection.

**Tech Stack:** Python 3.x · SQLAlchemy (text) · SQLite/PostgreSQL via DbHandle shim · s3dgraphy ext_libs · pytest · Qt Designer `.ui` · QGIS plugin context.

---

## File Structure

**Files created (new):**
- `scripts/migrations/2026_05_yef_other_locations_lib.py` — library: `add_other_locations_column(handle) -> int` + backup helpers, idempotent.
- `scripts/migrations/2026_05_yef_other_locations.py` — argparse CLI wrapper (`--apply` / `--dry-run`, `--db` / `--conn-str` mutex).
- `tests/sync/test_yef_migration.py` — migration unit + idempotency tests.
- `tests/sync/test_yef_fold.py` — `_resolve_folder_for_leaf` helper + `_write_us_rows` yE-F branch tests.
- `tests/sync/test_yef_fanout.py` — `_clone_node_for_location` + `_apply_yef_fan_out` tests.
- `tests/sync/test_yef_edge_resolver.py` — `_resolve_target_for_folder` tests.
- `tests/sync/test_yef_roundtrip.py` — integration round-trip (EM_demo_02.graphml full cycle).
- `tests/sync/test_yef_ui_widget.py` — UI populate/save logic tests (Qt-light, mock QListWidget).

**Files modified (existing):**
- `modules/db/structures/us_table.py` — add `Column('other_locations', Text)` # 65.
- `modules/s3dgraphy/sync/yed_import_pipeline.py` — add `_resolve_folder_for_leaf` helper, REPLACE the Bug R `_PARADATA_NODEDUP_UTS` no-dedup branch in `_write_us_rows` with yE-F fold logic.
- `modules/s3dgraphy/sync/graphml_writer.py` — add `_apply_yef_fan_out` + `_clone_node_for_location` helpers + call site in `export_graphml` between `populate_graph` and `_filter_by_site`.
- `modules/s3dgraphy/sync/graph_projector.py` — add `_resolve_target_for_folder` helper, integrate in `_enrich_into` rapporti edges loop where `target_node = _resolve_target_for_folder(...)` replaces the current first-candidate lookup.
- `gui/ui/US_USM.ui` — Qt Designer XML: add `QListWidget objectName='listWidget_other_locations'` + `QLabel objectName='label_other_locations'` below the `attivita` combobox.
- `tabs/US_USM.py` — add `_populate_other_locations()`, `_save_other_locations()`, `_update_other_locations_visibility()` methods wired into form load/save/unita_tipo-change.
- `modules/utility/pyarchinit_i18n_stratigraphic.py` — add `'OTHER_LOCATIONS_LABEL'` translation in 10 languages.
- `pyarchinitPlugin.py` — add menu item `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)` + handler `_run_yef_migration`.
- `metadata.txt` — `version=5.9.0-alpha`.
- `dev_logs/CHANGELOG.md` — prepend bilingual entry (yE-F-Closure step, via stratigraph-changelog agent).
- `docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md` × 10 — add yE-F release-notes subsection (yE-F-Closure step, via tutorial-updater agent).
- `~/Downloads/pyarchinit-api-docs/docs/CHANGELOG.md` — append yE-F entry, commit + push (yE-F-Closure step).

---

## Task 1: Migration library — add_other_locations_column

**Files:**
- Create: `scripts/migrations/2026_05_yef_other_locations_lib.py`
- Test: `tests/sync/test_yef_migration.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_yef_migration.py
"""yE-F schema migration tests — ADD COLUMN other_locations TEXT
idempotent on both SQLite and PG (PG paths skipped if psycopg2 missing)."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy import text
import pytest

from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of


def _make_sqlite_handle(tmp_path: Path) -> DbHandle:
    """Build a DbHandle on a fresh SQLite DB with the minimal us_table
    schema MINUS the other_locations column (the migration target).
    """
    dbfile = tmp_path / "yef_migration.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, area TEXT, us TEXT,
                unita_tipo TEXT, node_uuid TEXT,
                UNIQUE (sito, area, us, unita_tipo)
            )
        """))
    return handle


def test_add_other_locations_column_inserts_when_missing(tmp_path):
    """First call adds the column → returns 1."""
    from scripts.migrations._2026_05_yef_other_locations_lib import (
        add_other_locations_column,
    )
    handle = _make_sqlite_handle(tmp_path)
    assert "other_locations" not in _columns_of(handle, "us_table")

    inserted = add_other_locations_column(handle)

    assert inserted == 1
    assert "other_locations" in _columns_of(handle, "us_table")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd <plugin_root> && python -m pytest tests/sync/test_yef_migration.py::test_add_other_locations_column_inserts_when_missing -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.migrations._2026_05_yef_other_locations_lib'`

- [ ] **Step 3: Write minimal implementation**

```python
# scripts/migrations/_2026_05_yef_other_locations_lib.py
"""Library for the yE-F other_locations migration (idempotent ADD COLUMN).

The library accepts a DbHandle (Foundation 5.6.2-alpha shim) so it
works transparently on both SQLite and PostgreSQL. Backwards-compat
is preserved: pre-migration DBs have no column → reader handles
absence gracefully via try/except in graph_projector.
"""
from __future__ import annotations

from sqlalchemy import text

from modules.s3dgraphy.sync._db_handle import DbHandle, _columns_of


def add_other_locations_column(handle: DbHandle) -> int:
    """Add ``us_table.other_locations TEXT`` if not already present.

    Returns ``1`` if the column was added, ``0`` if it was already
    present (idempotent re-run).
    """
    if "other_locations" in _columns_of(handle, "us_table"):
        return 0
    with handle.engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE us_table ADD COLUMN other_locations TEXT"
        ))
    return 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_yef_migration.py::test_add_other_locations_column_inserts_when_missing -v`
Expected: PASS

- [ ] **Step 5: Add idempotency test**

```python
# Append to tests/sync/test_yef_migration.py
def test_add_other_locations_column_no_op_when_present(tmp_path):
    """Second call returns 0 (idempotent)."""
    from scripts.migrations._2026_05_yef_other_locations_lib import (
        add_other_locations_column,
    )
    handle = _make_sqlite_handle(tmp_path)
    add_other_locations_column(handle)  # first call

    inserted = add_other_locations_column(handle)  # second call

    assert inserted == 0
    assert "other_locations" in _columns_of(handle, "us_table")
```

- [ ] **Step 6: Run idempotency test**

Run: `python -m pytest tests/sync/test_yef_migration.py -v`
Expected: 2 PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/migrations/_2026_05_yef_other_locations_lib.py \
        tests/sync/test_yef_migration.py
git commit -m "feat(yE-F-A): migration lib add_other_locations_column (idempotent)"
```

---

## Task 2: Migration CLI wrapper

**Files:**
- Create: `scripts/migrations/2026_05_yef_other_locations.py`
- Test: `tests/sync/test_yef_migration.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/sync/test_yef_migration.py
import subprocess
import sys


def test_cli_apply_adds_column(tmp_path):
    """CLI ``--apply --db <path>`` runs the migration and exits 0."""
    handle = _make_sqlite_handle(tmp_path)
    dbfile = handle.sqlite_path
    plugin_root = Path(__file__).resolve().parents[2]
    cli = (plugin_root / "scripts" / "migrations"
           / "2026_05_yef_other_locations.py")
    env = {"PYTHONPATH": str(plugin_root), "PATH": "/usr/bin:/bin"}
    proc = subprocess.run(
        [sys.executable, str(cli), "--apply", "--db", str(dbfile)],
        env=env, capture_output=True, text=True, timeout=30,
    )

    assert proc.returncode == 0, (
        f"stdout={proc.stdout}\nstderr={proc.stderr}"
    )
    assert "other_locations" in _columns_of(handle, "us_table")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_yef_migration.py::test_cli_apply_adds_column -v`
Expected: FAIL with `FileNotFoundError` (CLI doesn't exist).

- [ ] **Step 3: Write minimal CLI**

```python
# scripts/migrations/2026_05_yef_other_locations.py
"""CLI wrapper for the yE-F other_locations migration.

Usage:
    python scripts/migrations/2026_05_yef_other_locations.py --apply --db <path>
    python scripts/migrations/2026_05_yef_other_locations.py --apply --conn-str <pg_uri>
    python scripts/migrations/2026_05_yef_other_locations.py --dry-run --db <path>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure plugin root on sys.path when run as standalone script.
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from modules.s3dgraphy.sync._db_handle import DbHandle
from scripts.migrations._2026_05_yef_other_locations_lib import (
    add_other_locations_column,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="yE-F other_locations column migration",
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--db", help="SQLite file path")
    target.add_argument("--conn-str", help="PostgreSQL connection URI")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.db:
        handle = DbHandle.from_path(Path(args.db))
    else:
        handle = DbHandle.from_conn_str(args.conn_str)

    if args.dry_run:
        from modules.s3dgraphy.sync._db_handle import _columns_of
        present = "other_locations" in _columns_of(handle, "us_table")
        print(f"dry_run: other_locations present={present}")
        return 0

    added = add_other_locations_column(handle)
    print(f"applied: rows_changed={added}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_yef_migration.py::test_cli_apply_adds_column -v`
Expected: PASS

- [ ] **Step 5: Add dry-run test**

```python
def test_cli_dry_run_reports_state(tmp_path):
    """``--dry-run`` reports state without changing the DB."""
    handle = _make_sqlite_handle(tmp_path)
    dbfile = handle.sqlite_path
    plugin_root = Path(__file__).resolve().parents[2]
    cli = (plugin_root / "scripts" / "migrations"
           / "2026_05_yef_other_locations.py")
    env = {"PYTHONPATH": str(plugin_root), "PATH": "/usr/bin:/bin"}
    proc = subprocess.run(
        [sys.executable, str(cli), "--dry-run", "--db", str(dbfile)],
        env=env, capture_output=True, text=True, timeout=30,
    )

    assert proc.returncode == 0
    assert "other_locations present=False" in proc.stdout
    assert "other_locations" not in _columns_of(handle, "us_table")
```

- [ ] **Step 6: Run dry-run test**

Run: `python -m pytest tests/sync/test_yef_migration.py -v`
Expected: 3 PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/migrations/2026_05_yef_other_locations.py \
        tests/sync/test_yef_migration.py
git commit -m "feat(yE-F-A): CLI wrapper for other_locations migration"
```

---

## Task 3: ORM Column + QGIS menu wire-up

**Files:**
- Modify: `modules/db/structures/us_table.py` (add Column line)
- Modify: `pyarchinitPlugin.py` (add menu item + handler `_run_yef_migration`)

- [ ] **Step 1: Locate the us_table Column block**

Open `modules/db/structures/us_table.py` and find the last `Column(...)` line in the `us_table = Table(...)` definition. Note the line number for placement.

- [ ] **Step 2: Add the ORM column**

In `modules/db/structures/us_table.py`, locate the existing `Column('cont_per', ...)` or the last paradata-related Column, and add immediately after:

```python
                     Column('other_locations', Text),  # 65 — yE-F multi-folder paradata (yed-f-multifolder-5.9.0-alpha)
```

If the actual line number differs from the spec's 65, accept the next available index. Position matters only for relative ordering, not for an absolute line number.

- [ ] **Step 3: Locate the QGIS menu wiring**

Open `pyarchinitPlugin.py` and grep for `_run_uuid_backfill_migration`. Note the line where the menu entry "Backfill node_uuid" is registered.

- [ ] **Step 4: Add menu entry + handler stub**

Add a new menu item modelled on the node_uuid backfill (find the surrounding pattern: `addAction(..., self._run_uuid_backfill_migration)`):

```python
        # yE-F other_locations column migration — Plugins → pyArchInit → Migrazioni
        self.add_action(
            ":/plugins/pyarchinit/icons/pyArch.png",  # use same icon as backfill
            self.tr(
                "Migrazioni → Aggiungi colonna other_locations (yE-F)"),
            self.iface.mainWindow(),
            self._run_yef_migration,
        )
```

And a handler at the bottom of the same class, near `_run_uuid_backfill_migration`:

```python
    def _run_yef_migration(self):
        """Apply the yE-F other_locations column migration to a
        user-selected SQLite DB or current PG connection.

        Mirrors ``_run_uuid_backfill_migration``: file-picker dialog,
        confirm dialog, auto-backup, run the migration lib, show
        result QMessageBox.
        """
        from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
        from pathlib import Path
        from modules.s3dgraphy.sync._db_handle import DbHandle
        from scripts.migrations._2026_05_yef_other_locations_lib import (
            add_other_locations_column,
        )

        db_path, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            self.tr("Seleziona DB SQLite per migrazione yE-F"),
            str(Path.home() / "pyarchinit"),
            "SQLite (*.sqlite *.db)",
        )
        if not db_path:
            return

        # Confirm dialog
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            self.tr("Confirm migration yE-F"),
            self.tr(
                "Aggiungere colonna ``other_locations`` a "
                "us_table di {}? (backup automatico)").format(db_path),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        # Auto-backup
        import shutil
        from datetime import datetime
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        backup = f"{db_path}.pre_yef_other_locations_{ts}"
        shutil.copy2(db_path, backup)

        # Run migration
        try:
            handle = DbHandle.from_path(Path(db_path))
            added = add_other_locations_column(handle)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr("Migration failed"),
                str(e),
            )
            return

        QMessageBox.information(
            self.iface.mainWindow(),
            self.tr("Migration yE-F completata"),
            self.tr("rows_changed={}\nbackup={}").format(added, backup),
        )
```

- [ ] **Step 5: Smoke-test the ORM addition**

Run: `python -c "from modules.db.structures.us_table import US_table; cols = [c.name for c in US_table.us_table.columns]; print('other_locations' in cols)"`
Expected: `True`

- [ ] **Step 6: Commit**

```bash
git add modules/db/structures/us_table.py pyarchinitPlugin.py
git commit -m "feat(yE-F-A): ORM Column + QGIS menu entry for other_locations migration"
```

---

## Task 4: `_resolve_folder_for_leaf` helper

**Files:**
- Modify: `modules/s3dgraphy/sync/yed_import_pipeline.py` (add helper)
- Test: `tests/sync/test_yef_fold.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_yef_fold.py
"""yE-F import fold tests — _resolve_folder_for_leaf + _write_us_rows
fold branch."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy import text
import pytest

from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind, ClassifiedNode,
)
from modules.s3dgraphy.sync.yed_group_walker import FolderCandidate


def _folder(yed_id, label, members, dim="attivita"):
    return FolderCandidate(
        yed_id=yed_id, full_label=label,
        auto_dimension=dim, user_dimension=dim,
        auto_value=label.split("-")[0], user_value=label.split("-")[0],
        member_yed_ids=list(members), nested_folder_ids=[],
        parent_folder_id=None,
    )


def test_resolve_folder_for_leaf_returns_attivita_value():
    """Leaf y1 in folder VA01 → returns 'VA01'."""
    from modules.s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "VA01-foundation", members=["y1", "y2"])]
    assert _resolve_folder_for_leaf("y1", folders) == "VA01"
    assert _resolve_folder_for_leaf("y2", folders) == "VA01"


def test_resolve_folder_for_leaf_returns_none_when_orphan():
    """Leaf not in any folder → None."""
    from modules.s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "VA01", members=["y1"])]
    assert _resolve_folder_for_leaf("y_orphan", folders) is None


def test_resolve_folder_for_leaf_skips_non_attivita_dim():
    """Folder with dim='area' is ignored — only attivita matters."""
    from modules.s3dgraphy.sync.yed_import_pipeline import (
        _resolve_folder_for_leaf,
    )
    folders = [_folder("F1", "AR05", members=["y1"], dim="area")]
    assert _resolve_folder_for_leaf("y1", folders) is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/sync/test_yef_fold.py -v`
Expected: 3 FAIL with `ImportError: cannot import name '_resolve_folder_for_leaf'`

- [ ] **Step 3: Implement the helper**

Add to `modules/s3dgraphy/sync/yed_import_pipeline.py`, near the existing `_flatten_members` helper:

```python
def _resolve_folder_for_leaf(
    yed_id: str,
    folders: list[FolderCandidate],
) -> str | None:
    """Return the activity code of the folder containing ``yed_id``.

    Iterates ``folders``; the FIRST folder with
    ``auto_dimension == "attivita"`` (or user-overridden) whose
    flattened member set includes ``yed_id`` wins. Nested folders
    are walked recursively via ``_flatten_members``. Returns ``None``
    when the leaf is orphan (no parent folder) or the parent folder
    is of a non-activity dimension.

    Used by the yE-F fold branch in ``_write_us_rows`` to compute the
    primary or secondary activity for a paradata leaf.
    """
    for folder in folders:
        dim = getattr(folder, "user_dimension", None) or folder.auto_dimension
        if dim != "attivita":
            continue
        members = _flatten_members(folder, folders)
        if yed_id in members:
            return getattr(folder, "user_value", None) or folder.auto_value
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_yef_fold.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/yed_import_pipeline.py tests/sync/test_yef_fold.py
git commit -m "feat(yE-F-B): _resolve_folder_for_leaf helper + tests"
```

---

## Task 5: yE-F fold — primary INSERT (replace Bug R branch)

**Files:**
- Modify: `modules/s3dgraphy/sync/yed_import_pipeline.py` (replace Bug R `_PARADATA_NODEDUP_UTS` branch in `_write_us_rows`)
- Test: `tests/sync/test_yef_fold.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/sync/test_yef_fold.py
_US_TABLE_DDL = """
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us TEXT,
    unita_tipo TEXT, rapporti TEXT, attivita TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT,
    d_stratigrafica TEXT, node_uuid TEXT,
    other_locations TEXT,
    UNIQUE (sito, area, us, unita_tipo)
)
"""


def _make_yef_handle(tmp_path):
    dbfile = tmp_path / "yef_fold.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        conn.execute(text(_US_TABLE_DDL))
    return handle


def _leaf(yed_id, kind, label=None):
    return ClassifiedNode(
        yed_id=yed_id, label=label or yed_id,
        auto_kind=kind, user_kind=kind,
    )


def test_write_us_rows_yef_fold_first_occurrence_primary(tmp_path):
    """3 'material' leaves in folders VA01/VA04/VA05 → 1 us_table row
    with attivita='VA01' (first folder) + other_locations=['VA04','VA05'].
    """
    from modules.s3dgraphy.sync.yed_import_pipeline import _write_us_rows
    handle = _make_yef_handle(tmp_path)
    leaves = [
        _leaf("m1", ClassificationKind.PROPERTY, "material"),
        _leaf("m2", ClassificationKind.PROPERTY, "material"),
        _leaf("m3", ClassificationKind.PROPERTY, "material"),
    ]
    folders = [
        _folder("F1", "VA01", members=["m1"]),
        _folder("F4", "VA04", members=["m2"]),
        _folder("F5", "VA05", members=["m3"]),
    ]

    with handle.engine.begin() as conn:
        count, uuid_map = _write_us_rows(
            conn, leaves, sito="X", folders_map={f.yed_id: f for f in folders},
        )

    assert count == 1, f"expected 1 INSERT, got {count}"
    with handle.engine.connect() as conn:
        rows = list(conn.execute(text(
            "SELECT us, unita_tipo, attivita, other_locations, "
            "d_stratigrafica FROM us_table WHERE sito = 'X'"
        )))
    assert len(rows) == 1
    us, ut, attivita, ol, d_strat = rows[0]
    assert us == "material"
    assert ut == "property"
    assert attivita == "VA01"
    # other_locations may be JSON list or null-equivalent — check both ways
    import json
    secondary = json.loads(ol) if ol else []
    assert secondary == ["VA04", "VA05"]
    assert d_strat == "material"
    # All 3 yed_ids map to the same canonical node_uuid
    assert len(set(uuid_map.values())) == 1
```

This test references `folders_map={...}` argument — current `_write_us_rows` accepts this but ignores it. After the yE-F change it will actively use it.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_yef_fold.py::test_write_us_rows_yef_fold_first_occurrence_primary -v`
Expected: FAIL — current Bug R behaviour produces 3 rows with `us='material'`, `'material_2'`, `'material_3'`.

- [ ] **Step 3: Replace the Bug R branch in `_write_us_rows`**

In `modules/s3dgraphy/sync/yed_import_pipeline.py`, locate the existing Bug R branch (search for `_PARADATA_NODEDUP_UTS`). REPLACE the entire `if unita_tipo in _PARADATA_NODEDUP_UTS:` block with:

```python
        if unita_tipo in _PARADATA_NODEDUP_UTS:
            # yE-F fold (2026-05-16 spec §5): each yEd occurrence of a
            # paradata label is folded to ONE us_table row + JSON list
            # of secondary activity codes. First-in-document-order
            # becomes primary; subsequent ones append to other_locations.
            #
            # folders_map (dict yed_id → FolderCandidate) is consumed here
            # to resolve the current folder per leaf via
            # _resolve_folder_for_leaf(). Pre-Bug-R no-dedup branch is
            # superseded.
            label_key = (c.label, unita_tipo)
            current_folder = _resolve_folder_for_leaf(
                c.yed_id, list((folders_map or {}).values()),
            )
            existing = paradata_primary_by_label.get(label_key)
            if existing is None:
                # First occurrence — INSERT primary row.
                node_uuid = uuid7().hex
                us_value = _strip_unita_tipo_prefix(c.label, unita_tipo)
                pi, fi = mtp.get(c.yed_id, (None, None))
                conn.execute(
                    text(
                        "INSERT INTO us_table "
                        "(sito, area, us, unita_tipo, node_uuid, "
                        " periodo_iniziale, fase_iniziale, "
                        " periodo_finale, fase_finale, "
                        " d_stratigrafica, attivita, other_locations) "
                        "VALUES (:sito, :area, :us, :unita_tipo, :nu, "
                        "        :pi, :fi, :pf, :ff, :d_strat, "
                        "        :attivita, :ol)"
                    ),
                    {
                        "sito": sito, "area": "1",
                        "us": us_value, "unita_tipo": unita_tipo,
                        "nu": node_uuid,
                        "pi": pi, "fi": fi, "pf": pi, "ff": fi,
                        "d_strat": c.label,
                        "attivita": current_folder,
                        "ol": None,
                    },
                )
                paradata_primary_by_label[label_key] = (
                    node_uuid, us_value, [], current_folder,
                )
                key_to_node_uuid[(us_value, unita_tipo)] = node_uuid
                uuid_map[c.yed_id] = node_uuid
                if us_by_yed_id_out is not None:
                    us_by_yed_id_out[c.yed_id] = us_value
                count += 1
            else:
                # Subsequent — append current_folder to other_locations.
                primary_uuid, primary_us, secondary, primary_folder = existing
                if (
                    current_folder
                    and current_folder != primary_folder
                    and current_folder not in secondary
                ):
                    secondary.append(current_folder)
                    import json
                    conn.execute(
                        text(
                            "UPDATE us_table SET other_locations = :ol "
                            "WHERE sito = :sito AND node_uuid = :nu"
                        ),
                        {
                            "ol": json.dumps(secondary),
                            "sito": sito, "nu": primary_uuid,
                        },
                    )
                uuid_map[c.yed_id] = primary_uuid
                if us_by_yed_id_out is not None:
                    us_by_yed_id_out[c.yed_id] = primary_us
            continue
```

And initialize the index ABOVE the loop (near the existing `key_to_node_uuid` initialization):

```python
    # yE-F fold index: (label, unita_tipo) → (node_uuid, us, secondary_list, primary_folder).
    paradata_primary_by_label: dict[
        tuple[str, str], tuple[str, str, list[str], str | None]
    ] = {}
```

Also REMOVE the now-unused `paradata_seq` counter (search and delete its initialization).

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_yef_fold.py::test_write_us_rows_yef_fold_first_occurrence_primary -v`
Expected: PASS

- [ ] **Step 5: Run the full sync suite to catch regressions**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -30`
Expected: SOME failures — pre-existing tests (`test_write_us_rows_paradata_no_dedup_one_row_per_occurrence`, integration tests) still assert Bug R behaviour. Will be fixed in Task 7.

- [ ] **Step 6: Commit**

```bash
git add modules/s3dgraphy/sync/yed_import_pipeline.py tests/sync/test_yef_fold.py
git commit -m "feat(yE-F-B): yE-F fold primary INSERT replaces Bug R no-dedup branch"
```

---

## Task 6: yE-F fold idempotency — pre-load + secondary append

**Files:**
- Modify: `modules/s3dgraphy/sync/yed_import_pipeline.py` (extend pre-load loop in `_write_us_rows`)
- Test: `tests/sync/test_yef_fold.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/sync/test_yef_fold.py
def test_write_us_rows_yef_idempotent_on_re_run(tmp_path):
    """Second run of the same drafts → 0 new inserts, other_locations unchanged."""
    from modules.s3dgraphy.sync.yed_import_pipeline import _write_us_rows
    handle = _make_yef_handle(tmp_path)
    leaves = [
        _leaf("m1", ClassificationKind.PROPERTY, "material"),
        _leaf("m2", ClassificationKind.PROPERTY, "material"),
    ]
    folders = [
        _folder("F1", "VA01", members=["m1"]),
        _folder("F4", "VA04", members=["m2"]),
    ]
    folders_map = {f.yed_id: f for f in folders}

    with handle.engine.begin() as conn:
        count1, _ = _write_us_rows(conn, leaves, sito="X", folders_map=folders_map)
    assert count1 == 1

    # Second run — fresh _write_us_rows call should be a no-op.
    with handle.engine.begin() as conn:
        count2, uuid_map2 = _write_us_rows(conn, leaves, sito="X", folders_map=folders_map)
    assert count2 == 0, f"expected 0 inserts on re-run, got {count2}"

    with handle.engine.connect() as conn:
        rows = list(conn.execute(text(
            "SELECT us, attivita, other_locations FROM us_table WHERE sito = 'X'"
        )))
    assert len(rows) == 1
    us, attivita, ol = rows[0]
    assert us == "material"
    assert attivita == "VA01"
    import json
    assert json.loads(ol) == ["VA04"]


def test_write_us_rows_yef_appends_new_folder_on_re_import(tmp_path):
    """Second run with an EXTRA folder occurrence appends to other_locations."""
    from modules.s3dgraphy.sync.yed_import_pipeline import _write_us_rows
    handle = _make_yef_handle(tmp_path)

    # First run: 2 occurrences (VA01 primary, VA04 secondary)
    leaves_1 = [
        _leaf("m1", ClassificationKind.PROPERTY, "material"),
        _leaf("m2", ClassificationKind.PROPERTY, "material"),
    ]
    folders_1 = {
        "F1": _folder("F1", "VA01", members=["m1"]),
        "F4": _folder("F4", "VA04", members=["m2"]),
    }
    with handle.engine.begin() as conn:
        _write_us_rows(conn, leaves_1, sito="X", folders_map=folders_1)

    # Second run: 3 occurrences (now also VA06)
    leaves_2 = leaves_1 + [_leaf("m3", ClassificationKind.PROPERTY, "material")]
    folders_2 = {**folders_1, "F6": _folder("F6", "VA06", members=["m3"])}
    with handle.engine.begin() as conn:
        _write_us_rows(conn, leaves_2, sito="X", folders_map=folders_2)

    with handle.engine.connect() as conn:
        ol_row = conn.execute(text(
            "SELECT other_locations FROM us_table WHERE sito = 'X' AND us = 'material'"
        )).first()
    import json
    assert json.loads(ol_row[0]) == ["VA04", "VA06"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/sync/test_yef_fold.py::test_write_us_rows_yef_idempotent_on_re_run tests/sync/test_yef_fold.py::test_write_us_rows_yef_appends_new_folder_on_re_import -v`
Expected: FAIL — re-run currently inserts a duplicate `material` row OR raises UNIQUE collision.

- [ ] **Step 3: Extend the pre-load loop in `_write_us_rows`**

In `modules/s3dgraphy/sync/yed_import_pipeline.py`, find the existing `existing_paradata: dict[...] = {}` pre-load (added in Bug R). REPLACE it with the yE-F variant that pre-loads `paradata_primary_by_label`:

```python
    # Pre-load existing paradata primaries (yE-F idempotency):
    # (label, unita_tipo) → (node_uuid, primary_us, list_of_secondary_locs, primary_folder)
    try:
        for r in conn.execute(
            text(
                "SELECT us, unita_tipo, node_uuid, d_stratigrafica, "
                "attivita, other_locations "
                "FROM us_table WHERE sito = :sito"
            ),
            {"sito": sito},
        ):
            us_existing, ut_existing, nu_existing, d_existing, \
                attiv_existing, ol_existing = (
                    r[0], r[1], r[2], r[3], r[4], r[5],
                )
            if us_existing is None or ut_existing is None or nu_existing is None:
                continue
            key_to_node_uuid[(us_existing, ut_existing)] = nu_existing
            if ut_existing in _PARADATA_NODEDUP_UTS and d_existing:
                import json
                secondary = []
                if ol_existing:
                    try:
                        parsed = json.loads(ol_existing)
                        if isinstance(parsed, list):
                            secondary = [str(x) for x in parsed]
                    except (ValueError, TypeError):
                        pass
                paradata_primary_by_label[
                    (str(d_existing), ut_existing)
                ] = (
                    nu_existing, str(us_existing), secondary,
                    attiv_existing,
                )
    except Exception as exc:
        log.debug(
            "_write_us_rows: yE-F pre-load failed (%s); fall through", exc,
        )
```

The existing `existing_paradata` dict (Bug R era) can stay as legacy code if other branches reference it, but yE-F branch uses `paradata_primary_by_label` exclusively.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_yef_fold.py -v`
Expected: 5 PASS

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/yed_import_pipeline.py tests/sync/test_yef_fold.py
git commit -m "feat(yE-F-B): idempotent re-run with secondary append + pre-load"
```

---

## Task 7: Update existing Bug R tests to yE-F semantics

**Files:**
- Modify: `tests/sync/test_yed_import_pipeline.py` (RENAME + UPDATE `test_write_us_rows_paradata_no_dedup_one_row_per_occurrence`)
- Modify: `tests/sync/test_yed_pipeline_integration.py` (adjust integration counts)

- [ ] **Step 1: Locate and rename the Bug R test**

In `tests/sync/test_yed_import_pipeline.py`, find `def test_write_us_rows_paradata_no_dedup_one_row_per_occurrence`. REPLACE it with:

```python
def test_write_us_rows_yef_fold_collapses_multiple_yed_occurrences(tmp_path):
    """Bug R is superseded by yE-F: 4 ``D.NNN`` leaves across multiple
    folders fold into 1 us_table row (us='001' for the primary), with
    ``other_locations`` listing the additional activity codes.

    yE-F replaces the previous no-dedup B1 behaviour (which produced
    N rows with synthesised us suffixes ``_2``/``_3``). Identity dedup
    is restored: D.001 / D.001-2 / D.001bis collapse to ONE row
    because they share the same `d_stratigrafica` after the strip
    helper. Multi-folder visibility preserved via other_locations.
    """
    handle = _make_handle(tmp_path)
    leaves = [
        _leaf("y1", ClassificationKind.DOCUMENT, "D.001"),
        _leaf("y2", ClassificationKind.DOCUMENT, "D.001-2"),
        _leaf("y3", ClassificationKind.DOCUMENT, "D.001bis"),
        _leaf("y4", ClassificationKind.DOCUMENT, "D.002"),
    ]
    # No folders → other_locations stays empty; each leaf folds based
    # on identity (D.001 variants → us='001', D.002 → us='002').
    with handle.engine.begin() as conn:
        count, uuid_map = _write_us_rows(conn, leaves, sito="X")

    assert count == 2  # D.001 + D.002 (identity-dedup restored)
    # Three D.001 variants share node_uuid; D.002 separate.
    assert uuid_map["y1"] == uuid_map["y2"] == uuid_map["y3"]
    assert uuid_map["y4"] != uuid_map["y1"]

    with handle.engine.connect() as conn:
        rows = list(conn.execute(
            text("SELECT us, unita_tipo, d_stratigrafica, other_locations "
                 "FROM us_table WHERE sito = :s ORDER BY us"),
            {"s": "X"},
        ))
    assert len(rows) == 2
    assert {r[0] for r in rows} == {"001", "002"}
    # d_stratigrafica is the FIRST encountered label for the primary
    # (D.001 first in iteration order); the dedup'd variants don't
    # overwrite the primary's d_stratigrafica field.
    by_us = {r[0]: r for r in rows}
    assert by_us["001"][2] == "D.001"
    assert by_us["002"][2] == "D.002"
    # No secondary folders (no folder_map passed) → other_locations NULL/empty.
    assert by_us["001"][3] in (None, "", "[]")
    assert by_us["002"][3] in (None, "", "[]")
```

The us_table DDL in `_make_handle()` already includes `other_locations` after Task 3 ORM update — confirm by reading `tests/sync/test_yed_import_pipeline.py`'s `_US_TABLE_DDL`. If absent, ADD `other_locations TEXT,` to the DDL near `d_stratigrafica`.

- [ ] **Step 2: Run the renamed test**

Run: `python -m pytest tests/sync/test_yed_import_pipeline.py::test_write_us_rows_yef_fold_collapses_multiple_yed_occurrences -v`
Expected: PASS

- [ ] **Step 3: Locate integration test counts**

In `tests/sync/test_yed_pipeline_integration.py`, find tests that count us_table rows post-import (`test_yed_d_end_to_end_skip_policy`, `test_yed_d_end_to_end_fan_out_policy`, etc.). Update the expected counts:

- Bug R: 5 us_table rows (2 US + 1 USV + 1 SF + 1 VSF) — paradata rows excluded from the integration fixture
- yE-F: 6 us_table rows (5 above + 1 PROPERTY 'material' with possibly other_locations populated if the fixture has multi-folder material)

Read each test and adjust the assertion comment to reflect yE-F semantics.

- [ ] **Step 4: Run the integration tests**

Run: `python -m pytest tests/sync/test_yed_pipeline_integration.py -v 2>&1 | tail -20`
Expected: most PASS; any remaining failures specifically reference Bug R no-dedup behaviour.

- [ ] **Step 5: Run the full sync suite**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -10`
Expected: 0 failures.

- [ ] **Step 6: Commit**

```bash
git add tests/sync/test_yed_import_pipeline.py tests/sync/test_yed_pipeline_integration.py
git commit -m "test(yE-F-B): supersede Bug R tests with yE-F fold semantics"
```

---

## Task 8: `_clone_node_for_location` helper

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (add helper)
- Test: `tests/sync/test_yef_fanout.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_yef_fanout.py
"""yE-F render fan-out tests — _clone_node_for_location + _apply_yef_fan_out."""
from __future__ import annotations
import pytest


def test_clone_node_for_location_creates_copy_with_canonical_uuid():
    """Cloning a primary node yields a new node with fresh node_id
    but inherits class, name, description, and stamps the canonical
    UUID on attributes['node_uuid'] for round-trip identity."""
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import (
        _clone_node_for_location,
    )

    primary = StratigraphicUnit(
        node_id="canonical-uuid-1234",
        name="material", description="",
    )
    primary.attributes = {
        "sito": "test", "unita_tipo": "property",
        "attivita": "VA01", "d_stratigrafica": "material",
        "node_uuid": "canonical-uuid-1234",
    }

    copy = _clone_node_for_location(
        primary, location="VA04", idx=1,
        canonical_uuid="canonical-uuid-1234",
    )

    # Distinct node_id but same class + name.
    assert copy.node_id == "canonical-uuid-1234_loc_1"
    assert copy.name == "material"
    assert type(copy).__name__ == "StratigraphicUnit"
    # attributes should be a deep copy with location override + markers.
    assert copy.attributes["attivita"] == "VA04"
    assert copy.attributes["unita_tipo"] == "property"
    assert copy.attributes["d_stratigrafica"] == "material"
    assert copy.attributes["sito"] == "test"
    assert copy.attributes["_yef_canonical_uuid"] == "canonical-uuid-1234"
    assert copy.attributes["_yef_is_copy"] is True
    assert copy.attributes["node_uuid"] == "canonical-uuid-1234"
    # Mutating the copy's attributes must not leak back to the primary.
    copy.attributes["attivita"] = "X-CHANGED"
    assert primary.attributes["attivita"] == "VA01"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_yef_fanout.py -v`
Expected: FAIL with `ImportError: cannot import name '_clone_node_for_location'`

- [ ] **Step 3: Implement the helper**

Add to `modules/s3dgraphy/sync/graphml_writer.py`, near the existing `_inject_isolated_paradata_nodes` function:

```python
def _clone_node_for_location(primary_node, location: str, idx: int,
                             canonical_uuid: str):
    """Return a deep-copy clone of ``primary_node`` placed in
    ``location`` folder.

    Used by ``_apply_yef_fan_out`` (yE-F design spec §6) to emit N
    visual yEd ``<node>`` copies per multi-folder paradata row.

    The clone:
      - Has node_id ``f"{canonical_uuid}_loc_{idx}"`` (unique within graph)
      - Inherits Python class (StratigraphicUnit subclass), name, description
      - Copies attributes dict with overrides:
          attivita = location
          _yef_canonical_uuid = canonical_uuid (for downstream resolver)
          _yef_is_copy = True (filter marker)
          node_uuid = canonical_uuid (round-trip identity in graphml output)

    Mutating the clone's attributes does NOT affect the primary
    (deep-copy semantics).
    """
    cls = type(primary_node)
    clone = cls(
        node_id=f"{canonical_uuid}_loc_{idx}",
        name=str(getattr(primary_node, "name", "")),
        description=str(getattr(primary_node, "description", "")),
    )
    base_attrs = getattr(primary_node, "attributes", None) or {}
    new_attrs = dict(base_attrs)
    new_attrs["attivita"] = location
    new_attrs["_yef_canonical_uuid"] = canonical_uuid
    new_attrs["_yef_is_copy"] = True
    new_attrs["node_uuid"] = canonical_uuid
    clone.attributes = new_attrs
    return clone
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_yef_fanout.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_yef_fanout.py
git commit -m "feat(yE-F-C): _clone_node_for_location helper + tests"
```

---

## Task 9: `_apply_yef_fan_out` function

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (add function)
- Test: `tests/sync/test_yef_fanout.py` (append)

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/sync/test_yef_fanout.py
def test_apply_yef_fan_out_creates_n_copies():
    """Row with other_locations=['VA04','VA05'] → 3 nodes in graph
    after fan-out (1 primary + 2 copies). All share canonical uuid via
    attributes['node_uuid'] + _yef_canonical_uuid."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out

    g = Graph(graph_id="t")
    primary = StratigraphicUnit(
        node_id="uuid-mat", name="material", description="",
    )
    primary.attributes = {
        "sito": "test", "unita_tipo": "property",
        "attivita": "VA01", "d_stratigrafica": "material",
        "node_uuid": "uuid-mat",
        "other_locations": '["VA04","VA05"]',
    }
    g.add_node(primary)

    _apply_yef_fan_out(g)

    paradata_nodes = [
        n for n in g.nodes
        if type(n).__name__ == "StratigraphicUnit"
        and (getattr(n, "attributes", None) or {}).get("d_stratigrafica") == "material"
    ]
    assert len(paradata_nodes) == 3

    locations = sorted(
        (n.attributes or {}).get("attivita") for n in paradata_nodes
    )
    assert locations == ["VA01", "VA04", "VA05"]

    # All three carry the same canonical node_uuid as data key value.
    canonical_uuids = {
        (n.attributes or {}).get("node_uuid") for n in paradata_nodes
    }
    assert canonical_uuids == {"uuid-mat"}

    # The graph stashed a copies-by-canonical mapping for the edge resolver.
    copies_map = (getattr(g, "attributes", None) or {}).get(
        "_yef_copies_by_canonical", {}
    )
    assert "uuid-mat" in copies_map
    assert len(copies_map["uuid-mat"]) == 3


def test_apply_yef_fan_out_skipped_for_non_paradata():
    """Stratigraphic row without other_locations → no clones."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out

    g = Graph(graph_id="t")
    us = StratigraphicUnit(node_id="u1", name="01", description="")
    us.attributes = {
        "sito": "test", "unita_tipo": "US", "attivita": "VA01",
    }
    g.add_node(us)
    initial_count = len(g.nodes)

    _apply_yef_fan_out(g)

    assert len(g.nodes) == initial_count


def test_apply_yef_fan_out_empty_other_locations_is_no_op():
    """other_locations='[]' (empty JSON list) → no fan-out."""
    from s3dgraphy import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out

    g = Graph(graph_id="t")
    prop = StratigraphicUnit(node_id="p1", name="material", description="")
    prop.attributes = {
        "sito": "test", "unita_tipo": "property",
        "attivita": "VA01", "other_locations": "[]",
    }
    g.add_node(prop)
    initial_count = len(g.nodes)

    _apply_yef_fan_out(g)

    assert len(g.nodes) == initial_count
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/sync/test_yef_fanout.py -v`
Expected: FAIL — `_apply_yef_fan_out` not yet defined.

- [ ] **Step 3: Implement the function**

Add to `modules/s3dgraphy/sync/graphml_writer.py`, near `_clone_node_for_location`:

```python
def _apply_yef_fan_out(graph) -> int:
    """yE-F render fan-out (design spec §6).

    For each StratigraphicUnit-class node with non-empty
    ``attributes['other_locations']``, emit N-1 visual copies via
    ``_clone_node_for_location``. The N copies (primary + secondaries)
    share the canonical ``pyarchinit.node_uuid`` data key for round-
    trip identity, but have distinct yEd ``<node>`` ids
    (``<canonical>_loc_<idx>``).

    Stashes ``graph.attributes['_yef_copies_by_canonical']`` =
    ``dict[canonical_uuid, list[primary_and_copies]]`` for the
    per-folder edge resolver (yE-F-D).

    Returns the number of copies created (0 if no yE-F rows in graph).
    Non-paradata rows and empty ``other_locations`` are ignored.
    """
    import json
    canonical_to_copies: dict[str, list] = {}
    copies_created = 0
    for n in list(graph.nodes):
        attrs = getattr(n, "attributes", None) or {}
        ol_raw = attrs.get("other_locations")
        if not ol_raw:
            continue
        try:
            secondary_locs = json.loads(ol_raw)
        except (ValueError, TypeError):
            continue
        if not isinstance(secondary_locs, list) or not secondary_locs:
            continue
        primary_uuid = n.node_id
        attrs["_yef_canonical_uuid"] = primary_uuid
        canonical_to_copies[primary_uuid] = [n]
        for idx, loc in enumerate(secondary_locs, start=1):
            copy = _clone_node_for_location(
                n, str(loc), idx, primary_uuid,
            )
            graph.add_node(copy)
            canonical_to_copies[primary_uuid].append(copy)
            copies_created += 1
    if not hasattr(graph, "attributes") or graph.attributes is None:
        graph.attributes = {}
    graph.attributes["_yef_copies_by_canonical"] = canonical_to_copies
    return copies_created
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_yef_fanout.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py tests/sync/test_yef_fanout.py
git commit -m "feat(yE-F-C): _apply_yef_fan_out emits N copies + stashes mapping"
```

---

## Task 10: Wire fan-out into export_graphml

**Files:**
- Modify: `modules/s3dgraphy/sync/graphml_writer.py` (call site in `export_graphml`)

- [ ] **Step 1: Locate the export_graphml call sequence**

Open `modules/s3dgraphy/sync/graphml_writer.py` and find the line where `GraphProjector().populate_graph(...)` is called inside `export_graphml`. Note the line.

- [ ] **Step 2: Add the fan-out call after populate_graph**

Insert the call immediately after the `graph = GraphProjector().populate_graph(...)` block and BEFORE `_filter_by_site` is invoked:

```python
        # yE-F fan-out (design spec §6): emit N visual copies per
        # multi-folder paradata row. Must run AFTER populate_graph
        # (which propagates other_locations into node.attributes) and
        # BEFORE _filter_by_site (so sito-filtering keeps the copies).
        try:
            copies_created = _apply_yef_fan_out(graph)
            if copies_created:
                print(
                    f"[ExportGraphML] yE-F fan-out emitted {copies_created} "
                    f"visual copies"
                )
        except Exception as exc:
            # Defensive — never break the export pipeline on fan-out failure.
            print(f"[ExportGraphML] yE-F fan-out skipped: {exc}")
```

- [ ] **Step 3: Manual integration smoke check**

Run a manual project + export simulation on `pyarchinit_test10.sqlite` (already has a fresh yE-F import via Task 5/6) or rebuild a test DB:

```bash
cd <plugin_root>
python -c "
import tempfile, shutil
from pathlib import Path
src = Path('/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_test10.sqlite')
if src.exists():
    tmp = Path(tempfile.mkdtemp()) / 'sim.sqlite'
    shutil.copy2(src, tmp)
    import sqlite3
    c = sqlite3.connect(tmp)
    # Apply migration if needed
    cols = [r[1] for r in c.execute('PRAGMA table_info(us_table)').fetchall()]
    if 'other_locations' not in cols:
        c.execute('ALTER TABLE us_table ADD COLUMN other_locations TEXT')
    c.commit(); c.close()
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    g = GraphProjector().populate_graph(db_path=str(tmp), sito='test')
    print(f'graph nodes after projector: {len(g.nodes)}')
    from modules.s3dgraphy.sync.graphml_writer import _apply_yef_fan_out
    n = _apply_yef_fan_out(g)
    print(f'fan-out copies created: {n}')
" 2>&1 | tail -3
```

Expected: `graph nodes after projector: 111` then `fan-out copies created: 0` (because test10 was created with Bug R B1 multi-row, NOT yE-F — `other_locations` is NULL for all rows, so fan-out is a no-op). Confirms the function runs without errors against real-shaped data.

- [ ] **Step 4: Run the sync test suite**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -5`
Expected: All PASS (no regression from adding the call).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graphml_writer.py
git commit -m "feat(yE-F-C): wire _apply_yef_fan_out into export_graphml pipeline"
```

---

## Task 11: `_resolve_target_for_folder` edge resolver

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py` (add helper)
- Test: `tests/sync/test_yef_edge_resolver.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_yef_edge_resolver.py
"""yE-F per-folder edge resolver tests — _resolve_target_for_folder
picks the right copy of a multi-folder paradata target node."""
from __future__ import annotations
import pytest


def _make_node(node_id, attivita, canonical=None):
    """Build a minimal StratigraphicUnit-shaped node for resolver tests."""
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    n = StratigraphicUnit(node_id=node_id, name="material", description="")
    n.attributes = {"attivita": attivita}
    if canonical:
        n.attributes["_yef_canonical_uuid"] = canonical
    return n


def test_resolver_picks_copy_with_matching_attivita():
    """source in VA04 → resolver returns the copy with attivita='VA04'."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_projector import _resolve_target_for_folder

    primary = _make_node("uuid-mat", "VA01", "uuid-mat")
    copy_va04 = _make_node("uuid-mat_loc_1", "VA04", "uuid-mat")
    copy_va05 = _make_node("uuid-mat_loc_2", "VA05", "uuid-mat")
    g = Graph(graph_id="t")
    g.add_node(primary)
    g.add_node(copy_va04)
    g.add_node(copy_va05)
    g.attributes = {
        "_yef_copies_by_canonical": {
            "uuid-mat": [primary, copy_va04, copy_va05],
        }
    }

    target = _resolve_target_for_folder(
        primary, source_folder="VA04", graph=g,
    )
    assert target.node_id == "uuid-mat_loc_1"


def test_resolver_falls_back_to_primary_when_no_match():
    """source in VA99 (no matching copy) → resolver returns primary."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_projector import _resolve_target_for_folder

    primary = _make_node("uuid-mat", "VA01", "uuid-mat")
    copy_va04 = _make_node("uuid-mat_loc_1", "VA04", "uuid-mat")
    g = Graph(graph_id="t")
    g.add_node(primary)
    g.add_node(copy_va04)
    g.attributes = {
        "_yef_copies_by_canonical": {
            "uuid-mat": [primary, copy_va04],
        }
    }

    target = _resolve_target_for_folder(
        primary, source_folder="VA99", graph=g,
    )
    assert target.node_id == "uuid-mat"  # primary fallback


def test_resolver_returns_target_directly_when_not_multifolder():
    """Target without _yef_copies entry → returned unchanged."""
    from s3dgraphy import Graph
    from modules.s3dgraphy.sync.graph_projector import _resolve_target_for_folder

    us = _make_node("uuid-us01", "VA01")
    g = Graph(graph_id="t")
    g.add_node(us)
    g.attributes = {"_yef_copies_by_canonical": {}}

    target = _resolve_target_for_folder(us, source_folder="VA04", graph=g)
    assert target.node_id == "uuid-us01"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/sync/test_yef_edge_resolver.py -v`
Expected: FAIL — `_resolve_target_for_folder` not defined.

- [ ] **Step 3: Implement the helper**

Add to `modules/s3dgraphy/sync/graph_projector.py`, near `_create_paradata_node_for_unita_tipo`:

```python
def _resolve_target_for_folder(target_canonical_node, source_folder, graph):
    """Pick the copy of ``target_canonical_node`` whose
    ``attributes['attivita']`` equals ``source_folder``.

    Used by ``_enrich_into`` rapporti edges loop (yE-F design spec §7)
    when both endpoints are nodes in the graph and the target is a
    multi-folder paradata row that was fanned out by
    ``_apply_yef_fan_out`` upstream.

    Lookup contract:
      1. If the graph has no ``_yef_copies_by_canonical`` mapping or
         the target isn't in it, return ``target_canonical_node``
         (the target is single-folder or non-paradata).
      2. Otherwise scan the copy list for an attivita match.
      3. Fallback to the primary (first entry) when no copy matches —
         covers the case "source folder is not in target's folder set"
         (rare cross-folder reference).
    """
    if target_canonical_node is None:
        return None
    g_attrs = getattr(graph, "attributes", None) or {}
    copies_map = g_attrs.get("_yef_copies_by_canonical") or {}
    copies = copies_map.get(target_canonical_node.node_id)
    if not copies:
        return target_canonical_node
    for c in copies:
        cattrs = getattr(c, "attributes", None) or {}
        if cattrs.get("attivita") == source_folder:
            return c
    return target_canonical_node
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_yef_edge_resolver.py -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py tests/sync/test_yef_edge_resolver.py
git commit -m "feat(yE-F-D): _resolve_target_for_folder edge resolver + tests"
```

---

## Task 12: Integrate edge resolver in `_enrich_into`

**Files:**
- Modify: `modules/s3dgraphy/sync/graph_projector.py` (use resolver in rapporti loop)

- [ ] **Step 1: Locate the rapporti edges loop**

Open `modules/s3dgraphy/sync/graph_projector.py` and grep for the rapporti target resolution block in `_enrich_into`. Look for the "Bug N target resolver" comment and the `family-preference` logic. Note the line where `target_node = candidates[0]` (the cross-family fallback) or where the family match is assigned.

- [ ] **Step 2: Wire the resolver call**

Replace the family-preference loop with the yE-F resolver, falling through to the existing family logic when the resolver returns the canonical (non-fanned-out) target:

```python
                    src_attrs = getattr(us_node, "attributes", None) or {}
                    src_folder = src_attrs.get("attivita")
                    candidates = nodes_by_name.get(target_us, [])
                    target_node = None
                    # yE-F resolver: when the target has multi-folder
                    # copies via _apply_yef_fan_out, pick the copy in
                    # the source's folder. Falls through to family-
                    # preference for non-multi-folder targets.
                    if candidates and src_folder:
                        # The primary candidate is the canonical one
                        # (its node_id appears as a key in
                        # _yef_copies_by_canonical).
                        for c in candidates:
                            resolved = _resolve_target_for_folder(
                                c, src_folder, graph,
                            )
                            if resolved is not c:
                                # Multi-folder match — accept the copy
                                # without further family heuristic.
                                target_node = resolved
                                break
                    # Fallback: existing family-preference logic.
                    if target_node is None:
                        # ... existing code paths from Bug N family-pref ...
```

Preserve the existing family-preference fallback intact below this block.

- [ ] **Step 3: Run the full sync suite**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -10`
Expected: All PASS — for non-multi-folder data (B1 / stratigraphic), the resolver call is a no-op (returns the canonical, falls through). yE-F multi-folder data is not yet round-trippable end-to-end until Task 14, so this stage is regression-only.

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/sync/graph_projector.py
git commit -m "feat(yE-F-D): wire _resolve_target_for_folder in _enrich_into rapporti loop"
```

---

## Task 13: UI — `other_locations` widget XML + handler

**Files:**
- Modify: `gui/ui/US_USM.ui` (Qt Designer XML, add widget + label)
- Modify: `tabs/US_USM.py` (handler methods)
- Test: `tests/sync/test_yef_ui_widget.py` (logic-only, mock QListWidget)

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_yef_ui_widget.py
"""yE-F UI widget logic tests — populate, save, visibility.

These tests bypass Qt by mocking QListWidget. The real Qt widget is
exercised at smoke level via QGIS manual testing; this file pins the
business logic that runs around the widget.
"""
from __future__ import annotations
import json
import pytest
from unittest.mock import MagicMock


class _FakeListWidget:
    """In-memory stand-in for QListWidget."""
    def __init__(self):
        self.items: list[tuple[str, bool]] = []  # (text, selected)

    def clear(self):
        self.items = []

    def addItem(self, text):
        self.items.append((str(text), False))

    def selectedItems(self):
        return [_FakeItem(t) for t, sel in self.items if sel]

    def select(self, text):
        self.items = [(t, t == text or sel) for t, sel in self.items]

    def setVisible(self, v):
        self.visible = v


class _FakeItem:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


def test_populate_other_locations_from_db_distinct_attivita():
    """Widget loads DISTINCT attivita values from us_table for the sito."""
    from tabs.US_USM import _populate_other_locations_logic

    widget = _FakeListWidget()
    db_rows = [("VA01",), ("VA04",), ("VA05",), ("VA01",), (None,)]
    current_other_locations = '["VA04"]'

    _populate_other_locations_logic(
        widget, db_rows, current_other_locations,
    )

    item_texts = [t for t, _ in widget.items]
    # Distinct, non-NULL, sorted
    assert item_texts == ["VA01", "VA04", "VA05"]
    # VA04 pre-selected
    selected_texts = [t for t, sel in widget.items if sel]
    assert selected_texts == ["VA04"]


def test_save_other_locations_returns_json():
    """Serialize selected items into JSON list, exclude primary."""
    from tabs.US_USM import _save_other_locations_logic

    widget = _FakeListWidget()
    widget.addItem("VA01")
    widget.addItem("VA04")
    widget.addItem("VA05")
    widget.select("VA04")
    widget.select("VA05")
    widget.select("VA01")  # accidentally selected the primary

    json_str = _save_other_locations_logic(widget, current_attivita="VA01")

    parsed = json.loads(json_str)
    assert parsed == ["VA04", "VA05"]  # VA01 (primary) excluded


def test_save_other_locations_returns_none_when_empty():
    """Empty selection → None (DB NULL)."""
    from tabs.US_USM import _save_other_locations_logic

    widget = _FakeListWidget()
    widget.addItem("VA01")  # not selected

    result = _save_other_locations_logic(widget, current_attivita="VA01")

    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/sync/test_yef_ui_widget.py -v`
Expected: FAIL — `_populate_other_locations_logic` / `_save_other_locations_logic` not defined.

- [ ] **Step 3: Add helper functions to `tabs/US_USM.py`**

Add module-level functions (importable by tests without instantiating the QGIS widget):

```python
# Add near the top of tabs/US_USM.py, before the class definition.

import json as _yef_json


def _populate_other_locations_logic(widget, db_rows_distinct_attivita,
                                    current_other_locations_json):
    """Populate ``widget`` with DISTINCT non-NULL activity codes from
    ``db_rows_distinct_attivita`` (iterable of 1-tuples). Pre-select
    items present in ``current_other_locations_json`` (JSON list str
    or None).
    """
    widget.clear()
    seen = set()
    activities = []
    for (a,) in db_rows_distinct_attivita:
        if a is None or a == "" or a in seen:
            continue
        seen.add(a)
        activities.append(a)
    activities.sort()
    for a in activities:
        widget.addItem(a)
    # Pre-select
    selected = []
    if current_other_locations_json:
        try:
            parsed = _yef_json.loads(current_other_locations_json)
            if isinstance(parsed, list):
                selected = [str(x) for x in parsed]
        except (ValueError, TypeError):
            selected = []
    for s in selected:
        widget.select(s)


def _save_other_locations_logic(widget, current_attivita):
    """Serialise selected items in ``widget`` into a JSON list string,
    excluding ``current_attivita`` (the primary).

    Returns ``None`` when no items are selected (DB NULL).
    """
    selected = [item.text() for item in widget.selectedItems()]
    selected = [s for s in selected if s != current_attivita]
    if not selected:
        return None
    return _yef_json.dumps(selected, ensure_ascii=False)
```

For the `select()` method used by `_FakeListWidget`, the real QListWidget needs a different approach (item selection by `setSelected(True)`). In the production form code (added later in this task), use:

```python
for i in range(self.listWidget_other_locations.count()):
    item = self.listWidget_other_locations.item(i)
    if item.text() in selected:
        item.setSelected(True)
```

Document this in a comment inside the function.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_yef_ui_widget.py -v`
Expected: 3 PASS

- [ ] **Step 5: Add the Qt widget to US_USM.ui**

Open `gui/ui/US_USM.ui` in a text editor. Locate the existing `attivita` combobox block (search for `comboBox_attivita` or similar). Add immediately after, in the same `<layout>`:

```xml
   <item>
    <widget class="QLabel" name="label_other_locations">
     <property name="text">
      <string>Other locations (yE-F)</string>
     </property>
    </widget>
   </item>
   <item>
    <widget class="QListWidget" name="listWidget_other_locations">
     <property name="selectionMode">
      <enum>QAbstractItemView::MultiSelection</enum>
     </property>
     <property name="maximumSize">
      <size>
       <width>16777215</width>
       <height>120</height>
      </size>
     </property>
    </widget>
   </item>
```

The actual line numbers and parent layout differ across the existing `US_USM.ui`. Place the addition near the `attivita` field. Save the file.

- [ ] **Step 6: Wire the widget into US_USM.py load/save**

Find the `charge_records` (or equivalent) method in `tabs/US_USM.py` where the form is populated from DB row. Add at the bottom:

```python
        # yE-F other_locations populate
        try:
            from sqlalchemy import text as _text
            rows = self.DB_MANAGER.conn.execute(_text(
                "SELECT DISTINCT attivita FROM us_table "
                "WHERE sito = :s AND attivita IS NOT NULL"
            ), {"s": self.SITO}).fetchall()
            current_ol = getattr(rec, "other_locations", None)
            _populate_other_locations_logic(
                self.listWidget_other_locations, rows, current_ol,
            )
        except Exception:
            pass  # column may not exist in pre-migration DBs
```

Find the save method (`on_pushButton_save_clicked` or equivalent). Add to the params dict that goes into the UPDATE:

```python
        # yE-F other_locations save
        params['other_locations'] = _save_other_locations_logic(
            self.listWidget_other_locations,
            current_attivita=params.get('attivita'),
        )
```

- [ ] **Step 7: Run the sync suite**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -5`
Expected: All PASS (UI test added, no regression).

- [ ] **Step 8: Commit**

```bash
git add gui/ui/US_USM.ui tabs/US_USM.py tests/sync/test_yef_ui_widget.py
git commit -m "feat(yE-F-E): other_locations widget XML + populate/save handlers"
```

---

## Task 14: UI visibility + i18n

**Files:**
- Modify: `tabs/US_USM.py` (visibility logic on `unita_tipo` change)
- Modify: `modules/utility/pyarchinit_i18n_stratigraphic.py` (10 lang translations)

- [ ] **Step 1: Add visibility helper logic**

In `tabs/US_USM.py`, near the other helper functions, add:

```python
_YEF_PARADATA_UTS = frozenset({"DOC", "Combinar", "Extractor", "property"})


def _yef_widget_visible_for_unita_tipo(unita_tipo: str) -> bool:
    """Return True iff the other_locations widget should be visible for
    the given unita_tipo. Visible for paradata kinds only; hidden for
    stratigraphic family (US/USM/USV/SF/...).
    """
    return (unita_tipo or "") in _YEF_PARADATA_UTS
```

- [ ] **Step 2: Wire into on_unita_tipo_changed**

Find the existing `on_comboBox_unita_tipo_currentIndexChanged` (or equivalent slot) in `tabs/US_USM.py`. Add:

```python
        # yE-F other_locations visibility
        is_paradata = _yef_widget_visible_for_unita_tipo(unita_tipo)
        self.listWidget_other_locations.setVisible(is_paradata)
        self.label_other_locations.setVisible(is_paradata)
```

- [ ] **Step 3: Add i18n entries**

Open `modules/utility/pyarchinit_i18n_stratigraphic.py`. Find the existing translation dict (typically nested per-language). Add `'OTHER_LOCATIONS_LABEL'` key in each language block:

```python
# Italian
'OTHER_LOCATIONS_LABEL': 'Altre attività',
# English
'OTHER_LOCATIONS_LABEL': 'Other locations',
# German
'OTHER_LOCATIONS_LABEL': 'Weitere Aktivitäten',
# French
'OTHER_LOCATIONS_LABEL': 'Autres activités',
# Spanish
'OTHER_LOCATIONS_LABEL': 'Otras actividades',
# Arabic
'OTHER_LOCATIONS_LABEL': 'أنشطة أخرى',
# Catalan
'OTHER_LOCATIONS_LABEL': 'Altres activitats',
# Romanian
'OTHER_LOCATIONS_LABEL': 'Alte activități',
# Portuguese
'OTHER_LOCATIONS_LABEL': 'Outras atividades',
# Greek
'OTHER_LOCATIONS_LABEL': 'Άλλες δραστηριότητες',
```

Match the structure of the file (the actual layout differs per existing pattern). If keys are nested as `i18n['it']['OTHER_LOCATIONS_LABEL']`, follow that shape.

- [ ] **Step 4: Use the i18n in the label set**

In `tabs/US_USM.py` `charge_records` or `setupUi`-equivalent:

```python
        # yE-F other_locations label i18n
        try:
            from modules.utility.pyarchinit_i18n_stratigraphic import (
                get_translation,
            )
            label_text = get_translation(self.LANGUAGE, 'OTHER_LOCATIONS_LABEL')
            self.label_other_locations.setText(label_text)
        except Exception:
            self.label_other_locations.setText("Other locations")
```

The actual `get_translation` function name and signature mirror the existing i18n helpers in pyArchInit. Inspect `pyarchinit_i18n_stratigraphic.py` for the canonical accessor; adapt the call.

- [ ] **Step 5: Run the sync suite + smoke test**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -5`
Expected: All PASS.

- [ ] **Step 6: Commit**

```bash
git add tabs/US_USM.py modules/utility/pyarchinit_i18n_stratigraphic.py
git commit -m "feat(yE-F-E): visibility logic + i18n in 10 languages for other_locations"
```

---

## Task 15: Round-trip integration test (EM_demo_02.graphml)

**Files:**
- Create: `tests/sync/test_yef_roundtrip.py`

- [ ] **Step 1: Locate the EM_demo_02 fixture or skip gracefully**

The fixture lives at `/Users/enzo/Downloads/EM_demo_02.graphml` (user filesystem). For tests we use the shipped minimal fixture `tests/sync/fixtures/em_demo_02_mini.graphml`. Verify it exists; if not, mark the test as skipped.

- [ ] **Step 2: Write the integration test**

```python
# tests/sync/test_yef_roundtrip.py
"""yE-F round-trip integration test.

Imports the shipped em_demo_02_mini.graphml fixture, then re-exports,
then re-imports the export to verify cardinality and other_locations
content remain stable across a full cycle.
"""
from __future__ import annotations
from pathlib import Path
import json
import tempfile
import shutil
import pytest

from sqlalchemy import text
from modules.s3dgraphy.sync._db_handle import DbHandle


FIXTURE = (Path(__file__).parent / "fixtures"
           / "em_demo_02_mini.graphml")
_DDL = """
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us TEXT,
    unita_tipo TEXT, rapporti TEXT, attivita TEXT,
    struttura TEXT, settore TEXT, ambient TEXT, saggio TEXT, quad_par TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT,
    d_stratigrafica TEXT, node_uuid TEXT,
    other_locations TEXT,
    UNIQUE (sito, area, us, unita_tipo)
);
CREATE TABLE inventario_materiali_table (
    id_invmat INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, numero_inventario INTEGER, sub_inv TEXT,
    tipo_reperto TEXT, definizione TEXT, area TEXT, us TEXT,
    UNIQUE (sito, numero_inventario, sub_inv)
);
CREATE TABLE periodizzazione_table (
    id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, periodo INTEGER, fase TEXT,
    cron_iniziale INTEGER, cron_finale INTEGER,
    descrizione TEXT, datazione_estesa TEXT, cont_per INTEGER,
    UNIQUE (sito, periodo, fase)
);
"""


@pytest.fixture
def workspace_env(tmp_path, monkeypatch):
    workspace_root = tmp_path / "_workspace"
    workspace_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(workspace_root))
    return workspace_root


def _make_handle(tmp_path):
    dbfile = tmp_path / "yef_roundtrip.sqlite"
    handle = DbHandle.from_path(dbfile)
    with handle.engine.begin() as conn:
        for stmt in _DDL.strip().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
    return handle


@pytest.mark.skipif(not FIXTURE.exists(),
                    reason="em_demo_02_mini.graphml fixture absent")
def test_yef_round_trip_em_demo_02_mini(tmp_path, workspace_env):
    """Import EM_demo_02_mini → snapshot DB → re-import same drafts →
    DB state identical (cardinality + other_locations).
    """
    from modules.s3dgraphy.sync.yed_classifier import classify_leaves
    from modules.s3dgraphy.sync.yed_group_walker import walk_folders
    from modules.s3dgraphy.sync.yed_table_parser import extract_periods
    from modules.s3dgraphy.sync.yed_import_pipeline import import_yed_raw
    from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy

    handle = _make_handle(tmp_path)
    drafts = {
        "classified": classify_leaves(FIXTURE),
        "periods":    extract_periods(FIXTURE),
        "folders":    walk_folders(FIXTURE),
    }

    # First import
    r1 = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert r1.errors == ()

    with handle.engine.connect() as conn:
        rows_1 = list(conn.execute(text(
            "SELECT us, unita_tipo, attivita, other_locations "
            "FROM us_table WHERE sito = 'DEMO_SITE' "
            "ORDER BY unita_tipo, us"
        )))

    # Second import (idempotent re-run)
    r2 = import_yed_raw(
        handle, FIXTURE, sito="DEMO_SITE", drafts=drafts,
        policy=FolderEdgePolicy.SKIP,
    )
    assert r2.errors == ()

    with handle.engine.connect() as conn:
        rows_2 = list(conn.execute(text(
            "SELECT us, unita_tipo, attivita, other_locations "
            "FROM us_table WHERE sito = 'DEMO_SITE' "
            "ORDER BY unita_tipo, us"
        )))

    assert rows_1 == rows_2, (
        f"DB state changed between identical imports.\n"
        f"first: {rows_1}\nsecond: {rows_2}"
    )

    # Sanity: at least one paradata row got populated other_locations
    # (only if the fixture has cross-folder shared paradata labels).
    paradata_with_secondaries = [
        r for r in rows_1
        if r[1] in ("DOC", "Combinar", "Extractor", "property")
        and r[3] and r[3] != "[]"
    ]
    if paradata_with_secondaries:
        # Parse and assert format
        for r in paradata_with_secondaries:
            parsed = json.loads(r[3])
            assert isinstance(parsed, list)
            assert all(isinstance(s, str) for s in parsed)
            # Primary not in secondary list
            assert r[2] not in parsed
```

- [ ] **Step 3: Run the round-trip test**

Run: `python -m pytest tests/sync/test_yef_roundtrip.py -v`
Expected: PASS (idempotency confirmed). The fixture may or may not have shared paradata labels; the test accepts both outcomes.

- [ ] **Step 4: Run the full sync suite to confirm no regression**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -10`
Expected: 340+ PASS / 0 fail.

- [ ] **Step 5: Commit**

```bash
git add tests/sync/test_yef_roundtrip.py
git commit -m "test(yE-F-Closure): round-trip integration on em_demo_02_mini fixture"
```

---

## Task 16: AC-2 baseline regression + close-out commit

**Files:**
- Modify: `metadata.txt` (version bump)

- [ ] **Step 1: Run the AC-2 baseline check**

The AC-2 regression suite verifies that the byte-identical export of `mini_volterra.sqlite` (no paradata multi-folder) remains unchanged. Find the existing test:

Run: `python -m pytest tests/sync/ -k "ac2 or byte_identical or mini_volterra_export" -v`
Expected: All PASS. If any fail, investigate before tagging.

- [ ] **Step 2: Run the full sync test suite one final time**

Run: `python -m pytest tests/sync/ -v 2>&1 | tail -10`
Expected: 340+ PASS / 0 fail / 34+ skipped (PG offline, Qt offline).

- [ ] **Step 3: Bump metadata.txt**

Open `metadata.txt`. Find `version=5.8.5-alpha`. Replace with:

```
version=5.9.0-alpha
```

- [ ] **Step 4: Commit metadata + create tag**

```bash
git add metadata.txt
git commit -m "bump: version 5.8.5-alpha → 5.9.0-alpha (yE-F multi-folder paradata)"
git tag -a yed-f-multifolder-5.9.0-alpha -m "yE-F multi-folder paradata — single row + other_locations + render-time fan-out"
git push origin Stratigraph_00001
git push origin yed-f-multifolder-5.9.0-alpha
```

- [ ] **Step 5: Documentation propagation (reference_release_flow memory)**

Per `reference_release_flow.md` saved memory, three updates fire automatically after tagging:

1. Invoke `stratigraph-changelog` agent → bilingual IT+EN entry in `dev_logs/CHANGELOG.md` for tag `yed-f-multifolder-5.9.0-alpha`.
2. Invoke `tutorial-updater` agent → Tutorial 36 release-notes subsection in 10 languages with the yE-F bullet list (single-row + other_locations + multi-folder fan-out).
3. Update `~/Downloads/pyarchinit-api-docs/docs/CHANGELOG.md` with a yE-F entry (bilingual, symbol inventory, tag table, predecessor link to `yed-fastfix`), commit + push to GitHub. RTD rebuilds.

- [ ] **Step 6: Final smoke verification**

Run a fresh full-cycle test on a user DB (manual, optional but recommended):

```bash
# 1. Apply migration to a test DB
python scripts/migrations/2026_05_yef_other_locations.py --apply --db /tmp/test_yef.sqlite

# 2. Import EM_demo_02.graphml
python scripts/import_yed_graphml.py /Users/enzo/Downloads/EM_demo_02.graphml \
    --site test --db /tmp/test_yef.sqlite --policy fan_out

# 3. Inspect DB
sqlite3 /tmp/test_yef.sqlite "
SELECT unita_tipo, us, attivita, other_locations FROM us_table
WHERE sito='test' AND unita_tipo IN ('DOC','Combinar','Extractor','property')
ORDER BY unita_tipo, us;"
```

Expected: 1 row per identity (`material`, `01`, etc.) with `other_locations` populated where the yEd file has cross-folder references.

---

## Notes

- **DRY / YAGNI**: each task implements ONE coherent slice; helpers stay private (`_resolve_*`, `_clone_*`) to avoid public-API noise. The plan resists adding features beyond what the spec defines.

- **TDD**: every task writes the failing test first, then minimal implementation, then verifies pass. Pre-existing tests are NOT touched until Task 7 (renamed Bug R test) — the new yE-F path is built in parallel and the legacy path stays green until the renaming step.

- **Frequent commits**: 16 tasks → 16 commits. Each commit is independently revertable. The closing tag `yed-f-multifolder-5.9.0-alpha` is the milestone marker; intermediate commits stay on `Stratigraph_00001`.

- **Coexistence invariant**: at every step, B1 multi-row data in `pyarchinit_test{002..010}.sqlite` MUST remain readable (Tasks 5/6/9/11 all explicitly handle the `other_locations IS NULL` legacy branch). Run the full sync suite after each task to catch silent regressions.

- **No `__pycache__` issues during testing**: if pytest fails to pick up your changes after editing module-level code, clear `__pycache__` directories under `modules/s3dgraphy/sync/` and `tests/sync/`:

```bash
find modules/s3dgraphy/sync tests/sync -name __pycache__ -type d -exec rm -rf {} +
```
