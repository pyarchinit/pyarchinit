"""Come si legge una voce dei rapporti, qualunque formato abbia (2026-10-08).

Segnalato da Enzo: «Esporta matrice» moriva con «list index out of range».
Il campo ``rapporti`` ha due formati vivi nello stesso database:
``[tipo, us, area, sito]`` (lungo) e ``[tipo, us]`` (corto). Nel DB di
esempio **1683 voci su 1870 sono corte**, e l'esportatore leggeva
``voce[2]`` senza guardare.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.rapporti_entries import rapporto_target  # noqa: E402


def test_the_long_format_gives_its_own_area():
    assert rapporto_target(["Copre", "2", "3", "Alfa"], "1") == (
        "Copre", "2", "3")


def test_the_short_format_means_the_same_area():
    """['Covers', '2'] è il formato che il DB di esempio usa 1683 volte:
    senza area dichiarata l'unità collegata sta nell'area di chi la cita."""
    assert rapporto_target(["Covers", "2"], "1") == ("Covers", "2", "1")


def test_an_empty_area_falls_back_too():
    assert rapporto_target(["Copre", "2", "", ""], "7") == ("Copre", "2", "7")


def test_an_entry_without_a_unit_is_not_a_relation():
    assert rapporto_target(["Copre", ""], "1") is None
    assert rapporto_target(["Copre"], "1") is None
    assert rapporto_target([], "1") is None
    assert rapporto_target("Copre", "1") is None
    assert rapporto_target(None, "1") is None


def test_numbers_are_returned_as_text():
    """Le voci scritte a mano portano interi: chi costruisce i nomi dei
    nodi concatena stringhe."""
    assert rapporto_target(["Copre", 2, 3, "Alfa"], 1) == ("Copre", "2", "3")


def test_rapporti2_long_and_short_forms():
    """``rapporti2`` è [tipo, us, unita_tipo, descrizione, periodizzazione,
    area, sito]; la variante vecchia si ferma a cinque posti (1683 voci su
    1870 nel DB di esempio)."""
    from modules.utility.rapporti_entries import rapporto2_target

    long_form = ["Copre", "2", "US", "Livellamento", "1-2", "3", "Alfa"]
    assert rapporto2_target(long_form, "1") == (
        "Copre", "2", "US", "Livellamento", "1-2", "3")
    short_form = ["Covers", "2", "SU", "Levelling", "1-2"]
    assert rapporto2_target(short_form, "1") == (
        "Covers", "2", "SU", "Levelling", "1-2", "1")


def test_a_truncated_rapporti2_entry_is_skipped():
    from modules.utility.rapporti_entries import rapporto2_target

    assert rapporto2_target(["Copre", "2"], "1") is None
    assert rapporto2_target(["Copre", "2", "US"], "1") is None
    assert rapporto2_target(None, "1") is None


def test_every_relation_in_the_sample_db_can_be_read():
    """Il database di esempio porta entrambi i formati: nessuna voce deve
    far cadere chi la legge (è il crash che Enzo ha visto il 2026-10-08)."""
    import ast
    import sqlite3

    import pytest

    from modules.utility.rapporti_entries import rapporto2_target

    db = _ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
    if not db.exists():
        pytest.skip("DB di esempio non presente")
    conn = sqlite3.connect(db)
    try:
        rows = conn.execute(
            "SELECT area, rapporti, rapporti2 FROM us_table").fetchall()
    finally:
        conn.close()
    short = long_ = 0
    for area, raw, raw2 in rows:
        for entry in (ast.literal_eval(raw) if raw else []) or []:
            got = rapporto_target(entry, area)
            if got is None:
                continue
            assert got[2], entry          # un'area c'è sempre
            if isinstance(entry, (list, tuple)) and len(entry) > 2:
                long_ += 1
            else:
                short += 1
        for entry in (ast.literal_eval(raw2) if raw2 else []) or []:
            rapporto2_target(entry, area)  # non deve sollevare
    # Il database di esempio che spediamo è scritto TUTTO col formato
    # corto (1870 voci su 1870, misurato il 2026-10-08): ecco perché
    # «Esporta matrice» cadeva per chiunque partisse da lì.
    assert short, (short, long_)
