# Il pannello che disegna la matrice dall'em.json — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vedere la matrice dell'Extended Matrix dentro QGIS, con le sue fasce di epoca e la simbologia giusta, senza EMStudio, senza nodo e senza login.

**Architecture:** Tre strati, e i primi due non sanno cosa sia Qt. (1) Un **modello** letto dall'em.json: unità, rapporti, epoche, con forma e colori risolti dalle regole visive della libreria. (2) Un **impaginatore** puro che mette ogni unità nella fascia della sua epoca e la incolonna secondo la stratigrafia, restituendo coordinate. (3) Una **vista** Qt (`QGraphicsView`) che disegna quelle coordinate, con zoom, selezione e salvataggio; e un writer SVG, che è la stessa cosa senza Qt e serve sia all'utente sia ai test.

Si parte dall'**em.json**, non dal grafo in memoria: così quello che si vede nel pannello è esattamente quello che viaggia nel file e che aprirebbe EMStudio. La voce di menu esporta in una cartella temporanea e legge quella.

**Tech Stack:** Python 3.9 (QGIS), PyQt5 (`QtWidgets`, `QtGui`; **niente** QtWebEngine né QtSvg per disegnare), s3dgraphy 1.6.0.dev40 (solo le regole visive, lette come dato), pytest.

**Spec:** nasce da una richiesta diretta di Enzo (2026-10-08): «fai il pannello che disegna la matrice dall'em.json», dopo aver constatato che la pagina per-stanza del nodo chiede di accedere e quindi non fa da visualizzatore.

## Ricognizione (misurata il 2026-10-08)

- `ext_libs/s3dgraphy/JSON_config/em_visual_rules.json` → `node_styles.<tipo>.style` dà **forma, riempimento, colore e stile del bordo** per 44 tipi. I nostri: `US` rectangle `#F0F0F0`/`#9B3333`, `USVs` parallelogram `#000000`/`#248FE7`, `USVn` hexagon `#000000`/`#31792D`, `SF` octagon `#CCCCCC`/`#D8BD30`, `BR` diamond nero, `USD` rounded_rectangle, `TSU` rectangle dotted, `serSU` ellipse. I paradati stanno sotto sigle diverse dai nostri `node_type`: `DOC` (ellipse), `EXT` (pentagon), `COMB` (hexagon dashed), `PROP` (circle) — serve una tabella di alias.
- L'em.json del sito di esempio: 76 nodi, 377 archi, 12 `EpochNode` con `data.start_time`/`end_time`/`color`, 45 unità ciascuna con un `has_first_epoch`.
- `dot` di Graphviz c'è su questo Mac (`/opt/homebrew/bin/dot`) ma **non lo usiamo**: il pannello deve funzionare su una installazione pulita, e l'impaginazione è vincolata dalle fasce, che non è il mestiere di `dot`.
- `PyQt5.QtSvg` è presente, ma non serve: si disegna con `QGraphicsScene` e si salva l'SVG scrivendolo noi (lo stesso writer che i test leggono).

## Global Constraints

- **Niente righe di attribuzione AI** in commit, issue, PR, commenti.
- **Solo ramo dev `Stratigraph_00001`.**
- **Confine GPL**: nessun codice EMStudio o del nodo dentro il plugin. Le regole visive sono un file di dati della libreria già vendorizzata, letto come dato.
- **Mai istanziare un widget Qt nei test**: il modello, l'impaginatore e il writer SVG sono puri e si provano headless; la vista e il pannello si difendono con prove sul sorgente, come `room_panel`.
- **Niente dipendenza da `dot`, matplotlib o rete.**
- Comando di test canonico: quello degli altri piani di oggi.

## Review Focus

1. **Un grafo con un ciclo.** I rapporti di uno scavo reale possono contenerne (la verifica rapporti li segnala): l'incolonnamento per livelli deve finire comunque, non girare all'infinito né perdere nodi.
2. **Unità senza epoca.** Un'unità senza `has_first_epoch` non deve sparire dal disegno: va in una fascia propria, dichiarata.
3. **Un sito grande.** 1311 US (il DB Ventena) non devono bloccare la GUI né produrre una scena di dimensioni assurde: l'impaginazione è un passo solo, e il disegno va fatto a blocchi o rinviato.
4. **Tipi che le regole visive non conoscono.** Un `node_type` assente da `em_visual_rules.json` (o un file delle regole mancante) non deve far cadere il pannello: rettangolo neutro e avanti.
5. **Nomi lunghi.** `1.Combinar900` e `Generico XIII secolo - Primi del XIV secolo` non devono sbordare dalla casella né dalla fascia.

---

### Task 1: Il modello letto dall'em.json

**Files:**
- Create: `modules/utility/em_matrix_model.py`
- Test: `tests/utility/test_em_matrix_model.py`

**Interfaces:**
- Produces:
  - `Unit(node_id, name, label, node_type, epoch_id, data)` — `label` è il nome corto mostrato
  - `Epoch(node_id, name, start, end, color)`
  - `Relation(source, target, kind)`
  - `MatrixModel(units, epochs, relations, warnings)`
  - `read_em_json(path_or_dict) -> MatrixModel`
  - `style_for(node_type) -> Style(shape, fill, stroke, dash, width)`

- [ ] **Step 1: Write the failing test**

```python
def test_the_model_reads_units_epochs_and_relations():
    model = read_em_json(_SAMPLE)          # l'em.json del sito di esempio
    assert len(model.units) == 45
    assert len(model.epochs) == 12
    assert {r.kind for r in model.relations} >= {"overlies", "cuts", "fills"}
    unita = {u.label: u for u in model.units}
    assert unita["1.US9"].epoch_id == unita["1.US3"].epoch_id   # stessa epoca


def test_the_epochs_come_out_newest_first():
    model = read_em_json(_SAMPLE)
    anni = [e.start for e in model.epochs]
    assert anni == sorted(anni, reverse=True), anni
    assert model.epochs[0].name == "Età contemporanea"


def test_a_unit_without_an_epoch_is_kept():
    model = read_em_json({"graphs": {"S": {"nodes": [
        {"id": "u1", "name": "1.US1", "node_type": "US", "data": {"us": "1"}}],
        "edges": []}}})
    assert len(model.units) == 1
    assert model.units[0].epoch_id is None


def test_the_symbology_is_the_extended_matrix_one():
    assert style_for("US").shape == "rectangle"
    assert style_for("US").stroke == "#9B3333"
    assert style_for("USVs").shape == "parallelogram"
    assert style_for("USVn").shape == "hexagon"
    assert style_for("SF").shape == "octagon"
    assert style_for("BR").shape == "diamond"
    # i paradati stanno sotto sigle diverse dai nostri node_type
    assert style_for("document").shape == "ellipse"
    assert style_for("extractor").shape == "pentagon"
    assert style_for("combiner").shape == "hexagon"
    assert style_for("property").shape == "circle"


def test_an_unknown_type_still_gets_a_shape():
    s = style_for("QUALCOSA")
    assert s.shape == "rectangle" and s.fill and s.stroke
```

- [ ] **Step 2: Run test to verify it fails**

Run: `… -m pytest tests/utility/test_em_matrix_model.py -q`
Expected: FAIL — `ModuleNotFoundError: modules.utility.em_matrix_model`.

- [ ] **Step 3: Write minimal implementation**

Dataclass semplici + lettura. Le regole visive si leggono una volta sola:

```python
#: I nostri node_type contro le sigle di em_visual_rules.json.
_STYLE_ALIASES = {"document": "DOC", "extractor": "EXT",
                  "combiner": "COMB", "property": "PROP",
                  "EpochNode": "EP", "author": "AUTH"}

#: Quando il tipo non è in tabella: un rettangolo neutro, mai un'eccezione.
_FALLBACK = Style(shape="rectangle", fill="#FFFFFF", stroke="#8C8C8C",
                  dash="solid", width=2.0)
```

e `read_em_json` che prende il grafo attivo (`active_graph_id`, altrimenti il primo), separa i nodi per `node_type` (`EpochNode` → epoche; i tipi stratigrafici e paradati → unità), legge `has_first_epoch` per l'epoca di ciascuna e tiene come relazioni solo i tipi stratigrafici (`STRATIGRAPHIC_KINDS`), scartando `has_property`/`has_documentation`/`is_in_location`/`has_author`/`has_first_epoch`/`survive_in_epoch`.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/em_matrix_model.py tests/utility/test_em_matrix_model.py
git commit -m "feat(matrice): il modello della matrice letto dall'em.json"
```

---

### Task 2: L'impaginatore (puro)

**Files:**
- Create: `modules/utility/em_matrix_layout.py`
- Test: `tests/utility/test_em_matrix_layout.py`

**Interfaces:**
- Consumes: `MatrixModel` del Task 1.
- Produces: `Box(unit, x, y, w, h)`, `Band(epoch, y, h, color, label)`, `Edge(points, kind)`, `Layout(bands, boxes, edges, width, height)`, `layout(model, config=LayoutConfig()) -> Layout`.

- [ ] **Step 1: Write the failing test**

```python
def test_each_unit_sits_in_the_band_of_its_epoch():
    lay = layout(read_em_json(_SAMPLE))
    per_id = {b.unit.node_id: b for b in lay.boxes}
    for band in lay.bands:
        for box in lay.boxes:
            if box.unit.epoch_id == band.epoch.node_id:
                assert band.y <= box.y and box.y + box.h <= band.y + band.h


def test_what_overlies_is_drawn_above():
    """La stratigrafia si legge dall'alto: chi copre sta sopra chi è coperto."""
    model = _two_units_one_over_the_other()
    lay = layout(model)
    sopra = next(b for b in lay.boxes if b.unit.label == "1.US1")
    sotto = next(b for b in lay.boxes if b.unit.label == "1.US2")
    assert sopra.y < sotto.y


def test_a_cycle_does_not_hang_and_loses_nothing():
    """Uno scavo reale può avere un ciclo nei rapporti (la verifica li
    segnala): l'incolonnamento deve finire comunque."""
    model = _cycle_of_three()
    lay = layout(model)
    assert len(lay.boxes) == 3


def test_units_without_an_epoch_get_their_own_band():
    model = _one_unit_without_epoch()
    lay = layout(model)
    assert lay.bands[-1].label.startswith("Senza epoca")
    assert len(lay.boxes) == 1


def test_a_big_site_lays_out_once_and_quickly():
    model = _synthetic(1311)
    import time
    t = time.time()
    lay = layout(model)
    assert len(lay.boxes) == 1311
    assert time.time() - t < 5.0
```

- [ ] **Step 2: Run test to verify it fails** — Expected: FAIL, modulo assente.

- [ ] **Step 3: Write minimal implementation**

```python
def _ranks_within(unit_ids, relations):
    """Livello di ogni unità dentro la sua fascia: 0 = nessuno la copre.

    Percorso più lungo calcolato a onde (Kahn), con il taglio dei cicli:
    quando nessun nodo ha più grado d'ingresso zero e ne restano, si
    prende quello con meno archi entranti e lo si promuove. Uno scavo
    reale un ciclo ce l'ha (la verifica rapporti lo segnala): il disegno
    non è il posto per rifiutarlo.
    """
```

più l'ordinamento baricentrico (due passate su e giù) per ridurre gli incroci, la geometria delle fasce (altezza = righe × passo) e gli archi come spezzate a tre segmenti.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(matrice): l'impaginatore — ogni unità nella fascia della sua epoca"
```

---

### Task 3: Il disegno in SVG (puro, e salvabile)

**Files:**
- Create: `modules/utility/em_matrix_svg.py`
- Test: `tests/utility/test_em_matrix_svg.py`

**Interfaces:**
- Produces: `to_svg(layout, title="") -> str`, `write_svg(layout, path, title="")`.

- [ ] **Step 1: Write the failing test**

```python
def test_the_svg_has_a_band_and_a_box_for_everything():
    lay = layout(read_em_json(_SAMPLE))
    svg = to_svg(lay, title="Scavo archeologico")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert svg.count("<g class=\"unit\"") == len(lay.boxes)
    assert svg.count("<g class=\"band\"") == len(lay.bands)
    assert "Età contemporanea" in svg and "Scavo archeologico" in svg


def test_each_shape_is_drawn_as_the_rules_say():
    lay = layout(read_em_json(_SAMPLE))
    svg = to_svg(lay)
    assert "<polygon" in svg          # parallelogrammi, esagoni, ottagoni
    assert "<ellipse" in svg or "<circle" in svg
    assert "#9B3333" in svg           # il bordo della US


def test_a_name_too_long_is_shortened_not_spilled():
    lay = layout(_model_with_label("1.Combinar900000000000"))
    svg = to_svg(lay)
    assert "1.Combinar900000000000" not in svg
    assert "…" in svg


def test_the_svg_escapes_what_must_be_escaped():
    lay = layout(_model_with_label('US <1> & "2"'))
    svg = to_svg(lay)
    assert "&lt;1&gt;" in svg and "&amp;" in svg
```

- [ ] **Step 2: Run test to verify it fails** — Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Un writer senza dipendenze: `<rect>` per le fasce (colore dell'epoca), un `<g class="unit">` per unità con la forma giusta (`rect`/`polygon`/`ellipse`/`circle`/`path`), `<polyline>` per gli archi, `<text>` per le etichette, tutto con `_esc()`.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Guardare il risultato con gli occhi**

```bash
… -c "from modules.utility.em_matrix_model import read_em_json; \
      from modules.utility.em_matrix_layout import layout; \
      from modules.utility.em_matrix_svg import write_svg; \
      write_svg(layout(read_em_json('<em.json del demo>')), '$SCRATCHPAD/matrice.svg', 'Scavo archeologico')"
```
Expected: un SVG apribile, con le fasce delle dodici epoche e le unità dentro la propria.

- [ ] **Step 6: Commit**

```bash
git commit -am "feat(matrice): il disegno in SVG, senza dipendenze"
```

---

### Task 4: La vista Qt

**Files:**
- Create: `modules/utility/em_matrix_view.py`
- Test: `tests/utility/test_em_matrix_view.py` (prove sul sorgente, nessun widget istanziato)

**Interfaces:**
- Produces: `build_scene(layout, scene) -> dict[str, QGraphicsItem]`, `MatrixView(QGraphicsView)` con `fit()`, `zoom(f)`, `selected` (segnale col node_id), `save_svg(path)`, `save_png(path)`.

- [ ] **Step 1: Write the failing test**

```python
def test_the_view_does_not_need_a_web_engine():
    src = Path(VIEW).read_text()
    assert "QtWebEngine" not in src and "QtWebKit" not in src


def test_the_view_draws_from_the_layout_not_from_the_file():
    """La vista non rilegge l'em.json: prende quello che l'impaginatore
    ha deciso, così quello che si vede è provato dai test puri."""
    src = Path(VIEW).read_text()
    assert "read_em_json" not in src


def test_saving_the_svg_goes_through_the_pure_writer():
    src = Path(VIEW).read_text()
    assert "em_matrix_svg" in src
```

- [ ] **Step 2: Run test to verify it fails** — Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

`build_scene` traduce ogni `Band`/`Box`/`Edge` in `QGraphicsRectItem` / `QGraphicsPolygonItem` / `QGraphicsEllipseItem` / `QGraphicsPathItem`, mette `node_id` nel `data(0)` dell'item e il testo dell'unità nel tooltip. `MatrixView` fa rotellina = zoom, doppio clic = adatta, clic = emette `selected`. Il salvataggio SVG passa dal writer puro; il PNG da `QImage` + `scene.render`.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git commit -am "feat(matrice): la vista Qt, senza motori web"
```

---

### Task 5: Il pannello e la voce di menu

**Files:**
- Create: `modules/s3dgraphy/em_matrix_panel.py`
- Modify: `pyarchinitPlugin.py`, `modules/s3dgraphy/s3dgraphy_dot_bridge.py`
- Test: `tests/sync/test_em_matrix_panel.py`

**Interfaces:**
- Produces: `open_matrix_panel(iface, em_json_path, title) -> bool`, `close_panel(iface)`, `PANEL_OBJECT_NAME`.

- [ ] **Step 1: Write the failing test**

```python
def test_one_panel_per_session_and_it_closes_with_the_plugin():
    src = Path(PANEL).read_text()
    assert "PANEL_OBJECT_NAME" in src and "findChild" in src
    plugin = Path(PLUGIN).read_text()
    assert "em_matrix_panel.close_panel" in plugin


def test_the_menu_entry_exists_and_is_removed_on_unload():
    plugin = Path(PLUGIN).read_text()
    assert "actionEmMatrixView" in plugin
    assert plugin.count('"actionEmMatrixView"') >= 1   # anche nella tupla di unload


def test_the_panel_says_why_when_the_file_cannot_be_read(tmp_path):
    from modules.s3dgraphy.em_matrix_panel import describe_failure
    rotto = tmp_path / "rotto.em.json"
    rotto.write_text("{non è json", encoding="utf-8")
    assert "non" in describe_failure(rotto).lower()


def test_the_export_window_can_show_the_matrix():
    src = Path(BRIDGE).read_text()
    assert "Vedi la matrice" in src
```

- [ ] **Step 2: Run test to verify it fails** — Expected: FAIL.

- [ ] **Step 3: Write minimal implementation**

Il pannello è un `QDockWidget` con la `MatrixView` a sinistra e, a destra, i dati del nodo selezionato (gli stessi campi della scheda: us, definizione, periodo, rapporti). In cima: «Adatta», «Salva SVG…», «Salva PNG…», e il conteggio «45 unità · 12 epoche». La voce di menu «Extended Matrix → Vedi la matrice…» chiede il sito (come l'export), esporta in una cartella temporanea e apre il pannello; la finestra dell'export prende un bottone «Vedi la matrice» accanto a «Apri in EMStudio», attivo dopo un export riuscito.

- [ ] **Step 4: Run test to verify it passes** — Expected: PASS.

- [ ] **Step 5: Run the whole suite** — Expected: PASS a parte il rumore noto.

- [ ] **Step 6: Commit**

```bash
git commit -am "feat(matrice): «Vedi la matrice» — il pannello dentro QGIS"
```

---

## Chiusura

- Suite intera col comando canonico.
- Collaudo vivo: SVG del sito di esempio guardato con gli occhi, e confronto delle fasce con quello che dice l'em.json.
- `tutorial-updater` (voce di menu e pannello nuovi) poi `stratigraph-changelog`.
- Review indipendente dell'intero ramo prima del tag.
- Release: bump `metadata.txt`, changelog bilingue, tag `em-matrix-panel-5.13.37-alpha`, push ramo + tag, `gh release create --prerelease`, voce api-docs RTD.
