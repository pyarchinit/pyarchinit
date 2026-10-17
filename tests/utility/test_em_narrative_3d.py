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


def _scena(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    f = tmp_path / "SU002.glb"
    f.write_bytes(b"glTF-proxy")
    return n3d.Scene(proxies=[n3d.SceneProxy("rp1", "u1", "proxies/SU002.glb", str(f), 10)],
                     unit_proxies={"u1": ["rp1"], "u3": ["rp1"]}, names={"u1": "SU002", "u3": "USV100"},
                     epochs={"u1": ["ep1"], "u3": ["ep1"]}, missing=["proxies/SU003.glb"])


def test_la_vista_porta_i_proxy_la_libreria_e_lo_script(tmp_path):
    import base64
    import json
    import re
    from modules.s3dgraphy import em_narrative_3d as n3d
    vista = n3d.scene_view(_scena(tmp_path), {"ep1": "II A.D."}, lang="it")
    assert vista.key == "3d" and vista.label == "3D"
    assert vista.panel.startswith('<div id="pya-3d" class="pya-3d"></div>')
    assert 'id="pya-3d-caption"' in vista.panel and 'class="pya-reset"' in vista.panel
    assert vista.script.count(n3d.three_bundle()[:300]) == 1                 # il pacchetto, una volta
    dati = json.loads(re.search(r'<script type="application/json" id="pya-3d-data">(.*?)</script>',
                                vista.script, re.S).group(1))
    assert dati["proxies"] == [{"k": "rp1", "u": "u1", "glb": base64.b64encode(b"glTF-proxy").decode()}]
    assert dati["unitProxies"] == {"u1": ["rp1"], "u3": ["rp1"]} and dati["missing"] == 1
    assert dati["epochNames"] == {"ep1": "II A.D."} and dati["words"]["noProxy"] == "senza proxy 3D"
    assert vista.script.index("pya-3d-data") < vista.script.index("PYA_SEL.add(")


def test_la_scena_non_chiede_niente_alla_rete(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    vista = n3d.scene_view(_scena(tmp_path), {}, lang="en")
    corpo = vista.script.replace(n3d.three_bundle(), "")
    for vietato in ("http://", "https://", " src=", "import(", "fetch("):
        assert vietato not in corpo


def test_sul_telefono_girare_la_scena_non_scorre_la_pagina():
    import re
    from modules.s3dgraphy import em_narrative_3d as n3d
    assert re.search(r"#pya-3d\s*\{[^}]*touch-action:\s*none", n3d._CSS)


def test_senza_il_pacchetto_niente_scena(tmp_path, monkeypatch):
    from modules.s3dgraphy import em_narrative_3d as n3d
    monkeypatch.setattr(n3d, "BUNDLE", str(tmp_path / "manca.js"))
    assert n3d.scene_view(_scena(tmp_path), {}, lang="it") is None


def test_il_pacchetto_e_quello_del_plugin():
    from modules.s3dgraphy import em_narrative_3d as n3d
    assert Path(n3d.BUNDLE) == _PACCHETTO


@pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")
def test_il_javascript_della_scena_si_legge(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    f = tmp_path / "scena.js"
    f.write_text(n3d._JS, encoding="utf-8")
    subprocess.run(["node", "--check", str(f)], check=True)


_BROWSER_FINTO = r"""
globalThis.window = globalThis;
globalThis.addEventListener = function () {};
function finto() {
  var messi = {}, f = function () {};
  var p = new Proxy(f, {
    get: function (t, k) {
      if (k in messi) { return messi[k]; }
      return k === Symbol.toPrimitive ? function () { return 0; } : p;
    },
    set: function (t, k, v) { messi[k] = v; return true; },
    apply: function () { return p; },
    construct: function () { return p; }
  });
  return p;
}
function Elemento() {
  this.hidden = false; this.style = {}; this.firstChild = {textContent: ''};
  this.clientWidth = 400; this.clientHeight = 300;
}
Elemento.prototype.appendChild = function () {};
Elemento.prototype.addEventListener = function () {};
Elemento.prototype.closest = function () { return new Elemento(); };
Elemento.prototype.getBoundingClientRect = function () { return {left: 0, top: 0, width: 400, height: 300}; };
var dati = {proxies: [{k: 'a', u: 'u1', glb: 'AAAA'}, {k: 'b', u: 'u2', glb: 'Z2xURi0xMjM0NTY3OA=='}],
  unitProxies: {u1: ['a'], u2: ['b']}, names: {u1: 'SU001', u2: 'SU002'}, epochs: {}, epochNames: {},
  missing: 0, skipped: 0, words: {site: 'Tutto il sito', chapter: 'Capitolo', proxies: 'proxy',
  noProxy: 'senza', failed: 'non caricati', skipped: 'fuori', missing: 'senza file', noWebgl: 'niente WebGL',
  loading: 'Carico i proxy'}};
var elementi = {'pya-3d-data': {textContent: JSON.stringify(dati)}, 'pya-3d': new Elemento(),
                'pya-3d-caption': new Elemento()};
globalThis.document = {
  getElementById: function (id) { return elementi[id] || null; },
  createElement: function () { var e = new Elemento(); e.getContext = function () { return {}; }; return e; },
  addEventListener: function () {}
};
globalThis.WebGLRenderingContext = function () {};
globalThis.PYA_SEL = {units: {}, firstEpoch: {}, add: function (fn) { fn(null, null, null); }};
var T = finto();
// come il GLTFLoader di three.js: un file che non è un GLB fa lanciare subito
// un errore (new Uint8Array(data, 0, 4), JSON.parse), senza onError
T.GLTFLoader = function () {};
T.GLTFLoader.prototype.parse = function (dati, via, ok, ko) {
  if (dati.byteLength < 12) { throw new RangeError('Invalid typed array length: 4'); }
  var mesh = {isMesh: true, userData: {}, material: {opacity: 1, transparent: false, depthWrite: true,
    userData: {}, clone: function () { return {opacity: 1, transparent: false, depthWrite: true, userData: {}}; }}};
  ok({scene: {traverse: function (fn) { fn(mesh); }}});
};
globalThis.PYA_THREE = T;
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")
def test_un_proxy_che_non_si_legge_non_ferma_la_scena(tmp_path):
    """Il GLTFLoader di three.js, per un file che non è un GLB (troppo corto,
    non JSON, compresso Draco senza decodificatore), lancia l'errore subito
    invece di chiamare onError: la scena restava ferma su «Carico i proxy…»
    e non si disegnava niente (prova nel browser su TempluMare, 17 ottobre)."""
    from modules.s3dgraphy import em_narrative_3d as n3d
    f = tmp_path / "scena.js"
    f.write_text(_BROWSER_FINTO + n3d._JS
                 + "\nconsole.log(document.getElementById('pya-3d-caption').firstChild.textContent);\n",
                 encoding="utf-8")
    esito = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert esito.returncode == 0, esito.stderr
    assert esito.stdout.strip() == "Tutto il sito · 2 proxy · 1 non caricati"
