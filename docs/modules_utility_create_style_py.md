# modules/utility/create_style.py

## Overview

This file contains 56 documented elements.

## Classes

### ThesaurusStyler

#### Methods

##### __init__(self, default_style_path)

Inizializza la classe con il percorso dello stile QML predefinito.

:param default_style_path: Percorso del file QML di default

##### load_default_style(self)

Carica lo stile predefinito dal file QML.

##### get_style(self, sigla)

Restituisce lo stile per una data sigla.
In questo caso, restituisce sempre lo stile predefinito.

:param sigla: La sigla per cui si vuole lo stile (non utilizzata in questa implementazione)
:return: QgsFillSymbol predefinito

##### apply_style_to_layer(self, layer, d_stratigrafica_field, thesaurus_mapping)

Applica gli stili al layer basandosi sul mapping del thesaurus.

:param layer: Il layer QGIS a cui applicare gli stili
:param d_stratigrafica_field: Il nome del campo contenente i valori d_stratigrafica
:param thesaurus_mapping: Il mapping tra d_stratigrafica e sigla_estesa

### USViewStyler

#### Methods

##### __init__(self, connection)

##### ask_user_style_preference(self)

##### load_style_from_db(self, layer)

##### load_style_from_db_new(self, layer)

##### apply_style_to_layer(self, layer)

##### show_message(self, message)

Mostra un messaggio all'utente.

##### save_style_to_db(self, layer)

##### get_all_styles(self)

### ThesaurusStyler

#### Methods

##### __init__(self, default_style_path)

Inizializza la classe con il percorso dello stile QML predefinito.

:param default_style_path: Percorso del file QML di default

##### load_default_style(self)

Carica lo stile predefinito dal file QML.

##### get_style(self, sigla)

Restituisce lo stile per una data sigla.
In questo caso, restituisce sempre lo stile predefinito.

:param sigla: La sigla per cui si vuole lo stile (non utilizzata in questa implementazione)
:return: QgsFillSymbol predefinito

##### apply_style_to_layer(self, layer, d_stratigrafica_field, thesaurus_mapping)

Applica gli stili al layer basandosi sul mapping del thesaurus.

:param layer: Il layer QGIS a cui applicare gli stili
:param d_stratigrafica_field: Il nome del campo contenente i valori d_stratigrafica
:param thesaurus_mapping: Il mapping tra d_stratigrafica e sigla_estesa

### USViewStyler

#### Methods

##### __init__(self, connection)

##### ask_user_style_preference(self)

##### load_style_from_db(self, layer)

##### load_style_from_db_new(self, layer)

##### apply_style_to_layer(self, layer)

##### show_message(self, message)

Mostra un messaggio all'utente.

##### save_style_to_db(self, layer)

##### get_all_styles(self)

### ThesaurusStyler

#### Methods

##### __init__(self, default_style_path)

Inizializza la classe con il percorso dello stile QML predefinito.

:param default_style_path: Percorso del file QML di default

##### load_default_style(self)

Carica lo stile predefinito dal file QML.

##### get_style(self, sigla)

Restituisce lo stile per una data sigla.
In questo caso, restituisce sempre lo stile predefinito.

:param sigla: La sigla per cui si vuole lo stile (non utilizzata in questa implementazione)
:return: QgsFillSymbol predefinito

##### apply_style_to_layer(self, layer, d_stratigrafica_field, thesaurus_mapping)

Applica gli stili al layer basandosi sul mapping del thesaurus.

:param layer: Il layer QGIS a cui applicare gli stili
:param d_stratigrafica_field: Il nome del campo contenente i valori d_stratigrafica
:param thesaurus_mapping: Il mapping tra d_stratigrafica e sigla_estesa

### USViewStyler

#### Methods

##### __init__(self, connection)

##### ask_user_style_preference(self)

##### load_style_from_db(self, layer)

##### load_style_from_db_new(self, layer)

##### apply_style_to_layer(self, layer)

##### show_message(self, message)

Mostra un messaggio all'utente.

##### save_style_to_db(self, layer)

##### get_all_styles(self)

### ThesaurusStyler

#### Methods

##### __init__(self, default_style_path)

Inizializza la classe con il percorso dello stile QML predefinito.

:param default_style_path: Percorso del file QML di default

##### load_default_style(self)

Carica lo stile predefinito dal file QML.

##### get_style(self, sigla)

Restituisce lo stile per una data sigla.
In questo caso, restituisce sempre lo stile predefinito.

:param sigla: La sigla per cui si vuole lo stile (non utilizzata in questa implementazione)
:return: QgsFillSymbol predefinito

##### apply_style_to_layer(self, layer, d_stratigrafica_field, thesaurus_mapping)

Applica gli stili al layer basandosi sul mapping del thesaurus.

:param layer: Il layer QGIS a cui applicare gli stili
:param d_stratigrafica_field: Il nome del campo contenente i valori d_stratigrafica
:param thesaurus_mapping: Il mapping tra d_stratigrafica e sigla_estesa

### USViewStyler

#### Methods

##### __init__(self, connection)

##### ask_user_style_preference(self)

##### load_style_from_db(self, layer)

##### load_style_from_db_new(self, layer)

##### apply_style_to_layer(self, layer)

##### show_message(self, message)

Mostra un messaggio all'utente.

##### save_style_to_db(self, layer)

##### get_all_styles(self)

