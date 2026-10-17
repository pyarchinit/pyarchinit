"""La scena 3D dei proxy nell'HTML della narrativa (Enzo, 17 ottobre 2026:
«assemblare insieme tutti i 3D … se ci clicco sopra si evidenzia il proxy
interessato e gli altri sono in trasparenza»)."""
from __future__ import annotations

import re
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
    assert testo.startswith("/*! three.js 0.186.1 ")
    # la licenza MIT vuole la nota di copyright in ogni copia: anche nelle pagine esportate
    assert re.search(r"@license Copyright 2010-20\d\d three\.js authors", testo[:400], re.I)
    assert "SPDX-License-Identifier: MIT" in testo[:400]
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


def _blocco(vista, ident):
    import json
    import re
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % ident, vista.script, re.S)
    return json.loads(m.group(1)) if m else None


def test_la_vista_porta_i_proxy_la_libreria_e_lo_script(tmp_path):
    import base64
    from modules.s3dgraphy import em_narrative_3d as n3d
    vista = n3d.scene_view(_scena(tmp_path), {"ep1": "II A.D."}, lang="it")
    assert vista.key == "3d" and vista.label == "3D"
    assert vista.panel.startswith('<div id="pya-scena-3d" class="pya-scena-3d"></div>')
    assert 'id="pya-scena-3d-caption"' in vista.panel and 'class="pya-reset"' in vista.panel
    assert vista.script.count(n3d.three_bundle()[:300]) == 1                 # il pacchetto, una volta
    dati = _blocco(vista, "pya-scena-3d-data")
    # i metadati, piccoli, si leggono subito; i GLB solo quando si apre il 3D
    assert dati["proxies"] == [{"k": "rp1", "u": "u1"}]
    assert _blocco(vista, "pya-scena-3d-glb") == {"rp1": base64.b64encode(b"glTF-proxy").decode()}
    assert dati["unitProxies"] == {"u1": ["rp1"], "u3": ["rp1"]} and dati["missing"] == 1
    assert dati["epochNames"] == {"ep1": "II A.D."} and dati["words"]["noProxy"] == "senza proxy 3D"
    assert vista.script.index("pya-scena-3d-glb") < vista.script.index("PYA_SEL.add(")


def test_un_file_che_non_si_apre_conta_fra_i_mancanti(tmp_path):
    """Un file trovato e poi illeggibile faceva cadere tutta la scena
    (revisione finale): ora conta fra i mancanti e gli altri restano."""
    from modules.s3dgraphy import em_narrative_3d as n3d
    scena = _scena(tmp_path)
    scena.proxies.append(n3d.SceneProxy("rp2", "u2", "proxies/SU003.glb", str(tmp_path / "sparito.glb"), 10))
    scena.unit_proxies["u2"] = ["rp2"]
    vista = n3d.scene_view(scena, {}, lang="it")
    dati = _blocco(vista, "pya-scena-3d-data")
    assert [p["k"] for p in dati["proxies"]] == ["rp1"] and dati["missing"] == 2
    assert "u2" not in dati["unitProxies"]
    scena.proxies = [n3d.SceneProxy("rp2", "u2", "proxies/SU003.glb", str(tmp_path / "sparito.glb"), 10)]
    assert n3d.scene_view(scena, {}, lang="it") is None                     # niente da mostrare


def test_lo_stesso_file_da_due_risorse_entra_una_volta(tmp_path):
    from s3dgraphy.nodes.property_node import PropertyNode
    from s3dgraphy.nodes.resource_node import ResourceNode
    from s3dgraphy.nodes.semantic_shape_node import SemanticShapeNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    from modules.s3dgraphy import em_narrative_3d as n3d
    g = _grafo()
    g.add_node(StratigraphicUnit("u4", "SU005"))
    g.add_node(PropertyNode("p4", "geometry", property_type="geometry"))
    g.add_node(SemanticShapeNode("sh4", "Shape"))
    g.add_node(ResourceNode("rp4", "SU002.glb", url="proxies/SU002.glb", url_type="proxy_model"))
    g.add_edge("u4_p", "u4", "p4", "has_property")
    g.add_edge("p4_s", "p4", "sh4", "has_semantic_shape")
    g.add_edge("sh4_r", "sh4", "rp4", "has_linked_resource")
    glb = _file(tmp_path / "Tempio" / "EM" / "proxies", "SU002.glb", 64)
    scena = n3d.build_scene(g, _db(tmp_path, [(1, "3d_model", "SU002", "glb", str(glb))]))
    assert [p.key for p in scena.proxies] == ["rp1"]                         # un file, una volta
    assert scena.unit_proxies["u4"] == ["rp1"] and scena.unit_proxies["u1"] == ["rp1"]


def test_la_scena_non_chiede_niente_alla_rete(tmp_path):
    from modules.s3dgraphy import em_narrative_3d as n3d
    vista = n3d.scene_view(_scena(tmp_path), {}, lang="en")
    corpo = vista.script.replace(n3d.three_bundle(), "")
    for vietato in ("http://", "https://", " src=", "import(", "fetch("):
        assert vietato not in corpo


def test_sul_telefono_girare_la_scena_non_scorre_la_pagina():
    import re
    from modules.s3dgraphy import em_narrative_3d as n3d
    assert re.search(r"#pya-scena-3d\s*\{[^}]*touch-action:\s*none", n3d._CSS)


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
var coda = [], disegni = 0, continuo = false, selezioni = [], raggi = [], tastiera = [];
globalThis.requestAnimationFrame = function (cb) { coda.push(cb); return coda.length; };
globalThis.cancelAnimationFrame = function () {};
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
  this.hidden = false; this.style = {}; this.firstChild = {textContent: ''}; this.attr = {}; this.ascolti = {};
  this.clientWidth = 400; this.clientHeight = 300;
}
Elemento.prototype.appendChild = function () {};
Elemento.prototype.setAttribute = function (k, v) { this.attr[k] = String(v); };
Elemento.prototype.getAttribute = function (k) { return k in this.attr ? this.attr[k] : null; };
Elemento.prototype.addEventListener = function (t, f) { (this.ascolti[t] = this.ascolti[t] || []).push(f); };
Elemento.prototype.emetti = function (t, ev) {
  ev = ev || {}; ev.preventDefault = function () {};
  (this.ascolti[t] || []).forEach(function (f) { f(ev); });
};
Elemento.prototype.getBoundingClientRect = function () { return {left: 0, top: 0, width: 400, height: 300}; };
var vistaFinta = new Elemento();
Elemento.prototype.closest = function () { return vistaFinta; };
var dati = __DATI__, testoGlb = JSON.stringify(__GLB__), glbLetto = 0, elementoGlb = {};
Object.defineProperty(elementoGlb, 'textContent', {
  get: function () { glbLetto += 1; return testoGlb; }, set: function (v) { testoGlb = v; }});
var elementi = {'pya-scena-3d-data': {textContent: JSON.stringify(dati)}, 'pya-scena-3d-glb': elementoGlb,
                'pya-scena-3d': new Elemento(), 'pya-scena-3d-caption': new Elemento()};
var ascoltiDocumento = {};
globalThis.document = {
  getElementById: function (id) { return elementi[id] || null; },
  createElement: function () { return new Elemento(); },
  addEventListener: function (t, f) { (ascoltiDocumento[t] = ascoltiDocumento[t] || []).push(f); }
};
function documentoEmetti(t, ev) { (ascoltiDocumento[t] || []).forEach(function (f) { f(ev); }); }
globalThis.PYA_SEL = {units: {}, firstEpoch: {}, fns: [],
  add: function (fn) { this.fns.push(fn); fn(null, null, null); },
  select: function (e, u, g) {
    selezioni.push([e, u, g]);
    this.fns.forEach(function (fn) { fn(e, u, g); });
  }};
var T = finto();
// come il GLTFLoader di three.js: un file che non è un GLB fa lanciare subito
// un errore (new Uint8Array(data, 0, 4), JSON.parse), senza onError
T.GLTFLoader = function () {};
T.GLTFLoader.prototype.parse = function (dati, via, ok, ko) {
  if (dati.byteLength < 12) { throw new RangeError('Invalid typed array length: 4'); }
  var mesh = {isMesh: true, userData: {}, geometry: {}, add: function () {}, material: {opacity: 1,
    transparent: false, depthWrite: true, userData: {},
    clone: function () { return {opacity: 1, transparent: false, depthWrite: true, userData: {}}; }}};
  ok({scene: {traverse: function (fn) { fn(mesh); }}});
};
var renderer = null;
T.WebGLRenderer = function () {
  renderer = {domElement: new Elemento(), setPixelRatio: function () {}, setSize: function () {},
              render: function () { disegni += 1; }, setAnimationLoop: function (fn) { continuo = !!fn; }};
  return renderer;
};
T.OrbitControls = function () {
  return {target: finto(), enableDamping: false, update: function () { return false; },
          addEventListener: function () {},
          listenToKeyEvents: function (el) { tastiera.push(!!renderer && el === renderer.domElement); }};
};
var colpo = null;                          // l'unità che il raggio trova sotto il puntatore
T.Raycaster = function () {
  return {setFromCamera: function () {}, intersectObjects: function (oggetti, ricorsivo) {
    raggi.push(ricorsivo === true);
    return colpo ? [{object: {isMesh: true, userData: {pyaUnit: colpo},
                              material: {transparent: false, opacity: 1}}}] : [];
  }};
};
globalThis.PYA_THREE = T;
function pompa(n) { for (var i = 0; i < n && coda.length; i += 1) { coda.shift()(i * 16); } }
function stato() {
  var c = elementi['pya-scena-3d-caption'];
  return {testo: c.firstChild.textContent.trim(), titolo: c.title || '', coda: coda.length,
          disegni: disegni, continuo: continuo, selezioni: selezioni, raggi: raggi,
          glbLetto: glbLetto, glbVuoto: testoGlb === '', tastiera: tastiera,
          attr: renderer ? renderer.domElement.attr : null};
}
"""

_PAROLE_FINTE = {"site": "Tutto il sito", "chapter": "Capitolo", "proxies": "proxy", "noProxy": "senza",
                 "notLoaded": "proxy non caricato", "failed": "non caricati", "skipped": "fuori",
                 "missing": "senza file", "noWebgl": "niente WebGL", "loading": "Carico i proxy",
                 "keys": "frecce, + e -, Esc"}
_GLB_BUONO = "Z2xURi0xMjM0NTY3OA=="


def _dati_finti(**altro):
    dati = {"proxies": [{"k": "a", "u": "u1"}, {"k": "b", "u": "u2"}],
            "unitProxies": {"u1": ["a"], "u2": ["b"]}, "names": {"u1": "SU001", "u2": "SU002"},
            "epochs": {"u1": ["ep1"], "u2": ["ep1"]}, "epochNames": {"ep1": "II A.D."},
            "missing": 0, "skipped": 0, "skippedNames": [], "words": _PAROLE_FINTE}
    dati.update(altro)
    return dati


def _esegui_scena(tmp_path, dati, *, glb=None, prima="", dopo="pompa(50);"):
    """Lo script della scena in node con un finto browser (three.js finto):
    torna lo stato della didascalia, dei fotogrammi e degli eventi dopo ``dopo``."""
    import json
    from modules.s3dgraphy import em_narrative_3d as n3d
    if glb is None:
        glb = {p["k"]: _GLB_BUONO for p in dati["proxies"]}
    f = tmp_path / "scena.js"
    f.write_text(_BROWSER_FINTO.replace("__DATI__", json.dumps(dati)).replace("__GLB__", json.dumps(glb))
                 + prima + n3d._JS + "\n" + dopo + "\nconsole.log(JSON.stringify(stato()));\n",
                 encoding="utf-8")
    esito = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert esito.returncode == 0, esito.stderr
    return json.loads(esito.stdout.strip().splitlines()[-1])


_NODE = pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")


@_NODE
def test_un_proxy_che_non_si_legge_non_ferma_la_scena(tmp_path):
    """Il GLTFLoader di three.js, per un file che non è un GLB (troppo corto,
    non JSON, compresso Draco senza decodificatore), lancia l'errore subito
    invece di chiamare onError: la scena restava ferma su «Carico i proxy…»
    e non si disegnava niente (prova nel browser su TempluMare, 17 ottobre)."""
    fuori = _esegui_scena(tmp_path, _dati_finti(), glb={"a": "AAAA", "b": _GLB_BUONO})
    assert fuori["testo"] == "Tutto il sito · 2 proxy · 1 non caricati"


@_NODE
def test_l_unita_col_proxy_non_caricato_lo_dice(tmp_path):
    fuori = _esegui_scena(tmp_path, _dati_finti(), glb={"a": "AAAA", "b": _GLB_BUONO},
                          dopo="pompa(50); PYA_SEL.select('ep1', 'u1', null); pompa(50);")
    assert "SU001: proxy non caricato" in fuori["testo"]


@_NODE
def test_senza_webgl_la_didascalia_lo_dice(tmp_path):
    """three.js 0.186 vuole WebGL 2 e lancia «Error creating WebGL context»
    se non lo ottiene: la scena restava un riquadro vuoto (revisione finale)."""
    fuori = _esegui_scena(tmp_path, _dati_finti(),
                          prima="T.WebGLRenderer = function () { throw new Error('Error creating WebGL context.'); };\n",
                          dopo="PYA_SEL.select('ep1', 'u1', null);")
    assert fuori["testo"] == "niente WebGL"


@_NODE
def test_la_scena_ferma_non_si_ridisegna(tmp_path):
    """Si disegna quando qualcosa cambia (caricamento, selezione, volo,
    mouse), non a ogni fotogramma: la pagina è un documento da leggere."""
    fuori = _esegui_scena(tmp_path, _dati_finti())
    assert fuori["continuo"] is False and fuori["coda"] == 0 and fuori["disegni"] >= 1
    fuori = _esegui_scena(tmp_path, _dati_finti(),
                          dopo="pompa(50); var prima = disegni; PYA_SEL.select('ep1', 'u1', null); pompa(50); "
                               "if (disegni <= prima) { throw new Error('la selezione non ridisegna'); }")
    assert fuori["coda"] == 0


@_NODE
def test_i_proxy_rimasti_fuori_si_elencano_nel_suggerimento(tmp_path):
    fuori = _esegui_scena(tmp_path, _dati_finti(skipped=2, skippedNames=["SU099.glb", "SU100.glb"]))
    assert fuori["testo"] == "Tutto il sito · 2 proxy · 2 fuori"
    assert "SU099.glb, SU100.glb" in fuori["titolo"]


@_NODE
def test_chi_eredita_la_geometria_porta_il_proxy_nel_suo_periodo(tmp_path):
    """La USV100 eredita la geometria di SU002 (decisione 2): nel periodo
    o nel capitolo della USV il proxy c'è anche se il proprietario non c'è."""
    dati = _dati_finti(proxies=[{"k": "a", "u": "u1"}], unitProxies={"u1": ["a"], "u3": ["a"]},
                       names={"u1": "SU002", "u3": "USV100"}, epochs={"u1": ["ep1"], "u3": ["ep2"]},
                       epochNames={"ep1": "II A.D.", "ep2": "III A.D."})
    fuori = _esegui_scena(tmp_path, dati, dopo="pompa(50); PYA_SEL.select('ep2', null, null); pompa(50);")
    assert fuori["testo"] == "III A.D. · 1 proxy"
    fuori = _esegui_scena(tmp_path, dati, dopo="pompa(50); PYA_SEL.select(null, null, ['u3']); pompa(50);")
    assert fuori["testo"] == "Capitolo · 1 proxy"


@_NODE
def test_il_clic_destro_e_due_dita_non_selezionano(tmp_path):
    fuori = _esegui_scena(tmp_path, _dati_finti(), dopo=r"""
pompa(50); colpo = 'u2'; var el = renderer.domElement;
el.emetti('pointerdown', {button: 2, pointerId: 1, clientX: 10, clientY: 10});
el.emetti('pointerup', {button: 2, pointerId: 1, clientX: 10, clientY: 10});
el.emetti('pointerdown', {button: 0, pointerId: 2, pointerType: 'touch', clientX: 10, clientY: 10});
el.emetti('pointerdown', {button: 0, pointerId: 3, pointerType: 'touch', clientX: 30, clientY: 30});
el.emetti('pointerup', {button: 0, pointerId: 2, pointerType: 'touch', clientX: 10, clientY: 10});
el.emetti('pointerup', {button: 0, pointerId: 3, pointerType: 'touch', clientX: 30, clientY: 30});
el.emetti('pointerdown', {button: 0, pointerId: 4, clientX: 50, clientY: 50});
el.emetti('pointerup', {button: 0, pointerId: 4, clientX: 51, clientY: 50});
""")
    assert fuori["selezioni"] == [["ep1", "u2", None]]


@_NODE
def test_i_modelli_si_leggono_solo_quando_si_apre_il_3d(tmp_path):
    """Con la mappa davanti la scheda 3D è nascosta: i GLB (fino a 40 MB)
    non si leggono finché non la si apre, e dopo la lettura il testo si
    libera."""
    fuori = _esegui_scena(tmp_path, _dati_finti(), prima="vistaFinta.hidden = true;\n", dopo="pompa(50);")
    assert fuori["glbLetto"] == 0 and fuori["testo"] == "Tutto il sito · 2 proxy"
    fuori = _esegui_scena(tmp_path, _dati_finti(), prima="vistaFinta.hidden = true;\n",
                          dopo="vistaFinta.hidden = false; documentoEmetti('pya:tab', {detail: '3d'}); pompa(50);")
    assert fuori["glbLetto"] >= 1 and fuori["glbVuoto"] is True and fuori["disegni"] >= 1


@_NODE
def test_il_passaggio_del_mouse_fa_un_raggio_per_fotogramma(tmp_path):
    """Un raggio a ogni movimento del mouse, e anche sui contorni: ora uno
    per fotogramma, solo sulle mesh."""
    fuori = _esegui_scena(tmp_path, _dati_finti(), dopo=r"""
pompa(50); colpo = 'u1'; var el = renderer.domElement;
for (var i = 0; i < 5; i += 1) { el.emetti('pointermove', {buttons: 0, pointerType: 'mouse', clientX: i, clientY: i}); }
var prima = raggi.length; pompa(5);
if (prima !== 0) { throw new Error('raggi prima del fotogramma: ' + prima); }
""")
    assert fuori["raggi"] == [False]


@_NODE
def test_la_scena_si_usa_anche_con_la_tastiera(tmp_path):
    fuori = _esegui_scena(tmp_path, _dati_finti(), dopo=r"""
pompa(50); var el = renderer.domElement;
el.emetti('keydown', {key: '+'});
if (!coda.length) { throw new Error('lo zoom da tastiera non ridisegna'); }
pompa(50); el.emetti('keydown', {key: 'Escape'});
""")
    assert fuori["attr"]["tabindex"] == "0" and fuori["attr"]["role"] == "application"
    assert fuori["attr"]["aria-label"] == "frecce, + e -, Esc"
    assert fuori["tastiera"] == [True] and fuori["selezioni"][-1] == [None, None, None]


@_NODE
def test_l_inquadratura_tiene_conto_della_larghezza(tmp_path):
    """Su un riquadro più stretto che alto l'oggetto stava nel campo
    verticale ma usciva ai lati: la distanza guarda il campo più stretto."""
    import json
    import math
    import re
    from modules.s3dgraphy import em_narrative_3d as n3d
    funzione = re.search(r"function distanza\(raggio, fov, aspetto\) \{.*?\n  \}", n3d._JS, re.S).group(0)
    f = tmp_path / "distanza.js"
    f.write_text(funzione + "\nconsole.log(JSON.stringify([distanza(10, 40, 2), distanza(10, 40, 0.5)]));\n",
                 encoding="utf-8")
    largo, stretto = json.loads(subprocess.run(["node", str(f)], capture_output=True, text=True,
                                               check=True).stdout)
    assert abs(largo - 10 / math.sin(math.radians(20)) * 1.05) < 1e-9
    assert stretto > largo * 1.5


def test_la_vista_passa_i_nomi_dei_proxy_rimasti_fuori(tmp_path):
    import json
    import re
    from modules.s3dgraphy import em_narrative_3d as n3d
    scena = _scena(tmp_path)
    scena.skipped = ["SU099.glb"]
    vista = n3d.scene_view(scena, {}, lang="it")
    dati = _blocco(vista, "pya-scena-3d-data")
    assert dati["skipped"] == 1 and dati["skippedNames"] == ["SU099.glb"]


def test_la_scena_non_riusa_gli_id_del_pannello_delle_fonti(tmp_path):
    """Il pannello delle fonti e dei media (em_narrative_html._JS_FONTI) crea
    per un modello 3D un elemento con id «pya-3d» e lo cerca con
    getElementById: con la scena che usava lo stesso id, il clic su un GLB
    scelto fra i media metteva il visore dentro il pannello della scena e la
    scena spariva (revisione finale, 17 ottobre)."""
    import re
    from modules.s3dgraphy import em_narrative_3d as n3d
    from modules.s3dgraphy import em_narrative_html as nh
    vista = n3d.scene_view(_scena(tmp_path), {}, lang="it")
    della_scena = set(re.findall(r'id="([\w-]+)"', vista.panel + vista.script.replace(n3d.three_bundle(), "")))
    della_scena |= set(re.findall(r"getElementById\('([\w-]+)'\)", n3d._JS))
    delle_fonti = set(re.findall(r'id="([\w-]+)"', nh._JS_FONTI))
    delle_fonti |= set(re.findall(r"getElementById\('([\w-]+)'\)", nh._JS_FONTI))
    assert "pya-3d" in delle_fonti and della_scena
    assert not (della_scena & delle_fonti)
