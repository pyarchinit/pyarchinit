# tabs/Tomba.py

## Overview

This file contains 288 documented elements.

## Classes

### pyarchinit_Tomba

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### numero_invetario(self)

##### loadCorredolist(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### loadMapPreview(self, mode)

##### dropEvent(self, event)

##### dragEnterEvent(self, event)

##### dragMoveEvent(self, event)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_reperti(self)

##### assignTags_reperti(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_removetags_pressed(self)

##### on_pushButton_all_images_pressed(self)

##### load_images(self, filter_text)

##### update_page_labels(self)

##### go_to_previous_page(self)

##### go_to_next_page(self)

##### on_page_label_clicked(self, page, _)

##### filter_items(self)

##### on_done_selecting_all(self)

##### update_list_widget_item(self, item)

##### fill_iconListWidget(self)

##### loadMediaPreview(self)

##### openWide_image(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_iniz_list(self)

This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.

##### charge_periodo_fin_list(self)

This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.

##### charge_fase_iniz_list(self)

This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.

##### charge_fase_fin_list(self)

This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.

##### charge_datazione_list(self)

This function charges the 'Datazione' combobox with the values from the 'Periodizzazione' table.

##### update_dating(self)

This function updates the 'Dating' field for all US records in the database.

##### charge_struttura_nr(self)

##### charge_struttura_list(self)

##### charge_individuo_list(self)

##### charge_oggetti_esterno_list(self)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_showSelectedFeatures_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### on_pushButton_insert_row_corredo_pressed(self)

##### on_pushButton_remove_row_corredo_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_showLayer_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### generate_list_pdf(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields_nosite(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### setTableEnable(self, t, v)

##### testing(self, name_file, message)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### on_pushButton_open_dir_pressed(self)

##### check_for_updates(self)

Check if current record has been modified by others

### pyarchinit_Tomba

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### numero_invetario(self)

##### loadCorredolist(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### loadMapPreview(self, mode)

##### dropEvent(self, event)

##### dragEnterEvent(self, event)

##### dragMoveEvent(self, event)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_reperti(self)

##### assignTags_reperti(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_removetags_pressed(self)

##### on_pushButton_all_images_pressed(self)

##### load_images(self, filter_text)

##### update_page_labels(self)

##### go_to_previous_page(self)

##### go_to_next_page(self)

##### on_page_label_clicked(self, page, _)

##### filter_items(self)

##### on_done_selecting_all(self)

##### update_list_widget_item(self, item)

##### fill_iconListWidget(self)

##### loadMediaPreview(self)

##### openWide_image(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_iniz_list(self)

This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.

##### charge_periodo_fin_list(self)

This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.

##### charge_fase_iniz_list(self)

This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.

##### charge_fase_fin_list(self)

This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.

##### charge_datazione_list(self)

This function charges the 'Datazione' combobox with the values from the 'Periodizzazione' table.

##### update_dating(self)

This function updates the 'Dating' field for all US records in the database.

##### charge_struttura_nr(self)

##### charge_struttura_list(self)

##### charge_individuo_list(self)

##### charge_oggetti_esterno_list(self)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_showSelectedFeatures_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### on_pushButton_insert_row_corredo_pressed(self)

##### on_pushButton_remove_row_corredo_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_showLayer_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### generate_list_pdf(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields_nosite(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### setTableEnable(self, t, v)

##### testing(self, name_file, message)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### on_pushButton_open_dir_pressed(self)

##### check_for_updates(self)

Check if current record has been modified by others

### pyarchinit_Tomba

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### numero_invetario(self)

##### loadCorredolist(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### loadMapPreview(self, mode)

##### dropEvent(self, event)

##### dragEnterEvent(self, event)

##### dragMoveEvent(self, event)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### delete_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_reperti(self)

##### assignTags_reperti(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_removetags_pressed(self)

##### on_pushButton_all_images_pressed(self)

##### load_images(self, filter_text)

##### update_page_labels(self)

##### go_to_previous_page(self)

##### go_to_next_page(self)

##### on_page_label_clicked(self, page, _)

##### filter_items(self)

##### on_done_selecting_all(self)

##### update_list_widget_item(self, item)

##### fill_iconListWidget(self)

##### loadMediaPreview(self)

##### openWide_image(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_iniz_list(self)

This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.

##### charge_periodo_fin_list(self)

This function charges the 'Periodo' combobox with the values from the 'Periodizzazione' table.

##### charge_fase_iniz_list(self)

This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.

##### charge_fase_fin_list(self)

This function charges the 'Fase' combobox with the values from the 'Periodizzazione' table.

##### charge_datazione_list(self)

This function charges the 'Datazione' combobox with the values from the 'Periodizzazione' table.

##### update_dating(self)

This function updates the 'Dating' field for all US records in the database.

##### charge_struttura_nr(self)

##### charge_struttura_list(self)

##### charge_individuo_list(self)

##### charge_oggetti_esterno_list(self)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_showSelectedFeatures_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### on_pushButton_insert_row_corredo_pressed(self)

##### on_pushButton_remove_row_corredo_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_showLayer_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### generate_list_pdf(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### charge_records(self)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields_nosite(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### setTableEnable(self, t, v)

##### testing(self, name_file, message)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### on_pushButton_open_dir_pressed(self)

##### check_for_updates(self)

Check if current record has been modified by others

## Functions

### r_id()

### update_done_button()

### r_list()

### r_id()

### update_done_button()

### r_list()

### r_id()

### update_done_button()

### r_list()

