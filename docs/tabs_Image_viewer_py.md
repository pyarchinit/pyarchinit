# tabs/Image_viewer.py

## Overview

This file contains 285 documented elements.

## Classes

### Main

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self)

##### remove_all(self)

##### on_pushButton_gptsketch_pressed(self)

##### split_2(self)

##### split_1(self)

##### customize_gui(self)

##### valuechange(self, value)

##### charge_list(self)

##### charge_sigla_list(self)

##### charge_nr_st_list(self)

##### charge_us_list(self)

##### charge_area_list(self)

##### connection(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_go_pressed(self)

##### getDirectoryVideo(self)

##### getDirectory(self)

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

##### db_search_check(self, table_class, field, value)

##### on_pushButton_sort_pressed(self)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

remove row into a table based on table_name

##### remove_rowall(self, table_name)

remove row into a table based on table_name

##### openWide_image(self)

##### charge_sito_list(self)

##### charge_area_us_list(self)

##### charge_us_us_list(self)

##### charge_sigla_us_list(self)

##### charge_nr_us_list(self)

##### generate_US(self)

##### remove_US(self)

##### generate_Pottery(self)

##### remove_pottery(self)

##### generate_Reperti(self)

##### remove_reperti(self)

##### generate_Tombe(self)

##### remove_Tombe(self)

##### generate_Tombe_2(self)

##### remove_Tombe_2(self)

##### table2dict(self, n)

##### charge_data(self)

##### clear_thumb_images(self)

##### open_images(self)

##### on_pushButton_dir_video_pressed(self)

##### on_pushButton_chose_dir_pressed(self)

##### on_pushButton_addRow_US_pressed(self)

##### on_pushButton_removeRow_US_pressed(self)

##### on_pushButton_addRow_POT_pressed(self)

##### on_pushButton_removeRow_POT_pressed(self)

##### on_pushButton_addRow_MAT_pressed(self)

##### on_pushButton_removeRow_MAT_pressed(self)

##### on_pushButton_addRow_tomba_pressed(self)

##### on_pushButton_removeRow_tomba_pressed(self)

##### on_pushButton_addRow_tomba_2_pressed(self)

##### on_pushButton_removeRow_tomba__2_pressed(self)

##### on_pushButton_assignTags_US_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_POT_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_MAT_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_tomba_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_tomba_2_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### remove_img1(self, path, img_name)

##### remove_img2(self, path, img_name)

##### on_pushButton_remove_thumb_pressed(self)

##### on_pushButton_remove_tags_pressed(self)

##### on_pushButton_remove_alltag_pressed(self)

##### on_pushButton_openMedia_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### view_num_rec(self)

##### on_toolButton_tags_on_off_clicked(self)

##### open_tags(self)

##### charge_records(self)

##### datestrfdate(self)

##### yearstrfdate(self)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### setTableEnable(self, t, v)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### tableInsertData(self, t, d)

Set the value into alls Grid

### Main

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self)

##### remove_all(self)

##### on_pushButton_gptsketch_pressed(self)

##### split_2(self)

##### split_1(self)

##### customize_gui(self)

##### valuechange(self, value)

##### charge_list(self)

##### charge_sigla_list(self)

##### charge_nr_st_list(self)

##### charge_us_list(self)

##### charge_area_list(self)

##### connection(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_go_pressed(self)

##### getDirectoryVideo(self)

##### getDirectory(self)

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

##### db_search_check(self, table_class, field, value)

##### on_pushButton_sort_pressed(self)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

remove row into a table based on table_name

##### remove_rowall(self, table_name)

remove row into a table based on table_name

##### openWide_image(self)

##### charge_sito_list(self)

##### charge_area_us_list(self)

##### charge_us_us_list(self)

##### charge_sigla_us_list(self)

##### charge_nr_us_list(self)

##### generate_US(self)

##### remove_US(self)

##### generate_Pottery(self)

##### remove_pottery(self)

##### generate_Reperti(self)

##### remove_reperti(self)

##### generate_Tombe(self)

##### remove_Tombe(self)

##### generate_Tombe_2(self)

##### remove_Tombe_2(self)

##### table2dict(self, n)

##### charge_data(self)

##### clear_thumb_images(self)

##### open_images(self)

##### on_pushButton_dir_video_pressed(self)

##### on_pushButton_chose_dir_pressed(self)

##### on_pushButton_addRow_US_pressed(self)

##### on_pushButton_removeRow_US_pressed(self)

##### on_pushButton_addRow_POT_pressed(self)

##### on_pushButton_removeRow_POT_pressed(self)

##### on_pushButton_addRow_MAT_pressed(self)

##### on_pushButton_removeRow_MAT_pressed(self)

##### on_pushButton_addRow_tomba_pressed(self)

##### on_pushButton_removeRow_tomba_pressed(self)

##### on_pushButton_addRow_tomba_2_pressed(self)

##### on_pushButton_removeRow_tomba__2_pressed(self)

##### on_pushButton_assignTags_US_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_POT_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_MAT_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_tomba_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_tomba_2_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### remove_img1(self, path, img_name)

##### remove_img2(self, path, img_name)

##### on_pushButton_remove_thumb_pressed(self)

##### on_pushButton_remove_tags_pressed(self)

##### on_pushButton_remove_alltag_pressed(self)

##### on_pushButton_openMedia_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### view_num_rec(self)

##### on_toolButton_tags_on_off_clicked(self)

##### open_tags(self)

##### charge_records(self)

##### datestrfdate(self)

##### yearstrfdate(self)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### setTableEnable(self, t, v)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### tableInsertData(self, t, d)

Set the value into alls Grid

### Main

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self)

##### remove_all(self)

##### on_pushButton_gptsketch_pressed(self)

##### split_2(self)

##### split_1(self)

##### customize_gui(self)

##### valuechange(self, value)

##### charge_list(self)

##### charge_sigla_list(self)

##### charge_nr_st_list(self)

##### charge_us_list(self)

##### charge_area_list(self)

##### connection(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_go_pressed(self)

##### getDirectoryVideo(self)

##### getDirectory(self)

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

##### db_search_check(self, table_class, field, value)

##### on_pushButton_sort_pressed(self)

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

remove row into a table based on table_name

##### remove_rowall(self, table_name)

remove row into a table based on table_name

##### openWide_image(self)

##### charge_sito_list(self)

##### charge_area_us_list(self)

##### charge_us_us_list(self)

##### charge_sigla_us_list(self)

##### charge_nr_us_list(self)

##### generate_US(self)

##### remove_US(self)

##### generate_Pottery(self)

##### remove_pottery(self)

##### generate_Reperti(self)

##### remove_reperti(self)

##### generate_Tombe(self)

##### remove_Tombe(self)

##### generate_Tombe_2(self)

##### remove_Tombe_2(self)

##### table2dict(self, n)

##### charge_data(self)

##### clear_thumb_images(self)

##### open_images(self)

##### on_pushButton_dir_video_pressed(self)

##### on_pushButton_chose_dir_pressed(self)

##### on_pushButton_addRow_US_pressed(self)

##### on_pushButton_removeRow_US_pressed(self)

##### on_pushButton_addRow_POT_pressed(self)

##### on_pushButton_removeRow_POT_pressed(self)

##### on_pushButton_addRow_MAT_pressed(self)

##### on_pushButton_removeRow_MAT_pressed(self)

##### on_pushButton_addRow_tomba_pressed(self)

##### on_pushButton_removeRow_tomba_pressed(self)

##### on_pushButton_addRow_tomba_2_pressed(self)

##### on_pushButton_removeRow_tomba__2_pressed(self)

##### on_pushButton_assignTags_US_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_POT_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_MAT_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_tomba_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### on_pushButton_assignTags_tomba_2_pressed(self)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### remove_img1(self, path, img_name)

##### remove_img2(self, path, img_name)

##### on_pushButton_remove_thumb_pressed(self)

##### on_pushButton_remove_tags_pressed(self)

##### on_pushButton_remove_alltag_pressed(self)

##### on_pushButton_openMedia_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### view_num_rec(self)

##### on_toolButton_tags_on_off_clicked(self)

##### open_tags(self)

##### charge_records(self)

##### datestrfdate(self)

##### yearstrfdate(self)

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### empty_fields(self)

##### fill_fields(self, n)

##### setComboBoxEnable(self, f, v)

##### setComboBoxEditable(self, f, n)

##### setTableEnable(self, t, v)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### tableInsertData(self, t, d)

Set the value into alls Grid

