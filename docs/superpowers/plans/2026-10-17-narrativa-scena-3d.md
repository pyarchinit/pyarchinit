# Narrativa: la scena 3D dei proxy — piano di lavoro

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** nell'HTML della narrativa, una scheda «3D» accanto alla mappa con tutti i proxy delle unità messi insieme, e una selezione sola per le due viste (clic sul nome di un'unità, sul titolo di un capitolo, su «tutto il sito», sul proxy nella scena).

**Architecture:** un modulo comune `em_narrative_views` (link delle menzioni e dei capitoli, pannello a schede, selezione `PYA_SEL`, `html_with_views` che mette in fila le viste); la mappa diventa una vista (`em_narrative_map.map_view`); un modulo `em_narrative_3d` (proxy da `s3dgraphy.paradata_view.proxy_instances`, file dal database con `em_project.media_index`/`media_file_for`, vista con three.js dentro la pagina); un pacchetto three.js costruito una volta con esbuild.

**Tech Stack:** Python ≥ 3.9 (QGIS ≥ 3.22), s3dgraphy dev57, SQLAlchemy Core, three.js 0.186.1 (MIT) con GLTFLoader e OrbitControls (esbuild 0.28.2, script classico `window.PYA_THREE`), Chrome senza schermo per la verifica.

**Spec:** `docs/superpowers/specs/2026-10-17-narrativa-scena-3d-design.md`

## Global Constraints

- `$R` = la radice del plugin, `/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit`; i comandi `$PYT` si lanciano da lì.
- Ramo `Stratigraph_00001`; commit con percorsi espliciti; nessuna riga di attribuzione all'AI nei messaggi di commit.
- Mai il database vivo di Enzo; il disco di TempluMare (`/Volumes/Extreme Pro/…`) solo in lettura; le prove sulle copie nello scratchpad (`$SP` = `/private/tmp/claude-501/-Users-enzo-Library-Application-Support-QGIS-QGIS3-profiles-default-python-plugins-pyarchinit/1dcdecdf-1fe5-446b-88a1-f49179369c46/scratchpad`).
- Solo l'HTML; Word e PDF non cambiano.
- La pagina basta a sé stessa: la scena 3D non carica niente dalla rete.
- Numeri del progetto: opacità 0,25 (stesso periodo) e 0,04 (gli altri); contorno `#f5b942`; volo di 600 ms; inquadratura sull'ingombro del proxy allargato tre volte; 15 MB per proxy, 40 MB in tutto.
- Parole in italiano e inglese (`_WORDS`), come la mappa.
- I test della mappa di oggi (`tests/utility/test_em_narrative_map.py`, `tests/sync/test_em_narrative_map_db.py`) passano senza essere cambiati.
- `$PYT` nei passi vuol dire, dalla radice del plugin: `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest -q -p no:warnings -p no:cacheprovider`. Una suite per volta; dopo la suite completa `git checkout -- modules/geoarchaeo/test_layers/villa_ceramica.gpkg`.
- Versione 5.13.132-alpha; tag `narrativa-3d-5.13.132-alpha` solo in locale: si pubblica solo col sì di Enzo.

## Modifica al progetto, con questo piano

Un capitolo senza epoca (TempluMare: i capitoli sono ancorati alle attività VAct.01…): il clic sul suo titolo seleziona come **gruppo** le unità del capitolo (`data-units`). Nel 3D quelle sono piene e le altre a 0,04; la mappa, che lavora per epoca, torna a tutto il sito. La selezione diventa quindi `(epoca, unità, gruppo)`. Il task 3 aggiorna anche il documento di progetto.

## Review Focus

1. Un GLB che il caricatore non legge (compresso con Draco, troncato): la scena carica gli altri e la didascalia conta «non caricati». → Task 8, copia della pagina con un proxy guastato.
2. Un'unità citata il cui proxy manca o è rimasto fuori dai limiti: la didascalia dice «senza proxy 3D» e la scena mostra il periodo. → Task 5 (test su `unit_proxies`) e task 8.
3. La pagina aperta senza rete: la scena funziona. → Task 6, test che lo script della vista non chiede niente alla rete.
4. Un capitolo ancorato a un'attività: il clic sul titolo mostra le sue unità. → Task 3 (test: `data-units` anche senza epoca, il gruppo nello script comune) e task 8.
5. Sul telefono girare la scena non deve far scorrere la pagina. → Task 6, test su `touch-action: none` di `#pya-3d`.

## File

- Modify: `modules/s3dgraphy/em_narrative_html.py` (il CSS di `.pya-u`).
- Modify: `modules/s3dgraphy/em_project.py` (`media_index`, `media_file_for` pubbliche).
- Create: `modules/s3dgraphy/em_narrative_views.py`.
- Modify: `modules/s3dgraphy/em_narrative_map.py` (`map_view`; `inject_map` passa da `inject_views`; lo script si registra in `PYA_SEL`).
- Create: `scripts/three_bundle_entry.js`, `scripts/build_three_bundle.sh`, `resources/js/pya_three_scene.min.js` (costruito), `resources/js/THREE_LICENSE.txt`.
- Create: `modules/s3dgraphy/em_narrative_3d.py`.
- Modify: `modules/s3dgraphy/em_narrative.py` (`export_file`).
- Test: `tests/utility/test_em_narrative_html.py` (+1), `tests/sync/test_em_project.py` (+1), `tests/utility/test_em_narrative_views.py` (nuovo), `tests/utility/test_em_narrative_map.py` (+1), `tests/utility/test_em_narrative_3d.py` (nuovo), `tests/sync/test_em_narrative_3d_db.py` (nuovo).
- Docs: tutorial 36 §10.7 (dieci lingue), `dev_logs/CHANGELOG.md`, `metadata.txt`, il documento di progetto (la modifica qui sopra).

---

### Task 1: il CSS delle righe delle unità non tocca i link delle menzioni

**Files:**
- Modify: `modules/s3dgraphy/em_narrative_html.py` (`_CSS_UNITA`, righe 875–900)
- Test: `tests/utility/test_em_narrative_html.py`

**Interfaces:** nessuna nuova.

- [ ] **Step 1: il test che fallisce** — in fondo a `tests/utility/test_em_narrative_html.py`:

```python
def test_le_righe_delle_unita_non_toccano_i_link_delle_menzioni():
    """Il CSS del blocco «Unità del capitolo» (5.13.130) dava a `.pya-u` un
    bordo e un margine: li prendevano anche i nomi delle unità nel testo,
    che sono link `a.pya-u` della mappa (e dalla 5.13.132 della scena 3D)."""
    assert re.search(r"(?m)^\.pya-u[\s\[{]", nh._CSS_UNITA) is None
    assert ".pya-unita .pya-u { border-bottom" in nh._CSS_UNITA
    assert ".pya-unita .pya-u[open] summary::before" in nh._CSS_UNITA
```

- [ ] **Step 2: vederlo rosso**

Run: `$PYT tests/utility/test_em_narrative_html.py -k righe_delle_unita`
Expected: FAIL (`assert <re.Match …> is None`).

- [ ] **Step 3: la correzione** — in `_CSS_UNITA` le cinque regole su `.pya-u` diventano:

```css
.pya-unita .pya-u { border-bottom: 1px solid rgba(128,128,128,.15); padding: .25rem 0; }
.pya-unita .pya-u summary { cursor: pointer; list-style: none; }
.pya-unita .pya-u summary::-webkit-details-marker { display: none; }
.pya-unita .pya-u summary::before { content: "\\25B8"; display: inline-block; width: 1.1em; color: #888; }
.pya-unita .pya-u[open] summary::before { content: "\\25BE"; }
```

(le righe `.pya-u-sola`, `.pya-u-nome`, … restano: sono altre classi).

- [ ] **Step 4: verde**

Run: `$PYT tests/utility/test_em_narrative_html.py`
Expected: tutti PASS.

- [ ] **Step 5: commit**

```bash
git -C "$R" add -- modules/s3dgraphy/em_narrative_html.py tests/utility/test_em_narrative_html.py
git -C "$R" commit -m "fix(narrativa): il CSS delle righe delle unità del capitolo non dà più bordo e margine ai nomi delle unità nel testo"
```

---

### Task 2: `media_index` e `media_file_for` pubbliche

**Files:**
- Modify: `modules/s3dgraphy/em_project.py` (`_indice_media` → `media_index`, `_sorgente` → `media_file_for`, e le due chiamate in `export_project`)
- Test: `tests/sync/test_em_project.py`

**Interfaces:**
- Produces: `media_index(connection_url: str, resize_base: str = "") -> Dict[str, List[Tuple[str, bool]]]`; `media_file_for(locator: str, index) -> Optional[str]` — comportamento identico alle funzioni private di oggi.

- [ ] **Step 1: il test che fallisce** — in fondo a `tests/sync/test_em_project.py`:

```python
def test_il_file_di_un_locator_dal_database(tmp_path):
    """media_index/media_file_for, pubbliche dalla 5.13.132 (le usa la scena
    3D della narrativa): prima l'originale il cui percorso finisce come il
    locator, poi quello col nome giusto; la copia delle ridotte solo con la
    stessa estensione."""
    import sqlite3
    from modules.s3dgraphy import em_project
    a = tmp_path / "A" / "proxies"
    a.mkdir(parents=True)
    b = tmp_path / "B"
    b.mkdir()
    (a / "SU002.glb").write_bytes(b"glTF-A")
    (b / "SU002.glb").write_bytes(b"glTF-B")
    ridotte = tmp_path / "ridotte"
    ridotte.mkdir()
    (ridotte / "3_D.07.png").write_bytes(b"png")
    (ridotte / "4_colonna.glb").write_bytes(b"glTF-copia")
    db = tmp_path / "m.sqlite"
    con = sqlite3.connect(str(db))
    con.execute("CREATE TABLE media_table (id_media INTEGER, mediatype TEXT, filename TEXT, "
                "filetype TEXT, filepath TEXT)")
    con.execute("CREATE TABLE media_thumb_table (id_media_thumb INTEGER, id_media INTEGER, path_resize TEXT)")
    con.executemany("INSERT INTO media_table VALUES (?,?,?,?,?)", [
        (1, "3d_model", "SU002", "glb", str(b / "SU002.glb")),
        (2, "3d_model", "SU002", "glb", str(a / "SU002.glb")),
        (3, "image", "D.07", "jpg", str(tmp_path / "staccato" / "D.07.jpg")),
        (4, "3d_model", "colonna", "glb", str(tmp_path / "staccato" / "colonna.glb"))])
    con.executemany("INSERT INTO media_thumb_table VALUES (?,?,?)",
                    [(3, 3, "3_D.07.png"), (4, 4, "4_colonna.glb")])
    con.commit()
    con.close()
    indice = em_project.media_index("sqlite:///" + str(db), str(ridotte) + "/")
    assert em_project.media_file_for("proxies/SU002.glb", indice) == str(a / "SU002.glb")
    assert em_project.media_file_for("../RB/colonna.glb", indice) == str(ridotte / "4_colonna.glb")
    assert em_project.media_file_for("DosCo/D.07.jpg", indice) is None        # la copia è un PNG
    assert em_project.media_file_for("proxies/SU099.glb", indice) is None
```

- [ ] **Step 2: rosso** — Run: `$PYT tests/sync/test_em_project.py -k locator_dal_database` → FAIL `AttributeError: … has no attribute 'media_index'`.

- [ ] **Step 3: il cambio di nome** — in `em_project.py`: `def _indice_media(` → `def media_index(`; `def _sorgente(` → `def media_file_for(locator: str, index: Dict[str, List[Tuple[str, bool]]]) -> Optional[str]:` (il corpo usa `index` al posto di `indice`); in `export_project`: `indice = media_index(connection_url, resize_base)` e `sorgente = media_file_for(locator, indice)`. Nessun altro cambiamento.

- [ ] **Step 4: verde** — Run: `$PYT tests/sync/test_em_project.py` → 9 PASS.

- [ ] **Step 5: commit**

```bash
git -C "$R" add -- modules/s3dgraphy/em_project.py tests/sync/test_em_project.py
git -C "$R" commit -m "refactor(em): media_index e media_file_for pubbliche, per la scena 3D della narrativa"
```

---

### Task 3: il pannello delle viste e la selezione comune; la mappa diventa una vista

**Files:**
- Create: `modules/s3dgraphy/em_narrative_views.py`
- Modify: `modules/s3dgraphy/em_narrative_map.py` (togliere `_MENTION`, `_H2`, `_resolve`, `_link_mentions` e il corpo di `inject_map`; `_CSS` e `_JS` della sola mappa; `map_view`; `"tab"` in `_WORDS`)
- Modify: `docs/superpowers/specs/2026-10-17-narrativa-scena-3d-design.md` (decisioni 8 e 9: il gruppo)
- Test: `tests/utility/test_em_narrative_views.py` (nuovo), `tests/utility/test_em_narrative_map.py` (+1)

**Interfaces:**
- Produces: `View(key: str, label: str, panel: str, css: str = "", script: str = "")`; `link_units(html: str, chapters: Sequence[dict], meta: Dict[str, dict]) -> str`; `inject_views(html: str, views: Sequence[View], chapters: Sequence[dict], meta: Dict[str, dict], lang: Optional[str] = None) -> str`; nel browser `PYA_SEL` con `units`, `firstEpoch`, `select(e, u, g)`, `add(fn)` — `fn(epoca|null, unità|null, gruppo: string[]|null)`; l'evento `pya:tab` con `detail` = chiave della scheda aperta. `em_narrative_map.map_view(svg: str, boxes: dict, meta: dict, epoch_names_map: dict, lang=None) -> View`.
- `chapters`: `[{"title": str, "epoch": str|None, "units": [id, …]}]` come oggi (`em_narrative.export_file`).

- [ ] **Step 1: i test che falliscono** — `tests/utility/test_em_narrative_views.py`:

```python
"""Il pannello delle viste della narrativa (17 ottobre 2026): i link delle
menzioni e dei capitoli anche senza mappa, le schede quando le viste sono
due, una selezione sola (PYA_SEL) per la mappa e la scena 3D."""
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

from modules.s3dgraphy import em_narrative_views as nv  # noqa: E402

_PAGINA = ('<html lang="it"><head><meta charset="utf-8"><style>body{}</style></head><body>\n'
           '<h1>Tempio</h1>\n<h2>Virtual Activity 1</h2><p>La fondazione <em class="em-mention">SU002</em> '
           'e <em class="em-mention">SU003</em>.</p>'
           '<h2>II A.D.</h2><p>Poi <em class="em-mention">SU002</em>.</p>'
           '<section class="em-sources"><h2>Fonti</h2><ul></ul></section></body></html>')
_CAPITOLI = [{"title": "Virtual Activity 1", "epoch": None, "units": ["u1", "u2"]},
             {"title": "II A.D.", "epoch": "ep1", "units": ["u1"]}]
_META = {"u1": {"name": "SU002", "epochs": ["ep1"]}, "u2": {"name": "SU003", "epochs": ["ep1"]}}


def _vista(key, label):
    return nv.View(key=key, label=label, panel='<div id="pannello-%s"></div>' % key,
                   css=".v-%s {}" % key, script="<script>/* %s */</script>" % key)


def test_senza_viste_la_pagina_resta_com_e():
    assert nv.inject_views(_PAGINA, [], _CAPITOLI, _META, lang="it") == _PAGINA


def test_con_la_sola_scena_3d_i_nomi_diventano_link():
    fuori = nv.inject_views(_PAGINA, [_vista("3d", "3D")], _CAPITOLI, _META, lang="it")
    assert '<a class="em-mention pya-u" href="#pya-map" data-u="u1" data-e="ep1">SU002</a>' in fuori
    # un capitolo ancorato a un'attività: niente epoca, ma le sue unità
    assert '<h2 id="pya-cap-0" class="pya-cap" data-e="" data-units="u1 u2">Virtual Activity 1</h2>' in fuori
    assert "pya-tabs" not in fuori                                   # una vista sola: niente schede
    assert '<div class="pya-view" data-pya-view="3d"><div id="pannello-3d"></div></div>' in fuori
    assert fuori.count("var PYA_SEL = ") == 1 and "/* 3d */" in fuori and ".v-3d {}" in fuori
    assert '<aside class="pya-map" id="pya-map">' in fuori and "<h2>Fonti</h2>" in fuori


def test_con_due_viste_le_schede_e_la_prima_aperta():
    fuori = nv.inject_views(_PAGINA, [_vista("map", "Mappa"), _vista("3d", "3D")], _CAPITOLI, _META,
                            lang="it")
    assert ('<nav class="pya-tabs"><a href="#pya-map" data-pya-tab="map" class="on">Mappa</a>'
            '<a href="#pya-map" data-pya-tab="3d">3D</a></nav>') in fuori
    assert '<div class="pya-view" data-pya-view="map">' in fuori
    assert '<div class="pya-view" data-pya-view="3d" hidden>' in fuori
    assert fuori.index("var PYA_SEL = ") < fuori.index("/* map */") < fuori.index("/* 3d */")


def test_la_selezione_comune_passa_epoca_unita_e_gruppo():
    js = nv._JS
    assert "PYA_SEL.select = function (e, u, g)" in js and "PYA_SEL.add = function (fn)" in js
    assert "data-units" in js and "'pya:tab'" in js and "closest('a.pya-u')" in js


@pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")
def test_lo_script_comune_si_legge(tmp_path):
    f = tmp_path / "sel.js"
    f.write_text("var PYA_SEL = {units: {}, firstEpoch: {}};" + nv._JS, encoding="utf-8")
    subprocess.run(["node", "--check", str(f)], check=True)
```

e in fondo a `tests/utility/test_em_narrative_map.py`:

```python
def test_la_mappa_si_registra_nella_selezione_comune():
    assert "PYA_SEL.add(" in nm._JS
    assert "addEventListener('click'" not in nm._JS        # i clic li ascolta lo script comune
    vista = nm.map_view('<svg id="pya-svg"></svg>', {"all": [0, 0, 1, 1]},
                        {"u1": {"name": "1.US1", "epochs": []}}, {}, lang="en")
    assert vista.key == "map" and vista.label == "Map" and vista.panel.startswith('<svg id="pya-svg">')
    assert 'id="pya-reset" class="pya-reset"' in vista.panel and "var PYA = " in vista.script
```

- [ ] **Step 2: rossi** — Run: `$PYT tests/utility/test_em_narrative_views.py tests/utility/test_em_narrative_map.py` → `ModuleNotFoundError: … em_narrative_views` e `AttributeError: … map_view`.

- [ ] **Step 3: il modulo comune** — `modules/s3dgraphy/em_narrative_views.py`:

```python
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
```

- [ ] **Step 4: la mappa come vista** — in `modules/s3dgraphy/em_narrative_map.py`:
  - `_WORDS`: aggiungere `"tab": "Mappa"` (it) e `"tab": "Map"` (en).
  - `_CSS` diventa solo quello dell'SVG (le regole di `body`, `.pya-layout`, `.pya-text`, `.pya-map`, `.pya-caption`, `a.pya-u` sono passate in `em_narrative_views._CSS`):

```python
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
```

  - `_JS`: tenere `fit` e `show` come sono; togliere tutto il `document.addEventListener('click', …)` e la riga finale `show(null, null);`, e al loro posto: `  PYA_SEL.add(function (epoch, unit) { show(epoch, unit); });`
  - togliere `_MENTION`, `_H2`, `_resolve`, `_link_mentions` (sono in `em_narrative_views`);
  - `map_view` e `inject_map`:

```python
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
        "firstEpoch": {u: (m.get("epochs") or [""])[0] for u, m in meta.items()},
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
```

  - `import json` resta solo se usato altrove nel modulo; se no si toglie.

- [ ] **Step 5: il documento di progetto** — nella decisione 8 aggiungere: «Un capitolo senza epoca (ancorato a un'attività) seleziona come gruppo le unità del capitolo (`data-units`): la selezione è `(epoca, unità, gruppo)`.»; nella decisione 9, dopo «Un capitolo: …»: «Un capitolo senza epoca: le sue unità piene, le altre a 0,04; inquadratura sul gruppo; la mappa torna a tutto il sito.»

- [ ] **Step 6: verdi** — Run: `$PYT tests/utility/test_em_narrative_views.py tests/utility/test_em_narrative_map.py tests/utility/test_em_narrative_html.py` → tutti PASS (i sei test della mappa di oggi senza cambiare).

- [ ] **Step 7: commit**

```bash
git -C "$R" add -- modules/s3dgraphy/em_narrative_views.py modules/s3dgraphy/em_narrative_map.py tests/utility/test_em_narrative_views.py tests/utility/test_em_narrative_map.py docs/superpowers/specs/2026-10-17-narrativa-scena-3d-design.md
git -C "$R" commit -m "refactor(narrativa): il pannello delle viste e una selezione sola (PYA_SEL); i link delle menzioni anche senza mappa; la mappa è una vista"
```

---

### Task 4: il pacchetto three.js

**Files:**
- Create: `scripts/three_bundle_entry.js`, `scripts/build_three_bundle.sh`
- Create (costruiti): `resources/js/pya_three_scene.min.js`, `resources/js/THREE_LICENSE.txt`
- Test: `tests/utility/test_em_narrative_3d.py` (nuovo, primo test)

**Interfaces:**
- Produces: nel browser `window.PYA_THREE` con `Box3, Color, DirectionalLight, EdgesGeometry, HemisphereLight, LineBasicMaterial, LineSegments, PerspectiveCamera, Raycaster, Scene, SRGBColorSpace, Vector2, Vector3, WebGLRenderer, GLTFLoader, OrbitControls`.

- [ ] **Step 1: il test che fallisce** — `tests/utility/test_em_narrative_3d.py`:

```python
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
```

- [ ] **Step 2: rosso** — Run: `$PYT tests/utility/test_em_narrative_3d.py` → FAIL `FileNotFoundError`.

- [ ] **Step 3: l'ingresso e lo script di costruzione** — `scripts/three_bundle_entry.js`:

```js
// L'ingresso del pacchetto three.js della scena 3D della narrativa
// (scripts/build_three_bundle.sh): solo quello che la scena usa.
import { Box3, Color, DirectionalLight, EdgesGeometry, HemisphereLight, LineBasicMaterial,
         LineSegments, PerspectiveCamera, Raycaster, Scene, SRGBColorSpace, Vector2, Vector3,
         WebGLRenderer } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

window.PYA_THREE = { Box3, Color, DirectionalLight, EdgesGeometry, HemisphereLight,
  LineBasicMaterial, LineSegments, PerspectiveCamera, Raycaster, Scene, SRGBColorSpace,
  Vector2, Vector3, WebGLRenderer, GLTFLoader, OrbitControls };
```

`scripts/build_three_bundle.sh`:

```bash
#!/usr/bin/env bash
# Rifà resources/js/pya_three_scene.min.js: three.js con GLTFLoader e
# OrbitControls in uno script classico (window.PYA_THREE), per la scena 3D
# dell'HTML della narrativa (modules/s3dgraphy/em_narrative_3d.py). Serve
# solo a chi sviluppa: npm ed esbuild in una cartella temporanea.
set -euo pipefail
THREE_VERSION="${THREE_VERSION:-0.186.1}"
ESBUILD_VERSION="${ESBUILD_VERSION:-0.28.2}"
QUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RADICE="$(dirname "$QUI")"
LAVORO="$(mktemp -d)"
trap 'rm -rf "$LAVORO"' EXIT
cp "$QUI/three_bundle_entry.js" "$LAVORO/entry.js"
cd "$LAVORO"
npm init -y >/dev/null
npm install --no-audit --no-fund --silent "three@$THREE_VERSION" "esbuild@$ESBUILD_VERSION"
mkdir -p "$RADICE/resources/js"
npx esbuild entry.js --bundle --minify --format=iife --target=es2020 --legal-comments=none \
  --banner:js="/*! three.js $THREE_VERSION (MIT, https://threejs.org) con GLTFLoader e OrbitControls — pyArchInit, scripts/build_three_bundle.sh */" \
  --outfile="$RADICE/resources/js/pya_three_scene.min.js"
cp node_modules/three/LICENSE "$RADICE/resources/js/THREE_LICENSE.txt"
echo "fatto: $(wc -c < "$RADICE/resources/js/pya_three_scene.min.js") byte"
```

- [ ] **Step 4: costruirlo** — Run: `chmod +x "$R/scripts/build_three_bundle.sh" && bash "$R/scripts/build_three_bundle.sh"` (scarica three ed esbuild da npm; se la rete è lenta, riprovare). Expected: `fatto: <tra 300000 e 1500000> byte`.

- [ ] **Step 5: verde** — Run: `$PYT tests/utility/test_em_narrative_3d.py` → 2 PASS.

- [ ] **Step 6: commit**

```bash
git -C "$R" add -- scripts/three_bundle_entry.js scripts/build_three_bundle.sh resources/js/pya_three_scene.min.js resources/js/THREE_LICENSE.txt tests/utility/test_em_narrative_3d.py
git -C "$R" commit -m "feat(narrativa): three.js 0.186.1 con GLTFLoader e OrbitControls in un solo script, per la scena 3D dentro la pagina"
```

---

### Task 5: i proxy della scena e i loro file

**Files:**
- Create: `modules/s3dgraphy/em_narrative_3d.py` (parte dei dati)
- Test: `tests/utility/test_em_narrative_3d.py`

**Interfaces:**
- Consumes: `em_project.media_index`, `em_project.media_file_for` (task 2); `em_narrative_map.epochs_of(graph) -> Dict[str, List[str]]`; `s3dgraphy.paradata_view.proxy_instances(graph)` → `[{owner, owner_name, beside, files: [id risorsa], removed, …}]`.
- Produces: `MAX_PROXY_FILE = 15 * 1024 * 1024`, `MAX_PROXY_FILES = 40 * 1024 * 1024`, `BUNDLE: str`; `SceneProxy(key, unit, locator, path="", size=0)`; `Scene(proxies, unit_proxies, names, epochs, missing, skipped)`; `scene_proxies(graph) -> Scene`; `build_scene(graph, connection_url: str, resize_base: str = "", *, max_file=MAX_PROXY_FILE, budget=MAX_PROXY_FILES) -> Scene`.

- [ ] **Step 1: i test che falliscono** — in `tests/utility/test_em_narrative_3d.py`, dopo gli import:

```python
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
```

- [ ] **Step 2: rossi** — Run: `$PYT tests/utility/test_em_narrative_3d.py` → i quattro nuovi FAIL con `ModuleNotFoundError: … em_narrative_3d`.

- [ ] **Step 3: la parte dei dati** — `modules/s3dgraphy/em_narrative_3d.py`:

```python
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
```

- [ ] **Step 4: verdi** — Run: `$PYT tests/utility/test_em_narrative_3d.py` → 6 PASS.

- [ ] **Step 5: commit**

```bash
git -C "$R" add -- modules/s3dgraphy/em_narrative_3d.py tests/utility/test_em_narrative_3d.py
git -C "$R" commit -m "feat(narrativa): i proxy della scena 3D dalla regola della libreria, i file dal database, i limiti"
```

---

### Task 6: la vista 3D

**Files:**
- Modify: `modules/s3dgraphy/em_narrative_3d.py` (parole, CSS, JavaScript della scena, `three_bundle`, `scene_view`)
- Test: `tests/utility/test_em_narrative_3d.py`

**Interfaces:**
- Consumes: `View` (task 3); `PYA_SEL.add`, `PYA_SEL.select`, `PYA_SEL.units`, `PYA_SEL.firstEpoch`, l'evento `pya:tab` (task 3); `window.PYA_THREE` (task 4); `Scene` (task 5).
- Produces: `three_bundle() -> str` (il pacchetto, con `</script` reso innocuo; `""` se manca); `scene_view(scene: Scene, epoch_names_map: Dict[str, str], lang: Optional[str] = None) -> Optional[View]` (None senza pacchetto); nella pagina `div#pya-3d`, `p#pya-3d-caption`, `script#pya-3d-data` (JSON: `proxies: [{k, u, glb}]`, `unitProxies`, `names`, `epochs`, `epochNames`, `missing`, `skipped`, `words`).

- [ ] **Step 1: i test che falliscono** — in `tests/utility/test_em_narrative_3d.py`:

```python
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
```

- [ ] **Step 2: rossi** — Run: `$PYT tests/utility/test_em_narrative_3d.py` → i sei nuovi FAIL (`AttributeError: … scene_view` / `_CSS` / `_JS`).

- [ ] **Step 3: la vista** — in `modules/s3dgraphy/em_narrative_3d.py`, in fondo:

```python
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
#pya-3d { position: relative; width: 100%; height: min(62vh, 560px); touch-action: none;
  background: rgba(127,127,127,.07); border-radius: 4px; overflow: hidden; }
@media (max-width: 899px) {
  #pya-3d { height: 34vh; }
}
#pya-3d canvas { display: block; width: 100%; height: 100%; }
.pya-3d-tip { position: absolute; pointer-events: none; padding: .1rem .45rem; border-radius: 3px;
  background: rgba(0,0,0,.75); color: #fff; font: 12px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  transform: translate(-50%, -150%); white-space: nowrap; }
"""

_JS = r"""
(function () {
  var T = window.PYA_THREE;
  var nodo = document.getElementById('pya-3d-data');
  var tela = document.getElementById('pya-3d');
  var cap = document.getElementById('pya-3d-caption');
  if (!nodo || !tela || !window.PYA_SEL) { return; }
  var D = JSON.parse(nodo.textContent), W = D.words;
  var vista = tela.closest('[data-pya-view]');
  var stato = {e: null, u: null, g: null}, S = null;

  function epoche(u) { return D.epochs[u] || []; }
  function nel(u, e) { return epoche(u).indexOf(e) >= 0; }
  function dentro(u) {
    if (stato.e) { return nel(u, stato.e); }
    if (stato.g) { return stato.g.indexOf(u) >= 0; }
    return false;
  }
  function scritta(t) { if (cap && cap.firstChild) { cap.firstChild.textContent = t + ' '; } }
  function didascalia() {
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
  }
  function webgl() {
    try {
      var c = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
    } catch (err) { return false; }
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
    if (S) { return; }
    if (!T || !webgl()) { scritta(W.noWebgl); return; }
    var r = new T.WebGLRenderer({antialias: true, alpha: true});
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.outputColorSpace = T.SRGBColorSpace;
    tela.appendChild(r.domElement);
    var scena = new T.Scene();
    var cam = new T.PerspectiveCamera(40, 1, 0.05, 20000);
    var ctl = new T.OrbitControls(cam, r.domElement);
    ctl.enableDamping = true;
    scena.add(new T.HemisphereLight(0xffffff, 0x666666, 2.2));
    var luce = new T.DirectionalLight(0xffffff, 1.5);
    luce.position.set(1, 2, 1.5);
    scena.add(luce);
    var tip = document.createElement('div');
    tip.className = 'pya-3d-tip';
    tip.hidden = true;
    tela.appendChild(tip);
    S = {r: r, scena: scena, cam: cam, ctl: ctl, tip: tip, items: [], failed: 0, volo: null, gira: false};
    var loader = new T.GLTFLoader(), attesi = D.proxies.length;
    function fatto() { attesi -= 1; if (attesi <= 0) { applica(true); } }
    scritta(W.loading);
    D.proxies.forEach(function (p) {
      var dati;
      try { dati = buffer(p.glb); } catch (err) { S.failed += 1; fatto(); return; }
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
        fatto();
      }, function () { S.failed += 1; fatto(); });
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
  }
  function avvia() {
    if (!S || S.gira) { return; }
    S.gira = true;
    S.r.setAnimationLoop(function (t) {
      if (S.volo) { vola(t); }
      S.ctl.update();
      S.r.render(S.scena, S.cam);
    });
  }
  function ferma() {
    if (S && S.gira) { S.r.setAnimationLoop(null); S.gira = false; }
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
  function forse() { if (!S && vista && !vista.hidden) { crea(); } }
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
            "missing": len(scene.missing), "skipped": len(scene.skipped), "words": parole}
    pannello = ('<div id="pya-3d" class="pya-3d"></div>'
                '<p class="pya-caption" id="pya-3d-caption"><span>%s </span>'
                '<a href="#pya-map" class="pya-reset">%s</a> <small>%s</small></p>'
                % (_html.escape(parole["site"]), _html.escape(parole["reset"]), _html.escape(parole["hint"])))
    script = ("<script>%s</script>" % pacchetto
              + '<script type="application/json" id="pya-3d-data">%s</script>' % _json_script(dati)
              + "<script>%s</script>" % _JS)
    return View(key="3d", label="3D", panel=pannello, css=_CSS, script=script)
```

- [ ] **Step 4: verdi** — Run: `$PYT tests/utility/test_em_narrative_3d.py` → 12 PASS.

- [ ] **Step 5: commit**

```bash
git -C "$R" add -- modules/s3dgraphy/em_narrative_3d.py tests/utility/test_em_narrative_3d.py
git -C "$R" commit -m "feat(narrativa): la vista 3D — i proxy nella pagina, la selezione con trasparenze, contorno e inquadratura, il nome al passaggio, il clic sul proxy"
```

---

### Task 7: l'export della narrativa con le viste

**Files:**
- Modify: `modules/s3dgraphy/em_narrative_views.py` (`html_with_views`)
- Modify: `modules/s3dgraphy/em_narrative.py` (`export_file`, il blocco `if map_conn:` alle righe 1339–1348)
- Test: `tests/sync/test_em_narrative_3d_db.py` (nuovo)

**Interfaces:**
- Consumes: `em_narrative_map.units_meta`, `epoch_names`, `drawings_from_db`, `svg_map`, `map_view`; `em_narrative_3d.build_scene`, `scene_view`.
- Produces: `html_with_views(html: str, graph, conn_str: Optional[str], site: Optional[str], chapters: Sequence[dict], lang: Optional[str] = None, *, resize_base: str = "") -> str`.

- [ ] **Step 1: il test che fallisce** — `tests/sync/test_em_narrative_3d_db.py`:

```python
"""L'HTML della narrativa con la scena 3D dei proxy (17 ottobre 2026): la
scena c'è quando il database ha i file dei proxy, e i nomi delle unità sono
link anche senza la mappa."""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "ext_libs")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.utility.test_em_narrative_3d import _db, _file, _grafo  # noqa: E402


def test_l_html_della_narrativa_porta_la_scena_3d(tmp_path):
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from modules.s3dgraphy import em_narrative as en
    g = _grafo()
    n = NarrativeNode(node_id="narr", name="Tempio")
    n.add_chapter("Virtual Activity 1", canonical=True).add_prose("La fondazione [[u1]] e la [[u3]].")
    n.add_chapter("Fine", canonical=True).add_prose("Niente proxy per [[u2]].")
    g.add_node(n)
    glb = _file(tmp_path / "Tempio" / "EM" / "proxies", "SU002.glb", 64)
    conn = _db(tmp_path, [(1, "3d_model", "SU002", "glb", str(glb))])
    percorso = tmp_path / "n.html"
    en.export_file(g, n, "html", percorso, map_conn=conn, lang="it", media_base=("", ""))
    pagina = percorso.read_text(encoding="utf-8")
    assert 'id="pya-3d-data"' in pagina and pagina.count("var PYA_SEL = ") == 1
    assert '<a class="em-mention pya-u" href="#pya-map" data-u="u1" data-e="ep1">SU002</a>' in pagina
    assert re.search(r'<a class="em-mention pya-u"[^>]*data-u="u2"', pagina)      # senza proxy: è un'unità
    assert "pya-svg" not in pagina and "pya-tabs" not in pagina                  # niente disegni, niente schede
    senza = tmp_path / "senza.html"
    en.export_file(g, n, "html", senza, lang="it")
    assert "pya-3d" not in senza.read_text(encoding="utf-8")                     # niente database, niente scena
```

- [ ] **Step 2: rosso** — Run: `$PYT tests/sync/test_em_narrative_3d_db.py` → FAIL (`'id="pya-3d-data"' in pagina`).

- [ ] **Step 3: `html_with_views`** — in fondo a `modules/s3dgraphy/em_narrative_views.py`:

```python
def html_with_views(html: str, graph, conn_str: Optional[str], site: Optional[str],
                    chapters: Sequence[Dict[str, Any]], lang: Optional[str] = None, *,
                    resize_base: str = "") -> str:
    """L'HTML con le viste che il sito ha: la mappa se il database dà dei
    disegni, la scena 3D se dà i file dei proxy. Ognuna si prova da sola:
    se una non riesce l'altra resta. Senza database, o senza viste, l'HTML
    torna com'è."""
    from . import em_narrative_map as nmap
    if not conn_str:
        return html
    meta = nmap.units_meta(graph)
    nomi_epoche = nmap.epoch_names(graph)
    viste = []
    if meta:
        try:
            svg, boxes = nmap.svg_map(nmap.drawings_from_db(conn_str, site, meta, lang), meta)
            if svg:
                viste.append(nmap.map_view(svg, boxes, meta, nomi_epoche, lang))
        except Exception as e:                      # noqa: BLE001
            _LOG.warning("Mappa della narrativa non aggiunta: %s", e)
    try:
        from . import em_narrative_3d as n3d
        scena = n3d.build_scene(graph, conn_str, resize_base)
        vista = n3d.scene_view(scena, nomi_epoche, lang) if scena.proxies else None
        if vista is not None:
            meta = dict(meta)
            for u, nome in scena.names.items():
                meta.setdefault(u, {"name": nome, "epochs": scena.epochs.get(u, [])})
            viste.append(vista)
    except Exception as e:                          # noqa: BLE001
        _LOG.warning("Scena 3D della narrativa non aggiunta: %s", e)
    return inject_views(html, viste, chapters, meta, lang) if viste else html
```

- [ ] **Step 4: `export_file`** — in `modules/s3dgraphy/em_narrative.py` il blocco `if map_conn:` diventa:

```python
        if map_conn:
            try:
                from . import em_narrative_map as nmap
                from . import em_narrative_views as nviews
                capitoli = [{"title": str(getattr(c, "title", "") or ""),
                             "epoch": nmap.epoch_anchor(graph, c),
                             "units": chapter_unit_ids(c)} for c in narrative.chapters]
                payload = nviews.html_with_views(payload, graph, map_conn, _site_name(graph), capitoli, lang,
                                                 resize_base=str((media_base or ("", ""))[1] or ""))
            except Exception as e:                  # noqa: BLE001
                import logging
                logging.getLogger(__name__).warning("Mappa e scena 3D della narrativa non aggiunte: %s", e)
```

e nel docstring di `export_file`, dopo la frase sulla mappa: «Con i file dei proxy nel database l'HTML porta anche la **scena 3D** (:mod:`em_narrative_3d`), nella stessa scheda della mappa (:mod:`em_narrative_views`).»

- [ ] **Step 5: verdi** — Run: `$PYT tests/sync/test_em_narrative_3d_db.py tests/sync/test_em_narrative_map_db.py tests/utility/test_em_narrative_map.py tests/utility/test_em_narrative_views.py tests/utility/test_em_narrative_html.py` → tutti PASS.

- [ ] **Step 6: commit**

```bash
git -C "$R" add -- modules/s3dgraphy/em_narrative_views.py modules/s3dgraphy/em_narrative.py tests/sync/test_em_narrative_3d_db.py
git -C "$R" commit -m "feat(narrativa): l'export HTML mette insieme mappa e scena 3D nel pannello, ognuna se il sito ce l'ha"
```

---

### Task 8: la prova nel browser su TempluMare

**Files:** niente nel plugin (tutto nello scratchpad `$SP/scena3d/`); se la prova trova un difetto del JavaScript si corregge in `em_narrative_3d.py` / `em_narrative_views.py` con un test e un commit.

- [ ] **Step 1: l'HTML vero** — copiare il database e l'em.json della prova del menu: `mkdir -p "$SP/scena3d" && cp "$SP/menu_prova/templu.sqlite" "$SP/scena3d/" && cp "$SP/menu_prova/home/pyarchinit_EM_folder/Temple.em.json" "$SP/scena3d/"`; poi `$SP/scena3d/esporta.py`:

```python
import os, sys
PLUGIN, SP = sys.argv[1], sys.argv[2]
sys.path[:0] = [os.path.join(PLUGIN, "ext_libs"), PLUGIN]
from qgis.core import QgsApplication
app = QgsApplication([], False); app.initQgis()
from modules.s3dgraphy import em_narrative as en
cartella = os.path.join(SP, "scena3d")
conn = "sqlite:///" + os.path.join(cartella, "templu.sqlite")
basi = (os.path.join(SP, "reale", "thumb") + "/", os.path.join(SP, "reale", "resize") + "/")
c, _ = en.load_project(os.path.join(cartella, "Temple.em.json"))
g = c.active(); n = en.narrative_of(g)
figure = en.figures_for(g, n, conn, *basi)
en.export_file(g, n, "html", os.path.join(cartella, "templu.html"), figures=figure, map_conn=conn,
               lang="it", media_base=basi)
print("ok", os.path.getsize(os.path.join(cartella, "templu.html")))
sys.stdout.flush(); os._exit(0)
```

Run (dalla radice del plugin): `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME="$SP/menu_prova/home" PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS /Applications/QGIS.app/Contents/MacOS/bin/python3 "$SP/scena3d/esporta.py" "$R" "$SP"` → `ok <byte>`; la pagina ha `id="pya-3d-data"` con 65 proxy (`grep -o '"k":' | wc -l`).

- [ ] **Step 2: le copie di prova** — `$SP/scena3d/copie.py` scrive tre copie della pagina: `riposo.html` (com'è), `unita.html` (dopo 3 secondi clicca la prima menzione la cui unità ha un proxy), `capitolo.html` (clicca il primo titolo con `data-units` non vuoto), `guasto.html` (il GLB del primo proxy sostituito da `"AAAA"`):

```python
import json, re, sys
d = sys.argv[1]
pagina = open(d + "/templu.html", encoding="utf-8").read()
def con(script):
    return pagina.replace("</body>", "<script>setTimeout(function(){%s}, 3000);</script></body>" % script, 1)
open(d + "/riposo.html", "w", encoding="utf-8").write(pagina)
open(d + "/unita.html", "w", encoding="utf-8").write(con(
    "var D=JSON.parse(document.getElementById('pya-3d-data').textContent);"
    "var a=Array.prototype.find.call(document.querySelectorAll('a.pya-u'),function(x){"
    "return (D.unitProxies[x.getAttribute('data-u')]||[]).length;}); if(a){a.click();}"))
open(d + "/capitolo.html", "w", encoding="utf-8").write(con(
    "var h=Array.prototype.find.call(document.querySelectorAll('h2.pya-cap'),function(x){"
    "return x.getAttribute('data-units');}); if(h){h.click();}"))
m = re.search(r'(<script type="application/json" id="pya-3d-data">)(.*?)(</script>)', pagina, re.S)
dati = json.loads(m.group(2)); dati["proxies"][0]["glb"] = "AAAA"
open(d + "/guasto.html", "w", encoding="utf-8").write(
    pagina[:m.start(2)] + json.dumps(dati, ensure_ascii=False).replace("</", "<\\/") + pagina[m.end(2):])
```

Run: `python3 "$SP/scena3d/copie.py" "$SP/scena3d"`.

- [ ] **Step 3: le schermate** — per ognuna delle quattro copie (e `riposo.html` anche a 390×844, il telefono):

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars --user-data-dir="$SP/scena3d/chrome" --window-size=1400,1000 --virtual-time-budget=9000 --screenshot="$SP/scena3d/unita.png" "file://$SP/scena3d/unita.html"
```

Expected, guardando i PNG: a riposo i proxy nei colori EM e «Tutto il sito · 65 proxy»; dopo il clic sull'unità il suo proxy pieno con il contorno arancione, gli altri trasparenti, e la didascalia col suo nome; dopo il capitolo le sue unità piene e «Le unità del capitolo · N proxy»; nella copia guasta la scena con 64 proxy e «1 non caricati»; sul telefono il pannello in alto. Se la scena è nera o vuota: provare `--use-gl=angle`; se resta nera, aprire la pagina in Chrome normale e leggere la console.

- [ ] **Step 4: correggere quello che non va** — ogni correzione con un test (Python) che la fissa, poi rifare i passi 1–3; commit con i percorsi dei file corretti.

- [ ] **Step 5: la pagina per Enzo** — `cp "$SP/scena3d/templu.html" ~/Downloads/TempluMare_narrativa_scena3D.html`.

---

### Task 9: tutorial, changelog, versione, suite

**Files:**
- Modify: `docs/tutorials/{it,en}/36_extended_matrix_s3dgraphy.md` (riga 12, il tag; §10.7, dopo il punto «la mappa del sito»), poi le altre otto lingue (`ar ca de el es fr pt ro`) con un traduttore in background, come per la 5.13.131
- Modify: `dev_logs/CHANGELOG.md` (voce in cima), `metadata.txt` (`version=5.13.132-alpha`)

- [ ] **Step 1: il tutorial in italiano** — tag `narrativa-3d-5.13.132-alpha`; in §10.7, dopo il punto della mappa:

```markdown
- **la scena 3D dei proxy** (dalla 5.13.132-alpha, solo nell'HTML), nel pannello fisso della mappa: con i disegni e i proxy, le schede **Mappa** e **3D**; con i soli proxy — TempluMare — il pannello ha solo il 3D. I proxy sono quelli delle unità, come li disegna EMStudio (unità → proprietà «geometry» → forma → `proxies/<unità>.glb`), presi dal database come gli altri media; ognuno porta la sua posizione nella scena, e messi insieme si incastrano. A riposo hanno i colori dei loro materiali, la codifica EM. Un clic sul nome di un'unità nel testo — ora un link anche senza la mappa — mette in evidenza il suo proxy, pieno e con il contorno arancione, rende trasparenti quelli dello stesso periodo e quasi invisibili gli altri, e lo inquadra; un clic sul titolo di un capitolo mostra pieni i proxy del suo periodo o, per un capitolo ancorato a un'attività, quelli delle sue unità; «tutto il sito» torna a tutto. Si gira con il mouse o con un dito e si ingrandisce con la rotella o con due dita; passando sopra un proxy se ne legge il nome, cliccandolo si seleziona la sua unità, anche sulla mappa. La didascalia dice il periodo, quanti proxy e l'unità («senza proxy 3D» quando non ne ha). three.js è dentro la pagina: la scena funziona anche senza rete. Un proxy entra fino a 15 MB, 40 MB in tutto; quelli rimasti fuori si contano. Su TempluMare: 65 proxy, 2,4 MB;
```

- [ ] **Step 2: in inglese** — tag `narrativa-3d-5.13.132-alpha` e, nello stesso punto di §10.7 di `docs/tutorials/en/36_extended_matrix_s3dgraphy.md`:

```markdown
- **the 3D scene of the proxies** (from 5.13.132-alpha, HTML only), in the map's fixed panel: with drawings and proxies, the **Mappa** (Map) and **3D** tabs; with proxies only — TempluMare — the panel has only the 3D. The proxies are those of the units, as EMStudio draws them (unit → «geometry» property → shape → `proxies/<unit>.glb`), taken from the database like the other media; each one carries its own position in the scene, and put together they fit. At rest they have the colours of their materials, the EM colour code. A click on a unit's name in the text — now a link even without the map — highlights its proxy, full and with an orange outline, makes those of the same period transparent and the others almost invisible, and frames it; a click on a chapter title shows the proxies of its period full or, for a chapter anchored to an activity, those of its units; «tutto il sito» (whole site) goes back to everything. You turn the scene with the mouse or a finger and zoom with the wheel or two fingers; hovering a proxy shows its name, clicking it selects its unit, on the map too. The caption gives the period, how many proxies and the unit («senza proxy 3D», no 3D proxy, when it has none). three.js is inside the page: the scene works without a network. A proxy goes into the page up to 15 MB, 40 MB in all; those left out are counted. On TempluMare: 65 proxies, 2.4 MB;
```

Poi il traduttore per le otto lingue, in background, con le regole della 5.13.131: tradurre dall'inglese controllando l'italiano, i nomi italiani dell'interfaccia restano in italiano con la glossa come ogni file già fa, il vocabolario e la punteggiatura di ogni file, solo i due punti (tag e §10.7).

- [ ] **Step 3: changelog e versione** — in cima a `dev_logs/CHANGELOG.md` (dopo l'intestazione e il primo `---`), con al posto di `N` e `M` i numeri misurati al passo 4:

```markdown
## [feat] - 2026-10-17 — La scena 3D dei proxy nella narrativa: tutti i proxy delle unità messi insieme nel pannello della mappa, il clic su un'unità che evidenzia il suo e rende trasparenti gli altri — 5.13.132-alpha

> Branch `Stratigraph_00001`. Suite **N verdi** (0 falliti, 0 errori; +M test). / The narrative's HTML gets a 3D tab next to the map with all the units' proxies; one selection drives both views.

#### Added / Aggiunto
- 🇮🇹 **IT**: **«assemblare insieme tutti i 3D come ad esempio per la mappa e quando nel capitolo si fa riferimento a quello se ci clicco sopra … si evidenzia il proxy interessato e gli altri sono in trasparenza»** (Enzo, 17 ottobre 2026). Nuovi moduli `modules/s3dgraphy/em_narrative_views.py` (`View`, `link_units`, `inject_views`, `html_with_views`: il pannello a schede «Mappa» e «3D», i link delle menzioni anche senza mappa, la selezione comune `PYA_SEL` con epoca, unità e gruppo — il gruppo è un capitolo senza epoca) e `modules/s3dgraphy/em_narrative_3d.py` (`scene_proxies` dalla regola della libreria `proxy_instances`, chi eredita la geometria punta al proxy del proprietario; `build_scene` con i file dal database e i limiti di 15/40 MB; `scene_view` con i proxy in base64 e la scena three.js: colori EM a riposo, il proxy scelto pieno col contorno arancione, lo stesso periodo a 0,25 e gli altri a 0,04, l'inquadratura in 0,6 s, il nome al passaggio, il clic sul proxy che seleziona l'unità anche sulla mappa). three.js 0.186.1 (MIT) con GLTFLoader e OrbitControls in `resources/js/pya_three_scene.min.js`, rifatto da `scripts/build_three_bundle.sh`: la pagina funziona senza rete. `em_narrative_map.map_view`; `em_project.media_index`/`media_file_for` pubbliche. Su TempluMare: 65 proxy, 2,4 MB, la scena di 43 × 14 × 52 m.
- 🇬🇧 **EN**: new `em_narrative_views` (tabbed panel, mention links without the map, shared `PYA_SEL` selection) and `em_narrative_3d` (proxies from the library's `proxy_instances`, files from the database, three.js scene embedded in the page with transparency, outline, framing, hover names and click-to-select).

#### Fixed / Corretto
- 🇮🇹 **IT**: il CSS del blocco «Unità del capitolo» (5.13.130) su `.pya-u` dava bordo e margine anche ai nomi delle unità nel testo (`a.pya-u`): ora vale solo dentro `.pya-unita`.
- 🇬🇧 **EN**: the 5.13.130 unit-row CSS no longer styles the mention links.

#### Test / Verifica
- 🇮🇹 **IT**: `tests/utility/test_em_narrative_views.py`, `tests/utility/test_em_narrative_3d.py`, `tests/sync/test_em_narrative_3d_db.py`, +1 in `test_em_narrative_map.py`, `test_em_narrative_html.py` e `test_em_project.py`; gli script controllati con `node --check`. Prova nel browser (Chrome senza schermo) su TempluMare: a riposo, dopo il clic su un'unità, dopo il clic su un capitolo, con un proxy guastato, sul telefono.
- 🇬🇧 **EN**: M new tests; headless Chrome check on TempluMare.

#### Documentation / Documentazione
- 🇮🇹 **IT**: tutorial 36 §10.7 (la scena 3D dei proxy), dieci lingue. `metadata.txt` 5.13.132-alpha.
- 🇬🇧 **EN**: tutorial 36 §10.7 in ten languages.

---
```

e `metadata.txt` → `version=5.13.132-alpha`.

- [ ] **Step 4: la suite completa** — Run: `$PYT tests/sync tests/utility tests/migrations --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py` → tutti verdi; poi `git -C "$R" checkout -- modules/geoarchaeo/test_layers/villa_ceramica.gpkg`.

- [ ] **Step 5: commit e tag locale**

```bash
git -C "$R" add -- docs/tutorials/it/36_extended_matrix_s3dgraphy.md docs/tutorials/en/36_extended_matrix_s3dgraphy.md dev_logs/CHANGELOG.md metadata.txt
git -C "$R" commit -m "docs: la scena 3D dei proxy nella narrativa — tutorial 36 §10.7, changelog (5.13.132-alpha)"
# dopo il traduttore:
git -C "$R" add -- docs/tutorials/{ar,ca,de,el,es,fr,pt,ro}/36_extended_matrix_s3dgraphy.md
git -C "$R" commit -m "docs(tutorial): 36 §10.7 — la scena 3D dei proxy, in ar ca de el es fr pt ro (5.13.132-alpha)"
git -C "$R" tag -a narrativa-3d-5.13.132-alpha -m "feat(narrativa): la scena 3D dei proxy nel pannello della mappa, una selezione sola per le due viste, three.js dentro la pagina (5.13.132-alpha)"
```

Pubblicare (ramo, tag, documentazione API) solo dopo il sì di Enzo.
