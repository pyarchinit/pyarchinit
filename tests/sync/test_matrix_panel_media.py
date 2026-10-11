"""I media nel pannello della matrice, e perché a volte non ci sono.

«Nella tab media li vedo; non compaiono quando esporto il matrix da
Extended Matrix e lo visualizzo: cliccando su un nodo dovrei vedere i
media associati» (Enzo, 12 ottobre 2026).

La catena è: il pannello ricorda le unità del file e la connessione del
progetto, poi per ogni nodo cliccato chiede i media a
`em_matrix_links.media_for_unit`, che trova la riga della scheda US e
legge `media_to_entity_table`. Qui si misura tutta, su un file esportato
davvero — in un grafo solo e diviso per saggi.

E si misura soprattutto il **perché**: finché la striscia spariva senza
dire niente, «non vedo i media» poteva essere il database senza media, la
connessione che non arriva al pannello, un nodo che non è una riga della
scheda (una continuità, un documento) o un errore di lettura. Quattro
cause, un sintomo solo, e tre giri di domande per distinguerle.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
URL = "sqlite:///" + str(DB)
SITO = "Scavo archeologico"


@pytest.fixture(scope="module")
def modelli():
    """Il modello della matrice, nelle due forme che il file può avere."""
    from modules.s3dgraphy import em_export as EX
    from modules.utility.em_matrix_model import read_em_json

    if not DB.is_file():
        pytest.skip("manca il database di esempio")
    fuori = {}
    for per_saggio in (False, True):
        cartella = Path(tempfile.mkdtemp())
        percorso, *_ = EX.export_site(URL, SITO, str(cartella),
                                      per_saggio=per_saggio)
        fuori[per_saggio] = read_em_json(Path(percorso))
    return fuori


@pytest.mark.parametrize("per_saggio", [False, True])
def test_ogni_unita_del_file_ha_i_suoi_media(modelli, per_saggio):
    """Vale sia sul file a un grafo sia sul contenitore diviso per saggi:
    la divisione non deve far perdere i media per strada."""
    from modules.s3dgraphy import em_matrix_panel as P

    modello = modelli[per_saggio]
    P.remember_units(modello.units)
    P.remember_connection(URL)
    senza = [u.label for u in modello.units if not P.media_for(u.node_id)]
    assert senza == [], senza
    assert len(modello.units) >= 39


def test_tre_media_per_unita_col_nome_del_file_giusto(modelli):
    from modules.s3dgraphy import em_matrix_panel as P

    modello = modelli[False]
    P.remember_units(modello.units)
    P.remember_connection(URL)
    uno = modello.units[0]
    media = P.media_for(uno.node_id)
    assert len(media) == 3, media
    for m in media:
        assert m.thumb_file.endswith("_thumb.png"), m
        assert m.thumb_file.split("_")[0].isdigit(), m


def test_senza_connessione_lo_dice(modelli):
    """Era il caso peggiore: il pannello aperto senza connessione
    mostrava la scheda e nascondeva i media, identico a un'unità che non
    ne ha."""
    from modules.s3dgraphy import em_matrix_panel as P

    modello = modelli[False]
    P.remember_units(modello.units)
    P.remember_connection(None)
    media, perche = P._media_e_perche(modello.units[0].node_id)
    assert media == []
    assert "senza connessione" in perche
    P.remember_connection(URL)


def test_un_database_che_non_si_apre_lo_dice(modelli, tmp_path):
    from modules.s3dgraphy import em_matrix_panel as P

    modello = modelli[False]
    P.remember_units(modello.units)
    P.remember_connection("sqlite:///%s" % (tmp_path / "non-esiste.sqlite"))
    media, perche = P._media_e_perche(modello.units[0].node_id)
    assert media == []
    assert "non si apre" in perche
    P.remember_connection(URL)


def test_un_nodo_che_non_e_una_scheda_lo_dice(modelli):
    """Una continuità o un documento non è una riga della scheda US: non
    ha media, e non è un guasto."""
    from modules.s3dgraphy import em_matrix_panel as P
    from modules.utility.em_matrix_links import unit_identity

    modello = modelli[False]
    P.remember_units(modello.units)
    P.remember_connection(URL)
    senza_identita = [u for u in modello.units if not unit_identity(u)]
    if not senza_identita:
        pytest.skip("in questo file ogni nodo è una riga della scheda")
    media, perche = P._media_e_perche(senza_identita[0].node_id)
    assert media == []
    assert "non è una riga della scheda" in perche


def test_un_nodo_sconosciuto_non_spiega_niente(modelli):
    from modules.s3dgraphy import em_matrix_panel as P

    P.remember_units(modelli[False].units)
    P.remember_connection(URL)
    media, perche = P._media_e_perche("questo-nodo-non-esiste")
    assert media == []
    assert perche == "nodo sconosciuto"


def test_database_reachable_distingue_i_due_casi(tmp_path):
    from modules.utility.em_matrix_links import database_reachable

    assert database_reachable(URL) is True
    assert database_reachable(
        "sqlite:///%s" % (tmp_path / "mai.sqlite")) is False
    assert database_reachable(None) is False
