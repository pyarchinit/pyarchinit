# PyArchInit - StratiGraph Development Changelog

> Registro dettagliato delle modifiche effettuate durante lo sviluppo dell'integrazione StratiGraph.
> Branch: `Stratigraph_00001`

---

## [5.0.4-alpha] - 2026-02-10

### Fix canvas resize in QtWebKit QWebView / Fix ridimensionamento canvas in QtWebKit QWebView

- **IT**: Risolto bug per cui le animazioni canvas HTML5 scomparivano quando si ridimensionava la finestra del Tutorial Viewer. QtWebKit non genera l'evento `window.resize` quando il widget QWebView padre viene ridimensionato, lasciando il buffer pixel del canvas con le dimensioni precedenti. Fix implementato su due livelli: (1) polling lato HTML ogni 250ms che controlla le dimensioni del container canvas e chiama `resize()` quando cambiano, e (2) bridge lato Python che intercetta `resizeEvent` del QWebView e invoca `resize()` via `evaluateJavaScript()`. Tutti i 12 file HTML delle animazioni aggiornati.
- **EN**: Fixed bug where HTML5 canvas animations disappeared when resizing the Tutorial Viewer window. QtWebKit does not fire `window.resize` when the parent QWebView widget is resized, leaving the canvas pixel buffer at stale dimensions. Fix implemented at two levels: (1) HTML-side polling every 250ms that checks canvas container dimensions and calls `resize()` when they change, and (2) Python-side bridge that intercepts QWebView `resizeEvent` and invokes `resize()` via `evaluateJavaScript()`. All 12 animation HTML files updated.

#### File modificati / Modified files
- `docs/animations/*.html` (12 file) — aggiunto polling dimensioni canvas / added canvas dimension polling
- `tabs/Tutorial_viewer.py` — aggiunto `eventFilter` + `_trigger_animation_resize()` / added resize event filter bridge
- `pyarchinitDockWidget.py` — aggiunto `eventFilter` + `_trigger_animation_resize()` / added resize event filter bridge

---

## [5.0.1-alpha] - 2026-02-10

### Riscrittura animazioni HTML5 per QtWebKit / HTML5 Animation Rewrite for QtWebKit

- **IT**: Riscrittura completa di tutte le 12 animazioni HTML5 in `docs/animations/` per compatibilita con il motore QtWebKit (~2015) integrato in QGIS 3.42.1 su macOS. Il Tutorial Viewer usa `QWebView` (QtWebKit) che supporta solo JavaScript ES5 e CSS3 senza funzionalita moderne.
- **EN**: Complete rewrite of all 12 HTML5 animations in `docs/animations/` for compatibility with the QtWebKit engine (~2015) bundled with QGIS 3.42.1 on macOS. The Tutorial Viewer uses `QWebView` (QtWebKit) which only supports ES5 JavaScript and CSS3 without modern features.

#### Modifiche JavaScript / JavaScript Changes
- `const`/`let` sostituiti con `var`
- Arrow functions `() => {}` sostituite con `function() {}`
- Template literals sostituite con concatenazione stringhe
- `String.padStart()` sostituito con funzione manuale `padTwo()`
- `NodeList.forEach()` sostituito con `Array.prototype.slice.call()` + ciclo `for`
- `classList.toggle(name, force)` sostituito con manipolazione `className` + `indexOf`/`replace`
- `element.dataset.xxx` sostituito con `getAttribute('data-xxx')`
- `String.includes()` sostituito con `indexOf() !== -1`
- `Array.findIndex()` sostituito con ciclo `for` manuale
- `ctx.ellipse()` sostituito con `drawEllipse()` custom (save/translate/scale/arc/restore)
- `.prepend()` sostituito con `insertBefore(el, firstChild)`
- Unicode escape ES6 `\u{1F3DB}` sostituiti con simboli BMP
- Optional chaining `?.` e nullish coalescing `??` rimossi

#### Modifiche CSS / CSS Changes
- Rimosso blocco `:root` e tutti i `var(--name)` — colori hardcoded inline
- Rimosso `backdrop-filter: blur()`
- CSS Grid sostituito con Flexbox + prefissi `-webkit-`
- `gap` sostituito con `margin` sui figli
- `inset: 0` sostituito con `top:0; right:0; bottom:0; left:0`
- Aggiunti prefissi `-webkit-` per: flex, transform, transition, animation, box-sizing, box-shadow
- Aggiunti `@-webkit-keyframes` per tutte le animazioni
- Rimosso `font-variant-numeric: tabular-nums`

#### File riscritti / Rewritten files
1. `pyarchinit_remote_storage_animation.html`
2. `pyarchinit_media_manager_animation.html`
3. `pyarchinit_installation_animation.html`
4. `harris_matrix_animation.html`
5. `pyarchinit_concurrency_animation.html`
6. `pyarchinit_image_classification_animation.html`
7. `pyarchinit_thesaurus_animation.html`
8. `pyarchinit_timemanager_animation.html`
9. `pyarchinit_image_export_animation.html`
10. `pyarchinit_create_map_animation.html`
11. `pyarchinit_pottery_tools_animation.html`
12. `stratigraph_sync_animation.html`

**Comportamento invariato / Behavior unchanged**: tutte le animazioni mantengono gli stessi scenari, controlli (Auto/Manual, speed, loop, pause, prev/next, restart, keyboard shortcuts), sidebar, event log, e animazioni canvas.

---

## [5.0.1-alpha] - 2026-02-08

### Fase 1 - Fondamenta

#### Commit `8abd7b2d` - Phase 1 StratiGraph integration
- **UUID Manager** (`modules/stratigraph/uuid_manager.py`): Creato modulo per generazione, validazione e gestione UUID v4. Funzioni: `generate_uuid()`, `ensure_uuid()`, `build_uri()`, `validate_uuid()`.
- **Bundle Creator** (`modules/stratigraph/bundle_creator.py`): Sistema di creazione bundle ZIP con struttura `data/`, `metadata/`, `media/`. Include export CIDOC-CRM, manifest e hash SHA-256.
- **Bundle Manifest** (`modules/stratigraph/bundle_manifest.py`): Generazione manifest JSON con 6 campi BMD obbligatori (schema_version, tool_id, provenance, integrity_hash, export_timestamp, ontology_references).
- **Bundle Validator** (`modules/stratigraph/bundle_validator.py`): Validazione pre-export con livelli ERROR/WARNING/INFO. Verifica BMD, file manifest, coerenza UUID, riferimenti ontologici.
- **Colonna entity_uuid**: Aggiunta a 19 tabelle in `structures/`, `entities/`, `structures_metadata/`.
- **Tabelle coinvolte**: site_table, us_table, inventario_materiali_table, tomba_table, periodizzazione_table, struttura_table, campioni_table, individui_table, pottery_table, media_table, media_thumb_table, media_to_entity_table, fauna_table, ut_table, tma_materiali_archeologici, tma_materiali_ripetibili, archeozoology_table, documentazione_table, inventario_lapidei_table.

#### Commit `fb1e67e5` - Auto-generate UUID on insert and migrate existing DBs
- **Entity auto-generation**: Tutte le 19 classi entity (`modules/db/entities/*.py`) ora generano automaticamente UUID v4 all'inserimento. Pattern: `entity_uuid=None` default + `uuid.uuid4()` nel `__init__`.
- **Migration hook**: `add_uuid_support.py` integrato nel flusso `connection()` di `pyarchinit_db_manager.py`. Usa pattern `_get_db_checked()` per esecuzione una tantum per sessione QGIS.
- **Engine sharing**: `UUIDSupport` accetta engine esterno per evitare connessioni duplicate.
- **Fix TMA table names**: Corretti nomi tabelle da `tma_table`/`tma_materiali_table` a `tma_materiali_archeologici`/`tma_materiali_ripetibili`.

#### Commit `85f14dac` - Add entity_uuid to SQL schemas, views, and template databases
- **PostgreSQL schema**: `entity_uuid text` aggiunto a 17 CREATE TABLE in `pyarchinit_schema_updated.sql` e 16 in `pyarchinit_schema_clean.sql`.
- **Migration SQL**: 19 ALTER TABLE in `pyarchinit_update_postgres.sql` (IF NOT EXISTS) e `pyarchinit_update_sqlite.sql`.
- **Views SQL**: `entity_uuid` aggiunto a 16 view SELECT in `create_view.sql` e `create_view_updated.sql`.
- **Template SQLite**: Colonna entity_uuid aggiunta a tutte le 19 tabelle in `pyarchinit.sqlite` e `pyarchinit_db.sqlite`.

#### Metadata
- **Versione**: Aggiornata a `5.0.1-alpha` in `metadata.txt`.
- **Experimental**: Impostato a `False` in `metadata.txt`.
- **Changelog**: Aggiunto blocco StratiGraph nel changelog di metadata.txt.

---

### Fase 2 — Offline-First

#### Sync State Machine (`modules/stratigraph/sync_state_machine.py`) — NUOVO
- **Enum `SyncState`**: 6 stati del ciclo di vita sync — `OFFLINE_EDITING`, `LOCAL_EXPORT`, `LOCAL_VALIDATION`, `QUEUED_FOR_SYNC`, `SYNC_SUCCESS`, `SYNC_FAILED`.
- **Classe `SyncStateMachine(QObject)`**: macchina a stati finiti con segnali Qt `state_changed(str, str)` e `transition_failed(str, str, str)`.
- **Mappa transizioni**: definizione esplicita delle transizioni valide tra stati.
- **Persistenza**: stato corrente e cronologia transizioni (max 50 voci, formato JSON) salvati in `QgsSettings` con prefisso `pyArchInit/stratigraph/`.
- **Metodi**: `transition()`, `get_transition_history()`, `reset()`.
- **Logging**: tutte le transizioni registrate via `QgsMessageLog`.

#### Sync Queue (`modules/stratigraph/sync_queue.py`) — NUOVO
- **Database SQLite dedicato**: `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite` con journal mode WAL.
- **Tabella `sync_queue`**: campi `id`, `bundle_path`, `bundle_hash`, `created_at`, `status`, `attempts`, `last_attempt_at`, `last_error`, `metadata`.
- **Dataclass `QueueEntry`**: rappresentazione in-memory di una voce della coda.
- **Classe `SyncQueue`**: operazioni FIFO — `enqueue`, `dequeue` (marca come uploading), `mark_completed`, `mark_failed` (auto-retry fino a 5 tentativi), `retry_failed`, `get_pending`, `get_all`, `cleanup_completed`, `get_stats`.
- **Thread-safety**: pattern open-use-close per le connessioni SQLite.

#### Connectivity Monitor (`modules/stratigraph/connectivity_monitor.py`) — NUOVO
- **Classe `ConnectivityMonitor(QObject)`**: monitoraggio periodico della connettivita di rete.
- **Segnali Qt**: `connection_available`, `connection_lost`, `connectivity_changed(bool)`.
- **Health check**: HTTP GET periodico (default 30s) verso URL configurabile (default `localhost:8080/health`).
- **Debounce**: N check consecutivi con stesso risultato prima di cambiare stato (default 2).
- **Rete**: usa `QgsNetworkAccessManager` con timeout 5 secondi.
- **Configurazione**: tutti i parametri regolabili via `QgsSettings`.

#### Sync Orchestrator (`modules/stratigraph/sync_orchestrator.py`) — NUOVO
- **Classe `SyncOrchestrator(QObject)`**: coordinamento centrale di state machine, coda e connectivity monitor.
- **Segnali Qt**: `sync_started(int)`, `sync_progress(int, int, str)`, `sync_completed(int, bool, str)`, `bundle_exported(str)`.
- **Pipeline `export_bundle(site_name)`**: flusso completo `OFFLINE_EDITING` -> `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC` con validazione bundle integrata (usa `BundleCreator` e `validate_bundle` dalla Fase 1).
- **`sync_now()`**: forza tentativo di sincronizzazione immediato.
- **`get_status()`**: snapshot dello stato corrente dell'orchestratore.
- **Auto-sync**: la coda viene processata automaticamente quando arriva il segnale `connection_available`.
- **Retry con backoff esponenziale**: intervalli `[30s, 60s, 120s, 300s, 900s]`.
- **Upload temporaneo**: wrapper HTTP POST placeholder in attesa delle specifiche API WP4.

#### UI Sync Panel (`gui/stratigraph_sync_panel.py`) — NUOVO
- **Classe `StratiGraphSyncPanel(QDockWidget)`**: pannello dock con indicatori di stato (stato sync, connettivita, statistiche coda, ultimo sync).
- **Pulsanti azione**: Export Bundle, Sync Now, Queue...
- **Log attivita**: `QTextEdit` read-only con voci timestampate.
- **`QueueDialog(QDialog)`**: finestra con `QTableWidget` per visualizzare tutte le voci della coda.
- **Aggiornamento live**: connesso ai segnali dell'orchestratore per aggiornamenti in tempo reale.
- **Refresh periodico**: timer a 5 secondi per statistiche della coda.

#### Icona (`resources/icons/stratigraph_sync.png`) — NUOVO
- Icona 22x22 PNG: cerchio verde con frecce di sync e lettera "S".

#### File modificati

- **`modules/stratigraph/__init__.py`**: aggiunti import Fase 2 — `SyncState`, `SyncStateMachine`, `SyncQueue`, `QueueEntry`, `ConnectivityMonitor`, `SyncOrchestrator`.
- **`pyarchinitPlugin.py`**: integrazione nel plugin principale:
  - `_init_stratigraph_sync()`: crea `SyncOrchestrator`, `StratiGraphSyncPanel`, aggiunge dock widget (nascosto per default), crea azione toolbar con icona `stratigraph_sync.png`, avvia orchestratore.
  - `_unload_stratigraph_sync()`: ferma orchestratore, rimuove dock widget e icona toolbar.
  - `_toggle_sync_panel()`: mostra/nasconde il pannello sync.
  - `_init_stratigraph_sync()` chiamato alla fine di tutti e 4 i blocchi locale in `initGui()` (it, en, de, else).
  - `_unload_stratigraph_sync()` chiamato all'inizio di `unload()`.
- **`STRATIGRAPH_INTEGRATION.md`**: aggiornamento stati Task 2.x da "DA FARE" a "FATTO 100%", gap analysis sezione 3.4 completata, retry sezione 3.5 completato, struttura moduli aggiornata, tabella riepilogativa da ~42% a ~57%.

---

### Strumenti di Testing

#### Mock Server (`scripts/stratigraph_mock_server.py`) — NUOVO

Server HTTP locale che simula il Knowledge Graph di WP4 per testare il flusso di sincronizzazione senza dipendere dall'infrastruttura esterna.

**Perché serve**: Il server StratiGraph (gestito da WP4) non è ancora disponibile. Per verificare che il flusso di sync funzioni end-to-end — dall'export del bundle alla validazione, all'invio HTTP — serve un endpoint locale che accetti i bundle e risponda correttamente al health check.

**Architettura StratiGraph**: PyArchInit NON sincronizza con un server personale. StratiGraph è un **Knowledge Graph condiviso** dove confluiscono dati da più strumenti archeologici (PyArchInit, 3DHOP, ArcheoGrid, ecc.), ciascuno specializzato in un aspetto. Il flusso è **unidirezionale**: PyArchInit esporta bundle CIDOC-CRM verso il KG, non riceve dati indietro. Il mock server simula esattamente questo comportamento.

**Endpoint simulati**:
- `GET /health` — health check (usato da `ConnectivityMonitor`)
- `POST /api/v1/bundles` — ricezione bundle ZIP (usato da `SyncOrchestrator`)
- `GET /api/v1/bundles` — lista bundle ricevuti (JSON)
- `GET /` — pagina web di stato (solo modalità FastAPI)

**Due modalità**:
- Completa (FastAPI + uvicorn): web UI, log dettagliati. Richiede `pip install fastapi uvicorn python-multipart`.
- Semplice (http.server built-in): nessuna dipendenza esterna, funzionalità base.

**Uso**:
```bash
python scripts/stratigraph_mock_server.py          # FastAPI (default)
python scripts/stratigraph_mock_server.py --simple  # http.server
```

I bundle ricevuti vengono salvati in `$PYARCHINIT_HOME/stratigraph_mock_received/`.

#### Documentazione architettura

- **`STRATIGRAPH_INTEGRATION.md` sezione 1.1**: Aggiunto diagramma completo dell'architettura del Knowledge Graph StratiGraph, spiegazione del flusso dati unidirezionale, chiarimento su cosa NON è il sistema, e motivazione dell'architettura offline-first.
- **`STRATIGRAPH_INTEGRATION.md` sezione 1.2**: Documentazione dettagliata del mock server con tabella endpoint, istruzioni d'uso e opzioni di configurazione.

---

### Tutorial Viewer — Embedded Animation Playback

#### `tabs/Tutorial_viewer.py` — RISCRITTO parzialmente
- **Multi-path import**: QWebEngineView importato tramite fallback chain (`qgis.PyQt.QtWebEngineWidgets` → `PyQt5.QtWebEngineWidgets` → `PyQt6.QtWebEngineWidgets`). Nuovi globali: `HAS_WEBENGINE_ANIM`, `_QWebEngineView`.
- **Rimossa classe `TutorialWebEnginePage`**: non più necessaria — QTextBrowser gestisce il markdown, QWebEngineView carica le animazioni direttamente via `setUrl()`.
- **QStackedWidget**: area contenuto ora usa `self.content_stack` con due pagine:
  - **Pagina 0**: `self.content_browser` (QTextBrowser) — sempre usato per rendering markdown
  - **Pagina 1**: `self.animation_viewer` (QWebEngineView) — per file HTML5 animazione
- **`_on_link_clicked()`**: rileva file `.html` locali e li carica nel viewer animazione embedded tramite `_load_animation()` invece di aprire il browser di sistema.
- **`_load_animation(path)`**: sostituisce `_load_local_html_file()` — switcha lo stack a pagina 1, carica via `setUrl()`, mostra pulsante indietro.
- **`_on_back_clicked()`**: switcha lo stack a pagina 0, pulisce il viewer animazione.
- **Gestione immagini**: rimosso branch `use_webengine` — sempre usa thumbnail base64 di QTextBrowser.

#### `pyarchinitDockWidget.py` — RISCRITTO parzialmente
- **Multi-path import**: stesso pattern di fallback chain. Nuovi globali: `_DockQWebEngineView`, `_dock_log()`.
- **Rimossa classe `DockTutorialWebPage`**: non più necessaria.
- **QStackedWidget**: tab tutorial ora usa `self.tutorial_content_stack` con:
  - **Pagina 0**: `self.tutorial_content` (QTextBrowser) — markdown
  - **Pagina 1**: `self.tutorial_animation` (QWebEngineView) — animazioni
- **`_on_tutorial_link_clicked(url)`**: nuovo handler per click su link in QTextBrowser, rileva `.html` e carica nel viewer embedded.
- **`_load_animation_in_viewer(path)`**: switcha lo stack a pagina 1.
- **`_on_tutorial_back()`**: switcha lo stack a pagina 0.
- **Gestione immagini**: sempre converte a base64 (rimossa condizione `not HAS_WEBENGINE`).

#### Degradazione graceful
Se QWebEngineView non è disponibile da nessun percorso di import, `self.animation_viewer` / `self.tutorial_animation` è `None`, e i link `.html` aprono nel browser di sistema (comportamento precedente).

---

### UI & Branding

#### Splash Screen — Redesign futuristico (`gui/pyarchinit_splash.py`) — RISCRITTO

Splash screen completamente riscritto con design futuristico "deep space", sempre in movimento.

**Nuove classi:**
- `Particle`: singola particella nel campo (usa `__slots__` per performance)
- `OrbitalRing`: anello orbitale con proiezione 3D
- `FuturisticSplashWidget(QWidget)`: widget principale con rendering custom via `paintEvent`

**Effetti visivi (tutti in movimento continuo):**
- **Particle field** (90 particelle): drift orbitale con gravita verso il centro, glow, fade-in/out, palette cyan/blue/orange
- **4 anelli orbitali 3D**: proiezione prospettica con tilt variabile, punti luminosi, color cycling
- **5 nodi energetici**: orbiting con trail ghosting (3 posizioni fantasma)
- **Onde energetiche**: 3 anelli concentrici espandibili dal centro
- **Griglia di scansione**: linee sottili con sweep line orizzontale animata
- **Logo centrale**: halo pulsante multi-layer (4 livelli), sfondo circolare scuro con bordo cyan
- **Titolo "pyArchInit 5"**: letter-spacing, glow cyan pulsante
- **Testo status**: effetto typewriter (30 chars/sec) con cursore lampeggiante
- **Accenti angolari**: bracket sui 4 angoli + tick dati mobili sui bordi superiore/inferiore
- **Sfondo**: gradiente radiale deep-space (15,25,60 -> 3,5,15)

**Loghi partner (in basso, centrati):**
- Logo CNR-ISPC con glow e pulsazione opacita
- Logo Horizon StratiGraph (placeholder) con glow
- Separatore luminoso con gradiente fade
- Label "in collaboration with" animata

**Compatibilita:**
- Qt5/Qt6: tutti gli import usano `qgis.PyQt` (version-independent)
- Enum Qt6 syntax: `Qt.WindowType.FramelessWindowHint`, `Qt.PenStyle.NoPen`, etc.
- API pubblica invariata: `PyArchInitSplash(parent, message, modal)`, `set_message()`, `show_splash_during_operation()`

**Dimensioni:** 700x500px (da 650x520)

#### Loghi partner — NUOVI
- `resources/icons/logo_cnr_ispc.png` (258x89px): logo compatto CNR-ISPC scaricato da ispc.cnr.it
- `resources/icons/logo_horizon_stratigraph.png` (258x89px): placeholder generato programmaticamente — da sostituire con logo ufficiale Horizon

---

### Documentation

#### README.md — Aggiornamento progetto StratiGraph
- Aggiunta sezione **StratiGraph / Horizon Europe Integration** con: CIDOC-CRM mapping, bundle system, offline-first architecture, UUID, connectivity monitoring, sync dashboard
- Aggiornato **Project Structure** con albero `modules/stratigraph/` (8 file)
- Aggiunta sezione **Acknowledgments > StratiGraph - Horizon Europe** con partner (CNR-ISPC, 3DR, ARC) e timeline
- Link a `STRATIGRAPH_INTEGRATION.md` per dettagli tecnici

---

### Organizzazione Progetto e Tooling / Project Organization & Tooling

#### Commit `284835e2` — 2026-02-10: Riorganizzazione animazioni, pulizia git, agenti autonomi / Reorganize animations, git cleanup, autonomous agents

##### Riorganizzazione file animazioni / Animation files reorganization
- IT: Spostati 12 file HTML5 animazione da `docs/` a `docs/animations/` per una struttura directory piu ordinata e manutenibile.
- EN: Moved 12 HTML5 animation files from `docs/` root to `docs/animations/` for a cleaner, more maintainable directory structure.

##### Aggiornamento riferimenti tutorial / Tutorial references update
- IT: Aggiornati 84 riferimenti in 77 file tutorial markdown in tutte le 7 lingue (it, en, de, es, fr, ar, ca) per puntare al nuovo percorso `../animations/` invece di `../../`.
- EN: Updated 84 references across 77 tutorial markdown files in all 7 languages (it, en, de, es, fr, ar, ca) to point to the new path `../animations/` instead of `../../`.

##### Aggiornamento `.gitignore` / `.gitignore` update
- IT: Aggiornato `.gitignore` per tracciare la directory `docs/animations/` e tutti e 4 i file di configurazione agenti in `.claude/agents/`.
- EN: Updated `.gitignore` to track the `docs/animations/` directory and all 4 agent config files in `.claude/agents/`.

##### Agenti autonomi in `CLAUDE.md` / Autonomous agents in `CLAUDE.md`
- IT: Aggiunta sezione "Autonomous Agents" a `CLAUDE.md` con istruzioni per l'invocazione automatica degli agenti `stratigraph-changelog` e `tutorial-updater` dopo ogni modifica al codice o all'interfaccia utente.
- EN: Added "Autonomous Agents" section to `CLAUDE.md` with instructions for automatic invocation of `stratigraph-changelog` and `tutorial-updater` agents after every code or UI change.

##### Aggiornamento configurazione agenti / Agent configuration update
- IT: Aggiornati `.claude/agents/stratigraph-changelog.md` (invocazione proattiva, voci bilingui IT+EN) e `.claude/agents/tutorial-updater.md` (invocazione proattiva).
- EN: Updated `.claude/agents/stratigraph-changelog.md` (proactive invocation, bilingual IT+EN entries) and `.claude/agents/tutorial-updater.md` (proactive invocation).

##### Pulizia cronologia git / Git history cleanup
- IT: Rimossi tutti i 108 riferimenti `Co-Authored-By: Claude` dalla cronologia git su tutti i branch tramite `git filter-repo` e force push. Tutti i commit risultano ora esclusivamente a nome di Enzo Cocca.
- EN: Removed all 108 `Co-Authored-By: Claude` lines from git history across all branches via `git filter-repo` and force push. All commits now appear solely under Enzo Cocca's authorship.

#### File modificati / Files modified
- `docs/animations/` — nuova directory con 12 file HTML5 animazione
- `docs/tutorials/{it,en,de,es,fr,ar,ca}/*.md` — 77 file, 84 riferimenti aggiornati
- `.gitignore` — regole per `docs/animations/` e `.claude/agents/`
- `CLAUDE.md` — sezione Autonomous Agents
- `.claude/agents/stratigraph-changelog.md` — configurazione aggiornata
- `.claude/agents/tutorial-updater.md` — configurazione aggiornata

---

### Compatibilita QtWebKit / QtWebKit Compatibility

#### `docs/animations/pyarchinit_remote_storage_animation.html` — RISCRITTO per QtWebKit / REWRITTEN for QtWebKit

##### Description / Descrizione
- 🇮🇹 **IT**: Riscritta completamente l'animazione HTML5 "Remote Storage" per compatibilita con il vecchio motore QtWebKit (circa 2015) usato dal QWebView di QGIS. Tutte le funzionalita ES6+ sono state sostituite con equivalenti ES5: `const`/`let` → `var`, arrow functions → `function()`, template literals → concatenazione stringhe, `padStart` → funzione manuale `padTwo()`, `classList.toggle(name, force)` → if/else con add/remove via regex, `forEach` su NodeList → `Array.prototype.slice.call()`, `ctx.ellipse()` → funzione `drawEllipse()` con `arc()` + `scale()`. Nel CSS: rimosso `:root` e `var()` con colori hardcoded, rimosso `backdrop-filter`, sostituito CSS Grid con Flexbox + prefissi `-webkit-`, aggiunti `@-webkit-keyframes`, aggiunti prefissi `-webkit-flex`, `-webkit-box-flex`, `-webkit-transform`, etc. Il layout, le animazioni Canvas, l'interattivita e il comportamento visivo sono identici all'originale.
- 🇬🇧 **EN**: Completely rewrote the "Remote Storage" HTML5 animation for compatibility with the old QtWebKit engine (circa 2015) used by QGIS QWebView. All ES6+ features replaced with ES5 equivalents: `const`/`let` → `var`, arrow functions → `function()`, template literals → string concatenation, `padStart` → manual `padTwo()` function, `classList.toggle(name, force)` → if/else with add/remove via regex, `forEach` on NodeList → `Array.prototype.slice.call()`, `ctx.ellipse()` → `drawEllipse()` function using `arc()` + `scale()`. In CSS: removed `:root` and `var()` with hardcoded colors, removed `backdrop-filter`, replaced CSS Grid with Flexbox + `-webkit-` prefixes, added `@-webkit-keyframes`, added `-webkit-flex`, `-webkit-box-flex`, `-webkit-transform` prefixes, etc. Layout, Canvas animations, interactivity and visual behavior are identical to the original.

##### File modificati / Files modified
- `docs/animations/pyarchinit_remote_storage_animation.html` — riscrittura completa ES5/QtWebKit

---

#### `docs/animations/pyarchinit_media_manager_animation.html` — RISCRITTO per QtWebKit / REWRITTEN for QtWebKit

##### Description / Descrizione
- IT: Riscritta completamente l'animazione HTML5 "Media Manager" per compatibilita con il vecchio motore QtWebKit (circa 2015) usato dal QWebView di QGIS. Tutte le funzionalita ES6+ sono state sostituite con equivalenti ES5: `const`/`let` -> `var`, arrow functions -> `function(){}`, template literals -> concatenazione stringhe, `padStart` -> funzione manuale `padTwo()`, `classList.toggle(name, force)` -> if/else con add/remove via regex su `className`, `forEach` su NodeList -> `Array.prototype.slice.call()` + for-loop, `dataset.xxx` -> `getAttribute('data-xxx')`, `String.includes()` -> `indexOf() !== -1`. Nel CSS: rimosso `:root` e `var(--name)` con colori hardcoded inline, rimosso `backdrop-filter`, sostituito CSS Grid con Flexbox + prefissi `-webkit-`, `gap` sostituito con `margin` sui figli, aggiunti `@-webkit-keyframes`, aggiunti prefissi `-webkit-flex`, `-webkit-transform`, `-webkit-transition`, `-webkit-animation`, `-webkit-align-items`, `-webkit-justify-content`, `-webkit-flex-direction`, `-webkit-flex-wrap`, `-webkit-flex-shrink`, `-webkit-order`. Il layout (header, main canvas, sidebar, log), le animazioni Canvas (media gallery, association diagram, entity nodes, dashed arrows), l'interattivita (auto/manual mode, speed, play/pause, loop, prev/next, keyboard shortcuts, scenario select) e il comportamento visivo sono identici all'originale.
- EN: Completely rewrote the "Media Manager" HTML5 animation for compatibility with the old QtWebKit engine (circa 2015) used by QGIS QWebView. All ES6+ features replaced with ES5 equivalents: `const`/`let` -> `var`, arrow functions -> `function(){}`, template literals -> string concatenation, `padStart` -> manual `padTwo()` function, `classList.toggle(name, force)` -> if/else with add/remove via regex on `className`, `forEach` on NodeList -> `Array.prototype.slice.call()` + for-loop, `dataset.xxx` -> `getAttribute('data-xxx')`, `String.includes()` -> `indexOf() !== -1`. In CSS: removed `:root` and `var(--name)` with hardcoded inline colors, removed `backdrop-filter`, replaced CSS Grid with Flexbox + `-webkit-` prefixes, `gap` replaced with `margin` on children, added `@-webkit-keyframes`, added `-webkit-flex`, `-webkit-transform`, `-webkit-transition`, `-webkit-animation`, `-webkit-align-items`, `-webkit-justify-content`, `-webkit-flex-direction`, `-webkit-flex-wrap`, `-webkit-flex-shrink`, `-webkit-order` prefixes. Layout (header, main canvas, sidebar, log), Canvas animations (media gallery, association diagram, entity nodes, dashed arrows), interactivity (auto/manual mode, speed, play/pause, loop, prev/next, keyboard shortcuts, scenario select) and visual behavior are identical to the original.

##### File modificati / Files modified
- `docs/animations/pyarchinit_media_manager_animation.html` — riscrittura completa ES5/QtWebKit

---

## Note

- Tutte le modifiche sono sul branch `Stratigraph_00001`
- La Fase 1 (Fondamenta) e la Fase 2 (Offline-First) sono completate
- La Fase 3 (Integrazione WP4) e in attesa delle specifiche API dal WP4
- La Fase 4 (CIDOC-CRM e ottimizzazione) e ancora da implementare
- I task bloccati dipendono da deliverable esterni WP3/WP4
