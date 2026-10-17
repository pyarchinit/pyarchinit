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
    assert sito[0][1] == "Tempio"           # il nome del grafo, non «Extended Matrix»
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


# ---------------------------------------------------------------------------
# I rapporti come li vuole la scheda US (Enzo, 17 ottobre 2026, video e log
# «log_rapporti_US_Temple»): ogni rapporto anche sulla scheda collegata,
# rovesciato, e mai un campo vuoto (NULL) — la verifica dei rapporti della
# scheda US dava 135 «malformed node or string: None» e centinaia di
# «Rapporto reciproco non trovato».
# ---------------------------------------------------------------------------

#: l'inverso di ogni segno, come lo cerca la verifica della scheda US
#: (``conversion_dict`` in ``tabs/US_USM.py``)
_INVERSO = {
    "Copre": "Coperto da", "Coperto da": "Copre", "Taglia": "Tagliato da",
    "Tagliato da": "Taglia", "Riempie": "Riempito da", "Riempito da": "Riempie",
    "Si appoggia a": "Gli si appoggia", "Gli si appoggia": "Si appoggia a",
    "Si lega a": "Si lega a", "Uguale a": "Uguale a",
    ">": "<", "<": ">", ">>": "<<", "<<": ">>",
}


def test_nessuna_scheda_ha_i_rapporti_vuoti(importato):
    db, _, _ = importato
    for (us, ut), riga in _righe(db).items():
        assert riga["rapporti"] is not None, (us, ut)
        assert isinstance(ast.literal_eval(riga["rapporti"]), list), (us, ut)
    assert ast.literal_eval(_righe(db)[("4", "USNt")]["rapporti"]) == []   # senza rapporti: lista vuota


def test_ogni_rapporto_ha_il_reciproco_sulla_scheda_collegata(importato):
    db, _, _ = importato
    righe = _righe(db)
    per_us = {us: riga for (us, _ut), riga in righe.items()}
    mancanti = []
    for (us, _ut), riga in righe.items():
        for segno, altra, area, sito in ast.literal_eval(riga["rapporti"]):
            voluto = [_INVERSO[segno], us, str(riga["area"]), sito]
            if voluto not in ast.literal_eval(per_us[altra]["rapporti"]):
                mancanti.append((us, segno, altra))
    assert mancanti == []
    assert ("Coperto da", "1") in _rapporti(righe[("2", "US")])
    assert ("Tagliato da", "3") in _rapporti(righe[("2", "US")])
    assert ("Gli si appoggia", "USD2") in _rapporti(righe[("1", "US")])
    assert ("<", "105") in _rapporti(righe[("106", "USVn")])
    assert ("<<", "105") in _rapporti(righe[("height (105)", "property")])
    assert ("<<", "05.02") in _rapporti(righe[("05", "DOC")])


def test_i_reciproci_non_raddoppiano_gli_archi(importato):
    """Il rapporto scritto sulle due schede resta UN arco nell'export."""
    db, _, _ = importato
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    grafo = GraphProjector().populate_graph(db, sito=SITO)
    per_id = {n.node_id: n for n in grafo.nodes}

    def nome(nid):
        n = per_id.get(nid)
        return str((getattr(n, "attributes", None) or {}).get("us") or n.name)

    terne = [(nome(e.edge_source), e.edge_type, nome(e.edge_target)) for e in grafo.edges]
    assert len(terne) == len(set(terne))
    coppie = [(s, t) for s, tipo, t in terne
              if tipo in ("overlies", "is_overlain_by", "is_after", "is_before",
                          "has_property", "has_data_provenance", "extracted_from", "combines")]
    doppie = [c for c in coppie if (c[1], c[0]) in coppie]
    assert doppie == []
    assert ("1", "overlies", "2") in terne


# ---------------------------------------------------------------------------
# Datazione e codice periodo (Enzo, 17 ottobre 2026): «la periodizzazione ci
# sta ma manca la datazione»; «dovrebbe crearmi anche il codice periodo in
# automatico, da 1 a n in sequenza: periodo 1 fase 1 → 1, periodo 2 fase 1
# → 2, periodo 3 fase 1 → 3».
# ---------------------------------------------------------------------------

def test_i_codici_periodo_vanno_in_sequenza():
    from modules.s3dgraphy.sync.em_native_import import plan_period_codes
    periodi = [{"periodo": 3, "fase": "1"}, {"periodo": 1, "fase": "2"},
               {"periodo": 1, "fase": "1"}, {"periodo": 10, "fase": "1"}]
    assert plan_period_codes(periodi) == {("1", "1"): 1, ("1", "2"): 2, ("3", "1"): 3, ("10", "1"): 4}
    # i codici già dati restano; i nuovi vengono dopo il più alto
    gia = [{"periodo": 1, "fase": "1", "cont_per": 7}, {"periodo": 2, "fase": "1", "cont_per": None}]
    assert plan_period_codes(gia) == {("1", "1"): 7, ("2", "1"): 8}


def test_il_codice_periodo_della_us_come_crea_codice_periodo():
    from modules.s3dgraphy.sync.em_native_import import us_period_code
    codici = {("1", "1"): 1, ("2", "1"): 2, ("3", "1"): 3}
    assert us_period_code(codici, "1", "1", "3", "1") == "1/2/3"
    assert us_period_code(codici, "2", "1", "2", "1") == "2"
    assert us_period_code(codici, "2", "1", None, None) == "2"
    assert us_period_code(codici, None, None, None, None) is None
    assert us_period_code(codici, "9", "1", None, None) is None        # periodo sconosciuto


def test_la_periodizzazione_ha_il_codice_e_le_us_la_datazione(importato):
    db, _, _ = importato
    con = sqlite3.connect(str(db))
    codici = con.execute("SELECT periodo, fase, cont_per FROM periodizzazione_table WHERE sito = ? "
                         "ORDER BY periodo", (SITO,)).fetchall()
    con.close()
    assert codici == [(1, "1", 1), (2, "1", 2)]
    r = _righe(db)
    assert r[("2", "US")]["datazione"] == "II A.D."                 # nasce nel periodo 1
    assert r[("1", "US")]["datazione"] == "Post antiquity"
    assert r[("105", "USVn")]["datazione"] == "II A.D."
    assert r[("2", "US")]["cont_per"] == "1/2"                      # vive dal periodo 1 al 2
    assert r[("1", "US")]["cont_per"] == "2"
    assert not r[("Material", "property")]["datazione"]             # senza periodo, niente data


# ---------------------------------------------------------------------------
# La scheda sito dall'em.json (Enzo, 17 ottobre 2026): «nella definizione non
# dovrebbe mettere Extended Matrix ma la definizione del Temple, e questo
# dovrebbe essere scritto anche nel thesaurus perché dovrebbe prenderlo da
# lì»; «se nell'em.json ci sono nazione, regione, provincia, comune questi
# andrebbero riempiti, e aggiornati anche nel thesaurus». Decisioni: il bene
# dichiarato (HC1), altrimenti il nome del grafo; i toponimi passano dal
# thesaurus, codici 1.2–1.5.
# ---------------------------------------------------------------------------

def _con_luoghi(tmp_path):
    """L'em.json di prova con la catena dei luoghi come la scrive
    l'esportazione di pyArchInit: comune ⊂ provincia ⊂ regione ⊂ nazione,
    e il sito nel comune."""
    sorgente = _em_json(tmp_path)
    dati = json.loads(sorgente.read_text(encoding="utf-8"))
    grafo = dati["graphs"]["g-1"]
    luoghi = [("t-naz", "nazione", "Italia"), ("t-reg", "regione", "Toscana"),
              ("t-pro", "provincia", "Pisa"), ("t-com", "comune", "Volterra")]
    for nid, livello, nome in luoghi:
        grafo["nodes"].append(_nodo(nid, "LocationNodeGroup", nome, group_kind="toponym",
                                    kind="toponym", propagation="additive",
                                    level=livello, name=nome))
    grafo["nodes"].append(_nodo("t-sito", "LocationNodeGroup", "Tempio", group_kind="toponym",
                                kind="toponym", propagation="additive",
                                level="sito", name="Tempio"))
    catena = ["t-sito", "t-com", "t-pro", "t-reg", "t-naz"]
    for basso, alto in zip(catena, catena[1:]):
        grafo["edges"].append(_arco(basso, "is_in_location", alto))
    sorgente.write_text(json.dumps(dati), encoding="utf-8")
    return sorgente


def _importa(db, sorgente, about=None):
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(sorgente))
    if about:
        from s3dgraphy import api
        api.declare_hdto(grafo, study={"name": "Saggio 2013"}, about={"name": about})
    return GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)


def _thesaurus_sito(db):
    con = sqlite3.connect(str(db))
    righe = con.execute("SELECT tipologia_sigla, sigla, sigla_estesa, lingua FROM pyarchinit_thesaurus_sigle "
                        "WHERE nome_tabella = 'site_table' ORDER BY tipologia_sigla, sigla_estesa").fetchall()
    con.close()
    return righe


def test_la_scheda_sito_prende_definizione_e_toponimi_dall_em_json(tmp_path, monkeypatch):
    from modules.s3dgraphy.sync import em_native_import as emn
    monkeypatch.setattr(emn, "thesaurus_lingua", lambda locale=None: "IT")
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    _importa(db, _con_luoghi(tmp_path))
    con = sqlite3.connect(str(db))
    sito = con.execute("SELECT definizione_sito, nazione, regione, provincia, comune "
                       "FROM site_table WHERE sito = ?", (SITO,)).fetchone()
    con.close()
    assert sito == ("Tempio", "Italia", "Toscana", "Pisa", "Volterra")   # il nome del grafo
    voci = {(cod, estesa, lingua) for cod, _sigla, estesa, lingua in _thesaurus_sito(db)}
    assert {("1.1", "Tempio", "IT"), ("1.2", "Italia", "IT"), ("1.3", "Toscana", "IT"),
            ("1.4", "Pisa", "IT"), ("1.5", "Volterra", "IT")} <= voci
    _importa(db, _con_luoghi(tmp_path))                                    # una seconda volta
    assert len(_thesaurus_sito(db)) == len(voci)                          # niente doppioni


def test_il_bene_dichiarato_vince_sul_nome_del_grafo(tmp_path, monkeypatch):
    from modules.s3dgraphy.sync import em_native_import as emn
    monkeypatch.setattr(emn, "thesaurus_lingua", lambda locale=None: "IT")
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    _importa(db, _em_json(tmp_path), about="Grande Tempio")
    con = sqlite3.connect(str(db))
    definizione = con.execute("SELECT definizione_sito FROM site_table WHERE sito = ?", (SITO,)).fetchone()[0]
    con.close()
    assert definizione == "Grande Tempio"
    assert ("1.1", "Grande Tempio") in {(c, e) for c, _s, e, _l in _thesaurus_sito(db)}


def test_una_scheda_sito_del_vecchio_import_si_ripara(tmp_path, monkeypatch):
    """Il database di Enzo ha già la scheda con «Extended Matrix» e i
    toponimi vuoti: reimportare li sistema; quello che l'utente ha scritto
    resta."""
    from modules.s3dgraphy.sync import em_native_import as emn
    monkeypatch.setattr(emn, "thesaurus_lingua", lambda locale=None: "IT")
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    con = sqlite3.connect(str(db))
    con.execute("INSERT INTO site_table (sito, nazione, regione, definizione_sito, descrizione) "
                "VALUES (?, '', 'Lazio', 'Extended Matrix', 'mia')", (SITO,))
    con.commit()
    con.close()
    _importa(db, _con_luoghi(tmp_path))
    con = sqlite3.connect(str(db))
    sito = con.execute("SELECT definizione_sito, nazione, regione, provincia, comune, descrizione "
                       "FROM site_table WHERE sito = ?", (SITO,)).fetchone()
    con.close()
    assert sito == ("Tempio", "Italia", "Lazio", "Pisa", "Volterra", "mia")


def test_la_lingua_del_thesaurus_come_la_scheda_sito():
    from modules.s3dgraphy.sync.em_native_import import thesaurus_lingua
    assert thesaurus_lingua("it_IT") == "IT"
    assert thesaurus_lingua("en_US") == "EN_US"
    assert thesaurus_lingua("de") == "DE"
    assert thesaurus_lingua("el_GR") == "EL"
    assert thesaurus_lingua("xx_YY") == "IT"


def test_le_sigle_restano_uniche():
    from modules.s3dgraphy.sync.em_native_import import unique_sigla
    assert unique_sigla("Barletta", {"BAR"}) not in {"BAR"}
    assert len(unique_sigla("Barletta", {"BAR"})) <= 3
    assert unique_sigla("Roma", set()) == "ROM"


def test_l_inverso_tiene_la_forma_della_parola():
    from modules.s3dgraphy.sync.em_native_import import inverse_rapporto
    assert inverse_rapporto("Copre") == "Coperto da"
    assert inverse_rapporto("copre") == "coperto da"           # schede scritte a mano
    assert inverse_rapporto("Si lega a") == "Si lega a"
    assert inverse_rapporto("Covers") == "Covered by"
    assert inverse_rapporto(">>") == "<<" and inverse_rapporto("<") == ">"
    assert inverse_rapporto("parola sconosciuta") is None


def test_l_anteprima_conta_le_schede_che_l_import_cambiera(importato):
    """Riimportando in un database del vecchio import l'anteprima diceva
    «850 invariate» e poi le cambiava: ora conta i rapporti con i reciproci,
    la datazione e il codice periodo come la scrittura."""
    db, sorgente, _ = importato
    con = sqlite3.connect(str(db))
    con.execute("UPDATE us_table SET rapporti = NULL WHERE us = '4' AND sito = ?", (SITO,))
    con.execute("UPDATE us_table SET rapporti = ? WHERE us = '2' AND sito = ?",
                ("[['Coperto da', '1', '1', '%s']]" % SITO, SITO))
    con.execute("UPDATE us_table SET datazione = NULL WHERE us = '1' AND sito = ?", (SITO,))
    con.commit()
    totale = con.execute("SELECT count(*) FROM us_table WHERE sito = ?", (SITO,)).fetchone()[0]
    con.close()
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(sorgente))
    esito = GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True, dry_run=True)
    assert (esito.inserted, esito.updated, esito.skipped) == (0, 3, totale - 3)


# ------------------------------------------------ «prima / dopo» fra due US

def test_prima_e_dopo_fra_due_us_resta_prima_e_dopo(tmp_path):
    """TempluMare ha nove «SU019 is_after SU001»: un «dopo» che non dice un
    contatto fisico. Fra due US l'importazione prendeva la parola della
    tabella della libreria, «Copre», e l'esportazione ne rifaceva
    ``overlies`` (17 ottobre 2026, confronto con l'em.json originale).
    Come fra gli altri tipi, è la freccia ``>`` / ``<``, che torna
    ``is_after``."""
    nodi = [_nodo("ep", "EpochNode", "II A.D.", start_time=100, end_time=199),
            _nodo("a", "US", "SU019", "Livello di cantiere"),
            _nodo("b", "US", "SU001", "Fondazione")]
    archi = [_arco("a", "is_after", "b"), _arco("a", "has_first_epoch", "ep"),
             _arco("b", "has_first_epoch", "ep")]
    sorgente = tmp_path / "dopo.em.json"
    sorgente.write_text(json.dumps({
        "version": "1.0", "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
        "active_graph_id": "g", "graphs": {"g": {"graph_id": "g", "name": "Dopo",
                                                 "nodes": nodi, "edges": archi}}}), encoding="utf-8")
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    grafo, _ = read_graph_for_import(str(sorgente))
    GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    righe = {r["node_uuid"]: r for r in _righe(db).values()}
    assert [s for s, _ in _rapporti(righe["a"])] == [">"]
    assert [s for s, _ in _rapporti(righe["b"])] == ["<"]
    esportato = GraphProjector().populate_graph(db, sito=SITO)
    tipi = {e.edge_type for e in esportato.edges if {e.edge_source, e.edge_target} == {"a", "b"}}
    assert tipi == {"is_after"}
