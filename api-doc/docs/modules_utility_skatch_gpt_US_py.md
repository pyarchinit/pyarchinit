# modules/utility/skatch_gpt_US.py

## Overview

This file contains 64 documented elements.

## Classes

### Worker

*No description available.*
A `QThread` subclass that performs asynchronous HTTP streaming requests to a language model API endpoint. It emits three signals during execution: `progress_updated` (int) to report streaming progress, `content_updated` (str) to deliver incremental response content chunks, and `tokens_used_updated` (int, float) to report token consumption alongside a calculated cost. The `run` method handles both standard text responses and image inputs, computing tile-based token costs for image requests based on the provided `image_width` and `image_height` dimensions.

**Inherits from**: QThread

#### Methods

##### __init__(self, headers, params, url, is_image, image_width, image_height)

Initializes the worker thread instance with the necessary configuration for making an API request. Accepts HTTP `headers`, request `params`, and a target `url`, along with optional image-related parameters `is_image` (defaulting to `False`), `image_width` (defaulting to `512`), and `image_height` (defaulting to `512`). All provided arguments are stored as instance attributes for use during thread execution.

##### run(self)

*No description available.*
Executes an HTTP POST request to the configured URL using a streaming response, processing server-sent event lines incrementally as they arrive. For each received content chunk, the method accumulates the reply text, estimates token usage, calculates the running cost based on fixed input and output cost-per-token rates (with an additional image cost derived from tile-based token estimation when `self.is_image` is set), and emits `progress_updated`, `tokens_used_updated`, and `content_updated` signals accordingly. If the server returns a non-200 status code or an exception occurs during processing, the method prints an error message and exits gracefully.

### GPTWindow

`GPTWindow` is a `QMainWindow` subclass that provides a graphical interface for AI-assisted analysis of archaeological images and documents within the PyArchInit application. It integrates with multiple LLM providers (OpenAI, Anthropic Claude, Ollama, and LM Studio) through an `LLMSelectorWidget`, enabling vision-based extraction of stratigraphic unit (US/USM) information from sketch images and Harris matrix diagrams, as well as text analysis from PDF, CSV, and DOCX documents. Extracted information can be validated by the user and persisted to the application database, with support for associating images to existing or newly created stratigraphic records.

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, selected_images, dbmanager, main_class)

Initializes a `GPTWindow` instance by configuring the main window properties, including title, geometry, and icon, then constructing the full UI layout using a `QGridLayout` containing an AI model selector (`LLMSelectorWidget`), a prompt input area (`QTextEdit`), three action buttons ("Analizza Immagini Selezionate", "Importa Immagine", "Importa Documento"), a progress bar, a token counter label, and a scrollable `QTextBrowser` for displaying AI responses. Stores the provided `selected_images`, `dbmanager`, and `main_class` arguments as instance attributes, and wraps the layout in a central `QWidget`. Finalizes setup by applying the window-stays-on-top flag and invoking `ThemeManager` to apply and register a theme toggle.

##### analyze_selected_images(self)

*No description available.*
Iterates over all currently selected images, extracting metadata (DPI, width, and height) from each file using PIL, and constructs a prompt by appending the file name, file path, and image dimensions to the user-defined prompt text. For each image, the assembled prompt is submitted to the configured LLM via `ask_with_llm`, and the response is processed by `extract_and_display_links` if it contains URL-like content. If no images are selected, the output widget displays the message `"No images selected for analysis."`; otherwise, the widget is cleared before processing begins.

##### extract_and_display_links(self, response)

*No description available.*
Parses the provided `response` string using a regular expression to identify all HTTP and HTTPS URLs. Any discovered URLs are appended to `listWidget_ai` as clickable HTML anchor elements, with external link opening enabled via `setOpenExternalLinks(True)`. If no URLs are found in the response, an informational `QMessageBox` dialog is displayed to the user with the message `"No links found in the response."`

##### set_icon(self, icon_path)

*No description available.*
Sets the window icon for the application using the specified icon file path. It accepts a single parameter, `icon_path`, which is passed to `QIcon` to construct the icon object, which is then applied via `setWindowIcon`. This method provides a straightforward way to assign a custom icon to the window at runtime.

##### start_worker(self, headers, params, url, is_image)

*No description available.*
Initializes a new `Worker` instance with the provided `headers`, `params`, and `url` arguments, then connects the worker's `progress_updated`, `content_updated`, and `tokens_used_updated` signals to their respective update handler methods. Once all signal connections are established, the worker thread is started by calling `self.worker.start()`. The `is_image` parameter is accepted but not visibly used within this method's body.

##### apikey_claude(self)

*No description available.*
Retrieves the Claude API key by first checking for an existing key stored in a plain-text file (`claude_api_key.txt`) located in the `bin` subdirectory of `self.HOME`. If the file does not exist, it prompts the user to enter the key via a `QInputDialog` text input dialog, and if confirmed, writes the provided key to that file for future use. Returns the API key as a string, or an empty string if no key is found or provided.

##### apikey_gpt(self)

*No description available.*
Retrieves the GPT API key by reading it from a file named `gpt_api_key.txt` located in the `bin` subdirectory of `self.HOME`. If the file does not exist, the method prompts the user via a `QInputDialog` to enter a new API key, which is then saved to that file. If the file exists but an exception occurs during the return, the user is offered the option to replace the stored key with a new one via a `QMessageBox` confirmation dialog.

##### ask_with_llm(self, prompt, file_path, config, is_image)

Vision/document Q&A unificato per qualsiasi provider.

Per OpenAI / Ollama / LM Studio usa il formato OpenAI multimodale
(``image_url`` con data-URI base64). Per Anthropic usa il formato
nativo ``source.type=base64``. Streaming aggiorna la UI in tempo reale.

##### ask_gpt4(self, prompt, apikey, file_path, is_image)

*No description available.*
Sends a prompt along with a file to the OpenAI API (model `"gpt-5.5"`) and returns the full streamed response as a string. When `is_image` is `True`, the file at `file_path` is read, Base64-encoded, and submitted as an inline JPEG image alongside the prompt; when `False`, text is extracted from the file via `extract_text_from_file` and appended to the prompt in a document-analysis system context. The response is streamed in chunks up to 4096 completion tokens, with each chunk passed to `update_content` as it arrives; on failure, a warning dialog is displayed and an empty string is returned.

##### ask_claude(self, prompt, apikey, file_path, is_image)

*No description available.*
Sends a prompt along with a file to the Anthropic Claude API (`claude-sonnet-4-6`) and returns the model's streamed response as an accumulated string. When `is_image` is `True`, the file at `file_path` is read, base64-encoded, and submitted as an inline image with a media type derived from the file extension (`.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`); when `False`, text is extracted from the file and appended directly to the prompt. Streamed response chunks are progressively passed to `self.update_content()` as they arrive, and any exception raised during execution triggers a warning dialog and causes the method to return an empty string.

##### manual_input(self, missing_fields)

*No description available.*
Prompts the user to provide values for each field listed in `missing_fields` by displaying a `QInputDialog` text input dialog for each one. Collected values are stripped of leading and trailing whitespace and stored in a dictionary keyed by field name. Returns the populated dictionary if all prompts are completed and confirmed, or `None` if the user cancels or provides an empty value at any point.

##### check_existing_record(self, info)

*No description available.*
Queries the database to determine whether a record matching the given `info` dictionary already exists, using the fields `sito`, `area`, `us`, and `unita_tipo` as search criteria. The query is executed against the table class defined by `self.mainclass.MAPPER_TABLE_CLASS` via `self.DB_MANAGER.query_bool`. Returns the `id_us` of the first matching record if one is found, or `None` if no match exists.

##### is_image_associated(self, file_path, record_id)

Checks whether a specific image file is associated with a given record in the database by querying the `MEDIATOENTITY` table. It extracts the base filename from the provided `file_path` and searches for a matching entry using `id_entity`, `entity_type` (`'US'`), and `media_name` as search criteria. Returns `True` if a matching association exists, or `False` otherwise.

##### scketchgpt(self)

*No description available.*
Clears the AI list widget and opens a file dialog prompting the user to select one or more image files (PNG, JPG, JPEG). For each selected image, it determines whether the image represents a Harris matrix (via `is_harris_matrix`) and, if confirmed by the user, performs a detailed stratigraphic relationship analysis using a localized prompt and the configured LLM, then creates or updates database records accordingly. For non-Harris matrix images, it extracts stratigraphic unit information (site, area, US, unit type) via the LLM, checks for existing records, and either associates the image with an existing record or creates a new one after user confirmation.

##### check_existing_record_matrix(self, info)

*No description available.*
Queries the `us_table` database table to check whether a record already exists matching the provided site (`sito`), area (`area`), and stratigraphic unit (`us`) values supplied in the `info` dictionary. Executes the query using the active database connection and returns the first matching record if found, or `None` if no match exists or an exception occurs. Any exception raised during query execution is caught and printed to standard output.

##### is_harris_matrix(self, prompt)

*No description available.*
Checks whether the provided `prompt` string contains the substring `"harris matrix"` or `"matrix"` (case-insensitive). Returns `True` if either substring is found, otherwise returns `False`.

**Parameters:**
- `prompt` (`str`): The input string to evaluate.

**Returns:** `bool` — `True` if the prompt contains `"harris matrix"` or `"matrix"`; `False` otherwise.

##### go_to_us_record(self, sito, area, us, unita_tipo)

*No description available.*
Navigates to a US (Unità Stratigrafica) record in the database by constructing a search dictionary from the provided `sito`, `area`, `us`, and `unita_tipo` parameters, removing any empty entries via `Utility.remove_empty_items_fr_dict`, and querying the database through `DB_MANAGER.query_bool`. If matching records are found, the method populates `mainclass.DATA_LIST` with the results, sets the current record to the first result, and updates the UI fields, browse status, and record counter accordingly. If no records are found, a warning dialog is displayed and the method returns without making any changes.

##### image_already_associated(self, file_path, record_id)

*No description available.*
Checks whether an image file is already associated with a record in the database by querying the `MediaTable` for an existing entry matching the given `file_path`. The method performs a database lookup via `db_search_check` on the `filepath` field and returns `True` if a matching record is found, or `False` if the result is `None`. Note that the `record_id` parameter is accepted but not used in the current implementation.

##### process_ai_response(self, response_text)

*No description available.*
Processes a raw AI response text by extracting a list of stratigraphic units (US/USM) and their spatial relationships. For each identified US or USM unit, it constructs a structured record containing the site (`sito`), area, unit number, unit type, and associated relations retrieved via `extract_relations_from_text`. Returns a dictionary keyed by unit label (e.g., `"US 1"`) where each value is a dictionary of the extracted fields for that unit.

##### extract_us_list(self, text)

*No description available.*
Parses the provided text string to extract all occurrences of stratigraphic unit identifiers (`US` and `USM`) followed by numeric values, returning their integer values as lists. It also searches the text for `sito` and `area` field values using case-insensitive pattern matching. If either `sito` or `area` cannot be found in the text, the method invokes `self.manual_input` to retrieve the missing fields, then returns a dictionary with keys `"US"`, `"USM"`, `"sito"`, and `"area"`.

##### extract_relations_from_text(self, text, sito, area)

*No description available.*
Parses a text string to identify stratigraphic relationships between Stratigraphic Units (US) using three predefined regex patterns: "Copre / Coperto da" (covers/covered by), "Taglia / Tagliato da" (cuts/cut by), and "Riempie / Riempito da" (fills/filled by). For each match found, the method records the relationship bidirectionally — appending an entry to both the primary and secondary US numbers — along with the associated area number and site name. Returns a `defaultdict(list)` keyed by US number, where each value is a list of relationship entries in the form `[relation_type, us_number, area_number, site_name]`.

##### extract_info_from_response_matrix(self, response)

*No description available.*
Parses a response string to extract site (`sito`) and area (`area`) information by splitting the response into lines and searching for matching keys in a case-insensitive manner. If any expected values are not found, it delegates to `extract_missing_info_matrix` to attempt recovery of the missing data, then calls `check_manual_input` to validate or supplement the collected information. Raises a `ValueError` if the response is empty, and returns the populated `info` dictionary upon completion.

##### extract_info_from_response(self, response)

*No description available.*
Parses a newline-delimited string response to extract four specific fields — `sito`, `area`, `us`, and `unita_tipo` — by searching each line for matching key-value patterns in the format `key: value` (case-insensitive). If any of the four fields remain unpopulated after the initial parsing pass, `extract_missing_info` is called to attempt recovery of the missing values. After extraction, `check_manual_input` is invoked on the resulting dictionary before it is returned; raises `ValueError` if the input response is empty or falsy.

##### extract_missing_info(self, response, info)

Attempts to populate missing fields in the `info` dictionary by extracting values from the provided `response` string. For each of the fields `sito`, `area`, `us`, and `unita_tipo` that are not already set, it calls `extract_info_generic` with the response and a list of relevant keyword variants to locate the corresponding value. The `unita_tipo` field is searched against an uppercased version of the response, while the remaining fields are searched against the original response.

##### extract_missing_info_matrix(self, response, info)

*No description available.*
Attempts to populate missing fields in the `info` dictionary by extracting values from the provided `response` string. Specifically, it checks whether `'sito'` and `'area'` fields are absent or empty, and if so, calls `extract_info_generic` with the corresponding keyword lists (`['sito', 'site']` and `['area']` respectively) to retrieve their values. The method operates on an uppercased copy of `response` for internal use, while passing the original `response` to the extraction calls.

##### check_manual_input(self, info)

*No description available.*
Checks the provided `info` dictionary for missing or empty values by collecting all keys whose value is `None` or an empty string into a `missing_fields` list. If any missing fields are found, displays a `QMessageBox.information` dialog notifying the user of the missing entries with the message "Le seguenti informazioni sono mancanti: {fields}. Procederemo con l'inserimento manuale.", then invokes `self.manual_input(missing_fields)` to collect the absent values. The returned data from manual input is merged back into `info` via `info.update(manual_info)`.

##### extract_info_generic(self, text, keywords)

*No description available.*
Searches the provided `text` for the first occurrence of any keyword in the `keywords` iterable, using a case-insensitive regular expression pattern that matches the keyword followed by an optional colon and any trailing content. If a match is found, returns the captured trailing value as a stripped string. Returns `None` if no keyword produces a match.

##### confirm_information(self, info, file_path)

*No description available.*
Displays a modal confirmation dialog prompting the user to verify the accuracy of the provided information. The dialog presents a formatted summary of the fields `sito`, `area`, `us`, and `unita_tipo` from the `info` dictionary, along with the given `file_path`, using a Yes/No button set. Returns `True` if the user confirms by selecting **Yes**, or `False` if the user selects **No**.

##### confirm_information_matrix(self, info, file_path)

*No description available.*
Displays a modal confirmation dialog box prompting the user to verify the accuracy of a set of matrix-related information fields. The dialog presents the values of `sito`, `area`, `us`, `rapporti`, and `unita_tipo` from the `info` dictionary, along with the provided `file_path`, as formatted detail text within a `QMessageBox`. Returns `True` if the user clicks **Yes**, or `False` if the user clicks **No**.

##### create_new_record_matrix(self, info)

*No description available.*
Inserts a new matrix record into the database using site, area, unit, relation, and unit-type values extracted from the `info` dictionary. It calls `DB_MANAGER.insert_number_of_rapporti_records` to perform the insertion, then retrieves and returns the ID of the newly created record via `DB_MANAGER.max_num_id`. If an error occurs during either operation, a critical `QMessageBox` is displayed and `None` is returned.

##### create_new_record(self, info)

*No description available.*
Inserts a new US (Unità Stratigrafica) record into the database using the `sito`, `area`, `us`, and `unita_tipo` values extracted from the `info` dictionary. It delegates the insertion to `self.DB_MANAGER.insert_number_of_us_records()` and then retrieves the newly created record's identifier via `self.DB_MANAGER.max_num_id('US', 'id_us')`. Returns the new record's ID (`id_us`) on success, or displays a critical error dialog and returns `None` if an exception occurs.

##### db_search_check(self, table_class, field, value)

Searches a database table for records matching a specified field-value pair. It constructs a search dictionary from the given field and value, removes any empty entries using the `Utility.remove_empty_items_fr_dict` method, and then executes a boolean query against the specified table class via `DB_MANAGER.query_bool`. Returns the result of the query.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database with the provided metadata, automatically assigning the next available ID by incrementing the current maximum `id_media` value. The record is created with the supplied `mediatype`, `filename`, `filetype`, and `filepath` parameters, along with fixed default values for the description (`'Insert description'`) and tags (`"['imagine']"`). Returns `1` on successful insertion, or `0` if the operation fails — distinguishing integrity constraint violations (e.g., duplicate entries) from other exceptions, with a warning dialog displayed for errors occurring during record construction.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table by assigning the next available ID and storing the provided metadata fields as instance attributes before delegating to `DB_MANAGER.insert_mediathumb_values`. The resulting data object is then committed to the database session via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if the operation fails — silently suppressing integrity constraint violations (e.g., duplicate thumbnail entries) while displaying a warning dialog for all other exceptions.

##### associate_image_with_record(self, file_path, record_id)

*No description available.*
Associates an image file with a database record by validating the file type, checking for duplicate entries in the `MEDIA` table, and inserting a new media record if the image is not already present. If the insertion succeeds, the method generates thumbnail and resized image variants using `Media_utility` and `Media_utility_resize`, inserts a corresponding thumbnail record, and adds the image as an icon item to `iconListWidget`. Accepted image formats are `jpg`, `jpeg`, `png`, `tiff`, `tif`, and `bmp`; any other file type raises a `ValueError`.

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

*No description available.*
Queries the database for a single US (Stratigraphic Unit) record matching the site (`sito`), area, and US number retrieved from the main class's UI controls. The matching record's `id_us` value is collected and packaged into a list of tuples in the format `[id_us, 'US', 'us_table']`. Returns this list representing the identified US records.

##### update_icon_list_widget(self, file_path, record_id)

*No description available.*
Adds a new item to the `iconListWidget` of the parent `mainclass` by creating a `QListWidgetItem` with an icon loaded from `file_path` and a label formatted as `"Record {record_id}"`. If the operation fails for any reason, a warning dialog is displayed to the user via `QMessageBox` containing the exception message.

**Parameters:**
- `file_path` — Path to the image file used as the item's icon.
- `record_id` — Identifier used to construct the item's display label.

##### ask_sketch(self, prompt, apikey, file_path)

Sends a multimodal prompt along with a file to the OpenAI API, handling image, video, and other file types differently. For image files, the file is base64-encoded and attached directly; for video files, up to five evenly spaced frames are extracted using OpenCV, base64-encoded, and included alongside metadata and an Italian-language analysis instruction. The constructed request targets the `gpt-5.5` model with streaming enabled and a maximum of 4096 completion tokens, then delegates execution to `self.start_worker` with the assembled headers and parameters.

##### extract_text_from_file(self, file_path)

*No description available.*
Extracts text content from a file at the given `file_path` by dispatching to a type-specific extraction method based on the file's extension. Supports `.pdf`, `.csv`, and `.docx` file types, delegating to `extract_text_from_pdf`, `extract_text_from_csv`, or `extract_text_from_docx` respectively. Returns `None` and prints `"Unsupported file type."` if the file extension does not match any of the supported types.

##### extract_text_from_pdf(self, file_path)

*No description available.*
Opens a PDF file at the specified `file_path` using the `fitz` library and iterates through each page, concatenating the extracted text into a single string. Returns the complete text content of the document upon success. If an exception occurs during reading, prints an error message and returns `None`.

##### extract_text_from_csv(self, file_path)

*No description available.*
Opens a CSV file at the specified `file_path` and reads its contents using a CSV reader. Each row is joined into a space-separated string and appended to the result with a newline character. Returns the complete extracted text as a single string.

##### extract_text_from_docx(self, file_path)

Extracts and returns all text content from a `.docx` file at the specified `file_path`. Opens the document using `docx.Document`, iterates over each paragraph in the document, and concatenates each paragraph's text followed by a newline character. Returns the resulting string containing the full text of the document.

##### save_corrected_file(self, original_file_path, original_lines, corrected_text)

*No description available.*
Prompts the user with a save dialog to choose a destination path for the corrected document, preserving the original file's extension as the filter. Based on the detected file type (`.pdf`, `.csv`, or `.docx`), it delegates to the appropriate type-specific save method (`save_corrected_pdf`, `save_corrected_csv`, or `save_corrected_docx`). If the user cancels the dialog or the file type is unsupported, the method either returns early or prints an unsupported file type message.

##### find_closest_match(self, corrected_line, original_lines)

*No description available.*
Searches for the closest matching string to `corrected_line` within the `original_lines` sequence using `difflib.SequenceMatcher` to compute similarity ratios. Iterates over all entries in `original_lines`, tracking the candidate with the highest similarity ratio. Returns the best-matching line if its similarity ratio exceeds `0.6`; otherwise returns `None`.

##### find_closest_match_pdf(self, corrected_line, original_lines)

*No description available.*
Searches for the closest matching line in `original_lines` that contains `corrected_line` as a case-insensitive substring. Iterates through each entry in `original_lines` and returns the first `original_line` whose lowercased form contains the lowercased `corrected_line`. Returns `None` if no matching line is found.

##### save_new_pdf_with_corrections(self, original_file_path, save_path, corrected_lines)

*No description available.*
Opens an existing PDF file at `original_file_path`, iterates over each page to locate the closest matching original line for each entry in `corrected_lines`, and overlays the corrected text at the position of the first found instance using `fitz`. The modified document is then saved to `save_path`. On success, a `QMessageBox` information dialog is displayed; on failure, the exception is printed and a `QMessageBox` critical error dialog is shown.

##### save_corrected_csv(self, save_path, corrected_text)

*No description available.*
Writes corrected text content to a CSV file at the specified `save_path` by splitting the input string on newlines and writing each resulting line as a whitespace-delimited row. On success, displays an informational message box confirming the file was saved. If an exception occurs during the write operation, the error is printed to the console and a critical message box is displayed to the user.

##### save_corrected_docx(self, original_file_path, save_path, corrected_text)

Saves a corrected version of an existing DOCX file by loading the original document from `original_file_path`, replacing each paragraph's text with the corresponding line from `corrected_text` (split by newline characters), and writing the result to `save_path`. The replacement is applied only up to the number of paragraphs present in the original document or the number of lines in `corrected_text`, whichever is smaller. On success, an informational message box is displayed; on failure, the exception is printed and a critical error message box is shown.

##### ask_doc(self, prompt, apikey, file_path)

*No description available.*
Sends a document-based query to the OpenAI Chat Completions API using the specified API key, user prompt, and file path. It first extracts text from the file via `extract_text_from_file`; if extraction fails and returns `None`, the method returns `None` immediately. Otherwise, it constructs a streaming request targeting the `gpt-5.5` model with a maximum of 4096 completion tokens and delegates execution to `start_worker`, passing the assembled headers, parameters, and the Chat Completions endpoint URL.

##### ask_doc_with_claude(self, prompt, apikey, file_path)

*No description available.*
Sends a document-based query to the Anthropic Claude API by extracting text from a local file and combining it with the provided prompt. The method sets the Anthropic API key, constructs a user message containing the prompt and extracted file text, and configures a streaming request targeting the `claude-sonnet-4-6` model with a maximum of 4096 tokens and a temperature of 0.5. If text extraction from the file fails, the method returns `None`; otherwise, it initiates an asynchronous worker via `start_worker` against the `https://api.anthropic.com/v1/message` endpoint.

##### update_progress(self, progress)

*No description available.*
Sets the current value of the progress indicator to the specified `progress` value. This method directly calls `setValue` on the internal `progress` widget, updating its displayed state to reflect the provided input.

##### update_content(self, content)

*No description available.*
Appends new content to the existing text displayed in the `listWidget_ai` plain text widget. It first retrieves the current text via `toPlainText()`, then sets the widget's text to the concatenation of the existing content and the new `content` argument using `setPlainText()`.

##### update_tokens_used(self, tokens_used, total_cost)

*No description available.*
Updates the `token_counter` widget's displayed text to reflect the current token usage and associated cost. The method formats the output as `"Tokens used: {tokens_used} - Total cost: ${total_cost:.4f}"`, where `total_cost` is rendered to four decimal places. This method accepts `tokens_used` and `total_cost` as parameters and directly sets the label text without returning a value.

##### docchgpt(self)

*No description available.*
Clears the AI output list widget and opens a file dialog prompting the user to select a document file (`.pdf`, `.csv`, or `.docx`). If a file is selected, it retrieves the current prompt text and LLM configuration, then invokes `ask_with_llm` with the selected file path and `is_image=False`. If the user cancels the dialog, a cancellation message is displayed in the output widget.

## Functions

### get_image_metadata(file_path)

*No description available.*
Opens an image file at the specified `file_path` and extracts its metadata. Retrieves the image's DPI from the file's info dictionary, defaulting to `(72, 72)` if no DPI value is present, along with the image's pixel dimensions (width and height). Returns a dictionary containing three keys: `'dpi'`, `'width'`, and `'height'`.

**Parameters:**
- `file_path`

### encode_file(file_path)

*No description available.*
Opens the file at the specified path in binary mode, reads its contents, and returns a Base64-encoded UTF-8 string representation of those contents. If the file does not exist at the given path, the function prints a diagnostic message and returns `None`.

**Parameters:**
- `file_path` *(str)*: The path to the file to be encoded.

**Returns:** A Base64-encoded UTF-8 string of the file's binary contents, or `None` if the file is not found.

**Parameters:**
- `file_path`

### get_file_type(file_path)

*No description available.*
Determines the general type of a file by inferring its MIME type from the given file path using `mimetypes.guess_type`. If a MIME type is successfully resolved, the function returns the top-level type category (e.g., `"image"`, `"video"`, `"text"`) by splitting the MIME string on `'/'` and returning the first segment. Returns `None` if the MIME type cannot be determined.

**Parameters:**
- `file_path`

### extract_video_frames(file_path, num_frames)

*No description available.*
Opens a video file at the specified `file_path` using OpenCV and extracts a fixed number of evenly distributed frames, defaulting to 5. Each extracted frame is JPEG-encoded and converted to a Base64-encoded UTF-8 string. Returns a tuple containing a summary string with the video's duration, FPS, and total frame count, along with a list of Base64-encoded frame strings; if the video cannot be opened, returns an error message string (`"Errore nell'apertura del video"`) and an empty list.

**Parameters:**
- `file_path`
- `num_frames`

