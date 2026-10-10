"""Le correzioni cronologiche atterrano nella tabella giusta, e si annullano.

Su SQLite di prova: la scrittura si guarda, non si deduce.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

from modules.utility import rapporti_check as RC


def _db(tmp_path):
    """us_table e periodizzazione_table, due siti, con i tipi dello schema:
    `periodo` intero e `fase` testo, che è dove PostgreSQL inciampa."""
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "chrono.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, us TEXT, rapporti TEXT,"
              " periodo_iniziale TEXT, fase_iniziale TEXT,"
              " periodo_finale TEXT, fase_finale TEXT, datazione TEXT)")
    c.execute("CREATE TABLE periodizzazione_table (sito TEXT,"
              " periodo INTEGER, fase TEXT, cron_iniziale INTEGER,"
              " cron_finale INTEGER, datazione_estesa TEXT, descrizione TEXT)")
    c.execute("INSERT INTO us_table VALUES ('S','12','[]','2','2.2','2','2.2',"
              "'Prima metà del XV secolo')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',2,'2.2',1500,1549,'Prima metà del XVI secolo','')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',3,'1',1500,1549,'Prima metà del XV secolo rec','')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('ALTRO',2,'2.2',1500,1549,'non toccare','')")
    c.commit(); c.close()
    return DbHandle.from_path(p)


def _periodo(h, sito, periodo, fase):
    from sqlalchemy import text
    with h.engine.connect() as c:
        return c.execute(text(
            "SELECT cron_iniziale, cron_finale FROM periodizzazione_table "
            "WHERE sito = :s AND CAST(periodo AS TEXT) = :p AND fase = :f"),
            {"s": sito, "p": periodo, "f": fase}).fetchone()


def test_a_period_edit_writes_in_the_periodization(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1500, 1480)
    with h.engine.connect() as c:
        # us_table non è stata sfiorata: nessuna riga 'us' = '2/2.2'
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_a_period_edit_leaves_the_other_sites_alone(tmp_path):
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    assert _periodo(h, "ALTRO", "2", "2.2") == (1500, 1549)


def test_a_period_edit_without_a_sito_refuses_to_write(tmp_path):
    """(periodo, fase) senza sito è la stessa fase in dieci siti."""
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    with pytest.raises(ValueError, match="sito"):
        RC.apply_edits([e], h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
    assert _periodo(h, "ALTRO", "2", "2.2") == (1500, 1549)


def test_an_edit_without_a_target_still_writes_in_us_table(tmp_path):
    """Nessuna chiamata esistente cambia: `target` vuoto vale us_table."""
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("XV secolo",)


def test_a_column_outside_the_whitelist_is_not_written(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("descrizione", "cancellata"),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text(
            "SELECT descrizione FROM periodizzazione_table "
            "WHERE sito='S' AND fase='2.2'")).fetchone() == ("",)


def test_datazione_is_writable_in_us_table_and_cron_is_not(tmp_path):
    """La whitelist è per tabella: `datazione` solo in us_table."""
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="12", set_fields=(("cron_iniziale", 1),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_rollback_restores_both_tables(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    edits = [
        RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),)),
        RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"})),
    ]
    tok = RC.apply_edits(edits, h, sito="S")
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_two_edits_on_the_same_row_roll_back_to_the_first_value(tmp_path):
    """Una fase che si sovrappone a due altre produce due Edit sulla stessa
    riga: si applicano insieme, e l'annulla torna a prima della prima."""
    h = _db(tmp_path)
    target = ("periodizzazione_table", {"periodo": "2", "fase": "2.2"})
    edits = [RC.Edit(us="2/2.2", set_fields=(("cron_iniziale", 1510),),
                     target=target),
             RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1540),),
                     target=target)]
    tok = RC.apply_edits(edits, h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1510, 1540)
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)


def test_an_edit_whose_row_is_gone_writes_nothing_and_does_not_raise(tmp_path):
    """Qualcuno ha cancellato la fase nel frattempo: zero righe aggiornate, e
    la riverifica che segue ripresenta il problema."""
    h = _db(tmp_path)
    e = RC.Edit(us="9/9", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "9", "fase": "9"}))
    tok = RC.apply_edits([e], h, sito="S")
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
