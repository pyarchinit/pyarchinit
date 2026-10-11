"""Il codice dello studio: quello con cui Blender riattacca i proxy.

`GT16.1.USM100`: il prefisso è il codice dello studio, e **non deve
derivare mai** — se cambia, i proxy di Blender puntano a cose che non ci
sono più. Parole di E.D. l'11 ottobre 2026, dev45.

pyArchInit non ha un codice breve dello scavo da mandare: `site_table` ha
undici colonne e i soli identificativi sono `id_sito`, che è un contatore,
ed `entity_uuid`. Aggiungerne uno vorrebbe dire una migrazione automatica
su ogni database esistente, e l'utente l'ha escluso. Si prende quindi la
strada prevista per questo caso: la libreria **propone** il codice una
volta e lo marca `code_proposed` finché una persona non lo conferma.

Il nodo della questione, e la ragione di questi test: noi rigeneriamo
l'em.json dal database **ogni volta**, e non rileggiamo mai il precedente.
«Proposto una volta e poi tenuto» per noi vale solo se la proposta è
deterministica. Lo è: iniziali del sito più le due cifre dell'anno nella
`date` dello studio, e come anno si sceglie il **primo** di `anno_scavo`,
che non si sposta quando si aggiunge una campagna.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.s3dgraphy.sync.graph_projector import GraphProjector


SCHEMA = """
CREATE TABLE site_table (
    id_sito INTEGER PRIMARY KEY, sito TEXT, nazione TEXT, regione TEXT,
    comune TEXT, provincia TEXT, descrizione TEXT, entity_uuid TEXT);
CREATE TABLE periodizzazione_table (
    id_perfas INTEGER PRIMARY KEY, sito TEXT, periodo INTEGER, fase TEXT,
    cron_iniziale INTEGER, cron_finale INTEGER, descrizione TEXT,
    datazione_estesa TEXT, cont_per INTEGER, entity_uuid TEXT);
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT,
    unita_tipo TEXT, d_stratigrafica TEXT, d_interpretativa TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT, periodo_finale TEXT,
    fase_finale TEXT, datazione TEXT, rapporti TEXT, node_uuid TEXT,
    attivita TEXT, struttura TEXT, settore TEXT, ambient TEXT,
    saggio TEXT, quad_par TEXT, documentazione TEXT, anno_scavo TEXT,
    UNIQUE(sito, area, us, unita_tipo));
"""


def _db(cartella, sito, anni, saggi=("",)):
    """Un database minimo con un sito, le sue campagne e i suoi saggi."""
    percorso = Path(cartella) / "t.sqlite"
    conn = sqlite3.connect(percorso)
    conn.executescript(SCHEMA)
    conn.execute("INSERT INTO site_table (sito, comune) VALUES (?, 'Volterra')",
                 (sito,))
    conn.execute(
        "INSERT INTO periodizzazione_table (sito, periodo, fase,"
        " cron_iniziale, cron_finale, datazione_estesa)"
        " VALUES (?, 1, '1', -100, 100, 'I secolo')", (sito,))
    n = 0
    for saggio in saggi:
        for anno in anni:
            n += 1
            conn.execute(
                "INSERT INTO us_table (sito, area, us, unita_tipo,"
                " d_stratigrafica, periodo_iniziale, fase_iniziale,"
                " rapporti, node_uuid, saggio, anno_scavo, documentazione)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (sito, "1", str(n), "US", "strato", "1", "1", "[]",
                 "019f8043-0000-7000-8000-%012d" % n, saggio, str(anno), ""))
    conn.commit()
    conn.close()
    return "sqlite:///%s" % percorso


def _studio(graph):
    for nodo in graph.nodes:
        if getattr(nodo, "node_type", None) == "study":
            return nodo
    return None


def test_il_codice_sono_le_iniziali_del_sito_e_l_anno(tmp_path):
    """«Scavo archeologico» scavato dal 2012 dà `SA12`."""
    url = _db(tmp_path, "Scavo archeologico", (2012, 2013, 2022))
    g = GraphProjector().populate_graph(url, sito="Scavo archeologico")
    studio = _studio(g)
    assert studio is not None, "ogni grafo proiettato dichiara il suo studio"
    assert studio.data.get("code") == "SA12", studio.data


def test_l_anno_e_il_primo_della_prima_campagna(tmp_path):
    """E non l'ultimo: aggiungere una campagna non cambia il codice.

    È la proprietà che tiene in piedi i proxy di Blender. Con l'ultimo
    anno, una campagna nuova cambierebbe il prefisso di ogni proxy.
    """
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    prima = _db(tmp_path / "a", "Scavo archeologico", (2012, 2013))
    poi = _db(tmp_path / "b", "Scavo archeologico", (2012, 2013, 2026))
    codici = []
    for url in (prima, poi):
        g = GraphProjector().populate_graph(url, sito="Scavo archeologico")
        codici.append(_studio(g).data.get("code"))
    assert codici == ["SA12", "SA12"], codici


def test_il_codice_e_marcato_come_proposta(tmp_path):
    """Finché una persona non lo conferma, è una proposta e lo dice."""
    url = _db(tmp_path, "Scavo archeologico", (2012,))
    g = GraphProjector().populate_graph(url, sito="Scavo archeologico")
    assert _studio(g).data.get("code_proposed") is True


def test_due_proiezioni_di_fila_danno_lo_stesso_codice(tmp_path):
    """La proprietà che conta: rigenerare non sposta il codice.

    Noi l'em.json lo rifacciamo dal database ogni volta e non rileggiamo
    mai il precedente, quindi «proposto una volta e poi tenuto» vale solo
    se la proposta è deterministica.
    """
    url = _db(tmp_path, "Scavo archeologico", (2012, 2022))
    codici = [
        _studio(GraphProjector().populate_graph(
            url, sito="Scavo archeologico")).data.get("code")
        for _ in range(3)]
    assert len(set(codici)) == 1, codici
    assert codici[0] == "SA12"


def test_senza_anno_resta_la_sola_sigla(tmp_path):
    """Un sito senza `anno_scavo` ha ancora un codice stabile."""
    url = _db(tmp_path, "Scavo archeologico", ("",))
    g = GraphProjector().populate_graph(url, sito="Scavo archeologico")
    assert _studio(g).data.get("code") == "SA", _studio(g).data


def test_le_particelle_del_nome_non_contano(tmp_path):
    """«Grotta di Tiberio» dà `GT16`, non `GDT16`: è l'esempio con cui
    E.D. descrive la regola, e il «di» resta fuori."""
    url = _db(tmp_path, "Grotta di Tiberio", (2016,))
    g = GraphProjector().populate_graph(url, sito="Grotta di Tiberio")
    assert _studio(g).data.get("code") == "GT16", _studio(g).data


def test_un_rapporto_fra_due_saggi_non_si_perde(tmp_path):
    """Con un grafo per saggio, il rapporto che li attraversa resta un link.

    `populate_container` divide il sito in un grafo per saggio; un rapporto
    fra unità di saggi diversi non può essere un arco, perché i due nodi
    stanno in grafi diversi, e diventa un **link** con l'indirizzo
    «grafo → nodo» (dev45).
    """
    percorso = Path(tmp_path) / "t.sqlite"
    conn = sqlite3.connect(percorso)
    conn.executescript(SCHEMA)
    conn.execute("INSERT INTO site_table (sito, comune)"
                 " VALUES ('Scavo a saggi', 'Volterra')")
    conn.execute(
        "INSERT INTO periodizzazione_table (sito, periodo, fase,"
        " cron_iniziale, cron_finale, datazione_estesa)"
        " VALUES ('Scavo a saggi', 1, '1', -100, 100, 'I secolo')")
    righe = (("1", "Saggio A", '[["Copre", "2", "1", "Scavo a saggi"]]'),
             ("2", "Saggio A", "[]"),
             # la 3 sta nel saggio B e copre la 2, che sta nel saggio A
             ("3", "Saggio B", '[["Copre", "2", "1", "Scavo a saggi"]]'),
             ("4", "Saggio B", "[]"))
    for i, (us, saggio, rapporti) in enumerate(righe, start=1):
        conn.execute(
            "INSERT INTO us_table (sito, area, us, unita_tipo,"
            " d_stratigrafica, periodo_iniziale, fase_iniziale, rapporti,"
            " node_uuid, saggio, anno_scavo, documentazione)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("Scavo a saggi", "1", us, "US", "strato", "1", "1", rapporti,
             "019f8043-0000-7000-8000-%012d" % i, saggio, "2016", ""))
    conn.commit()
    conn.close()

    contenitore = GraphProjector().populate_container(
        "sqlite:///%s" % percorso, "Scavo a saggi", groups=["saggio"])
    grafi = getattr(contenitore, "graphs", None) or {}
    assert len(grafi) >= 2, sorted(grafi)
    assert any("Saggio A" in k for k in grafi), sorted(grafi)
    assert any("Saggio B" in k for k in grafi), sorted(grafi)

    links = [l for g in grafi.values()
             for l in (getattr(g, "links", None) or [])]
    assert links, "il rapporto fra i due saggi deve restare come link"
    link = links[0]
    assert link["edge_type"] == "overlies", link
    assert isinstance(link["target"], dict) and "graph_id" in link["target"], \
        link
