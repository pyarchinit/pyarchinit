# searchDialog.py

## Overview

This file contains 54 documented elements.

## Classes

### LayerSearchDialog

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

### LayerSearchDialog

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

### LayerSearchDialog

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

