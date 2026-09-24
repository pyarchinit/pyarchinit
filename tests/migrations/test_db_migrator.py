"""Migrating a whole database into another one (2026-09-24).

The import tab moved one table at a time and named every column by hand,
so entire sheets had no way in — budget, personale, presenze,
attrezzature, computo metrico, inventario lapidei, archeozoologia,
detsesso, deteta — and the geometries never travelled with the data.
``modules/db/db_migrator.py`` takes the columns from the mapper instead,
so every mapped table is copied the same way.

The guards here are pure Python (they read the sources). The migration
itself runs on the two SQLite databases pyArchInit ships, and is skipped
where the plugin's database layer cannot be imported.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.db import db_migrator as dbm  # noqa: E402  (pure module)

_MAPPER_SOURCE = (_ROOT / "modules" / "db" / "pyarchinit_db_mapper.py").read_text(encoding="utf-8")
_MANAGER_SOURCE = (_ROOT / "modules" / "db" / "pyarchinit_db_manager.py").read_text(encoding="utf-8")

# Mapped tables that are not data of an excavation: a view, the staging
# tables of an import, the embeddings of the AI search.
_NOT_DATA = {'MEDIAVIEW', 'US_TOIMP', 'INVENTARIO_MATERIALI_TOIMP', 'POTTERY_EMBEDDING_METADATA'}


def _mapped_tables():
    """Every table pyArchInit maps, read from the mapper source."""
    return {m.group(1) for m in re.finditer(r'^\s*mapper\((\w+),', _MAPPER_SOURCE, re.M)}


def test_every_sheet_travels():
    """A sheet added tomorrow must be listed, or the migration would
    quietly leave it behind — which is how budget, personale and the
    others were lost in the first place."""
    forgotten = _mapped_tables() - set(dbm.ALL_TABLES) - set(dbm.NOT_MIGRATED) - _NOT_DATA
    assert not forgotten, "tabelle mappate che nessuno migra: %s" % sorted(forgotten)


def test_the_sheets_that_were_missing_are_there_now():
    for name in ('BUDGET', 'PERSONALE', 'PRESENZE', 'ATTREZZATURE', 'COMPUTO_METRICO',
                 'INVENTARIO_LAPIDEI', 'ARCHEOZOOLOGY', 'DETSESSO', 'DETETA',
                 'TMA_MATERIALI', 'PDF_ADMINISTRATOR', 'FAUNA'):
        assert name in dbm.ALL_TABLES, name


def test_the_geometries_travel_with_the_data():
    for name in ('PYUS', 'PYUSM', 'PYQUOTE', 'PYSITO_POINT', 'PYDOCUMENTAZIONE'):
        assert name in dbm.ALL_TABLES, name
    # the media links point at the records copied before them
    assert dbm.ALL_TABLES[-1] == 'MEDIATOENTITY'


def test_users_and_their_passwords_stay_where_they_are():
    for name in ('PYARCHINIT_USERS', 'PYARCHINIT_ROLES', 'PYARCHINIT_PERMISSIONS'):
        assert name not in dbm.ALL_TABLES
        assert name in dbm.NOT_MIGRATED


def test_every_table_it_copies_can_be_read():
    """query_bool() resolves a name through a dictionary of its own:
    ARCHEOZOOLOGY was missing from it, so that sheet could not even be
    read."""
    unknown = [n for n in dbm.ALL_TABLES if "'%s':" % n not in _MANAGER_SOURCE]
    assert not unknown, "nomi che il gestore non sa risolvere: %s" % unknown


def test_an_empty_value_becomes_nothing_only_where_it_is_not_text():
    class _Type(object):
        def __init__(self, name):
            self.__class__ = type(name, (object,), {})

    class _Column(object):
        def __init__(self, name, kind):
            self.name = name
            self.type = type(kind, (object,), {})()

    class _Mapper(object):
        columns = [_Column('sito', 'Text'), _Column('us', 'Integer'),
                   _Column('the_geom', 'Geometry'), _Column('data', 'Date')]

    coerce = dbm._empty_to_null(_Mapper())
    assert coerce('us', '') is None                  # PostgreSQL: bigint vuoto -> errore
    assert coerce('data', '') is None
    assert coerce('sito', '') == ''                  # un testo vuoto resta un testo vuoto
    assert coerce('the_geom', '') == ''
    assert coerce('us', 12) == 12


def test_the_summary_says_what_did_not_travel():
    good = dbm.TableOutcome('US')
    good.read = good.written = 51
    empty = dbm.TableOutcome('BUDGET')
    bad = dbm.TableOutcome('TOMBA')
    bad.read, bad.skipped, bad.error = 3, 3, 'invalid input syntax for type bigint'
    text = dbm.summary([good, empty, bad])
    assert 'US: 51 righe' in text
    assert 'TOMBA: 3 righe non scritte' in text and 'bigint' in text
    assert 'BUDGET' in text.split('Vuote')[1]


# --------------------------------------------------------------------------
# La migrazione vera, sui due database che il plugin distribuisce
# --------------------------------------------------------------------------

def _managers(tmp_path):
    """Source (the sample database) and destination (an empty one)."""
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "sorgente.sqlite")
    shutil.copy(resources / "pyarchinit.sqlite", folder / "destinazione.sqlite")
    os.environ["PYARCHINIT_HOME"] = str(tmp_path)
    try:
        from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
    except Exception as exc:                          # no SQLAlchemy/GeoAlchemy here
        pytest.skip("database layer not importable: %s" % exc)
    read = Pyarchinit_db_management("sqlite:///%s/sorgente.sqlite" % folder)
    write = Pyarchinit_db_management("sqlite:///%s/destinazione.sqlite" % folder)
    if not (read.connection() and write.connection()):
        pytest.skip("cannot open the sample databases")
    return read, write, folder


def test_a_whole_database_travels_in_one_go(tmp_path):
    read, write, folder = _managers(tmp_path)
    outcomes = {o.name: o for o in dbm.migrate(read, write)}

    # what the source holds is what the destination gets
    assert outcomes['US'].read > 0 and outcomes['US'].written == outcomes['US'].read
    assert outcomes['SITE'].written == outcomes['SITE'].read
    # the geometries come along, with the SRID of the data: the template
    # registers -1 and would refuse every one of them
    assert outcomes['PYUS'].read > 0 and outcomes['PYUS'].written == outcomes['PYUS'].read
    assert outcomes['PYUS'].srid_aligned == 3004
    assert outcomes['PYQUOTE'].written == outcomes['PYQUOTE'].read
    # and the media links find their media
    assert outcomes['MEDIA'].written == outcomes['MEDIA'].read
    assert outcomes['MEDIATOENTITY'].written == outcomes['MEDIATOENTITY'].read
    assert not [o.name for o in outcomes.values() if o.error]


def test_the_identifiers_of_an_empty_destination_are_the_ones_of_the_source(tmp_path):
    """The links between records are made of those numbers: renumbering
    them leaves a thumbnail pointing at nothing."""
    read, write, folder = _managers(tmp_path)
    dbm.migrate(read, write, tables=['SITE', 'US', 'MEDIA', 'MEDIA_THUMB'])
    before = {r.id_us for r in read.query_bool({}, 'US')}
    after = {r.id_us for r in write.query_bool({}, 'US')}
    assert before == after


def test_running_it_twice_is_announced_before_and_not_after(tmp_path):
    read, write, _ = _managers(tmp_path)
    assert not [n for n, _ in dbm.already_filled(write, ['US', 'PYUS'])]
    copiate = {o.name: o.written for o in dbm.migrate(read, write, tables=['US', 'PYUS'])}
    assert dict(dbm.already_filled(write, ['US', 'PYUS'])) == copiate


def test_the_import_tab_asks_the_engine_for_the_sheets_it_cannot_write():
    """The dialog cannot be exercised without QGIS: these two guards keep
    its wiring honest."""
    dialog = (_ROOT / "gui" / "pyarchinitConfigDialog.py").read_text(encoding="utf-8")
    assert "if scelta == 'ALL' or scelta in db_migrator.HANDLED_BY_MIGRATOR:" in dialog
    assert "db_migrator.migrate(" in dialog

    import xml.etree.ElementTree as ET
    ui = ET.parse(str(_ROOT / "gui" / "ui" / "pyarchinitConfigDialog.ui"))
    widgets = {w.get('name') for w in ui.iter('widget')}
    for side in ('rd', 'wt'):
        for prefix in ('comboBox_server', 'lineEdit_username', 'lineEdit_pass',
                       'lineEdit_host', 'lineEdit_port', 'lineEdit_database'):
            assert '%s_%s' % (prefix, side) in widgets, '%s_%s' % (prefix, side)
    assert 'progress_bar' in widgets

    # the sheets that did nothing when picked are now offered and handled
    combo = [i.find('property/string').text
             for w in ui.iter('widget') if w.get('name') == 'comboBox_mapper_read'
             for i in w.findall('item')]
    for name in ('BUDGET', 'PERSONALE', 'PRESENZE', 'ATTREZZATURE', 'COMPUTO_METRICO',
                 'INVENTARIO_LAPIDEI', 'PDF_ADMINISTRATOR', 'FAUNA'):
        assert name in combo, name
    assert combo[-1] == 'ALL', "ALL deve restare l'ultima voce"
