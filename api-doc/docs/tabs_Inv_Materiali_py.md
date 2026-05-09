# tabs/Inv_Materiali.py

## Overview

This file contains 184 documented elements.

## Classes

### pyarchinit_Inventario_reperti

`pyarchinit_Inventario_reperti` is a QDialog subclass that implements the artefact inventory form (`inventario_materiali_table`) within the PyArchInit QGIS plugin. It provides a full record management interface for archaeological finds, supporting browsing, searching, inserting, updating, and deleting inventory records, along with media management (images, video, 3D models), PDF export, quantification charts, and a statistics tab with optional AI-generated reports. The class is fully multilingual, adapting its field labels, status messages, sort items, and conversion dictionaries to the active QGIS locale (Italian, English, German, French, Spanish, Portuguese, Arabic, Catalan, Romanian, Greek, and others).

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes an instance of the class by calling the parent constructor, configuring the UI, and setting up all required components. This includes injecting supplementary UI fields (`_inject_sub_inv_field`), restructuring the quantitative data tab (`_restructure_dati_quantitativi_tab`), applying the application theme, initializing delegate and state variables, and establishing an image cache with a maximum limit of 100 entries. It also attempts a database connection via `on_pushButton_connect_pressed`, connects relevant signals to their handlers, and finalizes the interface through `customize_gui` and `set_sito`.

##### get_images_for_entities(self, entity_ids, log_signal)

*No description available.*
Retrieves thumbnail images from the `MEDIATOENTITY` and `MEDIA_THUMB` database tables for each entity ID provided in `entity_ids`, filtering records by `entity_type` `'REPERTO'`. For each matching media record, it constructs an image entry containing the entity ID, the full thumbnail URL (built from the configured resize path prefix and the stored thumbnail path), and the media name as caption. Returns a list of such image dictionaries, or an empty list if `entity_ids` is empty or an exception occurs; optional progress and error messages are emitted via `log_signal` if provided.

##### setnone(self)

*No description available.*
Iterates over a set of form fields — including `lineEdit_tipo_contenitore`, `lineEdit_n_reperto`, `comboBox_struttura`, `lineEditFormeMax`, `lineEditFormeMin`, `lineEditTotFram`, and `lineEdit_nr_cassa` — and clears each one if its current value evaluates to `'None'`, `None`, `'NULL'`, or `'Null'`. For each matching field, the method calls `clear()`, sets the text to an empty string, and triggers `update()` to refresh the widget. This method is intended to sanitize form fields by removing null-like placeholder values from the UI.

##### on_pushButtonQuant_pressed(self)

Opens a `QuantPanelMain` dialog pre-populated with `self.QUANT_ITEMS`, then processes the selected quantification type (`dlg.TYPE_QUANT`) and parameters (`dlg.ITEMS`) against `self.DATA_LIST`. Depending on the active language (`self.L`), it aggregates either minimum vessel forms (`forme_minime`) or total fragments (`totale_frammenti`) into a summarised dataset, exports the results to a CSV file in `self.QUANT_PATH`, and renders a chart via `self.plot_chart`. If the resulting dataset is empty, a language-appropriate warning dialog is displayed instead.

##### parameter_quant_creator(self, par_list, n_rec)

*No description available.*
Accepts a list of parameter names (`par_list`) and a record index (`n_rec`), then converts each parameter name to its corresponding internal attribute name using `CONVERSION_DICT`. For each converted parameter, it retrieves the associated value from `DATA_LIST` at the specified record index and formats it as a labeled string segment using the first four characters of the original parameter name. Returns a single concatenated string containing all formatted parameter-value pairs, each prefixed with ` -`.

##### plot_chart(self, d, t, yl)

*No description available.*
Renders a bar chart on the widget's canvas using the provided data. Accepts a list of `(team, value)` tuples as `d`, clears the existing canvas, and draws bars with a width of `0.5`, centered alignment, and an alpha of `0.4`. Each bar is annotated with a rotated label combining the team name and its integer height value, and the chart title and y-axis label are set from `t` and `yl` respectively.

##### torta_chart(self, d, t, yl)

*No description available.*
Renders a pie chart on the widget's canvas using the provided data, title, and y-axis label. If `d` is a list of `[label, value]` pairs, it clears the current axes, constructs a dictionary from the list, and draws a pie chart with percentage annotations (`'%1.1f%%'`), equal aspect ratio, and the specified title and y-label. The canvas is redrawn upon completion.

##### matrice_chart(self, d, t, yl)

*No description available.*
Accepts a list of key-value pairs (`d`), a chart title (`t`), and a y-axis label (`yl`), then constructs a correlation matrix from the numeric values using `numpy.corrcoef`. Renders the resulting correlation matrix as a color-mapped heatmap (`'coolwarm'`) on the widget's canvas using `matshow`, and attaches a colorbar to the figure. Clears any existing plot before drawing, then applies the provided title and y-axis label before refreshing the canvas.

##### on_pushButton_connect_pressed(self)

*No description available.*
Handles the connect button press event by establishing a database connection using `Connection` and obtaining a database manager via `get_db_manager`. If the connection succeeds, it determines whether the backend is SQLite, sets the database username on the concurrency manager if present, and loads existing records; when records are found, it initialises browse state and populates the UI fields, otherwise it displays a localised welcome message (Italian, German, or English) and opens a new record form. If the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar indicating a connection failure or detected bug.

##### loadMapPreview(self, mode)

*No description available.*
Loads or clears a map preview canvas based on the specified mode. When `mode=0`, the method retrieves the current record from `DATA_LIST` using `REC_CORR` as the index, constructs a filter expression from `ID_TABLE` and the record's corresponding attribute value, and passes it to `self.pyQGIS.loadMapPreviewReperti` to obtain layers, which are then set on `self.mapPreview` and zoomed to full extent. When `mode=1`, the method clears all layers from `self.mapPreview` and resets the zoom to full extent; the method exits immediately if `self.mapPreview` does not exist as an attribute.

##### customize_gui(self)

Initializes and configures all GUI components for the material inventory form based on the current user locale retrieved from `QgsSettings`. It populates `comboBox_area` and all table widget column delegates (`tableWidget_elementi_reperto`, `tableWidget_misurazioni`, `tableWidget_tecnologie`) with locale-specific thesaurus values queried from `PYARCHINIT_THESAURUS_SIGLE` via `DB_MANAGER`. It also configures the `iconListWidget` media preview widget, creates and attaches a `QgsMapCanvas` tab to `tabWidget`, updates media button visibility, and invokes `setup_filter_button` and `setup_statistics_tab` to complete the interface setup.

##### setup_filter_button(self)

Setup the filter button for Inventario Materiali

##### on_pushButton_filter_inv_pressed(self)

Open filter dialog for Inventario Materiali

##### filter_records_by_selection(self, selected_ids, selected_year, filter_type)

Filter records based on selected IDs and year

##### dropEvent(self, event)

Handles drop events by extracting file URLs from the event's MIME data and validating each dropped file against a predefined list of accepted formats (`jpg`, `jpeg`, `png`, `tiff`, `tif`, `bmp`, `mp4`, `avi`, `mov`, `mkv`, `flv`, `obj`, `stl`, `ply`, `fbx`, `3ds`). If a dropped file matches an accepted format, it is passed to `load_and_process_image`; otherwise, a warning dialog is displayed indicating the unsupported file type. Any exception encountered during file processing is caught and reported via a `QMessageBox` warning, after which the base class `dropEvent` is called.

##### dragEnterEvent(self, event)

*No description available.*
Handles the drag-enter event by inspecting the MIME data of the incoming drag action. If the dragged data contains URLs, the proposed action is accepted; otherwise, the event is ignored. This method controls whether a drag operation is permitted to proceed over the widget.

##### dragMoveEvent(self, event)

*No description available.*
Handles the drag move event triggered when a dragged object is moved within the widget's boundaries. Unconditionally accepts the proposed drop action by calling `event.acceptProposedAction()`, allowing the drag operation to continue without restriction.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database using the provided media metadata, automatically assigning the next available ID by incrementing the current maximum `id_media` value. The record is created with a default description of `'Insert description'` and a default tag of `"['imagine']"`, then committed via a database session.

Returns `1` on successful insertion, or `0` if the operation fails — distinguishing integrity constraint violations (e.g., duplicate entries) from other exceptions, with a warning dialog displayed for errors occurring during record construction.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the `MEDIA_THUMB` database table by assigning the next available ID and persisting the provided metadata fields. The method delegates record construction to `DB_MANAGER.insert_mediathumb_values` and commits the data via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if the operation fails — silently suppressing integrity constraint violations (e.g., duplicate thumbnail entries) and displaying a warning dialog for all other exceptions.

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

*No description available.*
Queries the database for an inventory material record matching the current site (`comboBox_sito`) and inventory number (`lineEdit_num_inv`) values from the UI. It constructs a search dictionary with the `sito` and `numero_inventario` fields and executes a boolean query against the `INVENTARIO_MATERIALI` table via `DB_MANAGER`. Returns a list containing a single tuple of the form `[id_invmat, 'REPERTO', 'inventario_materiali_table']` for the matched record.

##### assignTags_reperti(self, item)

*No description available.*
Assigns media tags to all reperto (find) records by linking a media file to each entity in the generated reperto list. For each reperto entry, it retrieves the corresponding media record from the database by querying against the filename derived from `item.text()`, then calls `insert_mediaToEntity_rec` to associate the media with the entity using its ID, type, and table reference. If no reperto records are found, the method returns immediately without performing any operations.

##### load_and_process_image(self, filepath)

*No description available.*
Loads a media file from the given `filepath`, determines its type (image, video, or 3D model) based on the file extension, and processes it for storage. If the thumbnail path is not configured, the user is notified via a localized `QMessageBox`; otherwise, the method checks for an existing database record and, if none exists, inserts a new media record, generates thumbnails and resized copies using the appropriate utility classes, and adds the resulting item to the `iconListWidget`. Remote storage upload of the original file is attempted when the configured resize path uses a recognized remote scheme; an `AssertionError` raised during processing is caught and reported to the user with a localized warning.

##### db_search_check(self, table_class, field, value)

*No description available.*
Performs a boolean database query against a specified table class using a single field-value pair as the search criterion. The method constructs a search dictionary from the provided field and value, removes any empty entries via the `Utility.remove_empty_items_fr_dict` helper, and delegates the query to `DB_MANAGER.query_bool`. Returns the result of the database query.

##### on_pushButton_search_images_pressed(self)

Open the Image Search dialog with pre-filled filters for current Inventario Materiali record.

##### on_pushButton_removetags_pressed(self)

*No description available.*
Handles the press event of the "remove tags" button by removing database tag associations from one or more selected thumbnail images in `iconListWidget`. If no items are selected, a language-appropriate warning is displayed; if items are selected, the user is prompted with a confirmation dialog before the irreversible operation proceeds. Upon confirmation, for each selected item the method resolves the current inventory record's database ID via an internal query against `INVENTARIO_MATERIALI`, calls `DB_MANAGER.remove_tags_from_db_sql_scheda` to remove the tags, and removes the item from the widget list. Display language is determined by `self.L`, with supported values `'it'` (Italian), `'de'` (German), and a default English fallback.

##### on_pushButton_all_images_pressed(self)

*No description available.*
Handles the press event of the "all images" button by querying the database for media thumbnails and media-to-entity records, displaying an informational message and returning early if no results are found. If records exist, it constructs and displays a new widget containing a `QListWidget` with single-selection mode, a search field, a paginated navigation bar (with previous/next buttons and up to five numbered page labels), and a "TAG" button that becomes visible only when an item is selected. Finally, it calls `load_images()` to populate the list and connects the search field's `returnPressed` signal to `filter_items()`.

##### load_images(self, filter_text)

Loads and displays thumbnail images into `new_list_widget`, applying an optional filename filter specified by `filter_text`. When the total number of images exceeds 100, only untagged images are displayed with pagination; otherwise, all images are shown, with tagged images (associated with a `'REPERTO'` entity type) displayed on a white background and annotated with their linked inventory numbers, while untagged images are highlighted in yellow. Thumbnail icons are managed through an LRU-style cache bounded by `cache_limit`, and page navigation labels are updated upon completion via `update_page_labels`.

##### update_page_labels(self)

*No description available.*
Updates the visual state of all pagination controls to reflect the current page. Enables or disables the `prevButton` and `nextButton` based on whether the current page is the first or last page, respectively, and toggles each label in `pageLabels` so that the label corresponding to the current page is disabled. Additionally, refreshes the `current_page_label` and `total_pages_label` text to display the current page number and total page count.

##### go_to_previous_page(self)

*No description available.*
Navigates to the previous page by decrementing `current_page` by one, provided the current page is greater than 1. After updating the page index, it reloads the image set by calling `load_images` with the active filter text stored in `current_filter_text`. No action is taken if the current page is already at the first page.

##### go_to_next_page(self)

*No description available.*
Advances to the next page of images if the current page is less than the total number of pages. When the condition is met, `current_page` is incremented by one and `load_images` is called with the current filter text to refresh the displayed content. If the current page is already the last page, no action is taken.

##### on_page_label_clicked(self, page, _)

*No description available.*
Handles a page label click event by navigating to the specified page. If the requested `page` differs from `self.current_page`, it updates `self.current_page` to the new value and reloads the image set by calling `self.load_images` with the current filter text. The optional second parameter `_` is accepted but ignored.

##### filter_items(self)

*No description available.*
Retrieves the current text from the search field, converts it to lowercase, and stores it in `self.current_filter_text`. It then calls `load_images` with the updated filter text to refresh the displayed items based on the search input.

##### on_done_selecting_all(self)

*No description available.*
Handles the completion of a bulk media-tagging operation by iterating over all selected items in `new_list_widget` and associating each selected media file with the inventory record identified by the current site (`comboBox_sito`) and inventory number (`lineEdit_num_inv`). For each selected item, it queries the `MEDIA` table by filename and, if a matching record is found and no existing `MEDIATOENTITY` entry already links it, inserts a new media-to-entity relationship via `insert_mediaToEntity_rec`. After processing all selected items, it refreshes the icon list widget by calling `fill_iconListWidget` and updates the last processed list widget item via `update_list_widget_item`.

##### update_list_widget_item(self, item)

*No description available.*
Updates the visual state and display text of a given `QListWidgetItem` based on its association with media-to-entity records in the database. It queries the `MEDIATOENTITY` table using the item's text as the media name; if a matching record is found, the item's background is set to white and its text is appended with the corresponding inventory number retrieved from the `INVENTARIO_MATERIALI` table (or `"Not found"` if no matching inventory record exists). If no `MEDIATOENTITY` record is found, the item's background is set to yellow to indicate it is untagged or unmatched.

##### fill_iconListWidget(self)

*No description available.*
Populates `iconListWidget` with icon-based list items derived from the currently selected items in `new_list_widget`. For each selected item, the method queries the `MEDIA_THUMB` database table using the item's filename, retrieves the corresponding thumbnail path via a `Connection` object, and constructs a `QListWidgetItem` with an icon loaded from the resolved file path. If a matching database record is found, the item is assigned the media filename as both its display text and custom user data before being added to `iconListWidget`.

##### connect_p(self)

Establishes a database connection using a `Connection` object and detects whether the backend is SQLite by inspecting the connection string. If the connection succeeds and records are present, it initialises browsing state, populates UI fields and counters, and disables relevant combo box and line edit controls; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`) and opens a new record form. If the connection or any subsequent operation raises an exception, a localised warning message is pushed to the QGIS message bar indicating the failure and advising a restart or bug report.

##### sketchgpt(self)

Open GPT Sketch window with lazy import to avoid DLL conflicts on Windows.

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

##### loadMediaPreview(self, mode)

Carica media per path remoti (con progress bar).

##### load_and_process_3d_model(self, filepath)

Loads and processes a 3D model file from the given `filepath` by extracting the filename and file type, inserting a media record into the database via `insert_record_media`, and generating a thumbnail using `generate_3d_thumbnail`. It then inserts a corresponding thumbnail record into the database using the current maximum media ID, and creates a `QListWidgetItem` populated with the filename, media ID, and thumbnail icon, which is added to `iconListWidget`. Finally, it calls `assignTags_reperti` on the newly created list item.

##### show_3d_model(self, file_path)

*No description available.*
Loads and renders a 3D mesh from the specified file path using PyVista, applying a JPEG texture if a matching file exists alongside the mesh file. Constructs and returns a `QWidget` containing an interactive `QtInteractor` plotter with trackball navigation, point-based distance measurement (activated via keyboard shortcut `'o'`), bounding box dimension display (`'m'`), measurement clearing (`'c'`), image export to PNG at 300 DPI (`'e'`), and multiple preset camera view shortcuts (`'r'`, `'x'`, `'y'`, `'z'`, `'w'`, `'v'`, `'b'`). Also provides a toggleable instructions panel and a read-only debug log widget (currently hidden from the layout).

##### generate_3d_thumbnail(self, filepath)

Generates a thumbnail image for a 3D model file by reading the mesh from the specified filepath using PyVista, rendering it off-screen with the camera positioned in the XY plane, and saving the resulting screenshot as a PNG file. The thumbnail filename is derived from the original file's base name with a `_thumb.png` suffix, and the file is saved to the directory specified by `self.thumb_path`. Returns the full path to the generated thumbnail file.

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

*No description available.*
Processes a 3D model file by generating a 2D thumbnail screenshot and copying the original file to a resize destination directory. Using PyVista, it loads the mesh from `filepath`, renders an off-screen XY-plane view, and saves the screenshot to `thumb_path_str` using the provided `media_max_num_id`, `filename`, and `media_thumb_suffix` to construct the output filename. If a JPEG texture file sharing the same base name as the model exists in the same source directory, it is also copied to the resize directory; the method returns a tuple of `(thumbnail_path, resize_path)`.

##### openWide_image(self)

Opens and displays the selected media items from `iconListWidget` in their appropriate viewer based on media type. For each selected item, the method queries the `MEDIA_THUMB` database table to retrieve the file path and media type, then resolves the full file path by combining it with the configured thumbnail resize base path, handling both local filesystem paths and remote URL protocols (`unibo://`, `http://`, `https://`, `cloudinary://`). Depending on the resolved media type, the file is displayed using an `ImageViewer` dialog for images, a `VideoPlayerWindow` for videos, a 3D model viewer embedded in a `QDialog` for `3d_model` types, or a warning dialog for unsupported types; a warning is also shown if no database record is found for a selected item.

##### numero_invetario(self)

*No description available.*
Handles automatic inventory number generation when the `checkBox_auto_inv` checkbox is checked. If the option is active, it displays an informational message, clears the `lineEdit_num_inv` field, and iterates over `DATA_LIST` to collect all existing `numero_inventario` values into a list, incrementing the last entry and sorting the result. The final value in the sorted list is then set as the text of `lineEdit_num_inv`; if the checkbox is not checked, the method takes no action.

##### charge_list(self)

Populates all combo box widgets in the form with data retrieved from the database, using the current QGIS locale to determine the display language. For the site list (`comboBox_sito`), values are fetched directly from the `site_table` via a `group_by` query; all other combo boxes (`comboBox_tipo_reperto`, `comboBox_tipologia`, `comboBox_criterio_schedatura`, `comboBox_definizione`, `comboBox_repertato`, `comboBox_diagnostico`, `comboBox_area`, `comboBox_lavato`, `comboBox_year`, `comboBox_compilatore`, and `comboBox_datazione`) are populated by querying the `PYARCHINIT_THESAURUS_SIGLE` table with language- and table-specific thesaurus codes. Each resulting list is sorted alphabetically before being added to its corresponding combo box.

##### msg_sito(self)

*No description available.*
Retrieves the currently configured archaeological site from the database connection and compares it against the value selected in `comboBox_sito`. If a matching site is found, it displays a localized informational message (Italian, German, or English) confirming the active connection. If no site has been configured, it displays a localized warning message prompting the user to set one, and opens the `pyArchInitDialog_Config` dialog if the user confirms.

##### set_sito(self)

*No description available.*
Retrieves the configured site (`sito`) setting via a `Connection` object and, if a site value is present, queries the database for all matching records using `DB_MANAGER.query_bool`. If records are found, it populates `DATA_LIST`, initialises the record counters, fills the UI fields, sets the browse status to `"b"`, and disables the `comboBox_sito` widget; if no records are found, a localised informational message is displayed in Italian, German, or English based on the current language setting `self.L`. Any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by first checking the current record state; if the record is not in a modified state, it opens a `SortPanelMain` dialog pre-populated with the existing `SORT_ITEMS` to allow the user to select sort fields and order type. Upon dialog completion, the selected items are converted using `CONVERSION_DICT`, and the current data list is re-queried from the database via `DB_MANAGER.query_sort` using the converted sort fields and sort mode. The method then resets the browse and sort status labels, updates record counters, clears the current fields, and repopulates them with the first record of the newly sorted data list.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by preparing the form to accept a new data entry. It first performs a data error check if existing records are present, then transitions the browse status to `"n"` (new), clears the input fields, and updates the status label, sort label, and record counter accordingly. Depending on whether the current site (`comboBox_sito`) matches the configured site setting retrieved from `Connection`, it either clears only non-site fields and locks the site combo box while auto-populating the inventory number, or clears all fields and enables the site combo box for manual entry; in both cases, input controls are reconfigured and action buttons are disabled via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event, branching behaviour based on the current browse status (`BROWSE_STATUS`). In edit mode (`"b"`), it performs a concurrency/version conflict check against `inventario_materiali_table` before validating data and prompting the user (in Italian, German, or English) to confirm saving any detected modifications; if no changes are detected, a warning is displayed instead. In insert mode, it validates the data, attempts to insert a new record, and upon success reloads the record list, updates UI controls, and resets the form state.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle event of `toolButtonGis`, displaying a localized informational message box to notify the user of the current GIS mode state. When the button is checked, a message indicates that GIS mode has been activated and search results will be displayed on the GIS; when unchecked, a message indicates that GIS mode has been deactivated and results will no longer be displayed. The displayed message text is determined by the language setting `self.L`, supporting Italian (`'it'`), German (`'de'`), and a default English fallback.

##### generate_list_foto(self)

*No description available.*
Iterates over all records in `self.DATA_LIST` and builds a list of photo-related data entries for items of entity type `'REPERTO'`. For each record that has an `id_invmat` attribute, it queries the `MEDIAVIEW` table via `self.DB_MANAGER` to retrieve associated media, resolving the first matching thumbnail path using a `Connection` instance. Each entry in the returned list contains eleven fields: site name, find number, thumbnail path, stratigraphic unit, definition, dating, conservation state, container type, box number, photo ID, and drawing ID.

##### generate_list(self)

*No description available.*
Iterates over all entries in `self.DATA_LIST` and converts each record into a flat list of string values. For each entry, it extracts thirteen fields — `sito` (with underscores replaced by spaces), `numero_inventario`, `area`, `us`, `tipo_reperto`, `repertato`, `n_reperto`, `tipo_contenitore`, `nr_cassa`, `luogo_conservazione`, `years`, `photo_id`, and `drawing_id` — where `photo_id` and `drawing_id` are safely resolved to an empty string if the attribute is absent or falsy. Returns the resulting list of lists as `data_list`.

##### generate_list_pdf(self)

*No description available.*
Iterates over `self.DATA_LIST` to build and return a structured list of records intended for PDF generation. For each entry that possesses an `id_invmat` attribute, it queries the `MEDIAVIEW` table via `DB_MANAGER` to retrieve associated media thumbnails, resolving the first available thumbnail path using the configured `thumb_resize` setting. Each record is assembled as a 30-element list containing fields such as inventory number, site, find type, conservation state, measurements, bibliographic references, and resolved thumbnail and identifier values; any per-record exceptions are surfaced to the user via a `QMessageBox` warning.

##### on_pushButton_print_pressed(self)

Slot handler triggered when the print push button is pressed. Determines the active interface language via `self.L` and, for each checked export checkbox (`checkBox_s_us`, `checkBox_e_us`, `checkBox_e_foto_t`, `checkBox_e_foto`), generates the corresponding PDF data list and invokes the appropriate language-specific build method on a `generate_reperti_pdf` instance to produce finds sheets, box indexes, or photo/inventory indexes. A `QMessageBox` confirmation or error dialog is displayed after each export operation; not all checkbox options are implemented for every language.

##### setPathpdf(self)

Opens a file dialog prompting the user to select an existing PDF file, using `self.PDFFOLDER` as the initial directory and filtering for `.pdf` files. If a file is selected, the chosen path is displayed in `self.lineEdit_pdf_path` and saved to `QgsSettings` with an empty string key. The method does not return a value.

##### openpdfDir(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path using the appropriate system command for the current operating system. On Windows, it uses `os.startfile`; on macOS (`Darwin`), it invokes `open` via `subprocess.Popen`; on all other systems, it uses `xdg-open` via `subprocess.Popen`.

##### generate_el_casse_pdf(self, sito)

Queries the database for all distinct crate numbers (`nr_cassa`) associated with the specified archaeological site (`sito`) and, for each crate, collects the inventory numbers with find types, the associated area/stratigraphic unit references (formatted according to the active language `self.L`: Italian, German, or English), and the conservation location. Assembles this information into a list of per-crate data lists (`data_for_pdf`), where each entry contains the crate identifier, inventory summary string, area/unit string, and conservation location. Returns the assembled list, or displays a warning dialog if an exception occurs (e.g., when the crate field is empty).

##### on_pushButton_esporta_a5_pressed(self)

Esporta la scheda inventario in formato A5 con immagine

##### record_to_list(self, record)

Converte un record inventario in lista per il PDF generator

##### exp_pdf_elenco_casse_main_experimental(self)

*No description available.*
An incomplete, experimental method intended to prepare structured data for PDF generation of a crate inventory list (*elenco casse*). It builds several intermediate dictionaries mapping crates to stratigraphic units (US), stratigraphic units to structures, and inventory numbers to their associated site/area/US/structure data, using `index_elenco_casse`, `us_list_from_casse`, and `strutture_list_from_us` as data sources. The method is not finished — it contains diagnostic `QMessageBox` calls throughout and does not produce any PDF output or return value; the call to the presumed completed counterpart `exp_pdf_elenco_casse_main` is commented out.

##### index_elenco_casse(self)

*No description available.*
Iterates over all records in `self.DATA_LIST` and collects the `nr_cassa` field value from each record into a list. Duplicate entries are then removed from the list using `self.UTILITY.remove_dup_from_list`. Returns the resulting deduplicated list of cassa numbers.

##### us_list_from_casse(self, sito, cassa)

*No description available.*
Queries the database for all records matching the given site (`sito`) and storage box number (`nr_cassa`), filtering out any records where the `us` field is empty or falsy. For each matching record, it collects a tuple of `(sito, area, us)` values into a list. Returns the list of `(sito, area, us)` tuples associated with the specified site and storage box.

##### strutture_list_from_us(self, sito, area, us)

*No description available.*
Queries the database for US (Unità Stratigrafica) records matching the specified `sito`, `area`, and `us` parameters, filtering out any records where the `struttura` field is empty or falsy. For each matching record that contains a valid `struttura` value, it collects a tuple of `(sito, struttura)` into a list. Returns the resulting list of `(sito, struttura)` tuples representing all structures associated with the given stratigraphic unit.

##### data_error_check(self)

*No description available.*
Validates required form fields before a record is saved by checking that the site (`comboBox_sito`) and inventory number (`lineEdit_num_inv`) fields are not empty, and that the inventory number, if provided, contains a numeric value. Validation messages are displayed via `QMessageBox.warning` in the appropriate language based on `self.L` (`'it'` for Italian, `'de'` for German, or English as the default). Returns `0` if all checks pass, or `1` if any validation error is detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates all field values from the form UI — including text inputs, combo boxes, table widgets (elementi reperto, misurazioni, rif_biblio, tecnologie, negative, diapositive), and optional fields such as quota and sub_inv — converting each to its appropriate type (`int`, `float`, `str`, or `None`) where required. It then constructs a new archaeological find (reperto) record by calling `self.DB_MANAGER.insert_values_reperti` with the assembled values and persists it to the database via `self.DB_MANAGER.insert_data_session`. Returns `1` on success, or `0` on failure, displaying a localized warning dialog if a duplicate record or any other exception is encountered.

##### on_pushButton_insert_row_elementi_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button is pressed. It delegates to `insert_new_row`, passing `'self.tableWidget_elementi_reperto'` as the target table widget. This results in a new row being inserted into the `tableWidget_elementi_reperto` table widget.

##### on_pushButton_remove_row_elementi_pressed(self)

Removes a row from the `tableWidget_elementi_reperto` table widget by delegating to the `remove_row` method with the widget's reference string as argument. This method serves as the slot handler for the `pushButton_remove_row_elementi_pressed` button's pressed signal.

##### on_pushButton_insert_row_misure_pressed(self)

*No description available.*
Event handler triggered when the "insert row" button for the measurements section is pressed. It calls `insert_new_row` with the target `'self.tableWidget_misurazioni'`, adding a new row to the measurements table widget.

##### on_pushButton_remove_row_misure_pressed(self)

*No description available.*
Slot method triggered when the "remove row" button for the measurements section is pressed. It delegates execution to `self.remove_row`, passing `'self.tableWidget_misurazioni'` as the target table identifier. This removes a row from the `tableWidget_misurazioni` table widget.

##### on_pushButton_insert_row_tecnologie_pressed(self)

*No description available.*
Event handler triggered when the "insert row" button for the *tecnologie* section is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidget_tecnologie'` as the target widget identifier. This results in a new row being added to the `tableWidget_tecnologie` table widget.

##### on_pushButton_remove_row_tecnologie_pressed(self)

*No description available.*
Handler triggered when the "remove row" button for the *tecnologie* section is pressed. It delegates to `self.remove_row`, passing `'self.tableWidget_tecnologie'` as the target table identifier. This removes a row from the `tableWidget_tecnologie` table widget.

##### on_pushButton_insert_row_rif_biblio_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button for the bibliographic references section is pressed. It calls `insert_new_row` with `'self.tableWidget_rif_biblio'` as the target, adding a new row to the bibliographic references table widget.

##### on_pushButton_remove_row_rif_biblio_pressed(self)

Removes a row from the bibliographic references table widget (`tableWidget_rif_biblio`) by delegating to the `remove_row` method. This method is triggered when the corresponding remove-row push button is pressed in the user interface.

##### on_pushButton_insert_row_negativi_pressed(self)

Handles the press event of the "insert row negativi" button by invoking `insert_new_row` with the target widget identifier `'self.tableWidget_negative'`. This inserts a new row into the `tableWidget_negative` table widget.

##### on_pushButton_remove_row_negativi_pressed(self)

*No description available.*
Handler method triggered when the "remove row" button for the negatives section is pressed. It delegates execution to `self.remove_row`, passing `'self.tableWidget_negative'` as the target table identifier. This results in the removal of a row from the `tableWidget_negative` table widget.

##### on_pushButton_insert_row_diapo_pressed(self)

*No description available.*
Handler method triggered when the "insert row" button for the diapositive section is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidget_diapositive'` as the target table widget. This results in a new row being added to the diapositive table widget.

##### on_pushButton_remove_row_diapo_pressed(self)

*No description available.*
Slot triggered when the "remove row" push button for the diapositive section is pressed. It delegates execution to `self.remove_row`, passing `'self.tableWidget_diapositive'` as the target widget identifier to remove a row from the diapositive table.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`, returning `1` immediately if any input errors are detected. If no input errors exist and the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog — in Italian, German, or English depending on `self.L` — prompting the user to save the changes, and delegates the response to `update_if()`. Returns `0` after handling the save prompt when no input errors are present.

##### on_pushButton_view_all_2_pressed(self)

*No description available.*
Handles the press event of the "view all" button by first checking the current record state via `check_record_state()`; if no unsaved changes are detected, it proceeds to load all records. It clears the current fields, reloads the full data list, and repopulates the fields, then sets the browse status to `"b"` and updates the status label accordingly. Finally, it resets the record counters to reflect the total number of records, navigates to the first record in `DATA_LIST`, and clears the sort indicator label.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Handles the press event of the "first record" navigation button. If the record state check returns `1`, no action is taken; otherwise, it clears the current fields, sets the current record position to the first entry in `DATA_LIST` (index `0`), and updates the record counter to reflect the total number of records and the current position. Any exception raised during this process is silently suppressed.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Handles the press event of the "last record" navigation button. If `check_record_state()` returns `1`, no action is taken; otherwise, it clears the current form via `empty_fields()`, sets both `REC_TOT` and `REC_CORR` to navigate to the final entry in `DATA_LIST`, and updates the display by calling `fill_fields()` and `set_rec_counter()`. Any exceptions raised during this process are silently suppressed.

##### on_pushButton_prev_rec_pressed(self)

Handles the "previous record" button press event by navigating to the preceding record in the dataset. If the current record index (`REC_CORR`) would fall below zero, it resets to zero and displays a localized warning message (Italian, German, or English) indicating that the first record has been reached. If navigation is valid and the record state check passes, it clears the current fields, populates them with the data for the previous record, and updates the record counter display.

##### on_pushButton_next_rec_pressed(self)

Advances the current record pointer (`REC_CORR`) to the next record in the dataset when the "next record" button is pressed. If the current record is already the last one, the pointer is not advanced and a localized warning dialog is displayed in Italian, German, or English depending on the value of `self.L`. Otherwise, the form fields are cleared and repopulated with the data for the new current record, and the record counter display is updated accordingly.

##### update_tma_inventario_field(self, sito, n_reperto, action)

Update TMA inventario field when n_reperto is added or removed

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently removing the currently displayed record from the database via `self.DB_MANAGER.delete_one_record`. Prior to deletion, if the current record carries an `n_reperto` value, the method captures it along with the associated `sito` and calls `self.update_tma_inventario_field` with `action='remove'` to update any referencing TMA records. After deletion, the UI state is refreshed accordingly: if the data list is empty, all record counters and fields are reset; otherwise, the list, fields, record counter, and sort status are updated to reflect the remaining records.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by resetting the form to a fresh search state (`BROWSE_STATUS = "f"`). If the current record state allows it, the method evaluates the active site (`comboBox_sito`) against the configured site setting retrieved via `Connection`: if they match, the site combo box is locked and only non-site fields are cleared via `empty_fields_nosite()`; otherwise, all fields are cleared via `empty_fields()` and the site combo box is made editable and enabled. In both branches, search-related UI elements are configured, the sort label is reset to the unsorted state (`"n"`), and the record counter is cleared.

##### on_pushButton_search_go_pressed(self)

Handles the execution of a database search when the search button is pressed. If the application is not in search mode (`BROWSE_STATUS != "f"`), a localized warning message is displayed instructing the user to initiate a new search first. Otherwise, it collects and type-converts values from all form fields (inventory number, area, US, crate number, fragment counts, measurements, and other attributes) into a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, queries the database using `DB_MANAGER.query_bool`, and updates the UI with the results — displaying localized warnings if no criteria were set or no records were found, populating the record list and fields on success, optionally refreshing GIS layers, and enabling navigation buttons when the search completes.

##### on_pushButton_tot_fram_pressed(self)

*No description available.*
Handles the press event of the `pushButton_tot_fram` button by displaying a localized warning dialog that prompts the user to choose between updating all fragments or only the current record. The dialog message is rendered in Italian, German, or English depending on the value of `self.L`. The user's response is passed directly to `update_tot_frammenti` to determine the scope of the update operation.

##### update_tot_frammenti(self, c)

*No description available.*
Updates the total fragment count based on the user's response `c` to a preceding confirmation dialog. If `c` equals `QMessageBox.StandardButton.Ok`, the method iterates over all records in `DATA_LIST`, evaluates each record's `elementi_reperto` field, sums the quantities of entries whose type matches `'frammenti'`, `'frammento'`, `'fragment'`, or `'fragments'`, and persists the computed total to the database via `DB_MANAGER.update`; it then queries the updated record and reflects the result in `lineEditTotFram`. If `c` is any other value (Cancel), only the current record's fragment total is recalculated from the in-memory `tableWidget_elementi_reperto` widget and displayed in `lineEditTotFram` without any database write.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by querying the database with either a default ascending sort on `ID_TABLE` or the current sort configuration depending on `SORT_STATUS`. Returns `1` if the update succeeds, `0` if it fails, and `None` if the user did not confirm.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by retrieving the record's primary key from `DATA_LIST` at index `REC_CORR` and passing it along with the updated field values returned by `rec_toupdate()` to `DB_MANAGER.update()`. Returns `1` on success, or `0` if `DATA_LIST` is empty, `REC_CORR` is out of bounds, the expected ID attribute is not found, or any exception occurs during the update. On failure, displays a localized `QMessageBox` warning appropriate to the error type — permission denial, encoding issues, or generic database errors — with message language determined by the `L` attribute (`'it'`, `'de'`, or default English).

##### charge_struttura(self)

*No description available.*
Populates the `comboBox_struttura` widget by querying the database for `struttura` values associated with the current record's site (`sito`), area, and stratigraphic unit (`us`). The method retrieves the `area` and `us` values from the current record in `DATA_LIST` using `REC_CORR` as the index, constructs a search dictionary, and executes a boolean query against the `US` table via `DB_MANAGER`. Duplicate entries are removed from the resulting list before populating the combo box, and the displayed text is cleared or set depending on the current browse status.

##### rec_toupdate(self)

*No description available.*
Returns a processed version of the temporary record list (`DATA_LIST_REC_TEMP`) by delegating to `self.UTILITY.pos_none_in_list`, which handles positioning or filtering of `None` values within the list. The resulting list, `rec_to_update`, is then returned to the caller. A commented-out line indicates a previously considered slice operation (`rec_to_update[:2]`) that is not active in the current implementation.

##### charge_records(self)

*No description available.*
Loads all records from the database into `DATA_LIST` by executing a single ordered query via `DB_MANAGER`. The query retrieves all entries from the table mapped by `MAPPER_TABLE_CLASS`, sorted in ascending order by `ID_TABLE`. This replaces a previously used double-query pattern for improved performance.

##### fill_fields(self, n)

*No description available.*
Populates all form widgets with data from the record at index `n` in `DATA_LIST`, setting `rec_num` to the given index and clearing the media widget before loading. Each UI field — including line edits, combo boxes, text edits, and table widgets — is populated with the corresponding attribute from the target record, converting `None` values to empty strings. After filling all fields, the method conditionally loads media previews based on whether the configured media path is local or remote, and always loads the map preview.

##### set_rec_counter(self, t, c)

Sets the total and current record counters for the widget. Assigns the provided values `t` and `c` to the instance attributes `rec_tot` and `rec_corr` respectively, then updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### tableInsertData(self, t, d)

Set the value into alls Grid - uses getattr instead of eval for security

##### insert_new_row(self, table_name)

Insert new row into a table - uses getattr instead of eval for security

##### remove_row(self, table_name)

Remove selected row from a table - uses getattr instead of eval for security

##### empty_fields(self)

Resets all input fields, combo boxes, and text editors in the form to their empty or default state. All rows are removed from the four table widgets (`tableWidget_elementi_reperto`, `tableWidget_misurazioni`, `tableWidget_rif_biblio`, and `tableWidget_tecnologie`), and a single new empty row is inserted into each after clearing. The optional `lineEdit_sub_inv` field is cleared only if the attribute exists and is not `None`.

##### empty_fields_nosite(self)

Resets all form fields to their empty or default state, excluding site-related fields. Clears all line edits, combo boxes, and text edits associated with inventory data (such as `num_inv`, `tipo_reperto`, `area`, `us`, `nr_cassa`, and related fields), as well as auxiliary numeric fields for ceramic measurements and typology. Additionally, removes all existing rows from the `tableWidget_elementi_reperto`, `tableWidget_misurazioni`, `tableWidget_rif_biblio`, and `tableWidget_tecnologie` tables, then inserts a single new empty row into each.

##### enable_button(self, n)

Enable/disable navigation and action buttons

##### enable_button_search(self, n)

Enable/disable buttons during search mode

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### setTableEnable(self, t, v)

Set enabled state for table widgets - uses getattr instead of eval

##### table2dict(self, n)

Convert table widget data to list - uses getattr instead of eval for security

##### set_LIST_REC_TEMP(self)

Collects and validates all form field values from the UI widgets, converting empty string inputs to `None` for database-compatible numeric and integer fields (`numero_inventario`, `forme_minime`, `forme_massime`, `totale_frammenti`, `n_reperto`, `diametro_orlo`, `peso`, `eve_orlo`, `nr_cassa`, and `years`). Table widget contents for `elementi_reperto`, `misurazioni`, `rif_biblio`, and `tecnologie` are extracted via `table2dict`. The resulting 33-element list is assigned to `self.DATA_LIST_REC_TEMP`, representing the current temporary record state of the form.

##### set_LIST_REC_CORR(self)

*No description available.*
Initializes `DATA_LIST_REC_CORR` as an empty list, then populates it with string-converted field values from the current record indicated by `REC_CORR` within `DATA_LIST`. Population only occurs if `DATA_LIST` is non-empty and `REC_CORR` falls within the valid index range of `DATA_LIST`. For each field name defined in `TABLE_FIELDS`, the corresponding attribute value is retrieved from `DATA_LIST[REC_CORR]` via `getattr` and appended as a string to `DATA_LIST_REC_CORR`.

##### records_equal_check(self)

*No description available.*
Compares the current record (`DATA_LIST_REC_CORR`) against a temporary record (`DATA_LIST_REC_TEMP`) by first populating both lists via `set_LIST_REC_CORR()` and `set_LIST_REC_TEMP()`. If `DATA_LIST_REC_CORR` is empty, indicating no current record exists, the method returns `0`. Returns `0` if the two record lists are equal, or `1` if they differ.

##### testing(self, name_file, message)

*No description available.*
Opens a file specified by `name_file` in write mode (`'w'`), writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are explicitly converted to strings via `str()` before use. This method returns no value.

##### on_pushButton_open_dir_pressed(self)

*No description available.*
Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path. The method detects the current operating system and uses the appropriate system call to launch the folder in the native file manager: `os.startfile` on Windows, `open` on macOS (Darwin), and `xdg-open` on all other platforms (typically Linux).

##### setPathpdf(self)

*No description available.*
Opens a file dialog prompting the user to select a PDF file, using `QFileDialog.getOpenFileName` filtered to `*.pdf` files and defaulting to the `PDFFOLDER` directory. If a valid path is selected, it updates the `lineEdit_pdf_path` widget with the chosen path and stores the value in `QgsSettings`.

##### openpdfDir(self)

*No description available.*
Opens the application's designated PDF output folder in the operating system's default file manager. The target directory path is constructed by combining the `PYARCHINIT_HOME` environment variable with the subdirectory name `pyarchinit_PDF_folder`. The method dispatches the appropriate system call based on the current platform: `os.startfile` on Windows, `open` on macOS (Darwin), and `xdg-open` on all other systems.

##### on_pushButton_export_ica_pressed(self)

Handles the press event of the `pushButton_export_ica` button. If the `mapper` attribute is `None`, it instantiates a new `ArchaeologicalDataMapper` object with `None` as its argument and assigns it to `self.mapper`. It then calls `show()` on the `mapper` instance to display it.

##### check_for_updates(self)

Check if current record has been modified by others

##### setup_statistics_tab(self)

Setup the Statistics tab with all necessary widgets

##### calculate_statistics(self)

Calculate all statistics for the current site

##### on_stats_combo_changed(self)

Handle statistics type combo box change

##### generate_category_stats(self, field)

Generate statistics for a specific category field

##### calculate_provenance_stats(self)

Calculate provenance statistics (area, US distributions)

##### generate_measurement_stats(self)

Generate statistics for measurement fields

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

### InventarioFilterDialog

Dialog for filtering Inventario Materiali records by numero_inventario, n_reperto, or years with checkboxes

**Inherits from**: QDialog

#### Methods

##### __init__(self, db_manager, parent, site_filter)

Initializes an instance of the class by calling the parent constructor and setting up core instance attributes, including `db_manager`, `selected_ids` (empty list), `selected_year` (None), `filter_type` (defaulting to `'numero_inventario'`), and `inv_records` (empty list). If `site_filter` is not explicitly provided and a `parent` is given, the method attempts to retrieve the site filter value from `parent.comboBox_sito.currentText()`. After resolving `site_filter`, the method stores it in `self.site_filter` and calls `self.initUI()` to build the user interface.

##### initUI(self)

Initializes and constructs the complete user interface for the inventory material filter dialog. It sets the window title and minimum size, then builds a `QVBoxLayout` containing a filter type combo box (`numero_inventario`, `n_reperto`, or `years`), an optional year combo box, a search bar, "Select All" / "Deselect All" buttons, a checkable `QListWidget`, a status label, and an "Apply Filter" button. All widget labels and titles are rendered in Italian, German, or English based on the value of `self.L`, and the window title is appended with site-specific information if `self.site_filter` is set.

##### natural_sort_key(self, text)

Natural sorting key that handles alphanumeric values correctly

##### populate_data(self)

Fetch inventory records and populate year combobox and list

##### on_filter_type_changed(self, index)

Handle filter type selection change

##### on_year_changed(self, index)

Handle year selection change

##### get_filtered_records(self)

Get records filtered by selected year

##### update_id_list(self)

Update the list based on current filter type and year filter

##### update_list_widget(self, values, records)

Update the list widget with the given values

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

Return the list of selected values

##### get_selected_year(self)

Return the selected year (None if 'All years')

##### get_filter_type(self)

Return the current filter type

## Functions

### log(message, level)

*No description available.*
An inner function defined within `get_images_for_entities` that conditionally emits a log message via the enclosing scope's `log_signal`. If `log_signal` is not `None`, it calls `log_signal.emit(message, level)`; otherwise, no action is taken. The `level` parameter defaults to `"info"`.

**Parameters:**
- `message`
- `level`

### r_id()

*No description available.*
A nested helper function defined within `on_pushButton_removetags_pressed` that retrieves the database ID of an inventory material record matching the current site and inventory number.

It constructs a search dictionary using the values from `comboBox_sito` and `lineEdit_num_inv`, queries the `INVENTARIO_MATERIALI` table via `DB_MANAGER.query_bool`, and returns the `id_invmat` field of the first matching record.

### update_done_button()

*No description available.*
A callback function connected to the `itemSelectionChanged` signal of `new_list_widget`. It hides the "TAG" button (`done_button`) when no items are selected in the list widget, and shows it when at least one item is selected. When made visible, it also connects the button's `clicked` signal to the `on_done_selecting_all` handler.

### r_list()

*No description available.*
An inner function defined within `on_done_selecting_all` that queries the database for inventory material records matching the current site (`comboBox_sito`) and inventory number (`lineEdit_num_inv`) values. It constructs a search dictionary and passes it to `DB_MANAGER.query_bool` against the `'INVENTARIO_MATERIALI'` table, then builds and returns a list of tuples containing each matching record's `id_invmat`, the string `'REPERTO'`, and the string `'inventario_materiali_table'`.

### process_file_path(file_path)

*No description available.*
Accepts a single `file_path` string parameter and returns it after decoding any percent-encoded characters using `urllib.parse.unquote`. This converts URL-encoded sequences (e.g., `%20`) back into their original characters, producing a plain, human-readable file path string.

**Parameters:**
- `file_path`

### query_media(search_dict, table)

*No description available.*
Queries the database for media records matching the provided search criteria. It first sanitizes the search dictionary by removing empty items via `Utility.remove_empty_items_fr_dict`, then delegates to `self.DB_MANAGER.query_bool` against the specified table, which defaults to `"MEDIA_THUMB"`. If the database query raises an exception, a warning dialog is displayed via `QMessageBox` and `None` is returned.

**Parameters:**
- `search_dict`
- `table`

### add_debug_message(message, important)

*No description available.*
Appends a timestamped message to a read-only `QTextEdit` debug widget, prefixing it with the current date and time in `yyyy-MM-dd HH:mm:ss` format. If `important` is `True`, the formatted message is wrapped in `<b>` tags to render it in bold. The widget is capped at 1,000 lines; when this limit is exceeded, the oldest line is removed to maintain the maximum message count.

**Parameters:**
- `message`
- `important`

### mouse_click_callback(obj, event)

*No description available.*
A VTK interactor observer callback that handles left mouse button press events during an active measuring session. When a `LeftButtonPressEvent` is received and `measuring` is `True`, it retrieves the screen coordinates from the plotter's interactor, uses a `vtkCellPicker` to resolve the 3D pick position on the renderer, and identifies the closest point on the mesh surface. If a valid cell is picked, it invokes `on_left_click` with the closest mesh point; otherwise, it logs a debug message indicating no surface point was found.

**Parameters:**
- `obj`
- `event`

### toggle_instructions()

*No description available.*
Toggles the visibility of the `instructions_widget` by showing it if it is currently hidden, or hiding it if it is currently visible. This function is connected to the `clicked` signal of the "Toggle Instructions" `QPushButton`, allowing the user to control the display of the instructions text on demand.

### toggle_measure()

*No description available.*
Toggles the active measurement state by inverting the boolean value of `measuring` and clearing the `points` collection. When measurement is enabled, a debug message `"Misurazione iniziata"` is logged as important; when disabled, `"Misurazione terminata"` is logged instead. This function also implicitly controls whether left-click point collection is active, as `on_left_click` returns early when `measuring` is `False`.

### on_left_click(picked_point)

*No description available.*
Handles a left-click event during an active measurement session by recording the selected 3D point. If `measuring` is active and `picked_point` is not `None`, the point is appended to the `points` list and a red sphere marker — sized relative to the mesh length — is added to the plotter at that location. Once exactly two points have been collected, `measure_distance` is called with both points and the `points` list is cleared; if no valid point was picked, a debug message is logged instead.

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

*No description available.*
Logs the provided coordinate pair for diagnostic purposes by emitting a formatted debug message containing both coordinate values. The message is marked as important, ensuring it is highlighted within the debug output. This function does not return a value or perform any validation beyond the debug logging call.

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
Removes all active measurement actors from the plotter by iterating over `measurement_objects` and calling `plotter.remove_actor()` on each one. After removal, both the `measurement_objects` and `points` collections are cleared. Finally, `plotter.render()` is called to refresh the display.

### export_image()

*No description available.*
Opens a save file dialog prompting the user to specify a destination path for a PNG image. If a path is provided, captures a screenshot of the current plotter view at a fixed resolution of 300 DPI with dimensions of 15×10 cm (1772×1181 pixels), preserving and restoring the camera position after capture. On success, displays an informational message box; on failure, catches the exception and displays a warning dialog alongside a debug message.

### get_visible_faces(plotter, mesh)

*No description available.*
Determines which faces of a axis-aligned box mesh are visible from the current camera position. It computes the direction vector from the mesh center to the camera, then evaluates it against six predefined axis-aligned face normals (±X, ±Y, ±Z) using the dot product. Returns a list of face indices (0–5) for which the dot product with the camera direction is positive, indicating those faces are oriented toward the camera.

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

Computes an offset label position for a line segment defined by two endpoints `p1` and `p2`. It calculates the midpoint of the segment, then derives a perpendicular vector (falling back to a cross product with `[0, 1, 0]` if the primary cross product with `[0, 0, 1]` is near-zero) to displace the label away from the line. The returned position is the midpoint shifted along the normalized perpendicular by a distance proportional to the segment length scaled by `offset_factor` (default `0.1`).

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

*No description available.*
Creates a 3D billboard text label at a specified position within a VTK plotter, styled with a centered black font (size 6) on a semi-transparent white background. The label is rotated in the Z-axis to align with the given `direction` vector, computing the angle via `arctan2`; if `is_vertical` is `True`, a fixed 90-degree orientation is applied instead. The constructed `vtkBillboardTextActor3D` actor is added to the plotter and returned.

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

*No description available.*
Renders dimensional measurement annotations for a mesh's bounding box within a 3D plotter, but only when `bounding_box_visible` is `True` and the elapsed time since the last update exceeds `update_interval`. On each valid update, it removes any existing measurement actors, computes the three primary bounding box edges corresponding to width (X), depth (Y), and height (Z), and draws each as a line with a formatted centimetre label positioned along the edge. Rendering is throttled by comparing the current time against `self.last_update_time` to avoid redundant updates within the defined interval.

### toggle_bounding_box_measures()

*No description available.*
Toggles the visibility state of bounding box measurements by inverting the `bounding_box_visible` flag. When enabled, it calls `show_measures()` to display the measurement objects and logs a debug message indicating activation; when disabled, it removes all actors in `measurement_objects` from the plotter, clears the list, triggers a render, and logs a deactivation message.

### camera_changed(obj, event)

*No description available.*
A callback function triggered by the `InteractionEvent` observer on the plotter's interactor. When invoked, it checks whether the bounding box is currently visible and, if so, calls `show_measures()` to refresh the displayed measurements. This ensures that bounding box measurements are updated in response to camera movement or interaction events.

**Parameters:**
- `obj`
- `event`

### reset_view()

*No description available.*
Resets the camera to its default position by calling `plotter.reset_camera()`. This function serves as a convenience wrapper to restore the plotter's camera view to a state that fits all visible actors within the viewport.

### change_view(direction)

*No description available.*
Changes the plotter's camera to a predefined view orientation by dynamically calling the corresponding `view_<direction>` method on the `plotter` object. The `direction` parameter is used to construct the method name via string formatting and `getattr`, allowing any supported view direction to be selected at runtime.

**Parameters:**
- `direction`

### process_file_path(file_path)

*No description available.*
Accepts a single `file_path` string parameter and returns the URL-decoded equivalent by calling `urllib.parse.unquote` on it. This converts any percent-encoded characters in the path (e.g., `%20`) back to their original Unicode representation. No additional transformation or validation is applied.

**Parameters:**
- `file_path`

### show_image(file_path)

*No description available.*
Opens a modal image viewer dialog for the specified file path. It instantiates an `ImageViewer` dialog parented to the current widget, calls its `show_image` method with the provided `file_path`, and then executes the dialog modally via `exec()`.

**Parameters:**
- `file_path` *(str)*: The path to the image file to be displayed.

**Parameters:**
- `file_path`

### show_video(file_path)

*No description available.*
Displays a video file in a `VideoPlayerWindow` instance. If no video player window has been created yet, one is instantiated with the current object as parent, along with references to `self.DB_MANAGER`, `self.iconListWidget`, and `self` as the main class. The specified file is then loaded into the player via `set_video` and the window is made visible.

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

Resolves the full file path for a given media file by detecting whether `file_path` is already an absolute or protocol-prefixed path, combining it with `thumb_resize_str` if necessary, or joining it as a local filesystem path. Once the full path is determined, dispatches to `show_video` or `show_image` based on the provided `media_type` argument. If `media_type` is neither `'video'` nor `'image'`, displays a warning dialog indicating an unsupported media type.

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

*No description available.*
Queries the database for media records matching the criteria specified in `search_dict`, targeting the table identified by `table` (defaulting to `"MEDIA_THUMB"`). Before executing the query, empty items are removed from `search_dict` using `Utility.remove_empty_items_fr_dict`. Returns the result of `DB_MANAGER.query_bool`, or `None` if an exception occurs, in which case a warning dialog is displayed with the error message.

**Parameters:**
- `search_dict`
- `table`

