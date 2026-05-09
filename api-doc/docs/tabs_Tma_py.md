# tabs/Tma.py

## Overview

This file contains 122 documented elements.

## Classes

### pyarchinit_Tma

This class provides the implementation of the TMA (Tabella Materiali Archeologici) tab.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the form widget by calling the parent constructor, setting up the UI layout, and applying the active theme via `ThemeManager`. Configures internal state flags (`materials_loaded`, `deleted_material_ids`, `loading_data`, `lists_loaded`), initializes a `QListWidget` for icon-based media display with drag-and-drop support, and adds media and table view tabs before customizing the GUI and establishing a database connection. Sets up concurrency management components (`ConcurrencyManager`, `RecordLockIndicator`) and starts a `QTimer` that fires every 60 seconds to check for concurrent record modifications, then initializes the remote image loader.

##### add_custom_toolbar_buttons(self)

Add custom buttons between toolbar and tabWidget.

##### customize_GUI(self)

Customize the GUI elements - connect signals to slots.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary navigation and record-management buttons simultaneously by passing `n` to each button's `setEnabled()` method. The buttons affected are: `pushButton_new_rec`, `pushButton_view_all_2`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. Passing a truthy value enables all listed buttons, while a falsy value disables them.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of a group of record-management buttons based on the value of `n`. The affected buttons are: `pushButton_new_rec`, `pushButton_view_all_2`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. Each button's `setEnabled` method is called with `n` as the argument, allowing all related controls to be activated or deactivated simultaneously.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` instance, detecting whether the backend is SQLite, and initialising the database manager via `get_db_manager`. If the database contains existing records, it loads and displays the first record, updating the browse status, record counter, and icon list accordingly; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`), enables relevant UI controls, and triggers new record creation. Any exception encountered during connection or data loading is caught and reported as a localised warning message in the QGIS message bar.

##### check_and_update_schema(self)

Check and update database schema if needed for both SQLite and PostgreSQL.

##### charge_list(self)

Load combobox lists.

##### charge_records(self)

*No description available.*
Loads all records from the `tma_materiali_archeologici` database table into `DATA_LIST` using an ascending ordered query via `DB_MANAGER`. Before and after loading, the method queries the record count directly from the database and logs a critical warning to `QgsMessageLog` if the count decreases during the operation, indicating unexpected record deletion. After loading, it refreshes the materials table delegates by calling `setup_materials_table_with_thesaurus()`.

##### datestrfdate(self)

Convert date fields to string format.

##### table_set_todelete(self)

Mark tables for deletion mode.

##### msg_sito(self)

Retrieves the currently configured site from the database connection and compares it against the value selected in `comboBox_sito`. If they match, displays an informational message confirming the active site connection, with text localised to Italian or English based on `self.L`. If no site has been configured, prompts the user to set one via a confirmation dialog; if the user confirms, opens the `pyArchInitDialog_Config` dialog to configure a site.

##### set_sito(self)

*No description available.*
Initializes the form's site context by retrieving the configured site value from a `Connection` instance and querying the database for matching records. If matching records are found, the data list and record counters are populated, the fields are filled, and the site combo box is locked to prevent editing; if no records exist for the configured site, the form is prepared for new record creation and an informational message is displayed in the appropriate language. If no site is configured, the site combo box is left enabled and editable to allow free input.

##### fill_fields(self, n)

*No description available.*
Populates all form fields with data from the record at index `n` in `DATA_LIST`, setting `rec_num` to the provided index. Combobox signals are blocked during population to prevent event handlers from firing, and `area` and `settore` values are explicitly handled to correctly display empty or `None` states. After filling standard fields, the method loads the materials table, inserts photo and drawing documentation into their respective table widgets, and — if a `concurrency_manager` is present — updates version tracking, lock indicators, and the editing record identifier for the current record.

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### fill_documentation_tables(self)

Fill documentation tables with data.

##### load_tma_media(self)

Load media associated with current TMA record.

##### set_rec_counter(self, t, c)

*No description available.*
Updates the record counter display labels in the user interface. Sets `label_rec_tot` to the total record count `t` and `label_rec_corrente` to the current record index `c`, converting both values to strings before display. Only the UI labels are updated; no internal variables are modified.

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### records_equal_check(self)

*No description available.*
Compares the current form state against the corresponding database record to determine whether any unsaved changes exist. It populates the temporary and current record lists via `set_LIST_REC_TEMP` and `set_LIST_REC_CORR`, then performs a field-by-field comparison across `TABLE_FIELDS`, excluding system fields (`created_at`, `updated_at`, `created_by`, `updated_by`), and additionally checks for changes in the materials state via `check_materials_state`. Returns `0` if no differences are detected, `1` if any changes are found, or `0` if an `IndexError` or other exception occurs during the comparison.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `self.DATA_LIST_REC_CORR` with the field values of the record at index `self.REC_CORR` within `self.DATA_LIST`. For each field name defined in `self.TABLE_FIELDS`, the corresponding attribute is retrieved from the target record, with `None` values converted to empty strings and all other values cast to `str`. Raises an `IndexError` if `self.REC_CORR` is out of the valid range of `self.DATA_LIST`.

##### set_LIST_REC_TEMP(self)

Build the temporary record list from form data.

##### get_foto_data(self)

Get photo data from table widget.

##### get_disegni_data(self)

Get drawings data from table widget.

##### setup_materials_table(self)

Setup the materials table widget with proper headers and structure.

##### load_materials_table(self)

Load materials data for current TMA record from database.

##### save_materials_data(self, tma_id)

Save materials table data to database.

##### on_pushButton_add_materiale_pressed(self)

Add a new row to materials table.

##### on_pushButton_remove_materiale_pressed(self)

Remove selected row from materials table.

##### update_material_navigation(self)

Update navigation buttons for materials table.

##### set_LIST_REC_CORR(self)

Set the current record list.

##### empty_fields(self)

Clear all form fields.

##### empty_fields_nosite(self)

Clear all form fields except site.

##### REC_TOT_TEMP(self)

Return the temporary total number of records.

##### check_record_state(self)

Check if record has been modified but don't show dialog or trigger actions.

##### check_materials_state(self)

Check if materials in the table have changed compared to database.

##### data_error_check(self)

Check for data errors in form fields.

##### update_if(self, msg)

Update interface message.

##### on_pushButton_import_pressed(self)

Open import dialog.

##### update_record(self)

Update the current record if modified.

##### setComboBoxEnable(self, f, v)

Enable/disable comboboxes.

##### setComboBoxEditable(self, f, n)

Set combobox editable state.

##### on_pushButton_first_rec_pressed(self)

Handles the "first record" navigation button press event, navigating to the first record in `DATA_LIST`. Before navigating, it applies a 500ms debounce guard and a re-entrancy lock (`_navigation_in_progress`) to prevent rapid or concurrent navigation calls; if the current record has unsaved modifications (`check_record_state() == 1`), the user is prompted to save, discard, or cancel the navigation. On confirmed navigation, it clears the current fields via `empty_fields()`, resets `REC_CORR` to `0`, populates the fields for the first record via `fill_fields(0)`, and updates the record counter display.

##### on_pushButton_last_rec_pressed(self)

Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to `len(DATA_LIST) - 1`, then clears and repopulates the form fields via `empty_fields` and `fill_fields`, and updates the record counter display. Before navigating, the method applies a 500ms debounce guard and a re-entrancy lock (`_navigation_in_progress`) to prevent rapid or concurrent navigation calls. If the current record has unsaved modifications (indicated by `check_record_state()` returning `1`), the user is prompted to save, discard, or cancel the navigation.

##### on_pushButton_prev_rec_pressed(self)

Handles the "previous record" button press event, navigating to the preceding record in the current dataset by decrementing `REC_CORR` and refreshing the form fields via `empty_fields`, `fill_fields`, and `set_rec_counter`. Includes a 500ms debounce mechanism and a re-entrancy guard (`_navigation_in_progress`) to prevent multiple rapid navigation calls. If the current record index is already at zero, a localized warning message is displayed (Italian, German, or English based on `self.L`); if the record has unsaved modifications (detected via `check_record_state`), the user is prompted to save, discard, or cancel the navigation.

##### on_pushButton_next_rec_pressed(self)

Advances the current record pointer (`REC_CORR`) to the next record in the dataset, with a 500 ms debounce guard and a re-entrancy lock (`_navigation_in_progress`) to prevent rapid or concurrent navigation calls. If the current record is already the last one (`REC_CORR >= REC_TOT - 1`), a localized warning dialog is displayed (Italian, German, or English depending on `self.L`) and navigation is aborted. If the current record has unsaved modifications (as determined by `check_record_state()`), the user is prompted to save, discard, or cancel before proceeding; on confirmation, the fields are cleared and repopulated via `empty_fields()` and `fill_fields()`, and the record counter is updated via `set_rec_counter()`.

##### on_pushButton_new_rec_pressed(self)

Create a new record.

##### on_pushButton_save_pressed(self)

Save the current record.

##### on_pushButton_delete_pressed(self)

Delete the current record.

##### on_pushButton_new_search_pressed(self)

Enable search mode.

##### on_pushButton_table_view_pressed(self)

Switch to table view tab when toolbar button is pressed.

##### on_pushButton_advanced_search_pressed(self)

Open advanced search dialog for US and cassette ranges.

##### on_pushButton_search_go_pressed(self)

Execute search.

##### on_pushButton_sort_pressed(self)

Open sort dialog.

##### on_pushButton_view_all_pressed(self)

View all records.

##### add_foto_row(self)

Add a photo row to the documentation table.

##### remove_foto_row(self)

Remove selected photo row from documentation table.

##### add_disegno_row(self)

Add a drawing row to the documentation table.

##### remove_disegno_row(self)

Remove selected drawing row from documentation table.

##### on_toolButtonGis_toggled(self)

Handle GIS button toggle.

##### on_pushButton_open_dir_pressed(self)

Open media directory.

##### build_search_dict(self)

Build search dictionary from form fields.

##### build_materials_search_dict(self)

Build search dictionary for materials table.

##### check_for_duplicate(self)

Check if a similar record was recently inserted to prevent duplicates.

##### insert_new_rec(self)

Insert a new record into the database.

##### update_record_to_db(self)

Update current record in database.

##### on_pushButton_export_pdf_pressed(self)

Export current TMA record to PDF.

##### on_pushButton_export_tma_pdf_pressed(self)

Export current TMA record to PDF using the specific TMA template.

##### on_pushButton_auto_fill_materials_pressed(self)

Auto-fill materials from inventory based on site/area/us.

##### on_us_changed(self)

Handle US field change - only updates inventory.

##### on_localita_changed(self)

Handle località field change to filter area and reset settore.

##### on_area_changed(self)

Handle area field change to update inventory and filter settore.

##### on_sito_changed(self)

Handles changes to the site (sito) field by updating the inventory field and resetting the area and settore combo boxes. If the `loading_data` flag is set, the method returns immediately to avoid clearing values that are being restored. In the event of an exception during area filtering, a warning is logged via `QgsMessageLog` and `load_area_values()` is called as a fallback.

##### filter_area_by_localita(self)

Filter area options based on selected località.

##### filter_settore_by_area(self)

Filter settore options based on selected area.

##### load_area_values(self)

Load all area values from thesaurus.

##### addTableViewTab(self)

Add table view tab after media tab.

##### on_tab_changed(self, index)

Handle tab changes to refresh table view when needed.

##### populate_table_view(self)

Populate the table view with TMA records.

##### on_table_item_double_clicked(self, item)

Handle double-click on table row to load record in form view.

##### load_settore_values(self)

Load all settore values from thesaurus.

##### update_inventory_field(self)

Update the inventory field with RA numbers from inventory materials.

##### load_thesaurus_values(self, field_type)

Load thesaurus values for material fields.

##### setup_materials_table_with_thesaurus(self)

Setup materials table with thesaurus support using delegates.

##### setup_documentation_delegates(self)

Setup delegates for photo and drawing documentation tables.

##### on_materials_table_changed(self, item)

Called when an item in the materials table is changed.

##### update_materiale_field(self)

Update the lineEdit_materiale field with unique categories from the table.

##### addMediaTab(self)

Add media and map tabs to the existing tab widget.

##### loadMediaPreview(self, mode)

Load media preview for the current TMA record.

##### openWide_image(self)

Open selected image in full view.

##### loadMapPreview(self, mode)

Load map preview for current TMA record.

##### assignTags_TMA_from_item(self, item)

Assign tags from a single media item to current TMA record.

##### assignTags_TMA(self)

Assign current TMA record as tag to selected media.

##### dropEvent(self, event)

Handle file drop events for media upload.

##### dragEnterEvent(self, event)

Accept drag events for supported file types.

##### load_and_process_image(self, filepath)

Process dropped image file and add to media.

##### removeTags_TMA(self)

Remove tags from selected media.

##### viewAllImages(self)

View all images in the database.

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

Insert record into MEDIATOENTITY table.

##### on_pushButton_print_pressed(self)

Handle print button click - show dialog to choose print type.

##### populate_filter_combos(self)

Populate filter combo boxes with unique values from database.

##### print_single_tma(self)

Print single TMA record.

##### print_all_tma(self)

Print all TMA records to PDF.

##### print_tma_list(self)

Print filtered TMA list.

##### on_pushButton_export_crate_list_pressed(self)

Export crate list with materials summary from TMA to Excel.

##### export_crate_list_to_excel(self, export_data)

Export crate list to Excel file.

##### on_pushButton_export_labels_pressed(self)

Handle label export button click.

##### export_single_label(self, label_format, label_style)

Export single label for current record.

##### export_all_labels(self, label_format, label_style)

Export labels for all TMA records.

##### export_filtered_labels(self, label_format, label_style)

Export labels for filtered TMA records.

##### insert_new_row(self, table_name)

Insert new row into a table based on table_name.

##### remove_row(self, table_name)

Remove selected row from a table based on table_name.

##### table2dict(self, table_name)

Convert table widget data to dictionary list.

### MaterialData

*No description available.*
A lightweight data container class defined inline to hold a single row of material records retrieved from a database query. Each instance maps positional columns from a result row to named attributes: `id`, `id_tma`, `madi`, `macc`, `macl`, `macp`, `macd`, `cronologia_mac`, `macq`, and `peso`. Instances are constructed by passing a row sequence to `__init__`, which assigns each indexed element to its corresponding attribute.

#### Methods

##### __init__(self, row_data)

*No description available.*
Initializes a `MaterialData` instance by mapping a sequence of indexed row values to corresponding instance attributes. Assigns `row_data[0]` through `row_data[9]` to the fields `id`, `id_tma`, `madi`, `macc`, `macl`, `macp`, `macd`, `cronologia_mac`, `macq`, and `peso`, respectively. This class serves as a lightweight data container for holding a single database row's material-related fields.

## Functions

### toggle_range()

*No description available.*
Enables or disables the range input fields (`us_from`, `us_to`) and the US list widget (`us_list_widget`) based on the checked state of the `use_range` checkbox. When the range is enabled, `us_from` and `us_to` become interactive and `us_list_widget` is disabled; when disabled, the inverse applies. The function also updates the label text of `us_list_label` to reflect the current active input mode, displaying either `"Intervallo US attivo (lista disabilitata):"` or `"Oppure seleziona US specifiche dalla lista:"` accordingly.

### toggle_filters()

*No description available.*
Enables or disables the `filters_group` and `font_group` widgets based on whether `radio_list` is the currently selected radio button. When filters are enabled, it restores the individual enabled states of `combo_filter_materiale` and `combo_filter_categoria` according to their corresponding checkboxes (`check_filter_materiale` and `check_filter_categoria`). This function is connected to the `toggled` signal of both `radio_single` and `radio_list`, and is also called once immediately upon setup to apply the initial state.

### toggle_label_filters()

*No description available.*
Enables or disables the `filters_group` widget based on whether the `radio_label_list` radio button is currently checked. It is connected to the `toggled` signal of `radio_label_single` so that it is invoked automatically whenever that radio button's state changes, and is also called once immediately upon setup to apply the correct initial state.

### get_cell_value(item, col_index)

*No description available.*
Retrieves the text value from a `QTableWidgetItem` by attempting multiple data-access methods in order of priority. It first calls `item.text()`, then falls back sequentially to `Qt.ItemDataRole.EditRole`, `Qt.ItemDataRole.DisplayRole`, and `Qt.ItemDataRole.UserRole + 1`, returning the first non-empty value found as a string. Returns an empty string if `item` is `None` or if all retrieval attempts yield empty results.

**Parameters:**
- `item`
- `col_index`

