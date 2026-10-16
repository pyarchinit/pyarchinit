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
