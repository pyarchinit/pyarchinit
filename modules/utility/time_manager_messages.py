"""I testi delle finestre della stampa delle tavole del Time Manager, in
italiano e in inglese (13 ottobre 2026: erano fissi in italiano con
qualunque lingua di QGIS). Puro: niente Qt, così si prova da solo."""
from __future__ import annotations

MESSAGES = {
    "it": {
        "warning": "Attenzione",
        "atlas": "Atlas",
        "no_layout": "Nessun layout caricato.",
        "no_templates": "Nessun modello (.qpt) trovato nelle cartelle standard.",
        "choose_title": "Scegli il modello di layout per l'atlante",
        "choose_intro": "Seleziona il modello per l'atlante.\n"
                        "✓ = titolo e matrice   • = solo mappa   ✗ = senza mappa",
        "browse": "Sfoglia...",
        "new": "Nuovo modello...",
        "use": "Usa il modello",
        "cancel": "Annulla",
        "browse_title": "Scegli un modello di layout (.qpt)",
        "browse_filter": "Modelli di layout QGIS (*.qpt);;Tutti i file (*)",
        "new_title": "Nuovo modello",
        "new_prompt": "Nome del nuovo modello:",
        "created_title": "Modello creato",
        "created_text": "Nuovo modello creato: {name}\n\n"
                        "Il Layout Designer è aperto per personalizzarlo.\n"
                        "Quando hai finito, chiudi il designer: il modello sarà disponibile.",
        "create_error_title": "Errore nella creazione del modello",
        "create_error_text": "Errore nella creazione del modello:\n{err}",
        "designer_title": "Layout Designer",
        "designer_text": "Il Layout Designer è aperto sul modello: {name}\n\n"
                         "Puoi modificare:\n"
                         "• posizione e dimensioni degli elementi\n"
                         "• stili, colori e caratteri\n"
                         "• aggiungere elementi (testo, immagini, ecc.)\n"
                         "• la mappa e la scala\n\n"
                         "Lascia pure il designer aperto: questa finestra non lo blocca.",
        "designer_error_title": "Errore del Layout Designer",
        "designer_error_text": "Errore nell'apertura del Layout Designer:\n{err}",
        "save_title": "Salva il modello",
        "save_prompt": "Nome del nuovo modello:",
        "exists_title": "Il file esiste",
        "exists_text": "Il modello «{name}» esiste già. Sovrascriverlo?",
        "saved_title": "Modello salvato",
        "saved_text": "Modello salvato:\n{path}",
        "save_error_title": "Errore nel salvataggio",
        "save_error_text": "Errore nel salvataggio del modello:\n{err}",
        "folder": "Scegli la cartella dove salvare le tavole",
        "template_error_title": "Errore del modello",
        "template_error_text": "Non riesco a caricare il modello:\n{path}",
        "proceed_anyway": "\n\nVuoi procedere lo stesso?",
        "edit_title": "Modifica del modello",
        "edit_text": "Vuoi aprire il Layout Designer per modificare il modello prima di generare l'atlante?",
        "continue_title": "Continua l'atlante",
        "continue_text": "Hai finito le modifiche al layout?\nProcedere con la generazione dell'atlante?",
        "no_order_layer": "Nessuna US ha un valore di «order_layer»: non c'è una sequenza da cui ricavare le tavole.",
        "info": "Informazione",
        "no_dated_level": "Nessun livello di order_layer con una datazione valida.",
        "progress_text": "Generazione delle tavole in corso...",
        "progress_title": "Generazione dell'atlante",
        "not_written": "\n\nNON scritte: {list} — controlla che la cartella sia scrivibile.",
        "done_title": "Atlante completato",
        "done_text": "Atlante generato.\nLivelli di order_layer elaborati: {done}/{total}\n"
                     "Tavole con datazione valida: {valid}\nSalvate in: {path}{tail}",
        "stopped_title": "Atlante interrotto",
        "stopped_text": "Generazione dell'atlante interrotta.\n"
                        "Livelli di order_layer elaborati prima dell'interruzione: {done}/{total}",
        "alert": "Attenzione",
        "no_periods": "Non vi sono periodizzazioni in questo intervallo di tempo",
        "no_geometries": "Non ci sono geometrie da visualizzare",
        "select_us_view_first": "Seleziona prima il layer della vista US nel pannello dei layer",
    },
    "en": {
        "warning": "Warning",
        "atlas": "Atlas",
        "no_layout": "No layout loaded.",
        "no_templates": "No template (.qpt) found in the standard folders.",
        "choose_title": "Choose the layout template for the atlas",
        "choose_intro": "Choose the template for the atlas.\n"
                        "✓ = title and matrix   • = map only   ✗ = no map",
        "browse": "Browse...",
        "new": "New template...",
        "use": "Use the template",
        "cancel": "Cancel",
        "browse_title": "Choose a layout template (.qpt)",
        "browse_filter": "QGIS layout templates (*.qpt);;All files (*)",
        "new_title": "New template",
        "new_prompt": "Name of the new template:",
        "created_title": "Template created",
        "created_text": "New template created: {name}\n\n"
                        "The Layout Designer is open to customise it.\n"
                        "When you are done, close the designer: the template will be available.",
        "create_error_title": "Template creation error",
        "create_error_text": "Error while creating the template:\n{err}",
        "designer_title": "Layout Designer",
        "designer_text": "The Layout Designer is open on the template: {name}\n\n"
                         "You can change:\n"
                         "• position and size of the items\n"
                         "• styles, colours and fonts\n"
                         "• add items (text, pictures, etc.)\n"
                         "• the map and the scale\n\n"
                         "Leave the designer open: this window does not block it.",
        "designer_error_title": "Layout Designer error",
        "designer_error_text": "Error opening the Layout Designer:\n{err}",
        "save_title": "Save the template",
        "save_prompt": "Name of the new template:",
        "exists_title": "File exists",
        "exists_text": "The template “{name}” already exists. Overwrite it?",
        "saved_title": "Template saved",
        "saved_text": "Template saved:\n{path}",
        "save_error_title": "Save error",
        "save_error_text": "Error while saving the template:\n{err}",
        "folder": "Choose the folder where the sheets will be saved",
        "template_error_title": "Template error",
        "template_error_text": "Cannot load the template:\n{path}",
        "proceed_anyway": "\n\nProceed anyway?",
        "edit_title": "Edit the template",
        "edit_text": "Open the Layout Designer to edit the template before generating the atlas?",
        "continue_title": "Continue the atlas",
        "continue_text": "Are the layout changes done?\nProceed with the atlas generation?",
        "no_order_layer": "No US has an «order_layer» value: there is no sequence to draw the sheets from.",
        "info": "Information",
        "no_dated_level": "No order_layer level with a valid dating.",
        "progress_text": "Generating the sheets...",
        "progress_title": "Atlas generation",
        "not_written": "\n\nNOT written: {list} — check that the folder is writable.",
        "done_title": "Atlas completed",
        "done_text": "Atlas generated.\nOrder layers processed: {done}/{total}\n"
                     "Sheets with a valid dating: {valid}\nSaved in: {path}{tail}",
        "stopped_title": "Atlas stopped",
        "stopped_text": "Atlas generation stopped.\n"
                        "Order layers processed before stopping: {done}/{total}",
        "alert": "Warning",
        "no_periods": "There are no periods in this time interval",
        "no_geometries": "There are no geometries to display",
        "select_us_view_first": "Select the US view layer in the layer panel first",
    },
    #: Il tedesco copre solo gli avvisi che aveva già nel codice (il resto
    #: cade sull'inglese, come per le altre lingue).
    "de": {
        "alert": "Achtung",
        "no_periods": "Es gibt keine Perioden in diesem Zeitintervall.",
        "no_geometries": "Es gibt keine Geometrien, die angezeigt werden können.",
        "select_us_view_first": "Wähle zuerst den Layer der US-Ansicht im Layerfenster.",
    },
}


def tm(lang, key: str, **kw) -> str:
    """Il testo ``key`` nella lingua data (``it``, ``en``, e ``de`` dove
    c'è; il resto cade sull'inglese); una chiave sconosciuta torna com'è."""
    prefisso = str(lang or "").lower()[:2]
    lingua = prefisso if prefisso in MESSAGES else "en"
    testo = MESSAGES[lingua].get(key, MESSAGES["en"].get(key, key))
    return testo.format(**kw) if kw else testo
