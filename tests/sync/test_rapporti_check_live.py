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
