# tabs/Pdf_administrator.py

## Overview

This file contains 36 documented elements.

## Classes

### pyarchinit_PDFAdministrator

*No description available.*
A QDialog subclass that provides a graphical interface for managing PDF configuration records stored in `pdf_administrator_table`. It supports full CRUD operations—browsing, creating, saving, deleting, and sorting records—where each record defines a table name, grid schema, cell-merge schema, and model template used for PDF generation. The dialog integrates with the application's database manager to load and persist these configurations, and exposes navigation controls for moving between records sequentially.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

*No description available.*
Initializes the dialog instance by calling the parent class constructor and setting up the UI via `setupUi`. Sets `currentLayerId` to `None` and connects the `itemSelectionChanged` signal of `tableWidget_schema_griglia` to the `cellchanged` slot. Accepts optional `parent` and `db` parameters, neither of which is directly used within the visible implementation body.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons simultaneously by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all navigation, search, and record-management controls to be enabled or disabled in a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This allows all listed controls to be collectively enabled or disabled with a single call.

##### connect(self)

Establishes a database connection using the connection string retrieved from the `Connection` class in `pyarchinit_conn_strings`, then initialises the database manager via `get_db_manager` and loads records by calling `charge_records`. If records are present in `DATA_LIST`, it sets the browse status, updates the record counter and status labels, and populates the form fields via `fill_fields`; if the database is empty, it displays a welcome `QMessageBox`, sets the browse status to `'x'`, charges the list, and triggers the new record action. Any exception encountered during this process is caught and reported to the user via a `QMessageBox` warning dialog.

##### cellchanged(self)

*No description available.*
Updates the instance variables `ROW` and `COL` with the current row and column indices of the selected cell in `tableWidget_schema_griglia`. It retrieves these values by calling `currentRow()` and `currentColumn()` on the table widget, storing the results in `self.ROW` and `self.COL` respectively. This method is intended to track the most recently active cell position within the grid schema table.

##### on_pushButton_inserisci_nome_campo_pressed(self)

*No description available.*
Handles the press event of the "inserisci nome campo" push button. Retrieves the currently selected text from `comboBox_elenco_campi` and inserts it as a `QTableWidgetItem` into `tableWidget_schema_griglia` at the row and column position previously recorded by `cellchanged` (stored in `self.ROW` and `self.COL`). The item is placed using a dynamically constructed and evaluated expression via `exec_str`.

##### cell_click_ed(self)

*No description available.*
This method is a placeholder handler for cell-click events on the table widget. Its body contains only a `pass` statement, with the functional implementation (a `QMessageBox` warning dialog) commented out. No logic is currently executed when this method is called.

##### set_table_name(self, tname)

*No description available.*
Sets the current table name by assigning the provided `tname` value to the instance attribute `TABLE_NAME`. Updates the `label_tabella_corrente` UI label by looking up the corresponding display name from `TABLE_NAME_DICT` using the new table name as the key.

**Parameters:**
- `tname` — the table name to assign to `TABLE_NAME`.

##### charge_list(self)

*No description available.*
Retrieves the list of field names for the currently set table (`TABLE_NAME`) from the database manager via `DB_MANAGER.fields_list()`. Any empty string entries are removed from the list, which is then sorted alphabetically. The resulting field names are loaded into the `comboBox_elenco_campi` combo box, replacing any previously displayed items.

##### add_id_list(self, id_list)

*No description available.*
Assigns the provided `id_list` parameter to the instance attribute `ID_LIST`. This method serves as a simple setter, storing the supplied list of identifiers for later use by the object.

**Signature:** `add_id_list(self, id_list)`

| Parameter | Description |
|-----------|-------------|
| `id_list` | The list of identifiers to be stored in `self.ID_LIST`. |

##### on_pushButton_charge_default_schema_pressed(self)

*No description available.*
Handles the press event of the "charge default schema" button by loading a hardcoded default grid schema into the table widget identified as `'self.tableWidget_schema_griglia'` via `tableInsertData`. The default schema is a 7×9 two-dimensional array of cell identifiers in `"CxRy"` format (columns 0–8, rows 0–6). After inserting the data, the method displays a warning dialog using `QMessageBox` that shows the current contents of `self.ID_LIST`.

##### on_pushButton_sort_pressed(self)

*No description available.*
Opens a `SortPanelMain` dialog pre-populated with `self.SORT_ITEMS`, allowing the user to select sort fields and an order type. Upon dialog completion, the selected items are converted using `self.CONVERSION_DICT`, and the current record list is re-queried from the database via `DB_MANAGER.query_sort` using the converted sort criteria and order. The resulting sorted data list is applied to `self.DATA_LIST`, the browse and sort status labels are updated, the record counter is reset, and the form fields are refreshed to display the first record.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by preparing the GUI for the creation of a new record. If the application is currently in browse mode (`"b"`) and unsaved modifications are detected via `records_equal_check()`, the user is prompted with a warning dialog (in Italian) asking whether to save the pending changes before proceeding. The method then transitions the interface to new-record mode (`"n"`) by updating the status label, clearing all fields, resetting the record counter, and adjusting the enabled state of UI buttons accordingly.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event by branching logic based on the current browse status (`BROWSE_STATUS`). If the application is in browse mode (`"b"`), it checks whether the current record has been modified via `records_equal_check()`; if modifications are detected, it prompts the user with a confirmation dialog before calling `update_if()` to apply changes, otherwise it notifies the user that no modifications were made. If the application is not in browse mode, it performs a data validation check via `data_error_check()` and, upon success, inserts a new record, refreshes the UI fields and record counters, and transitions the application back to browse mode.

##### data_error_check(self)

*No description available.*
Performs validation checks on form data before record insertion. In its current state, the method initializes a test counter to `0` and returns it directly, as all validation logic (including site field empty-check via `Error_check`) is commented out. Returns an integer value of `0`, indicating no errors detected.

##### insert_new_rec(self)

*No description available.*
Collects data from the UI widgets — including the current table name, grid schema, cell merge schema, and selected model — and inserts a new PDF administrator record into the database with an auto-incremented ID. On success, the method returns `1`; on failure, it displays a warning dialog with an appropriate error message and returns `0`. Integrity constraint violations are specifically detected and reported with a localized message indicating the record already exists in the database.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "view all" button by clearing the current input fields, reloading all records from the data source, and populating the fields with the retrieved data. Sets the browse status to `"b"`, updates the status label accordingly, resets the record counter to reflect the total number of records, and positions the current record pointer at the first entry in `DATA_LIST`. Also resets the sort label to the unsorted state indicator.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Handles the "first record" navigation button press event. If the current record has been modified, it prompts the user with a warning dialog asking whether to save the changes before navigating away. It then clears the current fields, sets the current record position to the first entry in `DATA_LIST` (index `0`), populates the fields with that record's data, and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in the data list. If the current record has been modified (detected via `records_equal_check()`), the user is prompted with a warning dialog asking whether to save the changes before proceeding. The method then clears the current fields, sets `REC_CORR` to the index of the last record in `DATA_LIST`, repopulates the fields with that record's data, and updates the record counter accordingly; any exception raised during this process is displayed in an error dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by navigating to the preceding record in the current dataset. If the current record has been modified, the user is prompted to save changes before navigation proceeds. Decrements `REC_CORR` by one; if the result is `-1`, it resets `REC_CORR` to `0` and displays a warning indicating the first record has been reached, otherwise it clears the current fields, populates them with the previous record's data, and updates the record counter display.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles navigation to the next record when the corresponding button is pressed. If the current record has unsaved modifications (detected via `records_equal_check()`), the user is prompted to save changes before proceeding. Increments `REC_CORR` and, if the resulting index does not exceed `REC_TOT`, clears the current fields, populates them with the next record's data, and updates the record counter; otherwise, decrements `REC_CORR` and displays a warning indicating that the last record has been reached.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by first displaying a confirmation warning dialog to the user before proceeding with any destructive action. If confirmed, it retrieves the identifier of the currently selected record, delegates its deletion to the database manager via `delete_one_record`, and reloads the record list. After deletion, it resets all internal data lists, counters, and UI fields if the dataset is empty, or navigates to the first record and updates the browse status and record counter if data remains.

##### on_pushButton_new_search_pressed(self)

Handles the "New Search" button press event by first checking whether the current record has unsaved modifications while in browse mode (`BROWSE_STATUS == "b"`), and if so, prompting the user with a warning dialog to save or discard changes via `update_if`. It then disables the search button by calling `enable_button_search(0)`. If the application is not already in search mode (`BROWSE_STATUS != "f"`), it transitions to search mode by updating `BROWSE_STATUS` to `"f"`, refreshing the status label, clearing all input fields via `empty_fields()`, resetting the record counter, and clearing the sort label.

##### on_pushButton_search_go_pressed(self)

*No description available.*
This method serves as the event handler triggered when the search execution button is pressed. In its current state, the method body contains only a `pass` statement and performs no operations. The implementation details are not documented in source.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the value of `msg`. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()`, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration depending on `SORT_STATUS`, and then sets `BROWSE_STATUS` to `"b"` while updating the status label accordingly. The method also resolves the current record correction index (`REC_CORR`), falling back to `0` if its type is a string.

##### charge_records(self)

*No description available.*
Loads all records from the database into the instance's `DATA_LIST` attribute by executing a single ordered query against the mapped table. The query retrieves records sorted by `ID_TABLE` in ascending order using `DB_MANAGER.query_ordered`, replacing a previously used double-query pattern for improved performance.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### empty_fields(self)

*No description available.*
Clears all rows from `tableWidget_schema_griglia` by iterating over the row count of both `tableWidget_schema_griglia` and `tableWidget_gestione_celle`, removing rows from `tableWidget_schema_griglia` in each loop. After clearing the table rows, it resets the text of `comboBox_modello` to an empty string.

##### fill_fields(self, n)

*No description available.*
Populates the form fields with data from the record at index `n` in `DATA_LIST`. It sets the current record number, updates the table name label, inserts grid schema and cell merge schema data into their respective table widgets, and sets the model combo box text. After populating all fields, it calls `charge_list()` to refresh any dependent list data.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

Collects the current form field values and stores them in `self.DATA_LIST_REC_TEMP` as a list of four elements: the current table name from `self.label_tabella_corrente`, the grid schema from `self.tableWidget_schema_griglia`, the cell merge schema from `self.tableWidget_gestione_celle`, and the selected model from `self.comboBox_modello`. The two table widgets are converted to dictionary representations via the `table2dict` method before being stored. This temporary record list captures an in-progress state of the form prior to confirmation or persistence.

##### set_LIST_REC_CORR(self)

Populates `DATA_LIST_REC_CORR` by resetting it to an empty list and iterating over `TABLE_FIELDS` to retrieve the corresponding attribute value from the current record (`DATA_LIST[REC_CORR]`) for each field. Each retrieved attribute value is converted to a string and appended to `DATA_LIST_REC_CORR`, effectively building a list representation of the currently selected record.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets - uses getattr instead of eval for security

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

