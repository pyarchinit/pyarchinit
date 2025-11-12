# tabs/Struttura.py

## Overview

This file contains 336 documented elements.

## Classes

### pyarchinit_Struttura

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### loadMediaPreview(self)

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

##### generate_US(self)

##### assignTags_US(self, item)

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_assigntags_pressed(self)

##### on_done_selecting(self)

##### on_pushButton_removetags_pressed(self)

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### on_pushButton_print_pressed(self)

##### openpdfDir(self)

##### on_pushButton_open_dir_pressed(self)

##### setPathpdf(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_iniz_list(self)

##### charge_periodo_fin_list(self)

##### charge_fase_iniz_list(self)

##### charge_fase_fin_list(self)

##### charge_datazione_list(self)

##### on_pushButton_sort_pressed(self)

##### add_value_to_categoria(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### generate_list_pdf(self)

##### on_toolButton_draw_strutture_toggled(self)

##### on_pushButton_draw_struttura_pressed(self)

##### on_pushButton_view_all_st_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### datestrfdate(self)

##### table2dict(self, n)

##### setTableEnable(self, t, v)

##### empty_fields_nosite(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### set_LIST_REC_TEMP(self)

##### rec_toupdate(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_remove_row_rapporti_pressed(self)

##### on_pushButton_insert_row_materiali_pressed(self)

##### on_pushButton_remove_row_materiali_pressed(self)

##### on_pushButton_insert_row_elementi_pressed(self)

##### on_pushButton_remove_row_elementi_pressed(self)

##### on_pushButton_insert_row_misurazioni_pressed(self)

##### on_pushButton_remove_row_misurazioni_pressed(self)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### update_record(self)

### pyarchinit_Struttura

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### loadMediaPreview(self)

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

##### generate_US(self)

##### assignTags_US(self, item)

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_assigntags_pressed(self)

##### on_done_selecting(self)

##### on_pushButton_removetags_pressed(self)

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### on_pushButton_print_pressed(self)

##### openpdfDir(self)

##### on_pushButton_open_dir_pressed(self)

##### setPathpdf(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_iniz_list(self)

##### charge_periodo_fin_list(self)

##### charge_fase_iniz_list(self)

##### charge_fase_fin_list(self)

##### charge_datazione_list(self)

##### on_pushButton_sort_pressed(self)

##### add_value_to_categoria(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### generate_list_pdf(self)

##### on_toolButton_draw_strutture_toggled(self)

##### on_pushButton_draw_struttura_pressed(self)

##### on_pushButton_view_all_st_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### datestrfdate(self)

##### table2dict(self, n)

##### setTableEnable(self, t, v)

##### empty_fields_nosite(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### set_LIST_REC_TEMP(self)

##### rec_toupdate(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_remove_row_rapporti_pressed(self)

##### on_pushButton_insert_row_materiali_pressed(self)

##### on_pushButton_remove_row_materiali_pressed(self)

##### on_pushButton_insert_row_elementi_pressed(self)

##### on_pushButton_remove_row_elementi_pressed(self)

##### on_pushButton_insert_row_misurazioni_pressed(self)

##### on_pushButton_remove_row_misurazioni_pressed(self)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### update_record(self)

### pyarchinit_Struttura

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

##### loadMediaPreview(self)

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

##### generate_US(self)

##### assignTags_US(self, item)

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_assigntags_pressed(self)

##### on_done_selecting(self)

##### on_pushButton_removetags_pressed(self)

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### on_pushButton_print_pressed(self)

##### openpdfDir(self)

##### on_pushButton_open_dir_pressed(self)

##### setPathpdf(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### customize_GUI(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### charge_periodo_iniz_list(self)

##### charge_periodo_fin_list(self)

##### charge_fase_iniz_list(self)

##### charge_fase_fin_list(self)

##### charge_datazione_list(self)

##### on_pushButton_sort_pressed(self)

##### add_value_to_categoria(self)

##### on_pushButton_new_rec_pressed(self)

##### on_pushButton_save_pressed(self)

##### data_error_check(self)

##### insert_new_rec(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_search_go_pressed(self)

##### generate_list_pdf(self)

##### on_toolButton_draw_strutture_toggled(self)

##### on_pushButton_draw_struttura_pressed(self)

##### on_pushButton_view_all_st_pressed(self)

##### update_if(self, msg)

##### charge_records(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### datestrfdate(self)

##### table2dict(self, n)

##### setTableEnable(self, t, v)

##### empty_fields_nosite(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### set_rec_counter(self, t, c)

##### check_for_updates(self)

Check if current record has been modified by others

##### set_LIST_REC_TEMP(self)

##### rec_toupdate(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_remove_row_rapporti_pressed(self)

##### on_pushButton_insert_row_materiali_pressed(self)

##### on_pushButton_remove_row_materiali_pressed(self)

##### on_pushButton_insert_row_elementi_pressed(self)

##### on_pushButton_remove_row_elementi_pressed(self)

##### on_pushButton_insert_row_misurazioni_pressed(self)

##### on_pushButton_remove_row_misurazioni_pressed(self)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### update_record(self)

## Functions

### r_list()

### r_id()

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

### r_list()

### r_id()

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

### r_list()

### r_id()

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

