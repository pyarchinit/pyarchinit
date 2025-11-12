# gui/tma_import_dialog.py

## Overview

This file contains 88 documented elements.

## Classes

### ImportWorker

Thread worker per l'importazione in background

**Inherits from**: QThread

#### Methods

##### __init__(self, import_manager, files, use_festos_parser)

##### run(self)

Esegue l'importazione

### TMAImportDialog

Dialog per l'importazione dei dati TMA

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### init_ui(self)

Inizializza l'interfaccia

##### add_files(self, filter_str)

Aggiunge file alla lista

##### remove_selected_files(self)

Rimuove i file selezionati dalla lista

##### clear_files(self)

Pulisce la lista dei file

##### toggle_custom_mapping(self, checked)

Abilita/disabilita mapping personalizzato

##### add_mapping_examples(self)

Aggiunge esempi di mapping nella tabella

##### add_mapping_row(self)

Aggiunge una nuova riga di mapping

##### remove_mapping_row(self)

Rimuove la riga di mapping selezionata

##### get_custom_mapping(self)

Ottiene il mapping personalizzato dalla tabella

##### load_mapping_from_file(self)

Carica mapping da file JSON

##### save_mapping_to_file(self)

Salva mapping in file JSON

##### preview_import(self)

Mostra anteprima dei dati da importare

##### start_import(self)

Avvia l'importazione

##### update_progress(self, value)

Aggiorna la progress bar

##### log_message(self, message)

Aggiunge messaggio al log

##### import_finished(self, results)

Gestisce il completamento dell'importazione

### ImportWorker

Thread worker per l'importazione in background

**Inherits from**: QThread

#### Methods

##### __init__(self, import_manager, files, use_festos_parser)

##### run(self)

Esegue l'importazione

### TMAImportDialog

Dialog per l'importazione dei dati TMA

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### init_ui(self)

Inizializza l'interfaccia

##### add_files(self, filter_str)

Aggiunge file alla lista

##### remove_selected_files(self)

Rimuove i file selezionati dalla lista

##### clear_files(self)

Pulisce la lista dei file

##### toggle_custom_mapping(self, checked)

Abilita/disabilita mapping personalizzato

##### add_mapping_examples(self)

Aggiunge esempi di mapping nella tabella

##### add_mapping_row(self)

Aggiunge una nuova riga di mapping

##### remove_mapping_row(self)

Rimuove la riga di mapping selezionata

##### get_custom_mapping(self)

Ottiene il mapping personalizzato dalla tabella

##### load_mapping_from_file(self)

Carica mapping da file JSON

##### save_mapping_to_file(self)

Salva mapping in file JSON

##### preview_import(self)

Mostra anteprima dei dati da importare

##### start_import(self)

Avvia l'importazione

##### update_progress(self, value)

Aggiorna la progress bar

##### log_message(self, message)

Aggiunge messaggio al log

##### import_finished(self, results)

Gestisce il completamento dell'importazione

### ImportWorker

Thread worker per l'importazione in background

**Inherits from**: QThread

#### Methods

##### __init__(self, import_manager, files, use_festos_parser)

##### run(self)

Esegue l'importazione

### TMAImportDialog

Dialog per l'importazione dei dati TMA

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### init_ui(self)

Inizializza l'interfaccia

##### add_files(self, filter_str)

Aggiunge file alla lista

##### remove_selected_files(self)

Rimuove i file selezionati dalla lista

##### clear_files(self)

Pulisce la lista dei file

##### toggle_custom_mapping(self, checked)

Abilita/disabilita mapping personalizzato

##### add_mapping_examples(self)

Aggiunge esempi di mapping nella tabella

##### add_mapping_row(self)

Aggiunge una nuova riga di mapping

##### remove_mapping_row(self)

Rimuove la riga di mapping selezionata

##### get_custom_mapping(self)

Ottiene il mapping personalizzato dalla tabella

##### load_mapping_from_file(self)

Carica mapping da file JSON

##### save_mapping_to_file(self)

Salva mapping in file JSON

##### preview_import(self)

Mostra anteprima dei dati da importare

##### start_import(self)

Avvia l'importazione

##### update_progress(self, value)

Aggiorna la progress bar

##### log_message(self, message)

Aggiunge messaggio al log

##### import_finished(self, results)

Gestisce il completamento dell'importazione

### ImportWorker

Thread worker per l'importazione in background

**Inherits from**: QThread

#### Methods

##### __init__(self, import_manager, files, use_festos_parser)

##### run(self)

Esegue l'importazione

### TMAImportDialog

Dialog per l'importazione dei dati TMA

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### init_ui(self)

Inizializza l'interfaccia

##### add_files(self, filter_str)

Aggiunge file alla lista

##### remove_selected_files(self)

Rimuove i file selezionati dalla lista

##### clear_files(self)

Pulisce la lista dei file

##### toggle_custom_mapping(self, checked)

Abilita/disabilita mapping personalizzato

##### add_mapping_examples(self)

Aggiunge esempi di mapping nella tabella

##### add_mapping_row(self)

Aggiunge una nuova riga di mapping

##### remove_mapping_row(self)

Rimuove la riga di mapping selezionata

##### get_custom_mapping(self)

Ottiene il mapping personalizzato dalla tabella

##### load_mapping_from_file(self)

Carica mapping da file JSON

##### save_mapping_to_file(self)

Salva mapping in file JSON

##### preview_import(self)

Mostra anteprima dei dati da importare

##### start_import(self)

Avvia l'importazione

##### update_progress(self, value)

Aggiorna la progress bar

##### log_message(self, message)

Aggiunge messaggio al log

##### import_finished(self, results)

Gestisce il completamento dell'importazione

