"""Regression tests for the rapporti stratigrafici QTableWidget round-trip
(tabs/US_USM.py): loading a record must REPLACE the table content, and
saving must never persist all-blank rows such as ['', '', '', ''].

Bug report 2026-08-20 (master 4.9.9): US 1 accumulated 78 674 blank rows
because tableInsertData removed at most 4 rows before reloading, and
table2dict(preserve_empty=True) turned the leftover rows into blanks that
were then saved on "Il record e' stato modificato. Vuoi salvare?".

The real methods are extracted from tabs/US_USM.py via AST and bound to a
stub object holding a real QTableWidget, so the test exercises production
code without importing qgis.
"""
import ast
import os
import textwrap
import warnings

import pytest

pytest.importorskip("PyQt5")
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem  # noqa: E402

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
US_USM = os.path.join(PLUGIN_DIR, 'tabs', 'US_USM.py')

US1 = "[['Copre', '2', '', ''], ['Copre', '5', '', '']]"
US_SIX = str([['Copre', str(n), '', ''] for n in range(2, 8)])
BLANK = ['', '', '', '']


def _extract_methods(*names):
    src = open(US_USM, encoding='utf-8').read()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', SyntaxWarning)  # pre-existing regex escapes in US_USM.py
        tree = ast.parse(src)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'pyarchinit_US':
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in names:
                    found[item.name] = textwrap.dedent(ast.get_source_segment(src, item))
    missing = set(names) - set(found)
    assert not missing, f"metodi non trovati in US_USM.py: {missing}"
    ns = {'ast': ast, 'QTableWidgetItem': QTableWidgetItem}
    for name in names:
        exec(found[name], ns)
    return {name: ns[name] for name in names}


@pytest.fixture(scope='module')
def qapp():
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    return QApplication.instance() or QApplication([])


@pytest.fixture
def form(qapp):
    methods = _extract_methods('table2dict', 'tableInsertData')

    class Form:
        def __init__(self):
            self.tableWidget_rapporti = QTableWidget(0, 4)

        def load(self, rapporti_str):
            methods['tableInsertData'](self, 'self.tableWidget_rapporti', rapporti_str)

        def rec_temp(self):
            # what set_LIST_REC_TEMP / insert_new_rec persist
            return methods['table2dict'](self, 'self.tableWidget_rapporti', preserve_empty=True)

        def rec_plain(self):
            return methods['table2dict'](self, 'self.tableWidget_rapporti')

    return Form()


def test_tableInsertData_replaces_rows_on_reload(form):
    form.load(US_SIX)
    assert form.tableWidget_rapporti.rowCount() == 6
    form.load(US_SIX)
    assert form.tableWidget_rapporti.rowCount() == 6, "reload must not leave stale rows"


def test_tableInsertData_clears_many_rows(form):
    form.load(str([['Copre', str(n), '', ''] for n in range(2, 52)]))  # 50 rows
    form.load(US1)
    assert form.tableWidget_rapporti.rowCount() == 2


def test_triple_load_like_init_yields_no_blank_rows(form):
    # __init__: on_pushButton_connect_pressed -> fill_fields() -> set_sito()
    for _ in range(3):
        form.load(US1)
    saved = form.rec_temp()
    assert BLANK not in saved
    assert saved == [['Copre', '2', '', ''], ['Copre', '5', '', '']]


def test_table2dict_preserve_empty_keeps_partial_rows(form):
    # guard for af431e71: area/sito left empty must still be saved as 4 columns
    t = form.tableWidget_rapporti
    t.insertRow(0)
    t.setItem(0, 0, QTableWidgetItem('Copre'))
    t.setItem(0, 1, QTableWidgetItem('2'))
    assert form.rec_temp() == [['Copre', '2', '', '']]


def test_table2dict_drops_all_blank_rows(form):
    t = form.tableWidget_rapporti
    t.insertRow(0)                       # row with all cells None (as after "+" button)
    t.insertRow(0)
    for c in range(4):                   # row with all cells '' (as loaded from a polluted DB)
        t.setItem(0, c, QTableWidgetItem(''))
    t.insertRow(0)
    t.setItem(0, 0, QTableWidgetItem('Copre'))
    t.setItem(0, 1, QTableWidgetItem('2'))
    assert form.rec_temp() == [['Copre', '2', '', '']]
    assert form.rec_plain() == [['Copre', '2']]


def test_polluted_record_is_cleaned_on_roundtrip(form):
    form.load(str([['Copre', '2', '', '']] + [BLANK] * 10))
    assert form.rec_temp() == [['Copre', '2', '', '']]
