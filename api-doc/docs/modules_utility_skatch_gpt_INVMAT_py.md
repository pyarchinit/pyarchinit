# modules/utility/skatch_gpt_INVMAT.py

## Overview

This file contains 53 documented elements.

## Classes

### Worker

*No description available.*
A `QThread` subclass that performs asynchronous HTTP streaming requests to the OpenAI Chat Completions API. It emits three signals during execution: `progress_updated` (int) to report streaming progress, `content_updated` (str) to deliver incremental response content chunks, and `tokens_used_updated` (int, float) to report token count and cumulative cost. When instantiated with `is_image=True`, it calculates an additional image token cost based on the provided `image_width` and `image_height` dimensions using a tile-based formula.

**Inherits from**: QThread

#### Methods

##### __init__(self, headers, params, is_image, image_width, image_height)

*No description available.*
Initializes the worker thread instance by calling the parent class constructor via `super().__init__()` and storing the provided arguments as instance attributes. Accepts `headers` and `params` for use in the subsequent API request, along with an optional `is_image` boolean flag (default `False`) and optional `image_width` and `image_height` dimensions (both defaulting to `512`). The class also defines three PyQt signals — `progress_updated`, `content_updated`, and `tokens_used_updated` — used to communicate progress, content, and token usage data respectively.

##### run(self)

*No description available.*
Executes an HTTP POST request to the OpenAI Chat Completions API using a streaming response, processing each incoming line to extract and accumulate reply content. As content chunks are received, the method emits signals for progress updates (`progress_updated`), token usage and estimated cost (`tokens_used_updated`), and individual content chunks (`content_updated`). If the request involves an image, the token cost is calculated based on the image dimensions using a tile-based formula; HTTP errors and exceptions are caught and printed without re-raising.

### GPTWindow

`GPTWindow` is a `QMainWindow` subclass that provides a graphical interface for AI-assisted analysis of images and documents within the PyArchInit application. It integrates with multiple LLM providers (OpenAI, Anthropic Claude, Ollama, and LM Studio) via an `LLMSelectorWidget`, enabling users to submit vision or document prompts and receive streamed responses displayed in a `QTextBrowser`. The window also supports extracting structured archaeological inventory data (site name and inventory number) from AI responses, creating or updating database records, and associating processed image files with those records through the application's database manager.

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, selected_images, dbmanager, main_class)

Initializes a `GPTWindow` instance by configuring the main window properties, including title, geometry, and icon, and setting up the complete UI layout using a `QGridLayout`. The constructor accepts optional parameters for pre-selected images (`selected_images`), a database manager (`dbmanager`), and a reference to the main application class (`main_class`), storing each as instance attributes. The UI is composed of an AI model selector (`LLMSelectorWidget`), a prompt input area (`QTextEdit`), action buttons for analyzing images and importing images or documents, a progress bar, a token usage label, and a scrollable text browser for displaying AI responses, with theming applied via `ThemeManager` upon completion.

##### analyze_selected_images(self)

*No description available.*
Iterates over all currently selected images, extracting metadata (DPI and pixel dimensions) from each file using PIL, and constructs a prompt by appending the file name, file path, and metadata to the user-defined prompt text before submitting it to the configured LLM via `ask_with_llm`. The `listWidget_ai` widget is cleared at the start of each invocation, and if no images are selected, a plain-text message is displayed in its place. For each LLM response received, the method delegates to `extract_and_display_links` to identify and render any URLs contained in the response.

##### extract_and_display_links(self, response)

*No description available.*
Parses the provided `response` string using a regular expression to identify all HTTP and HTTPS URLs. Any URLs found are appended to `listWidget_ai` as clickable HTML anchor elements, with external link handling enabled so that links open in the system's default browser. If no URLs are detected in the response, an informational `QMessageBox` dialog is displayed with the message `"No links found in the response."`.

##### set_icon(self, icon_path)

*No description available.*
Sets the window icon for the current widget using the specified icon path. It constructs a `QIcon` object from the provided `icon_path` and applies it to the window via `setWindowIcon`.

**Parameters:**
- `icon_path` — The file path to the icon image to be used as the window icon.

##### start_worker(self, headers, params, is_image)

*No description available.*
Initializes and starts a `Worker` instance with the provided `headers` and `params` arguments. Connects the worker's `progress_updated`, `content_updated`, and `tokens_used_updated` signals to the corresponding `update_progress`, `update_content`, and `update_tokens_used` handler methods, respectively. The `is_image` parameter is accepted but not referenced within the method body; see implementation for details.

##### apikey_claude(self)

*No description available.*
Retrieves the Claude API key by first checking for an existing key stored in a plain-text file (`claude_api_key.txt`) located in the `bin` subdirectory of `self.HOME`. If the file does not exist, it prompts the user to enter the key via a `QInputDialog` dialog, and if confirmed, writes the entered key to that file for future use. Returns the API key as a string, or an empty string if no key was provided.

##### apikey_gpt(self)

*No description available.*
Retrieves the GPT API key from a file named `gpt_api_key.txt` located in the `bin` subdirectory of `self.HOME`. If the file exists, its contents are read and returned as a stripped string; if the file does not exist, a `QInputDialog` prompt is presented to the user to enter a new key, which is then saved to the file before being returned. In the event of an exception during key retrieval, the user is offered the option to provide a replacement key via dialog, which overwrites the existing file.

##### ask_with_llm(self, prompt, file_path, config, is_image)

Vision/document Q&A unificato per qualsiasi provider configurato.

##### ask_gpt4(self, prompt, apikey, file_path, is_image)

*No description available.*
Sends a prompt along with either an image or a text document to the OpenAI API (model `"gpt-5.5"`) and returns the full response as a string. When `is_image` is `True`, the file at `file_path` is read, Base64-encoded, and submitted as an inline JPEG image alongside the prompt; when `False`, text is extracted from the file via `extract_text_from_file` and appended to the prompt in a document-analysis system context. The response is received as a stream, with each content chunk passed to `update_content` as it arrives; on any exception, a warning dialog is displayed and an empty string is returned.

##### ask_claude(self, prompt, apikey, file_path, is_image)

*No description available.*
Sends a prompt along with a file to the Anthropic Claude API (`claude-sonnet-4-6`) and returns the model's full text response. When `is_image` is `True`, the file is read, base64-encoded, and submitted as an inline image with a media type derived from the file extension (`.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`); when `False`, text is extracted from the file via `self.extract_text_from_file` and appended directly to the prompt. The response is streamed, with each text chunk passed to `self.update_content` for UI updates and accumulated into a single string that is returned; on failure, a warning dialog is displayed and an empty string is returned.

##### manual_input(self, missing_fields)

*No description available.*
Prompts the user to provide values for each field listed in `missing_fields` by displaying a sequential series of `QInputDialog` text input dialogs. For each field, if the user confirms the dialog and supplies a non-empty value, the stripped input is stored in a dictionary keyed by the field name; if the user cancels or provides an empty value at any point, the method immediately returns `None`. Returns the populated dictionary of field-value pairs upon successful completion of all prompts.

##### check_existing_record(self, info)

*No description available.*
Queries the database to determine whether a record already exists that matches the `sito` and `numero_inventario` values provided in the `info` dictionary. Uses `DB_MANAGER.query_bool` against `mainclass.MAPPER_TABLE_CLASS` to perform the lookup. Returns the `id_invmat` of the first matching record if one is found, or `None` if no match exists.

##### is_image_associated(self, file_path, record_id)

*No description available.*
Checks whether a given image file is associated with a specific record in the `MEDIATOENTITY` table. It extracts the filename from the provided file path and queries the database for a matching entry where `id_entity` equals `record_id`, `entity_type` is `'REPERTO'`, and `media_name` matches the extracted filename. Returns `True` if a matching association exists, or `False` otherwise.

##### scketchgpt(self)

Opens a file dialog allowing the user to select one or more image files, then submits each image along with a prompt to a configured LLM via `ask_with_llm`. The extracted information from each LLM response is used to check for an existing database record; if found, the image is associated with it (if not already linked), and if not found, the user is prompted to confirm the extracted data before a new record is created and the image associated. Upon successful record creation, the UI is updated and the application navigates to the corresponding record entry.

##### go_to_us_record(self, sito, numero_inventario)

*No description available.*
Navigates to a US (Unità Stratigrafica) record in the main interface by querying the database using the provided `sito` (site) and `numero_inventario` (inventory number) as search criteria. Empty values are stripped from the search dictionary before the query is executed; if no matching records are found, a warning dialog is displayed and the method returns without further action. On a successful match, the retrieved result set is loaded into the main class's data list, the UI fields are populated with the first record, and the browse status and record counter are updated accordingly.

##### image_already_associated(self, file_path, record_id)

Checks whether a given image file is already associated with a record by querying the `MediaTable` for an existing entry matching the specified `file_path`. Returns `True` if a matching record is found, or `False` if the result is `None`.

##### extract_info_from_response(self, response)

*No description available.*
Parses a text response string to extract structured inventory information, populating a dictionary with the keys `'sito'` and `'numero_inventario'`. Each line of the response is scanned for a matching key pattern (case-insensitive), and the corresponding value is extracted from the text following the colon delimiter. If any fields remain unpopulated after parsing, `extract_missing_info` is called to attempt recovery of the missing values, followed by a call to `check_manual_input` before the resulting dictionary is returned. Raises `ValueError` if the provided response is empty or falsy.

##### extract_missing_info(self, response, info)

*No description available.*
Attempts to populate missing fields in the `info` dictionary by extracting data from `response` using predefined keyword lists. Specifically, if `info['sito']` is empty or falsy, it is populated via `extract_info_generic` using the keywords `['sito', 'site']`; if `info['numero_inventario']` is empty or falsy, it is populated using the keywords `['reperto', 'inventario', 'numero', 'number']`. This method operates in-place on the `info` dictionary and does not return a value.

##### check_manual_input(self, info)

*No description available.*
Checks the provided `info` dictionary for any fields whose value is `None` or an empty string. If missing fields are found, displays an informational `QMessageBox` dialog titled `"Informazioni Mancanti"` listing the affected fields, then invokes `self.manual_input` with those fields to collect user-provided values. The returned values are merged back into `info` via `dict.update`.

##### extract_info_generic(self, text, keywords)

*No description available.*
Searches the provided text for the first occurrence of any keyword in the `keywords` list using a case-insensitive regular expression pattern. The pattern matches the keyword followed by an optional colon and captures the remaining content on the same line. Returns the captured text stripped of leading and trailing whitespace, or `None` if no keyword produces a match.

##### confirm_information(self, info, file_path)

*No description available.*
Displays a modal confirmation dialog box prompting the user to verify extracted record information before proceeding. The dialog presents the `sito` and `numero_inventario` fields from the `info` dictionary alongside the provided `file_path`, formatted as detail text within a `QMessageBox`. Returns `True` if the user clicks **Yes**, or `False` if the user clicks **No**.

##### create_new_record(self, info)

*No description available.*
Inserts a new inventory record into the database using the `sito` and `numero_inventario` values extracted from the `info` dictionary, by delegating to `DB_MANAGER.insert_number_of_reperti_records`. After insertion, retrieves and returns the ID of the newly created record via `DB_MANAGER.max_num_id` on the `INVENTARIO_MATERIALI` table, using the `id_invmat` column. If an exception occurs during either operation, displays a critical error dialog via `QMessageBox` and returns `None`.

##### db_search_check(self, table_class, field, value)

Searches a database table for records matching a specified field-value pair. It constructs a search dictionary from the given field and value, removes any empty entries using the `Utility.remove_empty_items_fr_dict` method, and then executes a boolean query against the specified table class via `DB_MANAGER.query_bool`. Returns the result of the query.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database with the provided metadata, automatically assigning the next available ID by incrementing the current maximum `id_media` value. The record is created with the supplied `mediatype`, `filename`, `filetype`, and `filepath` arguments, along with fixed default values for the description (`'Insert description'`) and tags (`"['imagine']"`). Returns `1` on successful insertion, or `0` if the operation fails — distinguishing integrity constraint violations (e.g., duplicate entries) from other exceptions, with a warning dialog displayed for errors occurring during record construction.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table by assigning the next available ID and storing the provided metadata fields as instance attributes before delegating to `DB_MANAGER.insert_mediathumb_values`. The resulting data object is then committed to the database session via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if an error occurs — silently suppressing integrity constraint violations (e.g., duplicate thumbnails) while displaying a warning dialog for all other exceptions.

##### associate_image_with_record(self, file_path, record_id)

*No description available.*
Associates an image file with a database record by validating the file type, checking for duplicate entries in the `MEDIA` table, and inserting a new media record if the image is not already present. If the insertion succeeds, the method generates thumbnail and resized versions of the image using `Media_utility` and `Media_utility_resize`, inserts a corresponding thumbnail record, and adds the image as an icon item to `iconListWidget`. Accepted image formats are `jpg`, `jpeg`, `png`, `tiff`, `tif`, and `bmp`; unsupported file types raise a `ValueError`, and all errors are reported via `QMessageBox` dialogs.

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
Queries the database for an `INVENTARIO_MATERIALI` record matching the current site (`sito`) and inventory number (`numero_inventario`) retrieved from the parent class's UI controls. Builds and returns a list of tuples, each containing the record's `id_invmat`, the string `'REPERTO'`, and the string `'inventario_materiali_table'`.

##### update_icon_list_widget(self, file_path, record_id)

*No description available.*
Adds a new icon item to the `iconListWidget` of the parent `mainclass` instance, constructing a `QListWidgetItem` from the provided file path as an icon and labeling it `"Record {record_id}"`. If the operation fails for any reason, a warning dialog is displayed to the user via `QMessageBox` containing the exception message.

**Parameters:**
- `file_path` — Path to the image file used as the item's icon.
- `record_id` — Identifier used to label the list widget item.

##### ask_sketch(self, prompt, apikey, file_path)

*No description available.*
Submits a prompt along with a file to the OpenAI API, handling three distinct file types: images (encoded as base64 and attached directly), videos (from which a set of frames are extracted and encoded as base64 images), and all other file types (described by MIME type and filename only). The method constructs a streaming API request targeting the `gpt-5.5` model with a maximum of 4096 completion tokens, using a system prompt configured for image and video analysis. Processing is delegated to `start_worker`, which receives the constructed headers and parameters along with a flag indicating whether the file is an image.

##### extract_text_from_file(self, file_path)

*No description available.*
Extracts text content from a file at the given `file_path` by dispatching to a type-specific extraction method based on the file's extension. Supports `.pdf`, `.csv`, and `.docx` file types, delegating to `extract_text_from_pdf`, `extract_text_from_csv`, or `extract_text_from_docx` respectively. Returns `None` and prints `"Unsupported file type."` if the file extension does not match any of the supported types.

##### extract_text_from_pdf(self, file_path)

*No description available.*
Opens a PDF file at the specified `file_path` using the `fitz` library and iterates through each page to extract and concatenate its text content. Returns the full extracted text as a single string upon success. If an exception occurs during file reading or processing, prints an error message and returns `None`.

##### extract_text_from_csv(self, file_path)

*No description available.*
Opens a CSV file at the specified `file_path` and reads its contents using a `csv.reader`. Each row is joined into a space-separated string and appended to the accumulated text with a newline character. Returns the complete text content of the CSV file as a single string.

##### extract_text_from_docx(self, file_path)

Extracts and returns all text content from a `.docx` file at the specified `file_path`. Opens the document using `docx.Document`, iterates over each paragraph in the document, and concatenates each paragraph's text followed by a newline character. Returns the resulting string containing the full text of the document.

##### save_corrected_file(self, original_file_path, original_lines, corrected_text)

*No description available.*
Prompts the user with a save dialog to choose a destination path for the corrected document, preserving the original file's extension as the expected format filter. Based on the detected file type (`.pdf`, `.csv`, or `.docx`), it delegates the actual writing operation to the corresponding type-specific save method. If the user cancels the dialog or the file type is not supported, the method either returns early or prints an unsupported file type message.

##### find_closest_match(self, corrected_line, original_lines)

*No description available.*
Searches a list of original lines to find the one most similar to a given corrected line, using `difflib.SequenceMatcher` to compute similarity ratios. Iterates over all entries in `original_lines`, tracking the candidate with the highest similarity ratio against `corrected_line`. Returns the best-matching line if its similarity ratio exceeds `0.6`; otherwise returns `None`.

##### save_corrected_pdf(self, original_file_path, save_path, corrected_lines, original_lines)

*No description available.*
Opens an existing PDF file specified by `original_file_path`, iterates over each page, and attempts to locate the closest matching original line for each corrected line using `find_closest_match`. For every match found, it inserts the corrected text at a fixed left margin in red at font size 12, incrementing the vertical position by the font size plus padding, up to a maximum of 100 insertions per page. The modified document is saved to `save_path`, with a success dialog displayed on completion or a critical error dialog shown if an exception occurs.

##### save_corrected_csv(self, save_path, corrected_text)

Writes corrected text content to a CSV file at the specified `save_path` by splitting the `corrected_text` string on newlines and writing each line as a whitespace-delimited row. On success, displays an informational message box confirming the file was saved. If an exception occurs during the write operation, the error is printed to the console and a critical message box is displayed to the user.

##### save_corrected_docx(self, original_file_path, save_path, corrected_text)

*No description available.*
Opens an existing DOCX file from `original_file_path` and replaces its paragraphs sequentially with the newline-delimited segments of `corrected_text`, then saves the modified document to `save_path`. Replacement is performed index-by-index up to the lesser of the document's paragraph count and the number of corrected segments. On success, displays an informational message box; on failure, prints the exception and displays a critical error message box.

##### ask_doc(self, prompt, apikey, file_path)

*No description available.*
Sends a document-based query to the OpenAI API by first setting the API key, then extracting text from the specified file using `extract_text_from_file`. If text extraction succeeds, it constructs an API request payload targeting the `"gpt-5.5"` model with streaming enabled, combining the provided `prompt` with the extracted file text as the user message. The request is then dispatched asynchronously by calling `start_worker` with the assembled headers and parameters in non-image mode.

##### update_progress(self, progress)

*No description available.*
Updates the progress bar widget with the specified progress value by calling `setValue` on `self.progress`. This method accepts a single parameter, `progress`, which is passed directly to the widget's `setValue` method. It is typically invoked as a callback to reflect the current state of an ongoing operation.

##### update_content(self, content)

*No description available.*
Appends new content to the existing text displayed in the `listWidget_ai` plain text widget. It retrieves the current text, concatenates the provided `content` string to it, and sets the resulting combined string as the widget's updated text.

##### update_tokens_used(self, tokens_used, total_cost)

*No description available.*
Updates the `token_counter` label to display the current token usage and cumulative cost of API interactions. The method formats the output as a string in the form `"Tokens used: {tokens_used} - Total cost: ${total_cost:.4f}"`, where `total_cost` is rendered to four decimal places. This method accepts `tokens_used` and `total_cost` as parameters and sets the resulting formatted string as the text of the `token_counter` widget.

##### docchgpt(self)

*No description available.*
Clears the AI output list widget and opens a file dialog prompting the user to select a document file (`.pdf`, `.csv`, or `.docx`). If a file is selected, it retrieves the current prompt text and LLM configuration, then invokes `ask_with_llm` with the selected file path and `is_image=False`. If the user cancels the dialog, a cancellation message is displayed in the output widget.

## Functions

### get_image_metadata(file_path)

*No description available.*
Opens the image file at the specified `file_path` and extracts its metadata. Returns a dictionary containing the image's DPI (defaulting to `(72, 72)` if not present in the file's info), pixel width, and pixel height. The returned dictionary contains the keys `'dpi'`, `'width'`, and `'height'`.

**Parameters:**
- `file_path`

### encode_file(file_path)

*No description available.*
Opens the file at the specified `file_path` in binary mode, reads its contents, and returns a Base64-encoded UTF-8 string representation of those contents. If the file does not exist at the given path, a message is printed to standard output and `None` is returned.

**Parameters:**
- `file_path`

### get_file_type(file_path)

*No description available.*
Determines the general type of a file by guessing its MIME type based on the provided file path. Uses `mimetypes.guess_type` to retrieve the MIME type, then extracts and returns the top-level type category (e.g., `"image"`, `"video"`, `"text"`) by splitting on the `'/'` character. Returns `None` if the MIME type cannot be determined.

**Parameters:**
- `file_path`

### extract_video_frames(file_path, num_frames)

*No description available.*
Opens a video file at the specified `file_path` using OpenCV and extracts a fixed number of evenly distributed frames, defaulting to 5. Each extracted frame is JPEG-encoded and converted to a Base64-encoded UTF-8 string. Returns a tuple containing a summary string with the video's duration, FPS, and total frame count, along with a list of Base64-encoded frame strings; if the video cannot be opened, returns an error message string (`"Errore nell'apertura del video"`) and an empty list.

**Parameters:**
- `file_path`
- `num_frames`

