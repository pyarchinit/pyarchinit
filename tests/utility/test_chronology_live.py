"""La verifica cronologica sul database di esempio: i numeri, non le opinioni.

Le quattro categorie si provano su righe costruite a mano in
`test_chronology_check.py`. Qui si prova che su un database vero trovano
quello che c'è — e che una seconda verifica non ripresenta quello che la
prima ha corretto.
"""
from __future__ import annotations

import shutil
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

from modules.utility import chronology_check as CC
from modules.utility import rapporti_check as RC

ITALIANO = "Scavo archeologico"
TRADOTTO = "Archaeological Excavation"


@pytest.fixture()
def handle(tmp_path):
    """Una copia del database di esempio: l'originale non si apre mai in
    scrittura — il QGIS di Enzo lo tiene aperto in WAL."""
    from s3dgraphy.sync._db_handle import DbHandle
    sorgente = _ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
    if not sorgente.exists():
        pytest.fail("il database di esempio manca: %s" % sorgente)
    copia = tmp_path / "db.sqlite"
    shutil.copy(sorgente, copia)
    return DbHandle.from_path(copia)


def _per_kind(handle, sito):
    periods, units = CC.load_chronology_rows(handle, sito)
    issues = CC.check_chronology(periods, units, sito=sito)
    out = {}
    for i in issues:
        out.setdefault(i.kind, []).append(i)
    return out


def test_the_italian_site_has_two_overlaps_and_thirteen_misalignments(handle):
    per_kind = _per_kind(handle, ITALIANO)
    assert len(per_kind.get("epoch_overlap", [])) == 2
    assert len(per_kind.get("datazione_mismatch", [])) == 13
    assert per_kind.get("epoch_reversed", []) == []
    assert per_kind.get("epoch_no_dates", []) == []


def test_the_two_overlaps_carry_no_proposal(handle):
    """Le due coppie portano intervalli identici — 1500–1549 e 1451–1499 — e
    qualunque restringimento farebbe finire una fase prima di cominciare.
    """
    periods, _ = CC.load_chronology_rows(handle, ITALIANO)
    per_fase = {CC._label(CC._key(p)): (CC._year(p["cron_iniziale"]),
                                        CC._year(p["cron_finale"]))
                for p in periods}
    issues = _per_kind(handle, ITALIANO)["epoch_overlap"]
    assert len(issues) == 2
    for iss in issues:
        assert iss.edits == [], iss.summary
        assert iss.auto is False
        # La ragione, scritta come asserzione e non solo in prosa: i due
        # intervalli sono lo stesso intervallo.
        a, b = iss.us_path
        assert per_fase[a] == per_fase[b], (a, b, per_fase[a], per_fase[b])


def test_a_translated_site_has_fifty_one_misalignments_with_both_texts(handle):
    """La periodizzazione è tradotta e la datazione nella scheda è rimasta in
    italiano: il summary deve mostrare tutti e due i testi, perché
    l'anteprima è l'unico punto in cui si vede cosa si sta per riscrivere."""
    issues = _per_kind(handle, TRADOTTO)["datazione_mismatch"]
    assert len(issues) == 51
    con_entrambi = [i for i in issues
                    if "Prima metà del XVI secolo" in i.summary
                    and "First half of the 16th century" in i.summary]
    assert con_entrambi, [i.summary for i in issues[:3]]


def test_applying_the_automatic_fixes_empties_the_category(handle):
    """Una seconda verifica non ripresenta quello che la prima ha corretto."""
    prima = _per_kind(handle, ITALIANO)["datazione_mismatch"]
    edits = [e for iss in prima for e in iss.edits]
    assert len(edits) == 13
    RC.apply_edits(edits, handle, sito=ITALIANO)
    dopo = _per_kind(handle, ITALIANO)
    assert dopo.get("datazione_mismatch", []) == []
    # Le sovrapposizioni restano: non sono automatiche e nessuno le ha spuntate.
    assert len(dopo["epoch_overlap"]) == 2


def test_the_fix_touches_only_its_own_site(handle):
    """La verifica è per sito, così non si riscrivono dieci siti in un colpo.

    Si confrontano i **valori**, non i conteggi: tutte le 51 US esistono in
    ogni sito, e una fuga scriverebbe il testo italiano sulle righe del sito
    tradotto — che resterebbero disallineate, quindi il conteggio non si
    muoverebbe di una virgola e il test passerebbe sopra una scrittura vera.
    """
    from sqlalchemy import text

    def righe_tradotte():
        with handle.engine.connect() as c:
            return c.execute(text(
                "SELECT us, datazione FROM us_table WHERE sito = :s "
                "ORDER BY us"), {"s": TRADOTTO}).fetchall()

    prima = righe_tradotte()
    assert prima, "il sito tradotto non ha righe: la prova non direbbe niente"
    edits = [e for iss in _per_kind(handle, ITALIANO)["datazione_mismatch"]
             for e in iss.edits]
    RC.apply_edits(edits, handle, sito=ITALIANO)
    assert righe_tradotte() == prima


def test_the_rollback_puts_the_site_back(handle):
    """E l'annulla rimette i valori di prima, non soltanto il conteggio."""
    from sqlalchemy import text

    def righe_italiane():
        with handle.engine.connect() as c:
            return c.execute(text(
                "SELECT us, datazione FROM us_table WHERE sito = :s "
                "ORDER BY us"), {"s": ITALIANO}).fetchall()

    prima = righe_italiane()
    edits = [e for iss in _per_kind(handle, ITALIANO)["datazione_mismatch"]
             for e in iss.edits]
    token = RC.apply_edits(edits, handle, sito=ITALIANO)
    # L'apply ha davvero scritto: senza questa prova, un apply che non fa
    # niente farebbe passare l'annulla senza averlo esercitato.
    assert _per_kind(handle, ITALIANO).get("datazione_mismatch", []) == []
    assert righe_italiane() != prima
    RC.rollback(token, handle)
    assert righe_italiane() == prima
    assert len(_per_kind(handle, ITALIANO)["datazione_mismatch"]) == 13
