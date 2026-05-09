# tabs/pyarchinit_Pottery_mainapp.py

## Overview

This file contains 214 documented elements.

## Classes

### pyarchinit_Pottery

`pyarchinit_Pottery` is a QGIS `QDialog` subclass that implements the complete data entry, browsing, search, and management interface for pottery records stored in `pottery_table` within the PyArchInit archaeological information system. It provides full CRUD operations for pottery finds, including fields for site, area, stratigraphic unit, fabric, form, ware, decoration, and measurements, with multilingual support for Italian, English, and German. The class also integrates media management (images, video, and 3D models), statistical analysis with chart generation, PDF export, and an optional visual similarity search engine based on CLIP/DINOv2/OpenAI embeddings.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes an instance of the class by setting up the user interface, applying the active theme, and configuring widget states including hiding dock widgets and enabling drag-and-drop on the icon list. Establishes a database connection via `on_pushButton_connect_pressed`, initializes an `OrderedDict`-based image cache with a limit of 100 entries, and sets `currentLayerId` and `video_player` to `None`. Completes initialization by populating fields, configuring site-related UI state, connecting toolbar button signals, and invoking `init_remote_loader` to prepare the remote image loader with credentials from QGIS settings.

##### get_images_for_entities(self, entity_ids, log_signal)

*No description available.*
Retrieves thumbnail images from the `MEDIATOENTITY` and `MEDIA_THUMB` database tables for each entity ID provided in `entity_ids`, filtering records by `entity_type = 'CERAMICA'`. For each matching media record, it constructs a full thumbnail URL by prepending the configured `thumb_resize` path prefix and collects the result as a dictionary containing the entity `id`, the resolved `url`, and the `caption` (media name). Returns a list of such image dictionaries, or an empty list if `entity_ids` is empty or an exception occurs during processing.

##### setnone(self)

*No description available.*
Clears and resets the text content of five line edit fields: `lineEdit_diametro_max`, `lineEdit_diametro_rim`, `lineEdit_diametro_bottom`, `lineEdit_diametro_preserved`, and `lineEdit_diametro_height`. For each field, the method checks whether its text value matches `'None'`, `None`, `'NULL'`, or `'Null'`, then calls `clear()`, `setText('')`, and `update()` on the widget if the condition is met. Note: several of the conditional checks use the `.text` attribute reference rather than the `.text()` method call, which may affect the intended comparison behavior.

##### generate_list_foto(self)

*No description available.*
Iterates over all records in `self.DATA_LIST` and builds a list of photo-related data entries for ceramics entities. For each record, it retrieves the configured thumbnail path via `Connection`, queries associated media records from the `MEDIAVIEW` table using the record's `id_rep` and entity type `'CERAMICA'`, and appends a list of eleven fields — including site, area, US, sector, year, ID number, notes, media ID, thumbnail path, photo value, and drawing value — to the result. If the thumbnail path is not configured, a localized informational message is displayed to the user (in Italian, German, or English based on `self.L`) and no media entries are appended for that record; the method returns the accumulated `data_list_foto`.

##### on_pushButton_print_pressed(self)

Handles the press event of the print push button, triggering PDF export of pottery photo index data based on the state of two checkboxes. If `checkBox_e_foto_t` is checked, it builds a two-column photo index PDF via `build_index_Foto_2` using the generated photo list; if `checkBox_e_foto` is checked, it builds a standard photo index PDF via `build_index_Foto`. In both cases, a success message is displayed upon completion, or a warning dialog is shown if the photo list is empty or an exception occurs.

##### setPathpdf(self)

Opens a file dialog prompting the user to select a PDF file, restricting the browser to the configured `PDFFOLDER` directory and filtering for `.pdf` files. If a valid file path is selected, it updates the `lineEdit_pdf_path` widget with the chosen path and persists the value using `QgsSettings`.

##### openpdfDir(self)

*No description available.*
Opens the `pyarchinit_PDF_folder` directory located under the user's home directory using the appropriate system command for the current operating system. On Windows, it uses `os.startfile`; on macOS (`Darwin`), it invokes `open` via `subprocess.Popen`; on all other systems, it uses `xdg-open`. The target path is constructed by joining `self.HOME`, the OS path separator, and the folder name `"pyarchinit_PDF_folder"`.

##### msg_sito(self)

*No description available.*
Checks the currently configured archaeological site by opening a `Connection` and retrieving the active site setting via `sito_set()`. If the combo box selection matches the configured site, it displays an informational message confirming the connection; if no site has been configured, it prompts the user to set one or cancel to view all records. All dialog messages are localised based on `self.L`, supporting Italian (`'it'`), German (`'de'`), and a default English fallback; if the user confirms the prompt, `pyArchInitDialog_Config` is opened to configure a site.

##### set_sito(self)

*No description available.*
Retrieves the configured site (`sito`) setting via a `Connection` object and, if a site value is present, queries the database for all matching records using `DB_MANAGER.query_bool`. If matching records are found, the method populates `DATA_LIST`, initialises the record counter, fills the UI fields, sets the browse status to `"b"`, and disables the `comboBox_sito` widget; if no records are found, a localised informational message is displayed in Italian, German, or English based on the current language setting (`self.L`). Any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### on_pushButtonQuant_pressed(self)

*No description available.*
Opens a `QuantPanelMain` dialog populated with `self.QUANT_ITEMS`, then processes the user's selections to perform a quantitative analysis. If the selected quantification type (`TYPE_QUANT`) is `'QTY'`, it iterates over `self.DATA_LIST`, builds a dataset of tuples using `parameter_quant_creator` and each record's `qty` value, aggregates the results via `self.UTILITY.sum_list_of_tuples_for_value`, and writes the summarised data to a CSV file at `self.QUANT_PATH`. If the resulting dataset is non-empty, it calls `self.plot_chart` to render a frequency analysis chart; otherwise, it displays a warning message box indicating no data is present.

##### parameter_quant_creator(self, par_list, n_rec)

*No description available.*
Builds and returns a formatted string of parameter-value pairs for a specified record. It iterates over the provided parameter list (`par_list`), translates each parameter name using `CONVERSION_DICT`, and retrieves the corresponding attribute value from `DATA_LIST` at index `n_rec` via `getattr`. Each parameter-value pair is appended to the result string in the format ` -<first 4 chars of parameter name>: <value>`.

##### plot_chart(self, d, t, yl)

*No description available.*
Renders a vertical bar chart on the embedded canvas widget using the provided data, title, and y-axis label. The method accepts a list of key-value pairs (`d`), converts them into a dictionary, and plots each entry as a bar with its height representing the numeric value. Each bar is annotated with a rotated text label combining the category name and its integer value, after which the canvas is redrawn.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of all primary UI buttons by passing `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. This allows all listed buttons to be enabled or disabled simultaneously with a single call.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously based on the value of `n`. The affected buttons are: `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. Each button's `setEnabled` method is called directly with `n` as the argument.

##### on_pushButton_connect_pressed(self)

Handles the connect button press event by establishing a database connection using a `Connection` object and initializing the database manager via `get_db_manager`. Upon a successful connection, it initializes a `ConcurrencyManager` with the current username (resolved from `QgsSettings`, the connection string, or the OS user as a fallback), a `RecordLockIndicator`, and loads records from the database via `charge_records`. If records exist, the form is set to browse mode and fields are populated; if the database is empty, a localized welcome message is displayed and a new record is initiated; if the connection fails, a localized warning message is pushed to the QGIS message bar.

##### on_toolButtonPreview_toggled(self)

*No description available.*
Handles the toggled state of the preview tool button, displaying a localized warning message (Italian, German, or English depending on `self.L`) when the button is checked to notify the user that SU/US preview mode has been activated. When checked, it switches the active tab to index 10 and calls `self.loadMapPreview()` to load the map preview; when unchecked, it calls `self.loadMapPreview(1)` and, for German and English locales, resets the active tab to index 0.

##### customize_GUI(self)

Configures and initializes the graphical user interface components for the dialog. It sets up the `iconListWidget` with drag-and-drop support, a fixed icon size of 430×570 pixels, uniform item sizes, and extended selection mode, and connects the item double-click signal to `openWide_image`. It then delegates further UI initialization to several setup methods covering media button visibility, the statistics tab, visual similarity search, embedding index auto-updating, a filter button, and an auto-populate button.

##### setup_auto_populate_button(self)

Setup the button to auto-populate photo and drawing fields from media associations

##### setup_filter_button(self)

Setup the filter button for ID Number selection

##### on_pushButton_filter_pottery_pressed(self)

Open the filter dialog for ID Number and Year selection

##### dropEvent(self, event)

*No description available.*
Handles drop events by extracting file URLs from the event's MIME data and validating each dropped file against a list of accepted formats, which includes common image types (`jpg`, `jpeg`, `png`, `tiff`, `tif`, `bmp`), video types (`mp4`, `avi`, `mov`, `mkv`, `flv`), and 3D model types (`obj`, `stl`, `ply`, `fbx`, `3ds`). If a dropped file matches an accepted format, `load_and_process_image` is called with the file path; otherwise, a warning dialog is displayed indicating the unsupported file type. Any exception raised during file processing is caught and reported via a warning `QMessageBox`, after which the base class `dropEvent` is invoked.

##### dragEnterEvent(self, event)

*No description available.*
Handles the drag-enter event by inspecting the MIME data of the incoming drag action. If the event's MIME data contains URLs, the proposed action is accepted; otherwise, the event is ignored. This method controls whether a drag operation is permitted to proceed over the widget based solely on the presence of URL data.

##### dragMoveEvent(self, event)

*No description available.*
Handles the drag move event that is triggered as a dragged object is moved over the widget. Unconditionally accepts the proposed drop action by calling `event.acceptProposedAction()`, allowing the drag operation to continue without restriction. This method overrides the default drag move behavior to permit all incoming drag movements.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database by assigning the next available ID and populating it with the provided media type, filename, file type, and file path, along with a default description of `'Insert description'` and a default tag of `"['imagine']"`. The method delegates record construction to `DB_MANAGER.insert_media_values()` and persists the result via `DB_MANAGER.insert_data_session()`.

Returns `1` on successful insertion, or `0` on failure; integrity constraint violations (e.g., duplicate entries) are handled silently with a descriptive message, while other construction-level exceptions are surfaced to the user via a `QMessageBox` warning.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
Inserts a media thumbnail record into the `MEDIA_THUMB` database table by assigning the provided metadata to instance attributes and delegating the actual record construction to `DB_MANAGER.insert_mediathumb_values`, using an auto-incremented ID derived from the current maximum ID in the table. The constructed record is then persisted via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if the operation fails; integrity constraint violations (e.g., duplicate thumbnail entries) are handled silently, while other database errors display a warning dialog.

**Parameters:**

| Parameter | Description |
|---|---|
| `media_max_num_id` | The ID of the associated media record. |
| `mediatype` | The type of the media. |
| `filename` | The original media filename. |
| `filename_thumb` | The thumbnail filename. |
| `filetype` | The file type of the media. |
| `filepath_thumb` | The file path to the thumbnail. |
| `filepath_resize` | The file path to the resized media. |

**Returns:** `1` on success, `0` on failure.

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

Queries the database for pottery records matching the current form values (`sito`, `area`, `us`, and `id_number`) retrieved from the corresponding UI widgets. Constructs a search dictionary and uses `DB_MANAGER.query_bool` to retrieve matching `POTTERY` records. Returns a list of tuples containing each record's `id_rep`, the string `'CERAMICA'`, and the string `'pottery_table'`.

##### assignTags_reperti(self, item)

id_mediaToEntity,
id_entity,
entity_type,
table_name,
id_media,
filepath,
media_name

##### load_and_process_image(self, filepath)

*No description available.*
Loads a media file from the given `filepath`, determines its type (image, video, or 3D model) based on the file extension, and processes it for storage. If the thumbnail path is not configured, the method displays a localized informational message and aborts; otherwise, it checks for an existing database record for the file and, if none exists, inserts a new media record, generates thumbnails and resized copies via the appropriate utility classes, and adds the resulting item to the UI list widget. Remote storage backends are supported for the original file upload when configured; an `AssertionError` during processing triggers a localized warning dialog, and an unrecognized file extension raises a `ValueError`.

##### db_search_check(self, table_class, field, value)

Queries the database for records matching a specified field-value pair within a given table class. Constructs a search dictionary from the provided field and value, removes any empty entries using a `Utility` helper, and executes a boolean query via `DB_MANAGER`. Returns the query result.

##### on_pushButton_search_images_pressed(self)

Open the Image Search dialog with pre-filled filters for current Pottery record.

##### on_pushButton_removetags_pressed(self)

*No description available.*
Handles the press event of the "remove tags" button by removing tags and embeddings from selected thumbnail images in `iconListWidget`. If no image is selected, a language-appropriate warning is displayed; if one or more images are selected, the user is prompted with a confirmation dialog (supporting Italian, German, and English locales) before proceeding. Upon confirmation, the method resolves the pottery record ID via a database query using the current site, area, US, and ID number field values, then calls `_remove_image_tag_and_embedding` for each selected item and removes it from the widget list.

##### on_pushButton_all_images_pressed(self)

*No description available.*
Handles the press event of the "all images" button by querying the database for media thumbnails and related `CERAMICA` entity records, displaying an informational message and returning early if no data is found. If records exist, it constructs and displays a new widget containing a `QListWidget` with single-selection mode, a search field, a paginated navigation bar (previous/next buttons and up to five numbered page labels), and a conditionally visible "TAG" button that appears only when an item is selected. Finally, it calls `load_images()` to populate the list and connects the search field's `returnPressed` signal to `filter_items` for filtering the displayed results.

##### load_images(self, filter_text)

*No description available.*
Queries the database for all media thumbnail records and determines which images are untagged by comparing them against the `MEDIATOENTITY` table. When the total image count exceeds 100, only untagged images are displayed with pagination and optional filename filtering; otherwise, all images are shown, with tagged entries annotated with their associated `POTTERY` entity identifiers and displayed on a white background, while untagged entries are highlighted in yellow. Thumbnail icons are loaded using an LRU-style cache bounded by `self.cache_limit`, and the `QListWidget` (`self.new_list_widget`) is refreshed and paginated according to `self.current_page` and `self.page_size` before page labels are updated via `update_page_labels()`.

##### update_page_labels(self)

*No description available.*
Updates the visual state of all pagination controls to reflect the current page. Enables or disables the previous and next navigation buttons based on whether `current_page` is at the first or last page respectively, and disables the page number label corresponding to the active page while leaving all others enabled. Additionally updates the `current_page_label` and `total_pages_label` text to display the current page number and total page count.

##### go_to_previous_page(self)

*No description available.*
Navigates to the previous page by decrementing `current_page` by one, provided the current page is greater than 1. After updating the page index, it reloads the image set by calling `load_images` with the active filter text (`current_filter_text`). If the current page is already at 1, no action is taken.

##### go_to_next_page(self)

*No description available.*
Advances to the next page of images if the current page is less than the total number of pages. Increments `current_page` by one and reloads the image set by calling `load_images` with the current filter text. If the current page is already the last page, no action is taken.

##### on_page_label_clicked(self, page, _)

*No description available.*
Handles a page label click event by navigating to the specified page. If the requested `page` differs from `self.current_page`, it updates `self.current_page` to the new value and reloads the image set by calling `self.load_images` with the current filter text. The optional second parameter `_` is accepted but ignored.

##### filter_items(self)

*No description available.*
Retrieves the current text from the search field, converts it to lowercase, and stores it in `self.current_filter_text`. It then triggers a reload of the image list by calling `self.load_images` with the updated filter text, effectively applying the search filter to the displayed items.

##### on_done_selecting_all(self)

Processes all currently selected items in `new_list_widget` by associating each selected media file with the corresponding pottery records retrieved via a database query built from the current values of `comboBox_sito`, `comboBox_area`, `lineEdit_us`, and `lineEdit_id_number`. For each selected item, it looks up the media record by filename and, if the media-to-entity relationship does not already exist in the database, inserts a new `MEDIATOENTITY` record via `insert_mediaToEntity_rec`. After processing all selections, it refreshes the icon list widget by calling `fill_iconListWidget` and updates the last processed list widget item via `update_list_widget_item`.

##### update_list_widget_item(self, item)

*No description available.*
Updates the visual state and display text of a given `QListWidgetItem` based on its association with media and pottery records in the database. It queries the `MEDIATOENTITY` table using the item's text as the media name; if a matching record is found, the item's background is set to white and its text is appended with the associated pottery ID number (or "Not found" if no corresponding `POTTERY` record exists). If no `MEDIATOENTITY` record is found, the item's background is set to yellow to indicate it is untagged or unmatched.

##### fill_iconListWidget(self)

Populates `iconListWidget` with thumbnail entries corresponding to the items selected in `new_list_widget`. For each selected item, it queries the `MEDIA_THUMB` table via `DB_MANAGER.query_bool` using the item's filename, retrieves the local thumbnail path from `Connection`, and constructs a `QListWidgetItem` with the media filename as its text and a `QIcon` loaded from the resolved thumbnail file path. The resulting item is then appended to `iconListWidget`.

##### is_media_path_remote(self)

Check if the configured media thumbnail path is remote.

##### update_media_button_visibility(self)

Show/hide toolButtonPreviewMedia based on media path type.
- Remote media: show button (user clicks to load)
- Local media: hide button (auto-load)

##### on_toolButtonPreviewMedia_toggled(self)

Handler per caricare i media quando l'utente clicca il bottone

##### loadMediaPreviewLocal(self)

Carica media per path locali (veloce, senza progress bar).

##### loadMediaPreview(self)

Carica media per path remoti (con progress bar).

##### load_and_process_3d_model(self, filepath)

*No description available.*
Loads a 3D model file from the given `filepath`, extracts the base filename and file extension, and inserts a media record of type `'3d_model'` into the database via `insert_record_media`. It then generates a thumbnail image of the model using `generate_3d_thumbnail`, retrieves the current maximum media ID, and inserts a corresponding thumbnail record via `insert_record_mediathumb`. Finally, it creates a `QListWidgetItem` populated with the filename, media ID, and thumbnail icon, adds it to `iconListWidget`, and calls `assignTags_reperti` on the new item.

##### show_3d_model(self, file_path)

*No description available.*
Loads and renders a 3D mesh from the specified file path using PyVista, applying a JPEG texture of the same base name if one exists alongside the mesh file. Constructs and returns a `QWidget` containing an interactive `QtInteractor` plotter that supports trackball navigation, point-to-point distance measurement (activated via key events), bounding box dimension display, camera view presets, measurement clearing, and image export to PNG at 300 DPI. A toggleable instructions panel and a timestamped debug log widget are also embedded in the layout, with keyboard shortcuts bound to `o`, `c`, `e`, `m`, `r`, `x`, `y`, `z`, `w`, `v`, and `b`.

##### generate_3d_thumbnail(self, filepath)

Generates a thumbnail image for a 3D model file by reading the mesh from the specified filepath using PyVista, rendering it off-screen with the camera positioned in the XY plane, and saving the result as a PNG file. The thumbnail filename is derived from the original file's base name with a `_thumb.png` suffix appended, and the file is saved to the directory specified by `self.thumb_path`. Returns the full path to the generated thumbnail file.

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

*No description available.*
Processes a 3D model file by generating a thumbnail screenshot and preparing a resized copy of the original file. Using PyVista, it loads the mesh from `filepath`, renders an off-screen XY-plane view, and saves the resulting screenshot as a thumbnail to `thumb_path_str`. Because 3D models cannot be resized like images, the original file is copied as-is to `thumb_resize_str`; if a JPEG texture file sharing the same base name exists in the same directory as the source model, it is also copied to the resize folder. Returns a tuple of `(thumbnail_path, resize_path)`.

##### openWide_image(self)

Opens and displays the full-resolution media file associated with each selected item in `iconListWidget`. For each selected item, the method queries the `MEDIA_THUMB` database table to retrieve the file's resize path and media type, then constructs the full file path by resolving it against the configured thumbnail resize base path, handling both local filesystem paths and remote URL protocols (`unibo://`, `http://`, `https://`, `cloudinary://`). Depending on the resolved media type, the file is displayed in an `ImageViewer` dialog for images, a `VideoPlayerWindow` for videos, or a `QDialog`-wrapped 3D model viewer for 3D models; a warning is shown if the file is not found or the media type is unsupported.

##### charge_list(self)

Initializes and populates the form's combo boxes with data from the database and thesaurus system. It first resolves the user's locale from `QgsSettings` to determine the appropriate language code (falling back to `"EN"` if no match is found), then loads the site list from the database into `comboBox_sito` and retrieves area values from the `PYARCHINIT_THESAURUS_SIGLE` table using typology code `'11.13'` into `comboBox_area`. Finally, it delegates loading of remaining Pottery-related thesaurus combo boxes to `charge_thesaurus_combos`, passing the resolved language code.

##### charge_thesaurus_combos(self, lang)

Load thesaurus values for all Pottery comboboxes

##### load_datazione_list(self)

Load datazione_estesa values from periodizzazione_table for current sito

##### on_toolButtonPreview_toggled(self)

*No description available.*
Handles the toggle state change of `toolButtonPreview`, activating or deactivating the US/SE map preview mode. When the button is checked, it displays a localized informational message (in Italian, German, or English depending on `self.L`) notifying the user that preview mode is enabled, then calls `self.loadMapPreview()` to load the preview. When the button is unchecked, it calls `self.loadMapPreview(1)` to unload or reset the map preview without displaying a message.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handler triggered when the sort button is pressed. If the record state check does not return `1`, it opens a `SortPanelMain` dialog pre-populated with `self.SORT_ITEMS`, retrieves the selected items and order type, converts the selected items using `self.CONVERSION_DICT`, and executes a database sort query via `self.DB_MANAGER.query_sort` against the current `DATA_LIST`. After sorting, it resets the browse status to `'b'`, updates the sort status label to reflect the sorted state, resets the record counters, and refreshes the displayed fields via `self.fill_fields()`.

##### insert_new_row(self, table_name)

insert new row into a table based on table_name - uses getattr instead of eval

##### remove_row(self, table_name)

Remove selected row from table - uses getattr instead of eval

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by initializing the form for a new record entry. It establishes a connection to retrieve the configured site setting and, if the current browse status is not already `"n"`, transitions `BROWSE_STATUS` to `"n"`, updates the status and sort labels accordingly, and clears the input fields — either preserving the current site selection (via `empty_fields_nosite()`) or fully resetting all fields (via `empty_fields()`) depending on whether the active site matches the configured site set. Field editability and enable states for relevant controls are adjusted accordingly, the record counter is cleared, and the action buttons are disabled via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behavior based on the current `BROWSE_STATUS`. In browse/edit mode (`"b"`), it first checks for version conflicts via `concurrency_manager`; if a conflict is detected, the user is prompted to either reload the record or overwrite it. If no conflict exists and the record has been modified (as determined by `data_error_check` and `records_equal_check`), the user is prompted with a localized confirmation dialog before the update is applied, fields are cleared, and the record lock is released; if the status is not `"b"`, the method attempts to insert a new record via `insert_new_rec` and, on success, reloads and refreshes the form state accordingly.

##### insert_new_rec(self)

*No description available.*
Reads and validates all pottery record field values from the form's UI widgets (line edits, combo boxes, and text edits), converting each to the appropriate type (`str`, `int`, or `float`) or `None` if the field is empty. It then calls `DB_MANAGER.insert_pottery_values` to construct a new record — assigning the next available ID via `DB_MANAGER.max_num_id` — and persists it to the database via `DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` on failure, displaying a `QMessageBox` warning if an integrity error or any other exception occurs during either the data preparation or insertion steps.

##### data_error_check(self)

*No description available.*
Validates required form fields by checking that `lineEdit_id_number` and `comboBox_sito` are not empty, using an `Error_check` instance to perform each validation. If either field is empty, a warning `QMessageBox` is displayed to the user and an internal error flag is set. Returns `0` if all checks pass, or `1` if one or more validation errors are detected.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If no data errors are found but the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog — in Italian, German, or English depending on `self.L` — asking whether to save the changes, and delegates the response to `update_if()`. Returns `1` if data entry errors are present, or `0` if the unsaved-changes prompt was displayed.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the "View All" button press event by clearing any active field inputs and loading all records from the data source. If no records are found, it displays a localized informational message (Italian or English, based on `self.L`) and returns early. On success, it initializes the record counters, populates the fields with the first record, sets the browse status to `"b"`, and resets the sort status to `"n"`.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the data list when the corresponding button is pressed. If `check_record_state()` does not return `1`, it clears the current fields, resets `REC_CORR` to `0` and `REC_TOT` to the total number of records in `DATA_LIST`, then populates the fields with the first record and updates the record counter display accordingly. If `check_record_state()` returns `1`, no action is performed.

##### on_pushButton_last_rec_pressed(self)

Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index (`len(DATA_LIST) - 1`) and `REC_TOT` to the total number of records. It first clears the current field display via `empty_fields()`, then populates the fields with the last record's data using `fill_fields()`, and updates the record counter accordingly via `set_rec_counter()`. If `check_record_state()` returns `1`, the operation is skipped entirely; any other exceptions raised during execution are silently suppressed.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by navigating to the preceding record in the dataset. If the current record index (`REC_CORR`) would decrement below zero, it is reset to `0` and a warning dialog is displayed informing the user they are already on the first record. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated accordingly. Navigation is blocked if `check_record_state()` returns `1`.

##### on_pushButton_next_rec_pressed(self)

Advances the current record index (`REC_CORR`) by one to navigate to the next record in the dataset. If the incremented index reaches or exceeds the total record count (`REC_TOT`), the index is reverted and a warning dialog is displayed informing the user that they are already on the last record. Otherwise, the form fields are cleared and repopulated with the data for the new current record, and the record counter display is updated accordingly.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by displaying a language-sensitive confirmation dialog (Italian, German, or English, determined by `self.L`) before permanently removing the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the deletion is confirmed and succeeds, the method reloads the record list from the database; if records remain, it resets navigation state to the first record, updates the browse status, record counter, and UI fields accordingly, whereas if the database becomes empty, all data lists and counters are cleared and the fields are emptied. Any exception raised during deletion is reported to the user via a warning dialog.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "new search" button, initiating a new search session by transitioning `BROWSE_STATUS` to `"f"`. If the current browse status is not already `"f"` and `check_record_state()` returns `1`, the method takes no action; otherwise, it disables the search button, resets the status label, sort label, and record counter, and reloads the field lists via `charge_list()`. Depending on whether the current site (`comboBox_sito`) matches the configured site set, the method calls either `empty_fields_nosite()` or `empty_fields()` to clear the form, and adjusts the enabled state of relevant UI controls accordingly.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search button press event by first verifying that the browse status is set to `"f"` (free/new search mode); if not, it displays a localized warning message instructing the user to initiate a new search. When the status is valid, it collects and type-converts values from all form input fields (text edits, combo boxes, and line edits) into a search dictionary keyed by `TABLE_FIELDS`, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database through `DB_MANAGER.query_bool`. Depending on the query result, it either warns the user that no records were found and restores the current record view, or populates `DATA_LIST` with the returned results, updates the record counter, fills the form fields, and displays a localized message reporting the number of records found; in all cases, `enable_button_search(1)` is called upon completion.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's confirmation dialog response. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying the database with either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Upon a successful update, the browse status is set to `"b"` and the method returns `1`; if the update fails, it returns `0`.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `self.DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `self.rec_toupdate()`. Returns `1` on success or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default), based on `self.L`.

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `self.UTILITY.pos_none_in_list()` on `self.DATA_LIST_REC_TEMP`, which identifies the positions of `None` values within the temporary record list. The returned value, `rec_to_update`, represents those positions and is passed directly back to the caller.

##### charge_records(self)

*No description available.*
Loads records from the database into `self.DATA_LIST` by executing a single ordered query against the mapped table class. The query retrieves all records sorted by `self.ID_TABLE` in ascending order using `self.DB_MANAGER.query_ordered`, replacing a previously used double-query pattern for improved performance. This method returns no value.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The resulting string is returned to the caller.

##### yearstrfdate(self)

*No description available.*
Returns the current year as a formatted string. The method retrieves today's date using `date.today()` and extracts the four-digit year component by applying the `"%Y"` format directive via `strftime`. The resulting year string is then returned to the caller.

##### table2dict(self, n)

Convert table widget data to list - uses getattr instead of eval for security

##### tableInsertData(self, t, d)

Set the value into alls Grid - uses getattr and ast.literal_eval instead of eval

##### empty_fields(self)

Clears and resets all input fields in the form to their default empty state. This includes clearing line edits, text edits, and resetting all combo boxes to empty strings, covering fields such as site, area, US, box, photo, drawing, year, fabric, material, form, ware, decorations, dimensions, and other related attributes.

##### empty_fields_nosite(self)

Clears and resets all input fields in the form, excluding the site field. This includes clearing line edits for identifiers, measurements, and metadata fields, as well as resetting all combo boxes to empty text for attributes such as area, fabric, material, form, ware, decoration type, and dating. Text edit fields for descriptions and notes are also cleared.

##### fill_fields(self, n)

*No description available.*
Populates all UI form fields with data from the record at index `n` in `DATA_LIST`, covering text fields, combo boxes, and text editors for pottery attributes such as site, area, fabric, form, ware, decoration, and dimensional measurements. Before populating, it clears the media widget and returns early if `DATA_LIST` is empty or the index is out of bounds; after populating, it conditionally loads media previews either automatically for local paths or manually for remote paths. If a `concurrency_manager` is present, the method also tracks the current record's version number and ID, updates the lock indicator, and sets a soft lock on the record in `pottery_table`.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counter values for the form. Assigns the provided values to the `rec_tot` and `rec_corr` instance attributes, then updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` with their string representations.

##### set_LIST_REC_TEMP(self)

*No description available.*
Reads and validates all input field values from the form UI, converting each field to its appropriate type (`int`, `float`, or `None` for empty fields, with `qty` defaulting to `0`). Assembles the validated values — including identifiers, site/area/unit metadata, ceramic attributes (fabric, form, ware, Munsell colour, surface treatment, decoration details), measurements (diameters, height, preserved percentage), and contextual fields — into an ordered list stored in `self.DATA_LIST_REC_TEMP`. This temporary record list represents the current state of the form's input data.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` with the field values of the currently selected record, identified by `REC_CORR`, from `DATA_LIST`. Before iterating, it performs a bounds check to ensure `DATA_LIST` is non-empty and `REC_CORR` falls within a valid index range, returning early if either condition is not met. For each field name defined in `TABLE_FIELDS`, the corresponding attribute is retrieved from the current record using `getattr` with a default of `None`, and appended to `DATA_LIST_REC_CORR` as a string, or as an empty string if the attribute is absent.

##### records_equal_check(self)

*No description available.*
Compares the current record's data against the corresponding record in the data list by first populating both `DATA_LIST_REC_TEMP` and `DATA_LIST_REC_CORR` via `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()`, respectively. Returns `0` if the two lists are equal, or `1` if they differ.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets - uses getattr instead of eval for security

##### setTableEnable(self, t, v)

Set enabled state for table widgets - uses getattr instead of eval

##### testing(self, name_file, message)

*No description available.*
Opens a file at the path specified by `name_file` in write mode (`'w'`), writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are converted to strings via `str()` before use. No return value is produced and no exception handling is implemented.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path using the operating system's default file manager. On Windows, it uses `os.startfile`; on macOS (`Darwin`), it invokes `open` via `subprocess.Popen`; on all other platforms, it uses `xdg-open`.

##### populate_photo_drawing_from_media(self)

Auto-populate photo and drawing fields for all Pottery records from media associations.
Photos = images NOT starting with 'D_'
Drawings = images starting with 'D_'

##### setup_statistics_tab(self)

Setup the Statistics tab with all necessary widgets - RESPONSIVE LAYOUT

##### calculate_statistics(self)

Calculate all statistics for the current site

##### on_stats_combo_changed(self)

Handle statistics type combo box change

##### on_chart_type_changed(self)

Handle chart type combo box change - refresh current chart

##### generate_category_stats(self, field)

Generate statistics for a specific category field

##### update_chart_display(self)

Update chart based on selected chart type

##### plot_advanced_chart(self, d, title, chart_type)

Generate various chart types

##### generate_measurement_stats(self)

Generate statistics for measurement fields

##### generate_crosstab_stats(self, field1, field2)

Generate cross-tabulation statistics for two fields

##### plot_crosstab_chart(self, crosstab, rows, cols, field1, field2)

Plot a stacked bar chart for crosstab data

##### update_crosstab_chart_display(self)

Update crosstab chart based on selected chart type

##### plot_crosstab_advanced(self, crosstab, rows, cols, field1, field2, chart_type)

Plot crosstab with various chart types

##### torta_chart(self, d, t, yl)

Generate a pie chart

##### calculate_provenance_stats(self)

Calculate provenance statistics (area, US, sector distributions)

##### build_statistics_prompt(self)

Build a prompt for AI report generation with language support

##### get_openai_api_key(self)

Get OpenAI API key from file or prompt user to enter it

##### generate_ai_report(self)

Generate AI-based descriptive report with streaming

##### generate_chart_image(self, data, title, chart_type)

Generate a chart image and return the path

##### export_statistics_pdf(self)

Export statistics to PDF with charts and multilingual support

##### setup_similarity_search_ui(self)

Setup UI controls for visual similarity search

##### setup_embedding_auto_updater(self)

Setup the automatic embedding index updater

##### on_embedding_added(self, pottery_id, media_id, model)

Callback when embedding is added to index

##### on_embedding_removed(self, pottery_id, media_id, model)

Callback when embedding is removed from index

##### on_embedding_error(self, error_msg)

Callback when embedding operation fails

##### on_auto_update_changed(self, state)

Handle checkbox state change for auto-update setting

##### eventFilter(self, obj, event)

Handle drag & drop events for external image comparison

##### on_compare_external_clicked(self)

Handle compare external image button click - opens file dialog

##### on_external_search_complete(self, results)

Handle completion of external image search

##### on_external_search_complete_with_meta(self, results, meta)

Handle completion of external image search with metadata

##### show_external_results_dialog(self, results)

Show similarity search results for external image with datazione info.

Args:
    results: List of match results

##### on_threshold_changed(self, value)

Update threshold label when slider changes

##### on_similarity_model_changed(self, index)

Show/hide custom prompt based on selected model

##### get_similarity_model_name(self)

Get model name from combo box selection

##### get_similarity_search_type(self)

Get search type from combo box selection

##### on_find_similar_clicked(self)

Handle find similar button click

##### show_image_selection_dialog(self, images, pottery_id_number)

Show dialog to let user select which image to use for similarity search

##### on_similarity_search_complete(self, results)

Handle search completion

##### on_similarity_search_complete_with_meta(self, results, meta)

Handle search completion with metadata (top scores)

##### on_similarity_error(self, error_msg)

Handle search error

##### show_similarity_results_dialog(self, results)

Show dialog with similarity search results

##### navigate_to_pottery(self, result_data)

Navigate to a pottery record from search results using id_number

##### export_similarity_results(self, results, thumb_path_str, is_cloudinary)

Export similarity results to Excel with thumbnails and embedded chart

##### export_similarity_to_csv(self, results, file_path)

Fallback CSV export without thumbnails

##### show_similarity_chart(self, results)

Show similarity distribution chart in a popup dialog

##### on_build_index_clicked(self)

Handle build index button click

##### on_index_progress(self, current, total, message)

Update progress during index building

##### on_index_complete(self, message)

Handle index building completion

##### on_export_indexes_clicked(self)

Export all similarity indexes to a ZIP file for sharing

##### on_import_indexes_clicked(self)

Import similarity indexes from a ZIP file

##### on_update_index_clicked(self)

Update existing indexes with new/modified/deleted images

##### on_update_complete(self, message)

Handle update completion

##### on_train_khutm_clicked(self)

Open training dialog for KhutmML-CLIP model

##### on_prepare_dataset_clicked(self)

Prepare dataset for KhutmML training

##### on_khutm_training_complete(self, success, message)

Handle training completion

##### run_khutm_indexing_pipeline(self)

Run the KhutmML indexing pipeline after training

##### on_export_khutm_model_clicked(self)

Export the trained KhutmML-CLIP model to a ZIP file

##### on_import_khutm_model_clicked(self)

Import a KhutmML-CLIP model from a ZIP file

### KhutmTrainingDialog

Dialog for fine-tuning the KhutmML-CLIP model

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

Initializes a `KhutmTrainingDialog` instance by calling the parent `QDialog` constructor with the optional `parent` widget. Stores the provided `db_manager` reference, sets `training_process` to `None`, and initializes `training_output` as an empty string. Completes setup by invoking `initUI()` to configure the dialog's user interface.

##### initUI(self)

*No description available.*
Initializes and assembles the complete user interface for the KhutmML-CLIP model training dialog. It constructs a vertically stacked layout containing five grouped sections: a header, a training data source selector (database or folder), a training parameters panel (epochs, batch size, learning rate, and minimum images per class), a model output directory selector, and a training progress section with a status label, progress bar, and log viewer. Finally, it adds "Start Training" and "Cancel" buttons connected to their respective handler methods.

##### browse_training_folder(self)

Opens a native directory selection dialog with the title `"Select Training Folder"` using `QFileDialog.getExistingDirectory`. If the user selects a valid directory and confirms the dialog, the chosen folder path is written to `self.lineEdit_folder`. If the dialog is cancelled or no folder is selected, no action is taken.

##### browse_output_folder(self)

Opens a directory selection dialog prompting the user to select an output folder. If a valid folder is selected, the chosen path is written to `self.lineEdit_output`.

##### start_training(self)

Start the training process

##### read_training_output(self)

Read output from training process

##### check_training_status(self)

Check if training is complete

##### cancel_or_close(self)

Cancel training or close dialog

### DatasetPreparationDialog

Dialog for preparing training dataset

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent)

Initializes a new instance of `DatasetPreparationDialog`, a `QDialog` subclass for preparing a training dataset. Accepts a `db_manager` object and an optional `parent` widget, storing `db_manager` as an instance attribute before delegating UI setup to `initUI()`.

##### initUI(self)

*No description available.*
Initializes and assembles the complete user interface for the "Prepare Training Dataset" dialog. Sets the window title and minimum size (550×400), then constructs a `QVBoxLayout` containing a description label, a `QGroupBox` with eight mutually exclusive `QRadioButton` options for grouping strategy (by Fabric, Form, Specific Form, Decoration Type, Decoration Motif, Decoration combined, Ware, or Site — with "Group by Form" selected by default), an output folder row with a `QLineEdit` pre-populated to `~/pyarchinit/bin/training_data` and a Browse button, a statistics label, a hidden `QProgressBar`, and three action buttons ("Analyze Database", "Prepare Dataset" — initially disabled, and "Close"). A `QTimer.singleShot` call schedules an immediate invocation of `analyze_database` 100 ms after the dialog is shown.

##### browse_output(self)

Opens a directory selection dialog prompting the user to choose an output folder. If a folder is selected, updates the `lineEdit_output` field with the chosen directory path.

##### get_grouping_field(self)

Return the field to use for grouping based on radio selection

##### analyze_database(self)

Analyze database to show statistics

##### prepare_dataset(self)

Prepare the training dataset

### PotteryFilterDialog

Dialog for filtering Pottery records by ID Number and Year with checkboxes

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent, site_filter)

Initializes a `PotteryFilterDialog` instance by calling the parent `QDialog` constructor and setting up the core instance attributes: `db_manager`, `selected_ids` (empty list), `selected_year` (None), and `pottery_records` (empty list). If `site_filter` is not explicitly provided and a `parent` is given, the method attempts to retrieve the current site value from `parent.comboBox_sito`. After resolving the site filter, it stores it in `self.site_filter` and delegates UI construction to `initUI`.

##### initUI(self)

Initializes and assembles the dialog's user interface, setting a localized window title (Italian, German, or English) that optionally appends site filter information, and establishing a minimum size of 450×550 pixels. It constructs a `QVBoxLayout` containing a year filter `QComboBox`, an ID Number search bar (`QLineEdit`), "Select All" / "Deselect All" buttons, and a checkable `QListWidget`, all with labels and placeholder text adapted to the active language (`self.L`). After populating the year combo box and list widget via `populate_years_and_ids()`, it appends a status label updated by `update_status_label()` and a localized "Apply Filter" button connected to `apply_filter`.

##### natural_sort_key(self, text)

Natural sorting key that handles alphanumeric values correctly

##### populate_years_and_ids(self)

Fetch pottery records and populate year combobox and ID list

##### on_year_changed(self, index)

Handle year selection change

##### get_filtered_records(self)

Get records filtered by selected year

##### update_id_list(self)

Update the ID list based on current year filter

##### update_list_widget(self, id_numbers, records)

Update the list widget with the given ID numbers

##### filter_list(self, text)

Filter the list based on search text

##### select_all(self)

Select all visible checkboxes

##### deselect_all(self)

Deselect all visible checkboxes

##### update_status_label(self)

Update the status label with count of selected items

##### get_selected_count(self)

Get the count of selected checkboxes

##### apply_filter(self)

Apply the filter and close the dialog

##### get_selected_ids(self)

Return the list of selected ID numbers

##### get_selected_year(self)

Return the selected year (None if 'All years')

## Functions

### log(message, level)

*No description available.*
An inner function defined within `get_images_for_entities` that conditionally emits a log message via the enclosing scope's `log_signal`. If `log_signal` is not provided (i.e., evaluates to falsy), the function performs no action. Accepts a `message` string and an optional `level` string parameter, defaulting to `"info"`.

**Parameters:**
- `message`
- `level`

### r_id()

*No description available.*
Queries the database for a `POTTERY` record matching the current values of `id_number`, `sito`, `area`, and `us` fields read from the UI controls. It constructs a search dictionary from these values and passes it to `DB_MANAGER.query_bool` to retrieve the matching record(s). Returns the `id_rep` value of the first result found, or `None` if no result is available.

### update_done_button()

*No description available.*
A callback function connected to the `itemSelectionChanged` signal of `new_list_widget`. It hides the "TAG" button (`done_button`) when no items are selected in the list widget, and shows it when at least one item is selected. When made visible, it also connects the button's `clicked` signal to the `on_done_selecting_all` handler.

### r_list()

*No description available.*
Builds and returns a list of pottery records matching the current filter criteria entered in the UI fields (`comboBox_sito`, `comboBox_area`, `lineEdit_us`, and `lineEdit_id_number`). It constructs a search dictionary from these field values and queries the database via `DB_MANAGER.query_bool` against the `POTTERY` table. Each matching record is appended to the result list as a three-element list containing the record's `id_rep`, the string `'CERAMICA'`, and the string `'pottery_table'`.

### add_debug_message(message, important)

*No description available.*
Appends a timestamped message to a read-only `QTextEdit` debug widget, prefixing each entry with the current date and time in `yyyy-MM-dd HH:mm:ss` format. If `important` is `True`, the formatted message is wrapped in `<b>` tags to render it in bold. The widget is capped at 1,000 lines; when this limit is exceeded, the oldest line is removed to maintain the maximum message count, and the cursor is scrolled to remain visible at the end.

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

*No description available.*
Toggles the active measurement state by inverting the boolean value of `measuring` and clearing the `points` collection. When measurement is enabled, a debug message `"Misurazione iniziata"` is logged as important; when disabled, `"Misurazione terminata"` is logged instead. This function also implicitly controls whether subsequent left-click events are processed, as `on_left_click` returns early when `measuring` is `False`.

### on_left_click(picked_point)

*No description available.*
Handles a left-click event during an active measurement session by recording the selected 3D point. If `measuring` is active and `picked_point` is not `None`, the point is appended to the `points` list and a red sphere marker — sized relative to the mesh length — is added to the plotter at that location. Once exactly two points have been collected, `measure_distance` is called with both points and the `points` list is cleared; if no valid point was picked, a debug message is logged instead.

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

*No description available.*
Logs the provided coordinate pair for diagnostic purposes by emitting a debug message that displays both `coord1` and `coord2`. The message is marked as important, ensuring it is surfaced prominently in the debug output. This function performs no computation or validation beyond the logging call.

**Parameters:**
- `coord1`
- `coord2`

### measure_distance(point1, point2)

*No description available.*
Computes the Euclidean distance between two 3D points using `numpy.linalg.norm` and visualises the measurement in the active `plotter` by adding a red line connecting the two points. Point labels `"P1"` and `"P2"` are rendered at each endpoint, and the computed distance (formatted to two decimal places, in centimetres) is displayed as a label at the midpoint of the line. All added actors are appended to `measurement_objects` for later removal, the plotter is re-rendered, and a debug message reporting the final distance is emitted.

**Parameters:**
- `point1`
- `point2`

### clear_measurements()

*No description available.*
Removes all active measurement actors from the plotter by iterating over `measurement_objects` and calling `plotter.remove_actor()` on each one. After removal, both the `measurement_objects` and `points` collections are cleared. The plotter is then re-rendered to reflect the updated state.

### export_image()

*No description available.*
Opens a save-file dialog prompting the user to specify a destination path for a PNG image. If a path is provided, captures a screenshot of the current plotter viewport at a fixed resolution of 300 DPI with dimensions of 15×10 cm (1772×1181 pixels), preserving and restoring the camera position after capture. On success, displays an informational message box; on failure, catches the exception and displays a warning dialog alongside a debug message.

### get_visible_faces(plotter, mesh)

*No description available.*
Determines which faces of a axis-aligned box mesh are visible from the current camera position. It computes the direction vector from the mesh center to the camera, then tests it against six predefined axis-aligned face normals (±X, ±Y, ±Z) using the dot product. Returns a list of face indices (0–5) for which the dot product with the camera direction is positive, indicating those faces are oriented toward the camera.

**Parameters:**
- `plotter`
- `mesh`

### edge_visibility(edge, visible_faces)

*No description available.*
Determines whether a given edge of a cube is visible based on the set of currently visible faces. The function uses a hardcoded mapping (`edge_to_faces`) that associates each edge, identified by a tuple of two vertex indices, with the list of face indices it borders. Returns `True` if at least one of the edge's associated faces is present in `visible_faces`, otherwise returns `False`.

**Parameters:**
- `edge`
- `visible_faces`

### calculate_label_position(p1, p2, offset_factor)

*No description available.*
Computes an offset label position for a line segment defined by two endpoints `p1` and `p2`. It first finds the midpoint of the segment, then calculates a perpendicular direction (preferring the cross product with `[0, 0, 1]`, falling back to `[0, 1, 0]` if the result is near-zero) and normalizes it. The final position is returned as the midpoint displaced along the perpendicular by a distance proportional to the segment length scaled by `offset_factor` (default `0.1`).

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

*No description available.*
Creates and adds a billboard text label to a VTK plotter at a specified 3D position, styled with a centered black font on a semi-transparent white background at font size 6. The label is oriented in 3D space by computing a rotation angle around the Z-axis: if `is_vertical` is `True`, the angle is fixed at 90 degrees; otherwise, it is derived from the `direction` vector using `arctan2`. The configured `vtkBillboardTextActor3D` instance is added to the plotter and returned.

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

*No description available.*
Renders dimensional measurements for a mesh's bounding box within a 3D plotter, provided the bounding box is currently visible and the update interval of 0.5 seconds has elapsed since the last refresh. It removes any existing measurement actors, then computes and draws line segments along the X (width), Y (depth), and Z (height) axes of the mesh bounds, annotating each with a distance label in centimeters. Vertical orientation is applied specifically to the Z-axis (height) label, and the plotter is re-rendered after all measurement actors are added.

### toggle_bounding_box_measures()

*No description available.*
Toggles the visibility state of bounding box measurements by inverting the `bounding_box_visible` flag. When activated, it calls `show_measures()` to display the measurement objects and logs a debug message; when deactivated, it removes all actors in `measurement_objects` from the plotter, clears the list, triggers a render, and logs a corresponding debug message.

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
Changes the active plotter's camera to a predefined view orientation by dynamically calling the corresponding `view_<direction>` method on the plotter object. The `direction` parameter is used to construct the method name via string formatting and `getattr`, allowing any valid view direction supported by the plotter to be invoked. No return value is produced.

**Parameters:**
- `direction`

### process_file_path(file_path)

*No description available.*
Accepts a single `file_path` string parameter and returns the URL-decoded equivalent by calling `urllib.parse.unquote` on it. This converts any percent-encoded characters in the file path (e.g., `%20`) back to their original Unicode representation.

**Parameters:**
- `file_path`

### show_image(file_path)

*No description available.*
Opens a modal image viewer dialog for the specified file path. It instantiates an `ImageViewer` with the current object as its parent, loads the image via `show_image`, and executes the dialog modally using `exec()`.

**Parameters:**
- `file_path`

### show_video(file_path)

*No description available.*
Displays a video file in a `VideoPlayerWindow` instance. If the video player window does not yet exist, it is instantiated with the parent object, `db_manager`, `icon_list_widget`, and `main_class` references before use. The specified video is then loaded via `set_video` and the player window is made visible.

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

Resolves the full file path for a given media file by detecting whether the input is already an absolute path (protocol-based or root-relative), a URL-based relative path, or a local filesystem path, and constructs the appropriate full path accordingly. Dispatches playback or display to the correct handler based on `media_type`, invoking `show_video` for video files, `show_image` for images, or `self.show_3d_model` for 3D models. If an unrecognized `media_type` is provided, a warning dialog is displayed to the user.

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

*No description available.*
Queries the database for media records matching the provided search criteria. It accepts a dictionary of search parameters and an optional table name (defaulting to `"MEDIA_THUMB"`), removes empty entries from the dictionary via `Utility.remove_empty_items_fr_dict`, then delegates to `self.DB_MANAGER.query_bool` to execute the boolean query. If the query raises an exception, a warning dialog is displayed and `None` is returned; otherwise, the query result is returned directly.

**Parameters:**
- `search_dict`
- `table`

### load_thesaurus(tipologia_sigla, use_sigla)

Queries the `PYARCHINIT_THESAURUS_SIGLE` database table for thesaurus entries matching the given `tipologia_sigla`, filtered by the specified language and the `'Pottery'` table name. Depending on the `use_sigla` flag, it extracts either the `sigla` or `sigla_estesa` field from each result, strips whitespace, deduplicates, and sorts the values. Returns a sorted list of unique string values suitable for populating a combobox.

**Parameters:**
- `tipologia_sigla`
- `use_sigla`

