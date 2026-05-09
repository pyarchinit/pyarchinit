# tabs/Presenze.py

## Overview

This file contains 46 documented elements.

## Classes

### pyarchinit_Presenze

`pyarchinit_Presenze` is a QDialog subclass that provides a multilingual data entry and management form for recording personnel attendance records within the pyArchInit archaeological site management system. It supports browsing, searching, creating, updating, and deleting records in the `presenze_table` database table, with fields covering site, personnel, date, clock-in/out times, regular and overtime hours, day type, shift, work area, notes, and daily cost. The class also provides quick-registration shortcuts for common attendance types, automatic hour and cost calculation, and export functionality to PDF and CSV/Excel formats, with all UI labels and status messages localized across ten languages.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the form widget by calling the parent constructor, setting up the UI, and applying the current theme with a toggle button. Connects UI signals to their respective slots, including site selection changes to reload the personnel list, export buttons for PDF and Excel output, and quick-register buttons for attendance types (`regular`, `holiday`, `sick`, `dayoff`). Database loading is deferred via `QTimer.singleShot` so the window becomes visible immediately before data is fetched.

##### quick_register(self, reg_type)

Quick-fill attendance form for today with selected type.

##### retranslate_ui(self)

Translate UI labels based on current locale.

##### enable_button(self, n)

Sets the enabled state of all primary action buttons in the interface by passing the value of `n` to each button's `setEnabled` method. The buttons affected include navigation controls (`pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`), record management controls (`pushButton_new_rec`, `pushButton_delete`), search controls (`pushButton_new_search`, `pushButton_search_go`), and the `pushButton_connect`, `pushButton_show_all`, and `pushButton_sort` buttons. The parameter `n` is passed directly to `setEnabled` for each button, determining whether they are interactive or disabled.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of a collection of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the primary navigation, record management, and connection controls as a group.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` object and determining whether the backend is SQLite. If the connection succeeds and records exist, it initialises browse state variables, updates UI labels and counters, and populates the form fields; if the database is empty, it displays a localised welcome message (Italian, German, or English) and triggers the new record workflow. If the connection or any subsequent operation raises an exception, a localised error message is constructed indicating either a missing table or a general bug, with guidance to restart QGIS or report the issue to the developer.

##### charge_list(self)

*No description available.*
Populates the site combo box (`comboBox_sito`) by retrieving and sorting all distinct site values from the `site_table` via the database manager, removing any empty entries before display. It then queries the thesaurus for the current language to populate `comboBox_tipo_giornata` with extended label values (`sigla_estesa`) corresponding to thesaurus key `'14.3'`. Finally, it delegates population of the personnel combo box to `charge_personale_list`.

##### charge_personale_list(self)

Populate comboBox_personale from personale_table.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured site from the connection settings and compares it against the value selected in `comboBox_sito`. If the values match, it displays a localized informational message confirming the active site connection in Italian (`'it'`), German (`'de'`), or English (default). If no site has been configured (`sito_set_str == ''`), it displays a localized warning message and, unless the user cancels, opens the `pyArchInitDialog_Config` dialog to allow site configuration.

##### set_sito(self)

Retrieves the configured site setting via a `Connection` instance and queries the database for all records matching that site using `DB_MANAGER.query_bool`. If matching records are found, it populates `DATA_LIST`, updates record counters, fills the form fields, sets the browse status, and disables the site combo box. If no records are found the method returns early; if an exception occurs, a warning dialog is displayed in either Italian or English depending on the language setting `self.L`.

##### calculate_hours(self)

Auto-calculate ore_ordinarie from ora_ingresso and ora_uscita.

##### calculate_cost(self)

Auto-calculate costo_giornata from hours * tariffa (query personale_table).

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by first checking the current record state; if no unsaved changes are pending, it opens a `SortPanelMain` dialog populated with the available sort items, allowing the user to select sort fields and order type. Upon dialog confirmation, the selected items are converted using `CONVERSION_DICT`, and the current data list is re-queried and reordered via `DB_MANAGER.query_sort` using the specified sort fields and mode. The UI is then updated to reflect the sorted results, resetting the browse status, record counters, and sort indicator label accordingly.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record in browse mode (`"b"`) has unsaved modifications; if so, it prompts the user with a localised warning dialog (Italian, German, or English depending on `self.L`) offering the option to save changes before proceeding. If the browse status is not already `"n"` (new), it transitions the form to new-record mode by updating `BROWSE_STATUS`, clearing fields, resetting the record counter and sort label, and enabling or disabling `comboBox_sito` depending on whether its current value matches the configured site setting (`sito_set_str`). Finally, it calls `self.enable_button(0)` to update the UI button states for new-record mode.

##### on_pushButton_save_pressed(self)

Handles the save button press event, branching logic based on the current `BROWSE_STATUS` value. In browse mode (`"b"`), it validates the data via `data_error_check()`, and if the record has been modified (as determined by `records_equal_check()`), prompts the user with a localised confirmation dialog (Italian, German, or English depending on `self.L`) before calling `update_if()` to persist the changes; if no modifications are detected, a localised warning is displayed instead. Outside browse mode, it validates the data and attempts to insert a new record via `insert_new_rec()`, then reloads and refreshes the UI state, record counters, and field values upon success.

##### data_error_check(self)

*No description available.*
Validates required form fields before a record is saved, checking that the site (`comboBox_sito`) is not empty and that the date (`lineEdit_data`) is not the default value of `QDate(2000, 1, 1)`. Warning dialogs are displayed in Italian, German, or English depending on the value of `self.L`. Returns `0` if all checks pass, or `1` if one or more validation errors are detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates input values from the form's UI controls — including personnel ID from the combobox, optional floating-point fields (`ore_ordinarie`, `ore_straordinario`, `costo_giornata`), and various text and date fields — then constructs a new presence record by calling `DB_MANAGER.insert_presenze_values` with the next available ID. The assembled record is persisted to the database via `DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` on failure, displaying a localized or generic error message via `QMessageBox.warning` if an `IntegrityError` (duplicate record) or any other exception occurs.

##### check_record_state(self)

*No description available.*
Checks the current state of the record by first performing a data error check via `data_error_check()`. If no data errors are found and the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompting the user to save changes, and calls `update_if()` with the user's response. Returns `1` if a data error is detected, or `0` if the record was modified and the save prompt was handled.

##### on_pushButton_view_all_pressed(self)

Handles the "View All" button press event by first checking the current record state via `check_record_state()`; if the check does not return `1`, it clears the current fields, reloads all records, and repopulates the fields. It then sets the browse status to `"b"`, updates the status label, resets the record counter, and sets both `REC_TOT` and `REC_CORR` to reflect the full dataset starting at the first record. The sort label is also reset to the unsorted state indicator, and this method is aliased as `on_pushButton_show_all_pressed`.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Navigates to the first record in the current data list when the corresponding button is pressed. If `check_record_state()` returns `1`, the action is suppressed; otherwise, the method clears the current fields, resets the record position to the beginning (`REC_CORR = 0`), populates the fields with the first record, and updates the record counter accordingly. Any exception raised during this process is caught and displayed to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It first checks the current record state via `check_record_state()` and aborts navigation if the return value is `1`; otherwise, it clears the current form fields with `empty_fields()`, populates them with the last record's data via `fill_fields()`, and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one and navigating to the preceding record. If the index reaches `-1`, it is reset to `0` and a localised warning message is displayed (Italian, German, or English depending on `self.L`) to inform the user that the first record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; any exception raised during this process is reported through a warning dialog.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Advances navigation to the next record in the dataset by incrementing `REC_CORR`. If the incremented index reaches or exceeds `REC_TOT`, it reverts the counter and displays a localized warning message (Italian, German, or English) indicating that the last record has been reached. Otherwise, it clears the current fields, populates them with the data for the new record, and updates the record counter display; any exception encountered during this process is reported via an error dialog.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed, the method removes the record identified by `self.ID_TABLE` from `self.TABLE_NAME`, then reloads the record list and updates the UI state accordingly. If the data list becomes empty after deletion, all record tracking fields are reset and form fields are cleared; otherwise, the browse position is reset to the first record and the display is refreshed via `self.charge_list()`, `self.fill_fields()`, and `self.set_sito()`. In all cases, the sort status is reset to `"n"` upon completion.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by resetting the interface to a fresh search state (`BROWSE_STATUS = "f"`). If the current site selection matches the configured site set, it clears all fields except the site field and locks the site combo box; otherwise, it clears all fields, enables the site combo box, and reloads the combo box list via `charge_list()`. The method performs no action if `check_record_state()` returns `1`, and disables the search button at the start of execution via `enable_button_search(0)`.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the "search go" button press event by first verifying that the application is in search mode (`BROWSE_STATUS == "f"`); if not, it displays a localized warning message (Italian, German, or English) instructing the user to initiate a new search instead. When in search mode, it constructs a search dictionary from the current UI field values (`comboBox_sito`, `lineEdit_data`, `comboBox_tipo_giornata`, `comboBox_turno`, `lineEdit_area_lavoro`, `textEdit_note`), removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database using `DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no records were found and restores the previous data state, or populates `DATA_LIST` with the returned records, updates the record counter, refreshes the displayed fields, transitions `BROWSE_STATUS` to `"b"`, and disables `comboBox_sito`; the search button is re-enabled via `enable_button_search(1)` in all cases.

##### update_if(self, msg)

*No description available.*
Conditionally performs a record update based on the user's confirmation response. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying and re-sorting the records according to the current sort status (`SORT_STATUS`), applying either a default ascending sort on `ID_TABLE` or a custom sort using `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Upon successful completion, sets `BROWSE_STATUS` to `"b"`, updates the status label, and returns `1`; returns `0` if the update fails.

##### charge_records(self)

Retrieves all records from the database for the current mapper table class, ordered by the table's ID column in ascending order. The results are stored in the instance attribute `DATA_LIST` via a call to `self.DB_MANAGER.query_ordered`, using `self.MAPPER_TABLE_CLASS`, `self.ID_TABLE`, and the sort direction `'asc'` as arguments.

##### setComboBoxEditable(self, f, n)

Sets the editable state of one or more combo box widgets on the current instance.

Accepts a list of widget name strings `f` and an integer or boolean value `n`. For each name in `f`, the method resolves the corresponding instance attribute (stripping a leading `'self.'` prefix if present) and calls `setEditable(bool(n))` on it, provided the attribute exists.

##### setComboBoxEnable(self, f, v)

*No description available.*
Iterates over a list of widget name strings `f`, resolving each to an instance attribute by stripping any leading `'self.'` prefix. For each resolved widget, calls `setEnabled()` with a boolean value derived by comparing the string parameter `v` against `"True"`. Widgets that cannot be resolved as instance attributes are silently skipped.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total record count and current record counter by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels by setting `self.label_rec_tot` to the string representation of `self.rec_tot` and `self.label_rec_corrente` to the string representation of `self.rec_corr`.

##### empty_fields_nosite(self)

Resets a predefined set of form fields to their default or empty states, excluding the site (`comboBox_sito`) field. Specifically, it sets `comboBox_personale` to an unselected state, resets `lineEdit_data` to January 1, 2000, clears the entry and exit time fields, clears ordinary and overtime hours, sets the day type and shift combo boxes to empty text, and clears the work area, notes, and daily cost fields.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to their default empty or initial states. String-based combo boxes are cleared to an empty string, the personnel combo box selection is reset to index `-1` (no selection), the date field is set to `2000-01-01`, and all remaining line edit and text edit fields are cleared. This method is typically called to prepare the form for new data entry.

##### fill_fields(self, n)

Populates all form fields with data from the record at position `n` in `DATA_LIST`, storing the index in `self.rec_num`. It sets the site combo box, resolves the personnel combo box by `id_personale`, parses the date string using multiple formats (`"yyyy-MM-dd"`, `"dd/MM/yyyy"`, `"dd-MM-yyyy"`) before applying it to `lineEdit_data`, and fills the remaining fields for entry/exit times, ordinary and overtime hours, day type, shift, work area, notes, and daily cost. Any exception raised during the operation is silently suppressed.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects the current values from all form fields and widgets into a temporary record list, storing the result in `self.DATA_LIST_REC_TEMP`. The list is populated in a fixed order comprising: the selected site (`comboBox_sito`), personnel ID (`comboBox_personale.currentData()`), date formatted as `"yyyy-MM-dd"` (`lineEdit_data`), entry and exit times, ordinary and extraordinary hours, day type, shift, work area, notes, and daily cost. Fields that are empty or return `None` are stored as empty strings to ensure consistent list structure.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and iterating over `TABLE_FIELDS`, appending the string representation of each corresponding attribute from the current record (`DATA_LIST[REC_CORR]`) via `getattr`. The resulting list represents the stored field values of the current record as it exists in `DATA_LIST`, identified by the `REC_CORR` index. This method is used in conjunction with `set_LIST_REC_TEMP` to enable comparison between the current record's persisted state and any temporary modifications.

##### records_equal_check(self)

*No description available.*
Compares the current record (`DATA_LIST_REC_CORR`) against a temporary record (`DATA_LIST_REC_TEMP`) to determine whether they are identical. Both internal lists are refreshed prior to comparison by calling `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`. Returns `0` if the two records are equal, or `1` if they differ.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `rec_toupdate()`. Returns `1` on success, or `0` if an exception occurs. On failure, the exception message is appended to `error_encodig_data_recover.txt` in the report folder, and a warning dialog is displayed to the user in either Italian or English depending on the value of `self.L`.

##### rec_toupdate(self)

*No description available.*
Returns the list of records that require updating by delegating to `self.UTILITY.pos_none_in_list`, passing `self.DATA_LIST_REC_TEMP` as the argument. The result, representing positions or entries identified as pending update within the temporary data list, is returned directly to the caller.

##### datestrfdate(self)

Returns the current date as a formatted string in `DD-MM-YYYY` format.

The method retrieves today's date using `date.today()` and applies `strftime("%d-%m-%Y")` to produce the formatted string. The resulting string is returned to the caller.

##### on_pushButton_export_pdf_pressed(self)

Export attendance records to a professional full-page landscape PDF.

##### on_pushButton_export_excel_pressed(self)

Export attendance records to Excel.

## Functions

### resolve_name(id_pers)

*No description available.*
Looks up a personnel identifier in `personnel_map` and returns the corresponding full name string. If the initial lookup fails, it attempts to coerce `id_pers` to an integer and retries the lookup. If no match is found, it returns the string representation of `id_pers`, or an empty string if `id_pers` is falsy.

**Parameters:**
- `id_pers`

### header_footer(canvas, doc)

*No description available.*
A ReportLab page callback function that renders a consistent header and footer on every page of a landscape A4 PDF document. The header draws a filled colour bar with an accent line beneath it, displaying the application name (`pyArchInit`), site name, date range, and the generation timestamp aligned to the right. The footer draws a matching colour bar at the bottom of the page containing a localised footer text string on the left and the current page number on the right.

**Parameters:**
- `canvas`
- `doc`

