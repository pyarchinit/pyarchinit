# PyArchInit - StratiGraph Development Changelog

> Registro dettagliato delle modifiche effettuate durante lo sviluppo dell'integrazione StratiGraph.
> Branch: `Stratigraph_00001`

---

## [5.0.6-alpha] - 2026-03-26

### Corretto / Fixed

- **fix(db): Aggiornamento DB ora esegue SQL statement per statement con autocommit**: L'esecuzione del file SQL di aggiornamento (`update_production_db_safe.sql` e `add_concurrency_fixed.sql`) ora splitta ogni statement e li esegue singolarmente con try/except. Se uno statement fallisce (colonna già esistente, tabella pre-esistente, tipo mismatch), viene saltato e si prosegue col successivo. Errori non critici loggati in QgsMessageLog. Aggiunto `ALTER TABLE ADD COLUMN IF NOT EXISTS` prima degli INSERT in pyarchinit_roles per gestire tabelle pre-esistenti con schema diverso. / **fix(db): DB update now executes SQL statement-by-statement with autocommit**: SQL update file execution now splits each statement and executes them individually with try/except. If a statement fails (column already exists, pre-existing table, type mismatch), it is skipped and execution continues. Non-critical errors logged to QgsMessageLog. Added `ALTER TABLE ADD COLUMN IF NOT EXISTS` before INSERT into pyarchinit_roles to handle pre-existing tables with different schema.

- **fix(geoarchaeo): Errore QVariant float conversion in main_dock.py**: Le feature QGIS restituiscono QVariant NULL che non è convertibile con float(). Protetti tutti i 4 punti di chiamata float(feature[field]) con try/except e filtro str(val) per valori NULL/None. / **fix(geoarchaeo): QVariant float conversion error in main_dock.py**: QGIS features return QVariant NULL which is not convertible with float(). Protected all 4 float(feature[field]) call sites with try/except and str(val) filter for NULL/None values.

- **fix(geoarchaeo): Errore MultiPolygonZ asPoint() in main_dock.py**: La funzione asPoint() fallisce su geometrie Polygon/MultiPolygon. Sostituiti tutti i 4 geom.asPoint() con geom.centroid().asPoint() per supportare qualsiasi tipo di geometria. / **fix(geoarchaeo): MultiPolygonZ asPoint() error in main_dock.py**: The asPoint() function fails on Polygon/MultiPolygon geometries. Replaced all 4 geom.asPoint() with geom.centroid().asPoint() to support any geometry type.

### Aggiornamento / Update

- **feat(ai): Tradotta scheda RAG AI Query in 10 lingue con ThemeManager**: Aggiunto dizionario traduzioni con 35 chiavi (it/en/de/es/fr/ar/ca/ro/pt/el) a RAGQueryDialog. Sostituiti tutti gli string hardcoded italiani in setup_ui. Aggiunto ThemeManager.apply_theme e add_theme_toggle_to_form. / **feat(ai): Translated RAG AI Query dialog to 10 languages with ThemeManager**: Added 35-key translation dict (it/en/de/es/fr/ar/ca/ro/pt/el) to RAGQueryDialog. Replaced all hardcoded Italian strings in setup_ui. Added ThemeManager.apply_theme and add_theme_toggle_to_form.

- **feat(ai): Aggiornati modelli Claude a Sonnet 4.6, fix path API key**: Aggiornato claude-sonnet-4-5-20250929 a claude-sonnet-4-6 in textTosql.py, skatch_gpt_US.py, skatch_gpt_INVMAT.py. Corretto lookup API key: ora cerca prima claude_api_key.txt poi fallback a anthropic_api_key.txt. / **feat(ai): Updated Claude models to Sonnet 4.6, fix API key path**: Updated claude-sonnet-4-5-20250929 to claude-sonnet-4-6 in textTosql.py, skatch_gpt_US.py, skatch_gpt_INVMAT.py. Fixed API key lookup: now tries claude_api_key.txt first, fallback to anthropic_api_key.txt.

### File modificati / Modified files
- `modules/geoarchaeo/gui/main_dock.py` (QVariant + centroid fix)
- `tabs/US_USM.py` (RAG dialog i18n + ThemeManager)
- `modules/utility/textTosql.py` (Claude 4.6 + key path)
- `modules/utility/skatch_gpt_US.py` (Claude 4.6)
- `modules/utility/skatch_gpt_INVMAT.py` (Claude 4.6)

---

## [5.0.5-alpha.3] - 2026-03-24

### Aggiornamento / Update

- **fix(ai): Sostituito `max_tokens` con `max_completion_tokens` nelle chiamate API OpenAI per compatibilità GPT-5.4**: I nuovi modelli GPT-5.4 richiedono il parametro `max_completion_tokens` anziché `max_tokens` nelle chiamate `client.chat.completions.create()` e nei dizionari di parametri per richieste HTTP dirette. Aggiornati 14 punti di chiamata in 6 file. Non modificati: variabili interne (`self.max_tokens`), logica di splitting token, chiamate API Anthropic (che usano correttamente `max_tokens`). File modificati: modules/utility/textTosql.py (2), modules/utility/skatch_gpt_US.py (3), modules/utility/skatch_gpt_INVMAT.py (3), modules/utility/pottery_similarity/embedding_models.py (1), tabs/US_USM.py (4), scripts/translate_ts_complete.py (1). / **fix(ai): Replaced `max_tokens` with `max_completion_tokens` in OpenAI API calls for GPT-5.4 compatibility**: New GPT-5.4 models require the `max_completion_tokens` parameter instead of `max_tokens` in `client.chat.completions.create()` calls and HTTP request parameter dicts. Updated 14 call sites across 6 files. Not modified: internal variables (`self.max_tokens`), token splitting logic, Anthropic API calls (which correctly use `max_tokens`). Files modified: modules/utility/textTosql.py (2), modules/utility/skatch_gpt_US.py (3), modules/utility/skatch_gpt_INVMAT.py (3), modules/utility/pottery_similarity/embedding_models.py (1), tabs/US_USM.py (4), scripts/translate_ts_complete.py (1).

---

## [5.0.5-alpha.2] - 2026-03-24

### Aggiornamento / Update

- **chore(ai): Aggiornati tutti i riferimenti ai modelli OpenAI GPT alla versione marzo 2026**: Sostituiti tutti i modelli GPT obsoleti (gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-4-vision-preview, gpt-3.5-turbo) con le versioni aggiornate (gpt-5.4, gpt-5.4-mini). Le liste dropdown/combobox ora offrono ["gpt-5.4-mini", "gpt-5.4", "gpt-5.3-codex"]. File modificati: tabs/US_USM.py, tabs/Thesaurus.py, tabs/Periodizzazione.py, tabs/Inv_Materiali.py, tabs/pyarchinit_Pottery_mainapp.py, modules/utility/skatch_gpt_US.py, modules/utility/skatch_gpt_INVMAT.py, modules/utility/textTosql.py, modules/utility/pottery_similarity/embedding_models.py, scripts/translate_ts_complete.py, scripts/auto_translate_ts.py. / **chore(ai): Updated all OpenAI GPT model references to March 2026 versions**: Replaced all obsolete GPT models (gpt-4.1, gpt-4.1-mini, gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-4-vision-preview, gpt-3.5-turbo) with updated versions (gpt-5.4, gpt-5.4-mini). Dropdown/combobox lists now offer ["gpt-5.4-mini", "gpt-5.4", "gpt-5.3-codex"]. Files modified: tabs/US_USM.py, tabs/Thesaurus.py, tabs/Periodizzazione.py, tabs/Inv_Materiali.py, tabs/pyarchinit_Pottery_mainapp.py, modules/utility/skatch_gpt_US.py, modules/utility/skatch_gpt_INVMAT.py, modules/utility/textTosql.py, modules/utility/pottery_similarity/embedding_models.py, scripts/translate_ts_complete.py, scripts/auto_translate_ts.py.

---

## [5.0.5-alpha.1] - 2026-03-24

### Corretto / Fixed

- **fix(ui): Corretto overlap tra DB Settings e Path Settings nel Config Dialog**: Le sezioni groupBox_3 (DB Settings) e groupBox_4 (Path Settings) nel primo tab del dialog di configurazione si sovrapponevano quando entrambe espanse. Aggiunto wrapping automatico in QScrollArea tramite `_fix_settings_tab_overlap()` nel costruttore Python che ri-parentizza i widget in un layout verticale scrollabile. / **fix(ui): Fixed overlap between DB Settings and Path Settings in Config Dialog**: The groupBox_3 (DB Settings) and groupBox_4 (Path Settings) sections in the first tab of the configuration dialog overlapped when both expanded. Added automatic QScrollArea wrapping via `_fix_settings_tab_overlap()` in the Python constructor that re-parents widgets into a scrollable vertical layout.

- **fix(i18n): Tradotte etichette e messaggi hardcoded italiani nel Config Dialog in 10 lingue**: Sostituiti oltre 30 messaggi italiani hardcoded (Connessione avvenuta, Errore di connessione, Imposta variabile ambientale, Non dimenticarti di inserire la password, etc.) con chiamate `self.tr()` per supporto i18n. Aggiunto metodo `_translate_ui_labels()` che traduce titoli tab, titoli groupbox, testi pulsanti e tooltip dal caricamento UI italiano. Eliminata la triplicazione di codice per it/de/else in `try_connection()`, `connection_up()`, `save_p()`, `on_pushButton_save_pressed()` e altri metodi. / **fix(i18n): Translated hardcoded Italian labels and messages in Config Dialog to 10 languages**: Replaced 30+ hardcoded Italian messages (Connessione avvenuta, Errore di connessione, Imposta variabile ambientale, Non dimenticarti di inserire la password, etc.) with `self.tr()` calls for i18n support. Added `_translate_ui_labels()` method that translates tab titles, groupbox titles, button texts and tooltips from Italian UI definitions. Eliminated triplicated code for it/de/else in `try_connection()`, `connection_up()`, `save_p()`, `on_pushButton_save_pressed()` and other methods.

- **feat(ui): Modernizzato Info Dialog con interfaccia a schede professionale e supporto 10 lingue**: Riscritto `pyarchinitInfoDialog.py` con QTabWidget a 4 schede (About, System, Dependencies, Links & Support). Tab About: logo, badge versione, sviluppatori, ringraziamenti, licenza. Tab System: tabella con versione plugin, Python, QGIS, Qt, OS, tipo DB e stato connessione con indicatori colorati. Tab Dependencies: tabella 11 dipendenze con stato disponibile/mancante e versione. Tab Links: card con link a sito, GitHub, documentazione, gruppo supporto, email, PayPal donazioni. Aggiunto ThemeManager con apply_theme e toggle. Dizionario I18N completo per 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(ui): Modernized Info Dialog with professional tabbed interface and 10-language support**: Rewrote `pyarchinitInfoDialog.py` with 4-tab QTabWidget (About, System, Dependencies, Links & Support). About tab: logo, version badge, developers, acknowledgments, license. System tab: table with plugin version, Python, QGIS, Qt, OS, DB type and connection status with colored indicators. Dependencies tab: table of 11 dependencies with available/missing status and version. Links tab: cards with links to website, GitHub, documentation, support group, email, PayPal donations. Added ThemeManager with apply_theme and toggle. Complete I18N dictionary for 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el).

---

## [5.0.5-alpha] - 2026-03-24

### Corretto / Fixed

- **fix(charts): Corretto rendering grafici nel tab Analytics di Budget.py - matplotlib come backend primario**: I grafici Plotly nel tab Budget Analytics non venivano visualizzati perche' QWebEngineView spesso non e' disponibile nell'ambiente QGIS. Riscritti i tre metodi di disegno grafici (`draw_category_chart`, `draw_timeline_chart`, `draw_variance_chart`) per usare matplotlib come backend primario con FigureCanvasQTAgg, mantenendo Plotly come fallback opzionale. Grafico a ciambella per categorie con legenda esterna, grafico barre+linea cumulativa per timeline mensile con doppio asse Y, grafico barre orizzontali raggruppate per scostamento con colori verde/rosso. DPI 100, stile professionale, palette colori coerente, titoli multilingua. Aggiunta `_plotly_html_template()` helper e `FuncFormatter` per formattazione assi. / **fix(charts): Fixed chart rendering in Budget.py Analytics tab - matplotlib as primary backend**: Plotly charts in the Budget Analytics tab were not displaying because QWebEngineView is often unavailable in QGIS environments. Rewrote all three chart drawing methods (`draw_category_chart`, `draw_timeline_chart`, `draw_variance_chart`) to use matplotlib as the primary backend with FigureCanvasQTAgg, keeping Plotly as an optional fallback. Donut chart with external legend for categories, bar+cumulative line chart for monthly timeline with dual Y axes, grouped horizontal bar chart for variance with green/red coloring. 100 DPI, professional styling, consistent color palette, language-aware titles. Added `_plotly_html_template()` helper and `FuncFormatter` for axis formatting.

- **fix(ui): Riposizionato pulsante toggle tema in basso a destra per evitare sovrapposizione con toolbar**: Il pulsante toggle tema in `pyarchinit_theme_manager.py` era posizionato in alto a destra (y=10) e si sovrapponeva con barre degli strumenti e label dei form. Spostato in basso a destra (`form.width()-40, form.height()-40`) con aggiornamento dinamico al resize. / **fix(ui): Repositioned theme toggle button to bottom-right to avoid toolbar overlap**: The theme toggle button in `pyarchinit_theme_manager.py` was positioned at top-right (y=10) and overlapped with toolbars and labels in many forms. Moved to bottom-right (`form.width()-40, form.height()-40`) with dynamic repositioning on resize.

- **feat(theme): Aggiunto supporto tema a GPT Sketch e DB Management dialog**: Integrato ThemeManager con `apply_theme()` e `add_theme_toggle_to_form()` in `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py` e `gui/dbmanagment.py` per coerenza visiva con il resto del plugin. / **feat(theme): Added theme support to GPT Sketch and DB Management dialog**: Integrated ThemeManager with `apply_theme()` and `add_theme_toggle_to_form()` in `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py` and `gui/dbmanagment.py` for visual consistency with the rest of the plugin.

### Internazionalizzazione / Internationalization

- **feat(i18n): Tradotto sistema gestione utenti e permessi in 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el)**: Aggiunta internazionalizzazione completa a `gui/user_management_dialog.py` con dizionario TRANSLATIONS contenente 80+ chiavi tradotte per etichette, pulsanti, intestazioni colonne, messaggi di errore/conferma/successo e metodo helper `tr_()`. Refactoring di `modules/db/permission_handler.py` da 3 lingue (it/de/en) a 10, con dizionari classificati per tipo errore (encoding, connection, duplicate, foreign_key, generic) e messaggi permessi per operazione (INSERT/UPDATE/DELETE/SELECT). Completata `_show_cantiere_permission_denied()` in `pyarchinitPlugin.py` aggiungendo le 5 lingue mancanti (ar, ca, ro, pt, el) alle 5 esistenti. / **feat(i18n): Translated user management and permissions system into 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el)**: Added full internationalization to `gui/user_management_dialog.py` with TRANSLATIONS dictionary containing 80+ translated keys for labels, buttons, column headers, error/confirm/success messages and `tr_()` helper method. Refactored `modules/db/permission_handler.py` from 3 languages (it/de/en) to 10, with dictionaries organized by error type (encoding, connection, duplicate, foreign_key, generic) and permission messages per operation (INSERT/UPDATE/DELETE/SELECT). Completed `_show_cantiere_permission_denied()` in `pyarchinitPlugin.py` by adding the 5 missing languages (ar, ca, ro, pt, el) to the existing 5.

### Migliorato / Improved

- **feat(analytics): Aggiunta funzionalità analytics al form Budget.py**: Nuovo tab Analytics con schede riepilogative (totale previsto, totale effettivo, scostamento con colori verde/rosso, barra progresso utilizzo budget), tabella riepilogativa raggruppata per categoria con ordinamento e colorazione, tre grafici Plotly interattivi (donut spesa per categoria, timeline mensile con barre spesa e linea cumulativa previsto, barre orizzontali raggruppate planned vs actual per categoria con colori verde/rosso). Export PDF analytics con ReportLab (tabella sommario + dettaglio per categoria). Pattern QWebEngineView con 3 percorsi import e fallback matplotlib. Supporto completo i18n per 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(analytics): Added analytics functionality to Budget.py form**: New Analytics tab with summary cards (total planned, total actual, variance with green/red coloring, budget usage progress bar), summary table grouped by category with sorting and color-coding, three interactive Plotly charts (category spending donut, monthly timeline with spending bars and cumulative planned line, horizontal grouped bars planned vs actual per category with green/red coloring). Analytics PDF export with ReportLab (summary table + category breakdown). QWebEngineView pattern with 3 import paths and matplotlib fallback. Full i18n support for 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el).

- **feat(pdf): Ridisegnato export PDF professionale per Presenze.py**: Layout landscape A4 full-page con header/footer su ogni pagina (barra blu scuro #1a237e con nome sito, periodo, data generazione), tabella presenze con colori alternati, risoluzione nomi personale da personale_table (non solo ID), sezione riepilogo con ore totali ordinarie/straordinarie, costo totale, giorni lavorati e personale coinvolto. Supporto multilingua completo (it/en/de/es/fr). Font Helvetica coerente. / **feat(pdf): Redesigned professional PDF export for Presenze.py**: Full-page landscape A4 layout with header/footer on every page (dark blue #1a237e bar with site name, period, generation date), attendance table with alternating row colors, personnel name resolution from personale_table (not just IDs), summary section with total regular/overtime hours, total cost, days worked and personnel count. Full multilingual support (it/en/de/es/fr). Consistent Helvetica fonts throughout.

- **feat(pdf): Ridisegnato export PDF dashboard professionale per Cantiere.py**: PDF portrait A4 multi-pagina con pagina titolo (nome sito, anno, data generazione), sezione budget con tabella dettagliata (preventivato/effettivo/differenza con colori verde/rosso) e grafico a barre orizzontali ReportLab (Drawing/Rect/String), tabella personale con 6 colonne, inventario attrezzature con stato colorato, sezione statistiche riepilogative. Header/footer professionali su ogni pagina, supporto multilingua (it/en/de/es/fr). / **feat(pdf): Redesigned professional dashboard PDF export for Cantiere.py**: Multi-page portrait A4 PDF with title page (site name, year, generation date), budget section with detailed table (budgeted/actual/variance with green/red coloring) and horizontal bar chart using ReportLab Drawing primitives (Drawing/Rect/String), personnel table with 6 columns, equipment inventory with color-coded status, summary statistics section. Professional header/footer on every page, multilingual support (it/en/de/es/fr).

### Sicurezza / Security

- **feat(permissions): Collegato sistema permessi ai form gestione cantiere in pyarchinitPlugin.py**: Aggiunti controlli permessi prima dell'apertura dei 5 form cantiere (Cantiere, Personale, Presenze, Attrezzature, Budget). Solo utenti con ruolo 'admin' o 'responsabile' possono accedere. Il controllo e' un soft gate: se il sistema permessi non e' installato, se si usa SQLite, o se si verifica un errore, l'accesso e' consentito per retrocompatibilita'. Aggiunti metodi _check_cantiere_permission() e _show_cantiere_permission_denied() con messaggi in 5 lingue (it/en/de/es/fr). / **feat(permissions): Connected permission system to cantiere management forms in pyarchinitPlugin.py**: Added permission checks before opening the 5 cantiere forms (Cantiere, Personale, Presenze, Attrezzature, Budget). Only users with 'admin' or 'responsabile' role can access. The check is a soft gate: if the permission system tables don't exist, if using SQLite, or if any error occurs, access is allowed for backward compatibility. Added _check_cantiere_permission() and _show_cantiere_permission_denied() helper methods with messages in 5 languages (it/en/de/es/fr).

### Migliorato / Improved

- **feat(chart): Sostituito grafico budget matplotlib con Plotly interattivo in Cantiere.py**: Il metodo draw_budget_chart ora genera un grafico a ciambella Plotly interattivo renderizzato in QWebEngineView, con tooltip in euro, palette professionale Material Design, titoli multilingua (10 lingue) e fallback automatico a matplotlib se Plotly o QWebEngineView non sono disponibili. Refactoring in metodi helper (_clear_chart_layout, _aggregate_budget_by_category, _get_chart_title, _draw_budget_chart_plotly, _draw_budget_chart_matplotlib). / **feat(chart): Replaced matplotlib budget pie chart with interactive Plotly in Cantiere.py**: The draw_budget_chart method now generates an interactive Plotly donut chart rendered in QWebEngineView, with hover tooltips showing euro amounts, a professional Material Design color palette, locale-aware titles (10 languages), and automatic fallback to matplotlib if Plotly or QWebEngineView are unavailable. Refactored into helper methods (_clear_chart_layout, _aggregate_budget_by_category, _get_chart_title, _draw_budget_chart_plotly, _draw_budget_chart_matplotlib).

- **feat(ui): Convertiti campi data da QLineEdit a QDateEdit con popup calendario in 4 schede cantiere**: Sostituiti 10 campi data (QLineEdit) con QDateEdit dotati di calendario popup e formato yyyy-MM-dd nei file UI: Personale.ui (3 campi), Presenze.ui (1 campo), Attrezzature.ui (3 campi), Budget.ui (2 campi). Aggiornati i 4 file Python corrispondenti (Personale.py, Presenze.py, Attrezzature.py, Budget.py) per usare QDate con parsing multi-formato e fallback. / **feat(ui): Converted date fields from QLineEdit to QDateEdit with calendar popup in 4 cantiere forms**: Replaced 10 date fields (QLineEdit) with QDateEdit widgets featuring calendar popup and yyyy-MM-dd display format in UI files: Personale.ui (3 fields), Presenze.ui (1 field), Attrezzature.ui (3 fields), Budget.ui (2 fields). Updated the 4 corresponding Python files (Personale.py, Presenze.py, Attrezzature.py, Budget.py) to use QDate with multi-format parsing and fallback.

### Corretto / Fixed

- **fix(presenze): Collegata comboBox_personale a charge_list() e al cambio sito in Presenze.py**: La comboBox del personale nel form Presenze non si popolava automaticamente. Collegata la comboBox_personale a charge_list() e al segnale di cambio sito, così la lista del personale ora si popola automaticamente in base al sito selezionato. / **fix(presenze): Connected comboBox_personale to charge_list() and site change signal in Presenze.py**: The personnel comboBox in the Attendance form was not auto-populating. Connected comboBox_personale to charge_list() and the site change signal, so the personnel list now auto-populates based on the selected site.

### Migliorato / Improved

- **feat(thesaurus): TABLE_DISPLAY_MAPPING ora multilingua (10 lingue) con 4 tabelle cantiere aggiunte**: Esteso TABLE_DISPLAY_MAPPING in pyarchinit_thesaurus_compatibility.py per supportare 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el) e aggiunte le 4 tabelle del modulo cantiere (personale, presenze, attrezzature, budget). / **feat(thesaurus): TABLE_DISPLAY_MAPPING now multilingual (10 languages) with 4 cantiere tables added**: Extended TABLE_DISPLAY_MAPPING in pyarchinit_thesaurus_compatibility.py to support 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el) and added the 4 cantiere module tables (personnel, attendance, equipment, budget).

- **feat(i18n): Aggiunta traduzione dinamica UI (retranslate_ui) per 4 schede cantiere in 6 lingue (it/en/de/es/fr/ar)**: Implementato il metodo retranslate_ui() nelle 4 schede del modulo cantiere per aggiornare dinamicamente label, placeholder e tooltip al cambio lingua dell'interfaccia, supportando 6 lingue. / **feat(i18n): Added dynamic UI translation (retranslate_ui) for 4 cantiere forms in 6 languages (it/en/de/es/fr/ar)**: Implemented retranslate_ui() method in the 4 cantiere module forms to dynamically update labels, placeholders and tooltips on UI language change, supporting 6 languages.

- **feat(thesaurus): Aggiunto code_descriptions con tooltips per tabelle cantiere (14.1-14.7) in Thesaurus.py**: Aggiunte le definizioni code_descriptions per i codici thesaurus 14.1-14.7 relativi alle tabelle cantiere, con tooltip descrittivi per ogni vocabolario. / **feat(thesaurus): Added code_descriptions with tooltips for cantiere tables (14.1-14.7) in Thesaurus.py**: Added code_descriptions definitions for thesaurus codes 14.1-14.7 related to cantiere tables, with descriptive tooltips for each vocabulary.

### Dati / Data

- **data(db): Inseriti 4 record personale nel DB khutm2 (Al-Khutm)**: Aggiunti i record del personale per il sito Al-Khutm nel database khutm2: Cattani, Gambino, Garbelli, Vinci. / **data(db): Inserted 4 personnel records in khutm2 DB (Al-Khutm)**: Added personnel records for the Al-Khutm site in the khutm2 database: Cattani, Gambino, Garbelli, Vinci.

- **data(thesaurus): Inseriti 130+ record thesaurus nel DB per 7 vocabolari cantiere (14.1-14.7) in IT e en_US**: Aggiunti oltre 130 record nella tabella thesaurus del database per i 7 vocabolari del modulo cantiere (14.1 ruolo, 14.2 tipo_contratto, 14.3 tipo_giornata, 14.4 categoria_attrezzature, 14.5 stato, 14.6 proprietà, 14.7 categoria_budget) nelle lingue italiano e inglese (en_US). / **data(thesaurus): Inserted 130+ thesaurus records in DB for 7 cantiere vocabularies (14.1-14.7) in IT and en_US**: Added over 130 records in the database thesaurus table for the 7 cantiere module vocabularies (14.1 role, 14.2 contract_type, 14.3 day_type, 14.4 equipment_category, 14.5 status, 14.6 ownership, 14.7 budget_category) in Italian and English (en_US).

- **data(db): Aggiornati tutti i campi dei 5 record personale nel DB khutm2 (ruolo, qualifica, email, telefono, contratto, tariffe, IBAN, note)**: Completati i dati di tutti e 5 i record del personale nel database khutm2 con informazioni dettagliate su ruolo, qualifica, email, telefono, tipo di contratto, tariffe orarie, IBAN e note operative. / **data(db): Updated all fields for 5 personnel records in khutm2 DB (role, qualification, email, phone, contract, rates, IBAN, notes)**: Completed data for all 5 personnel records in the khutm2 database with detailed information on role, qualification, email, phone, contract type, hourly rates, IBAN and operational notes.

### Corretto / Fixed

- **fix(presenze): Corretto mismatch widget: lineEdit_turno→comboBox_turno con metodi corretti (currentText, setEditText)**: Il codice Python referenziava lineEdit_turno ma il file UI conteneva comboBox_turno. Aggiornati tutti i riferimenti nel controller Presenze.py per usare comboBox_turno con i metodi corretti currentText() e setEditText(). / **fix(presenze): Fixed widget mismatch: lineEdit_turno→comboBox_turno with correct methods (currentText, setEditText)**: The Python code referenced lineEdit_turno but the UI file contained comboBox_turno. Updated all references in the Presenze.py controller to use comboBox_turno with the correct currentText() and setEditText() methods.

- **fix(budget): Corretto mismatch widget: lineEdit_anno→comboBox_anno e textEdit_descrizione→lineEdit_descrizione**: Il codice Python referenziava widget inesistenti nel file UI. Aggiornati i riferimenti in Budget.py: lineEdit_anno→comboBox_anno (con currentText/setEditText) e textEdit_descrizione→lineEdit_descrizione (con text/setText). / **fix(budget): Fixed widget mismatch: lineEdit_anno→comboBox_anno and textEdit_descrizione→lineEdit_descrizione**: The Python code referenced widgets that did not exist in the UI file. Updated references in Budget.py: lineEdit_anno→comboBox_anno (with currentText/setEditText) and textEdit_descrizione→lineEdit_descrizione (with text/setText).

- **fix(attrezzature): Corretto mismatch widget: lineEdit_nome→comboBox_nome e lineEdit_assegnato_a→comboBox_assegnato_a**: Il codice Python referenziava lineEdit per nome e assegnato_a ma il file UI conteneva comboBox. Aggiornati tutti i riferimenti in Attrezzature.py per usare comboBox_nome e comboBox_assegnato_a con i metodi corretti. / **fix(attrezzature): Fixed widget mismatch: lineEdit_nome→comboBox_nome and lineEdit_assegnato_a→comboBox_assegnato_a**: The Python code referenced lineEdit for nome and assegnato_a but the UI file contained comboBox. Updated all references in Attrezzature.py to use comboBox_nome and comboBox_assegnato_a with the correct methods.

### Migliorato / Improved

- **feat(i18n): Tradotti bottoni rapidi Presenze (Registra Oggi, Ferie, Malattia, Permesso) in 10 lingue**: Aggiunte le traduzioni per i 4 bottoni rapidi del form Presenze in tutte le 10 lingue supportate (it, en, de, es, fr, ar, ca, ro, pt, el). / **feat(i18n): Translated Presenze quick buttons (Register Today, Holiday, Sick Leave, Day Off) in 10 languages**: Added translations for the 4 quick buttons in the Attendance form across all 10 supported languages (it, en, de, es, fr, ar, ca, ro, pt, el).

- **feat(ui): Convertiti tutti i campi data da QLineEdit a QDateEdit con calendario popup in 4 schede (9 campi totali)**: Sostituzione sistematica di tutti i campi data rimasti come QLineEdit con widget QDateEdit dotati di calendario popup e formato yyyy-MM-dd nelle schede Personale, Presenze, Attrezzature e Budget. / **feat(ui): Converted all date fields from QLineEdit to QDateEdit with calendar popup in 4 forms (9 total fields)**: Systematic replacement of all remaining date fields from QLineEdit to QDateEdit widgets with calendar popup and yyyy-MM-dd format in the Personale, Presenze, Attrezzature and Budget forms.

- **feat(i18n): Completate traduzioni retranslate_ui a 10 lingue (aggiunte ca, ro, pt, el)**: Esteso il metodo retranslate_ui() nelle 4 schede cantiere per supportare tutte le 10 lingue, aggiungendo le traduzioni mancanti per catalano, rumeno, portoghese e greco. / **feat(i18n): Completed retranslate_ui translations to 10 languages (added ca, ro, pt, el)**: Extended the retranslate_ui() method in the 4 cantiere forms to support all 10 languages, adding the missing translations for Catalan, Romanian, Portuguese and Greek.

#### File modificati / Modified files
- `tabs/Presenze.py` - fix comboBox_personale charge_list() + site change signal
- `modules/utility/pyarchinit_thesaurus_compatibility.py` - TABLE_DISPLAY_MAPPING multilingual + cantiere tables
- `tabs/Personale.py` - retranslate_ui() dynamic i18n
- `tabs/Presenze.py` - retranslate_ui() dynamic i18n + fix lineEdit_turno→comboBox_turno + i18n quick buttons
- `tabs/Attrezzature.py` - retranslate_ui() dynamic i18n + fix lineEdit_nome→comboBox_nome, lineEdit_assegnato_a→comboBox_assegnato_a
- `tabs/Budget.py` - retranslate_ui() dynamic i18n + fix lineEdit_anno→comboBox_anno, textEdit_descrizione→lineEdit_descrizione
- `modules/utility/pyarchinit_thesaurus.py` - code_descriptions tooltips 14.1-14.7
- `gui/ui/Personale.ui` - QDateEdit conversion
- `gui/ui/Presenze.ui` - QDateEdit conversion
- `gui/ui/Attrezzature.ui` - QDateEdit conversion
- `gui/ui/Budget.ui` - QDateEdit conversion

---

## [5.0.5-alpha] - 2026-02-20

### i18n e Thesaurus / i18n and Thesaurus

- **feat(i18n): Espansione traduzioni da 3 a 10 lingue per le tab Gestione Cantiere**: Aggiunte traduzioni per es, fr, ar, ca, ro, pt, el nelle variabili MSG_BOX_TITLE, STATUS_ITEMS e SORTED_ITEMS per Personale.py, Presenze.py, Attrezzature.py e Budget.py. Le CONVERSION_DICT e SORT_ITEMS erano già complete in 10 lingue. / **feat(i18n): Expand translations from 3 to 10 languages for Site Management tabs**: Added translations for es, fr, ar, ca, ro, pt, el in MSG_BOX_TITLE, STATUS_ITEMS and SORTED_ITEMS variables for Personale.py, Presenze.py, Attrezzature.py and Budget.py. CONVERSION_DICT and SORT_ITEMS were already complete in 10 languages.

- **feat(thesaurus): Nuovo thesaurus codici 14.1-14.7 per Gestione Cantiere (~470 record)**: Creati 7 codici tipologia_sigla per le tabelle cantiere: 14.1 ruolo (10 valori), 14.2 tipo_contratto (6), 14.3 tipo_giornata (6), 14.4 categoria_attrezzature (7), 14.5 stato (4), 14.6 proprietà (4), 14.7 categoria_budget (7), ciascuno in 10 lingue. Seed implementato sia in sqlite_db_updater.py che postgres_db_updater.py con guard idempotente. / **feat(thesaurus): New thesaurus codes 14.1-14.7 for Site Management (~470 records)**: Created 7 tipologia_sigla codes for cantiere tables: 14.1 role (10 values), 14.2 contract_type (6), 14.3 day_type (6), 14.4 equipment_category (7), 14.5 status (4), 14.6 ownership (4), 14.7 budget_category (7), each in 10 languages. Seed implemented in both sqlite_db_updater.py and postgres_db_updater.py with idempotent guard.

- **feat(tabs): Integrazione thesaurus nei combobox delle tab Cantiere**: I combobox ruolo/tipo_contratto (Personale), tipo_giornata (Presenze), categoria/stato/proprietà (Attrezzature), categoria (Budget) ora si popolano dal thesaurus tramite query_thesaurus_batch() nella lingua corrente dell'interfaccia. Aggiunta mappa LANG_TO_THESAURUS in ogni tab. Aggiornato pyarchinit_thesaurus_compatibility.py con mapping per le 4 tabelle cantiere. / **feat(tabs): Thesaurus integration in Site Management comboboxes**: Comboboxes for role/contract_type (Personnel), day_type (Attendance), category/status/ownership (Equipment), category (Budget) now populate from the thesaurus via query_thesaurus_batch() in the current UI language. Added LANG_TO_THESAURUS mapping in each tab. Updated pyarchinit_thesaurus_compatibility.py with mapping for the 4 cantiere tables.

#### File modificati / Modified files
- `tabs/Personale.py` - i18n expansion + thesaurus charge_list()
- `tabs/Presenze.py` - i18n expansion + thesaurus charge_list()
- `tabs/Attrezzature.py` - i18n expansion + thesaurus charge_list()
- `tabs/Budget.py` - i18n expansion + thesaurus charge_list()
- `modules/db/sqlite_db_updater.py` - update_site_management_thesaurus()
- `modules/db/postgres_db_updater.py` - update_site_management_thesaurus()
- `modules/utility/pyarchinit_thesaurus_compatibility.py` - cantiere table mappings

### Documentazione / Documentation

- **docs(tutorials): Tutorial spagnolo per il modulo Gestion de Obra (35_gestion_obra.md)**: Creato tutorial completo in spagnolo per il modulo Gestione Cantiere (~276 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Panel de Obra/Dashboard (selettori sito/anno, riepilogo budget con barra progresso codificata per colori e grafico a torta, riepilogo personale con presenti/vacaciones/baja e totali mensili ore/costi, riepilogo attrezzature con alert manutenzione, computo metrico con differenza DEM e DEM+poligono), Formulario de Personal (9 campi), Formulario de Asistencia (8 campi con tipi giornata: laboral/vacaciones/baja/permiso), Formulario de Equipamiento (11 campi con stati: en_uso/mantenimiento/fuera_servicio), Formulario de Presupuesto (7 campi con 7 categorie di spesa), flusso di lavoro operativo (configurazione iniziale e gestione giornaliera), FAQ, note tecniche con tabelle database e file sorgente. / **docs(tutorials): Spanish tutorial for Site Management module (35_gestion_obra.md)**: Created comprehensive Spanish tutorial for the Gestione Cantiere module (~276 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Panel de Obra/Dashboard (site/year selectors, budget summary with color-coded progress bar and pie chart, personnel summary with present/vacation/sick and monthly hour/cost totals, equipment summary with maintenance alerts, computo metrico with DEM difference and DEM+polygon), Personnel form (9 fields), Attendance form (8 fields with day types: laboral/vacaciones/baja/permiso), Equipment form (11 fields with states: en_uso/mantenimiento/fuera_servicio), Budget form (7 fields with 7 expense categories), operational workflow (initial setup and daily management), FAQ, technical notes with database tables and source files.

#### File creati / Created files
- `docs/tutorials/es/35_gestion_obra.md`

- **docs(tutorials): Tutorial greco moderno per il modulo Διαχειριση Εργοταξιου (35_διαχειριση_εργοταξιου.md)**: Creato tutorial completo in greco moderno per il modulo Gestione Cantiere (~495 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Πινακας Εργοταξιου/Dashboard (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione Computo Metrico con calcolo differenza DEM e DEM+poligono, storico), Φορμα Προσωπικου (9 campi), Φορμα Παρουσιων (8 campi con tabella tipo_giornata), Φορμα Εξοπλισμου (11 campi con tabella stato), Φορμα Προυπολογισμου (7 campi con categorie tipiche), flusso di lavoro operativo (6 passi), FAQ (7 domande), note tecniche con file sorgente e tabelle database. / **docs(tutorials): Modern Greek tutorial for Site Management module (35_διαχειριση_εργοταξιου.md)**: Created comprehensive Modern Greek tutorial for the Gestione Cantiere module (~495 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Πινακας Εργοταξιου/Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, Computo Metrico section with DEM difference and DEM+polygon calculation, history), Personnel form (9 fields), Attendance form (8 fields with day type table), Equipment form (11 fields with status table), Budget form (7 fields with typical categories), operational workflow (6 steps), FAQ (7 questions), technical notes with source files and database tables.

#### File creati / Created files
- `docs/tutorials/el/35_διαχειριση_εργοταξιου.md`

- **docs(tutorials): Tutorial portoghese europeo per il modulo Gestao de Obra (35_gestao_obra.md)**: Creato tutorial completo in portoghese europeo per il modulo Gestione Cantiere (~454 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone) e menu estensione, Painel de Obra/Dashboard (selettori sito/anno, riepilogo orcamento con barra progresso e grafico a torta, riepilogo pessoal con presenti/ferias/baixa e totali mensili ore/costi, riepilogo equipamentos con alert manutencao, computo metrico con differenza DEM e DEM+poligono e storico), Ficha de Pessoal (9 campi), Ficha de Presencas (8 campi con tipi di giornata), Ficha de Equipamentos (11 campi con stati), Ficha de Orcamento (7 campi con categorie suggerite), flussi di lavoro operativi (configurazione iniziale, routine giornaliera, aggiornamento budget, computo volumi), FAQ (7 domande), note tecniche con tabelle DB e file sorgente. / **docs(tutorials): European Portuguese tutorial for Site Management module (35_gestao_obra.md)**: Created comprehensive European Portuguese tutorial for the Gestione Cantiere module (~454 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons) and plugin menu, Painel de Obra/Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly hour/cost totals, equipment summary with maintenance alerts, computo metric with DEM difference and DEM+polygon and history), Personnel form (9 fields), Attendance form (8 fields with day types), Equipment form (11 fields with states), Budget form (7 fields with suggested categories), operational workflows (initial setup, daily routine, budget update, volume computation), FAQ (7 questions), technical notes with DB tables and source files.

#### File creati / Created files
- `docs/tutorials/pt/35_gestao_obra.md`

- **docs(tutorials): Tutorial arabo per il modulo إدارة الموقع (35_إدارة_الموقع.md)**: Creato tutorial completo in arabo per il modulo Gestione Cantiere (~517 righe). Copre: indice con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Dashboard/لوحة القيادة (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione computo metrico con calcolo differenza DEM e DEM+poligono, storico computi), Scheda Personale/الموظفون (18 campi), Scheda Presenze/الحضور (12 campi con tipi giornata), Scheda Attrezzature/المعدات (16 campi con stati), Scheda Budget/الميزانية (11 campi con categorie spesa), barra strumenti DBMS, flussi di lavoro operativi (setup iniziale + lavoro quotidiano + calcolo quantità), FAQ (7 domande), note tecniche con tabelle database. / **docs(tutorials): Arabic tutorial for Site Management module (35_إدارة_الموقع.md)**: Created comprehensive Arabic tutorial for the Gestione Cantiere module (~517 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, quantity surveying section with DEM difference and DEM+polygon, computo history), Personnel form (18 fields), Attendance form (12 fields with day types), Equipment form (16 fields with statuses), Budget form (11 fields with expense categories), DBMS toolbar, operational workflows (initial setup + daily work + quantity calculation), FAQ (7 questions), technical notes with database tables.

#### File creati / Created files
- `docs/tutorials/ar/35_إدارة_الموقع.md`

- **docs(tutorials): Tutorial tedesco per il modulo Baustellenverwaltung (35_baustellenverwaltung.md)**: Creato tutorial completo in tedesco per il modulo Gestione Cantiere (~300 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 componenti, accesso dalla barra strumenti (5 icone), Baustellen-Dashboard (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione Massenberechnung con calcolo differenza DEM e DEM+poligono, storico computi), Personalformular (18 campi), Anwesenheitsformular (12 campi con tabella tipo_giornata), Ausruestungsformular (16 campi con tabella stato), Budgetformular (11 campi), flusso di lavoro operativo, FAQ, risoluzione problemi, note tecniche con file sorgente e tabelle database. / **docs(tutorials): German tutorial for Site Management module (35_baustellenverwaltung.md)**: Created comprehensive German tutorial for the Gestione Cantiere module (~300 lines). Covers: TOC with anchors, module introduction with 5-component table, toolbar access (5 icons), Baustellen-Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, Massenberechnung section with DEM difference and DEM+polygon calculation, computo history), Personnel form (18 fields), Attendance form (12 fields with tipo_giornata table), Equipment form (16 fields with stato table), Budget form (11 fields), operational workflow, FAQ, troubleshooting, technical notes with source files and database tables.

#### File creati / Created files
- `docs/tutorials/de/35_baustellenverwaltung.md`

- **docs(tutorials): Tutorial catalano per il modulo Gestio d'Obra (35_gestio_obra.md)**: Creato tutorial completo in catalano per il modulo Gestione Cantiere (~567 righe). Copre: indice con ancoraggi, introduzione al modulo, accesso dalla barra strumenti (5 icone), Tauler d'Obra/Dashboard (selettori lloc/any, riepilogo pressupost con barra di avanzamento e grafico a torta, riepilogo personale con presents/vacances/malaltia e totali mensili, riepilogo equipament con alert manteniment, sezione comput metric con calcolo differenza DEM e DEM+poligon, storico computi), Fitxa de Personal (18 campi), Fitxa d'Assistencia (12 campi), Fitxa d'Equipament (16 campi), Fitxa de Pressupost (11 campi), barra d'eines DBMS condivisa, flussi di lavoro operativi, FAQ, note tecniche. / **docs(tutorials): Catalan tutorial for Site Management module (35_gestio_obra.md)**: Created comprehensive Catalan tutorial for the Gestione Cantiere module (~567 lines). Covers: TOC with anchors, module introduction, toolbar access (5 icons), Tauler d'Obra dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/vacation/sick and monthly totals, equipment summary with maintenance alerts, computo metric section with DEM difference and DEM+polygon, computo history), Personnel form (18 fields), Attendance form (12 fields), Equipment form (16 fields), Budget form (11 fields), shared DBMS toolbar, operational workflows, FAQ, technical notes.

#### File creati / Created files
- `docs/tutorials/ca/35_gestio_obra.md`

- **docs(tutorials): Tutorial romeno per il modulo Gestiune Santier (35_gestiune_santier.md)**: Creato tutorial completo in romeno per il modulo Gestione Cantiere (~457 righe). Copre: sommario con ancoraggi, introduzione al modulo con tabella dei 5 formulari, accesso dalla barra strumenti (5 icone), Panou Santier/Dashboard (selettori sito/anno, riepilogo budget con barra progresso e grafico a torta, riepilogo personale con presenti/concediu/medical e totali mensili ore/costi, riepilogo attrezzature con alert manutenzione), Fisa Personal (18 campi), Fisa Prezente (12 campi con flusso tipico), Fisa Echipamente (16 campi con alert manutenzione), Fisa Buget (11 campi con categorie tipiche), Computo Metric (differenza DEM e DEM+Poligon, storico), flusso di lavoro operativo (configurazione iniziale, operazioni giornaliere, monitoraggio periodico), depanare, FAQ, note tecniche. / **docs(tutorials): Romanian tutorial for Site Management module (35_gestiune_santier.md)**: Created comprehensive Romanian tutorial for the Gestione Cantiere module (~457 lines). Covers: TOC with anchors, module introduction with 5-form table, toolbar access (5 icons), Panou Santier/Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary with present/leave/medical and monthly hour/cost totals, equipment summary with maintenance alerts), Personnel form (18 fields), Attendance form (12 fields with typical workflow), Equipment form (16 fields with maintenance alerts), Budget form (11 fields with typical categories), Computo Metric (DEM difference and DEM+Polygon, history), operational workflow (initial setup, daily operations, periodic monitoring), troubleshooting, FAQ, technical notes.

#### File creati / Created files
- `docs/tutorials/ro/35_gestiune_santier.md`

- **docs(tutorials): Tutorial francese per il modulo Gestion de Chantier (35_gestion_chantier.md)**: Creato tutorial completo in francese per il modulo Gestione Cantiere (~480 righe). Copre: sommario con ancoraggi, introduzione al modulo, accesso dalla barra strumenti (5 icone), Tableau de Bord (selettori sito/anno, riepilogo budget con barra di avanzamento e grafico a torta, riepilogo personale con presenti/ferie/malattia e totali mensili, riepilogo attrezzature con alert manutenzione, sezione metrages con calcolo differenza DEM e DEM+poligono, storico computi), Fiche Personnel (18 campi), Fiche Presences (12 campi), Fiche Equipements (16 campi), Fiche Budget (11 campi), flussi di lavoro operativi, FAQ, note tecniche. / **docs(tutorials): French tutorial for Site Management module (35_gestion_chantier.md)**: Created comprehensive French tutorial for the Gestione Cantiere module (~480 lines). Covers: TOC with anchors, module introduction, toolbar access (5 icons), Dashboard (site/year selectors, budget summary with progress bar and pie chart, personnel summary, equipment summary with maintenance alerts, metrages section with DEM difference and DEM+polygon, computo history), Personnel form (18 fields), Attendance form (12 fields), Equipment form (16 fields), Budget form (11 fields), operational workflows, FAQ, technical notes.

#### File creati / Created files
- `docs/tutorials/fr/35_gestion_chantier.md`

- **docs: Tutorial inglese per il modulo Site Management (35_site_management.md)**: Creato tutorial completo in inglese per il modulo Gestione Cantiere. Il tutorial copre tutte e 5 le componenti del modulo: Dashboard Cantiere (riepilogo budget con grafico a torta, riepilogo personale, riepilogo attrezzature con alert manutenzione, computo metrico con calcolo differenza DEM e statistiche zonali), form CRUD Personale (18 campi inclusi ruolo, qualifica, tariffe, contratto), form CRUD Presenze (12 campi inclusi tipo giornata, ore ordinarie/straordinario, turno, area di lavoro), form CRUD Attrezzature (17 campi inclusi stato, costi, date manutenzione), form CRUD Budget (11 campi inclusi importo previsto/effettivo, fornitore, fattura). Include: indice con ancore, workflow operativo completo, sezione FAQ, note tecniche con tabelle database e file sorgente. / **docs: English tutorial for the Site Management module (35_site_management.md)**: Created comprehensive English tutorial for the Gestione Cantiere module. The tutorial covers all 5 module components: Site Dashboard (budget summary with pie chart, personnel summary, equipment summary with maintenance alerts, computo metrico with DEM difference calculation and zonal statistics), Personnel CRUD form (18 fields including role, qualification, rates, contract), Attendance CRUD form (12 fields including day type, regular/overtime hours, shift, work area), Equipment CRUD form (17 fields including status, costs, maintenance dates), Budget CRUD form (11 fields including estimated/actual amounts, supplier, invoice). Includes: table of contents with anchors, complete operational workflow, FAQ section, technical notes with database tables and source files.

#### File creati / Created files
- `docs/tutorials/en/35_site_management.md`

---

## [5.0.5-alpha] - 2026-02-20

### Corretto / Fixed

- **fix(db): Autenticazione password fallita nelle funzioni admin (#660)** (commit `4bdff5cb`): In SQLAlchemy 2.0, `str(engine.url)` maschera le password come `***`, causando il fallimento di `psycopg2.connect()` nelle funzioni `apply_concurrency_system()` e `update_database_schema()`. Corretto accedendo direttamente agli attributi dell'oggetto `engine.url` (host, port, database, username, password) invece di convertire l'URL in stringa. / **fix(db): Resolve password auth failure in admin functions (#660)** (commit `4bdff5cb`): In SQLAlchemy 2.0, `str(engine.url)` masks passwords as `***`, causing `psycopg2.connect()` to fail in `apply_concurrency_system()` and `update_database_schema()`. Fixed by accessing `engine.url` object attributes (host, port, database, username, password) directly instead of converting the URL to a string.

- **fix(db): SQLite updater non creava le nuove tabelle Site Management (#660)** (commit `9d053ed9`): Aggiunti controlli `needs_update()` per 5 nuove tabelle del modulo Site Management (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) e per `inventario_lapidei_table`. Corretto `test2()` per eseguire solo su SQLite e chiudere correttamente le connessioni. Aggiunto metodo `apply_sito_set()` alla dashboard Cantiere. / **fix(db): SQLite updater not creating new site management tables (#660)** (commit `9d053ed9`): Added `needs_update()` checks for 5 new Site Management module tables (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) and for `inventario_lapidei_table`. Fixed `test2()` to only run for SQLite and properly close connections. Added `apply_sito_set()` method to the Cantiere dashboard.

- **fix(db): Aggiunta inventario_lapidei_table e fix stringa connessione DB_update (#660)** (commit `6223cb73`): Usato `render_as_string(hide_password=False)` per ottenere la stringa di connessione corretta in DB_update, evitando il mascheramento della password. Creata `inventario_lapidei_table` sia nel SQLite updater che nel PostgreSQL updater: la tabella era referenziata nelle viste SQL del sistema di concorrenza ma non era mai stata creata, causando errori durante `apply_concurrency_system()`. / **fix(db): Add inventario_lapidei_table and fix DB_update password auth (#660)** (commit `6223cb73`): Used `render_as_string(hide_password=False)` to get the correct connection string in DB_update, avoiding password masking. Created `inventario_lapidei_table` in both SQLite and PostgreSQL updaters: the table was referenced in concurrency system SQL views but had never been created, causing errors during `apply_concurrency_system()`.

- **fix(db): Backport correzioni password auth su branch qt6-migration (#660)** (commit `9a5c7dae` su `feature/qt6-migration`): Portate le stesse correzioni per l'autenticazione password (`engine.url` attributes e `render_as_string(hide_password=False)`) e la creazione di `inventario_lapidei_table` sul branch `feature/qt6-migration`, senza le tabelle Site Management. / **fix(db): Backport password auth fixes to qt6-migration branch (#660)** (commit `9a5c7dae` on `feature/qt6-migration`): Backported the same password authentication fixes (`engine.url` attributes and `render_as_string(hide_password=False)`) and `inventario_lapidei_table` creation to the `feature/qt6-migration` branch, without the Site Management tables.

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (fix `str(engine.url)` password masking, `render_as_string(hide_password=False)`, attributi `engine.url` per psycopg2)
- `modules/db/sqlite_db_updater.py` (aggiunti `needs_update()` per 6 tabelle, creazione `inventario_lapidei_table`)
- `modules/db/postgres_db_updater.py` (creazione `inventario_lapidei_table`)
- `tabs/Cantiere.py` (aggiunto metodo `apply_sito_set()`)

---

## [5.0.5-alpha] - 2026-02-20

### Aggiunto / Added
- **Dashboard Controller Cantiere (Cantiere.py)**: Creato il controller dashboard `tabs/Cantiere.py` che aggrega i dati dalle 4 tabelle del modulo Site Management (Budget, Presenze, Attrezzature, Computo Metrico). Non e' un form CRUD standard ma una vista di aggregazione/dashboard. Include: riepilogo budget con progress bar e grafico a torta matplotlib, riepilogo personale presente oggi con totali mensili ore/costi, riepilogo attrezzature con alert scadenze manutenzione, calcolo computo metrico GIS (differenza DEM e DEM su poligono) tramite QgsRasterCalculator e QgsZonalStatistics, storico computi in QTableWidget, salvataggio risultati calcolo nel database. Supporto i18n per 10 lingue nei titoli. Segue il pattern di connessione DB singleton da `Personale.py`. / Created the dashboard controller `tabs/Cantiere.py` that aggregates data from the 4 Site Management module tables (Budget, Presenze, Attrezzature, Computo Metrico). This is NOT a standard CRUD form but an aggregation/dashboard view. Includes: budget summary with progress bar and matplotlib pie chart, today's personnel summary with monthly hour/cost totals, equipment summary with overdue maintenance alerts, GIS computo metrico calculation (DEM difference and DEM over polygon) via QgsRasterCalculator and QgsZonalStatistics, computo history in QTableWidget, saving calculation results to database. i18n support for 10 languages in titles. Follows the DB singleton connection pattern from `Personale.py`.

#### File creati / Created files
- `tabs/Cantiere.py`

- **Controller CRUD Tab per Site Management**: Creati 4 controller tab Python per il modulo Site Management: `Personale.py`, `Presenze.py`, `Attrezzature.py`, `Budget.py`. Ogni controller segue esattamente il pattern di `Periodizzazione.py` con: supporto i18n per 10 lingue (it, en, de, es, fr, ar, ca, ro, pt, el), integrazione ThemeManager, operazioni CRUD complete via `get_db_manager()` singleton, navigazione record, ricerca/ordinamento, gestione sito, metodi `fill_fields`/`empty_fields`/`insert_new_rec`/`update_record`. Presenze.py include metodi extra `calculate_hours()` e `calculate_cost()`. Attrezzature.py include `check_maintenance_alert()` per avvisi scadenza manutenzione. / Created 4 Python tab controllers for the Site Management module: `Personale.py`, `Presenze.py`, `Attrezzature.py`, `Budget.py`. Each controller follows the exact `Periodizzazione.py` pattern with: i18n support for 10 languages (it, en, de, es, fr, ar, ca, ro, pt, el), ThemeManager integration, full CRUD operations via `get_db_manager()` singleton, record navigation, search/sort, site management, `fill_fields`/`empty_fields`/`insert_new_rec`/`update_record` methods. Presenze.py includes extra `calculate_hours()` and `calculate_cost()` methods. Attrezzature.py includes `check_maintenance_alert()` for maintenance due date warnings.

#### File creati / Created files
- `tabs/Personale.py`
- `tabs/Presenze.py`
- `tabs/Attrezzature.py`
- `tabs/Budget.py`

- **Database Updaters per Site Management**: Aggiunti metodi CREATE TABLE per le 5 nuove tabelle (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) sia nel SQLite updater che nel PostgreSQL updater. I database esistenti riceveranno le nuove tabelle automaticamente alla prossima connessione. Il SQLite updater usa `self.cursor.execute()` con `table_exists()` guard, il PostgreSQL updater usa il pattern `with self.db_manager.engine.connect()` con `sqlalchemy.text()` e `COMMIT` esplicito. / Added CREATE TABLE methods for the 5 new tables (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) to both the SQLite and PostgreSQL database updaters. Existing databases will receive the new tables automatically on next connection. The SQLite updater uses `self.cursor.execute()` with `table_exists()` guard; the PostgreSQL updater uses the `with self.db_manager.engine.connect()` pattern with `sqlalchemy.text()` and explicit `COMMIT`.

#### File modificati / Modified files
- `modules/db/sqlite_db_updater.py`
- `modules/db/postgres_db_updater.py`

- **Mapper registration + DB Manager per Site Management**: Registrate le 5 nuove entita (PERSONALE, PRESENZE, ATTREZZATURE, BUDGET, COMPUTO_METRICO) nel sistema di mapping SQLAlchemy e nel DB manager. Aggiunti import entita e strutture, chiamate `mapper()`, 5 metodi `insert_*_values()`, e voci nei dizionari `table_classes` di `query_bool` e `group_by`. / Registered the 5 new entity classes (PERSONALE, PRESENZE, ATTREZZATURE, BUDGET, COMPUTO_METRICO) in the SQLAlchemy mapping system and DB manager. Added entity and structure imports, `mapper()` calls, 5 `insert_*_values()` methods, and entries in the `table_classes` dictionaries of `query_bool` and `group_by`.

#### File modificati / Modified files
- `modules/db/pyarchinit_db_mapper.py`
- `modules/db/pyarchinit_db_manager.py`

- **Strutture tabelle Site Management**: Creati 10 file di definizione tabelle per il modulo Site Management (5 in `modules/db/structures/` e 5 in `modules/db/structures_metadata/`). Le tabelle coprono: personale (`personale_table`), presenze (`presenze_table`), attrezzature (`attrezzature_table`), budget (`budget_table`) e computo metrico (`computo_metrico_table`). Le strutture seguono i pattern esistenti del progetto (Pattern A con `MetaData()` a livello di classe e Pattern B con `@classmethod define_table`). / Created 10 table definition files for the Site Management module (5 in `modules/db/structures/` and 5 in `modules/db/structures_metadata/`). Tables cover: personnel (`personale_table`), attendance (`presenze_table`), equipment (`attrezzature_table`), budget (`budget_table`) and metric computation (`computo_metrico_table`). Structures follow existing project patterns (Pattern A with class-level `MetaData()` and Pattern B with `@classmethod define_table`).

#### File creati / Created files
- `modules/db/structures/Personale_table.py`
- `modules/db/structures/Presenze_table.py`
- `modules/db/structures/Attrezzature_table.py`
- `modules/db/structures/Budget_table.py`
- `modules/db/structures/Computo_metrico_table.py`
- `modules/db/structures_metadata/Personale_table.py`
- `modules/db/structures_metadata/Presenze_table.py`
- `modules/db/structures_metadata/Attrezzature_table.py`
- `modules/db/structures_metadata/Budget_table.py`
- `modules/db/structures_metadata/Computo_metrico_table.py`

---

## [5.0.5-alpha] - 2026-02-19

### Corretto / Fixed
- **Import geometrie PostgreSQL #659**: La clausola `ON CONFLICT` veniva aggiunta dopo `RETURNING` nella SQL generata, causando un `SyntaxError`. Corretto posizionando `ON CONFLICT` prima di `RETURNING` in tutti e tre i gestori di import (replace/ignore/abort). / The `ON CONFLICT` clause was appended after `RETURNING` in the generated SQL, causing a `SyntaxError`. Fixed by inserting `ON CONFLICT` before `RETURNING` in all three import mode handlers (replace/ignore/abort).

---

## [5.0.5-alpha] - 2026-02-19

### Corretto / Fixed
- **Import PostgreSQL #658**: Aggiunto helper `_pg_quote()` nel codice di importazione tabelle per quotare i nomi di colonna con lettere maiuscole (es. `id_mediaToEntity`) nella clausola `ON CONFLICT DO UPDATE SET`. PostgreSQL fa il fold dei nomi non quotati a lowercase causando un `UndefinedColumn`. / Added `_pg_quote()` helper in the table import code to double-quote mixed-case column names (e.g. `id_mediaToEntity`) in `ON CONFLICT DO UPDATE SET`. PostgreSQL folds unquoted identifiers to lowercase, causing `UndefinedColumn` errors.

---

## [5.0.5-alpha] - 2026-02-19

### Corretto / Fixed
- **Schema PostgreSQL #657**: Aggiunto `quota_usm`, `unita_misura_quota`, `photo_id`, `drawing_id`, `audit_trail` al CREATE TABLE di `inventario_materiali_table` in `pyarchinit_schema_updated.sql`. I nuovi database PostgreSQL ora includono tutte le colonne necessarie fin dalla creazione. Aggiornati anche i template SQLite (`pyarchinit.sqlite`, `pyarchinit_db.sqlite`). / Added missing columns (`quota_usm`, `unita_misura_quota`, `photo_id`, `drawing_id`, `audit_trail`) to the `inventario_materiali_table` CREATE TABLE in `pyarchinit_schema_updated.sql`. Newly created PostgreSQL databases now include all required columns. Also updated SQLite template files.

---

## [5.0.5-alpha] - 2026-02-19

### Aggiunto / Added
- **Traduzioni ro/pt/el**: Aggiunte traduzioni complete per Rumeno (ro_RO), Portoghese (pt_PT) e Greco (el_GR) con ~2100+ stringhe tradotte per ciascuna lingua. Aggiornato pyarchinit.pro per includere le tre lingue. / Added complete translations for Romanian (ro_RO), Portuguese (pt_PT) and Greek (el_GR) with ~2100+ strings translated per language. Updated pyarchinit.pro to include all three languages.
- **Combobox US/USM dinamico**: Il combobox del tipo di unità stratigrafica (US/USM) viene ora popolato dinamicamente in base alla lingua impostata in QGIS. / The stratigraphic unit type combobox (US/USM) is now dynamically populated based on the language set in QGIS.

---

## [5.3.20-alpha] - 2026-02-18

### feat(i18n): Add Romanian, Portuguese, and Greek translations

- **IT**: Infrastruttura di traduzione aggiornata e traduzioni generate per tre nuove lingue: rumeno (ro_RO), portoghese (pt_PT) e greco (el_GR). (1) **pyarchinit.pro**: Aggiunte le voci mancanti per ro_RO, pt_PT e el_GR nella variabile TRANSLATIONS. (2) **Traduzione dei file .ts**: Scritto ed eseguito script Python che utilizza dizionari completi di termini UI comuni e vocabolario archeologico per tradurre i blocchi <message> dei file .ts dal testo inglese nelle rispettive lingue target. Tradotti 1.044 blocchi per il rumeno, 1.055 per il portoghese e 1.081 per il greco, coprendo etichette di pulsanti, voci di menu, termini GIS/archeologici e frasi comuni dell'interfaccia. (3) **Compilazione file .qm**: Compilati i file .qm binari usando lrelease di PySide6. Ciascun file compila 2.734 traduzioni finite con 92 stringhe sorgente non tradotte ignorate. Le dimensioni dei file confermano l'incorporamento corretto delle traduzioni (ro: 295KB, pt: 296KB, el: 296KB vs. 292KB quando erano copie solo in inglese).
- **EN**: Updated translation infrastructure and generated translations for three new languages: Romanian (ro_RO), Portuguese (pt_PT), and Greek (el_GR). (1) **pyarchinit.pro**: Added missing entries for ro_RO, pt_PT, and el_GR to the TRANSLATIONS variable. (2) **.ts file translation**: Wrote and executed Python script using comprehensive dictionaries of common UI terms and archaeological vocabulary to translate .ts file <message> blocks from English text into respective target languages. Translated 1,044 blocks for Romanian, 1,055 for Portuguese, and 1,081 for Greek, covering button labels, menu items, GIS/archaeological terms, and common UI phrases. (3) **.qm compilation**: Compiled binary .qm files using PySide6's lrelease. Each file compiles 2,734 finished translations with 92 untranslated source texts ignored. File sizes confirm correct translation embedding (ro: 295KB, pt: 296KB, el: 296KB vs. 292KB when they were English-only copies).

#### File modificati / Modified files
- `pyarchinit.pro` (aggiunte voci TRANSLATIONS per ro_RO, pt_PT, el_GR)
- `i18n/pyarchinit_plugin_ro_RO.ts` (1.044 stringhe tradotte in rumeno)
- `i18n/pyarchinit_plugin_pt_PT.ts` (1.055 stringhe tradotte in portoghese)
- `i18n/pyarchinit_plugin_el_GR.ts` (1.081 stringhe tradotte in greco)
- `i18n/pyarchinit_plugin_ro_RO.qm` (file binario compilato)
- `i18n/pyarchinit_plugin_pt_PT.qm` (file binario compilato)
- `i18n/pyarchinit_plugin_el_GR.qm` (file binario compilato)

---

## [5.3.19-alpha] - 2026-02-18

### fix(postgres): Non-blocking PostgreSQL version check and improved error handling (#656)

- **IT**: Risolto il problema di blocco della pipeline save/connect quando il controllo della versione PostgreSQL fallisce. (1) **select_version_sql() non-bloccante**: la funzione ora restituisce `None` se il controllo della versione fallisce, invece di sollevare un'eccezione che interrompe l'intero flusso. Questa modifica consente al plugin di continuare a funzionare anche quando il database non supporta il controllo della versione o quando si verificano errori transitori di connessione. (2) **Messaggi di errore migliorati**: sostituite le eccezioni generiche "Problema di connessione al db" con messaggi di errore dettagliati che mostrano l'effettivo errore restituito dal database, migliorando notevolmente la diagnostica per gli utenti. (3) **Corretta perdita di risorse**: aggiunto `engine.dispose()` dopo il controllo della versione SQLAlchemy per garantire il rilascio adeguato delle risorse del pool di connessioni.
- **EN**: Fixed issue where PostgreSQL version check failure blocked the entire save/connect pipeline. (1) **Non-blocking select_version_sql()**: function now returns `None` if version check fails instead of raising an exception that blocks the entire flow. This allows the plugin to continue working even when the database doesn't support version checking or transient connection errors occur. (2) **Improved error messages**: replaced generic "Problema di connessione al db" exceptions with detailed error messages showing the actual database error, significantly improving diagnostics for users. (3) **Fixed resource leak**: added `engine.dispose()` after SQLAlchemy version check to ensure proper cleanup of connection pool resources.

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (reso non-bloccante select_version_sql(), migliorati messaggi errore)
- `metadata.txt` (versione patch)

---

## [5.3.22-alpha] - 2026-02-17

### feat(ui): Splash screen non-bloccante con durata minima 5s / Smooth non-blocking splash screen with 5s minimum duration

- **IT**: Reso lo splash screen non-bloccante con chiamate `processEvents()` durante l'inizializzazione, garantendo che la UI rimanga reattiva. Aggiunta durata minima di 5 secondi con messaggi di stato rotanti. Aggiunta animazione di fade-out di 0.6s. Lo splash non si blocca piu durante le operazioni pesanti di init.
- **EN**: Made splash screen non-blocking with `processEvents()` calls during initialization, ensuring the UI remains responsive. Added 5-second minimum duration with rotating status messages. Added smooth 0.6s fade-out animation. Splash no longer freezes during heavy init operations.

#### File modificati / Modified files
- `pyarchinitPlugin.py` (splash screen non-bloccante con processEvents, durata minima 5s, fade-out animato)

---

## [5.3.21-alpha] - 2026-02-17

### fix(db): Compatibilita SQLAlchemy 2.x in db_createdump e db_migrations / SQLAlchemy 2.x compatibility in db_createdump and db_migrations

- **IT**: Risolto errore `'Connection' object has no attribute 'rollback'/'commit'` in `db_createdump.py`. Cambiato al pattern esplicito `transaction = conn.begin()` compatibile con SA 1.x e 2.x. Corretto `db_migrations.py` per usare il context manager `engine.begin()`.
- **EN**: Fixed `'Connection' object has no attribute 'rollback'/'commit'` error in `db_createdump.py`. Changed to explicit `transaction = conn.begin()` pattern compatible with SA 1.x and 2.x. Fixed `db_migrations.py` to use `engine.begin()` context manager.

#### File modificati / Modified files
- `modules/db/db_createdump.py` (pattern transazione esplicito per SA 2.x / explicit transaction pattern for SA 2.x)
- `modules/db/db_migrations.py` (engine.begin() context manager)

---

## [5.3.20-alpha] - 2026-02-17

### fix(deps): Gestione commenti inline in requirements.txt / Strip inline comments from requirements.txt when parsing versions

- **IT**: Risolto `ValueError` quando le righe di `requirements.txt` contengono commenti inline come `pkg>=1.0  # Optional`. Il parser ora rimuove i commenti prima di confrontare le versioni.
- **EN**: Fixed `ValueError` when `requirements.txt` lines have inline comments like `pkg>=1.0  # Optional`. The parser now strips comments before comparing versions.

#### File modificati / Modified files
- `__init__.py` (strip dei commenti inline nel parsing di requirements.txt)

---

## [5.3.19-alpha] - 2026-02-17

### fix(deps): Isolamento dipendenze plugin con ext_libs e correzione compatibilita versioni / Isolate plugin dependencies with ext_libs and fix version compatibility

- **IT**: Creata directory `ext_libs/` per isolare le dipendenze del plugin dai pacchetti bundled di QGIS. Corretti tutti i pin `==` in `requirements.txt` sostituiti con versioni minime `>=` (molte versioni pinnate non esistevano per Python 3.9). Corrette le versioni dei pacchetti langchain (erano completamente inventate, es. `langchain==1.2.10` non esiste). Aggiunta lista `QGIS_PROTECTED_PACKAGES` per evitare di sovrascrivere numpy, scipy, sip, pyqt5. Corretto `PackageManager.install()` su tutte le piattaforme per installare in `ext_libs/` con `--target`. Corretta logica di confronto versioni per pacchetti 0.x (es. GeoAlchemy2 0.9 vs 0.18).
- **EN**: Created `ext_libs/` directory for dependency isolation from QGIS-bundled packages. Fixed all pinned `==` versions in `requirements.txt` replaced with `>=` minimum versions (many pinned versions didn't exist for Python 3.9). Fixed langchain package versions (were completely fabricated, e.g. `langchain==1.2.10` doesn't exist). Added `QGIS_PROTECTED_PACKAGES` to prevent overriding numpy, scipy, sip, pyqt5. Fixed `PackageManager.install()` on all platforms to install to `ext_libs/` with `--target`. Fixed version checking logic for 0.x packages (GeoAlchemy2 0.9 vs 0.18).

#### File creati / Created files
- `ext_libs/` (directory per dipendenze isolate del plugin / directory for isolated plugin dependencies)

#### File modificati / Modified files
- `requirements.txt` (tutte le versioni corrette da == a >= con versioni reali / all versions fixed from == to >= with real versions)
- `__init__.py` (QGIS_PROTECTED_PACKAGES, PackageManager.install con --target ext_libs, logica confronto versioni 0.x / QGIS_PROTECTED_PACKAGES, PackageManager.install with --target ext_libs, 0.x version comparison logic)
- `modules/db/db_createdump.py` (compatibilita SA 2.x / SA 2.x compatibility)
- `modules/db/db_migrations.py` (engine.begin() context manager)

---

## [5.3.17-alpha] - 2026-02-17

### feat(rust): Phase 5 — Pipeline di distribuzione modulo Rust / Phase 5 — Rust module distribution pipeline

- **IT**: Implementata la pipeline completa di distribuzione per il modulo opzionale di accelerazione Rust `pyarchinit_core`. (1) **CI/CD**: Creato workflow GitHub Actions `.github/workflows/build-rust.yml` che compila wheel cross-platform (Linux x86_64, Windows x86_64, macOS universal2) usando `maturin-action`, con trigger su tag `rust-v*` e pubblicazione automatica come GitHub Release. (2) **Installer**: Creato `scripts/rust_installer.py` con funzioni `check_rust_available()` (verifica importabilita e versione) e `install_rust_acceleration()` (rileva piattaforma/architettura, costruisce URL wheel corretto, installa via pip dal GitHub Release). (3) **Pannello impostazioni**: Aggiunto tab "Rust Acceleration" nel dialog di configurazione (`gui/pyarchinitConfigDialog.py`) con: stato del modulo (installato/non installato con versione), checkbox per abilitare/disabilitare l'accelerazione (persistita in `QgsSettings pyArchInit/rust_acceleration_enabled`), pulsante Install/Update con feedback visivo, e dettagli tecnici sugli algoritmi accelerati. (4) **Indicatore di stato**: Aggiunto log message all'avvio del plugin (`pyarchinitPlugin.py`) che riporta lo stato dell'accelerazione Rust nel pannello messaggi di QGIS.
- **EN**: Implemented the complete distribution pipeline for the optional Rust acceleration module `pyarchinit_core`. (1) **CI/CD**: Created GitHub Actions workflow `.github/workflows/build-rust.yml` that builds cross-platform wheels (Linux x86_64, Windows x86_64, macOS universal2) using `maturin-action`, triggered on `rust-v*` tags with automatic GitHub Release publishing. (2) **Installer**: Created `scripts/rust_installer.py` with `check_rust_available()` (checks importability and version) and `install_rust_acceleration()` (detects platform/architecture, builds correct wheel URL, installs via pip from GitHub Release). (3) **Settings panel**: Added "Rust Acceleration" tab to the configuration dialog (`gui/pyarchinitConfigDialog.py`) with: module status (installed/not installed with version), checkbox to enable/disable acceleration (persisted in `QgsSettings pyArchInit/rust_acceleration_enabled`), Install/Update button with visual feedback, and technical details about accelerated algorithms. (4) **Status indicator**: Added startup log message (`pyarchinitPlugin.py`) that reports Rust acceleration status in the QGIS message log panel.

#### File creati / Created files
- `.github/workflows/build-rust.yml` (CI/CD workflow cross-platform wheel build)
- `scripts/rust_installer.py` (installer e checker per modulo Rust)

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (aggiunto tab Rust Acceleration con UI gestione modulo)
- `pyarchinitPlugin.py` (aggiunto log stato Rust all'avvio plugin)

---

## [5.3.18-alpha] - 2026-02-17

### feat(rust): Phase 4 — Layout Sugiyama per Harris Matrix / Phase 4 — Sugiyama Harris Matrix layout engine

- **IT**: Implementato l'algoritmo di layout a livelli Sugiyama completo nel modulo Rust `matrix` (`_rust_core/src/matrix/mod.rs`) per la visualizzazione della Harris Matrix senza dipendenza da graphviz/dot per il posizionamento dei nodi. L'algoritmo comprende 4 fasi: (1) **Assegnazione livelli**: algoritmo longest-path basato su Kahn con supporto opzionale per vincoli di raggruppamento per fase (nodi contemporanei sullo stesso livello); (2) **Inserimento nodi dummy**: per archi che attraversano livelli multipli, inserimento di nodi virtuali per mantenere l'instradamento corretto degli archi; (3) **Minimizzazione incroci**: euristica del baricentro con sweep alternati top-down/bottom-up (6 iterazioni configurabili); (4) **Assegnazione coordinate**: posizionamento mediano con risoluzione sovrapposizioni e centratura dei livelli. Integrato nella pipeline di esportazione matrix (`modules/utility/pyarchinit_matrix_exp.py`): aggiunta funzione `_rust_transitive_reduction()` che sostituisce il subprocess `tred` usando il modulo Rust `graph.transitive_reduction()`, con fallback automatico al subprocess. Tutti e 4 i punti di chiamata `tred` in `HarrisMatrix.export_matrix`, `export_matrix_2`, `ViewHarrisMatrix.export_matrix` e `export_matrix_3` ora provano prima Rust e ricadono sul subprocess automaticamente. Aggiunte anche le funzioni pubbliche `rust_harris_layout()` e `rust_layout_to_dot()` per uso programmatico del layout engine.
- **EN**: Implemented the complete Sugiyama layered layout algorithm in the Rust `matrix` module (`_rust_core/src/matrix/mod.rs`) for Harris Matrix visualization without dependency on graphviz/dot for node positioning. The algorithm comprises 4 phases: (1) **Layer assignment**: longest-path algorithm based on Kahn's topological sort with optional phase group constraints (contemporary nodes on same layer); (2) **Dummy node insertion**: for edges spanning multiple layers, virtual nodes are inserted to maintain proper edge routing; (3) **Crossing minimization**: barycenter heuristic with alternating top-down/bottom-up sweeps (6 configurable iterations); (4) **Coordinate assignment**: median positioning with overlap resolution and layer centering. Integrated into the matrix export pipeline (`modules/utility/pyarchinit_matrix_exp.py`): added `_rust_transitive_reduction()` function that replaces the `tred` subprocess using the Rust `graph.transitive_reduction()` module, with automatic fallback to subprocess. All 4 `tred` call sites in `HarrisMatrix.export_matrix`, `export_matrix_2`, `ViewHarrisMatrix.export_matrix`, and `export_matrix_3` now try Rust first and fall back to subprocess automatically. Also added public functions `rust_harris_layout()` and `rust_layout_to_dot()` for programmatic use of the layout engine.

#### File modificati / Modified files
- `_rust_core/src/matrix/mod.rs` (implementazione completa Sugiyama: layer assignment, dummy nodes, crossing minimization, coordinate assignment)
- `modules/utility/pyarchinit_matrix_exp.py` (Rust fast path per tred + funzioni layout pubbliche)

---

## [5.3.16-alpha] - 2026-02-17

### feat(rust): Phase 3 — Modulo geostatistico Rust / Phase 3 — Rust geostatistics module

- **IT**: Implementato il modulo geostatistico completo in Rust (`_rust_core/src/geostat/mod.rs`) con 5 funzioni ad alte prestazioni: (1) `calculate_variogram` -- calcolo variogramma empirico con binning per lag e computazione pairwise parallelizzata via rayon; (2) `ordinary_kriging` -- kriging ordinario su griglia regolare con matrice di covarianza, risoluzione del sistema lineare via LU decomposition (nalgebra) e parallelizzazione per cella via rayon, supporta 4 modelli di variogramma (sferico, esponenziale, gaussiano, lineare); (3) `idw_interpolation` -- interpolazione IDW (Inverse Distance Weighting) parallelizzata con raggio di ricerca opzionale; (4) `maximin_design` -- campionamento ottimale maximin greedy per la selezione di nuovi punti di campionamento che massimizzano la distanza minima dai punti esistenti; (5) `cross_validate_kriging` -- cross-validation leave-one-out parallelizzata per kriging con sottocampionamento deterministico. Aggiornato il bridge Python `modules/_rust_bridge.py` con metodi wrapper per tutte le 5 funzioni geostatistiche. Integrati fast path Rust in `modules/geoarchaeo/core/geostat_engine.py` (variogramma, kriging, cross-validation) e in `modules/analysis/ut_heatmap_generator.py` (IDW), ciascuno con fallback automatico alle implementazioni Python in caso di errore.
- **EN**: Implemented the complete geostatistics module in Rust (`_rust_core/src/geostat/mod.rs`) with 5 high-performance functions: (1) `calculate_variogram` -- empirical variogram computation with lag binning and rayon-parallelized pairwise distance/semivariance calculation; (2) `ordinary_kriging` -- ordinary kriging on regular grid with covariance matrix, LU decomposition solver (nalgebra) and per-cell rayon parallelization, supporting 4 variogram models (spherical, exponential, gaussian, linear); (3) `idw_interpolation` -- parallelized IDW (Inverse Distance Weighting) interpolation with optional search radius; (4) `maximin_design` -- greedy maximin optimal sampling design for selecting new sample points that maximize minimum distance to existing points; (5) `cross_validate_kriging` -- parallelized leave-one-out cross-validation for kriging with deterministic subsampling. Updated Python bridge `modules/_rust_bridge.py` with wrapper methods for all 5 geostatistical functions. Integrated Rust fast paths into `modules/geoarchaeo/core/geostat_engine.py` (variogram, kriging, cross-validation) and `modules/analysis/ut_heatmap_generator.py` (IDW), each with automatic fallback to Python implementations on error.

#### File modificati / Modified files
- `_rust_core/src/geostat/mod.rs` (implementazione completa: variogramma, kriging, IDW, maximin, cross-validation)
- `modules/_rust_bridge.py` (aggiunti 5 metodi wrapper geostatistici)
- `modules/geoarchaeo/core/geostat_engine.py` (Rust fast path per variogramma, kriging, cross-validation)
- `modules/analysis/ut_heatmap_generator.py` (Rust fast path per IDW)

---

## [5.3.15-alpha] - 2026-02-17

### feat(rust): Phase 2 — Scaffolding modulo Rust pyarchinit_core / Phase 2 — Rust pyarchinit_core module scaffolding

- **IT**: Creato il crate Rust `pyarchinit_core` con PyO3 0.22 (abi3-py39) per accelerazione opzionale del plugin. Il modulo `graph` implementa tre algoritmi: (1) `topological_sort_with_levels` (algoritmo di Kahn con raggruppamento per livelli), (2) `detect_and_remove_cycles` (DFS iterativo per rilevamento e rimozione cicli), (3) `transitive_reduction` (algoritmo di Warshall per riduzione transitiva, sostituisce il subprocess `tred`). I moduli `geostat` e `matrix` sono placeholder per le fasi 3-4. Creato il bridge Python `modules/_rust_bridge.py` con pattern singleton lazy-loading e graceful degradation (il plugin funziona anche senza il modulo Rust). Integrato il Rust engine in `Order_layer_graph._remove_cycles()` e `_topological_sort_with_levels()` con fallback automatico alle implementazioni Python. Build verificato con maturin 1.12 su macOS ARM64.
- **EN**: Created `pyarchinit_core` Rust crate with PyO3 0.22 (abi3-py39) for optional plugin acceleration. The `graph` module implements three algorithms: (1) `topological_sort_with_levels` (Kahn's algorithm with level grouping), (2) `detect_and_remove_cycles` (iterative DFS for cycle detection and removal), (3) `transitive_reduction` (Warshall's algorithm for transitive reduction, replaces `tred` subprocess). `geostat` and `matrix` modules are placeholders for phases 3-4. Created Python bridge `modules/_rust_bridge.py` with lazy-loading singleton pattern and graceful degradation (plugin works without Rust module). Integrated Rust engine into `Order_layer_graph._remove_cycles()` and `_topological_sort_with_levels()` with automatic fallback to Python implementations. Build verified with maturin 1.12 on macOS ARM64.

#### File creati / Created files
- `_rust_core/Cargo.toml`, `_rust_core/pyproject.toml` (configurazione crate/build)
- `_rust_core/src/lib.rs` (entry point #[pymodule])
- `_rust_core/src/graph/mod.rs` (topo_sort, cycle detection, tred)
- `_rust_core/src/geostat/mod.rs`, `_rust_core/src/matrix/mod.rs` (placeholder)
- `modules/_rust_bridge.py` (bridge Python con graceful degradation)

#### File modificati / Modified files
- `modules/gis/pyarchinit_pyqgis.py` (Rust fast path in _remove_cycles e _topological_sort_with_levels)
- `.gitignore` (aggiunto `_rust_core/target/`)

---

## [5.3.14-alpha] - 2026-02-17

### perf: Phase 1 — Ottimizzazioni prestazioni Python / Phase 1 — Python Performance Optimizations

#### Gruppo A: Order Layer (`modules/gis/pyarchinit_pyqgis.py`)

- **IT**: (1) Sostituito `eval()` con `ast.literal_eval()` in `_build_graph()` — sicurezza e prestazioni. (2) Riscritta `_remove_cycles()` da DFS ricorsivo O(N²) a iterativo O(N+E) con stack esplicito e `path_set`. (3) Riscritta `update_database_with_order()` con singola query batch `UPDATE ... SET order_layer = CASE WHEN ... END` invece di N query + N `clear_cache()`.
- **EN**: (1) Replaced `eval()` with `ast.literal_eval()` in `_build_graph()` — security and performance. (2) Rewrote `_remove_cycles()` from recursive O(N²) DFS to iterative O(N+E) with explicit stack and `path_set`. (3) Rewrote `update_database_with_order()` with single batch `UPDATE ... SET order_layer = CASE WHEN ... END` instead of N queries + N `clear_cache()` calls.

#### Gruppo B: Time Manager (`tabs/Gis_Time_controller.py`)

- **IT**: (1) Rimosso `QThread.sleep(2)` — sostituito con `canvas.renderComplete` signal + `QEventLoop` con timeout 10s. (2) Debounce dial/spinbox con `QTimer.singleShot(300ms)` + cache sito/area. (3) Lazy matrix rebuild solo al cambio stato checkbox. (4) Pre-scan SQL ottimizzato: singola query `SELECT COUNT(DISTINCT order_layer)` invece di triplo ciclo annidato.
- **EN**: (1) Removed `QThread.sleep(2)` — replaced with `canvas.renderComplete` signal + `QEventLoop` with 10s timeout. (2) Debounce dial/spinbox with `QTimer.singleShot(300ms)` + cached sito/area. (3) Lazy matrix rebuild only on checkbox state change. (4) Optimized pre-scan SQL: single `SELECT COUNT(DISTINCT order_layer)` query instead of triple nested loop.

#### Gruppo C: DB Manager (`modules/db/pyarchinit_db_manager.py`)

- **IT**: (1) Rimosso `engine.dispose()` dopo ogni insert in `insert_data_session()`. (2) Riuso `self.Session()` in `update()` invece di creare nuovo `sessionmaker` per chiamata.
- **EN**: (1) Removed `engine.dispose()` after every insert in `insert_data_session()`. (2) Reuse `self.Session()` in `update()` instead of creating new `sessionmaker` per call.

#### Gruppo D: Database Sync (`modules/db/database_sync.py`)

- **IT**: (1) Connessione SQLite persistente in `SQLiteAdapter` con validazione `SELECT 1`. (2) Import batch con `executemany()` + fallback row-by-row. (3) Supporto SQLAlchemy engine per `PostgreSQLAdapter` — elimina ~188 subprocess `psql` per sessione.
- **EN**: (1) Persistent SQLite connection in `SQLiteAdapter` with `SELECT 1` validation. (2) Batch import with `executemany()` + row-by-row fallback. (3) SQLAlchemy engine support for `PostgreSQLAdapter` — eliminates ~188 `psql` subprocess spawns per session.

#### Gruppo E: DB Index

- **IT**: Aggiunto indice `idx_us_order_layer` su `us_table.order_layer` in structures e structures_metadata.
- **EN**: Added `idx_us_order_layer` index on `us_table.order_layer` in structures and structures_metadata.

#### File modificati / Modified files
- `modules/gis/pyarchinit_pyqgis.py` (eval→ast.literal_eval, DFS iterativo, batch SQL update)
- `tabs/Gis_Time_controller.py` (renderComplete signal, debounce, lazy matrix, SQL pre-scan)
- `modules/db/pyarchinit_db_manager.py` (rimosso engine.dispose, riuso self.Session)
- `modules/db/database_sync.py` (connessione persistente, executemany, SQLAlchemy engine)
- `modules/db/structures/US_table.py` (indice order_layer)
- `modules/db/structures_metadata/US_table.py` (indice order_layer)

---

## [5.3.13-alpha] - 2026-02-16

### refactor(cleanup): Rimossi eseguibili obsoleti e codice morto associato / Removed obsolete bundled executables and associated dead code

- **IT**: Rimossi 4 eseguibili obsoleti dalla directory `resources/dbfiles/`: `sqldiff.exe`, `sqldiff_linux`, `sqldiff_osx` e `spatialite_convert.exe`. Questi file non erano piu utilizzati dal plugin e appesantivano inutilmente il pacchetto. Rimosso il metodo `compare()` da `gui/pyarchinitConfigDialog.py`, che eseguiva `os.system("start cmd /k...")` per lanciare `sqldiff` solo su Windows — un pattern insicuro (shell injection) e non portabile. Rimosso il metodo `on_pushButton_convertdb_pressed()` dallo stesso file, anch'esso esclusivamente Windows-only e legato a `spatialite_convert.exe`. Rimosso il pannello UI `mDockWidget` dal file `gui/ui/pyarchinitConfigDialog.ui` che ospitava i pulsanti per queste funzionalita. Rimosse le voci di copia file per i 4 eseguibili da `modules/utility/pyarchinit_folder_installation.py`, che li copiava nella directory utente durante l'installazione delle cartelle del plugin. Il risultato e un plugin piu leggero, senza codice specifico Windows/insicuro e senza binari inutilizzati.
- **EN**: Removed 4 obsolete executables from the `resources/dbfiles/` directory: `sqldiff.exe`, `sqldiff_linux`, `sqldiff_osx`, and `spatialite_convert.exe`. These files were no longer used by the plugin and unnecessarily bloated the package. Removed the `compare()` method from `gui/pyarchinitConfigDialog.py`, which ran `os.system("start cmd /k...")` to launch `sqldiff` on Windows only — an insecure pattern (shell injection risk) and non-portable. Removed the `on_pushButton_convertdb_pressed()` method from the same file, also Windows-only and tied to `spatialite_convert.exe`. Removed the `mDockWidget` UI panel from `gui/ui/pyarchinitConfigDialog.ui` that hosted the buttons for these features. Removed the file-copy entries for the 4 executables from `modules/utility/pyarchinit_folder_installation.py`, which copied them into the user directory during plugin folder installation. The result is a lighter plugin, free of Windows-specific/insecure code paths and unused binaries.

#### File eliminati / Deleted files
- `resources/dbfiles/sqldiff.exe`
- `resources/dbfiles/sqldiff_linux`
- `resources/dbfiles/sqldiff_osx`
- `resources/dbfiles/spatialite_convert.exe`

#### File modificati / Modified files
- `gui/pyarchinitConfigDialog.py` (rimossi metodi `compare()` e `on_pushButton_convertdb_pressed()` / removed `compare()` and `on_pushButton_convertdb_pressed()` methods)
- `gui/ui/pyarchinitConfigDialog.ui` (rimosso pannello `mDockWidget` / removed `mDockWidget` panel)
- `modules/utility/pyarchinit_folder_installation.py` (rimosse voci copia eseguibili / removed executable copy entries)

---

## [5.3.12-alpha] - 2026-02-16

### fix(perf): Risolto CPU 100% su Windows al caricamento del plugin / Fixed Windows CPU 100% at plugin load

- **IT**: Risolto un problema critico di prestazioni che causava il blocco della CPU al 100% su macchine Windows durante il caricamento del plugin, in particolare quando PostgreSQL o Graphviz non erano installati. Tre interventi principali: (1) **Timeout sui subprocess**: aggiunto `timeout=5` alle chiamate `subprocess.run()` per i controlli di versione `pg_dump -V` e `dot -V` in `__init__.py` e `modules/utility/pyarchinit_OS_utility.py`. In precedenza veniva usato `subprocess.call()` senza timeout, che poteva bloccarsi indefinitamente su Windows in assenza dei programmi esterni. (2) **Import lazy dei tab**: spostati oltre 30 import di moduli tab/dialog dal livello di modulo all'interno dei rispettivi metodi `run*()` (click handler) sia in `pyarchinitPlugin.py` che in `pyarchinitDockWidget.py`. Questo differisce il caricamento delle dipendenze pesanti (cv2, matplotlib, pandas, numpy, ecc.) dall'avvio del plugin al momento in cui l'utente apre effettivamente ciascun tab. (3) **Cache dei percorsi**: aggiunta variabile cache `_cached_windows_python_path` in `PackageManager.get_windows_qgis_python()` in `__init__.py` per evitare scansioni ripetute del filesystem in `C:\Program Files` durante l'installazione dei pacchetti.
- **EN**: Fixed a critical performance issue causing 100% CPU lock on Windows machines during plugin loading, particularly when PostgreSQL or Graphviz were not installed. Three main interventions: (1) **Subprocess timeout**: added `timeout=5` to `subprocess.run()` calls for `pg_dump -V` and `dot -V` version checks in `__init__.py` and `modules/utility/pyarchinit_OS_utility.py`. Previously bare `subprocess.call()` was used without timeout, which could hang indefinitely on Windows when the external programs were missing. (2) **Lazy tab imports**: moved 30+ tab/dialog module imports from module-level to inside their respective `run*()` click handler methods in both `pyarchinitPlugin.py` and `pyarchinitDockWidget.py`. This defers loading heavy dependencies (cv2, matplotlib, pandas, numpy, etc.) from plugin startup to when the user actually opens each tab. (3) **Path caching**: added `_cached_windows_python_path` cache variable to `PackageManager.get_windows_qgis_python()` in `__init__.py` to avoid repeated filesystem scans of `C:\Program Files` during package installation.

#### File modificati / Modified files
- `__init__.py` (timeout subprocess, cache percorsi / subprocess timeout, path caching)
- `pyarchinitPlugin.py` (import lazy dei tab / lazy tab imports)
- `pyarchinitDockWidget.py` (import lazy dei tab / lazy tab imports)
- `modules/utility/pyarchinit_OS_utility.py` (timeout subprocess / subprocess timeout)

---

## [5.3.11-alpha] - 2026-02-16

### fix(docs): Corretto tutorial MoveCost greco (el/34_movecost.md) da traslitterazione latina a caratteri greci / Fixed Greek MoveCost tutorial (el/34_movecost.md) from Latin transliteration to Greek characters

- **IT**: Riscritto completamente il file `docs/tutorials/el/34_movecost.md` convertendo tutto il testo dalla traslitterazione latina (Greeklish, es. "Eisagwgi", "Periechomena", "Algorithmoi") ai caratteri greci propri (es. "Εισαγωγη", "Περιεχομενα", "Αλγοριθμοι"). Lo stile adottato e il greco monotonico senza accenti, coerente con il tutorial GeoArchaeo greco (`el/33_geoarchaeo.md`). I termini tecnici (MoveCost, QGIS, R, DTM, CSV, HTML, PDF, Processing, ecc.) sono stati mantenuti in caratteri latini. La struttura e il contenuto del documento sono rimasti invariati (574 righe, 11 sezioni).
- **EN**: Completely rewrote the file `docs/tutorials/el/34_movecost.md` converting all text from Latin transliteration (Greeklish, e.g. "Eisagwgi", "Periechomena", "Algorithmoi") to proper Greek characters (e.g. "Εισαγωγη", "Περιεχομενα", "Αλγοριθμοι"). The style used is monotonic Greek without accents, consistent with the Greek GeoArchaeo tutorial (`el/33_geoarchaeo.md`). Technical terms (MoveCost, QGIS, R, DTM, CSV, HTML, PDF, Processing, etc.) were kept in Latin characters. The document structure and content remain unchanged (574 lines, 11 sections).

#### File modificati / Modified files
- `docs/tutorials/el/34_movecost.md`

---

## [5.3.10-alpha] - 2026-02-16

### docs(tutorials): Creato tutorial GeoArchaeo (33_geoarchaeo.md) in 10 lingue / Created GeoArchaeo tutorial (33_geoarchaeo.md) in 10 languages

- **IT**: Creato il file tutorial `33_geoarchaeo.md` in tutte le 10 directory linguistiche (it, en, de, fr, es, ar, ca, ro, pt, el) per lo strumento di analisi geostatistica GeoArchaeo. Ogni file contiene circa 463-466 righe di markdown con: indice, introduzione (cos'e GeoArchaeo, perche l'analisi geostatistica in archeologia), accesso allo strumento (Analysis Tools toolbar), interfaccia utente (6 schede), scheda Dati (caricamento layer, selezione campi, dati di esempio, esplorazione), scheda Variogramma (calcolo variogramma sperimentale, modellazione con 4 tipi di modello, variogrammi direzionali, parametri nugget/sill/range), scheda Kriging (kriging ordinario e universale, parametri griglia, risultati predizione e varianza), scheda Machine Learning (Random Forest, Gradient Boosting, SVR, validazione crociata, importanza variabili), scheda Campionamento (4 strategie: casuale semplice, stratificato, griglia regolare, ottimizzato), scheda Report (generazione automatica, formati PDF/HTML/Markdown), flusso di lavoro operativo in 6 passi, risoluzione problemi (tabella con 6 problemi comuni e soluzioni), note tecniche (dipendenze, CRS, esportazione, integrazione QGIS). Ogni versione linguistica e una traduzione propria, non una copia.
- **EN**: Created the tutorial file `33_geoarchaeo.md` in all 10 language directories (it, en, de, fr, es, ar, ca, ro, pt, el) for the GeoArchaeo geostatistical analysis tool. Each file contains approximately 463-466 lines of markdown with: table of contents, introduction (what is GeoArchaeo, why geostatistical analysis in archaeology), accessing the tool (Analysis Tools toolbar), user interface (6 tabs), Data tab (loading layers, field selection, example data, exploration), Variogram tab (experimental variogram computation, modelling with 4 model types, directional variograms, nugget/sill/range parameters), Kriging tab (ordinary and universal kriging, grid parameters, prediction and variance results), Machine Learning tab (Random Forest, Gradient Boosting, SVR, cross-validation, variable importance), Sampling tab (4 strategies: simple random, stratified, regular grid, optimised), Report tab (automatic generation, PDF/HTML/Markdown formats), 6-step operational workflow, troubleshooting (table with 6 common issues and solutions), technical notes (dependencies, CRS, export, QGIS integration). Each language version is a proper translation, not a copy.

#### File creati / Created files
- `docs/tutorials/it/33_geoarchaeo.md`
- `docs/tutorials/en/33_geoarchaeo.md`
- `docs/tutorials/de/33_geoarchaeo.md`
- `docs/tutorials/fr/33_geoarchaeo.md`
- `docs/tutorials/es/33_geoarchaeo.md`
- `docs/tutorials/ar/33_geoarchaeo.md`
- `docs/tutorials/ca/33_geoarchaeo.md`
- `docs/tutorials/ro/33_geoarchaeo.md`
- `docs/tutorials/pt/33_geoarchaeo.md`
- `docs/tutorials/el/33_geoarchaeo.md`

---

## [5.3.9-alpha] - 2026-02-16

### docs(tutorials): Creato tutorial MoveCost (34_movecost.md) in 10 lingue / Created MoveCost tutorial (34_movecost.md) in 10 languages

- **IT**: Creato il file tutorial `34_movecost.md` in tutte le 10 directory linguistiche (it, en, de, fr, es, ar, ca, ro, pt, el) per lo strumento autonomo MoveCost di analisi percorsi di minor costo. Ogni file contiene circa 450-550 righe di markdown con: indice, introduzione (storia dell'estrazione dalla scheda Sito), accesso allo strumento (Analysis Tools toolbar), prerequisiti (R, pacchetto movecost, Processing R Provider), interfaccia utente (4 schede), scheda Algoritmi (14 algoritmi in 3 gruppi: Superficie di Costo e Percorsi, Analisi Corridoi e Reti, Confronto e Classificazione), scheda Risultati (riepilogo costi e visualizzatore grafici R), scheda Esportazione (CSV, PDF stub, HTML), scheda Impostazioni (script R, lingua, organizzazione layer, help), flusso di lavoro operativo passo-passo, risoluzione problemi (R non trovato, script mancanti, grafici non visibili, pacchetto non installato, analisi lenta, errore CRS), note tecniche (architettura, file sorgente, funzioni di costo supportate, riferimenti bibliografici, compatibilita).
- **EN**: Created the tutorial file `34_movecost.md` in all 10 language directories (it, en, de, fr, es, ar, ca, ro, pt, el) for the standalone MoveCost least-cost path analysis tool. Each file contains approximately 450-550 lines of markdown with: table of contents, introduction (history of extraction from Site form), accessing the tool (Analysis Tools toolbar), prerequisites (R, movecost package, Processing R Provider), user interface (4 tabs), Algorithms tab (14 algorithms in 3 groups: Cost Surface & Paths, Corridor & Network Analysis, Comparison & Ranking), Results tab (cost summary and R plot viewer), Export tab (CSV, PDF stub, HTML), Settings tab (R scripts, language, layer organization, help), step-by-step operational workflow, troubleshooting (R not found, scripts missing, plots not showing, package not installed, slow analysis, CRS error), technical notes (architecture, source files, supported cost functions, bibliographic references, compatibility).

#### File creati / Created files
- `docs/tutorials/it/34_movecost.md`
- `docs/tutorials/en/34_movecost.md`
- `docs/tutorials/de/34_movecost.md`
- `docs/tutorials/fr/34_movecost.md`
- `docs/tutorials/es/34_movecost.md`
- `docs/tutorials/ar/34_movecost.md`
- `docs/tutorials/ca/34_movecost.md`
- `docs/tutorials/ro/34_movecost.md`
- `docs/tutorials/pt/34_movecost.md`
- `docs/tutorials/el/34_movecost.md`

### docs(tutorials): Aggiornamento tutorial Scheda Sito (02_*) in 10 lingue: rimossa sezione MoveCost, aggiunta nota strumenti di analisi standalone / Update Site Form tutorial (02_*) in 10 languages: removed MoveCost section, added standalone analysis tools note

- **IT**: Aggiornati i tutorial della Scheda Sito (02_*) in tutte le 10 directory linguistiche (it, en, de, fr, es, ar, ca, ro, pt, el). Modifiche: (1) Rimossa voce MoveCost dall'indice e sostituita con "Strumenti di Analisi"; (2) Aggiornata tabella interfaccia utente, riga 5 da "MoveCost" a "Strumenti di Analisi"; (3) Rimossa intera sezione MoveCost (prerequisiti, funzioni R, screenshot) e sostituita con una breve nota sugli strumenti di analisi standalone accessibili dalla toolbar (MoveCost, GeoArchaeo, SAM Segmentation, Pottery Tools, TOPS, Image Search) con link ai tutorial dedicati; (4) Sostituita voce troubleshooting "MoveCost non funziona" con riferimento generico ai tutorial dedicati; (5) Aggiornato elenco video nella versione IT.
- **EN**: Updated the Site Form tutorials (02_*) in all 10 language directories (it, en, de, fr, es, ar, ca, ro, pt, el). Changes: (1) Removed MoveCost entry from table of contents and replaced with "Analysis Tools"; (2) Updated user interface table, row 5 from "MoveCost" to "Analysis Tools"; (3) Removed entire MoveCost section (prerequisites, R functions, screenshots) and replaced with a short note about standalone analysis tools accessible from the toolbar (MoveCost, GeoArchaeo, SAM Segmentation, Pottery Tools, TOPS, Image Search) with links to dedicated tutorials; (4) Replaced troubleshooting entry "MoveCost not working" with a generic reference to dedicated tutorials; (5) Updated video list in IT version.

#### File modificati / Modified files
- `docs/tutorials/it/02_scheda_sito.md`
- `docs/tutorials/en/02_scheda_sito.md`
- `docs/tutorials/de/02_fundort_formular.md`
- `docs/tutorials/fr/02_fiche_site.md`
- `docs/tutorials/es/02_ficha_sitio.md`
- `docs/tutorials/ar/02_بطاقة_الموقع.md`
- `docs/tutorials/ca/02_fitxa_lloc.md`
- `docs/tutorials/ro/02_scheda_sito.md`
- `docs/tutorials/pt/02_scheda_sito.md`
- `docs/tutorials/el/02_scheda_sito.md`

### refactor(movecost): Estrazione MoveCost dalla scheda Sito in strumento di analisi standalone / Extract MoveCost from Site form into standalone analysis tool

- **IT**: Estratto MoveCost dalla scheda Sito (`tabs/Site.py`, `gui/ui/Site.ui`) in uno strumento di analisi standalone. Creato nuovo dialogo `tabs/Movecost.py` (classe `pyarchinit_Movecost`) con tutte le funzionalità movecost: 14 algoritmi R (movecost, movebound, movecorr, movealloc, movecomp, movenetw, moverank con varianti polygon), organizzazione layer, riepilogo risultati, visualizzazione plot R, esportazione CSV/PDF/HTML, impostazioni (script R, lingua, help). Creato file UI `gui/ui/Movecost.ui` con 4 tab (Algoritmi, Risultati, Esportazione, Impostazioni). Rimosso `QgsDockWidget mDockWidget`, `pushButton_mc` e connessione signal/slot da `Site.ui`. Rimossi tutti i metodi movecost e import inutilizzati da `Site.py`. Aggiunto `actionMovecost` al `analysisToolButton` in tutte le 4 sezioni locali (IT/EN/DE/else) di `pyarchinitPlugin.py`. Aggiunto metodo `runMovecost` al plugin.
- **EN**: Extracted MoveCost from the Site form (`tabs/Site.py`, `gui/ui/Site.ui`) into a standalone analysis tool. Created new dialog `tabs/Movecost.py` (class `pyarchinit_Movecost`) containing all movecost functionality: 14 R algorithms (movecost, movebound, movecorr, movealloc, movecomp, movenetw, moverank with polygon variants), layer organization, results summary, R plot viewer, CSV/PDF/HTML export, settings (R scripts, language, help). Created UI file `gui/ui/Movecost.ui` with 4 tabs (Algorithms, Results, Export, Settings). Removed `QgsDockWidget mDockWidget`, `pushButton_mc` and signal/slot connection from `Site.ui`. Removed all movecost methods and unused imports from `Site.py`. Added `actionMovecost` to `analysisToolButton` in all 4 locale sections (IT/EN/DE/else) of `pyarchinitPlugin.py`. Added `runMovecost` method to the plugin.

#### File creati / Created files
- `tabs/Movecost.py` (nuovo / new)
- `gui/ui/Movecost.ui` (nuovo / new)

#### File modificati / Modified files
- `tabs/Site.py` (rimossi metodi e import movecost / removed movecost methods and imports)
- `gui/ui/Site.ui` (rimosso mDockWidget, pushButton_mc e connessione / removed mDockWidget, pushButton_mc and connection)
- `pyarchinitPlugin.py` (aggiunto actionMovecost e runMovecost / added actionMovecost and runMovecost)

### feat(ui): Creato file UI standalone per MoveCost Analysis / Created standalone MoveCost Analysis UI file

- **IT**: Creato nuovo file Qt Designer `gui/ui/Movecost.ui` con classe `MovecostDialog` (QDialog, 420x700). Il dialogo contiene un QTabWidget con 4 tab: (1) Algorithms -- pulsanti per movecost, movebound, movecorr, movealloc, movenetw, movecomp, moverank con varianti "by polygon", raggruppati in 3 QGroupBox (Cost Surface & Paths, Corridor & Network Analysis, Comparison & Ranking); (2) Results -- QTextEdit per il riepilogo costi e QLabel per visualizzazione plot R con pulsanti Refresh/Save; (3) Export -- pulsanti per esportazione CSV, PDF e HTML; (4) Settings -- installazione script R, selezione lingua, organizzazione layer automatica, help. Applicato stylesheet completo con bordi arrotondati, colori tematici per ogni pulsante e stile coerente per tab, gruppi, combo e text edit.
- **EN**: Created new Qt Designer file `gui/ui/Movecost.ui` with class `MovecostDialog` (QDialog, 420x700). The dialog contains a QTabWidget with 4 tabs: (1) Algorithms -- buttons for movecost, movebound, movecorr, movealloc, movenetw, movecomp, moverank with "by polygon" variants, grouped in 3 QGroupBoxes (Cost Surface & Paths, Corridor & Network Analysis, Comparison & Ranking); (2) Results -- QTextEdit for cost summary and QLabel for R plot display with Refresh/Save buttons; (3) Export -- buttons for CSV, PDF and HTML export; (4) Settings -- R script installation, language selection, automatic layer organization, help. Applied comprehensive stylesheet with rounded borders, themed colors per button, and consistent styling for tabs, groups, combos, and text edits.

#### File creati / Created files
- `gui/ui/Movecost.ui` (nuovo / new)

### refactor(toolbar): Raggruppamento strumenti di analisi nelle sezioni EN ed else della toolbar / Group analysis tools in EN and else toolbar sections

- **IT**: Aggiornate le sezioni `elif l == 'en'` ed `else` in `pyarchinitPlugin.py` per allinearle alla sezione italiana (`l == 'it'`) gia' modificata. Modifiche: (1) rimosso `self.toolBar.addAction(self.actionSamSegmentation)` -- SAM ora raggruppato nell'analysisToolButton; (2) rimosso `self.actionPotteryTools` dal `dataToolButton`; (3) sostituito il vecchio pulsante standalone TOPS con un nuovo `analysisToolButton` che contiene: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo; (4) rimossa la vecchia definizione di `ImageSearch` dalla sezione documentazione (ora creata nell'area analysis tools); (5) rimosso `ImageSearch` dal `docToolButton`; (6) aggiunti `actionImageSearch` e `actionGeoArchaeo` al menu plugin; (7) aggiornato il QMenu per raggruppare gli strumenti di analisi e rimuovere PotteryTools dalla riga data entry.
- **EN**: Updated the `elif l == 'en'` and `else` sections in `pyarchinitPlugin.py` to match the already-modified Italian (`l == 'it'`) section. Changes: (1) removed `self.toolBar.addAction(self.actionSamSegmentation)` -- SAM now grouped in analysisToolButton; (2) removed `self.actionPotteryTools` from `dataToolButton`; (3) replaced the old standalone TOPS button with a new `analysisToolButton` containing: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo; (4) removed old `ImageSearch` definition from the documentation section (now created in the analysis tools area); (5) removed `ImageSearch` from `docToolButton`; (6) added `actionImageSearch` and `actionGeoArchaeo` to the plugin menu; (7) updated the QMenu to group analysis tools and remove PotteryTools from the data entry line.

#### File modificati / Modified files
- `pyarchinitPlugin.py` (aggiornate sezioni EN ed else / updated EN and else sections)

### fix(security): Aggiornamento dipendenze per vulnerabilita' Dependabot / Update dependencies for Dependabot vulnerabilities

- **IT**: Aggiornato `requirements.txt` per risolvere vulnerabilita' segnalate da Dependabot: `langchain` da 1.2.3 a 1.2.10 e `langchain-core` da 1.2.7 a 1.2.13. Le nuove versioni includono patch di sicurezza e fix di stabilita'.
- **EN**: Updated `requirements.txt` to resolve Dependabot-reported vulnerabilities: `langchain` from 1.2.3 to 1.2.10 and `langchain-core` from 1.2.7 to 1.2.13. The new versions include security patches and stability fixes.

#### File modificati / Modified files
- `requirements.txt` (aggiornato / updated)

### feat(ai): Aggiornamento modelli AI a GPT-4.1 e Claude 4.5 Sonnet / Update AI models to GPT-4.1 and Claude 4.5 Sonnet

- **IT**: Aggiornati tutti i riferimenti ai modelli AI nel codebase. Tutti i riferimenti a GPT-4o sostituiti con GPT-4.1 in 5 file: `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py`, `embedding_models.py`, `translate_ts_complete.py`, `textTosql.py`. Modello Claude aggiornato da `claude-3-5-sonnet` a `claude-sonnet-4-5-20250929`. Aggiunto Anthropic Claude 4.5 Sonnet come alternativa nel modulo txt2sql (`textTosql.py`) per query SQL in linguaggio naturale.
- **EN**: Updated all AI model references across the codebase. All GPT-4o references replaced with GPT-4.1 in 5 files: `skatch_gpt_US.py`, `skatch_gpt_INVMAT.py`, `embedding_models.py`, `translate_ts_complete.py`, `textTosql.py`. Claude model updated from `claude-3-5-sonnet` to `claude-sonnet-4-5-20250929`. Added Anthropic Claude 4.5 Sonnet as alternative in the txt2sql module (`textTosql.py`) for natural language SQL queries.

#### File modificati / Modified files
- `modules/ai/skatch_gpt_US.py` (aggiornato / updated)
- `modules/ai/skatch_gpt_INVMAT.py` (aggiornato / updated)
- `modules/ai/embedding_models.py` (aggiornato / updated)
- `scripts/translate_ts_complete.py` (aggiornato / updated)
- `modules/ai/textTosql.py` (aggiornato / updated)

### feat(geoarchaeo): Integrazione plugin GeoArchaeo per analisi geostatistica / GeoArchaeo geostatistical analysis plugin integration

- **IT**: Integrato il plugin GeoArchaeo per analisi geostatistica come modulo interno in `modules/geoarchaeo/`. Aggiunto alla toolbar in tutte le sezioni locali (IT/EN/DE/else) all'interno del nuovo `analysisToolButton`. Implementato metodo `runGeoArchaeo` in `pyarchinitPlugin.py` che avvia il pannello dock widget per l'analisi geostatistica. Il plugin fornisce strumenti per analisi spaziale, interpolazione e statistica dei dati archeologici direttamente dall'interfaccia PyArchInit.
- **EN**: Integrated the GeoArchaeo geostatistical analysis plugin as an internal module at `modules/geoarchaeo/`. Added to the toolbar in all locale sections (IT/EN/DE/else) within the new `analysisToolButton`. Implemented `runGeoArchaeo` method in `pyarchinitPlugin.py` that launches the dock widget panel for geostatistical analysis. The plugin provides tools for spatial analysis, interpolation and statistics on archaeological data directly from the PyArchInit interface.

#### File modificati / Modified files
- `modules/geoarchaeo/` (nuovo modulo / new module)
- `pyarchinitPlugin.py` (aggiornato / updated)

### refactor(tops): Riscrittura completa del modulo TOPS con API Python diretta / Complete rewrite of TOPS module with direct Python API

- **IT**: Riscrittura completa di `tabs/tops_pyarchinit.py`: rimosso il vecchio approccio basato su subprocess a favore dell'API Python diretta. Aggiunto auto-rilevamento dei formati di input disponibili. Ora supporta 17 formati di input (CSV, DXF, GeoJSON, GML, GPX, JSON, KML, KMZ, MapInfo, ODS, OpenFileGDB, Parquet, SHP, SQLite, XLSX, GeoPackage, TopoJSON) e 11 formati di output (CSV, DXF, GeoJSON, GML, GPX, KML, MapInfo, SHP, SQLite, GeoPackage, XLSX). Aggiornata l'interfaccia utente `gui/ui/Tops2pyarchinit.ui` con le nuove liste di formati.
- **EN**: Complete rewrite of `tabs/tops_pyarchinit.py`: removed the old subprocess-based approach in favor of direct Python API. Added auto-detection of available input formats. Now supports 17 input formats (CSV, DXF, GeoJSON, GML, GPX, JSON, KML, KMZ, MapInfo, ODS, OpenFileGDB, Parquet, SHP, SQLite, XLSX, GeoPackage, TopoJSON) and 11 output formats (CSV, DXF, GeoJSON, GML, GPX, KML, MapInfo, SHP, SQLite, GeoPackage, XLSX). Updated the UI `gui/ui/Tops2pyarchinit.ui` with the new format lists.

#### File modificati / Modified files
- `tabs/tops_pyarchinit.py` (riscritto / rewritten)
- `gui/ui/Tops2pyarchinit.ui` (aggiornato / updated)

### fix(toolbar): Correzione sezione DE della toolbar per allineamento con IT/EN/else / Fix DE toolbar section to match IT/EN/else

- **IT**: Corretta la sezione tedesca (`elif l == 'de'`) della toolbar in `pyarchinitPlugin.py` per allinearla alle sezioni IT/EN/else gia' aggiornate. Rimosso il pulsante standalone `self.toolBar.addAction(self.actionSamSegmentation)`. Sostituito il vecchio `manageToolButton` standalone per TOPS con il nuovo `analysisToolButton` che raggruppa: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo. Ora tutte e 4 le sezioni della toolbar (IT/EN/DE/else) hanno la stessa struttura.
- **EN**: Fixed the German (`elif l == 'de'`) toolbar section in `pyarchinitPlugin.py` to match the already-updated IT/EN/else sections. Removed the standalone `self.toolBar.addAction(self.actionSamSegmentation)` button. Replaced the old standalone TOPS `manageToolButton` with the new `analysisToolButton` grouping: SAM Segmentation, Pottery Tools, TOPS, Image Search, GeoArchaeo. All 4 toolbar sections (IT/EN/DE/else) now have the same structure.

#### File modificati / Modified files
- `pyarchinitPlugin.py` (aggiornata sezione DE / updated DE section)

---

## [5.3.8-alpha] - 2026-02-16

### feat(movecost): Integrazione MoveCost completa nella Scheda Sito con interfaccia a 4 tab / Complete MoveCost integration in Site tab with 4-tab interface

- **IT**: Completamente ristrutturata l'integrazione MoveCost nella Scheda Sito (`Site.ui` + `Site.py`). **UI** (`gui/ui/Site.ui`): Rimosso il vecchio dock widget a posizionamento assoluto con 8 pulsanti (371x221px), sostituito con un'interfaccia moderna a 4 schede (420x700px): (1) Tab "Algorithms" con 14 pulsanti organizzati in 3 gruppi (Cost Surface & Paths: movecost, movecost_focalcost, movecost_focalslope, movealloc, movecorr; Corridor & Network Analysis: movecorr, movenetw; Comparison & Ranking: movecomp, moverank) per 7 algoritmi base + 7 varianti poligonali -- aggiunge i nuovi algoritmi movecomp, movenetw, moverank; (2) Tab "Results" con riepilogo costi (statistiche) e visualizzatore R Plot con funzioni refresh/salva; (3) Tab "Export" con opzioni esportazione CSV, HTML e PDF per i dati di analisi dei costi; (4) Tab "Settings" con installatore R Scripts, selettore lingua (5 lingue), controlli organizzazione layer e documentazione help. **Backend** (`tabs/Site.py`): Sostituiti i metodi handler semplici con implementazione completa: wrapper `_mc_run_algorithm()` con auto-organizzazione layer e aggiornamento automatico tab risultati; 14 handler di algoritmo (7 base + 7 poligonali) invece di 8; tab risultati con riepilogo costi e statistiche + auto-rilevamento R plot; esportazione CSV e generazione report HTML; integrazione organizzatore layer (dal plugin movecost); sistema tooltip multilingua (carica dai file JSON i18n del plugin movecost); documentazione help (apre le pagine help del plugin movecost); installatore R script aggiornato: ora copia dalla directory `rscripts/` del plugin movecost (28 script) con fallback agli script propri di pyarchinit.
- **EN**: Completely restructured the MoveCost integration in the Site tab (`Site.ui` + `Site.py`). **UI** (`gui/ui/Site.ui`): Removed the old absolute-positioned dock widget with 8 buttons (371x221px), replaced with a modern 4-tab interface (420x700px): (1) "Algorithms" tab with 14 buttons organized in 3 groups (Cost Surface & Paths: movecost, movecost_focalcost, movecost_focalslope, movealloc, movecorr; Corridor & Network Analysis: movecorr, movenetw; Comparison & Ranking: movecomp, moverank) for 7 base + 7 polygon variants -- adds new movecomp, movenetw, moverank algorithms; (2) "Results" tab with cost summary display (statistics) and R Plot Viewer with refresh/save capabilities; (3) "Export" tab with CSV, HTML and PDF export options for cost analysis data; (4) "Settings" tab with R Scripts installer, language selector (5 languages), layer organization controls and help documentation. **Backend** (`tabs/Site.py`): Replaced simple handler methods with full-featured implementation: `_mc_run_algorithm()` wrapper with auto-organize layers and results tab auto-update; 14 algorithm handlers (7 base + 7 polygon variants) instead of 8; results tab with cost summary and statistics + R plot auto-detection; CSV export and HTML report generation; layer organizer integration (from movecost plugin); multi-language tooltips system (loads from movecost plugin's i18n JSON files); help documentation (opens movecost plugin's help pages); updated R script installer: now copies from movecost plugin's `rscripts/` directory (28 scripts) with fallback to pyarchinit's own scripts.

#### File modificati / Modified files
- `gui/ui/Site.ui` (ristrutturato / restructured)
- `tabs/Site.py` (aggiornato / updated)

---

## [5.3.7-alpha] - 2026-02-16

### fix(i18n): Compilazione .qm mancanti e completamento traduzioni italiane / Compile missing .qm files and complete Italian translations

- **IT**: Compilati i 3 file `.qm` mancanti per rumeno (`ro_RO`), portoghese (`pt_PT`) e greco (`el_GR`) — prima gli utenti di queste lingue vedevano il testo italiano di fallback per tutte le etichette dei form .ui. Completato il file di traduzione italiano (`it_IT.ts`): 2.252 voci vuote riempite (271 tradotte dall'inglese, 1.981 copiate dal sorgente italiano). Ricompilato `it_IT.qm` con 2.826 traduzioni finite. Ora tutti i 10 file `.qm` sono presenti e completi.
- **EN**: Compiled the 3 missing `.qm` files for Romanian (`ro_RO`), Portuguese (`pt_PT`) and Greek (`el_GR`) — previously users of these languages saw Italian fallback text for all .ui form labels. Completed the Italian translation file (`it_IT.ts`): 2,252 empty entries filled (271 translated from English, 1,981 copied from Italian source text). Recompiled `it_IT.qm` with 2,826 finished translations. All 10 `.qm` files now present and complete.

#### File modificati / Modified files
- `i18n/pyarchinit_plugin_it_IT.ts` (completato / completed)
- `i18n/pyarchinit_plugin_it_IT.qm` (ricompilato / recompiled)
- `i18n/pyarchinit_plugin_ro_RO.qm` (nuovo / new)
- `i18n/pyarchinit_plugin_pt_PT.qm` (nuovo / new)
- `i18n/pyarchinit_plugin_el_GR.qm` (nuovo / new)

---

## [5.3.6-alpha] - 2026-02-16

### feat(i18n): Espansione completa CONVERSION_DICT e SORT_ITEMS a 10 lingue / Complete expansion of CONVERSION_DICT and SORT_ITEMS to 10 languages

- **IT**: Espansi `CONVERSION_DICT` e `SORT_ITEMS` da 3 lingue (it/de/en) a 10 lingue (it/de/en/es/fr/ar/ca/ro/pt/el) + fallback else in tutti i 14 file tab. File aggiornati: `Site.py` (8 campi), `Struttura.py` (13 campi), `Tomba.py` (33 campi), `Schedaind.py` (12 campi), `Campioni.py` (4 campi + SORT_ITEMS), `Thesaurus.py` (6 campi), `Documentazione.py` (8 campi), `Tafonomia.py` (33 campi), `US_USM.py` (~85 campi + SORT_ITEMS), `Deteta.py` (~40 campi), `Inv_Lapidei.py` (20 campi), `Inv_Materiali.py` (29 campi + QUANT_ITEMS), `UT.py` (48 campi + SORT_ITEMS). Corretti bug: blocchi `if` separati in Inv_Materiali.py convertiti in catena `elif` corretta. Corretto blocco `else:` → `elif L=='en':` in Inv_Lapidei.py, UT.py, US_USM.py. Corretti refusi inglesi in Inv_Lapidei.py. Espanso `LAYERS_CONVERT_DIZ` in `pyarchinit_pyqgis.py` (33 layer) e aggiunto sistema centralizzato `_GROUP_NAMES` + `_gn()` per 21 nomi di gruppi GIS. Creati 3 file HTML codici thesaurus: `codici_el.html`, `codici_pt.html`, `codici_ro.html`. Totale: ~15.000 nuove righe.
- **EN**: Expanded `CONVERSION_DICT` and `SORT_ITEMS` from 3 languages (it/de/en) to 10 languages (it/de/en/es/fr/ar/ca/ro/pt/el) + else fallback across all 14 tab files. Files updated: `Site.py` (8 fields), `Struttura.py` (13 fields), `Tomba.py` (33 fields), `Schedaind.py` (12 fields), `Campioni.py` (4 fields + SORT_ITEMS), `Thesaurus.py` (6 fields), `Documentazione.py` (8 fields), `Tafonomia.py` (33 fields), `US_USM.py` (~85 fields + SORT_ITEMS), `Deteta.py` (~40 fields), `Inv_Lapidei.py` (20 fields), `Inv_Materiali.py` (29 fields + QUANT_ITEMS), `UT.py` (48 fields + SORT_ITEMS). Bug fixes: separate `if` blocks in Inv_Materiali.py converted to proper `elif` chain. Fixed `else:` → `elif L=='en':` in Inv_Lapidei.py, UT.py, US_USM.py. Fixed English typos in Inv_Lapidei.py. Expanded `LAYERS_CONVERT_DIZ` in `pyarchinit_pyqgis.py` (33 layers) and added centralized `_GROUP_NAMES` + `_gn()` system for 21 GIS group names. Created 3 thesaurus codes HTML files: `codici_el.html`, `codici_pt.html`, `codici_ro.html`. Total: ~15,000 new lines.

#### File modificati / Modified files
- `tabs/Site.py`, `tabs/Struttura.py`, `tabs/Tomba.py`, `tabs/Schedaind.py`
- `tabs/Campioni.py`, `tabs/Thesaurus.py`, `tabs/Documentazione.py`, `tabs/Tafonomia.py`
- `tabs/US_USM.py`, `tabs/Deteta.py`, `tabs/Inv_Lapidei.py`, `tabs/Inv_Materiali.py`, `tabs/UT.py`
- `modules/gis/pyarchinit_pyqgis.py`
- `tabs/codici_el.html`, `tabs/codici_pt.html`, `tabs/codici_ro.html`

---

## [5.3.5-alpha] - 2026-02-16

### feat(i18n): Thesaurus codes HTML per greco, portoghese e rumeno / Thesaurus codes HTML for Greek, Portuguese and Romanian

- **IT**: Creati 3 nuovi file HTML di codici thesaurus tradotti dalla versione inglese: `tabs/codici_el.html` (Greco moderno), `tabs/codici_pt.html` (Portoghese europeo), `tabs/codici_ro.html` (Rumeno). Ogni file contiene 12 sezioni tabellari (Sito, US/USM, Struttura, Sepoltura, Inventario Materiali, Campioni, Individui, Documentazione, TMA, Ceramica, UT, Fauna) con intestazioni di colonna, titoli di sezione, descrizioni dei campi e valori di esempio tradotti. Struttura HTML, CSS e nomi tecnici dei campi database mantenuti identici alla versione inglese. ~300 righe per file.
- **EN**: Created 3 new translated thesaurus codes HTML files from the English version: `tabs/codici_el.html` (Modern Greek), `tabs/codici_pt.html` (European Portuguese), `tabs/codici_ro.html` (Romanian). Each file contains 12 table sections (Site, SU/WSU, Structure, Burial, Finds Inventory, Samples, Individuals, Documentation, TMA, Pottery, UT, Fauna) with translated column headers, section titles, field descriptions and example values. HTML structure, CSS and technical database field names kept identical to the English version. ~300 lines per file.

#### File modificati / Modified files
- `tabs/codici_el.html` (nuovo / new)
- `tabs/codici_pt.html` (nuovo / new)
- `tabs/codici_ro.html` (nuovo / new)

---

## [5.3.4-alpha] - 2026-02-16

### feat(i18n): CONVERSION_DICT, QUANT_ITEMS e SORT_ITEMS multilingua in Inv_Materiali / Multilingual CONVERSION_DICT, QUANT_ITEMS and SORT_ITEMS in Inv_Materiali

- **IT**: Aggiunti blocchi `CONVERSION_DICT`, `QUANT_ITEMS` e `SORT_ITEMS` per 7 lingue aggiuntive (es, fr, ar, ca, ro, pt, el) nel file `tabs/Inv_Materiali.py`. Corretta la catena di `if` separati: le istruzioni `if L =='de':` e `if L =='en':` sono state convertite in `elif` per formare una catena corretta `if/elif/else`. Aggiunto blocco `else:` finale con fallback inglese. 29 campi tradotti per ogni lingua (sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione, descrizione, area, us, lavato, nr_cassa, luogo_conservazione, stato_conservazione, datazione_reperto, forme_minime, forme_massime, totale_frammenti, corpo_ceramico, rivestimento, diametro_orlo, peso, tipo, eve_orlo, repertato, diagnostico, n_reperto, tipo_contenitore, struttura, years). QUANT_ITEMS include 9 voci tradotte per lingua. Totale: ~580 nuove righe.
- **EN**: Added `CONVERSION_DICT`, `QUANT_ITEMS` and `SORT_ITEMS` blocks for 7 additional languages (es, fr, ar, ca, ro, pt, el) in `tabs/Inv_Materiali.py`. Fixed separate `if` statements: `if L =='de':` and `if L =='en':` were converted to `elif` to form a proper `if/elif/else` chain. Added final `else:` block with English fallback. 29 fields translated per language (site, inventory_number, artefact_type, material_class, definition, description, area, stratigraphic_unit, washed, box, place_of_conservation, status_of_conservation, artefact_period, min_shape, max_shape, total_fragments, body_sherds, coating, rim_diameter, weight, type, eve_rim, reperted, diagnostic, ra, container_type, structure, years). QUANT_ITEMS includes 9 translated entries per language. Total: ~580 new lines.

#### File modificati / Modified files
- `tabs/Inv_Materiali.py` (aggiornato / updated)

---

## [5.3.3-alpha] - 2026-02-16

### feat(i18n): CONVERSION_DICT e SORT_ITEMS multilingua in Inv_Lapidei / Multilingual CONVERSION_DICT and SORT_ITEMS in Inv_Lapidei

- **IT**: Aggiunti blocchi `CONVERSION_DICT` e `SORT_ITEMS` per 7 lingue aggiuntive (es, fr, ar, ca, ro, pt, el) nel file `tabs/Inv_Lapidei.py`. Il blocco `else:` (fallback inglese) è stato convertito in `elif L=='en':` esplicito, seguito da 7 nuovi blocchi `elif` per ciascuna lingua e un blocco `else:` finale che usa l'inglese come default. 19 campi tradotti per ogni lingua (sito, scheda_numero, collocazione, oggetto, tipologia, materiale, d_letto_posa, d_letto_attesa, toro, spessore, larghezza, lunghezza, h, descrizione, lavorazione_e_stato_di_conservazione, confronti, cronologia, bibliografia, compilatore). Corretti refusi nelle etichette inglesi: "Thikness" -> "Thickness", "Weight" -> "Width", "Lenght" -> "Length", "presevation" -> "preservation", "Comparision" -> "Comparisons". Totale: ~370 nuove righe.
- **EN**: Added `CONVERSION_DICT` and `SORT_ITEMS` blocks for 7 additional languages (es, fr, ar, ca, ro, pt, el) in `tabs/Inv_Lapidei.py`. The `else:` block (English fallback) was converted to an explicit `elif L=='en':`, followed by 7 new `elif` blocks for each language and a final `else:` block defaulting to English. 19 fields translated per language (site, form_number, placement, object, typology, material, bed_pose, waiting_bed, toro, thickness, width, length, h, description, processing_and_preservation_state, comparisons, chronology, bibliography, author). Fixed English label typos: "Thikness" -> "Thickness", "Weight" -> "Width", "Lenght" -> "Length", "presevation" -> "preservation", "Comparision" -> "Comparisons". Total: ~370 new lines.

#### File modificati / Modified files
- `tabs/Inv_Lapidei.py` (aggiornato / updated)

---

## [5.3.2-alpha] - 2026-02-16

### feat(i18n): CONVERSION_DICT e SORT_ITEMS multilingua in Documentazione e Tafonomia / Multilingual CONVERSION_DICT and SORT_ITEMS in Documentazione and Tafonomia

- **IT**: Aggiunti blocchi `CONVERSION_DICT` e `SORT_ITEMS` per 7 lingue aggiuntive (es, fr, ar, ca, ro, pt, el) nei file `Documentazione.py` e `Tafonomia.py`. Il blocco `else:` (fallback inglese) è stato convertito in `elif L=='en':` esplicito, seguito da 7 nuovi blocchi `elif` per ciascuna lingua e un blocco `else:` finale che usa l'inglese come default. In `Documentazione.py`: 8 campi tradotti per ogni lingua (sito, nome_doc, data, tipo_documentazione, sorgente, scala, disegnatore, note). In `Tafonomia.py`: 33 campi tradotti per ogni lingua (sito, nr_scheda_taf, sigla_struttura, nr_struttura, nr_individuo, rito, descrizione, interpretazione, segnacoli, canale_libatorio, oggetti_rinvenuti, stato_conservazione, copertura, contenitore_resti, orientamento_asse/azimut, corredo, lunghezza/posizione_scheletro, cranio, arti_superiori/inferiori, completo, disturbato, connessione, caratteristiche, periodo/fase iniziale/finale, datazione_estesa). Totale: ~560 nuove righe in Documentazione.py, ~1050 nuove righe in Tafonomia.py.
- **EN**: Added `CONVERSION_DICT` and `SORT_ITEMS` blocks for 7 additional languages (es, fr, ar, ca, ro, pt, el) in `Documentazione.py` and `Tafonomia.py`. The `else:` block (English fallback) was converted to an explicit `elif L=='en':`, followed by 7 new `elif` blocks for each language and a final `else:` block defaulting to English. In `Documentazione.py`: 8 fields translated per language (site, doc_name, date, documentation_type, source, scale, draftsman, notes). In `Tafonomia.py`: 33 fields translated per language (site, taphonomy_sheet_nr, structure_acronym, structure_nr, individual_nr, rite, description, interpretation, markers, libation_channel, external_objects, conservation_state, covering_type, remains_container_type, axis/azimuth_orientation, grave_goods, skeleton_length/position, cranium/upper_limbs/lower_limbs position, complete, disturbed, in_connection, characteristics, initial/final period/phase, extended_dating). Total: ~560 new lines in Documentazione.py, ~1050 new lines in Tafonomia.py.

#### File modificati / Modified files
- `tabs/Documentazione.py` (aggiornato / updated)
- `tabs/Tafonomia.py` (aggiornato / updated)

---

## [5.3.1-alpha] - 2026-02-15

### feat(db): Estensione dati i18n: tabelle aggiuntive + layer GIS / Extend i18n example data: additional tables + GIS layers

- **IT**: Esteso lo script `scripts/populate_i18n_example_data.py` per popolare 6 tabelle aggiuntive in tutte le 10 lingue: `struttura_table` (10 record: edifici, focolare, muri, pavimenti, fossa, spoliazione), `tomba_table` (10 sepolture: inumazioni e cremazione, vari tipi), `individui_table` (10 individui con sesso, età, posizioni), `pottery_table` (10 ceramiche: maiolica, invetriata, grezza, ingobbiata), `inventario_materiali_table` (10 reperti: ceramica, metallo, vetro, osso, moneta, laterizio). Replicati i layer GIS per 9 lingue aggiuntive: `pyunitastratigrafiche` (482×10=4820 righe), `pyunitastratigrafiche_usm` (19×10=190 righe), `pyarchinit_quote` (70×10=700 righe) con traduzione dei tipi di materiale (tipo_us_s) e delle abbreviazioni unità tipo. Gestione trigger SpatiaLite per pyarchinit_quote. Aggiunti ~25 dizionari di traduzione per i nuovi campi. Totale: 500 record per le nuove tabelle (100 ciascuna × 5 tabelle), 5710 geometrie GIS.
- **EN**: Extended `scripts/populate_i18n_example_data.py` to populate 6 additional tables across all 10 languages: `struttura_table` (10 records: buildings, hearth, walls, floors, pit, robber trench), `tomba_table` (10 burials: inhumations and cremation, various types), `individui_table` (10 individuals with sex, age, positions), `pottery_table` (10 ceramics: majolica, glazed, coarse, slipped), `inventario_materiali_table` (10 finds: ceramic, metal, glass, bone, coin, brick). Replicated GIS layers for 9 additional languages: `pyunitastratigrafiche` (482×10=4820 rows), `pyunitastratigrafiche_usm` (19×10=190 rows), `pyarchinit_quote` (70×10=700 rows) with translation of material types (tipo_us_s) and unit type abbreviations. Handled SpatiaLite geometry triggers for pyarchinit_quote. Added ~25 translation dictionaries for new fields. Total: 500 records for new tables (100 each × 5 tables), 5710 GIS geometries.

#### File modificati / Modified files
- `scripts/populate_i18n_example_data.py` (aggiornato / updated)
- `resources/dbfiles/pyarchinit_db.sqlite` (aggiornato / updated)

---

## [5.3.0-alpha] - 2026-02-15

### feat(db): Dati di esempio i18n per 10 lingue nel template SQLite / i18n example data for 10 languages in template SQLite

- **IT**: Creato script `scripts/populate_i18n_example_data.py` che popola il database template `resources/dbfiles/pyarchinit_db.sqlite` con dati di esempio tradotti per tutte le 10 lingue supportate (IT, EN, DE, ES, FR, AR, CA, RO, PT, EL). Partendo dai 51 record US italiani esistenti ("Scavo archeologico"), vengono generati 9 siti aggiuntivi con nomi localizzati (es. "Archaeological Excavation", "Archäologische Ausgrabung", "Αρχαιολογική Ανασκαφή"). Per ogni sito: 51 record US con termini di relazione tradotti (rapporti/rapporti2), abbreviazioni unità tipo localizzate (US→SU/SE/UE/ΣΜ, USM→WSU/MSE/UEM/USZ/ΤΣΜ), campi testuali tradotti (d_stratigrafica, d_interpretativa, formazione, stato_di_conservazione, colore, consistenza, metodo_di_scavo, inclusi, documentazione) e testi lunghi (descrizione/interpretazione) con sostituzione terminologica. 12 record periodizzazione con descrizioni cronologiche tradotte. Totale: 510 US, 120 periodizzazioni, 11 siti. Lo script utilizza il modulo centrale `pyarchinit_i18n_stratigraphic` per i termini di relazione e le abbreviazioni.
- **EN**: Created script `scripts/populate_i18n_example_data.py` that populates the template database `resources/dbfiles/pyarchinit_db.sqlite` with translated example data for all 10 supported languages (IT, EN, DE, ES, FR, AR, CA, RO, PT, EL). Starting from the existing 51 Italian US records ("Scavo archeologico"), 9 additional sites are generated with localized names (e.g. "Archaeological Excavation", "Archäologische Ausgrabung", "Αρχαιολογική Ανασκαφή"). For each site: 51 US records with translated relationship terms (rapporti/rapporti2), localized unit type abbreviations (US→SU/SE/UE/ΣΜ, USM→WSU/MSE/UEM/USZ/ΤΣΜ), translated text fields (d_stratigrafica, d_interpretativa, formazione, stato_di_conservazione, colore, consistenza, metodo_di_scavo, inclusi, documentazione) and long texts (descrizione/interpretazione) with term replacement. 12 periodizzazione records with translated chronological descriptions. Total: 510 US, 120 periods, 11 sites. The script uses the central `pyarchinit_i18n_stratigraphic` module for relationship terms and abbreviations.

#### File modificati / Modified files
- `scripts/populate_i18n_example_data.py` (nuovo / new)
- `resources/dbfiles/pyarchinit_db.sqlite` (aggiornato / updated)

---

## [5.2.9-alpha] - 2026-02-15

### refactor(i18n): Integrazione modulo i18n centrale per relazioni stratigrafiche in 5 file / Integrate central i18n module for stratigraphic relationships in 5 files

- **IT**: Aggiornati 5 file per utilizzare il modulo centrale `pyarchinit_i18n_stratigraphic` al posto di termini di relazione stratigrafica hardcoded. In `pyarchinit_matrix_exp.py`: le etichette della legenda "Contemporaneo" / "Same as" / "Sama as" ora utilizzano `RELATIONSHIPS[lang][0]` per la localizzazione corretta in tutte le 10 lingue. In `pyarchinit_pyqgis.py`: le liste `rel_covers_*` e `rel_equals_*` per 6 lingue sostituite con i group set del modulo centrale (`COVERS_GROUP`, `FILLS_GROUP`, `CUTS_GROUP`, `ABUTS_GROUP`, `SAME_AS_GROUP`, `CONNECTED_GROUP`) che coprono automaticamente tutte le 10 lingue. In `pyarchinit_db_manager.py`: i filtri SQL `select_not_like_from_db_sql()` per 3 lingue (it/en/de) sostituiti con filtri generati dinamicamente dai group set, coprendo tutte le 10 lingue. In `skatch_gpt_US.py`: il prompt di analisi Harris Matrix con termini italiani hardcoded ora utilizza `RELATIONSHIPS[lang]` per inserire i termini localizzati. In `Struttura.py`: il blocco `valuesRapporti` if/elif/else per 3 lingue (it/de/en) sostituito con lookup dinamico da `RELATIONSHIPS` + dizionario `_STRUTTURA_EXTRA` per i termini specifici delle strutture, ora con supporto per tutte le 10 lingue.
- **EN**: Updated 5 files to use the central `pyarchinit_i18n_stratigraphic` module instead of hardcoded stratigraphic relationship terms. In `pyarchinit_matrix_exp.py`: legend labels "Contemporaneo" / "Same as" / "Sama as" now use `RELATIONSHIPS[lang][0]` for correct localization across all 10 languages. In `pyarchinit_pyqgis.py`: per-language `rel_covers_*` and `rel_equals_*` lists for 6 languages replaced with central module group sets (`COVERS_GROUP`, `FILLS_GROUP`, `CUTS_GROUP`, `ABUTS_GROUP`, `SAME_AS_GROUP`, `CONNECTED_GROUP`) that automatically cover all 10 languages. In `pyarchinit_db_manager.py`: SQL filters in `select_not_like_from_db_sql()` for 3 languages (it/en/de) replaced with dynamically generated filters from group sets, covering all 10 languages. In `skatch_gpt_US.py`: Harris Matrix analysis prompt with hardcoded Italian terms now uses `RELATIONSHIPS[lang]` to insert localized terms. In `Struttura.py`: `valuesRapporti` if/elif/else block for 3 languages (it/de/en) replaced with dynamic lookup from `RELATIONSHIPS` + `_STRUTTURA_EXTRA` dict for structure-specific terms, now supporting all 10 languages.

#### File modificati / Modified files
- `modules/utility/pyarchinit_matrix_exp.py`
- `modules/gis/pyarchinit_pyqgis.py`
- `modules/db/pyarchinit_db_manager.py`
- `modules/utility/skatch_gpt_US.py`
- `tabs/Struttura.py`

---

## [5.2.8-alpha] - 2026-02-15

### refactor(pdf): Pulizia codice orfano in pyarchinit_exp_USsheet_pdf.py / Remove orphan code from pyarchinit_exp_USsheet_pdf.py

- **IT**: Rimossi ~983 righe di codice orfano dal file `pyarchinit_exp_USsheet_pdf.py`. Eliminati i due metodi placeholder `_unzip_compat_placeholder()` e tutti i blocchi `len==4`, `len==3`, `len==2` rimasti dopo la sostituzione dei vecchi metodi `unzip_rapporti_stratigrafici()` con la nuova versione unificata basata sui group set del modulo i18n centrale (`pyarchinit_i18n_stratigraphic`). I metodi `unzip_rapporti_stratigrafici_de()` e `unzip_rapporti_stratigrafici_en()` (4 istanze totali, 2 per classe) sono stati sostituiti con one-liner che delegano al metodo unificato `unzip_rapporti_stratigrafici()`. Sintassi Python verificata dopo le modifiche.
- **EN**: Removed ~983 lines of orphan code from `pyarchinit_exp_USsheet_pdf.py`. Deleted two `_unzip_compat_placeholder()` methods and all leftover `len==4`, `len==3`, `len==2` blocks remaining after replacing the old `unzip_rapporti_stratigrafici()` methods with the new unified version based on group sets from the central i18n module (`pyarchinit_i18n_stratigraphic`). The `unzip_rapporti_stratigrafici_de()` and `unzip_rapporti_stratigrafici_en()` methods (4 total instances, 2 per class) were replaced with one-liners that delegate to the unified `unzip_rapporti_stratigrafici()`. Python syntax verified after changes.

#### File modificati / Modified files
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`

---

## [5.2.7-alpha] - 2026-02-15

### feat(i18n): Aggiunta supporto lingua Greco Moderno (el_GR) / Added Modern Greek (el_GR) language support

- **IT**: Aggiunta completa del supporto per la lingua Greca Moderna (Ελληνικά) al plugin, decima lingua supportata. Modifiche effettuate: aggiunta `'el': 'el_GR'` al `LOCALE_MAPPING` in `pyarchinitPlugin.py`; aggiunta `'el': 'Ελληνικά'` a `SUPPORTED_LANGUAGES` e relativi `TUTORIALS_METADATA` + `UI_LABELS` in `Tutorial_viewer.py` e `pyarchinitDockWidget.py`; aggiunta `'el'` a `SUPPORTED_LANGUAGES` in `Fauna.py`; aggiunta voce `"EL"` ai dizionari `LANG` in tutti i 13 file tab (US_USM, Tma, Pottery, Tomba, Thesaurus, Tafonomia, Struttura, Site, Schedaind, Inv_Materiali, Inv_Lapidei, Documentazione, Campioni); creazione di 32 file tutorial tradotti in greco in `docs/tutorials/el/` con terminologia archeologica appropriata (ΣΜ per Στρωματογραφική Μονάδα, ΤΝ per Τεχνητή Νοημοσύνη ecc.); creazione file i18n `pyarchinit_plugin_el_GR.ts`; aggiornamento di tutti i 7 script di traduzione con voci `el_GR`; aggiornamento `build_docs.py`, `conf.py` e `metadata.txt`.
- **EN**: Complete addition of Modern Greek (Ελληνικά) language support to the plugin, now the tenth supported language. Changes made: added `'el': 'el_GR'` to `LOCALE_MAPPING` in `pyarchinitPlugin.py`; added `'el': 'Ελληνικά'` to `SUPPORTED_LANGUAGES` and related `TUTORIALS_METADATA` + `UI_LABELS` in `Tutorial_viewer.py` and `pyarchinitDockWidget.py`; added `'el'` to `SUPPORTED_LANGUAGES` in `Fauna.py`; added `"EL"` entry to `LANG` dicts in all 13 tab files (US_USM, Tma, Pottery, Tomba, Thesaurus, Tafonomia, Struttura, Site, Schedaind, Inv_Materiali, Inv_Lapidei, Documentazione, Campioni); created 32 Greek tutorial files in `docs/tutorials/el/` with proper archaeological terminology (ΣΜ for Στρωματογραφική Μονάδα, ΤΝ for Τεχνητή Νοημοσύνη etc.); created i18n file `pyarchinit_plugin_el_GR.ts`; updated all 7 translation scripts with `el_GR` entries; updated `build_docs.py`, `conf.py` and `metadata.txt`.

#### File modificati / Modified files
- `pyarchinitPlugin.py`
- `tabs/Tutorial_viewer.py`
- `pyarchinitDockWidget.py`
- `tabs/Fauna.py`
- `tabs/US_USM.py`, `tabs/Tma.py`, `tabs/pyarchinit_Pottery_mainapp.py`
- `tabs/Tomba.py`, `tabs/Thesaurus.py`, `tabs/Tafonomia.py`, `tabs/Struttura.py`
- `tabs/Site.py`, `tabs/Schedaind.py`, `tabs/Inv_Materiali.py`, `tabs/Inv_Lapidei.py`
- `tabs/Documentazione.py`, `tabs/Campioni.py`
- `docs/tutorials/el/` (32 file)
- `i18n/pyarchinit_plugin_el_GR.ts`
- `scripts/update_translations.py`, `scripts/update_struttura_translations.py`
- `scripts/update_fauna_translations.py`, `scripts/update_other_translations.py`
- `scripts/add_sync_translations.py`, `scripts/auto_translate_ts.py`
- `scripts/translate_ts_complete.py`
- `docs/tutorials/build_docs.py`
- `metadata.txt`

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
