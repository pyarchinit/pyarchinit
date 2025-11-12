# tabs/Inv_Materiali.py

## Overview

This file contains 444 documented elements.

## Classes

### pyarchinit_Inventario_reperti

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### get_images_for_entities(self, entity_ids, log_signal)

##### setnone(self)

##### on_pushButtonQuant_pressed(self)

##### parameter_quant_creator(self, par_list, n_rec)

##### plot_chart(self, d, t, yl)

##### torta_chart(self, d, t, yl)

##### matrice_chart(self, d, t, yl)

##### on_pushButton_connect_pressed(self)

##### loadMapPreview(self, mode)

##### customize_gui(self)

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

##### connect_p(self)

##### sketchgpt(self)

##### loadMediaPreview(self, mode)

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### numero_invetario(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonPreviewMedia_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### on_toolButtonGis_toggled(self)

##### generate_list_foto(self)

##### generate_list(self)

##### generate_list_pdf(self)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### generate_el_casse_pdf(self, sito)

##### on_pushButton_esporta_a5_pressed(self)

Esporta la scheda inventario in formato A5 con immagine

##### record_to_list(self, record)

Converte un record inventario in lista per il PDF generator

##### exp_pdf_elenco_casse_main_experimental(self)

##### index_elenco_casse(self)

##### us_list_from_casse(self, sito, cassa)

##### strutture_list_from_us(self, sito, area, us)

##### data_error_check(self)

##### insert_new_rec(self)

##### on_pushButton_insert_row_elementi_pressed(self)

##### on_pushButton_remove_row_elementi_pressed(self)

##### on_pushButton_insert_row_misure_pressed(self)

##### on_pushButton_remove_row_misure_pressed(self)

##### on_pushButton_insert_row_tecnologie_pressed(self)

##### on_pushButton_remove_row_tecnologie_pressed(self)

##### on_pushButton_insert_row_rif_biblio_pressed(self)

##### on_pushButton_remove_row_rif_biblio_pressed(self)

##### on_pushButton_insert_row_negativi_pressed(self)

##### on_pushButton_remove_row_negativi_pressed(self)

##### on_pushButton_insert_row_diapo_pressed(self)

##### on_pushButton_remove_row_diapo_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_2_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### update_tma_inventario_field(self, sito, n_reperto, action)

Update TMA inventario field when n_reperto is added or removed

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_tot_fram_pressed(self)

##### update_tot_frammenti(self, c)

##### update_if(self, msg)

##### update_record(self)

##### charge_struttura(self)

##### rec_toupdate(self)

##### charge_records(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### empty_fields_nosite(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### setTableEnable(self, t, v)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### testing(self, name_file, message)

##### on_pushButton_open_dir_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### on_pushButton_export_ica_pressed(self)

##### check_for_updates(self)

Check if current record has been modified by others

### pyarchinit_Inventario_reperti

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### get_images_for_entities(self, entity_ids, log_signal)

##### setnone(self)

##### on_pushButtonQuant_pressed(self)

##### parameter_quant_creator(self, par_list, n_rec)

##### plot_chart(self, d, t, yl)

##### torta_chart(self, d, t, yl)

##### matrice_chart(self, d, t, yl)

##### on_pushButton_connect_pressed(self)

##### loadMapPreview(self, mode)

##### customize_gui(self)

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

##### connect_p(self)

##### sketchgpt(self)

##### loadMediaPreview(self, mode)

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### numero_invetario(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonPreviewMedia_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### on_toolButtonGis_toggled(self)

##### generate_list_foto(self)

##### generate_list(self)

##### generate_list_pdf(self)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### generate_el_casse_pdf(self, sito)

##### on_pushButton_esporta_a5_pressed(self)

Esporta la scheda inventario in formato A5 con immagine

##### record_to_list(self, record)

Converte un record inventario in lista per il PDF generator

##### exp_pdf_elenco_casse_main_experimental(self)

##### index_elenco_casse(self)

##### us_list_from_casse(self, sito, cassa)

##### strutture_list_from_us(self, sito, area, us)

##### data_error_check(self)

##### insert_new_rec(self)

##### on_pushButton_insert_row_elementi_pressed(self)

##### on_pushButton_remove_row_elementi_pressed(self)

##### on_pushButton_insert_row_misure_pressed(self)

##### on_pushButton_remove_row_misure_pressed(self)

##### on_pushButton_insert_row_tecnologie_pressed(self)

##### on_pushButton_remove_row_tecnologie_pressed(self)

##### on_pushButton_insert_row_rif_biblio_pressed(self)

##### on_pushButton_remove_row_rif_biblio_pressed(self)

##### on_pushButton_insert_row_negativi_pressed(self)

##### on_pushButton_remove_row_negativi_pressed(self)

##### on_pushButton_insert_row_diapo_pressed(self)

##### on_pushButton_remove_row_diapo_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_2_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### update_tma_inventario_field(self, sito, n_reperto, action)

Update TMA inventario field when n_reperto is added or removed

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_tot_fram_pressed(self)

##### update_tot_frammenti(self, c)

##### update_if(self, msg)

##### update_record(self)

##### charge_struttura(self)

##### rec_toupdate(self)

##### charge_records(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### empty_fields_nosite(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### setTableEnable(self, t, v)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### testing(self, name_file, message)

##### on_pushButton_open_dir_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### on_pushButton_export_ica_pressed(self)

##### check_for_updates(self)

Check if current record has been modified by others

### pyarchinit_Inventario_reperti

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### get_images_for_entities(self, entity_ids, log_signal)

##### setnone(self)

##### on_pushButtonQuant_pressed(self)

##### parameter_quant_creator(self, par_list, n_rec)

##### plot_chart(self, d, t, yl)

##### torta_chart(self, d, t, yl)

##### matrice_chart(self, d, t, yl)

##### on_pushButton_connect_pressed(self)

##### loadMapPreview(self, mode)

##### customize_gui(self)

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

##### connect_p(self)

##### sketchgpt(self)

##### loadMediaPreview(self, mode)

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### numero_invetario(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonPreviewMedia_toggled(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### on_toolButtonGis_toggled(self)

##### generate_list_foto(self)

##### generate_list(self)

##### generate_list_pdf(self)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### generate_el_casse_pdf(self, sito)

##### on_pushButton_esporta_a5_pressed(self)

Esporta la scheda inventario in formato A5 con immagine

##### record_to_list(self, record)

Converte un record inventario in lista per il PDF generator

##### exp_pdf_elenco_casse_main_experimental(self)

##### index_elenco_casse(self)

##### us_list_from_casse(self, sito, cassa)

##### strutture_list_from_us(self, sito, area, us)

##### data_error_check(self)

##### insert_new_rec(self)

##### on_pushButton_insert_row_elementi_pressed(self)

##### on_pushButton_remove_row_elementi_pressed(self)

##### on_pushButton_insert_row_misure_pressed(self)

##### on_pushButton_remove_row_misure_pressed(self)

##### on_pushButton_insert_row_tecnologie_pressed(self)

##### on_pushButton_remove_row_tecnologie_pressed(self)

##### on_pushButton_insert_row_rif_biblio_pressed(self)

##### on_pushButton_remove_row_rif_biblio_pressed(self)

##### on_pushButton_insert_row_negativi_pressed(self)

##### on_pushButton_remove_row_negativi_pressed(self)

##### on_pushButton_insert_row_diapo_pressed(self)

##### on_pushButton_remove_row_diapo_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_2_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### update_tma_inventario_field(self, sito, n_reperto, action)

Update TMA inventario field when n_reperto is added or removed

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### on_pushButton_tot_fram_pressed(self)

##### update_tot_frammenti(self, c)

##### update_if(self, msg)

##### update_record(self)

##### charge_struttura(self)

##### rec_toupdate(self)

##### charge_records(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### datestrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, table_name, data)

Insert data into a table widget
:param table_name: name of the table widget
:param data: data to insert (list of lists or list of dictionaries)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### empty_fields_nosite(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### setTableEnable(self, t, v)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### testing(self, name_file, message)

##### on_pushButton_open_dir_pressed(self)

##### setPathpdf(self)

##### openpdfDir(self)

##### on_pushButton_export_ica_pressed(self)

##### check_for_updates(self)

Check if current record has been modified by others

## Functions

### log(message, level)

**Parameters:**
- `message`
- `level`

### r_id()

### update_done_button()

### r_list()

### process_file_path(file_path)

**Parameters:**
- `file_path`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### add_debug_message(message, important)

**Parameters:**
- `message`
- `important`

### mouse_click_callback(obj, event)

**Parameters:**
- `obj`
- `event`

### toggle_instructions()

### toggle_measure()

### on_left_click(picked_point)

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

**Parameters:**
- `coord1`
- `coord2`

### measure_distance(point1, point2)

**Parameters:**
- `point1`
- `point2`

### clear_measurements()

### export_image()

### get_visible_faces(plotter, mesh)

**Parameters:**
- `plotter`
- `mesh`

### edge_visibility(edge, visible_faces)

**Parameters:**
- `edge`
- `visible_faces`

### calculate_label_position(p1, p2, offset_factor)

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

### toggle_bounding_box_measures()

### camera_changed(obj, event)

**Parameters:**
- `obj`
- `event`

### reset_view()

### change_view(direction)

**Parameters:**
- `direction`

### process_file_path(file_path)

**Parameters:**
- `file_path`

### show_image(file_path)

**Parameters:**
- `file_path`

### show_video(file_path)

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### log(message, level)

**Parameters:**
- `message`
- `level`

### r_id()

### update_done_button()

### r_list()

### process_file_path(file_path)

**Parameters:**
- `file_path`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### add_debug_message(message, important)

**Parameters:**
- `message`
- `important`

### mouse_click_callback(obj, event)

**Parameters:**
- `obj`
- `event`

### toggle_instructions()

### toggle_measure()

### on_left_click(picked_point)

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

**Parameters:**
- `coord1`
- `coord2`

### measure_distance(point1, point2)

**Parameters:**
- `point1`
- `point2`

### clear_measurements()

### export_image()

### get_visible_faces(plotter, mesh)

**Parameters:**
- `plotter`
- `mesh`

### edge_visibility(edge, visible_faces)

**Parameters:**
- `edge`
- `visible_faces`

### calculate_label_position(p1, p2, offset_factor)

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

### toggle_bounding_box_measures()

### camera_changed(obj, event)

**Parameters:**
- `obj`
- `event`

### reset_view()

### change_view(direction)

**Parameters:**
- `direction`

### process_file_path(file_path)

**Parameters:**
- `file_path`

### show_image(file_path)

**Parameters:**
- `file_path`

### show_video(file_path)

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### log(message, level)

**Parameters:**
- `message`
- `level`

### r_id()

### update_done_button()

### r_list()

### process_file_path(file_path)

**Parameters:**
- `file_path`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### add_debug_message(message, important)

**Parameters:**
- `message`
- `important`

### mouse_click_callback(obj, event)

**Parameters:**
- `obj`
- `event`

### toggle_instructions()

### toggle_measure()

### on_left_click(picked_point)

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

**Parameters:**
- `coord1`
- `coord2`

### measure_distance(point1, point2)

**Parameters:**
- `point1`
- `point2`

### clear_measurements()

### export_image()

### get_visible_faces(plotter, mesh)

**Parameters:**
- `plotter`
- `mesh`

### edge_visibility(edge, visible_faces)

**Parameters:**
- `edge`
- `visible_faces`

### calculate_label_position(p1, p2, offset_factor)

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

### toggle_bounding_box_measures()

### camera_changed(obj, event)

**Parameters:**
- `obj`
- `event`

### reset_view()

### change_view(direction)

**Parameters:**
- `direction`

### process_file_path(file_path)

**Parameters:**
- `file_path`

### show_image(file_path)

**Parameters:**
- `file_path`

### show_video(file_path)

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

