# tabs/Periodizzazione.py

## Overview

This file contains 55 documented elements.

## Classes

### pyarchinit_Periodizzazione

`pyarchinit_Periodizzazione` is a QDialog-based form class within the PyArchInit QGIS plugin that provides a user interface for managing archaeological periodization records stored in the `periodizzazione_table` database table. It supports full CRUD operations (create, read, update, delete), record navigation, sorting, and search functionality against the `PERIODIZZAZIONE` mapper class, with fields covering site, period, phase, initial and final chronology, description, extended dating, and period code. The class adapts its labels, status messages, and field conversion dictionaries to the active QGIS locale, supporting Italian, English, German, Spanish, French, Arabic, Catalan, Romanian, Portuguese, Greek, and a default English fallback, and additionally provides PDF export, QGIS vector layer visualization, and optional GPT-assisted content suggestions.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the form widget by calling the parent constructor and setting up core instance attributes, including the QGIS interface reference (`iface`) and a `Pyarchinit_pyqgis` instance. Builds the UI via `setupUi`, applies the current theme using `ThemeManager`, and adds a theme toggle button to the form. Completes initialization by resetting `currentLayerId` to `None`, attempting a database connection, and invoking `fill_fields`, `set_sito`, `msg_sito`, and `read_epoche` to populate and configure the form's initial state.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. The parameter `n` is passed directly to `setEnabled`, controlling whether these buttons are interactive or disabled.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the main set of record-management and navigation controls as a group.

##### on_pushButton_connect_pressed(self)

Handles the connect button press event by establishing a database connection using a `Connection` object and retrieving the appropriate database manager via `get_db_manager`. If the connection succeeds, it loads records from the database, updates the concurrency manager's username, and either populates the UI fields and record counters (if data exists) or displays a localized welcome message and initializes a new record (if the database is empty). If the connection or any subsequent operation raises an exception, a localized warning message is pushed to the QGIS message bar indicating the failure and advising a restart or bug report.

##### read_epoche(self)

*No description available.*
Reads a CSV file referenced by `self.CSV` and populates `self.comboBox_per_estesa` with formatted period entries derived from the `Periodo`, `Evento`, and `Anno/Secolo` columns. Each year or year range string is parsed to extract numeric start and end values, with support for BCE/CE era markers (e.g., `a.C.`, `BCE`, `d.C.`) and slash-delimited or hyphen-delimited intervals; the resulting numeric pair is stored as associated item data in the combo box. The method preserves the previously selected combo box value where possible and connects the `currentIndexChanged` signal to `self.update_anni`.

##### update_anni(self, index)

*No description available.*
Updates the chronological range fields based on the selected item in the combo box. When a valid index (≥ 0) is provided, retrieves the associated years stored as item data from `comboBox_per_estesa` and populates `lineEdit_cron_iniz` and `lineEdit_cron_fin` with the start and end year values respectively. An index of `-1`, indicating no selection, is ignored.

##### contenuto(self, b)

Get content suggestions from GPT with lazy import to avoid pydantic conflicts.

##### handleComboActivated(self, index)

*No description available.*
Handles the activation signal of `comboBox_per_estesa` by retrieving the text of the item at the given `index` and passing it to `contenuto()` to generate a text value. Presents the generated text to the user in an informational `QMessageBox` dialog offering **Ok** and **Cancel** options. If the user confirms with **Ok**, the generated text is written to `textEdit_descrizione_per`; otherwise, no action is taken.

##### on_suggerimenti_pressed(self)

*No description available.*
Retrieves the content associated with the current selection of `comboBox_per_estesa` by calling `self.contenuto()` and assigns the result to `generate_text`. Displays the generated text in an informational `QMessageBox` dialog with **Ok** and **Cancel** buttons. Upon confirmation, sets the text of `textEdit_descrizione_per` with the string representation of `generate_text`.

##### apikey_gpt(self)

*No description available.*
Retrieves the GPT API key by reading it from `gpt_api_key.txt` located in the application's `bin` directory. If the file does not exist, the method prompts the user via a `QInputDialog` to enter a new API key, which is then saved to that file. If the file exists but the key cannot be returned, the user is warned via a `QMessageBox` and given the option to provide a replacement key, which overwrites the existing file.

##### charge_list_sito(self)

*No description available.*
This method is defined but contains no implementation, consisting solely of a `pass` statement. Its intended behavior is not documented in the source; see implementation for details.

##### charge_list(self)

*No description available.*
Retrieves a list of site values from the `site_table` database table by grouping on the `sito` column using the database manager, then converts the result to a list via the utility helper `tup_2_list_III`. Any empty string entries are removed from the list, which is then sorted alphabetically. The method clears the `comboBox_sito` combo box and repopulates it with the cleaned, sorted site values.

##### msg_sito(self)

Displays a localized informational message box indicating the current site connection status based on the value retrieved from the `Connection` object and the currently selected item in `comboBox_sito`. If the selected site matches the configured site, a confirmation message is shown in Italian, German, or English depending on `self.L`. If no site has been configured (`sito_set_str` is empty), the user is prompted to set one, and if confirmed, the configuration dialog `pyArchInitDialog_Config` is opened; if cancelled, no action is taken.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` object and queries the database for all records matching that site name using `query_bool`. If matching records are found, it populates `DATA_LIST`, initializes the record counter, fills the form fields, sets the browse status, and disables the site combo box to lock the selection. If no records exist for the configured site, a localized informational message is displayed (in Italian, German, or English based on `self.L`); any exception raised during the process triggers a localized warning dialog.

##### on_pushButton_pdf_scheda_exp_pressed(self)

*No description available.*
Handles the press event of the PDF export button for the Periodizzazione record sheet. It instantiates a `generate_Periodizzazione_pdf` object, retrieves the current data via `generate_list_pdf()`, and delegates PDF generation to the appropriate language-specific build method — `build_Periodizzazione_sheets` for Italian (`'it'`), `build_Periodizzazione_sheets_de` for German (`'de'`), or `build_Periodizzazione_sheets_en` for all other languages.

##### on_pushButton_pdf_lista_exp_pressed(self)

*No description available.*
Handles the press event of the PDF list export button by generating an index-style PDF list for the Periodizzazione records. It instantiates a `generate_Periodizzazione_pdf` object and retrieves the data via `generate_list_pdf()`, then delegates to a language-specific build method based on the current language setting (`self.L`): `build_index_Periodizzazione` for Italian (`'it'`), `build_index_Periodizzazione_de` for German (`'de'`), or `build_index_Periodizzazione_en` for all other languages. The first element of the data list (`data_list[0][0]`) is passed alongside the full data list to the selected build method.

##### generate_list_pdf(self)

*No description available.*
Iterates over `self.DATA_LIST` and compiles a list of records formatted for PDF list generation. For each record, it safely converts the fields `periodo`, `fase`, `cron_iniziale`, and `cron_finale` to strings, substituting an empty string where a field is absent, while `sito`, `datazione_estesa`, and `descrizione` are always converted directly. Returns a list of seven-element lists, each representing one record with the fields: site name (with underscores replaced by spaces), period, phase, initial chronology, final chronology, extended dating, and description.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available `SORT_ITEMS`, allowing the user to select sort fields and order type. If no record is currently in an unsaved state (i.e., `check_record_state()` does not return `1`), the selected sort criteria are converted via `CONVERSION_DICT` and used to re-query the database through `DB_MANAGER.query_sort`, replacing the current `DATA_LIST` with the sorted results. After sorting, the browse status is set to `"b"`, the sort status is set to `"o"`, the record counter is reset to the first record, and the fields are refreshed to reflect the newly ordered data.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record has unsaved modifications; if so, it prompts the user with a language-aware confirmation dialog (Italian, German, or English) offering the option to save changes before proceeding. Once any pending save is resolved, it transitions the form to new-record entry mode (`BROWSE_STATUS = "n"`), configuring the editability and enabled state of the site, period, and phase combo boxes based on whether the current site matches the configured site setting. Finally, it resets the record counter, updates the sort and status labels, clears the input fields (either fully or preserving the site field), and disables the action buttons.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behaviour based on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it checks for version conflicts against `periodizzazione_table` using the concurrency manager before validating data and, if the record has been modified, prompting the user with a localised confirmation dialog (Italian, German, or English) to confirm the update via `update_if`. In insert mode, it validates the data via `data_error_check` and, on a successful `insert_new_rec` call, clears the form, reloads records and lists, resets sort and status indicators, updates the record counter, configures combo box states, and refreshes the displayed fields.

##### data_error_check(self)

*No description available.*
Validates all form fields for the current record, enforcing required and optional field constraints based on the active UI language (`self.L`). The three mandatory fields — Site (`comboBox_sito`), Period (`comboBox_periodo`), and Phase (`comboBox_fase`) — are checked for presence and numeric type where applicable; optional fields (`comboBox_per_estesa`, `lineEdit_cron_iniz`, `lineEdit_cron_fin`, `lineEdit_codice_periodo`) are validated only when non-empty, with length and numeric-type checks performed via an `Error_check` instance. Warning dialogs are displayed in Italian (`'it'`), German (`'de'`), or English (default) according to `self.L`, and the method returns `0` if all checks pass or `1` if any validation failure is detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates input field values from the UI to construct a new periodizzazione record, handling optional fields (`cron_iniz`, `cron_fin`, `cont_per`, `datazione_estesa`) by converting empty inputs to `None` or empty strings as appropriate for database storage. Delegates record creation to `DB_MANAGER.insert_periodizzazione_values` using the next available ID, then attempts to persist the record via `DB_MANAGER.insert_data_session`. Returns `1` on success or `0` on failure, displaying a localized warning dialog (Italian, German, or English) if an `IntegrityError` or other exception occurs during insertion.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If a data entry error is detected, the method returns `1` immediately; if no error is found but the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the changes, then delegates the response to `update_if()` and returns `0`. Returns `0` when no input errors are present.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button by loading and displaying the complete set of records. If no unsaved record state is detected (i.e., `check_record_state()` does not return `1`), the method clears the current fields, reloads all records via `charge_records()`, and repopulates the fields with the first record in the list. It also updates the browse status to `"b"`, resets the record counters to reflect the full dataset, and clears any active sort indicator on the corresponding label.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data list. If the record state check does not return `1`, it clears the existing fields, resets the current record counter (`REC_CORR`) to `0` and the total record count (`REC_TOT`) to the length of `DATA_LIST`, then populates the fields with the first entry (index `0`) and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during the process is caught and displayed as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one and navigating to the preceding record. If the index reaches `-1`, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) to inform the user that the first record has already been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`. If the record state check returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a localized warning message indicating the user is already at the last record (supporting Italian, German, and a default English message). Otherwise, it clears the current form fields via `empty_fields()`, populates them with the next record via `fill_fields()`, and updates the record counter display via `set_rec_counter()`.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by prompting the user with a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed, the method removes the record identified by `self.ID_TABLE` from `self.TABLE_NAME`, then reloads the record list and updates the UI state accordingly. If the database becomes empty after deletion, all data lists and counters are reset and the form fields are cleared; otherwise, the view is repositioned to the first record and the browse status is restored.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by transitioning the UI to search mode (`BROWSE_STATUS = "f"`), provided no unsaved record changes are pending (as determined by `check_record_state()`). It establishes a database connection to retrieve the current site setting (`sito_set`) and conditionally clears form fields — either preserving the current site selection via `empty_fields_nosite()` or performing a full reset via `empty_fields()` — depending on whether the active `comboBox_sito` value matches the configured site. Combo box editability and enabled states for `comboBox_sito`, `comboBox_periodo`, `comboBox_fase`, and `textEdit_descrizione_per` are adjusted accordingly, and the sort label and record counter are reset.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search execution triggered by the "search go" button. If the current browse status is not in search mode (`"f"`), a localized warning message (Italian, German, or English) is displayed instructing the user to initiate a new search first. Otherwise, it collects field values from the UI controls (`comboBox_sito`, `comboBox_periodo`, `comboBox_fase`, `lineEdit_cron_iniz`, `lineEdit_cron_fin`, `textEdit_descrizione_per`, `comboBox_per_estesa`, `lineEdit_codice_periodo`), builds a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean database query; depending on the result, it updates `DATA_LIST`, refreshes the displayed fields, adjusts combo box editability and enabled states, updates the browse status to `"b"`, and displays a localized message reporting the number of records found or warning that no records were found. The search button is re-enabled via `enable_button_search(1)` at the end of the method regardless of the outcome.

##### on_pushButton_show_periodo_pressed(self)

*No description available.*
Handles the press event of the "show periodo" button. If the period code field (`lineEdit_codice_periodo`) is empty, a warning dialog is displayed informing the user that a period code has not been provided. Otherwise, it retrieves the current site, period code, period label, phase label, and extended period values from the respective UI controls, then invokes `charge_vector_layers_periodo` and `charge_vector_usm_layers_periodo` on the `pyQGIS` object to load the corresponding vector layers for the specified period.

##### on_pushButton_all_period_pressed(self)

Handles the press event of the "all period" button by loading vector layers for all periods associated with a configured site. If the period code field (`lineEdit_codice_periodo`) is empty, a warning dialog is displayed and no further action is taken. Otherwise, the method queries the database for all records matching the configured site, iterates over the results, and calls `charge_vector_layers_all_period` on the `pyQGIS` instance for each record using its site, period counter, period label, phase label, and extended dating values.

##### on_pushButton_all_period_usm_pressed(self)

*No description available.*
Handles the press event of the "all period USM" button. If the `lineEdit_codice_periodo` field is empty, a warning dialog is displayed informing the user that a period code has not been provided. Otherwise, it retrieves the configured site setting via `Connection`, queries the database for all matching records filtered by site, and iterates over the results to invoke `self.pyQGIS.charge_vector_layers_usm_all_period` for each record, passing the site, period counter, period label, phase label, and extended dating values. Any exception raised during the query or layer-loading process is caught and printed to standard output.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the value of `msg`. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration depending on `SORT_STATUS`. Returns `1` if the update succeeds, `0` if `update_record()` returns `0`, and updates `BROWSE_STATUS` and the status label accordingly.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the current mapper table and populates `self.DATA_LIST` with the results. The query is executed in ascending order based on `self.ID_TABLE` using a single ordered query via `self.DB_MANAGER.query_ordered`, replacing a previously used double-query pattern for improved performance.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it as a `"%d-%m-%Y"` string (e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### table2dict(self, n)

Converts a table widget, identified by the string name `n`, into a list of lists containing the text values of each cell. The method resolves the table attribute from the instance using the provided name, stripping a `"self."` prefix if present, then iterates over all rows and columns, collecting non-empty cell text values into sublists. Returns a list of sublists, where each sublist represents one row of the table's non-null cell contents.

##### empty_fields_nosite(self)

*No description available.*
Clears the values of all form fields related to a period record, excluding the site (`comboBox_sito`) and area (`comboBox_area`) fields, which remain unchanged. Specifically, it resets the period, phase, initial and final chronology, extended dating, description, and period code fields to empty strings or cleared states.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to their default empty state. Specifically, it clears the combo boxes for site (`comboBox_sito`), period (`comboBox_periodo`), phase (`comboBox_fase`), and extended dating (`comboBox_per_estesa`) by setting their text to an empty string, and clears the line edit fields for initial chronology (`lineEdit_cron_iniz`), final chronology (`lineEdit_cron_fin`), and period code (`lineEdit_codice_periodo`), as well as the description text area (`textEdit_descrizione_per`).

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` in `DATA_LIST`, setting UI widgets — including combo boxes, line edits, and a text edit — with the corresponding field values for site, period, phase, initial and final chronology, extended dating, description, and period code. Fields whose source values are falsy are explicitly cleared rather than populated. If a `concurrency_manager` is present, the method additionally tracks the record's `version_number` and `id_perfass` for concurrency control, updates the lock indicator with any active editing user information, and logs any errors encountered during version tracking via `QgsMessageLog`.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### set_rec_counter(self, t, c)

*No description available.*
Sets the record counter values by assigning the provided total (`t`) and current (`c`) arguments to the instance attributes `rec_tot` and `rec_corr`, respectively. It then updates the corresponding UI labels, `label_rec_tot` and `label_rec_corrente`, to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects and validates the current values from the form's input fields and combo boxes, substituting empty strings for any blank text inputs. Assembles the retrieved values — including site, period, phase, initial and final chronology, description, extended chronology, and period code — into an ordered list stored in `self.DATA_LIST_REC_TEMP`. This temporary record list represents the current state of the form's data entry fields.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and then iterating over `TABLE_FIELDS` to retrieve the corresponding attribute value from the current record (`DATA_LIST[REC_CORR]`) for each field. Each retrieved value is cast to a string and appended to `DATA_LIST_REC_CORR`. This method is called as part of `records_equal_check` to capture the current record's state for comparison purposes.

##### records_equal_check(self)

*No description available.*
Compares the current record in its corrected state (`DATA_LIST_REC_CORR`) against a temporary working copy (`DATA_LIST_REC_TEMP`) to determine whether any modifications have been made. Both internal lists are refreshed prior to comparison by calling `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`. Returns `0` if the two lists are identical, or `1` if they differ.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `rec_toupdate()`. Returns `1` on success, or `0` if an exception occurs. On failure, the error is appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), English, or German (`de`) depending on the value of `self.L`.

##### rec_toupdate(self)

*No description available.*
Retrieves the record designated for updating by delegating to `self.UTILITY.pos_none_in_list`, passing `self.DATA_LIST_REC_TEMP` as the argument. Returns the resulting value from that call, which represents the processed record with `None` values positioned within the list.

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode, writes `message` to it as a string, then closes the file. Both `name_file` and `message` are cast to `str` before use. This method does not return a value.

##### check_for_updates(self)

Check if current record has been modified by others

## Functions

### estrai_numero(anno_str)

*No description available.*
Helper function that extracts a numeric year value from a string that may contain era markers. It recognizes BC/BCE markers (`a.C.`, `ac`, `aC`, `AC`, `BCE`, and their case variants) and returns the year as a negative integer, CE/AD markers (`d.C.`, `dc`, `dC`, `DC`, `CE`, and their case variants) and returns the year as a positive integer, or — if no era marker is present — extracts the digits and returns them as a positive integer. Raises a `ValueError` if no numeric digits can be found in the input string.

**Parameters:**
- `anno_str`

### processa_intervallo_slash(intervallo_str)

*No description available.*
Processes a string representing a slash-delimited interval (e.g., `1930/1950`) by splitting it on the `/` character and extracting the first and last numeric values using `estrai_numero`. Returns a tuple `(primo, ultimo)` where `primo` is the number extracted from the first part and `ultimo` is the number extracted from the last part. If no slash is present in the input string, the single numeric value extracted from the string is returned as both elements of the tuple.

**Parameters:**
- `intervallo_str`

