"""Il pannello delle viste nell'HTML della narrativa: la mappa e la scena 3D
dei proxy, a schede, con una selezione sola (Enzo, 17 ottobre 2026).

Prima la mappa (:mod:`em_narrative_map`, 13 ottobre) faceva da sé i link
delle menzioni, i titoli dei capitoli, il pannello e i clic: senza disegni
— TempluMare — niente link. Qui stanno le parti comuni: i link
(:func:`link_units`), il pannello con le schede e la selezione
(:func:`inject_views`), e :func:`html_with_views`, che mette in fila le
viste che il sito ha. Una vista è una :class:`View`: il suo pezzo di
pannello, il suo CSS e i suoi script; si registra con ``PYA_SEL.add(fn)`` e
a ogni selezione riceve ``fn(epoca, unità, gruppo)``: l'epoca e l'unità di
un clic sul testo, o il gruppo delle unità di un capitolo senza epoca.
"""
from __future__ import annotations

import html as _html
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

_LOG = logging.getLogger(__name__)


@dataclass
class View:
    """Una vista del pannello: ``key`` («map», «3d»), il nome della scheda,
    l'HTML dentro il pannello, il suo CSS e i suoi ``<script>``."""
    key: str
    label: str
    panel: str
    css: str = ""
    script: str = ""


_CSS = """
/* pyArchInit: il pannello delle viste della narrativa (mappa, 3D) */
body { max-width: min(96vw, 1500px) !important; }
.pya-layout { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1.5rem; }
.pya-text { max-width: 46rem; }
.pya-map { position: sticky; top: 0; align-self: start; z-index: 5; padding: .4rem 0;
  border-bottom: 1px solid rgba(127,127,127,.35); background: inherit; }
@media (min-width: 900px) {
  .pya-layout { grid-template-columns: minmax(0, 1fr) minmax(300px, 42%); }
  .pya-map { order: 2; border-bottom: 0; }
}
@media (max-width: 899px) {
  .pya-map { order: -1; }
}
.pya-tabs { display: flex; gap: .35rem; margin: 0 0 .4rem; }
.pya-tabs a { padding: .15rem .75rem; border: 1px solid rgba(127,127,127,.45); border-radius: 999px;
  color: inherit; text-decoration: none; font: .85rem -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.pya-tabs a.on { background: rgba(127,127,127,.2); font-weight: 600; }
.pya-view[hidden] { display: none !important; }
.pya-caption { font-size: .85rem; opacity: .85; margin: .35rem 0 0; }
.pya-caption a { margin-left: .5rem; }
a.pya-u { color: inherit; font-style: italic; text-decoration: underline dotted; cursor: pointer; }
"""

_JS = r"""
(function () {
  PYA_SEL.views = []; PYA_SEL.epoch = null; PYA_SEL.unit = null; PYA_SEL.group = null;
  PYA_SEL.select = function (e, u, g) {
    PYA_SEL.epoch = e || null; PYA_SEL.unit = u || null; PYA_SEL.group = (g && g.length) ? g : null;
    PYA_SEL.views.forEach(function (fn) {
      try { fn(PYA_SEL.epoch, PYA_SEL.unit, PYA_SEL.group); }
      catch (err) { if (window.console) { console.warn(err); } }
    });
  };
  PYA_SEL.add = function (fn) {
    PYA_SEL.views.push(fn);
    fn(PYA_SEL.epoch, PYA_SEL.unit, PYA_SEL.group);
  };
  function apri(k) {
    document.querySelectorAll('[data-pya-view]').forEach(function (v) {
      v.hidden = v.getAttribute('data-pya-view') !== k;
    });
    document.querySelectorAll('[data-pya-tab]').forEach(function (t) {
      t.classList.toggle('on', t.getAttribute('data-pya-tab') === k);
    });
    document.dispatchEvent(new CustomEvent('pya:tab', {detail: k}));
  }
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!t || !t.closest) { return; }
    var a = t.closest('a.pya-u');
    if (a) {
      ev.preventDefault();
      var u = a.getAttribute('data-u');
      PYA_SEL.select(a.getAttribute('data-e') || PYA_SEL.firstEpoch[u] || null, u, null);
      var p = document.getElementById('pya-map');
      if (p && p.getBoundingClientRect().top < 0) { p.scrollIntoView({block: 'start'}); }
      return;
    }
    var h = t.closest('h2.pya-cap');
    if (h) {
      var e = h.getAttribute('data-e') || null;
      var g = (h.getAttribute('data-units') || '').split(' ').filter(Boolean);
      if (e || g.length) { PYA_SEL.select(e, null, e ? null : g); }
      return;
    }
    var r = t.closest('.pya-reset');
    if (r) { ev.preventDefault(); PYA_SEL.select(null, null, null); return; }
    var k = t.closest('[data-pya-tab]');
    if (k) { ev.preventDefault(); apri(k.getAttribute('data-pya-tab')); }
  });
})();
"""

_MENTION = re.compile(r'<em class="em-mention">(.*?)</em>', re.S)
_H2 = re.compile(r"<h2>(.*?)</h2>", re.S)


def _resolve(label: str, chapter_units: Sequence[str], meta: Dict[str, Dict[str, Any]]) -> Optional[str]:
    nome = _html.unescape(label).strip()
    nel_capitolo = [u for u in chapter_units if u in meta and meta[u].get("name") == nome]
    if len(nel_capitolo) == 1:
        return nel_capitolo[0]
    ovunque = [u for u, m in meta.items() if m.get("name") == nome]
    return ovunque[0] if len(ovunque) == 1 else None


def _link_mentions(segmento: str, epoca: Optional[str], unita: Sequence[str],
                   meta: Dict[str, Dict[str, Any]]) -> str:
    def sost(m):
        uid = _resolve(m.group(1), unita, meta)
        if uid is None:
            return m.group(0)
        e = epoca or (meta[uid].get("epochs") or [""])[0]
        return ('<a class="em-mention pya-u" href="#pya-map" data-u="%s" data-e="%s">%s</a>'
                % (_html.escape(uid, quote=True), _html.escape(e, quote=True), m.group(1)))
    return _MENTION.sub(sost, segmento)


def link_units(html: str, chapters: Sequence[Dict[str, Any]], meta: Dict[str, Dict[str, Any]]) -> str:
    """Le menzioni risolte diventano link (``data-u`` l'unità, ``data-e``
    l'epoca del capitolo o la prima dell'unità) e i titoli dei capitoli
    portano epoca e unità (``h2.pya-cap``): il k-esimo ``<h2>`` è il
    k-esimo capitolo, controllato sul titolo. Le fonti non si toccano."""
    testa, sep, coda = html.partition('<section class="em-sources">')
    pezzi = _H2.split(testa)                      # [prima, titolo1, corpo1, titolo2, corpo2, ...]
    out = [pezzi[0]]
    k = 0
    for i in range(1, len(pezzi), 2):
        titolo, corpo = pezzi[i], pezzi[i + 1] if i + 1 < len(pezzi) else ""
        cap = chapters[k] if k < len(chapters) else None
        if cap is not None and str(cap.get("title", "")) and _html.escape(str(cap["title"])) != titolo:
            # titolo diverso: cerco il capitolo con quel titolo, altrimenti per ordine
            trovato = next((c for c in chapters if _html.escape(str(c.get("title", ""))) == titolo), None)
            cap = trovato or cap
        if cap is not None:
            epoca = cap.get("epoch") or ""
            unita = list(cap.get("units") or [])
            out.append('<h2 id="pya-cap-%d" class="pya-cap" data-e="%s" data-units="%s">%s</h2>'
                       % (k, _html.escape(str(epoca), quote=True),
                          _html.escape(" ".join(unita), quote=True), titolo))
            out.append(_link_mentions(corpo, epoca or None, unita, meta))
            k += 1
        else:
            out.append("<h2>%s</h2>" % titolo)
            out.append(_link_mentions(corpo, None, [], meta))
    return "".join(out) + sep + coda


def inject_views(html: str, views: Sequence[View], chapters: Sequence[Dict[str, Any]],
                 meta: Dict[str, Dict[str, Any]], lang: Optional[str] = None) -> str:
    """L'HTML della libreria con il pannello delle viste: i link
    (:func:`link_units`), il pannello fisso ``aside#pya-map`` — con le schede
    se le viste sono più d'una, la prima aperta —, il CSS e gli script:
    prima la selezione comune ``PYA_SEL``, poi quelli delle viste, nel loro
    ordine. Senza viste l'HTML torna com'è."""
    from .em_narrative_html import _json_script
    if not views:
        return html
    pagina = link_units(html, chapters, meta)
    sel = {"units": {u: m.get("name", u) for u, m in meta.items()},
           "firstEpoch": {u: (m.get("epochs") or [""])[0] for u, m in meta.items()}}
    schede = ""
    if len(views) > 1:
        schede = '<nav class="pya-tabs">%s</nav>' % "".join(
            '<a href="#pya-map" data-pya-tab="%s"%s>%s</a>'
            % (_html.escape(v.key, quote=True), ' class="on"' if i == 0 else "", _html.escape(v.label))
            for i, v in enumerate(views))
    corpi = "".join('<div class="pya-view" data-pya-view="%s"%s>%s</div>'
                    % (_html.escape(v.key, quote=True), "" if i == 0 else " hidden", v.panel)
                    for i, v in enumerate(views))
    pannello = '<aside class="pya-map" id="pya-map">%s%s</aside>' % (schede, corpi)
    script = ("<script>var PYA_SEL = %s;%s</script>" % (_json_script(sel), _JS)
              + "".join(v.script for v in views))
    pagina = pagina.replace("</style>", _CSS + "".join(v.css for v in views) + "</style>", 1)
    pagina = re.sub(r"<body([^>]*)>",
                    lambda m: '<body%s>\n<div class="pya-layout"><div class="pya-text">' % m.group(1),
                    pagina, count=1)
    return pagina.replace("</body>", "</div>%s</div>%s</body>" % (pannello, script), 1)
