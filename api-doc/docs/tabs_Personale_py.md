# tabs/Personale.py

## Overview

This file contains 39 documented elements.

## Classes

### pyarchinit_Personale

*No description available.*
A QDialog subclass that implements the personnel management form (`personale_table`) within the PyArchInit QGIS plugin. It provides a full record-browsing, searching, inserting, updating, and deleting interface for site personnel data — including personal details, contract information, hourly and daily rates, and active status — mapped to the `PERSONALE` ORM class. The dialog supports ten locales (Italian, English, German, Spanish, French, Arabic, Catalan, Romanian, Portuguese, and Greek), applying locale-aware UI labels, status messages, sort item labels, and field-to-column conversion dictionaries at class definition time via `QgsSettings`.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog by calling the parent constructor, storing the provided `iface` reference, and setting up the UI via `setupUi`. Applies the current theme using `ThemeManager.apply_theme` and attaches a theme toggle button to the form, then sets `currentLayerId` to `None` and calls `retranslate_ui`. Schedules `_deferred_init` to execute after the window becomes visible using `QTimer.singleShot`.

##### retranslate_ui(self)

Translate UI labels based on current locale.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary navigation and action buttons by passing `n` to each button's `setEnabled` method. The buttons affected are `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. Passing a truthy value enables all listed buttons simultaneously, while a falsy value disables them.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of a collection of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the main navigation and record-management controls as a group.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` object and determining whether the backend is SQLite. If the connection succeeds and records exist, it initialises browse state variables, updates UI labels and counters, and populates the form fields; if the database is empty, it displays a localised welcome message (Italian, German, or English) and triggers the new record workflow. If the connection or any subsequent operation raises an exception, a localised error message is constructed indicating either a missing table condition or a general bug, prompting the user to restart QGIS or report the issue to the developer.

##### charge_list(self)

*No description available.*
Populates the site combo box (`comboBox_sito`) by retrieving and sorting distinct site values from the `site_table` database table, removing any empty entries before display. Additionally, queries the thesaurus for the current language to populate the role combo box (`comboBox_ruolo`) with values from thesaurus key `'14.1'` and the contract type combo box (`comboBox_tipo_contratto`) with values from thesaurus key `'14.2'`, both sourced from `cantiere_personale_table`. Any exceptions raised during the thesaurus query are silently suppressed.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured archaeological site from the connection settings and compares it against the value selected in `comboBox_sito`. If the values match, it displays a localised informational message (Italian, German, or English) confirming the active site connection. If no site has been configured, it displays a localised warning dialog prompting the user to set one, and opens the `pyArchInitDialog_Config` configuration dialog if the user confirms; if the user cancels, no action is taken.

##### set_sito(self)

*No description available.*
Retrieves the configured site value from a `Connection` instance and queries the database for all records associated with that site using `DB_MANAGER.query_bool`. If matching records are found, it populates `DATA_LIST`, initialises the record counter, fills the form fields, sets the browse status to `"b"`, and disables the site combo box; if no records are found, an informational message is displayed in the appropriate language (Italian, German, or English). Any exception raised during the process is caught and reported to the user via a language-specific warning dialog.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by first checking the current record state; if no unsaved changes are pending, it opens a `SortPanelMain` dialog pre-populated with `SORT_ITEMS` to allow the user to select sort fields and order type. Upon dialog completion, the selected items are converted using `CONVERSION_DICT`, and the current data list is re-queried and reordered via `DB_MANAGER.query_sort` using the converted sort fields and sort mode. The method then resets the browse status, updates the sort status label, refreshes the record counter, and repopulates the form fields to reflect the newly sorted data.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record in browse mode (`"b"`) has unsaved modifications, and if so, prompting the user with a localized save-confirmation dialog (supporting Italian, German, and English based on `self.L`). If the browse status is not already in new-record mode (`"n"`), it transitions to that state by updating status labels and the record counter. Depending on whether the current site (`comboBox_sito`) matches the configured site setting, it either locks the site combo box and clears non-site fields via `empty_fields_nosite()`, or enables the site combo box and clears all fields via `empty_fields()`, before disabling action buttons via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behaviour based on the current `BROWSE_STATUS`. In browse mode (`"b"`), it validates the form data via `data_error_check()` and, if changes are detected by `records_equal_check()`, prompts the user with a localised confirmation dialog (Italian, German, or English) before calling `update_if()` to persist the modifications; if no changes are detected, a localised warning is displayed instead. In insert mode, it validates the data, attempts to insert a new record via `insert_new_rec()`, and on success resets the UI state, reloads the record list, updates counters, and switches back to browse mode.

##### data_error_check(self)

Validates required form fields by checking that `comboBox_sito`, `lineEdit_nome`, and `lineEdit_cognome` are not empty, displaying a localized warning dialog (`QMessageBox.warning`) for each missing value based on the current language setting (`self.L`), which supports Italian (`'it'`), German (`'de'`), and a default English fallback. A local integer variable `test` is initialized to `0` and set to `1` for each validation failure encountered. Returns `test`, where a value of `0` indicates all required fields are populated and `1` indicates one or more validation errors were found.

##### insert_new_rec(self)

*No description available.*
Collects personnel data from the form's UI fields and inserts a new record into the database via `DB_MANAGER.insert_personale_values`, assigning it an ID one greater than the current maximum. Optional numeric fields (`tariffa_oraria`, `tariffa_giornaliera`) are parsed as floats and set to `None` if empty or invalid, and the `attivo` checkbox is converted to an integer value of `1` or `0`. Returns `1` on successful insertion, or `0` if an exception occurs, displaying a localized error message via `QMessageBox.warning` in the event of an integrity violation or other database error.

##### check_record_state(self)

*No description available.*
Checks the current state of the record by first performing a data error check via `data_error_check()`. If no data errors are found and the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog — in Italian, German, or English depending on `self.L` — prompting the user to save the changes, then delegates the response to `update_if()`. Returns `1` if a data error is detected, or `0` if the record was found to be modified and the save prompt was handled.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the "View All" button press event by first checking the current record state via `check_record_state()`; if the check does not return `1`, it clears existing fields, reloads all records, and repopulates the fields. The method then sets the browse status to `"b"`, updates the status label, resets the record counters so that the first record in `DATA_LIST` is current, and clears the sort label to its default unsorted state. An alias `on_pushButton_show_all_pressed` is defined for UI button name compatibility.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data list. If `check_record_state()` does not return `1`, it clears the current fields via `empty_fields()`, resets `REC_CORR` to `0` and `REC_TOT` to the total number of entries in `DATA_LIST`, then populates the fields with the first record by calling `fill_fields(0)` and updates the record counter accordingly. Any exception raised during this process is caught and displayed to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It first checks the current record state via `check_record_state()`; if the check returns `1`, no action is taken. Otherwise, it clears the current form fields with `empty_fields()`, populates them with the last record's data via `fill_fields()`, and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

Navigates to the previous record in the dataset by decrementing `REC_CORR` by one. If the resulting index is `-1`, it resets `REC_CORR` to `0` and displays a localized warning message (Italian, German, or English) indicating that the user is already at the first record. Otherwise, it clears the current fields, populates them with the data for the new current record, and updates the record counter display; any exception encountered during this process is reported via a warning dialog.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Advances the current record index (`REC_CORR`) by one when the "next record" button is pressed, provided `check_record_state()` does not return `1`. If the incremented index reaches or exceeds the total record count (`REC_TOT`), the index is rolled back and a localized warning message is displayed (Italian, German, or English depending on `self.L`) informing the user that the last record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated for the new record via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; any exception during this process is reported through a warning dialog.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently displayed record from the database. If confirmed, it retrieves the current record's ID from `self.DATA_LIST[self.REC_CORR]`, calls `self.DB_MANAGER.delete_one_record()` to remove it, and reloads the record list via `self.charge_records()`. After deletion, the UI state is updated accordingly: if the data list is empty, all record lists and counters are reset and fields are cleared; if records remain, navigation is reset to the first record, fields are repopulated, and the browse status is restored. Finally, the sort status is reset to `"n"` regardless of the outcome.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by resetting the interface to a fresh search state (`BROWSE_STATUS = "f"`). If the current site selection matches the configured site set, it clears all fields except the site field and locks the site combo box; otherwise, it clears all fields, enables the site combo box, and reloads the site list via `charge_list()`. The method performs no action if `check_record_state()` returns `1`, and disables the search button at the start of execution via `enable_button_search(0)`.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search execution triggered by the "search go" button. If the current browse status is not in search mode (`"f"`), a localized warning message is displayed (in Italian, German, or English) instructing the user to initiate a new search first. Otherwise, the method collects field values from the form inputs into a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database using `DB_MANAGER.query_bool`; depending on the result, it either warns the user that no records were found and restores the current record, or populates `DATA_LIST` with the matching results, updates the record counter, fills the form fields, and transitions the browse status to `"b"`. In all cases, the search buttons are re-enabled via `enable_button_search(1)` upon completion.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's confirmation dialog response. If `msg` equals `QMessageBox.StandardButton.Ok`, it calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either the default sort order or the current custom sort configuration. Sets `BROWSE_STATUS` to `"b"` and updates the status label accordingly, returning `1` on success or `0` on failure; no action is taken if the message does not match `Ok`.

##### charge_records(self)

*No description available.*
Queries the database via `DB_MANAGER` to retrieve all records from the mapped table, ordered by `ID_TABLE` in ascending order. The results are stored in the instance attribute `DATA_LIST`, replacing any previously held data.

##### setComboBoxEditable(self, f, n)

*No description available.*
Iterates over a list of widget name strings `f` and sets the editable state of each corresponding combo box widget on the instance. Each string in `f` is resolved to an instance attribute by stripping a leading `'self.'` prefix if present, then retrieved via `getattr`. The editable state of each located widget is set by calling `widget.setEditable(bool(n))`, where `n` is cast to a boolean to determine whether the combo box is editable.

##### setComboBoxEnable(self, f, v)

*No description available.*
Iterates over a list of widget name strings `f`, resolving each to an instance attribute by stripping any leading `'self.'` prefix. For each resolved widget, calls `setEnabled()` with a boolean value derived by comparing the string parameter `v` to `"True"`. Widgets that cannot be resolved as instance attributes are silently skipped.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total record count and current record counter by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### empty_fields_nosite(self)

Resets all personnel-related input fields in the form to their default empty or initial states, excluding the site (`comboBox_sito`) field. Text inputs and text areas are cleared, combo boxes are set to empty strings, date fields are reset to `QDate(2000, 1, 1)`, numeric rate fields are cleared, and the active status checkbox is unchecked. This method is the site-agnostic counterpart to `empty_fields`, which additionally clears the site combo box.

##### empty_fields(self)

Resets all input fields in the form to their default empty or initial state. String-based fields (`comboBox_sito`, `comboBox_ruolo`, `comboBox_tipo_contratto`) are cleared via `setEditText("")`, text and line edit fields are cleared via `clear()`, date fields (`lineEdit_data_nascita`, `lineEdit_data_inizio_contratto`, `lineEdit_data_fine_contratto`) are reset to `QDate(2000, 1, 1)`, and `checkBox_attivo` is set to unchecked (`False`).

##### fill_fields(self, n)

*No description available.*
Populates all form fields with data from the record at index `n` within `DATA_LIST`, storing the index in `self.rec_num`. Text fields, combo boxes, and the IBAN/notes widgets are set directly from the corresponding record attributes, while date fields (`data_nascita`, `data_inizio_contratto`, `data_fine_contratto`) are parsed from either `"yyyy-MM-dd"` or `"dd/MM/yyyy"` format, falling back to `QDate(2000, 1, 1)` when no valid date is present. The `checkBox_attivo` state is derived from the record's `attivo` attribute, and any exception raised during the operation is silently suppressed.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects the current values from all form widgets and assembles them into `DATA_LIST_REC_TEMP`, a list representing a temporary record of personnel data. Optional numeric fields (`tariffa_oraria` and `tariffa_giornaliera`) are read from their respective `QLineEdit` widgets and stored as empty strings if no input is present; the `attivo` checkbox state is converted to `'1'` (checked) or `'0'` (unchecked). The resulting list contains eighteen fields in a fixed order: site, first name, last name, role, qualification, tax code, email, phone, date of birth, address, contract type, contract start date, contract end date, hourly rate, daily rate, IBAN, notes, and active status.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and iterating over `TABLE_FIELDS`, retrieving the corresponding attribute value from the current record (`DATA_LIST[REC_CORR]`) for each field. Each retrieved value is converted to a string and appended to `DATA_LIST_REC_CORR`. This method is used in conjunction with `set_LIST_REC_TEMP` by `records_equal_check` to capture the current record's stored state for comparison purposes.

##### records_equal_check(self)

*No description available.*
Compares the current record's stored state (`DATA_LIST_REC_CORR`) against a temporary working copy (`DATA_LIST_REC_TEMP`) by first refreshing both lists via `set_LIST_REC_CORR()` and `set_LIST_REC_TEMP()`. Returns `0` if the two lists are identical, or `1` if they differ, indicating that unsaved modifications are present.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `rec_toupdate()`. Returns `1` on success, or `0` if an exception occurs. On failure, the exception detail is appended to `error_encodig_data_recover.txt` in the report folder, and a localized warning dialog is displayed to the user indicating an encoding problem with unsupported characters.

##### rec_toupdate(self)

*No description available.*
Returns the list of records that require updating by delegating to the `UTILITY` object's `pos_none_in_list` method, passing `DATA_LIST_REC_TEMP` as the input. The result represents the positions or entries within the temporary record list that contain `None` values, identifying which records are pending an update.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name `n` as a string, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each cell, it retrieves the item's text value if the item is non-null, appending it to a per-row sublist. Returns a list of sublists, where each sublist contains the string text values of the non-null cells in that row.

