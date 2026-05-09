# tabs/Deteta.py

## Overview

This file contains 101 documented elements.

## Classes

### pyarchinit_Deteta

`pyarchinit_Deteta` is a QDialog-based form class within the PyArchInit QGIS plugin that provides a data entry and management interface for recording skeletal age-at-death determinations for archaeological individuals. It maps to the `deteta_table` database table via the `DETETA` mapper class and supports the full CRUD lifecycle — browsing, searching, inserting, updating, and deleting records — covering osteological age indicators such as pubic symphysis phases (Suchey-Brooks and Kimmerle methods), auricular surface scores (SSPIA–SSPID), dental wear ranges, endocranial and ectocranial suture scores, and vault and anterolateral suture totals. The class is fully internationalised, adapting its field labels, status messages, sort items, and conversion dictionaries to the active QGIS locale (Italian, German, English, Spanish, French, Arabic, Catalan, Romanian, Portuguese, or Greek).

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the dialog by calling the parent constructor, storing the provided QGIS interface reference (`iface`), and instantiating a `Pyarchinit_pyqgis` helper object. Sets up the UI layout, applies the current theme via `ThemeManager`, and adds a theme toggle button to the form. Attempts to establish a database connection via `on_pushButton_connect_pressed`, catching any exceptions as a warning dialog, then populates fields and configures the GUI by calling `fill_fields`, `customize_GUI`, `set_sito`, and `msg_sito`.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary navigation and action buttons in the GUI to the value specified by `n`. The affected buttons include `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. Each button's `setEnabled` method is called individually with `n` as the argument.

##### enable_button_search(self, n)

*No description available.*
Enables or disables a set of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically called to collectively control the interactive state of the main record-navigation and data-management controls.

##### enable_button_Suchey_Brooks(self, n)

*No description available.*
Enables or disables the six phase buttons associated with the Suchey-Brooks method by passing the value `n` to the `setEnabled()` method of each button. The affected buttons correspond to phases I through VI (`pushButton_I_fase`, `pushButton_II_fase`, `pushButton_III_fase`, `pushButton_IV_fase`, `pushButton_V_fase`, `pushButton_VI_fase`). The parameter `n` is expected to be a boolean or equivalent value controlling the interactive state of all six buttons simultaneously.

##### enable_button_Kimmerle_m(self, n)

*No description available.*
Enables or disables the set of male Kimmerle push buttons (`pushButton_m_1` through `pushButton_m_7`) by applying the value `n` to each button's `setEnabled` method. The parameter `n` is passed directly to all seven buttons simultaneously, allowing their interactive state to be controlled in a single call.

##### enable_button_Kimmerle_f(self, n)

*No description available.*
Enables or disables all eight female Kimmerle-related push buttons (`pushButton_f_1` through `pushButton_f_8`) by calling `setEnabled(n)` on each. The parameter `n` is passed directly to each button's `setEnabled` method, controlling their interactive state collectively.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` instance and determining whether the target database is SQLite. If the connection succeeds, it loads records from the database and either populates the UI fields and browse state (when data exists) or displays a localized welcome message and initiates a new record prompt (when the database is empty). If the connection or any subsequent operation raises an exception, a localized warning message is pushed to the QGIS message bar indicating a connection failure or detected bug.

##### customize_GUI(self)

*No description available.*
Queries the sex value of the current individual from the database via `sex_from_individuo_table()` and conditionally enables or disables the Kimmerle (male/female) and Suchey-Brooks analysis buttons based on the result. If no query result is returned, all three buttons are disabled. If a sex value is present, button availability is determined by matching the sex string against locale-specific values for Italian (`self.L == 'it'`), German (`self.L == 'de'`), or the default English locale, enabling the sex-appropriate Kimmerle button and the Suchey-Brooks button, or disabling all three if the sex value does not match any recognised option.

##### loadMapPreview(self, mode)

*No description available.*
Loads a map preview based on the specified mode. This method is currently defined as a stub with no implemented logic (`pass`).

**Parameters:**
- `mode` *(int, optional)*: Controls the preview mode. Defaults to `0`.

##### charge_list(self)

*No description available.*
Populates the `comboBox_sito` combo box with a sorted list of site values retrieved from the `site_table` database table, grouped by the `sito` column. The raw query results are converted to a plain list via `UTILITY.tup_2_list_III`, and any empty string entries are removed before the list is sorted and loaded into the combo box.

##### msg_sito(self)

*No description available.*
Validates the currently selected site in `comboBox_sito` against the configured site retrieved from the `Connection` object, then displays a localized `QMessageBox` informing the user of the connection status. If the configured site string is empty, it prompts the user — in Italian, German, or English depending on `self.L` — to set up an archaeological site, offering the option to open the `pyArchInitDialog_Config` configuration dialog. If the user dismisses the prompt without confirming, no further action is taken.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` object and, if a site value is present, queries the database for all records matching that site, populating `DATA_LIST` and updating the UI fields, browse status, record counter, and disabling the site combo box. If no matching records are found for the configured site, a localized warning message is displayed in Italian, German, or English informing the user that the site does not exist in the current tab and advising them to disable the site filter or create the corresponding record. If the site setting string is empty, no action is taken.

##### charge_periodo_list(self)

*No description available.*
Placeholder method intended to load or populate a period list within the current tab or form. The method body contains no implementation (`pass`) and performs no operations in its current state. See implementation for any subclass overrides or future logic.

##### charge_fase_iniz_list(self)

*No description available.*
Placeholder method intended to load or populate the initial phase (`fase_iniz`) list within the interface. The method body contains no implementation and performs no operations in the current source. See implementation for any future or overridden behavior.

##### charge_fase_fin_list(self)

*No description available.*
Loads or populates the final phase list within the current context. This method is the counterpart to `charge_fase_iniz_list`, which handles the initial phase list. Implementation details are not documented in source.

##### generate_list_pdf(self)

Iterates over all entries in `self.DATA_LIST` and constructs a list of lists, where each inner list represents a single individual's osteological age estimation data. Each row contains the site name (with underscores replaced by spaces), individual number, and integer-cast values for a comprehensive set of skeletal age indicators, including pubic symphysis ranges, auricular surface ranges, dental wear ranges, endocranial and ectocranial suture scores and ranges, and vault and anterolateral suture scores and ranges. Returns the fully assembled `data_list`.

##### on_toolButtonPan_toggled(self)

*No description available.*
Slot method triggered when the pan tool button is toggled. It instantiates a `QgsMapToolPan` object bound to the `mapPreview` canvas and sets it as the active map tool, enabling pan interaction on the map preview widget.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog that allows the user to select sort fields and order type. If the record state check passes, the selected sort items are converted using `CONVERSION_DICT`, and the current data list is re-queried and reordered via `DB_MANAGER.query_sort` using the specified sort criteria. Upon completion, the browse status and sort status are updated, the record counter is reset to the first entry, and the fields and GUI are refreshed to reflect the newly sorted data.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle event for the GIS mode tool button, displaying a localized notification message to inform the user whether GIS mode has been activated or deactivated. The message is presented via a `QMessageBox.warning` dialog and is rendered in Italian, German, or English depending on the value of `self.L`. When `toolButtonGis` is checked, the message indicates that search results will be displayed on the GIS; when unchecked, it indicates that GIS display has been disabled.

##### on_toolButtonPreview_toggled(self)

*No description available.*
Handles the toggle event of `toolButtonPreview`, activating or deactivating the US (Stratigraphic Unit) preview mode. When the button is checked, a language-specific informational message is displayed (Italian, German, or English) notifying the user that US plan previews will be shown in the Plants section, then calls `loadMapPreview()` to load the preview. When the button is unchecked, `loadMapPreview(1)` is called directly without displaying a message, effectively disabling the preview mode.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current data list is non-empty and validating the existing data via `data_error_check()`. If the application is in browse mode (`"b"`) and the current record has been modified (detected by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the pending changes before proceeding. If the browse status is not already `"n"`, it transitions the GUI to new-record mode by updating status labels, clearing all fields via `empty_fields()`, resetting the record counter, and disabling relevant buttons via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behavior based on the current `BROWSE_STATUS`. In browse mode (`"b"`), it first checks for version conflicts on `deteta_table` via the concurrency manager — prompting the user to reload or overwrite if a conflict is detected — then, if data validation passes and the record has been modified, presents a localized confirmation dialog before persisting the update. In insert mode, it validates the data, attempts to insert a new record, and on success resets the form state, reloads the record list, and switches back to browse mode.

##### data_error_check(self)

Validates all form input fields for the current record by checking that required fields (site and individual number) are not empty and that all non-empty numeric fields contain integer values. Validation logic and warning message text are branched according to the active UI language (`self.L`), supporting Italian (`'it'`), German (`'de'`), and a default (English) locale. Returns an integer `test` value of `0` if all validations pass, or `1` if one or more validation errors were detected; a `QMessageBox` warning dialog is displayed for each individual violation encountered.

##### insert_new_rec(self)

*No description available.*
Collects and validates all field values from the form's UI controls (line edits and combo boxes), converting non-empty inputs to integers and mapping empty inputs to `None`. It then calls `self.DB_MANAGER.insert_values_deteta` with a newly generated record ID and all 56 collected field values — including site, individual number, skeletal age indicators, endocranial suture scores, vault and lateral measurements, and wear ranges — followed by `self.DB_MANAGER.insert_data_session` to persist the record. Returns `1` on success, or `0` on failure, displaying a localized warning `QMessageBox` if an `IntegrityError` (duplicate record) or any other exception is encountered.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first invoking `data_error_check()` and returning `1` immediately if input errors are detected. If no input errors exist and `records_equal_check()` indicates the record has been modified, it prompts the user with a localized warning dialog (Italian, German, or English, based on `self.L`) asking whether to save the changes, then delegates the user's response to `update_if()`. Returns `0` when no input errors are present, regardless of whether the record was modified.

##### on_pushButton_insert_row_rapporti_pressed(self)

*No description available.*
Event handler triggered when the "insert row" button associated with the *rapporti* section is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidget_rapporti'` as the target table identifier. This results in a new row being added to the `tableWidget_rapporti` widget.

##### on_pushButton_insert_row_inclusi_pressed(self)

Handles the press event of the "insert row inclusi" button by invoking `insert_new_row` with the target widget identifier `'self.tableWidget_inclusi'`. This adds a new row to the `tableWidget_inclusi` table widget. The method delegates all insertion logic to `insert_new_row`.

##### on_pushButton_insert_row_campioni_pressed(self)

Handles the press event of the "insert row campioni" button by invoking `insert_new_row` with the argument `'self.tableWidget_campioni'`. This triggers the insertion of a new row into the `tableWidget_campioni` table widget. The method follows the same pattern as `on_pushButton_insert_row_inclusi_pressed`, which performs the equivalent operation on `tableWidget_inclusi`.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button. If the current record state check does not return `1`, the method clears existing fields, reloads all records via `charge_records()`, and repopulates the fields, transitioning the interface to browse status (`"b"`). It then resets the record counter and current record pointer to the beginning of `DATA_LIST`, updates the sort label to its default state, and refreshes the GUI layout by calling `customize_GUI()`.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the data list when the "first record" button is pressed. If the record state check returns `1`, the GUI is refreshed via `customize_GUI()`; otherwise, the current fields are cleared, the record counters are reset to position `0`, the first record's data is loaded via `fill_fields(0)`, and the record counter display is updated accordingly. Any exception raised during this process is caught and presented to the user as a warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Handles the press event of the "last record" navigation button. If `check_record_state()` returns `1`, the GUI is customized via `customize_GUI()`; otherwise, the current fields are cleared, the record counters (`REC_TOT`, `REC_CORR`) are set to navigate to the final entry in `DATA_LIST`, and the fields are populated accordingly using `fill_fields()`. If an exception occurs during this process, a warning dialog is displayed to the user.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles navigation to the previous record when the corresponding button is pressed. If the current record state check passes, it decrements `REC_CORR` by one; if the resulting index is `-1`, it resets `REC_CORR` to `0` and displays a localized warning message (Italian, German, or English) indicating that the first record has been reached. Otherwise, it clears the current fields, populates them with the previous record's data via `fill_fields`, updates the record counter display, and finalizes the operation by calling `customize_GUI`.

##### on_pushButton_next_rec_pressed(self)

Advances the current record pointer (`REC_CORR`) to the next record in the dataset when the "next record" button is pressed. If the current record is already the last one (`REC_CORR >= REC_TOT`), the pointer is not advanced and a localized warning message is displayed (Italian, German, or English depending on `self.L`). If navigation succeeds, the form fields are cleared and repopulated with the next record's data via `empty_fields()` and `fill_fields()`, the record counter is updated, and `customize_GUI()` is called regardless of the outcome. If `check_record_state()` returns `1`, the navigation is skipped entirely.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by prompting the user with a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed, the method removes the record identified by `self.ID_TABLE` from `self.TABLE_NAME`, reloads the record list, and updates the UI state accordingly — resetting all record counters, lists, and fields if the database becomes empty, or navigating to the first record and refreshing the display if records remain. Upon completion, the sort status is reset to `"n"` and `self.customize_GUI()` is called regardless of the outcome.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "New Search" button by first checking the current record state; if a record is in an unsaved or modified state, no action is taken. Otherwise, it disables the search button, makes the site combo box editable, and, if the browse status is not already set to `"f"` (search mode), transitions the interface into search mode by updating the status label, clearing all fields, resetting the record counter, and resetting the sort label to its default unsorted state.

##### on_pushButton_search_go_pressed(self)

Executes a database search when the search button is pressed, first verifying that `BROWSE_STATUS` is set to `"f"` (search mode); if not, a localized warning message is displayed instructing the user to initiate a new search. When in search mode, it collects values from all relevant form fields and combo boxes — covering individual identifiers, pubic symphysis scores, auricular surface scores, dental wear, endocranial and ectocranial suture scores, and their respective ranges — into a dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database through `self.DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no records were found (restoring the current record view) or populates `self.DATA_LIST` with the results, updates the record counter, fills the form fields, and optionally triggers a GIS layer update; a localized summary message reporting the number of records found is displayed in all cases, after which `enable_button_search` and `customize_GUI` are called.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Upon successful completion, the browse status is set to `"b"` and the method returns `1`; if the update fails, it returns `0`.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the mapped table class, ordered by the table's ID column in ascending order. The results are stored directly in the instance attribute `self.DATA_LIST`, replacing any previously held data. This method uses a single ordered query via `self.DB_MANAGER.query_ordered` as a performance optimisation over a double-query pattern.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each cell, it retrieves the item's text value, collecting non-empty cells into a sub-list per row. Returns a list of sub-lists, where each sub-list represents a non-empty row of cell text values from the table.

##### tableInsertData(self, t, d)

*No description available.*
This method accepts two parameters, `t` and `d`, whose roles are not documented in the source. The method body contains only a `pass` statement, indicating no implementation is currently present.

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

Resets all input fields in the form to their default empty state. Clears all `QLineEdit` fields and sets all `QComboBox` fields to an empty string, covering site identification, individual number, pubic symphysis ranges, auricular surface ranges, dental wear ranges, endocranial and ectocranial suture selections and ranges, and vault and anterolateral suture selections and totals.

##### fill_fields(self, n)

*No description available.*
Populates all UI form fields with data from the record at index `n` in `self.DATA_LIST`, setting `self.rec_num` to the given index. For each field, `None` values are represented as empty strings in the corresponding `lineEdit` or `comboBox` widget; otherwise, the value is converted to a string and applied. If a `concurrency_manager` is present, the method additionally tracks the record's `version_number` and `id_det_eta`, updates the lock indicator with any active editing user information, and logs any errors encountered during version tracking via `QgsMessageLog`.

##### set_rec_counter(self, t, c)

Sets the total and current record counters for the UI. Assigns the provided values `t` and `c` to `self.rec_tot` and `self.rec_corr` respectively, then updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

Collects the current values from all form input widgets — including `lineEdit` fields and `comboBox` selections — related to skeletal age estimation indicators such as pubic symphysis, auricular surface, dental wear, endocranial sutures, vault sutures, and anterolateral sutures. For each widget, an empty string is treated as `None`; otherwise, the value is converted to a string. The collected values are assembled in a fixed-order list and assigned to `self.DATA_LIST_REC_TEMP`, along with the current site (`comboBox_sito`) and individual number (`lineEdit_nr_individuo`) as the first two entries.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by iterating over `TABLE_FIELDS` and evaluating each field name against the current record identified by `REC_CORR` in `DATA_LIST`. Each field value is retrieved dynamically via `eval` and converted to a string before being appended to `DATA_LIST_REC_CORR`, which is reset to an empty list at the start of each call. This method is called as part of `records_equal_check` to prepare the current record's data for comparison.

##### records_equal_check(self)

*No description available.*
Compares the current record's data against a temporary working copy by invoking `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate `DATA_LIST_REC_TEMP` and `DATA_LIST_REC_CORR` respectively. Returns `0` if the two lists are equal, indicating no changes have been made, or `1` if they differ, indicating the record has been modified.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### update_record(self)

*No description available.*
Attempts to persist changes to the current record by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `rec_toupdate()`. Returns `1` on success, or `0` if an exception occurs. On failure, the exception details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user based on the language setting `self.L` (`'it'`, `'de'`, or a fallback).

##### rec_toupdate(self)

*No description available.*
Retrieves the record designated for updating by delegating to `self.UTILITY.pos_none_in_list`, passing `self.DATA_LIST_REC_TEMP` as the argument. Returns the resulting value from that call, representing the record to be updated.

##### charge_id_us_for_individuo(self)

Iterates over all records in `self.DATA_LIST`, extracting the `sito` and `us` fields from each record to construct a search dictionary, then queries the database via `self.DB_MANAGER.query_bool` against the `"US"` table for each entry. Collects the resulting US records and extracts the `id_us` attribute from the first result of each query into a separate list. Returns the list of `id_us` values corresponding to all records in `self.DATA_LIST`.

##### on_pushButton_openSinfisi_pubica_pressed(self)

Opens the pubic symphysis age determination table based on the sex retrieved from the individual record (`sex_from_individuo_table()`). If no individual record exists or no sex is recorded, a warning dialog is displayed instructing the user to create the individual record and specify the sex first. If a valid sex is found, it calls `open_tables_det_eta` with argument `2` for male (`"Maschio"`) or `1` for female (`"Femmina"`); any other sex value triggers a warning indicating that age estimation via pubic symphysis is not possible.

##### on_pushButton_openSinfisi_pubica_2_pressed(self)

*No description available.*
Handles the press event of the `pushButton_openSinfisi_pubica_2` button by retrieving the sex of the individual from the individual record via `sex_from_individuo_table()`. If no result is found, a warning dialog is displayed instructing the user to first create the individual record and specify the sex. If a valid sex is found, it opens the corresponding age determination table by calling `open_tables_det_eta(4)` for males or `open_tables_det_eta(3)` for females; if the sex value is neither "Maschio" nor "Femmina", a warning is displayed indicating that age estimation based on the pubic symphysis is not possible.

##### sex_from_individuo_table(self)

*No description available.*
Retrieves the individual's sex record from the `SCHEDAIND` database table by querying with the current site (`sito`) and individual number (`nr_individuo`) values read from the corresponding UI controls (`comboBox_sito` and `lineEdit_nr_individuo`). Constructs a search dictionary with these two fields and delegates the query to `self.DB_MANAGER.query_bool`, returning the raw query result.

##### on_pushButton_SSPIA_pressed(self)

*No description available.*
Event handler triggered when the `pushButton_SSPIA` button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer argument `5`. No additional logic or return value is defined within this method.

##### on_pushButton_SSPIB_pressed(self)

*No description available.*
Slot method triggered when the SSPI B push button is pressed. It delegates execution to `open_tables_det_eta` with the integer argument `6`, which identifies the SSPI B-specific data set or table configuration. This method follows the same pattern as adjacent button handlers (`on_pushButton_SSPIA_pressed`, `on_pushButton_SSPIC_pressed`), each passing a distinct index to the same underlying method.

##### on_pushButton_SSPIC_pressed(self)

*No description available.*
Handler method triggered when the `pushButton_SSPIC` button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer value `7` as its argument. This follows the same pattern used by adjacent button handlers, which invoke `open_tables_det_eta` with sequential index values (`6`, `7`, `8`).

##### on_pushButton_SSPID_pressed(self)

*No description available.*
Event handler triggered when the `pushButton_SSPID` button is pressed. Delegates execution to `open_tables_det_eta` with the integer argument `8`. This method follows the same pattern as adjacent button handlers, each of which invokes `open_tables_det_eta` with a distinct numeric identifier.

##### on_pushButton_mascellare_superiore_pressed(self)

*No description available.*
Event handler triggered when the *mascellare superiore* (upper jaw) button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer argument `9` to identify the corresponding age determination table. No additional parameters are accepted and no value is returned.

##### on_pushButton_mascellare_inferiore_pressed(self)

*No description available.*
Slot method triggered when the *mascellare inferiore* (lower jaw/mandible) push button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer argument `10` to identify the corresponding age-determination table. This follows the same pattern used by adjacent button handlers, each of which invokes `open_tables_det_eta` with a distinct numeric identifier.

##### on_pushButton_suture_endocraniche_pressed(self)

*No description available.*
Event handler triggered when the *suture endocraniche* (endocranial sutures) button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer argument `11` to identify the corresponding age determination table. This method follows the same pattern used by adjacent button handlers for other anatomical criteria.

##### on_pushButton_suture_ectocraniche_pressed(self)

*No description available.*
Handler method triggered when the ectocranial sutures button is pressed. It delegates execution to `open_tables_det_eta`, passing the integer value `12` as the argument to identify the corresponding age determination table. This call opens the image visualization window associated with ectocranial suture data.

##### open_tables_det_eta(self, n)

*No description available.*
Opens an `ImageViewer` dialog displaying a reference anthropological image for age determination, selected according to the integer parameter `n`. Each value of `n` (1–12) maps to a specific reference table image, including female and male pubic symphysis charts, Kimmerle tables, auricular surface charts (SSPIA–SSPID), upper and lower jaw dental wear tables, and endocranial and ectocranial suture tables. If the specified image file cannot be loaded, a warning dialog is displayed with the corresponding error message.

##### on_pushButton_I_fase_pressed(self)

*No description available.*
Handles the press event for the Phase I button by first querying the individual's sex via `sex_from_individuo_table()`. If no individual record exists or no sex is recorded, a warning dialog is displayed instructing the user to create the individual record and specify the sex before using pubic symphysis-based age estimation. If a valid sex ("Maschio" or "Femmina") is found, the corresponding minimum and maximum age range values are retrieved from the Suchey-Brooks dictionaries, populated into `lineEdit_sinf_min` and `lineEdit_sinf_max`, and the record is saved by calling `on_pushButton_save_pressed()`.

##### on_pushButton_II_fase_pressed(self)

*No description available.*
Handles the press event for the Phase II button in the pubic symphysis age estimation workflow. It queries the individual's sex via `sex_from_individuo_table()`; if no result is found, it displays a warning dialog instructing the user to first create the individual record and specify the sex. If a valid sex ("Maschio" or "Femmina") is found, it retrieves the corresponding minimum and maximum age range values from `DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks` or `DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks` at index `2`, populates `lineEdit_sinf_min` and `lineEdit_sinf_max` with those values, and triggers `on_pushButton_save_pressed()`; if the sex value is neither of the two expected strings, a warning is displayed indicating that age estimation cannot be performed.

##### on_pushButton_III_fase_pressed(self)

*No description available.*
Handles the press event for the Phase III button in the pubic symphysis age estimation interface. It queries the individual's sex via `sex_from_individuo_table()`; if no record is found, it displays a warning instructing the user to first create the individual record and specify the sex. If a valid sex ("Maschio" or "Femmina") is found, it retrieves the corresponding minimum and maximum age range values from phase index `3` of either `DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks` or `DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks`, populates `lineEdit_sinf_min` and `lineEdit_sinf_max` accordingly, and then calls `on_pushButton_save_pressed()`; if the sex value is neither of the two expected strings, a warning is displayed indicating that age estimation cannot be performed.

##### on_pushButton_IV_fase_pressed(self)

*No description available.*
Handles the press event for the Phase IV button in the pubic symphysis age estimation workflow. It queries the individual's sex via `sex_from_individuo_table()`; if no result is found, it displays a warning instructing the user to first create the individual record and specify the sex. If a valid sex ("Maschio" or "Femmina") is found, it retrieves the corresponding minimum and maximum age range values from phase index 4 of either `DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks` or `DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks`, populates `lineEdit_sinf_min` and `lineEdit_sinf_max` with those values, and then triggers `on_pushButton_save_pressed()`; if the sex value is neither of the two expected strings, a warning is displayed indicating that age estimation cannot be performed.

##### on_pushButton_V_fase_pressed(self)

*No description available.*
Handles the press event for the Phase V button in the pubic symphysis age estimation workflow. It queries the individual's sex via `sex_from_individuo_table()`; if no record is found, a warning dialog is displayed instructing the user to first create the individual record and specify the sex. If a valid sex of `"Maschio"` or `"Femmina"` is found, the corresponding minimum and maximum age range values are retrieved from phase index `5` of either `DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks` or `DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks`, written to `lineEdit_sinf_min` and `lineEdit_sinf_max`, and saved by invoking `on_pushButton_save_pressed()`; any other sex value triggers a warning indicating that age estimation cannot be performed.

##### on_pushButton_VI_fase_pressed(self)

*No description available.*
Handles the press event for the "VI fase" button by first querying the individual's record via `sex_from_individuo_table()`. If no record is found, a warning dialog is displayed instructing the user to create the individual record and specify the sex before using pubic symphysis-based age estimation. If a valid sex ("Maschio" or "Femmina") is found, the method retrieves the corresponding minimum and maximum age range values from phase 6 of the Suchey-Brooks dictionaries (`DIZ_VALORI_SINFISI_MASCHIO_Suchey_Brooks` or `DIZ_VALORI_SINFISI_FEMMINA_Suchey_Brooks`), populates `lineEdit_sinf_min` and `lineEdit_sinf_max` with those values, and triggers `on_pushButton_save_pressed()`; if the sex value is neither "Maschio" nor "Femmina", a warning is displayed indicating that age estimation cannot be performed.

##### on_pushButton_f_1_pressed(self)

*No description available.*
Handles the press event for the female button `f_1` by retrieving the minimum and maximum range values associated with key `1` from the `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle` dictionary. The extracted `val_min` and `val_max` values are then written as strings into the `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` line edit fields, respectively. Finally, it triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_f_2_pressed(self)

*No description available.*
Handles the press event for the female button corresponding to category 2. Retrieves the minimum and maximum range values from index `2` of `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle` and populates `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` with those values as strings. Immediately triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_f_3_pressed(self)

*No description available.*
Handles the press event for the female button corresponding to index 3. Retrieves the minimum and maximum range values from `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle` at key `3`, then populates `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` with those values as strings. Finally, triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_f_4_pressed(self)

*No description available.*
Handles the press event for the female phase 4 button by retrieving the minimum and maximum age range values from index `4` of `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle`. It populates `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` with the corresponding minimum and maximum values respectively. After updating the fields, it triggers `on_pushButton_save_pressed` to persist the changes.

##### on_pushButton_f_5_pressed(self)

Handles the press event of the female push button corresponding to index 5. Retrieves the minimum and maximum range values from `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle` at key `5`, then populates `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` with the respective string representations of those values. Finally, triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_f_6_pressed(self)

Handles the press event of the `pushButton_f_6` button by retrieving the minimum and maximum values stored at index `6` of `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle`. It populates `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` with the retrieved minimum and maximum values respectively. Finally, it triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_f_7_pressed(self)

*No description available.*
Handles the press event for female button 7 by retrieving the minimum and maximum range values stored at key `7` of `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle`. It populates `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` with the corresponding minimum and maximum values respectively. Finally, it triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_f_8_pressed(self)

*No description available.*
Handles the press event for the female phase 8 button by retrieving the minimum and maximum age range values from index 8 of `DIZ_VALORI_SINFISI_2_FEMMINA_Kimmerle`. The retrieved values are then written to the `lineEdit_sinf_min_2` and `lineEdit_sinf_max_2` text fields respectively. Finally, it triggers `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_sup_aur_pressed(self)

*No description available.*
Handles the press event of the `pushButton_sup_aur` button by reading the current integer values from the four combo boxes (`comboBox_SSPIA`, `comboBox_SSPIB`, `comboBox_SSPIC`, `comboBox_SSPID`) and constructing a list used as a lookup key. It retrieves the corresponding minimum and maximum values from two dictionaries, `DIZ_VALORI_SUP_AUR` and `DIZ_VALORI_SUP_AUR_2`, and populates the four line edit fields (`lineEdit_sup_aur_min`, `lineEdit_sup_aur_max`, `lineEdit_sup_aur_min_2`, `lineEdit_sup_aur_max_2`) with the retrieved values. Finally, it invokes `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_ms_sup_12_18_pressed(self)

Sets the minimum and maximum supervisor values in the `lineEdit_ms_sup_min` and `lineEdit_ms_sup_max` fields to `'12'` and `'18'` respectively. After updating the fields, it immediately triggers `on_pushButton_save_pressed()` to persist the changes.

##### on_pushButton_ms_sup_16_20_pressed(self)

Sets the minimum superior millisecond value to `'16'` and the maximum superior millisecond value to `'20'` by updating `lineEdit_ms_sup_min` and `lineEdit_ms_sup_max` respectively. After applying these preset values, it immediately invokes `on_pushButton_save_pressed` to persist the changes.

##### on_pushButton_ms_sup_18_22_pressed(self)

*No description available.*
Sets the minimum superior MS value to `'18'` and the maximum superior MS value to `'22'` by updating the text of `lineEdit_ms_sup_min` and `lineEdit_ms_sup_max` respectively. After updating both fields, it immediately invokes `on_pushButton_save_pressed()` to persist the new values.

##### on_pushButton_ms_sup_20_24_pressed(self)

*No description available.*
Sets the minimum superior MS value to `'20'` and the maximum superior MS value to `'24'` by updating the text of `lineEdit_ms_sup_min` and `lineEdit_ms_sup_max` respectively. After updating both fields, it invokes `on_pushButton_save_pressed` to persist the new values.

##### on_pushButton_ms_sup_24_30_pressed(self)

*No description available.*
Sets the minimum superior threshold value to `'24'` and the maximum superior threshold value to `'30'` by updating `lineEdit_ms_sup_min` and `lineEdit_ms_sup_max` respectively. After updating both fields, it immediately invokes `on_pushButton_save_pressed()` to persist the changes. This method serves as a button handler for selecting the 24–30 superior range preset.

##### on_pushButton_ms_sup_30_35_pressed(self)

*No description available.*
Sets the superior minimum value field (`lineEdit_ms_sup_min`) to `'30'` and the superior maximum value field (`lineEdit_ms_sup_max`) to `'35'`. After updating both fields, it immediately invokes `on_pushButton_save_pressed()` to persist the changes. This method serves as the handler for the corresponding button press event targeting the 30–35 range.

##### on_pushButton_ms_sup_35_40_pressed(self)

*No description available.*
Sets the minimum superior millisecond value to `'35'` and the maximum superior millisecond value to `'40'` by writing these values to `lineEdit_ms_sup_min` and `lineEdit_ms_sup_max` respectively. After updating both fields, it immediately invokes `on_pushButton_save_pressed()` to persist the changes.

##### on_pushButton_ms_sup_40_50_pressed(self)

*No description available.*
Sets the superior minimum value field (`lineEdit_ms_sup_min`) to `'40'` and the superior maximum value field (`lineEdit_ms_sup_max`) to `'50'`. After updating both fields, it immediately triggers `on_pushButton_save_pressed()` to persist the new values. This method serves as a preset handler, activated when the corresponding button is pressed to apply the 40–50 superior range configuration.

##### on_pushButton_ms_inf_12_18_pressed(self)

Sets the inferior minimum value to `'12'` and the inferior maximum value to `'18'` by populating `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max` respectively. After updating both fields, it invokes `on_pushButton_save_pressed` to persist the changes.

##### on_pushButton_ms_inf_16_20_pressed(self)

Sets the minimum inference value to `'16'` and the maximum inference value to `'20'` by populating `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max` respectively. After updating both fields, it immediately invokes `on_pushButton_save_pressed` to persist the new values.

##### on_pushButton_ms_inf_18_22_pressed(self)

Sets the minimum and maximum inference range fields to `'18'` and `'22'`, respectively, by calling `setText` on `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max`. After updating both fields, it invokes `on_pushButton_save_pressed` to persist the new values.

##### on_pushButton_ms_inf_20_24_pressed(self)

Sets the minimum inference value to `'20'` and the maximum inference value to `'24'` by updating `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max` respectively. After applying these values, it immediately invokes `on_pushButton_save_pressed` to persist the changes.

##### on_pushButton_ms_inf_24_30_pressed(self)

Sets the minimum inference value to `'24'` and the maximum inference value to `'30'` by populating `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max` respectively. After updating both fields, it immediately invokes `on_pushButton_save_pressed()` to persist the changes.

##### on_pushButton_ms_inf_30_35_pressed(self)

Sets the minimum and maximum inference range fields (`lineEdit_ms_inf_min` and `lineEdit_ms_inf_max`) to `'30'` and `'35'`, respectively. After updating the fields, it immediately invokes `on_pushButton_save_pressed()` to persist the new values.

##### on_pushButton_ms_inf_35_40_pressed(self)

*No description available.*
Sets the minimum inference millisecond value to `'35'` and the maximum inference millisecond value to `'40'` by writing these strings to `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max` respectively. After updating both fields, it immediately invokes `on_pushButton_save_pressed()` to persist the new range values.

##### on_pushButton_ms_inf_40_45_pressed(self)

Sets the minimum and maximum inference time range fields to `'40'` and `'45'` respectively by calling `setText` on `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max`. After updating the fields, it immediately invokes `on_pushButton_save_pressed` to persist the new values.

##### on_pushButton_ms_inf_45_55_pressed(self)

*No description available.*
Sets the minimum inference range value to `'45'` and the maximum inference range value to `'55'` by populating `lineEdit_ms_inf_min` and `lineEdit_ms_inf_max` respectively. After updating both fields, it immediately triggers `on_pushButton_save_pressed()` to persist the new range configuration.

##### on_pushButton_range_sut_end_pressed(self)

*No description available.*
Handles the press event of the range SUT end button by computing the arithmetic mean of all non-empty endocranial combobox values (spanning cranial regions Id through Xs). The computed mean is then mapped to a predefined age range tuple according to fixed threshold intervals (0.400–1.599 → 15–40, 1.600–2.599 → 30–60, 2.600–2.999 → 35–65, 3.000–3.999 → 45–75, ≥4.000 → 50–80), and the resulting minimum, maximum, and mean values are written to the corresponding `lineEdit_endo_min`, `lineEdit_endo_max`, and `lineEdit_valore_medio` fields. Finally, the method invokes `on_pushButton_save_pressed` to persist the updated values.

##### on_pushButton_calcola_volta_ant_lat_clicked(self)

*No description available.*
Slot triggered when the corresponding button is clicked. It computes two independent age range estimates: one based on the sum of integer values from up to seven `comboBox_volta_*` combo boxes, and one based on the sum of integer values from five `comboBox_lat_*` combo boxes (indices 6–10). The resulting minimum and maximum age bounds for each calculation are written to their respective `lineEdit_volta_min`/`lineEdit_volta_max` and `lineEdit_ant_lat_min`/`lineEdit_ant_lat_max` fields using predefined score-to-range lookup tables; if all relevant combo boxes are empty for a given group, the corresponding fields are cleared. The method concludes by invoking `on_pushButton_save_pressed`.

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode (`'w'`) and writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are explicitly cast to `str` before use. This method performs no return value or exception handling as shown in the source.

