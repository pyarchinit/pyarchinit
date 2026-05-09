# tabs/Attrezzature.py

## Overview

This file contains 39 documented elements.

## Classes

### pyarchinit_Attrezzature

`pyarchinit_Attrezzature` is a QDialog subclass that implements the equipment management form (`Scheda Attrezzature`) within the PyArchInit QGIS plugin, providing a full CRUD interface for records stored in `attrezzature_table`. The class handles browsing, searching, inserting, updating, and deleting equipment records — each identified by fields such as site, inventory code, name, category, brand, model, serial number, ownership, costs, status, assignment, and maintenance dates. All UI labels, status indicators, sort descriptors, and field-to-column mappings are localized at class level based on the QGIS user locale, with explicit support for Italian, English, German, Spanish, French, Arabic, Catalan, Romanian, Portuguese, and Greek.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog by calling the parent constructor, assigning the provided `iface` parameter, and setting up the UI via `setupUi`. Applies the current theme using `ThemeManager.apply_theme` and adds a theme toggle button to the form, then sets `currentLayerId` to `None`, calls `retranslate_ui`, and schedules `_deferred_init` to execute after the window becomes visible via `QTimer.singleShot`.

##### retranslate_ui(self)

Translate UI labels based on current locale.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary action buttons in the interface by passing `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all navigation, record management, and search controls to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of a collection of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This allows all listed controls to be simultaneously enabled or disabled with a single call.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` object and determining whether the backend is SQLite. If the connection succeeds and records exist, it initialises browse state variables, updates UI labels and counters, and populates the form fields; if the database is empty, it displays a localised welcome message (Italian, German, or English) and triggers the new record workflow. If the connection or query fails, a localised error message is constructed indicating that a QGIS restart is required.

##### charge_list(self)

*No description available.*
Populates the site combo box (`comboBox_sito`) by retrieving and sorting distinct site values from the `site_table` via the database manager, removing any empty entries before display. Additionally, populates the `comboBox_categoria`, `comboBox_stato`, and `comboBox_proprieta` combo boxes using thesaurus entries queried from `cantiere_attrezzature_table` for the current language, using thesaurus keys `14.4`, `14.5`, and `14.6` respectively. Any exceptions raised during the thesaurus query are silently suppressed.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured site from the database connection and compares it against the value selected in `comboBox_sito`. If the values match, it displays a localised informational message (Italian, German, or English) confirming the active site connection; if no site has been configured, it displays a localised warning message and, unless the user cancels, opens the `pyArchInitDialog_Config` dialog to allow site configuration.

##### set_sito(self)

Retrieves the configured site setting via a `Connection` object and queries the database for all records matching that site name using `DB_MANAGER.query_bool`. If matching records are found, it populates `DATA_LIST`, updates record counters, fills the form fields, sets the browse and sort status indicators, and disables the site combo box. If no records are found the method returns early; any exception encountered during execution is reported to the user via a `QMessageBox` warning dialog.

##### check_maintenance_alert(self)

Check if next maintenance date is past due and show alert.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available sort items, allowing the user to select sort fields and order type. If no unsaved record state is detected, it converts the selected items using `CONVERSION_DICT`, executes a `query_sort` against the database manager, and replaces `DATA_LIST` with the sorted results. The UI is then updated to reflect browse mode, reset record counters, and display the first record of the sorted dataset.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record in browse mode (`"b"`) has unsaved modifications, and if so, prompting the user with a localized warning dialog (Italian, German, or English) offering the option to save those changes before proceeding. Once any pending save is resolved, the method transitions the form to new-record mode (`"n"`), clearing the fields and updating the status label, sort label, and record counter accordingly. If the current site (`comboBox_sito`) matches the configured site setting, the site combo box is locked; otherwise it remains editable, and in both cases the UI buttons are updated to reflect the new entry state.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event by branching on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it validates the form data via `data_error_check()` and, if the record has been modified (as determined by `records_equal_check()`), prompts the user with a localized confirmation dialog (Italian, German, or English) before calling `update_if()` to persist the changes; if no changes are detected, a localized warning is displayed instead. In insert mode, it validates the data and attempts to insert a new record via `insert_new_rec()`, then reloads the record list, updates the UI counters and status labels, and switches the interface back to browse mode upon success.

##### data_error_check(self)

*No description available.*
Validates that the mandatory fields `comboBox_sito` (Site) and `comboBox_nome` (Name) are not empty before a record operation is performed. If either field is empty, a localized warning dialog is displayed to the user — in Italian (`'it'`), German (`'de'`), or English (default) — based on the value of `self.L`. Returns `0` if all required fields pass validation, or `1` if one or more validation errors are detected.

##### insert_new_rec(self)

Collects and validates input field values from the form UI to construct a new equipment (`attrezzature`) record, converting `costo_acquisto` and `costo_noleggio` to `float` where provided (defaulting to `None` on empty or invalid input). Assigns the next available ID via `DB_MANAGER.max_num_id` and delegates persistence to `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if an exception occurs, displaying a localized warning dialog for integrity errors (duplicate record) or a generic error message for all other failures.

##### check_record_state(self)

*No description available.*
Checks the current state of the record by first performing a data error validation via `data_error_check()`. If no data errors are found but the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog (Italian, German, or English depending on `self.L`) prompting the user to save changes, and delegates the response to `update_if()`. Returns `1` if a data error is detected, or `0` if the record was modified and the save prompt was handled.

##### on_pushButton_view_all_pressed(self)

Handles the "View All" button press event by reloading and displaying all records from the data source. If the record state check passes, it clears the current fields, reloads all records, and repopulates the fields, resetting the browse status to `"b"`, updating the status label, and setting the record counter to reflect the full dataset starting from the first record. The sort label is also reset to the unsorted state indicator, and the method is aliased as `on_pushButton_show_all_pressed`.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Navigates to the first record in the current data list when the corresponding button is pressed. If `check_record_state()` returns `1`, no action is taken; otherwise, it clears the current fields, resets the current record index (`REC_CORR`) to `0` and the total record count (`REC_TOT`) to the length of `DATA_LIST`, then populates the fields with the first record and updates the record counter display. Any exception raised during this process is caught and displayed to the user as a warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during execution is caught and displayed as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one and navigating to the preceding record. If the index reaches `-1`, it is reset to `0` and a localised warning message is displayed (Italian, German, or English depending on `self.L`) to inform the user that the first record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; any exception raised during this process is reported through a warning dialog.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), the index is reverted and a localized warning message is displayed (Italian, German, or English depending on `self.L`) to inform the user they are already at the last record. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the next record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; any exception raised during this process is reported through a warning dialog.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the deletion of the currently displayed database record when the delete button is pressed. It first presents a localized confirmation dialog (Italian, German, or English depending on `self.L`), and proceeds with deletion only if the user confirms; the record's primary key is retrieved from `self.DATA_LIST[self.REC_CORR]` and passed to `self.DB_MANAGER.delete_one_record()`. After deletion, the UI state is updated accordingly — resetting all record lists, counters, and fields if no records remain, or reloading and displaying the first available record if the list is non-empty, and resetting the sort status to `"n"`.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by transitioning the form into search mode (`BROWSE_STATUS = "f"`), provided `check_record_state()` does not return `1`. Depending on whether the current site (`comboBox_sito`) matches the configured site setting retrieved via `Connection().sito_set()`, it either clears fields while preserving the site selection (disabling `comboBox_sito`) or performs a full field reset with the site combo box re-enabled and the list recharged via `charge_list()`. In both branches, the record counter and sort label are reset to their default states, and the search button is disabled via `enable_button_search(0)`.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the "search go" button press event by first verifying that the application is in search mode (`BROWSE_STATUS == "f"`); if not, it displays a localized warning instructing the user to initiate a new search instead. When in search mode, it collects field values from `comboBox_sito`, `lineEdit_codice_inventario`, `comboBox_nome`, `comboBox_categoria`, `comboBox_stato`, `comboBox_assegnato_a`, and `textEdit_note` into a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database using `DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no records were found and restores the previous data state, or populates `DATA_LIST` with the returned records, updates the record counter, fills the form fields, and displays a localized message reporting the number of matching records found; in all cases, `enable_button_search(1)` is called upon completion.

##### update_if(self, msg)

*No description available.*
Conditionally performs a record update based on the user's confirmation message. If `msg` equals `QMessageBox.StandardButton.Ok`, it calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying the database with either a default ascending sort on `ID_TABLE` or the current sort configuration depending on `SORT_STATUS`. Returns `1` if the update and reload succeed, `0` if `update_record()` fails, or `None` implicitly if the confirmation message is not `Ok`.

##### charge_records(self)

*No description available.*
Queries the database via `DB_MANAGER` to retrieve all records from the mapped table, ordered by `ID_TABLE` in ascending order. The results are stored in the instance attribute `DATA_LIST`, replacing any previously held data.

##### setComboBoxEditable(self, f, n)

*No description available.*
Iterates over a list of widget name strings `f` and sets the editable state of each corresponding combo box widget on the instance. For each name, it strips a leading `'self.'` prefix if present, resolves the attribute via `getattr`, and calls `setEditable(bool(n))` on the widget if it exists. The parameter `n` is cast to `bool` to determine whether the combo boxes should be editable or read-only.

##### setComboBoxEnable(self, f, v)

*No description available.*
Iterates over a list of widget name strings `f`, resolving each to an instance attribute by stripping any leading `'self.'` prefix. For each resolved widget, calls `setEnabled()` with a boolean value derived by comparing the string parameter `v` against `"True"`. Widgets that cannot be resolved as instance attributes are silently skipped.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### empty_fields_nosite(self)

*No description available.*
Resets all form fields to their default empty state, excluding the site (`comboBox_sito`) field. Text inputs and combo boxes are cleared or set to empty strings, while date fields (`lineEdit_data_acquisto`, `lineEdit_data_ultima_manutenzione`, and `lineEdit_data_prossima_manutenzione`) are reset to January 1, 2000. This method is the counterpart to `empty_fields`, which additionally clears the site combo box.

##### empty_fields(self)

Resets all input fields in the form to their default empty state. Combo boxes are cleared by setting their edit text to an empty string, text and line edit fields are cleared using their respective `clear()` methods, and date fields (`lineEdit_data_acquisto`, `lineEdit_data_ultima_manutenzione`, `lineEdit_data_prossima_manutenzione`) are reset to `QDate(2000, 1, 1)`. This method affects the following controls: `comboBox_sito`, `lineEdit_codice_inventario`, `comboBox_nome`, `comboBox_categoria`, `lineEdit_marca`, `lineEdit_modello`, `lineEdit_numero_serie`, `comboBox_proprieta`, `lineEdit_costo_acquisto`, `lineEdit_costo_noleggio_giorno`, `comboBox_stato`, `comboBox_assegnato_a`, and `textEdit_note`.

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` within `self.DATA_LIST`, storing the index in `self.rec_num`. Text and combo box fields are filled directly from the corresponding record attributes, while date fields (`data_acquisto`, `data_ultima_manutenzione`, `data_prossima_manutenzione`) are parsed from both `"yyyy-MM-dd"` and `"dd/MM/yyyy"` formats, falling back to `QDate(2000, 1, 1)` when the value is absent or invalid. After populating all fields, `check_maintenance_alert()` is called; any exception raised during the process is silently suppressed.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects the current values from all form widgets and populates `DATA_LIST_REC_TEMP` with a ordered list of field values representing a temporary record snapshot. Acquisition cost and rental cost fields are read as strings only if non-empty, otherwise defaulting to an empty string; the assignee field is cast to `int` if non-blank, otherwise set to `None`. Date fields are formatted as `"yyyy-MM-dd"` strings, and all remaining fields are read directly from their respective combo boxes, line edits, and text edit widgets.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and then iterating over `TABLE_FIELDS`, appending the string representation of each corresponding attribute from the current record (`DATA_LIST[REC_CORR]`) using `getattr`. The resulting list reflects the persisted field values of the currently active record as stored in `DATA_LIST`. This method is used in conjunction with `set_LIST_REC_TEMP` by `records_equal_check` to compare the stored record state against temporary (UI) values.

##### records_equal_check(self)

*No description available.*
Compares the current record (`DATA_LIST_REC_CORR`) against a temporary record (`DATA_LIST_REC_TEMP`) to determine whether any changes have been made. Both internal lists are refreshed prior to comparison by calling `set_LIST_REC_CORR()` and `set_LIST_REC_TEMP()` respectively. Returns `0` if the two records are identical, or `1` if they differ.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, the ID value of the current record (`DATA_LIST[REC_CORR]`), the defined table fields, and the prepared update data from `rec_toupdate()`. Returns `1` on success. If an exception occurs, the error is appended to `error_encodig_data_recover.txt` in the report folder, a warning dialog is displayed to the user indicating an encoding problem, and `0` is returned.

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `pos_none_in_list` on `self.DATA_LIST_REC_TEMP` via the `self.UTILITY` helper. This identifies the positions or records within the temporary data list that contain `None` values and are therefore pending an update. The method returns the resulting value directly without additional processing.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded, separated by hyphens). The formatted date string is then returned to the caller.

