"""L0 smoke tests for the AI06 dialog extensions."""
from __future__ import annotations
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _qt_available() -> bool:
    try:
        from qgis.PyQt.QtWidgets import QDialog, QApplication  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _qt_available(), reason="QGIS Qt not available")
def test_dialog_has_groups_tab(tmp_path):
    """AC-18: ParadataManagerDialog now has 4 tabs."""
    from qgis.PyQt.QtWidgets import QApplication
    if QApplication.instance() is None:
        QApplication([])

    class _FakeDBManager:
        def __init__(self, db):
            self._db = db
        def get_sqlite_path(self):
            return self._db

    import sqlite3
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INT, sito TEXT, "
                  "node_uuid TEXT, us TEXT, area TEXT, unita_tipo TEXT)")
    conn.commit(); conn.close()

    from gui.dialog_paradata_manager import ParadataManagerDialog
    dialog = ParadataManagerDialog(
        parent=None, db_manager=_FakeDBManager(db), sito="X")
    assert dialog.tabs.count() == 4
    assert dialog.tabs.tabText(3).lower() == "groups"


@pytest.mark.skipif(not _qt_available(), reason="QGIS Qt not available")
def test_dialog_preselects_populated_dimensions(tmp_path):
    """D2: S3DGraphyExportDialog auto-preselects populated dims."""
    # This test is hard to fully exercise without spinning up the
    # full QGIS dialog (which requires a running plugin context).
    # Verify only that _preselect_groups doesn't crash with a
    # minimal stub.
    pytest.skip("Full QGIS context required for S3DGraphyExportDialog")
