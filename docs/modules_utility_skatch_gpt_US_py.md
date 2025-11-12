# modules/utility/skatch_gpt_US.py

## Overview

This file contains 252 documented elements.

## Classes

### Worker

**Inherits from**: QThread

#### Methods

##### __init__(self, headers, params, url, is_image, image_width, image_height)

##### run(self)

### GPTWindow

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, selected_images, dbmanager, main_class)

##### analyze_selected_images(self)

##### extract_and_display_links(self, response)

##### set_icon(self, icon_path)

##### start_worker(self, headers, params, url, is_image)

##### apikey_claude(self)

##### apikey_gpt(self)

##### ask_gpt4(self, prompt, apikey, file_path, is_image)

##### ask_claude(self, prompt, apikey, file_path, is_image)

##### manual_input(self, missing_fields)

##### check_existing_record(self, info)

##### is_image_associated(self, file_path, record_id)

##### scketchgpt(self)

##### check_existing_record_matrix(self, info)

##### is_harris_matrix(self, prompt)

##### go_to_us_record(self, sito, area, us, unita_tipo)

##### image_already_associated(self, file_path, record_id)

##### process_ai_response(self, response_text)

##### extract_us_list(self, text)

##### extract_relations_from_text(self, text, sito, area)

##### extract_info_from_response_matrix(self, response)

##### extract_info_from_response(self, response)

##### extract_missing_info(self, response, info)

##### extract_missing_info_matrix(self, response, info)

##### check_manual_input(self, info)

##### extract_info_generic(self, text, keywords)

##### confirm_information(self, info, file_path)

##### confirm_information_matrix(self, info, file_path)

##### create_new_record_matrix(self, info)

##### create_new_record(self, info)

##### db_search_check(self, table_class, field, value)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### associate_image_with_record(self, file_path, record_id)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_US(self)

##### update_icon_list_widget(self, file_path, record_id)

##### ask_sketch(self, prompt, apikey, file_path)

##### extract_text_from_file(self, file_path)

##### extract_text_from_pdf(self, file_path)

##### extract_text_from_csv(self, file_path)

##### extract_text_from_docx(self, file_path)

##### save_corrected_file(self, original_file_path, original_lines, corrected_text)

##### find_closest_match(self, corrected_line, original_lines)

##### find_closest_match_pdf(self, corrected_line, original_lines)

##### save_new_pdf_with_corrections(self, original_file_path, save_path, corrected_lines)

##### save_corrected_csv(self, save_path, corrected_text)

##### save_corrected_docx(self, original_file_path, save_path, corrected_text)

##### ask_doc(self, prompt, apikey, file_path)

##### ask_doc_with_claude(self, prompt, apikey, file_path)

##### update_progress(self, progress)

##### update_content(self, content)

##### update_tokens_used(self, tokens_used, total_cost)

##### docchgpt(self)

### Worker

**Inherits from**: QThread

#### Methods

##### __init__(self, headers, params, url, is_image, image_width, image_height)

##### run(self)

### GPTWindow

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, selected_images, dbmanager, main_class)

##### analyze_selected_images(self)

##### extract_and_display_links(self, response)

##### set_icon(self, icon_path)

##### start_worker(self, headers, params, url, is_image)

##### apikey_claude(self)

##### apikey_gpt(self)

##### ask_gpt4(self, prompt, apikey, file_path, is_image)

##### ask_claude(self, prompt, apikey, file_path, is_image)

##### manual_input(self, missing_fields)

##### check_existing_record(self, info)

##### is_image_associated(self, file_path, record_id)

##### scketchgpt(self)

##### check_existing_record_matrix(self, info)

##### is_harris_matrix(self, prompt)

##### go_to_us_record(self, sito, area, us, unita_tipo)

##### image_already_associated(self, file_path, record_id)

##### process_ai_response(self, response_text)

##### extract_us_list(self, text)

##### extract_relations_from_text(self, text, sito, area)

##### extract_info_from_response_matrix(self, response)

##### extract_info_from_response(self, response)

##### extract_missing_info(self, response, info)

##### extract_missing_info_matrix(self, response, info)

##### check_manual_input(self, info)

##### extract_info_generic(self, text, keywords)

##### confirm_information(self, info, file_path)

##### confirm_information_matrix(self, info, file_path)

##### create_new_record_matrix(self, info)

##### create_new_record(self, info)

##### db_search_check(self, table_class, field, value)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### associate_image_with_record(self, file_path, record_id)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_US(self)

##### update_icon_list_widget(self, file_path, record_id)

##### ask_sketch(self, prompt, apikey, file_path)

##### extract_text_from_file(self, file_path)

##### extract_text_from_pdf(self, file_path)

##### extract_text_from_csv(self, file_path)

##### extract_text_from_docx(self, file_path)

##### save_corrected_file(self, original_file_path, original_lines, corrected_text)

##### find_closest_match(self, corrected_line, original_lines)

##### find_closest_match_pdf(self, corrected_line, original_lines)

##### save_new_pdf_with_corrections(self, original_file_path, save_path, corrected_lines)

##### save_corrected_csv(self, save_path, corrected_text)

##### save_corrected_docx(self, original_file_path, save_path, corrected_text)

##### ask_doc(self, prompt, apikey, file_path)

##### ask_doc_with_claude(self, prompt, apikey, file_path)

##### update_progress(self, progress)

##### update_content(self, content)

##### update_tokens_used(self, tokens_used, total_cost)

##### docchgpt(self)

### Worker

**Inherits from**: QThread

#### Methods

##### __init__(self, headers, params, url, is_image, image_width, image_height)

##### run(self)

### GPTWindow

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, selected_images, dbmanager, main_class)

##### analyze_selected_images(self)

##### extract_and_display_links(self, response)

##### set_icon(self, icon_path)

##### start_worker(self, headers, params, url, is_image)

##### apikey_claude(self)

##### apikey_gpt(self)

##### ask_gpt4(self, prompt, apikey, file_path, is_image)

##### ask_claude(self, prompt, apikey, file_path, is_image)

##### manual_input(self, missing_fields)

##### check_existing_record(self, info)

##### is_image_associated(self, file_path, record_id)

##### scketchgpt(self)

##### check_existing_record_matrix(self, info)

##### is_harris_matrix(self, prompt)

##### go_to_us_record(self, sito, area, us, unita_tipo)

##### image_already_associated(self, file_path, record_id)

##### process_ai_response(self, response_text)

##### extract_us_list(self, text)

##### extract_relations_from_text(self, text, sito, area)

##### extract_info_from_response_matrix(self, response)

##### extract_info_from_response(self, response)

##### extract_missing_info(self, response, info)

##### extract_missing_info_matrix(self, response, info)

##### check_manual_input(self, info)

##### extract_info_generic(self, text, keywords)

##### confirm_information(self, info, file_path)

##### confirm_information_matrix(self, info, file_path)

##### create_new_record_matrix(self, info)

##### create_new_record(self, info)

##### db_search_check(self, table_class, field, value)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### associate_image_with_record(self, file_path, record_id)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_US(self)

##### update_icon_list_widget(self, file_path, record_id)

##### ask_sketch(self, prompt, apikey, file_path)

##### extract_text_from_file(self, file_path)

##### extract_text_from_pdf(self, file_path)

##### extract_text_from_csv(self, file_path)

##### extract_text_from_docx(self, file_path)

##### save_corrected_file(self, original_file_path, original_lines, corrected_text)

##### find_closest_match(self, corrected_line, original_lines)

##### find_closest_match_pdf(self, corrected_line, original_lines)

##### save_new_pdf_with_corrections(self, original_file_path, save_path, corrected_lines)

##### save_corrected_csv(self, save_path, corrected_text)

##### save_corrected_docx(self, original_file_path, save_path, corrected_text)

##### ask_doc(self, prompt, apikey, file_path)

##### ask_doc_with_claude(self, prompt, apikey, file_path)

##### update_progress(self, progress)

##### update_content(self, content)

##### update_tokens_used(self, tokens_used, total_cost)

##### docchgpt(self)

### Worker

**Inherits from**: QThread

#### Methods

##### __init__(self, headers, params, url, is_image, image_width, image_height)

##### run(self)

### GPTWindow

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, selected_images, dbmanager, main_class)

##### analyze_selected_images(self)

##### extract_and_display_links(self, response)

##### set_icon(self, icon_path)

##### start_worker(self, headers, params, url, is_image)

##### apikey_claude(self)

##### apikey_gpt(self)

##### ask_gpt4(self, prompt, apikey, file_path, is_image)

##### ask_claude(self, prompt, apikey, file_path, is_image)

##### manual_input(self, missing_fields)

##### check_existing_record(self, info)

##### is_image_associated(self, file_path, record_id)

##### scketchgpt(self)

##### check_existing_record_matrix(self, info)

##### is_harris_matrix(self, prompt)

##### go_to_us_record(self, sito, area, us, unita_tipo)

##### image_already_associated(self, file_path, record_id)

##### process_ai_response(self, response_text)

##### extract_us_list(self, text)

##### extract_relations_from_text(self, text, sito, area)

##### extract_info_from_response_matrix(self, response)

##### extract_info_from_response(self, response)

##### extract_missing_info(self, response, info)

##### extract_missing_info_matrix(self, response, info)

##### check_manual_input(self, info)

##### extract_info_generic(self, text, keywords)

##### confirm_information(self, info, file_path)

##### confirm_information_matrix(self, info, file_path)

##### create_new_record_matrix(self, info)

##### create_new_record(self, info)

##### db_search_check(self, table_class, field, value)

##### insert_record_media(self, mediatype, filename, filetype, filepath)

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

##### associate_image_with_record(self, file_path, record_id)

##### insert_mediaToEntity_rec(self, id_entity, entity_type, table_name, id_media, filepath, media_name)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### generate_US(self)

##### update_icon_list_widget(self, file_path, record_id)

##### ask_sketch(self, prompt, apikey, file_path)

##### extract_text_from_file(self, file_path)

##### extract_text_from_pdf(self, file_path)

##### extract_text_from_csv(self, file_path)

##### extract_text_from_docx(self, file_path)

##### save_corrected_file(self, original_file_path, original_lines, corrected_text)

##### find_closest_match(self, corrected_line, original_lines)

##### find_closest_match_pdf(self, corrected_line, original_lines)

##### save_new_pdf_with_corrections(self, original_file_path, save_path, corrected_lines)

##### save_corrected_csv(self, save_path, corrected_text)

##### save_corrected_docx(self, original_file_path, save_path, corrected_text)

##### ask_doc(self, prompt, apikey, file_path)

##### ask_doc_with_claude(self, prompt, apikey, file_path)

##### update_progress(self, progress)

##### update_content(self, content)

##### update_tokens_used(self, tokens_used, total_cost)

##### docchgpt(self)

## Functions

### get_image_metadata(file_path)

**Parameters:**
- `file_path`

### encode_file(file_path)

**Parameters:**
- `file_path`

### get_file_type(file_path)

**Parameters:**
- `file_path`

### extract_video_frames(file_path, num_frames)

**Parameters:**
- `file_path`
- `num_frames`

### get_image_metadata(file_path)

**Parameters:**
- `file_path`

### encode_file(file_path)

**Parameters:**
- `file_path`

### get_file_type(file_path)

**Parameters:**
- `file_path`

### extract_video_frames(file_path, num_frames)

**Parameters:**
- `file_path`
- `num_frames`

### get_image_metadata(file_path)

**Parameters:**
- `file_path`

### encode_file(file_path)

**Parameters:**
- `file_path`

### get_file_type(file_path)

**Parameters:**
- `file_path`

### extract_video_frames(file_path, num_frames)

**Parameters:**
- `file_path`
- `num_frames`

### get_image_metadata(file_path)

**Parameters:**
- `file_path`

### encode_file(file_path)

**Parameters:**
- `file_path`

### get_file_type(file_path)

**Parameters:**
- `file_path`

### extract_video_frames(file_path, num_frames)

**Parameters:**
- `file_path`
- `num_frames`

