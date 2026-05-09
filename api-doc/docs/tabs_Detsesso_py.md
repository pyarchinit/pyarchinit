# tabs/Detsesso.py

## Overview

This file contains 63 documented elements.

## Classes

### pyarchinit_Detsesso

`pyarchinit_Detsesso` is a QGIS QDialog form class within the PyArchInit plugin that implements the "Scheda Determinazione del sesso" (sex determination record sheet) for bioarchaeological analysis of skeletal individuals. It provides a full CRUD interface for recording, searching, sorting, and managing sex determination data stored in `detsesso_table`, covering cranial morphological traits (glabella, mastoid process, nuchal plane, etc.), mandibular features, and pelvic indicators (preauricular surface, greater sciatic notch, composite arc, ischio-pubic ramus, and ischio-pubic proportions). The class also includes built-in calculation logic for deriving the cranial sexualization index (`ind_cr_sex`) and pelvic sexualization index (`ind_bac_sex`) from the entered morphological grades and values, and supports multilingual display in Italian, German, and English based on the QGIS locale setting.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the dialog by calling the parent constructor, storing the provided QGIS interface (`iface`), and instantiating a `Pyarchinit_pyqgis` object. Sets up the UI via `setupUi`, applies the current theme, adds a theme toggle button, and performs GUI customizations while initializing `currentLayerId` to `None`. Attempts to establish a database connection via `on_pushButton_connect_pressed`, catching any exceptions and displaying a warning message, then populates fields and sets the site context by calling `fill_fields`, `set_sito`, and `msg_sito`.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons by passing the value `n` to each button's `setEnabled()` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all main interface controls to be collectively enabled or disabled with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously by passing the value `n` to the `setEnabled()` method of each button. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the main toolbar controls as a group, depending on the current application state.

##### on_pushButton_connect_pressed(self)

Handles the press event of the connect button by establishing a database connection using a `Connection` object and retrieving the connection string, setting `DB_SERVER` to `"sqlite"` if the connection string indicates an SQLite database. If the connection succeeds, it loads records via `charge_records()`; if records exist, it initialises browse state, counters, and populates the UI fields, otherwise it displays a localised welcome message (supporting `'it'`, `'de'`, and a default English variant) and triggers new record creation. If an exception occurs during connection or record loading, a localised warning message is pushed to the QGIS message bar, distinguishing between a missing-table condition and other errors.

##### customize_GUI(self)

*No description available.*
A placeholder method intended to apply customizations to the graphical user interface. The method body contains no implementation (`pass`), indicating it is either reserved for future development or designed to be overridden in a subclass. See implementation for any concrete behavior defined in derived classes.

##### loadMapPreview(self, mode)

*No description available.*
```python
def loadMapPreview(self, mode=0):
```

Loads and displays a map preview within the interface. Accepts an optional `mode` parameter (default `0`) that controls the preview loading behavior. Implementation details are not documented in source.

##### charge_list(self)

*No description available.*
Populates the `comboBox_sito` combo box with a sorted list of site values retrieved from the `site_table` database table. The method queries the database via `DB_MANAGER.group_by` on the `sito` column, converts the result to a list using `UTILITY.tup_2_list_III`, and removes any empty string entries before sorting and loading the values into the combo box. The combo box is cleared before the new items are added.

##### msg_sito(self)

*No description available.*
Validates the currently selected site in `comboBox_sito` against the configured site retrieved from the `Connection` object and displays a localized informational `QMessageBox` accordingly. If the selected site matches the configured site, a confirmation message is shown in Italian, German, or English based on `self.L`. If no site has been configured (`sito_set_str` is empty), a localized warning message is displayed prompting the user to configure one, and if the user confirms, the configuration dialog `pyArchInitDialog_Config` is opened.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` object and, if a site value is present, queries the database for all records matching that site, populating `DATA_LIST` and updating the UI fields, browse status, record counter, and disabling the site combo box. If no matching records are found for the configured site, a localized warning message is displayed to the user in Italian, German, or English depending on the value of `self.L`. If the site setting string is empty or falsy, the method takes no action.

##### charge_periodo_list(self)

*No description available.*
A placeholder method that currently contains no implementation. It is defined with a `pass` statement, indicating it is reserved for future logic intended to populate or refresh a period list within the interface. No parameters are accepted beyond the implicit `self` reference, and no value is returned.

##### charge_fase_iniz_list(self)

*No description available.*
Loads or populates the initial phase list used within the application. This method is part of a group of related list-loading methods, alongside `charge_periodo_list` and `charge_fase_fin_list`, which handle period and final phase lists respectively. See implementation for details on the data source and population logic.

##### charge_fase_fin_list(self)

*No description available.*
Loads or populates the final phase list within the current context. This method is the counterpart to `charge_fase_iniz_list`, which handles the initial phase list. Implementation details are not documented in source.

##### generate_list_pdf(self)

Iterates over all records in `self.DATA_LIST` and constructs a list of rows suitable for PDF generation. Each row contains 53 fields per individual, including site name (with underscores replaced by spaces), individual number, cranial and mandibular morphological trait scores (degree of importance and values), cranial sexualisation totals and index, and pelvic sex indicators. Returns the assembled `data_list`.

##### on_toolButtonPan_toggled(self)

*No description available.*
Slot method triggered when the pan tool button is toggled. It instantiates a `QgsMapToolPan` object bound to the `mapPreview` canvas and sets it as the active map tool, enabling pan interaction on the map preview widget.

##### on_pushButton_sort_pressed(self)

*No description available.*
Opens a `SortPanelMain` dialog pre-populated with the current `SORT_ITEMS`, allowing the user to select sort fields and order type. Upon dialog confirmation, the selected items are converted using `CONVERSION_DICT` and the current dataset is re-queried via `DB_MANAGER.query_sort` using the converted sort fields and sort mode. The resulting sorted list replaces `DATA_LIST`, resets the record counter and browse status, and refreshes the displayed fields accordingly.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle state change of the `toolButtonGis` button. When the button is checked, displays a warning message box informing the user that GIS mode is active and that search results will be displayed in the GIS; when unchecked, displays a warning message box informing the user that GIS mode has been deactivated and search results will no longer be shown in the GIS. Both notifications use a standard `Ok` button to dismiss the dialog.

##### on_toolButtonPreview_toggled(self)

*No description available.*
Handles the toggle state change of the `toolButtonPreview` button. When the button is checked, it displays a warning message box informing the user that "US Preview Mode" has been activated and that US plans will be shown in the Plans section, then calls `loadMapPreview()` with no arguments. When the button is unchecked, it calls `loadMapPreview(1)` directly without displaying any message.

##### on_pushButton_addRaster_pressed(self)

*No description available.*
Handles the press event of the "Add Raster" button. When triggered, it checks whether `toolButtonGis` is in a checked state, and if so, calls `self.pyQGIS.addRasterLayer()` to add a raster layer. No action is taken if `toolButtonGis` is not checked.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the application is in browse mode (`BROWSE_STATUS == "b"`) and, if unsaved modifications are detected via `records_equal_check()`, prompting the user with a warning dialog to save or discard changes. If the current status is not already `"n"` (new), it transitions the application to new-record mode by updating `BROWSE_STATUS`, refreshing the status label, clearing all input fields via `empty_fields()`, and resetting the sort label. Finally, it resets the record counter display and updates the button states by calling `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behaviour based on the current `BROWSE_STATUS`. In browse mode (`"b"`), it performs a version conflict check against `detsesso_table` using the concurrency manager before validating data and, if the record has been modified, prompting the user with a confirmation dialog to save or discard changes. In insert mode, it validates the data, inserts a new record, and upon success resets the form fields, reloads the record list, updates status labels and counters, and re-enables the interface buttons.

##### data_error_check(self)

*No description available.*
Performs a data validation check on the current input state and returns an integer result code. In its current implementation, the method initializes a test variable to `0` and returns it directly, with error-checking logic noted as pending via commented-out code. Returns `0` upon completion.

##### insert_new_rec(self)

Collects and validates input values from all UI combo boxes and line edit fields related to cranial and pelvic sex determination indicators, converting empty selections to `None` and non-empty selections to their appropriate numeric or string types. It then calls `self.DB_MANAGER.insert_values_detsesso` with the next available record ID and all collected field values to construct a new database record, followed by `self.DB_MANAGER.insert_data_session` to persist it. Returns `1` on success, or `0` if either operation raises an exception, displaying a warning dialog with an integrity-related message or the raw exception text accordingly.

##### check_record_state(self)

*No description available.*
Validates the current record by first invoking `data_error_check()` to detect any input errors, returning `1` immediately if errors are found. If no input errors exist and `records_equal_check()` indicates the record has been modified, it prompts the user with a warning dialog asking whether to save the changes, delegating the save operation to `update_if()`. Returns `0` when no input errors are present, regardless of whether the record was modified.

##### on_pushButton_insert_row_rapporti_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button for the *rapporti* table is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidget_rapporti'` as the target table identifier. This results in a new row being inserted into `tableWidget_rapporti`.

##### on_pushButton_insert_row_inclusi_pressed(self)

Handles the press event of the "insert row" button associated with the inclusions table. Calls `self.insert_new_row` with the string `'self.tableWidget_inclusi'` as the target table identifier, triggering the insertion of a new row into `tableWidget_inclusi`.

##### on_pushButton_insert_row_campioni_pressed(self)

Handles the press event of the "insert row campioni" button by invoking `insert_new_row` with the argument `'self.tableWidget_campioni'`. This triggers the insertion of a new row into the `tableWidget_campioni` table widget. The method follows the same pattern as `on_pushButton_insert_row_inclusi_pressed`, which performs the equivalent operation on `tableWidget_inclusi`.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button. If `check_record_state()` returns `1`, no action is taken; otherwise, the method clears current field values, reloads all records via `charge_records()`, and repopulates the fields. It then sets the browse status to `"b"`, updates the status label, resets the record counters to reflect the full dataset, sets the current record to the first entry in `DATA_LIST`, and clears the sort label to its default unsorted state.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data set. If the record state check does not return `1`, it clears the existing fields, resets `REC_TOT` to the total number of items in `DATA_LIST` and `REC_CORR` to `0`, then populates the fields with the first entry (index `0`) and updates the record counter accordingly. Any exception raised during this process is caught and displayed to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any exception raised during the process is caught and displayed to the user as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one. If the index reaches `-1`, it is reset to `0` and a warning dialog is displayed informing the user that they are already at the first record. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter is updated via `set_rec_counter()`; any exception raised during this process is caught and displayed as a warning dialog. If `check_record_state()` returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a warning message indicating the user is already on the last record. Otherwise, it clears the current fields via `empty_fields()`, populates them with the next record's data via `fill_fields()`, and updates the record counter display via `set_rec_counter()`; any exception raised during this process is reported through a warning dialog.

##### on_pushButton_delete_pressed(self)

Handles the deletion of the currently selected database record when the delete button is pressed. Displays a confirmation dialog (in Italian) warning the user that the action is irreversible; if confirmed, retrieves the ID of the current record from `DATA_LIST`, calls `DB_MANAGER.delete_one_record` to remove it from the database, and reloads the record list via `charge_records`. If the database becomes empty after deletion, all internal record lists and counters are reset and fields are cleared; otherwise, the UI is updated to display the first remaining record in browse mode, and the sort status is reset to unsorted.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "new search" button by first verifying the current record state via `check_record_state()`; if the check does not return `1`, the search buttons are disabled and the GUI is prepared for a new search. When the browse status is not already `"f"`, it sets `BROWSE_STATUS` to `"f"`, updates the status label, clears all input fields via `empty_fields()`, resets the record counter, and resets the sort label to its unsorted state.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search button press event by first verifying that the application is in search mode (`BROWSE_STATUS == "f"`); if not, it displays a warning message instructing the user to initiate a new search. When in the correct state, it constructs a search dictionary from 53 form fields — including site, individual number, cranial and mandibular morphology grades and values, sex indices, and pelvic indicators — then removes empty entries via `Utility.remove_empty_items_fr_dict` before executing a boolean database query through `DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no records were found and restores the current record view, or populates `DATA_LIST` with the results, updates the record counter and display fields, and optionally triggers a GIS layer update via `pyQGIS.charge_individui_us` before re-enabling the search button.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the current mapper table class, ordered by the ID field in ascending order. The results are stored directly in `self.DATA_LIST`, replacing any previously held data. This method uses a single ordered query via `self.DB_MANAGER.query_ordered` for improved performance over a double-query pattern.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each row, it collects non-`None` cell text values into a sublist, and appends non-empty sublists to a result list. Returns the assembled list of sublists representing the table's data.

##### tableInsertData(self, t, d)

*No description available.*
Accepts two parameters, `t` and `d`, intended for inserting data into a table structure. The method body is not yet implemented (`pass`). Behavior and parameter semantics are not documented in source.

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

Resets all input fields in the form to an empty state by clearing the text of every combo box and line edit widget associated with skeletal sex determination data. This includes fields for cranial morphological traits, pelvic indicators, and their corresponding sex index values. The method operates on all relevant UI controls without returning a value.

##### fill_fields(self, n)

Populates all form fields in the UI with data from the record at index `n` in `self.DATA_LIST`, setting `self.rec_num` to the provided index. For each field, `None` values are rendered as empty strings, while non-`None` values are converted to strings and applied to the corresponding combo boxes or line edits. After populating the fields, if a `concurrency_manager` is present, the method attempts to track the record's version number, record ID (`id_det_sesso`), lock indicator status, and soft lock ownership for the loaded record.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Reads the current values from all form widgets — including combo boxes and line edits — and assembles them into `self.DATA_LIST_REC_TEMP`, a list of 53 string entries representing a temporary record. For each combo box field, an empty selection is converted to `None` before being stored. The resulting list covers cranial and pelvic morphological observation fields, including degree-of-impression grades, categorical values, sex determination indices, and pelvic surface assessments.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and iterating over `TABLE_FIELDS` to extract the corresponding field values from the current record in `DATA_LIST`, identified by the `REC_CORR` index. Each field value is retrieved via `eval` and appended as a string to `DATA_LIST_REC_CORR`. This method is called as part of `records_equal_check` to capture the stored record state for comparison purposes.

##### records_equal_check(self)

*No description available.*
Compares the current record's data against a temporary working copy by invoking `set_LIST_REC_CORR()` and `set_LIST_REC_TEMP()` to populate `DATA_LIST_REC_CORR` and `DATA_LIST_REC_TEMP` respectively. Returns `0` if the two lists are equal, indicating no changes have been made, or `1` if they differ, indicating the record has been modified.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### update_if(self, msg)

*No description available.*
Handles a conditional record update triggered by a user confirmation dialog. If `msg` matches `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Upon completion, it sets `BROWSE_STATUS` to `"b"`, updates the status label accordingly, and returns `1` on success or `0` on failure.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `self.DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `self.rec_toupdate()`. Returns `1` on success or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), English, or German (`de`) depending on `self.L`.

##### rec_toupdate(self)

*No description available.*
Retrieves the record designated for updating by delegating to `self.UTILITY.pos_none_in_list`, passing `self.DATA_LIST_REC_TEMP` as the argument. Returns the resulting value, which represents the position or record from the temporary data list where `None` values have been handled. This method serves as a thin wrapper to identify the current record pending an update operation.

##### charge_id_us_for_individuo(self)

Iterates over `self.DATA_LIST` to extract the `sito`, `area`, and `us` fields from each record, then queries the database via `self.DB_MANAGER.query_bool` using those fields against the `"US"` table. Collects the resulting US records and retrieves the `id_us` attribute from the first result of each query. Returns a list of `id_us` integer identifiers corresponding to each entry in `self.DATA_LIST`.

##### on_pushButton_calcola_ind_sex_pressed(self)

*No description available.*
Slot triggered when the "calcola ind sex" button is pressed. It iterates over up to seventeen cranial morphological traits (e.g., glabella, mastoid process, nuchal crest, zygomatic arch), and for each trait whose combo box is non-empty, multiplies its importance grade by its selected value, accumulating both the weighted products and the sum of grades used. The weighted mean (sum of grade×value products divided by sum of grades) is then compared against fixed threshold ranges to classify the sex index as `"Femmina"` (≤ −0.39), `"Indeterminato"` (−0.4 to 0.4), or `"Maschio"` (≥ 0.41); the computed total value and classification are written to `lineEdit_sex_cr_tot` and `comboBox_ind_cr_sex` respectively, followed by a call to `on_pushButton_save_pressed()`. If no diagnostic trait has been entered, a `QMessageBox` warning is displayed instead.

##### on_pushButton_cranio_pressed(self)

*No description available.*
Event handler triggered when the cranio (cranium) push button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer argument `13` to identify the cranium-specific age determination table. No return value is produced.

##### on_pushButton_bacino_sup_preauricolare_pressed(self)

*No description available.*
Event handler triggered when the `pushButton_bacino_sup_preauricolare` button is pressed. It calls `open_tables_det_eta` with the integer argument `14`, opening the age determination table associated with the preauricular surface of the pelvis. This method follows the same pattern used by adjacent button handlers for other skeletal indicators in the age determination workflow.

##### on_pushButton_bacino_grande_incisura_ischiatica_pressed(self)

*No description available.*
Slot method triggered when the `pushButton_bacino_grande_incisura_ischiatica` button is pressed. It calls `open_tables_det_eta` with the integer argument `15`, opening the age determination table associated with index 15 (grande incisura ischiatica). No parameters are accepted and no value is returned.

##### on_pushButton_bacino_arco_composito_pressed(self)

*No description available.*
Event handler triggered when the `pushButton_bacino_arco_composito` button is pressed. It calls `open_tables_det_eta` with the integer argument `16`, opening the age determination table associated with index 16 (corresponding to the composite arc of the pelvis). This method follows the same pattern used by adjacent button handlers for other pelvic morphological indicators.

##### on_pushButton_bacino_ramo_ischio_pubico_pressed(self)

*No description available.*
Event handler triggered when the *bacino ramo ischio-pubico* button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer value `17` as the identifier for the corresponding age determination table. This method follows the same pattern used by adjacent button handlers within the same UI component group.

##### on_pushButton_proporzioni_ischio_pubiche_pressed(self)

*No description available.*
Handler method triggered when the "proporzioni ischio pubiche" push button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer value `18` as the identifier. This call opens the age determination table or image viewer associated with index `18`.

##### open_tables_det_eta(self, n)

Opens an `ImageViewer` dialog to display a reference anthropological image corresponding to the integer value `n`. Each supported value of `n` maps to a specific image file located in the `resources/anthropo_images/` directory relative to the module's parent directory, covering reference tables such as female/male pubic symphysis (n=1, 2), Kimmerle age estimation charts (n=3, 13), and various pelvic sex determination tables (n=14–18). If the image file cannot be loaded or displayed, a warning `QMessageBox` is shown with the encountered exception message.

##### on_pushButton_calcola_ind_sex_bac_pressed(self)

*No description available.*
Handles the press event of the "calcola ind sex bac" button by computing the sex determination index for the pelvis. It retrieves and evaluates five pelvic indicators — preauricular surface (`sup_p_sex`), greater sciatic notch (`in_isch_sex`), composite arc (`arco_c_sex`), ischiopubic ramus (`ramo_ip_sex`), and ischiopubic proportions (`prop_ip_sex`) — using `find_ind_sex`, then populates the corresponding combo boxes with the computed sex values. Finally, it derives an overall pelvic sex index (`ind_bac_sex`) from the five indicators, maps the result to a human-readable label (`"Maschio"`, `"Femmina"`, `"Indeterminato"`, or `"Dati insufficienti"`), sets the result in `comboBox_ind_bac_sex`, and triggers `on_pushButton_save_pressed`.

##### find_ind_sex(self, sing_char_list)

*No description available.*
Accepts a list of individual sex-indicator characters (`sing_char_list`), where each element is expected to be `"F"` (female), `"M"` (male), `"I"` (indeterminate), or `""` (undeterminable due to post-depositional factors), and counts the occurrences of each category. Applies a priority-based decision logic to determine the prevailing sex classification from the tallied counts. Returns a single string representing the partial sex index: `"F"`, `"M"`, `"I"`, `""`, or `"Error"` if no condition is satisfied.

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode (`'w'`) and writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are explicitly converted to strings via `str()` before use. This method does not return a value.

