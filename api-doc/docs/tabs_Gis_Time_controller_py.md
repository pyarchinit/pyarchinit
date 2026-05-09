# tabs/Gis_Time_controller.py

## Overview

This file contains 27 documented elements.

## Classes

### ZoomableGraphicsView

*No description available.*
A `QGraphicsView` subclass that provides mouse wheel-driven zoom functionality with position-anchored scaling. It initializes with antialiasing and smooth pixmap transform render hints, and enables scroll-hand drag mode for panning. On each wheel event, the view scales in or out by a factor of 1.25, translating the scene to keep the cursor's scene position stable during zoom.

**Inherits from**: QGraphicsView

#### Methods

##### __init__(self, parent)

*No description available.*
Initializes a `ZoomableGraphicsView` instance by calling the parent `QGraphicsView` constructor with the optional `parent` widget. Enables antialiasing and smooth pixmap transform render hints to improve visual quality. Sets the drag mode to `ScrollHandDrag`, allowing the user to pan the view by clicking and dragging.

##### wheelEvent(self, event)

*No description available.*
Handles mouse wheel events to implement zoom functionality on the graphics view. When the wheel is scrolled forward, the view is scaled up by a factor of 1.25; when scrolled backward, it is scaled down by the reciprocal of that factor. The scene position under the cursor is preserved across the zoom operation by computing the delta between the pre- and post-scale scene coordinates and applying a compensating translation.

### pyarchinit_Gis_Time_Controller

`pyarchinit_Gis_Time_Controller` is a QDialog-based controller that provides a GIS time management interface for the PyArchInit QGIS plugin, enabling users to filter and visualize archaeological stratigraphic unit (US) layers by relative chronological order (`order_layer`). It exposes controls — a dial, a spin box, and a checkable layer list — to step through stratigraphic levels in either cumulative (`order_layer <= value`) or single-level (`order_layer = value`) mode, applying the corresponding subset filter to all selected map layers. The class also supports atlas generation by iterating over all order-layer values, exporting a georeferenced layout image per valid level, and optionally embedding a Harris matrix graphic into each exported plate.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the widget instance by setting up the QGIS interface reference, configuring UI components via `setupUi`, and establishing internal state including a debounce timer (300 ms, single-shot) for dial/spinbox interactions and cached site/area string fields. It scans all layers in the current QGIS project to identify those containing an `order_layer` field, populates a `listWidget` with checkable items for each relevant layer, and conditionally creates a `checkBox_cumulative` widget (defaulting to unchecked) with localized text based on the active language. Signal-slot connections are then established between UI controls — including the dial, spinbox, list widget, matrix checkbox, and stop button — and their respective handler methods, and an initial database connection attempt is made via `self.connect()`.

##### connect(self)

*No description available.*
Attempts to establish a database connection by instantiating a `Connection` object and retrieving its connection string, then initialises `self.DB_MANAGER` via `get_db_manager` using that string with singleton mode enabled. If an exception occurs and its message contains `"no such table"`, the method displays a localised warning message through the QGIS message bar, with distinct messages for Italian (`'it'`), German (`'de'`), and a default English fallback, each advising the user to restart QGIS.

##### update_selected_layers(self)

*No description available.*
Iterates over all items in `self.listWidget` and collects the text of those whose check state equals `Qt.CheckState.Checked`. Updates `self.selected_layers` by filtering `self.relevant_layers` to retain only those layers whose name appears in the collected list of checked item names.

##### update_layers(self, layers)

*No description available.*
Accepts a list of `QgsMapLayer` objects and stores it in the instance attribute `self.selected_layers`. This method serves as the mechanism for registering the currently selected layers within the instance for subsequent use by other methods, such as `set_max_num`.

**Parameters:**
- `layers` — a list of `QgsMapLayer` objects representing the selected layers to be stored.

##### set_max_num(self)

*No description available.*
Initializes the relative chronology controls by building a `datazione_dict` dictionary that maps each `order_layer` value to its corresponding list of `datazione` attribute values, iterating over all layers stored in `self.selected_layers`. If `selected_layers` is empty or `None`, an error message is added to `self.listWidget` and the method returns early. The method then determines the maximum `order_layer` value for the current site by querying the database — falling back to a global maximum if the site-scoped query fails — increments it by one, applies it as the upper bound of both `self.dial_relative_cronology` and `self.spinBox_relative_cronology`, and connects the spin box's `valueChanged` signal to `self.update_datazione`.

##### update_graphics_view(self)

*No description available.*
Refreshes the graphics view by regenerating the Harris matrix when the matrix checkbox is checked. It iterates over all selected layers, collecting feature data whose `order_layer` attribute is less than or equal to the current value of `spinBox_relative_cronology`, then passes the collected data and dating information to `pyarchinit_view_Matrix_pre` to generate an updated matrix image. The existing `graphicsView` widget is replaced with a new `ZoomableGraphicsView` instance, which loads and displays the generated matrix image from the expected output path while preserving aspect ratio; any `AssertionError` raised during the process is caught and displayed as a warning dialog.

##### define_order_layer_value(self, v, apply_period_filter)

Aggiorna il filtro dei layer in base al valore di order_layer e opzionalmente alla periodizzazione.

Args:
    v: Valore di order_layer
    apply_period_filter: Se True, applica anche il filtro sulla periodizzazione basato sull'intervallo cronologico

##### update_datazione(self, value)

*No description available.*
Looks up the given `value` in `self.datazione_dict` and retrieves the associated list of datazioni entries. Duplicate entries are removed by converting the list to a set, and the resulting unique values are joined with newline characters and displayed in `self.textEdit_datazione` as plain text.

##### liststring(self, sito, area, i, e, periodi_fasi, cumulative)

Imposta il filtro sui layer in base a order_layer, sito, area e opzionalmente periodizzazione.

Args:
    sito: Lista di siti da filtrare
    area: Lista di aree da filtrare
    i: Layer
    e: Data provider
    periodi_fasi: Lista opzionale di tuple (periodo, fase) per filtrare le US
    cumulative: Se True usa "order_layer <= valore" (cumulativo), se False usa "order_layer = valore" (singolo livello)

##### on_pushButton_visualize_pressed(self)

*No description available.*
Handles the press event of the visualize button by querying the database for `PERIODIZZAZIONE` records whose chronological range overlaps with the interval defined by `spinBox_cron_iniz` and `spinBox_cron_fin`. If matching periods are found, it retrieves the associated `US` records for each period and attempts to load them as vector layers via `self.pyQGIS.charge_vector_layers`; if no periods or no geometries are found, a localized warning dialog is displayed in Italian, German, or English depending on `self.L`. After loading the layers, it calls `self.update_graphics_view()`, catching any `AssertionError` and displaying a warning if the required layer is not selected in the TOC.

##### on_pushButton_atlas_pressed(self)

*No description available.*
Slot method triggered when the atlas push button is pressed. It delegates execution to the `generate_images()` method, which handles the atlas image generation process.

##### load_template(self, template_path)

*No description available.*
Loads a QGIS print layout from an XML template file located at `template_path` and registers it with the current project's layout manager. If a layout named `'layout_Time_Manager'` already exists in the manager, it is removed before the new layout is added. The newly created layout is assigned the name `'layout_Time_Manager'`, added to the project, and stored as `self.current_layout`.

##### get_available_templates(self)

Ottiene la lista dei template disponibili

##### choose_template(self)

Dialog avanzato per scegliere il template da utilizzare

##### browse_for_template(self, parent_dialog)

Permette di sfogliare per un template personalizzato

##### create_new_template(self, parent_dialog)

Crea un nuovo template da zero

##### open_layout_designer(self)

Apre il Layout Designer di QGIS per modificare il template corrente

##### save_current_as_template(self)

Salva il layout corrente come nuovo template

##### generate_images(self)

Orchestrates the generation of a series of atlas layout images (tavole) by first prompting the user to select a layout template and an output directory, then iterating over all `order_layer` values from 0 to the maximum found in the database. For each `order_layer` that contains at least one feature with a valid `datazione` attribute, the method refreshes the map canvas, updates the HTML title element and optionally the Harris matrix image within the current QGIS layout, and exports the rendered layout to a JPEG file named `Tavola_{value}.jpg` in the chosen directory. A non-modal `QProgressDialog` tracks progress throughout the operation, and the process can be cancelled by the user at any iteration; upon completion or cancellation, an informational message box reports the results.

##### stop_processes_named(self, name)

*No description available.*
Iterates over all currently running system processes using `psutil.process_iter` and terminates any process whose name matches the provided `name` argument. Each matching process is killed via `proc.kill()`; if the process no longer exists at the time of termination, a `psutil.NoSuchProcess` exception is caught and an informational `QMessageBox` dialog is displayed to the user. The method does not return a value.

##### stop_image_generation(self)

*No description available.*
Terminates the active image generation process by stopping all running `dot` executable instances appropriate to the current operating system (`dot.exe` on Windows, `dot` on macOS and Linux). After halting the platform-specific processes, it sets the `abort` flag to `True` to signal that the generation operation has been cancelled.

## Functions

### update_info()

*No description available.*
Retrieves the currently selected item from `template_list` and updates `info_path_label` with the file path associated with that item. The path is read from the item's `Qt.ItemDataRole.UserRole` data and displayed in the label using the format `"Path: {path}"`. If no item is currently selected, the label is left unchanged.

