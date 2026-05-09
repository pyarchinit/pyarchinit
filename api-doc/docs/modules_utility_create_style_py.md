# modules/utility/create_style.py

## Overview

This file contains 15 documented elements.

## Classes

### ThesaurusStyler

*No description available.*
Manages the loading and application of QML-based fill styles to QGIS vector layers using a thesaurus mapping. It initialises with a default QML style file path, from which it extracts a `QgsFillSymbol` to serve as the base style, falling back to a simple grey fill symbol if the file is unavailable or invalid. The class applies categorized rendering to a target layer by mapping field values through a provided thesaurus dictionary and assigning each category a randomly coloured, semi-transparent symbol derived from the default style.

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

*No description available.*
Manages the creation and application of QGIS vector layer styles for stratigraphic unit (US) data loaded from a database connection. The class queries the `us_table` to retrieve stratigraphic records, generates rule-based fill symbols differentiated by stratigraphic phase, unit type, and stratigraphic index, and provides interactive workflows for applying, saving, or loading named styles to a target layer. It also enforces feature rendering order based on `order_layer` and `stratigraph_index_us` fields to ensure correct stratigraphic drawing sequence.

#### Methods

##### __init__(self, connection, sito)

*No description available.*
Initializes a `USViewStyler` instance by storing the provided `connection` object and optional `sito` parameter as instance attributes. A SQLAlchemy engine is created from the connection string, and the database server type is determined as either `"sqlite"` or `"postgres"` based on the connection string prefix. Upon initialization, stratigraphic unit data is immediately loaded via `_load_us_data()` and the corresponding styles are generated via `_create_styles_for_us()`, storing the results in `self.us_data` and `self.us_styles` respectively.

##### ask_user_style_preference(self)

Displays a locale-aware modal dialog prompting the user to choose how to manage a layer's style. The dialog presents four options — save a new style, load an existing style, use a temporary style, or apply a single-symbol outline-only style — with labels rendered in Italian or English based on the QGIS user locale setting. Returns one of the string values `"save"`, `"load"`, `"null_fill"`, or `"temp"` corresponding to the button clicked by the user.

##### ask_user_categorization_field(self, layer)

Ask user which field to use for rule-based categorization.
Only shows fields that are available in the layer.
Uses localized labels based on QGIS language settings.

Args:
    layer: Optional QgsVectorLayer to check for available fields

Returns the selected field name or default if cancelled.

##### load_style_from_db(self, layer)

*No description available.*
Retrieves and returns a style XML string from the database for the given layer by calling `layer.listStylesInDatabase()`. If exactly one style is found, it is loaded automatically; if multiple styles exist, the user is prompted via a `QInputDialog` to select one by name. Returns `None` if the styles data is invalid, no styles are found, the selection is cancelled, or an exception occurs during the process.

##### load_style_from_db_new(self, layer)

*No description available.*
Retrieves a style definition in XML format from the database associated with the given layer by calling `layer.listStylesInDatabase()`. If exactly one style is found, it is loaded automatically; if multiple styles are present, a `QInputDialog` prompt is displayed to allow the user to select the desired style by name. Returns the style XML string on success, or `None` if no styles are found, the selection is cancelled, or an error occurs.

##### apply_style_to_layer(self, layer)

*No description available.*
Applies a visual style to the given QGIS vector layer based on user preference and field availability. The method first validates the layer and checks for required fields (`stratigraph_index_us`, `tipo_us_s`) and at least one categorization field (`d_stratigrafica`, `tipo_us_s`, `d_interpretativa`), then prompts the user to choose between loading a saved style from the database, applying a null-fill (transparent fill with dark grey outline) style, or generating and optionally saving a temporary categorized style. After applying the chosen style, the method triggers a layer repaint, emits a legend change signal, and invokes `_apply_feature_ordering` to ensure correct stratigraphic rendering order.

##### show_message(self, message)

Mostra un messaggio all'utente.

##### save_style_to_db(self, layer)

Prompts the user via a `QInputDialog` to enter a name for the style, then reads the current style from the provided `layer` using `QgsMapLayerStyle` and attempts to save it to the database by calling `layer.saveStyleToDatabase`. If the save operation raises an exception or returns `None`, diagnostic information is printed or displayed via `show_message`; if the user cancels the dialog or leaves the name empty, a cancellation message is shown. Any outer exception during the process is also caught and reported through `show_message`.

##### get_all_styles(self)

*No description available.*
Returns the `us_styles` collection held by the instance. This method provides direct access to all styles currently stored in the object without applying any filtering or transformation.

