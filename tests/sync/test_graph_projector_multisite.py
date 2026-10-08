"""A projection is ONE site (I1, one-bridge final review 2026-10-07).

On SQLite the library runs PyArchInitImporter with no site filter and
its post-filter keeps every dev40 node (they carry no attributes['sito']):
projecting one site of a multi-site DB returned every other site's units
too — 210 strat nodes instead of the site's own rows on the sample DB.
The wrapper must prune what the attribute pass did not claim.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

from modules.s3dgraphy.sync.graph_projector import GraphProjector  # noqa: E402

SAMPLE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"


@pytest.fixture
def multisite_db(tmp_path):
    dst = tmp_path / "sample.sqlite"
    shutil.copy2(SAMPLE_DB, dst)
    from scripts.migrations._2026_05_node_uuid_backfill_lib import (
        add_columns, backfill_uuids)
    add_columns(dst)
    backfill_uuids(dst)
    return dst


def test_projecting_one_site_keeps_only_that_sites_units(multisite_db):
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
    graph = GraphProjector().populate_graph(multisite_db, sito=SITO)
    strat = [n for n in graph.nodes if isinstance(n, StratigraphicNode)]
    foreign = [n for n in strat
               if (getattr(n, "attributes", None) or {}).get("sito") != SITO]
    assert not foreign, (
        "%d foreign/unclaimed strat nodes, e.g. %s"
        % (len(foreign), [n.name for n in foreign[:5]]))
    conn = sqlite3.connect(multisite_db)
    n_rows = conn.execute(
        "SELECT COUNT(*) FROM us_table WHERE sito=?", (SITO,)).fetchone()[0]
    conn.close()
    assert len(strat) == n_rows


def test_pruning_takes_the_orphans_with_it(multisite_db):
    """Property/epoch/group nodes that only served foreign units must not
    survive as dangling decoration."""
    graph = GraphProjector().populate_graph(multisite_db, sito=SITO)
    ids = {n.node_id for n in graph.nodes}
    for e in graph.edges:
        assert e.edge_source in ids and e.edge_target in ids
    by_type = {}
    for n in graph.nodes:
        by_type.setdefault(type(n).__name__, []).append(n)
    # the sample ships ~10 sites; one site's projection must not carry
    # the whole DB's property cloud (was 1010 pre-fix)
    assert len(by_type.get("PropertyNode", [])) < 300


def test_only_the_sites_epochs_travel(multisite_db):
    """Scoperto da Enzo sul demo (2026-10-07, EMStudio): le unità erano
    filtrate ma le EPOCHE no — 57 epoche in dieci lingue (le
    periodizzazioni degli altri siti) sopravvivevano alla potatura perché
    tengono archi fra sé e le proprie date. L'importer le firma per sito
    (epoch::sito::p::f): quelle d'altri siti non devono viaggiare."""
    import sqlite3
    graph = GraphProjector().populate_graph(multisite_db, sito=SITO)
    epochs = [n for n in graph.nodes if type(n).__name__ == "EpochNode"]
    foreign = [n.node_id for n in epochs
               if str(n.node_id).startswith("epoch::")
               and str(n.node_id).split("::")[1] != SITO]
    assert foreign == [], foreign[:5]
    conn = sqlite3.connect(multisite_db)
    n_periods = conn.execute(
        "SELECT COUNT(DISTINCT periodo || '/' || fase) "
        "FROM periodizzazione_table WHERE sito=?", (SITO,)).fetchone()[0]
    conn.close()
    assert len(epochs) <= n_periods + 2, (
        "%d epoche per %d periodi del sito" % (len(epochs), n_periods))


#: L'ordine delle colonne per le righe passate come tupla (forma storica).
_MINI_COLUMNS = ("sito", "area", "us", "unita_tipo", "node_uuid", "rapporti")


def _mini_db(tmp_path, rows):
    """Un DB minimo con le tre tabelle che il proiettore legge.

    Una riga è una tupla nell'ordine di ``_MINI_COLUMNS`` (forma storica)
    oppure un dizionario colonna→valore, che è più leggibile quando la
    prova riguarda una colonna sola (``documentazione``, ``inclusi``).
    """
    import sqlite3
    db = tmp_path / "mini.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, area TEXT DEFAULT '1', us TEXT, unita_tipo TEXT,
        node_uuid TEXT, rapporti TEXT,
        periodo_iniziale TEXT, fase_iniziale TEXT,
        periodo_finale TEXT, fase_finale TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT,
        attivita TEXT, struttura TEXT, settore TEXT, ambient TEXT,
        saggio TEXT, quad_par TEXT, documentazione TEXT,
        inclusi TEXT, colore TEXT, consistenza TEXT,
        other_locations TEXT)""")
    conn.execute("""CREATE TABLE periodizzazione_table (
        id_perfas INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT, periodo TEXT, fase TEXT,
        cron_iniziale INTEGER, cron_finale INTEGER,
        descrizione TEXT, datazione_estesa TEXT)""")
    conn.execute("""CREATE TABLE site_table (
        id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT,
        nazione TEXT, regione TEXT, provincia TEXT, comune TEXT)""")
    for n, row in enumerate(rows, start=1):
        values = (dict(row) if isinstance(row, dict)
                  else dict(zip(_MINI_COLUMNS, row)))
        values.setdefault("area", "1")
        values.setdefault("node_uuid", "u-%d" % n)
        columns = sorted(values)
        conn.execute(
            "INSERT INTO us_table (%s) VALUES (%s)"
            % (", ".join(columns), ", ".join("?" for _ in columns)),
            [values[c] for c in columns])
    conn.commit(); conn.close()
    return db


INVERSE_TYPES = {"is_overlain_by", "is_cut_by", "is_filled_by",
                 "is_abutted_by", "is_leaned_on_by", "is_before"}


def test_reciprocal_rapporti_become_one_forward_edge(tmp_path):
    """Visto negli avvisi di EMStudio sul demo (datamodel:
    «is_overlain_by … is not allowed towards a US»): il projector
    emetteva i tipi INVERSI tal quali, e la coppia Copre/Coperto da
    faceva due archi. Come nell'adapter della stanza: piega nel tipo
    diretto con gli estremi scambiati, un arco per relazione."""
    db = _mini_db(tmp_path, [
        ("S", "1", "1", "US", "u-1", '[["Copre", "2", "1", "S"]]'),
        ("S", "1", "2", "US", "u-2", '[["Coperto da", "1", "1", "S"]]'),
    ])
    graph = GraphProjector().populate_graph(db, sito="S")
    rap = [e for e in graph.edges
           if str(getattr(e, "edge_id", "")).startswith("rap_")]
    assert len(rap) == 1, [(e.edge_type, e.edge_id) for e in rap]
    edge = rap[0]
    assert edge.edge_type == "overlies"
    by_id = {n.node_id: n for n in graph.nodes}
    assert (by_id[edge.edge_source].attributes or {}).get("us") == "1"
    assert (by_id[edge.edge_target].attributes or {}).get("us") == "2"
    assert not [e for e in graph.edges
                if getattr(e, "edge_type", None) in INVERSE_TYPES]


def test_a_symmetric_relation_declared_twice_is_one_edge(tmp_path):
    db = _mini_db(tmp_path, [
        ("S", "1", "1", "US", "u-1", '[["Uguale a", "2", "1", "S"]]'),
        ("S", "1", "2", "US", "u-2", '[["Uguale a", "1", "1", "S"]]'),
    ])
    graph = GraphProjector().populate_graph(db, sito="S")
    eq = [e for e in graph.edges if getattr(e, "edge_type", None) == "equals"]
    assert len(eq) == 1, [(e.edge_type, e.edge_id) for e in eq]


def test_only_the_sites_own_rows_are_imported(tmp_path):
    """Due siti che numerano le US allo stesso modo non si fondono.

    Il nome del nodo non contiene il sito
    (``{area}.{settore}.{unita_tipo}{us}``): senza filtro alla sorgente le
    due righe collassano su un nodo solo, che si porta dietro la
    documentazione di entrambi i siti. Misurato sul demo il 2026-10-08: il
    sito italiano usciva con «Fotografie» E «Photographies», perché il
    sito francese numera le sue US come l'italiano.
    """
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             documentazione="[['Fotografie', 'Si']]"),
        dict(sito="Beta", us="1", unita_tipo="US",
             documentazione="[['Photographies', 'Si']]"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    units = [n for n in graph.nodes
             if type(n).__name__ == "StratigraphicUnit"]
    assert len(units) == 1, [n.name for n in units]
    docs = sorted(n.name for n in graph.nodes
                  if type(n).__name__ == "DocumentNode")
    assert docs == ["Fotografie"], docs


def test_a_single_site_db_is_unchanged_by_the_filter(tmp_path):
    """Il filtro è una restrizione: su un DB a sito unico non toglie nulla."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US"),
        dict(sito="Alfa", us="2", unita_tipo="US"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert sorted(n.name for n in graph.nodes
                  if type(n).__name__ == "StratigraphicUnit") == [
        "1.US1", "1.US2"]


def test_two_projections_at_once_keep_their_own_site(tmp_path):
    """Il filtro si installa su un simbolo di modulo: due proiezioni
    insieme (una in QgsTask, una sul thread GUI) non devono scambiarsi i
    siti."""
    import threading
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US"),
        dict(sito="Beta", us="2", unita_tipo="US"),
    ])
    out = {}

    def run(sito):
        graph = GraphProjector().populate_graph(db, sito=sito)
        out[sito] = sorted(n.name for n in graph.nodes
                           if type(n).__name__ == "StratigraphicUnit")

    threads = [threading.Thread(target=run, args=(s,))
               for s in ("Alfa", "Beta")]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert out == {"Alfa": ["1.US1"], "Beta": ["1.US2"]}
