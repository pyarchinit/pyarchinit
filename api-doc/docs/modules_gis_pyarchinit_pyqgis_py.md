# modules/gis/pyarchinit_pyqgis.py

## Overview

This file contains 72 documented elements.

## Classes

### Pyarchinit_pyqgis

`Pyarchinit_pyqgis` is a QGIS dialog class (`QDialog`) that serves as the primary geospatial layer management interface for the pyarchinit archaeological information system. It handles loading, filtering, styling, and organizing vector layers from both SpatiaLite and PostgreSQL/PostGIS databases into the QGIS layer tree, covering all core archaeological data types including stratigraphic units (US/USM), documentation, finds, sites, individuals, taphonomy, structures, and topographic units (UT). The class provides multilingual support for layer and group names across ten languages, determined at class load time from the QGIS locale setting, and applies rule-based and nested symbology to stratigraphic view layers.

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

Initializes a new instance of the class by calling the parent class constructor via `super().__init__()`. Stores the provided `iface` parameter as an instance attribute for later use.

##### create_us_nested_symbology(self, layer, site_filter)

Create nested rule-based symbology for US layer.

Creates a hierarchy where:
- Parent rules: one per US number (us_s)
- Child rules: one per stratigraph_index_us within each US

This way, toggling a US on/off will toggle all its stratigraph_index variants together.

Args:
    layer: QgsVectorLayer to apply symbology to
    site_filter: Optional site filter expression (e.g., "sito = 'MySite'")

Returns:
    True if successful, False otherwise

##### load_us_view_with_sketched_sketched_sketched(self, db_path, view_name, filter_expr, srid, layer_name, use_sketched_sketched_sketched)

Load US view (pyarchinit_us_view or pyarchinit_usm_view) with optional nested symbology.

Args:
    db_path: Path to database (SQLite)
    view_name: Name of the view ('pyarchinit_us_view' or 'pyarchinit_usm_view')
    filter_expr: Optional filter expression
    srid: Optional SRID
    layer_name: Name for the layer (defaults to view_name)
    use_sketched_sketched_sketched: If True, apply nested US symbology

Returns:
    QgsVectorLayer or None

##### remove_USlayer_from_registry(self)

*No description available.*
Removes the US (Unità Stratigrafica) map layer from the QGIS project registry by calling `QgsProject.instance().removeMapLayer()` with the instance's `USLayerId`. This effectively unregisters the layer from the current QGIS project. Returns `0` upon completion.

##### charge_individui_us(self, data)

Loads and displays filtered stratigraphic unit (US/SE/SU) and elevation view layers in QGIS for a given list of record identifiers, supporting both SQLite/SpatiaLite and PostgreSQL backends. The method reads database connection settings from a configuration file, constructs a filter expression based on the provided `data` list of `id_us` values, and loads the corresponding `pyarchinit_us_view` and `pyarchinit_quote_view` spatial views as QGIS vector layers. Both layers are assigned unique names (localised according to the language setting `self.L`), grouped under a collapsed layer tree group, and registered with the current QGIS project; nested symbology is applied to the US view layer via `create_us_nested_symbology`.

##### charge_vector_layers_from_matrix(self, idus)

Loads and registers vector layers for stratigraphic unit (US/SE/SU) and elevation (Quote/Hoch/Elevation) views into the QGIS map registry, filtered by the provided `idus` identifier. It reads database connection settings from the application configuration file and branches execution based on whether the backend is SQLite (SpatiaLite) or PostgreSQL, loading the corresponding view layers via the appropriate provider. Valid layers are assigned unique names, styled with locale-appropriate QML style files, grouped under a dedicated layer tree group named via `_gn('view_us_matrix')`, and added to the current QGIS project.

##### charge_vector_layers_doc(self, data)

Loads and registers multiple documentation-related vector layers into a new QGIS layer group named after the `view_documentazione` group key, based on the provided `data` list of documentation records. It reads database connection settings from the application configuration file and branches execution for either a SpatiaLite (`sqlite`) or PostgreSQL (`postgres`) backend, constructing attribute filter expressions from the `sito`, `nome_doc`, and `tipo_documentazione` fields of each record. For each backend, it attempts to load layers from the views `pyarchinit_sezioni_view`, `pyarchinit_doc_view`, `pyarchinit_us_negative_doc_view`, `pyarchinit_us_view`, and `pyarchinit_usm_view`, inserting valid layers into the group and displaying a warning dialog for any that fail validation.

##### charge_vector_layers_doc_from_scheda_US(self, lista_draw_doc)

Loads multiple QGIS vector layers from database views filtered by site, area, stratigraphic unit, documentation type, and document name, as extracted from the five-element list `lista_draw_doc`. The method reads database connection settings from `config.cfg` and branches on the configured server type (`sqlite` or `postgres`) to query the views `pyarchinit_doc_view`, `pyarchinit_us_negative_doc_view`, `pyarchinit_us_view`, and `pyarchinit_usm_view`, adding each valid layer to a new, collapsed QGIS layer group named via `_gn('view_us_documentazione')`. Layer display names are resolved according to the active interface language (`self.L`), and a warning dialog is shown for any layer that fails validation.

##### charge_vector_layers(self, data)

Loads and registers stratigraphic unit (US/SU/SE) vector layers into the QGIS project by reading database connection settings from the configuration file and querying either a SpatiaLite or PostgreSQL backend. For each supported database type, it loads two view-based vector layers — an elevation/quote layer and a stratigraphic unit view layer — applies named styles and categorized symbology via `USViewStyler`, and inserts them into a dedicated layer tree group. Optionally leverages a Rust extension to accelerate style category computation, and adapts layer names and filter expressions according to the active language setting (`self.L`) and the provided `data` records.

##### charge_usm_layers(self, data)

Loads and registers QGIS vector layers for USM (Unità Stratigrafica Muraria) vertical stratigraphy and elevation views into a new, collapsed layer group in the current QGIS project. Reads database connection settings from the configuration file and branches execution based on the server type (`sqlite` or `postgres`), constructing appropriate data source URIs and applying filters derived from the supplied `data` list. For each backend, it loads a quote (elevation) layer and a stratigraphy layer, assigns localized names based on `self.L`, applies QML styles and symbology, and inserts both layers into the group; invalid layers trigger a `QMessageBox` warning.

##### charge_ut_layers(self, data)

Load UT (Unità Topografica) geometry layers.

Args:
    data: List of UT records with progetto and nr_ut attributes

##### charge_vector_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

Loads and registers QGIS vector layers for stratigraphic units and their associated elevation data, filtered by site and period context, into a named layer group within the current QGIS project. The method reads database connection settings from a configuration file and supports both SQLite/SpatiaLite and PostgreSQL backends, constructing a filter expression based on `sito_p` and `cont_per` to retrieve matching records from `pyarchinit_us_view` and `pyarchinit_quote_view`. Layer names are assigned according to the active language setting (`self.L`), and named QML styles are applied to each loaded layer before insertion into the group.

##### charge_vector_usm_layers_periodo(self, sito_p, cont_per, per_label, fas_label, dat)

*No description available.*
Loads vertical stratigraphic unit (USM) vector layers filtered by site and chronological period into the current QGIS project. It reads database connection settings from the `config.cfg` configuration file and creates a named, collapsed layer group in the QGIS layer tree, then loads two views — `pyarchinit_quote_usm_view` (elevation data) and `pyarchinit_usm_view` (stratigraphic units) — applying provider-specific logic for either a SpatiaLite or PostgreSQL backend. Layer names are set according to the active language (`self.L`), named styles are applied from the configured style paths, and a warning dialog is displayed if the USM layer is invalid.

##### charge_vector_layers_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

Loads and registers stratigraphic unit (US) and elevation (Quote) vector layers into the current QGIS project for all periods specified in `cont_per`, grouped under a single named layer tree group. For each period, it constructs a filtered data source query scoped to the given site (`sito_p`) and period context, then loads the corresponding layers from either a SpatiaLite or PostgreSQL database as determined by the application configuration. If the US layer carries a `QgsRuleBasedRenderer`, its rules are refined with the period filter expression, a user-selected style preference is applied (load, save, or temporary), and valid layers are inserted into the group and added to the `QgsProject` instance; invalid layers trigger a warning dialog.

##### charge_vector_layers_usm_all_period(self, sito_p, cont_per, per_label, fas_label, dat)

Loads vector layers for vertical stratigraphic masonry units (USM) and their associated elevation data (quote) for all periods matching a given site and stratigraphic context period, adding them to a named QGIS layer group. The method reads database connection settings from a configuration file and supports both SQLite/SpatiaLite and PostgreSQL backends, constructing a filter expression that matches the specified `cont_per` value including hierarchical slash-delimited variants. Layer names are localized based on the language setting (`self.L`), and each valid layer is assigned a named style and inserted into a collapsed QGIS layer tree group.

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

*No description available.*
Retrieves the fields from the data provider of the currently active layer on the map canvas. It accesses the current layer via `self.iface.mapCanvas().currentLayer()`, calls `dataProvider().fields()` on it, and returns the resulting fields collection.

##### selectedFeatures(self)

*No description available.*
Retrieves the currently selected features from the active layer on the map canvas. It accesses the current layer via `self.iface.mapCanvas().currentLayer()` and returns the result of calling `selectedFeatures()` on that layer. Returns the collection of selected features as provided by the layer's data provider.

##### findFieldFrDict(self, fn)

*No description available.*
Searches for a field by name within the data provider's fields dictionary, as returned by `dataProviderFields()`. Iterates over all entries in the dictionary and returns the key (`res`) corresponding to the field whose `.name()` matches the provided `fn` argument; returns `None` if no match is found. **Note:** according to inline comments in the source, this function is marked as no longer working after a changelog update and is pending restoration.

##### findItemInAttributeMap(self, fp, fl)

*No description available.*
Accepts a field position `fp` and a features list `fl`, storing them as instance attributes `self.field_position` and `self.features_list` respectively. Iterates over the currently selected features of the active map canvas layer, retrieving the attribute value at the specified field position from each feature's attribute map and collecting the results as strings. Returns a list of those string values.

> **Note:** Per the inline comment in the source, this method is marked as non-functional following a changelog and is pending restoration (`###FUNZIONE DA RIPRISTINARE PER le selectedFeatures / ##non funziona piu dopo changelog`).

##### charge_layers_for_draw(self, options)

*No description available.*
Loads all pyarchinit archaeological vector layers from either a SpatiaLite or PostgreSQL database into the QGIS map registry, depending on the server type specified in the project configuration file (`config.cfg`). The layers are organized into a collapsed layer group named `layer_archeologici`, which contains three subgroups (`rif_localizzazione`, `linee_riferimento`, and `ingombri`) into which individual layers such as `pyarchinit_individui`, `pyunitastratigrafiche`, `pyarchinit_siti`, `pyarchinit_reperti`, and others are inserted. For the SpatiaLite backend, the SRID is dynamically retrieved from the `geometry_columns` table of the database and applied to each layer's coordinate reference system; if any layer fails validation, a warning dialog is displayed.

##### charge_sites_geometry(self, options, col, val)

Loads and organizes all archaeological site geometry layers for a specified site value into a structured QGIS layer tree group, supporting both SpatiaLite (`sqlite`) and PostgreSQL (`postgres`) database backends as determined by the application configuration file. The method creates a named root group containing three subgroups — `rif_localizzazione`, `linee_riferimento`, and `ingombri` — and distributes layers such as `pyarchinit_individui`, `pyunitastratigrafiche`, `pyarchinit_siti`, `pyarchinit_tafonomia`, `pyarchinit_sezioni`, and others across these subgroups, each filtered by the provided site value. For SpatiaLite connections, the CRS is derived from the SRID stored in the `geometry_columns` table of the database; if any layer fails validation, a warning dialog is displayed.

##### charge_sites_from_research(self, data)

Loads and displays site geometry layers in QGIS based on a list of site records provided in `data`. It reads the database connection settings from the `config.cfg` file, constructs a SQL filter expression matching the site names in `data`, and loads the `pyarchinit_site_view` layer using either a SpatiaLite or PostgreSQL provider depending on the configured server type. The resulting layer is added to a new, collapsed layer tree group named after the `view_sito` group identifier, and the map canvas extent is updated to match the layer's extent if the layer is valid.

##### charge_reperti_layers(self, data)

*No description available.*
Loads artefact (reperti) records as a QGIS vector layer from either a SpatiaLite or PostgreSQL database, depending on the server type defined in the project configuration file. It constructs a SQL filter expression based on the `numero_inventario` values present in the provided `data` list, querying the `pyarchinit_reperti_view` view, and adds the resulting layer to a dedicated layer tree group named via `_gn('view_reperti')`. For SpatiaLite connections, the CRS is set explicitly using the SRID retrieved from the `geometry_columns` table; if the layer is invalid for either backend, a warning dialog is displayed.

##### charge_tomba_layers(self, data)

Loads the `pyarchinit_tomba_view` spatial layer into the QGIS map for a given set of tomb records provided via the `data` parameter. It reads database connection settings from `config.cfg`, constructs a filter expression based on `nr_scheda_taf` values from the data, and adds the resulting vector layer to a new, collapsed layer group named via `_gn('view_tomba')`. Both SQLite/SpatiaLite and PostgreSQL/PostGIS backends are supported; if the layer is invalid, a warning dialog is displayed.

##### charge_vector_layers_all_st(self, sito_p, sigla_st, n_st)

Loads and displays vector layers for a specific archaeological structure into a QGIS project by filtering records based on site (`sito_p`), structure abbreviation (`sigla_st`), and structure number (`n_st`). It reads database connection settings from a configuration file and supports both SQLite/SpatiaLite and PostgreSQL backends, querying the `pyarchinit_strutture_view` view with the appropriate provider in each case. The resulting layer is added to a newly created, collapsed layer tree group named after the structure, and the map canvas extent is adjusted to match the loaded layer.

##### charge_structure_from_research(self, data)

Loads and displays spatial structure (`struttura`) data from a research result set onto the QGIS map canvas. It reads database connection settings from the configuration file, constructs a filter expression based on the `id_struttura` values present in `data`, and loads the `pyarchinit_strutture_view` layer using either a SpatiaLite or PostgreSQL connection depending on the configured server type. The resulting layer is added to a new, collapsed layer tree group named via `_gn('view_struttura')`; if the layer is invalid, a warning dialog is displayed.

##### charge_individui_from_research(self, data)

*No description available.*
Loads the `pyarchinit_individui_view` spatial layer into the QGIS map canvas based on a list of individual records returned from a research query. The method reads the database connection settings from the `config.cfg` file and constructs a SQL filter expression using the `id_scheda_ind` field of each record in `data`, supporting both SQLite/SpatiaLite and PostgreSQL backends. The resulting vector layer is inserted into a dedicated layer tree group named via `_gn('view_individui')`; if the layer is invalid, a warning dialog is displayed to the user.

##### unique_layer_name(self, base_name)

funzione per creare un nome unico alle view quando vengono caricate

##### internet_on(self)

*No description available.*
Checks for internet connectivity by attempting to open a WMS capabilities request to `https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php` with a timeout of 0.5 seconds. Returns `True` if the request succeeds, or `False` if a `urllib.error.URLError` is raised, indicating that the connection could not be established.

### Order_layer_v2

*No description available.*
A QGIS-integrated class that computes the stratigraphic ordering of archaeological units (US) by iteratively traversing a matrix of stratigraphic relationships stored in a database. Starting from the base units of the matrix, it resolves equivalence relationships (e.g., "Same as", "Connected to") and superposition relationships (e.g., "Covers", "Fills", "Cuts") across successive cycles, building an ordered dictionary that maps each stratigraphic level to its corresponding units. Execution is bounded by a maximum cycle count of 3000 and a 90-second timeout, and the process is accompanied by a `QProgressBar` dialog; the method returns the ordered dictionary on success or the string `"error"` if limits are exceeded.

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

*No description available.*
Initializes the object by assigning the provided database connection and site/area identifiers to their corresponding instance attributes. The `dbconn` parameter is stored as `self.db`, while `SITOol` and `AREAol` are stored as `self.SITO` and `self.AREA` respectively.

##### center_on_screen(self, widget)

*No description available.*
Centers the given widget on the screen where the mouse cursor is currently located. It retrieves the widget's frame geometry and the center point of the active screen, then moves the widget so that its frame is aligned to that center point.

**Parameters:**
- `widget` — the Qt widget to be repositioned on the screen.

##### main_order_layer(self)

This method is used to perform the main order layering process. It takes no parameters and returns a dictionary or a string.

Returns:
- order_dict (dict): The dictionary containing the ordered matrix of user stories if the order_count is less than 3000.
- "error" (str): If the order_count is greater than or equal to 3000 or if the execution time exceeds 90 seconds.

##### find_base_matrix(self)

*No description available.*
Queries the database for records that do not match the current site (`SITO`) and area (`AREA`) using `select_not_like_from_db_sql`. Iterates over the returned result set, converting each record's `us` attribute to a string and appending it to a list. Returns the resulting list of `us` values as strings.

##### create_list_values(self, rapp_type_list, value_list, ar, si)

*No description available.*
Constructs and returns a list of formatted query strings by iterating over every combination of elements from `rapp_type_list` and `value_list`, pairing each combination with the `ar` and `si` parameters. Each resulting entry is a string formatted as `"['<rapp>', '<value>', '<ar>', '<si>']"` and appended to the output list. The method assigns all four input arguments to instance attributes before processing.

##### us_extractor(self, res)

*No description available.*
Accepts a collection of records `res` and iterates over each record to extract its `us` attribute. The extracted values are accumulated into a list, which is returned upon completion.

**Parameters:**
- `res` — An iterable of record objects, each expected to have a `us` attribute.

**Returns:** A list containing the `us` attribute value from each record in `res`.

##### insert_into_dict(self, base_matrix, v)

*No description available.*
Stores the provided `base_matrix` into the instance's `order_dict` at the current `order_count` index, then increments `order_count` to register a new ordering level. If the optional parameter `v` is set to `1`, the method first calls `remove_from_list_in_dict` on `base_matrix` before inserting it. The `base_matrix` value is also assigned to the instance attribute `self.base_matrix`.

##### insert_into_dict_equal(self, base_matrix, v)

*No description available.*
Inserts `base_matrix` into `self.order_dict` at the current `self.order_count` index, then increments `self.order_count` to register a new ordering level. If the parameter `v` is set to `1`, `remove_from_list_in_dict` is called on `base_matrix` before the insertion. The parameter `v` defaults to `0`, in which case no removal is performed prior to insertion.

##### remove_from_list_in_dict(self, curr_base_matrix)

*No description available.*
Iterates over all entries in `self.order_dict` and removes, from each associated list value, any element that matches an item in `curr_base_matrix` (compared as strings). Removal failures are silently suppressed via a bare `except` clause, ensuring the method continues processing all dictionary entries regardless of missing elements. After processing, each modified list is written back to its corresponding key in `self.order_dict`, and `curr_base_matrix` is stored as `self.curr_base_matrix`.

### LogHandler

Handler personalizzato per mostrare i log in un QTextEdit

**Inherits from**: logging.Handler

#### Methods

##### __init__(self, text_widget)

*No description available.*
Initializes a new `LogHandler` instance by invoking the parent `logging.Handler` constructor and storing the provided `text_widget` as an instance attribute. The `text_widget` parameter is expected to be a `QTextEdit` widget used to display log output.

##### emit(self, record)

*No description available.*
Formats and appends a log record to the associated text widget as a colour-coded HTML `<span>` element, applying red for `ERROR` and above, orange for `WARNING`, black for `INFO`, and gray for all lower levels. After inserting the message, it automatically scrolls the text widget's vertical scrollbar to its maximum position to keep the latest entry visible. Finally, it calls `QApplication.processEvents()` to ensure the UI is updated immediately.

### Order_layer_graph

Versione ottimizzata con grafi in memoria per il calcolo del matrix stratigrafico.
Carica tutti i dati in memoria una volta sola, evitando query ripetute.

**Inherits from**: object

#### Methods

##### __init__(self, dbconn, SITOol, AREAol)

Initializes an instance of the class by establishing a database connection and setting the site and area identifiers from the provided arguments. It initializes internal data structures for graph processing, including adjacency and reverse adjacency mappings, equality relationships between nodes, and a complete node set, as well as counters and dictionaries for ordering. It also sets up optional UI widget references for progress and logging output, initializes the list for generated levels, and invokes `_setup_logging()` to configure the logging system.

##### center_on_screen(self, widget)

*No description available.*
Positions the given `widget` at the center of the screen on which the mouse cursor is currently located. It retrieves the widget's frame geometry and the center point of the active screen, then moves the widget so that its frame center aligns with the screen center.

##### main_order_layer(self, reverse_order)

Metodo principale che calcola l'ordine stratigrafico usando grafi in memoria.

Args:
    reverse_order (bool): Se True, ordina da antico a recente (default).
                         Se False, ordina da recente ad antico.

Returns:
- order_dict (dict): Il dizionario con l'ordinamento delle US per livelli
- "error" (str): In caso di errore

##### update_database_with_order(self, db_manager, mapper_table_class, id_table, sito, area)

Aggiorna il database con l'order layer calcolato — versione batch.

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

##### close_progress_widget(self)

Chiude manualmente la finestra di progress se ancora aperta

### MyError

*No description available.*
A custom exception class that extends the built-in `Exception`. It accepts a single `value` argument upon instantiation, storing it as an instance attribute. The `__str__` method returns the `repr()` of the stored value when the exception is converted to a string.

**Inherits from**: Exception

#### Methods

##### __init__(self, value)

*No description available.*
Initializes a `MyError` exception instance with the provided value. Stores the given `value` argument as an instance attribute (`self.value`).

##### __str__(self)

*No description available.*
Returns the string representation of the object by delegating to `repr(self.value)`. This means the built-in `repr()` output of the stored `value` attribute is used as the human-readable string form of the instance. Consequently, calling `str()` on this object produces the same result as calling `repr()` directly on `self.value`.

### ProgressDialog

*No description available.*
A wrapper class around Qt's `QProgressDialog` that displays a modal progress dialog for updating area and site reports ("Aggiornamento rapporti area e sito"). On initialization, the dialog is configured with an indeterminate range, a modal window, and an Italian-language label ("Inizializzazione..."). The class exposes a `setValue` method to update the displayed progress label text and a `closeEvent` method to programmatically close the underlying dialog.

#### Methods

##### __init__(self)

## `__init__` — `ProgressDialog`

Initializes a `ProgressDialog` instance by creating and configuring a `QProgressDialog` widget. Sets the window title to `"Aggiornamento rapporti area e sito"`, the label text to `"Inizializzazione..."`, and configures the dialog with an indeterminate range `(0, 0)` in modal mode. The dialog is immediately displayed upon initialization via `show()`.

##### setValue(self, value)

*No description available.*
Updates the progress dialog with the specified value by calling `setValue(value)` on the internal `progressDialog` instance. If `value` is less than `value + 1` (which is always true as written), the dialog label is set to the Italian text `"Aggiornamento in corso... {value}"`; otherwise, the label is set to `"Finito"`. The branch that sets the label to `"Finito"` and the commented-out `close()` call are unreachable given the current condition.

##### closeEvent(self, event)

*No description available.*
Handles the close event triggered when the widget is about to be closed. It closes the associated `progressDialog` before suppressing the close action by calling `event.ignore()`, which prevents the widget itself from being closed.

## Functions

### generate_us_color(us_val)

Generate a consistent color based on US value

**Parameters:**
- `us_val`

