# tabs/Thesaurus.py

## Overview

This file contains 73 documented elements.

## Classes

### pyarchinit_Thesaurus

`pyarchinit_Thesaurus` is a QGIS `QDialog` subclass that provides a multilingual data entry and management interface for the `pyarchinit_thesaurus_sigle` database table, which stores controlled vocabulary codes (sigla), their extended forms, descriptions, typologies, and associated table names used across the PyArchInit archaeological recording system. The dialog supports browsing, searching, creating, updating, and deleting thesaurus records, with field labels, status messages, and sort items adapted to the active QGIS locale across multiple languages including Italian, German, English, Spanish, French, Arabic, Catalan, Romanian, Portuguese, and Greek. It also provides optional GPT-assisted description generation, hierarchical parent–child record management for TMA archaeological material entries, cross-table field synchronization, CSV import for SQLite connections, and an integrated web view for querying an external thesaurus service.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the form widget by calling the parent constructor, storing the provided QGIS interface reference, and instantiating a `Pyarchinit_pyqgis` object. Sets up the UI via `setupUi`, applies the current theme using `ThemeManager`, adds a theme toggle button, and creates hierarchy widgets. Establishes signal connections for `comboBox_nome_tabella` and `comboBox_sigla_estesa`, attempts a database connection via `on_pushButton_connect_pressed` (displaying a warning dialog on failure), and performs a database check via `check_db`.

##### read_api_key(self, path)

*No description available.*
Opens the file at the specified `path` in read mode and returns its contents as a string with leading and trailing whitespace removed. The method accepts a single parameter, `path`, representing the file path to read from, and returns the stripped string value read from that file.

##### write_api_key(self, path, api_key)

*No description available.*
Opens the file at the specified `path` in write mode and writes the provided `api_key` string to it. If the file does not exist it will be created; if it already exists, its contents will be overwritten. No return value is produced by this method.

##### apikey_gpt(self)

*No description available.*
Retrieves the GPT API key from a file named `gpt_api_key.txt` located in the `bin` subdirectory of `self.HOME`. If the file does not exist, the user is prompted via a `QInputDialog` to enter a new API key, which is then saved to that file. If the file exists but the key is considered invalid, a `QMessageBox` warning is displayed offering the user the option to provide a replacement key, which is also persisted to the same file before being returned.

##### check_db(self)

*No description available.*
Checks the type of database connection currently configured by retrieving the connection string via `Connection` and testing whether it references an SQLite database. If the connection string begins with `'sqlite'`, the `pushButton_import_csvthesaurus` button is made visible; otherwise, the button is hidden.

##### contenuto(self, b)

*No description available.*
Queries the OpenAI Chat Completions API to generate an archaeological description and three Wikipedia links for the content provided in parameter `b`, using a user-selected GPT model chosen via a `QInputDialog`. The response is streamed incrementally and displayed in real time within `self.textEdit_descrizione_sigla` using `QApplication.processEvents()` to keep the UI responsive. If the `openai` package is unavailable, a warning dialog is shown and an empty string is returned; if model selection is cancelled, the method returns `"Model selection was canceled."`.

##### webview(self)

*No description available.*
Extracts the plain text content from `textEdit_descrizione_sigla` and scans it for HTTP/HTTPS URLs using a regular expression. Constructs an HTML string that renders the description text with line breaks preserved and appends a list of any detected URLs as clickable hyperlinks. The resulting HTML is displayed in an informational message box and then loaded into the `webView_adarte` widget, which is subsequently shown.

##### handleComboActivated(self, index)

*No description available.*
Handles the activation of a combo box item at the given `index` by retrieving the corresponding item text from `comboBox_sigla_estesa` and passing it to `contenuto()` to generate a text string. Displays the generated text in an informational `QMessageBox` dialog offering **Ok** and **Cancel** options. If the user confirms with **Ok**, the generated text is written to the `textEdit_descrizione_sigla` text editor; otherwise, no action is taken.

##### on_suggerimenti_pressed(self)

*No description available.*
Handles the press event of the "suggerimenti" (suggestions) button by retrieving the content associated with the currently selected text in `comboBox_sigla_estesa` via the `contenuto` method. If the confirmation condition is met, it populates `textEdit_descrizione_sigla` with the retrieved text and triggers a web view refresh by calling `self.webview()`. No action is taken in the else branch.

##### find_text(self)

*No description available.*
Constructs a thesaurus query URI based on the current text of `comboBox_sigla_estesa`: if the field is empty, a default base URI is used; otherwise, a search URI is built incorporating the selected text as the query parameter. The method then performs an HTTP GET request to the resolved URI (with a 10-second timeout) and renders the response HTML in the `webView_adarte` widget. If the request fails, a warning dialog is displayed to the user with the corresponding error message.

##### on_pushButton_import_csvthesaurus_pressed(self)

funzione valida solo per sqlite

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI push buttons by passing the value `n` to each button's `setEnabled` method. The buttons affected are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all listed controls to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the main toolbar controls as a group, depending on the current application state.

##### on_pushButton_connect_pressed(self)

Handles the press event of the connect button by establishing a database connection using a `Connection` object and determining whether the backend is SQLite. If the connection succeeds, it loads records from the database and either populates the form fields and browse state (when data exists) or displays a localized welcome message and initializes a new record (when the database is empty). If an exception occurs, a localized warning message is pushed to the QGIS message bar, distinguishing between a missing table error and a general bug, based on the current language setting (`self.L`).

##### charge_list(self)

Populates the `comboBox_lingua` combo box with language keys from `self.LANG` and populates `comboBox_nome_tabella` with localized, user-friendly table display names derived from an internal multilingual mapping (`TABLE_DISPLAY_MAPPING_I18N`). The active language mapping is selected based on `self.L`, falling back to English and then Italian if the current language is not found, and is stored in `self.TABLE_DISPLAY_MAPPING` for later use by other methods. Additionally, the method initializes `self.SYNCHRONIZED_FIELDS`, a dictionary defining shared fields and their associated table-typology code pairs across multiple database tables.

##### get_table_name_from_display(self, display_name)

Convert display name to actual table name

##### get_display_name_from_table(self, table_name)

Convert table name to display name

##### charge_n_sigla(self)

Clears and repopulates `comboBox_tipologia_sigla` based on the table currently selected in `comboBox_nome_tabella`, using a statically defined multilingual dictionary (`code_descriptions`) that maps table names to code keys and their translations across supported languages (`it`, `en`, `de`, `es`, `fr`, `ar`, `ca`). For each code applicable to the selected table, the method adds the code string as a combo box item and attaches the corresponding localized description as a tooltip, falling back to Italian if the active language (`self.L`) is unsupported or absent. If the resolved table name is `'TMA materiali archeologici'`, the method additionally calls `setup_tma_hierarchy_widgets()`.

##### setup_tma_hierarchy_widgets(self)

Setup hierarchy management widgets for TMA materials.

##### on_tma_tipologia_changed(self)

Handle TMA tipologia change to show hierarchy options.

##### hide_hierarchy_widgets(self)

Hide all hierarchy selection widgets.

##### show_area_parent_widgets(self)

Show widgets for selecting località parent for area.

##### show_settore_parent_widgets(self)

Show widgets for selecting località and area parents for settore.

##### show_area_parent_dialog(self)

Show dialog for selecting località parent for area.

##### show_settore_parent_dialog(self)

Show dialog for selecting località and area parents for settore.

##### create_hierarchy_widgets(self)

Create hierarchy selection widgets dynamically.

##### load_parent_areas(self)

Load available parent areas from thesaurus.

##### load_parent_localita(self)

Load available località from thesaurus.

##### on_parent_localita_changed(self)

When località selection changes, update available areas.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog that allows the user to select sort fields and order type, provided the record state check does not block the operation. The selected sort items are converted using `CONVERSION_DICT`, and the current `DATA_LIST` is re-queried and reordered via `DB_MANAGER.query_sort` using the converted fields and sort mode. After sorting, the browse status and sort status labels are updated, the record counter is reset to the first record, and the fields are refreshed to reflect the newly ordered data.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by first checking whether the current record in browse mode (`"b"`) has unsaved modifications; if so, it prompts the user with a localized warning dialog (Italian, German, or English) asking whether to save the changes before proceeding. If the browse status is not already set to new (`"n"`), it transitions the UI into new-record mode by clearing all fields, updating the status label and sort label, making the relevant combo boxes editable and enabled, and resetting the record counter. Finally, it disables the action buttons via `enable_button(0)` to reflect the empty, unsaved state.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event by branching logic based on the current browse status (`self.BROWSE_STATUS`). In browse mode (`"b"`), it performs a data validation check and, if the record has been modified, prompts the user with a localized confirmation dialog (Italian, German, or English) before calling `update_if` to persist the changes; if no modifications are detected, a localized warning is displayed instead. Outside browse mode, it validates the data and attempts to insert a new record via `insert_new_rec`, and on success resets the form fields, reloads the record list, updates status labels and counters, configures combo box editability and enabled states, and re-enables the UI buttons.

##### data_error_check(self)

*No description available.*
Validates that the required form fields — abbreviation code (`comboBox_sigla`), extended abbreviation (`comboBox_sigla_estesa`), abbreviation typology (`comboBox_tipologia_sigla`), table name (`comboBox_nome_tabella`), language (`comboBox_lingua`), and description (`textEdit_descrizione_sigla`) — are not empty before a record is saved. For each empty field detected via `Error_check.data_is_empty`, a localized `QMessageBox` warning dialog is displayed in Italian (`'it'`), German (`'de'`), or English (default), according to the value of `self.L`. Returns an integer `test` value of `0` if all fields pass validation, or `1` if one or more validation failures were found.

##### insert_new_rec(self)

*No description available.*
Inserts a new thesaurus record into the database using field values collected from the UI (table name, sigla, extended sigla, description, typology, and language). For records belonging to the `tma_materiali_archeologici` table, the method resolves hierarchical parent relationships by querying the database for a matching parent record based on typology (`10.3` Località for Area entries, `10.7` Area for Settore entries), falling back through multiple search strategies (display name, lowercase table name, then without language constraint) to determine `id_parent`, `parent_sigla`, and `hierarchy_level`. After a successful insert, field values are synchronized via `synchronize_field_values`; the method returns `1` on success and `0` on failure, displaying a localized warning message for integrity errors or general exceptions.

##### check_synchronized_field(self, sigla_estesa, tipologia_sigla, table_name)

Check if this field should be synchronized across tables

##### synchronize_field_values(self, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua, table_name)

Synchronize field values across all related tables

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If data entry errors are found, the method returns `1` immediately; if no errors are found but the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompting the user to save changes, delegating the response to `update_if()`. Returns `0` when no data entry errors are present.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button by loading and displaying the complete set of records. If no unsaved record state is detected (`check_record_state() != 1`), the method clears the current fields, reloads all records via `charge_records()`, and repopulates the form fields using `fill_fields()`. It then sets the browse status to `"b"`, updates the record counter and status labels, resets the current record position to the first entry in `DATA_LIST`, and clears any active sort indicator.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data list. If the record state check does not return `1`, it clears the existing field values, resets the record counters so that `REC_CORR` is set to `0` and `REC_TOT` reflects the total number of items in `DATA_LIST`, then populates the fields with the first entry (index `0`) and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during execution is caught and displayed as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one. If the index reaches `-1`, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) to inform the user that the first record has been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter is updated via `set_rec_counter()`; if the record state check returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a localized warning message (Italian, German, or English) indicating that the last record has been reached. Otherwise, it clears the current fields, populates them with the next record's data via `fill_fields`, and updates the record counter display; any exception during this process is reported via an error dialog.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. Upon confirmed deletion, the method reloads the record list from the database and, if records remain, resets the browse state to the first record and refreshes the UI fields and counters; if the database is empty after deletion, all data lists are cleared and the record counter is reset to zero. Any exception raised during the deletion operation is caught and displayed to the user via a warning message box.

##### on_pushButton_sigle_pressed(self)

Load thesaurus codes documentation in webView_adarte

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "new search" button by first verifying the current record state via `check_record_state()`; if the record state check does not return `1`, the method proceeds to initialize a new search session. It sets `BROWSE_STATUS` to `"f"`, updates the status label, resets the record counter and sort label, and configures the relevant combo boxes (`comboBox_sigla`, `comboBox_sigla_estesa`, `comboBox_tipologia_sigla`, `comboBox_nome_tabella`, `comboBox_lingua`) to be both editable and enabled, while disabling `textEdit_descrizione_sigla`. Finally, it reloads the combo box lists and clears all input fields by calling `charge_list()` and `empty_fields()`.

##### on_pushButton_search_go_pressed(self)

Handles the press event of the search button (`pushButton_search_go`). If the browse status is not in search mode (`"f"`), a localized warning message is displayed instructing the user to initiate a new search first; otherwise, a search dictionary is built from the current values of the combo boxes (`comboBox_nome_tabella`, `comboBox_sigla`, `comboBox_sigla_estesa`, `comboBox_tipologia_sigla`, `comboBox_lingua`), empty entries are removed, and a boolean query is executed against the database. Depending on the query result, the method updates `DATA_LIST`, refreshes the displayed fields, sets the browse status to `"b"`, adjusts the enabled and editable state of the combo boxes, and displays a localized message reporting the number of records found or warning that no records were found; the search button is re-enabled at the end regardless of outcome.

##### on_pushButton_test_pressed(self)

*No description available.*
This method serves as the event handler triggered when the test push button is pressed. In its current state, the method body contains only a `pass` statement, meaning it performs no operations when invoked. The commented-out code beneath the method suggests a future or deferred implementation involving site data retrieval and test execution, but this logic is not active.

##### on_pushButton_draw_pressed(self)

*No description available.*
Slot method triggered when the "draw" push button is pressed in the user interface. The method body is currently a no-op (`pass`), with the active drawing logic commented out; the commented code suggests an intended call to `self.pyQGIS.charge_layers_for_draw` with a predefined list of layer identifiers. No operations are performed upon invocation in the current implementation.

##### on_pushButton_sites_geometry_pressed(self)

*No description available.*
Handler method triggered when the "sites geometry" push button is pressed. The method body contains no active implementation; the functional logic — which appears to have involved loading site geometry layers filtered by a site identifier — is present only as commented-out code and is not currently executed. See implementation for any future or restored behavior.

##### on_pushButton_sync_tma_thesaurus_pressed(self)

Sincronizza il thesaurus TMA con inventario materiali e aree

##### on_pushButton_rel_pdf_pressed(self)

*No description available.*
This method serves as the event handler for the "rel\_pdf" push button press action. In its current state, the method body contains only a `pass` statement and performs no operations. Commented-out code suggests the original intent was to trigger a PDF relation export via an `exp_rel_pdf` instance using the current site selection from `comboBox_sito`, but this functionality is not active in the present implementation.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's confirmation dialog response. If `msg` equals `QMessageBox.StandardButton.Ok`, it calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying and re-sorting the updated records using either the default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Upon completion, the browse status is set to `"b"` and the status label is refreshed; returns `1` on success or `0` on failure.

##### charge_records(self)

*No description available.*
Loads all records from the database into the `DATA_LIST` attribute by executing a single ordered query against the mapped table class. The query retrieves results sorted by `ID_TABLE` in ascending order, using `DB_MANAGER.query_ordered` to replace a previously used double-query pattern for improved performance.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded and hyphen-separated). The formatted date string is returned to the caller.

##### table2dict(self, n)

Converts a UI table widget into a list of lists by accepting a table name string `n`, resolving the corresponding table attribute on the instance, and iterating over all rows and columns to extract cell text values. Each non-empty cell's text is appended to a per-row sub-list, and all sub-row lists are collected into a single outer list. Returns the resulting list of lists representing the table's content.

##### empty_fields(self)

*No description available.*
Resets all input fields in the form to an empty state. Clears the `comboBox_sigla`, `comboBox_sigla_estesa`, `comboBox_tipologia_sigla`, `comboBox_nome_tabella`, and `comboBox_lingua` combo boxes by setting their edit text to an empty string, and clears the `textEdit_descrizione_sigla` text editor. This method is typically used to blank out the form in preparation for new data entry or after a record operation.

##### fill_fields(self, n)

*No description available.*
Populates all form fields with data from the record at index `n` in `DATA_LIST`, setting the current record number via `self.rec_num`. Each UI widget — including `comboBox_sigla`, `comboBox_sigla_estesa`, `comboBox_tipologia_sigla`, `comboBox_nome_tabella`, `textEdit_descrizione_sigla`, and `comboBox_lingua` — is updated with the corresponding attribute from the selected record, with the table name converted to a display name via `get_display_name_from_table`. If the record has a non-empty `parent_sigla` attribute, a deferred call to `_restore_parent_selections` is scheduled via `QTimer.singleShot` to restore hierarchy field selections after the relevant widgets have been created.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values for the UI. Assigns the provided values `t` and `c` to the instance attributes `rec_tot` and `rec_corr` respectively, then updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Populates `self.DATA_LIST_REC_TEMP` with a ten-element list representing the current state of the form's input fields for a temporary record. Before building the list, the method resolves the selected language from `comboBox_lingua`, converts the displayed table name to its internal name via `get_table_name_from_display`, and — when the current record belongs to the `'TMA materiali archeologici'` table — derives hierarchy fields (`id_parent`, `parent_sigla`, `hierarchy_level`) by inspecting the active tipologia value (`'10.7'` for Area or `'10.15'` for Settore) and querying the database through `self.DB_MANAGER.query_bool` to resolve parent record identifiers. Existing hierarchy and ordering values are first read from the current record in `self.DATA_LIST` at index `self.REC_CORR` and are overwritten only when the relevant hierarchy widgets are present and the table name matches.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by iterating over `TABLE_FIELDS` and retrieving the corresponding attribute values from the current record (`DATA_LIST[REC_CORR]`) using `getattr`. Any attribute value that is `None` is converted to the string `'None'` for compatibility with `pos_none_in_list`. All retrieved values are cast to strings before being appended to `DATA_LIST_REC_CORR`.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets - uses getattr instead of eval for security

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `pos_none_in_list` on `self.DATA_LIST_REC_TEMP` via the `self.UTILITY` helper. The method identifies positions of `None` values within the temporary record data list and returns that result as `rec_to_update`. No parameters are accepted beyond the implicit `self`.

##### records_equal_check(self)

Compares the current temporary record data against the corresponding corrected record data to determine whether any changes have been made. Returns `0` if the records are equal, if `BROWSE_STATUS` is `"n"` (new record mode), or if `DATA_LIST` is empty; returns `1` if the records differ. Prior to comparison, the method calls `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate the respective data lists.

##### update_record(self)

*No description available.*
Persists changes to the currently selected thesaurus record by invoking `DB_MANAGER.update` with the current record's identifier, table fields, and updated values produced by `rec_toupdate()`. After a successful database update, it compares the pre-update values of `sigla`, `tipologia_sigla`, `lingua`, and `nome_tabella` against the current UI field values, and if those key fields are unchanged, calls `synchronize_field_values` to propagate the updated `sigla_estesa` and `descrizione` values. On failure, the exception details and `DATA_LIST_REC_TEMP` are appended to `error_encoding_data_recover.txt` in the report folder, a localized warning dialog is displayed, and the method returns `0`; on success it returns `1`.

##### testing(self, name_file, message)

*No description available.*
Opens a file at the path specified by `name_file` in write mode, writes the string representation of `message` to it, and then closes the file. This method provides a simple mechanism for persisting diagnostic or log output to disk.

## Functions

### on_ok()

Confirms the dialog and stores the selected locality value. If the current index of `combo_localita` is greater than 0, it extracts the portion of the selected text before the `' - '` separator and assigns it to `self.selected_localita_parent`; otherwise, `self.selected_localita_parent` retains its previously set value. Closes the dialog by calling `dialog.accept()`.

### on_cancel()

*No description available.*
Sets `self.selected_localita_parent` to `None` and dismisses the dialog by calling `dialog.reject()`. This function serves as the cancel action handler, ensuring that no locality selection is retained when the user aborts the dialog. It is connected to the cancel button's `clicked` signal.

### on_localita_changed()

*No description available.*
A slot function connected to the `currentIndexChanged` signal of `combo_localita`. When triggered, it clears `combo_area` and, if a valid località is selected (index greater than 0), enables `combo_area` and populates it by querying the database for records matching the extracted `localita_sigla`, the table name `'TMA materiali archeologici'`, and the tipologia sigla `'10.7'`. If no valid località is selected, `combo_area` is disabled and displays a placeholder prompt instructing the user to first select a località.

### on_ok()

Confirms the dialog and stores the user's area selection. If the combo box has a valid selection (index greater than 0), extracts the area identifier from the selected text by splitting on `' - '` and taking the first segment, storing it in `self.selected_area_parent`. Closes the dialog by calling `dialog.accept()`.

### on_cancel()

Sets `selected_area_parent` to `None` and dismisses the dialog by calling `dialog.reject()`. This function serves as the cancel handler, discarding any pending selection and closing the dialog without accepting the input.

