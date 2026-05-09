# tabs/UT.py

## Overview

This file contains 71 documented elements.

## Classes

### pyarchinit_UT

`pyarchinit_UT` is a QDialog subclass that implements the Topographic Unit (UT/TU/TE) data entry and management form within the PyArchInit QGIS plugin. It provides a full record management interface for the `ut_table` database table, supporting browsing, searching, inserting, updating, and deleting UT records, along with media attachment, PDF export, GNA GeoPackage export, and optional archaeological potential/risk analysis. The class is fully internationalised, adapting its field labels, status messages, sort items, and conversion dictionaries to the active QGIS locale across Italian, German, English, Spanish, French, Arabic, Catalan, Romanian, Portuguese, Greek, and other languages.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the form by calling the parent constructor, storing the provided `iface` reference, and instantiating a `Pyarchinit_pyqgis` object. Sets up the UI, applies the current theme and adds a theme toggle button, configures drag-and-drop support on `iconListWidget`, and attempts a database connection via `on_pushButton_connect_pressed`, displaying a warning dialog if the connection fails. Completes initialization by setting the site context, displaying a site message, and wiring up the analysis tab signals.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI navigation and action buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. The parameter `n` is passed directly to `setEnabled`, and is expected to be a boolean or equivalent value controlling whether the buttons are interactive.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons include `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, `pushButton_sort`, `pushButton_insert_row_documentazione`, `pushButton_remove_row_documentazione`, `pushButton_insert_row_bibliografia`, and `pushButton_remove_row_bibliografia`. This method is typically used to collectively enable or disable the main navigation, record management, and row manipulation controls based on the boolean-compatible value of `n`.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using `Connection` and `get_db_manager`, detecting whether the backend is SQLite, and loading records via `charge_records()`. If the database contains existing records, it initialises navigation state, updates status and sort labels, sets the record counter, and populates the UI fields; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`) and triggers new record creation. Any exception encountered during connection or loading is reported as a localised warning message in the QGIS message bar.

##### customize_GUI(self)

*No description available.*
Sets the initial column widths for two table widgets in the user interface. Specifically, it sets the first column of `tableWidget_bibliografia` to a width of 380 pixels, and configures `tableWidget_documentazione` with its first column at 150 pixels and its second column at 300 pixels.

##### charge_list(self)

Populates the UI combo boxes with data required for site-related forms. It retrieves the list of sites from the database via `DB_MANAGER.group_by`, removes any empty entries, sorts the results, and loads them into `comboBox_progetto`; it also populates `comboBox_regione` and `comboBox_provincia` with hardcoded lists of Italian regions and provinces respectively. Any errors encountered during the site list retrieval are reported to the user via a localized `QMessageBox` warning, with messages available in Italian, German, and English. Finally, it delegates loading of thesaurus values to `charge_thesaurus_combos`.

##### charge_thesaurus_combos(self)

Load thesaurus values for UT survey comboboxes

##### msg_sito(self)

*No description available.*
Retrieves the currently configured site setting via a `Connection` instance and compares it against the value selected in `comboBox_progetto`. If the selected project matches the configured site, an informational `QMessageBox` is displayed confirming the active site connection; if no site has been configured (empty string), a warning `QMessageBox` notifies the user that all records will be visible.

##### set_sito(self)

*No description available.*
Retrieves the configured site (`sito_set`) from the `Connection` object and, if a site string is present, queries the database for all records whose `progetto` field matches that value. If matching records are found, the method populates `DATA_LIST`, sets `comboBox_progetto` to the site string (disabling further editing), loads the first record into the form via `fill_fields()`, and updates the browse status and record counter accordingly. If no records are found, a localised informational message is displayed (Italian, German, or English based on `self.L`); any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the current `SORT_ITEMS`, allowing the user to select sort fields and order type. If no record edit is in progress (i.e., `check_record_state()` does not return `1`), it converts the selected items using `CONVERSION_DICT`, queries the database via `DB_MANAGER.query_sort()` using the current record IDs, and replaces `DATA_LIST` with the sorted results. The UI is then updated to browse mode, resetting the record counter, status labels, and field display to reflect the newly sorted dataset.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether any unsaved changes exist in the current record. If the browse status is `"b"` (browse mode) and the record has been modified (as detected by `records_equal_check`), the user is prompted via a localized warning dialog (Italian, German, or English depending on `self.L`) to confirm whether changes should be saved before proceeding. The method then transitions the interface to new-record mode (`"n"`), clears all fields, updates status labels and the record counter, configures the editability and enabled state of relevant combo boxes and input fields, and disables action buttons.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behaviour based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it first validates the data via `data_error_check()` and, if the record has been modified (as determined by `records_equal_check()`), prompts the user with a localised confirmation dialog (Italian, German, or English) before calling `update_if()` to persist the changes; if no modifications are detected, a localised warning is displayed instead. In insert mode, it validates the data and attempts to insert a new record via `insert_new_rec()`, then refreshes the UI state, record counters, combo box configurations, and field values upon success, or displays a localised error message on failure.

##### data_error_check(self)

*No description available.*
Validates the required input fields of the form by checking that the Project (`comboBox_progetto`) and UT/TU number (`comboBox_nr_ut`) combo boxes are not empty, and that the UT/TU number value is numeric when provided. Validation messages are displayed via `QMessageBox.warning` dialogs in the appropriate language based on the `self.L` attribute, supporting Italian (`'it'`), German (`'de'`), and a default English fallback. Returns `0` if all checks pass, or `1` if one or more validation errors are detected.

##### insert_new_rec(self)

*No description available.*
Collects all field values from the UI form — including location details, survey metadata, bibliographic references, documentation, periodization data, and optional new survey fields (visibility percentage, GPS method, vegetation coverage, etc.) — and constructs a new record by calling `DB_MANAGER.insert_ut_values` with the next available ID. The assembled record is then persisted to the database via `DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` on failure, displaying a localized warning dialog (Italian, German, or English) if an `IntegrityError` or other exception occurs during insertion.

##### check_record_state(self)

*No description available.*
Checks the current state of the active record by first performing a data validation check via `data_error_check()`. If validation passes and the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the changes, then delegates the response to `update_if()`. Returns `1` if input errors are detected, or `0` if no input errors are present.

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

remove row into a table based on table_name

##### on_pushButton_insert_row_documentazione_pressed(self)

*No description available.*
Slot method triggered when the "insert row" push button for the documentation section is pressed. It calls `insert_new_row` with `'self.tableWidget_documentazione'` as the target table, inserting a new row into the documentation table widget.

##### on_pushButton_remove_row_documentazione_pressed(self)

*No description available.*
Slot method triggered when the "remove row" button for the documentation section is pressed. It delegates to `self.remove_row`, passing `'self.tableWidget_documentazione'` as the target table identifier to remove a row from the documentation table widget.

##### on_pushButton_insert_row_bibliografia_pressed(self)

*No description available.*
Event handler triggered when the insert row button for the bibliography section is pressed. It calls `insert_new_row` with `'self.tableWidget_bibliografia'` as the target, adding a new row to the bibliography table widget.

##### on_pushButton_remove_row_bibliografia_pressed(self)

*No description available.*
Event handler triggered when the "remove row" button is pressed in the bibliography section. It delegates to the `remove_row` method, passing `'self.tableWidget_bibliografia'` as the target widget to identify the table from which a row will be removed.

##### on_pushButton_view_all_pressed(self)

Handles the "View All" button press event by verifying the current record state before loading all records. If the record state check does not return `1`, it clears the current fields, reloads all records, and repopulates the fields, then sets the browse status to `"b"` and updates the status label accordingly. It also resets the record counter and sort label to their default states, positioning the view at the first record in `DATA_LIST`.

##### on_pushButton_show_layer_pressed(self)

Load UT geometry layers for current record(s)

##### on_toolButtonGis_2_toggled(self, checked)

Toggle GIS layer auto-loading when navigating records

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the data list. If the current record has been modified (as determined by `records_equal_check()`), a localized warning dialog is displayed in Italian, German, or English prompting the user to save pending changes before proceeding. The method then clears the current fields, resets the record counter to position 1, and populates the fields with the first entry in `DATA_LIST`, displaying an error dialog if an exception occurs.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Handles the press event of the "last record" navigation button. If the current record has been modified (as determined by `records_equal_check()`), the method prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the pending changes before navigating, passing the dialog result to `update_if()`. It then clears the current fields, sets `REC_CORR` to the index of the last entry in `DATA_LIST`, populates the form with that record via `fill_fields()`, and updates the record counter display; any exception raised during this process is reported via a `QMessageBox` warning.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by first checking whether the current record has unsaved modifications via `check_record_state()`. If unsaved changes are detected, a localized warning dialog is displayed (in Italian, German, or English depending on `self.L`) prompting the user to save before navigating. If no unsaved changes exist, the method decrements `self.REC_CORR` by one; if already at the first record, it resets the counter and displays a localized warning, otherwise it clears the current fields, populates them with the previous record's data via `fill_fields()`, and updates the record counter display.

##### on_pushButton_next_rec_pressed(self)

Handles the "previous record" navigation button press event by first checking whether the current record has unsaved modifications; if so, it prompts the user with a localized confirmation dialog (Italian, German, or English) asking whether to save the changes before navigating. If no unsaved changes exist, it decrements `REC_CORR` by one to move to the previous record. If the resulting index is `-1`, it resets to `0` and displays a localized warning indicating the user is already at the first record; otherwise, it clears the current fields, populates them with the previous record's data, and updates the record counter display.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently removing the currently displayed record from the database via `self.DB_MANAGER.delete_one_record`. If the user confirms, the record identified by `self.ID_TABLE` at `self.REC_CORR` is deleted, the data list is reloaded, and the UI state is updated accordingly — resetting counters, clearing fields, and navigating to the first record if any remain. If the resulting data list is empty, all internal record lists and counters are reset to zero and the form fields are cleared.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "new search" button by first checking the current record state; if the check returns `1`, no action is taken. Otherwise, it disables the search button and, provided the current browse status is not already `"f"`, transitions the GUI into search mode by updating `BROWSE_STATUS`, refreshing the status label, clearing all fields, resetting the record counter and sort label, and enabling editability on the `comboBox_progetto`, `comboBox_nr_ut`, and `lineEdit_ut_letterale` controls.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the "search go" button press event by first verifying that the application is in search mode (`BROWSE_STATUS == "f"`); if not, it displays a localized warning message (Italian, German, or English) instructing the user to initiate a new search instead.

When in the correct browse status, the method collects values from all relevant form fields (combo boxes and line edits) into a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database using `DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no criteria were set or no records were found, or populates `DATA_LIST` with the returned records, updates the record counter, fills the form fields, sets `BROWSE_STATUS` to `"b"`, and displays a localized summary message indicating the number of records found, before re-enabling the search button via `enable_button_search(1)`.

##### update_if(self, msg)

Updates the current record conditionally based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()`, rebuilds `DATA_LIST` by querying and re-sorting the records using either the default ascending sort or the current sort configuration, and sets the browse status to `"b"`. The corrected record position (`REC_CORR`) is also resolved to an integer index, guarding against a string type.

##### update_record(self)

*No description available.*
Attempts to update the currently selected record in the database by calling `self.DB_MANAGER.update` with the current record's identifier, table fields, and values returned by `self.rec_toupdate()`. Before performing the update, it validates that `DATA_LIST` is non-empty and that `REC_CORR` is a valid index, displaying a localized warning dialog (Italian, German, or English based on `self.L`) and returning `0` if either check fails. If an exception occurs during the update, the error is appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory and a localized encoding-related warning is shown to the user; the method returns `1` on success and `0` on a failed safety check.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the current mapper table class and populates `self.DATA_LIST` with the results. The query is ordered by `self.ID_TABLE` in ascending order, using `self.DB_MANAGER.query_ordered` to replace a previously used double-query pattern for improved performance.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded and hyphen-separated). The formatted date string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each cell, it retrieves the item's text value if the item is non-null, appending it to a per-row sublist. Returns a list of sublists, where each sublist contains the string text values of the non-null cells in that row.

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to an empty state by clearing or removing their contents. Combo boxes are reset via `setEditText("")`, line edits and text edits are cleared using their respective `.clear()` methods, and all rows are removed from both the `tableWidget_documentazione` and `tableWidget_bibliografia` table widgets. This method is typically called to prepare the form for new data entry or to discard the currently displayed record.

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` in `DATA_LIST`, setting the internal record pointer `self.rec_num` to `n`. It assigns values to line edits, combo boxes, text edits, spin boxes, a checkbox, and table widgets for all core record fields, then conditionally populates extended survey fields (introduced in v4.9.21+) only when the corresponding attributes exist on the record object. If any exception occurs during the population process, a warning dialog is displayed; upon successful completion, `loadMediaPreview()` is called.

##### set_rec_counter(self, t, c)

Sets the record counter values by assigning the provided total and current record parameters to the instance fields `rec_tot` and `rec_corr`, respectively. It then updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects and serializes the current state of all form fields into `DATA_LIST_REC_TEMP`, a flat list of string values representing a temporary record snapshot. Field values are read from combo boxes, line edits, text edits, spin boxes, and table widgets (the latter two converted via `table2dict`); the `quota` field is set to `None` if its corresponding line edit is empty. Extended survey fields introduced in v4.9.21 (such as visibility percentage, GPS method, vegetation coverage, and others) are conditionally included using `hasattr` guards to maintain backward compatibility.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` with the field values of the currently selected record, identified by `REC_CORR`, from `DATA_LIST`. Before populating, the method resets `DATA_LIST_REC_CORR` to an empty list and returns early if `DATA_LIST` is empty or `REC_CORR` is out of bounds. Each field defined in `TABLE_FIELDS` is evaluated dynamically and appended as a string to `DATA_LIST_REC_CORR`.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### rec_toupdate(self)

*No description available.*
Determines which records require updating by delegating to `self.UTILITY.pos_none_in_list`, passing the current temporary record list `self.DATA_LIST_REC_TEMP` as input. Returns the result of that call, which represents the positions or records identified for update within the temporary data list.

##### records_equal_check(self)

*No description available.*
Compares the current temporary record list against the corrected record list to determine whether they are equal. It first populates both lists by calling `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`, then compares `DATA_LIST_REC_CORR` with `DATA_LIST_REC_TEMP`. Returns `0` if the two lists are equal, or `1` if they differ.

##### on_pushButton_pdf_exp_pressed(self)

Export individual UT sheets to PDF.

##### on_pushButton_pdf_list_pressed(self)

Export list of all UT records to PDF.

##### on_pushButton_gna_export_pressed(self)

Open GNA export dialog to export UT data to GNA GeoPackage format.

Creates a GeoPackage with:
- MOPR: Project perimeter
- MOSI: Archaeological sites/findings
- VRP: Archaeological potential map
- VRD: Archaeological risk map

##### generate_list_pdf(self)

Iterates over all records in `self.DATA_LIST` and converts each record's fields into a flat list of strings, assembling these per-record lists into a master list suitable for PDF generation. Each sub-list contains up to 57 fields covering project metadata, geographic coordinates, survey attributes, and analysis scores; optional fields introduced in later versions (v4.9.21+ and v4.9.67+) are included conditionally using `hasattr` checks, falling back to empty strings or `None` when absent. Returns the completed `data_list` of string-converted record rows.

##### testing(self, name_file, message)

Writes the given `message` to a file specified by `name_file`, overwriting any existing content. The file is opened in write mode, the message is converted to a string and written, then the file handle is closed.

##### loadMediaPreview(self)

Load media thumbnails for current record

##### dropEvent(self, event)

Handle file drop events for media

##### dragEnterEvent(self, event)

*No description available.*
Handles the drag-enter event by inspecting the MIME data of the incoming drag action. If the event's MIME data contains URLs, the proposed drop action is accepted; otherwise, the event is ignored. This method controls whether a drag operation is permitted to proceed over the widget based solely on the presence of URL data.

##### dragMoveEvent(self, event)

*No description available.*
Handles the drag move event that is triggered when a dragged object is moved within the widget's boundaries. Unconditionally accepts the proposed drop action by calling `event.acceptProposedAction()`, allowing the drag operation to continue without restriction.

##### load_and_process_image(self, path)

Process and add an image to the media database

##### insert_record_media(self, mediatype, filename, filetype, filepath)

Insert media record into database

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

Insert media thumbnail record into database

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

Link media to entity record

##### delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

Unlink media from entity record

##### on_pushButton_removetags_pressed(self)

Remove tags from selected media items

##### on_pushButton_search_images_pressed(self)

Open the Image Search dialog with pre-filled filters for current UT record.

##### generate_UT(self)

Generate UT entity data for media linking

##### assignTags_UT(self, item)

Assign media tags to UT entity

##### on_pushButton_calculate_analysis_pressed(self)

Calculate archaeological potential and risk for current UT record.

##### on_pushButton_generate_heatmap_pressed(self)

Generate heatmap for all UT records in current project.

##### on_pushButton_export_analysis_pdf_pressed(self)

Export analysis report as PDF.

## Functions

### load_thesaurus(tipologia_sigla, use_sigla)

Queries the `PYARCHINIT_THESAURUS_SIGLE` database table for thesaurus entries matching a given `tipologia_sigla` value, filtered by the current language (`lang`) and a fixed table name (`'ut_table'`). Returns a sorted list of unique string values drawn from either the `sigla` (abbreviation) or `sigla_estesa` (extended label) field of each matching record, depending on the `use_sigla` flag. Returns an empty list if the query raises an exception, such as when the thesaurus table does not exist.

**Parameters:**
- `tipologia_sigla`
- `use_sigla`

### get_ut_id()

*No description available.*
A nested helper function defined within `on_pushButton_removetags_pressed` that retrieves the database identifier for a UT (survey unit) record. It reads the current values of `comboBox_progetto` and `comboBox_nr_ut` to construct a search dictionary, then queries the database via `DB_MANAGER.query_bool` against the `'UT'` table. Returns the `id_ut` of the first matching record if found, or `None` if no match exists.

