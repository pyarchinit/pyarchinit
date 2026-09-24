"""Period and phase of the US sheet: values chosen, not typed (2026-09-24).

The list of those boxes comes from the Periodizzazione sheet, so nothing
else should end up in them; they were editable only because the sheet
wrote the value of the record with setEditText(), which does nothing on
a combo box that is not editable. Now the value is selected — and a
value the list does not have (a period renamed or removed, a database
whose Periodizzazione was never filled in) is added to the list, so the
sheet keeps showing it and saving the record does not wipe it.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.combo_value import show_value  # noqa: E402

_US_USM = (_ROOT / "tabs" / "US_USM.py").read_text(encoding="utf-8")
_COMBOS = ("comboBox_per_iniz", "comboBox_fas_iniz", "comboBox_per_fin", "comboBox_fas_fin")


@pytest.fixture(scope="module")
def qgs():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from qgis.core import QgsApplication
    except ImportError:
        pytest.skip("QGIS not available")
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


def _combo(qgs, items=("1", "2", "3")):
    from qgis.PyQt.QtWidgets import QComboBox
    combo = QComboBox()
    combo.addItems(list(items))
    return combo


def test_the_value_of_the_record_is_shown(qgs):
    combo = _combo(qgs)
    assert show_value(combo, "2") is True
    assert combo.currentText() == "2" and combo.currentIndex() == 1


def test_a_number_is_shown_like_the_list_writes_it(qgs):
    combo = _combo(qgs)
    assert show_value(combo, 3) is True          # periodo salvato come intero
    assert combo.currentText() == "3" and combo.count() == 3


def test_a_value_the_list_does_not_have_is_kept(qgs):
    # the database of a site whose Periodizzazione was never filled in
    combo = _combo(qgs, items=())
    assert show_value(combo, "5") is True
    assert combo.currentText() == "5", "il periodo del record andrebbe perso salvando"
    assert combo.count() == 1


def test_an_empty_value_leaves_the_box_empty(qgs):
    combo = _combo(qgs)
    assert show_value(combo, None) is False
    assert combo.currentText() == "" and combo.currentIndex() == -1
    assert show_value(combo, "") is False
    assert combo.currentText() == ""


def test_showing_a_value_does_not_wake_the_handlers_of_the_box(qgs):
    # they recompute the dating from Periodizzazione: a record nobody
    # touched would come out modified, and ask to be saved
    combo = _combo(qgs)
    woken = []
    combo.currentIndexChanged.connect(lambda *_: woken.append("index"))
    combo.currentTextChanged.connect(lambda *_: woken.append("text"))
    show_value(combo, "2")
    show_value(combo, "fuori elenco")
    show_value(combo, None)
    assert woken == []
    assert combo.currentText() == ""


def test_the_four_boxes_are_no_longer_opened_to_free_typing():
    for name in _COMBOS:
        assert 'setComboBoxEditable(["self.%s"]' % name not in _US_USM, name


def test_the_sheet_shows_those_values_by_choosing_them():
    for name in _COMBOS:
        assert not re.search(r'self\.%s\.setEditText' % name, _US_USM), name
        assert 'show_value(self.%s,' % name in _US_USM, name
