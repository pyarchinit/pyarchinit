"""Tests for modules.utility.temporal_check (temporal paradox detection)."""
import sqlite3
from pathlib import Path

from modules.utility import temporal_check as TC


def test_classify_relation():
    for et in ("overlies", "cuts", "fills", "abuts", "is_after"):
        assert TC._classify_relation(et) == "later"
    for et in ("is_overlain_by", "is_cut_by", "is_filled_by",
               "is_abutted_by", "is_before"):
        assert TC._classify_relation(et) == "earlier"
    for et in ("is_physically_equal_to", "is_bonded_to"):
        assert TC._classify_relation(et) == "contemp"
    assert TC._classify_relation("generic_connection") is None
    assert TC._classify_relation(None) is None


# ---------------------------------------------------------------------------
# Task 2: chronology readers + unit_span
# ---------------------------------------------------------------------------

def _db(tmp_path):
    p = tmp_path / "t.sqlite"
    c = sqlite3.connect(p)
    c.executescript(
        "CREATE TABLE periodizzazione_table (sito TEXT, periodo INTEGER,"
        " fase TEXT, cron_iniziale INTEGER, cron_finale INTEGER);"
        "CREATE TABLE us_table (sito TEXT, us TEXT, periodo_iniziale TEXT,"
        " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT);")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',1,'1',-100,0)")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',2,'1',0,100)")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',3,'1',100,200)")
    c.execute("INSERT INTO us_table VALUES ('S','US5','1','1','1','1')")
    c.execute("INSERT INTO us_table VALUES ('S','US7','3','1','3','1')")
    c.execute("INSERT INTO us_table VALUES ('S','US9',NULL,NULL,NULL,NULL)")
    c.commit(); c.close()
    from modules.s3dgraphy.sync._db_handle import DbHandle
    return DbHandle.from_path(p)


def test_build_chronology(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    assert chrono[("1", "1")] == (-100, 0)
    assert chrono[("3", "1")] == (100, 200)


def test_load_unit_periods(tmp_path):
    up = TC.load_unit_periods(_db(tmp_path), "S")
    assert up["US5"] == ("1", "1", "1", "1")
    assert up["US9"] == ("", "", "", "")


def test_unit_span(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    assert TC.unit_span(("1", "1", "1", "1"), chrono) == (-100, 0)
    assert TC.unit_span(("1", "1", "3", "1"), chrono) == (-100, 200)  # span both
    assert TC.unit_span(("", "", "", ""), chrono) is None
    assert TC.unit_span(("9", "1", "9", "1"), chrono) is None  # no such period


def test_unit_span_fase_fallback(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    # blank fase -> aggregate over the periodo
    assert TC.unit_span(("2", "", "2", ""), chrono) == (0, 100)
