# PyArchInit - StratiGraph Development Changelog

> Registro dettagliato delle modifiche effettuate durante lo sviluppo dell'integrazione StratiGraph.
> Branch: `Stratigraph_00001`

---

## [5.2.6-alpha] - 2026-02-12

### refactor(ui): Refactoring layout descrizioni in 12 animazioni docs/animations / Description layout refactoring in 12 animations docs/animations

- **IT**: Refactoring completo del layout descrizioni in tutti i 12 file HTML in `docs/animations/`. I pannelli descrizione (`.desc-box`, `.scene-desc`, `.dsc`, `.scenario-desc` — 4 varianti di classe diverse) erano overlay assoluti (`position:absolute; top/left`) che si sovrapponevano al contenuto del canvas. Sono stati tutti trasformati in `.desc-panel` — un pannello flex dedicato posizionato sotto l'area canvas. Miglioramenti: descrizioni spostate da overlay assoluto a child flex, nuovo CSS con tipografia migliorata (font 0.9rem, line-height 1.7, monospace per nomi di funzioni in `<strong>`), preservati gli schemi colore specifici di ogni file (#4ec9b0 per harris_matrix, #4fc3f7 per stratigraph_sync, #58a6ff per i restanti), regole responsive aggiunte in tutti i blocchi `@media`. Script batch Python per 10 file + 2 fix manuali per strutture HTML particolari (installation con `<div class="scene">` e stratigraph_sync con `step-indicator` e `kg-overlay`).
- **EN**: Complete description layout refactoring in all 12 HTML files in `docs/animations/`. The description panels (`.desc-box`, `.scene-desc`, `.dsc`, `.scenario-desc` — 4 different class variants) were absolute-positioned overlays (`position:absolute; top/left`) that overlapped canvas content. They have all been transformed into `.desc-panel` — a dedicated flex panel positioned below the canvas area. Improvements: descriptions moved from absolute overlay to proper flex child, new CSS with improved typography (font 0.9rem, line-height 1.7, monospace for function names in `<strong>`), preserved each file's specific color scheme (#4ec9b0 for harris_matrix, #4fc3f7 for stratigraph_sync, #58a6ff for the rest), responsive rules added in all `@media` blocks. Python batch script for 10 files + 2 manual fixes for particular HTML structures (installation with `<div class="scene">` and stratigraph_sync with `step-indicator` and `kg-overlay`).

#### File modificati / Modified files
- `docs/animations/harris_matrix_animation.html`
- `docs/animations/pyarchinit_concurrency_animation.html`
- `docs/animations/pyarchinit_create_map_animation.html`
- `docs/animations/pyarchinit_image_classification_animation.html`
- `docs/animations/pyarchinit_image_export_animation.html`
- `docs/animations/pyarchinit_installation_animation.html`
- `docs/animations/pyarchinit_media_manager_animation.html`
- `docs/animations/pyarchinit_pottery_tools_animation.html`
- `docs/animations/pyarchinit_remote_storage_animation.html`
- `docs/animations/pyarchinit_thesaurus_animation.html`
- `docs/animations/pyarchinit_timemanager_animation.html`
- `docs/animations/stratigraph_sync_animation.html`

---

## [5.2.5-alpha] - 2026-02-12

### refactor(ui): Refactoring layout descrizioni in 11 animazioni algoritmi / Description layout refactoring in 11 algorithm animations

- **IT**: Refactoring completo del layout descrizioni in tutti gli 11 file HTML in `docs/algorithm_animations/`. I pannelli descrizione (`.desc-box`) erano in precedenza overlay assoluti (`position:absolute; top/left`) che si sovrapponevano al contenuto del canvas e agli elementi animati. Sono stati trasformati in `.desc-panel` - un pannello flex dedicato posizionato sotto l'area canvas che non si sovrappone mai. Miglioramenti chiave: descrizioni spostate da overlay assoluto a child flex di `.main`, nuovo CSS con tipografia migliorata (font 0.9rem invece di 0.8rem, line-height 1.7 invece di 1.4, styling monospace per nomi di funzioni), tag `<strong>` ora renderizzati con font monospace e sfondo accent sottile per migliore leggibilità del codice, regole responsive aggiunte per schermi piccoli (max-height ridotto, padding compatto), tutti gli 11 file aggiornati in modo consistente (escluso file sperimentale MODERN_TEST), dots bar rimane nel canvas, pannello descrizione si posiziona tra canvas e area sidebar/log.
- **EN**: Complete description layout refactoring in all 11 HTML files in `docs/algorithm_animations/`. The description panels (`.desc-box`) were previously absolute-positioned overlays (`position:absolute; top/left`) that overlapped canvas content and animation elements. They have been transformed into `.desc-panel` - a dedicated flex panel positioned below the canvas area that never overlaps. Key improvements: descriptions moved from absolute overlay to proper flex child of `.main`, new CSS with improved typography (font 0.9rem instead of 0.8rem, line-height 1.7 instead of 1.4, monospace styling for function names), `<strong>` tags now rendered with monospace font and subtle accent background for better code readability, responsive rules added for small screens (reduced max-height, compact padding), all 11 files updated consistently (excluding MODERN_TEST experimental file), dots bar remains in canvas, description panel sits between canvas and sidebar/log area.

#### File modificati / Modified files
- `docs/algorithm_animations/crud_operations_algorithm.html`
- `docs/algorithm_animations/database_creation_algorithm.html`
- `docs/algorithm_animations/db_import_export_algorithm.html`
- `docs/algorithm_animations/harris_matrix_algorithm.html`
- `docs/algorithm_animations/image_classification_algorithm.html`
- `docs/algorithm_animations/media_management_algorithm.html`
- `docs/algorithm_animations/order_layer_algorithm.html`
- `docs/algorithm_animations/package_installation_algorithm.html`
- `docs/algorithm_animations/pdf_creation_algorithm.html`
- `docs/algorithm_animations/report_ai_algorithm.html`
- `docs/algorithm_animations/tops_algorithm.html`

---

## [5.2.4-alpha] - 2026-02-11

### Fix nested flex layout per 6 animazioni docs/animations / Nested flex layout fix for 6 animations in docs/animations

- **IT**: Applicato il fix del layout flex nidificato a 6 file HTML in `docs/animations/`. Il vecchio layout usava `flex-wrap:wrap` su `.app` che causava bug di ridimensionamento del canvas. Il fix introduce un nuovo wrapper `.middle` (flex row) tra header e log, cambia `.app` da `flex-wrap:wrap` a `flex-direction:column`, imposta `body` a `height:100vh;overflow:hidden` (rimosso `min-height:100vh;overflow-x:hidden`), aggiunge `min-height:0` a `.main` e alla classe scene (`.scene-wrap`/`.scene`), rimuove `width:100%`, `order`, `flex-basis`, `flex-shrink` dalla classe log (`.log-area`/`.log`), e cambia i riferimenti `.app` nei media query in `.middle`. Gestiti sia layout multi-riga (harris_matrix, concurrency) sia layout compatti su riga singola (installation, media_manager, pottery_tools, thesaurus), con varianti di nomi classe (`.sidebar`/`.side`, `.scene-wrap`/`.scene`, `.log-area`/`.log`, `.main`/`.main-col`).
- **EN**: Applied the nested flex layout fix to 6 HTML files in `docs/animations/`. The old layout used `flex-wrap:wrap` on `.app` which caused canvas resize bugs. The fix introduces a new `.middle` wrapper (flex row) between header and log, changes `.app` from `flex-wrap:wrap` to `flex-direction:column`, sets `body` to `height:100vh;overflow:hidden` (removed `min-height:100vh;overflow-x:hidden`), adds `min-height:0` to `.main` and the scene class (`.scene-wrap`/`.scene`), removes `width:100%`, `order`, `flex-basis`, `flex-shrink` from the log class (`.log-area`/`.log`), and changes `.app` references in media queries to `.middle`. Handled both multi-line layouts (harris_matrix, concurrency) and compact single-line layouts (installation, media_manager, pottery_tools, thesaurus), with class name variants (`.sidebar`/`.side`, `.scene-wrap`/`.scene`, `.log-area`/`.log`, `.main`/`.main-col`).

#### File modificati / Modified files
- `docs/animations/harris_matrix_animation.html`
- `docs/animations/pyarchinit_concurrency_animation.html`
- `docs/animations/pyarchinit_installation_animation.html`
- `docs/animations/pyarchinit_media_manager_animation.html`
- `docs/animations/pyarchinit_pottery_tools_animation.html`
- `docs/animations/pyarchinit_thesaurus_animation.html`

---

## [5.2.3-alpha] - 2026-02-11

### Rimozione completa DPR scaling dal canvas in tutte le animazioni / Complete DPR scaling removal from canvas in all animations

- **IT**: Rimosso completamente il sistema di scaling `devicePixelRatio` da tutte le 23 animazioni HTML (11 in `docs/algorithm_animations/` + 12 in `docs/animations/`). Il fix precedente (cap a 4096px + `ctx.setTransform`) non risolveva il problema: il canvas continuava a spostarsi e sparire durante il resize perché `canvas.style.width/height` settato da JS sovrascriveva il CSS `width:100%;height:100%` rompendo il flex layout. Nuovo approccio: resize semplificato a `canvas.width = wrap.clientWidth; canvas.height = h` (mapping 1:1 buffer↔display), rimosso `canvas.style.width/height` da JS, rimosso `ctx.setTransform(scale,...)`, rimosso tutte le divisioni per DPR nelle funzioni di disegno (`cv.width/(window.devicePixelRatio||1)` → `cv.width`), rimossi i fallback `canvas.clientWidth || parseInt(canvas.style.width, 10) || canvas.width` → `canvas.width`.
- **EN**: Completely removed `devicePixelRatio` scaling system from all 23 animation HTML files (11 in `docs/algorithm_animations/` + 12 in `docs/animations/`). The previous fix (4096px cap + `ctx.setTransform`) didn't solve the problem: canvas kept shifting and disappearing on resize because JS-set `canvas.style.width/height` overrode CSS `width:100%;height:100%` breaking flex layout. New approach: simplified resize to `canvas.width = wrap.clientWidth; canvas.height = h` (1:1 buffer↔display mapping), removed `canvas.style.width/height` from JS, removed `ctx.setTransform(scale,...)`, removed all DPR divisions in drawing functions (`cv.width/(window.devicePixelRatio||1)` → `cv.width`), removed `canvas.clientWidth || parseInt(...)` fallbacks → `canvas.width`.

#### File modificati / Modified files
- `docs/algorithm_animations/*.html` (tutti 11 file / all 11 files)
- `docs/animations/*.html` (tutti 12 file / all 12 files)

---

## [5.2.2-alpha] - 2026-02-11

### Fix canvas e posizione desc-box in 5 animazioni (Gruppo B) / Fix canvas and desc-box position in 5 animations (Group B)

- **IT**: Corretti gli stessi due bug nelle rimanenti 5 animazioni HTML (Gruppo B: `crud_operations_algorithm.html`, `database_creation_algorithm.html`, `image_classification_algorithm.html`, `pdf_creation_algorithm.html`, `db_import_export_algorithm.html`). Bug 1: il canvas spariva a dimensioni finestra grandi; fix: dimensioni interne limitate a max 4096px per asse con DPR-aware scaling e `ctx.setTransform(scale, ...)`. Per i file 1-4 che usavano `canvas.width = wrap.clientWidth` senza DPR, aggiunto calcolo scale completo. Per `db_import_export_algorithm.html` che gia usava DPR, aggiunto solo il cap. Aggiornate anche le funzioni `layoutBoxes()`/`drawScene()` per leggere le dimensioni CSS (`canvas.clientWidth`/`canvas.clientHeight`) invece di `canvas.width`/`canvas.height` (ora in pixel fisici). Bug 2: `.desc-box` spostato da `top:10px` a `bottom:40px`. Tutto in ES5 puro.
- **EN**: Fixed the same two bugs in the remaining 5 animation HTML files (Group B: `crud_operations_algorithm.html`, `database_creation_algorithm.html`, `image_classification_algorithm.html`, `pdf_creation_algorithm.html`, `db_import_export_algorithm.html`). Bug 1: canvas disappeared at large window sizes; fix: internal canvas dimensions capped at max 4096px per axis with DPR-aware scaling and `ctx.setTransform(scale, ...)`. For files 1-4 that used `canvas.width = wrap.clientWidth` without DPR, added full scale calculation. For `db_import_export_algorithm.html` that already used DPR, added only the cap. Also updated `layoutBoxes()`/`drawScene()` functions to read CSS dimensions (`canvas.clientWidth`/`canvas.clientHeight`) instead of `canvas.width`/`canvas.height` (now in physical pixels). Bug 2: `.desc-box` moved from `top:10px` to `bottom:40px`. All pure ES5.

#### File modificati / Modified files
- `docs/algorithm_animations/crud_operations_algorithm.html`
- `docs/algorithm_animations/database_creation_algorithm.html`
- `docs/algorithm_animations/image_classification_algorithm.html`
- `docs/algorithm_animations/pdf_creation_algorithm.html`
- `docs/algorithm_animations/db_import_export_algorithm.html`

---

## [5.2.1-alpha] - 2026-02-11

### Fix canvas e posizione desc-box in 6 animazioni / Fix canvas and desc-box position in 6 animations

- **IT**: Corretti due bug in 6 file animazione HTML (`order_layer_algorithm.html`, `harris_matrix_algorithm.html`, `media_management_algorithm.html`, `tops_algorithm.html`, `report_ai_algorithm.html`, `package_installation_algorithm.html`). Bug 1: il canvas spariva a dimensioni finestra grandi perche `canvas.width = parent.width * devicePixelRatio` poteva superare il limite browser (~16384px); fix: le dimensioni interne del canvas sono ora limitate a max 4096px per asse con guard `Math.floor`/`Math.max` e fattore `scale` calcolato come `Math.min(dpr, maxPx/w, maxPx/h)`. Bug 2: il box descrizione (`.desc-box`) era posizionato a `top:10px` sovrapponendosi all'animazione canvas; fix: spostato a `bottom:40px` sopra la dots-bar (`bottom:10px`). Tutto in ES5 puro senza `const`/`let`/arrow functions.
- **EN**: Fixed two bugs in 6 animation HTML files (`order_layer_algorithm.html`, `harris_matrix_algorithm.html`, `media_management_algorithm.html`, `tops_algorithm.html`, `report_ai_algorithm.html`, `package_installation_algorithm.html`). Bug 1: canvas disappeared at large window sizes because `canvas.width = parent.width * devicePixelRatio` could exceed browser limits (~16384px); fix: internal canvas dimensions are now capped at max 4096px per axis with `Math.floor`/`Math.max` guards and a `scale` factor computed as `Math.min(dpr, maxPx/w, maxPx/h)`. Bug 2: description box (`.desc-box`) was positioned at `top:10px` overlapping the canvas animation; fix: moved to `bottom:40px` above the dots-bar (`bottom:10px`). All pure ES5, no `const`/`let`/arrow functions.

#### File modificati / Modified files
- `docs/algorithm_animations/order_layer_algorithm.html`
- `docs/algorithm_animations/harris_matrix_algorithm.html`
- `docs/algorithm_animations/media_management_algorithm.html`
- `docs/algorithm_animations/tops_algorithm.html`
- `docs/algorithm_animations/report_ai_algorithm.html`
- `docs/algorithm_animations/package_installation_algorithm.html`

---

## [5.2.0-alpha] - 2026-02-11

### 11 animazioni tecniche algoritmi / 11 Technical Algorithm Animations

- **IT**: Create 11 animazioni HTML5 interattive per documentazione tecnica sviluppatori in `docs/algorithm_animations/`. Ogni animazione visualizza il flusso del codice reale: file sorgente, classi, funzioni, call chain, data flow tra moduli. Include canvas animato con `requestAnimationFrame`, sidebar con Source/Call Stack/Data, event log con formato `[file.py:line] Class.method()`, controlli Auto/Manual, speed 1x/2x/4x, shortcuts tastiera. Pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created 11 interactive HTML5 animations for technical developer documentation in `docs/algorithm_animations/`. Each animation visualizes real code flow: source files, classes, functions, call chains, data flow between modules. Includes animated canvas with `requestAnimationFrame`, sidebar with Source/Call Stack/Data widgets, event log with `[file.py:line] Class.method()` format, Auto/Manual controls, speed 1x/2x/4x, keyboard shortcuts. ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
1. `harris_matrix_algorithm.html` — HarrisMatrix class, Graphviz DOT, transitive reduction, adaptive DPI
2. `order_layer_algorithm.html` — Gis_Time_Controller, field definition, filter, atlas generation
3. `report_ai_algorithm.html` — ReportGenerator, OpenAI streaming, text cleaner, DOCX output
4. `image_classification_algorithm.html` — CLIP/DINOv2/OpenAI embeddings, FAISS index, similarity search
5. `media_management_algorithm.html` — Media_utility, PIL resample, remote storage, CloudinarySync
6. `crud_operations_algorithm.html` — insert/query/update/delete, session_scope, cache TTL
7. `database_creation_algorithm.html` — connection(), engine creation, Spatialite, schema mapper, migrations
8. `db_import_export_algorithm.html` — pg_dump/pg_restore, SQLite backup, Excel/GeoPackage export
9. `pdf_creation_algorithm.html` — ReportLab, NumberedCanvas, table construction, story build
10. `tops_algorithm.html` — Total Open Station CLI, CSV enrichment, coordinate transform, QGIS layers
11. `package_installation_algorithm.html` — requirements parsing, pip install loop, GitHub ZIP, verification

---

## [5.1.4-alpha] - 2026-02-11

### Nuova animazione algoritmo PDF Creation / New PDF Creation Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/pdf_creation_algorithm.html` che documenta il flusso interno del sistema di generazione PDF delle schede US di PyArchInit (`modules/utility/pyarchinit_exp_USsheet_pdf.py`). L'animazione visualizza 5 scenari: (1) Constructor `single_US_pdf_sheet.__init__(data)` con ricezione tupla di 115 campi dall'ORM US, mapping posizionale `self.sito = data[0]` fino a `self.consistenza_p = data[114]`, suddivisione in campi core US (data[0..28]), campi USM muro (data[29..50]), campi ICCD estesi (data[51..114]), e `unzip_rapporti_stratigrafici()` per parsing relazioni (copre, coperto_da, taglia, tagliato_da, riempie, riempito_da, si_appoggia_a, gli_si_appoggia, uguale_a, si_lega_a) con supporto tuple da 2 a 5 elementi e varianti multilingua (it/en/de), (2) Document Setup con registrazione font a livello modulo `pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))` per 4 varianti (Regular/Bold/Italic/BoldItalic) e `registerFontFamily('Cambria')`, `SimpleDocTemplate(f, pagesize=(21*cm, 29*cm), topMargin=10, bottomMargin=20, leftMargin=10, rightMargin=10)`, canvas personalizzato `NumberedCanvas_USsheet` con `_saved_page_states = []` in `__init__`, `showPage()` che salva stato pagina, `save()` che itera tutti gli stati e chiama `draw_page_number(num_pages)`, e `drawRightString(200*mm, 8*mm, "Pag. X di Y")` con Cambria 5pt, piu 5+ varianti ParagraphStyle (`styNormal` 7pt LEFT, `styDescrizione` 7pt JUSTIFIED, `styUnitaTipo` 14pt CENTER, `styTitoloComponenti` 7pt CENTER, `styVerticale` 7pt CENTER leading=8), (3) Table Construction con `create_sheet_archeo3_usm_fields_2()` che costruisce griglia 18 colonne, celle Paragraph con HTML (`<b>LOCALITA</b><br/>` + `escape_html(sito)`), matrice `cell_schema` di 34 righe x 18 colonne con Paragraph objects e placeholder per SPAN, `TableStyle` con `GRID(0,0,-1,-1, 0.3, black)` e ~60 regole SPAN per merge celle (header, relazioni, descrizioni, datazione, campioni, responsabile), `colWidths = (15,30,30,...,30)` per 18 colonne ~485pt totali, `Table(cell_schema, colWidths=colWidths, rowHeights=None, style=table_style)`, e branch US/USM con layout differenti, (4) Image Integration con `Connection().logo_path()` per recupero path logo personalizzato da DB settings con fallback a `$PYARCHINIT_HOME/pyarchinit_DB_folder/logo.jpg`, `Image(logo_path)` ReportLab con scaling proporzionale `drawWidth=2.5*inch, drawHeight=2.5*inch*h/w, hAlign="CENTER"`, logo separato a 2" per header scheda in `create_sheet_archeo3_usm_fields_2()`, `PIL Image` aliasato come `giggino` per ispezione dimensioni con `ImageReader` per compatibilita formato, e pattern `story.append(logo) + Spacer(4,6)` per gap verticale 6pt tra logo e tabella, (5) Build Final PDF con `elements_us_iccd = []` story list, loop `for i in range(len(records)):` su tutti i record US, per-record: `single_US_pdf_sheet(records[i])` + `elements.append(logo)` + `elements.append(Spacer(4,6))` + `elements.append(create_sheet_archeo3_usm_fields_2())` + `elements.append(PageBreak())`, output `filename = "Scheda USICCD.pdf"` aperto in `"wb"`, `doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)` per rendering finale con numerazione automatica pagine, e 7 varianti linguistiche (`build_US_sheets_en/de/fr/es/ar/ca`) con metodi `create_sheet_*()` locale-specifici. Include canvas con pipeline 5 box orizzontale (US ORM Record -> Field Mapping -> Sheet Builder -> Story List -> PDF Output), miniatura pagina PDF animata con logo placeholder, type label US/USM, righe tabella che appaiono progressivamente (LOCALITA, AREA/SAGGIO, DEF. STRATIGRAFICA, RAPPORTI, DESCRIZIONE, INTERPRETAZIONE, DATAZIONE, CAMPIONI, AFFIDABILITA, RESPONSABILE), grid overlay per styling, effetto stack multi-pagina, footer "Pag. X di Y", stage labels colorati (DATA, MAP, BUILD, STORY, PDF), particelle animate lungo il pipeline, e sidebar con Source/Call Stack/Data (Page Size, Font, Tables, Pages). Dati reali da `pyarchinit_exp_USsheet_pdf.py` linee 41-5729: classi `NumberedCanvas_USsheet`, `NumberedCanvas_USindex`, `single_US_pdf_sheet`, `US_index_pdf_sheet`, metodi `build_US_sheets()` e 7 varianti linguistiche. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/pdf_creation_algorithm.html` documenting the internal code flow of PyArchInit's US sheet PDF generation system (`modules/utility/pyarchinit_exp_USsheet_pdf.py`). The animation visualizes 5 scenarios: (1) Constructor `single_US_pdf_sheet.__init__(data)` receiving a tuple of 115 fields from the US ORM entity, positional mapping from `self.sito = data[0]` through `self.consistenza_p = data[114]`, split into core US fields (data[0..28]), USM wall fields (data[29..50]), extended ICCD fields (data[51..114]), and `unzip_rapporti_stratigrafici()` for relationship parsing (copre, coperto_da, taglia, tagliato_da, riempie, riempito_da, si_appoggia_a, gli_si_appoggia, uguale_a, si_lega_a) supporting 2-to-5-element tuples with multilingual variants (it/en/de), (2) Document Setup with module-level font registration `pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))` for 4 variants (Regular/Bold/Italic/BoldItalic) and `registerFontFamily('Cambria')`, `SimpleDocTemplate(f, pagesize=(21*cm, 29*cm), topMargin=10, bottomMargin=20, leftMargin=10, rightMargin=10)`, custom canvas `NumberedCanvas_USsheet` with `_saved_page_states = []` in `__init__`, `showPage()` saving page state, `save()` iterating all states calling `draw_page_number(num_pages)`, and `drawRightString(200*mm, 8*mm, "Pag. X di Y")` in Cambria 5pt, plus 5+ ParagraphStyle variants (`styNormal` 7pt LEFT, `styDescrizione` 7pt JUSTIFIED, `styUnitaTipo` 14pt CENTER, `styTitoloComponenti` 7pt CENTER, `styVerticale` 7pt CENTER leading=8), (3) Table Construction with `create_sheet_archeo3_usm_fields_2()` building an 18-column grid layout, Paragraph cells with HTML (`<b>LOCALITA</b><br/>` + `escape_html(sito)`), `cell_schema` matrix of 34 rows x 18 columns with Paragraph objects and placeholders for SPAN, `TableStyle` with `GRID(0,0,-1,-1, 0.3, black)` and ~60 SPAN rules for cell merging (header, relationships, descriptions, dating, samples, responsible), `colWidths = (15,30,30,...,30)` for 18 columns ~485pt total, `Table(cell_schema, colWidths=colWidths, rowHeights=None, style=table_style)`, and US/USM branch with different layouts, (4) Image Integration with `Connection().logo_path()` for custom logo path retrieval from DB settings with fallback to `$PYARCHINIT_HOME/pyarchinit_DB_folder/logo.jpg`, `Image(logo_path)` ReportLab with proportional scaling `drawWidth=2.5*inch, drawHeight=2.5*inch*h/w, hAlign="CENTER"`, separate 2" logo for sheet header in `create_sheet_archeo3_usm_fields_2()`, `PIL Image` aliased as `giggino` for dimension inspection with `ImageReader` for format compatibility, and `story.append(logo) + Spacer(4,6)` pattern for 6pt vertical gap between logo and table, (5) Build Final PDF with `elements_us_iccd = []` story list, `for i in range(len(records)):` loop over all US records, per-record: `single_US_pdf_sheet(records[i])` + `elements.append(logo)` + `elements.append(Spacer(4,6))` + `elements.append(create_sheet_archeo3_usm_fields_2())` + `elements.append(PageBreak())`, output `filename = "Scheda USICCD.pdf"` opened in `"wb"`, `doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)` for final rendering with automatic page numbering, and 7 language variants (`build_US_sheets_en/de/fr/es/ar/ca`) with locale-specific `create_sheet_*()` methods. Includes canvas with horizontal 5-box pipeline (US ORM Record -> Field Mapping -> Sheet Builder -> Story List -> PDF Output), animated PDF page miniature with logo placeholder, US/USM type label, progressively appearing table rows (LOCALITA, AREA/SAGGIO, DEF. STRATIGRAFICA, RAPPORTI, DESCRIZIONE, INTERPRETAZIONE, DATAZIONE, CAMPIONI, AFFIDABILITA, RESPONSABILE), grid overlay for styling, multi-page stack effect, "Pag. X di Y" footer, colored stage labels (DATA, MAP, BUILD, STORY, PDF), animated particles along the pipeline, and sidebar with Source/Call Stack/Data (Page Size, Font, Tables, Pages). Real data from `pyarchinit_exp_USsheet_pdf.py` lines 41-5729: classes `NumberedCanvas_USsheet`, `NumberedCanvas_USindex`, `single_US_pdf_sheet`, `US_index_pdf_sheet`, methods `build_US_sheets()` and 7 language variants. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/pdf_creation_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.3-alpha] - 2026-02-11

### Nuova animazione algoritmo Database Creation / New Database Creation Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/database_creation_algorithm.html` che documenta il flusso interno del metodo `connection()` di `pyarchinit_db_manager.py` (linee 352-556). L'animazione visualizza 5 scenari: (1) DB Type Detection con `conn_str.find("sqlite")` per branch detection, check host remoti (supabase.com, amazonaws.com, neon.tech, azure.com, heroku.com) e albero decisionale SQLite local / PG remote / PG local, (2) Engine Creation con `create_engine()` differenziato per tipo: SQLite senza pool + `listen(engine, 'connect', load_spatialite)`, PG remote con `pool_size=10, max_overflow=20, pool_timeout=60, pool_recycle=1800, pool_pre_ping=True` e `connect_args` ottimizzati, PG local con `pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600`, (3) Spatialite Loading (Mac) con `dbapi_conn.enable_load_extension(True)`, ricerca path QGIS.app/Contents/MacOS/lib/ e Contents/Frameworks/, fallback homebrew (/opt/homebrew/lib/, /usr/local/lib/), glob pattern per versioni QGIS, `dbapi_conn.load_extension(mod_spatialite)` e `PRAGMA foreign_keys=ON`, (4) Schema Setup & Mapper con `MetaData()`, `sessionmaker(bind=engine, autoflush=False, autocommit=False)`, test connessione `engine.connect()/close()`, `mapper_registry = registry()` da `pyarchinit_db_mapper.py`, e `map_imperatively()` per 40 entita (25 data + 15 GIS + 1 view: US, SITE, TOMBA, STRUTTURA, MEDIA, POTTERY, TMA, PYUS, PYUSM, PYSITO_*, PYQUOTE*, ecc.), (5) Migrations con `_get_db_checked()/_set_db_checked()` guard once-per-session via `sys.modules`, `check_and_update_sqlite_db(db_path)` pre-engine per SQLite, `check_and_update_postgres_db(self)` post-engine per PostgreSQL, `UUIDSupport(engine=engine).update_all_tables()` per 19 tabelle entity_uuid, `ensure_ut_geometry_tables_exist()` solo SQLite, e `return True` a linea 556. Include canvas con pipeline 9 box (ConnStr -> Detection -> Decision diamond -> Engine -> Spatialite/PostGIS -> Extension Search -> Schema+Session -> Mapper 40 entities -> Migrations), griglia entita animata per Sc4, branch labels per Sc1, indicatori fase colorati, particelle animate lungo il pipeline, e sidebar con Source/Call Stack/Data (DB Type, Pool Size, Tables, Migrations). Dati reali da `pyarchinit_db_manager.py:352-556`, `pyarchinit_db_mapper.py:25-246`, `sqlite_db_updater.py:2075`, `postgres_db_updater.py:1915`, `add_uuid_support.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/database_creation_algorithm.html` documenting the internal code flow of `pyarchinit_db_manager.py`'s `connection()` method (lines 352-556). The animation visualizes 5 scenarios: (1) DB Type Detection with `conn_str.find("sqlite")` for branch detection, remote host check (supabase.com, amazonaws.com, neon.tech, azure.com, heroku.com) and decision tree SQLite local / PG remote / PG local, (2) Engine Creation with differentiated `create_engine()`: SQLite with no pool + `listen(engine, 'connect', load_spatialite)`, PG remote with `pool_size=10, max_overflow=20, pool_timeout=60, pool_recycle=1800, pool_pre_ping=True` and optimized `connect_args`, PG local with `pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600`, (3) Spatialite Loading (Mac) with `dbapi_conn.enable_load_extension(True)`, QGIS.app/Contents/MacOS/lib/ and Contents/Frameworks/ path search, homebrew fallback (/opt/homebrew/lib/, /usr/local/lib/), glob patterns for QGIS versions, `dbapi_conn.load_extension(mod_spatialite)` and `PRAGMA foreign_keys=ON`, (4) Schema Setup & Mapper with `MetaData()`, `sessionmaker(bind=engine, autoflush=False, autocommit=False)`, connection test `engine.connect()/close()`, `mapper_registry = registry()` from `pyarchinit_db_mapper.py`, and `map_imperatively()` for 40 entities (25 data + 15 GIS + 1 view: US, SITE, TOMBA, STRUTTURA, MEDIA, POTTERY, TMA, PYUS, PYUSM, PYSITO_*, PYQUOTE*, etc.), (5) Migrations with `_get_db_checked()/_set_db_checked()` once-per-session guard via `sys.modules`, `check_and_update_sqlite_db(db_path)` pre-engine for SQLite, `check_and_update_postgres_db(self)` post-engine for PostgreSQL, `UUIDSupport(engine=engine).update_all_tables()` for 19 tables entity_uuid, `ensure_ut_geometry_tables_exist()` SQLite only, and `return True` at line 556. Includes canvas with 9-box pipeline (ConnStr -> Detection -> Decision diamond -> Engine -> Spatialite/PostGIS -> Extension Search -> Schema+Session -> Mapper 40 entities -> Migrations), animated entity grid for Sc4, branch labels for Sc1, colored phase indicators, animated particles along the pipeline, and sidebar with Source/Call Stack/Data (DB Type, Pool Size, Tables, Migrations). Real data from `pyarchinit_db_manager.py:352-556`, `pyarchinit_db_mapper.py:25-246`, `sqlite_db_updater.py:2075`, `postgres_db_updater.py:1915`, `add_uuid_support.py`. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/database_creation_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.2-alpha] - 2026-02-11

### Nuova animazione algoritmo Report AI / New Report AI Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/report_ai_algorithm.html` che documenta il flusso interno del sistema di generazione report AI di PyArchInit (`modules/utility/report_generator.py`, `modules/utility/report_text_cleaner.py`). L'animazione visualizza 5 scenari: (1) Read Data from DB con `ReportGenerator.read_data_from_db(db_url, table_name)`, `create_engine(db_url)` per PostgreSQL/SQLite, `MetaData(bind=engine)` e `Table(table_name, metadata, autoload_with=engine)` per reflection schema, `sessionmaker(bind=engine)` e `session.query(table).all()` per fetch record, e `return records, columns` con session cleanup, (2) Chunk Data con `ReportGenerator.chunk_data(data, chunk_size)` generator statico, `for i in range(0, len(data), chunk_size)` per iterazione a step, `yield data[i:i + chunk_size]` per rispettare limiti token API, tracking conteggio e dimensione chunk, (3) Generate Report with OpenAI con `generate_report_with_openai(prompt, modello, apikey)`, lazy import `from openai import OpenAI` per evitare conflitti pydantic, `OpenAI(api_key=apikey)` per client init, `client.chat.completions.create(model=modello, messages=[...], stream=True)` per streaming, `for chunk in response:` loop streaming con `chunk.choices[0].delta.content` per estrazione token, `messaggio_combinato += content` per accumulazione, e `ReportTextCleaner.clean_report_text()` prima del return, (4) Clean Report Text con `ReportTextCleaner.clean_report_text(text)`, `text.split('\\n')` per split in linee, `_is_list_item(line, i, lines)` per discriminare liste vere da paragrafi (check lunghezza >80, contesto ELENCO/LISTA, elementi consecutivi, keyword paragrafo), rimozione dash e capitalizzazione per falsi list item, e `prepare_for_docx(cleaned)` per strutturazione in `{paragraphs: [{text, style, level}], has_lists, has_tables}` con parsing heading (#), liste (- /bullet), tabelle (|), (5) Save Report to File con `save_report_to_file(report, file_path)`, doppia pulizia via `clean_report_text()` + `prepare_for_docx()`, `Document()` python-docx, loop `for para_info in prepared['paragraphs']` con dispatch `doc.add_heading(text, level)` / `doc.add_paragraph(text, 'List Bullet')` / `doc.add_paragraph(text)`, styling `run.font.name = 'Cambria'` e `run.font.size = Pt(12)`, e `doc.save(file_path)`. Include canvas con pipeline 5 moduli animata (Database -> Chunker -> OpenAI API -> Text Cleaner -> DOCX Writer), visualizzazione streaming token con cursore lampeggiante, icona DB con cilindro, griglia chunk con progress tracking, pattern regex cleaner animati, icona DOCX con indicatore salvataggio, particelle flusso dati tra moduli, e sidebar con Source/Call Stack/Data widgets. Dati reali da `report_generator.py` (linee 19-131) e `report_text_cleaner.py` (linee 17-302). Segue pattern ES5-strict con helper bezier per ellisse (compatibilita QtWebKit, no ctx.ellipse nativo).
- **EN**: Created new technical developer animation at `docs/algorithm_animations/report_ai_algorithm.html` documenting the internal code flow of PyArchInit's AI report generation system (`modules/utility/report_generator.py`, `modules/utility/report_text_cleaner.py`). The animation visualizes 5 scenarios: (1) Read Data from DB with `ReportGenerator.read_data_from_db(db_url, table_name)`, `create_engine(db_url)` for PostgreSQL/SQLite, `MetaData(bind=engine)` and `Table(table_name, metadata, autoload_with=engine)` for schema reflection, `sessionmaker(bind=engine)` and `session.query(table).all()` for record fetch, and `return records, columns` with session cleanup, (2) Chunk Data with `ReportGenerator.chunk_data(data, chunk_size)` static generator, `for i in range(0, len(data), chunk_size)` step iteration, `yield data[i:i + chunk_size]` to respect API token limits, chunk count and size tracking, (3) Generate Report with OpenAI with `generate_report_with_openai(prompt, modello, apikey)`, lazy import `from openai import OpenAI` to avoid pydantic conflicts, `OpenAI(api_key=apikey)` for client init, `client.chat.completions.create(model=modello, messages=[...], stream=True)` for streaming, `for chunk in response:` streaming loop with `chunk.choices[0].delta.content` for token extraction, `messaggio_combinato += content` for accumulation, and `ReportTextCleaner.clean_report_text()` before return, (4) Clean Report Text with `ReportTextCleaner.clean_report_text(text)`, `text.split('\\n')` for line splitting, `_is_list_item(line, i, lines)` to discriminate true lists from paragraphs (length check >80, ELENCO/LISTA context, consecutive items, paragraph keywords), dash removal and capitalization for false list items, and `prepare_for_docx(cleaned)` for structuring into `{paragraphs: [{text, style, level}], has_lists, has_tables}` with heading (#), list (- /bullet), table (|) parsing, (5) Save Report to File with `save_report_to_file(report, file_path)`, double cleaning via `clean_report_text()` + `prepare_for_docx()`, `Document()` python-docx, `for para_info in prepared['paragraphs']` loop dispatching `doc.add_heading(text, level)` / `doc.add_paragraph(text, 'List Bullet')` / `doc.add_paragraph(text)`, `run.font.name = 'Cambria'` and `run.font.size = Pt(12)` styling, and `doc.save(file_path)`. Includes canvas with animated 5-module pipeline (Database -> Chunker -> OpenAI API -> Text Cleaner -> DOCX Writer), streaming token visualization with blinking cursor, DB icon with cylinder, chunk grid with progress tracking, animated cleaner regex patterns, DOCX icon with save indicator, data flow particles between modules, and sidebar with Source/Call Stack/Data widgets. Real data from `report_generator.py` (lines 19-131) and `report_text_cleaner.py` (lines 17-302). Follows ES5-strict pattern with bezier ellipse helper (QtWebKit compatible, no native ctx.ellipse).

#### File creati / Created files
- `docs/algorithm_animations/report_ai_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.1-alpha] - 2026-02-11

### Nuova animazione algoritmo Image Classification / New Image Classification Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/image_classification_algorithm.html` che documenta il flusso interno del sistema di classificazione immagini e similarita ceramica di PyArchInit (`modules/utility/pottery_similarity/`). L'animazione visualizza 5 scenari: (1) Embedding Models con 4 implementazioni — `CLIPEmbeddingModel` (dim=512, ViT-B/32, locale), `DINOv2EmbeddingModel` (dim=768, ViT-B/14, locale), `OpenAIVisionEmbeddingModel` (dim=1536, text-embedding-3-small, cloud API con prompt specializzati per decorazione/forma/generale), `KhutmCLIPEmbeddingModel` (dim=512, fine-tuned per ceramica archeologica con projection layer addestrato), (2) Generate Embedding con `model.get_embedding(image_path, search_type, auto_crop, edge_preprocessing)`, esecuzione via `subprocess.run()` con `pottery_embedding_runner.py` in virtualenv pulito (rimozione PYTHONHOME/PYTHONPATH), preprocessing opzionale (auto_crop, edge detection, segment_decoration, remove_background), e ritorno `np.ndarray` float32 via file .npy temporaneo, (3) Build FAISS Index con `build_index_for_model(model_name, search_type)`, `db_manager.get_all_pottery_with_images()` per lista immagini, loop per-immagine con `build_full_image_path()` da config THUMB_RESIZE, `model.get_embedding()` + `compute_image_hash()`, e `index_manager.rebuild_index()` che crea `faiss.IndexIDMap(IndexFlatL2(dim))` salvato come .faiss + _mapping.pkl, (4) Search Similar Images con `search_similar(query_image_path, model_name, threshold)`, generazione embedding query, `index_manager.search()` per FAISS nearest neighbor, arricchimento risultati con pottery_id/media_id/similarity/similarity_percent/image_path/pottery_data, e `normalize_similarity()` model-specific (CLIP: [0.5,1.0]->[0,100], DINOv2: [0.4,1.0]->[0,100], OpenAI: lineare), (5) Text-to-Image Search con `search_by_text(text_query, model_name="openai")`, `OpenAI().embeddings.create(model="text-embedding-3-small", input=text_query)` per embedding cross-modale testo-immagine, ricerca FAISS con embedding testuale sullo stesso indice immagini, e risultati con score di similarita. Include canvas con pipeline ML animata (Image -> Preprocessing -> Embedding Model -> Vector Space -> FAISS Index -> Results), visualizzazione dots FAISS con query vector e nearest neighbors, barre similarita percentuali, icone 4 modelli con dimensioni, particelle animate lungo il pipeline, e sidebar con Source/Call Stack/Data widgets. Dati reali da `embedding_models.py`, `similarity_search.py`, `index_manager.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/image_classification_algorithm.html` documenting the internal code flow of PyArchInit's image classification and pottery similarity system (`modules/utility/pottery_similarity/`). The animation visualizes 5 scenarios: (1) Embedding Models with 4 implementations — `CLIPEmbeddingModel` (dim=512, ViT-B/32, local), `DINOv2EmbeddingModel` (dim=768, ViT-B/14, local), `OpenAIVisionEmbeddingModel` (dim=1536, text-embedding-3-small, cloud API with specialized prompts for decoration/shape/general), `KhutmCLIPEmbeddingModel` (dim=512, fine-tuned for archaeological pottery with trained projection layer), (2) Generate Embedding with `model.get_embedding(image_path, search_type, auto_crop, edge_preprocessing)`, execution via `subprocess.run()` with `pottery_embedding_runner.py` in clean virtualenv (removing PYTHONHOME/PYTHONPATH), optional preprocessing (auto_crop, edge detection, segment_decoration, remove_background), and return `np.ndarray` float32 via temporary .npy file, (3) Build FAISS Index with `build_index_for_model(model_name, search_type)`, `db_manager.get_all_pottery_with_images()` for image list, per-image loop with `build_full_image_path()` from config THUMB_RESIZE, `model.get_embedding()` + `compute_image_hash()`, and `index_manager.rebuild_index()` creating `faiss.IndexIDMap(IndexFlatL2(dim))` saved as .faiss + _mapping.pkl, (4) Search Similar Images with `search_similar(query_image_path, model_name, threshold)`, query embedding generation, `index_manager.search()` for FAISS nearest neighbor, result enrichment with pottery_id/media_id/similarity/similarity_percent/image_path/pottery_data, and model-specific `normalize_similarity()` (CLIP: [0.5,1.0]->[0,100], DINOv2: [0.4,1.0]->[0,100], OpenAI: linear), (5) Text-to-Image Search with `search_by_text(text_query, model_name="openai")`, `OpenAI().embeddings.create(model="text-embedding-3-small", input=text_query)` for cross-modal text-to-image embedding, FAISS search with text embedding on the same image index, and results with similarity scores. Includes canvas with animated ML pipeline (Image -> Preprocessing -> Embedding Model -> Vector Space -> FAISS Index -> Results), FAISS dots visualization with query vector and nearest neighbors, percentage similarity bars, 4 model icons with dimensions, animated particles along the pipeline, and sidebar with Source/Call Stack/Data widgets. Real data from `embedding_models.py`, `similarity_search.py`, `index_manager.py`. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/image_classification_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.1.0-alpha] - 2026-02-11

### Nuova animazione algoritmo Harris Matrix / New Harris Matrix Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/harris_matrix_algorithm.html` che documenta il flusso interno del codice dell'algoritmo Harris Matrix di PyArchInit (`modules/utility/pyarchinit_matrix_exp.py`). L'animazione visualizza 5 scenari: (1) Constructor `HarrisMatrix.__init__` con ricezione dei 6 parametri (sequence, negative, conteporene, connection, connection_to, periodi), query `db_manager.query_bool()` per record US, e apertura dialogo `Setting_Matrix().exec()`, (2) export_matrix Graph Creation con `Digraph(engine='dot', strict=False)`, configurazione `rankdir='TB'`, `splines='ortho'`, costruzione `us_rilevanti = set()`, creazione edge lists (elist1/elist2/elist3) per relazioni sequenziali/negative/contemporanee con styling da combo_box del dialogo, (3) Subgraph Clustering Period/Phase con iterazione `self.periodi`, generazione chiavi cluster gerarchiche `cluster_{site}_sito_{area}_per_{period}_fase_{phase}`, subgraph annidati `G.subgraph(name=site_key)` con `rank='same'`, query periodizzazione_table per datazione, e assegnazione nodi US alle fasi con colorazione per tipo (negative_sources/conteporene_sources/default), (4) Transitive Reduction con `G.render()` per file DOT, `subprocess.call(['tred', dot_file])` per riduzione transitiva, `Source.from_file().render()` per grafo ridotto, confronto before/after 15->11 edges, (5) Adaptive DPI Rendering con `dpi_levels = ['150','120','100','75','50']`, loop try/render con fallback automatico a DPI inferiore, check `matrix_error.txt` per errori critici vs warning cicli, e output finale JPG/PNG. Include canvas con grafi DAG Harris Matrix animati (12 nodi US, 15 edges), box periodi colorati, moduli codice (pyarchinit_matrix_exp.py, graphviz, subprocess, db_manager, Setting_Matrix, OS_utility), particelle animate lungo gli edges, indicatore DPI cascade, e confronto visuale riduzione transitiva. Dati reali dal codice sorgente `pyarchinit_matrix_exp.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/harris_matrix_algorithm.html` documenting the internal code flow of PyArchInit's Harris Matrix algorithm (`modules/utility/pyarchinit_matrix_exp.py`). The animation visualizes 5 scenarios: (1) Constructor `HarrisMatrix.__init__` receiving 6 parameters (sequence, negative, conteporene, connection, connection_to, periodi), `db_manager.query_bool()` query for US records, and `Setting_Matrix().exec()` dialog opening, (2) export_matrix Graph Creation with `Digraph(engine='dot', strict=False)`, `rankdir='TB'` and `splines='ortho'` configuration, `us_rilevanti = set()` construction, edge list creation (elist1/elist2/elist3) for sequential/negative/contemporary relationships with styling from dialog combo_boxes, (3) Subgraph Clustering Period/Phase with `self.periodi` iteration, hierarchical cluster key generation `cluster_{site}_sito_{area}_per_{period}_fase_{phase}`, nested subgraphs `G.subgraph(name=site_key)` with `rank='same'`, periodizzazione_table query for dating labels, and US node assignment to phases with type-based coloring (negative_sources/conteporene_sources/default), (4) Transitive Reduction with `G.render()` for DOT file, `subprocess.call(['tred', dot_file])` for transitive reduction, `Source.from_file().render()` for reduced graph, before/after comparison 15->11 edges, (5) Adaptive DPI Rendering with `dpi_levels = ['150','120','100','75','50']`, try/render loop with automatic fallback to lower DPI, `matrix_error.txt` check for critical errors vs cycle warnings, and final JPG/PNG output. Includes canvas with animated Harris Matrix DAG graphs (12 US nodes, 15 edges), colored period boxes, code module boxes (pyarchinit_matrix_exp.py, graphviz, subprocess, db_manager, Setting_Matrix, OS_utility), animated particles along edges, DPI cascade indicator, and transitive reduction visual comparison. Real data from `pyarchinit_matrix_exp.py` source code. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/harris_matrix_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.9-alpha] - 2026-02-11

### Nuova animazione algoritmo Package Installation / New Package Installation Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/package_installation_algorithm.html` che documenta il flusso interno del sistema di installazione pacchetti di PyArchInit (`scripts/modules_installer.py`, `__init__.py`). L'animazione visualizza 5 scenari: (1) Requirements Parsing con `sys.argv[1].split(',')` e fallback a `requirements.txt` con lettura di 39 pacchetti pinned (SQLAlchemy==2.0.45, reportlab==4.4.7, openai==2.15.0, langchain==1.2.3, ecc.), piu lista separata `l = ["totalopenstation"]` per pacchetti GitHub, (2) Platform Detection con `platform.system()` per Windows/Darwin/Linux, `sys.exec_prefix` per path Python, costruzione comando `cmd = "{}/bin/python{}"` e template pip con `--upgrade --user`, (3) Standard Install Loop con `for p in packages:` e `subprocess.call(["python", "-m", "pip", "install", "--upgrade", p, "--user"], shell=True)` per ogni pacchetto, tracking successo/fallimento, contatore progresso, (4) GitHub ZIP Packages con URL hardcoded `https://github.com/enzococca/totalopenstation/zipball/main`, `subprocess.call()` con `shell=True`, try/except KeyError con fallback a `shell=False`, download+extract+build wheel, (5) Verification con `get_missing_packages()` e `importlib.import_module()` per ogni pacchetto, validazione versione, report errori per import falliti, e `QgsSettings().setValue("pyArchInit/dependenciesInstalled", True)`. Include griglia 40 pacchetti (39 pip + 1 GitHub) con color coding (verde=installato, giallo=in corso, rosso=fallito, grigio=pending), pipeline 5-stage animata con frecce e dot pulsante, sidebar con Source/Call Stack/Data widgets, barra progresso e visualizzazione verifica import. Dati reali da `requirements.txt` e `modules_installer.py`. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/package_installation_algorithm.html` documenting the internal code flow of PyArchInit's package installation system (`scripts/modules_installer.py`, `__init__.py`). The animation visualizes 5 scenarios: (1) Requirements Parsing with `sys.argv[1].split(',')` and fallback to `requirements.txt` reading 39 pinned packages (SQLAlchemy==2.0.45, reportlab==4.4.7, openai==2.15.0, langchain==1.2.3, etc.), plus separate `l = ["totalopenstation"]` list for GitHub packages, (2) Platform Detection with `platform.system()` for Windows/Darwin/Linux, `sys.exec_prefix` for Python path, command construction `cmd = "{}/bin/python{}"` and pip template with `--upgrade --user`, (3) Standard Install Loop with `for p in packages:` and `subprocess.call(["python", "-m", "pip", "install", "--upgrade", p, "--user"], shell=True)` per package, success/failure tracking, progress counter, (4) GitHub ZIP Packages with hardcoded URL `https://github.com/enzococca/totalopenstation/zipball/main`, `subprocess.call()` with `shell=True`, try/except KeyError with fallback to `shell=False`, download+extract+build wheel, (5) Verification with `get_missing_packages()` and `importlib.import_module()` per package, version validation, error reporting for failed imports, and `QgsSettings().setValue("pyArchInit/dependenciesInstalled", True)`. Includes 40-package grid (39 pip + 1 GitHub) with color coding (green=installed, yellow=installing, red=failed, gray=pending), animated 5-stage pipeline with arrows and pulsing dot, sidebar with Source/Call Stack/Data widgets, progress bar and import verification visualization. Real data from `requirements.txt` and `modules_installer.py`. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/package_installation_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.8-alpha] - 2026-02-11

### Nuova animazione algoritmo Total Open Station / New Total Open Station Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/tops_algorithm.html` che documenta il flusso interno del codice di integrazione Total Open Station (TOPS) di PyArchInit (`tabs/tops_pyarchinit.py`). L'animazione visualizza 5 scenari: (1) Input File Setup con `setPathinput()` via QFileDialog, selezione formato input (Leica/Topcon/Nikon/Sokkia) e formato output (csv/shp/gpkg), (2) CLI Processing con `subprocess.check_call()` che lancia `totalopenstation-cli-parser.py` con argomenti -i/-o/-f/-t/--overwrite, gestione errori e cattura output, (3) CSV Loading & Enrichment con `loadCsv()` via csv.reader in QStandardItemModel, `convert_csv()` con pandas split point_name su '-', e dialoghi QInputDialog per sito/unita_misura/disegnatore, (4) Coordinate Transformation con `checkBox_coord.isChecked()`, calcolo `p = float(ID_Z) + float(attr_Q)` per quota assoluta, e `feature.setAttribute('quota_q', p)`, (5) QGIS Layer Creation con `QgsVectorLayer("file:///path?type=csv&xField=x&yField=y")`, copia features da sourceLYR a destLYR via `dataProvider().addFeatures()`, `commitChanges()` e cleanup con `removeMapLayer()`. Include sidebar con Source, Call Stack e Data widgets, canvas con icona strumento topografico, griglia coordinate con punti survey animati, diagramma flusso 9 moduli con frecce animate, barra pipeline e visualizzazione trasferimento layer. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/tops_algorithm.html` documenting the internal code flow of PyArchInit's Total Open Station (TOPS) integration (`tabs/tops_pyarchinit.py`). The animation visualizes 5 scenarios: (1) Input File Setup with `setPathinput()` via QFileDialog, input format selection (Leica/Topcon/Nikon/Sokkia) and output format (csv/shp/gpkg), (2) CLI Processing with `subprocess.check_call()` launching `totalopenstation-cli-parser.py` with -i/-o/-f/-t/--overwrite arguments, error handling and output capture, (3) CSV Loading & Enrichment with `loadCsv()` via csv.reader into QStandardItemModel, `convert_csv()` with pandas split point_name on '-', and QInputDialog prompts for site/unit/drawer, (4) Coordinate Transformation with `checkBox_coord.isChecked()`, computing `p = float(ID_Z) + float(attr_Q)` for absolute quota, and `feature.setAttribute('quota_q', p)`, (5) QGIS Layer Creation with `QgsVectorLayer("file:///path?type=csv&xField=x&yField=y")`, feature copy from sourceLYR to destLYR via `dataProvider().addFeatures()`, `commitChanges()` and cleanup with `removeMapLayer()`. Includes sidebar with Source, Call Stack and Data widgets, canvas with survey instrument icon, coordinate grid with animated survey points, 9-module flow diagram with animated arrows, pipeline bar and layer transfer visualization. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/tops_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

---

## [5.0.7-alpha] - 2026-02-11

### Nuova animazione algoritmo DB Import/Export / New DB Import/Export Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/db_import_export_algorithm.html` che documenta il flusso interno del sistema di backup, ripristino ed esportazione dati di PyArchInit (`gui/dbmanagment.py`, `tabs/Excel_export.py`, `tabs/gpkg_export.py`). L'animazione visualizza 4 scenari: (1) Backup PostgreSQL con `BackupThread(QThread)`, pg_dump -Fc -Z9, monitoraggio progresso basato su file size e timeout 300s, (2) Backup SQLite con `shutil.copy()` e naming convention `backup_{name}_{date}.sqlite`, (3) Restore PostgreSQL in 3 step (dropdb/createdb -T template_postgis con fallback CREATE EXTENSION postgis/pg_restore --no-owner --no-acl) + fix sequenze e creazione tabelle utenti, (4) Export Excel/GeoPackage con psycopg2, pandas DataFrame, df.to_excel() e QgsVectorFileWriter.writeAsVectorFormat(). Include sidebar con Source, Call Stack e Data widgets, canvas con icone DB/file, frecce animate con particelle e barra progresso. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/db_import_export_algorithm.html` documenting the internal code flow of PyArchInit's backup, restore and data export system (`gui/dbmanagment.py`, `tabs/Excel_export.py`, `tabs/gpkg_export.py`). The animation visualizes 4 scenarios: (1) PostgreSQL Backup with `BackupThread(QThread)`, pg_dump -Fc -Z9, file-size-based progress monitoring and 300s timeout, (2) SQLite Backup with `shutil.copy()` and naming convention `backup_{name}_{date}.sqlite`, (3) PostgreSQL Restore in 3 steps (dropdb/createdb -T template_postgis with fallback CREATE EXTENSION postgis/pg_restore --no-owner --no-acl) + sequence fixes and user table creation, (4) Excel/GeoPackage Export with psycopg2, pandas DataFrame, df.to_excel() and QgsVectorFileWriter.writeAsVectorFormat(). Includes sidebar with Source, Call Stack and Data widgets, canvas with DB/file icons, animated arrows with particles and progress bar. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/db_import_export_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 4 scenari / complete algorithm animation with canvas, sidebar, event log, 4 scenarios

---

## [5.0.6-alpha] - 2026-02-11

### Nuova animazione algoritmo Order Layer / New Order Layer Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/order_layer_algorithm.html` che documenta il flusso interno del codice del sistema Order Layer di PyArchInit (`Gis_Time_controller.py`). L'animazione visualizza 4 scenari: (1) Field Definition & Schema con definizione colonna in `US_table.py:44`, entity mapping in `US.py:158`, variante import in `US_table_toimp.py:45`, e styling QML con `orderByClause`, (2) Controller Initialization con constructor `__init__()`, layer discovery via `fields().indexFromName('order_layer')`, query `max_num_id()` e configurazione dial/spinbox, (3) Filter Application con `define_order_layer_value()`, modalita cumulativa (`<=`) vs esatta (`=`), e `setSubsetString()` su ogni layer, (4) Atlas Generation con loop `range(0, max+1)`, filtro per-step, export `QgsLayoutExporter.exportToImage()` e completamento. Include sidebar con Source, Call Stack e Data widgets, visualizzazione layer stack animata, diagramma flusso moduli con particelle, e confronto visuale modalita cumulativa/esatta. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/order_layer_algorithm.html` documenting the internal code flow of PyArchInit's Order Layer system (`Gis_Time_controller.py`). The animation visualizes 4 scenarios: (1) Field Definition & Schema with column definition in `US_table.py:44`, entity mapping in `US.py:158`, import variant in `US_table_toimp.py:45`, and QML styling with `orderByClause`, (2) Controller Initialization with `__init__()` constructor, layer discovery via `fields().indexFromName('order_layer')`, `max_num_id()` query and dial/spinbox configuration, (3) Filter Application with `define_order_layer_value()`, cumulative (`<=`) vs exact (`=`) modes, and `setSubsetString()` on each layer, (4) Atlas Generation with `range(0, max+1)` loop, per-step filter, `QgsLayoutExporter.exportToImage()` export and completion. Includes sidebar with Source, Call Stack and Data widgets, animated layer stack visualization, module flow diagram with particles, and visual cumulative/exact mode comparison. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/order_layer_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 4 scenari / complete algorithm animation with canvas, sidebar, event log, 4 scenarios

---

## [5.0.5-alpha] - 2026-02-11

### Nuova animazione algoritmo Media Management / New Media Management Algorithm Animation

- **IT**: Creata nuova animazione tecnica per sviluppatori in `docs/algorithm_animations/media_management_algorithm.html` che documenta il flusso interno del codice di gestione media di PyArchInit (`pyarchinit_media_utility.py`). L'animazione visualizza 5 scenari: (1) Input Detection con `is_remote_path()` e `get_storage_manager()`, (2) Local Thumbnail Resample con `Media_utility` (150x150 @100 DPI), (3) High-Res Resample con `Media_utility_resize` (2008x1417 @300 DPI), (4) Remote Storage Pipeline con download/resample/upload e CloudinarySync (AI tagging + OCR), (5) Video Utility con `shutil.move()`/`shutil.copy()`. Include sidebar con Source, Call Stack e Data widgets aggiornati ad ogni step. Segue pattern ES5-strict per compatibilita QtWebKit.
- **EN**: Created new technical developer animation at `docs/algorithm_animations/media_management_algorithm.html` documenting the internal code flow of PyArchInit's media management system (`pyarchinit_media_utility.py`). The animation visualizes 5 scenarios: (1) Input Detection with `is_remote_path()` and `get_storage_manager()`, (2) Local Thumbnail Resample with `Media_utility` (150x150 @100 DPI), (3) High-Res Resample with `Media_utility_resize` (2008x1417 @300 DPI), (4) Remote Storage Pipeline with download/resample/upload and CloudinarySync (AI tagging + OCR), (5) Video Utility with `shutil.move()`/`shutil.copy()`. Includes sidebar with Source, Call Stack and Data widgets updated at each step. Follows ES5-strict pattern for QtWebKit compatibility.

#### File creati / Created files
- `docs/algorithm_animations/media_management_algorithm.html` — animazione algoritmo completa con canvas, sidebar, event log, 5 scenari / complete algorithm animation with canvas, sidebar, event log, 5 scenarios

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
