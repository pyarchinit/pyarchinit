# Narrativa con l'AI nel pannello della matrice — disegno

Data: 2026-10-12 · ramo `Stratigraph_00001` · plugin 5.13.105-alpha → 5.13.106-alpha · s3dgraphy 1.6.0.dev45 (in `ext_libs`).

## Da dove viene

Enzo, 12 ottobre 2026: «dato che l'AI c'è perché non inseriamo anche la narrativa come fa EMStudio? nel widget dell'Extended Matrix, una volta generato l'em.json, se abbiamo l'AI settata — non settiamo da lì, la facciamo leggere dalle altre parti in cui è settata — gli facciamo fare la narrativa».

La matrice interattiva (B dello stesso brainstorming) è **rinviata** per sua decisione: questo documento copre solo la narrativa (A).

## Decisioni prese nel brainstorming

1. **Nessuna impostazione AI nuova.** Si legge la configurazione già salvata dalle altre finestre (`LLMProviderManager.load_config`), nell'ordine: Relazione AI della scheda US (`us_report`), interrogazione AI del database (`rag_query`), relazione Palimpsest (`palimpsest_report`), testo in SQL (`text2sql`). Vale la prima con un modello e, se il fornitore la vuole, una chiave. Il pannello dice quale modello usa e da dove.
2. **Lingua dell'interfaccia di QGIS** per i testi del pannello (it/en) e per la prosa generata. Lo scheletro della libreria conosce italiano e inglese; per le altre lingue scrive i titoli in inglese.
3. **Capitoli generati: epoche e attività**, cioè quelli che la libreria sa istruire (`build_narrative_generation_context` accetta un `EpochNode` o un `ActivityNodeGroup`). «Presentazione» e «Dove si trova» restano segnaposto per l'autore: nel grafo non c'è niente da cui scriverli senza inventare.
4. **Convalida dentro pyArchInit**, scegliendo l'autore umano fra quelli del grafo (gli schedatori ci sono già come `AuthorNode`), o scrivendo un nome nuovo.
5. **Un file solo.** «Vedi la matrice» esporta in `<home>/pyarchinit_EM_folder/<sito>.em.json`, lo stesso file di «Esporta in em.json» e di EMStudio, invece che in una cartella temporanea. A ogni riesportazione dal database **la narrativa si conserva** con i nodi che la sostengono.

## Obiettivo

Dal pannello della matrice, su un sito esportato in em.json: preparare i capitoli, far scrivere all'AI già impostata la prosa dei capitoli di epoca e di attività, leggerla, convalidarla con un autore umano, esportarla in HTML o DOCX e aprirla in EMStudio — scrivendo tutto nello stesso em.json che EMStudio legge, nel formato della libreria (NarrativeNode, blocchi `ai_draft` attribuiti, prompt registrato come estrattore).

## Non obiettivi

- Modificare la prosa a mano dentro pyArchInit: si fa in EMStudio.
- Generare «Presentazione» e «Dove si trova».
- Figure negli export (la matrice per epoca): la libreria le accetta, non le produciamo ora; gli embed visivi restano segnaposto nel documento esportato.
- Conservare alla riesportazione **altre** modifiche fatte in EMStudio al file (posizioni, descrizioni riscritte): come oggi, non sopravvivono. Si conserva la narrativa.
- Stimare i costi in token.
- Il flusso con EMStudio aperto sullo stesso file: chi scrive per ultimo vince; il tutorial dice di chiudere EMStudio prima di generare.

## Che cosa fa la libreria, misurato il 12 ottobre

- `s3dgraphy.narrative.build_narrative(graph, "site_story", lang=, existing=)` restituisce una `NarrativeNode` **non aggiunta al grafo** (va aggiunta da noi) con: Presentazione (canonico), Dove si trova (solo se il grafo ha una posizione), un capitolo per epoca che ha unità (`anchor` = id dell'epoca, un segnaposto `[da scrivere: …]` e un embed `us` per unità), un capitolo per attività. Con `existing=` **fonde**: i capitoli canonici non si toccano, quelli ancorati si estendono, i nuovi si aggiungono, nessuna prosa sparisce.
- `s3dgraphy.api.build_narrative_generation_context(graph, anchor)` dà il briefing: `activity` (l'àncora), `actions` (le unità: id, nome, tipo, descrizione, epoche, evidenza), `epochs`, `sources`, `constraints` (cinque regole di stile). **Non porta i rapporti fra le unità** e l'ordine è stratigrafico solo per gli archi `is_after`, che le nostre schede hanno di rado: per la nostra esportazione l'ordine è quello di inserimento.
- `s3dgraphy.narrative.write_ai_draft(graph, target, text, model=, version=, date=, prompt=, narrative_id=, chapter_title=, sources=)` scrive il blocco `ai_draft` nel capitolo ancorato a `target`, riusa l'`AuthorAINode` del modello (`AI.<modello>`), registra il prompt come `ExtractorNode` (`EXT.prompt.<sha1>`) collegato alle fonti. L'omonima in `s3dgraphy.api` non accetta `sources`: si usa quella del pacchetto e si chiama `s3dgraphy.language.stamp_born_nodes` dopo, come fa l'api.
- Le menzioni `[[id]]` nella prosa contano come citazioni; gli esportatori le scrivono col nome del nodo; `narrative.unresolved_refs(graph)` elenca quelle che non risolvono.
- `endorse_block` / `endorse_narrative(graph, narrative, author_id)` vogliono un `AuthorNode` umano presente nel grafo (ORCID non richiesto); lo stato del blocco diventa `ai_endorsed`.
- `s3dgraphy.api.export_narrative(graph, narrative_id, "html"|"docx", include_unvalidated=True)` → `{"format","payload","excluded"}`; HTML 3,4 KB e DOCX 37 KB sul grafo di prova (python-docx 1.1.2 è in `ext_libs`). Senza `include_unvalidated` le bozze non convalidate **non entrano** nell'export.
- `s3dgraphy.container.load_container_file(path)` → `(Container, warnings)`, `container.graphs`, `container.active()`; `save_container_file(container, path, bump=True)` fa avanzare la revisione del progetto se il contenuto è cambiato.
- Il giro em.json → rilettura conserva capitoli, stati, autore AI, estrattore e convalide (provato).
- Sul DB di prova (`resources/dbfiles/pyarchinit_db.sqlite`, sito arabo, 44 unità): esportazione in 0,5 s, 81 nodi, 585 archi, epoche `epoch_<periodo>_<fase>`, autori `author::<nome>`, 2 documenti, 0 attività, 11 capitoli; il `data` delle unità porta `unita_tipo`, `d_stratigrafica`, `d_interpretativa`, `periodo/fase`, `datazione_estesa`, `attivita`, `struttura`, `saggio`, `ambient`.

## Architettura

Tre pezzi, dal puro all'impuro.

### 1. `modules/s3dgraphy/em_narrative.py` — puro, niente Qt, niente rete

Tutta la logica, con la chiamata al modello **iniettata** (`chat(messages) -> str | (str, truncated)`), così i test la provano con un modello finto e il modulo non importa nessun SDK.

- `SCOPES`, `llm_config(load=None) -> (cfg, scope) | None`, `scope_label(scope, lang)`, `describe_config(cfg, scope, lang)`.
- `load_project(path) -> (Container, warnings)`; `save_project(container, path)` scrive in `<path>.tmp`, **rilegge**, poi `os.replace`: un errore a metà non lascia un em.json rotto.
- `scaffold(graph, lang) -> NarrativeNode`: `build_narrative(..., existing=quella del grafo)`, aggiunge il nodo se nuovo. La lingua di una narrativa esistente è la sua (`data.lang`), non quella dell'interfaccia di oggi.
- `is_placeholder(block)`, `chapter_status(chapter)` ∈ {`empty`, `ai_draft`, `ai_endorsed`, `human`} (il peggiore vince: una bozza non convalidata rende il capitolo «bozza AI»), `chapter_text(chapter, name_of)` (prosa non segnaposto, menzioni scritte col nome), `can_generate(graph, chapter)` (àncora epoca o attività, non canonico), `chapters_to_generate(graph, narrative, only_empty)`.
- `briefing(graph, anchor)`: il contesto della libreria **arricchito**: per ogni unità i campi della scheda da `data` (tipo, definizioni, interpretazione, periodo/fase, datazione, attività, struttura, saggio, ambiente), le epoche senza doppioni, i **rapporti** con le altre unità (tipo, soggetto, oggetto, con i nomi), e le unità **dalla più antica alla più recente** secondo gli archi `overlies/covers/cuts/fills/abuts/leans_on/is_after` (la sorgente è più recente). Oltre `MAX_ACTIONS` (80) unità si tengono le prime 80 in ordine e si dice quante mancano.
- `messages(brief, lang)`: sistema (ruolo: archeologo che scrive la storia del sito nella lingua chiesta; i cinque vincoli della libreria; «nomina le unità con `[[id]]` usando l'id fornito»; uno-tre paragrafi; «se il contesto è povero, dillo») + utente (intestazione del capitolo e il briefing in JSON).
- `prompt_record(brief, lang)`: il testo che va nell'estrattore: il sistema più l'intestazione del capitolo con gli id delle unità — non il JSON intero, che gonfierebbe il file.
- `normalize_mentions(text, graph)`: `[[x]]` con `x` id del grafo resta; con `x` nome di un'unità diventa `[[id]]`; altrimenti si tolgono le parentesi.
- `generate_chapter(graph, narrative, chapter, *, chat, model, lang, now, version) -> Outcome(anchor, title, ok, text, error, truncated)`: briefing → messaggi → `chat` → normalizza → `write_ai_draft` con le fonti del briefing → `stamp_born_nodes`. Testo vuoto o eccezione = esito negativo, mai un'eccezione fuori.
- `forget_ai_drafts(chapter)`: toglie i blocchi AI **non convalidati** (i convalidati restano).
- `generate(container, *, chat, model, lang, anchors=None, progress, cancelled) -> Report`: `anchors=None` genera i capitoli vuoti di tutti i grafi del contenitore (uno per saggio nell'esportazione divisa); `anchors` dati = rigenerazione di quei capitoli (prima `forget_ai_drafts`). Un capitolo fallito non ferma gli altri; `cancelled()` si legge prima di ogni capitolo.
- `human_authors(graph)`, `add_author(graph, name)`, `endorse(graph, narrative, author_id, anchor=None) -> int`.
- `export_file(graph, narrative, fmt, path)` con `include_unvalidated=True` (le bozze entrano, segnate dalla libreria con ⚠).
- `overview(container, lang) -> [ChapterView(graph_id, narrative_id, index, title, anchor, status, text, can_generate, truncated)]`.
- `carry_over(previous_graphs, fresh_graphs, lang) -> int`: per ogni grafo nuovo con lo stesso id nel file precedente, porta la `NarrativeNode`, gli autori (AI e umani citati da `authored_by`/`validated_by`), gli estrattori dei prompt (`EXT.prompt.*`) e gli archi `has_author` ed `extracted_from` le cui due estremità esistono; poi `build_narrative(existing=)` per dare un capitolo alle epoche nuove.
- Messaggi it/en con `set_language`/`msg`, come i moduli SAM.

### 2. `modules/s3dgraphy/em_narrative_tab.py` — la scheda «Narrativa», Qt

- `build_tab(parent, iface) -> QWidget` (objectName `narrativa`): in alto `stato` (modello e provenienza, o la frase su dove impostare l'AI); elenco `capitoli` (titolo · stato in parole; nell'esportazione per saggi il nome del grafo in testa al gruppo); `testo` (`QTextBrowser`, menzioni col nome); riga di bottoni **Genera con l'AI** (tutti i capitoli vuoti) · **Rigenera capitolo** · **Convalida…** (questo capitolo / tutti); seconda riga **Prepara i capitoli** (solo scheletro, senza AI) · **Esporta…** (HTML/DOCX) · **Apri in EMStudio**; `avanzamento` («capitolo 3 di 9 · Età romana») con **Annulla**.
- `show_file(widget, path)`: ricarica l'elenco dal file; abilita i bottoni secondo `llm_config()` e la presenza di una narrativa.
- `NarrativeThread(QThread)`: carica il progetto, `chat` = `LLMProviderManager.stream_chat(cfg, messages, max_tokens=MAX_TOKENS, meta=meta)` concatenato, con `meta["truncated"]`; `generate`; `save_project` se ha scritto almeno un capitolo; segnali `progress(int, int, str)` e `finished_ok(bool, str)`.
- Convalida: `QInputDialog.getItem` editabile con gli autori umani del grafo; un nome nuovo crea l'`AuthorNode`.
- Apri in EMStudio: `em_export.open_in_emstudio(path)`; se non è installato, la barra dei messaggi rimanda alla voce di menu «Installa EMStudio…».
- Stringhe it/en in `_L` con `_t()`, lingua da `locale/userLocale` come la finestra SAM.

### 3. Cablaggio

- `em_matrix_panel.open_in_panel(iface, path, title, conn_str, tab=None)`: la colonna di destra diventa un `QTabWidget` (`schede`) con «Unità» (quello che c'è oggi) e «Narrativa» (`build_tab`); a ogni apertura `show_file`; `tab="narrativa"` la porta davanti.
- `em_matrix_model.read_em_json`: i nodi di supporto della narrativa (`node_type` `narrative` e `author_ai`, estrattori con id `EXT.prompt.*`) **non entrano** nel disegno né negli avvisi — altrimenti dopo la generazione il prompt comparirebbe come nodo di paradati appeso ai documenti (`extracted_from` è fra i tipi disegnati).
- `em_export.export_site(..., keep_narrative=True)`: se il file di destinazione esiste e si legge, `carry_over` prima di scrivere; un avviso dice «narrativa conservata (N capitoli)». Un file che non si legge non ferma l'esportazione: avviso e si va avanti.
- `pyarchinitPlugin`: `_ask_split(site, conn_str)` estratto da `_run_em_export` e usato anche da `_run_em_matrix_view`, che esporta in `pyarchinit_EM_folder` (niente `tempfile`, niente `_matrice_temp`); «Esporta in em.json» chiude con tre bottoni: **Apri in EMStudio**, **Narrativa con l'AI** (solo se `llm_config()` trova qualcosa; apre il pannello sulla scheda Narrativa), **Chiudi**.

## Flusso

1. Menu «Vedi la matrice» (o «Esporta in em.json» → «Narrativa con l'AI»): esportazione in `pyarchinit_EM_folder/<sito>.em.json`, con la narrativa precedente conservata; pannello aperto.
2. Scheda Narrativa: senza narrativa nel file, l'elenco dice «Nessuna narrativa: “Prepara i capitoli” o “Genera con l'AI” la creano» e quante epoche e attività diventerebbero capitoli.
3. «Genera con l'AI»: thread; per ogni capitolo vuoto di epoca/attività: briefing → modello → blocco `ai_draft`; salvataggio; riepilogo «7 capitoli generati, 1 fallito: <motivo>»; elenco ricaricato.
4. Lettura, «Rigenera capitolo» per uno solo, «Convalida…» con l'autore umano, «Esporta…», «Apri in EMStudio»: EMStudio mostra la stessa narrativa nella sua scheda Narrative.
5. Riesportazione dal DB (anche dalla scheda US): la narrativa resta, le epoche nuove ricevono un capitolo.

## Errori, detti all'utente

| Caso | Che cosa succede |
|---|---|
| nessuna AI impostata | «Genera» e «Rigenera» spenti; `stato` dice dove impostarla (scheda US → Relazione AI) |
| il modello sbaglia su un capitolo | esito negativo con il messaggio del fornitore (già leggibile da `_annotate_error`); gli altri capitoli continuano; riepilogo finale |
| risposta vuota | «il modello non ha scritto niente» per quel capitolo |
| risposta troncata (`max_tokens`) | testo tenuto, segnato «troncato» nell'elenco |
| file non leggibile | frase con il nome del file e il motivo; nessun bottone attivo |
| salvataggio fallito | il file precedente è intatto (scrittura in `.tmp` + rilettura + rinomina); messaggio |
| nessun autore umano nel grafo | la finestra di convalida accetta un nome e crea l'autore |
| EMStudio non installato | barra dei messaggi: menu «Installa EMStudio…» |
| annulla | si ferma dopo il capitolo in corso; quanto fatto è salvato |

## Prove

- `tests/utility/test_em_narrative.py` (puro, modello finto su un grafo di tre unità e due epoche costruito a mano): ordine degli scope e scarto delle configurazioni senza chiave o modello; scheletro aggiunto una volta sola; segnaposto e stati; briefing (campi della scheda, epoche senza doppioni, ordine dalla più antica, rapporti, taglio a `MAX_ACTIONS`); messaggi (lingua, vincoli, regola `[[id]]`); `generate_chapter` (blocco `ai_draft`, autore AI, estrattore con il testo registrato e le fonti, menzioni normalizzate); rigenerazione che toglie solo le bozze; `generate` che continua dopo un fallimento, rispetta `cancelled` e salta i capitoli già scritti; `carry_over` (narrativa, autore, estrattore, convalida conservati; epoca nuova → capitolo nuovo); convalida con autore esistente e con nome nuovo; export HTML e DOCX con il testo dentro; `save_project` atomico e rilettura.
- `tests/sync/test_em_narrative_wiring.py`: lettura del sorgente (pannello con la scheda e `show_file`; plugin senza `tempfile` nella vista, `_ask_split` in entrambe le voci, tre bottoni; `export_site` con `keep_narrative`; `_L` completo it/en; `read_em_json` che ignora i nodi di supporto) e fumo offscreen: `build_tab` + `show_file` su un em.json con narrativa → l'elenco mostra i capitoli con gli stati; senza AI i bottoni di generazione sono spenti.
- `tests/sync/test_em_narrative_export.py` (DB di prova): esporta → genera col modello finto → riesporta → la narrativa c'è ancora con il testo e la convalida, e un'epoca nuova riceve un capitolo; stessa cosa sul contenitore per saggi (`con_saggi`).
- Un giro vero col modello impostato sul Mac di Enzo prima della release, con tempi e lunghezza per capitolo nel changelog.

## Documentazione e release

- Tutorial 36 (dieci lingue): sezione «Narrativa con l'AI» (che cosa genera, da dove legge l'AI, convalida, export, EMStudio, il file in `pyarchinit_EM_folder`, chiudere EMStudio prima di generare).
- `dev_logs/CHANGELOG.md` 5.13.106-alpha, `metadata.txt`, tag `narrativa-ai-5.13.106-alpha`, tutorial pubblicati su `pyarchinitDOC` dev.
