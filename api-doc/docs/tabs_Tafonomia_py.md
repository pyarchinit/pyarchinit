# tabs/Tafonomia.py

## Overview

This file contains 68 documented elements.

## Classes

### pyarchinit_Tomba

`pyarchinit_Tomba` is a QGIS `QDialog` subclass that implements the taphonomic record form ("Scheda Tafonomica") within the PyArchInit archaeological data management plugin. It provides a full data-entry, browsing, searching, sorting, and deletion interface for burial records stored in `Tomba_table`, mapping to the `TOMBA` ORM class with fields covering site, structure, individual, burial rite, skeletal position, grave goods, conservation state, orientation, and chronological phasing. The dialog adapts its labels, field dictionaries (`CONVERSION_DICT`), and sort item lists to the active QGIS user locale, supporting Italian, German, English, Spanish, French, Arabic, Catalan, Romanian, Portuguese, Greek, and other languages.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the form widget by calling the parent constructor, storing the QGIS interface reference, and setting up the UI via `setupUi`. Applies the active theme, initializes a theme toggle button, and attempts a database connection via `on_pushButton_connect_pressed`, displaying a warning dialog if the connection fails. Completes initialization by customizing the GUI, wiring signal/slot connections for site, period, and phase combo boxes, and invoking `fill_fields`, `set_sito`, and `msg_sito` to populate and configure the form state.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all listed controls to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously by passing the value `n` to each button's `setEnabled` method. The buttons affected are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the main toolbar controls as a group.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` instance, detecting whether the target database is SQLite, and initialising the database manager via `get_db_manager`. If the database contains existing records, it populates the UI with the first record, updates browse status and record counters, and loads field data; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`) and triggers new record creation. Any exception encountered during connection or data loading is reported as a localised warning message pushed to the QGIS message bar.

##### customize_GUI(self)

*No description available.*
Applies initial customization settings to the graphical user interface components of the form. Specifically, it enables editing on a set of combo boxes (`comboBox_sito`, `comboBox_sigla_struttura`, `comboBox_nr_struttura`, `comboBox_nr_individuo`, `comboBox_per_iniz`, `comboBox_fas_iniz`, `comboBox_per_fin`, and `comboBox_fas_fin`) and enables the `lineEdit_nr_scheda` line edit field. Several additional combo box customizations are present in the method body but are currently commented out.

##### loadMapPreview(self, mode)

*No description available.*
Loads or clears a map preview in the `mapPreview` canvas based on the specified `mode`. When `mode` is `0`, it constructs a filter expression using the current record's ID, loads the corresponding geometry layer via `self.pyQGIS.loadMapPreview`, assigns it to the canvas, and zooms to the full extent. When `mode` is `1`, it clears all layers from the canvas and resets the zoom to the full extent.

##### loadMediaPreview(self, mode)

*No description available.*
Loads a media preview with an optional mode parameter that defaults to `0`. The method body contains no implemented logic in the provided source.

**Parameters:** `mode` *(int, optional)* — Controls the preview loading behavior; defaults to `0`. See implementation for details.

##### openWide_image(self)

*No description available.*
Opens the current media item in a wide or expanded image view. This method provides an enlarged display mode for the associated image content. It takes no parameters and returns no documented value.

##### charge_list(self)

Populates all combo box widgets in the form by querying the database for site names and thesaurus entries filtered by the current user locale language. Site names are retrieved from `site_table` via a `group_by` query, while all other combo boxes (`rito`, `segnacoli`, `canale_libatorio`, `oggetti_esterno`, `conservazione_taf`, `copertura_tipo`, `tipo_contenitore_resti`, `corredo_presenza`, `disturbato`, `completo`, `in_connessione`) are populated from the `PYARCHINIT_THESAURUS_SIGLE` table using language-specific, typology-coded queries against `Tomba_table`. Each list is sorted alphabetically before being added to its corresponding combo box; errors encountered during the site list update are reported via a localized `QMessageBox` warning.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured site setting via a `Connection` instance and compares it against the value selected in `comboBox_sito`. If both values are non-empty and match, an informational `QMessageBox` is displayed confirming the active site connection. If the configured site setting is an empty string, a warning `QMessageBox` is displayed notifying the user that no site has been set and all records will be visible.

##### set_sito(self)

## `set_sito` Method

Retrieves the configured site setting via a `Connection` object and, if a site value is present, queries the database for all records matching that site using `query_bool`. The resulting records are loaded into `DATA_LIST`, the UI fields are populated via `fill_fields()`, browse and sort statuses are updated, and the site combo box is disabled to prevent modification. If the specified site does not exist in the current table, an informational `QMessageBox` is displayed advising the user to either deactivate the site filter in the plugin configuration or create the corresponding record.

##### charge_periodo_iniz_list(self)

*No description available.*
Queries the database for `PERIODIZZAZIONE` records matching the currently selected site (`comboBox_sito`) and populates the `comboBox_per_iniz` combo box with a deduplicated list of period values. After clearing and reloading the combo box items, it conditionally sets the displayed text to an empty string or attempts to restore the initial period value from the current record in `DATA_LIST`, depending on the active browse status. Any exceptions during the period removal or text restoration steps are silently suppressed.

##### charge_periodo_fin_list(self)

Queries the database for periodization records associated with the currently selected site in `comboBox_sito`, then populates `comboBox_per_fin` with a deduplicated list of period values retrieved from the `PERIODIZZAZIONE` table. After clearing and reloading the combo box items, it sets the edit text of `comboBox_per_fin` based on the current browse status: an empty string when in "Trova"/"Find" mode, or the `periodo_iniziale` value of the current record when in "Usa"/"Current" mode.

##### charge_fase_iniz_list(self)

*No description available.*
Queries the database for phase (`fase`) records from the `PERIODIZZAZIONE` table matching the currently selected site (`comboBox_sito`) and initial period (`comboBox_per_iniz`). The retrieved phase values are deduplicated, sorted, and loaded into the `comboBox_fas_iniz` combo box after clearing its previous contents. If the current browse status corresponds to "Trova" or "Find", the combo box edit text is cleared; otherwise, it is set to the initial phase value of the current record in `DATA_LIST`.

##### charge_fase_fin_list(self)

*No description available.*
Queries the `PERIODIZZAZIONE` database table using the currently selected site (`comboBox_sito`) and final period (`comboBox_per_fin`) as search criteria, then populates the `comboBox_fas_fin` combo box with a sorted, deduplicated list of matching phase values. Empty string entries are removed from the list before it is displayed. If the current browse status corresponds to "Trova" or "Find", the combo box edit text is cleared; otherwise, it is set to the final phase value of the current record.

##### charge_struttura_list(self)

Queries the database for all `STRUTTURA` records matching the currently selected site (`comboBox_sito`), then extracts and deduplicates the `sigla_struttura` and `numero_struttura` field values from the results. Each deduplicated list is sorted, stripped of empty entries, and used to populate the corresponding combo boxes (`comboBox_sigla_struttura` and `comboBox_nr_struttura`), which are cleared beforehand and reset to an empty edit text after loading.

##### charge_individuo_list(self)

*No description available.*
Queries the database for all `SCHEDAIND` records matching the currently selected site (`comboBox_sito`) and extracts their `nr_individuo` values into a sorted list. Empty string entries are removed from the list before sorting. The resulting list is then used to populate `comboBox_nr_individuo`, which is cleared and reset to an empty edit text beforehand.

##### on_pushButton_exp_index_pressed(self)

Handles the press event of the export index button by generating a PDF index document for Tomba records. It instantiates a `generate_tomba_pdf` object and retrieves a data list via `generate_list_pdf`, then delegates the PDF construction to `build_index_Tomba`, passing the full data list and the first element of the first record as arguments.

##### on_toolButtonPan_toggled(self)

*No description available.*
Handles the toggle event for the pan tool button by instantiating a `QgsMapToolPan` object bound to the `mapPreview` canvas. The newly created pan tool is then set as the active map tool on `mapPreview` via `setMapTool`, enabling pan interaction on the map canvas.

##### on_pushButton_showSelectedFeatures_pressed(self)

Retrieves the currently selected map features and resolves their corresponding record identifiers by locating the relevant field position within the attribute map. Queries the database manager to fetch and sort the matching records, then populates `DATA_LIST` with the results and refreshes the form fields. Sets the browse status to `'b'` and updates the record counter to reflect the newly loaded selection.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available `SORT_ITEMS`, allowing the user to select sort fields and order type. If the record state check passes, the selected items are converted using `CONVERSION_DICT`, and the current data list is re-queried and reordered via `DB_MANAGER.query_sort` using the converted sort fields and specified sort mode. Upon completion, the browse status is set to `'b'`, the sort status is set to `'o'`, the record counter and status labels are updated, and the fields are refreshed to reflect the first record of the newly sorted list.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle event for the GIS mode button (`toolButtonGis`), displaying a localized notification message to the user whenever the button's checked state changes. If the button becomes checked, a message is shown indicating that GIS mode has been activated and search results will be displayed on the GIS; if unchecked, a message is shown indicating that GIS mode has been deactivated. The notification message is rendered in Italian (`it`), German (`de`), or English (default) based on the value of `self.L`.

##### on_toolButtonPreview_toggled(self)

*No description available.*
Handles the toggle state change of `toolButtonPreview`, displaying a localized informational message and updating the map preview accordingly. When the button is checked, it shows a warning dialog notifying the user that Preview SU mode has been enabled and calls `loadMapPreview()` with no arguments; when unchecked, it calls `loadMapPreview(1)` without displaying a message. The displayed message text is determined by the current language setting (`self.L`), with distinct strings provided for Italian (`'it'`), German (`'de'`), and a default English fallback.

##### on_toolButtonPreviewMedia_toggled(self)

*No description available.*
Handles the toggle event for the `toolButtonPreviewMedia` button, responding to its checked state to enable or disable the media preview mode. When the button is checked, a language-specific warning message is displayed (Italian, German, or English depending on `self.L`) informing the user that SU/SE media preview mode has been activated, then calls `self.loadMediaPreview()` to load the preview. When the button is unchecked, `self.loadMediaPreview(1)` is called directly without displaying a message.

##### on_pushButton_addRaster_pressed(self)

*No description available.*
Event handler triggered when the `pushButton_addRaster` button is pressed. If the `toolButtonGis` toggle button is currently checked, it invokes `addRasterLayer()` on the `pyQGIS` instance to add a raster layer. No action is taken if `toolButtonGis` is not in a checked state.

##### on_pushButton_new_rec_pressed(self)

Handles the "New Record" button press event by preparing the form to accept a new entry. If the current record has been modified while in browse mode, it prompts the user (in Italian, German, or English depending on `self.L`) to save pending changes before proceeding. Once any unsaved changes are resolved, it transitions `BROWSE_STATUS` to `"n"`, clears the form fields (preserving the site selection if it matches the configured site set), and configures the enabled and editable states of the relevant combo boxes and input fields accordingly.

##### on_pushButton_save_pressed(self)

Handles the save button press event by branching logic based on the current `BROWSE_STATUS` value. In browse mode (`"b"`), it performs a data validation check via `data_error_check()` and, if the record has been modified (as determined by `records_equal_check()`), prompts the user with a localized confirmation dialog before calling `update_if()` to persist the changes; if no modifications are detected, a localized warning is displayed. In non-browse mode (new record entry), it validates the data and attempts to insert a new record via `insert_new_rec()`, updating UI controls, record counters, combo box states, and field contents upon success, or displaying a localized error message upon failure.

##### data_error_check(self)

*No description available.*
Validates the site (`sito`) input field by checking whether it is empty using an `Error_check` instance. If the field is empty, a language-specific warning dialog is displayed — in Italian (`it`), German (`de`), or English (default) — and the internal test flag is set to `1`. Returns `0` if validation passes, or `1` if a validation error is detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates all field values from the form UI — including table widgets (`caratteristiche`, `corredo_tipo`, `misurazioni`), combo boxes, line edits, and text edits — and constructs a new tomb record (`tomba`) for insertion into the database. Numeric fields such as `orientamento_azimut`, `lunghezza_scheletro`, and period/phase identifiers are converted to their appropriate types (`float` or `int`), with empty inputs mapped to `None`. The method attempts to persist the record via `DB_MANAGER.insert_data_session`, returning `1` on success or `0` on failure, and displays a localized warning `QMessageBox` if an integrity error or other exception occurs.

##### on_pushButton_insert_row_corredo_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button for the corredo section is pressed. It delegates to `insert_new_row`, passing `'self.tableWidget_corredo_tipo'` as the target table widget into which a new row is inserted.

##### on_pushButton_remove_row_corredo_pressed(self)

*No description available.*
Event handler triggered when the "remove row" button associated with the corredo section is pressed. It delegates execution to the `remove_row` method, passing `'self.tableWidget_corredo_tipo'` as the target table widget. This results in the removal of a row from the `tableWidget_corredo_tipo` table widget.

##### on_pushButton_insert_row_caratteristiche_pressed(self)

Handles the press event of the "insert row" button associated with the *caratteristiche* section. Calls `insert_new_row` with the target widget identifier `'self.tableWidget_caratteristiche'` to add a new row to that table. No parameters are accepted and no value is returned.

##### on_pushButton_remove_row_caratteristiche_pressed(self)

Handles the press event of the "remove row" button associated with the `tableWidget_caratteristiche` widget. Delegates the row removal operation by calling `self.remove_row` with the string identifier `'self.tableWidget_caratteristiche'` as its argument.

##### on_pushButton_insert_row_misure_pressed(self)

Inserts a new row into the `tableWidget_misurazioni` table widget by invoking `insert_new_row` with the string reference `'self.tableWidget_misurazioni'`. This method serves as the slot handler for the `pushButton_insert_row_misure` button's pressed signal. It delegates all row insertion logic to the `insert_new_row` method.

##### on_pushButton_remove_row_misure_pressed(self)

Removes a row from the `tableWidget_misurazioni` table widget by delegating to the `remove_row` method with `'self.tableWidget_misurazioni'` as the target argument. This method is triggered when the `pushButton_remove_row_misure` button is pressed.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If no data errors are found and the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the changes, and delegates the response to `update_if()`. Returns `1` if data entry errors exist, or `0` if no errors are present.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the "View All" button press event by loading and displaying the complete set of records. If `check_record_state()` returns `1`, no action is taken; otherwise, the form fields are cleared, all records are reloaded via `charge_records()`, and the first record is displayed by populating the fields accordingly. The browse status is set to `"b"`, the record counter is updated to reflect the total number of records, and the sort label is reset to the unsorted state.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the data list by resetting the current record index (`REC_CORR`) to `0` and the total record count (`REC_TOT`) to the length of `DATA_LIST`. Before navigating, it calls `check_record_state()` and aborts the operation if the return value is `1`. On success, it clears the current fields via `empty_fields()`, populates them with the first record via `fill_fields(0)`, and updates the record counter display; any exception raised during this process is caught and presented to the user as a warning dialog.

##### on_pushButton_last_rec_pressed(self)

Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during execution is caught and displayed to the user via a `QMessageBox` warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles navigation to the previous record when the corresponding button is pressed. If the current record state check passes, it decrements `REC_CORR` by one; if the result is `-1`, it resets `REC_CORR` to `0` and displays a localized warning message (Italian, German, or English) indicating that the first record has been reached. Otherwise, it clears the current fields, populates them with the data for the new current record, and updates the record counter display.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a localized warning message indicating the user is already at the last record (supporting Italian, German, and a default English message). Otherwise, it clears the current form fields, populates them with the next record's data, and updates the record counter display.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed, the record identified by `self.ID_TABLE` at `self.DATA_LIST[self.REC_CORR]` is removed, and the data list is reloaded; if the database becomes empty afterward, all record-tracking fields are reset and the form is cleared, otherwise the UI is updated to display the first record in browse status.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by transitioning the form into search (`"f"`) browse status, provided the current record state does not block the action. Depending on whether the current site (`comboBox_sito`) matches the configured site set from the database connection, it selectively enables or disables combo boxes, line edits, text edits, and table widgets to prepare the form for a new search query. It also resets the status label, record counter, sort label, and clears the input fields — reloading the site list only when the site combo box is made fully editable.

##### on_pushButton_showLayer_pressed(self)

*No description available.*
Handles the press event of the "Show Layer" button. Retrieves the currently selected record from `DATA_LIST` using the current record index (`REC_CORR`) and packages it into a single-element list. Passes that list to `self.pyQGIS.charge_vector_layers` to load the corresponding vector layer in QGIS.

##### on_pushButton_crea_codice_periodo_pressed(self)

Handles the press event of the "crea codice periodo" button by retrieving the currently selected site name from `comboBox_sito` and invoking `DB_MANAGER.update_cont_per` to update the period code for that site in the database. After the update, it resets the form fields, reloads all records, and repopulates the fields for the current record index (`REC_CORR`). Finally, it displays a confirmation dialog informing the user that the period code has been updated for the selected excavation site.

##### on_pushButton_search_go_pressed(self)

Handles the execution of a database search when the search button is pressed. If the current browse status is not `"f"` (search mode), a language-appropriate warning is displayed instructing the user to initiate a new search first. Otherwise, field values are collected from the form controls, converted to their appropriate types, assembled into a `search_dict`, stripped of empty entries via `Utility.remove_empty_items_fr_dict`, and passed to `DB_MANAGER.query_bool`; depending on whether matching records are found, `DATA_LIST` is updated, form fields and combo boxes are reconfigured, the record counter and browse status are updated to `"b"`, and a language-appropriate summary message is displayed, with optional GIS layer loading if `toolButtonGis` is checked.

##### on_pushButton_pdf_exp_pressed(self)

*No description available.*
Handles the PDF export button press event by generating a PDF sheet for tomb (Tomba) records based on the currently active language setting (`self.L`). It instantiates a `generate_tomba_pdf` object and retrieves the data to export via `self.generate_list_pdf()`, then delegates the PDF construction to the appropriate language-specific build method: `build_Tomba_sheets` for Italian (`'it'`), `build_Tomba_sheets_de` for German (`'de'`), or `build_Tomba_sheets_en` for all other languages.

##### generate_list_pdf(self)

*No description available.*
Iterates over all records in `self.DATA_LIST` and compiles a structured list of data entries for PDF generation. For each record, it queries the database for associated individual (`SCHEDAIND`) and structure (`US`) records, retrieves their corresponding elevation values (`quote`) via `select_quote_from_db_sql`, and determines minimum and maximum elevation strings — falling back to a localised "not inserted in GIS" message (in Italian, German, or English based on `self.L`) when no GIS data is available. Each entry is appended to `data_list` as a 40-element list containing tomb record fields, computed elevation bounds, and associated US lists, which is then returned for use by `build_Tomba_sheets_en`.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, it calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration depending on `SORT_STATUS`. Returns `1` if the update succeeds, `0` if it fails, and `None` if the user did not confirm.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `self.DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `self.rec_toupdate()`. Returns `1` on success, or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default).

##### rec_toupdate(self)

*No description available.*
Retrieves the record designated for updating by delegating to the `UTILITY` object's `pos_none_in_list` method, passing `DATA_LIST_REC_TEMP` as the argument. Returns the resulting record object or value produced by `pos_none_in_list`.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the mapped table class, ordered by the table's ID column in ascending order. The results are stored directly in the instance attribute `self.DATA_LIST`, replacing any previously held data. This method uses a single ordered query to improve performance over a double-query pattern.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it as a `DD-MM-YYYY` string via `strftime`. The formatted date string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves the corresponding table widget attribute on the instance (stripping a `"self."` prefix if present), and iterates over all rows and columns of that table. For each row, it collects the text content of non-`None` cells into a sub-list, discarding empty sub-lists. Returns a list of sub-lists, where each non-empty sub-list represents the text values of a single row.

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields_nosite(self)

*No description available.*
Clears and resets all input fields and table widgets in the form, preserving the current site (`comboBox_sito`) value without modification. All rows are removed from `tableWidget_caratteristiche`, `tableWidget_corredo_tipo`, and `tableWidget_misurazioni`, each of which is then re-initialized with a single blank row via `insert_new_row`. All remaining combo boxes, line edits, and text edits — covering fields such as structure details, rite, description, interpretation, skeletal measurements, burial attributes, and chronological data — are cleared or reset to empty strings.

##### empty_fields(self)

Resets all input fields in the form to their default empty state. It first removes all existing rows from the `tableWidget_caratteristiche`, `tableWidget_corredo_tipo`, and `tableWidget_misurazioni` table widgets, then inserts a single new blank row into each. All combo boxes, line edits, and text edit fields across the form are then cleared of any current values.

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` within `DATA_LIST`, setting `self.rec_num` to the provided index before reading field values. Directly mapped UI controls — including combo boxes, line edits, text edits, and table widgets — are populated with the corresponding attributes of the selected record, covering fields such as site, burial card number, structure identifiers, rite, descriptions, skeletal position, grave goods, measurements, and chronological data. Nullable fields (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `orientamento_azimut`, `lunghezza_scheletro`) are explicitly checked and set to an empty string when `None`; if the map or media preview toolbar buttons are active, their respective previews are also refreshed. Any exception raised during execution is silently suppressed.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot_2` and `label_rec_corrente_2` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects and validates the current values from all form fields and widgets, converting empty strings to `None` for optional fields including `nr_scheda`, `nr_struttura`, `nr_individuo`, `orientamento_azimut`, `lunghezza_scheletro`, and the period/phase combo boxes. Table widget contents for `caratteristiche`, `corredo_tipo`, and `misurazioni` are extracted via `table2dict`. The resulting values are assembled into `self.DATA_LIST_REC_TEMP` as a list of 34 string entries representing the complete temporary record state of the current form.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by clearing it and iterating over `TABLE_FIELDS`, retrieving the corresponding attribute value from the current record (`DATA_LIST[REC_CORR]`) for each field. Each retrieved attribute value is converted to a string and appended to `DATA_LIST_REC_CORR`. This method is called as part of `records_equal_check` to build a snapshot of the current record's stored data for comparison purposes.

##### records_equal_check(self)

*No description available.*
Compares the current record against the corresponding record in the data list by first populating both `DATA_LIST_REC_TEMP` and `DATA_LIST_REC_CORR` via `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`. Returns `0` if the two lists are equal, indicating no changes have been made, or `1` if they differ, indicating the records are not identical.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode (`'w'`) and writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are explicitly cast to `str` before use. This method does not return a value and provides no error handling for file I/O operations.

