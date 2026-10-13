# Stili delle viste — disegno

Data: 2026-10-13 · ramo `Stratigraph_00001` · plugin 5.13.111-alpha → 5.13.112-alpha · QGIS 3.42 (misurato), minimo 3.22.

## Da dove viene

Enzo, 13 ottobre 2026, dopo il giro sulle etichette «0,00 ha» rimaste sulle viste: «potresti creare una nuova scheda che possa gestire gli stili, crearne nuovi, con etichette ecc. — una scheda completa per la gestione dello stile», e poi: «non solo per le US: estendilo anche per le quote e tutti i layer di pyArchInit (le view)».

Oggi lo stile di una vista nasce in tre posti che non si parlano: i QML forniti con il plugin (`modules/gis/styles_spatialite`, sei file, solo per US e quote), la finestra in tre passi di `USViewStyler` (nuovo stile / stile esistente / temporaneo / solo contorno, poi il campo di categorizzazione) che vale solo per US e USM, e le etichette cablate nel codice dalla 5.13.110 (`label_us_view`, `label_quote_view`). Le altre viste — documentazione, strutture, tombe, UT, siti, reperti, sezioni — si caricano senza stile. Nessuno di questi stili ha un posto dove vivere per sito, e quello che QGIS lascia sui layer (lo stile predefinito, le etichette di un'altra sessione) non si vede da nessuna parte.

## Obiettivo

Una finestra sola, **Stili delle viste**, dalla quale per ogni vista di pyArchInit si compone lo stile — simbologia ed etichette — con un'anteprima sui dati del sito corrente, lo si salva nel database del progetto con un nome, lo si fa diventare predefinito per il sito o per tutti, lo si esporta e importa come QML. Le schede che caricano le viste applicano lo stile predefinito senza chiedere niente; la finestra si apre dal menu e da un bottone nelle schede.

## Non obiettivi

- Layer raster, layer che non sono di pyArchInit, layout di stampa, stili di progetto QGIS.
- L'editor delle etichette a regole di QGIS (`QgsLabelingGui`): non è esposto a Python; le etichette si compongono con un pannello nostro (vedi sotto).
- Toccare i QML forniti: restano i modelli di partenza.
- Migrare gli stili salvati con QGIS nella tabella `layer_styles`: si leggono e si possono importare, non si riscrivono.

## Decisioni

1. **Tutte le viste, da un registro.** `modules/utility/view_styles.py::VIEWS` elenca le viste che i caricatori usano davvero (SQLite e PostgreSQL): `pyarchinit_us_view`, `pyarchinit_usm_view`, `pyarchinit_quote_view`, `pyarchinit_quote_usm_view`, `pyarchinit_doc_view`, `pyarchinit_doc_view_b`, `pyarchinit_us_negative_doc_view`, `pyarchinit_strutture_view`, `pyarchinit_tomba_view`, `pyarchinit_individui_view`, `pyarchinit_ut_point_view`, `pyarchinit_ut_line_view`, `pyarchinit_ut_polygon_view`, `pyarchinit_site_view`, `pyarchinit_siti_polygonal_view`, `pyarchinit_reperti_view`, `pyarchinit_sezioni_view`. Per ciascuna: nome a schermo (it/en dai dizionari che il plugin ha già), geometria, campo del sito (`scavo_s`, `sito`, `sito_q`…), QML fornito se c'è, **ricetta delle etichette** di partenza (`us_circle` per US e USM, `quota` per le quote, nessuna per le altre), campi di categorizzazione sensati.
2. **Gli editor sono quelli di QGIS**, non copie: la simbologia con `QgsRendererPropertiesDialog(layer, QgsStyle.defaultStyle(), embedded=True)` dentro la finestra, il testo delle etichette con un pannello nostro (carattere, corpo in mm, grassetto, colore, alone bianco, sfondo a cerchio con riempimento e bordo): il `QgsTextFormatWidget` di QGIS va in segfault fuori dall'applicazione (misurato il 13 ottobre, anche con `QgsGui` inizializzata), e un widget che non si può provare non entra. Il pannello delle etichette è nostro perché QGIS non espone il suo: *acceso/spento*, *che cosa scrivere* (un campo della vista o un'espressione), *dove* (al centro / intorno al punto / sopra la linea del simbolo, con lo scostamento in mm), *una etichetta per unità* (solo viste di unità: il disegno più grande che si vede, come nelle tavole), più i preset «Numero US cerchiato», «Quota sopra il simbolo», «Nessuna».
3. **Anteprima vera.** Un `QgsMapCanvas` nella finestra con la vista caricata dal database del progetto, filtrata sul sito corrente, con il bottone «Inquadra». Ogni modifica si vede subito; niente tocca i layer del progetto finché non si clicca «Applica ai layer caricati».
4. **Gli stili vivono nel database del progetto**, in una tabella nostra `pyarchinit_view_styles` (`id`, `view_name`, `site` nullo = tutti i siti, `name`, `qml` testo con simbologia ed etichette da `exportNamedStyle`, `recipe` JSON con quello che il QML non sa — `one_per_unit`, il preset — `is_default`, `author`, `updated_at`), creata su entrambi i motori con `metadata.create_all` come le tabelle TMA e Fauna. Gli stili salvati con QGIS in `layer_styles` compaiono in elenco come «Salvato con QGIS», importabili.
5. **Chi comanda al caricamento** (`apply_view_style(layer, view_name, site)`): lo stile predefinito del sito; se non c'è, quello predefinito per tutti i siti; se non c'è, il QML fornito più la ricetta di partenza delle etichette — cioè quello che il plugin fa oggi. Il QML salvato non porta l'elenco dei disegni da etichettare (cambia a ogni filtro): «una per unità» è nella ricetta e si ricalcola al caricamento. Tutti i caricatori (`pyarchinit_pyqgis.py`: i sette punti della vista US, gli otto delle quote, e le altre viste) passano da qui; `label_us_view` e `label_quote_view` restano come ricette, non più come chiamate sparse.
6. **La finestra in tre passi di `USViewStyler` non sparisce**, ma si vede solo quando per quella vista non c'è nessuno stile predefinito: con un predefinito salvato la scheda US carica e basta. Le sue categorizzazioni («per definizione stratigrafica», «per tipo US», «per interpretativa», «per periodo e fase», «solo contorno») diventano preset di simbologia nella finestra nuova, sopra l'editor di QGIS.
7. **Dove si apre.** Voce di menu **pyArchInit → Stili delle viste…**; bottone «Stile…» nella scheda US accanto a quello che carica i layer; dal pannello dei layer, per una vista caricata, la finestra si apre già su quella vista (voce di menu con il layer corrente).
8. **Lingua.** Testi della finestra in italiano e inglese (tabella `_L` come le altre finestre recenti); nomi delle viste dai dizionari esistenti per le dieci lingue.

## Che cosa fa la finestra

Colonna sinistra: l'elenco delle viste del registro, raggruppate (Unità, Quote, Documentazione, Strutture e tombe, UT, Siti, Reperti, Sezioni); sotto, gli **stili salvati** per la vista scelta (nome, sito o «tutti», predefinito ✓, autore, data) con Nuovo, Duplica, Rinomina, Elimina, «Predefinito per questo sito», «Predefinito per tutti», Esporta QML…, Importa QML….

Colonna destra: in alto l'**anteprima**; sotto, due schede — **Simbologia** (i preset di pyArchInit e l'editor di QGIS) ed **Etichette** (il pannello descritto al punto 2). In basso: «Applica ai layer caricati» (ai layer del progetto che vengono da quella vista), «Salva», «Salva come…», «Chiudi».

Salvare scrive la riga nella tabella; rendere predefinito ne sposta il flag (uno solo per vista e sito, uno solo per vista «tutti»). Eliminare chiede conferma. Importare un QML crea uno stile con il nome del file; esportare scrive il QML con simbologia ed etichette.

## Errori e casi limite

- Database non collegato o vista assente nel database: la vista compare in elenco ma grigia, con la frase «Vista non presente in questo database».
- Sito senza righe nella vista: anteprima vuota con la frase «Nessuna geometria per il sito corrente», lo stile si compone lo stesso.
- Tabella degli stili assente (database vecchio): la finestra la crea al primo salvataggio (`ensure_view_styles_table`); su PostgreSQL senza permesso di creare tabelle, messaggio chiaro e lavoro solo in memoria con «Esporta QML».
- QML non leggibile all'importazione: messaggio con il nome del file, niente scritto.
- Uno stile salvato per una vista che nel frattempo ha perso un campo (categorizzazione su un campo che non c'è più): al caricamento QGIS applica quello che può; la finestra lo segnala nell'anteprima.
- «Una per unità» su una vista senza i campi di raggruppamento (`area`/`us` o `area_s`/`us_s`): l'opzione è spenta e lo dice.

## Verifica

- **Modello puro** (`view_styles.py`, senza Qt): il registro, la scelta dello stile (sito → tutti → fornito), la ricetta delle etichette ricalcolata, lettura e scrittura della tabella su SQLite e sulla fixture PostgreSQL, importazione/esportazione del QML, la lettura di `layer_styles`.
- **Caricatori** (guardie AST sul sorgente): ogni vista del registro passa da `apply_view_style`; nessuna chiamata sparsa a `loadNamedStyle` dei QML forniti fuori da lì.
- **Finestra in offscreen**: si costruisce, elenca le viste, carica l'anteprima dal DB di prova, applica un preset, salva, rende predefinito, esporta e reimporta, applica a un layer caricato; il tutto senza toccare il progetto.
- **A mano in QGIS** (Enzo): un giro completo su US, quote e una vista «muta» (strutture), su SQLite; su PostgreSQL con la fixture locale.
- Tutorial 14 riscritto nella parte «Scelta dello stile» e un paragrafo per le altre viste; tutorial 36 §10.13 per la vista US; changelog bilingue.

## Fuori da questa release, da decidere dopo

- Stili per livello di zoom o per periodo (il Time Manager ha i suoi).
- Condivisione degli stili fra database diversi (oggi: Esporta/Importa QML).
- La stessa finestra per i layer di disegno «grezzi» (`pyunitastratigrafiche`, `pyarchinit_quote`…): si aggiungono al registro quando serve.
