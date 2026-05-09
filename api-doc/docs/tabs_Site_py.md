# tabs/Site.py

## Overview

This file contains 69 documented elements.

## Classes

### QgsMapLayerRegistry

*No description available.*
A placeholder class with no implemented members or methods. Its purpose and behavior are not documented in the provided source.

### pyarchinit_Site

This class provides to manage the Site Sheet

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the form widget by calling the parent constructor, setting up the UI, and configuring core instance attributes including the QGIS interface, map canvas, and the `PYARCHINIT_HOME` environment variable. Applies the active theme via `ThemeManager`, adds a theme toggle button, and attempts an immediate database connection via `on_pushButton_connect_pressed()`, displaying a warning dialog if the connection fails. Also initializes concurrency management components (`ConcurrencyManager`, `RecordLockIndicator`), connects UI button signals to their respective slots, and starts a `QTimer` that fires every 60 seconds to check for concurrent record modifications.

##### setPathToSites(self)

Opens a directory selection dialog prompting the user to choose a folder, using the instance's `HOME` attribute as the initial directory. If a valid directory is selected, the chosen path is stored in `self.siti_path` and displayed in the `lineEdit_sito_path` text field.

##### openSiteDir(self)

*No description available.*
Opens the directory path specified in `lineEdit_sito_path` using the system's default file manager via `QDesktopServices.openUrl`. Before attempting to open, it verifies that the path exists on the filesystem using `os.path.exists`. If the directory does not exist, a warning message box is displayed to the user with the text `"Directory not found"`.

##### on_wms_vincoli_pressed(self)

*No description available.*
Creates a new layer tree group named `"Vincoli Archelogici"` in the current QGIS project and populates it with a subgroup `"Vincoli"` containing three WMS raster layers sourced from the Italian *Vincoli in Rete* (Beni Culturali) geoserver. The three layers — `"Vincoli puntuali"`, `"Vincoli Lineari"`, and `"Vincoli poligonali"` — represent point, linear, and polygonal archaeological heritage constraints respectively, each filtered by the municipality name currently selected in `self.comboBox_comune`. All three `QgsRasterLayer` instances are inserted into the subgroup and registered with the QGIS project without being added to the main layer panel tree root directly.

##### internet_on(self)

*No description available.*
Checks for an active internet connection by attempting to open a specific WMS capabilities URL (`https://wms.cartografia.agenziaentrate.gov.it/inspire/wms/ows01.php?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities`) with a timeout of 0.5 seconds. Returns `True` if the request succeeds, or `False` if a `urllib.error.URLError` is raised.

##### on_basemap_pressed(self)

*No description available.*
Handles the basemap loading action by first verifying internet connectivity via `internet_on()`. If a connection is available, it creates a collapsed layer group named `"BaseMap"` in the current QGIS project's layer tree and populates it with XYZ tile layers for Google Maps and Wikimedia Maps; when the language is set to Italian (`self.L == 'it'`), it additionally loads locale-specific WMS/WFS layers for Italian cadastral data (Catasto), IGM 25000 raster maps, and toponymy from the currently selected municipality. If no internet connection is detected, a warning `QMessageBox` is displayed to the user.

##### enable_button(self, n)

This method Unable or Enable the GUI buttons on browse modality

##### enable_button_search(self, n)

This method Unable or Enable the GUI buttons on searching modality

##### on_pushButton_connect_pressed(self)

This method establishes a connection between GUI and database

##### charge_list(self)

Populates the form's combo boxes with data retrieved from the database and predefined lists. It queries the `site_table` to load available site values into `comboBox_sito`, and conditionally populates `comboBox_regione` and `comboBox_provincia` with Italian regions and provinces when the interface language is set to Italian (`'it'`), or clears those lists otherwise. It also queries the `PYARCHINIT_THESAURUS_SIGLE` table using the current locale and a fixed typology code (`'1.1'`) to populate `comboBox_definizione_sito` with sorted site-definition values.

##### on_pushButton_pdf_pressed(self)

*No description available.*
Event handler triggered when the PDF push button is pressed. The method body contains no implemented logic in the provided source (`pass`).

> **Note:** The full implementation is not documented in source.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the current `SORT_ITEMS`, provided the record state check does not return `1`. Upon dialog confirmation, it converts the selected sort items using `CONVERSION_DICT`, applies the chosen sort order by querying the database via `DB_MANAGER.query_sort`, and rebuilds `DATA_LIST` with the sorted results. The method then resets the browse and sort status indicators, updates the record counter, and refreshes the displayed fields to reflect the newly sorted data.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking for unsaved changes when the current browse status is `"b"` (browse mode). If the current record has been modified, a language-sensitive warning dialog (Italian, German, or English) is displayed, prompting the user to save or discard the changes before proceeding. The method then transitions the UI to new-record mode (`"n"`), clearing all fields, updating status labels, enabling and making editable the site-related combo boxes, resetting the record counter, and disabling the action buttons.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behaviour based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it performs a version conflict check against `site_table` before validating data errors and comparing the current record against its stored state; if changes are detected, it prompts the user with a localised confirmation dialog (Italian, German, or English) before calling `update_if` to persist the modifications. Outside browse mode, it validates data, attempts to insert a new record via `insert_new_rec`, and on success resets the form state, refreshes the record list, and updates the UI controls accordingly.

##### data_error_check(self)

*No description available.*
Validates the required form fields before a record is saved by checking whether the site (`comboBox_sito`) field is empty using an `Error_check` instance. If the field is empty, a localized warning dialog is displayed to the user in Italian (`'it'`), German (`'de'`), or English (default), depending on the value of `self.L`. Returns `1` if a validation error is detected, or `0` if all checks pass.

##### insert_new_rec(self)

*No description available.*
Attempts to insert a new site record into the database by collecting values from the form's UI fields — including site name, nation, region, municipality, province, description, site definition, path, and a default find-check value of `0` — assigning it the next available ID via `max_num_id`. It then commits the record to the database session and returns `1` on success. On failure, it displays a localized warning dialog (Italian, German, or English) distinguishing between integrity constraint violations and other errors, returning `0` in either failure case.

##### check_record_state(self)

*No description available.*
Checks the current state of a record by first performing a data validation check via `data_error_check()`. If validation passes and the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the changes, and delegates the response to `update_if()`. Returns `1` if input errors are detected, or `0` if no input errors are present.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button by loading and displaying the complete set of records. If the record state check passes, the method clears the current fields, reloads all records, and updates the UI to reflect browse mode (`"b"`), resetting the record counter to the first entry in `DATA_LIST`. The sort label is also reset to its default unsorted state using `SORTED_ITEMS["n"]`.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data set. If the record state check (via `check_record_state`) does not return `1`, it clears the current fields with `empty_fields`, resets `REC_TOT` to the total number of items in `DATA_LIST` and `REC_CORR` to `0`, then populates the fields with the first record by calling `fill_fields(0)` and updates the record counter accordingly. Any exception raised during this process is caught and displayed to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any exception raised during the process is caught and displayed to the user as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles navigation to the previous record when the corresponding button is pressed. If the current record state check passes, it decrements `REC_CORR` by one; if the resulting index is `-1`, it resets `REC_CORR` to `0` and displays a localized warning message (Italian, German, or English) indicating that the first record has been reached. Otherwise, it clears the current fields, populates them with the data for the new current record, and updates the record counter display.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a localized warning message (Italian, German, or English) indicating that the last record has been reached. Otherwise, it clears the current fields, populates them with the next record's data via `fill_fields`, and updates the record counter display.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by prompting the user with a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed and succeeds, the method reloads the record list and either resets all data structures and counters if the database is empty, or navigates to the first record and refreshes the UI fields and record counter. Any exception raised during deletion is reported to the user via a warning dialog.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "New Search" button by first verifying the current record state via `check_record_state()`; if the check does not return `1`, the method proceeds to configure the interface for a new search operation. It sets `BROWSE_STATUS` to `"f"` (if not already), updates the status label, adjusts the enabled state of the site and site-definition combo boxes and description text field, resets the record counter and sort label, and reloads the list and clears all input fields. If `check_record_state()` returns `1`, no action is taken.

##### msg_sito(self)

Displays a localized informational message indicating the currently connected archaeological site by retrieving the configured site value via `Connection.sito_set()` and comparing it against the current selection in `comboBox_sito`. If the configured site matches the selected value, a confirmation dialog is shown in Italian, German, or English depending on `self.L`. If no site has been configured (empty string), a warning dialog prompts the user to set one, optionally opening the `pyArchInitDialog_Config` dialog if the user confirms.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` instance and, if a site value is present, queries the database for all records matching that site using `DB_MANAGER.query_bool`. If matching records are found, the method populates `DATA_LIST`, initialises the browse state, fills the form fields, updates the record counter, and disables the site combo box; if no records are found, it displays a localised informational message (Italian, German, or English) and returns without updating the UI. Any exception raised during execution is caught, logged to the console with a full traceback, and reported to the user via a localised warning dialog.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search button press event by first verifying that the form is in search mode (`BROWSE_STATUS == "f"`); if not, a localized warning is displayed instructing the user to initiate a new search. When in the correct state, it constructs a search dictionary from the current values of the site-related combo boxes and text fields (`sito`, `nazione`, `regione`, `comune`, `descrizione`, `provincia`, `definizione_sito`), removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database using `DB_MANAGER.query_bool`. Depending on the query result, it updates `DATA_LIST`, refreshes the displayed fields, sets `BROWSE_STATUS` to `"b"`, updates the record counter, adjusts the enabled state of relevant UI controls, and displays a localized message indicating the number of records found; appropriate warnings are shown if no search criteria were set or no records were returned.

##### on_pushButton_test_pressed(self)

*No description available.*
This method serves as the handler for the test push button's pressed event. The original test functionality has been removed and the method currently performs no operations, containing only a `pass` statement. It is retained as a placeholder, with an inline comment noting that the test area (`Test_area`) is no longer required.

##### on_pushButton_draw_pressed(self)

*No description available.*
Handler triggered when the draw push button is pressed. It invokes `self.pyQGIS.charge_layers_for_draw()`, passing a predefined list of layer identifiers (`["19", "12", "10", "7", "8", "13", "16", "3", "1", "2", "4", "5", "9", "24", "26"]`) to load the corresponding layers for drawing. No parameters are accepted and no value is returned.

##### on_pushButton_sites_geometry_pressed(self)

Retrieves the currently selected site value from `comboBox_sito` and passes it to `self.pyQGIS.charge_sites_geometry`, requesting geometry data for layers identified by the codes `"13"`, `"3"`, `"1"`, `"2"`, `"4"`, and `"24"`. The site value is used as a filter, applied against the field `"sito"`, to load only geometry records matching the selected site.

##### on_pushButton_draw_sito_pressed(self)

*No description available.*
Handles the press event of the "draw sito" button. Retrieves the currently selected record from `DATA_LIST` using the `REC_CORR` index, wraps it in a single-element list, and passes it to `self.pyQGIS.charge_sites_from_research` to load and render the corresponding site geometry on the map.

##### on_pushButton_rel_pdf_pressed(self)

Displays a warning dialog notifying the user that the feature is under testing and may contain bugs, requiring explicit confirmation before proceeding. If the user confirms by clicking **Ok**, it instantiates an `exp_rel_pdf` object using the current text of `comboBox_sito` and calls its `export_rel_pdf()` method to generate the PDF report. If the user cancels, no further action is taken.

##### on_toolButton_draw_siti_toggled(self)

Handles the toggle event of the `toolButton_draw_siti` button by displaying a localized warning message box to inform the user whether GIS mode has been activated or deactivated. The displayed message is determined by the current language setting (`self.L`), supporting Italian (`'it'`), German (`'de'`), and a default English fallback. When the button is checked, a message indicates that search results will be displayed on the GIS; when unchecked, a message indicates that GIS display has been disabled.

##### on_pushButton_genera_us_pressed(self)

*No description available.*
Slot triggered when the "genera US" push button is pressed. It calls `DB_MANAGER.insert_arbitrary_number_of_us_records` with the values retrieved from the UI controls — specifically the US range (`lineEdit_us_range`), site (`comboBox_sito`), area (`lineEdit_area`), US number (`lineEdit_n_us`), and US type (`comboBox_t_us`) — to insert the specified number of US (Stratigraphic Unit) records into the database. Upon completion, a confirmation message box is displayed in the appropriate language based on the value of `self.L` (`'it'` for Italian, `'de'` for German, or English as the default).

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the value of the `msg` parameter, proceeding only if `msg` equals `QMessageBox.StandardButton.Ok`. If the update succeeds (indicated by `update_record()` returning `1`), it rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or a custom sort order depending on `SORT_STATUS`, then sets `BROWSE_STATUS` to `"b"` and updates the status label accordingly. Returns `1` on success or `0` if the update fails.

##### charge_records(self)

*No description available.*
Loads all records from the database into the `DATA_LIST` attribute by executing a single ordered query against the mapped table class. The query retrieves results sorted by `ID_TABLE` in ascending order, using `DB_MANAGER.query_ordered()` to replace a previously used double-query pattern for improved performance.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name `n` as a string, resolves the corresponding table widget attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table. For each cell, it retrieves the item's text value if the item is non-empty, building a list of sub-lists where each sub-list represents one row's non-empty cell values. Returns the resulting list of lists containing the table's cell data as strings.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to their default empty state. This includes clearing the edit text of seven combo boxes (`comboBox_sito`, `comboBox_nazione`, `comboBox_regione`, `comboBox_comune`, `comboBox_provincia`, `comboBox_definizione_sito`), clearing the `textEdit_descrizione_site` text editor, and setting the `lineEdit_sito_path` line edit to an empty string.

##### fill_fields(self, n)

Populates all UI form fields with data from the record at index `n` in `DATA_LIST`, setting values for site, nation, region, municipality, description, province, site definition, and path fields (fields 1–8). Sets `self.rec_num` to the provided index `n` (defaulting to `0`). If a `concurrency_manager` attribute is present, the method additionally attempts to track the record's version number and ID (`id_sito`), update the lock indicator with any existing editing user information, and prepare a soft lock for the current record, logging a warning via `QgsMessageLog` if an error occurs during this process.

##### set_rec_counter(self, t, c)

Sets the total and current record counters for the UI display. Assigns the provided values `t` and `c` to `self.rec_tot` and `self.rec_corr` respectively, then updates the corresponding labels `label_rec_tot` and `label_rec_corrente` with their string representations.

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### set_LIST_REC_TEMP(self)

*No description available.*
Populates `DATA_LIST_REC_TEMP` with the current values from the form's input widgets, capturing a temporary snapshot of the record being edited. The list contains eight fields in order: Sito, Nazione, Regione, Comune, Descrizione, Provincia, Definizione sito, and path, sourced from their respective combo boxes, text edit, and line edit controls.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and then iterating over `TABLE_FIELDS` to extract the corresponding attribute values from the current record in `DATA_LIST`, identified by the `REC_CORR` index. Each extracted attribute value is converted to a string before being appended to `DATA_LIST_REC_CORR`.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `pos_none_in_list` on `self.DATA_LIST_REC_TEMP` via the `self.UTILITY` helper. The return value, `rec_to_update`, represents the output of that utility operation applied to the temporary record data list. This method contains no parameters beyond `self` and raises no documented exceptions.

##### records_equal_check(self)

*No description available.*
Compares the current temporary record data against the corresponding corrected record data to determine whether any changes have been made. It first refreshes both internal data lists by calling `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`, then performs a direct equality comparison between `DATA_LIST_REC_CORR` and `DATA_LIST_REC_TEMP`. Returns `0` if the two lists are equal, or `1` if they differ.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the result of `rec_toupdate()`. Returns `1` on success or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default).

##### testing(self, name_file, message)

*No description available.*
Opens a file at the path specified by `name_file` in write mode and writes the string representation of `message` to it, then closes the file. This method is used to persist a copy of data or error information to disk, typically in conjunction with encoding error handling in the surrounding context.

**Parameters:**
- `name_file` — The path and name of the file to be created or overwritten.
- `message` — The content to be written to the file, converted to a string via `str()`.

##### get_config(self, key, default)

*No description available.*
Retrieves a configuration parameter from the `PythonPlugins/pyarchinit/` namespace by appending the provided `key` to the base path and querying `self.config`. If the specified key does not exist, the method returns the `default` value, which defaults to an empty string. Returns the value associated with the constructed configuration path.

##### set_config(self, key, value)

*No description available.*
Stores a configuration parameter under the `PythonPlugins/pyarchinit/` namespace by appending the provided `key` to form the full configuration path. Delegates to `self.config.setValue()` to persist the value and returns its result.

##### reverse(self)

*No description available.*
Initiates a reverse geocoding operation by first validating the current plugin settings via `check_settings()`, displaying an error message and aborting if any configuration issues are found. If settings are valid, it updates the status bar with a prompt instructing the user to click on the map, then installs a `ClickTool` as the active map tool on the canvas, storing the previously active map tool in `self.previous_map_tool`. The `ClickTool` is configured to invoke `self.reverse_action` upon a map click event.

##### reverse_action(self, point)

*No description available.*
Performs a reverse geocoding lookup for a given map point by first transforming its coordinates to WGS84, then querying the configured geocoder instance to retrieve the corresponding address. If a result is returned, it displays the resolved address in an informational dialog and saves the point along with the address via `save_point`; if the result is empty or an exception occurs, an appropriate error dialog is shown instead. All intermediate coordinate values and geocoder responses are written to the log via `logMessage`.

##### on_pushButton_locate_pressed(self)

*No description available.*
Handler triggered when the locate push button is pressed. It restores the previous map tool if one exists, validates the current settings via `check_settings()`, and attempts to geocode the address entered in the `address` field using the configured geocoder instance. If a single result is returned it is processed directly via `process_point()`; if multiple results are returned, a `PlaceSelectionDialog` is presented to the user to select the desired location before processing.

##### logMessage(self, msg)

*No description available.*
Logs a message to the QGIS message log under the `'GeoCoding'` tag by calling `QgsMessageLog.logMessage`. The message is only written if the `'writeDebug'` configuration option is enabled, as determined by `self.get_config('writeDebug')`.

##### get_geocoder_instance(self)

Loads a concrete Geocoder class

##### process_point(self, place, point)

Transforms the point and save

##### save_point(self, point, address)

*No description available.*
Saves a geographic point (expressed in the project's coordinate reference system) along with its associated address to an in-memory QGIS vector layer named `"Pyrchinit localizzazione trovata"`. If the layer already exists in the project registry, it is removed and recreated; if it does not exist, a new point layer is created with `id` and `indirizzo` fields, labeling configured, and the layer registered in the project. After adding the feature, the method extends the layer with additional address-derived fields (`sito`, `nazione`, `regione`, `comune`, `descrizione`, `provincia`) populated by splitting the address string on commas, then commits all changes and refreshes the map canvas.

##### check_settings(self)

*No description available.*
Validates the current QGIS project's coordinate reference system (CRS) configuration when running under Qt version 4. If on-the-fly reprojection is disabled and the destination CRS is not `EPSG:4326`, the method returns a translated error message instructing the user to enable on-the-fly reprojection. Returns an empty string if no configuration issues are detected.

### GeoCodeException

*No description available.*
A custom exception class that extends Python's built-in `Exception`. It serves as a specialised exception type for geocoding-related errors within the `pyarchinit` plugin. The class provides no additional methods or attributes beyond those inherited from `Exception`.

**Inherits from**: Exception

### OsmGeoCoder

*No description available.*
A geocoding client that interfaces with the OpenStreetMap Nominatim REST API to perform forward and reverse geocoding operations. The `geocode` method converts a text address into a list of `(display_name, (lon, lat))` tuples, while the `reverse` method converts a longitude/latitude coordinate pair into a single-element list of the same structure. Both methods raise `GeoCodeException` on failure and log each constructed request URL via the plugin's debug logging mechanism.

#### Methods

##### geocode(self, address)

*No description available.*
Sends a forward geocoding request to the Nominatim OpenStreetMap search API for the given address, decoding it from UTF-8 before constructing the request URL. Performs a blocking HTTP request and parses the JSON response, returning a list of tuples where each tuple contains the display name and a `(lon, lat)` coordinate pair for each result. Raises a `GeoCodeException` if any error occurs during the request or parsing process.

##### reverse(self, lon, lat)

single result

## Functions

### logMessage(msg)

*No description available.*
Logs a message to the QGIS message log under the `'GeoCoding'` category, but only if the `'PythonPlugins/pyarchinit/writeDebug'` setting is enabled in `QgsSettings`. The function takes a single parameter, `msg`, which is the message string to be logged. No value is returned.

**Parameters:**
- `msg`

