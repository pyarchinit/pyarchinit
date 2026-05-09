# searchWorker.py

## Overview

This file contains 7 documented elements.

## Classes

### Worker

Questo fa tutto il lavoro duro. Prende tutti i parametri di ricerca e 
cerca una corrispondenza attraverso i livelli vettoriali.

**Inherits from**: QObject

#### Methods

##### __init__(self, vlayers, infield, searchStr, comparisonMode, selectedField, maxResults)

Initializes the worker object by calling the parent `QObject` constructor and storing the provided search parameters as instance attributes. Accepts `vlayers` (vector layers to search), `infield`, `searchStr` (the search string), `comparisonMode`, `selectedField`, and `maxResults` as configuration for the search operation. Also initializes the `killed` flag to `False`, which is used to control the worker's execution lifecycle.

##### run(self)

Worker esegue routine

##### kill(self)

imposta uno stop alla ricerca

##### searchLayer(self, layer, searchStr, comparisonMode)

Esegue una ricerca per stringa in tutte le colonne di una tabella

##### searchFieldInLayer(self, layer, searchStr, comparisonMode, selectedField)

Esegue una ricerca per stringa su una colonna specifica della tabella.

