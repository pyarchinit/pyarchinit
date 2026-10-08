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


def _seed_db(p: Path, rapporti=None, rapporti2=None):
    conn = sqlite3.connect(p)
    conn.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            rapporti TEXT, rapporti2 TEXT
        )""")
    rows = [
        (1, "S", "1", "1", "US"),
        (2, "S", "1", "2", "USVA"),
        (3, "S", "1", "3", "USVB"),
        (4, "S", "1", "4", "USVC"),
        (5, "S", "1", "5", "USVs"),  # already aligned
    ]
    conn.executemany(
        "INSERT INTO us_table (id_us, sito, area, us, unita_tipo, rapporti,"
        " rapporti2) VALUES (?,?,?,?,?,?,?)",
        [r + (rapporti, rapporti2) for r in rows])
    conn.commit()
    conn.close()


def _column(db: Path, name: str):
    conn = sqlite3.connect(db)
    try:
        colonne = {row[1] for row in conn.execute(
            "PRAGMA table_info(us_table)")}
        ordine = " ORDER BY id_us" if "id_us" in colonne else ""
        return [r[0] for r in conn.execute(
            "SELECT %s FROM us_table%s" % (name, ordine)).fetchall()]
    finally:
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
    # USVA → USVs (parallelogram), USVB → USVn (hexagon, was a bug
    # that mapped both to USVs), USVC → USVn.
    assert [r[0] for r in rows] == ["US", "USVs", "USVn", "USVn", "USVs"]


def test_apply_idempotent(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db)
    apply_changes(db)
    apply_changes(db)  # second run must be a no-op
    conn = sqlite3.connect(db)
    rows = conn.execute("SELECT unita_tipo FROM us_table ORDER BY id_us").fetchall()
    conn.close()
    assert [r[0] for r in rows] == ["US", "USVs", "USVn", "USVn", "USVs"]


def test_replacements_constant():
    assert REPLACEMENTS["USVA"] == "USVs"
    # USVB → USVn (was incorrectly mapped to USVs in the original
    # 5.1.0-alpha migration; legacy dot.py renders USVB as a hexagon
    # = Non-Structural Virtual SU = USVn).
    assert REPLACEMENTS["USVB"] == "USVn"
    assert REPLACEMENTS["USVC"] == "USVn"


def test_the_unit_type_is_rewritten_inside_rapporti2(tmp_path: Path):
    """``rapporti2`` è [tipo, us, unita_tipo, descr, periodo, area, sito]:
    il tipo dell'unità collegata sta in posizione 2 e porta i vecchi
    codici — 60 righe nel database di esempio."""
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti2="[['Copre', '3', 'USVB', 'muro', '2-1', '1', 'S']]")
    plan = plan_changes(db)
    assert plan["rapporti2 (voci)"] == 5

    applied = apply_changes(db)
    assert applied["rapporti2 (voci)"] == 5
    import ast
    assert ast.literal_eval(_column(db, "rapporti2")[0])[0][2] == "USVn"


def test_the_unit_type_is_rewritten_inside_rapporti_too(tmp_path: Path):
    """Chiesto da Enzo: anche il campo «rapporti». Lì il tipo non ha una
    colonna sua ([tipo, us, area, sito]): compare attaccato al numero
    dell'unità («USVA104»), ed è l'unico posto che si tocca — la
    posizione 2 è l'AREA, non un tipo."""
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti="[['Copre', 'USVA104', '1', 'S'],"
                          " ['Taglia', '7', 'USVC', 'S']]")
    applied = apply_changes(db)
    assert applied["rapporti (voci)"] == 5           # 1 voce × 5 righe
    import ast
    voci = ast.literal_eval(_column(db, "rapporti")[0])
    assert voci[0][1] == "USVs104"
    assert voci[1] == ["Taglia", "7", "USVC", "S"]   # l'area resta l'area


def test_applying_twice_changes_nothing_the_second_time(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti2="[['Copre', '3', 'USVA', 'muro', '2-1', '1', 'S']]")
    apply_changes(db)
    first = _column(db, "rapporti2")
    second = apply_changes(db)
    assert _column(db, "rapporti2") == first
    assert second["rapporti2 (voci)"] == 0


def test_an_unreadable_cell_is_left_alone(tmp_path: Path):
    """Una cella che non si legge si lascia com'è e si conta a parte: una
    lista riscritta a metà è peggio di una lista vecchia."""
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti2="non una lista")
    applied = apply_changes(db)
    assert _column(db, "rapporti2")[0] == "non una lista"
    assert applied["illeggibili"] == 5
    assert _column(db, "unita_tipo") == ["US", "USVs", "USVn", "USVn", "USVs"]


def test_an_empty_cell_is_not_a_problem(tmp_path: Path):
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti="[]", rapporti2=None)
    applied = apply_changes(db)
    assert applied["illeggibili"] == 0
    assert applied["rapporti (voci)"] == 0


def test_free_text_is_never_rewritten(tmp_path: Path):
    """Dalla review: la riscrittura girava su OGNI cella della voce, e la
    posizione 3 di rapporti2 è la descrizione libera. «USVA: il muro
    visto da ovest» diventava «USVs: il muro…», e una descrizione con due
    occorrenze ne vedeva riscritta una sola — proprio la riscrittura a
    metà che la funzione dice di rifiutare. Si tocca solo dove un codice
    ci sta per davvero."""
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti2="[['Copre', '3', 'USVB', "
                           "'USVC_3 e USVC_4 rimosse', '2-1', '1', 'S']]")
    apply_changes(db)
    import ast
    voce = ast.literal_eval(_column(db, "rapporti2")[0])[0]
    assert voce[2] == "USVn"                      # il tipo sì
    assert voce[3] == "USVC_3 e USVC_4 rimosse"   # la descrizione no


def test_a_code_glued_to_the_unit_number_is_rewritten(tmp_path: Path):
    """Chiesto da Enzo: anche il campo «rapporti». Lì il codice compare
    attaccato al numero dell'unità."""
    db = tmp_path / "x.sqlite"
    _seed_db(db, rapporti="[['Copre', 'USVA104', '1', 'S']]")
    apply_changes(db)
    import ast
    assert ast.literal_eval(_column(db, "rapporti")[0])[0][1] == "USVs104"


def test_a_table_without_id_us_still_migrates_the_unit_type(tmp_path: Path):
    """Dalla review: la lettura delle colonne dei rapporti chiedeva
    id_us, e su uno schema che non ce l'ha non si migrava più niente."""
    db = tmp_path / "x.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
        rapporti TEXT, rapporti2 TEXT)""")
    conn.execute("INSERT INTO us_table VALUES ('S','1','1','USVA','[]','[]')")
    conn.commit()
    conn.close()
    apply_changes(db)
    assert _column(db, "unita_tipo") == ["USVs"]
