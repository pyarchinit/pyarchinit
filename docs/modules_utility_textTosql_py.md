# modules/utility/textTosql.py

## Overview

This file contains 124 documented elements.

## Classes

### Text2SQLWidget

Widget per l'interfaccia Text2SQL con modalità dual (API e locale)

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

##### setup_ui(self)

Configura l'interfaccia utente

##### check_model_status(self)

Controlla se il modello locale è disponibile

##### on_mode_toggled(self)

Gestisce il cambio di modalità

##### on_download_model_clicked(self)

Gestisce il click sul pulsante di download del modello

##### on_generate_clicked(self)

Gestisce il click sul pulsante di generazione

##### on_explain_clicked(self)

Gestisce il click sul pulsante di spiegazione

##### on_clear_clicked(self)

Pulisce l'interfaccia

##### on_copy_clicked(self)

Copia la query negli appunti

##### on_use_clicked(self)

Usa la query generata

##### apikey_text2sql(self)

Restituisce la chiave API (per compatibilità con il codice esistente)

### DownloadModelWorker

Worker per il download del modello in background

**Inherits from**: QObject

#### Methods

##### __init__(self)

##### download_model(self, download_url, save_path)

##### stop(self)

### DownloadModelDialog

Dialog per scaricare il modello

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### start_download(self)

Avvia il download del modello

##### update_progress(self, percent, status)

Aggiorna il progresso del download

##### download_finished(self, success, message)

Gestisce il completamento del download

##### cancel_download(self)

Annulla il download in corso

### MakeSQL

#### Methods

##### __init__(self)

##### schema_to_text(metadata)

##### make_api_request(prompt, db, apikey)

##### explain_request(prompt, apikey)

##### check_local_model()

Verifica se il modello locale esiste

##### download_model_dialog(parent)

Mostra il dialog per scaricare il modello

##### make_local_request(prompt, db, parent)

Genera una query SQL usando il modello locale Phi-3

Args:
    prompt: La domanda in linguaggio naturale
    db: Tipo di database (sqlite, postgresql, etc.)
    parent: Widget genitore per i dialoghi

Returns:
    La query SQL generata o None in caso di errore

##### explain_local_request(prompt, parent)

Spiega una query SQL usando il modello locale Phi-3

Args:
    prompt: La query SQL da spiegare
    parent: Widget genitore per i dialoghi

Returns:
    Spiegazione della query o None in caso di errore

### Text2SQLWidget

Widget per l'interfaccia Text2SQL con modalità dual (API e locale)

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

##### setup_ui(self)

Configura l'interfaccia utente

##### check_model_status(self)

Controlla se il modello locale è disponibile

##### on_mode_toggled(self)

Gestisce il cambio di modalità

##### on_download_model_clicked(self)

Gestisce il click sul pulsante di download del modello

##### on_generate_clicked(self)

Gestisce il click sul pulsante di generazione

##### on_explain_clicked(self)

Gestisce il click sul pulsante di spiegazione

##### on_clear_clicked(self)

Pulisce l'interfaccia

##### on_copy_clicked(self)

Copia la query negli appunti

##### on_use_clicked(self)

Usa la query generata

##### apikey_text2sql(self)

Restituisce la chiave API (per compatibilità con il codice esistente)

### DownloadModelWorker

Worker per il download del modello in background

**Inherits from**: QObject

#### Methods

##### __init__(self)

##### download_model(self, download_url, save_path)

##### stop(self)

### DownloadModelDialog

Dialog per scaricare il modello

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### start_download(self)

Avvia il download del modello

##### update_progress(self, percent, status)

Aggiorna il progresso del download

##### download_finished(self, success, message)

Gestisce il completamento del download

##### cancel_download(self)

Annulla il download in corso

### MakeSQL

#### Methods

##### __init__(self)

##### schema_to_text(metadata)

##### make_api_request(prompt, db, apikey)

##### explain_request(prompt, apikey)

##### check_local_model()

Verifica se il modello locale esiste

##### download_model_dialog(parent)

Mostra il dialog per scaricare il modello

##### make_local_request(prompt, db, parent)

Genera una query SQL usando il modello locale Phi-3

Args:
    prompt: La domanda in linguaggio naturale
    db: Tipo di database (sqlite, postgresql, etc.)
    parent: Widget genitore per i dialoghi

Returns:
    La query SQL generata o None in caso di errore

##### explain_local_request(prompt, parent)

Spiega una query SQL usando il modello locale Phi-3

Args:
    prompt: La query SQL da spiegare
    parent: Widget genitore per i dialoghi

Returns:
    Spiegazione della query o None in caso di errore

### Text2SQLWidget

Widget per l'interfaccia Text2SQL con modalità dual (API e locale)

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

##### setup_ui(self)

Configura l'interfaccia utente

##### check_model_status(self)

Controlla se il modello locale è disponibile

##### on_mode_toggled(self)

Gestisce il cambio di modalità

##### on_download_model_clicked(self)

Gestisce il click sul pulsante di download del modello

##### on_generate_clicked(self)

Gestisce il click sul pulsante di generazione

##### on_explain_clicked(self)

Gestisce il click sul pulsante di spiegazione

##### on_clear_clicked(self)

Pulisce l'interfaccia

##### on_copy_clicked(self)

Copia la query negli appunti

##### on_use_clicked(self)

Usa la query generata

##### apikey_text2sql(self)

Restituisce la chiave API (per compatibilità con il codice esistente)

### DownloadModelWorker

Worker per il download del modello in background

**Inherits from**: QObject

#### Methods

##### __init__(self)

##### download_model(self, download_url, save_path)

##### stop(self)

### DownloadModelDialog

Dialog per scaricare il modello

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### start_download(self)

Avvia il download del modello

##### update_progress(self, percent, status)

Aggiorna il progresso del download

##### download_finished(self, success, message)

Gestisce il completamento del download

##### cancel_download(self)

Annulla il download in corso

### MakeSQL

#### Methods

##### __init__(self)

##### schema_to_text(metadata)

##### make_api_request(prompt, db, apikey)

##### explain_request(prompt, apikey)

##### check_local_model()

Verifica se il modello locale esiste

##### download_model_dialog(parent)

Mostra il dialog per scaricare il modello

##### make_local_request(prompt, db, parent)

Genera una query SQL usando il modello locale Phi-3

Args:
    prompt: La domanda in linguaggio naturale
    db: Tipo di database (sqlite, postgresql, etc.)
    parent: Widget genitore per i dialoghi

Returns:
    La query SQL generata o None in caso di errore

##### explain_local_request(prompt, parent)

Spiega una query SQL usando il modello locale Phi-3

Args:
    prompt: La query SQL da spiegare
    parent: Widget genitore per i dialoghi

Returns:
    Spiegazione della query o None in caso di errore

### Text2SQLWidget

Widget per l'interfaccia Text2SQL con modalità dual (API e locale)

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

##### setup_ui(self)

Configura l'interfaccia utente

##### check_model_status(self)

Controlla se il modello locale è disponibile

##### on_mode_toggled(self)

Gestisce il cambio di modalità

##### on_download_model_clicked(self)

Gestisce il click sul pulsante di download del modello

##### on_generate_clicked(self)

Gestisce il click sul pulsante di generazione

##### on_explain_clicked(self)

Gestisce il click sul pulsante di spiegazione

##### on_clear_clicked(self)

Pulisce l'interfaccia

##### on_copy_clicked(self)

Copia la query negli appunti

##### on_use_clicked(self)

Usa la query generata

##### apikey_text2sql(self)

Restituisce la chiave API (per compatibilità con il codice esistente)

### DownloadModelWorker

Worker per il download del modello in background

**Inherits from**: QObject

#### Methods

##### __init__(self)

##### download_model(self, download_url, save_path)

##### stop(self)

### DownloadModelDialog

Dialog per scaricare il modello

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### start_download(self)

Avvia il download del modello

##### update_progress(self, percent, status)

Aggiorna il progresso del download

##### download_finished(self, success, message)

Gestisce il completamento del download

##### cancel_download(self)

Annulla il download in corso

### MakeSQL

#### Methods

##### __init__(self)

##### schema_to_text(metadata)

##### make_api_request(prompt, db, apikey)

##### explain_request(prompt, apikey)

##### check_local_model()

Verifica se il modello locale esiste

##### download_model_dialog(parent)

Mostra il dialog per scaricare il modello

##### make_local_request(prompt, db, parent)

Genera una query SQL usando il modello locale Phi-3

Args:
    prompt: La domanda in linguaggio naturale
    db: Tipo di database (sqlite, postgresql, etc.)
    parent: Widget genitore per i dialoghi

Returns:
    La query SQL generata o None in caso di errore

##### explain_local_request(prompt, parent)

Spiega una query SQL usando il modello locale Phi-3

Args:
    prompt: La query SQL da spiegare
    parent: Widget genitore per i dialoghi

Returns:
    Spiegazione della query o None in caso di errore

