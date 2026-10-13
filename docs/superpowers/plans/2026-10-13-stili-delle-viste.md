# Stili delle viste — piano di lavoro

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline) to implement this plan task-by-task; one fresh reviewer at the end. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** una finestra «Stili delle viste» che compone, anteprima, salva nel database e applica al caricamento lo stile (simbologia ed etichette) di ogni vista di pyArchInit, su SQLite e PostgreSQL.

**Architecture:** un modulo puro con il registro delle viste, le ricette delle etichette e la scelta dello stile; una tabella `pyarchinit_view_styles` letta e scritta con SQLAlchemy Core; un modulo QGIS che applica QML e ricetta a un layer e che i caricatori chiamano; una finestra Qt che usa gli editor di QGIS (`QgsRendererPropertiesDialog`, `QgsTextFormatWidget`) e un canvas di anteprima.

**Tech Stack:** PyQGIS 3.42 (minimo 3.22), SQLAlchemy Core, QDomDocument per i QML; test offscreen con `QT_QPA_PLATFORM=offscreen` e il Python di QGIS.

**Spec:** `docs/superpowers/specs/2026-10-13-stili-delle-viste-design.md`

## Global Constraints

- Nessun QML fornito viene modificato; nessuna colonna nuova su tabelle esistenti: una tabella nuova soltanto (`pyarchinit_view_styles`).
- Il progetto QGIS dell'utente non si tocca finché non preme «Applica ai layer caricati».
- Testi della finestra in it/en (tabella `_L`), nomi delle viste dai dizionari esistenti di `pyarchinit_pyqgis.py`.
- Mai aprire il database vivo di Enzo nei test: si usa `resources/dbfiles/pyarchinit_db.sqlite` copiato in `tmp_path`, e la fixture PostgreSQL di `tests/sync/conftest_pg.py` (salta se il server non c'è).
- Commit con percorsi espliciti; niente attribuzioni all'AI.
- Il comando della suite: `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python QGIS_PREFIX_PATH=/Applications/QGIS.app/Contents/MacOS /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest …` con `set -o pipefail` davanti a ogni `| grep`.

## Review Focus

1. Un QML salvato con «una per unità» porta un `$id IN (…)` stantio: al caricamento la ricetta deve ricalcolarlo, mai fidarsi del QML (test: salva con 2 unità, ricarica un layer con 3, le etichette sono 3).
2. Il predefinito del sito vince su quello «per tutti», e c'è un solo predefinito per (vista, sito) e uno per (vista, tutti): impostarne uno nuovo spegne il vecchio (test su SQLite e PG).
3. Una vista assente nel database (per esempio `pyarchinit_tomba_view` su SQLite senza tombe) non rompe la finestra: grigia e con la frase.
4. `apply_view_style` senza motore (`engine=None`, database non collegato) fa esattamente quello che il plugin fa oggi: QML fornito + ricetta.
5. Il canvas di anteprima e i layer caricati nella finestra non finiscono in `QgsProject.instance()` (test: il conteggio dei layer del progetto non cambia).

---

### Task 1: Registro, ricette e scelta dello stile (modulo puro)

**Files:**
- Create: `modules/utility/view_styles.py`
- Test: `tests/utility/test_view_styles.py`

**Interfaces:**
- Produces: `ViewSpec(name, label: dict[lang,str], geometry: 'polygon'|'line'|'point', site_field: str|None, qml: str|None, recipe: str|None, category_fields: tuple, group: str)`; `VIEWS: tuple[ViewSpec]`; `view_by_name(name) -> ViewSpec|None`; `GROUPS` (ordine e nomi it/en); `LabelRecipe(enabled: bool, preset: str|None, expression: str|None, placement: str, offset_mm: float, one_per_unit: bool)` con `to_json()/from_json()`, `default_recipe(spec) -> LabelRecipe`; `SavedStyle(id, view_name, site, name, qml, recipe: LabelRecipe, is_default, author, updated_at)`; `choose_style(styles, site) -> SavedStyle|None` (predefinito del sito, poi di «tutti», poi None); `PRESETS` delle etichette: `("none", "us_circle", "quota", "field")`.

- [ ] Scrivi i test: registro (ogni vista caricata dal plugin è nel registro: `pyarchinit_us_view`, `_usm_view`, `_quote_view`, `_quote_usm_view`, `_doc_view`, `_doc_view_b`, `_us_negative_doc_view`, `_strutture_view`, `_tomba_view`, `_individui_view`, `_ut_point_view`, `_ut_line_view`, `_ut_polygon_view`, `_site_view`, `_siti_polygonal_view`, `_reperti_view`, `_sezioni_view`; US e USM hanno ricetta `us_circle`, le quote `quota`, le altre `None`; i QML dichiarati esistono in `modules/gis/styles_spatialite`); ricetta: `to_json`/`from_json` giro completo, `default_recipe`; `choose_style`: sito batte tutti, tutti batte niente, uno stile non predefinito non si sceglie mai.
- [ ] Esegui: falliscono per `ModuleNotFoundError`.
- [ ] Implementa `view_styles.py` (nessun import Qt o QGIS a livello di modulo).
- [ ] Esegui: verdi. Commit: `feat(stili): registro delle viste, ricette delle etichette, scelta dello stile`.

### Task 2: La tabella `pyarchinit_view_styles` e il suo accesso

**Files:**
- Create: `modules/db/structures/View_styles_table.py`, `modules/utility/view_styles_store.py`
- Modify: `modules/db/pyarchinit_db_manager.py` (metodo `ensure_view_styles_table_exists`, come `ensure_fauna_table_exists`)
- Test: `tests/utility/test_view_styles_store.py` (SQLite in `tmp_path`), `tests/sync/test_view_styles_store_pg.py` (fixture `pg_engine`, come `test_site_filter_pg.py`)

**Interfaces:**
- Produces: `ensure_table(engine)`, `list_styles(engine, view_name) -> list[SavedStyle]`, `save_style(engine, style) -> int` (inserisce o aggiorna per id), `delete_style(engine, id)`, `set_default(engine, id)` (spegne gli altri con stessa vista e stesso sito — `site` nullo compreso), `clear_default(engine, id)`, `rename_style(engine, id, name)`, `legacy_qgis_styles(layer) -> list[(id, name)]` (da `layer.listStylesInDatabase()`), `now_iso()`.

- [ ] Test: la tabella si crea due volte senza errore; salva/elenca/rinomina/elimina; `set_default` spegne il predefinito precedente della stessa (vista, sito) e non tocca un altro sito né «tutti»; `choose_style(list_styles(...), site)` dà quello giusto; la ricetta torna identica dal JSON. Lo stesso file di test su PG (salta se il server manca).
- [ ] Esegui: rossi. Implementa con `Table(...)` SQLAlchemy e `metadata.create_all(engine)`; colonne: `id Integer PK autoincrement`, `view_name String(64) not null`, `site String(350)`, `name String(200) not null`, `qml Text not null`, `recipe Text`, `is_default Integer default 0`, `author String(100)`, `updated_at String(32)`.
- [ ] Esegui: verdi su SQLite; esegui il file PG. Commit: `feat(stili): tabella pyarchinit_view_styles su SQLite e PostgreSQL`.

### Task 3: Applicare uno stile a un layer (QGIS)

**Files:**
- Create: `modules/utility/view_styles_apply.py`
- Modify: `modules/utility/atlas_labels.py` (nessuna modifica di comportamento; `label_us_view`/`label_quote_view` restano e vengono riusate)
- Test: `tests/utility/test_view_styles_apply.py` (offscreen, layer in memoria e DB di prova copiato)

**Interfaces:**
- Produces: `export_qml_text(layer) -> str`; `import_qml_text(layer, text) -> bool`; `apply_recipe(layer, recipe)` (preset `us_circle` → `label_us_view`; `quota` → `label_quote_view`; `field` → etichetta semplice sul campo/espressione con posizione e scostamento; `none` → etichette spente; `one_per_unit` ricalcolato ogni volta); `shipped_qml(spec) -> str|None` (percorso assoluto); `apply_view_style(layer, view_name, site=None, *, engine=None) -> str` che torna `"saved:<id>"`, `"shipped"` o `"none"`: con `engine` cerca `choose_style(list_styles(engine, view_name), site)`; se trovato `import_qml_text` + `apply_recipe`; altrimenti QML fornito (se c'è) + `apply_recipe(default_recipe(spec))`.
- [ ] Test: `export`/`import` giro completo su un layer in memoria con categorie ed etichette; `apply_recipe(us_circle)` su un layer con 3 disegni di 2 unità mette 2 etichette anche se il QML importato ne portava 1 (Review Focus 1); `apply_view_style` con `engine=None` su `pyarchinit_quote_view` applica il QML fornito e la quota; con uno stile salvato predefinito lo applica e torna `saved:<id>`; su una vista senza QML e senza stile torna `"none"` e non tocca etichette.
- [ ] Esegui rossi, implementa, verdi. Commit: `feat(stili): applicare QML e ricetta a un layer, con la scelta del predefinito`.

### Task 4: I caricatori passano da `apply_view_style`

**Files:**
- Modify: `modules/gis/pyarchinit_pyqgis.py` (gli otto punti di `quote_us_view.qml`, i sette di `apply_style_to_layer`, e le altre viste del registro quando vengono caricate)
- Test: `tests/utility/test_us_view_labels.py` (le guardie esistenti si aggiornano), `tests/sync/test_view_styles_loaders.py` (AST: per ogni `_load_spatialite_view(..., '<vista del registro>', ...)` e ogni `setDataSource("public", "<vista>", ...)` segue `apply_view_style(` entro 12 righe; nessun `loadNamedStyle` dei QML forniti fuori da `view_styles_apply.py`; nessuna chiamata diretta a `label_us_view`/`label_quote_view` in `pyarchinit_pyqgis.py`)
- Interfaces: `Pyarchinit_pyqgis._stile_vista(layer, view_name, site)` → chiama `apply_view_style(layer, view_name, site, engine=self._engine_stili())`, dove `_engine_stili()` apre `create_engine(Connection().conn_str())` una volta e torna `None` se fallisce. Per la vista US: se `apply_view_style` torna `"saved:…"` il vecchio `styler.apply_style_to_layer` **non** si chiama; altrimenti si chiama come oggi e poi `_stile_vista` applica solo la ricetta (`apply_recipe(default_recipe)`).
- [ ] Scrivi la guardia AST (rossa), poi il refactoring con uno script che tocca ogni punto con un'asserzione sul numero di sostituzioni; `pyflakes` pulito.
- [ ] Esegui le guardie e le prove delle etichette; poi la suite intera. Commit: `feat(stili): i caricatori applicano lo stile predefinito della vista`.

### Task 5: La finestra «Stili delle viste»

**Files:**
- Create: `gui/view_styles_dialog.py`
- Test: `tests/sync/test_view_styles_dialog_smoke.py` (offscreen; DB di prova copiato in `tmp_path`; salta se `qgis.gui` manca)

**Interfaces:**
- Produces: `ViewStylesDialog(iface, engine, conn_str, site, parent=None, view_name=None)` con `objectName` sui widget: `viste` (QTreeWidget), `stili` (QListWidget), bottoni `nuovo`, `duplica`, `rinomina`, `elimina`, `predefinito_sito`, `predefinito_tutti`, `esporta`, `importa`, `applica`, `salva`, `salva_come`, `chiudi`; `anteprima` (QgsMapCanvas), `schede` (QTabWidget con «Simbologia» ed «Etichette»), `preset_simbologia` (QComboBox: «Solo contorno», «Categorie per …» uno per campo del registro), `editor_simbologia` (QgsRendererPropertiesDialog embedded), `etichette_attive`, `preset_etichette`, `campo_etichetta`, `espressione`, `posizione`, `scostamento`, `una_per_unita`, `formato_testo` (QgsTextFormatWidget); metodi pubblici per i test: `select_view(name)`, `current_layer()`, `current_recipe()`, `save(name=None, site=None)`, `set_default(scope)`, `export_qml(path)`, `import_qml(path)`, `apply_to_project()`.
- Comportamento: la vista scelta si carica dal DB (OGR su SQLite, `QgsDataSourceUri` su PG) **senza** aggiungerla al progetto, filtrata sul sito se la vista ha `site_field`; l'anteprima la mostra; i preset riempiono gli editor; «Salva» scrive via `save_style`; «Applica ai layer caricati» cerca nel progetto i layer la cui sorgente nomina la vista e applica QML + ricetta; una vista assente appare grigia con la frase; nessuna frase fissa in italiano fuori da `_L`.
- [ ] Test smoke: costruzione; elenco delle viste con gruppi; selezione di `pyarchinit_us_view` carica l'anteprima (`current_layer().featureCount() > 0`) e il conteggio dei layer del progetto non cambia (Review Focus 5); preset «Solo contorno» → renderer a simbolo singolo; preset etichette «Numero US cerchiato» → `current_recipe().preset == "us_circle"`; `save("prova")` → una riga; `set_default("site")` → `choose_style` la trova; `export_qml` scrive un file con `<labeling`; `import_qml` di quel file crea un secondo stile; `apply_to_project()` su un layer di progetto con quella sorgente cambia il suo renderer; `select_view("pyarchinit_tomba_view")` su un DB senza tombe non alza e mostra la frase.
- [ ] Esegui rossi, implementa, verdi. Commit: `feat(stili): la finestra Stili delle viste`.

### Task 6: Menu, scheda US, pannello dei layer

**Files:**
- Modify: `pyarchinitPlugin.py` (azione «Stili delle viste…» nel menu, come `actionEmMatrixView`; azione sul layer corrente con `iface.addCustomActionForLayerType` e `addCustomActionForLayer` sui layer di vista), `tabs/US_USM.py` (bottone «Stile…» accanto al bottone che carica i layer; trova il nome del bottone leggendo il metodo che chiama `charge_vector_layers` intorno alla riga 24599), `modules/utility/create_style.py` (`apply_style_to_layer` non chiede più niente se chi la chiama ha già applicato uno stile salvato: parametro `skip_if_styled` non serve — la decisione sta nel caricatore, Task 4)
- Test: `tests/sync/test_view_styles_wiring.py` (AST: l'azione esiste, è collegata a un metodo che costruisce `ViewStylesDialog`; il bottone della scheda US chiama lo stesso metodo; il nome delle azioni in it/en)
- [ ] Rossi, implementa, verdi. Commit: `feat(stili): voce di menu, bottone nella scheda US, azione sul layer`.

### Task 7: Documentazione, changelog, versione, rilascio

- [ ] Agente dei tutorial: tutorial 14 — la parte «Scelta dello stile» riscritta (la finestra in tre passi resta solo senza predefinito), sezione nuova «Stili delle viste» (elenco, anteprima, simbologia, etichette, stili salvati, predefiniti, QML), il paragrafo «Etichette» aggiornato; tutorial 36 §10.13 (vista US); dieci lingue; conteggi dei titoli allineati.
- [ ] Changelog 5.13.112-alpha bilingue (titolo, suite, Added/Changed/Test/Documentation); `metadata.txt` 5.13.112-alpha.
- [ ] Suite intera verde; commit `release: 5.13.112-alpha — Stili delle viste`; tag `stili-delle-viste-5.13.112-alpha`; push; `python3 scripts/publish_tutorials.py --push`.

### Task 8: Revisione finale

- [ ] Un revisore con contesto nuovo legge il diff dal commit della spec a HEAD contro spec e piano, con il Review Focus; Critical/Important si correggono in un passaggio solo con test rosso→verde; Minor nel changelog.
