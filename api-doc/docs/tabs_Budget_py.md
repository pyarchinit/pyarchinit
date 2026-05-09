# tabs/Budget.py

## Overview

This file contains 46 documented elements.

## Classes

### pyarchinit_Budget

`pyarchinit_Budget` is a multilingual QDialog form for managing archaeological site budget records within the PyArchInit QGIS plugin. It provides a full CRUD interface backed by a database manager, supporting browsing, searching, sorting, inserting, updating, and deleting records from `budget_table`, with fields covering site, year, category, description, estimated and actual amounts, dates, supplier, and invoice number. The class also includes an analytics tab that renders summary statistics, a category spending chart, a monthly timeline chart, and a planned-versus-actual variance chart, with optional PDF export via ReportLab; all UI labels and status messages are localized for ten languages based on the active QGIS locale.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog by calling the parent constructor, assigning the provided `iface` parameter, and setting up the UI via `setupUi`. Applies the current theme using `ThemeManager.apply_theme` and adds a theme toggle button to the form, then sets `currentLayerId` to `None`, calls `retranslate_ui`, and schedules `_deferred_init` to execute after the window becomes visible via `QTimer.singleShot`.

##### retranslate_ui(self)

Translate UI labels based on current locale.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of the primary UI control buttons by passing `n` to the `setEnabled()` method of each button. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This method can be used to enable or disable all listed controls simultaneously by passing a truthy or falsy value for `n`.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of a collection of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_show_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically called to collectively enable or disable these controls based on the current application state.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` object and determining whether the backend is SQLite. If the connection succeeds and records exist, it initialises browsing state variables, updates UI labels and counters, and populates the form fields; if the database is empty, it displays a localised welcome message (Italian, German, or English) and triggers the new record flow. If the connection or query fails, a localised error message is constructed indicating that a QGIS restart is required.

##### charge_list(self)

Populates the site (`sito`) combo box by retrieving and sorting distinct site values from the `site_table` via the database manager, removing any empty entries before adding the results to `comboBox_sito`. It then queries the thesaurus for the current language (mapped via `LANG_TO_THESAURUS`) against `cantiere_budget_table`, extracting extended label values (`sigla_estesa`) for thesaurus key `'14.7'` and populating `comboBox_categoria` with those values. Any exception raised during the thesaurus query is silently suppressed.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured site from the database via `Connection.sito_set()` and compares it against the value selected in `comboBox_sito`. If the values match, it displays a localised informational message (Italian, German, or English) confirming the active site connection. If no site has been configured (empty string), it displays a localised warning and, unless the user cancels, opens the `pyArchInitDialog_Config` dialog to allow site setup.

##### set_sito(self)

*No description available.*
Retrieves the configured site (`sito`) setting via a `Connection` object and queries the database for all records matching that site value. If matching records are found, it populates `DATA_LIST`, updates the record counter, fills the UI fields with the first record, and sets the browse status to `"b"` while disabling the `comboBox_sito` widget. Any exception raised during this process is caught and displayed to the user as a warning dialog.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog that allows the user to select sort fields and order type. If no unsaved record state is detected, it converts the selected sort items using `CONVERSION_DICT`, executes a database sort query via `DB_MANAGER.query_sort`, and repopulates `DATA_LIST` with the sorted results. The method then updates the browse status, record counters, sort label, and refreshes the displayed fields to reflect the newly sorted data.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record in browse mode (`"b"`) has been modified, and if so, prompting the user with a localised warning dialog (Italian, German, or English) to optionally save pending changes before proceeding. If the browse status is not already `"n"` (new), it transitions the form to new-record mode by setting `BROWSE_STATUS` to `"n"`, updating the status and sort labels, and clearing the record counter. Depending on whether the current site (`comboBox_sito`) matches the configured site setting, the site combo box is either locked (disabled) with fields partially cleared via `empty_fields_nosite()`, or left editable with all fields fully cleared via `empty_fields()`, after which the UI buttons are reconfigured via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

Handles the save button press event by branching logic based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it validates the data via `data_error_check()`, and if changes are detected through `records_equal_check()`, prompts the user with a localized confirmation dialog (Italian, German, or English) before calling `update_if()` to persist the modifications; if no changes are detected, a localized warning is displayed. In insert mode, it validates the data and attempts to insert a new record via `insert_new_rec()`, then reloads and refreshes the UI state, record counters, and field display upon success.

##### data_error_check(self)

*No description available.*
Validates the required form fields `comboBox_sito` (site) and `comboBox_anno` (year) before a record is saved, displaying localized warning dialogs in Italian (`'it'`), German (`'de'`), or English (default) depending on the value of `self.L`. The year field is additionally verified to be numeric using `EC.data_is_int()`. Returns `0` if all validations pass, or `1` if one or more validation errors are detected.

##### insert_new_rec(self)

*No description available.*
Collects budget record data from the form's UI fields, converting `importo_previsto` and `importo_effettivo` to `float` where provided (defaulting to `None` on empty input or `ValueError`), and inserts a new record into the database via `DB_MANAGER.insert_budget_values` using the next available ID. The assembled data object is then persisted through `DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` if an exception occurs — displaying a localized warning dialog for integrity constraint violations (supporting `'it'`, `'de'`, and default English messages) or a generic error message for all other failures.

##### check_record_state(self)

*No description available.*
Checks the current state of the record by first performing a data error check via `data_error_check()`. If no data errors are found but the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompting the user to save changes, and delegates the response to `update_if()`. Returns `1` if a data error is detected, or `0` if the record was modified and the user was prompted; returns `None` implicitly if no errors and no modifications are found.

##### on_pushButton_view_all_pressed(self)

Handles the "View All" button press event by first checking the current record state via `check_record_state()`; if the check does not return `1`, it clears the current fields, reloads all records, and repopulates the fields. It then sets the browse status to `"b"`, updates the status label, resets the record counter, and sets both `REC_TOT` and `REC_CORR` to reflect the full dataset starting at the first record. The sort label is also reset to the unsorted state indicated by `self.SORTED_ITEMS["n"]`, and the method is aliased as `on_pushButton_show_all_pressed`.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Navigates to the first record in the current data list when the corresponding button is pressed. If `check_record_state()` returns `1`, the action is suppressed; otherwise, the method clears existing field values, resets the current record counter (`REC_CORR`) to `0` and the total record count (`REC_TOT`) to the length of `DATA_LIST`, then populates the fields with the first record and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during execution is caught and displayed as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one. If the index reaches `-1`, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) to inform the user that the first record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`. If the record state check returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), the index is reverted and a localized warning message is displayed (Italian, German, or English) informing the user that the last record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the next record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`; any exception during this process is reported through an error dialog.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the deletion of the currently displayed database record when the delete button is pressed. It first presents a localized confirmation dialog (Italian, German, or English depending on `self.L`), and if the user confirms, retrieves the current record's ID from `self.DATA_LIST`, calls `self.DB_MANAGER.delete_one_record()` to remove it from the database, then reloads the record list via `self.charge_records()`. After deletion, the UI state is updated accordingly: if no records remain, all data lists and counters are reset and fields are cleared; if records still exist, the view is repositioned to the first record, the browse status and sort status are reset, and the fields are repopulated.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by transitioning the form to search mode (`BROWSE_STATUS = "f"`), provided `check_record_state()` does not return `1`. Depending on whether the current site (`comboBox_sito`) matches the configured site setting retrieved via `Connection.sito_set()`, it either clears fields while preserving the site selection (disabling `comboBox_sito`) or performs a full field reset with `comboBox_sito` enabled and reloads the combo list via `charge_list()`. In both branches, the record counter and sort label are reset to their default states.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search execution triggered by the "search go" button. If the current browse status is not in search mode (`"f"`), a warning message is displayed (in Italian or English depending on `self.L`) instructing the user to initiate a new search first. Otherwise, it builds a search dictionary from the current values of the site, year, category, description, supplier, invoice number, and notes fields; removes empty entries via `Utility.remove_empty_items_fr_dict`; and executes a boolean query against the database, updating `DATA_LIST`, the record counter, and the UI fields accordingly — displaying a warning if no criteria were set or no matching records were found, and a result count message on success. The method concludes by re-enabling the search button via `enable_button_search(1)`.

##### update_if(self, msg)

*No description available.*
Conditionally performs a record update based on the user's confirmation response. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying the database with either a default ascending sort on `ID_TABLE` or the current sort configuration depending on `SORT_STATUS`. Returns `1` if the update and reload succeed, `0` if `update_record()` fails, or `None` implicitly if the confirmation message does not match `Ok`.

##### charge_records(self)

*No description available.*
Queries the database via `DB_MANAGER` to retrieve all records from the mapped table, ordered by `ID_TABLE` in ascending order. The results are stored in the instance attribute `DATA_LIST`, replacing any previously held data.

##### setComboBoxEditable(self, f, n)

Sets the editable state of one or more combo box widgets on the current instance.

Accepts a list of widget name strings `f` and an integer or boolean value `n`. For each name in `f`, the method resolves the corresponding instance attribute (stripping a leading `'self.'` prefix if present) and calls `setEditable(bool(n))` on the widget if it exists.

##### setComboBoxEnable(self, f, v)

*No description available.*
Iterates over a list of widget name strings `f`, resolving each to an instance attribute by stripping any leading `'self.'` prefix. For each resolved widget, calls `setEnabled()` with a boolean value derived by comparing the string parameter `v` to `"True"`. Widgets that cannot be resolved as instance attributes are silently skipped.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels by setting `self.label_rec_tot` to the string representation of `self.rec_tot` and `self.label_rec_corrente` to the string representation of `self.rec_corr`.

##### empty_fields_nosite(self)

Resets all input fields in the form to their default empty state, excluding the site (`comboBox_sito`) field. Combo boxes for year and category are cleared by setting their text to an empty string, date fields (`lineEdit_data_registrazione` and `lineEdit_data_spesa`) are reset to January 1, 2000, and all remaining line edit and text edit fields are cleared. This method is intended for use when a site selection is not part of the reset operation.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to their default empty state. Combo boxes for site, year, and category are cleared by setting their text to an empty string, text and line edit fields for description, expected amount, actual amount, supplier, and invoice number are cleared, and both date fields (`lineEdit_data_registrazione` and `lineEdit_data_spesa`) are reset to January 1, 2000. This method is typically called to prepare the form for new data entry or to discard the currently displayed values.

##### fill_fields(self, n)

*No description available.*
Populates all form fields with data from the record at index `n` in `DATA_LIST`, storing the index in `self.rec_num`. Each UI widget is updated with the corresponding record attribute (`sito`, `anno`, `categoria`, `descrizione`, `importo_previsto`, `importo_effettivo`, `data_registrazione`, `data_spesa`, `fornitore`, `numero_fattura`, `note`), with `None` or empty values resulting in blank fields. Date fields accept both `"yyyy-MM-dd"` and `"dd/MM/yyyy"` formats, falling back to the current date if parsing fails or to `QDate(2000, 1, 1)` if no date value is present; any exception raised during the process is silently suppressed.

##### set_LIST_REC_TEMP(self)

Collects the current values from all form widgets and assembles them into a list stored in `self.DATA_LIST_REC_TEMP`. The list contains eleven string elements in a fixed order: site, year, category, description, expected amount, actual amount, registration date (formatted as `"yyyy-MM-dd"`), expense date (formatted as `"yyyy-MM-dd"`), supplier, invoice number, and notes. Empty widget values are represented as empty strings rather than `None`.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and iterating over `TABLE_FIELDS` to extract the corresponding attribute values from the current record (`DATA_LIST[REC_CORR]`). Each attribute value is retrieved via `getattr` and appended as a string to `DATA_LIST_REC_CORR`. This method is used in conjunction with `set_LIST_REC_TEMP` to provide the stored record state for comparison in `records_equal_check`.

##### records_equal_check(self)

*No description available.*
Compares the current record (`DATA_LIST_REC_CORR`) against a temporary record (`DATA_LIST_REC_TEMP`) to determine whether any changes have been made. Both internal lists are refreshed prior to comparison by calling `set_LIST_REC_CORR()` and `set_LIST_REC_TEMP()` respectively. Returns `0` if the two records are identical, or `1` if they differ.

##### update_record(self)

Attempts to update the current record in the database by calling `self.DB_MANAGER.update` with the mapped table class, ID field, the ID value of the current record (`self.DATA_LIST[self.REC_CORR]`), the table fields, and the prepared update data from `rec_toupdate()`. Returns `1` on success. If an exception occurs, the error message is appended to `error_encodig_data_recover.txt` in the report folder, a warning `QMessageBox` is displayed to the user indicating an encoding problem, and `0` is returned.

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `pos_none_in_list` on `self.DATA_LIST_REC_TEMP` via the `self.UTILITY` helper. This identifies positions of `None` values within the temporary record data list, returning that result directly to the caller.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### on_tab_changed(self, index)

When analytics tab is selected, refresh analytics data.

##### refresh_analytics(self)

Refresh all analytics widgets with current data.

##### update_summary_cards(self, records)

Calculate and display summary statistics on card labels.

##### update_summary_table(self, records)

Populate the budget summary table grouped by category.

##### draw_category_chart(self, records)

Draw a donut chart of actual spending by category using matplotlib (primary).

##### draw_timeline_chart(self, records)

Draw a bar+line chart of monthly spending trend using matplotlib (primary).

##### draw_variance_chart(self, records)

Draw a horizontal grouped bar chart for planned vs actual by category using matplotlib (primary).

##### export_analytics_pdf(self)

Export analytics summary to PDF using ReportLab.

