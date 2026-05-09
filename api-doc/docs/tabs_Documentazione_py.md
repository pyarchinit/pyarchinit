# tabs/Documentazione.py

## Overview

This file contains 46 documented elements.

## Classes

### pyarchinit_Documentazione

*No description available.*
A QDialog subclass that provides the graphical user interface for managing archaeological documentation records within the PyArchInit QGIS plugin. It handles full CRUD operations against the `documentazione_table` database table, supporting record browsing, creation, modification, deletion, searching, and sorting for fields including site, document name, date, documentation type, source, scale, draughtsman, and notes. The dialog adapts its labels, status messages, and field mappings to the active QGIS locale, with explicit support for Italian, English, German, French, Spanish, Portuguese, Arabic, Catalan, Romanian, Greek, and several other languages, and includes PDF export functionality for both individual record sheets and indexed lists.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog by calling the parent constructor, setting up the QGIS interface reference, instantiating a `Pyarchinit_pyqgis` object, and building the UI via `setupUi`. Applies the current theme using `ThemeManager` and adds a theme toggle button to the form, then sets `currentLayerId` to `None` and attempts to establish a database connection via `on_pushButton_connect_pressed`, displaying a warning dialog if the connection raises an exception. Completes initialization by populating fields with `fill_fields`, and invoking `set_sito` and `msg_sito`.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary navigation and action buttons in the interface by passing the value `n` to each button's `setEnabled` method. The buttons affected include `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all listed controls to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously based on the value of `n`. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. Each button's `setEnabled` method is called with `n` as the argument, allowing all listed controls to be enabled or disabled in a single call.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` instance, determining whether the backend is SQLite, and initialising the database manager via `get_db_manager`. If the connection succeeds, it retrieves the database username, optionally sets it on the concurrency manager, loads records from the database, and updates the UI state (record counters, browse status, sort label, and field values) accordingly. If the database is empty, it displays a localised welcome message (Italian, German, or English) and initiates a new record; if the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar.

##### charge_list(self)

Populates several combo box widgets in the user interface with data retrieved from the database, localized according to the current QGIS user locale. It loads the site list from `site_table` into `comboBox_sito_doc`, documentation type values (combining hardcoded locale-specific labels with thesaurus entries for typology `9.1`) into `comboBox_tipo_doc`, and source values from thesaurus entries for typology `9.2` into `comboBox_sorgente_doc`. Errors encountered during the removal of empty entries from the site list are reported via a localized `QMessageBox` warning in Italian, English, or German depending on the active language setting.

##### msg_sito(self)

*No description available.*
Checks whether the currently selected site in `comboBox_sito_doc` matches the configured site retrieved from the `Connection` object. If a match is found, it displays a localised informational message (Italian, German, or English) confirming the active site connection. If no site has been configured (`sito_set_str` is empty), it prompts the user with a localised warning offering the option to open the configuration dialog (`pyArchInitDialog_Config`) to set one up, or cancel to proceed without a site filter.

##### set_sito(self)

*No description available.*
Retrieves the configured site (`sito`) setting via a `Connection` object and, if a non-empty site string is found, queries the database for all matching records using `DB_MANAGER.query_bool`. If records are found, the method populates `DATA_LIST`, initialises the record counters, fills the UI fields, sets the browse status, and disables the `comboBox_sito_doc` combo box; if no records are found, a localised informational message is displayed in Italian, German, or English depending on the value of `self.L`. Any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### generate_list_pdf(self)

*No description available.*
Iterates over all records in `self.DATA_LIST` and compiles a structured list of documentation data intended for PDF generation. For each record, it queries the database via `self.DB_MANAGER` to retrieve associated stratigraphic unit (US) and negative US references, then constructs a locale-aware, HTML-formatted string (supporting Italian, German, and a default fallback) that groups unit numbers by area. Returns a list of lists, where each inner list contains the site name, document name, date, documentation type, source, scale, draughtsman, notes, and the formatted area/unit string.

##### on_pushButton_disegno_doc_pressed(self)

*No description available.*
Handles the press event of the `pushButton_disegno_doc` button. Retrieves the current record from `DATA_LIST` using the `REC_CORR` index, wraps it in a single-element list, and passes it to `self.pyQGIS.charge_vector_layers_doc` to load the corresponding vector layers for the current documentation record.

##### on_pushButton_exp_scheda_doc_pressed(self)

Handles the press event of the export sheet button by generating a PDF documentation sheet for the current record set. It instantiates a `generate_documentazione_pdf` object and retrieves the data via `self.generate_list_pdf()`, then delegates PDF construction to a language-specific build method based on `self.L`: `build_Documentazione_sheets` for Italian (`'it'`), `build_Documentazione_sheets_de` for German (`'de'`), or `build_Documentazione_sheets_en` for all other language values.

##### on_pushButton_exp_elenco_doc_pressed(self)

*No description available.*
Handles the press event of the export index button by generating a documentation index PDF based on the current language setting (`self.L`). It instantiates a `generate_documentazione_pdf` object, retrieves the data list via `self.generate_list_pdf()`, and dispatches to the appropriate locale-specific build method: `build_index_Documentazione` for Italian (`'it'`), `build_index_Documentazione_de` for German (`'de'`), or `build_index_Documentazione_en` for all other languages. In all cases, the first element of the first record (`data_list[0][0]`) is passed as a secondary argument to the build method alongside the full data list.

##### on_pushButtonPreview_pressed(self)

Constructs a SQL-style filter string using the `sito`, `nome_doc`, and `tipo_documentazione` fields of the currently selected record (`DATA_LIST[REC_CORR]`). Displays the resulting query string in a warning `QMessageBox` for inspection, then opens a `pyarchinit_doc_preview` dialog initialized with that filter string. The dialog is executed modally via `dlg.exec()`.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available sort items, then applying the user-selected fields and order type to the current data list. If the record state check passes, the method aborts; otherwise, it converts the selected sort items using `CONVERSION_DICT`, queries the database via `query_sort`, and rebuilds `DATA_LIST` with the sorted results. After sorting, it resets the browse status, record counters, and UI labels, then refreshes the displayed fields to reflect the newly ordered data.

##### on_pushButton_new_rec_pressed(self)

Handles the "New Record" button press event by first checking whether the current record has unsaved modifications and prompting the user to save them via a localized warning dialog (Italian, German, or English depending on `self.L`). If a site filter is active and matches the configured site setting (`sito_set_str`), it transitions the form to new-record mode (`"n"`) while preserving the site field and clearing only the remaining fields via `empty_fields_nosite()`; otherwise, it clears all fields via `empty_fields()` and enables the site combo box for editing. In both cases, the browse status label, sort label, and record counter are updated accordingly, and the UI buttons are reconfigured for new-record entry mode.

##### on_pushButton_save_pressed(self)

Handles the save button press event, branching logic based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it performs a concurrency version conflict check against `documentazione_table` before validating data and prompting the user with a localised confirmation dialog (Italian, German, or English) to confirm saving modifications to an existing record. In insert mode, it validates data, inserts a new record, resets and refreshes the form fields and UI controls, updates record counters, and transitions the interface back to browse mode upon successful insertion.

##### data_error_check(self)

*No description available.*
Validates that the required form fields — site (`comboBox_sito_doc`), documentation type (`comboBox_tipo_doc`), and documentation name (`lineEdit_nome_doc`) — are not empty before a record is submitted. For each empty field detected via `Error_check.data_is_empty()`, a localized warning dialog is displayed using `QMessageBox.warning()`, with message text determined by the current language setting (`self.L`), supporting Italian (`'it'`), German (`'de'`), and a default English fallback. Returns `0` if all fields pass validation, or `1` if one or more validation errors are found.

##### insert_new_rec(self)

Attempts to insert a new documentation record into the database by collecting field values from the UI controls (site, name, date, type, source, scale, draughtsman, and notes) and assigning the next available ID via `DB_MANAGER.max_num_id`. It then commits the record to the current session using `DB_MANAGER.insert_data_session`, returning `1` on success. If an `IntegrityError` is detected, a localized warning message is displayed (Italian, German, or English depending on `self.L`) indicating a duplicate record, and `0` is returned; any other exception also triggers a warning dialog and returns `0`.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If no entry errors are found but the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the changes, and delegates the response to `update_if()`. Returns `1` if data entry errors are present, or `0` if no entry errors were detected.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button by loading and displaying the complete set of records. If no unsaved record state is detected (i.e., `check_record_state()` does not return `1`), the method clears the current fields, reloads all records via `charge_records()`, and repopulates the fields with the first record in the list. It then sets the browse status to `"b"`, updates the record counter and status labels accordingly, and resets the sort label to the unsorted state.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data list. If the record state check does not return `1`, it clears the existing field values, resets the record counters so that `REC_CORR` is set to `0` and `REC_TOT` reflects the total number of entries in `DATA_LIST`, then populates the fields with the first record (index `0`) and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It first checks the current record state via `check_record_state()` and aborts navigation if the return value is `1`; otherwise, it clears the current form fields with `empty_fields()`, populates them with the last record's data via `fill_fields()`, and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user as a warning dialog via `QMessageBox`.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one. If the decremented index reaches `-1`, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) to inform the user that the first record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; if the record state check returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles navigation to the next record in the dataset when the corresponding button is pressed. If the current record state passes validation, it increments `REC_CORR` by one and checks whether the new index exceeds the total record count (`REC_TOT`); if so, it reverts the increment and displays a localized warning message (Italian, German, or English) indicating that the last record has been reached. Otherwise, it clears the current fields, populates them with the data for the new record, and updates the record counter display.

##### on_pushButton_delete_pressed(self)

Handles the delete button press event by displaying a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. Upon confirmed deletion, the method reloads the record list from the database and, if records remain, resets navigation to the first record, updates the browse status, record counter, and UI fields; if the data list is empty after deletion, all record lists and counters are reset and the form fields are cleared. Any exception raised during the delete operation is reported to the user via a warning dialog.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "new search" button by transitioning the form into search mode (`BROWSE_STATUS = "f"`), provided no unsaved record state is detected. Depending on whether a site (`sito`) is already set via the connection configuration and matches the current combo box value, it selectively enables or disables specific input fields (`comboBox_sito_doc`, `lineEdit_nome_doc`, `comboBox_tipo_doc`, `textEdit_note_doc`) and clears the relevant form fields accordingly. In both cases, the status label, record counter, and sort label are reset to reflect the new search state.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search execution triggered by the search button. If the current browse status is not `"f"` (search mode), a localized warning message is displayed instructing the user to initiate a new search first. Otherwise, a search dictionary is built from the current values of the site, document name, date, document type, source, scale, and draughtsman fields; empty entries are removed via `Utility.remove_empty_items_fr_dict`, and the resulting query is executed against the database through `DB_MANAGER.query_bool` — displaying a localized warning if no criteria were set or no records were found, or populating `DATA_LIST` and updating the UI status, record counter, and field states upon a successful result.

##### on_pushButton_test_pressed(self)

*No description available.*
This method serves as an event handler triggered when the test push button is pressed. In its current state, the method body contains only a `pass` statement, meaning it performs no operations and returns `None`. The implementation details are not documented in source.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a message box dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, it calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Returns `1` if the update and refresh succeed, `0` if `update_record()` fails, and implicitly `None` if the user did not confirm.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the mapped table class, ordered by the table's ID column in ascending order. The results are stored directly in the instance attribute `self.DATA_LIST`, replacing any previously held data. This method uses a single ordered query via `self.DB_MANAGER.query_ordered` as a performance optimisation over a double-query pattern.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded and hyphen-separated). The formatted date string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table widget name `n` as a string, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table. For each cell, it retrieves the item's text value and appends it to a per-row sublist, skipping empty or null cells. Returns a list of sublists, where each sublist represents the non-empty text values found in a single row of the table.

##### empty_fields_nosite(self)

Clears and resets all documentation form fields except the site field (`comboBox_sito_doc`). Specifically, it clears the Nome Documentazione, Data, Disegnatore, and Note fields, and resets the Tipo Documentazione, Sorgente, and Scala combo boxes to empty strings.

##### empty_fields(self)

Resets all input fields in the documentation form to their default empty state. It clears the combo boxes for site (`comboBox_sito_doc`), documentation type (`comboBox_tipo_doc`), source (`comboBox_sorgente_doc`), and scale (`comboBox_scala_doc`) by setting their edit text to an empty string, and clears the line edits for name (`lineEdit_nome_doc`), date (`lineEdit_data_doc`), and draughtsman (`lineEdit_disegnatore_doc`), as well as the notes text area (`textEdit_note_doc`). This method covers all eight documented form fields, corresponding to: site, documentation name, date, documentation type, source, scale, draughtsman, and notes.

##### fill_fields(self, n)

Populates the form fields with data from the record at index `n` in `DATA_LIST`, setting values for site, document name, date, documentation type, source, scale, draughtsman, and notes across the corresponding UI widgets. Any exceptions raised during field population are silently suppressed. If a `concurrency_manager` is present, the method additionally tracks the record's `version_number` and `id_documentazione`, updates the lock indicator based on the record's `editing_by` and `editing_since` attributes, and logs any errors encountered during version tracking via `QgsMessageLog`.

##### set_rec_counter(self, t, c)

Sets the total and current record counters for the UI, updating both the internal state and the corresponding display labels.

Accepts two parameters, `t` (total records) and `c` (current record), assigning them to `self.rec_tot` and `self.rec_corr` respectively. The method then reflects these values in the UI by updating `label_rec_tot` and `label_rec_corrente` with their string representations.

##### set_LIST_REC_TEMP(self)

*No description available.*
Populates `DATA_LIST_REC_TEMP` with the current values from the form's input widgets, capturing a temporary snapshot of the record being edited. The list contains eight fields in order: site (`comboBox_sito_doc`), documentation name (`lineEdit_nome_doc`), date (`lineEdit_data_doc`), documentation type (`comboBox_tipo_doc`), source (`comboBox_sorgente_doc`), scale (`comboBox_scala_doc`), draughtsman (`lineEdit_disegnatore_doc`), and notes (`textEdit_note_doc`).

##### set_LIST_REC_CORR(self)

Populates `DATA_LIST_REC_CORR` by iterating over `TABLE_FIELDS` and retrieving the corresponding attribute values from the current record in `DATA_LIST`, identified by the `REC_CORR` index. Each retrieved attribute value is converted to a string and appended to the `DATA_LIST_REC_CORR` list, which is reset to an empty list at the start of each call.

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
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update data returned by `rec_toupdate()`. Returns `1` on success or `0` on failure.

If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default), advising that an encoding problem was encountered and that error data can be retrieved from the report folder.

##### testing(self, name_file, message)

Writes the given `message` to a file specified by `name_file`, opening it in write mode, writing the string representation of the message, and then closing the file. This method is used to create a copy of error data, such as encoding-related failures, that can be retrieved from the report folder.

##### check_for_updates(self)

Check if current record has been modified by others

