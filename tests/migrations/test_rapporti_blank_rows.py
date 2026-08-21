"""Tests for the rapporti blank-rows repair (2026-08, bug report on 4.9.9)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from modules.s3dgraphy.sync._db_handle import DbHandle
from scripts.migrations._2026_08_rapporti_blank_rows_lib import (
    is_blank_row,
    strip_blank_rows,
    repair_blank_rapporti,
)

BLANK = "['', '', '', '']"
POLLUTED = "[" + ", ".join([BLANK] * 5 + ["['Copre', '2', '', '']"] + [BLANK] * 3 + ["['Copre', '5', '', '']"]) + "]"
CLEAN = "[['Coperto da', '1', '', '']]"


def _seed_db(p: Path):
    conn = sqlite3.connect(p)
    conn.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT, area TEXT, us TEXT, rapporti TEXT, rapporti2 TEXT
        )""")
    rows = [
        (1, "S", "1", "1", POLLUTED, "[]"),
        (2, "S", "1", "2", CLEAN, "[['', '', '', '']]"),   # blank only in rapporti2
        (3, "S", "1", "3", "[]", None),
        (4, "S", "1", "4", "not a list at all", ""),          # unparseable: untouched
        (5, "S", "1", "5", "[['', ''], ['Taglia', '9']]", None),  # 2-col legacy blank
    ]
    conn.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def _rows(p: Path):
    conn = sqlite3.connect(p)
    rows = conn.execute("SELECT id_us, rapporti, rapporti2 FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    return rows


def test_is_blank_row():
    assert is_blank_row(['', '', '', ''])
    assert is_blank_row([' ', None, ''])
    assert is_blank_row([])
    assert not is_blank_row(['Copre', '2', '', ''])
    assert not is_blank_row("['', '']")          # not a list → not a blank row


def test_strip_blank_rows_values():
    assert strip_blank_rows(POLLUTED) == ("[['Copre', '2', '', ''], ['Copre', '5', '', '']]", 8)
    assert strip_blank_rows(CLEAN) == (CLEAN, 0)
    assert strip_blank_rows(None) == (None, 0)
    assert strip_blank_rows("") == ("", 0)
    assert strip_blank_rows("not a list at all") == ("not a list at all", 0)
    assert strip_blank_rows("[[]]") == ("[]", 1)


def test_dry_run_reports_without_mutating(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    before = _rows(db)
    res = repair_blank_rapporti(DbHandle.from_path(db), dry_run=True)
    assert res.dry_run is True
    assert res.rows_scanned == 5
    assert res.rows_changed == 3          # id 1 (rapporti), 2 (rapporti2), 5 (rapporti)
    assert res.blank_rows_removed == 10   # 8 + 1 + 1
    assert [d.id_us for d in res.details] == [1, 2, 5]
    assert _rows(db) == before


def test_apply_rewrites_only_polluted_rows(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    res = repair_blank_rapporti(DbHandle.from_path(db), dry_run=False)
    assert res.rows_changed == 3
    rows = dict((r[0], (r[1], r[2])) for r in _rows(db))
    assert rows[1] == ("[['Copre', '2', '', ''], ['Copre', '5', '', '']]", "[]")
    assert rows[2] == (CLEAN, "[]")
    assert rows[3] == ("[]", None)
    assert rows[4] == ("not a list at all", "")
    assert rows[5] == ("[['Taglia', '9']]", None)


def test_apply_is_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    repair_blank_rapporti(DbHandle.from_path(db), dry_run=False)
    after_first = _rows(db)
    res = repair_blank_rapporti(DbHandle.from_path(db), dry_run=False)
    assert res.rows_changed == 0 and res.blank_rows_removed == 0
    assert _rows(db) == after_first
