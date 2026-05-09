# tabs/US_USM.py

## Overview

This file contains 528 documented elements.

## Classes

### CollapsibleSection

*No description available.*
A `QWidget` subclass that renders a titled, toggleable section composed of a header button and a collapsible content area. Clicking the header button calls `toggle_content`, which alternates the visibility of the content widget and updates the button's arrow indicator (`▼` when expanded, `▶` when collapsed). Child widgets and layouts can be added to the content area via `add_widget` and `add_layout` respectively; the section initializes in the expanded state.

**Inherits from**: QWidget

#### Methods

##### __init__(self, title, parent)

Initializes a `CollapsibleSection` widget with a given title and optional parent widget. Sets up a vertical layout containing a styled `QPushButton` as a header toggle button and a `QWidget` as the collapsible content area, connecting the button's `clicked` signal to the `toggle_content` method. The section is initialized in an expanded state (`is_expanded = True`), with the toggle button displaying a downward arrow prefix followed by the provided title.

##### toggle_content(self)

Toggles the expanded or collapsed state of the content section by inverting the `is_expanded` boolean and updating the visibility of the `content` widget accordingly. Updates the `toggle_button` label to display a downward arrow (`▼`) when expanded or a rightward arrow (`▶`) when collapsed. If the current button text is at least two characters long, the method preserves the existing label text after the arrow prefix; otherwise, it falls back to using `self.title`.

##### add_widget(self, widget)

Adds a widget to the collapsible section's internal content layout by delegating to `self.content_layout.addWidget(widget)`. The provided `widget` is appended to the existing content area managed by `content_layout`. This method accepts a single parameter, `widget`, representing the widget to be added.

##### add_layout(self, layout)

*No description available.*
Adds the given layout to the dialog's `content_layout`. This method delegates directly to `content_layout.addLayout()`, inserting the provided layout as a nested child within the content area. It serves as a convenience wrapper for incorporating sub-layouts into the dialog's main content structure.

### ReportGeneratorDialog

*No description available.*
A modal `QDialog` subclass that provides a user interface for configuring and initiating archaeological report generation. It presents collapsible sections for selecting the output language, enabling streaming text generation, choosing database tables (`site_table`, `us_table`, `inventario_materiali_table`, `pottery_table`, `tma_table`, `periodizzazione_table`, `struttura_table`, `tomba_table`), applying filters by excavation year or US range, and selecting an AI provider via an embedded `LLMSelectorWidget`. The dialog also exposes methods to retrieve the current configuration values and to validate completeness of the selected tables' data before report generation proceeds.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent)

*No description available.*
Initializes a `ReportGeneratorDialog` instance as a modal `QDialog` with the title `'Generatore di Report'` and a fixed size of 500×400 pixels. Constructs the dialog's main vertical layout, which contains collapsible sections for language selection (including a streaming checkbox and a `QComboBox` populated with ten language options), table selection (via a `CheckableComboBox` pre-loaded with eight table names), data filters (excavation year and US range inputs), and an AI provider selector (`LLMSelectorWidget`). A button row at the bottom provides a `'Verifica Dati Mancanti'` validation button alongside standard Ok/Cancel dialog buttons.

##### get_llm_config(self)

Return the LLMConfig chosen in the selector widget.

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

*No description available.*
A `QComboBox` subclass that supports individually checkable items within its dropdown list. Each item can be toggled between checked and unchecked states by pressing it, with the check state managed via a `QStandardItemModel`. Provides methods to add checkable items with a default check state (`add_item`) and to retrieve the text of all currently checked items (`items_checked`).

**Inherits from**: QComboBox

#### Methods

##### __init__(self)

Initializes a `CheckableComboBox` instance by calling the parent `QComboBox` constructor and configuring the widget with a `QStandardItemModel`. Connects the view's `pressed` signal to the `handle_item_pressed` slot to handle item interaction. Applies a stylesheet that disables the default popup behavior by setting `combobox-popup` to `0`.

##### add_item(self, text, checked)

Add a checkable item to the combo box

##### items_checked(self)

Get list of checked items

##### handle_item_pressed(self, index)

Handle item check/uncheck

### ReportDialog

*No description available.*
A modal `QDialog` subclass that provides a split-pane interface for previewing and managing generated reports. The upper pane displays HTML report content in a read-only `QTextEdit`, while the lower pane shows a process terminal with timestamped, color-coded log messages and a time-based progress bar. The dialog supports saving report content to `.docx` or `.txt` files, copying plain text to the clipboard, streaming token appending, and interactive link/image handling via mouse events.

**Inherits from**: QDialog

#### Methods

##### __init__(self, content, parent)

Initializes a `ReportDialog` instance, a modal `QDialog` subclass titled "Report Preview" with a default size of 1000×800 pixels. The constructor builds a vertically split layout containing a read-only HTML report preview area (`QTextEdit`) and a process terminal panel with a time progress bar and elapsed-time label, along with "Save Report", "Copy to Clipboard", and "Close" buttons. If a non-empty `content` string is provided, it is immediately rendered as HTML in the report preview; a `QTimer` is also initialized for time tracking with a default estimated duration of 600 seconds.

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

`GenerateReportThread` is a `QThread` subclass that performs asynchronous generation of structured archaeological excavation reports using a large language model (LLM). It accepts archaeological dataset inputs (stratigraphic units, materials, pottery, tombs, periodization, structures, and TMA records), selected tables, analysis steps, and LLM configuration, then iterates through analysis steps to produce formatted report sections via a LangChain agent or direct provider calls. The class supports multiple LLM providers (OpenAI, Anthropic, Ollama, LM Studio), optional token streaming, Retrieval-Augmented Generation (RAG) via FAISS vector stores for large datasets, image embedding in the output, and multi-language report output, emitting progress and results through the `report_generated`, `log_message`, `report_completed`, and `stream_token` signals.

**Inherits from**: QThread

#### Methods

##### __init__(self, custom_prompt, descriptions_text, api_key, selected_model, selected_tables, analysis_steps, agent, us_data, materials_data, pottery_data, site_data, py_dialog, output_language, tomba_data, periodizzazione_data, struttura_data, tma_data, enable_streaming, llm_config)

Initializes a worker instance for generating archaeological analysis reports, storing all provided parameters as instance attributes. Accepts configuration for the LLM backend either via a full `llm_config` object or legacy `api_key` and `selected_model` fields; when `llm_config` is `None`, the legacy OpenAI-based path is used. Optional data parameters (`tomba_data`, `periodizzazione_data`, `struttura_data`, `tma_data`) default to empty lists if not supplied, and `full_report` and `formatted_report` are initialized as empty strings.

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

Executes the full archaeological report generation pipeline as the thread's main entry point. It converts and validates all input data tables, iterates through each analysis step defined by `ArchaeologicalAnalysis`, and generates report section content via an AI agent (OpenAI/LangChain), applying RAG-based chunking for large datasets and falling back to simplified approaches on token-limit errors. For each completed section, the method emits formatted HTML content progressively via signals, and upon completion emits the full report text along with formatted table data through `report_completed`.

##### clean_ai_notes(self, text)

Remove AI's notes, recommendations, and meta-commentary from the text

##### create_prompt(self, selected_language)

*No description available.*
Constructs a language-specific instruction prompt based on the provided `selected_language` argument. The method maps a set of supported languages — including Italian, English (UK and US), Spanish, French, German, Arabic, Greek, Russian, and Portuguese — to their corresponding instruction strings, then returns the matching instruction as a formatted string. The returned value is intended to be used as a base prompt directive enforcing the response language.

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

### RAGRebuildWorker

Worker thread for rebuilding RAG vectorstore in background

**Inherits from**: QThread

#### Methods

##### __init__(self, db_manager, parent_dialog)

Initializes the worker instance by calling the parent class constructor and storing references to the provided `db_manager` and `parent_dialog` arguments as instance attributes. Accepts a database manager object and an optional parent dialog reference, defaulting `parent_dialog` to `None` if not supplied.

##### run(self)

Rebuild the RAG vectorstore

### RAGQueryDialog

Dialog for RAG-based database querying with GPT-5

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

*No description available.*
Initializes the dialog instance by setting up core attributes, including the database manager reference, conversation history, memory, RAG rebuild worker, and several state-tracking flags (`current_results`, `vectorstore`, `agent`, `last_data_hash`, `auto_update_enabled`). Detects the user's locale from QGIS settings to select the appropriate translation strings from the `TR` dictionary, then configures the window title and dimensions before calling `setup_ui()`. After initialization, applies the application theme via `ThemeManager` if available, and schedules a deferred call to `check_and_rebuild_rag` using a 100 ms `QTimer` single-shot.

##### setup_ui(self)

Setup the user interface

##### check_and_rebuild_rag(self)

Check if RAG needs rebuilding when dialog opens

##### on_rebuild_progress(self, message)

Handle rebuild progress updates

##### on_rebuild_complete(self, result)

Handle rebuild completion

##### on_rebuild_error(self, error_msg)

Handle rebuild errors

##### force_rebuild_rag(self)

Force a complete rebuild of the RAG vectorstore

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

##### display_media(self, media_list)

Display media thumbnails in the gallery widget

##### open_media(self, media)

Open media file in default application

##### export_text(self)

Export text results

##### export_table_csv(self)

Export table as CSV

##### export_excel(self)

Export table as Excel

##### export_chart(self)

Export chart as image

##### export_pdf_report(self)

Export complete report as PDF with text, tables, and charts

##### export_excel_complete(self)

Export complete results to Excel with multiple sheets

##### clear_query(self)

Clear query and results

##### populate_spatial_us_list(self, us_records)

Populate the US list widget for spatial operations

##### on_us_selection_changed(self)

Handle US selection change in the list

##### zoom_to_query_results(self)

Zoom to all US from query results on the map

##### highlight_query_results(self)

Highlight all US from query results on the map

##### highlight_us_on_map(self, us_numbers)

Highlight specific US on the QGIS map

##### clear_highlights(self)

Clear all highlights from the map

##### show_dedicated_map_window(self, us_numbers)

Show query results in a dedicated map window

##### handle_error(self, error_msg)

Handle errors

##### update_progress(self, message)

Update progress status

##### force_refresh_vectorstore(self)

Force refresh of vectorstore cache - clears cache and reloads all data

### RAGQueryWorker

Worker thread for RAG queries

**Inherits from**: QThread

#### Methods

##### __init__(self, query, db_manager, api_key, model, conversation_history, parent, enable_streaming, force_reload, llm_config)

*No description available.*
Initializes the instance by invoking the parent class constructor and assigning all provided parameters to their corresponding instance attributes, including `query`, `db_manager`, `api_key`, `model`, `conversation_history`, `parent`, `enable_streaming`, `force_reload`, and `llm_config`. When `conversation_history` is not provided, it defaults to an empty list; when `llm_config` is `None`, LLM operations fall back to OpenAI using `self.api_key` and `self.model`. Media path attributes `_thumb_path` and `_thumb_resize` are initialized to `None` and then populated via `_load_media_paths()`.

##### get_media_thumbnail_path(self, media_record)

Get the full thumbnail path for a media record

##### get_media_resize_path(self, media_record)

Get the full resize path for a media record from MEDIA_THUMB table

##### run(self)

Execute the RAG query

##### load_all_database_data(self)

Load all available data from database without filters - uses RAG_TABLE_CONFIG

##### load_complete_database_data(self, use_site_filter)

Load complete database data using RAG_TABLE_CONFIG without limits

##### load_database_data(self)

Load relevant data from database - delegates to load_complete_database_data

##### prepare_texts(self, data)

Prepare texts for vectorstore using RAG_TABLE_CONFIG

##### find_media_for_entity(self, entity_type, entity_id, data)

Find media records linked to a specific entity.

Uses pre-loaded mappings to convert readable entity numbers to internal IDs.
entity_type can be: US, CERAMICA, REPERTO
entity_id is the readable number (e.g., US number, not id_us)

##### find_all_media_for_us(self, us_number, data)

Find ALL media related to a US: direct US media + pottery media + inventory media.

This is useful when user asks "show me media for US 644" and wants to see
all related media including pottery and inventory items from that US.

##### extract_media_from_response(self, response_text, data)

Extract media references from AI response and find corresponding thumbnails.

Supports US, CERAMICA (pottery), and REPERTO (inventario materiali).

##### create_analysis_tools(self, data, vectorstore)

Create analysis tools

##### query_data(self, query, data)

Query data based on natural language

##### create_table_data(self, request, data)

Create table data from request

##### calculate_statistics(self, request, data)

Calculate comprehensive statistics from all database tables

##### parse_response(self, response_text, data)

Parse AI response and extract structured data including media

##### extract_table_from_text(self, text, data)

Extract table data from text response

##### extract_chart_data(self, text, data)

Extract chart data from response

### ProgressDialog

*No description available.*
A wrapper class around `QProgressDialog` that displays a modal progress dialog with no cancel button. It supports both determinate progress (when `total_items` is provided) and indeterminate progress (when `total_items` is `None`), and automatically computes and displays elapsed time, percentage completion, and estimated remaining time when updating progress via `setValue`. The dialog is shown immediately on instantiation and forces GUI updates after each state change via `QApplication.processEvents()`.

#### Methods

##### __init__(self, title, total_items)

Initializes a `ProgressDialog` instance by creating and configuring a `QProgressDialog` with the given `title` (defaulting to `"Aggiornamento rapporti area e sito"`). If `total_items` is provided, the progress bar is set to a determinate range from `0` to `total_items`; otherwise, an indeterminate range (`0` to `0`) is used. The dialog is configured as modal with no cancel button, displayed immediately with a minimum duration of `0`, and the current time is recorded in `self.start_time`.

##### setValue(self, value, label_text)

*No description available.*
Updates the progress dialog to reflect the current progress value and refreshes the displayed label text. If `label_text` is provided, it is set directly on the dialog; otherwise, if `total_items` was specified, the label is automatically computed to show the current count, percentage completion, and an estimated remaining time in seconds; if neither condition applies, a generic update message displaying the raw value is shown. After updating, `QApplication.processEvents()` is called to force an immediate GUI refresh.

##### close(self)

*No description available.*
Closes the progress dialog by invoking the `close()` method on the underlying `progressDialog` instance. This method provides a direct interface for dismissing the dialog when the associated operation has completed or been terminated.

##### setLabelText(self, text)

*No description available.*
Sets the label text of the underlying progress dialog to the specified `text` value by delegating directly to `self.progressDialog.setLabelText(text)`. After updating the label, it calls `QApplication.processEvents()` to ensure the UI is refreshed and the new text is rendered immediately.

##### closeEvent(self, event)

Handles the window close event by stopping the refresh timer if it exists and is active, then closes the progress dialog. The incoming close event is explicitly ignored, preventing the window from actually closing. This ensures proper cleanup of the timer resource while keeping the form visible when a close action is triggered.

### pyarchinit_US

This class creates the main dialog for the US form

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### natural_sort_key(text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### __init__(self, iface)

Initializes an instance of the stratigraphic unit form, setting up the QGIS interface reference, UI components, theme management, concurrency management, and an image cache with a configurable limit. It dynamically creates and positions UI widgets (such as a stratigraphic order direction checkbox, a relationship search button, and an AI query button) using multiple fallback layout strategies, and connects signals from combo boxes, buttons, table widgets, and keyboard shortcuts to their respective handler methods. Finally, it attempts a database connection, populates form fields, blocks and unblocks signals during initialization to prevent cascading queries, and starts a periodic refresh timer for detecting concurrent record modifications.

##### get_images_for_entities(self, entity_ids, log_signal, entity_type)

*No description available.*
Retrieves thumbnail image records from the database for a list of entity IDs by querying the `MEDIATOENTITY` and `MEDIA_THUMB` tables. The `entity_type` parameter (defaulting to `'US'`) determines which ID column is used for the lookup, based on an internal mapping that supports types such as `'US'`, `'REPERTO'`, `'INVENTARIO_MATERIALI'`, `'CERAMICA'`, `'POTTERY'`, `'TOMBA'`, and `'STRUTTURA'`; for certain material and pottery types, fallback entity types are also attempted if no records are found. Returns a list of dictionaries, each containing the entity `id`, thumbnail `url`, `caption`, and resolved `entity_type`, or an empty list if no entity IDs are provided or an error occurs.

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

*No description available.*
Orchestrates the full report generation workflow by first checking for missing data and prompting the user to confirm continuation if any are found. Upon user acceptance in the `ReportGeneratorDialog`, it establishes a database connection, fetches and processes records from the selected tables (applying site, year, and US range filters), formats the retrieved data into structured text sections, and constructs a custom LLM prompt. It then verifies internet connectivity, initialises the configured LLM provider (OpenAI, Anthropic, Ollama, or LM Studio) with a `GPT5DirectWrapper` agent, opens a `ReportDialog`, and launches a `GenerateReportThread` whose output signals are connected to the dialog for live display of the generated report.

##### on_report_generated(self, report_text, report_data)

*No description available.*
Handles the post-generation workflow for an archaeological report by validating the generated text, prompting the user to confirm template usage, and collecting a `.docx` save path via a file dialog. If the report text is non-empty and the user confirms, it parses the report into named sections (introduzione, descrizione\_metodologica\_ed\_esito, descrizione\_metodologica, analisi\_stratigrafica, descrizione\_materiali, conclusioni), applying fallback default content for any missing or empty sections, and appending formatted materials and pottery table data to `report_data`. Finally, it verifies the existence and validity of the Word template at `<HOME>/bin/template_report_adarte.docx` and delegates the actual file writing to `save_report_to_template`, displaying a success or error message upon completion.

##### parse_report_into_sections(self, report_text)

Parse the report text into sections based on headings

##### save_report_as_plain_doc(self, report_text, output_path)

*No description available.*
Creates a new Word document containing a single paragraph with the provided report text and saves it to the specified output path. The method instantiates a `Document` object, adds `report_text` as a paragraph, and writes the resulting file to `output_path` via `doc.save()`.

##### process_section_content(self, doc, section_info, content, report_data)

Process the content of a section and add it to the document with proper styles.

Args:
    doc: Word document
    section_info: Dictionary with section information
    content: Text content of the section
    report_data: Dictionary with all report data

##### save_report_to_template(self, report_data, template_path, output_path)

Populates a Word document template with structured archaeological report data and saves the result to a specified output path. The method replaces metadata placeholders (e.g., `{{SITO}}`, `{{CANTIERE}}`, `{{DATA}}`) in the template's first-page paragraphs with corresponding values from `report_data`, then processes and inserts section content (introduction, methodological description, stratigraphic analysis, materials description, and conclusions) by resolving both exact and alternative placeholder patterns. It also applies page margins, inserts page breaks to position content starting at page 5, appends optional materials and pottery tables if present in `report_data`, and returns `True` on successful save or `False` if an exception occurs.

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

Open GPT Sketch window with lazy import to avoid DLL conflicts on Windows.

##### on_pushButton_trick_pressed(self)

Opens a modal dialog window titled "Scorciatoie da tastiera" (Keyboard Shortcuts) with a fixed width of 400 pixels. The dialog displays a `QLabel` containing a list of keyboard shortcuts: `Ctrl+Shift+X`, `Ctrl+U`, `Ctrl+Shift+D`, and `Ctrl+Shift+N`, each paired with a brief Italian description of its associated action. The dialog is presented using `exec()`, blocking interaction with the parent window until it is closed.

##### get_input_prompt(self, label)

*No description available.*
Displays a text input dialog to the user, prompting them to enter a value for the specified `label`. The dialog title is always `"Input"`, and the prompt message is localized based on `self.L`: Italian (`'it'`) renders `"Inserire il {label}"`, while any other language value renders `"Insert the {label}"`. Returns the result of `QInputDialog.getText()`, which includes the entered text and a boolean indicating whether the user confirmed the dialog.

##### show_warning(self, message)

*No description available.*
Displays a warning dialog box to the user indicating that a site or the specified input has not been provided. The dialog title is `"Input"` and the message text is localized based on `self.L`: Italian (`'it'`) renders `"Sito o {message} non forniti."`, while all other language settings render `"Site or {message} not provided."`. The `message` parameter is interpolated directly into the warning string to identify the missing input.

##### show_error(self, error, original_message)

*No description available.*
Displays a warning dialog box to notify the user that an error has occurred. The message is rendered in Italian if the instance language (`self.L`) is set to `'it'`, otherwise it defaults to English; in both cases the dialog includes the `original_message` context and the `error` detail. The dialog presents a single **Ok** button (`QMessageBox.StandardButton.Ok`).

##### update_all_areas(self)

Update all areas with progress tracking (synchronous version)

##### get_all_areas(self, sito)

Retrieves all distinct area values from the `us_table` database table using a SQLAlchemy connection. Accepts an optional `sito` parameter; when provided, the query is filtered to return only areas associated with that site. Returns a list of area strings derived from index-based access on the query result rows.

##### update_rapporti_col(self, sito, area)

*No description available.*
Updates the `rapporti` column of all records in `us_table` that match the specified `sito` (site) and `area` values. For each matching row, it parses the existing `rapporti` string as a Python list and normalises each sub-list to a four-element format by appending the missing `area` and/or `sito` values where the sub-list contains only two or three elements; sub-lists already at four or more elements are truncated to four. If either `sito` or `area` is not provided the method emits a warning and returns immediately; all errors encountered during row retrieval, conversion, or individual record updates are logged to a file at `self.HOME/error_log.txt`, and a final `commit` is issued upon successful completion of all updates.

##### update_rapporti_col_2(self)

Updates both the `rapporti` and `rapporti2` fields for all records in `us_table` belonging to the configured site by enriching each relationship entry with `area` and `sito` columns. For each row retrieved, it parses the stored string representations of the relationship lists, delegates the field-level enrichment to `_update_rapporti_add_area_sito` and `_update_rapporti2_add_area_sito`, and writes back only those records whose serialized value has changed. All operations are executed within a single database transaction that is explicitly committed on success; errors at each stage are logged to `rapporti_update_log.txt` and reported via the UI error/warning helpers, after which the form is refreshed to reflect the updated data.

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

*No description available.*
Removes inline comments from a given string by discarding everything from the `##` delimiter onward. Additionally strips all newline characters from the resulting text. Returns the cleaned string.

##### EM_extract_node_name(self, node_element)

*No description available.*
Parses a GraphML node element to extract its associated metadata by iterating over all `data` child elements and inspecting their attributes. Retrieves the node label, description (with comments stripped), URL, shape type, vertical position, and fill color from yWorks-namespaced sub-elements keyed as `d4`, `d5`, and `d6`. Returns a tuple of `(nodename, nodedescription, nodeurl, nodeshape, node_y_pos, fillcolor)`, defaulting `nodeurl` and `nodedescription` to `'--None--'` if their respective `d4` or `d5` data elements are absent.

##### check_if_empty(self, name)

*No description available.*
Checks whether the provided `name` value is `None` and, if so, replaces it with the placeholder string `"--None--"`. Returns the original `name` value unchanged if it is not `None`, or the substituted placeholder string if it was `None`.

**Parameters:**
- `name` — The value to check for `None`.

**Returns:** The original `name` value, or `"--None--"` if `name` was `None`.

##### on_pushButton_graphml2csv_pressed(self)

*No description available.*
Handles the press event of the `pushButton_graphml2csv` button by prompting the user to select a `.graphml` file via a file dialog, then parsing its XML content using an `ElementTree` instance. It iterates over all parsed elements, applying a regular expression to extract node name components, and applies a series of string-replacement rules to determine the `unit_type` field value for each row. The resulting data — including site, area, stratigraphic unit number, unit type, and stratigraphic index — is written as rows to a CSV file named `graphml2csv.csv` in the `pyarchinit_DB_folder` directory.

##### on_pushButton_csv2us_pressed(self)

Opens a file dialog prompting the user to select a CSV file, then deduplicates its lines by writing unique rows to a staging file (`export_csv2us.csv`). The deduplicated records are parsed as a `DictReader` and the fields `site`, `area`, `us`, `unit_type`, and `i_stratigrafica` are bulk-inserted into the `us_table` table of the connected SQLite database. On success, an informational message box is displayed and the view-all button is triggered; on `AssertionError`, a warning message box is shown instead.

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

Get the reciprocal relationship type with support for all 10 languages

##### find_orphan_forms(self)

Find US forms that have no relationships with other forms

##### delete_orphan_forms(self, orphan_forms)

Delete orphan US forms

##### fix_incomplete_relationships(self, incomplete_errors)

Fix relationships missing area/site information

##### on_pushButton_fix_pressed(self)

Enhanced fix button that offers options to resolve different types of errors

##### check_listoflist(self)

*No description available.*
Validates and synchronizes the inverse stratigraphic relationship for a selected row in `tableWidget_rapporti`, but only when `checkBox_validation_rapp` is checked. It retrieves the selected row's site, area, stratigraphic unit, and relationship values, computes the inverse relationship via `get_inverse_relationship`, then queries the database to determine whether the related stratigraphic unit already exists. Depending on the query result and the number of matching items found in the table, it either updates an existing row with the inverse relationship data, inserts a new row, creates a new database record via `insert_number_of_us_records`, or displays a warning about potential duplicate units; in all cases, `save_rapp` is called to persist changes.

##### log_message(self, message)

Aggiunge un messaggio alla listWidget

##### check_inverse_relationships(self, unverified_list)

Processes a list of unverified stratigraphic relationships by parsing each entry to identify the source unit, target unit, and relationship type, then looking up the expected inverse relationship from `INVERSE_MAP`. For each parsed entry, the method queries the database for the target stratigraphic unit record and checks whether the inverse relationship already exists in `tableWidget_rapporti`; if it does not, the inverse relationship is inserted and saved. Progress is tracked via `progressBar_3`, results are logged to `listWidget_rapp`, and a summary dialog is displayed upon completion indicating how many relationships were corrected out of the total processed.

##### unit_type_select(self)

*No description available.*
Presents a modal `QInputDialog` to the user, populated with localized unit type items retrieved via `get_unit_type_items`, and prompts the user to select a single unit type from the list. Returns the selected item as a string. Silently suppresses any `KeyError` exceptions that occur during execution.

##### search_rapp(self)

*No description available.*
Performs a search operation on `tableWidget_rapporti`, though the current implementation exits immediately due to an unconditional empty string check (`s=''`) that causes an early return before any search is executed. If the early return were not triggered, the method would search for items containing the string `'1'` using `Qt.MatchFlag.MatchContains` and set the first matching item as the current selection in the table widget. The commented-out line suggests the original intent also included clearing the current selection before searching.

##### check_v(self)

*No description available.*
Controls the visibility of the `checkBox_validate` widget based on the current selection in `comboBox_per_iniz`. If the combo box's current text is an empty string, the checkbox is hidden; otherwise, it is made visible.

##### change_label(self)

*No description available.*
Updates the UI dynamically based on the currently selected value in `comboBox_unita_tipo`. When the selected unit type is `'DOC'`, it sets the text of `label_5` using the localised label retrieved from `get_unit_type_label`, hides `comboBox_def_intepret`, and repositions and displays `mQgsFileWidget` and `toolButton_file_doc`; for all other unit types, it hides those file-related widgets and shows `comboBox_def_intepret` instead. Finally, it calls `get_unit_type_label` for the current unit type and, if a label is returned, updates `label_5` accordingly.

##### refresh(self)

*No description available.*
Iterates over each item in `DATA_LIST`, calling `self.us_t()` for every element in the collection. Returns `None` upon completion.

##### charge_insert_ra(self)

Legacy function - now handled by sync_ra_from_inventario

##### sync_tm_from_tma(self)

Synchronize TM (ref_tm) field with cassetta from TMA table

##### sync_ra_from_inventario(self)

Automatically synchronize ref_ra field with inventory numbers from inventario_materiali only.
This populates the field without requiring user interaction with the combobox.
The field becomes read-only when auto-populated from inventory.

##### sync_n_from_pottery(self)

Automatically synchronize ref_n field with id_number from pottery table.
This populates the field without requiring user interaction.
The field becomes read-only when auto-populated from pottery.

##### charge_insert_ra_pottery(self)

Legacy function - pottery is now handled by sync_n_from_pottery for ref_n field

##### sync_current_record(self)

Sincronizza i campi TM, RA e N per il record corrente.
Chiamato quando l'utente clicca 'Sincronizza Record'.

##### sync_all_records(self)

Sincronizza i campi TM, RA e N per TUTTI i record del sito corrente.
Mostra una progress bar durante l'operazione.

##### setup_ref_click_handlers(self)

Setup click handlers for ref_ra and ref_n to open related records

##### eventFilter(self, obj, event)

Handle click events on ref_ra and ref_n fields

##### show_ref_ra_menu(self, pos)

Show context menu with inventory numbers from ref_ra

##### show_ref_n_menu(self, pos)

Show context menu with pottery numbers from ref_n

##### open_inventario_record(self, n_reperto)

Open the Inventario Materiali form and navigate to the specified record

##### open_pottery_record(self, id_number)

Open the Pottery form and navigate to the specified record

##### listview_us(self)

This function is used to filter the 'Unità Stratigrafiche' table.

##### submit(self)

*No description available.*
Attempts to persist pending changes in `model_a` to the database using a transaction, but only if `checkBox_query` is checked. On success, the transaction is committed and an informational message box is displayed in the appropriate language (`'it'` for Italian, `'de'` for German, or English by default). On failure, the transaction is rolled back and a warning message box is shown containing the error text reported by `model_a.lastError()`; if `checkBox_query` is not checked, it is explicitly set to unchecked.

##### value_check(self)

*No description available.*
Responds to changes in the `field` combo box by querying the `us_table` database table, grouping results by the currently selected field text. The retrieved values are processed into a list, stripped of empty entries, sorted, and used to populate the `search_1` widget. Any exceptions raised during this process are silently suppressed.

##### update_filter(self, s)

This function is used to filter the 'Unità Stratigrafiche' table.

##### on_pushButton_globalsearch_pressed(self)

This function is used to search for a specific record in the database.

##### format_struttura_item(self, struttura)

*No description available.*
Formats a `struttura` object into a single string representation by combining its `sigla_struttura` and `numero_struttura` attributes, separated by a hyphen. Returns the resulting formatted string in the pattern `"{sigla_struttura}-{numero_struttura}"`.

##### charge_struttura_list(self)

This function charges the 'Struttura' combobox with the values from the 'Struttura' table.

##### show_struttura_context_menu(self, position)

Show context menu for comboBox_struttura with clear option.

##### clear_struttura_field(self)

Clear the struttura combobox selection.

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

*No description available.*
Handles the press event of the "draw documentation" button by collecting the current site (`sito`), area (`area`), and stratigraphic unit (`us`) values from their respective widgets, along with the document type and document name from the selected row in `tableWidget_documentazione`. Assembles these five values into a list (`lista_draw_doc`) and passes it to `self.pyQGIS.charge_vector_layers_doc_from_scheda_US` to load the corresponding vector layers. Requires exactly one row to be selected in `tableWidget_documentazione` prior to invocation; no explicit selection validation is performed.

##### save_us(self)

*No description available.*
Saves the current US (Unità Stratigrafica) record depending on the active browse status. If the form is in browse mode (`BROWSE_STATUS == "b"`), it validates the data via `data_error_check()` and, if the record has been modified (detected by `records_equal_check()`), prompts the user with a localized confirmation dialog (Italian, German, or English) before calling `update_if()` to persist the changes. If the form is in insert mode, it validates the data and attempts to insert a new record via `insert_new_rec()`, subsequently refreshing the UI fields, counters, and combo boxes upon success.

##### selectRows(self)

Iterates over all rows in `tableWidget_rapporti` and selects each one sequentially. For every row, it retrieves the item in column 1 and skips the row if the item is `None`; otherwise, it reads the `UserRole` data from the item and calls `selectRow` on that row. The net effect is that all valid rows in the table widget are selected.

##### on_pushButton_update_pressed(self)

*No description available.*
Handles the update button press event by querying the database for all records matching the currently selected site (`comboBox_sito`) and area (`comboBox_area`) values. Iterates over each retrieved record, sequentially selecting rows, advancing to the next record, executing `us_t()`, and saving via `save_rapp()`. Progress is reflected in real time on `progressBar_2`, which is reset upon completion of the iteration.

##### us_t(self)

*No description available.*
Validates and populates a secondary relationship table (`tableWidget_rapporti2`) based on the currently selected rows in the primary relationship table (`tableWidget_rapporti`). For each selected row, it constructs a search dictionary from the row's site, area, and US values, queries the database via `DB_MANAGER.query_bool`, and writes the retrieved record fields — including unit type, interpretive description, initial period/phase, area, and site — into the corresponding row of `tableWidget_rapporti2`. This method only executes when the `checkBox_validate` checkbox is checked; otherwise, it performs no action.

##### on_pushButton_go_to_us_pressed(self)

Slot handler triggered when the "Go to US" button is pressed. If the form is in browse mode (`BROWSE_STATUS == "b"`) and the current record has been modified, the user is prompted (in Italian, German, or English depending on `self.L`) to save changes before navigating; if confirmed, the record is updated and the application navigates to the US selected in `tableWidget_rapporti`. In all cases, the method retrieves the site, area, and US values from the selected row of `tableWidget_rapporti`, queries the database for matching records, and either displays a localized warning if no record is found or loads the matching records into `DATA_LIST`, updates the display fields, and optionally refreshes associated GIS vector layers.

##### on_pushButton_go_to_scheda_pressed(self)

*No description available.*
Handles the press event of the "go to scheda" button by retrieving the currently selected row from `tableWidget_rapporti` and extracting the `sito`, `area`, and `us` field values from columns 3, 2, and 1 respectively. It constructs a search dictionary from these values, queries the database via `DB_MANAGER.query_bool`, and populates `DATA_LIST` with the results before refreshing the form fields and setting the browse status to `"b"`. If no row is selected or an error occurs, a localized warning dialog is displayed via `QMessageBox` in Italian, German, or English depending on the value of `self.L`.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary navigation and action buttons by passing the value `n` to each button's `setEnabled` method. The buttons affected include `pushButton_list`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This method provides a single point of control for enabling or disabling the full set of UI buttons simultaneously.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of a collection of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons include navigation controls (`pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`), record management controls (`pushButton_delete`, `pushButton_save`, `pushButton_sort`), and row insertion/removal buttons for the following categories: `rapporti`, `inclusi`, `campioni`, `organici`, `inorganici`, and `documentazione`. This method is typically called to enable or disable the full set of search-related and data-entry controls simultaneously, depending on the boolean or integer value of `n`.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using a `Connection` instance and determining the database server type (e.g., SQLite). On a successful connection, it initialises the database manager (`DB_MANAGER`), sets the current database username in the concurrency manager, configures the permission handler if present, and loads records from the database — populating the UI fields and updating browse state accordingly, or prompting the user with a localised welcome message and opening a new record form if the database is empty. If the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar indicating a connection failure or detected bug.

##### connect_p(self)

Establishes a database connection using a `Connection` object and detects whether the backend is SQLite by inspecting the connection string. If the connection succeeds and the database contains records, it initialises browsing state, populates UI fields and counters, and disables relevant combo box controls; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`) and opens a new record form. Connection or table-related exceptions are caught and reported as localised warning messages via the QGIS message bar.

##### customize_GUI(self)

Initializes and configures all GUI components of the stratigraphic unit form after construction, including updating the icon list widget, setting up click handlers for reference fields, and populating `comboBox_unita_tipo` with language-specific items. Configures column widths for `tableWidget_rapporti`, `tableWidget_rapporti2`, and `tableWidget_documentazione`; adds a `QgsMapCanvas` map preview tab; and applies drag-and-drop settings and selection mode to `iconListWidget`. Assigns language-aware tab titles and button labels (Italian, German, or English), sets editable states on combo boxes, attaches `ComboBoxDelegate` instances populated from the thesaurus batch to multiple table widget columns, and conditionally disables `pushButton_export_matrix` if Graphviz is not installed.

##### loadMapPreview(self, mode)

*No description available.*
Loads and displays a map preview for the currently selected record based on the specified mode. When `mode=0`, it constructs a filter expression using the current record's ID, loads the corresponding geometry layers via `pyQGIS.loadMapPreview_new`, sets them on the map canvas, and zooms to the combined extent of all loaded layers with a 10% buffer — falling back to the full extent if no layers are returned or an error occurs. When `mode=1`, it clears all layers from the map canvas and resets the view to the full extent.

##### dropEvent(self, event)

*No description available.*
Handles drop events by extracting file URLs from the event's MIME data and validating each dropped file against a predefined list of accepted formats, which includes common image formats (`jpg`, `jpeg`, `png`, `tiff`, `tif`, `bmp`), video formats (`mp4`, `avi`, `mov`, `mkv`, `flv`), and 3D model formats (`obj`, `stl`, `ply`, `fbx`, `3ds`). If a dropped file matches an accepted format, it is passed to `load_and_process_image`; otherwise, a warning dialog is displayed indicating the unsupported file type. Any exception raised during file processing is caught and reported to the user via a `QMessageBox` warning, after which the base class `dropEvent` is called.

##### dragEnterEvent(self, event)

*No description available.*
Handles the drag-enter event triggered when a dragged object enters the widget's boundaries. If the dragged data contains URLs, the proposed drop action is accepted; otherwise, the event is ignored. This method controls whether a drag operation is permitted to proceed based on the presence of URL-based MIME data.

##### dragMoveEvent(self, event)

*No description available.*
Handles the drag move event that is triggered as a dragged object is moved over the widget. Unconditionally accepts the proposed drop action by calling `event.acceptProposedAction()`, allowing the drag operation to continue without restriction. This ensures the widget remains a valid drop target throughout the entire drag movement.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database by assigning the next available ID and constructing a media entry with the provided type, filename, file type, and file path, along with a default description of `'Insert description'` and a default tag of `"['imagine']"`. The method attempts to persist the record via `DB_MANAGER.insert_data_session()` and returns `1` on success. If the insertion fails due to an integrity constraint (e.g., a duplicate entry), it returns `0` without displaying a warning; for all other exceptions during record construction, it displays a warning dialog and returns `0`.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table by assigning the next available ID and persisting the provided metadata via `DB_MANAGER`. The method accepts parameters describing the associated media identifier, media type, original filename, thumbnail filename, file type, thumbnail file path, and resized file path, storing each as instance attributes before the database operation. Returns `1` on successful insertion, or `0` if the operation fails — silently suppressing integrity constraint violations (such as duplicate thumbnail entries) and displaying a warning dialog for all other exceptions.

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

*No description available.*
Queries the database for a single Stratigraphic Unit (US) record matching the current values of the site (`comboBox_sito`), area (`comboBox_area`), and US number (`lineEdit_us`) fields. The query is executed via `DB_MANAGER.query_bool` using a dictionary of those three field values against the `'US'` table. Returns a list containing a single tuple of `[id_us, 'US', 'us_table']` for the matched record.

##### assignTags_US(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

*No description available.*
Loads a media file from the given `filepath`, determines its type (image, video, or 3D model) based on the file extension, and processes it for storage. If the configured thumbnail path is set and the file has not already been registered in the database, the method inserts a new media record, generates thumbnail and resized variants using the appropriate utility classes, and optionally uploads the original file to a configured remote storage backend. The processed media item is then added to the UI list widget and tagged via `assignTags_US`; an `AssertionError` raised during processing is caught and reported to the user via a localized warning dialog.

##### db_search_check(self, table_class, field, value)

*No description available.*
Performs a boolean database query against a specified table class using a single field-value pair as the search criterion. The method constructs a search dictionary from the provided field and value, removes any empty entries via the `Utility.remove_empty_items_fr_dict` helper, and delegates the query to `DB_MANAGER.query_bool`. Returns the result of the database query.

##### on_pushButton_search_images_pressed(self)

Open the Image Search dialog with pre-filled filters for current US.

##### on_pushButton_assigntags_pressed(self)

Handles the press event of the `pushButton_assigntags` button by validating that one or more items are selected in `iconListWidget`, displaying a locale-aware warning (`it`, `de`, or default English) if no selection exists. Queries all US records from the database, sorts them by site, area, and US using a natural sort key, and populates a `QListWidget` with the results, including a non-selectable header item and multi-selection enabled. Presents the list alongside a locale-appropriate "Done" button within a new `QWidget`, which when clicked triggers `on_done_selecting`.

##### on_done_selecting(self)

Handles the event triggered when the user confirms their selection by clicking the "Done" button, with button text and message content localized based on the current QGIS locale setting (Italian, German, or English by default). If no items are selected in the US list widget, a locale-appropriate warning message box is displayed; otherwise, the method resolves the selected US records from the database by querying on site, area, and US fields. For each selected media item in `iconListWidget`, the method associates it with each resolved US record by calling `insert_mediaToEntity_rec`, then closes the widget upon completion.

##### on_pushButton_removetags_pressed(self)

*No description available.*
Handles the press event of the "remove tags" button by first verifying that at least one item is selected in `iconListWidget`, displaying a localized warning if no selection exists. If items are selected, the method presents a confirmation dialog (in Italian, German, or English depending on `self.L`) warning that the operation is irreversible; upon confirmation, it resolves the current US record ID via a database query using the values from `comboBox_sito`, `comboBox_area`, and `lineEdit_us`, then calls `DB_MANAGER.remove_tags_from_db_sql_scheda` for each selected item and removes that item from `iconListWidget`. If the user cancels the confirmation dialog, the operation is aborted and no changes are made.

##### on_pushButton_all_images_pressed(self)

*No description available.*
Handles the press event of the "all images" button by querying the database for media thumbnails and media-to-entity relationships, displaying an informational message and returning early if no records are found. If records exist, it constructs and displays a new widget containing a paginated `QListWidget`, a search field, page navigation controls (previous/next buttons and numbered page labels), and a conditionally visible "TAG" button that appears only when an item is selected. Finally, it calls `load_images()` to populate the list and connects the search field's `returnPressed` signal to `filter_items()`.

##### load_images(self, filter_text)

*No description available.*
Loads and displays thumbnail images from the database into `new_list_widget`, applying optional filename filtering via the `filter_text` parameter. The method follows two distinct code paths based on whether the total image count exceeds 100: for larger collections it displays only untagged images with pagination, while for smaller collections it also queries `MEDIATOENTITY` associations and highlights tagged images in white (appending associated US entity names to their labels) and untagged images in yellow. Thumbnail icons are managed through an LRU-style cache (`image_cache`) bounded by `cache_limit`, and the displayed records are paginated according to `current_page` and `page_size`.

##### update_page_labels(self)

*No description available.*
Updates the visual state of all pagination controls to reflect the current page. Enables or disables the previous and next navigation buttons based on whether `current_page` is at the first or last page respectively, and updates each page number label by disabling the one corresponding to the current page. Additionally, refreshes the `current_page_label` and `total_pages_label` text to display the current page number and total page count.

##### go_to_previous_page(self)

*No description available.*
Navigates to the previous page by decrementing `current_page` by one, provided the current page is greater than 1. After updating the page index, it reloads the image set by calling `load_images` with the active filter text stored in `current_filter_text`. If the current page is already 1, the method takes no action.

##### go_to_next_page(self)

*No description available.*
Advances to the next page of images if the current page is less than the total number of pages. Increments `current_page` by one and reloads the image set by calling `load_images` with the current filter text. No action is taken if the current page is already the last page.

##### on_page_label_clicked(self, page, _)

*No description available.*
Handles a page label click event by navigating to the specified page. If the requested `page` differs from `self.current_page`, it updates `self.current_page` to the new value and reloads the image set by calling `self.load_images` with the current filter text. The optional second parameter `_` is accepted but ignored.

##### filter_items(self)

*No description available.*
Retrieves the current text from the search field, converts it to lowercase, and stores it in `self.current_filter_text`. It then invokes `self.load_images` with the updated filter text to reload the displayed images according to the new search criteria.

##### on_done_selecting_all(self)

*No description available.*
Processes all currently selected items in `new_list_widget` by associating each selected media file with the US (Stratigraphic Unit) record identified by the current values of `comboBox_sito`, `comboBox_area`, and `lineEdit_us`. For each selected item, the method queries the database for matching media records and, if a media entry exists and has not already been linked, inserts a new `MEDIATOENTITY` relationship record via `insert_mediaToEntity_rec`. After all associations are processed, the method refreshes the icon list widget and updates the list widget item display.

##### update_list_widget_item(self, item)

Updates a `QListWidgetItem` based on its association with media-to-entity records in the database. It queries the `MEDIATOENTITY` table using the item's text as the media name; if a matching record is found, the item's background is set to white and its text is appended with the associated US identifier retrieved from the `US` table (or `" - US: Not found"` if no US record exists). If no `MEDIATOENTITY` record is found, the item's background is set to yellow to indicate an untagged state.

##### fill_iconListWidget(self)

Populates `iconListWidget` with icon-based list items derived from the currently selected items in `new_list_widget`. For each selected item, it queries the `MEDIA_THUMB` database table using the item's filename, retrieves the corresponding thumbnail path via `Connection`, and constructs a `QListWidgetItem` with the media filename as its text and a `QIcon` loaded from the resolved file path. The resulting item is then added to `iconListWidget` with the media filename stored as custom user-role data.

##### is_media_path_remote(self)

Check if the configured media thumbnail path is remote.
Returns True if remote (HTTP, HTTPS, Cloudinary, Unibo), False if local.

##### update_media_button_visibility(self)

Show/hide toolButtonPreviewMedia based on media path type.
- Remote media: show button (user clicks to load)
- Local media: hide button (auto-load)

##### loadMediaPreviewLocal(self)

Carica le anteprime media per path locali (veloce, senza progress bar).
Usato per auto-caricamento quando i media sono su disco locale.

##### loadMediaPreview(self)

*No description available.*
Clears the `iconListWidget` and loads thumbnail previews for all media entities associated with the current record by querying the `MEDIATOENTITY` table filtered by the current record's ID and entity type `'US'`. All required media thumbnail records are retrieved in a single batch query via `query_media_thumb_batch` rather than individual per-media queries. A modal `QProgressDialog` is displayed during loading to track progress and estimated remaining time, with support for user cancellation; each valid thumbnail is constructed into a `QListWidgetItem` with an icon and added to `iconListWidget`.

##### load_and_process_3d_model(self, filepath)

*No description available.*
Loads a 3D model file from the given `filepath`, extracts the base filename and file extension, and inserts a media record of type `'3d_model'` into the database via `insert_record_media`. A thumbnail image is then generated for the model using `generate_3d_thumbnail`, and a corresponding thumbnail record is inserted into the database using the current maximum media ID. Finally, the model is represented as a `QListWidgetItem` with the generated thumbnail as its icon, added to `iconListWidget`, and tagged via `assignTags_US`.

##### show_3d_model(self, file_path)

Loads and renders a 3D mesh file specified by `file_path` using PyVista, constructing an interactive Qt-based widget that embeds a `QtInteractor` plotter within a horizontal layout. The method applies a JPEG texture to the mesh if a matching file exists, and registers keyboard shortcuts and mouse event observers to support operations including point-to-point distance measurement, bounding box dimension display, view orientation changes, measurement clearing, and image export. Returns the assembled `QWidget` containing the plotter and a toggleable instructions panel.

##### generate_3d_thumbnail(self, filepath)

Generates a thumbnail image for a 3D model file by reading the mesh from the specified filepath using PyVista, rendering it off-screen with the camera positioned in the XY plane, and saving the result as a PNG file. The thumbnail filename is derived from the original file's base name with a `_thumb.png` suffix, and the file is saved to the directory specified by `self.thumb_path`. Returns the full path to the generated thumbnail file.

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

*No description available.*
Processes a 3D model file by loading it with PyVista, generating a thumbnail screenshot rendered from the `'xy'` camera position, and copying the original model file to a resize destination directory (since 3D models cannot be resized like images). If a JPEG texture file sharing the same base name as the model exists in the same source directory, it is also copied to the resize directory. Returns a tuple containing the thumbnail path and the resize path.

##### openWide_image(self)

Opens and displays the full-resolution media file associated with each selected item in `iconListWidget`. For each selected item, the method queries the `MEDIA_THUMB` database table to retrieve the file path and media type, then resolves the full path by combining it with the configured thumbnail resize base URL or directory (supporting local paths as well as remote protocols such as `http://`, `https://`, `cloudinary://`, and `unibo://`). Depending on the resolved media type, the file is displayed in an `ImageViewer` dialog for images, a `VideoPlayerWindow` for videos, or a `QDialog`-wrapped 3D model viewer for `3d_model` types; an error message is shown if the media type is unsupported or the file is not found.

##### charge_list(self)

*No description available.*
Populates all combo box widgets in the form by loading data from the database and thesaurus in a single batch operation. It first resolves the user's locale via `QgsSettings` to determine the active language, then retrieves the list of sites from `site_table` and loads it into the site-related combo boxes. All remaining combo boxes — covering stratigraphic, constructive, material, and personnel categories — are populated using a single batch thesaurus query against `us_table`, with values extracted and sorted via an internal helper function `get_thesaurus_values`.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured site from the `Connection` object and compares it against the value selected in `comboBox_sito`. If a matching site is found, it displays a localised informational message (Italian, German, or English) confirming the active connection. If no site has been configured, it displays a localised warning message prompting the user to set one, and opens the `pyArchInitDialog_Config` dialog if the user confirms.

##### set_sito(self)

Retrieves the configured site identifier from the `Connection` object and queries the database for all records matching that site. If matching records are found, it populates `DATA_LIST`, updates the record counter, fills the form fields, sets the browse status, and disables the site combo box. If no records are found or an exception occurs, it displays a localized warning message (Italian, German, or English) informing the user that the specified site does not exist in the current tab.

##### generate_list_foto(self)

Iterates over all records in `self.DATA_LIST` and builds a list of photo metadata entries for each associated media record found in the `MEDIAVIEW` table. For each record, it retrieves the configured thumbnail path via a `Connection` instance and queries the database using the record's `id_us` and entity type `'US'`; if the thumbnail path is not set, a localised informational message is displayed to the user (supporting Italian, German, and a default English variant). Each valid media entry is appended as a seven-element list containing the site name (with underscores replaced by spaces), area, US identifier, unit type, stratigraphic description, media ID, and full thumbnail file path, and the completed list is returned.

##### generate_list_pdf(self)

Iterates over all records in `self.DATA_LIST` and constructs a flat list of string-converted field values for each record, suitable for PDF list generation. For each record, it queries the database via `self.DB_MANAGER` to retrieve and sort elevation quotes (computing `quota_min` and `quota_max`) and plant/drawing information, applying locale-aware fallback strings based on `self.L` when values are absent. Returns `data_list`, a list of lists where each inner list contains up to 113 ordered field values per record, covering stratigraphic, interpretive, dimensional, masonry, and cataloguing attributes.

##### on_pushButton_exp_tavole_pressed(self)

*No description available.*
Slot triggered when the export tables button is pressed. It establishes a database connection using `Connection`, then instantiates a `Print_utility` object with the current interface and data list, connecting its `progressBarUpdated` signal to `updateProgressBar` for progress tracking. Depending on whether the connection string indicates a PostgreSQL or SQLite backend, it calls `first_batch_try` with the appropriate database type string (`"postgres"` or `"sqlite"`).

##### updateProgressBar(self, tav, tot)

*No description available.*
A PyQt slot that receives two integer arguments, `tav` (current progress value) and `tot` (total value), and updates the UI progress bar accordingly. It calculates the completion percentage by dividing `tav` by `tot`, multiplying by 100, and converting the result to an integer before passing it to `self.progressBar.setValue()`.

**Decorator:** `@pyqtSlot(int, int)`

##### on_pushButton_print_pressed(self)

*No description available.*
Slot triggered when the print push button is pressed. Based on the active interface language (`self.L`), it evaluates the state of the checkboxes `checkBox_s_us`, `checkBox_e_us`, `checkBox_e_foto_t`, and `checkBox_e_foto` to determine which PDF export operations to perform, invoking the appropriate language-specific build methods on a `generate_US_pdf` instance for US record sheets, US index lists, and photo index lists (with or without thumbnails). Each export operation displays a `QMessageBox` confirmation on success or an error/warning message if the data list is empty or an exception is raised; supported languages are Italian (`it`), English (`en`), German (`de`), French (`fr`), Spanish (`es`), Arabic (`ar`), and Catalan (`ca`).

##### setPathpdf(self)

Opens a file dialog allowing the user to select an existing PDF file, filtering for files with a `.pdf` extension and defaulting to the directory specified by `self.PDFFOLDER`. If a file is selected, the chosen path is written to `self.lineEdit_pdf_path` and persisted via `QgsSettings` with an empty key string. The method uses `QFileDialog.getOpenFileName` and operates on the current widget as the parent dialog.

##### setPathdot(self)

Opens a file dialog prompting the user to select an existing `.dot` file, using `self.MATRIX_PATH` as the initial directory and filtering for files with the `.dot` extension. If a valid file path is selected, it updates `self.lineEdit_input` with the chosen path and stores the value in `QgsSettings`.

##### setPathgraphml(self)

Opens a save file dialog prompting the user to specify a file path for a GraphML output file, filtering for files with the `.graphml` extension. If a valid path is selected, it updates the `lineEdit_output` widget with the chosen path and persists the value using `QgsSettings`.

##### setDoc_ref(self)

Opens a save file dialog prompting the user to specify a file path, using `"Set file name"` as the dialog title and `self.MATRIX_PATH` as the default directory, filtered to `" All files (*.*)"`. If a valid path is selected, it extracts the filename from the path and sets the `mQgsFileWidget` text to `'DosCo\\'` prepended to that filename. The selected path is also persisted to `QgsSettings` with an empty key.

##### list2pipe(self, x)

*No description available.*
Converts a string representation of a Python list into a formatted, human-readable string. If the input string contains nested lists (detected by the presence of `[` at the start and specific delimiters), it evaluates the string using `ast.literal_eval`, joins the elements with `', '`, and strips a predefined set of relational label prefixes (e.g., `'Copre'`, `'Taglia'`, `'Uguale a'`) along with residual bracket and quote characters. If the input is a simple list string, it joins the elements of the first evaluated sub-list; otherwise, the input is returned unchanged.

##### on_pushButton_graphml_pressed(self)

Handles the press event of the GraphML export button by invoking the external `dottoxml.py` script via a platform-appropriate Python interpreter (`python` on Windows, `python3` on Linux, or the QGIS-bundled Python 3 on macOS) to convert the input DOT file specified in `lineEdit_input` to a GraphML file at the path specified in `lineEdit_output`, then performs string cleanup on the resulting file to remove artefacts such as `b'` and `graphml>'`. Following the conversion, the method reads database connection settings from `config.cfg` and, for SQLite backends, queries the `us_table` to export stratigraphic unit context data and stratigraphic relationship data (posterior, anterior, and contemporary) into a timestamped `.xlsx` file written to the matrix path, with relationship values cleaned of extraneous characters before output. On successful completion a confirmation `QMessageBox` is displayed; a `ValueError` is caught and reported via a warning dialog.

##### openpdfDir(self)

Opens the application's designated PDF output directory in the operating system's default file manager. The target path is constructed by combining the `PYARCHINIT_HOME` environment variable with the `pyarchinit_PDF_folder` subdirectory. Platform detection is used to invoke the appropriate system command: `os.startfile` on Windows, `open` on macOS (Darwin), and `xdg-open` on Linux and other Unix-like systems.

##### on_pushButton_viewmatrix_pressed(self)

*No description available.*
Handles the press event of the view matrix button by building a dictionary mapping stratigraphic unit (`us`) values to their corresponding IDs from `DATA_LIST`, then instantiating a `pyarchinit_view_Matrix` dialog and invoking its `generate_matrix()` method. After matrix generation, it constructs the expected output image path (`Harris_matrix_viewtred.dot.jpg`) within the `pyarchinit_Matrix_folder` directory under the `PYARCHINIT_HOME` environment variable, opens the image using `PIL.Image`, and renders it in a matplotlib figure with axes hidden. Any `AssertionError` raised during this process is silently suppressed.

##### on_pushButton_export_extended_matrix_integrated(self)

Export Extended Matrix with integrated s3dgraphy + DOT/GraphML support
This provides compatibility with yEd and other graph visualization tools

##### on_pushButton_export_matrix_pressed(self)

*No description available.*
Slot method triggered when the export matrix button is pressed. It builds a dictionary mapping each stratigraphic unit (`us`) to its corresponding `id_us` from `DATA_LIST`, then instantiates a `pyarchinit_Interactive_Matrix` dialog using the current interface, data list, and that dictionary. If the `checkBox_ED` checkbox is checked, it calls `generate_matrix_2()` to produce the matrix data; otherwise, it calls `generate_matrix()`.

##### launch_matrix_exp_if(self, msg)

*No description available.*
Conditionally triggers the matrix export operation based on the value of the `msg` parameter. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `self.on_pushButton_export_matrix_pressed()`; otherwise, no action is taken. This method is intended to serve as a confirmation-gated callback for initiating the matrix export workflow.

##### export_extended_matrix_action(self)

Alternative method to call Extended Matrix export
Can be called from menu or toolbar

##### on_pushButton_export_extended_matrix_pressed(self)

Export to Extended Matrix format (S3DGraphy)

##### on_pushButton_orderLayers_pressed(self)

*No description available.*
Slot handler triggered when the "Order Layers" button is pressed. Displays a localized warning dialog to the user based on the current language setting (`self.L`), alerting them that stratigraphic paradoxes may cause the layer ordering operation to fail. The user's response to the warning dialog is then passed to `self.launch_order_layer_if()`, which determines whether to proceed with the operation.

##### format_message(self, sing_rapp, us)

*No description available.*
Constructs and returns a formatted message string by combining a base message extracted from `sing_rapp[0]`, a language-dependent relativity prefix, and the string representation of `us`.

The relativity prefix is resolved from a predefined mapping of language codes (`'it'`, `'de'`, `'en'`) using the instance attribute `self.L`, falling back to `"concerning: "` if the language code is not found. The resulting string is terminated with a space and a newline character (`" \n"`).

##### launch_order_layer_if(self, msg)

*No description available.*
Executes the stratigraphic ordering workflow when `msg` equals `QMessageBox.StandardButton.Ok`. It validates stratigraphic relationships across all records in `self.DATA_LIST`, checking for missing relationship types, missing report numbers, and paradoxical relationships, then instantiates `Order_layer_graph` to compute the layer order for the current site and area and updates the database with the results via `OL.update_database_with_order`. Upon completion, it writes validation error reports to locale-specific text files in `self.REPORT_PATH` and displays a localized warning message indicating the sorting process has finished.

##### on_toolButtonPan_toggled(self)

*No description available.*
Activates the pan map tool on the `mapPreview` canvas when the corresponding toggle button is triggered. It instantiates a `QgsMapToolPan` object bound to `mapPreview` and sets it as the active map tool via `setMapTool`.

##### on_pushButton_showSelectedFeatures_pressed(self)

*No description available.*
Retrieves the currently selected features from the active map canvas layer and extracts their attribute values corresponding to the field defined by `self.ID_TABLE`. It then queries the database via `self.DB_MANAGER.query_sort` using the collected IDs, populates `self.DATA_LIST` with the results, and refreshes the form fields by calling `self.empty_fields()` and `self.fill_fields()`. If no layer is active, a localised warning message is displayed (Italian, German, or English depending on `self.L`); any other exception is caught and reported via a warning dialog.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog that allows the user to select sort fields and order type. Once confirmed, it converts the selected sort items using `CONVERSION_DICT`, queries the database via `DB_MANAGER.query_sort`, and rebuilds `DATA_LIST` with the sorted results — applying additional natural sort ordering (via `natural_sort_key`) when the `'us'` field is among the sort parameters. After sorting, it resets the browse state, updates the record counter and status labels, and refreshes the displayed fields.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle event of the GIS tool button (`toolButtonGis`), displaying a localized notification message to the user whenever the GIS mode is activated or deactivated. The message content is determined by the current language setting (`self.L`), with distinct messages provided for Italian (`'it'`), German (`'de'`), and a default English fallback. Each notification is presented as a `QMessageBox.warning` dialog informing the user whether their search results will or will not be displayed on the GIS going forward.

##### on_toolButtonPreview_toggled(self)

*No description available.*
Handles the toggle state change of `toolButtonPreview`, displaying a localised informational message box in Italian, German, or English depending on the value of `self.L`. When the button is checked, the method switches the active tab in `tabWidget` to index 13 and calls `self.loadMapPreview()` to load the map preview. When the button is unchecked, `self.loadMapPreview(1)` is called to unload the preview, and for German and English locales the tab is additionally reset to index 0.

##### on_toolButtonPreviewMedia_toggled(self)

Handler per caricare i media quando l'utente clicca il bottone

##### on_pushButton_addRaster_pressed(self)

*No description available.*
Handles the press event of the "Add Raster" button. When triggered, it checks whether the GIS tool button (`toolButtonGis`) is in a checked state, and if so, calls `addRasterLayer()` on the `pyQGIS` instance to add a raster layer. No action is taken if `toolButtonGis` is not checked.

##### on_pushButton_new_rec_pressed(self)

Handles the "New Record" button press event by initializing the form for creating a new entry. If the current browse status is not already in new-record mode (`"n"`), it checks whether a site (`comboBox_sito`) is selected and matches the configured site set: if so, it locks the site field, enables area and unit-type fields, reconnects period and phase combo box signals to `charge_datazione_list`, and clears non-site fields via `empty_fields_nosite()`; otherwise, it makes all fields editable and clears all fields via `empty_fields()`. In both branches, the browse and sort status labels are updated, the record counter is reset, and the action buttons are disabled via `enable_button(0)`.

##### save_rapp(self)

Saves the current report (`rapp`) record by first unchecking the query checkbox and conditionally closing the associated database connection if the checkbox remains checked. If the browse status is `"b"`, it validates the form data via `data_error_check()` and verifies record equality via `records_equal_check()` before proceeding with an update operation confirmed through a `QMessageBox` dialog. No value is returned by this method.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event by performing a concurrency check before persisting data, detecting version conflicts on records in `us_table` and offering the user options to reload, cancel, or overwrite. In browse mode (`BROWSE_STATUS == "b"`), if a data validation check passes and the record has been modified, the user is prompted to confirm saving changes; upon confirmation, fields are cleared, sort status is reset, and the current record is reloaded. In insert mode, a new record is inserted and, on success, the UI state is updated to browse mode with refreshed record counters, combo box states, and field values; localized warning messages are displayed in Italian, German, or English based on `self.L` for change warnings, no-change notifications, and data entry errors.

##### apikey_gpt(self)

*No description available.*
Retrieves the GPT API key by reading it from a file named `gpt_api_key.txt` located in the `bin` subdirectory of `self.HOME`. If the file does not exist, the method prompts the user via a `QInputDialog` to enter a new API key, which is then saved to that file. If the file exists but the key cannot be used, the user is offered the option to replace it with a new key via a confirmation dialog; the method returns the API key string in all cases.

##### on_pushButton_rapp_check_pressed(self)

*No description available.*
Handles the press event of the stratigraphic relationships check button by retrieving the current site and area values from their respective combo boxes (`comboBox_sito_rappcheck` and `comboBox_area_rappcheck`). It then invokes `rapporti_stratigrafici_check` and `def_strati_to_rapporti_stratigrafici_check` (marked as experimental) using the selected site value. If an `AssertionError` is raised during execution, a critical error dialog is displayed; otherwise, a localised success message is shown via an information dialog, with supported languages being Italian (`it`), German (`de`), and English (`en`).

##### on_pushButton_h_check_pressed(self)

Clears the `listWidget_rapp` widget and performs a multi-step archaeological data validation sequence for the currently selected site (`comboBox_sito`) and area (`comboBox_area`), tracking progress via a `ProgressDialog`. The mandatory steps execute `rapporti_stratigrafici_check` and `automaticform_check`; if `checkBox_validate` is checked, `def_strati_to_rapporti_stratigrafici_check` and `periodi_to_rapporti_stratigrafici_check` are also run. If an exception occurs, the progress dialog is closed, the full traceback is passed to an OpenAI GPT model selected by the user, and the streamed response is displayed incrementally in `listWidget_rapp`; on success, a localised success message is added to the same list widget.

##### data_error_check(self)

*No description available.*
Validates all form input fields against required and formatting constraints, branching on the current language setting (`self.L`) to display warning messages in Italian (`'it'`), German (`'de'`), or English (default). Mandatory fields — Site (`comboBox_sito`), Area (`comboBox_area`), SU (`lineEdit_us`), and Unit Type (`comboBox_unita_tipo`) — are checked for emptiness, while numeric fields (USM measurements and elevation/dimension values) are validated as floats and alphanumeric fields are validated against maximum character lengths using an `Error_check` instance. Returns `0` if all checks pass, or `1` if any validation failure is detected.

##### automaticform_check(self, sito_check)

*No description available.*
Queries all records associated with the specified site (`sito_check`) and scans each record's stratigraphic definition field for markers indicating automatically created forms (`'SCHEDA CREATA IN AUTOMATICO'` in Italian, `'FORM MADE AUTOMATIC'` in other languages). For each matching record, it builds a localized report string identifying the site, area, and stratigraphic unit, then appends the full report to the `listWidget_rapp` widget. The resulting report is also written to a language-specific log file (`log_schedeautomatiche.txt`, `log_def_strat_to_SE relation.txt`, or `log_strat_def_to_SU relation.txt`) located in the `pyarchinit_Report_folder` directory under `PYARCHINIT_HOME`.

##### rapporti_stratigrafici_check(self, sito_check)

Validates the stratigraphic relationships for all stratigraphic units (US/SU/SE) belonging to the specified site (`sito_check`) by querying the database and checking for four categories of errors: empty areas in relationships, non-existent referenced units, missing reciprocal relationships, and incomplete relationships lacking area or site data. A multilingual report (Italian, German, or English, determined by `self.L`) is assembled in `self.report_rapporti`, displayed line-by-line in `self.listWidget_rapp`, and written to a UTF-8 text file in the `pyarchinit_Report_folder` directory under `PYARCHINIT_HOME`. If any errors are found, a `QMessageBox` warning is shown to the user summarising the total error count and the path of the saved report file; the method returns `self.report_rapporti`.

##### def_strati_to_rapporti_stratigrafici_check(self, sito_check)

Validates the consistency between stratigraphic definitions (`d_stratigrafica`) and their associated stratigraphic relationships (`rapporti`) for all records belonging to a given site (`sito_check`). It detects logical contradictions — such as a layer (`Strato`/`Stra`/`Stratum`) using a "connected to" relationship, a fill (`Riempimento`/`Fills`/`Verfullüng`) using a cutting or connecting relationship, or a cut (`Taglio`) using a filling or abutting relationship — across Italian, English, and German terminology. Any detected inconsistencies are appended to a report string, added to `self.listWidget_rapp`, and written to a language-specific log file in the `pyarchinit_Report_folder` directory.

##### concat(self, a, b)

Concatenate two numbers as strings and return as integer - safe alternative to eval

##### report_with_phrase(self, ut, us, sing_rapp, periodo_in, fase_in, sito, area)

Validates that a stratigraphic relationship entry has a consistent initial period value when the relationship type is one of `'Si lega a'`, `'Uguale a'`, `'Same as'`, or `'Connected to'`. If the period derived from `sing_rapp[4]` (after stripping hyphens) does not match `periodo_in`, the method returns a formatted Italian error string identifying the site, area, unit, and the expected relationship details. Returns an empty string if the condition is not met or the relationship type is not one of the specified values.

##### periodi_to_rapporti_stratigrafici_check(self, sito_check)

Validates the consistency between periodization/unit-type assignments and stratigraphic relationships for all records belonging to a given site (`sito_check`). For each record, it iterates over the secondary stratigraphic relationships (`rapporti2`), checking that relationship types are directionally correct relative to period/phase values, that unit types (US/USM, SU/WSU) are compatible with the relationship used, and that periodization data is not missing. The resulting report is appended to `self.listWidget_rapp` and written to a language-specific log file in the `pyarchinit_Report_folder` directory.

##### insert_new_rec(self)

*No description available.*
Collects and validates all field values from the form's UI widgets — including table widgets (rapporti, inclusi, campioni, organici, inorganici, documentazione, and USM-related tables) and line edit/combo box fields — converting numeric inputs to their appropriate types (`int` or `float`) and substituting `None` for empty optional numeric fields. It then constructs a new record by calling `self.DB_MANAGER.insert_values` with the next available ID and all collected field values, and attempts to persist it to the database via `self.DB_MANAGER.insert_data_session`. On success, it calls `self.sync_tm_from_tma()` and returns `1`; on failure, it displays a localized warning dialog (distinguishing integrity constraint violations from other errors) and returns `0`.

##### on_pushButton_insert_row_rapporti_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button for the *rapporti* table is pressed. It calls `insert_new_row` with the target widget identifier `'self.tableWidget_rapporti'` to add a new row to that table. This method serves as the direct UI callback binding the button action to the underlying row-insertion logic.

##### on_pushButton_remove_row_rapporti_pressed(self)

*No description available.*
Handles the press event of the "remove row" button associated with the `tableWidget_rapporti` widget. Delegates execution to the `remove_row` method, passing `'self.tableWidget_rapporti'` as the target table identifier. This method serves as the counterpart to `on_pushButton_insert_row_rapporti_pressed`, which inserts rows into the same table.

##### on_pushButton_insert_row_rapporti2_pressed(self)

*No description available.*
Event handler triggered when the user presses the insert-row button associated with the second relationships table. It delegates execution to `insert_new_row`, passing `'self.tableWidget_rapporti2'` as the target table identifier. This results in a new row being added to `tableWidget_rapporti2`.

##### on_pushButton_remove_row_rapporti2_pressed(self)

*No description available.*
Event handler triggered when the "remove row" button associated with the `rapporti2` table is pressed. It delegates execution to the `remove_row` method, passing `'self.tableWidget_rapporti2'` as the target widget identifier. This removes a row from the `tableWidget_rapporti2` table widget as defined by the `remove_row` implementation.

##### on_pushButton_insert_row_inclusi_pressed(self)

*No description available.*
Slot method triggered when the `pushButton_insert_row_inclusi` button is pressed. It delegates to `insert_new_row`, passing `'self.tableWidget_inclusi'` as the target table identifier to insert a new row into the `tableWidget_inclusi` table widget.

##### on_pushButton_remove_row_inclusi_pressed(self)

*No description available.*
Handles the press event of the "remove row" button associated with the inclusi section. When triggered, it calls `self.remove_row` with `'self.tableWidget_inclusi'` as the target, removing a row from the `tableWidget_inclusi` table widget.

##### on_pushButton_insert_row_campioni_pressed(self)

*No description available.*
Event handler triggered when the "insert row" button for the *campioni* section is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidget_campioni'` as the target table widget. This results in a new row being added to `tableWidget_campioni`.

##### on_pushButton_remove_row_campioni_pressed(self)

*No description available.*
Slot method triggered when the "remove row" push button associated with the *campioni* section is pressed. It delegates execution to `self.remove_row()`, passing `'self.tableWidget_campioni'` as the target table identifier, which removes a row from the `tableWidget_campioni` widget.

##### on_pushButton_insert_row_organici_pressed(self)

*No description available.*
Handler triggered when the "insert row" button for the *organici* section is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidget_organici'` as the target table identifier. This results in a new row being inserted into the `tableWidget_organici` widget.

##### on_pushButton_remove_row_organici_pressed(self)

*No description available.*
Handler triggered when the "remove row" button associated with the organici section is pressed. It delegates execution to the `remove_row` method, passing `'self.tableWidget_organici'` as the target table identifier. This results in the removal of a row from the `tableWidget_organici` table widget.

##### on_pushButton_insert_row_inorganici_pressed(self)

*No description available.*
Handler triggered when the insert-row button associated with the inorganici section is pressed. It delegates execution to `self.insert_new_row`, passing `'self.tableWidget_inorganici'` as the target table identifier. This results in a new row being added to the `tableWidget_inorganici` table widget.

##### on_pushButton_remove_row_inorganici_pressed(self)

*No description available.*
Slot method triggered when the "remove row" button for the inorganici section is pressed. It delegates to `self.remove_row`, passing `'self.tableWidget_inorganici'` as the target table identifier to remove a row from the inorganici table widget.

##### on_pushButton_insert_row_documentazione_pressed(self)

*No description available.*
Slot method triggered when the insert-row button associated with the documentation section is pressed. It calls `insert_new_row` with the string `'self.tableWidget_documentazione'` as the target widget identifier, adding a new row to the `tableWidget_documentazione` table widget.

##### on_pushButton_remove_row_documentazione_pressed(self)

*No description available.*
Handles the press event of the "remove row" button associated with the documentation section. Calls `self.remove_row` with `'self.tableWidget_documentazione'` as the target, triggering the removal of a row from the documentation table widget.

##### on_pushButton_insert_row_inclusi_materiali_pressed(self)

*No description available.*
Handler triggered when the insert-row button for the *inclusi materiali* section is pressed. It calls `self.insert_new_row` with the target identifier `'self.tableWidget_inclusi_materiali_usm'`, adding a new row to the `tableWidget_inclusi_materiali_usm` table widget.

##### on_pushButton_remove_row_inclusi_materiali_pressed(self)

*No description available.*
Slot method triggered when the "remove row" button for the *inclusi materiali* section is pressed. It delegates to `self.remove_row`, passing `'self.tableWidget_inclusi_materiali_usm'` as the target table widget from which a row will be removed.

##### on_pushButton_insert_row_inclusi_leganti_pressed(self)

*No description available.*
Handler triggered when the "insert row" button for the *inclusi leganti* section is pressed. It calls `self.insert_new_row` with the target identifier `'self.tableWidget_inclusi_leganti_usm'`, adding a new row to the corresponding table widget. This method follows the same pattern used by analogous insert-row handlers for other USM table widgets in the form.

##### on_pushButton_remove_row_inclusi_leganti_pressed(self)

Handles the press event of the "remove row" button for the inclusi leganti section. Calls `self.remove_row` with the string identifier `'self.tableWidget_inclusi_leganti_usm'` to remove a row from the corresponding table widget. This method is the counterpart to `on_pushButton_insert_row_inclusi_leganti_pressed`, which inserts a new row into the same table.

##### on_pushButton_insert_row_colore_legante_usm_pressed(self)

*No description available.*
Handles the press event of the "insert row" button associated with the binder colour (colore legante) section of the USM form. Calls `insert_new_row` with the target table identifier `'self.tableWidget_colore_legante_usm'` to add a new row to that table widget.

##### on_pushButton_remove_row_colore_legante_usm_pressed(self)

Handles the press event of the "remove row" button for the binder color (colore legante) USM table. Calls `self.remove_row` with the string identifier `'self.tableWidget_colore_legante_usm'` to remove a row from the corresponding table widget. This method follows the same pattern used by analogous remove-row button handlers throughout the form.

##### on_pushButton_insert_row_consistenza_texture_mat_usm_pressed(self)

*No description available.*
Handles the press event of the insert-row button associated with the consistency and texture material USM section. Calls `insert_new_row` with the string `'self.tableWidget_consistenza_texture_mat_usm'` to add a new row to the corresponding table widget.

##### on_pushButton_remove_row_consistenza_texture_mat_usm_pressed(self)

Removes a row from the `tableWidget_consistenza_texture_mat_usm` table widget by invoking the `remove_row` method with the string reference `'self.tableWidget_consistenza_texture_mat_usm'`. This method serves as the event handler triggered when the corresponding remove-row push button for the consistency/texture/material USM table is pressed.

##### on_pushButton_insert_row_colore_materiale_usm_pressed(self)

*No description available.*
Slot method triggered when the corresponding insert-row push button is pressed. It calls `insert_new_row` with the target widget identifier `'self.tableWidget_colore_materiale_usm'`, adding a new row to the `tableWidget_colore_materiale_usm` table widget.

##### on_pushButton_remove_row_colore_materiale_usm_pressed(self)

Removes a row from the `tableWidget_colore_materiale_usm` table widget by delegating to the `remove_row` method with the widget's reference string as argument. This method serves as the event handler for the `pushButton_remove_row_colore_materiale_usm` button's pressed signal.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`; if errors are found, it returns `1` immediately. If no data errors exist but the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog — in Italian, German, or English depending on `self.L` — prompting the user to save the changes, then delegates the response to `update_if()`. Returns `0` after the save prompt is handled, or `1` if data entry errors were detected.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Slot triggered when the "View All" push button is pressed. It unchecks the query checkbox (closing the associated database connection if the checkbox remains checked), clears current field values, reloads all records, and repopulates the fields with the first record in the dataset. The method then resets the browse status to `"b"`, updates the record counter and status labels, sets the current and total record indices accordingly, and resets the sort status to `"n"`.

##### view_all(self)

*No description available.*
Resets the query filter by unchecking `checkBox_query` and clears all input fields before loading records filtered by the currently selected site. If no records are found, it initialises an empty state, enables the relevant combo box and line edit controls, and triggers the new record workflow. When records are available, it populates the fields, sets the browse status to `"b"`, resets the record counter and current record position to the first entry, and clears the sort status indicator.

##### charge_records_filtered_by_site(self)

Carica i record filtrati per il sito selezionato

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Handles the press event of the "first record" navigation button. It updates the icon list widget, unchecks the query checkbox (closing the associated database connection if it was active), and navigates to the first record in `DATA_LIST` by resetting `REC_CORR` to `0`, clearing the current fields, repopulating them with the first record's data, and updating the record counter display. If the current record has unsaved changes (indicated by `check_record_state()` returning `1`) or an exception occurs during navigation, the operation is silently skipped.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Handles the press event of the "last record" button by updating the icon list widget and unchecking the query checkbox. If the record state check does not return `1`, it clears the current fields, sets `REC_CORR` to the index of the last entry in `DATA_LIST` and `REC_TOT` to the total number of entries, then populates the fields with the last record and updates the record counter accordingly. Any exceptions raised during this process are silently suppressed.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by navigating backward through the record set by the number of steps specified in `lineEdit_goto`. It updates the icon list widget, unchecks the query checkbox, and decrements `REC_CORR` by the goto value, preventing navigation below index `-1` by reverting the offset if the boundary is reached. If a valid previous record exists, it clears the current fields and repopulates them with the target record's data, updating the record counter accordingly.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Advances the current record position forward by the number of steps specified in `lineEdit_goto`, then refreshes the form by calling `empty_fields`, `fill_fields`, and `set_rec_counter` to display the new record. If the resulting position meets or exceeds the total record count (`REC_TOT`), the navigation is reverted to prevent moving beyond the last record. Additionally, the method updates the icon list widget, unchecks the query checkbox, and conditionally invokes `selectRows` if the validation checkbox is checked.

##### on_pushButton_delete_pressed(self)

Handles the press event of the delete button by prompting the user with a localized confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. Upon confirmed deletion, it reloads the record list using `charge_records()` and updates all relevant UI state, including record counters, field displays, and list widgets. If the database becomes empty after deletion, internal data lists and counters are reset and form fields are cleared; otherwise, navigation is repositioned to the first record and browse status is restored.

##### delete_all_filtered_records(self)

*No description available.*
Deletes all records currently present in `self.DATA_LIST` after prompting the user for confirmation via a localized warning dialog (Italian, German, or English, based on `self.L`). If `DATA_LIST` is empty, a warning is displayed and the operation is aborted immediately; if the user cancels the confirmation dialog, the action is likewise halted. Upon confirmed deletion, each record is removed individually from the database via `self.DB_MANAGER.delete_one_record`, after which `self.charge_records()` and `self.view_all()` are called to refresh the data and update the user interface.

##### on_pushButton_new_search_pressed(self)

Handles the "New Search" button press event by resetting the interface to search mode (`BROWSE_STATUS = "f"`). It unchecks the query checkbox, clears all input fields, and configures the enabled/editable state of combo boxes, line edits, text edits, and table widgets according to whether a site filter (`sito_set`) is currently active. If a pending record modification is detected (`check_record_state() == 1`) and the browse status is not already in search mode, the method takes no action; otherwise, it disables the search button, updates the status label, resets the record counter and sort label, and conditionally reloads the field lists.

##### on_pushButton_showLayer_pressed(self)

for sing_us in range(len(self.DATA_LIST)):
    sing_layer = [self.DATA_LIST[sing_us]]
    self.pyQGIS.charge_vector_layers(sing_layer)

##### on_pushButton_crea_codice_periodo_pressed(self)

Updates the period code for the currently selected excavation site by calling `set_sito()` to initialize the site context, retrieving the site name from `comboBox_sito`, and invoking `DB_MANAGER.update_cont_per(sito)` to perform the database update. After the update, it clears the current fields and reloads them via `fill_fields(self.REC_CORR)`. A localized confirmation message is displayed in Italian, German, or English depending on `self.L`; if a `KeyError` is raised during the process, a localized warning dialog is shown instead.

##### switch_search_mode(self)

Toggles the search mode between `query_bool_like` and regular `query_bool` by inverting the `use_like_query` boolean flag. When `query_bool_like` mode is activated, the majority of form fields are disabled and a subset of specific fields (`comboBox_area`, `comboBox_struttura`, `lineEdit_quadrato`, `comboBox_settore`, `lineEdit_ambiente`, `lineEdit_saggio`) are selectively re-enabled, and an informational message is displayed instructing the user to use Ctrl+Shift+N to deactivate. When deactivated, most form fields are re-enabled according to their standard editable state, table widgets are re-enabled via `setTableEnable`, and `use_like_query` is explicitly set to `False`.

##### on_pushButton_search_go_pressed(self)

Handles the "search go" button press event by collecting and validating all field values from the form, then executing a database query against the stratigraphic unit table using either a standard boolean query or a LIKE-based query depending on the `use_like_query` flag. If the browse status is not in search mode (`"f"`), a localized warning message is displayed instead of performing the search. On completion, the method updates `DATA_LIST` with the query results, refreshes the UI record counter and field display, conditionally triggers GIS layer loading via `pyQGIS`, and resets `use_like_query` to `False`.

##### update_if(self, msg)

*No description available.*
Conditionally saves the current record based on the value of `msg`; the update is only performed if `msg` equals `QMessageBox.StandardButton.Ok`. On a successful save (indicated by `update_record()` returning `1`), the method reloads and re-sorts the full data list, then restores the navigation position to the previously current record by matching its ID. Finally, it updates the browse status, sort label, and record counter to reflect the refreshed state.

##### update_record(self)

*No description available.*
Attempts to persist changes to the current record by invoking `DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the values returned by `rec_toupdate()`. If a permission error is detected, it is delegated to `permission_handler.handle_permission_error` and the method returns `0`. For other exceptions, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory and a localized warning dialog is displayed to the user (supporting `'it'`, `'en'`, and `'de'` locales), after which the method returns `0`; on success, it returns `1`.

##### rec_toupdate(self)

*No description available.*
Returns the record to be updated by delegating to `self.UTILITY.pos_none_in_list`, passing `self.DATA_LIST_REC_TEMP` as the argument. The result of that call is stored in the local variable `rec_to_update` and returned directly. This method serves as a thin wrapper to retrieve the current temporary record's position or value for update operations.

##### charge_records(self)

*No description available.*
Loads all records from the database into `DATA_LIST` using a single ordered query. Records are retrieved via `DB_MANAGER.query_ordered()`, sorted by `ID_TABLE` in ascending order, replacing a previously used double-query pattern for improved performance.

##### charge_records_n(self)

*No description available.*
Populates `self.DATA_LIST` with all records queried from the database via `self.DB_MANAGER` using `self.MAPPER_TABLE_CLASS`. For SQLite backends, records are appended directly from the query result; for other database backends, record identifiers are first collected, sorted in descending order by `self.ID_TABLE` via `query_sort`, and then reversed before being stored in `self.DATA_LIST`. The end result in both cases is a populated `self.DATA_LIST` reflecting the available records for the mapped table.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"`, producing a string in `DD-MM-YYYY` format. The formatted date string is then returned to the caller.

##### yearstrfdate(self)

*No description available.*
Retrieves the current date and extracts the four-digit year component from it. The method uses `date.today()` to obtain today's date and formats it using `strftime("%Y")`, returning the year as a string. No parameters are accepted beyond the implicit `self`.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n` and resolves the corresponding table widget attribute on the instance, stripping a leading `"self."` prefix if present. Iterates over all rows and columns of the table, collecting non-`None` cell text values into sublists, and skips any empty sublists. Returns a list of sublists, where each non-empty sublist represents a row of cell text values from the table.

##### tableInsertData(self, t, d)

Set the value into alls Grid - uses getattr instead of eval for security

##### insert_new_row(self, table_name)

insert new row into a table based on table_name - uses getattr instead of eval

##### remove_row(self, table_name)

Remove selected row from table - uses getattr instead of eval

##### empty_fields(self)

Resets all form fields and table widgets to their default empty state. For each table widget (rapporti, rapporti2, campioni, inclusi, organici, inorganici, documentazione, colore\_legante\_usm, inclusi\_leganti\_usm, consistenza\_texture\_mat\_usm, inclusi\_materiali\_usm, colore\_materiale\_usm), all existing rows are removed and a single new blank row is inserted. Combo boxes are cleared via `setEditText("")`, line edits and text edits are cleared, and the `lineEdit_anno` and `lineEdit_data_schedatura` fields are conditionally populated with the current year and date respectively when `BROWSE_STATUS` equals `"n"`.

##### empty_fields_nosite(self)

Resets all form fields to their default empty state, excluding the site field. For combo boxes, the method clears the current text using `setEditText("")`; for line edits and text edits, it calls `clear()`. All table widgets (`tableWidget_rapporti`, `tableWidget_rapporti2`, `tableWidget_campioni`, `tableWidget_inclusi`, `tableWidget_organici`, `tableWidget_inorganici`, `tableWidget_documentazione`, `tableWidget_colore_legante_usm`, `tableWidget_inclusi_leganti_usm`, `tableWidget_consistenza_texture_mat_usm`, `tableWidget_inclusi_materiali_usm`, and `tableWidget_colore_materiale_usm`) have all existing rows removed and a single new blank row inserted; when `BROWSE_STATUS` equals `"n"`, the year and date schedatura fields are populated with the current date values rather than being cleared.

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` in `self.DATA_LIST`, setting `self.rec_num` to `n` before filling. Signals on key combo boxes and line edits are blocked during the fill operation to prevent cascading database queries, and are unconditionally unblocked in a `finally` block. After populating fields, the method conditionally loads map and media previews, resets the record comparison list if in browse mode, and updates concurrency tracking attributes (`current_record_version`, `editing_record_id`) and the lock indicator if a `concurrency_manager` is present.

##### get_current_form_data(self)

Get current form data as a dictionary for conflict resolution

##### check_for_updates(self)

Check if current record has been modified by others

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total record count and the current record index by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels by setting `self.label_rec_tot` to the string representation of `self.rec_tot` and `self.label_rec_corrente` to the string representation of `self.rec_corr`.

**Parameters:**
- `t` — The total number of records.
- `c` — The current (active) record index or counter.

##### set_LIST_REC_TEMP(self)

Collects and assembles all field values from the current form into the `DATA_LIST_REC_TEMP` list, which serves as a temporary record buffer. It reads data from table widgets (via `table2dict`), combo boxes, line edits, and text edits, converting each value to a string. Numeric and optional fields (such as `order_layer`, `qmin_usm`, `qmax_usm`, and various quota and dimension fields) are set to `None` or `0` when their corresponding input fields are empty.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` with the string-converted field values of the current record identified by `REC_CORR` within `DATA_LIST`. For each field name defined in `TABLE_FIELDS`, the corresponding attribute is retrieved from `DATA_LIST[REC_CORR]` via `getattr` and appended as a string to `DATA_LIST_REC_CORR`. Raises an `IndexError` if `REC_CORR` is out of the valid bounds of `DATA_LIST`, and re-raises any `IndexError` or unexpected exception encountered during field attribute retrieval after logging the error details.

##### records_equal_check(self)

*No description available.*
Compares the current record state against a temporary record state by invoking `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate `DATA_LIST_REC_TEMP` and `DATA_LIST_REC_CORR` respectively. Returns `0` if the two data lists are equal, or `1` if they differ. In the event of an `IndexError` or any other exception, the method returns `0`.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets - uses getattr instead of eval for security

##### setTableEnable(self, t, v)

Set enabled state for table widgets - uses getattr instead of eval

##### testing(self, name_file, message)

*No description available.*
Opens a file at the path specified by `name_file` in write mode, writes the string representation of `message` to it, and then closes the file. This method overwrites any existing content in the target file. No return value is produced.

##### on_pushButton_open_dir_pressed(self)

Opens the application's PDF output directory in the system's default file manager. The target path is constructed by combining the `PYARCHINIT_HOME` environment variable with the `pyarchinit_PDF_folder` subdirectory. The method handles cross-platform execution by using `os.startfile` on Windows, `open` on macOS (Darwin), and `xdg-open` on all other systems.

##### on_pushButton_open_dir_matrix_pressed(self)

*No description available.*
Opens the `pyarchinit_Matrix_folder` directory located under the `PYARCHINIT_HOME` environment variable path. The method constructs the target path by joining `PYARCHINIT_HOME` with the folder name using the OS-appropriate separator, then launches the directory in the native file manager using `os.startfile` on Windows, `open` on macOS (Darwin), or `xdg-open` on other platforms (e.g., Linux). This method is triggered when the corresponding push button is pressed in the user interface.

##### on_pushButton_open_dir_tavole_pressed(self)

Opens the `pyarchinit_MAPS_folder` directory located under the `PYARCHINIT_HOME` environment variable path. The method detects the current operating system and uses the appropriate system call to launch the folder in the native file manager: `os.startfile` on Windows, `open` on macOS (Darwin), or `xdg-open` on Linux and other platforms.

##### check_db(self)

*No description available.*
Checks the current database connection type by retrieving the connection string via a `Connection` instance and testing whether it references an SQLite database. If the connection string begins with `'sqlite'`, the `pushButton_import_ed2pyarchinit` button is made visible; otherwise, the button is hidden.

##### cast_tipo_dati(self, valore)

*No description available.*
Attempts to cast the input value `valore` to the most appropriate Python data type through a sequential conversion process. It first tries to convert the value to `int`, then to `float` if the integer conversion fails, and returns `None` if the value is an empty string. If all numeric conversions fail and the value is not empty, the value is returned as a `str`.

##### on_pushButton_import_ed2pyarchinit_pressed(self)

funzione valida solo per sqlite

##### on_pushButton_filter_us_pressed(self)

*No description available.*
Handles the press event of the filter US button by saving the current site selection, clearing existing fields, and launching a `USFilterDialog` to allow the user to select specific Stratigraphic Units (US). If the dialog is confirmed, it filters and sorts `DATA_LIST` to include only records whose `us` value matches the user's selection, then updates the record counter, display fields, browse status, and any active GIS or USM vector layers accordingly. If no records match the selected filters, an informational message box is displayed to notify the user.

##### on_pushButton_search_relationships_pressed(self)

Open a dialog showing all stratigraphic relationships of the current US
with navigation, filtering and search-by-type capabilities.

##### text2sql(self)

Opens a `SQLPromptDialog` modal dialog, passing the current `iface` instance to it. The method instantiates the dialog and immediately executes it via `exec()`, blocking until the dialog is closed.

### SQLPromptDialog

`SQLPromptDialog` is a `QDialog` subclass that provides a graphical interface for generating, executing, and analyzing SQL queries using either a remote Text2SQL API or a local language model (`phi3_text2sql.gguf`). It accepts a natural-language prompt from the user, converts it to SQL, displays the generated query, and executes it against either a SpatiaLite or PostGIS database connection. The dialog also supports exporting query results to Excel, rendering data graphs, and adding spatial query results as vector layers to the QGIS map canvas.

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface, parent)

*No description available.*
Initializes a `SQLPromptDialog` instance by calling the parent `QDialog` constructor and setting up all UI elements, including text inputs, combo boxes, radio buttons, push buttons, and a mode selection group for choosing between API-based and local Text2SQL generation. It configures the dialog's layout by arranging all widgets vertically and connects each button and input signal to its corresponding slot method. Instance attributes `generated_sql`, `data`, and `iface` are initialized, the window title is set to `"SQL Query Prompt"`, and previously saved prompts are loaded from `last_five_prompts.txt` in the application's `bin` directory.

##### clear_fields(self)

Clear all text fields and disable buttons

##### clear_results_table(self)

Clears and resets the `results_table` widget if it exists on the instance. It removes all cell contents, resets both the row and column counts to zero, and hides the table from view. The method first checks for the presence of `results_table` using `hasattr` before performing any operations to avoid attribute errors.

##### on_prompt_selected(self, index)

*No description available.*
Handles the selection event from the prompt combo box by retrieving the text of the item at the given `index`. The selected prompt text is then set as the plain text content of `prompt_input`. This method is intended to be used as a slot or callback triggered when the user selects an entry from `prompt_combobox`.

##### update_prompt_ui(self)

*No description available.*
Refreshes the prompt-related UI elements by clearing the existing contents of `prompt_combobox` and repopulating it with the entries stored in `last_five_prompts`. This ensures the combo box reflects the current state of the prompt history.

##### on_select_prompt_clicked(self)

*No description available.*
Handles the select prompt button click event by repopulating the prompt dropdown with the most recently recorded prompts. Clears the existing contents of `prompt_combobox` and refills it with the entries stored in `last_five_prompts`.

##### record_prompt(self, prompt)

*No description available.*
Inserts the given `prompt` at the beginning of the `last_five_prompts` list, then truncates the list to a maximum of five entries. After updating the list, it calls `save_prompts_to_file()` to persist the changes.

##### load_prompts_from_file(self)

*No description available.*
Reads prompts from the file located at `self.path_prompt`, returning up to the first five lines as a list of strings. If the file does not exist, it creates an empty file at that path and returns an empty list.

##### save_prompts_to_file(self)

*No description available.*
Opens the file located at `self.path_prompt` in write mode and iterates over `self.last_five_prompts`, writing each prompt as a separate line to the file. Each prompt is written with a trailing newline character using an f-string. This method overwrites any existing content in the file upon each call.

##### handle_text_changed(self)

*No description available.*
Responds to changes in the prompt input field by evaluating whether the current text constitutes a valid SQL query. If `is_sql_query` returns `True` for the plain text content of `prompt_input`, the `explain_button` is enabled; otherwise, it is disabled.

##### is_sql_query(query)

*No description available.*
A static method that determines whether a given string is a SQL query by checking if it begins with any of a predefined set of SQL keywords. The keywords checked include `select`, `update`, `insert`, `delete`, `create`, `drop`, `alter`, `truncate`, `grant`, `revoke`, `commit`, `rollback`, `savepoint`, `set`, and `show`. The match is performed using a case-insensitive regular expression anchored to the start of the string, and the method returns `True` if any keyword matches, otherwise `False`.

##### apikey_text2sql(self)

Retrieves the API key for the text2sql service by reading it from `text2sql_api_key.txt` located in the application's `bin` directory. If the file does not exist, a `QInputDialog` prompts the user to enter a new API key, which is then saved to that file. Returns the API key as a stripped string.

##### on_download_model_clicked(self)

Download the Phi-3 model for local use

##### on_start_button_clicked(self)

*No description available.*
Handles the start button click event by retrieving the user's prompt from the input field and determining the active database type (SQLite or PostgreSQL) via the current connection string. Depending on the selected mode, it dispatches the prompt either to an external API (`MakeSQL.make_api_request`) or to a local model (`MakeSQL.make_local_request`), prompting the user to download the local model file if it is not found. After SQL generation, it optionally enhances spatial `CREATE VIEW` statements, displays the resulting SQL in the output field, and records the prompt before clearing the input and refreshing the prompt UI.

##### on_explainsql_button_clicked(self)

*No description available.*
Handles the click event for the "Explain SQL" button by retrieving the current prompt text and generating a natural-language explanation of the SQL using either a remote API or a local model, depending on which radio button is selected. When the locale is Italian (`"it"`), an Italian translation instruction is appended to the API request, or the local model path is resolved and validated before use; if the local model file is not found, a critical error dialog is displayed and execution halts. The resulting explanation is written to `self.sql_output` via `setText`.

##### on_start_sql_query_clicked(self)

Execute SQL query and show results

##### execute_sql_statements(self, statements, con_string)

Execute SQL statements with spatialite specific handling

##### on_explainsql_button_clicked(self)

Handles the click event for the "Explain SQL" button by retrieving the user's locale setting and the prompt text from the input field. If the locale is Italian (`"it"`), it appends a translation instruction to the prompt before calling `MakeSQL.explain_request` with the prompt and the API key; otherwise, the prompt is passed unmodified. The generated explanation is then displayed in the `sql_output` text field.

##### populate_results_list(self, results)

*No description available.*
Populates a `QTableWidget` with the provided query results, dynamically creating the table widget if it does not already exist on the layout, or clearing and resizing it if it does. Column headers are derived from the keys of the first result row, and each cell is filled with the string representation of the corresponding value. If `results` is empty or falsy, the table is hidden if it exists.

##### on_export_to_excel_button_clicked(self)

Exports the current contents of `results_table` to an Excel file when the export button is clicked. It reads all row and column data from the table, constructs a `pandas` DataFrame using the table's horizontal header labels as column names, and writes the result to `export_result_sql.xlsx` in the `pyarchinit_EXCEL_folder` directory under `pyarchinit_US.HOME`. Upon completion, the output path is displayed in `results_output`.

##### on_create_graph_button_clicked(self)

*No description available.*
Handles the graph creation button click event by collecting category-value pairs from all rows of `results_table` and passing them to a new `GraphWindow` instance via its `plot` method. The resulting graph window is then embedded in a `QDockWidget` titled `"Graph Widget"` and docked to the bottom dock widget area of the QGIS interface. If any exception occurs during this process, the error message is displayed in `results_output`.

##### on_explain_button_clicked(self)

*No description available.*
Handles the click event for the explain button by retrieving the current text content from the `prompt_input` field and storing it in the local variable `prompt`. The method reads the plain text representation of the input widget's contents. No further processing or output is performed beyond this retrieval within the visible source.

##### add_spatial_layer_to_canvas(self)

Attempts to add a spatial vector layer to the QGIS map canvas based on the currently stored SQL query (`self.generated_sql`). It determines the database type (SpatiaLite or PostgreSQL) from the connection URI, prompts the user to select or enter a geometry column name, constructs the appropriate layer URI, and creates a `QgsVectorLayer` from the query result. If the resulting layer is valid, it is added to the active `QgsProject`, set as the active layer, and the canvas zooms to its extent; otherwise, provider error details are written to `self.results_output`.

##### enhance_spatial_view_creation(self, sql_query)

Enhances a spatial query by converting SELECT to VIEW when needed

### MplCanvas

*No description available.*
A `FigureCanvas` subclass that embeds a Matplotlib `Figure` within a Qt-compatible canvas widget. During initialization, it creates a `Figure` instance and adds a single subplot accessible via the `axes` attribute using the standard `111` grid specification. An optional `parent` parameter is accepted but passed implicitly through the superclass constructor.

**Inherits from**: FigureCanvas

#### Methods

##### __init__(self, parent)

## `__init__` — `GraphWindow`

Initializes a new instance of `GraphWindow` by invoking the parent class `QDockWidget` constructor via `super()`. No additional parameters are accepted beyond the implicit `self`, and no further instance attributes or configuration are applied within this method.

---

## `__init__` — `MplCanvas`

Initializes a new instance of `MplCanvas` by creating a `Figure` object and adding a single subplot at position `111`, storing the resulting axes in `self.axes`. The `Figure` instance is then passed to the `FigureCanvas` parent constructor via `super().__init__(fig)`. Accepts an optional `parent` parameter, which defaults to `None` but is not explicitly forwarded to the parent constructor.

### GraphWindow

*No description available.*
A `QDockWidget` subclass that embeds an `MplCanvas` instance to display bar chart visualisations within a dockable panel. Its `plot` method accepts a sequence of `(category, value)` tuples, clears the current figure, computes each category's percentage share of the total values, and renders a labelled bar chart with percentage annotations above each bar. X-axis labels are auto-rotated to prevent overlap, and the canvas is refreshed via `draw_idle` upon each call to `plot`.

**Inherits from**: QDockWidget

#### Methods

##### __init__(self)

*No description available.*
Initializes the `GraphWindow` instance by calling the parent `QDockWidget` constructor. Creates an `MplCanvas` instance and assigns it to `self.canvas`, then sets it as the widget of the `QDockWidget` via `setWidget`.

##### plot(self, data)

*No description available.*
Clears the existing figure and renders a bar chart on the internal canvas using the provided `data`, which is expected as an iterable of `(category, value)` tuples. Each bar represents a category's percentage contribution relative to the total sum of all values, with the formatted percentage label rendered above each bar. X-axis labels are automatically rotated to prevent overlap, and the chart is refreshed via `draw_idle()` upon completion.

### USFilterDialog

*No description available.*
A `QDialog` subclass that provides a filterable, searchable dialog for selecting Stratigraphic Unit (SU/US) records from a database. It displays records as a scrollable list of checkboxes, supports optional site-based pre-filtering inherited from a parent widget, and applies natural sort ordering to alphanumeric US identifiers. The dialog exposes the user's checkbox selections via `get_selected_us()`, returning a list of selected US ID strings upon confirmation.

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent, site_filter)

Initializes a `USFilterDialog` instance by calling the parent `QDialog` constructor and setting up core instance attributes, including `db_manager`, `selected_us` (an empty list), and `us_records` (an empty list for storing US records). If `site_filter` is not explicitly provided and a `parent` is given, the method attempts to retrieve the current site value from the parent's `comboBox_sito` widget. After resolving the site filter, `initUI` is called to complete the dialog's user interface setup.

##### initUI(self)

Initializes and constructs the dialog's user interface by setting the window title based on the active language (`'it'` for Italian or otherwise English) and appending the site filter value when present. It builds a vertical layout containing a search bar (`QLineEdit`) connected to `filter_list`, a list widget (`QListWidget`) populated via `populate_list_with_us`, and a "Filter" button connected to `apply_filter`. The completed layout is then applied to the dialog.

##### natural_sort_key(self, text)

Convert a string into a list of mixed strings and integers for natural sorting.
This allows proper sorting of alphanumeric US values like US1, US2, US10, US-A, etc.

##### populate_list_with_us(self)

Fetches all records from `us_table` via `db_manager`, optionally filtering them to only those whose `sito` attribute matches `site_filter`. The filtered records are then sorted in natural order using `natural_sort_key` on the `us` field and stored in `us_records`. Finally, the method delegates to `update_list_widget` to refresh the list widget with the sorted records.

##### update_list_widget(self, records)

*No description available.*
Clears the existing contents of `list_widget` and repopulates it with the provided `records` collection. For each record, a `QListWidgetItem` is created and paired with a `QCheckBox` whose label is composed of the record's `unita_tipo` and `us` fields; the `us` value is also stored directly on the checkbox instance. The item and its associated checkbox widget are then added to `list_widget` via `addItem` and `setItemWidget`.

##### filter_list(self, text)

*No description available.*
Filters the list of US records by retaining only those whose `us` attribute, when converted to a string, starts with the provided `text` value. The resulting subset of matching records is then passed to `update_list_widget` to refresh the displayed list widget accordingly.

##### apply_filter(self)

*No description available.*
Clears the `selected_us` list and iterates over all items in `list_widget`, inspecting the checkbox widget associated with each item. For any checked checkbox, it extracts the US ID from the checkbox text (the second whitespace-delimited token) and appends it to `selected_us`. After processing all items, it prints the collected US IDs to standard output and calls `self.accept()` to close the dialog.

##### get_selected_us(self)

Returns the list of selected US IDs stored in the `selected_us` instance attribute.

This method provides read access to the collection of user story identifiers that have been selected within the dialog, and is intended to be called after the dialog has been accepted.

### IntegerDelegate

The IntegerDelegate class is a subclass of QStyledItemDelegate from the PyQt5 library. It is used to create a delegate for editing integer values in a Qt model/view framework.
Example Usage
# Import the necessary libraries
from qgis.PyQt import QtGui, QtWidgets

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

*No description available.*
Initializes a new instance of `IntegerDelegate`, passing the optional `parent` parameter to the superclass constructor via `super()`. The `parent` parameter defaults to `None` if not provided.

##### createEditor(self, parent, option, index)

Creates and returns a `QLineEdit` editor widget configured to accept only integer input. A `QIntValidator` is applied to the editor to restrict user input to valid integer values. The editor is parented to the provided `parent` widget as required by the delegate interface.

### SimpleGPT5Wrapper

*No description available.*
A locally-defined wrapper class that provides direct LLM invocation as an alternative to agent-based query execution. It accepts an LLM instance, a vector store, a parent thread reference, a streaming flag, and an optional dictionary of raw archaeological data, then exposes an `invoke` method that builds a context-enriched prompt by querying the vector store or raw data directly and dispatches the request to the LLM either as a streaming or non-streaming call. The class also provides a helper method, `_get_available_tables_info`, that inspects `raw_data` to report which archaeological database tables (US, USM, TMA, INVENTARIO_MATERIALI, POTTERY, SITE, PERIODIZZAZIONE, STRUTTURA, TOMBA, MEDIA) currently contain data.

#### Methods

##### __init__(self, llm, vectorstore, parent_thread, enable_streaming, raw_data)

Initializes a `SimpleGPT5Wrapper` instance by storing the provided language model, vector store, parent thread, streaming flag, and optional raw data as instance attributes. The `raw_data` parameter defaults to an empty dictionary if no value is supplied. This constructor sets up the core dependencies required for the wrapper's direct LLM call functionality.

##### invoke(self, input_dict)

Processes a natural language query by extracting the input string, building a contextual data payload from either raw archaeological data or vector similarity search results, and constructing a structured prompt for the language model. Query routing distinguishes between requests requiring complete dataset enumeration (e.g., totals, full lists) and specific similarity-based lookups, with additional targeted searches for TMA/cassette, pottery, and inventory data; when a specific stratigraphic unit (US) number is detected, related pottery, inventory, and media records are appended to the context. The assembled prompt is then submitted to the language model either via streaming token emission or a standard synchronous call, returning the response as a dictionary with an `"output"` key.

### GPT5DirectWrapper

*No description available.*
A wrapper class that simulates LangChain agent behavior through direct LLM invocation, designed specifically to work around GPT-5's lack of support for the `stop` parameter. It accepts an LLM instance, a list of tools, an optional system message, and an optional parent thread reference, and exposes an `invoke` method that constructs a prompt, calls the LLM directly, and returns the response in an `{"output": ...}` dictionary. When callbacks are provided via the `config` argument and expose an `on_llm_new_token` handler, the wrapper simulates streaming by emitting the response in fixed-size chunks of 100 characters.

#### Methods

##### __init__(self, llm, tools, system_message, parent_thread)

Initializes a `GPT5DirectWrapper` instance that simulates agent behavior by directly invoking an LLM without relying on LangChain agents. Accepts an LLM instance, a collection of tools, an optional system message, and an optional reference to a parent thread. All provided arguments are stored as instance attributes for use during subsequent invocations.

##### invoke(self, input_dict, config)

Direct LLM invocation that simulates agent behavior

### StreamingHandler

*No description available.*
A callback handler that extends `BaseCallbackHandler` from LangChain to support token-level streaming during LLM inference. It is initialized with a reference to a parent thread and, upon receiving each new token via `on_llm_new_token`, emits that token through the parent thread's `stream_token` signal. The class also maintains a `current_section` string attribute, initialized to an empty string.

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

*No description available.*
Initializes a new `StreamingHandler` instance by accepting a `parent_thread` argument and assigning it to the `self.parent_thread` attribute. Also initializes `self.current_section` as an empty string. This method is a constructor for the `StreamingHandler` class, which extends `BaseCallbackHandler` from `langchain.callbacks.base`.

##### on_llm_new_token(self, token)

*No description available.*
Callback method invoked each time a new token is produced during LLM streaming. Emits the received token via the parent thread's `stream_token` signal. Accepts additional keyword arguments that are not used within the method body.

### OverviewStreamHandler

*No description available.*
A `BaseCallbackHandler` subclass that intercepts streaming token output from a LangChain LLM invocation. It is initialized with a reference to a parent thread and, upon receiving each new token via `on_llm_new_token`, emits that token through the parent thread's `stream_token` signal. This handler is intended to be passed as a callback during agent invocation to enable real-time token streaming to the parent thread.

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

*No description available.*
Initializes an instance of `OverviewStreamHandler` by accepting a `parent_thread` argument and storing it as the instance attribute `self.parent_thread`. This reference is used by the handler's `on_llm_new_token` method to emit streamed tokens back to the parent thread via its `stream_token` signal.

##### on_llm_new_token(self, token)

*No description available.*
A callback method invoked each time the language model produces a new token during streaming. It emits the received `token` via the parent thread's `stream_token` signal, forwarding streamed output incrementally to the parent thread. Additional keyword arguments are accepted but not used.

### StreamHandler

*No description available.*
A `LangChain` callback handler that extends `BaseCallbackHandler` to support token-level streaming for smaller datasets. It holds a reference to a parent thread and accumulates incoming tokens in an internal `buffer` string, while simultaneously emitting each token via the parent thread's `stream_token` signal through the `on_llm_new_token` callback. Instances are only created and registered as callbacks when streaming is enabled on the parent thread.

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

## `__init__` Method

Initializes a `StreamHandler` instance by accepting a `parent_thread` parameter and storing it as an instance attribute. Also initializes an empty string `buffer` attribute intended to accumulate content. This constructor sets up the foundational state required for the handler to process and emit streaming tokens via the parent thread.

##### on_llm_new_token(self, token)

Callback method invoked each time the language model produces a new token during streaming generation. Emits the token via the parent thread's `stream_token` signal for real-time display, and appends the token to the internal `buffer` string to accumulate the complete response. Accepts additional keyword arguments through `**kwargs` which are not used by this implementation.

### FakeMatch

*No description available.*
A locally-defined utility class that mimics the interface of a regular expression match object. It implements a `group(n)` method that returns `manual_path` when `n` is `1`, or `manual_caption` for any other value of `n`. This allows manually parsed path and caption values to be consumed by code that expects a standard regex match result.

#### Methods

##### group(self, n)

*No description available.*
Returns a predefined string value based on the integer argument `n`, simulating the interface of a regular expression match object. When `n` equals `1`, the method returns `manual_path`; for any other value of `n`, it returns `manual_caption`. This method is defined within the inner class `FakeMatch`, which is used as a substitute for an actual regex match result.

### SimplifiedStreamHandler

*No description available.*
A `BaseCallbackHandler` subclass that intercepts streaming tokens produced by a language model during invocation. It accepts a `parent_thread` reference at construction and, for each new token received via `on_llm_new_token`, emits that token through the parent thread's `stream_token` signal. This handler is intended to be passed as a callback when invoking an agent, enabling real-time token streaming to the calling thread.

**Inherits from**: BaseCallbackHandler

#### Methods

##### __init__(self, parent_thread)

*No description available.*
Initializes a `SimplifiedStreamHandler` instance by accepting a `parent_thread` argument and assigning it to the instance attribute `self.parent_thread`. This handler extends `BaseCallbackHandler` from `langchain.callbacks.base` and stores the reference to the parent thread for use in subsequent callback methods.

##### on_llm_new_token(self, token)

*No description available.*
Callback method invoked each time the language model produces a new token during streaming. Emits the received token via the parent thread's `stream_token` signal, forwarding it for downstream handling. Additional keyword arguments are accepted but not used by this implementation.

## Functions

### replace_image(match)

Gestisce la sostituzione delle immagini con il markup HTML appropriato.

**Parameters:**
- `match`

### convert_to_html(text, style_analysis)

Converts a plain text string containing Markdown-style formatting into an HTML string. The function processes the input line by line, translating Markdown constructs — including section headings (underline-style and `#`-prefixed), unordered lists, tables, bold and italic inline formatting, and `[IMMAGINE ...]` image references — into corresponding inline-styled HTML elements. An optional `style_analysis` parameter, when provided, supplies per-line style hints (such as `'title'`, `'heading2'`, `'list'`, or `'normal'`) that override the default content-based style detection for normal text lines.

**Parameters:**
- `text`
- `style_analysis`

### log(message, level)

*No description available.*
An inner helper function defined within `get_images_for_entities` that conditionally emits a log message via the provided signal. If `log_signal` is not `None`, it calls `log_signal.emit(message, level)`; otherwise, the call is silently ignored. The `level` parameter defaults to `"info"`.

**Parameters:**
- `message`
- `level`

### process_file_path(file_path)

*No description available.*
Decodes a percent-encoded (URL-encoded) file path string by converting escape sequences back into their original characters using `urllib.parse.unquote`. Accepts a single parameter `file_path` and returns the decoded string. No additional transformation or validation is applied to the input.

**Parameters:**
- `file_path`

### query_media(search_dict, table)

*No description available.*
Queries a database table for media records matching the criteria specified in `search_dict`, defaulting to the `"MEDIA_THUMB"` table if no table name is provided. Before executing the query, empty items are removed from `search_dict` using `Utility.remove_empty_items_fr_dict`. If the database query raises an exception, a warning dialog is displayed to the user and `None` is returned; otherwise, the query results are returned directly.

**Parameters:**
- `search_dict`
- `table`

### log_error(message, error_type, filename)

*No description available.*
Appends a timestamped log entry to a text file, formatting each entry as `[YYYY-MM-DD HH:MM:SS] {error_type}: {message}`. The timestamp is generated at call time using `datetime.datetime.now()`. The target file defaults to `error_log.txt` located in `self.HOME`, and is opened in append mode with UTF-8 encoding; both `error_type` and `filename` are optional parameters.

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

*No description available.*
```python
def log_error(message, error_type="ERROR", filename=self.HOME+"/rapporti_update_log.txt")
```

Appends a timestamped log entry to a text file, formatting each entry as `[YYYY-MM-DD HH:MM:SS] {error_type}: {message}`. The `error_type` parameter defaults to `"ERROR"` and the target log file defaults to `rapporti_update_log.txt` located in `self.HOME`, both of which can be overridden by the caller. The file is opened in append mode with UTF-8 encoding, preserving any existing log content.

**Parameters:**
- `message`
- `error_type`
- `filename`

### log_error(message, error_type, filename)

*No description available.*
Appends a formatted error entry to a log file, prefixing the message with a timestamp and an error type label. The timestamp is generated at call time using the format `YYYY-MM-DD HH:MM:SS`, and the entry is written as `[{timestamp}] {error_type}: {message}\n`. The default log file is `error_log_fetch.txt` located in `self.HOME`, and the default error type is `"ERROR"`.

**Parameters:**
- `message`
- `error_type`
- `filename`

### get_thesaurus_values(tipologia, attr)

Helper per estrarre valori dal thesaurus batch

**Parameters:**
- `tipologia`
- `attr`

### r_list()

*No description available.*
Retrieves the US (Unità Stratigrafica) records currently selected in `us_listwidget` by parsing each item's text into `sito`, `area`, and `us` components and querying the database via `DB_MANAGER.query_bool`. For each matching record returned, it constructs a list of entries formatted as `[id_us, 'US', 'us_table']`. Returns the compiled list of these structured entries.

### r_id()

*No description available.*
A nested helper function defined within `on_pushButton_removetags_pressed` that retrieves the database ID of a US (Unità Stratigrafica) record matching the currently selected site (`sito`), area (`area`), and US number (`us`) from the corresponding UI controls. It constructs a search dictionary from these three field values and queries the database via `DB_MANAGER.query_bool` against the `'US'` table. Returns the `id_us` value of the first matching record, or `None` if no record is found.

### update_done_button()

*No description available.*
Updates the visibility of the "TAG" `QPushButton` based on the current selection state of `new_list_widget`. If no items are selected, the button is hidden; otherwise, it is made visible and its `clicked` signal is connected to `self.on_done_selecting_all`. This function is registered as a slot for the `new_list_widget.itemSelectionChanged` signal, so it is invoked automatically whenever the selection changes.

### r_list()

*No description available.*
An inner function defined within `on_done_selecting_all` that queries the database for a US (Unità Stratigrafica) record matching the current values of the site (`comboBox_sito`), area (`comboBox_area`), and US number (`lineEdit_us`) fields. It constructs a search dictionary from those values, executes a boolean query against the `'US'` table via `DB_MANAGER.query_bool`, and returns a list of entries in the form `[id_us, 'US', 'us_table']`. The returned list is subsequently iterated alongside selected widget items in the enclosing `on_done_selecting_all` method.

### add_debug_message(message, important)

*No description available.*
Appends a timestamped message to a read-only `QTextEdit` debug widget, prefixing it with the current date and time in `yyyy-MM-dd HH:mm:ss` format. If `important` is `True`, the formatted message is wrapped in `<b>` tags to render it in bold. The widget is capped at 1,000 lines; when this limit is exceeded, the oldest line is removed to maintain the maximum message count.

**Parameters:**
- `message`
- `important`

### mouse_click_callback(obj, event)

*No description available.*
A VTK interactor observer callback that handles left mouse button press events during an active measuring session. When a `LeftButtonPressEvent` is received and `measuring` is `True`, it retrieves the screen coordinates from the plotter's interactor, uses a `vtkCellPicker` with a tolerance of `10` to pick a cell at that position, and resolves the closest point on the mesh surface via `mesh.find_closest_point`. If a valid cell is picked, it invokes `on_left_click` with the closest mesh surface point; otherwise, it logs a debug message indicating no surface point was found.

**Parameters:**
- `obj`
- `event`

### toggle_instructions()

Toggles the visibility of the `instructions_widget` by showing it if it is currently hidden, or hiding it if it is currently visible. This function is connected to the `clicked` signal of a `QPushButton` labeled `"Toggle Instructions"`, allowing the user to interactively show or hide the instructions panel.

### toggle_measure()

Toggles the active measurement state by inverting the boolean `measuring` flag and clearing the `points` collection. When measurement is activated, a debug message `"Misurazione iniziata"` is logged as important; when deactivated, `"Misurazione terminata"` is logged instead. Both `measuring` and `points` are accessed via `nonlocal` binding from the enclosing scope.

### on_left_click(picked_point)

*No description available.*
Handles a left-click event during an active measurement session by recording the selected 3D point. If `measuring` is active and `picked_point` is not `None`, the point is appended to the `points` list and a red sphere marker — sized relative to the mesh length — is added to the plotter at that location. Once exactly two points have been collected, the distance measurement is triggered via `measure_distance` and the `points` list is cleared; if no valid point was picked, a debug message is logged instead.

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

*No description available.*
Logs the provided coordinate pair for diagnostic purposes by emitting a debug message that displays both `coord1` and `coord2`. The message is marked as important, ensuring it is highlighted within the debug output. This function performs no computation or validation on the coordinates beyond reporting their values.

**Parameters:**
- `coord1`
- `coord2`

### measure_distance(point1, point2)

*No description available.*
Computes the Euclidean distance between two 3D points using `numpy.linalg.norm` and visualises the measurement in the active `plotter` by adding a red line connecting the two points. Point labels `"P1"` and `"P2"` are rendered at each endpoint, and a distance label formatted to two decimal places (in centimetres) is placed at the midpoint between them. All created actors (line, point labels, and distance label) are appended to `measurement_objects`, the plotter is re-rendered, and coordinate verification is performed via `verify_coordinates`.

**Parameters:**
- `point1`
- `point2`

### clear_measurements()

*No description available.*
Removes all active measurement actors from the plotter by iterating over `measurement_objects` and calling `plotter.remove_actor()` on each one. After removal, both the `measurement_objects` and `points` collections are cleared. The plotter is then re-rendered to reflect the updated state.

### export_image()

*No description available.*
Opens a save file dialog prompting the user to specify a destination path for a PNG image. If a path is selected, captures a screenshot of the current plotter viewport at a fixed resolution of 300 DPI with dimensions of 15×10 cm (1772×1181 pixels), preserving and restoring the camera position after capture. On success, displays an informational message box; on failure, logs the error via `add_debug_message` and displays a warning dialog.

### get_visible_faces(plotter, mesh)

*No description available.*
Determines which faces of an axis-aligned box mesh are visible from the current camera position. It computes the direction vector from the mesh center to the camera, then tests each of the six cardinal face normals (`±X`, `±Y`, `±Z`) using a dot product to identify faces oriented toward the camera. Returns a list of indices (0–5) corresponding to the faces whose normals have a positive dot product with the camera direction vector.

**Parameters:**
- `plotter`
- `mesh`

### edge_visibility(edge, visible_faces)

*No description available.*
Determines whether a given edge of a cuboid is visible based on the set of currently visible faces. The function uses a hardcoded mapping (`edge_to_faces`) that associates each edge, identified by a tuple of two vertex indices, with the list of face indices it borders. Returns `True` if at least one of the edge's adjacent faces is present in `visible_faces`, otherwise `False`.

**Parameters:**
- `edge`
- `visible_faces`

### calculate_label_position(p1, p2, offset_factor)

*No description available.*
Computes an offset label position for a line segment defined by two endpoints `p1` and `p2`. It first finds the midpoint of the segment, then calculates a perpendicular vector to the segment direction (falling back to a cross product with `[0, 1, 0]` if the primary cross product with `[0, 0, 1]` is zero), and returns a position displaced from the midpoint along that perpendicular by a distance proportional to the segment length scaled by `offset_factor`. The default `offset_factor` is `0.1`.

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

*No description available.*
Creates and adds a billboard text label to a VTK plotter at a specified 3D position, rendered with a white semi-transparent background and black text at font size 6. The label is oriented in 3D space by computing a rotation angle from the given direction vector, or set to 90 degrees if `is_vertical` is `True`. The constructed `vtkBillboardTextActor3D` is added to the provided plotter and returned.

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

*No description available.*
Displays dimensional measurements (width, height, and depth) of a mesh's bounding box within a 3D plotter, but only when the bounding box is visible and the elapsed time since the last update exceeds the configured update interval (`update_interval`). On each valid update, it removes any previously rendered measurement actors, recomputes the bounding box corners from `mesh.bounds`, and draws line actors along three edges (X, Y, and Z axes) with corresponding distance labels expressed in centimetres. Label positions and orientations are determined via `calculate_label_position` and `create_oriented_label`, and the plotter is re-rendered after all actors are added.

### toggle_bounding_box_measures()

*No description available.*
Toggles the visibility of bounding box measurements in the plotter by inverting the `bounding_box_visible` state. When enabled, it calls `show_measures()` to display the measurement objects and logs a debug message indicating activation; when disabled, it removes all current measurement actors from the plotter, clears the `measurement_objects` list, triggers a render update, and logs a deactivation message.

### camera_changed(obj, event)

*No description available.*
A callback function triggered by `InteractionEvent` observer events on the plotter's interactor. When invoked, it checks whether the bounding box is currently visible and, if so, calls `show_measures()` to refresh the displayed measurements. This ensures that bounding box measurements remain synchronized with the current camera position whenever the user interacts with the viewport.

**Parameters:**
- `obj`
- `event`

### reset_view()

*No description available.*
Resets the camera to its default position by calling `plotter.reset_camera()`. This function serves as a convenience wrapper to restore the plotter's camera view to a state that fits all visible actors within the viewport.

### change_view(direction)

*No description available.*
Changes the plotter's camera to a predefined view orientation by dynamically calling the corresponding `view_<direction>` method on the `plotter` object. The `direction` parameter is used to construct the method name via an `f`-string and `getattr`, allowing any direction supported by the plotter's `view_*` interface to be invoked.

**Parameters:**
- `direction`

### process_file_path(file_path)

*No description available.*
Accepts a single `file_path` string parameter and returns the URL-decoded equivalent by calling `urllib.parse.unquote` on it. This converts any percent-encoded characters in the file path (e.g., `%20`) back to their original Unicode representation.

**Parameters:**
- `file_path`

### show_image(file_path)

*No description available.*
Opens a modal image viewer dialog for the specified file path. It instantiates an `ImageViewer` dialog with the current object as its parent, loads the image via `show_image`, and executes the dialog modally using `exec()`.

**Parameters:**
- `file_path`

### show_video(file_path)

*No description available.*
Displays a video file in a `VideoPlayerWindow` instance. If no video player window currently exists, one is instantiated with the parent object, `db_manager`, `icon_list_widget`, and `main_class` references. The specified file is then loaded into the player via `set_video` and the window is made visible.

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

Resolves the full file path for a given media file by detecting whether the provided `file_path` is already an absolute path (identified by a known protocol prefix or leading slash) or requires combination with a base path from `thumb_resize_str`. Once the full path is determined, it dispatches to the appropriate handler based on `media_type`, calling `show_video` for video files, `show_image` for images, or `self.show_3d_model` for 3D models. If the `media_type` is not one of the three supported values, a warning dialog is displayed to the user indicating an unsupported media type.

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

*No description available.*
Queries the database for media records matching the provided search criteria. It accepts a dictionary of search parameters and an optional table name (defaulting to `"MEDIA_THUMB"`), removes empty entries from the dictionary via `Utility.remove_empty_items_fr_dict`, then delegates to `self.DB_MANAGER.query_bool` to execute the boolean query. If the database query raises an exception, a warning dialog is displayed and `None` is returned.

**Parameters:**
- `search_dict`
- `table`

### get_thesaurus_values(tipologia, attr, unique)

Helper per estrarre valori dal thesaurus batch

**Parameters:**
- `tipologia`
- `attr`
- `unique`

### populate_table(rows)

rows: list of [rel_type, us_number, area, sito, direction_label]

**Parameters:**
- `rows`

### navigate_to_us(us_num, area_val, sito_val)

Navigate to a specific US record.

**Parameters:**
- `us_num`
- `area_val`
- `sito_val`

### get_all_relationship_rows(show_inverse)

Build complete list of relationship rows for the current US.

**Parameters:**
- `show_inverse`

### do_search_by_type()

Search all US records in the current sito for a given relationship type.

### filter_data_list_by_type()

Filter DATA_LIST to only US records that have the selected relationship type.

### show_all_related()

Filter DATA_LIST to only show US records related to the current US.

### process_markdown_table(table_lines)

*No description available.*
Converts a list of Markdown table lines into an HTML table string. The first line is treated as the header row and rendered as `<th>` elements with a light grey background; any line matching the pattern `^\|\s*[-:]+\s*\|` is identified as a separator and skipped; all remaining lines are rendered as `<td>` data rows. The resulting table is wrapped in a `<table>` element with inline styles for full width, collapsed borders, and 15px vertical margin, and the completed HTML is returned as a single newline-joined string.

**Parameters:**
- `table_lines`

### process_list_items(items)

*No description available.*
Converts a list of plain-text list items into an HTML unordered list (`<ul>`) with inline styles applied. For each item, the leading list marker (`- `) is stripped and any remaining text is passed through `format_text` to apply inline formatting such as bold or italic. Returns the complete HTML list as a single newline-joined string.

**Parameters:**
- `items`

### format_text(text)

*No description available.*
Applies inline text formatting to a plain-text string by converting markdown-style syntax to HTML `<span>` elements. Double asterisks (`**...**`) are replaced with bold styling, single asterisks (`*...*`) with italic styling, and `[IMMAGINE...:...]` references are processed via a `replace_image` callback. Returns the transformed string with all substitutions applied.

**Parameters:**
- `text`

### is_section_title(line)

*No description available.*
Checks whether a given line of text matches one of the predefined section title strings used in the document. The recognized titles are: `"INTRODUZIONE"`, `"METODOLOGIA DI SCAVO"`, `"ANALISI STRATIGRAFICA E INTERPRETAZIONE"`, `"CATALOGO DEI MATERIALI"`, `"DESCRIZIONE DEI MATERIALI"`, and `"CONCLUSIONI"`. Returns `True` if the line exactly matches one of these titles, `False` otherwise.

**Parameters:**
- `line`

### is_standalone_section_title(line, next_line)

*No description available.*
Determines whether a given line constitutes a standalone section title rather than part of a paragraph. A line is considered a standalone section title if it satisfies `is_section_title` and is immediately followed by a non-empty line composed entirely of `=` characters. Returns a boolean result based on both conditions being met simultaneously.

**Parameters:**
- `line`
- `next_line`

### safe_convert_data(data)

Converts input data of various types into a dictionary, handling `None`, `tuple`, and `dict` inputs safely. If the input is a tuple containing dictionaries, the first element is returned; if it contains nested tuples, conversion to a dictionary is attempted via `dict()`; if conversion fails or the type is unrecognized, an empty dictionary is returned. Returns the input unchanged if it is already a `dict`, and returns an empty dictionary for all other unsupported types or on any conversion error.

**Parameters:**
- `data`

### safe_convert_list(data)

*No description available.*
Converts the provided `data` argument into a list in a safe, fault-tolerant manner. If `data` is `None` or any type other than `list` or `tuple`, the function returns an empty list; if `data` is a `tuple`, it is converted to a `list`; if `data` is already a `list`, it is returned unchanged. This function prevents type-related errors by guaranteeing a `list` return value regardless of the input type.

**Parameters:**
- `data`

### converti_int(valore)

*No description available.*
Converts a value intended for integer use by replacing an empty string with the string `'0'`. If the input `valore` is not an empty string, it is returned unchanged. This function is used as a helper to ensure empty fields do not cause type errors when inserting data into the SQLite database.

**Parameters:**
- `valore`

### converti_float(valore)

*No description available.*
Converts a value intended for float processing by normalizing empty string inputs. If `valore` is an empty string (`''`), the function returns `None`; otherwise, it returns `valore` unchanged. This ensures that empty fields are represented as `None` rather than an empty string in float contexts.

**Parameters:**
- `valore`

### converti_list(valore)

*No description available.*
Converts an empty string value to the string representation of an empty list (`'[]'`). If the input value is not an empty string, it is returned unchanged. This function is used as a conversion helper when reading CSV data, ensuring that list-type fields have a valid default representation when no value is present.

**Parameters:**
- `valore`

### clean_relationship(value)

*No description available.*
Cleans and normalizes a comma-separated string of relationship values by extracting only isolated numeric tokens from each segment. Duplicate numbers are removed, and any occurrence of `'1'` that follows another number is filtered out. Returns an empty string if the input is `None` or an empty string; otherwise returns the cleaned numbers joined as a comma-separated string.

**Parameters:**
- `value`

### format_requirements(requirements, indent)

*No description available.*
Recursively formats a list of content requirements into indented bullet-point strings. Each string element in the input list is rendered as a single indented bullet, while dictionary elements are rendered as a labeled group (`"For each {key}:"`) followed by their associated sub-requirements at an increased indentation level. Returns a flat list of formatted strings ready to be extended into a prompt.

**Parameters:**
- `requirements`
- `indent`

### invoke_batch()

*No description available.*
Invokes the RAG chain with a combined prompt containing all questions in a single call, passing a dictionary with the key `"query"` mapped to `combined_prompt`. Returns the `"result"` value extracted from the RAG chain's response dictionary. This function is intended to be submitted to a `ThreadPoolExecutor` for execution with a timeout, rather than called directly.

### invoke_with_timeout()

*No description available.*
Invokes the `rag_chain` with the enhanced question as input and returns the `"result"` field from the response. This function serves as a callable wrapper intended to be submitted to a `ThreadPoolExecutor`, enabling external timeout control over the RAG chain execution. It takes no parameters and its return value is the string result produced by `rag_chain.invoke({"query": enhanced_question})`.

### invoke_with_timeout()

*No description available.*
A locally defined helper function that invokes the `rag_chain` with a formatted query dictionary containing `enhanced_question` and returns the `"result"` field from the response. It is designed to be submitted to a `ThreadPoolExecutor` so that the caller can enforce a 30-second timeout on the RAG chain invocation. No parameters are accepted and no exceptions are explicitly handled within the function itself.

