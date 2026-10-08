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
    # Ogni riga ha il suo nodo; dal 2026-10-08 non sono tutti nodi
    # stratigrafici, perché le righe che l'Extended Matrix legge come
    # paradati (property, DOC, Extractor, Combinar) prendono la loro
    # classe — nel sito di esempio sono sei.
    from_rows = [n for n in graph.nodes
                 if (getattr(n, "attributes", None) or {}).get("us")]
    assert len(from_rows) == n_rows
    assert len(strat) == n_rows - 6


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


def _periodi(db, righe):
    """Riempie periodizzazione_table del DB di prova."""
    import sqlite3
    conn = sqlite3.connect(db)
    conn.executemany(
        "INSERT INTO periodizzazione_table (sito, periodo, fase,"
        " datazione_estesa, cron_iniziale, cron_finale)"
        " VALUES ('Alfa', ?, ?, ?, ?, ?)", righe)
    conn.commit()
    conn.close()


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


def _types_by_us(graph):
    return {(getattr(n, "attributes", None) or {}).get("us"): n.node_type
            for n in graph.nodes
            if (getattr(n, "attributes", None) or {}).get("us")}


def test_each_unit_gets_the_class_its_type_declares(tmp_path):
    """``node_type`` è quello che EMStudio legge per disegnare: una unità
    virtuale non può uscire come «US» col rettangolo bianco.

    Visto da Enzo sul demo (2026-10-08): tutte e 51 le unità del sito
    uscivano `US`, comprese USVA, USVB, SF e CON.
    """
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US"),
        dict(sito="Alfa", us="2", unita_tipo="USVA"),
        dict(sito="Alfa", us="3", unita_tipo="USVB"),
        dict(sito="Alfa", us="4", unita_tipo="SF"),
        dict(sito="Alfa", us="5", unita_tipo="CON"),
        dict(sito="Alfa", us="6", unita_tipo="USM"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert _types_by_us(graph) == {
        "1": "US", "2": "USVs", "3": "USVn", "4": "SF", "5": "BR",
        "6": "US"}
    usm = next(n for n in graph.nodes
               if (getattr(n, "attributes", None) or {}).get("us") == "6")
    assert usm.stratigraphic_kind == "masonry"     # USM = US + genere
    virtuale = next(n for n in graph.nodes
                    if (getattr(n, "attributes", None) or {}).get("us") == "2")
    assert virtuale.symbol != "white rectangle"    # la forma cambia davvero


def test_a_localized_us_code_is_not_a_stratigraphic_event(tmp_path):
    """SE è il codice tedesco per US, e STRATIGRAPHIC_CLASS_MAP['SE'] è
    StratigraphicEventNode: si canonicalizza PRIMA di scegliere la classe,
    o un sito intero diventa una fila di eventi."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="SE"),
        dict(sito="Alfa", us="2", unita_tipo="UE"),
        dict(sito="Alfa", us="3", unita_tipo="ΣΜ"),
        dict(sito="Alfa", us="4", unita_tipo="SU"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert set(_types_by_us(graph).values()) == {"US"}


def test_an_unknown_type_stays_a_plain_unit(tmp_path):
    """Un codice che nessuno conosce non deve far sparire l'unità né
    diventare un nodo senza tipo: resta una US."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="QUALCOSA"),
        dict(sito="Alfa", us="2", unita_tipo=""),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert _types_by_us(graph) == {"1": "US", "2": "US"}


def test_paradata_rows_are_not_stratigraphic_units(tmp_path):
    """Le righe di us_table nate da un round-trip yEd (property, DOC,
    Extractor, Combinar) sono paradati dell'Extended Matrix: in em.json
    devono portare il loro node_type, non «US». Restavano unità perché la
    forma la sceglieva il writer GraphML dall'attributo unita_tipo, e quel
    writer non c'è più (demolito in A4)."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="800", unita_tipo="property"),
        dict(sito="Alfa", us="4001", unita_tipo="DOC"),
        dict(sito="Alfa", us="400", unita_tipo="Extractor"),
        dict(sito="Alfa", us="900", unita_tipo="Combinar"),
        dict(sito="Alfa", us="1", unita_tipo="US"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert _types_by_us(graph) == {
        "800": "property", "4001": "document", "400": "extractor",
        "900": "combiner", "1": "US"}


def test_a_paradata_row_keeps_its_name_and_its_edges(tmp_path):
    """Cambiare classe non deve perdere né l'identità né i rapporti."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             rapporti="[['Copre', '400', '1', 'Alfa']]"),
        dict(sito="Alfa", us="400", unita_tipo="Extractor"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    estrattore = next(n for n in graph.nodes
                      if (getattr(n, "attributes", None) or {}).get("us")
                      == "400")
    assert estrattore.name == "1.Extractor400"
    assert estrattore.node_id
    ids = {n.node_id for n in graph.nodes}
    assert any(e.edge_target == estrattore.node_id
               or e.edge_source == estrattore.node_id for e in graph.edges)
    for e in graph.edges:
        assert e.edge_source in ids and e.edge_target in ids


def test_an_empty_column_does_not_become_a_property(tmp_path):
    """La colonna `inclusi` vuota di pyArchInit vale la stringa «[]», che
    a monte conta come valore pieno: 30 dei 219 nodi proprietà del sito
    demo dicevano «[]»."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US", inclusi="[]"),
        dict(sito="Alfa", us="2", unita_tipo="US", inclusi="['ceramica']"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa",
                                            column_properties=True)
    values = [getattr(n, "value", None) for n in graph.nodes
              if n.node_type == "property"]
    assert "[]" not in values
    assert "['ceramica']" in values


def test_a_paradata_row_is_not_swept_away_as_empty(tmp_path):
    """Una riga di us_table che è un paradato ha una classe PropertyNode
    ma nessun `value`: è dato dell'utente, non decorazione vuota."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="800", unita_tipo="property"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert _types_by_us(graph) == {"800": "property"}


def test_a_paradatum_has_no_paradata_of_its_own(tmp_path):
    """Visto in EMStudio il 2026-10-08: una riga che è un paradato
    (property, DOC, Extractor, Combinar) portava con sé i nodi nati dalle
    sue colonne — «Interpretation», la documentazione — e il datamodel
    protestava («has_property is not allowed towards a property»). Un
    paradato non ha paradati."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="800", unita_tipo="property",
             d_interpretativa="materiale pietra dura",
             documentazione="[['Fotografie', 'Si']]"),
        dict(sito="Alfa", us="1", unita_tipo="US",
             d_interpretativa="strato di crollo"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa",
                                            column_properties=True)
    paradato = next(n for n in graph.nodes
                    if (getattr(n, "attributes", None) or {}).get("us")
                    == "800")
    uscenti = [e.edge_type for e in graph.edges
               if e.edge_source == paradato.node_id]
    assert "has_property" not in uscenti, uscenti
    assert "has_documentation" not in uscenti, uscenti
    # l'unità vera tiene le sue
    unita = next(n for n in graph.nodes
                 if (getattr(n, "attributes", None) or {}).get("us") == "1")
    assert any(e.edge_type == "has_property" and e.edge_source == unita.node_id
               for e in graph.edges)


def test_the_same_documentation_is_one_node_for_the_whole_site(tmp_path):
    """«Fotografie: Sì» nella scheda non è un documento diverso per ogni
    US: è la stessa voce di spunta. L'importer ne faceva un nodo per
    unità e EMStudio contava i nomi doppi (35 «Fotografie» identiche sul
    demo, 2026-10-08). Uno solo, appeso a tutte le unità che ce l'hanno."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             documentazione="[['Fotografie', 'Si'], ['Planimetrie', 'Si']]"),
        dict(sito="Alfa", us="2", unita_tipo="US",
             documentazione="[['Fotografie', 'Si']]"),
        dict(sito="Alfa", us="3", unita_tipo="US",
             documentazione="[['Sezioni', 'Si']]"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    docs = [n for n in graph.nodes if n.node_type == "document"]
    assert sorted(n.name for n in docs) == [
        "Fotografie", "Planimetrie", "Sezioni"]
    fotografie = next(n for n in docs if n.name == "Fotografie")
    chi_la_cita = {e.edge_source for e in graph.edges
                   if e.edge_target == fotografie.node_id
                   and e.edge_type == "has_documentation"}
    assert len(chi_la_cita) == 2, chi_la_cita
    ids = {n.node_id for n in graph.nodes}
    for e in graph.edges:
        assert e.edge_source in ids and e.edge_target in ids


def test_the_sheet_columns_do_not_become_a_cloud_of_nodes(tmp_path):
    """Osservato da Enzo guardando la matrice: «se sono 56 US devono
    essere 56 nodi, non 400».

    L'importer fa un nodo proprietà per ogni colonna piena di ogni US
    (interpretazione, colore, consistenza, inclusi, stato di
    conservazione…): 190 nodi sul sito demo, che ripetono quello che
    l'unità già porta nel suo `data`, non hanno epoca — quindi la
    matrice li ammucchia nella prima fascia — e seppelliscono la
    stratigrafia. Di norma non viaggiano; chi li vuole li chiede."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             d_interpretativa="strato di crollo", colore="bruno",
             consistenza="compatta"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert [n for n in graph.nodes if n.node_type == "property"] == []
    unita = next(n for n in graph.nodes
                 if (getattr(n, "attributes", None) or {}).get("us") == "1")
    # il dato non si perde: resta sull'unità
    assert unita.attributes["d_interpretativa"] == "strato di crollo"

    con_proprieta = GraphProjector().populate_graph(
        db, sito="Alfa", column_properties=True)
    nomi = {n.name for n in con_proprieta.nodes
            if n.node_type == "property"}
    assert "Interpretation" in nomi and "Color" in nomi


def test_a_paradata_row_survives_the_cloud_sweep(tmp_path):
    """Una riga di us_table che È una proprietà non è una colonna
    rispecchiata: resta."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="800", unita_tipo="property",
             d_interpretativa="materiale pietra dura"),
        dict(sito="Alfa", us="1", unita_tipo="US",
             rapporti="[['Copre', '800', '1', 'Alfa']]"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    assert _types_by_us(graph) == {"800": "property", "1": "US"}


def test_only_rows_of_the_sheet_change_class(tmp_path):
    """Dalla review: il passaggio riclassificava QUALUNQUE nodo con un
    `unita_tipo` negli attributi, e la fascia di un'area — che
    l'assegnazione degli attributi può rivendicare per omonimia quando
    manca il node_uuid — diventava una unità virtuale. Solo le righe
    della scheda cambiano classe."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", area="1", settore="B", us="1", unita_tipo="USVA",
             node_uuid=None),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    gruppi = [n for n in graph.nodes
              if str(n.node_id).startswith("loc::")]
    for gruppo in gruppi:
        assert type(gruppo).__name__ == "LocationNodeGroup", (
            gruppo.node_id, type(gruppo).__name__)


def test_a_retyped_node_keeps_nothing_of_its_old_class(tmp_path):
    """Dalla review: le classi paradato non hanno `symbol` né `label`, e
    il nodo si teneva «white rectangle» e «US (or SU)» della US — proprio
    le due stringhe che erano il sintomo di partenza."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="800", unita_tipo="property"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    paradato = next(n for n in graph.nodes
                    if (getattr(n, "attributes", None) or {}).get("us")
                    == "800")
    for campo in ("symbol", "label", "detailed_description",
                  "stratigraphic_kind", "source_code", "definition"):
        assert not hasattr(paradato, campo), campo
    assert isinstance(getattr(paradato, "data", None), dict)


def test_a_stratigraphic_verb_towards_a_paradatum_is_not_published(tmp_path):
    """Dalla review: «Copre 400» verso un estrattore produce un arco che
    il datamodel dell'Extended Matrix rifiuta, e l'arco disegnato
    dall'archeologo sparirebbe in silenzio. Si declassa e lo si dice."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             rapporti="[['Copre', '400', '1', 'Alfa']]"),
        dict(sito="Alfa", us="400", unita_tipo="Extractor"),
    ])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    estrattore = next(n for n in graph.nodes
                      if (getattr(n, "attributes", None) or {}).get("us")
                      == "400")
    verso = [e.edge_type for e in graph.edges
             if e.edge_target == estrattore.node_id
             or e.edge_source == estrattore.node_id]
    assert "overlies" not in verso, verso
    assert any("Copre" in str(w) or "400" in str(w)
               for w in (getattr(graph, "warnings", None) or [])), \
        getattr(graph, "warnings", None)


def _epoche_di(graph, us):
    unita = next(n for n in graph.nodes
                 if (getattr(n, "attributes", None) or {}).get("us") == us)
    fuori = {}
    for e in graph.edges:
        if e.edge_source == unita.node_id and e.edge_type in (
                "has_first_epoch", "survive_in_epoch"):
            nodo = next((n for n in graph.nodes
                         if n.node_id == e.edge_target), None)
            fuori[e.edge_type] = getattr(nodo, "name", None)
    return fuori


def test_every_unit_says_where_it_stops_existing(tmp_path):
    """In una matrice dell'Extended Matrix ogni unità dice DOVE NASCE e
    FINO A DOVE sopravvive: nella matrice yEd di riferimento
    (tests/sync/fixtures/mini_volterra_baseline_ai03.graphml) le cinque US
    hanno tutte e due gli archi. Noi mandavamo solo il primo, e chi
    disegna non sapendo dove l'unità si ferma la portava fino alla fascia
    più recente — è quello che Enzo vede in EMStudio.

    Quando la scheda non dichiara il periodo finale, l'unità sopravvive
    nella propria epoca e basta: è quello che la scheda dice.
    """
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             periodo_iniziale="2", fase_iniziale="1"),
    ])
    _periodi(db, [("2", "1", "XV secolo", 1451, 1499)])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    epoche = _epoche_di(graph, "1")
    assert epoche.get("has_first_epoch") == "XV secolo"
    assert epoche.get("survive_in_epoch") == "XV secolo"


def test_a_declared_final_period_is_respected(tmp_path):
    """Chi dichiara il periodo finale sopravvive fin lì, non oltre."""
    db = _mini_db(tmp_path, [
        dict(sito="Alfa", us="1", unita_tipo="US",
             periodo_iniziale="2", fase_iniziale="1",
             periodo_finale="1", fase_finale="1"),
    ])
    _periodi(db, [("2", "1", "XV secolo", 1451, 1499),
                  ("1", "1", "Età moderna", 1600, 1799)])
    graph = GraphProjector().populate_graph(db, sito="Alfa")
    epoche = _epoche_di(graph, "1")
    assert epoche.get("has_first_epoch") == "XV secolo"
    assert epoche.get("survive_in_epoch") == "Età moderna"
