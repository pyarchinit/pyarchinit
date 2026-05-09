# tabs/Campioni.py

## Overview

This file contains 45 documented elements.

## Classes

### pyarchinit_Campioni

*No description available.*
A QDialog subclass that implements the Samples (Campioni) data entry and management form within the PyArchInit QGIS plugin. It provides a full record browsing, searching, inserting, updating, and deleting interface for the `campioni_table` database table, which stores archaeological sample records including site, sample number, sample type, description, area, stratigraphic unit, material inventory number, box number, and storage location. The class supports multiple interface languages (Italian, German, English, Spanish, French, Arabic, Catalan, Romanian, Portuguese, and Greek) and includes PDF export functionality for sample index sheets, box lists, and box labels.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog by calling the parent constructor, storing the provided QGIS interface reference, and instantiating a `Pyarchinit_pyqgis` object. Sets up the UI, applies the current theme via `ThemeManager`, and adds a theme toggle button to the form. Attempts to establish a database connection via `on_pushButton_connect_pressed`, catching any exceptions as a warning dialog, then populates fields and initializes site-related state by calling `fill_fields`, `set_sito`, and `msg_sito`.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary navigation and action buttons in the interface to the value specified by `n`. The affected buttons include `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. The parameter `n` is passed directly to each button's `setEnabled()` method, enabling or disabling all buttons simultaneously.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This allows all listed controls to be collectively enabled or disabled with a single call.

##### on_pushButton_connect_pressed(self)

Handles the press event of the connect button by establishing a database connection using a `Connection` object and initialising the database manager via `get_db_manager`. If the connection succeeds and records are present, it loads and displays the first record in browse mode; if the database is empty, it displays a localised welcome message (Italian, German, or English) and transitions to new-record mode. If the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar, distinguishing between a missing-table error and a general bug condition.

##### charge_list(self)

*No description available.*
Populates the UI combo boxes with data retrieved from the database, scoped to the current user locale. It queries the `site_table` to build a sorted list of site names loaded into `comboBox_sito`, removing any empty entries and displaying a localised warning message (Italian, German, or English) if an unexpected error occurs. It then queries the `PYARCHINIT_THESAURUS_SIGLE` thesaurus table for sample type entries matching the `campioni_table` typology code `4.1` in the detected language, and populates `comboBox_tipo_campione` with the resulting sorted values.

##### msg_sito(self)

Displays a localized informational message indicating the current site connection status by comparing the value in `comboBox_sito` against the configured site retrieved via `Connection().sito_set()`. If the current combo box text matches the configured site, a confirmation message is shown in Italian, German, or English depending on `self.L`. If no site has been configured (`sito_set_str` is empty), the method prompts the user to set one via a localized warning dialog, and if the user confirms, opens the `pyArchInitDialog_Config` dialog to configure a site.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` instance and, if a site value is present, queries the database for all records matching that site using `query_bool`. If matching records are found, the method populates `DATA_LIST`, initialises the browse state, fills the form fields, updates the record counter, and disables the site combo box; if no records are found, it displays a localised informational message (Italian, German, or English) and returns without updating the UI. Any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### on_pushButton_pdf_pressed(self)

*No description available.*
Event handler triggered when the PDF push button is pressed. The method currently contains no implementation and performs no operations (`pass`). Functionality for this button has not yet been implemented in the provided source.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the current `SORT_ITEMS`, allowing the user to select sort fields and order type. If the record state check does not return `1`, it converts the selected items using `CONVERSION_DICT`, executes a database sort query via `DB_MANAGER.query_sort()` using the IDs from the current `DATA_LIST`, and replaces `DATA_LIST` with the sorted results. After sorting, it resets the browse and sort status indicators, updates the record counter, clears the current fields, and repopulates them with data from the first record in the sorted list.

##### on_pushButton_new_rec_pressed(self)

Handles the "New Record" button press event by first checking for unsaved modifications to the current record and prompting the user to save changes via a localized warning dialog (Italian, German, or English) if the record has been altered. Sets the browse status to `"n"` (new) and resets the UI accordingly by clearing fields (excluding the site), updating status and sort labels, and resetting the record counter. Depending on whether the current site combo box value matches the configured site setting, the method either locks the site combo box and enables only the sample number field, or makes both fields fully editable.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behavior based on the current browse status (`self.BROWSE_STATUS`). In browse mode (`"b"`), it performs a data validation check and, if the record has been modified, prompts the user with a localized confirmation dialog (Italian, German, or English) before calling `update_if` to persist the changes; if no modifications are detected, a localized warning is displayed instead. Outside browse mode, it validates the data and attempts to insert a new record via `insert_new_rec`, then reloads and refreshes the UI state upon success, or displays a localized error message on failure.

##### data_error_check(self)

*No description available.*
Validates required form fields by checking that the site (`comboBox_sito`) and sample number (`lineEdit_nr_campione`) fields are not empty, and that the sample number value is numeric when provided. Validation messages are displayed via `QMessageBox.warning` in the appropriate language based on `self.L` (`'it'` for Italian, `'de'` for German, or English as the default). Returns `0` if all checks pass, or `1` if any validation error is detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates field values from the UI form, converting empty inputs to `None` and non-empty inputs to their appropriate types (`int` or `str`), then constructs a new campioni record by calling `self.DB_MANAGER.insert_campioni_values()` with the next available ID and all gathered field values.

Attempts to persist the new record to the database via `self.DB_MANAGER.insert_data_session()`; returns `1` on success. On failure, displays a localized warning dialog (Italian, German, or English) depending on `self.L`, distinguishing between integrity constraint violations and other errors, and returns `0` in all failure cases.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If a data error is detected, the method returns `1` immediately; if no data error exists but the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog (Italian, German, or English depending on `self.L`) asking whether to save the changes, then calls `update_if()` with the user's response and returns `0`. Returns `0` when no errors are present, or `1` when data entry errors are found.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button by loading and displaying all available records. If `check_record_state()` returns `1`, no action is taken; otherwise, the method clears the current fields, reloads all records via `charge_records()`, and repopulates the fields with `fill_fields()`. It then sets the browse status to `"b"`, updates the record counter and status labels, resets the current record position to the first entry in `DATA_LIST`, and clears any active sort indicator.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data list. If the record state check does not return `1`, it clears the existing field values, resets the record counters so that `REC_CORR` is set to `0` and `REC_TOT` reflects the total number of items in `DATA_LIST`, then populates the fields with the first entry (index `0`) and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It first checks the current record state via `check_record_state()` and aborts navigation if the return value is `1`; otherwise, it clears the current form fields with `empty_fields()`, populates them with the last record's data via `fill_fields()`, and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one. If the index reaches `-1`, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) to inform the user that the first record has already been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`. If the record state check (`check_record_state()`) returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a localized warning message indicating the user is already at the last record (supporting Italian, German, and a default English message). Otherwise, it clears the current form fields, populates them with the next record's data, and updates the record counter display.

##### on_pushButton_delete_pressed(self)

Handles the delete button press event by prompting the user with a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. Upon confirmed deletion, the method reloads the record list and, if records remain, resets navigation to the first record and refreshes the UI fields and counters; if the database is empty after deletion, all data lists and counters are cleared and the form fields are emptied. Any exception raised during deletion is reported to the user via a warning dialog.

##### on_pushButton_new_search_pressed(self)

Handles the "New Search" button press event by transitioning the interface to search mode (`BROWSE_STATUS = "f"`) when no unsaved record changes are detected. Depending on whether the current site (`comboBox_sito`) matches a preconfigured site setting retrieved from the database connection, it selectively enables or disables relevant input fields (`comboBox_sito`, `lineEdit_nr_campione`, `textEdit_descrizione_camp`) and either clears site-dependent fields only or performs a full field reset along with reloading the site list. The sort label is reset to its default unsorted state and the record counter is cleared in both cases.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search execution triggered by the search button. If the form is not in search mode (`BROWSE_STATUS != "f"`), a localized warning message is displayed instructing the user to initiate a new search first. Otherwise, it collects field values from the UI controls (`lineEdit_nr_campione`, `lineEdit_us`, `lineEdit_cassa`, `lineEdit_n_inv_mat`, `comboBox_sito`, `comboBox_tipo_campione`, `lineEdit_area`, `lineEdit_luogo_conservazione`), builds a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database through `DB_MANAGER.query_bool`; the results are loaded into `DATA_LIST`, the display fields are populated, the browse status is set to `"b"`, and a localized summary message reporting the number of records found is shown, with a warning displayed if no criteria were set or no records were returned. The search button is re-enabled via `enable_button_search(1)` upon completion regardless of outcome.

##### on_pushButton_test_pressed(self)

*No description available.*
This method serves as the event handler for the test push button's pressed signal. The method body contains only a `pass` statement, indicating that no logic is currently implemented. Its behavior and intended functionality are not documented in source.

##### on_pushButton_index_pdf_pressed(self)

Handles the press event of the "index PDF" button by generating locale-specific PDF index documents for sample records (*campioni*) and storage box records (*casse*). The active language (`self.L`) determines which build methods are invoked: Italian (`'it'`), German (`'de'`), or English (default), each producing a samples index, a box index, and box label documents. The site value is read from `self.comboBox_sito` and used as a parameter when generating the box-level PDF data and documents.

##### on_pushButton_exp_champ_sheet_pdf_pressed(self)

*No description available.*
Handles the press event of the "export sample sheet PDF" button by generating a PDF report of sample (campioni) data in a language-dependent format. It instantiates a `generate_campioni_pdf` object and calls `generate_list_pdf` to retrieve the data list, then delegates PDF construction to `build_Champ_sheets` for Italian (`'it'`), `build_Champ_sheets_de` for German (`'de'`), or `build_Champ_sheets_en` for all other language settings. The target language is determined by the instance attribute `self.L`.

##### generate_el_casse_pdf(self, sito)

Generates the data required to produce a PDF inventory list of sample storage boxes (*casse*) for a given archaeological site. For each distinct box number found in the `CAMPIONI` table, the method collects the box identifier, the associated sample numbers and types, the stratigraphic units (area/US) with any structural references formatted according to the active language (`it`, `de`, or a default), and the conservation location. Returns a list of per-box data sublists (`data_for_pdf`) ready for PDF rendering.

##### generate_list_pdf(self)

*No description available.*
Iterates over `self.DATA_LIST` and compiles a list of records formatted for PDF generation. For each record, fields that evaluate to `'None'` — specifically `nr_campione`, `us`, `numero_inventario_materiale`, and `nr_cassa` — are normalized to empty strings, while all other fields are converted directly to strings. Returns a list of nine-element lists, each containing the site name (with underscores replaced by spaces), sample number, sample type, description, area, stratigraphic unit, material inventory number, conservation location, and crate number.

##### update_if(self, msg)

*No description available.*
Handles the conditional execution of a record update based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort or the current sort configuration depending on `SORT_STATUS`. Returns `1` if the update and data reload succeed, `0` if `update_record()` fails, and resets the browse status label accordingly.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the mapped table class, ordered by the ID column in ascending order. The results are stored directly in the instance attribute `self.DATA_LIST`, replacing any previously held data. This method uses a single ordered query via `self.DB_MANAGER.query_ordered` as a performance optimisation over a double-query pattern.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each cell that contains a non-empty item, the cell's text value is appended to a per-row sublist. Returns a list of sublists, where each sublist represents one row's non-empty cell values as strings.

##### empty_fields_nosite(self)

Clears and resets all input fields in the form except for the site (`comboBox_sito`) field. Specifically, it clears `lineEdit_nr_campione`, `lineEdit_area`, `lineEdit_us`, `lineEdit_n_inv_mat`, `lineEdit_luogo_conservazione`, and `lineEdit_cassa`, and resets `comboBox_tipo_campione` and `textEdit_descrizione_camp` to empty values. This method is intended for scenarios where the site field should retain its current value while all other fields are reset.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to their default empty state. This includes clearing the combo boxes for site (`comboBox_sito`) and sample type (`comboBox_tipo_campione`), the text editor for description (`textEdit_descrizione_camp`), and the line edit fields for sample number, area, stratigraphic unit, inventory number, conservation location, and storage box (fields 1–10).

##### fill_fields(self, n)

*No description available.*
Populates the form's UI fields with data from the record at index `n` in `DATA_LIST`, storing the index in `self.rec_num`. Before assignment, the fields `nr_campione`, `us`, `numero_inventario_materiale`, and `nr_cassa` are individually checked for `'None'` string values and replaced with empty strings. Any exception raised during the operation is silently suppressed.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values for the UI. Assigns the parameters `t` and `c` to the instance variables `rec_tot` and `rec_corr` respectively, then updates the corresponding labels `label_rec_tot` and `label_rec_corrente` with their string representations.

##### set_LIST_REC_TEMP(self)

*No description available.*
Reads the current values from the form's input widgets and constructs a temporary data record, storing it in `self.DATA_LIST_REC_TEMP` as a list of nine string elements. Integer fields (`nr_campione`, `us`, `numero_inventario_materiale`, and `nr_cassa`) are parsed from their respective `lineEdit` widgets, with empty inputs converted to `None` before being cast to strings. The resulting list captures, in order: site, sample number, sample type, description, area, stratigraphic unit, material inventory number, box number, and conservation location.

##### set_LIST_REC_CORR(self)

Populates `DATA_LIST_REC_CORR` by clearing the list and iterating over `TABLE_FIELDS`, retrieving the corresponding attribute value from the current record (`DATA_LIST[REC_CORR]`) for each field using `getattr`. Each retrieved value is converted to a string and appended to `DATA_LIST_REC_CORR`. This method effectively synchronizes the correction record list with the data of the currently active record index.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `pos_none_in_list` on `self.DATA_LIST_REC_TEMP` via the `self.UTILITY` helper. The return value, stored in `rec_to_update`, represents the output of that utility operation on the temporary record data list. This method takes no parameters beyond `self` and produces a single return value.

##### records_equal_check(self)

*No description available.*
Compares the current temporary record data against the corresponding corrected record data to determine whether any changes have been made. It first refreshes both internal data lists by calling `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`, then performs a direct equality comparison between `DATA_LIST_REC_CORR` and `DATA_LIST_REC_TEMP`. Returns `0` if the two lists are equal, or `1` if they differ.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `self.DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the result of `self.rec_toupdate()`. Returns `1` on success, or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user based on the language setting `self.L` (`'it'`, `'de'`, or a fallback).

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode and writes the provided `message` string to it, then closes the file. Both `name_file` and `message` are explicitly cast to `str` before use.

