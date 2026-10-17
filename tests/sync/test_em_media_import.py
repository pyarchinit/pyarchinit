"""I file che un em.json di EMStudio cita diventano media di pyArchInit,
registrati come quelli caricati dalla scheda (Enzo, 16 ottobre 2026: «non
trova i media»; media anche 3D, pdf, excel, word, txt, csv; «fai gestire
anche i glb»).

Un progetto EM ha il suo albero (``EM/``, ``EM/DosCo``, ``EM/proxies``,
``RB``…): i file si cercano come li cerca EMStudio, con il risolutore della
libreria. Il media punta al file originale, la miniatura e la copia vanno
nelle cartelle di pyArchInit (prima si copiava tutto nella radice di
``pyarchinit_5`` e i .glb restavano senza miniatura, quindi invisibili). Il
proxy di un'unità sta sulla proprietà «geometry» nel grafo: va sull'unità."""
from __future__ import annotations

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
GLB = PLUGIN_ROOT / "ext_libs" / "s3dgraphy" / "JSON_config" / "src" / "3D" / "SF.glb"
SITO = "Tempio media"


def _nodo(nid, tipo, nome, **data):
    return {"id": nid, "node_type": tipo, "name": nome, "data": dict(data)}


def _arco(src, tipo, dst):
    return {"id": "%s_%s_%s" % (src, tipo, dst), "edge_type": tipo, "source": src, "target": dst}


NODI = [
    _nodo("u1", "US", "SU002"),
    _nodo("p1", "property", "geometry"),
    _nodo("sh1", "semantic_shape", "Shape for SU002"),
    _nodo("rp1", "resource", "SU002.glb", url="proxies/SU002.glb"),
    _nodo("u2", "US", "SU003"),
    _nodo("p2", "property", "geometry"),
    _nodo("sh2", "semantic_shape", "Shape for SU003"),
    _nodo("rp2", "resource", "SU003.glb", url="proxies/SU003.glb"),
    _nodo("doc", "document", "D.05", url="D.05 Relazione.pdf"),
    _nodo("rd", "resource", "D.05 Relazione.pdf", url="DosCo/D.05 Relazione.pdf"),
    _nodo("ex", "extractor", "D.07.05", url="D.07.05.jpg"),
    _nodo("rm", "representation_model", "Colonna"),
    _nodo("rr", "resource", "Colonna LOD1"),
    _nodo("rf1", "resource_file", "colonna.glb", url="../RB/colonna.glb"),
    _nodo("rf2", "resource_file", "colonna.mtl", url="../RB/colonna.mtl"),
    _nodo("rm2", "representation_model", "Architrave"),
    _nodo("rb", "resource", "Architrave", url="blend://../SB/Tempio.blend#Mesh/Architrave"),
    _nodo("web", "resource", "Scheda online", url="http://example.org/scheda"),
]
ARCHI = [
    _arco("u1", "has_property", "p1"), _arco("p1", "has_semantic_shape", "sh1"),
    _arco("sh1", "has_linked_resource", "rp1"),
    _arco("u2", "has_property", "p2"), _arco("p2", "has_semantic_shape", "sh2"),
    _arco("sh2", "has_linked_resource", "rp2"),
    _arco("doc", "has_linked_resource", "rd"),
    _arco("ex", "extracted_from", "doc"),
    _arco("doc", "has_representation_model", "rm"), _arco("rm", "has_linked_resource", "rr"),
    _arco("rr", "has_file", "rf1"), _arco("rr", "has_file", "rf2"),
    _arco("doc", "has_representation_model", "rm2"), _arco("rm2", "has_linked_resource", "rb"),
    _arco("ex", "has_linked_resource", "web"),
]


@pytest.fixture
def progetto(tmp_path):
    radice = tmp_path / "Tempio"
    (radice / "EM" / "DosCo").mkdir(parents=True)
    (radice / "EM" / "proxies").mkdir()
    (radice / "RB").mkdir()
    shutil.copy2(GLB, radice / "EM" / "proxies" / "SU002.glb")
    shutil.copy2(GLB, radice / "RB" / "colonna.glb")
    (radice / "RB" / "colonna.mtl").write_text("newmtl x", encoding="utf-8")
    (radice / "EM" / "DosCo" / "D.05 Relazione.pdf").write_bytes(b"%PDF-1.4 finto")
    from PIL import Image
    Image.new("RGB", (64, 48), (200, 90, 40)).save(radice / "EM" / "DosCo" / "D.07.05.jpg")
    em = radice / "EM" / "tempio.em.json"
    em.write_text(json.dumps({"version": "1.0", "active_graph_id": "g",
                              "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
                              "graphs": {"g": {"graph_id": "g", "name": "Tempio",
                                               "nodes": NODI, "edges": ARCHI}}}), encoding="utf-8")
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(em))
    GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    thumb, resize = tmp_path / "thumb", tmp_path / "resize"
    thumb.mkdir()
    resize.mkdir()
    return {"db": db, "em": em, "grafo": grafo, "radice": radice,
            "thumb": str(thumb) + "/", "resize": str(resize) + "/", "tmp": tmp_path}


def _importa(p, em=None, **kw):
    from modules.s3dgraphy.sync.em_media_import import import_emjson_media
    kw.setdefault("thumb_path", p["thumb"])
    kw.setdefault("thumb_resize", p["resize"])
    return import_emjson_media(p["db"], p["grafo"], SITO, str(em or p["em"]), **kw)


def _collegati(db):
    con = sqlite3.connect(str(db))
    righe = con.execute(
        "SELECT u.node_uuid, m.filename, m.filetype, m.mediatype, m.filepath, l.media_name "
        "FROM media_to_entity_table l JOIN us_table u ON u.id_us = l.id_entity "
        "JOIN media_table m ON m.id_media = l.id_media "
        "WHERE l.entity_type = 'US' AND l.table_name = 'us_table' ORDER BY u.node_uuid, m.filename").fetchall()
    con.close()
    return righe


def test_ogni_file_va_sulla_sua_scheda(progetto):
    esito = _importa(progetto)
    righe = _collegati(progetto["db"])
    assert [(r[0], r[1], r[2], r[3]) for r in righe] == [
        ("doc", "D.05 Relazione", "pdf", "document"),
        ("doc", "colonna", "glb", "3d_model"),
        ("ex", "D.07.05", "jpg", "image"),
        ("u1", "SU002", "glb", "3d_model"),           # il proxy sull'unità, non sulla proprietà
    ]
    radice = progetto["radice"].resolve()
    assert {r[4] for r in righe} == {
        str(radice / "EM" / "DosCo" / "D.05 Relazione.pdf"), str(radice / "RB" / "colonna.glb"),
        str(radice / "EM" / "DosCo" / "D.07.05.jpg"), str(radice / "EM" / "proxies" / "SU002.glb")}
    assert all(r[5] == r[1] for r in righe)          # media_name = nome della miniatura
    assert esito.inserted == 4 and esito.linked == 4
    assert esito.missing == ["proxies/SU003.glb"]
    assert esito.skipped_types == {"mtl": 1, "blend": 1}
    assert esito.references == 1


def test_ogni_media_ha_miniatura_e_copia(progetto):
    esito = _importa(progetto)
    con = sqlite3.connect(str(progetto["db"]))
    righe = con.execute("SELECT t.mediatype, t.media_filename, t.filepath, t.path_resize "
                        "FROM media_thumb_table t JOIN media_table m ON m.id_media = t.id_media "
                        "ORDER BY t.media_filename").fetchall()
    con.close()
    assert len(righe) == 4 and esito.thumbnails == 4
    for _tipo, _nome, miniatura, copia in righe:
        assert Path(progetto["thumb"], miniatura).is_file(), miniatura
        assert Path(progetto["resize"], copia).is_file(), copia
    assert {r[1]: r[3].split("_", 1)[1] for r in righe} == {
        "D.05 Relazione": "D.05 Relazione.pdf", "colonna": "colonna.glb",
        "D.07.05": "D.07.05.png", "SU002": "SU002.glb"}


def test_i_modelli_3d_si_disegnano_tutti_insieme(progetto, monkeypatch):
    """I proxy di un em.json si disegnano in un processo solo, fuori da
    QGIS (dentro, su macOS, VTK lo faceva cadere alla chiusura del
    riepilogo: Enzo, 17 ottobre 2026)."""
    import modules.utility.media_preview as mp
    lotti = []
    vero = mp.render_models_png
    monkeypatch.setattr(mp, "render_models_png",
                        lambda lavori, *a, **k: lotti.append(len(lavori)) or vero(lavori, *a, **k))
    esito = _importa(progetto)
    assert lotti == [2]                              # colonna.glb e SU002.glb insieme
    assert esito.thumbnails == 4


def test_reimportare_non_duplica(progetto):
    _importa(progetto)
    esito = _importa(progetto)
    con = sqlite3.connect(str(progetto["db"]))
    conti = [con.execute("SELECT count(*) FROM %s" % t).fetchone()[0]
             for t in ("media_table", "media_thumb_table", "media_to_entity_table")]
    con.close()
    assert conti == [4, 4, 4]
    assert esito.inserted == 0 and esito.linked == 0 and esito.already_present == 4


def test_em_json_da_solo_poi_la_cartella_del_progetto(progetto):
    altrove = progetto["tmp"] / "altrove" / "tempio.em.json"
    altrove.parent.mkdir()
    shutil.copy2(progetto["em"], altrove)
    esito = _importa(progetto, em=altrove)
    assert esito.inserted == 0 and len(esito.missing) == 5
    assert "cartella" in esito.summary()                      # dice cosa fare
    esito = _importa(progetto, em=altrove, search_dirs=[str(progetto["radice"])])
    assert esito.inserted == 4 and esito.missing == ["proxies/SU003.glb"]


def test_una_copia_vuota_del_cloud_si_dice(progetto):
    (progetto["radice"] / "EM" / "proxies" / "SU003.glb").write_bytes(b"\0" * 5000)
    esito = _importa(progetto)
    assert esito.empty_copies == ["proxies/SU003.glb"] and esito.missing == []
    assert "vuot" in esito.summary()


def test_senza_cartelle_delle_miniature_registra_e_lo_dice(progetto):
    esito = _importa(progetto, thumb_path="", thumb_resize="")
    assert esito.inserted == 4 and esito.thumbnails == 0
    assert any("miniature" in w for w in esito.warnings)


# ---------------------------------------------------------------------------
# s3dgraphy 1.6.0.dev57: chi possiede davvero una proprietà, e gli indirizzi
# alternativi di un file
# ---------------------------------------------------------------------------

def _grafo(nodi, archi):
    from s3dgraphy.importer.emjson_importer import parse_emjson
    grafo, _ = parse_emjson({"version": "1.0", "active_graph_id": "g",
                             "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
                             "graphs": {"g": {"graph_id": "g", "name": "Tempio",
                                              "nodes": nodi, "edges": archi}}})
    return grafo


def _schede(grafo):
    from modules.s3dgraphy.sync import em_native_import as emn
    from modules.s3dgraphy.sync.graph_ingestor import (
        _NON_STRAT_TYPES, _PARADATA_ROW_TYPES, _is_synthetic_node)
    return emn.row_nodes(grafo, _NON_STRAT_TYPES - _PARADATA_ROW_TYPES, _is_synthetic_node)


def test_il_proxy_di_una_proprieta_ereditata_va_al_proprietario_originale():
    """Una USV che completa la SU002 ne eredita la proprietà (E.D.: una
    proprietà, più proprietari, ognuno col suo has_property; quello che
    eredita è marcato ``inherited``). Il proxy prendeva la strada del primo
    arco del file e finiva sulla USV: va alla SU002, come lo disegna EMStudio
    (``s3dgraphy.ownership.original_owner``)."""
    nodi = [_nodo("u1", "US", "SU002"), _nodo("v9", "USVs", "USV9"),
            _nodo("p1", "property", "geometry"),
            _nodo("sh1", "semantic_shape", "Shape for SU002"),
            _nodo("rp1", "resource", "SU002.glb", url="proxies/SU002.glb")]
    eredita = dict(_arco("v9", "has_property", "p1"), attributes={"inherited": True})
    archi = [eredita, _arco("u1", "has_property", "p1"),
             _arco("p1", "has_semantic_shape", "sh1"), _arco("sh1", "has_linked_resource", "rp1")]
    from modules.s3dgraphy.sync.em_media_import import collect_files
    grafo = _grafo(nodi, archi)
    file_di = collect_files(grafo, _schede(grafo))
    assert [v["locator"] for v in file_di.get("u1", [])] == ["proxies/SU002.glb"]
    assert "v9" not in file_di


def test_un_file_nel_bucket_con_la_copia_sul_disco_si_importa(progetto, tmp_path):
    """Una risorsa può avere più indirizzi degli stessi byte (il bucket e il
    disco, ``data.addresses``): il risolutore della libreria, quando
    l'indirizzo principale non è locale, prova quello locale. Noi la
    scartavamo prima di chiederglielo, come un semplice riferimento web."""
    nodi = [dict(n) for n in NODI]
    for n in nodi:
        if n["id"] == "rp2":
            n["data"] = {"url": "https://bucket.example.org/tempio/SU003.glb",
                         "addresses": [{"locator": "proxies/SU003.glb"}]}
    radice = progetto["radice"]
    shutil.copy2(GLB, radice / "EM" / "proxies" / "SU003.glb")
    em = radice / "EM" / "tempio_bucket.em.json"
    em.write_text(json.dumps({"version": "1.0", "active_graph_id": "g",
                              "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
                              "graphs": {"g": {"graph_id": "g", "name": "Tempio",
                                               "nodes": nodi, "edges": ARCHI}}}), encoding="utf-8")
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    grafo, _ = read_graph_for_import(str(em))
    esito = _importa(dict(progetto, grafo=grafo), em=em)
    collegati = {(r[0], r[1]) for r in _collegati(progetto["db"])}
    assert ("u2", "SU003") in collegati, collegati
    assert esito.missing == [] and esito.references == 1     # resta solo la scheda online


# ------------------------------------------------ le fonti della narrativa (5.13.129)

def test_le_fonti_della_narrativa_trovano_il_file_del_documento(progetto):
    """Il documento dell'em.json, importato con il suo PDF, è una fonte con
    il file dentro la pagina, l'anteprima e il percorso dell'originale."""
    from modules.s3dgraphy import em_export
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_html as nh
    _importa(progetto)
    conn = "sqlite:///" + str(progetto["db"])
    percorso, *_ = em_export.export_site(conn, SITO, str(progetto["tmp"] / "out"), per_saggio=False)
    grafo = en.load_project(percorso)[0].active()
    doc = [n for n in grafo.nodes if getattr(n, "node_type", "") == "document"][0]
    registro = nh.sources_registry(grafo, {doc.node_id: nh.Source(doc.node_id, doc.name, "Relazione")},
                                   conn, progetto["thumb"], progetto["resize"])
    voce = registro[doc.node_id]
    assert voce["title"] == doc.name and voce["description"] == "Relazione"
    assert voce["kind"] == "PDF" and voce["mime"] == "application/pdf"
    assert voce["file"]                                       # piccolo: dentro la pagina
    assert voce["preview"].startswith("data:image/")          # la miniatura dell'importazione
    assert voce["path"].endswith("D.05 Relazione.pdf") and voce["link"].startswith("file://")


def test_un_file_troppo_grande_resta_fuori_dalla_pagina(progetto):
    from modules.s3dgraphy import em_export
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_html as nh
    _importa(progetto)
    conn = "sqlite:///" + str(progetto["db"])
    percorso, *_ = em_export.export_site(conn, SITO, str(progetto["tmp"] / "out"), per_saggio=False)
    grafo = en.load_project(percorso)[0].active()
    doc = [n for n in grafo.nodes if getattr(n, "node_type", "") == "document"][0]
    registro = nh.sources_registry(grafo, {doc.node_id: nh.Source(doc.node_id, doc.name)},
                                   conn, progetto["thumb"], progetto["resize"], max_file=3)
    assert registro[doc.node_id]["file"] == "" and registro[doc.node_id]["link"]
