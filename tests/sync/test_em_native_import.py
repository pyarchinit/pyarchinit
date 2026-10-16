"""Importare un em.json scritto da EMStudio (non da pyArchInit) in un
database vuoto (Enzo, 16 ottobre 2026, con TempluMare_v3.2.em.json):

* solo le unità stratigrafiche e i paradati (proprietà, estrattori,
  combinatori, documenti) diventano schede; risorse, file, modelli 3D,
  forme e processi del gemello digitale no (erano diventati 1064 «US»);
* i rapporti collegano anche virtuali, reperti e paradati, con i segni
  che l'esportazione rilegge negli archi giusti;
* le epoche di EMStudio (id generici, solo nome e date) riempiono la
  periodizzazione, e le unità prendono periodo iniziale e finale;
* l'attività va nella colonna «attivita», non nei rapporti;
* la scheda sito si crea anche con il database vuoto.
"""
from __future__ import annotations

import ast
import json
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
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("s3dgraphy")

TEMPLATE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite"
SITO = "Tempio di prova"


def _nodo(nid, tipo, nome, descrizione=None, **data):
    n = {"id": nid, "node_type": tipo, "name": nome, "data": dict(data)}
    if descrizione:
        n["description"] = descrizione
    return n


def _arco(src, tipo, dst):
    return {"id": "%s_%s_%s" % (src, tipo, dst), "edge_type": tipo, "source": src, "target": dst}


def _em_json(tmp_path):
    """Un grafo come lo scrive EMStudio: id generici, niente attributi
    pyArchInit, epoche con solo nome e date."""
    nodi = [
        _nodo("g-root", "graph", "Graph"),
        _nodo("geo", "geo_position", "geo_position", epsg=31700, shift_x=327300.0, shift_y=448370.0),
        _nodo("aut", "author", "Autrice Prova", name="Autrice", surname="Prova"),
        _nodo("ep-a", "EpochNode", "II A.D.", start_time=100, end_time=199),
        _nodo("ep-b", "EpochNode", "Post antiquity", start_time=200, end_time=1800),
        _nodo("u1", "US", "US1", "Strato di crollo"),
        _nodo("u2", "US", "US2", "Pavimento"),
        _nodo("un", "USN", "USN3", "Taglio della fossa"),
        _nodo("ut", "USNt", "USNt4", "Superficie neutra"),
        _nodo("v1", "USVn", "105", "Architrave ricostruito"),
        _nodo("v2", "USVn", "106", "Colonna ricostruita"),
        _nodo("vs", "serUSVn", "200", "Serie di colonne"),
        _nodo("sf", "SF", "T21", "Frammento di colonna"),
        _nodo("vsf", "VSF", "VT21", "Colonna completata"),
        _nodo("p1", "property", "height", "Altezza 5.14 / 4 = 1.285"),
        _nodo("p2", "property", "height", "Altezza misurata 2.10"),
        _nodo("p3", "property", "Material", "Pietra calcarea"),
        _nodo("ex", "extractor", "D.05.02", "Architrave = 1/4 della colonna"),
        _nodo("co", "combiner", "C.05", "Architrave compatibile con legno"),
        _nodo("usd", "USD", "USD2", "Pavimento da documento"),
        _nodo("doc", "document", "D.05", "Relazione di scavo 2013", url="D.05 Relazione 2013.pdf"),
        _nodo("act", "ActivityNodeGroup", "VAct.03 Architrave"),
        _nodo("pg", "ParadataNodeGroup", "PD 105"),
        _nodo("res", "resource", "Link alla scheda", url="http://example.org/scheda"),
        _nodo("rf", "resource_file", "colonna.obj", url="../RB/colonna.obj", media_type="model/obj"),
        _nodo("rm", "representation_model", "Colonna_BAKE"),
        _nodo("ss", "semantic_shape", "Shape for USV105"),
        _nodo("dtc", "dtc_process", "LOD generation of colonna"),
    ]
    archi = [
        _arco("u1", "overlies", "u2"),
        _arco("un", "cuts", "u2"),
        _arco("usd", "abuts", "u1"),
        _arco("v1", "is_after", "v2"),
        _arco("v2", "is_after", "u1"),
        _arco("vs", "is_after", "v2"),
        _arco("sf", "is_part_of", "vsf"),
        _arco("v1", "has_property", "p1"),
        _arco("sf", "has_property", "p2"),
        _arco("v2", "has_property", "p3"),
        _arco("p1", "has_data_provenance", "ex"),
        _arco("p3", "has_data_provenance", "co"),
        _arco("co", "combines", "ex"),
        _arco("ex", "extracted_from", "doc"),
        _arco("v1", "is_in_activity", "act"),
        _arco("v2", "is_in_activity", "act"),
        _arco("p1", "is_in_paradata_nodegroup", "pg"),
        _arco("doc", "has_linked_resource", "res"),
        _arco("res", "has_file", "rf"),
        _arco("rm", "has_linked_resource", "res"),
        _arco("ss", "has_linked_resource", "res"),
        _arco("dtc", "dtc_had_output", "res"),
        _arco("doc", "has_author", "aut"),
        _arco("u1", "has_first_epoch", "ep-b"),
        _arco("u2", "has_first_epoch", "ep-a"),
        _arco("u2", "survive_in_epoch", "ep-b"),
        _arco("un", "has_first_epoch", "ep-a"),
        _arco("v1", "has_first_epoch", "ep-a"),
        _arco("v2", "has_first_epoch", "ep-a"),
        _arco("sf", "has_first_epoch", "ep-a"),
    ]
    contenitore = {
        "version": "1.0",
        "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
        "active_graph_id": "g-1",
        "graphs": {"g-1": {"graph_id": "g-1", "name": "Tempio", "nodes": nodi, "edges": archi}},
    }
    percorso = tmp_path / "tempio.em.json"
    percorso.write_text(json.dumps(contenitore), encoding="utf-8")
    return percorso


@pytest.fixture
def importato(tmp_path):
    """Il database vuoto del plugin, con l'em.json importato una volta."""
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    sorgente = _em_json(tmp_path)
    grafo, _ = read_graph_for_import(str(sorgente))
    esito = GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    return db, sorgente, esito


def _righe(db):
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    righe = {(r["us"], r["unita_tipo"]): dict(r) for r in con.execute(
        "SELECT * FROM us_table WHERE sito = ?", (SITO,))}
    con.close()
    return righe


def _rapporti(riga):
    return [tuple(r[:2]) for r in ast.literal_eval(riga["rapporti"] or "[]")]


def test_solo_unita_e_paradati_diventano_schede(importato):
    db, _, _ = importato
    tipi = sorted(ut for _us, ut in _righe(db))
    assert tipi == sorted(["US", "US", "USN", "USNt", "USVn", "USVn", "serUSVn", "SF", "VSF", "USD",
                           "property", "property", "property", "Extractor", "Combinar", "DOC"])


def test_le_proprieta_omonime_restano_distinte(importato):
    db, _, _ = importato
    righe = _righe(db)
    assert ("height (105)", "property") in righe and ("height (T21)", "property") in righe
    assert righe[("height (105)", "property")]["descrizione"] == "Altezza 5.14 / 4 = 1.285"
    assert righe[("height (T21)", "property")]["descrizione"] == "Altezza misurata 2.10"
    assert ("Material", "property") in righe                     # nome unico: resta com'è


def test_i_rapporti_collegano_virtuali_reperti_e_paradati(importato):
    db, _, _ = importato
    r = _righe(db)
    assert ("Copre", "2") in _rapporti(r[("1", "US")])
    assert ("Taglia", "2") in _rapporti(r[("3", "USN")])           # fisico fra tipi diversi: per esteso
    v1 = _rapporti(r[("105", "USVn")])
    assert (">", "106") in v1                                      # prima/dopo fra virtuali
    assert (">>", "height (105)") in v1                            # la sua proprietà
    assert (">", "1") in _rapporti(r[("106", "USVn")])
    assert (">", "106") in _rapporti(r[("200", "serUSVn")])
    assert (">>", "VT21") in _rapporti(r[("T21", "SF")])          # parte di
    assert (">>", "05.02") in _rapporti(r[("height (105)", "property")])
    assert (">>", "C.05") in _rapporti(r[("Material", "property")])
    assert (">>", "05.02") in _rapporti(r[("C.05", "Combinar")])
    assert ("Si appoggia a", "1") in _rapporti(r[("USD2", "USD")])
    assert (">>", "05") in _rapporti(r[("05.02", "Extractor")])
    tutti = [t for riga in r.values() for _l, t in _rapporti(riga)]
    assert "VAct.03 Architrave" not in tutti and "Link alla scheda" not in tutti


def test_l_attivita_va_nella_sua_colonna(importato):
    db, _, _ = importato
    r = _righe(db)
    assert r[("105", "USVn")]["attivita"] == "VAct.03 Architrave"
    assert r[("106", "USVn")]["attivita"] == "VAct.03 Architrave"


def test_le_descrizioni_e_il_documento_arrivano(importato):
    db, _, _ = importato
    r = _righe(db)
    assert r[("1", "US")]["descrizione"] == "Strato di crollo"
    assert r[("05", "DOC")]["documentazione"] == "D.05 Relazione 2013.pdf"


def test_le_epoche_di_emstudio_riempiono_la_periodizzazione(importato):
    db, _, esito = importato
    con = sqlite3.connect(str(db))
    periodi = con.execute(
        "SELECT periodo, fase, cron_iniziale, cron_finale, datazione_estesa, node_uuid "
        "FROM periodizzazione_table WHERE sito = ? ORDER BY periodo", (SITO,)).fetchall()
    con.close()
    assert periodi == [(1, "1", 100, 199, "II A.D.", "ep-a"), (2, "1", 200, 1800, "Post antiquity", "ep-b")]
    assert esito.epochs_created == 2
    r = _righe(db)
    assert (r[("2", "US")]["periodo_iniziale"], r[("2", "US")]["fase_iniziale"]) == ("1", "1")
    assert (r[("2", "US")]["periodo_finale"], r[("2", "US")]["fase_finale"]) == ("2", "1")
    assert (r[("1", "US")]["periodo_iniziale"], r[("1", "US")]["periodo_finale"]) == ("2", "2")
    assert r[("105", "USVn")]["periodo_iniziale"] == "1"


def test_la_scheda_sito_nasce_dal_grafo(importato):
    db, _, _ = importato
    con = sqlite3.connect(str(db))
    sito = con.execute("SELECT sito, definizione_sito, descrizione FROM site_table").fetchall()
    con.close()
    assert len(sito) == 1 and sito[0][0] == SITO
    assert sito[0][1] == "Extended Matrix"
    assert "Tempio" in sito[0][2] and "Autrice Prova" in sito[0][2] and "31700" in sito[0][2]


def test_reimportare_non_duplica(importato, tmp_path):
    db, sorgente, _ = importato
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    prima = _righe(db)
    grafo, _ = read_graph_for_import(str(sorgente))
    esito = GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    assert _righe(db).keys() == prima.keys()
    assert esito.epochs_created == 0
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT count(*) FROM periodizzazione_table").fetchone()[0] == 2
    assert con.execute("SELECT count(*) FROM site_table").fetchone()[0] == 1
    con.close()


def test_l_esportazione_ritrova_gli_archi(importato):
    """Andata e ritorno: dalle schede importate l'esportazione rifà gli
    archi dell'Extended Matrix, non connessioni generiche."""
    db, _, _ = importato
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    grafo = GraphProjector().populate_graph(db, sito=SITO)
    per_id = {n.node_id: n for n in grafo.nodes}

    def nome(nid):
        n = per_id.get(nid)
        return (getattr(n, "node_type", "?"), str((getattr(n, "attributes", None) or {}).get("us") or n.name))

    archi = {(nome(e.edge_source), e.edge_type, nome(e.edge_target)) for e in grafo.edges}
    assert (("USVn", "105"), "is_after", ("USVn", "106")) in archi
    assert (("USVn", "105"), "has_property", ("property", "height (105)")) in archi
    assert (("property", "height (105)"), "has_data_provenance", ("extractor", "05.02")) in archi
    assert (("extractor", "05.02"), "extracted_from", ("document", "05")) in archi
    assert (("combiner", "C.05"), "combines", ("extractor", "05.02")) in archi


def test_i_nomi_brevi_non_si_confondono_fra_tipi(importato):
    """«C.05» e «D.05» diventerebbero entrambi «05», «USD2» e «US2»
    entrambi «2»: i rapporti indicano il bersaglio solo con numero e area,
    e l'esportazione attaccava i legami all'unità sbagliata. Il tipo più
    forte tiene il numero, l'altro il nome completo di EMStudio."""
    db, _, _ = importato
    r = _righe(db)
    assert ("2", "US") in r and ("USD2", "USD") in r and ("2", "USD") not in r
    assert ("05", "DOC") in r and ("C.05", "Combinar") in r
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    grafo = GraphProjector().populate_graph(db, sito=SITO)
    per_id = {n.node_id: n for n in grafo.nodes}
    tipi = {(per_id[e.edge_source].node_type, e.edge_type, per_id[e.edge_target].node_type)
            for e in grafo.edges if e.edge_source in per_id and e.edge_target in per_id}
    assert ("property", "has_data_provenance", "combiner") in tipi
    assert ("USD", "abuts", "US") in tipi
    assert not any(a == "document" and t == "has_property" for a, t, _b in tipi)
