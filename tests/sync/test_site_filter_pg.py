"""Il filtro del sito su PostgreSQL — il meccanismo della dev44.

`_filter_by_site` non esiste più. Dalla dev44 un grafo appartiene a un sito
quando il suo **studio** si è svolto là, o in un luogo dentro il sito, e la
domanda la fa `s3dgraphy.hdto.graphs_at` leggendo la catena del grafo
stesso. La versione di prima guardava `attributes['sito']` su ogni unità —
e quell'attributo lo scriveva **solo** l'importatore PostgreSQL, così
l'esportazione da SQLite veniva vuota. Di qui due test che girano **su
PostgreSQL**: è il lato che prima funzionava per caso, e che quindi non
accorgerebbe di una regressione se nessuno lo guardasse.

Due siti nello stesso database è la forma minima in cui un filtro può
sbagliare: con un sito solo, qualunque filtro — anche nessun filtro — dà
la risposta giusta.
"""
from __future__ import annotations

import json

import pytest
from sqlalchemy import text

from s3dgraphy.container import Container
from s3dgraphy.hdto import graphs_at
from s3dgraphy.sync.graphml_writer import _graphs_of_site, _site_place_of

from modules.s3dgraphy.em_export import EmExportError, export_site
from modules.s3dgraphy.sync.graph_projector import GraphProjector
from tests.sync.conftest_pg import PG_CONN_STR, pg_engine, clean_pg  # noqa: F401


#: I due siti stanno nello stesso comune: così la catena dei luoghi ha un
#: anello sopra il sito, ed è quello che prova il test del contenimento.
COMUNE = "Valdera"
US = {"Alfa": ("1", "2"), "Beta": ("90", "91")}


@pytest.fixture
def due_siti(clean_pg):  # noqa: F811
    """`us_table` e `site_table` con due siti, due US ciascuno."""
    with clean_pg.begin() as conn:
        for sito in US:
            conn.execute(
                text("INSERT INTO site_table (sito, comune) "
                     "VALUES (:s, :c)"), {"s": sito, "c": COMUNE})
            for us in US[sito]:
                conn.execute(
                    text("INSERT INTO us_table (sito, area, us, unita_tipo, "
                         "d_stratigrafica) VALUES (:s, '1', :u, 'US', "
                         "'strato')"), {"s": sito, "u": us})
    return clean_pg


@pytest.fixture
def due_grafi(due_siti):
    """I due grafi proiettati, come li farebbe l'esportazione."""
    return {s: GraphProjector().populate_graph(PG_CONN_STR, sito=s)
            for s in US}


def test_il_filtro_distingue_i_due_siti_su_pg(due_grafi):
    """Chiesto un sito, torna il suo grafo e non quello dell'altro.

    È il cuore del filtro: `_graphs_of_site` riceve **entrambi** i grafi e
    ne deve scegliere uno. Un filtro che tiene tutto, o che tiene il primo
    che capita, qui diventa rosso — mentre con un sito solo nel database
    passerebbe comunque.
    """
    assert _graphs_of_site(due_grafi, "Alfa") == ["Alfa"]
    assert _graphs_of_site(due_grafi, "Beta") == ["Beta"]


def test_il_filtro_passa_dal_luogo_del_sito_e_non_dagli_attributi(due_grafi):
    """Il grafo si trova dal **luogo** del sito, com'è dalla dev44.

    Il luogo è il `LocationNodeGroup` di livello `sito`
    (`hdto.site_place_id`), e `graphs_at` risale da lì.

    La seconda metà è la prova che il meccanismo è cambiato davvero, e si
    può fare **solo su PostgreSQL**: `attributes['sito']` sulle unità
    l'importatore PostgreSQL lo scrive (questo test lo verifica, prima di
    toglierlo), quello SQLite no — era proprio questa asimmetria a lasciare
    vuota l'esportazione da SQLite col vecchio `_filter_by_site`. Togliamo
    l'attributo da tutte le unità dei due grafi: il filtro deve rispondere
    uguale. Un filtro che lo guardasse ancora qui non troverebbe più niente.
    """
    luogo = _site_place_of(due_grafi["Alfa"], "Alfa")
    assert luogo is not None, "il sito deve avere il suo luogo"
    assert (luogo.attributes or {}).get("level") == "sito"

    trovati = graphs_at(Container(graphs=dict(due_grafi)), luogo)
    assert trovati == ["Alfa"]

    unita = [n for g in due_grafi.values() for n in g.nodes
             if type(n).__name__ == "StratigraphicUnit"]
    assert unita, "i siti hanno le loro unità"
    assert any((n.attributes or {}).get("sito") for n in unita), (
        "su PostgreSQL l'attributo c'è: è il presupposto di questo test")

    for n in unita:
        (n.attributes or {}).pop("sito", None)
    assert _graphs_of_site(due_grafi, "Alfa") == ["Alfa"], (
        "il filtro non deve dipendere da attributes['sito'] sulle unità")


def test_il_luogo_che_contiene_il_sito_trova_i_grafi_su_pg(due_grafi):
    """Chiesto il comune, tornano i siti che stanno dentro.

    `graphs_at` risale la catena `is_in_location`: è la promessa della sua
    docstring («a trench in an area of a site is found by asking for the
    site»), qui di un anello più in alto — due siti nello stesso comune.
    """
    comuni = [n for n in due_grafi["Alfa"].nodes
              if type(n).__name__ == "LocationNodeGroup"
              and (n.attributes or {}).get("level") == "comune"]
    assert len(comuni) == 1 and comuni[0].name == COMUNE

    trovati = graphs_at(Container(graphs=dict(due_grafi)), comuni[0])
    assert sorted(trovati) == ["Alfa", "Beta"]


def test_un_sito_che_non_c_e_tiene_tutti_i_grafi(due_grafi):
    """Un sito che non esiste **non** filtra niente: tornano tutti.

    Non è un test di una cosa giusta, è il recinto intorno a una cosa
    sorprendente, misurata. Quando il sito chiesto non ha un luogo — non
    sta in `site_table` — `_graphs_of_site` ha un ripiego inclusivo
    («the projection, made for `sito` only, is the site's»): giusto per
    `export_graphml`, che gli passa **un** grafo solo, sbagliato con un
    contenitore di più grafi, dove chiedere un sito inesistente restituisce
    gli altri.

    All'utente non arriva, perché la nostra esportazione si rifiuta prima
    (il test qui sotto). Quando il ripiego diventerà più stretto in
    s3dgraphy, è questo test che lo dirà.
    """
    assert sorted(_graphs_of_site(due_grafi, "Gamma")) == ["Alfa", "Beta"]


def test_l_export_del_sito_porta_solo_le_sue_us_su_pg(due_siti, tmp_path):
    """L'em.json di un sito, su PostgreSQL, non contiene l'altro sito.

    Il filtro vero è il `sito` passato a `populate_graph`: l'esportazione
    legge solo le righe di quel sito. Questo test guarda il file scritto,
    che è quello che l'utente porta in EMStudio.
    """
    percorso, n_nodi, _archi, _avvisi = export_site(
        PG_CONN_STR, "Alfa", str(tmp_path))

    with open(percorso, encoding="utf-8") as f:
        dati = json.load(f)
    testo = json.dumps(dati)
    nomi = {n["name"] for g in dati["graphs"].values()
            for n in g["nodes"] if n.get("node_type") == "US"}

    assert nomi == {"1", "2"}, "solo le US di Alfa"
    for altra in US["Beta"]:
        assert '"name": "%s"' % altra not in testo, (
            "l'US %s di Beta non deve entrare nell'em.json di Alfa" % altra)
    assert n_nodi > 0


def test_un_sito_che_non_c_e_non_si_esporta_su_pg(due_siti, tmp_path):
    """Chiesto un sito senza righe, l'esportazione si rifiuta e lo dice.

    È la guardia di `em_export.export_site`, e qui si misura su
    PostgreSQL con **altri** siti presenti nel database: senza di lei si
    scriverebbe un file che si apre e non contiene niente.
    """
    with pytest.raises(EmExportError, match="non ha righe in us_table"):
        export_site(PG_CONN_STR, "Gamma", str(tmp_path))
