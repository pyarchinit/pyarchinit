# modules/gis/pyarchinit_pyqgis.py

## Overview

This file contains 280 documented elements.

## Classes

### Pyarchinit_pyqgis

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

##### remove_USlayer_from_registry(self)

##### charge_individui_us(self, data)

##### charge_vector_layers_from_matrix(self, idus)

##### charge_vector_layers_doc(self, data)

##### charge_vector_layers_doc_from_scheda_US(self, lista_draw_doc)

##### charge_vector_layers(self, data)

##### charge_usm_layers(self, data)

##### charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_usm_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_usm_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### loadMapPreview(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreview_new(self, gidstr)

if has geometry column load to map canvas 

##### show_message(self, message)

Mostra un messaggio all'utente.

##### set_layer_opacity(self, layer, opacity)

Imposta l'opacità per tutti i simboli in un layer, indipendentemente dal tipo di renderer.

##### get_thesaurus_mapping(self, conn)

Ottiene il mapping tra sigla_estesa e d_stratigrafica.

:param conn: Connessione al database
:return: Dizionario con sigla_estesa come chiave e d_stratigrafica come valore

##### get_thesaurus_mapping_postgres(self, uri)

Ottiene il mapping tra d_stratigrafica e sigla dal thesaurus per PostgreSQL usando solo QGIS.

:param uri: QgsDataSourceUri configurato per la connessione PostgreSQL
:return: Dizionario con d_stratigrafica come chiave e sigla_estesa come valore

##### loadMapPreviewReperti(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreviewDoc(self, docstr)

if has geometry column load to map canvas 

##### dataProviderFields(self)

##### selectedFeatures(self)

##### findFieldFrDict(self, fn)

##### findItemInAttributeMap(self, fp, fl)

##### charge_layers_for_draw(self, options)

##### charge_sites_geometry(self, options, col, val)

##### charge_sites_from_research(self, data)

##### charge_reperti_layers(self, data)

##### charge_tomba_layers(self, data)

##### charge_vector_layers_all_st(self, sito_p, sigla_st, n_st)

##### charge_structure_from_research(self, data)

##### charge_individui_from_research(self, data)

##### unique_layer_name(self, base_name)

funzione per creare un nome unico alle view quando vengono caricate

##### internet_on(self)

### Order_layer_v2

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

Returns:
- order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
- "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.

##### find_base_matrix(self)

##### create_list_values(self, rapp_type_list, value_list, ar, si)

##### us_extractor(self, res)

##### insert_into_dict(self, base_matrix, v)

##### insert_into_dict_equal(self, base_matrix, v)

##### remove_from_list_in_dict(self, curr_base_matrix)

### LogHandler

Handler personalizzato per mostrare i log in un QTextEdit

**Inherits from**: logging.Handler

#### Methods

##### __init__(self, text_widget)

##### emit(self, record)

### Order_layer_graph

Versione ottimizzata con grafi in memoria per il calcolo del matrix stratigrafico.
Carica tutti i dati in memoria una volta sola, evitando query ripetute.

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

Metodo principale che calcola l'ordine stratigrafico usando grafi in memoria.

Returns:
- order_dict (dict): Il dizionario con l'ordinamento delle US per livelli
- "error" (str): In caso di errore

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

##### find_base_matrix(self)

Trova le US di base (senza predecessori) - compatibilità con vecchio codice

##### create_list_values(self, rapp_type_list, value_list, ar, si)

Metodo mantenuto per compatibilità

##### us_extractor(self, res)

Metodo mantenuto per compatibilità

##### insert_into_dict(self, base_matrix, v)

Metodo mantenuto per compatibilità

##### remove_from_list_in_dict(self, curr_base_matrix)

Metodo mantenuto per compatibilità

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

### MyError

**Inherits from**: Exception

#### Methods

##### __init__(self, value)

##### __str__(self)

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

### Pyarchinit_pyqgis

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

##### remove_USlayer_from_registry(self)

##### charge_individui_us(self, data)

##### charge_vector_layers_from_matrix(self, idus)

##### charge_vector_layers_doc(self, data)

##### charge_vector_layers_doc_from_scheda_US(self, lista_draw_doc)

##### charge_vector_layers(self, data)

##### charge_usm_layers(self, data)

##### charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_usm_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_usm_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### loadMapPreview(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreview_new(self, gidstr)

if has geometry column load to map canvas 

##### show_message(self, message)

Mostra un messaggio all'utente.

##### set_layer_opacity(self, layer, opacity)

Imposta l'opacità per tutti i simboli in un layer, indipendentemente dal tipo di renderer.

##### get_thesaurus_mapping(self, conn)

Ottiene il mapping tra sigla_estesa e d_stratigrafica.

:param conn: Connessione al database
:return: Dizionario con sigla_estesa come chiave e d_stratigrafica come valore

##### get_thesaurus_mapping_postgres(self, uri)

Ottiene il mapping tra d_stratigrafica e sigla dal thesaurus per PostgreSQL usando solo QGIS.

:param uri: QgsDataSourceUri configurato per la connessione PostgreSQL
:return: Dizionario con d_stratigrafica come chiave e sigla_estesa come valore

##### loadMapPreviewReperti(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreviewDoc(self, docstr)

if has geometry column load to map canvas 

##### dataProviderFields(self)

##### selectedFeatures(self)

##### findFieldFrDict(self, fn)

##### findItemInAttributeMap(self, fp, fl)

##### charge_layers_for_draw(self, options)

##### charge_sites_geometry(self, options, col, val)

##### charge_sites_from_research(self, data)

##### charge_reperti_layers(self, data)

##### charge_tomba_layers(self, data)

##### charge_vector_layers_all_st(self, sito_p, sigla_st, n_st)

##### charge_structure_from_research(self, data)

##### charge_individui_from_research(self, data)

##### unique_layer_name(self, base_name)

funzione per creare un nome unico alle view quando vengono caricate

##### internet_on(self)

### Order_layer_v2

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

Returns:
- order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
- "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.

##### find_base_matrix(self)

##### create_list_values(self, rapp_type_list, value_list, ar, si)

##### us_extractor(self, res)

##### insert_into_dict(self, base_matrix, v)

##### insert_into_dict_equal(self, base_matrix, v)

##### remove_from_list_in_dict(self, curr_base_matrix)

### LogHandler

Handler personalizzato per mostrare i log in un QTextEdit

**Inherits from**: logging.Handler

#### Methods

##### __init__(self, text_widget)

##### emit(self, record)

### Order_layer_graph

Versione ottimizzata con grafi in memoria per il calcolo del matrix stratigrafico.
Carica tutti i dati in memoria una volta sola, evitando query ripetute.

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

Metodo principale che calcola l'ordine stratigrafico usando grafi in memoria.

Returns:
- order_dict (dict): Il dizionario con l'ordinamento delle US per livelli
- "error" (str): In caso di errore

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

##### find_base_matrix(self)

Trova le US di base (senza predecessori) - compatibilità con vecchio codice

##### create_list_values(self, rapp_type_list, value_list, ar, si)

Metodo mantenuto per compatibilità

##### us_extractor(self, res)

Metodo mantenuto per compatibilità

##### insert_into_dict(self, base_matrix, v)

Metodo mantenuto per compatibilità

##### remove_from_list_in_dict(self, curr_base_matrix)

Metodo mantenuto per compatibilità

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

### MyError

**Inherits from**: Exception

#### Methods

##### __init__(self, value)

##### __str__(self)

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

### Pyarchinit_pyqgis

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

##### remove_USlayer_from_registry(self)

##### charge_individui_us(self, data)

##### charge_vector_layers_from_matrix(self, idus)

##### charge_vector_layers_doc(self, data)

##### charge_vector_layers_doc_from_scheda_US(self, lista_draw_doc)

##### charge_vector_layers(self, data)

##### charge_usm_layers(self, data)

##### charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_usm_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_usm_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### loadMapPreview(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreview_new(self, gidstr)

if has geometry column load to map canvas 

##### show_message(self, message)

Mostra un messaggio all'utente.

##### set_layer_opacity(self, layer, opacity)

Imposta l'opacità per tutti i simboli in un layer, indipendentemente dal tipo di renderer.

##### get_thesaurus_mapping(self, conn)

Ottiene il mapping tra sigla_estesa e d_stratigrafica.

:param conn: Connessione al database
:return: Dizionario con sigla_estesa come chiave e d_stratigrafica come valore

##### get_thesaurus_mapping_postgres(self, uri)

Ottiene il mapping tra d_stratigrafica e sigla dal thesaurus per PostgreSQL usando solo QGIS.

:param uri: QgsDataSourceUri configurato per la connessione PostgreSQL
:return: Dizionario con d_stratigrafica come chiave e sigla_estesa come valore

##### loadMapPreviewReperti(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreviewDoc(self, docstr)

if has geometry column load to map canvas 

##### dataProviderFields(self)

##### selectedFeatures(self)

##### findFieldFrDict(self, fn)

##### findItemInAttributeMap(self, fp, fl)

##### charge_layers_for_draw(self, options)

##### charge_sites_geometry(self, options, col, val)

##### charge_sites_from_research(self, data)

##### charge_reperti_layers(self, data)

##### charge_tomba_layers(self, data)

##### charge_vector_layers_all_st(self, sito_p, sigla_st, n_st)

##### charge_structure_from_research(self, data)

##### charge_individui_from_research(self, data)

##### unique_layer_name(self, base_name)

funzione per creare un nome unico alle view quando vengono caricate

##### internet_on(self)

### Order_layer_v2

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

Returns:
- order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
- "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.

##### find_base_matrix(self)

##### create_list_values(self, rapp_type_list, value_list, ar, si)

##### us_extractor(self, res)

##### insert_into_dict(self, base_matrix, v)

##### insert_into_dict_equal(self, base_matrix, v)

##### remove_from_list_in_dict(self, curr_base_matrix)

### LogHandler

Handler personalizzato per mostrare i log in un QTextEdit

**Inherits from**: logging.Handler

#### Methods

##### __init__(self, text_widget)

##### emit(self, record)

### Order_layer_graph

Versione ottimizzata con grafi in memoria per il calcolo del matrix stratigrafico.
Carica tutti i dati in memoria una volta sola, evitando query ripetute.

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

Metodo principale che calcola l'ordine stratigrafico usando grafi in memoria.

Returns:
- order_dict (dict): Il dizionario con l'ordinamento delle US per livelli
- "error" (str): In caso di errore

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

##### find_base_matrix(self)

Trova le US di base (senza predecessori) - compatibilità con vecchio codice

##### create_list_values(self, rapp_type_list, value_list, ar, si)

Metodo mantenuto per compatibilità

##### us_extractor(self, res)

Metodo mantenuto per compatibilità

##### insert_into_dict(self, base_matrix, v)

Metodo mantenuto per compatibilità

##### remove_from_list_in_dict(self, curr_base_matrix)

Metodo mantenuto per compatibilità

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

### MyError

**Inherits from**: Exception

#### Methods

##### __init__(self, value)

##### __str__(self)

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

### Pyarchinit_pyqgis

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

##### remove_USlayer_from_registry(self)

##### charge_individui_us(self, data)

##### charge_vector_layers_from_matrix(self, idus)

##### charge_vector_layers_doc(self, data)

##### charge_vector_layers_doc_from_scheda_US(self, lista_draw_doc)

##### charge_vector_layers(self, data)

##### charge_usm_layers(self, data)

##### charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_usm_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### charge_vector_layers_usm_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

##### loadMapPreview(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreview_new(self, gidstr)

if has geometry column load to map canvas 

##### show_message(self, message)

Mostra un messaggio all'utente.

##### set_layer_opacity(self, layer, opacity)

Imposta l'opacità per tutti i simboli in un layer, indipendentemente dal tipo di renderer.

##### get_thesaurus_mapping(self, conn)

Ottiene il mapping tra sigla_estesa e d_stratigrafica.

:param conn: Connessione al database
:return: Dizionario con sigla_estesa come chiave e d_stratigrafica come valore

##### get_thesaurus_mapping_postgres(self, uri)

Ottiene il mapping tra d_stratigrafica e sigla dal thesaurus per PostgreSQL usando solo QGIS.

:param uri: QgsDataSourceUri configurato per la connessione PostgreSQL
:return: Dizionario con d_stratigrafica come chiave e sigla_estesa come valore

##### loadMapPreviewReperti(self, gidstr)

if has geometry column load to map canvas 

##### loadMapPreviewDoc(self, docstr)

if has geometry column load to map canvas 

##### dataProviderFields(self)

##### selectedFeatures(self)

##### findFieldFrDict(self, fn)

##### findItemInAttributeMap(self, fp, fl)

##### charge_layers_for_draw(self, options)

##### charge_sites_geometry(self, options, col, val)

##### charge_sites_from_research(self, data)

##### charge_reperti_layers(self, data)

##### charge_tomba_layers(self, data)

##### charge_vector_layers_all_st(self, sito_p, sigla_st, n_st)

##### charge_structure_from_research(self, data)

##### charge_individui_from_research(self, data)

##### unique_layer_name(self, base_name)

funzione per creare un nome unico alle view quando vengono caricate

##### internet_on(self)

### Order_layer_v2

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

Returns:
- order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
- "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.

##### find_base_matrix(self)

##### create_list_values(self, rapp_type_list, value_list, ar, si)

##### us_extractor(self, res)

##### insert_into_dict(self, base_matrix, v)

##### insert_into_dict_equal(self, base_matrix, v)

##### remove_from_list_in_dict(self, curr_base_matrix)

### LogHandler

Handler personalizzato per mostrare i log in un QTextEdit

**Inherits from**: logging.Handler

#### Methods

##### __init__(self, text_widget)

##### emit(self, record)

### Order_layer_graph

Versione ottimizzata con grafi in memoria per il calcolo del matrix stratigrafico.
Carica tutti i dati in memoria una volta sola, evitando query ripetute.

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

##### center_on_screen(self, widget)

##### main_order_layer(self)

Metodo principale che calcola l'ordine stratigrafico usando grafi in memoria.

Returns:
- order_dict (dict): Il dizionario con l'ordinamento delle US per livelli
- "error" (str): In caso di errore

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

##### find_base_matrix(self)

Trova le US di base (senza predecessori) - compatibilità con vecchio codice

##### create_list_values(self, rapp_type_list, value_list, ar, si)

Metodo mantenuto per compatibilità

##### us_extractor(self, res)

Metodo mantenuto per compatibilità

##### insert_into_dict(self, base_matrix, v)

Metodo mantenuto per compatibilità

##### remove_from_list_in_dict(self, curr_base_matrix)

Metodo mantenuto per compatibilità

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato.
Mantiene aperta la finestra di progress durante l'aggiornamento.

Args:
    db_manager: Il DB manager per le query
    mapper_table_class: La classe mapper della tabella
    id_table: Il nome del campo ID
    sito: Il sito
    area: L'area

Returns:
    int: Numero di record aggiornati

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

### MyError

**Inherits from**: Exception

#### Methods

##### __init__(self, value)

##### __str__(self)

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

## Functions

### dfs(node, path)

**Parameters:**
- `node`
- `path`

### dfs(node, path)

**Parameters:**
- `node`
- `path`

### dfs(node, path)

**Parameters:**
- `node`
- `path`

### dfs(node, path)

**Parameters:**
- `node`
- `path`

