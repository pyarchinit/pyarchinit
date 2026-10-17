"""La mappa interattiva nell'HTML della narrativa (Enzo, 13 ottobre 2026:
«cliccando una US nel testo la mappa evidenzia quella US e solo le US di
quel periodo, contorno ed etichette»).

Quattro pezzi, i primi tre senza QGIS: i periodi delle unità dagli archi
del grafo (:func:`epochs_of`, :func:`units_meta`), l'SVG dei disegni
(:func:`svg_map`), la mappa come vista del pannello (:func:`map_view`: il
suo CSS e il suo script, che si registra nella selezione comune); e il
lettore delle geometrie dal database (:func:`drawings_from_db`, QGIS).
Dalla 5.13.132 i link delle menzioni, i titoli dei capitoli, il pannello e
i clic sono di :mod:`em_narrative_views`, che mette la mappa accanto alla
scena 3D (:func:`em_narrative_views.html_with_views`); :func:`inject_map`
e :func:`html_with_map` restano per la sola mappa.
"""
from __future__ import annotations

import html as _html
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

EPOCH_EDGES = ("has_first_epoch", "survive_in_epoch")

#: Un disegno di un'unità: gli anelli (il primo esterno, gli altri buchi)
#: in coordinate del layer, e il punto dell'etichetta (None = senza).
@dataclass
class Drawing:
    unit_id: str
    rings: List[List[Tuple[float, float]]]
    label: Optional[Tuple[float, float]] = None


_WORDS = {
    "it": {"site": "Tutto il sito", "reset": "tutto il sito", "drawings": "unità", "tab": "Mappa",
           "hint": "Clicca il nome di un'unità nel testo o il titolo di un capitolo."},
    "en": {"site": "Whole site", "reset": "whole site", "drawings": "units", "tab": "Map",
           "hint": "Click a unit name in the text or a chapter title."},
}


def _lang(lang: Optional[str]) -> str:
    return "it" if str(lang or "it")[:2] == "it" else "en"


# ---------------------------------------------------------------- periodi

def epochs_of(graph) -> Dict[str, List[str]]:
    """Unità → le sue epoche: prima quella di ``has_first_epoch``, poi
    quelle in cui sopravvive (``survive_in_epoch``), nell'ordine degli archi."""
    out: Dict[str, List[str]] = {}
    for e in getattr(graph, "edges", None) or []:
        tipo = getattr(e, "edge_type", None)
        if tipo not in EPOCH_EDGES:
            continue
        src, dst = str(e.edge_source), str(e.edge_target)
        lista = out.setdefault(src, [])
        if dst in lista:
            continue
        if tipo == "has_first_epoch":
            lista.insert(0, dst)
        else:
            lista.append(dst)
    return out


def epoch_names(graph) -> Dict[str, str]:
    return {str(n.node_id): str(getattr(n, "name", "") or n.node_id)
            for n in (getattr(graph, "nodes", None) or []) if type(n).__name__ == "EpochNode"}


def epoch_anchor(graph, chapter) -> Optional[str]:
    """L'epoca di un capitolo: la sua ancora, se è un nodo epoca."""
    ancora = getattr(chapter, "anchor", None)
    if not ancora or graph is None:
        return None
    nodo = graph.find_node_by_id(str(ancora))
    return str(ancora) if nodo is not None and type(nodo).__name__ == "EpochNode" else None


def units_meta(graph) -> Dict[str, Dict[str, Any]]:
    """Le unità del grafo che sono righe della scheda (sito e numero), con
    nome, numero, area, tipo ed epoche."""
    from ..utility.em_matrix_links import unit_identity
    epoche = epochs_of(graph)
    out: Dict[str, Dict[str, Any]] = {}
    for n in getattr(graph, "nodes", None) or []:
        identita = unit_identity(n)
        if not identita:
            continue
        uid = str(n.node_id)
        out[uid] = {"name": str(getattr(n, "name", "") or uid), "number": identita["us"],
                    "area": identita.get("area", ""), "sito": identita["sito"],
                    "unita_tipo": identita.get("unita_tipo", ""), "epochs": list(epoche.get(uid, []))}
    return out


# ---------------------------------------------------------------- SVG

def _num(v: float) -> str:
    s = "%.2f" % float(v)
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return "0" if s in ("-0", "") else s


def _plain(v: float):
    v = round(float(v), 2)
    return int(v) if v == int(v) else v


def svg_map(drawings: Sequence[Drawing], meta: Dict[str, Dict[str, Any]]) -> Tuple[str, Dict[str, list]]:
    """L'SVG dei disegni (y capovolta, origine nell'angolo in alto a sinistra
    del sito) e i riquadri: ``all`` e uno per epoca, ``[x, y, w, h]``."""
    punti = [p for d in drawings for anello in d.rings for p in anello]
    if not punti:
        return "", {}
    minx = min(p[0] for p in punti); maxx = max(p[0] for p in punti)
    miny = min(p[1] for p in punti); maxy = max(p[1] for p in punti)

    def sx(x): return x - minx
    def sy(y): return maxy - y

    paths, labels = [], []
    riquadri: Dict[str, List[float]] = {}

    def allarga(chiave, xs, ys):
        box = riquadri.get(chiave)
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        if box is None:
            riquadri[chiave] = [x0, y0, x1, y1]
        else:
            box[0], box[1], box[2], box[3] = min(box[0], x0), min(box[1], y0), max(box[2], x1), max(box[3], y1)

    for d in drawings:
        if not d.rings:
            continue
        m = meta.get(d.unit_id, {})
        epoche = " ".join(m.get("epochs", []) or [])
        pezzi = []
        xs, ys = [], []
        for anello in d.rings:
            if len(anello) < 3:
                continue
            coppie = [(sx(x), sy(y)) for x, y in anello]
            if coppie[0] == coppie[-1]:
                coppie = coppie[:-1]
            xs += [c[0] for c in coppie]; ys += [c[1] for c in coppie]
            pezzi.append("M" + "L".join("%s %s" % (_num(x), _num(y)) for x, y in coppie) + "Z")
        if not pezzi:
            continue
        paths.append('<path class="u" data-u="%s" data-e="%s" d="%s"/>'
                     % (_html.escape(d.unit_id, quote=True), _html.escape(epoche, quote=True), "".join(pezzi)))
        for ep in (m.get("epochs", []) or []):
            allarga(ep, xs, ys)
        if d.label is not None:
            labels.append('<text class="l" data-u="%s" data-e="%s" x="%s" y="%s">%s</text>'
                          % (_html.escape(d.unit_id, quote=True), _html.escape(epoche, quote=True),
                             _num(sx(d.label[0])), _num(sy(d.label[1])),
                             _html.escape(str(m.get("number") or m.get("name") or d.unit_id))))
    larg, alt = maxx - minx, maxy - miny
    boxes: Dict[str, list] = {"all": [0, 0, _plain(larg), _plain(alt)]}
    for ep, (x0, y0, x1, y1) in riquadri.items():
        boxes[ep] = [_plain(x0), _plain(y0), _plain(x1 - x0), _plain(y1 - y0)]
    svg = ('<svg id="pya-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
           'preserveAspectRatio="xMidYMid meet"><g id="pya-units">%s</g><g id="pya-labels">%s</g></svg>'
           % (_num(larg), _num(alt), "".join(paths), "".join(labels)))
    return svg, boxes


# ---------------------------------------------------------------- innesto

_CSS = """
/* pyArchInit: la mappa della narrativa */
#pya-svg { display: block; width: 100%; height: auto; max-height: min(78vh, 640px);
  background: rgba(127,127,127,.07); border-radius: 4px; }
@media (max-width: 899px) {
  #pya-svg { max-height: 34vh; }
}
#pya-svg .u { fill: #e4e4e4; stroke: #b4b4b4; stroke-width: 1; vector-effect: non-scaling-stroke; }
#pya-svg.focus .u { fill: none; stroke: #c9c9c9; opacity: .45; }
#pya-svg.focus .u.on { opacity: 1; stroke: #2f2f2f; fill: none; }
#pya-svg .u.hi { fill: #f5b942 !important; opacity: 1 !important; stroke: #7a4b00 !important; }
#pya-svg .l { display: none; font: bold var(--pya-fs, 12px) sans-serif; fill: #1d1d1d;
  paint-order: stroke; stroke: #fff; stroke-width: .28em; stroke-linejoin: round;
  text-anchor: middle; dominant-baseline: middle; pointer-events: none; }
#pya-svg.focus .l.on { display: block; }
"""

_JS = """
(function () {
  var svg = document.getElementById('pya-svg'); if (!svg) { return; }
  var cap = document.getElementById('pya-caption');
  var all = PYA.boxes.all;
  function fit(b) {
    b = b || all;
    var pad = Math.max(b[2], b[3]) * 0.08 + 0.5;
    var vb = [b[0] - pad, b[1] - pad, b[2] + 2 * pad, b[3] + 2 * pad];
    svg.setAttribute('viewBox', vb.join(' '));
    svg.style.setProperty('--pya-fs', (Math.max(vb[2], vb[3]) / 36) + 'px');
  }
  function show(epoch, unit) {
    var viste = {};
    svg.querySelectorAll('[data-u]').forEach(function (el) {
      var on = !!epoch && (' ' + el.getAttribute('data-e') + ' ').indexOf(' ' + epoch + ' ') >= 0;
      el.classList.toggle('on', on);
      el.classList.toggle('hi', !!unit && el.getAttribute('data-u') === unit);
      if (on) { viste[el.getAttribute('data-u')] = 1; }
    });
    svg.classList.toggle('focus', !!epoch);
    fit(epoch ? PYA.boxes[epoch] : null);
    if (cap) {
      var testo = epoch ? ((PYA.epochNames[epoch] || epoch) + ' \\u00b7 ' + Object.keys(viste).length + ' ' + PYA.words.drawings
                            + (unit ? ' \\u00b7 ' + (PYA.units[unit] || unit) : ''))
                        : PYA.words.site;
      cap.firstChild.textContent = testo + ' ';
    }
  }
  PYA_SEL.add(function (epoch, unit) { show(epoch, unit); });
})();
"""

def map_view(svg: str, boxes: Dict[str, list], meta: Dict[str, Dict[str, Any]],
             epoch_names_map: Dict[str, str], lang: Optional[str] = None):
    """La mappa come vista del pannello (:mod:`em_narrative_views`)."""
    from .em_narrative_html import _json_script
    from .em_narrative_views import View
    parole = _WORDS[_lang(lang)]
    dati = {
        "boxes": boxes,
        "epochNames": {k: v for k, v in (epoch_names_map or {}).items()},
        "units": {u: m.get("name", u) for u, m in meta.items()},
        "words": parole,
    }
    pannello = ('%s<p class="pya-caption" id="pya-caption"><span>%s </span>'
                '<a href="#pya-map" id="pya-reset" class="pya-reset">%s</a> <small>%s</small></p>'
                % (svg, _html.escape(parole["site"]), _html.escape(parole["reset"]),
                   _html.escape(parole["hint"])))
    return View(key="map", label=parole["tab"], panel=pannello, css=_CSS,
                script="<script>var PYA = %s;%s</script>" % (_json_script(dati), _JS))


def inject_map(html: str, svg: str, boxes: Dict[str, list], chapters: Sequence[Dict[str, Any]],
               meta: Dict[str, Dict[str, Any]], epoch_names_map: Dict[str, str],
               lang: Optional[str] = None) -> str:
    """L'HTML della libreria con la sola mappa (:func:`em_narrative_views.
    inject_views`). Senza SVG torna l'HTML com'è."""
    if not svg or not meta:
        return html
    from .em_narrative_views import inject_views
    return inject_views(html, [map_view(svg, boxes, meta, epoch_names_map, lang)], chapters, meta, lang)


# ---------------------------------------------------------------- QGIS

def drawings_from_db(conn_str: str, site: Optional[str], meta: Dict[str, Dict[str, Any]],
                     lang: Optional[str] = None, *, simplify_fraction: float = 1 / 1500.0) -> List[Drawing]:
    """I disegni delle unità dalle viste US e USM del database del progetto
    (sito del grafo), legati alle unità per area e numero; semplificati
    (tolleranza = la diagonale del sito / 1500) e con il punto
    dell'etichetta sul disegno più grande di ogni unità."""
    from qgis.core import QgsWkbTypes
    from ..utility.view_layers import load_view_layer
    from ..utility.view_styles import view_by_name
    out: List[Drawing] = []
    if not meta:
        return out
    for vista in ("pyarchinit_us_view", "pyarchinit_usm_view"):
        e_usm = vista.endswith("usm_view")
        indice: Dict[Tuple[str, str], List[str]] = {}
        for uid, m in meta.items():
            tipo = str(m.get("unita_tipo") or "").upper()
            if tipo.startswith("USM") != e_usm:
                continue
            indice.setdefault((str(m.get("area") or "").strip(), str(m.get("number") or "").strip()), []).append(uid)
        if not indice:
            continue
        spec = view_by_name(vista)
        layer = load_view_layer(conn_str, spec, site, lang) if spec is not None else None
        if layer is None:
            continue
        campi = [f.name() for f in layer.fields()]
        ca = "area_s" if "area_s" in campi else ("area" if "area" in campi else None)
        cu = "us_s" if "us_s" in campi else ("us" if "us" in campi else None)
        if cu is None:
            continue
        ext = layer.extent()
        tol = max(ext.width(), ext.height()) * simplify_fraction if not ext.isEmpty() else 0.0
        per_unita: Dict[str, List[Tuple[float, Drawing]]] = {}
        for f in layer.getFeatures():
            chiave = ((str(f[ca]).strip() if ca and f[ca] is not None else ""), str(f[cu]).strip() if f[cu] is not None else "")
            ids = indice.get(chiave)
            if not ids and chiave[0]:
                ids = indice.get(("", chiave[1]))        # unità senza area nel grafo
            if not ids:
                continue
            g = f.geometry()
            if g is None or g.isEmpty() or QgsWkbTypes.geometryType(g.wkbType()) != QgsWkbTypes.PolygonGeometry:
                continue
            if tol > 0:
                semplice = g.simplify(tol)
                if semplice is not None and not semplice.isEmpty():
                    g = semplice
            poligoni = g.asMultiPolygon() if g.isMultipart() else [g.asPolygon()]
            for poligono in poligoni:
                anelli = [[(float(p.x()), float(p.y())) for p in anello] for anello in poligono if len(anello) >= 3]
                if not anelli:
                    continue
                area = abs(_area(anelli[0]))
                for uid in ids:
                    per_unita.setdefault(uid, []).append((area, Drawing(uid, [list(a) for a in anelli], None)))
        for uid, voci in per_unita.items():
            voci.sort(key=lambda v: -v[0])
            for k, (_a, d) in enumerate(voci):
                if k == 0:
                    d.label = _label_point(d.rings[0])
                out.append(d)
    return out


def _area(anello: Sequence[Tuple[float, float]]) -> float:
    s = 0.0
    n = len(anello)
    for i in range(n):
        x0, y0 = anello[i]; x1, y1 = anello[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return s / 2.0


def _label_point(anello: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    """Un punto dentro il disegno: il centroide dell'anello esterno, che per
    i poligoni delle US (per lo più convessi) cade dentro; per quelli
    concavi QGIS darebbe di meglio, ma qui non serve il layer."""
    try:
        from qgis.core import QgsGeometry, QgsPointXY
        g = QgsGeometry.fromPolygonXY([[QgsPointXY(x, y) for x, y in anello]])
        p = g.pointOnSurface().asPoint()
        return (float(p.x()), float(p.y()))
    except Exception:                               # noqa: BLE001
        n = len(anello)
        return (sum(x for x, _ in anello) / n, sum(y for _, y in anello) / n)


def html_with_map(html: str, graph, conn_str: Optional[str], site: Optional[str],
                  chapters: Sequence[Dict[str, Any]], lang: Optional[str] = None) -> str:
    """L'HTML con la mappa, se il database dà almeno un disegno; altrimenti
    l'HTML com'è."""
    meta = units_meta(graph)
    if not meta or not conn_str:
        return html
    disegni = drawings_from_db(conn_str, site, meta, lang)
    svg, boxes = svg_map(disegni, meta)
    return inject_map(html, svg, boxes, chapters, meta, epoch_names(graph), lang)
