# tabs/Schedaind.py

## Overview

This file contains 57 documented elements.

## Classes

### pyarchinit_Schedaind

`pyarchinit_Schedaind` is a QGIS `QDialog` subclass that implements the Individual Record form (`Scheda Individuo`) within the PyArchInit archaeological data management plugin, providing a full CRUD interface for records stored in `individui_table`. The form manages osteological and burial data fields including site, area, stratigraphic unit, individual number, sex estimation, age estimation, skeletal position, orientation, and associated structure references. It supports multilingual display (Italian, English, German, French, Spanish, Portuguese, Arabic, Catalan, Romanian, Greek, and others), record browsing and sorting, database connection management, GIS integration via `Pyarchinit_pyqgis`, and PDF export of individual sheets and indexes.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the dialog by calling the parent constructor, setting up the UI, and applying the current theme along with a theme toggle button. Establishes the initial widget state by hiding the export and secondary dock widgets, initializing `currentLayerId` to `None`, and attempting a database connection — displaying a warning message if the connection fails. Configures signal-slot connections for the `lineEdit_individuo` field, populates form fields, and invokes `set_sito()`, `msg_sito()`, and `numero_invetario()` to complete the initial form state.

##### numero_invetario(self)

*No description available.*
Automatically populates the `lineEdit_individuo` field with an inventory number when the field is empty. It iterates over `DATA_LIST`, collecting each record's `nr_individuo` value into a list, incrementing the last appended value by one after each insertion, and sorting the list in ascending order on each iteration. After processing all records, the field is set to the string representation of the final element in the sorted list.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all listed controls to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the general record-navigation and management controls as a group.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` object, detecting whether the target database is SQLite, and initialising the database manager via `get_db_manager`. If the connection succeeds, it retrieves the database username to update the concurrency manager, then loads records from the database; if records exist, it initialises browse state and populates the UI fields, otherwise it displays a localised welcome message (Italian, German, or English) and opens a new record form. If the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar indicating the failure and advising a restart or bug report.

##### customize_GUI(self)

*No description available.*
Configures the graphical user interface by setting specific combo boxes to an editable state. Applies editable mode (value `1`) to four combo box widgets: `comboBox_sigla_struttura`, `comboBox_nr_struttura`, `comboBox_area`, and `comboBox_us` via the `setComboBoxEditable` method.

##### loadMapPreview(self, mode)

*No description available.*
Loads a map preview within the interface, with an optional `mode` parameter that defaults to `0`. The method body contains no implemented logic in the provided source (`pass`).

> **Note:** The full implementation details are not documented in the source.

##### charge_list(self)

Populates all combo boxes in the form with data retrieved from the database and the thesaurus, using the current QGIS user locale to filter language-specific entries. The site list (`comboBox_sito`) is loaded directly from the `site_table` database table, while all remaining combo boxes (`comboBox_area`, `comboBox_disturbato`, `comboBox_completo`, `comboBox_in_connessione`, `comboBox_posizione_cranio`, `comboBox_posizione_scheletro`, `comboBox_orientamento_asse`, `comboBox_arti_superiori`, `comboBox_arti_inferiori`) are populated by querying the `PYARCHINIT_THESAURUS_SIGLE` table using typology codes specific to `individui_table`. All lists are sorted alphabetically before being added to their respective combo boxes.

##### msg_sito(self)

Displays a localized informational message box indicating the connection status of the currently selected archaeological site by comparing the value in `comboBox_sito` against the site configured in the active `Connection`. If the configured site string is empty, a warning dialog is shown (in Italian, German, or English depending on `self.L`) offering the user the option to configure a site via `pyArchInitDialog_Config`, or to cancel and view all records. If the user confirms, the configuration dialog is loaded and executed via `charge_list()` and `exec()`.

##### set_sito(self)

*No description available.*
Retrieves the configured site (`sito`) value from a `Connection` object and queries the database manager for all records matching that site using `query_bool`. If matching records are found, the method populates `DATA_LIST`, initialises record counters, fills the form fields, sets the browse status, and disables the site combo box; if no records are found, a localised informational message is displayed in Italian, German, or English depending on `self.L`. Any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### charge_struttura_nr(self)

*No description available.*
Queries the database for all `TOMBA` records matching the currently selected site (`comboBox_sito`), then extracts and deduplicates the `nr_struttura` values into a sorted list. The method clears and repopulates `comboBox_nr_struttura` with the resulting structure numbers, removing any empty entries before sorting. Depending on the current browse status, it either clears the combo box edit text (in "Find/Trova/Finden" mode) or attempts to restore the `nr_struttura` value from the current record in `DATA_LIST` (in "Use/Usa/Aktuell/Current" mode).

##### charge_struttura_list(self)

*No description available.*
Queries the database for `TOMBA` records matching the currently selected site (`comboBox_sito`), then extracts and deduplicates the `sigla_struttura` values from the results. The resulting list is sorted, stripped of empty entries, and used to populate `comboBox_sigla_struttura`. Depending on the current browse status, the combo box edit text is either cleared (in "Trova"/"Finden"/"Find" mode) or set to the `sigla_struttura` value of the current record in the data list.

##### charge_periodo_list(self)

*No description available.*
This method is defined within the class but contains no implemented logic in the provided source. Its body consists solely of a `pass` statement, indicating a placeholder or stub. Refer to the implementation or subclass for functional details.

##### charge_fase_iniz_list(self)

*No description available.*
Loads or populates the initial phase list used within the application. This method is part of a group of related list-loading methods, alongside `charge_periodo_list` and `charge_fase_fin_list`, which handle period and final phase lists respectively. See implementation for details on the data source and population logic.

##### charge_fase_fin_list(self)

*No description available.*
Loads or populates the final phase list within the current context. This method is the counterpart to `charge_fase_iniz_list`, which handles the initial phase list. Implementation details are not documented in source.

##### generate_list_pdf(self)

*No description available.*
Iterates over `self.DATA_LIST` and constructs a two-dimensional list where each inner list represents a single record's fields as strings. The extracted fields include site (`sito`, with underscores replaced by spaces), area, stratigraphic unit (`us`), individual number, scheduling date, recorder, sex, minimum and maximum age, age class, observations, structure code and number, completeness, disturbance, connection status, skeleton length, skeleton position, skull position, upper and lower limb positions, axis orientation, and azimuth orientation. Returns the resulting `data_list`.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available `SORT_ITEMS`, allowing the user to select sort fields and order type. If the record state check does not return `1`, it converts the selected items using `CONVERSION_DICT`, queries the database manager via `query_sort` using the current record IDs, and replaces `DATA_LIST` with the sorted results. After sorting, it resets the browse status, updates the record counter and status labels, and refreshes the displayed fields to reflect the first record in the sorted list.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle event of `toolButtonGis`, displaying a localized informational message box to notify the user whether GIS mode has been activated or deactivated. The message content is determined by the current language setting (`self.L`), with distinct messages provided for Italian (`'it'`), German (`'de'`), and a default English fallback. When the button is checked, a message indicates that search results will be displayed on the GIS; when unchecked, a message indicates that GIS display has been disabled.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by preparing the form to accept a new entry. If the current data list is non-empty and the browse status is not already in new-record mode (`"n"`), it performs a data integrity check and verifies whether any unsaved modifications exist before proceeding. Depending on whether the current site (`comboBox_sito`) matches the configured site set, it clears the form fields (either preserving or resetting the site selection), updates UI state labels, configures the editability and enabled state of relevant input controls, resets sort and browse status indicators, and invokes `numero_invetario()` to assign a new inventory number.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event by branching logic based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it performs a data validation check and, if the record has been modified, displays a localized confirmation dialog (Italian, German, or English) before invoking `update_if` to persist the changes; if no modifications are detected, a localized warning is shown instead. Outside browse mode, it validates the data and attempts to insert a new record via `insert_new_rec`, then refreshes the UI state, record counters, combo box configurations, and field display upon success, or shows a localized data entry error warning upon failure.

##### data_error_check(self)

*No description available.*
Validates required form fields and data types before a record is saved, using an `Error_check` instance to perform individual field checks. It verifies that the site (`comboBox_sito`) and individual number (`lineEdit_individuo`) fields are not empty, and conditionally validates the area field length and the skeleton length or individual number fields for numeric/float format depending on the active language (`self.L`). Returns an integer `test` value of `0` if all checks pass, or `1` if one or more validation errors were detected, displaying a localized `QMessageBox` warning for each failure in Italian (`it`), German (`de`), or English (default).

##### insert_new_rec(self)

*No description available.*
Collects field values from the form's UI controls and inserts a new individual (anthropological) record into the database by invoking `DB_MANAGER.insert_values_ind` with a newly generated ID and all associated attributes, including site, area, stratigraphic unit, individual number, scheduling data, sex, age range, age class, observations, structural references, skeletal completeness/disturbance/connection status, skeleton length, skeletal and cranial position, limb positions, and orientation data. The assembled record is then committed to the session via `DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` if an exception occurs, displaying a localized warning dialog (Italian, German, or English) distinguishing integrity constraint violations from other errors.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If no data errors are found and the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompting the user to save changes, then delegates the response to `update_if()`. Returns `1` if data entry errors exist, or `0` if no errors are present.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the "View All" button press event by loading and displaying the complete set of records. If the record state check passes, the method clears current field values, reloads all records, and repopulates the fields, setting the browse status to `"b"` and updating the status label accordingly. It also resets the record counters so that navigation begins from the first record in `DATA_LIST`, and clears any active sort indicator on `label_sort`.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Navigates to the first record in the current dataset when triggered by the corresponding button press. If the record state check returns `1`, no action is taken; otherwise, it clears the current fields, resets the record counters so that `REC_CORR` is set to `0` and `REC_TOT` reflects the total number of items in `DATA_LIST`, then populates the fields with the first record (index `0`). The record counter display is updated accordingly to reflect position `1` of the total record count.

##### on_pushButton_last_rec_pressed(self)

Navigates to the last record in the dataset when the corresponding button is pressed. If `check_record_state()` does not return `1`, it clears the current fields, sets `REC_TOT` and `REC_CORR` to reflect the final position in `DATA_LIST`, populates the fields with the last record's data, and updates the record counter accordingly. Any exceptions raised during this process are silently suppressed.

##### on_pushButton_prev_rec_pressed(self)

Handles the "previous record" button press event by navigating to the preceding record in the dataset. If the current record state check passes, no action is taken; otherwise, `REC_CORR` is decremented, and if it would fall below zero, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) informing the user that the first record has been reached. If a valid previous record exists, the form fields are cleared, repopulated with the data at the new index, and the record counter display is updated accordingly.

##### on_pushButton_next_rec_pressed(self)

Advances the current record pointer (`REC_CORR`) to the next record in the dataset when the "next record" button is pressed. If the pointer would exceed the total number of records (`REC_TOT`), it is rolled back and a localized warning message is displayed (Italian, German, or English) informing the user they are already at the last record. Otherwise, the form fields are cleared and repopulated with the data for the new current record, and the record counter display is updated accordingly.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the user confirms, the record identified by `self.ID_TABLE` is removed, the data list is reloaded, and the UI state (fields, record counter, status label, and sort status) is updated accordingly. If the deletion results in an empty dataset, all internal data lists and counters are reset to zero and the form fields are cleared; otherwise, navigation is repositioned to the first record in browse mode.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by transitioning the form into search mode (`BROWSE_STATUS = "f"`). Depending on whether the current site (`comboBox_sito`) matches the configured site set, it either clears only non-site fields via `empty_fields_nosite()` or performs a full field reset via `empty_fields()` along with reloading the combo box list via `charge_list()`. In both cases, search-related UI elements are reconfigured (combo box editability and enabled states, status label, record counter, and sort label) to reflect the new search state.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Slot triggered when the search execution button is pressed. If the current browse status is not in search mode (`"f"`), a localized warning message is displayed instructing the user to initiate a new search first; otherwise, the method collects field values from the form (site, area, US, individual, dates, skeletal measurements, and other attributes) into a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database through `DB_MANAGER.query_bool`. Depending on the query result, it either displays a localized warning if no criteria were set or no records were found, or populates `DATA_LIST` with the returned records, updates the browse status and record counter, fills the form fields, and optionally triggers GIS layer loading via `pyQGIS`; the search button is re-enabled upon completion regardless of outcome.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's confirmation dialog response. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying the database with either a default ascending sort on `ID_TABLE` or a custom sort order depending on `SORT_STATUS`. Returns `1` if the update and data reload succeed, `0` if the update fails, and updates `BROWSE_STATUS` and the status label accordingly.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the mapped table class, ordered by the table's ID column in ascending order. The results are stored directly in the instance attribute `self.DATA_LIST`, replacing any previously held data. This method uses a single ordered query via `self.DB_MANAGER.query_ordered` as a performance optimisation over a double-query pattern.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves it to the corresponding table attribute on the instance (stripping a `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each cell, it retrieves the item's text value, collecting non-empty cells into a sub-list per row. Returns a list of sub-lists, where each sub-list represents a row containing only the non-`None` cell text values from that row.

##### tableInsertData(self, t, d)

*No description available.*
Accepts a table name `t` and a data parameter `d`, but performs no operations in its current state as the entire implementation body is commented out.

The commented-out implementation indicates the method was intended to clear the specified table's contents, remove its existing rows, sort the provided data list, and repopulate the table by inserting new rows and setting each cell with a corresponding `QTableWidgetItem`. The method currently contains only a `pass` statement and is effectively a no-op.

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields_nosite(self)

Clears and resets all form fields related to a record entry, excluding the site field. Combo box fields are reset to an empty string using `setEditText("")`, while line edit and text edit fields are cleared using their respective `clear()` methods. The fields reset include area, US, data schedatura, schedatore, individuo, sesso, age range and class, observations, structure details, skeleton attributes, and orientation data.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to an empty state. ComboBox fields are cleared by setting their editable text to an empty string, while line edit and text edit fields are cleared using their respective `clear()` methods. The fields reset include site, area, stratigraphic unit, scheduling date, scheduler, individual, sex, age range, age class, observations, structure details, skeleton completeness and disturbance status, skeletal measurements, positional attributes, and orientation data.

##### fill_fields(self, n)

*No description available.*
Populates all form fields in the UI with data from the record at index `n` in `DATA_LIST`, storing the index in `self.rec_num`. Each UI widget (combo boxes, line edits, and text edits) is populated with the corresponding attribute of the selected record, covering fields such as site, area, stratigraphic unit, individual number, scheduling date, sex, age range, age class, observations, structure details, skeletal completeness/disturbance/connection status, skeleton length, skeletal position attributes, and orientation data. If an exception occurs during the population process, a warning dialog is displayed to the user via `QMessageBox`.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counters by assigning the provided values to the instance attributes `rec_tot` and `rec_corr` respectively. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects and assembles the current values from all form input widgets — including combo boxes, line edits, and a text edit — into the `DATA_LIST_REC_TEMP` list, which represents a temporary record of the currently displayed data. Before building the list, it checks whether the `lineEdit_lunghezza_scheletro` field is empty, assigning `None` if so or its text value otherwise. The resulting list contains 23 ordered fields covering site, area, stratigraphic unit, individual details, scheduling metadata, biological profile data, and skeletal position attributes.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by iterating over `TABLE_FIELDS` and extracting the corresponding attribute values from the current record in `DATA_LIST`, identified by the `REC_CORR` index. Each extracted value is converted to a string and appended to the freshly initialised `DATA_LIST_REC_CORR` list. This method is called as part of `records_equal_check` to capture the stored record state for comparison purposes.

##### records_equal_check(self)

*No description available.*
Compares the current record (`DATA_LIST_REC_CORR`) against a temporary record (`DATA_LIST_REC_TEMP`) by first invoking `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate both lists. Returns `0` if the two lists are equal, or `1` if they differ.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### update_record(self)

*No description available.*
Attempts to persist the current record's changes to the database by calling `DB_MANAGER.update` with the current record's ID, table fields, and the data returned by `rec_toupdate()`, returning `1` on success. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory. A localized warning dialog is then displayed to the user in Italian (`'it'`), English, or German (`'de'`) depending on the value of `self.L`, and the method returns `0`.

##### rec_toupdate(self)

*No description available.*
Retrieves the record designated for update by delegating to `self.UTILITY.pos_none_in_list`, passing `self.DATA_LIST_REC_TEMP` as the argument. The result, stored in `rec_to_update`, is returned directly to the caller. Commented-out debug statements indicate this method was previously used to write the result to a file for inspection purposes.

##### charge_id_us_for_individuo(self)

*No description available.*
Iterates over `self.DATA_LIST` and, for each record, constructs a search dictionary using the record's `sito`, `area`, and `us` fields, then queries the database manager via `query_bool` against the `"SCHEDAIND"` table to retrieve matching stratigraphic unit (`us`) entries. The results are collected and subsequently reduced to a flat list containing the `us` value from the first matching result of each query. Returns this list of `us` identifiers as `data_list_id_us`.

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode (`'w'`) and writes the string representation of `message` to it, then closes the file. This method creates or overwrites the target file with the provided message content.

##### on_pushButton_print_pressed(self)

Handles the print button press event by generating and exporting PDF documents based on the state of the UI checkboxes (`checkBox_s_us`, `checkBox_e_us`, `checkBox_e_foto_t`, `checkBox_e_foto`) and the active interface language (`self.L`). Depending on the language (`'it'`, `'en'`, or `'de'`), it invokes the appropriate PDF builder methods to produce individual/stratigraphic unit sheets, index lists, and photo lists with or without thumbnails. A `QMessageBox` notification is displayed upon successful export or when an error or empty data condition is encountered.

##### setPathpdf(self)

*No description available.*
Opens a file dialog prompting the user to select an existing PDF file, starting from the directory defined by `self.PDFFOLDER`. If a valid file path is selected, the method populates `self.lineEdit_pdf_path` with the chosen path and persists the value using `QgsSettings`.

##### openpdfDir(self)

Opens the application's PDF output directory in the operating system's default file manager. The target path is constructed by combining the `PYARCHINIT_HOME` environment variable with the subdirectory `pyarchinit_PDF_folder`. The method dispatches the appropriate system call based on the current platform: `os.startfile` on Windows, `open` on macOS (Darwin), and `xdg-open` on all other systems.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path. The method resolves the target directory path and launches it in the native file manager using `os.startfile` on Windows, `open` on macOS (Darwin), or `xdg-open` on Linux and other platforms.

##### check_for_updates(self)

Check if current record has been modified by others

