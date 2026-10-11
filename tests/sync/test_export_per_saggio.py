"""La scelta fra un grafo solo e un grafo per saggio.

Chiesta da Enzo l'11 ottobre 2026 come tre bottoni nella finestra di
esportazione. Dalla dev45 `GraphProjector.populate_container` divide il
sito in un grafo per saggio, e un rapporto fra unità di due saggi diversi
non si perde: diventa un `link` con l'indirizzo «grafo → nodo».

I test stanno sulla funzione, non sulla finestra: costruire un QWidget
sotto pytest fa abortire il processo in questo ambiente, e quello che conta
è che la scelta arrivi all'esportazione e che i tre esiti siano quelli.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.s3dgraphy.em_export import (EmExportError, export_site,
                                         saggi_del_sito)

#: Il database di prova, che ha tutto lo schema.
PROVA = _ROOT / "resources" / "dbfiles" / "pyarchinit_db_test.sqlite"
SITO = "Scavo a due aree"


@pytest.fixture
def con_saggi(tmp_path):
    """Una copia del database di prova in cui le due aree sono due saggi."""
    if not PROVA.is_file():
        pytest.skip("manca il database di prova")
    copia = tmp_path / "t.sqlite"
    shutil.copy(PROVA, copia)
    conn = sqlite3.connect(copia)
    conn.execute(
        "UPDATE us_table SET saggio = CASE WHEN CAST(area AS TEXT) = '1'"
        " THEN 'Saggio A' ELSE 'Saggio B' END")
    conn.commit()
    conn.close()
    return "sqlite:///%s" % copia


@pytest.fixture
def senza_saggi(tmp_path):
    if not PROVA.is_file():
        pytest.skip("manca il database di prova")
    copia = tmp_path / "t.sqlite"
    shutil.copy(PROVA, copia)
    return "sqlite:///%s" % copia


def _grafi(percorso) -> list:
    with open(percorso, encoding="utf-8") as f:
        return sorted(json.load(f)["graphs"])


def test_i_saggi_si_leggono_dal_database(con_saggi):
    assert saggi_del_sito(con_saggi, SITO) == ["Saggio A", "Saggio B"]


def test_un_sito_senza_saggi_non_ne_dichiara(senza_saggi):
    assert saggi_del_sito(senza_saggi, SITO) == []


def test_un_grafo_solo(con_saggi, tmp_path):
    """La scelta di sempre: tutte le unità in un grafo, qualunque saggio
    dichiarino."""
    percorso, _n, _a, _w = export_site(
        con_saggi, SITO, str(tmp_path / "uno"), per_saggio=False)
    assert _grafi(percorso) == [SITO]


def test_un_grafo_per_ogni_saggio(con_saggi, tmp_path):
    percorso, _n, _a, _w = export_site(
        con_saggi, SITO, str(tmp_path / "per"), per_saggio=True)
    grafi = _grafi(percorso)
    assert len(grafi) == 2, grafi
    assert all("Saggio" in g for g in grafi), grafi


def test_l_automatico_divide_quando_i_saggi_ci_sono(con_saggi, tmp_path):
    percorso, _n, _a, _w = export_site(
        con_saggi, SITO, str(tmp_path / "auto"), per_saggio=None)
    assert len(_grafi(percorso)) == 2


def test_l_automatico_non_divide_quando_non_ce_ne_sono(senza_saggi, tmp_path):
    """Su uno scavo senza saggi l'automatico si comporta come prima: è per
    questo che è il valore predefinito e nessuna chiamata esistente cambia."""
    percorso, _n, _a, _w = export_site(
        senza_saggi, SITO, str(tmp_path / "auto"), per_saggio=None)
    assert _grafi(percorso) == [SITO]


def test_chiedere_la_divisione_dove_non_c_e_niente_da_dividere(senza_saggi,
                                                               tmp_path):
    """Si dice, invece di scrivere un file che finge di essere diviso."""
    with pytest.raises(EmExportError, match="non ha saggi"):
        export_site(senza_saggi, SITO, str(tmp_path / "x"), per_saggio=True)


def test_dividendo_non_si_perde_nessuna_unita(con_saggi, tmp_path):
    """Le unità sono le stesse, in un grafo o in tre."""
    uno, _n1, _a1, _w = export_site(
        con_saggi, SITO, str(tmp_path / "uno"), per_saggio=False)
    molti, _n2, _a2, _w = export_site(
        con_saggi, SITO, str(tmp_path / "molti"), per_saggio=True)

    def unita(percorso):
        with open(percorso, encoding="utf-8") as f:
            dati = json.load(f)
        return sorted(n["name"] for g in dati["graphs"].values()
                      for n in g["nodes"] if n.get("node_type") == "US")

    assert unita(molti) == unita(uno), (unita(molti), unita(uno))


def test_il_file_diviso_si_rilegge(con_saggi, tmp_path):
    """`export_site` rilegge quello che ha scritto e conta: un contenitore
    si rilegge col suo lettore, non con quello di un grafo solo."""
    percorso, nodi, archi, _w = export_site(
        con_saggi, SITO, str(tmp_path / "per"), per_saggio=True)
    with open(percorso, encoding="utf-8") as f:
        dati = json.load(f)
    letti = sum(len(g["nodes"]) for g in dati["graphs"].values())
    assert letti == nodi, (letti, nodi)
    assert archi > 0
