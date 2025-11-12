# tabs/US_USM.py

## Overview

This file contains 1401 documented elements.

## Classes

### CollapsibleSection

**Inherits from**: QWidget

#### Methods

##### __init__(self, title, parent)

##### toggle_content(self)

##### add_widget(self, widget)

##### add_layout(self, layout)

### ReportGeneratorDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### get_selected_language(self)

Get the selected output language

##### get_streaming_enabled(self)

Get whether streaming is enabled

##### validate_data(self)

Esegue la validazione dei dati

##### get_us_data(self)

Recupera i dati delle US dal database

##### get_materials_data(self)

Recupera i dati dei materiali dal database

##### get_pottery_data(self)

Recupera i dati della ceramica dal database

##### get_tma_data(self)

Recupera i dati TMA dal database

##### get_selected_tables(self)

Get list of checked tables

##### get_year_filter(self)

Get year filter value

##### get_us_range(self)

Get US range values

### CheckableComboBox

**Inherits from**: QComboBox

#### Methods

##### __init__(self)

##### add_item(self, text)

Add a checkable item to the combo box

##### items_checked(self)

Get list of checked items

##### handle_item_pressed(self, index)

Handle item check/uncheck

### ReportDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, content, parent)

##### update_content(self, new_content)

Update the report content

##### append_streaming_token(self, token)

Append a streaming token to the content

##### handle_mouse_press(self, event)

Gestisce il click del mouse nel text edit

##### log_to_terminal(self, message, msg_type)

Add a new log message to the terminal

##### add_toc(self, doc)

Inserisce un 'campo TOC' nel documento, visibile come indice.
Quando apri il doc in Word, fai tasto destro > "Aggiorna campo"
o vai su "Riferimenti > Aggiorna sommario" per visualizzare l'indice.

##### save_report(self)

Save the report content to a file

##### process_html_content(self, soup, doc, figure_counter)

Process HTML content and convert it to Word document format

##### process_html_element(self, element, doc, figure_counter)

Process an HTML element and its children recursively

##### convert_html_table_to_docx(self, table_element, doc)

Convert an HTML table to a Word table

##### process_image(self, img_element, doc, figure_counter)

Process an image element and add it to the document

##### copy_to_clipboard(self)

Copy the report content to clipboard

##### start_timer(self)

Start the timer for tracking report generation time

##### update_time(self)

Update the time display and progress bar

##### close(self)

Override close to stop timer

### GenerateReportThread

**Inherits from**: QThread

#### Methods

##### __init__(self, custom_prompt, descriptions_text, api_key, selected_model, selected_tables, analysis_steps, agent, us_data, materials_data, pottery_data, site_data, py_dialog, output_language, tomba_data, periodizzazione_data, struttura_data, tma_data, enable_streaming)

##### create_vector_db(self, data, table_name)

Create a vector database from the data for RAG approach.

Args:
    data: List of data records
    table_name: Name of the table for context

Returns:
    FAISS vector store for retrieval

##### retrieve_relevant_data(self, vector_store, query, k)

Retrieve the most relevant data from the vector store based on the query.

Args:
    vector_store: FAISS vector store
    query: Query string
    k: Number of documents to retrieve

Returns:
    String containing the retrieved documents

##### create_rag_chain(self, vector_store, llm)

Create a RetrievalQA chain for the RAG approach.

Args:
    vector_store: FAISS vector store
    llm: Language model

Returns:
    RetrievalQA chain

##### count_tokens(self, text)

Estimate the number of tokens in a text.
This is a simple estimation based on character count.

Args:
    text: The text to count tokens for

Returns:
    Estimated token count

##### validate_us(self)

Validate US data using ArchaeologicalValidators

##### validate_materials(self)

Validate materials data using ArchaeologicalValidators

##### validate_pottery(self)

Validate pottery data using ArchaeologicalValidators

##### validate_tomba(self)

Validate tomb data using ArchaeologicalValidators

##### validate_periodizzazione(self)

Validate periodization data using ArchaeologicalValidators

##### validate_struttura(self)

Validate structure data using ArchaeologicalValidators

##### validate_tma(self)

Validate TMA data

##### format_prompt_from_json(self, prompt_template)

Converte il template JSON in un prompt testuale strutturato in modo sicuro

##### get_language_instructions(self)

Get specific instructions for the selected language

##### format_for_widget(self, text)

Converte il formato immagine per la visualizzazione nel widget e formatta il testo in HTML con stili corretti.

##### run(self)

##### clean_ai_notes(self, text)

Remove AI's notes, recommendations, and meta-commentary from the text

##### create_prompt(self, selected_language)

##### format_materials_table(self)

Formatta i dati dei materiali per la tabella

##### format_pottery_table(self)

Formatta i dati della ceramica per la tabella

##### format_tma_table(self)

Formatta i dati TMA per la tabella

##### create_tma_statistics(self)

Crea statistiche complete per i dati TMA

##### generate_tma_report_section(self)

Genera una sezione completa del report TMA con statistiche e grafici

##### format_tomba_table(self)

Formatta i dati delle tombe per la tabella

##### format_periodizzazione_table(self)

Formatta i dati della periodizzazione per la tabella

##### format_struttura_table(self)

Formatta i dati delle strutture per la tabella

##### create_materials_table(self)

Create a formatted table of materials

##### create_pottery_table(self)

Create a formatted table of pottery

##### format_table(self, table_data)

Format table data into a markdown table

### RAGQueryDialog

Dialog for RAG-based database querying with GPT-5

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### setup_ui(self)

Setup the user interface

##### execute_query(self)

Execute the RAG query with conversation history

##### append_streaming_response(self, token)

Append streaming response tokens to the text results

##### handle_results(self, results)

Handle query results and update conversation history

##### format_text_results(self, text)

Format text results for display

##### display_table(self, table_data)

Display table data in the table widget

##### display_chart(self, chart_data)

Display chart in the chart widget

##### export_text(self)

Export text results

##### export_table_csv(self)

Export table as CSV

##### export_excel(self)

Export table as Excel

##### export_chart(self)

Export chart as image

##### clear_query(self)

Clear query and results

##### handle_error(self, error_msg)

Handle errors

##### update_progress(self, message)

Update progress status

### RAGQueryWorker

Worker thread for RAG queries

**Inherits from**: QThread

#### Methods

##### __init__(self, query, db_manager, api_key, model, conversation_history, parent, enable_streaming, force_reload)

##### run(self)

Execute the RAG query

##### load_all_database_data(self)

Load all available data from database without filters

##### load_database_data(self)

Load relevant data from database

##### prepare_texts(self, data)

Prepare texts for vectorstore

##### create_analysis_tools(self, data, vectorstore)

Create analysis tools

##### query_data(self, query, data)

Query data based on natural language

##### create_table_data(self, request, data)

Create table data from request

##### calculate_statistics(self, request, data)

Calculate statistics from data

##### parse_response(self, response_text, data)

Parse AI response and extract structured data

##### extract_table_from_text(self, text, data)

Extract table data from text response

##### extract_chart_data(self, text, data)

Extract chart data from response

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

### pyarchinit_US

This class creates the main dialog for the US form

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### natural_sort_key(text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### __init__(self, iface)

##### get_images_for_entities(self, entity_ids, log_signal, entity_type)

##### count_tokens(self, text)

Estimate the number of tokens in the text.
This is a more accurate approximation than just splitting on whitespace.

##### create_vector_db(self, data, table_name)

Create a vector database from the data for RAG approach.

Args:
    data: List of data records
    table_name: Name of the table for context

Returns:
    FAISS vector store for retrieval

##### retrieve_relevant_data(self, vector_store, query, k)

Retrieve the most relevant data from the vector store based on the query.

Args:
    vector_store: FAISS vector store
    query: Query string
    k: Number of documents to retrieve

Returns:
    String containing the retrieved documents

##### create_rag_chain(self, vector_store, llm)

Create a RetrievalQA chain for the RAG approach.

Args:
    vector_store: FAISS vector store
    llm: Language model

Returns:
    RetrievalQA chain

##### split_data_to_fit_tokens(self, data, columns, max_tokens_per_chunk)

Split data into chunks that fit within token limits.
Uses a more efficient algorithm that prioritizes keeping related data together.

Args:
    data: List of data records
    columns: List of columns to include
    max_tokens_per_chunk: Maximum tokens per chunk (default: 8000)

Returns:
    List of chunks, where each chunk is a list of records

##### analyze_site_context(self, report_data)

Analyze site context in detail

##### analyze_stratigraphy_relationships(self, us_data)

Analyze stratigraphic relationships

##### analyze_stratigraphy_by_area(self, us_data)

Analyze stratigraphy by area

##### analyze_materials_by_type(self, material_data)

Analyze materials by type

##### analyze_pottery_by_class(self, pottery_data)

Analyze pottery by class

##### analyze_pottery_photo(self, pottery_data)

Analyze pottery photos

##### validate_us_description(self, us_data)

Validate US descriptions

##### validate_materials_description(self, materials_data)

Validate materials descriptions

##### validate_pottery_description(self, pottery_data)

Validate pottery descriptions

##### create_materials_table(self, materials_data)

Create formatted materials table

##### create_pottery_table(self, pottery_data)

Create formatted pottery table

##### format_us_data(self, us_data)

Format US data for the report

##### format_material_data(self, material_data)

Format material data for the report

##### format_pottery_data(self, pottery_data)

Format pottery data for the report

##### format_tomba_data(self, tomba_data)

Format tomb data for the report

##### format_periodizzazione_data(self, periodizzazione_data)

Format periodization data for the report

##### format_struttura_data(self, struttura_data)

Format structure data for the report

##### format_tma_data(self, tma_data)

Format TMA (Tipologia Materiali Archeologici) data for the report

##### create_analysis_tools(self, report_data, site_data, us_data, materials_data, pottery_data)

Create analysis tools for the LangChain agent

##### create_validation_tools(self, site_data, us_data, materials_data, pottery_data)

Create validation tools for the LangChain agent

##### process_site_table(self, records, current_site, report_data)

Process site table records and update report data

##### process_us_table(self, records, year_filter, us_start, us_end, us_data)

Process US table records and update US data

##### process_materials_table(self, records, year_filter, us_start, us_end, materials_data)

Process materials table records and update materials data

##### process_pottery_table(self, records, year_filter, us_start, us_end, pottery_data)

Process pottery table records and update pottery data

##### filter_records(self, records, year_filter, start, end, year_field, range_field)

Filter records based on year or range criteria

year_filter can be a single year or multiple years separated by commas
e.g. "2024" or "2024, 2025, 2026" or "2024,2025,2026"

##### initialize_report_data(self)

Initialize the report data dictionary with empty values

##### process_table_data(self, table_name, records, current_site, year_filter, us_start, us_end, report_data, us_data, materials_data, pottery_data, tomba_data, periodizzazione_data, struttura_data, tma_data)

Process table data and update corresponding data structures

##### create_system_message(self)

Create the system message for the LangChain agent with full schema knowledge

##### create_custom_prompt(self, formatted_us_data, formatted_material_data, formatted_pottery_data, report_data, formatted_tomba_data, formatted_periodizzazione_data, formatted_struttura_data, formatted_tma_data)

Create the custom prompt for the report generation

##### check_missing_data(self)

Verifica e riporta i dati mancanti in tutte le tabelle selezionate

##### open_rag_query_dialog(self)

Open the RAG query dialog

##### generate_and_display_report(self)

##### on_report_generated(self, report_text, report_data)

##### parse_report_into_sections(self, report_text)

Parse the report text into sections based on headings

##### save_report_as_plain_doc(self, report_text, output_path)

##### process_section_content(self, doc, section_info, content, report_data)

Process the content of a section and add it to the document with proper styles.

Args:
    doc: Word document
    section_info: Dictionary with section information
    content: Text content of the section
    report_data: Dictionary with all report data

##### save_report_to_template(self, report_data, template_path, output_path)

##### convert_markdown_table(self, table_lines, doc)

Convert a list of markdown table lines to a Word table.

Args:
    table_lines: List of strings representing markdown table lines
    doc: Word document to add the table to

Returns:
    Word table object

##### clean_heading(self, text)

Remove markdown heading markers (##, --, etc.) from text.

Args:
    text: Text to clean

Returns:
    Cleaned text

##### sketchgpt(self)

##### on_pushButton_trick_pressed(self)

##### get_input_prompt(self, label)

##### show_warning(self, message)

##### show_error(self, error, original_message)

##### update_all_areas(self)

##### get_all_areas(self, sito)

##### update_rapporti_col(self, sito, area)

##### update_rapporti_col_2(self)

##### ensure_utf8(self, s)

Assicura che una stringa sia codificata correttamente in UTF-8.

Args:
    s (str): La stringa da codificare.

Returns:
    str: La stringa codificata in UTF-8.

##### find_correct_area_for_us(self, us, sito, connection)

Trova l'area corretta per una data unità stratigrafica (us) e sito.

Args:
    us (str): L'identificativo dell'unità stratigrafica.
    sito (str): Il nome del sito.
    connection: Connessione al database esistente.

Returns:
    str: L'area corretta o None se non trovata.

##### clean_comments(self, text_to_clean)

##### EM_extract_node_name(self, node_element)

##### check_if_empty(self, name)

##### on_pushButton_graphml2csv_pressed(self)

##### on_pushButton_csv2us_pressed(self)

##### parse_error_report(self)

Parse the stratigraphic check report to extract different error types

##### fix_empty_areas(self, empty_area_errors)

Update all relationships with empty areas

##### delete_auto_created_forms(self)

Delete all US forms that were automatically created

##### fix_missing_forms(self, missing_form_errors)

Create missing US forms with proper initialization

##### fix_missing_relationships(self, relationship_errors)

Add missing reciprocal relationships

##### get_reciprocal_relationship_type(self, rel_type)

Get the reciprocal relationship type

##### on_pushButton_fix_pressed(self)

Enhanced fix button that offers options to resolve different types of errors

##### check_listoflist(self)

##### log_message(self, message)

Aggiunge un messaggio alla listWidget

##### check_inverse_relationships(self, unverified_list)

##### unit_type_select(self)

##### search_rapp(self)

##### check_v(self)

##### change_label(self)

##### refresh(self)

##### charge_insert_ra(self)

##### sync_tm_from_tma(self)

Synchronize TM (ref_tm) field with cassetta from TMA table

##### charge_insert_ra_pottery(self)

##### listview_us(self)

This function is used to filter the 'Unità Stratigrafiche' table.

##### submit(self)

##### value_check(self)

##### update_filter(self, s)

This function is used to filter the 'Unità Stratigrafiche' table.

##### on_pushButton_globalsearch_pressed(self)

This function is used to search for a specific record in the database.

##### format_struttura_item(self, struttura)

##### charge_struttura_list(self)

This function charges the 'Struttura' combobox with the values from the 'Struttura' table.

##### calculate_centroid_from_geometries(self, geometry_records)

Calculate the centroid of multiple polygon geometries from pyunitastratigrafiche

##### geometry_unitastratigrafiche(self)

This function charges the 'Posizione' combobox with the values from the 'Unità Stratigrafiche' table.
Enhanced to calculate and display centroid when multiple polygons exist.

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

##### update_dating_deferred(self)

This function updates Dating fields after the interface has loaded.
Deferred execution to avoid false "save changes" prompts.

##### update_dating(self)

This function updates the 'Dating' field.
For new records (INSERT mode), only updates the form field.
For existing records (UPDATE mode), can update the database if the user has permissions.

##### on_pushButton_draw_doc_pressed(self)

##### save_us(self)

##### selectRows(self)

##### on_pushButton_update_pressed(self)

##### us_t(self)

##### on_pushButton_go_to_us_pressed(self)

##### on_pushButton_go_to_scheda_pressed(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### connect_p(self)

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

##### generate_US(self)

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_assigntags_pressed(self)

##### on_done_selecting(self)

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

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### generate_list_foto(self)

##### generate_list_pdf(self)

##### on_pushButton_exp_tavole_pressed(self)

##### updateProgressBar(self, tav, tot)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### setPathdot(self)

##### setPathgraphml(self)

##### setDoc_ref(self)

##### list2pipe(self, x)

##### on_pushButton_graphml_pressed(self)

##### openpdfDir(self)

##### on_pushButton_viewmatrix_pressed(self)

##### on_pushButton_export_matrix_pressed(self)

##### launch_matrix_exp_if(self, msg)

##### export_extended_matrix_action(self)

Alternative method to call Extended Matrix export
Can be called from menu or toolbar

##### on_pushButton_export_extended_matrix_pressed(self)

Export to Extended Matrix format (S3DGraphy)

##### on_pushButton_orderLayers_pressed(self)

##### format_message(self, sing_rapp, us)

##### launch_order_layer_if(self, msg)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_showSelectedFeatures_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_toolButtonPreview_toggled(self)

##### on_pushButton_addRaster_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### save_rapp(self)

##### on_pushButton_save_pressed(self)

##### apikey_gpt(self)

##### on_pushButton_rapp_check_pressed(self)

##### on_pushButton_h_check_pressed(self)

##### data_error_check(self)

##### automaticform_check(self, sito_check)

##### rapporti_stratigrafici_check(self, sito_check)

##### def_strati_to_rapporti_stratigrafici_check(self, sito_check)

##### concat(self, a, b)

##### report_with_phrase(self, ut, us, sing_rapp, periodo_in, fase_in, sito, area)

##### periodi_to_rapporti_stratigrafici_check(self, sito_check)

##### insert_new_rec(self)

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_remove_row_rapporti_pressed(self)

##### on_pushButton_insert_row_rapporti2_pressed(self)

##### on_pushButton_remove_row_rapporti2_pressed(self)

##### on_pushButton_insert_row_inclusi_pressed(self)

##### on_pushButton_remove_row_inclusi_pressed(self)

##### on_pushButton_insert_row_campioni_pressed(self)

##### on_pushButton_remove_row_campioni_pressed(self)

##### on_pushButton_insert_row_organici_pressed(self)

##### on_pushButton_remove_row_organici_pressed(self)

##### on_pushButton_insert_row_inorganici_pressed(self)

##### on_pushButton_remove_row_inorganici_pressed(self)

##### on_pushButton_insert_row_documentazione_pressed(self)

##### on_pushButton_remove_row_documentazione_pressed(self)

##### on_pushButton_insert_row_inclusi_materiali_pressed(self)

##### on_pushButton_remove_row_inclusi_materiali_pressed(self)

##### on_pushButton_insert_row_inclusi_leganti_pressed(self)

##### on_pushButton_remove_row_inclusi_leganti_pressed(self)

##### on_pushButton_insert_row_colore_legante_usm_pressed(self)

##### on_pushButton_remove_row_colore_legante_usm_pressed(self)

##### on_pushButton_insert_row_consistenza_texture_mat_usm_pressed(self)

##### on_pushButton_remove_row_consistenza_texture_mat_usm_pressed(self)

##### on_pushButton_insert_row_colore_materiale_usm_pressed(self)

##### on_pushButton_remove_row_colore_materiale_usm_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### view_all(self)

##### charge_records_filtered_by_site(self)

Carica i record filtrati per il sito selezionato

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### delete_all_filtered_records(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_showLayer_pressed(self)

for sing_us in range(len(self.DATA_LIST)):
    sing_layer = [self.DATA_LIST[sing_us]]
    self.pyQGIS.charge_vector_layers(sing_layer)

##### on_pushButton_crea_codice_periodo_pressed(self)

##### switch_search_mode(self)

##### on_pushButton_search_go_pressed(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### charge_records(self)

##### charge_records_n(self)

##### datestrfdate(self)

##### yearstrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### empty_fields_nosite(self)

##### fill_fields(self, n)

##### get_current_form_data(self)

Get current form data as a dictionary for conflict resolution

##### check_for_updates(self)

Check if current record has been modified by others

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### setTableEnable(self, t, v)

##### testing(self, name_file, message)

##### on_pushButton_open_dir_pressed(self)

##### on_pushButton_open_dir_matrix_pressed(self)

##### on_pushButton_open_dir_tavole_pressed(self)

##### check_db(self)

##### cast_tipo_dati(self, valore)

##### on_pushButton_import_ed2pyarchinit_pressed(self)

funzione valida solo per sqlite

##### on_pushButton_filter_us_pressed(self)

##### text2sql(self)

### SQLPromptDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface, parent)

##### clear_fields(self)

Clear all text fields and disable buttons

##### clear_results_table(self)

##### on_prompt_selected(self, index)

##### update_prompt_ui(self)

##### on_select_prompt_clicked(self)

##### record_prompt(self, prompt)

##### load_prompts_from_file(self)

##### save_prompts_to_file(self)

##### handle_text_changed(self)

##### is_sql_query(query)

##### apikey_text2sql(self)

##### on_download_model_clicked(self)

Download the Phi-3 model for local use

##### on_start_button_clicked(self)

##### on_explainsql_button_clicked(self)

##### on_start_sql_query_clicked(self)

Execute SQL query and show results

##### execute_sql_statements(self, statements, con_string)

Execute SQL statements with spatialite specific handling

##### on_explainsql_button_clicked(self)

##### populate_results_list(self, results)

##### on_export_to_excel_button_clicked(self)

##### on_create_graph_button_clicked(self)

##### on_explain_button_clicked(self)

##### add_spatial_layer_to_canvas(self)

##### enhance_spatial_view_creation(self, sql_query)

Enhances a spatial query by converting SELECT to VIEW when needed

### MplCanvas

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self, parent)

### GraphWindow

**Inherits from**: QDockWidget

#### Methods

##### __init__(self)

##### plot(self, data)

### USFilterDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### initUI(self)

##### natural_sort_key(self, text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### populate_list_with_us(self)

##### update_list_widget(self, records)

##### filter_list(self, text)

##### apply_filter(self)

##### get_selected_us(self)

### IntegerDelegate

The IntegerDelegate class is a subclass of QStyledItemDelegate from the PyQt5 library. It is used to create a delegate for editing integer values in a Qt model/view framework.
Example Usage
# Import the necessary libraries
from PyQt5 import QtGui, QtWidgets

# Create an instance of the IntegerDelegate class
delegate = IntegerDelegate()

# Set the delegate for a specific column in a QTableView
tableView.setItemDelegateForColumn(columnIndex, delegate)
Code Analysis
Main functionalities
The main functionality of the IntegerDelegate class is to provide a custom editor for integer values in a Qt model/view framework. It creates a QLineEdit widget as the editor and sets a QIntValidator to ensure that only valid integer values can be entered.

Methods
createEditor(parent, option, index): This method is called when a cell in the view needs to be edited. It creates and returns a QLineEdit widget as the editor for the cell. It also sets a QIntValidator to ensure that only valid integer values can be entered.

Fields
None

**Inherits from**: QtWidgets.QStyledItemDelegate

#### Methods

##### __init__(self, parent)

##### createEditor(self, parent, option, index)

### SimpleGPT5Wrapper

#### Methods

##### __init__(self, llm, vectorstore, parent_thread, enable_streaming)

##### invoke(self, input_dict)

### GPT5DirectWrapper

#### Methods

##### __init__(self, llm, tools, system_message, parent_thread)

##### invoke(self, input_dict, config)

Direct LLM invocation that simulates agent behavior

### StreamingHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### OverviewStreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### StreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### SimplifiedStreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### CollapsibleSection

**Inherits from**: QWidget

#### Methods

##### __init__(self, title, parent)

##### toggle_content(self)

##### add_widget(self, widget)

##### add_layout(self, layout)

### ReportGeneratorDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### get_selected_language(self)

Get the selected output language

##### get_streaming_enabled(self)

Get whether streaming is enabled

##### validate_data(self)

Esegue la validazione dei dati

##### get_us_data(self)

Recupera i dati delle US dal database

##### get_materials_data(self)

Recupera i dati dei materiali dal database

##### get_pottery_data(self)

Recupera i dati della ceramica dal database

##### get_tma_data(self)

Recupera i dati TMA dal database

##### get_selected_tables(self)

Get list of checked tables

##### get_year_filter(self)

Get year filter value

##### get_us_range(self)

Get US range values

### CheckableComboBox

**Inherits from**: QComboBox

#### Methods

##### __init__(self)

##### add_item(self, text)

Add a checkable item to the combo box

##### items_checked(self)

Get list of checked items

##### handle_item_pressed(self, index)

Handle item check/uncheck

### ReportDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, content, parent)

##### update_content(self, new_content)

Update the report content

##### append_streaming_token(self, token)

Append a streaming token to the content

##### handle_mouse_press(self, event)

Gestisce il click del mouse nel text edit

##### log_to_terminal(self, message, msg_type)

Add a new log message to the terminal

##### add_toc(self, doc)

Inserisce un 'campo TOC' nel documento, visibile come indice.
Quando apri il doc in Word, fai tasto destro > "Aggiorna campo"
o vai su "Riferimenti > Aggiorna sommario" per visualizzare l'indice.

##### save_report(self)

Save the report content to a file

##### process_html_content(self, soup, doc, figure_counter)

Process HTML content and convert it to Word document format

##### process_html_element(self, element, doc, figure_counter)

Process an HTML element and its children recursively

##### convert_html_table_to_docx(self, table_element, doc)

Convert an HTML table to a Word table

##### process_image(self, img_element, doc, figure_counter)

Process an image element and add it to the document

##### copy_to_clipboard(self)

Copy the report content to clipboard

##### start_timer(self)

Start the timer for tracking report generation time

##### update_time(self)

Update the time display and progress bar

##### close(self)

Override close to stop timer

### GenerateReportThread

**Inherits from**: QThread

#### Methods

##### __init__(self, custom_prompt, descriptions_text, api_key, selected_model, selected_tables, analysis_steps, agent, us_data, materials_data, pottery_data, site_data, py_dialog, output_language, tomba_data, periodizzazione_data, struttura_data, tma_data, enable_streaming)

##### create_vector_db(self, data, table_name)

Create a vector database from the data for RAG approach.

Args:
    data: List of data records
    table_name: Name of the table for context

Returns:
    FAISS vector store for retrieval

##### retrieve_relevant_data(self, vector_store, query, k)

Retrieve the most relevant data from the vector store based on the query.

Args:
    vector_store: FAISS vector store
    query: Query string
    k: Number of documents to retrieve

Returns:
    String containing the retrieved documents

##### create_rag_chain(self, vector_store, llm)

Create a RetrievalQA chain for the RAG approach.

Args:
    vector_store: FAISS vector store
    llm: Language model

Returns:
    RetrievalQA chain

##### count_tokens(self, text)

Estimate the number of tokens in a text.
This is a simple estimation based on character count.

Args:
    text: The text to count tokens for

Returns:
    Estimated token count

##### validate_us(self)

Validate US data using ArchaeologicalValidators

##### validate_materials(self)

Validate materials data using ArchaeologicalValidators

##### validate_pottery(self)

Validate pottery data using ArchaeologicalValidators

##### validate_tomba(self)

Validate tomb data using ArchaeologicalValidators

##### validate_periodizzazione(self)

Validate periodization data using ArchaeologicalValidators

##### validate_struttura(self)

Validate structure data using ArchaeologicalValidators

##### validate_tma(self)

Validate TMA data

##### format_prompt_from_json(self, prompt_template)

Converte il template JSON in un prompt testuale strutturato in modo sicuro

##### get_language_instructions(self)

Get specific instructions for the selected language

##### format_for_widget(self, text)

Converte il formato immagine per la visualizzazione nel widget e formatta il testo in HTML con stili corretti.

##### run(self)

##### clean_ai_notes(self, text)

Remove AI's notes, recommendations, and meta-commentary from the text

##### create_prompt(self, selected_language)

##### format_materials_table(self)

Formatta i dati dei materiali per la tabella

##### format_pottery_table(self)

Formatta i dati della ceramica per la tabella

##### format_tma_table(self)

Formatta i dati TMA per la tabella

##### create_tma_statistics(self)

Crea statistiche complete per i dati TMA

##### generate_tma_report_section(self)

Genera una sezione completa del report TMA con statistiche e grafici

##### format_tomba_table(self)

Formatta i dati delle tombe per la tabella

##### format_periodizzazione_table(self)

Formatta i dati della periodizzazione per la tabella

##### format_struttura_table(self)

Formatta i dati delle strutture per la tabella

##### create_materials_table(self)

Create a formatted table of materials

##### create_pottery_table(self)

Create a formatted table of pottery

##### format_table(self, table_data)

Format table data into a markdown table

### RAGQueryDialog

Dialog for RAG-based database querying with GPT-5

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### setup_ui(self)

Setup the user interface

##### execute_query(self)

Execute the RAG query with conversation history

##### append_streaming_response(self, token)

Append streaming response tokens to the text results

##### handle_results(self, results)

Handle query results and update conversation history

##### format_text_results(self, text)

Format text results for display

##### display_table(self, table_data)

Display table data in the table widget

##### display_chart(self, chart_data)

Display chart in the chart widget

##### export_text(self)

Export text results

##### export_table_csv(self)

Export table as CSV

##### export_excel(self)

Export table as Excel

##### export_chart(self)

Export chart as image

##### clear_query(self)

Clear query and results

##### handle_error(self, error_msg)

Handle errors

##### update_progress(self, message)

Update progress status

### RAGQueryWorker

Worker thread for RAG queries

**Inherits from**: QThread

#### Methods

##### __init__(self, query, db_manager, api_key, model, conversation_history, parent, enable_streaming, force_reload)

##### run(self)

Execute the RAG query

##### load_all_database_data(self)

Load all available data from database without filters

##### load_database_data(self)

Load relevant data from database

##### prepare_texts(self, data)

Prepare texts for vectorstore

##### create_analysis_tools(self, data, vectorstore)

Create analysis tools

##### query_data(self, query, data)

Query data based on natural language

##### create_table_data(self, request, data)

Create table data from request

##### calculate_statistics(self, request, data)

Calculate statistics from data

##### parse_response(self, response_text, data)

Parse AI response and extract structured data

##### extract_table_from_text(self, text, data)

Extract table data from text response

##### extract_chart_data(self, text, data)

Extract chart data from response

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

### pyarchinit_US

This class creates the main dialog for the US form

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### natural_sort_key(text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### __init__(self, iface)

##### get_images_for_entities(self, entity_ids, log_signal, entity_type)

##### count_tokens(self, text)

Estimate the number of tokens in the text.
This is a more accurate approximation than just splitting on whitespace.

##### create_vector_db(self, data, table_name)

Create a vector database from the data for RAG approach.

Args:
    data: List of data records
    table_name: Name of the table for context

Returns:
    FAISS vector store for retrieval

##### retrieve_relevant_data(self, vector_store, query, k)

Retrieve the most relevant data from the vector store based on the query.

Args:
    vector_store: FAISS vector store
    query: Query string
    k: Number of documents to retrieve

Returns:
    String containing the retrieved documents

##### create_rag_chain(self, vector_store, llm)

Create a RetrievalQA chain for the RAG approach.

Args:
    vector_store: FAISS vector store
    llm: Language model

Returns:
    RetrievalQA chain

##### split_data_to_fit_tokens(self, data, columns, max_tokens_per_chunk)

Split data into chunks that fit within token limits.
Uses a more efficient algorithm that prioritizes keeping related data together.

Args:
    data: List of data records
    columns: List of columns to include
    max_tokens_per_chunk: Maximum tokens per chunk (default: 8000)

Returns:
    List of chunks, where each chunk is a list of records

##### analyze_site_context(self, report_data)

Analyze site context in detail

##### analyze_stratigraphy_relationships(self, us_data)

Analyze stratigraphic relationships

##### analyze_stratigraphy_by_area(self, us_data)

Analyze stratigraphy by area

##### analyze_materials_by_type(self, material_data)

Analyze materials by type

##### analyze_pottery_by_class(self, pottery_data)

Analyze pottery by class

##### analyze_pottery_photo(self, pottery_data)

Analyze pottery photos

##### validate_us_description(self, us_data)

Validate US descriptions

##### validate_materials_description(self, materials_data)

Validate materials descriptions

##### validate_pottery_description(self, pottery_data)

Validate pottery descriptions

##### create_materials_table(self, materials_data)

Create formatted materials table

##### create_pottery_table(self, pottery_data)

Create formatted pottery table

##### format_us_data(self, us_data)

Format US data for the report

##### format_material_data(self, material_data)

Format material data for the report

##### format_pottery_data(self, pottery_data)

Format pottery data for the report

##### format_tomba_data(self, tomba_data)

Format tomb data for the report

##### format_periodizzazione_data(self, periodizzazione_data)

Format periodization data for the report

##### format_struttura_data(self, struttura_data)

Format structure data for the report

##### format_tma_data(self, tma_data)

Format TMA (Tipologia Materiali Archeologici) data for the report

##### create_analysis_tools(self, report_data, site_data, us_data, materials_data, pottery_data)

Create analysis tools for the LangChain agent

##### create_validation_tools(self, site_data, us_data, materials_data, pottery_data)

Create validation tools for the LangChain agent

##### process_site_table(self, records, current_site, report_data)

Process site table records and update report data

##### process_us_table(self, records, year_filter, us_start, us_end, us_data)

Process US table records and update US data

##### process_materials_table(self, records, year_filter, us_start, us_end, materials_data)

Process materials table records and update materials data

##### process_pottery_table(self, records, year_filter, us_start, us_end, pottery_data)

Process pottery table records and update pottery data

##### filter_records(self, records, year_filter, start, end, year_field, range_field)

Filter records based on year or range criteria

year_filter can be a single year or multiple years separated by commas
e.g. "2024" or "2024, 2025, 2026" or "2024,2025,2026"

##### initialize_report_data(self)

Initialize the report data dictionary with empty values

##### process_table_data(self, table_name, records, current_site, year_filter, us_start, us_end, report_data, us_data, materials_data, pottery_data, tomba_data, periodizzazione_data, struttura_data, tma_data)

Process table data and update corresponding data structures

##### create_system_message(self)

Create the system message for the LangChain agent with full schema knowledge

##### create_custom_prompt(self, formatted_us_data, formatted_material_data, formatted_pottery_data, report_data, formatted_tomba_data, formatted_periodizzazione_data, formatted_struttura_data, formatted_tma_data)

Create the custom prompt for the report generation

##### check_missing_data(self)

Verifica e riporta i dati mancanti in tutte le tabelle selezionate

##### open_rag_query_dialog(self)

Open the RAG query dialog

##### generate_and_display_report(self)

##### on_report_generated(self, report_text, report_data)

##### parse_report_into_sections(self, report_text)

Parse the report text into sections based on headings

##### save_report_as_plain_doc(self, report_text, output_path)

##### process_section_content(self, doc, section_info, content, report_data)

Process the content of a section and add it to the document with proper styles.

Args:
    doc: Word document
    section_info: Dictionary with section information
    content: Text content of the section
    report_data: Dictionary with all report data

##### save_report_to_template(self, report_data, template_path, output_path)

##### convert_markdown_table(self, table_lines, doc)

Convert a list of markdown table lines to a Word table.

Args:
    table_lines: List of strings representing markdown table lines
    doc: Word document to add the table to

Returns:
    Word table object

##### clean_heading(self, text)

Remove markdown heading markers (##, --, etc.) from text.

Args:
    text: Text to clean

Returns:
    Cleaned text

##### sketchgpt(self)

##### on_pushButton_trick_pressed(self)

##### get_input_prompt(self, label)

##### show_warning(self, message)

##### show_error(self, error, original_message)

##### update_all_areas(self)

##### get_all_areas(self, sito)

##### update_rapporti_col(self, sito, area)

##### update_rapporti_col_2(self)

##### ensure_utf8(self, s)

Assicura che una stringa sia codificata correttamente in UTF-8.

Args:
    s (str): La stringa da codificare.

Returns:
    str: La stringa codificata in UTF-8.

##### find_correct_area_for_us(self, us, sito, connection)

Trova l'area corretta per una data unità stratigrafica (us) e sito.

Args:
    us (str): L'identificativo dell'unità stratigrafica.
    sito (str): Il nome del sito.
    connection: Connessione al database esistente.

Returns:
    str: L'area corretta o None se non trovata.

##### clean_comments(self, text_to_clean)

##### EM_extract_node_name(self, node_element)

##### check_if_empty(self, name)

##### on_pushButton_graphml2csv_pressed(self)

##### on_pushButton_csv2us_pressed(self)

##### parse_error_report(self)

Parse the stratigraphic check report to extract different error types

##### fix_empty_areas(self, empty_area_errors)

Update all relationships with empty areas

##### delete_auto_created_forms(self)

Delete all US forms that were automatically created

##### fix_missing_forms(self, missing_form_errors)

Create missing US forms with proper initialization

##### fix_missing_relationships(self, relationship_errors)

Add missing reciprocal relationships

##### get_reciprocal_relationship_type(self, rel_type)

Get the reciprocal relationship type

##### on_pushButton_fix_pressed(self)

Enhanced fix button that offers options to resolve different types of errors

##### check_listoflist(self)

##### log_message(self, message)

Aggiunge un messaggio alla listWidget

##### check_inverse_relationships(self, unverified_list)

##### unit_type_select(self)

##### search_rapp(self)

##### check_v(self)

##### change_label(self)

##### refresh(self)

##### charge_insert_ra(self)

##### sync_tm_from_tma(self)

Synchronize TM (ref_tm) field with cassetta from TMA table

##### charge_insert_ra_pottery(self)

##### listview_us(self)

This function is used to filter the 'Unità Stratigrafiche' table.

##### submit(self)

##### value_check(self)

##### update_filter(self, s)

This function is used to filter the 'Unità Stratigrafiche' table.

##### on_pushButton_globalsearch_pressed(self)

This function is used to search for a specific record in the database.

##### format_struttura_item(self, struttura)

##### charge_struttura_list(self)

This function charges the 'Struttura' combobox with the values from the 'Struttura' table.

##### calculate_centroid_from_geometries(self, geometry_records)

Calculate the centroid of multiple polygon geometries from pyunitastratigrafiche

##### geometry_unitastratigrafiche(self)

This function charges the 'Posizione' combobox with the values from the 'Unità Stratigrafiche' table.
Enhanced to calculate and display centroid when multiple polygons exist.

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

##### update_dating_deferred(self)

This function updates Dating fields after the interface has loaded.
Deferred execution to avoid false "save changes" prompts.

##### update_dating(self)

This function updates the 'Dating' field.
For new records (INSERT mode), only updates the form field.
For existing records (UPDATE mode), can update the database if the user has permissions.

##### on_pushButton_draw_doc_pressed(self)

##### save_us(self)

##### selectRows(self)

##### on_pushButton_update_pressed(self)

##### us_t(self)

##### on_pushButton_go_to_us_pressed(self)

##### on_pushButton_go_to_scheda_pressed(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### connect_p(self)

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

##### generate_US(self)

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_assigntags_pressed(self)

##### on_done_selecting(self)

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

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### generate_list_foto(self)

##### generate_list_pdf(self)

##### on_pushButton_exp_tavole_pressed(self)

##### updateProgressBar(self, tav, tot)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### setPathdot(self)

##### setPathgraphml(self)

##### setDoc_ref(self)

##### list2pipe(self, x)

##### on_pushButton_graphml_pressed(self)

##### openpdfDir(self)

##### on_pushButton_viewmatrix_pressed(self)

##### on_pushButton_export_matrix_pressed(self)

##### launch_matrix_exp_if(self, msg)

##### export_extended_matrix_action(self)

Alternative method to call Extended Matrix export
Can be called from menu or toolbar

##### on_pushButton_export_extended_matrix_pressed(self)

Export to Extended Matrix format (S3DGraphy)

##### on_pushButton_orderLayers_pressed(self)

##### format_message(self, sing_rapp, us)

##### launch_order_layer_if(self, msg)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_showSelectedFeatures_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_toolButtonPreview_toggled(self)

##### on_pushButton_addRaster_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### save_rapp(self)

##### on_pushButton_save_pressed(self)

##### apikey_gpt(self)

##### on_pushButton_rapp_check_pressed(self)

##### on_pushButton_h_check_pressed(self)

##### data_error_check(self)

##### automaticform_check(self, sito_check)

##### rapporti_stratigrafici_check(self, sito_check)

##### def_strati_to_rapporti_stratigrafici_check(self, sito_check)

##### concat(self, a, b)

##### report_with_phrase(self, ut, us, sing_rapp, periodo_in, fase_in, sito, area)

##### periodi_to_rapporti_stratigrafici_check(self, sito_check)

##### insert_new_rec(self)

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_remove_row_rapporti_pressed(self)

##### on_pushButton_insert_row_rapporti2_pressed(self)

##### on_pushButton_remove_row_rapporti2_pressed(self)

##### on_pushButton_insert_row_inclusi_pressed(self)

##### on_pushButton_remove_row_inclusi_pressed(self)

##### on_pushButton_insert_row_campioni_pressed(self)

##### on_pushButton_remove_row_campioni_pressed(self)

##### on_pushButton_insert_row_organici_pressed(self)

##### on_pushButton_remove_row_organici_pressed(self)

##### on_pushButton_insert_row_inorganici_pressed(self)

##### on_pushButton_remove_row_inorganici_pressed(self)

##### on_pushButton_insert_row_documentazione_pressed(self)

##### on_pushButton_remove_row_documentazione_pressed(self)

##### on_pushButton_insert_row_inclusi_materiali_pressed(self)

##### on_pushButton_remove_row_inclusi_materiali_pressed(self)

##### on_pushButton_insert_row_inclusi_leganti_pressed(self)

##### on_pushButton_remove_row_inclusi_leganti_pressed(self)

##### on_pushButton_insert_row_colore_legante_usm_pressed(self)

##### on_pushButton_remove_row_colore_legante_usm_pressed(self)

##### on_pushButton_insert_row_consistenza_texture_mat_usm_pressed(self)

##### on_pushButton_remove_row_consistenza_texture_mat_usm_pressed(self)

##### on_pushButton_insert_row_colore_materiale_usm_pressed(self)

##### on_pushButton_remove_row_colore_materiale_usm_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### view_all(self)

##### charge_records_filtered_by_site(self)

Carica i record filtrati per il sito selezionato

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### delete_all_filtered_records(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_showLayer_pressed(self)

for sing_us in range(len(self.DATA_LIST)):
    sing_layer = [self.DATA_LIST[sing_us]]
    self.pyQGIS.charge_vector_layers(sing_layer)

##### on_pushButton_crea_codice_periodo_pressed(self)

##### switch_search_mode(self)

##### on_pushButton_search_go_pressed(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### charge_records(self)

##### charge_records_n(self)

##### datestrfdate(self)

##### yearstrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### empty_fields_nosite(self)

##### fill_fields(self, n)

##### get_current_form_data(self)

Get current form data as a dictionary for conflict resolution

##### check_for_updates(self)

Check if current record has been modified by others

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### setTableEnable(self, t, v)

##### testing(self, name_file, message)

##### on_pushButton_open_dir_pressed(self)

##### on_pushButton_open_dir_matrix_pressed(self)

##### on_pushButton_open_dir_tavole_pressed(self)

##### check_db(self)

##### cast_tipo_dati(self, valore)

##### on_pushButton_import_ed2pyarchinit_pressed(self)

funzione valida solo per sqlite

##### on_pushButton_filter_us_pressed(self)

##### text2sql(self)

### SQLPromptDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface, parent)

##### clear_fields(self)

Clear all text fields and disable buttons

##### clear_results_table(self)

##### on_prompt_selected(self, index)

##### update_prompt_ui(self)

##### on_select_prompt_clicked(self)

##### record_prompt(self, prompt)

##### load_prompts_from_file(self)

##### save_prompts_to_file(self)

##### handle_text_changed(self)

##### is_sql_query(query)

##### apikey_text2sql(self)

##### on_download_model_clicked(self)

Download the Phi-3 model for local use

##### on_start_button_clicked(self)

##### on_explainsql_button_clicked(self)

##### on_start_sql_query_clicked(self)

Execute SQL query and show results

##### execute_sql_statements(self, statements, con_string)

Execute SQL statements with spatialite specific handling

##### on_explainsql_button_clicked(self)

##### populate_results_list(self, results)

##### on_export_to_excel_button_clicked(self)

##### on_create_graph_button_clicked(self)

##### on_explain_button_clicked(self)

##### add_spatial_layer_to_canvas(self)

##### enhance_spatial_view_creation(self, sql_query)

Enhances a spatial query by converting SELECT to VIEW when needed

### MplCanvas

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self, parent)

### GraphWindow

**Inherits from**: QDockWidget

#### Methods

##### __init__(self)

##### plot(self, data)

### USFilterDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### initUI(self)

##### natural_sort_key(self, text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### populate_list_with_us(self)

##### update_list_widget(self, records)

##### filter_list(self, text)

##### apply_filter(self)

##### get_selected_us(self)

### IntegerDelegate

The IntegerDelegate class is a subclass of QStyledItemDelegate from the PyQt5 library. It is used to create a delegate for editing integer values in a Qt model/view framework.
Example Usage
# Import the necessary libraries
from PyQt5 import QtGui, QtWidgets

# Create an instance of the IntegerDelegate class
delegate = IntegerDelegate()

# Set the delegate for a specific column in a QTableView
tableView.setItemDelegateForColumn(columnIndex, delegate)
Code Analysis
Main functionalities
The main functionality of the IntegerDelegate class is to provide a custom editor for integer values in a Qt model/view framework. It creates a QLineEdit widget as the editor and sets a QIntValidator to ensure that only valid integer values can be entered.

Methods
createEditor(parent, option, index): This method is called when a cell in the view needs to be edited. It creates and returns a QLineEdit widget as the editor for the cell. It also sets a QIntValidator to ensure that only valid integer values can be entered.

Fields
None

**Inherits from**: QtWidgets.QStyledItemDelegate

#### Methods

##### __init__(self, parent)

##### createEditor(self, parent, option, index)

### SimpleGPT5Wrapper

#### Methods

##### __init__(self, llm, vectorstore, parent_thread, enable_streaming)

##### invoke(self, input_dict)

### GPT5DirectWrapper

#### Methods

##### __init__(self, llm, tools, system_message, parent_thread)

##### invoke(self, input_dict, config)

Direct LLM invocation that simulates agent behavior

### StreamingHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### OverviewStreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### StreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### SimplifiedStreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### CollapsibleSection

**Inherits from**: QWidget

#### Methods

##### __init__(self, title, parent)

##### toggle_content(self)

##### add_widget(self, widget)

##### add_layout(self, layout)

### ReportGeneratorDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

##### get_selected_language(self)

Get the selected output language

##### get_streaming_enabled(self)

Get whether streaming is enabled

##### validate_data(self)

Esegue la validazione dei dati

##### get_us_data(self)

Recupera i dati delle US dal database

##### get_materials_data(self)

Recupera i dati dei materiali dal database

##### get_pottery_data(self)

Recupera i dati della ceramica dal database

##### get_tma_data(self)

Recupera i dati TMA dal database

##### get_selected_tables(self)

Get list of checked tables

##### get_year_filter(self)

Get year filter value

##### get_us_range(self)

Get US range values

### CheckableComboBox

**Inherits from**: QComboBox

#### Methods

##### __init__(self)

##### add_item(self, text)

Add a checkable item to the combo box

##### items_checked(self)

Get list of checked items

##### handle_item_pressed(self, index)

Handle item check/uncheck

### ReportDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, content, parent)

##### update_content(self, new_content)

Update the report content

##### append_streaming_token(self, token)

Append a streaming token to the content

##### handle_mouse_press(self, event)

Gestisce il click del mouse nel text edit

##### log_to_terminal(self, message, msg_type)

Add a new log message to the terminal

##### add_toc(self, doc)

Inserisce un 'campo TOC' nel documento, visibile come indice.
Quando apri il doc in Word, fai tasto destro > "Aggiorna campo"
o vai su "Riferimenti > Aggiorna sommario" per visualizzare l'indice.

##### save_report(self)

Save the report content to a file

##### process_html_content(self, soup, doc, figure_counter)

Process HTML content and convert it to Word document format

##### process_html_element(self, element, doc, figure_counter)

Process an HTML element and its children recursively

##### convert_html_table_to_docx(self, table_element, doc)

Convert an HTML table to a Word table

##### process_image(self, img_element, doc, figure_counter)

Process an image element and add it to the document

##### copy_to_clipboard(self)

Copy the report content to clipboard

##### start_timer(self)

Start the timer for tracking report generation time

##### update_time(self)

Update the time display and progress bar

##### close(self)

Override close to stop timer

### GenerateReportThread

**Inherits from**: QThread

#### Methods

##### __init__(self, custom_prompt, descriptions_text, api_key, selected_model, selected_tables, analysis_steps, agent, us_data, materials_data, pottery_data, site_data, py_dialog, output_language, tomba_data, periodizzazione_data, struttura_data, tma_data, enable_streaming)

##### create_vector_db(self, data, table_name)

Create a vector database from the data for RAG approach.

Args:
    data: List of data records
    table_name: Name of the table for context

Returns:
    FAISS vector store for retrieval

##### retrieve_relevant_data(self, vector_store, query, k)

Retrieve the most relevant data from the vector store based on the query.

Args:
    vector_store: FAISS vector store
    query: Query string
    k: Number of documents to retrieve

Returns:
    String containing the retrieved documents

##### create_rag_chain(self, vector_store, llm)

Create a RetrievalQA chain for the RAG approach.

Args:
    vector_store: FAISS vector store
    llm: Language model

Returns:
    RetrievalQA chain

##### count_tokens(self, text)

Estimate the number of tokens in a text.
This is a simple estimation based on character count.

Args:
    text: The text to count tokens for

Returns:
    Estimated token count

##### validate_us(self)

Validate US data using ArchaeologicalValidators

##### validate_materials(self)

Validate materials data using ArchaeologicalValidators

##### validate_pottery(self)

Validate pottery data using ArchaeologicalValidators

##### validate_tomba(self)

Validate tomb data using ArchaeologicalValidators

##### validate_periodizzazione(self)

Validate periodization data using ArchaeologicalValidators

##### validate_struttura(self)

Validate structure data using ArchaeologicalValidators

##### validate_tma(self)

Validate TMA data

##### format_prompt_from_json(self, prompt_template)

Converte il template JSON in un prompt testuale strutturato in modo sicuro

##### get_language_instructions(self)

Get specific instructions for the selected language

##### format_for_widget(self, text)

Converte il formato immagine per la visualizzazione nel widget e formatta il testo in HTML con stili corretti.

##### run(self)

##### clean_ai_notes(self, text)

Remove AI's notes, recommendations, and meta-commentary from the text

##### create_prompt(self, selected_language)

##### format_materials_table(self)

Formatta i dati dei materiali per la tabella

##### format_pottery_table(self)

Formatta i dati della ceramica per la tabella

##### format_tma_table(self)

Formatta i dati TMA per la tabella

##### create_tma_statistics(self)

Crea statistiche complete per i dati TMA

##### generate_tma_report_section(self)

Genera una sezione completa del report TMA con statistiche e grafici

##### format_tomba_table(self)

Formatta i dati delle tombe per la tabella

##### format_periodizzazione_table(self)

Formatta i dati della periodizzazione per la tabella

##### format_struttura_table(self)

Formatta i dati delle strutture per la tabella

##### create_materials_table(self)

Create a formatted table of materials

##### create_pottery_table(self)

Create a formatted table of pottery

##### format_table(self, table_data)

Format table data into a markdown table

### RAGQueryDialog

Dialog for RAG-based database querying with GPT-5

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### setup_ui(self)

Setup the user interface

##### execute_query(self)

Execute the RAG query with conversation history

##### append_streaming_response(self, token)

Append streaming response tokens to the text results

##### handle_results(self, results)

Handle query results and update conversation history

##### format_text_results(self, text)

Format text results for display

##### display_table(self, table_data)

Display table data in the table widget

##### display_chart(self, chart_data)

Display chart in the chart widget

##### export_text(self)

Export text results

##### export_table_csv(self)

Export table as CSV

##### export_excel(self)

Export table as Excel

##### export_chart(self)

Export chart as image

##### clear_query(self)

Clear query and results

##### handle_error(self, error_msg)

Handle errors

##### update_progress(self, message)

Update progress status

### RAGQueryWorker

Worker thread for RAG queries

**Inherits from**: QThread

#### Methods

##### __init__(self, query, db_manager, api_key, model, conversation_history, parent, enable_streaming, force_reload)

##### run(self)

Execute the RAG query

##### load_all_database_data(self)

Load all available data from database without filters

##### load_database_data(self)

Load relevant data from database

##### prepare_texts(self, data)

Prepare texts for vectorstore

##### create_analysis_tools(self, data, vectorstore)

Create analysis tools

##### query_data(self, query, data)

Query data based on natural language

##### create_table_data(self, request, data)

Create table data from request

##### calculate_statistics(self, request, data)

Calculate statistics from data

##### parse_response(self, response_text, data)

Parse AI response and extract structured data

##### extract_table_from_text(self, text, data)

Extract table data from text response

##### extract_chart_data(self, text, data)

Extract chart data from response

### ProgressDialog

#### Methods

##### __init__(self)

##### setValue(self, value)

##### closeEvent(self, event)

### pyarchinit_US

This class creates the main dialog for the US form

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### natural_sort_key(text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### __init__(self, iface)

##### get_images_for_entities(self, entity_ids, log_signal, entity_type)

##### count_tokens(self, text)

Estimate the number of tokens in the text.
This is a more accurate approximation than just splitting on whitespace.

##### create_vector_db(self, data, table_name)

Create a vector database from the data for RAG approach.

Args:
    data: List of data records
    table_name: Name of the table for context

Returns:
    FAISS vector store for retrieval

##### retrieve_relevant_data(self, vector_store, query, k)

Retrieve the most relevant data from the vector store based on the query.

Args:
    vector_store: FAISS vector store
    query: Query string
    k: Number of documents to retrieve

Returns:
    String containing the retrieved documents

##### create_rag_chain(self, vector_store, llm)

Create a RetrievalQA chain for the RAG approach.

Args:
    vector_store: FAISS vector store
    llm: Language model

Returns:
    RetrievalQA chain

##### split_data_to_fit_tokens(self, data, columns, max_tokens_per_chunk)

Split data into chunks that fit within token limits.
Uses a more efficient algorithm that prioritizes keeping related data together.

Args:
    data: List of data records
    columns: List of columns to include
    max_tokens_per_chunk: Maximum tokens per chunk (default: 8000)

Returns:
    List of chunks, where each chunk is a list of records

##### analyze_site_context(self, report_data)

Analyze site context in detail

##### analyze_stratigraphy_relationships(self, us_data)

Analyze stratigraphic relationships

##### analyze_stratigraphy_by_area(self, us_data)

Analyze stratigraphy by area

##### analyze_materials_by_type(self, material_data)

Analyze materials by type

##### analyze_pottery_by_class(self, pottery_data)

Analyze pottery by class

##### analyze_pottery_photo(self, pottery_data)

Analyze pottery photos

##### validate_us_description(self, us_data)

Validate US descriptions

##### validate_materials_description(self, materials_data)

Validate materials descriptions

##### validate_pottery_description(self, pottery_data)

Validate pottery descriptions

##### create_materials_table(self, materials_data)

Create formatted materials table

##### create_pottery_table(self, pottery_data)

Create formatted pottery table

##### format_us_data(self, us_data)

Format US data for the report

##### format_material_data(self, material_data)

Format material data for the report

##### format_pottery_data(self, pottery_data)

Format pottery data for the report

##### format_tomba_data(self, tomba_data)

Format tomb data for the report

##### format_periodizzazione_data(self, periodizzazione_data)

Format periodization data for the report

##### format_struttura_data(self, struttura_data)

Format structure data for the report

##### format_tma_data(self, tma_data)

Format TMA (Tipologia Materiali Archeologici) data for the report

##### create_analysis_tools(self, report_data, site_data, us_data, materials_data, pottery_data)

Create analysis tools for the LangChain agent

##### create_validation_tools(self, site_data, us_data, materials_data, pottery_data)

Create validation tools for the LangChain agent

##### process_site_table(self, records, current_site, report_data)

Process site table records and update report data

##### process_us_table(self, records, year_filter, us_start, us_end, us_data)

Process US table records and update US data

##### process_materials_table(self, records, year_filter, us_start, us_end, materials_data)

Process materials table records and update materials data

##### process_pottery_table(self, records, year_filter, us_start, us_end, pottery_data)

Process pottery table records and update pottery data

##### filter_records(self, records, year_filter, start, end, year_field, range_field)

Filter records based on year or range criteria

year_filter can be a single year or multiple years separated by commas
e.g. "2024" or "2024, 2025, 2026" or "2024,2025,2026"

##### initialize_report_data(self)

Initialize the report data dictionary with empty values

##### process_table_data(self, table_name, records, current_site, year_filter, us_start, us_end, report_data, us_data, materials_data, pottery_data, tomba_data, periodizzazione_data, struttura_data, tma_data)

Process table data and update corresponding data structures

##### create_system_message(self)

Create the system message for the LangChain agent with full schema knowledge

##### create_custom_prompt(self, formatted_us_data, formatted_material_data, formatted_pottery_data, report_data, formatted_tomba_data, formatted_periodizzazione_data, formatted_struttura_data, formatted_tma_data)

Create the custom prompt for the report generation

##### check_missing_data(self)

Verifica e riporta i dati mancanti in tutte le tabelle selezionate

##### open_rag_query_dialog(self)

Open the RAG query dialog

##### generate_and_display_report(self)

##### on_report_generated(self, report_text, report_data)

##### parse_report_into_sections(self, report_text)

Parse the report text into sections based on headings

##### save_report_as_plain_doc(self, report_text, output_path)

##### process_section_content(self, doc, section_info, content, report_data)

Process the content of a section and add it to the document with proper styles.

Args:
    doc: Word document
    section_info: Dictionary with section information
    content: Text content of the section
    report_data: Dictionary with all report data

##### save_report_to_template(self, report_data, template_path, output_path)

##### convert_markdown_table(self, table_lines, doc)

Convert a list of markdown table lines to a Word table.

Args:
    table_lines: List of strings representing markdown table lines
    doc: Word document to add the table to

Returns:
    Word table object

##### clean_heading(self, text)

Remove markdown heading markers (##, --, etc.) from text.

Args:
    text: Text to clean

Returns:
    Cleaned text

##### sketchgpt(self)

##### on_pushButton_trick_pressed(self)

##### get_input_prompt(self, label)

##### show_warning(self, message)

##### show_error(self, error, original_message)

##### update_all_areas(self)

##### get_all_areas(self, sito)

##### update_rapporti_col(self, sito, area)

##### update_rapporti_col_2(self)

##### ensure_utf8(self, s)

Assicura che una stringa sia codificata correttamente in UTF-8.

Args:
    s (str): La stringa da codificare.

Returns:
    str: La stringa codificata in UTF-8.

##### find_correct_area_for_us(self, us, sito, connection)

Trova l'area corretta per una data unità stratigrafica (us) e sito.

Args:
    us (str): L'identificativo dell'unità stratigrafica.
    sito (str): Il nome del sito.
    connection: Connessione al database esistente.

Returns:
    str: L'area corretta o None se non trovata.

##### clean_comments(self, text_to_clean)

##### EM_extract_node_name(self, node_element)

##### check_if_empty(self, name)

##### on_pushButton_graphml2csv_pressed(self)

##### on_pushButton_csv2us_pressed(self)

##### parse_error_report(self)

Parse the stratigraphic check report to extract different error types

##### fix_empty_areas(self, empty_area_errors)

Update all relationships with empty areas

##### delete_auto_created_forms(self)

Delete all US forms that were automatically created

##### fix_missing_forms(self, missing_form_errors)

Create missing US forms with proper initialization

##### fix_missing_relationships(self, relationship_errors)

Add missing reciprocal relationships

##### get_reciprocal_relationship_type(self, rel_type)

Get the reciprocal relationship type

##### on_pushButton_fix_pressed(self)

Enhanced fix button that offers options to resolve different types of errors

##### check_listoflist(self)

##### log_message(self, message)

Aggiunge un messaggio alla listWidget

##### check_inverse_relationships(self, unverified_list)

##### unit_type_select(self)

##### search_rapp(self)

##### check_v(self)

##### change_label(self)

##### refresh(self)

##### charge_insert_ra(self)

##### sync_tm_from_tma(self)

Synchronize TM (ref_tm) field with cassetta from TMA table

##### charge_insert_ra_pottery(self)

##### listview_us(self)

This function is used to filter the 'Unità Stratigrafiche' table.

##### submit(self)

##### value_check(self)

##### update_filter(self, s)

This function is used to filter the 'Unità Stratigrafiche' table.

##### on_pushButton_globalsearch_pressed(self)

This function is used to search for a specific record in the database.

##### format_struttura_item(self, struttura)

##### charge_struttura_list(self)

This function charges the 'Struttura' combobox with the values from the 'Struttura' table.

##### calculate_centroid_from_geometries(self, geometry_records)

Calculate the centroid of multiple polygon geometries from pyunitastratigrafiche

##### geometry_unitastratigrafiche(self)

This function charges the 'Posizione' combobox with the values from the 'Unità Stratigrafiche' table.
Enhanced to calculate and display centroid when multiple polygons exist.

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

##### update_dating_deferred(self)

This function updates Dating fields after the interface has loaded.
Deferred execution to avoid false "save changes" prompts.

##### update_dating(self)

This function updates the 'Dating' field.
For new records (INSERT mode), only updates the form field.
For existing records (UPDATE mode), can update the database if the user has permissions.

##### on_pushButton_draw_doc_pressed(self)

##### save_us(self)

##### selectRows(self)

##### on_pushButton_update_pressed(self)

##### us_t(self)

##### on_pushButton_go_to_us_pressed(self)

##### on_pushButton_go_to_scheda_pressed(self)

##### enable_button(self, n)

##### enable_button_search(self, n)

##### on_pushButton_connect_pressed(self)

##### connect_p(self)

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

##### generate_US(self)

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

##### db_search_check(self, table_class, field, value)

##### on_pushButton_assigntags_pressed(self)

##### on_done_selecting(self)

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

##### load_and_process_3d_model(self, filepath)

##### show_3d_model(self, file_path)

##### generate_3d_thumbnail(self, filepath)

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

##### openWide_image(self)

##### charge_list(self)

##### msg_sito(self)

##### set_sito(self)

##### generate_list_foto(self)

##### generate_list_pdf(self)

##### on_pushButton_exp_tavole_pressed(self)

##### updateProgressBar(self, tav, tot)

##### on_pushButton_print_pressed(self)

##### setPathpdf(self)

##### setPathdot(self)

##### setPathgraphml(self)

##### setDoc_ref(self)

##### list2pipe(self, x)

##### on_pushButton_graphml_pressed(self)

##### openpdfDir(self)

##### on_pushButton_viewmatrix_pressed(self)

##### on_pushButton_export_matrix_pressed(self)

##### launch_matrix_exp_if(self, msg)

##### export_extended_matrix_action(self)

Alternative method to call Extended Matrix export
Can be called from menu or toolbar

##### on_pushButton_export_extended_matrix_pressed(self)

Export to Extended Matrix format (S3DGraphy)

##### on_pushButton_orderLayers_pressed(self)

##### format_message(self, sing_rapp, us)

##### launch_order_layer_if(self, msg)

##### on_toolButtonPan_toggled(self)

##### on_pushButton_showSelectedFeatures_pressed(self)

##### on_pushButton_sort_pressed(self)

##### on_toolButtonGis_toggled(self)

##### on_toolButtonPreview_toggled(self)

##### on_pushButton_addRaster_pressed(self)

##### on_pushButton_new_rec_pressed(self)

##### save_rapp(self)

##### on_pushButton_save_pressed(self)

##### apikey_gpt(self)

##### on_pushButton_rapp_check_pressed(self)

##### on_pushButton_h_check_pressed(self)

##### data_error_check(self)

##### automaticform_check(self, sito_check)

##### rapporti_stratigrafici_check(self, sito_check)

##### def_strati_to_rapporti_stratigrafici_check(self, sito_check)

##### concat(self, a, b)

##### report_with_phrase(self, ut, us, sing_rapp, periodo_in, fase_in, sito, area)

##### periodi_to_rapporti_stratigrafici_check(self, sito_check)

##### insert_new_rec(self)

##### on_pushButton_insert_row_rapporti_pressed(self)

##### on_pushButton_remove_row_rapporti_pressed(self)

##### on_pushButton_insert_row_rapporti2_pressed(self)

##### on_pushButton_remove_row_rapporti2_pressed(self)

##### on_pushButton_insert_row_inclusi_pressed(self)

##### on_pushButton_remove_row_inclusi_pressed(self)

##### on_pushButton_insert_row_campioni_pressed(self)

##### on_pushButton_remove_row_campioni_pressed(self)

##### on_pushButton_insert_row_organici_pressed(self)

##### on_pushButton_remove_row_organici_pressed(self)

##### on_pushButton_insert_row_inorganici_pressed(self)

##### on_pushButton_remove_row_inorganici_pressed(self)

##### on_pushButton_insert_row_documentazione_pressed(self)

##### on_pushButton_remove_row_documentazione_pressed(self)

##### on_pushButton_insert_row_inclusi_materiali_pressed(self)

##### on_pushButton_remove_row_inclusi_materiali_pressed(self)

##### on_pushButton_insert_row_inclusi_leganti_pressed(self)

##### on_pushButton_remove_row_inclusi_leganti_pressed(self)

##### on_pushButton_insert_row_colore_legante_usm_pressed(self)

##### on_pushButton_remove_row_colore_legante_usm_pressed(self)

##### on_pushButton_insert_row_consistenza_texture_mat_usm_pressed(self)

##### on_pushButton_remove_row_consistenza_texture_mat_usm_pressed(self)

##### on_pushButton_insert_row_colore_materiale_usm_pressed(self)

##### on_pushButton_remove_row_colore_materiale_usm_pressed(self)

##### check_record_state(self)

##### on_pushButton_view_all_pressed(self)

##### view_all(self)

##### charge_records_filtered_by_site(self)

Carica i record filtrati per il sito selezionato

##### on_pushButton_first_rec_pressed(self)

##### on_pushButton_last_rec_pressed(self)

##### on_pushButton_prev_rec_pressed(self)

##### on_pushButton_next_rec_pressed(self)

##### on_pushButton_delete_pressed(self)

##### delete_all_filtered_records(self)

##### on_pushButton_new_search_pressed(self)

##### on_pushButton_showLayer_pressed(self)

for sing_us in range(len(self.DATA_LIST)):
    sing_layer = [self.DATA_LIST[sing_us]]
    self.pyQGIS.charge_vector_layers(sing_layer)

##### on_pushButton_crea_codice_periodo_pressed(self)

##### switch_search_mode(self)

##### on_pushButton_search_go_pressed(self)

##### update_if(self, msg)

##### update_record(self)

##### rec_toupdate(self)

##### charge_records(self)

##### charge_records_n(self)

##### datestrfdate(self)

##### yearstrfdate(self)

##### table2dict(self, n)

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields(self)

##### empty_fields_nosite(self)

##### fill_fields(self, n)

##### get_current_form_data(self)

Get current form data as a dictionary for conflict resolution

##### check_for_updates(self)

Check if current record has been modified by others

##### set_rec_counter(self, t, c)

##### set_LIST_REC_TEMP(self)

##### set_LIST_REC_CORR(self)

##### records_equal_check(self)

##### setComboBoxEditable(self, f, n)

##### setComboBoxEnable(self, f, v)

##### setTableEnable(self, t, v)

##### testing(self, name_file, message)

##### on_pushButton_open_dir_pressed(self)

##### on_pushButton_open_dir_matrix_pressed(self)

##### on_pushButton_open_dir_tavole_pressed(self)

##### check_db(self)

##### cast_tipo_dati(self, valore)

##### on_pushButton_import_ed2pyarchinit_pressed(self)

funzione valida solo per sqlite

##### on_pushButton_filter_us_pressed(self)

##### text2sql(self)

### SQLPromptDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface, parent)

##### clear_fields(self)

Clear all text fields and disable buttons

##### clear_results_table(self)

##### on_prompt_selected(self, index)

##### update_prompt_ui(self)

##### on_select_prompt_clicked(self)

##### record_prompt(self, prompt)

##### load_prompts_from_file(self)

##### save_prompts_to_file(self)

##### handle_text_changed(self)

##### is_sql_query(query)

##### apikey_text2sql(self)

##### on_download_model_clicked(self)

Download the Phi-3 model for local use

##### on_start_button_clicked(self)

##### on_explainsql_button_clicked(self)

##### on_start_sql_query_clicked(self)

Execute SQL query and show results

##### execute_sql_statements(self, statements, con_string)

Execute SQL statements with spatialite specific handling

##### on_explainsql_button_clicked(self)

##### populate_results_list(self, results)

##### on_export_to_excel_button_clicked(self)

##### on_create_graph_button_clicked(self)

##### on_explain_button_clicked(self)

##### add_spatial_layer_to_canvas(self)

##### enhance_spatial_view_creation(self, sql_query)

Enhances a spatial query by converting SELECT to VIEW when needed

### MplCanvas

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self, parent)

### GraphWindow

**Inherits from**: QDockWidget

#### Methods

##### __init__(self)

##### plot(self, data)

### USFilterDialog

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

##### initUI(self)

##### natural_sort_key(self, text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### populate_list_with_us(self)

##### update_list_widget(self, records)

##### filter_list(self, text)

##### apply_filter(self)

##### get_selected_us(self)

### IntegerDelegate

The IntegerDelegate class is a subclass of QStyledItemDelegate from the PyQt5 library. It is used to create a delegate for editing integer values in a Qt model/view framework.
Example Usage
# Import the necessary libraries
from PyQt5 import QtGui, QtWidgets

# Create an instance of the IntegerDelegate class
delegate = IntegerDelegate()

# Set the delegate for a specific column in a QTableView
tableView.setItemDelegateForColumn(columnIndex, delegate)
Code Analysis
Main functionalities
The main functionality of the IntegerDelegate class is to provide a custom editor for integer values in a Qt model/view framework. It creates a QLineEdit widget as the editor and sets a QIntValidator to ensure that only valid integer values can be entered.

Methods
createEditor(parent, option, index): This method is called when a cell in the view needs to be edited. It creates and returns a QLineEdit widget as the editor for the cell. It also sets a QIntValidator to ensure that only valid integer values can be entered.

Fields
None

**Inherits from**: QtWidgets.QStyledItemDelegate

#### Methods

##### __init__(self, parent)

##### createEditor(self, parent, option, index)

### SimpleGPT5Wrapper

#### Methods

##### __init__(self, llm, vectorstore, parent_thread, enable_streaming)

##### invoke(self, input_dict)

### GPT5DirectWrapper

#### Methods

##### __init__(self, llm, tools, system_message, parent_thread)

##### invoke(self, input_dict, config)

Direct LLM invocation that simulates agent behavior

### StreamingHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### OverviewStreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### StreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

### SimplifiedStreamHandler

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

##### on_llm_new_token(self, token)

## Functions

### replace_image(match)

Gestisce la sostituzione delle immagini con il markup HTML appropriato.

**Parameters:**
- `match`

### convert_to_html(text, style_analysis)

**Parameters:**
- `text`
- `style_analysis`

### log(message, level)

**Parameters:**
- `message`
- `level`

### process_file_path(file_path)

**Parameters:**
- `file_path`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### r_list()

### r_id()

### update_done_button()

### r_list()

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

### process_markdown_table(table_lines)

**Parameters:**
- `table_lines`

### process_list_items(items)

**Parameters:**
- `items`

### format_text(text)

**Parameters:**
- `text`

### is_section_title(line)

**Parameters:**
- `line`

### is_standalone_section_title(line, next_line)

**Parameters:**
- `line`
- `next_line`

### safe_convert_data(data)

**Parameters:**
- `data`

### safe_convert_list(data)

**Parameters:**
- `data`

### converti_int(valore)

**Parameters:**
- `valore`

### converti_float(valore)

**Parameters:**
- `valore`

### converti_list(valore)

**Parameters:**
- `valore`

### clean_relationship(value)

**Parameters:**
- `value`

### format_requirements(requirements, indent)

**Parameters:**
- `requirements`
- `indent`

### invoke_batch()

### invoke_with_timeout()

### invoke_with_timeout()

### replace_image(match)

Gestisce la sostituzione delle immagini con il markup HTML appropriato.

**Parameters:**
- `match`

### convert_to_html(text, style_analysis)

**Parameters:**
- `text`
- `style_analysis`

### log(message, level)

**Parameters:**
- `message`
- `level`

### process_file_path(file_path)

**Parameters:**
- `file_path`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### r_list()

### r_id()

### update_done_button()

### r_list()

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

### process_markdown_table(table_lines)

**Parameters:**
- `table_lines`

### process_list_items(items)

**Parameters:**
- `items`

### format_text(text)

**Parameters:**
- `text`

### is_section_title(line)

**Parameters:**
- `line`

### is_standalone_section_title(line, next_line)

**Parameters:**
- `line`
- `next_line`

### safe_convert_data(data)

**Parameters:**
- `data`

### safe_convert_list(data)

**Parameters:**
- `data`

### converti_int(valore)

**Parameters:**
- `valore`

### converti_float(valore)

**Parameters:**
- `valore`

### converti_list(valore)

**Parameters:**
- `valore`

### clean_relationship(value)

**Parameters:**
- `value`

### format_requirements(requirements, indent)

**Parameters:**
- `requirements`
- `indent`

### invoke_batch()

### invoke_with_timeout()

### invoke_with_timeout()

### replace_image(match)

Gestisce la sostituzione delle immagini con il markup HTML appropriato.

**Parameters:**
- `match`

### convert_to_html(text, style_analysis)

**Parameters:**
- `text`
- `style_analysis`

### log(message, level)

**Parameters:**
- `message`
- `level`

### process_file_path(file_path)

**Parameters:**
- `file_path`

### query_media(search_dict, table)

**Parameters:**
- `search_dict`
- `table`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

**Parameters:**
- `message`
- `error_type`
- `filename`

### r_list()

### r_id()

### update_done_button()

### r_list()

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

### process_markdown_table(table_lines)

**Parameters:**
- `table_lines`

### process_list_items(items)

**Parameters:**
- `items`

### format_text(text)

**Parameters:**
- `text`

### is_section_title(line)

**Parameters:**
- `line`

### is_standalone_section_title(line, next_line)

**Parameters:**
- `line`
- `next_line`

### safe_convert_data(data)

**Parameters:**
- `data`

### safe_convert_list(data)

**Parameters:**
- `data`

### converti_int(valore)

**Parameters:**
- `valore`

### converti_float(valore)

**Parameters:**
- `valore`

### converti_list(valore)

**Parameters:**
- `valore`

### clean_relationship(value)

**Parameters:**
- `value`

### format_requirements(requirements, indent)

**Parameters:**
- `requirements`
- `indent`

### invoke_batch()

### invoke_with_timeout()

### invoke_with_timeout()

