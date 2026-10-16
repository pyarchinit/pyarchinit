"""Andata e ritorno di un em.json di EMStudio (Enzo, 16 ottobre 2026:
«confronta con l'em.json originale»; e in EMStudio l'export si apriva come
«Untitled (TE)», con i nomi «1.USDUSD003», le descrizioni «None», gli archi
di epoca doppi, senza proxy né risorse).

pyArchInit tiene nelle sue tabelle le unità, i paradati, i rapporti e le
epoche. Il resto del grafo di EMStudio — risorse, forme semantiche, processi,
gruppi, autori, licenze, la georeferenziazione, il codice dello studio, i
nomi — si ricorda all'importazione (``em_sources``) e si rimette
all'esportazione, agganciato alle schede che esistono ancora."""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from collections import Counter
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

from modules.s3dgraphy import em_export  # noqa: E402

if not em_export.emjson_available():
    pytest.skip("s3dgraphy senza em.json", allow_module_level=True)

TEMPLATE_DB = PLUGIN_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite"
SITO = "Tempio di prova"


def _nodo(nid, tipo, nome, descrizione=None, **data):
    n = {"id": nid, "node_type": tipo, "name": nome, "data": dict(data)}
    if descrizione:
        n["description"] = descrizione
    return n


def _arco(src, tipo, dst):
    return {"id": "%s_%s_%s" % (src, tipo, dst), "edge_type": tipo, "source": src, "target": dst}


NODI = [
    _nodo("g1_graphroot", "graph", "Graph", em_id="TS16"),
    _nodo("geo-ts", "geo_position", "geo_position", epsg=31700, shift_x=327300.0,
          shift_y=448370.0, shift_z=500.0),
    _nodo("aut", "author", "Emanuel Demetrescu", name="Emanuel", surname="Demetrescu"),
    _nodo("ep-a", "EpochNode", "II A.D.", start_time=100, end_time=199),
    _nodo("ep-b", "EpochNode", "Post antiquity", start_time=200, end_time=1800),
    _nodo("ep-c", "EpochNode", "XX sec", start_time=1801, end_time=2013),
    _nodo("pt", "property", "absolute_time_start", "100"),
    _nodo("u1", "US", "SU001", "Foundation of the Temple"),
    _nodo("u2", "US", "SU002", "Foundation of the Columnade"),
    _nodo("d3", "USD", "USD003", "Rete di canali"),
    _nodo("u3", "US", "SU003", "Destruction"),
    _nodo("v1", "USVn", "USV105", "Architrave ricostruito"),
    _nodo("sf", "SF", "T24", "Moulding"),
    _nodo("p1", "property", "height", "Altezza 5.14"),
    _nodo("p2", "property", "height", "Altezza 2.10"),
    _nodo("pg1", "property", "geometry", value="ss1", property_type="geometry"),
    _nodo("pg2", "property", "geometry", value="ss2", property_type="geometry"),
    _nodo("ex", "extractor", "D.05.02", "Architrave = 1/4 della colonna"),
    _nodo("co", "combiner", "C.05", "Architrave compatibile"),
    _nodo("doc", "document", "D.05", "Relazione di scavo 2013", url="D.05 Relazione.pdf"),
    _nodo("ss1", "semantic_shape", "Shape for SU001"),
    _nodo("rp1", "resource", "SU001.glb", url="proxies/SU001.glb"),
    _nodo("ss2", "semantic_shape", "Shape for SU002"),
    _nodo("rp2", "resource", "SU002.glb", url="proxies/SU002.glb"),
    _nodo("rd", "resource", "D.05 Relazione.pdf", url="DosCo/D.05 Relazione.pdf"),
    _nodo("rdf", "resource_file", "D.05 Relazione.pdf", url="DosCo/D.05 Relazione.pdf"),
    _nodo("dtc", "dtc_process", "Fotogrammetria del documento", dtc_kind="photogrammetry"),
    _nodo("rdo", "resource", "D.05 OCR.pdf", url="DosCo/D.05 OCR.pdf"),
    _nodo("pd", "ParadataNodeGroup", "PD 105"),
    _nodo("act", "ActivityNodeGroup", "VAct.03 Architrave"),
    _nodo("br", "BR", "continuity_node", "_continuity"),
]
ARCHI = [
    _arco("u1", "overlies", "u2"),
    _arco("u3", "cuts", "u1"),
    _arco("d3", "abuts", "u1"),
    _arco("v1", "is_after", "u1"),
    _arco("v1", "has_property", "p1"), _arco("sf", "has_property", "p2"),
    _arco("u1", "has_property", "pg1"), _arco("u2", "has_property", "pg2"),
    _arco("p1", "has_data_provenance", "ex"), _arco("co", "combines", "ex"),
    _arco("ex", "extracted_from", "doc"),
    _arco("pg1", "has_semantic_shape", "ss1"), _arco("ss1", "has_linked_resource", "rp1"),
    _arco("pg2", "has_semantic_shape", "ss2"), _arco("ss2", "has_linked_resource", "rp2"),
    _arco("doc", "has_linked_resource", "rd"),
    dict(_arco("rd", "has_file", "rdf"), attributes={"role": "entry_point", "path": "D.05 Relazione.pdf"}),
    _arco("dtc", "dtc_had_input", "rd"), _arco("dtc", "dtc_had_output", "rdo"),
    _arco("dtc", "has_author", "aut"), _arco("ex", "has_author", "aut"),
    _arco("p1", "is_in_paradata_nodegroup", "pd"), _arco("v1", "has_paradata_nodegroup", "pd"),
    _arco("v1", "is_in_activity", "act"), _arco("act", "has_first_epoch", "ep-a"),
    _arco("br", "is_after", "u1"), _arco("br", "has_first_epoch", "ep-b"),
    _arco("u1", "has_first_epoch", "ep-a"), _arco("u2", "has_first_epoch", "ep-a"),
    _arco("u3", "has_first_epoch", "ep-b"), _arco("d3", "has_first_epoch", "ep-b"),
    _arco("u1", "survive_in_epoch", "ep-b"),
    _arco("u2", "survive_in_epoch", "ep-b"), _arco("u2", "survive_in_epoch", "ep-c"),
    _arco("ep-a", "has_property", "pt"),
    _arco("v1", "has_first_epoch", "ep-a"), _arco("sf", "has_first_epoch", "ep-a"),
]


@pytest.fixture
def mondo(tmp_path, monkeypatch):
    cartella = tmp_path / "pyarchinit_DB_folder"
    cartella.mkdir()
    shutil.copy(PLUGIN_ROOT / "resources" / "dbfiles" / "config.cfg", cartella / "config.cfg")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    db = cartella / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    em = tmp_path / "Tempio.em.json"
    em.write_text(json.dumps({
        "version": "1.0", "active_graph_id": "g1",
        "header": {"format": "em.json", "version": "1.0", "schema_version": 2},
        "graphs": {"g1": {"graph_id": "g1", "name": "Tempio", "nodes": NODI, "edges": ARCHI}}}),
        encoding="utf-8")
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(em))
    GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    return {"db": db, "em": em, "tmp": tmp_path}


def _ricorda(m):
    from modules.s3dgraphy.sync.em_sources import remember_source
    remember_source(m["db"], SITO, str(m["em"]))


def _esporta(m, nome="out"):
    path, _n, _e, _w = em_export.export_site("sqlite:///%s" % m["db"], SITO,
                                             str(m["tmp"] / nome), per_saggio=False)
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    grafo = list(doc["graphs"].values())[0]
    return doc, grafo, {n["id"]: n for n in grafo["nodes"]}, grafo["edges"]


def _terne(archi):
    return Counter((e["source"], e["edge_type"], e["target"]) for e in archi)


# ------------------------------------------------- correzioni dell'export

def test_un_arco_per_rapporto_anche_per_le_epoche(mondo):
    _doc, _g, _nodi, archi = _esporta(mondo)
    doppi = {k: v for k, v in _terne(archi).items() if v > 1}
    assert doppi == {}
    prime = Counter(e["source"] for e in archi if e["edge_type"] == "has_first_epoch")
    assert prime["u1"] == 1 and prime["v1"] == 1


def test_le_descrizioni_tornano_e_mai_none(mondo):
    _doc, _g, nodi, _archi = _esporta(mondo)
    assert nodi["u1"]["description"] == "Foundation of the Temple"
    assert nodi["sf"]["description"] == "Moulding"
    assert [n["id"] for n in nodi.values() if n.get("description") == "None"] == []


def test_il_grafo_ha_un_nome_anche_senza_memoria(mondo):
    _doc, grafo, _nodi, _archi = _esporta(mondo)
    nome = grafo.get("name")
    assert (nome.get("default") if isinstance(nome, dict) else nome) == SITO


# ------------------------------------------------- la memoria dell'em.json

def test_i_nomi_di_emstudio_tornano(mondo):
    _ricorda(mondo)
    _doc, _g, nodi, _archi = _esporta(mondo)
    assert {k: nodi[k]["name"] for k in ("u1", "d3", "v1", "sf", "p1", "p2", "ex", "co", "doc")} == {
        "u1": "SU001", "d3": "USD003", "v1": "USV105", "sf": "T24", "p1": "height",
        "p2": "height", "ex": "D.05.02", "co": "C.05", "doc": "D.05"}


def test_titolo_codice_e_georeferenziazione_tornano(mondo):
    _ricorda(mondo)
    _doc, grafo, nodi, _archi = _esporta(mondo)
    nome = grafo.get("name")
    assert (nome.get("default") if isinstance(nome, dict) else nome) == "Tempio"
    assert grafo.get("code") == "TS16" and not grafo.get("code_proposed")
    geo = [n for n in nodi.values() if n["node_type"] == "geo_position"]
    assert len(geo) == 1
    assert (geo[0]["data"]["epsg"], geo[0]["data"]["shift_x"], geo[0]["data"]["shift_z"]) == (31700, 327300.0, 500.0)


def test_i_nodi_che_pyarchinit_non_tiene_tornano_coi_loro_archi(mondo):
    _ricorda(mondo)
    _doc, _g, nodi, archi = _esporta(mondo)
    for nid in ("ss1", "rp1", "ss2", "rp2", "rd", "rdo", "dtc", "aut", "pd", "act", "br"):
        assert nid in nodi, nid
    terne = _terne(archi)
    epoca_a = next(t for (s, ty, t) in terne if s == "u1" and ty == "has_first_epoch")
    for attesa in [("pg1", "has_semantic_shape", "ss1"), ("ss1", "has_linked_resource", "rp1"),
                   ("doc", "has_linked_resource", "rd"), ("dtc", "dtc_had_input", "rd"),
                   ("dtc", "dtc_had_output", "rdo"), ("ex", "has_author", "aut"),
                   ("p1", "is_in_paradata_nodegroup", "pd"), ("v1", "has_paradata_nodegroup", "pd"),
                   ("v1", "is_in_activity", "act"), ("act", "has_first_epoch", epoca_a),
                   ("br", "is_after", "u1")]:
        assert terne[attesa] == 1, attesa
    assert [k for k, v in terne.items() if v > 1] == []
    assert not any(t in ("ep-a", "ep-b") or s in ("ep-a", "ep-b") for (s, _ty, t) in terne)


def test_una_scheda_rinominata_tiene_il_nome_nuovo(mondo):
    _ricorda(mondo)
    con = sqlite3.connect(str(mondo["db"]))
    con.execute("UPDATE us_table SET us = '1bis' WHERE node_uuid = 'u1'")
    con.commit()
    con.close()
    _doc, _g, nodi, _archi = _esporta(mondo)
    assert nodi["u1"]["name"] != "SU001" and "1bis" in nodi["u1"]["name"]
    assert nodi["u2"]["name"] == "SU002"


def test_un_ramo_rimasto_senza_scheda_non_torna(mondo):
    _ricorda(mondo)
    con = sqlite3.connect(str(mondo["db"]))
    con.execute("DELETE FROM us_table WHERE node_uuid = 'pg2'")
    con.commit()
    con.close()
    _doc, _g, nodi, _archi = _esporta(mondo)
    assert "ss2" not in nodi and "rp2" not in nodi
    assert "ss1" in nodi and "rp1" in nodi


def test_reimportare_l_export_non_raddoppia_niente(mondo):
    _ricorda(mondo)
    doc, _g, _nodi, _archi = _esporta(mondo)
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    percorso = next((mondo["tmp"] / "out").glob("*.em.json"))
    grafo, _ = read_graph_for_import(str(percorso))
    GraphIngestor().populate_list(grafo, mondo["db"], sito=SITO, create_missing_epochs=True)
    con = sqlite3.connect(str(mondo["db"]))
    conti = con.execute("SELECT unita_tipo, count(*) FROM us_table WHERE sito = ? GROUP BY unita_tipo",
                        (SITO,)).fetchall()
    periodi = con.execute("SELECT count(*) FROM periodizzazione_table WHERE sito = ?", (SITO,)).fetchone()[0]
    con.close()
    assert dict(conti) == {"US": 3, "USD": 1, "USVn": 1, "SF": 1, "property": 5,
                           "Extractor": 1, "Combinar": 1, "DOC": 1}
    assert periodi == 3


def test_un_unita_sopravvive_in_ogni_epoca_fino_all_ultima(mondo):
    """In TempluMare le unità nate nel II secolo sopravvivono in «Post
    antiquity» e nel «XX sec»: due archi. La scheda dice solo il periodo
    finale, e l'export scriveva solo l'ultimo."""
    _doc, _g, nodi, archi = _esporta(mondo)
    epoca = {n["name"]: i for i, n in nodi.items() if n["node_type"] == "EpochNode"}
    sopravvive = {e["target"] for e in archi if e["source"] == "u2" and e["edge_type"] == "survive_in_epoch"}
    assert sopravvive == {epoca["Post antiquity"], epoca["XX sec"]}
    prima = [e["target"] for e in archi if e["source"] == "u2" and e["edge_type"] == "has_first_epoch"]
    assert prima == [epoca["II A.D."]]


def test_i_legami_fra_un_epoca_e_una_scheda_tornano(mondo):
    """Un'epoca che possiede una proprietà (absolute_time_start): l'arco non
    è nelle schede, che non sanno dire «questa proprietà è dell'epoca»."""
    _ricorda(mondo)
    _doc, _g, nodi, archi = _esporta(mondo)
    epoca = {n["name"]: i for i, n in nodi.items() if n["node_type"] == "EpochNode"}
    assert _terne(archi)[(epoca["II A.D."], "has_property", "pt")] == 1


def test_i_dati_dei_nodi_delle_schede_tornano(mondo):
    """EMStudio riconosce il proxy di un'unità dalla sua proprietà
    «geometry»: ``property_type`` «geometry» e ``value`` con l'id della forma.
    L'export la riscriveva come proprietà «string» senza valore, e EMStudio
    contava 0 proxy su 114 (Enzo, 16-10-2026)."""
    _ricorda(mondo)
    _doc, _g, nodi, _archi = _esporta(mondo)
    assert nodi["pg1"]["data"]["property_type"] == "geometry"
    assert nodi["pg1"]["data"]["value"] == "ss1"
    assert nodi["doc"]["data"]["url"] == "D.05 Relazione.pdf"
    assert nodi["u1"]["data"]["us"]                         # i dati di pyArchInit restano


def test_gli_archi_che_tornano_tengono_i_loro_attributi(mondo):
    """Una risorsa di più file dice quale è il file principale con gli
    attributi dell'arco ``has_file`` (``role``, ``path``)."""
    _ricorda(mondo)
    _doc, _g, _nodi, archi = _esporta(mondo)
    arco = next(e for e in archi if (e["source"], e["edge_type"], e["target"]) == ("rd", "has_file", "rdf"))
    assert arco.get("attributes", {}).get("role") == "entry_point"
    assert arco["attributes"].get("path") == "D.05 Relazione.pdf"


def test_un_export_di_pyarchinit_non_diventa_memoria(mondo):
    """Un em.json scritto da pyArchInit (anche quello di un altro sito)
    non è un grafo di EMStudio da ricordare: titolo, codice e posizione
    dell'altro sito finivano nell'export di questo, col codice confermato."""
    from modules.s3dgraphy.sync.em_sources import load_source, remember_source
    _esporta(mondo)
    percorso = next((mondo["tmp"] / "out").glob("*.em.json"))
    assert remember_source(mondo["db"], "Altro sito", str(percorso)) is False
    assert load_source(mondo["db"], "Altro sito") is None


def test_i_dati_cambiati_nella_scheda_vincono_sul_file(mondo):
    """Un dato che la scheda tiene (il file di un documento) e che si cambia
    in pyArchInit esce nuovo, non come era nel file importato."""
    _ricorda(mondo)
    con = sqlite3.connect(str(mondo["db"]))
    con.execute("UPDATE us_table SET documentazione = 'D.05 Nuova.pdf' WHERE node_uuid = 'doc'")
    con.commit()
    con.close()
    _doc, _g, nodi, _archi = _esporta(mondo)
    assert nodi["doc"]["data"]["url"] == "D.05 Nuova.pdf"
