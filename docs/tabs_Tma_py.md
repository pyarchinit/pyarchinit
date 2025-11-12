# tabs/Tma.py

## Overview

This file contains 366 documented elements.

## Classes

### pyarchinit_Tma

This class provides the implementation of the TMA (Tabella Materiali Archeologici) tab.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### add_custom_toolbar_buttons(self)

Add custom buttons between toolbar and tabWidget.

##### customize_GUI(self)

Customize the GUI elements - connect signals to slots.

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### check_and_update_schema(self)

Check and update database schema if needed for both SQLite and PostgreSQL.

##### charge_list(self)

Load combobox lists.

##### charge_records(self)

##### datestrfdate(self)

Convert date fields to string format.

##### table_set_todelete(self)

Mark tables for deletion mode.

##### msg_sito(self)

##### set_sito(self)

##### fill_fields(self, n)

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### fill_documentation_tables(self)

Fill documentation tables with data.

##### load_tma_media(self)

Load media associated with current TMA record.

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### records_equal_check(self)

##### set_LIST_REC_CORR(self)

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

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

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

##### on_pushButton_add_foto_pressed(self)

Add a photo row to the documentation table.

##### on_pushButton_remove_foto_pressed(self)

Remove selected photo row from documentation table.

##### on_pushButton_add_disegno_pressed(self)

Add a drawing row to the documentation table.

##### on_pushButton_remove_disegno_pressed(self)

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

#### Methods

##### __init__(self, row_data)

### pyarchinit_Tma

This class provides the implementation of the TMA (Tabella Materiali Archeologici) tab.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### add_custom_toolbar_buttons(self)

Add custom buttons between toolbar and tabWidget.

##### customize_GUI(self)

Customize the GUI elements - connect signals to slots.

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### check_and_update_schema(self)

Check and update database schema if needed for both SQLite and PostgreSQL.

##### charge_list(self)

Load combobox lists.

##### charge_records(self)

##### datestrfdate(self)

Convert date fields to string format.

##### table_set_todelete(self)

Mark tables for deletion mode.

##### msg_sito(self)

##### set_sito(self)

##### fill_fields(self, n)

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### fill_documentation_tables(self)

Fill documentation tables with data.

##### load_tma_media(self)

Load media associated with current TMA record.

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### records_equal_check(self)

##### set_LIST_REC_CORR(self)

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

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

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

##### on_pushButton_add_foto_pressed(self)

Add a photo row to the documentation table.

##### on_pushButton_remove_foto_pressed(self)

Remove selected photo row from documentation table.

##### on_pushButton_add_disegno_pressed(self)

Add a drawing row to the documentation table.

##### on_pushButton_remove_disegno_pressed(self)

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

#### Methods

##### __init__(self, row_data)

### pyarchinit_Tma

This class provides the implementation of the TMA (Tabella Materiali Archeologici) tab.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### add_custom_toolbar_buttons(self)

Add custom buttons between toolbar and tabWidget.

##### customize_GUI(self)

Customize the GUI elements - connect signals to slots.

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### check_and_update_schema(self)

Check and update database schema if needed for both SQLite and PostgreSQL.

##### charge_list(self)

Load combobox lists.

##### charge_records(self)

##### datestrfdate(self)

Convert date fields to string format.

##### table_set_todelete(self)

Mark tables for deletion mode.

##### msg_sito(self)

##### set_sito(self)

##### fill_fields(self, n)

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### fill_documentation_tables(self)

Fill documentation tables with data.

##### load_tma_media(self)

Load media associated with current TMA record.

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### closeEvent(self, event)

Handle form close event - stop refresh timer

##### records_equal_check(self)

##### set_LIST_REC_CORR(self)

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

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

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

##### on_pushButton_add_foto_pressed(self)

Add a photo row to the documentation table.

##### on_pushButton_remove_foto_pressed(self)

Remove selected photo row from documentation table.

##### on_pushButton_add_disegno_pressed(self)

Add a drawing row to the documentation table.

##### on_pushButton_remove_disegno_pressed(self)

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

#### Methods

##### __init__(self, row_data)

## Functions

### toggle_range()

### toggle_filters()

### toggle_label_filters()

### get_cell_value(item, col_index)

**Parameters:**
- `item`
- `col_index`

### toggle_range()

### toggle_filters()

### toggle_label_filters()

### get_cell_value(item, col_index)

**Parameters:**
- `item`
- `col_index`

### toggle_range()

### toggle_filters()

### toggle_label_filters()

### get_cell_value(item, col_index)

**Parameters:**
- `item`
- `col_index`

