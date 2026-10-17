"""La scena 3D dei proxy nell'HTML della narrativa (Enzo, 17 ottobre 2026:
«assemblare insieme tutti i 3D come ad esempio per la mappa e quando nel
capitolo si fa riferimento a quello se ci clicco sopra … si evidenzia il
proxy interessato e gli altri sono in trasparenza»).

I proxy vengono dalla regola della libreria, la stessa di EMStudio
(``s3dgraphy.paradata_view.proxy_instances``: unità → proprietà «geometry» →
forma → risorsa ``proxy_model``; una proprietà ereditata si disegna una
volta, dal proprietario); i file dal database, come per il progetto EM
(:func:`em_project.media_index`, :func:`em_project.media_file_for`). Ogni GLB
di EMStudio porta già la sua posizione nella scena (il nodo con traslazione
e rotazione esportato da Blender): messi insieme si incastrano — TempluMare:
65 proxy, 2,4 MB, 43 × 14 × 52 m. La pagina li porta in base64 e li disegna
con three.js, che sta dentro la pagina (:data:`BUNDLE`, rifatto da
``scripts/build_three_bundle.sh``): niente rete.
"""
from __future__ import annotations

import base64
import html as _html
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_LOG = logging.getLogger(__name__)

#: un proxy più grande non entra nella pagina; né oltre il totale
MAX_PROXY_FILE = 15 * 1024 * 1024
MAX_PROXY_FILES = 40 * 1024 * 1024

#: three.js 0.186.1 con GLTFLoader e OrbitControls, in uno script classico (window.PYA_THREE)
BUNDLE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "resources", "js", "pya_three_scene.min.js")


@dataclass
class SceneProxy:
    """Un file di proxy: la risorsa (``key``), l'unità che lo possiede, il
    locator dell'em.json e, trovato il file, dove sta e quanto pesa."""
    key: str
    unit: str
    locator: str
    path: str = ""
    size: int = 0


@dataclass
class Scene:
    proxies: List[SceneProxy] = field(default_factory=list)
    unit_proxies: Dict[str, List[str]] = field(default_factory=dict)
    names: Dict[str, str] = field(default_factory=dict)
    epochs: Dict[str, List[str]] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _locatore(nodo) -> str:
    """Il primo indirizzo locale del file della risorsa: l'url, o uno degli
    indirizzi alternativi (``data.addresses``)."""
    dati = getattr(nodo, "data", None) or {}
    candidati = [getattr(nodo, "url", None), dati.get("url")]
    candidati += [a.get("locator") for a in dati.get("addresses") or [] if isinstance(a, dict)]
    for c in candidati:
        c = str(c or "").strip()
        if c and "://" not in c:
            return c
    return ""


def scene_proxies(graph) -> Scene:
    """I proxy dal grafo, senza file: uno per risorsa col suo proprietario,
    e per ogni unità le chiavi dei suoi proxy — anche per chi ha la stessa
    proprietà «geometry» senza esserne il proprietario (la USV che eredita
    la geometria della US che completa)."""
    from s3dgraphy.paradata_view import proxy_instances
    from .em_narrative_map import epochs_of
    scena = Scene()
    epoche = epochs_of(graph)
    eredi: Dict[str, List[str]] = {}
    for e in getattr(graph, "edges", None) or []:
        if getattr(e, "edge_type", None) == "has_property":
            eredi.setdefault(str(e.edge_target), []).append(str(e.edge_source))
    visti = set()
    for ist in proxy_instances(graph):
        if ist.get("removed") or not ist.get("files"):
            continue
        proprietario = str(ist["owner"])
        chiavi = []
        for rid in ist["files"]:
            rid = str(rid)
            loc = _locatore(graph.find_node_by_id(rid))
            if not loc:
                continue
            if rid not in visti:
                visti.add(rid)
                scena.proxies.append(SceneProxy(key=rid, unit=proprietario, locator=loc))
            chiavi.append(rid)
        if not chiavi:
            continue
        for u in [proprietario] + [x for x in eredi.get(str(ist.get("beside")), []) if x != proprietario]:
            lista = scena.unit_proxies.setdefault(u, [])
            lista.extend(k for k in chiavi if k not in lista)
            nodo = graph.find_node_by_id(u)
            scena.names[u] = str(getattr(nodo, "name", "") or u)
            scena.epochs[u] = list(epoche.get(u, []))
    return scena


def build_scene(graph, connection_url: str, resize_base: str = "", *,
                max_file: int = MAX_PROXY_FILE, budget: int = MAX_PROXY_FILES) -> Scene:
    """:func:`scene_proxies` con i file dal database (come il progetto EM) e
    i limiti: i più piccoli entrano per primi finché ci stanno, quelli
    rimasti fuori si contano. Un'unità senza più proxy resta col suo nome."""
    from .em_project import media_file_for, media_index
    scena = scene_proxies(graph)
    if not scena.proxies:
        return scena
    indice = media_index(connection_url, resize_base or "")
    trovati = []
    for p in scena.proxies:
        percorso = media_file_for(p.locator, indice)
        if percorso is None:
            scena.missing.append(p.locator)
            continue
        p.path, p.size = percorso, os.path.getsize(percorso)
        trovati.append(p)
    dentro, totale = set(), 0
    for p in sorted(trovati, key=lambda x: x.size):
        if p.size > max_file or totale + p.size > budget:
            scena.skipped.append(os.path.basename(p.locator))
            continue
        dentro.add(p.key)
        totale += p.size
    scena.proxies = [p for p in trovati if p.key in dentro]
    tenute = {u: [k for k in ks if k in dentro] for u, ks in scena.unit_proxies.items()}
    scena.unit_proxies = {u: ks for u, ks in tenute.items() if ks}
    return scena


_WORDS = {
    "it": {"site": "Tutto il sito", "chapter": "Le unità del capitolo", "reset": "tutto il sito",
           "proxies": "proxy", "noProxy": "senza proxy 3D", "failed": "non caricati",
           "skipped": "rimasti fuori (troppo grandi)", "missing": "senza file",
           "noWebgl": "Questo browser non mostra il 3D (WebGL).", "loading": "Carico i proxy…",
           "hint": "Trascina per girare, rotella per lo zoom; clic su un proxy o su un'unità nel testo."},
    "en": {"site": "Whole site", "chapter": "The chapter's units", "reset": "whole site",
           "proxies": "proxies", "noProxy": "no 3D proxy", "failed": "not loaded",
           "skipped": "left out (too large)", "missing": "without a file",
           "noWebgl": "This browser cannot show 3D (WebGL).", "loading": "Loading the proxies…",
           "hint": "Drag to turn, wheel to zoom; click a proxy or a unit in the text."},
}


def _lang(lang: Optional[str]) -> str:
    return "it" if str(lang or "it")[:2] == "it" else "en"


_CSS = """
/* pyArchInit: la scena 3D dei proxy */
#pya-scena-3d { position: relative; width: 100%; height: min(62vh, 560px); touch-action: none;
  background: rgba(127,127,127,.07); border-radius: 4px; overflow: hidden; }
@media (max-width: 899px) {
  #pya-scena-3d { height: 34vh; }
}
#pya-scena-3d canvas { display: block; width: 100%; height: 100%; }
.pya-scena-3d-tip { position: absolute; pointer-events: none; padding: .1rem .45rem; border-radius: 3px;
  background: rgba(0,0,0,.75); color: #fff; font: 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  transform: translate(-50%, -150%); white-space: nowrap; }
"""

_JS = r"""
(function () {
  var T = window.PYA_THREE;
  var nodo = document.getElementById('pya-scena-3d-data');
  var tela = document.getElementById('pya-scena-3d');
  var cap = document.getElementById('pya-scena-3d-caption');
  if (!nodo || !tela || !window.PYA_SEL) { return; }
  var D = JSON.parse(nodo.textContent), W = D.words;
  var vista = tela.closest('[data-pya-view]');
  var stato = {e: null, u: null, g: null}, S = null, senza3d = false;

  function epoche(u) { return D.epochs[u] || []; }
  function nel(u, e) { return epoche(u).indexOf(e) >= 0; }
  function dentro(u) {
    if (stato.e) { return nel(u, stato.e); }
    if (stato.g) { return stato.g.indexOf(u) >= 0; }
    return false;
  }
  function scritta(t) { if (cap && cap.firstChild) { cap.firstChild.textContent = t + ' '; } }
  function didascalia() {
    if (senza3d) { scritta(W.noWebgl); return; }
    var gruppo = !!(stato.e || stato.g), n = 0, parti = [];
    D.proxies.forEach(function (p) { if (!gruppo || dentro(p.u)) { n += 1; } });
    parti.push(stato.e ? (D.epochNames[stato.e] || stato.e) : (stato.g ? W.chapter : W.site));
    parti.push(n + ' ' + W.proxies);
    if (stato.u) {
      var nome = D.names[stato.u] || PYA_SEL.units[stato.u] || stato.u;
      parti.push((D.unitProxies[stato.u] || []).length ? nome : nome + ': ' + W.noProxy);
    }
    if (S && S.failed) { parti.push(S.failed + ' ' + W.failed); }
    if (D.skipped) { parti.push(D.skipped + ' ' + W.skipped); }
    if (D.missing) { parti.push(D.missing + ' ' + W.missing); }
    scritta(parti.join(' · '));
    if (cap) { cap.title = D.skipped ? W.skipped + ': ' + (D.skippedNames || []).join(', ') : ''; }
  }
  function buffer(b64) {
    var s = atob(b64), n = s.length, a = new Uint8Array(n);
    for (var i = 0; i < n; i += 1) { a[i] = s.charCodeAt(i); }
    return a.buffer;
  }
  function clona(m) {
    var c = m.clone();
    c.userData.pya = {opacity: m.opacity, transparent: m.transparent, depthWrite: m.depthWrite};
    return c;
  }
  function trasparenza(m, alfa) {
    var b = m.userData.pya;
    if (alfa === null) {
      m.opacity = b.opacity; m.transparent = b.transparent; m.depthWrite = b.depthWrite;
    } else {
      m.opacity = Math.min(b.opacity, alfa); m.transparent = true; m.depthWrite = false;
    }
    m.needsUpdate = true;
  }
  function contorno(it, acceso) {
    if (acceso && !it.bordi) {
      it.bordi = it.mesh.map(function (o) {
        var l = new T.LineSegments(new T.EdgesGeometry(o.geometry, 30),
          new T.LineBasicMaterial({color: 0xf5b942, depthTest: false, transparent: true}));
        l.renderOrder = 999;
        o.add(l);
        return l;
      });
    }
    (it.bordi || []).forEach(function (l) { l.visible = acceso; });
  }
  function crea() {
    if (S || senza3d) { return; }
    // three.js 0.186 vuole WebGL 2 e lancia se non lo ottiene: niente
    // contesto di prova, si prova il vero
    var r = null;
    try { r = T ? new T.WebGLRenderer({antialias: true, alpha: true}) : null; } catch (err) { r = null; }
    if (!r) { senza3d = true; didascalia(); return; }
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.outputColorSpace = T.SRGBColorSpace;
    tela.appendChild(r.domElement);
    var scena = new T.Scene();
    var cam = new T.PerspectiveCamera(40, 1, 0.05, 20000);
    var ctl = new T.OrbitControls(cam, r.domElement);
    ctl.enableDamping = true;
    ctl.addEventListener('change', pianifica);
    scena.add(new T.HemisphereLight(0xffffff, 0x666666, 2.2));
    var luce = new T.DirectionalLight(0xffffff, 1.5);
    luce.position.set(1, 2, 1.5);
    scena.add(luce);
    var tip = document.createElement('div');
    tip.className = 'pya-scena-3d-tip';
    tip.hidden = true;
    tela.appendChild(tip);
    S = {r: r, scena: scena, cam: cam, ctl: ctl, tip: tip, items: [], failed: 0, volo: null,
         giro: null, fermo: false};
    var loader = new T.GLTFLoader(), attesi = D.proxies.length;
    function fatto() { attesi -= 1; if (attesi <= 0) { applica(true); } }
    scritta(W.loading);
    D.proxies.forEach(function (p) {
      // il GLTFLoader, per un file che non è un GLB (troppo corto, non JSON,
      // compresso Draco senza decodificatore), lancia l'errore subito invece
      // di chiamare onError: ogni proxy si chiude una volta sola, letto o no
      var chiuso = false, dati;
      function finito() { if (!chiuso) { chiuso = true; fatto(); } }
      function guasto() { if (!chiuso) { S.failed += 1; } finito(); }
      try { dati = buffer(p.glb); } catch (err) { guasto(); return; }
      try {
        loader.parse(dati, '', function (gltf) {
          var it = {u: p.u, k: p.k, root: gltf.scene, mat: [], mesh: [], bordi: null};
          gltf.scene.traverse(function (o) {
            if (!o.isMesh) { return; }
            o.material = Array.isArray(o.material) ? o.material.map(clona) : clona(o.material);
            [].concat(o.material).forEach(function (m) { it.mat.push(m); });
            o.userData.pyaUnit = p.u;
            it.mesh.push(o);
          });
          scena.add(gltf.scene);
          it.box = new T.Box3().setFromObject(gltf.scene);
          S.items.push(it);
          finito();
        }, guasto);
      } catch (err) { guasto(); }
    });
    if (!D.proxies.length) { applica(true); }
    if (window.ResizeObserver) { new ResizeObserver(misura).observe(tela); }
    window.addEventListener('resize', misura);
    misura();
    eventi();
    avvia();
  }
  function misura() {
    if (!S) { return; }
    var w = tela.clientWidth, h = tela.clientHeight;
    if (!w || !h) { return; }
    S.r.setSize(w, h, false);
    S.cam.aspect = w / h;
    S.cam.updateProjectionMatrix();
    pianifica();
  }
  // si disegna quando qualcosa cambia (caricamento, selezione, volo, mouse,
  // misure), non a ogni fotogramma: la pagina è un documento da leggere
  function pianifica() {
    if (!S || S.fermo || S.giro) { return; }
    S.giro = window.requestAnimationFrame(disegna);
  }
  function disegna(t) {
    S.giro = null;
    var ancora = false;
    if (S.volo) { vola(t); ancora = true; }
    if (S.ctl.update()) { ancora = true; }       // l'inerzia dei controlli
    S.r.render(S.scena, S.cam);
    if (ancora) { pianifica(); }
  }
  function avvia() { if (S) { S.fermo = false; pianifica(); } }
  function ferma() {
    if (!S) { return; }
    S.fermo = true;
    if (S.giro) { window.cancelAnimationFrame(S.giro); S.giro = null; }
  }
  function applica(subito) {
    if (!S) { didascalia(); return; }
    var bersagli = stato.u ? (D.unitProxies[stato.u] || []) : [];
    var gruppo = !!(stato.e || stato.g), box = new T.Box3(), scelti = 0;
    S.items.forEach(function (it) {
      var hi = bersagli.indexOf(it.k) >= 0, alfa = null;
      if (bersagli.length) { alfa = hi ? null : (dentro(it.u) ? 0.25 : 0.04); }
      else if (gruppo) { alfa = dentro(it.u) ? null : 0.04; }
      it.mat.forEach(function (m) { trasparenza(m, alfa); });
      contorno(it, hi);
      if (hi) { box.union(it.box); scelti += 1; }
    });
    if (scelti) {
      var c = box.getCenter(new T.Vector3()), s = box.getSize(new T.Vector3()).multiplyScalar(1.5);
      box.set(c.clone().sub(s), c.clone().add(s));
    } else if (gruppo) {
      S.items.forEach(function (it) { if (dentro(it.u)) { box.union(it.box); } });
    }
    if (box.isEmpty()) { S.items.forEach(function (it) { box.union(it.box); }); }
    if (!box.isEmpty()) { inquadra(box, subito); }
    didascalia();
    pianifica();
  }
  function inquadra(box, subito) {
    var centro = box.getCenter(new T.Vector3());
    var raggio = Math.max(box.getSize(new T.Vector3()).length() / 2, 0.5);
    var dir = S.cam.position.clone().sub(S.ctl.target);
    if (dir.lengthSq() < 1e-9) { dir.set(1, 0.8, 1); }
    dir.normalize();
    var dist = raggio / Math.sin(S.cam.fov * Math.PI / 360) * 1.05;
    S.cam.near = Math.max(dist / 1000, 0.01);
    S.cam.far = dist * 100;
    S.cam.updateProjectionMatrix();
    var pos = centro.clone().add(dir.multiplyScalar(dist));
    if (subito) {
      S.cam.position.copy(pos);
      S.ctl.target.copy(centro);
      S.volo = null;
      return;
    }
    S.volo = {da: S.cam.position.clone(), a: pos, t0: S.ctl.target.clone(), t1: centro, inizio: null};
  }
  function vola(t) {
    var v = S.volo;
    if (v.inizio === null) { v.inizio = t; }
    var x = Math.min((t - v.inizio) / 600, 1), k = x * x * (3 - 2 * x);
    S.cam.position.lerpVectors(v.da, v.a, k);
    S.ctl.target.lerpVectors(v.t0, v.t1, k);
    if (x >= 1) { S.volo = null; }
  }
  function sotto(ev) {
    var b = S.r.domElement.getBoundingClientRect();
    var p = new T.Vector2(((ev.clientX - b.left) / b.width) * 2 - 1,
                          -((ev.clientY - b.top) / b.height) * 2 + 1);
    var rc = new T.Raycaster();
    rc.setFromCamera(p, S.cam);
    var colpi = rc.intersectObjects(S.items.map(function (it) { return it.root; }), true);
    for (var i = 0; i < colpi.length; i += 1) {
      var o = colpi[i].object, m = [].concat(o.material)[0];
      if (o.isMesh && o.userData.pyaUnit && m && (!m.transparent || m.opacity >= 0.2)) {
        return o.userData.pyaUnit;
      }
    }
    return null;
  }
  function eventi() {
    var el = S.r.domElement, giu = null;
    el.addEventListener('pointermove', function (ev) {
      if (ev.buttons) { S.tip.hidden = true; return; }
      var u = sotto(ev);
      S.tip.hidden = !u;
      if (u) {
        var b = tela.getBoundingClientRect();
        S.tip.textContent = D.names[u] || PYA_SEL.units[u] || u;
        S.tip.style.left = (ev.clientX - b.left) + 'px';
        S.tip.style.top = (ev.clientY - b.top) + 'px';
      }
    });
    el.addEventListener('pointerleave', function () { S.tip.hidden = true; });
    el.addEventListener('pointerdown', function (ev) { giu = [ev.clientX, ev.clientY]; });
    el.addEventListener('pointerup', function (ev) {
      var mosso = !giu || Math.abs(ev.clientX - giu[0]) + Math.abs(ev.clientY - giu[1]) > 5;
      giu = null;
      if (mosso) { return; }
      var u = sotto(ev);
      if (!u) { return; }
      var e = (stato.e && nel(u, stato.e)) ? stato.e : (epoche(u)[0] || PYA_SEL.firstEpoch[u] || null);
      PYA_SEL.select(e, u, null);
    });
  }
  function forse() { if (!S && !senza3d && vista && !vista.hidden) { crea(); } }
  document.addEventListener('pya:tab', function (ev) {
    if (ev.detail === '3d') { forse(); misura(); avvia(); } else { ferma(); }
  });
  PYA_SEL.add(function (e, u, g) { stato = {e: e, u: u, g: g}; applica(false); });
  forse();
})();
"""


def three_bundle() -> str:
    """Il pacchetto three.js da mettere nella pagina (``</script`` reso
    innocuo), o una stringa vuota se manca."""
    try:
        with open(BUNDLE, encoding="utf-8") as fh:
            return fh.read().replace("</script", "<\\/script")
    except OSError:
        return ""


def scene_view(scene: Scene, epoch_names_map: Dict[str, str], lang: Optional[str] = None):
    """La scena come vista del pannello (:mod:`em_narrative_views`): il
    riquadro, la didascalia, il pacchetto three.js, i proxy in base64 e lo
    script della scena. None se il pacchetto non c'è."""
    from .em_narrative_html import _json_script
    from .em_narrative_views import View
    pacchetto = three_bundle()
    if not pacchetto:
        _LOG.warning("Scena 3D della narrativa: manca %s", BUNDLE)
        return None
    parole = _WORDS[_lang(lang)]
    proxy = []
    for p in scene.proxies:
        with open(p.path, "rb") as fh:
            proxy.append({"k": p.key, "u": p.unit, "glb": base64.b64encode(fh.read()).decode("ascii")})
    dati = {"proxies": proxy, "unitProxies": scene.unit_proxies, "names": scene.names,
            "epochs": scene.epochs, "epochNames": dict(epoch_names_map or {}),
            "missing": len(scene.missing), "skipped": len(scene.skipped),
            "skippedNames": list(scene.skipped[:50]), "words": parole}
    pannello = ('<div id="pya-scena-3d" class="pya-scena-3d"></div>'
                '<p class="pya-caption" id="pya-scena-3d-caption"><span>%s </span>'
                '<a href="#pya-map" class="pya-reset">%s</a> <small>%s</small></p>'
                % (_html.escape(parole["site"]), _html.escape(parole["reset"]), _html.escape(parole["hint"])))
    script = ("<script>%s</script>" % pacchetto
              + '<script type="application/json" id="pya-scena-3d-data">%s</script>' % _json_script(dati)
              + "<script>%s</script>" % _JS)
    return View(key="3d", label="3D", panel=pannello, css=_CSS, script=script)
