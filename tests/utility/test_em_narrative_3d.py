"""La scena 3D dei proxy nell'HTML della narrativa (Enzo, 17 ottobre 2026:
«assemblare insieme tutti i 3D … se ci clicco sopra si evidenzia il proxy
interessato e gli altri sono in trasparenza»)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "ext_libs")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_PACCHETTO = _ROOT / "resources" / "js" / "pya_three_scene.min.js"


def test_il_pacchetto_three_e_quello_fissato():
    testo = _PACCHETTO.read_text(encoding="utf-8")
    assert testo.startswith("/*! three.js 0.186.1 (MIT")
    assert "PYA_THREE" in testo and "GLTFLoader" in testo and "OrbitControls" in testo
    assert 300_000 < len(testo.encode("utf-8")) < 1_500_000
    assert (_PACCHETTO.parent / "THREE_LICENSE.txt").read_text(encoding="utf-8").startswith("The MIT License")


@pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")
def test_il_pacchetto_si_legge():
    subprocess.run(["node", "--check", str(_PACCHETTO)], check=True)


def _grafo():
    """Come i file di EMStudio: SU002 e SU003 col loro proxy; la USV100
    eredita la proprietà «geometry» di SU002."""
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.property_node import PropertyNode
    from s3dgraphy.nodes.resource_node import ResourceNode
    from s3dgraphy.nodes.semantic_shape_node import SemanticShapeNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="T")
    g.add_node(EpochNode("ep1", "II A.D.", 100, 199))
    for uid, nome in (("u1", "SU002"), ("u2", "SU003"), ("u3", "USV100")):
        g.add_node(StratigraphicUnit(uid, nome))
        g.add_edge(uid + "_fe", uid, "ep1", "has_first_epoch")
    for pid, sid, rid, url in (("p1", "sh1", "rp1", "proxies/SU002.glb"),
                               ("p2", "sh2", "rp2", "proxies/SU003.glb")):
        g.add_node(PropertyNode(pid, "geometry", property_type="geometry"))
        g.add_node(SemanticShapeNode(sid, "Shape"))
        g.add_node(ResourceNode(rid, url.split("/")[-1], url=url, url_type="proxy_model"))
        g.add_edge(pid + "_s", pid, sid, "has_semantic_shape")
        g.add_edge(sid + "_r", sid, rid, "has_linked_resource")
    g.add_edge("u1_p", "u1", "p1", "has_property")
    g.add_edge("u2_p", "u2", "p2", "has_property")
    g.add_edge("u3_p", "u3", "p1", "has_property")
    return g


def _db(tmp_path, righe, copie=()):
    import sqlite3
    db = tmp_path / "media.sqlite"
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE media_table (id_media INTEGER, mediatype TEXT, filename TEXT, "
                "filetype TEXT, filepath TEXT)")
    con.execute("CREATE TABLE media_thumb_table (id_media_thumb INTEGER, id_media INTEGER, path_resize TEXT)")
    con.executemany("INSERT INTO media_table VALUES (?,?,?,?,?)", righe)
    con.executemany("INSERT INTO media_thumb_table VALUES (?,?,?)", copie)
    con.commit()
    con.close()
    return "sqlite:///" + str(db)


def _file(cartella, nome, quanti):
    cartella.mkdir(parents=True, exist_ok=True)
    p = cartella / nome
    p.write_bytes(b"glTF" + b"\0" * (quanti - 4))
    return p


def test_i_proxy_vengono_dalla_regola_della_libreria():
    from modules.s3dgraphy import em_narrative_3d as n3d
    scena = n3d.scene_proxies(_grafo())
    assert [(p.key, p.unit, p.locator) for p in scena.proxies] == [
        ("rp1", "u1", "proxies/SU002.glb"), ("rp2", "u2", "proxies/SU003.glb")]
    assert scena.unit_proxies == {"u1": ["rp1"], "u3": ["rp1"], "u2": ["rp2"]}   # chi eredita punta al proprietario
    assert scena.names["u3"] == "USV100" and scena.epochs["u3"] == ["ep1"]


def test_i_file_dal_database_e_chi_resta_senza_proxy(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    glb = _file(tmp_path / "Tempio" / "EM" / "proxies", "SU002.glb", 64)
    conn = _db(tmp_path, [(1, "3d_model", "SU002", "glb", str(glb))])
    scena = n3d.build_scene(_grafo(), conn)
    assert [(p.key, p.path, p.size) for p in scena.proxies] == [("rp1", str(glb), 64)]
    assert scena.missing == ["proxies/SU003.glb"]
    assert scena.unit_proxies == {"u1": ["rp1"], "u3": ["rp1"]}        # SU003 resta senza proxy
    assert scena.names["u2"] == "SU003"                                 # ma resta un'unità con un nome


def test_oltre_i_limiti_restano_fuori_i_piu_grandi(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    a = _file(tmp_path / "p", "SU002.glb", 64)
    b = _file(tmp_path / "p", "SU003.glb", 200)
    conn = _db(tmp_path, [(1, "3d_model", "SU002", "glb", str(a)), (2, "3d_model", "SU003", "glb", str(b))])
    scena = n3d.build_scene(_grafo(), conn, max_file=150)
    assert [p.key for p in scena.proxies] == ["rp1"] and scena.skipped == ["SU003.glb"]
    scena = n3d.build_scene(_grafo(), conn, budget=100)
    assert [p.key for p in scena.proxies] == ["rp1"] and scena.skipped == ["SU003.glb"]


def test_col_disco_staccato_la_copia_delle_ridotte(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    copia = _file(tmp_path / "ridotte", "1_SU002.glb", 64)
    conn = _db(tmp_path, [(1, "3d_model", "SU002", "glb", str(tmp_path / "staccato" / "SU002.glb"))],
               [(1, 1, "1_SU002.glb")])
    scena = n3d.build_scene(_grafo(), conn, str(tmp_path / "ridotte") + "/")
    assert [(p.key, p.path) for p in scena.proxies] == [("rp1", str(copia))]
