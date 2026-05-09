# searchDialog.py

## Overview

This file contains 18 documented elements.

## Classes

### LayerSearchDialog

*No description available.*
A QGIS dialog window, built from the `searchlayers.ui` form, that allows users to search for features across vector layers loaded in the current QGIS project. It supports searching across all layers, selected layers, or a single specified layer, with configurable field targeting and comparison modes (`=`, `contains`, `start with`), and displays up to 1,500 matching results in a sortable four-column table showing value, table name, field name, and feature ID. Search operations are executed in a separate thread via a `Worker` object, and selecting a result row deselects all current map selections, selects the matching feature in its layer, and zooms the map canvas to it. The dialog adapts its UI labels to the user's QGIS locale, with explicit support for Italian (`it`) and German (`de`).

**Inherits from**: QDialog, FORM_CLASS

#### Methods

##### __init__(self, iface, parent)

Initialize the LayerSearch dialog box

##### closeDialog(self)

Chiudere la finestra di dialogo quando si preme il pulsante Chiudi

##### updateLayers(self)

Chiamato quando un livello è stato aggiunto o cancellato in QGIS.
Forza la finestra di dialogo a ricaricare.

##### select_feature(self)

Una features è stata selezionata dalla lista, quindi dobbiamo selezionare
e zoomare su di esso

##### layerSelected(self)

L'utente ha fatto una selezione, quindi dobbiamo inizializzare altre
parti della finestra di dialogo

##### showEvent(self, event)

Si mostra l'evento

##### populateLayerListComboBox(self)

Trova tutti i livelli vettoriali e aggiungili alla lista dei livelli
che l'utente può selezionare. Inoltre l'utente può cercare su tutti gli
strati o tutti i livelli selezionati.

##### initFieldList(self)

*No description available.*
Populates the `searchFieldComboBox` with field names based on the currently selected layer in `layerListComboBox`. A locale-dependent default entry is inserted first — `'<Tutti i campi>'` for Italian (`'it'`) or `'<Alle felder>'` for German (`'de'`), followed by `'<All fields>'` for Italian. If the selected layer index is greater than 1, the combo box is enabled and each field name from the corresponding layer in `searchLayers` is added; otherwise, the combo box is reset to index 0 and disabled.

##### runSearch(self)

Chiamata quando l'utente preme il pulsante Cerca

##### workerFinished(self, status)

pulisci il worker e thread

##### workerError(self, exception_string)

appare un errore sul display

##### killWorker(self)

Questo viene avviato quando l'utente preme il pulsante Stop
e interromperà il processo di ricerca

##### clearResults(self)

Pulisci il risultato della ricerca

##### addFoundItem(self, layer, feature, attrname, value)

Abbiamo trovato un elemento, quindi aggiungilo alla lista 

##### showErrorMessage(self, message)

Si mostra un messaggio di errore

##### on_pushButton_go_to_scheda_pressed(self)

*No description available.*
Handles the press event of the "go to scheda" button by retrieving the currently active layer from the map canvas and identifying a field whose name contains `'id_'` or `'gid'` to use as the unique identifier. It then validates that a layer is present — displaying a localized warning dialog (Italian, German, or English depending on `self.L`) if none is found — and collects the selected features' identifier values into a list. Finally, it queries the database via `self.DB_MANAGER.query_sort` using the collected identifiers and populates `self.DATA_LIST` with the sorted results, setting the browse status to `'b'`.

