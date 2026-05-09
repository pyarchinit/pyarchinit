# tabs/Inv_Lapidei.py

## Overview

This file contains 50 documented elements.

## Classes

### pyarchinit_Inventario_Lapidei

`pyarchinit_Inventario_Lapidei` is a QDialog subclass that implements the stone finds inventory form (`inventario_lapidei_table`) within the PyArchInit QGIS plugin. It provides a full record management interface — including create, read, update, delete, search, and sort operations — for stone architectural elements, capturing fields such as site, form number, object type, typology, material, dimensional measurements (bed dimensions, torus, thickness, width, length, height), description, processing and conservation state, comparisons, chronology, bibliography, and compiler. The dialog adapts its labels, status messages, and field mappings to the active QGIS locale, with explicit support for Italian, English, German, French, Spanish, Portuguese, Romanian, Arabic, Catalan, Greek, and other languages.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the dialog by calling the parent constructor, storing the provided `iface` reference, and setting up the UI via `setupUi`. Applies the current theme using `ThemeManager` and adds a theme toggle button to the form, then attempts to establish a database connection via `on_pushButton_connect_pressed`, catching any exceptions and displaying them in a warning dialog. Completes initialization by populating fields, setting the site, displaying a site message, and invoking `init_remote_loader`.

##### plot_chart(self, d, t, yl)

*No description available.*
Renders a vertical bar chart on the embedded canvas widget using the provided data, title, and y-axis label. The method converts the input list `d` of key-value pairs into a dictionary, then draws bars whose heights represent the corresponding values, clearing any previously rendered chart beforehand. Each bar is annotated with a rotated text label combining the category name and its integer value, positioned at the base of the bar.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` object and determining whether the backend is SQLite. If the connection succeeds and records exist, it initialises browsing state variables, updates status labels, and populates the UI fields; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`) and triggers new record creation. If the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar, distinguishing between a missing table error and a general bug condition.

##### customize_gui(self)

*No description available.*
Initializes and configures a `QListWidget` (`iconListWidget`) for media preview display, setting its visual properties such as frame style, icon size (150×150), grid size (160×160), icon view mode, batch size, and multi-selection mode. The widget is connected to the `openWide_image` slot on double-click and added as a "Media" tab to the existing `tabWidget`. After construction, the method populates the list widget by querying media thumbnail records associated with the current data record when `mode` is `0`, or clears the widget when `mode` is `1`.

##### openWide_image(self)

*No description available.*
Opens a full-size image viewer for each selected item in `iconListWidget`. For each selected item, it retrieves the original filename from the item's text, queries the database via `DB_MANAGER` using the media ID to obtain the corresponding file path, and displays the image in an `ImageViewer` dialog. If the database query fails, a warning message box is shown with the error details.

##### charge_list(self)

Populates multiple combo boxes in the user interface with data retrieved from the database. It loads the site list from `site_table` via a `group_by` query, removing any empty entries and sorting the results before adding them to `comboBox_sito`, with localized error messages displayed in Italian, English, or German if the removal fails. It then queries the `PYARCHINIT_THESAURUS_SIGLE` thesaurus table for the current user locale to populate `comboBox_tipologia`, `comboBox_materiale`, and `comboBox_oggetto` using entries corresponding to `inventario_lapidei_table` with type codes `5.1`, `5.2`, and `5.3` respectively.

##### msg_sito(self)

*No description available.*
Checks the currently selected site in `comboBox_sito` against the configured site retrieved from the `Connection` object. If the values match, it displays a localised informational message (Italian, German, or English) confirming the active site connection. If no site has been configured (`sito_set_str` is empty), it displays a localised warning message offering the user the option to open the configuration dialog (`pyArchInitDialog_Config`) to set one up, or to cancel and proceed without a site filter.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` object and, if a site value is present, queries the database for all records matching that site, populating `DATA_LIST` and updating the UI fields, browse status, record counter, and disabling the site combo box. If no matching records are found for the configured site, a localized warning message is displayed in Italian, German, or English depending on the value of `self.L`, informing the user that the site does not exist in the current tab. If the site setting string is empty or falsy, the method takes no action.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available sort items, allowing the user to select sort fields and order type. If the record state check passes, the method aborts; otherwise, it converts the selected items using `CONVERSION_DICT`, queries the database via `DB_MANAGER.query_sort()` using the current record ID list, and replaces `DATA_LIST` with the sorted results. After sorting, it resets the browse and sort status labels, updates the record counter, clears the current fields, and repopulates them with the first record of the sorted dataset.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record has unsaved modifications; if so, it prompts the user with a localized warning dialog (Italian, German, or English) asking whether to save the changes before proceeding. Once any pending save is resolved, the method transitions the browse status to `"n"` (new) and clears the form fields, configuring the site combo box and inventory number field enable/editable states based on whether the current site matches the configured site setting retrieved from `Connection`. Finally, it updates the status label, sort label, and record counter to reflect the new-record state, and disables relevant UI buttons via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behavior based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it validates the data via `data_error_check()` and, if the record has been modified (as determined by `records_equal_check()`), prompts the user with a localized confirmation dialog (Italian, German, or English) before calling `update_if()` to persist the changes; if no modifications are detected, a localized warning is displayed instead. In insert mode, it validates the data, attempts to insert a new record via `insert_new_rec()`, and on success resets the form state, reloads records and lists, updates navigation counters, and re-enables relevant UI controls.

##### generate_list_pdf(self)

Iterates over all records in `self.DATA_LIST` and constructs a list of lists, where each inner list contains 20 string (or integer) fields extracted from a single `DATA_LIST` entry, including `id_invlap`, `sito`, `scheda_numero`, `collocazione`, `oggetto`, `tipologia`, `materiale`, dimensional measurements, `descrizione`, `lavorazione_e_stato_di_conservazione`, `confronti`, `cronologia`, `bibliografia`, and `compilatore`. The field at index 2 (`scheda_numero`) is cast to `int` while all remaining fields are cast to `str`. Returns the fully populated `data_list` for use in PDF generation, as seen in `on_pushButton_exp_pdf_sheet_pressed`.

##### on_pushButton_exp_pdf_sheet_pressed(self)

Handles the press event of the PDF export button by generating a PDF sheet for the current data list based on the active language setting (`self.L`). It instantiates a `generate_reperti_pdf` object and calls `generate_list_pdf()` to retrieve the data, then dispatches to the appropriate build method: `build_Invlap_sheets` for Italian (`'it'`), `build_Invlap_sheets_de` for German (`'de'`), or `build_Invlap_sheets_en` for all other languages.

##### data_error_check(self)

*No description available.*
Validates required form fields before a record is saved by checking that the context/provenance combo box (`comboBox_sito`) and inventory number field (`lineEdit_num_inv`) are not empty, and that the inventory number, if provided, contains a numeric value. Validation messages are displayed via `QMessageBox.warning` in the appropriate language based on `self.L` (`'it'` for Italian, `'de'` for German, or English as the default). Returns `0` if all checks pass, or `1` if any validation error is detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates form field values for a new *Lapidei* (stone artifact) record, converting numeric fields (`d_letto_posa`, `d_letto_attesa`, `toro`, `spessore`, `larghezza`, `lunghezza`, `h`) to `float` or `None` if empty, then passes all gathered data — including site, inventory number, object type, material, descriptions, chronology, bibliography, and compiler — to `DB_MANAGER.insert_values_Lapidei` for record construction. The resulting record is then committed to the database session via `DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` on failure, displaying a localized warning dialog (`QMessageBox`) for integrity constraint violations (duplicate record) or other exceptions.

##### on_pushButton_insert_row_bibliografia_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button for the bibliography section is pressed. It delegates to `insert_new_row`, passing `'self.tableWidget_bibliografia'` as the target table widget identifier. This results in a new row being added to the bibliography table widget.

##### on_pushButton_remove_row_bibliografia_pressed(self)

*No description available.*
Slot method triggered when the "remove row" button for the bibliography section is pressed. It delegates execution to `self.remove_row()`, passing `'self.tableWidget_bibliografia'` as the target widget identifier to remove a row from the bibliography table. This method serves as the event handler counterpart to `on_pushButton_insert_row_bibliografia_pressed`.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If a data error is detected, the method returns `1` immediately; if no data errors exist but the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompting the user to save changes, delegating the response to `update_if()`. Returns `0` after handling the modification prompt when no data entry errors are present.

##### on_pushButton_view_all_2_pressed(self)

*No description available.*
Handles the press event of the "View All" button by first checking the current record state; if no unsaved changes are detected, it clears the current fields, reloads all records, and repopulates the fields with the first record in the dataset. The browse status is set to `"b"` and the corresponding status label is updated accordingly. The record counter and internal tracking variables (`REC_TOT`, `REC_CORR`, `DATA_LIST_REC_TEMP`, `DATA_LIST_REC_CORR`) are reset to reflect the full dataset starting from the first record, and the sort label is updated to reflect an unsorted state.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the dataset. If the record state check returns `1`, it loads a media preview by calling `self.loadMediaPreview(1)`; otherwise, it clears the current fields, sets `REC_CORR` to `0` and `REC_TOT` to the total number of records in `DATA_LIST`, populates the fields with the first record via `self.fill_fields(0)`, and updates the record counter accordingly. Any exception raised during this process is caught and displayed to the user as a warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Handles the press event of the "last record" navigation button. If `check_record_state()` returns `1`, it invokes `loadMediaPreview(0)`; otherwise, it clears the current fields via `empty_fields()`, sets `REC_CORR` to the index of the last entry in `DATA_LIST`, and updates both the displayed fields and the record counter to reflect the final record. Any exception raised during this process is caught and displayed to the user as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles navigation to the previous record when the corresponding button is pressed. If the current record state check passes, it decrements `REC_CORR` by one; if the resulting index is `-1`, it resets `REC_CORR` to `0` and displays a localized warning message (Italian, German, or English) indicating that the user is already at the first record. Otherwise, it clears the current fields, populates them with the data for the previous record, and updates the record counter display.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one, provided the record state check does not return `1`. If the incremented index reaches or exceeds the total record count (`REC_TOT`), the index is reverted and a localized warning message is displayed (Italian, German, or default English) indicating the user is already at the last record. Otherwise, the form fields are cleared via `empty_fields()`, repopulated for the new record via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; any exception raised during this process is caught and shown as an error dialog.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by prompting the user with a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed and succeeds, the record list is reloaded; if the database becomes empty, all data lists and counters are reset and fields are cleared, otherwise the UI is updated to display the first record in browse mode with refreshed counters, lists, and fields. Any exception raised during deletion is reported to the user via a warning dialog.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by resetting the UI to search mode (`BROWSE_STATUS = "f"`). If the current record state allows it, the method disables the search button, evaluates the active site (`comboBox_sito`) against a configured site set, and conditionally toggles the editability and enabled state of the site combo box accordingly. Depending on the outcome, it resets the status label, record counter, sort label, and clears the input fields — either preserving the site field value (`empty_fields_nosite`) or fully clearing all fields (`empty_fields`) after reloading the site list.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search button press event by first verifying that the application is in search mode (`BROWSE_STATUS == "f"`); if not, a localized warning message is displayed instructing the user to initiate a new search. When in the correct state, it collects and converts field values from the form's input controls into a search dictionary, removes empty entries using `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database via `DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no criteria were set, notifies that no records were found, or populates `DATA_LIST` with the returned records, updates the record counter, fills the form fields, transitions `BROWSE_STATUS` to `"b"`, and enables search-related buttons.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a confirmation dialog. If `msg` matches `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Returns `1` if the update succeeds, `0` if it fails, or `None` if the confirmation was not accepted.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `rec_toupdate()`. Returns `1` on success, or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default).

##### rec_toupdate(self)

*No description available.*
Returns a processed version of the temporary record list (`DATA_LIST_REC_TEMP`) after passing it through the `UTILITY.pos_none_in_list` method. The result, stored in `rec_to_update`, represents the list with `None` values handled according to the logic defined in `pos_none_in_list`. The processed list is then returned to the caller.

##### charge_records(self)

Loads all records from the database into the `DATA_LIST` attribute by executing a single ordered query against the mapped table class. The query retrieves records sorted by `ID_TABLE` in ascending order using `DB_MANAGER.query_ordered`, replacing a previously used double-query pattern for improved performance.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets - uses getattr instead of eval for security

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it as a `"%d-%m-%Y"` string (day-month-year, zero-padded). The formatted date string is then returned to the caller.

##### table2dict(self, n)

Convert table widget data to list - uses getattr instead of eval for security

##### tableInsertData(self, t, d)

Set the value into alls Grid - uses getattr and ast.literal_eval instead of eval

##### insert_new_row(self, table_name)

insert new row into a table based on table_name - uses getattr instead of eval

##### remove_row(self, table_name)

Remove selected row from table - uses getattr instead of eval

##### empty_fields_nosite(self)

Clears and resets all input fields in the form except for the site (`comboBox_sito`) field, which is intentionally left unchanged. The method clears text inputs, combo boxes, and text edit widgets corresponding to inventory number, placement, object, typology, material, various measurements, description, workmanship/conservation state, comparisons, chronology, and compiler fields. It also removes all existing rows from `tableWidget_bibliografia` and inserts a single new empty row in its place.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to their default empty state. This includes clearing combo boxes (sito, oggetto, tipologia, materiale), line edits (num\_inv, collocazione, d\_letto\_posa, d\_letto\_attesa, toro, spessore, larghezza, lunghezza, h, cronologia, compilatore), and text edits (descrizione, lavorazione\_e\_stato\_di\_conservazione, confronti). All existing rows in `tableWidget_bibliografia` are removed and replaced with a single new empty row via `insert_new_row`.

##### fill_fields(self, n)

*No description available.*
Populates all form fields and widgets with data from the record at index `n` in `self.DATA_LIST`, storing the index in `self.rec_num`. Combo boxes, line edits, and text edits are updated with string fields such as `sito`, `tipologia`, `materiale`, `oggetto`, `descrizione`, `lavorazione_e_stato_di_conservazione`, `collocazione`, `compilatore`, `confronti`, and `cronologia`, while numeric fields (`d_letto_posa`, `d_letto_attesa`, `toro`, `spessore`, `larghezza`, `lunghezza`, `h`) are set to an empty string when their value is `None`. The `tableWidget_bibliografia` table is populated via `tableInsertData`, and any exception raised during the operation is silently suppressed.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counters for the UI. Assigns the provided values `t` and `c` to the instance attributes `rec_tot` and `rec_corr` respectively, then updates the corresponding labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

Collects and assembles the current state of all form fields into a temporary record list stored in `self.DATA_LIST_REC_TEMP`. It reads values from combo boxes, line edits, and text edits, converting dimensional fields (`d_letto_posa`, `d_letto_attesa`, `toro`, `spessore`, `larghezza`, `lunghezza`, `h`) to `None` if their corresponding `lineEdit` fields are empty. Bibliography data is retrieved via `self.table2dict("self.tableWidget_bibliografia")` and included as the final structured entry in the resulting list.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons by passing `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all_2`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all listed controls to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

Sets the enabled state of multiple UI buttons by passing the boolean value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all_2`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to collectively enable or disable navigation, record management, and sorting controls.

##### setTableEnable(self, t, v)

Set enabled state for table widgets - uses getattr instead of eval

##### set_LIST_REC_CORR(self)

Build list of current record values - uses getattr instead of eval

##### records_equal_check(self)

*No description available.*
Compares the current record state against the corresponding saved record by invoking `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate `DATA_LIST_REC_TEMP` and `DATA_LIST_REC_CORR` respectively. Returns `0` if the two lists are equal, or `1` if they differ.

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode (`'w'`) and writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are explicitly cast to `str` before use. This method does not return a value.

