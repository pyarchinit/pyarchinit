"""I file che un em.json di EMStudio cita diventano media di pyArchInit
(Enzo, 16 ottobre 2026: «dovrebbe poter importare anche i media»).

Si seguono i legami del grafo da ogni scheda importata verso i file —
documento → risorsa → file, documento → modello 3D → risorsa → file — e i
file che esistono accanto all'em.json diventano media collegati a quella
scheda; quelli che mancano si elencano. I PDF restano nel campo
«documentazione» della scheda: la scheda media non li apre."""
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
SITO = "Tempio media"


def _nodo(nid, tipo, nome, **data):
    return {"id": nid, "node_type": tipo, "name": nome, "data": dict(data)}


def _arco(src, tipo, dst):
    return {"id": "%s_%s_%s" % (src, tipo, dst), "edge_type": tipo, "source": src, "target": dst}


@pytest.fixture
def progetto(tmp_path):
    cartella = tmp_path / "progetto"
    (cartella / "RB").mkdir(parents=True)
    (cartella / "foto").mkdir()
    (cartella / "foto" / "colonna.jpg").write_bytes(b"\xff\xd8\xff\xe0finto jpeg")
    (cartella / "RB" / "colonna.glb").write_bytes(b"glTF finto")
    (cartella / "RB" / "colonna.mtl").write_text("newmtl x", encoding="utf-8")
    (cartella / "D.05 Relazione.pdf").write_bytes(b"%PDF-1.4 finto")
    nodi = [
        _nodo("u1", "US", "US1"),
        _nodo("doc", "document", "D.05", url="D.05 Relazione.pdf"),
        _nodo("ex", "extractor", "D.05.01"),
        _nodo("res-img", "resource", "Foto della colonna"),
        _nodo("rf-img", "resource_file", "colonna.jpg", url="foto/colonna.jpg", media_type="image/jpeg"),
        _nodo("rm", "representation_model", "Colonna_BAKE"),
        _nodo("res-3d", "resource", "Modello della colonna"),
        _nodo("rf-3d", "resource_file", "colonna.glb", url="RB/colonna.glb", media_type="model/gltf-binary"),
        _nodo("rf-mtl", "resource_file", "colonna.mtl", url="RB/colonna.mtl"),
        _nodo("rf-manca", "resource_file", "sezione.png", url="foto/sezione.png"),
        _nodo("res-web", "resource", "Link", url="http://example.org/scheda"),
    ]
    archi = [
        _arco("ex", "extracted_from", "doc"),
        _arco("doc", "has_linked_resource", "res-img"),
        _arco("res-img", "has_file", "rf-img"),
        _arco("res-img", "has_file", "rf-manca"),
        _arco("doc", "has_representation_model", "rm"),
        _arco("rm", "has_linked_resource", "res-3d"),
        _arco("res-3d", "has_file", "rf-3d"),
        _arco("res-3d", "has_file", "rf-mtl"),
        _arco("ex", "has_linked_resource", "res-web"),
    ]
    em = cartella / "tempio.em.json"
    em.write_text(json.dumps({"version": "1.0", "active_graph_id": "g", "header": {"format": "em.json", "version": "1.0", "schema_version": "2"},
                              "graphs": {"g": {"graph_id": "g", "name": "Tempio", "nodes": nodi, "edges": archi}}}),
                  encoding="utf-8")
    db = tmp_path / "vuoto.sqlite"
    shutil.copy2(TEMPLATE_DB, db)
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    grafo, _ = read_graph_for_import(str(em))
    GraphIngestor().populate_list(grafo, db, sito=SITO, create_missing_epochs=True)
    destinazione = tmp_path / "media"
    destinazione.mkdir()
    return db, em, grafo, destinazione


def test_i_file_citati_diventano_media_della_scheda(progetto):
    db, em, grafo, destinazione = progetto
    from modules.s3dgraphy.sync.em_media_import import import_emjson_media
    esito = import_emjson_media(db, grafo, SITO, str(em), media_dest=str(destinazione), make_thumbs=False)
    con = sqlite3.connect(str(db))
    media = sorted(con.execute("SELECT filename, filetype, mediatype FROM media_table").fetchall())
    assert media == [("colonna", "glb", "3d_model"), ("colonna", "jpg", "image")]
    collegati = con.execute(
        "SELECT u.us, u.unita_tipo, m.mediatype FROM media_to_entity_table l "
        "JOIN us_table u ON u.id_us = l.id_entity JOIN media_table m ON m.id_media = l.id_media "
        "WHERE l.entity_type = 'US' ORDER BY m.mediatype").fetchall()
    con.close()
    assert collegati == [("05", "DOC", "3d_model"), ("05", "DOC", "image")]
    assert (destinazione / "colonna.jpg").exists() and (destinazione / "colonna.glb").exists()
    assert esito.inserted == 2
    assert [Path(p).name for p in esito.missing] == ["sezione.png"]          # citato, non c'è
    assert esito.skipped_types == {"pdf": 1, "mtl": 1}                       # restano fuori dai media


def test_reimportare_i_media_non_li_duplica(progetto):
    db, em, grafo, destinazione = progetto
    from modules.s3dgraphy.sync.em_media_import import import_emjson_media
    import_emjson_media(db, grafo, SITO, str(em), media_dest=str(destinazione), make_thumbs=False)
    esito = import_emjson_media(db, grafo, SITO, str(em), media_dest=str(destinazione), make_thumbs=False)
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT count(*) FROM media_table").fetchone()[0] == 2
    assert con.execute("SELECT count(*) FROM media_to_entity_table").fetchone()[0] == 2
    con.close()
    assert esito.inserted == 0


def test_senza_file_accanto_non_scrive_niente(progetto, tmp_path):
    db, em, grafo, destinazione = progetto
    from modules.s3dgraphy.sync.em_media_import import import_emjson_media
    altrove = tmp_path / "altrove" / "tempio.em.json"
    altrove.parent.mkdir()
    shutil.copy2(em, altrove)
    esito = import_emjson_media(db, grafo, SITO, str(altrove), media_dest=str(destinazione), make_thumbs=False)
    assert esito.inserted == 0 and len(esito.missing) == 3
    con = sqlite3.connect(str(db))
    assert con.execute("SELECT count(*) FROM media_table").fetchone()[0] == 0
    con.close()
