"""Every SQLite spatial view the plugin code creates must expose the ROWID
of its geometry table as ``ROWID`` (2026-09-11).

The dev schema updater recreated pyarchinit_us_view, pyarchinit_strutture_view
and pyarchinit_reperti_view at every update with no ROWID column: the key
QGIS/OGR use to match the R*Tree became NULL and the layers drew nothing.
This test reads the SQL straight from the source files (SQLite code paths
only: PostgreSQL views have no ROWID) and checks each statement with the
same parser the self-healing uses. Pure Python, runs everywhere.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.db.spatial_view_repair import rewrite_view_with_base_rowid  # noqa: E402

BASE = {
    'pyarchinit_us_view': 'pyunitastratigrafiche',
    'pyarchinit_usm_view': 'pyunitastratigrafiche_usm',
    'pyarchinit_strutture_view': 'pyarchinit_strutture_ipotesi',
    'pyarchinit_reperti_view': 'pyarchinit_reperti',
    'pyarchinit_quote_view': 'pyarchinit_quote',
    'pyarchinit_quote_usm_view': 'pyarchinit_quote_usm',
    'pyarchinit_uscaratterizzazioni_view': 'pyuscaratterizzazioni',
    'pyarchinit_tomba_view': 'pyarchinit_tafonomia',
    'pyarchinit_us_negative_doc_view': 'pyarchinit_us_negative_doc',
    'pyarchinit_ut_point_view': 'pyarchinit_ut_point',
    'pyarchinit_ut_line_view': 'pyarchinit_ut_line',
    'pyarchinit_ut_polygon_view': 'pyarchinit_ut_polygon',
}


def _region(text, start_marker, end_re=r'\n    def '):
    i = text.find(start_marker)
    if i < 0:
        return ''
    m = re.compile(end_re).search(text, i + len(start_marker))
    return text[i:m.start() if m else len(text)]


def _statements(text):
    for m in re.finditer(r'CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?"?(\w+)"?\s+AS\b(.*?)(?:"""|\'\'\')', text, re.S | re.I):
        name = m.group(1).lower()
        if name in BASE:
            yield name, m.group(0)[:-3]


def _sqlite_sources():
    read = lambda p: (_ROOT / p).read_text(encoding='utf-8')
    updater = read('modules/db/sqlite_db_updater.py')
    yield 'sqlite_db_updater.py', updater
    db_update = read('modules/db/pyarchinit_db_update.py')
    for marker in ('def _recreate_sqlite_views', 'def _recreate_sqlite_us_view', 'def _recreate_sqlite_usm_view'):
        yield 'pyarchinit_db_update.py:%s' % marker[4:], _region(db_update, marker)
    manager = read('modules/db/pyarchinit_db_manager.py')
    yield 'pyarchinit_db_manager.py:ensure_ut_geometry_tables_exist', _region(manager, 'def ensure_ut_geometry_tables_exist')
    dialog = read('gui/pyarchinitConfigDialog.py')
    i = dialog.find('sql_view_us=("""CREATE VIEW  IF NOT EXISTS "pyarchinit_us_view"')
    yield 'pyarchinitConfigDialog.py:sql_view_us', dialog[i:i + 4000] if i >= 0 else ''
    # the "update SQLite" button recreated the quote views keyed on us_table
    yield ('pyarchinitConfigDialog.py:on_pushButton_upd_sqlite_pressed',
           _region(dialog, 'def on_pushButton_upd_sqlite_pressed'))


CASES = [(src, name, sql) for src, text in _sqlite_sources() for name, sql in _statements(text)]


def test_the_sqlite_view_statements_were_found():
    names = {n for _s, n, _q in CASES}
    assert {'pyarchinit_us_view', 'pyarchinit_strutture_view', 'pyarchinit_reperti_view',
            'pyarchinit_ut_point_view'} <= names
    assert {'pyarchinit_quote_view', 'pyarchinit_quote_usm_view'} <= {
        n for s, n, _q in CASES if s.endswith('upd_sqlite_pressed')}


@pytest.mark.parametrize('src,name,sql', CASES, ids=['%s:%s' % (s, n) for s, n, _ in CASES])
def test_view_key_is_the_rowid_of_the_geometry_table(src, name, sql):
    assert rewrite_view_with_base_rowid(sql, BASE[name]) == sql, (
        '%s in %s does not select %s.ROWID AS ROWID' % (name, src, BASE[name]))
