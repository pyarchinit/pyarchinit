"""L0 smoke test for ParadataManagerDialog: dialog instantiates
without crash and has 3 tabs. Skipped if Qt is not available."""
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


@pytest.mark.skipif(not _qt_available(),
                    reason="QGIS Qt not available")
def test_paradata_dialog_can_open(tmp_path):
    """Dialog instantiates with 3 tabs and doesn't crash on
    _load_data()."""
    from qgis.PyQt.QtWidgets import QApplication
    if QApplication.instance() is None:
        QApplication([])

    # Stub db_manager
    class _FakeDBManager:
        def __init__(self, db):
            self._db = db
        def get_sqlite_path(self):
            return self._db

    # Make a real tmp DB
    import sqlite3
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id INT, sito TEXT)")
    conn.commit(); conn.close()

    from gui.dialog_paradata_manager import ParadataManagerDialog
    dialog = ParadataManagerDialog(
        parent=None, db_manager=_FakeDBManager(db), sito="X")
    assert dialog.tabs.count() == 3
    assert dialog.tabs.tabText(0).lower() == "authors"
    assert dialog.tabs.tabText(1).lower() == "licenses"
    assert dialog.tabs.tabText(2).lower() == "embargoes"
