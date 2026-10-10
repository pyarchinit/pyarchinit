"""«Verifica rapporti» risponde davvero (2026-10-08).

Enzo ha chiesto se la scheda funziona: nel suo screenshot la tabella è
vuota. Lo è perché la verifica non era ancora stata lanciata — il
controllo, sul database di esempio, trova le reciprocità mancanti.
"""
from __future__ import annotations

import os
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


@pytest.fixture()
def sample_db(tmp_path, monkeypatch):
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    return "sqlite:///%s" % (folder / "db.sqlite")


def test_the_sample_site_has_no_missing_reciprocity(sample_db):
    """Sul database di esempio i rapporti sono scritti in coppia, quindi di
    reciproci mancanti non ce ne sono.

    Questo test diceva il contrario fino al 2026-10-10, e aveva torto: il
    controllo cercava il verso inverso fra gli **archi**, ma il projector
    fonde una coppia reciproca in un arco canonico solo. Risultato, 81
    problemi su 81 falsi, e un «fix» che aggiungeva un doppione a quattro
    elementi di un rapporto già scritto in forma corta, su 38 righe, a ogni
    clic (Enzo: «il fix automatico dice corretti ma non applica i fix»)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    graph = GraphProjector().populate_graph(sample_db, "Scavo archeologico")
    report = RC.check_rapporti(graph, sito="Scavo archeologico")
    falsi = [i.summary for i in report.issues
             if i.kind == RC.MISSING_RECIPROCITY]
    assert not falsi, "reciproci «mancanti» che invece sono scritti: %s" % falsi[:3]


def test_a_reciprocal_really_removed_is_found_and_the_fix_sticks(sample_db):
    """E quando ne manca uno davvero: lo trova, lo scrive, e alla riverifica
    è sparito. È la catena intera, sul database vero."""
    import sqlite3

    from s3dgraphy.sync._db_handle import _resolve_db_handle

    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    SITO = "Scavo archeologico"
    percorso = sample_db.replace("sqlite:///", "")
    conn = sqlite3.connect(percorso)
    riga = conn.execute(
        "SELECT us, rapporti FROM us_table WHERE sito = ? AND rapporti "
        "LIKE '%Coperto da%' LIMIT 1", (SITO,)).fetchone()
    if riga is None:
        import pytest
        pytest.skip("nessun «Coperto da» nel database di esempio")
    us, rapporti = riga
    import ast
    voci = [list(map(str, x)) for x in ast.literal_eval(rapporti)]
    tolta = next(v for v in voci if v[0] == "Coperto da")
    conn.execute("UPDATE us_table SET rapporti = ? WHERE sito = ? AND us = ?",
                 (str([v for v in voci if v is not tolta]), SITO, us))
    conn.commit(); conn.close()

    def verifica():
        g = GraphProjector().populate_graph(sample_db, SITO)
        r = RC.check_rapporti(g, sito=SITO)
        return [i for i in r.issues if i.kind == RC.MISSING_RECIPROCITY]

    mancanti = verifica()
    assert len(mancanti) == 1, [i.summary for i in mancanti]
    edits = [e for i in mancanti for e in i.edits]
    assert edits, "trovato ma senza correzione automatica"

    RC.apply_edits(edits, _resolve_db_handle(sample_db), sito=SITO)
    assert verifica() == [], "il fix non è rimasto: il problema si ripresenta"


def test_the_checker_speaks_about_the_site_it_was_given(sample_db):
    """Ogni sito ha le sue: il controllo non deve rispondere con i
    problemi del sito accanto (i dieci siti del demo sono traduzioni
    dello stesso scavo e si somigliano)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    for sito, unita in (("Scavo archeologico", "1.1.US1"),
                        ("Archaeological Excavation", "1.1.SU1")):
        graph = GraphProjector().populate_graph(sample_db, sito)
        assert any(n.name == unita for n in graph.nodes), sito
        report = RC.check_rapporti(graph, sito=sito)
        assert report.sito == sito


# ---------------------------------------------------------------------------
# Uno scavo a due aree, sul database vero (2026-10-10)
# ---------------------------------------------------------------------------
# Il database di esempio ha un'area sola su tutte e 510 le righe, quindi lo
# scavo a più aree — dove l'identità di una scheda smette di essere il numero
# di US — va costruito. La US 1 e la US 9 di «Scavo archeologico» si clonano
# in un'area 2, ognuna col suo `node_uuid`, che è quello che fa del clone un
# nodo suo invece di una riga che si fonde con l'originale.

_SITO = "Scavo archeologico"


@pytest.fixture()
def due_aree(sample_db):
    """Lo stesso scavo con la US 1 e la US 9 anche nell'area 2.

    Nell'area 2 le due schede si rispondono («Copre 9 area 2» ⇄ «Coperto da 1
    area 2»); nell'area 1 la US 1 dichiara «Copre 9 area 1» e la US 9 non
    risponde. Il reciproco mancante è uno, e sta nell'area 1.
    """
    import sqlite3

    percorso = sample_db.replace("sqlite:///", "")
    conn = sqlite3.connect(percorso)
    colonne = [r[1] for r in conn.execute("PRAGMA table_info(us_table)")]

    def clona(us, area, rapporti, uuid):
        riga = conn.execute(
            "SELECT * FROM us_table WHERE sito = ? AND us = ? AND area = '1'",
            (_SITO, us)).fetchone()
        valori = dict(zip(colonne, riga))
        valori.pop("id_us", None)      # la chiave primaria la rifà SQLite
        valori["area"] = area
        valori["rapporti"] = rapporti
        valori["node_uuid"] = uuid
        nomi = list(valori)
        conn.execute("INSERT INTO us_table (%s) VALUES (%s)"
                     % (", ".join(nomi), ", ".join("?" * len(nomi))),
                     [valori[c] for c in nomi])

    conn.execute(
        "UPDATE us_table SET rapporti = ? WHERE sito = ? AND us = '1' "
        "AND area = '1'",
        ("[['Copre', '2'], ['Copre', '8'], ['Copre', '9', '1', '%s']]" % _SITO,
         _SITO))
    clona("1", "2", "[['Copre', '9', '2', '%s']]" % _SITO,
          "019f8043-0000-7000-8000-000000000001")
    clona("9", "2", "[['Coperto da', '1', '2', '%s']]" % _SITO,
          "019f8043-0000-7000-8000-000000000009")
    conn.commit()
    conn.close()
    return sample_db


def _verifica(url):
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    graph = GraphProjector().populate_graph(url, _SITO)
    report = RC.check_rapporti(graph, sito=_SITO)
    return [i for i in report.issues if i.kind == RC.MISSING_RECIPROCITY]


def _rapporti(url):
    import sqlite3
    conn = sqlite3.connect(url.replace("sqlite:///", ""))
    righe = dict(conn.execute(
        "SELECT area, rapporti FROM us_table WHERE sito = ? AND us = '9'",
        (_SITO,)).fetchall())
    conn.close()
    return righe


def test_two_rows_with_the_same_number_are_two_nodes(due_aree):
    """Il presupposto di tutto il resto: con un `node_uuid` suo, il clone è
    un nodo suo, e il numero di US compare due volte fra i nodi veri."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    graph = GraphProjector().populate_graph(due_aree, _SITO)
    veri = [n for n in graph.nodes if RC._real_us(n) is not None]
    assert len(veri) == 53, len(veri)        # 51 righe + i due cloni
    aree = sorted(n.attributes.get("area") for n in veri
                  if RC._real_us(n) == "9")
    assert aree == ["1", "2"], aree


def test_the_missing_reciprocal_is_the_one_of_area_1(due_aree):
    """Trovato, e la correzione nomina l'area 1.

    Prima il reciproco scritto nell'area 2 zittiva l'avviso dell'area 1: il
    controllo indicizzava le schede per numero di US, e la seconda riga
    copriva la prima.
    """
    mancanti = _verifica(due_aree)
    assert len(mancanti) == 1, [i.summary for i in mancanti]
    assert mancanti[0].us_path == ["1", "9"]
    e = mancanti[0].edits[0]
    assert e.us == "9"
    assert e.target == ("us_table", {"us": "9", "area": "1",
                                     "unita_tipo": "US"})
    assert ("Coperto da", "1", "1", _SITO) in e.add


def test_the_fix_writes_one_row_and_the_undo_restores_only_that_one(due_aree):
    """La sequenza che distruggeva i dati prima della guardia: un fix sulla
    chiave `{'us': '9'}` riscriveva **entrambe** le righe numero 9 e
    l'annulla le appiattiva sullo snapshot della prima, cancellando il
    «Coperto da 1 area 2» che l'area 2 aveva davvero."""
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    from modules.utility import rapporti_check as RC

    prima = _rapporti(due_aree)
    mancanti = _verifica(due_aree)
    edits = [e for i in mancanti for e in i.edits]
    assert edits, "trovato ma senza correzione automatica"

    token = RC.apply_edits(edits, _resolve_db_handle(due_aree), sito=_SITO)
    dopo = _rapporti(due_aree)
    assert "Coperto da" in dopo["1"] and "'1'" in dopo["1"], dopo["1"]
    assert dopo["2"] == prima["2"], "l'area 2 è stata riscritta"
    assert _verifica(due_aree) == [], "il fix non è rimasto"

    RC.rollback(token, _resolve_db_handle(due_aree))
    assert _rapporti(due_aree) == prima, "l'annulla non ha rimesso le cose"


def test_apply_no_longer_refuses_for_an_ambiguous_key(due_aree):
    """`apply_edits` rifiuta una chiave che individua più di una riga — e
    rifiutava **tutte** le correzioni dello stesso clic, perché il `raise`
    sta dentro la transazione. Le correzioni dei rapporti non la chiedono
    più."""
    from s3dgraphy.sync._db_handle import _resolve_db_handle
    from modules.utility import rapporti_check as RC

    edits = [e for i in _verifica(due_aree) for e in i.edits]
    RC.apply_edits(edits, _resolve_db_handle(due_aree), sito=_SITO)
