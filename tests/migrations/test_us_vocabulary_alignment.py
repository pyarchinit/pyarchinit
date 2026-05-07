"""Tests for the USVA/USVB→USVs, USVC→USVn migration."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
    plan_changes,
    apply_changes,
    REPLACEMENTS,
)


def _seed_db(p: Path):
    conn = sqlite3.connect(p)
    conn.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT
        )""")
    rows = [
        (1, "S", "1", "1", "US"),
        (2, "S", "1", "2", "USVA"),
        (3, "S", "1", "3", "USVB"),
        (4, "S", "1", "4", "USVC"),
        (5, "S", "1", "5", "USVs"),  # already aligned
    ]
    conn.executemany("INSERT INTO us_table VALUES (?,?,?,?,?)", rows)
    conn.commit()
    conn.close()


def test_plan_reports_counts(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    plan = plan_changes(db)
    assert plan["USVA"] == 1
    assert plan["USVB"] == 1
    assert plan["USVC"] == 1
    assert plan["USVs (already-aligned)"] == 1


def test_plan_does_not_mutate(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    plan_changes(db)
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVA", "USVB", "USVC", "USVs"]


def test_apply_rewrites_in_place(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    apply_changes(db)
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVs", "USVs", "USVn", "USVs"]


def test_apply_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    apply_changes(db)
    apply_changes(db)  # second run must be a no-op
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVs", "USVs", "USVn", "USVs"]


def test_replacements_constant():
    assert REPLACEMENTS["USVA"] == "USVs"
    assert REPLACEMENTS["USVB"] == "USVs"
    assert REPLACEMENTS["USVC"] == "USVn"
