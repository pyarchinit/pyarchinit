# tabs/Struttura.py

## Overview

This file contains 127 documented elements.

## Classes

### pyarchinit_Struttura

`pyarchinit_Struttura` is a QDialog subclass that implements the Structure (Struttura) data entry and management form for the PyArchInit QGIS plugin. It provides a full CRUD interface for archaeological structure records stored in `struttura_table`, supporting browsing, searching, sorting, inserting, updating, and deleting records. The class also handles multilingual UI labels and field mappings across Italian, English, German, French, Spanish, Portuguese, Arabic, Catalan, Romanian, Greek, and other locales, and integrates media management (images, video, 3D models), map preview via QGIS layers, and PDF export of structure sheets and indexes.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the form widget by setting up the UI, applying the current theme, and adding a theme toggle button. Establishes a database connection via `on_pushButton_connect_pressed` (with error handling via `QMessageBox`), configures drag-and-drop support on `iconListWidget`, and initializes an `OrderedDict`-based image cache with a limit of 100 entries. Connects various combo box signals to their respective slot methods for site, period, and phase list population, then finalizes setup by calling `customize_GUI`, `set_sito`, `msg_sito`, the initial period/phase list loaders, and `init_remote_loader`.

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

##### loadMapPreview(self, mode)

Loads or clears a map preview in the `mapPreview` canvas based on the specified `mode` parameter. When `mode` is `0`, it constructs a filter expression using the current record's ID, retrieves the corresponding map layers via `self.pyQGIS.loadMapPreview`, sets them on the canvas, and zooms to the full extent. When `mode` is `1`, it clears all layers from the canvas and resets the zoom to the full extent.

##### dropEvent(self, event)

*No description available.*
Handles drop events by extracting file URLs from the event's MIME data and validating each dropped file against a predefined list of accepted formats, which includes common image formats (`jpg`, `jpeg`, `png`, `tiff`, `tif`, `bmp`), video formats (`mp4`, `avi`, `mov`, `mkv`, `flv`), and 3D model formats (`obj`, `stl`, `ply`, `fbx`, `3ds`). If a dropped file matches an accepted format, it is passed to `load_and_process_image`; otherwise, a warning dialog is displayed indicating the unsupported file type. Any exception raised during file processing is caught and reported via a `QMessageBox` warning, after which the base class `dropEvent` is called.

##### dragEnterEvent(self, event)

*No description available.*
Handles the drag-enter event by inspecting the MIME data of the incoming drag action. If the event's MIME data contains URLs, the proposed action is accepted; otherwise, the event is ignored. This method controls whether a drag operation is permitted to proceed over the widget.

##### dragMoveEvent(self, event)

*No description available.*
Handles the drag move event that is triggered as a dragged object is moved over the widget. Unconditionally accepts the proposed drop action by calling `event.acceptProposedAction()`, allowing the drag operation to continue without restriction. This method overrides the default drag move behavior to ensure the drop target remains active throughout the drag interaction.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database by assigning the next available ID and constructing a media entry with the provided type, filename, file type, and file path, along with a default description of `'Insert description'` and a default tag of `"['imagine']"`. The method delegates record construction to `DB_MANAGER.insert_media_values()` and persists the result via `DB_MANAGER.insert_data_session()`. Returns `1` on successful insertion, or `0` on failure; integrity constraint violations (e.g., duplicate entries) are handled silently with a descriptive message, while other construction-level exceptions display a warning dialog.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
Inserts a media thumbnail record into the `MEDIA_THUMB` database table by assigning the provided metadata to instance attributes and invoking `DB_MANAGER.insert_mediathumb_values` with an auto-incremented primary key. The method passes the media ID, media type, filename, thumbnail filename, file type, thumbnail filepath, and resized filepath as string-converted values to the database session via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if the operation fails — silently suppressing integrity constraint violations (such as duplicate thumbnail entries) and displaying a warning dialog for all other exceptions.

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
Queries the database for a `STRUTTURA` record matching the currently selected site (`sito`), structure abbreviation (`sigla_struttura`), and structure number (`numero_struttura`) retrieved from the corresponding UI controls. The query is executed via `DB_MANAGER.query_bool` using a dictionary of search criteria against the `'STRUTTURA'` table. Returns a list of tuples, each containing the record's `id_struttura`, the string `'STRUTTURA'`, and the string `'struttura_table'`.

##### assignTags_US(self, item)

*No description available.*
Assigns media tags to a list of US (Unità Stratigrafica) entities by linking a given media item to each entry returned by `generate_US()`. For each US record, the method queries the database for the media file matching the original filename of the provided `item`, then calls `insert_mediaToEntity_rec` with the US identifier, type, table name, and the resolved media record's ID, filepath, and filename. If `generate_US()` returns an empty list, the method exits without performing any operations.

##### load_and_process_image(self, filepath)

*No description available.*
Loads a media file from the given `filepath`, determines its type (image, video, or 3D model) based on the file extension, and processes it for storage. If the configured thumbnail path is unset, the method displays a localised informational message and aborts; otherwise, it checks for a duplicate database entry by filepath and, if none exists, inserts a new media record, generates thumbnail and resized variants using the appropriate utility classes, and optionally uploads the original file to a configured remote storage backend. Upon successful processing, a new item representing the media is added to `self.iconListWidget` and tags are assigned via `self.assignTags_US`.

##### db_search_check(self, table_class, field, value)

*No description available.*
Performs a boolean database query to check for records matching a specified field-value pair within a given table class. It constructs a search dictionary from the provided `field` and `value`, removes any empty entries using a `Utility` helper, and delegates the query to `self.DB_MANAGER.query_bool`. Returns the result of the query.

##### on_pushButton_assigntags_pressed(self)

Handles the press event of the `pushButton_assigntags` button by validating that one or more items are selected in `iconListWidget`, displaying a locale-aware warning message (`it`, `de`, or default English) if no items are selected. Queries all `STRUTTURA` records from the database, sorts them by `sito`, `area`, and `us`, and populates a new `QListWidget` with the sorted records formatted as `"{sito} - {sigla_struttura} - {numero_struttura}"`. Presents the list in a standalone `QWidget` with a locale-aware "Done" button connected to `on_done_selecting`, allowing the user to select multiple records for tag assignment.

##### on_done_selecting(self)

*No description available.*
Handles the "Done" button click event by first determining the active locale via `QgsSettings` and setting locale-appropriate UI strings for Italian, German, or English. If no items are selected in `us_listwidget`, a warning message box is displayed; otherwise, it resolves the selected US records by querying the database through `DB_MANAGER` and associates each selected media item from `iconListWidget` to the corresponding `STRUTTURA` entity via `insert_mediaToEntity_rec`. Once processing is complete, the widget is closed.

##### on_pushButton_search_images_pressed(self)

Open the Image Search dialog with pre-filled filters for current Struttura record.

##### on_pushButton_removetags_pressed(self)

*No description available.*
Slot triggered when the "remove tags" button is pressed. It first checks whether any items are selected in `iconListWidget`; if none are selected, it displays a language-appropriate warning message requiring the user to select an image first. If items are selected, it prompts the user with a confirmation dialog (supporting Italian, German, and English based on `self.L`), and upon confirmation, removes the database tags associated with each selected thumbnail by calling `self.DB_MANAGER.remove_tags_from_db_sql_scheda` with the current structure's record ID and the item's filename, then removes each processed item from `iconListWidget`.

##### load_and_process_3d_model(self, filepath)

*No description available.*
Loads a 3D model from the specified file path and registers it in the database by inserting a media record with the derived filename, file type, and media type `'3d_model'`. Generates a thumbnail image for the model, inserts a corresponding thumbnail record linked to the media entry's maximum ID, and adds the model as an icon-bearing item to `iconListWidget`. Finally, assigns tags to the newly created list item via `assignTags_US`.

##### show_3d_model(self, file_path)

Loads and renders a 3D mesh file specified by `file_path` using PyVista, constructing an interactive Qt-based widget that embeds a `QtInteractor` plotter within a horizontal layout. If a JPEG texture file with the same base name exists alongside the mesh file, it is applied to the mesh; otherwise the mesh is rendered without texture. The method provides interactive keyboard shortcuts for toggling point-to-point distance measurement, displaying bounding box dimensions, exporting a 300 DPI screenshot, clearing measurements, resetting the camera, and switching between predefined orthographic views, then returns the assembled `QWidget`.

##### generate_3d_thumbnail(self, filepath)

Generates a thumbnail image for a 3D model file by reading the mesh from the specified filepath using PyVista, rendering it off-screen with the camera positioned in the XY plane, and saving the result as a PNG file. The thumbnail filename is derived from the original file's base name with a `_thumb.png` suffix, and the file is saved to the directory specified by `self.thumb_path`. Returns the full path to the generated thumbnail file.

##### process_3d_model(self, media_max_num_id, filepath, filename, thumb_path_str, thumb_resize_str, media_thumb_suffix, media_resize_suffix)

*No description available.*
Processes a 3D model file by generating a 2D thumbnail screenshot and preparing a resized copy of the original file. Using PyVista, it loads the mesh from `filepath`, renders an off-screen XY-plane view, and saves the screenshot to the thumbnail directory using the constructed filename derived from `media_max_num_id`, `filename`, and `media_thumb_suffix`. The original 3D model file is copied (not resized) to the resize directory, and if a JPEG texture file sharing the same base name exists in the source directory, it is also copied to the resize directory. Returns a tuple of `(thumbnail_path, resize_path)`.

##### openWide_image(self)

Opens and displays the full-resolution media file associated with each selected item in `iconListWidget`. For each selected item, the method queries the `MEDIA_THUMB` database table to retrieve the file path and media type, then resolves the full path by combining it with the configured thumbnail resize base path, handling both local filesystem paths and remote URL protocols (`unibo://`, `http://`, `https://`, `cloudinary://`). Depending on the resolved media type, the file is displayed in an `ImageViewer` dialog, a `VideoPlayerWindow`, or a `QDialog`-wrapped 3D model viewer; if no matching record is found, a warning message is shown.

##### on_pushButton_print_pressed(self)

*No description available.*
Handles the print button press event by generating and exporting PDF documents for Structure records based on the active UI language (`self.L`) and the state of the `checkBox_s_us` and `checkBox_e_us` checkboxes. When `checkBox_s_us` is checked, it instantiates `generate_struttura_AR_pdf`, builds the data list via `generate_list_pdf_ar()`, and calls the appropriate language-specific AR sheet builder method; when `checkBox_e_us` is checked (supported for Italian and English only), it instantiates `generate_struttura_pdf`, builds the data list via `generate_list_pdf()`, and exports a Structure index PDF. A `QMessageBox` confirmation or warning dialog is displayed upon completion or failure of each export operation.

##### openpdfDir(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path using the appropriate system command for the current operating system. On Windows, it uses `os.startfile`; on macOS (`Darwin`), it invokes `open` via `subprocess.Popen`; on all other systems, it uses `xdg-open` via `subprocess.Popen`.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path. The method detects the current operating system and uses the appropriate system call to launch the directory in the native file manager: `os.startfile` on Windows, `open` on macOS (Darwin), or `xdg-open` on Linux and other platforms.

##### setPathpdf(self)

Opens a file dialog allowing the user to select a PDF file, using `self.PDFFOLDER` as the initial directory and filtering for `.pdf` files. If a valid file path is selected, it updates `self.lineEdit_pdf_path` with the chosen path and stores the value in `QgsSettings`. The settings key used in `s.setValue` is an empty string, as shown in the source.

##### enable_button(self, n)

*No description available.*
Enables or disables a set of UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. Typically called with a boolean value to collectively control the interactive state of the main navigation and action controls.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons simultaneously by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_connect`, `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. This method is typically used to enable or disable the main toolbar controls as a group, depending on the current application state.

##### on_pushButton_connect_pressed(self)

Handles the press event of the connect button by establishing a database connection using a `Connection` object and initialising the database manager via `get_db_manager`. If the connection targets an SQLite database, `DB_SERVER` is set accordingly; the database username is retrieved and, if a `concurrency_manager` is present, assigned to it. Upon a successful connection, records are loaded from the database and the UI is updated to reflect the current browse state, or a localised welcome message is displayed if the database is empty; any exception triggers a localised warning message pushed to the QGIS message bar.

##### customize_GUI(self)

Initializes and configures all GUI components for the structure (*struttura*) form after resolving the current QGIS user locale. It sets up `iconListWidget` display properties and drag-and-drop behavior, applies fixed column widths to all table widgets (`tableWidget_rapporti`, `tableWidget_materiali_impiegati`, `tableWidget_elementi_strutturali`, `tableWidget_misurazioni`, and others), and assigns `ComboBoxDelegate` instances—populated from thesaurus queries against `PYARCHINIT_THESAURUS_SIGLE` and from locale-aware relationship term dictionaries—to the appropriate columns of each table widget. It also makes several combo boxes editable, updates media button visibility, and connects all table widget row-insertion and row-removal push buttons to their respective slot methods.

##### charge_list(self)

Populates all combo boxes in the form with data retrieved from the database and predefined value lists. Site values are fetched from `site_table` via `DB_MANAGER.group_by`, while structure-related fields (`sigla_struttura`, `categoria_struttura`, `tipologia_struttura`, `definizione_struttura`, and `sviluppo_planimetrico`) are queried from the `PYARCHINIT_THESAURUS_SIGLE` table filtered by language and typology codes (`6.1`–`6.4`, `6.15`). Orientation, articulation, and archaeological potential combo boxes are populated with hardcoded value lists, and a `ComboBoxDelegate` is applied to column 1 of `tableWidget_rapporti` using the site values.

##### msg_sito(self)

Displays a localized informational message box indicating the currently connected archaeological site, retrieved via the `Connection` class. If the current site selection matches the configured site, it notifies the user of the active connection in Italian, German, or English depending on `self.L`. If no site has been configured (`sito_set_str` is empty), it prompts the user to set one, and if the user confirms, opens the `pyArchInitDialog_Config` dialog to configure a site.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting via a `Connection` object and, if a site is set, queries the database for all records matching that site using `query_bool`. If matching records are found, the method populates `DATA_LIST`, initialises the record counter, fills the form fields, sets the browse status, and disables the site combo box; if no records are found, it displays a localised informational message (Italian, German, or English) and returns early. Any exception raised during the process is caught and reported to the user via a localised warning dialog.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### tableInsertData(self, t, d)

Set the value into table widget

##### table2dict(self, n)

Convert a QTableWidget to a list of lists

##### empty_fields_nosite(self)

Clear all fields except sito

##### empty_fields(self)

Clear all fields including sito

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` in `DATA_LIST`, setting `rec_num` to the specified index and clearing the media widget before loading. Core fields such as site, structure identifiers, category, typology, description, interpretation, dating, and associated table data (materials, structural elements, relationships, measurements) are always populated, while optional fields (e.g., `data_compilazione`, `nome_compilatore`, `stato_conservazione`, and various AR-specific attributes) are conditionally set only when present and non-null on the record. After populating fields, the method conditionally triggers a map preview and loads media either automatically for local paths or on demand for remote paths.

##### set_rec_counter(self, t, c)

Sets the total and current record counters for the component.

Assigns the provided values `t` and `c` to the instance attributes `rec_tot` and `rec_corr` respectively, then updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects and assembles the current values from all form widgets into a temporary record list stored in `self.DATA_LIST_REC_TEMP`, following the order defined by `TABLE_FIELDS`. Period-related values (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`) are read from their respective combo boxes and set to `None` if the combo box contains no selection. Table widget contents are serialized to dictionary representations via `self.table2dict`, while all other field values are read directly from their corresponding UI controls as strings.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by iterating over `TABLE_FIELDS` and retrieving the corresponding attribute values from the current record in `DATA_LIST`, identified by the `REC_CORR` index. Each retrieved attribute value is converted to a string and appended to the `DATA_LIST_REC_CORR` list, which is reset to an empty list at the start of each call. This method is used in conjunction with `set_LIST_REC_TEMP` within `records_equal_check` to facilitate comparison between record states.

##### records_equal_check(self)

*No description available.*
Compares the current record's data against a temporary working copy by invoking `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate their respective data lists. Returns `0` if `DATA_LIST_REC_CORR` and `DATA_LIST_REC_TEMP` are equal, or `1` if they differ.

##### charge_periodo_iniz_list(self)

*No description available.*
Populates the `comboBox_per_iniz` combo box with a deduplicated list of initial period values retrieved from the `PERIODIZZAZIONE` table, filtered by the currently selected site in `comboBox_sito`. After clearing and reloading the combo box items, it sets the editable text based on the current browse status: clears the field when the status is `"Trova"`/`"Find"`, or attempts to populate it with the `periodo_iniziale` value of the current record in `DATA_LIST` when the status is `"Usa"`/`"Current"`.

##### charge_periodo_fin_list(self)

*No description available.*
Queries the `PERIODIZZAZIONE` database table for all period records associated with the currently selected site (`comboBox_sito`), then populates the `comboBox_per_fin` combo box with a deduplicated list of the retrieved period values. After loading the items, it sets the combo box edit text based on the current browse status: clearing it when the status corresponds to "Trova"/"Find", or attempting to populate it with the current record's `periodo_iniziale` value when the status corresponds to "Usa"/"Current".

##### charge_fase_iniz_list(self)

*No description available.*
Queries the database for phase (`fase`) records matching the currently selected site (`comboBox_sito`) and initial period (`comboBox_per_iniz`) by building a search dictionary and calling `DB_MANAGER.query_bool` against the `PERIODIZZAZIONE` table. The retrieved phase values are deduplicated, sorted, and loaded into the `comboBox_fas_iniz` combo box after clearing its previous contents and removing any empty string entries. If the current browse status corresponds to a search/find mode, the combo box edit text is cleared; otherwise, it is set to the initial phase value of the current record.

##### charge_fase_fin_list(self)

*No description available.*
Queries the database for phase (`fase`) records matching the currently selected site (`comboBox_sito`) and ending period (`comboBox_per_fin`) by building a search dictionary and calling `DB_MANAGER.query_bool` against the `PERIODIZZAZIONE` table. The retrieved phase values are collected into a list, deduplicated, sorted, and loaded into the `comboBox_fas_fin` combo box after clearing its previous contents. If the current browse status corresponds to "Trova" or "Find", the combo box edit text is cleared; otherwise, it is set to the final phase value of the current record.

##### charge_datazione_list(self)

*No description available.*
Populates the `comboBox_datazione_estesa` combo box with a sorted, deduplicated list of extended dating values (`datazione_estesa`) retrieved from the `PERIODIZZAZIONE` table. The query is filtered by the current values of `comboBox_sito`, `comboBox_per_iniz`, and `comboBox_fas_iniz`, and empty string entries are removed from the results before display. Depending on the current browse status, the combo box edit text is either cleared or set to the `datazione_estesa` value of the current record; all exceptions are silently suppressed.

##### insert_row_stato(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_stato_conservazione` by inserting it at the index equal to the current row count. This method serves as a handler for the add-row button associated with the conservation status table widget. It is intentionally named without the `on_` prefix to prevent automatic signal-slot connection by Qt.

##### remove_row_stato(self)

Removes the currently selected row from the `tableWidget_stato_conservazione` table widget. The method retrieves the index of the current row and performs the removal only if a valid row is selected (index greater than or equal to zero). If no row is selected, the method takes no action.

##### insert_row_prospetto(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_prospetto_ingresso` by inserting it at the index equal to the current row count. This effectively increments the table's row count by one each time it is called.

##### remove_row_prospetto(self)

*No description available.*
Removes the currently selected row from `tableWidget_prospetto_ingresso`. The method first retrieves the index of the current row and proceeds with removal only if a valid row is selected (index greater than or equal to zero). If no row is selected, no action is taken.

##### insert_row_elementi_cost(self)

*No description available.*
Inserts a new empty row at the end of `tableWidget_elementi_costitutivi` by appending it after the last existing row. The insertion position is determined by the current row count of the table, ensuring the new row is always added at the bottom. This method takes no parameters and returns no value.

##### remove_row_elementi_cost(self)

Removes the currently selected row from the `tableWidget_elementi_costitutivi` table widget. The method retrieves the index of the current row and performs the removal only if a valid row is selected (index greater than or equal to zero). If no row is selected, no action is taken.

##### insert_row_manufatti(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_manufatti` by inserting it at the current row count. The new row index is determined by calling `rowCount()` on the table widget, ensuring the row is always added after the last existing entry.

##### remove_row_manufatti(self)

*No description available.*
Removes the currently selected row from `tableWidget_manufatti`. The method first retrieves the index of the current row and proceeds with removal only if a valid row is selected (index greater than or equal to zero). If no row is selected, no action is taken.

##### insert_row_fasi(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_fasi_funzionali` by inserting it at the index equal to the current row count. This effectively increments the table's row count by one each time it is called.

##### remove_row_fasi(self)

*No description available.*
Removes the currently selected row from `tableWidget_fasi_funzionali`. The method first retrieves the index of the current row and performs the removal only if a valid row is selected (i.e., the row index is greater than or equal to zero). If no row is selected, no action is taken.

##### insert_row_rapporti(self)

*No description available.*
Inserts a new empty row at the end of `tableWidget_rapporti` by appending it after the last existing row. The new row position is determined by the current row count of the widget, ensuring the row is always added at the bottom of the table.

##### remove_row_rapporti(self)

Removes the currently selected row from `tableWidget_rapporti`. The method retrieves the index of the current row and removes it only if a valid row is selected (i.e., the index is greater than or equal to zero). No action is taken if no row is currently selected.

##### insert_row_materiali(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_materiali_impiegati` by inserting it at the index equal to the current row count. This effectively increments the table's row count by one each time it is called.

##### remove_row_materiali(self)

*No description available.*
Removes the currently selected row from the `tableWidget_materiali_impiegati` table widget. The method first retrieves the index of the current row and only proceeds with the removal if a valid row is selected (index greater than or equal to zero). If no row is selected, no action is taken.

##### insert_row_elementi(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_elementi_strutturali` by inserting it at the index equal to the current row count. This effectively increments the table's row count by one each time it is called.

##### remove_row_elementi(self)

*No description available.*
Removes the currently selected row from `tableWidget_elementi_strutturali`. The method first retrieves the index of the current row and only proceeds with removal if a valid row is selected (i.e., the row index is greater than or equal to zero).

##### insert_row_misurazioni(self)

*No description available.*
Appends a new empty row at the end of `tableWidget_misurazioni` by inserting it at the current row count index. This effectively increments the table's row count by one each time it is called.

##### remove_row_misurazioni(self)

Removes the currently selected row from `tableWidget_misurazioni`. The method retrieves the index of the current row and removes it only if a valid row is selected (i.e., the row index is greater than or equal to zero). No action is taken if no row is currently selected.

##### insert_row_orient_amb(self)

*No description available.*
Inserts a new empty row at the end of `tableWidget_orientamento_ambienti` by appending it at the current row count. The new row is added using `insertRow` with `rowCount()` as the target index, effectively placing it after all existing rows.

##### remove_row_orient_amb(self)

*No description available.*
Removes the currently selected row from `tableWidget_orientamento_ambienti`. The method first retrieves the index of the current row and proceeds with removal only if the returned index is greater than or equal to zero, ensuring no action is taken when no row is selected.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available `SORT_ITEMS`, allowing the user to select sort fields and order type. If the record state check passes, the selected items are converted using `CONVERSION_DICT` and passed to `DB_MANAGER.query_sort` to retrieve a reordered version of the current `DATA_LIST`. The method then resets the browse status, updates the record counter and sort label, and refreshes the displayed fields to reflect the newly sorted data.

##### add_value_to_categoria(self)

*No description available.*
Checks whether the current text of `comboBox_sigla_struttura` is an empty string. If the combo box contains no value, it calls `setComboBoxEditable` with the combo box reference and the value `1`, enabling user input on that widget.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the press event of the "new record" button by preparing the GUI to accept a new record entry. It first performs a data error check on the existing data list, then transitions the browse status to `"n"` (new), clears the relevant fields, and resets sort and status labels. Depending on whether the current site (`comboBox_sito`) matches the configured site set, it either preserves the site selection and restricts its editability or fully clears all fields and enables free site entry; in both cases, it reloads the initial and final period lists and disables the action buttons via `enable_button(0)`.

##### on_pushButton_save_pressed(self)

*No description available.*
Slot triggered when the save button is pressed, handling both record update and new record insertion depending on the current browse status (`BROWSE_STATUS`). In browse mode (`"b"`), it validates the data via `data_error_check()`, checks for modifications via `records_equal_check()`, and if changes are detected, prompts the user with a localized confirmation dialog before calling `update_if()` to persist the changes; if no changes are detected, a localized warning is displayed. Outside browse mode, it validates the data and attempts to insert a new record via `insert_new_rec()`, updating the UI state, record counters, combo box configurations, and field contents upon success, or displaying a localized error message on failure. Localized messages are displayed in Italian, German, or English based on the value of `self.L`.

##### data_error_check(self)

*No description available.*
Validates the required form fields — site (`comboBox_sito`), structure code (`comboBox_sigla_struttura`), and structure number (`numero_struttura`) — by delegating emptiness and integer-type checks to an `Error_check` instance. If any validation fails, a localized `QMessageBox` warning is displayed according to the active language (`self.L`), which supports Italian (`'it'`), German (`'de'`), and a default English fallback. Returns `0` if all checks pass, or `1` if one or more validation errors are detected.

##### insert_new_rec(self)

*No description available.*
Collects and validates all form field values — including table widget data (materials, structural elements, relationships, measurements, conservation state, and functional phases), combo box selections, date fields, and numeric inputs — then constructs a new structure record by calling `self.DB_MANAGER.insert_struttura_values` with a newly assigned ID and all 35 mapped field values. The assembled record is persisted to the database via `self.DB_MANAGER.insert_data_session`. Returns `1` on success; returns `0` on failure, displaying a localized warning dialog that distinguishes between integrity constraint violations (duplicate record) and other exceptions.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data entry error check via `data_error_check()`. If a data entry error is detected, the method returns `1` immediately; if no error is found but the record has been modified (as determined by `records_equal_check()`), it prompts the user with a localized warning dialog (Italian, German, or English depending on `self.L`) asking whether to save the changes, delegating the save decision to `update_if()`. Returns `1` if there are data entry errors, or `0` if the record is unmodified or the user has been prompted to handle unsaved changes.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the "View All" button press event by loading and displaying the complete set of records. If `check_record_state()` indicates a pending state (returns `1`), the action is suppressed; otherwise, the method clears current fields, reloads all records via `charge_records()`, and repopulates the display with `fill_fields()`. It then sets the browse status to `"b"`, resets the record counters to reflect the full dataset, positions the cursor at the first record, and updates the sort label to the unsorted state.

##### on_pushButton_first_rec_pressed(self)

Navigates to the first record in the current data list. If the record state check does not return `1`, it clears the existing fields, resets the record counters so that `REC_CORR` is set to `0` and `REC_TOT` reflects the total number of items in `DATA_LIST`, then populates the fields with the first entry (index `0`) and updates the record counter display accordingly. Any exception raised during this process is caught and presented to the user via a `QMessageBox` warning dialog.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during the process is caught and displayed as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one and navigating to the preceding record. If the index reaches `-1`, it is reset to `0` and a localized warning message is displayed (Italian, German, or English) to inform the user that the first record has already been reached. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter display is updated via `set_rec_counter()`. If the record state check returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Handles the "Next Record" button press event by advancing the current record index (`REC_CORR`) by one. If the incremented index reaches or exceeds the total record count (`REC_TOT`), it reverts the index and displays a localized warning message indicating the user is already at the last record (supporting Italian, German, and a default English message). Otherwise, it clears the current form fields, populates them with the next record's data, and updates the record counter display.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently removing the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. Upon confirmed deletion, the method reloads the record list from the database and either resets all data structures and UI fields if the database is empty, or navigates to the first record and refreshes the display if records remain. Any exception raised during deletion is caught and reported to the user via a warning message box.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the "New Search" button press event by transitioning the form to search mode (`BROWSE_STATUS = "f"`), provided the current record state check does not return `1`. Depending on whether the current site (`comboBox_sito`) matches the configured site set retrieved via `Connection`, the method either locks the site combo box and clears only non-site fields (`empty_fields_nosite`), or enables all search-related combo boxes and clears all fields (`empty_fields`) along with reloading the combo box list via `charge_list`. In both cases, search-irrelevant controls (description text edits, interpretation text edits, and associated table widgets) are disabled, the status label and sort label are reset, and the record counter is cleared.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search execution triggered by the "search go" button. If the current browse status is not in search mode (`"f"`), a localized warning message is displayed instructing the user to initiate a new search first; otherwise, it collects and converts field values (structure number, site, abbreviation, category, typology, definition, initial/final period and phase, and extended dating) into a search dictionary, removes empty entries via `Utility.remove_empty_items_fr_dict`, and executes a boolean query against the database through `DB_MANAGER.query_bool`. On a successful query result, `DATA_LIST` is populated with the returned records, the UI is transitioned to browse status (`"b"`), relevant fields and tables are enabled or disabled accordingly, and a localized summary message reports the number of records found; if `toolButton_draw_strutture` is checked, the results are also passed to `pyQGIS.charge_structure_from_research`. The method concludes by re-enabling the search button via `enable_button_search(1)`.

##### on_pushButton_pdf_exp_pressed(self)

Show export dialog

##### do_pdf_export(self, dialog)

Execute PDF export based on dialog selections

##### generate_list_pdf(self)

Iterates over all records in `self.DATA_LIST`, querying the database for associated stratigraphic units (US) and their elevation data (quote) for each structure. For each record, it determines the minimum and maximum elevation values, falling back to a localized "not inserted in GIS" string (in Italian, German, or English based on `self.L`) when no elevation data is found. Returns a list of lists, where each inner list contains nineteen fields per structure record — including site, structure code, category, typology, definition, description, interpretation, chronological phases, extended dating, materials, structural elements, relationships, measurements, and the computed minimum and maximum elevations — suitable for PDF generation.

##### generate_list_pdf_ar(self)

Generate data list with all AR (Architettura Rupestre) fields for PDF export

##### on_toolButton_draw_strutture_toggled(self)

*No description available.*
Handles the toggle state change of the `toolButton_draw_strutture` button by displaying a localized notification message to the user. When the button is checked, a warning dialog informs the user that GIS mode has been activated and search results will be displayed on the GIS; when unchecked, a corresponding dialog notifies the user that GIS mode has been deactivated. The displayed message language is determined by `self.L`, supporting Italian (`'it'`), German (`'de'`), and a default English fallback.

##### on_pushButton_draw_struttura_pressed(self)

*No description available.*
Handles the press event of the `pushButton_draw_struttura` button. Retrieves the current record from `DATA_LIST` using the `REC_CORR` index, wraps it in a single-element list, and passes it to `self.pyQGIS.charge_structure_from_research` to render the corresponding structure on the GIS layer.

##### on_pushButton_view_all_st_pressed(self)

*No description available.*
Handles the press event of the "view all structures" button by retrieving the active site filter from the connection settings and querying the database for all structure records matching that site. For each record returned, it extracts the site name, structure abbreviation, and structure number, then calls `self.pyQGIS.charge_vector_layers_all_st` to load the corresponding vector layers. Any exceptions raised during the process are silently suppressed.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, it calls `update_record()` and, on success, refreshes `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Upon a successful update, the browse status is set to `"b"` and the method returns `1`; if the update fails, it returns `0`.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the current mapper table and populates `self.DATA_LIST` with the results. The query is executed in ascending order based on `self.ID_TABLE` using a single ordered query via `self.DB_MANAGER.query_ordered`, replacing a previously used double-query pattern for improved performance.

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### rec_toupdate(self)

*No description available.*
Returns the result of calling `pos_none_in_list` on `self.DATA_LIST_REC_TEMP` via the `self.UTILITY` helper. The method delegates the processing of the temporary record data list to `UTILITY.pos_none_in_list`, which identifies positions of `None` values within that list. The resulting value is returned directly to the caller, typically for use in a subsequent update operation.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `DB_MANAGER.update` with the mapped table class, table ID, current record identifier, table fields, and the prepared update values returned by `rec_toupdate()`. Returns `1` on success, or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default).

## Functions

### r_list()

*No description available.*
Retrieves database records corresponding to the US items currently selected in `us_listwidget` by parsing each selected item's text into site (`sito`), structure code (`sigla_struttura`), and structure number (`numero_struttura`) components. For each parsed entry, it performs a boolean query against the `STRUTTURA` table via `DB_MANAGER` and collects the results. Returns a list of tuples containing the `id_struttura`, the string `'STRUTTURA'`, and the string `'struttura_table'` for each matched record.

### r_id()

*No description available.*
An inner function defined within `on_pushButton_removetags_pressed` that retrieves the database ID of a `STRUTTURA` record matching the currently selected site (`sito`), structure abbreviation (`sigla_struttura`), and structure number (`numero_struttura`) from the UI form fields. It constructs a search dictionary from these three field values, queries the database via `DB_MANAGER.query_bool`, and returns the `id_us` attribute of the first matching record. The returned value is used by the enclosing method to identify the target record for subsequent tag removal operations.

### add_debug_message(message, important)

*No description available.*
Appends a timestamped message to a read-only `QTextEdit` debug widget, prefixing it with the current date and time in `yyyy-MM-dd HH:mm:ss` format. If `important` is `True`, the formatted message is wrapped in `<b>` tags to render it in bold. The widget is capped at 1,000 message blocks; when this limit is exceeded, the oldest line is removed to maintain the maximum count.

**Parameters:**
- `message`
- `important`

### mouse_click_callback(obj, event)

*No description available.*
A VTK interactor observer callback that handles left mouse button press events during an active measuring session. When a `LeftButtonPressEvent` is received and `measuring` is `True`, it retrieves the screen coordinates from the plotter's interactor, uses a `vtkCellPicker` to resolve the 2D screen position to a 3D point on the rendered geometry, then finds the closest point on the mesh surface and forwards it to `on_left_click`. If no surface point is found by the picker (i.e., `GetCellId()` returns `-1`), a debug message is logged indicating the failure.

**Parameters:**
- `obj`
- `event`

### toggle_instructions()

*No description available.*
Toggles the visibility of the `instructions_widget` by showing it if it is currently hidden, or hiding it if it is currently visible. This function is connected to the `clicked` signal of the "Toggle Instructions" `QPushButton`, allowing the user to control the display of the instructions text on demand.

### toggle_measure()

Toggles the active measurement state by inverting the boolean value of the `measuring` flag and clearing the `points` collection. When measurement is activated, a debug message `"Misurazione iniziata"` is logged as important; when deactivated, `"Misurazione terminata"` is logged instead. Both `measuring` and `points` are accessed via `nonlocal` binding from the enclosing scope.

### on_left_click(picked_point)

*No description available.*
Handles a left-click event during an active measurement session by recording the selected 3D point. If `measuring` is active and `picked_point` is not `None`, the point is appended to the `points` list and a red sphere marker — sized relative to the mesh length — is added to the plotter at that location. Once exactly two points have been collected, `measure_distance` is called with both points and the `points` list is cleared; if no valid point was picked, a debug message is logged instead.

**Parameters:**
- `picked_point`

### verify_coordinates(coord1, coord2)

*No description available.*
Logs the provided coordinate pair for diagnostic purposes by emitting a debug message containing the values of both points. The message is marked as important, ensuring it is highlighted within the debug output. This function does not return a value or perform any validation beyond the debug trace.

**Parameters:**
- `coord1`
- `coord2`

### measure_distance(point1, point2)

*No description available.*
Computes the Euclidean distance between two 3D points using `numpy.linalg.norm` and visualizes the measurement in the active `plotter`. A red line is drawn between the two points, "P1" and "P2" labels are added at each endpoint, and a distance label formatted to two decimal places (in centimetres) is placed at the midpoint; all three visual actors are appended to `measurement_objects`. The plotter is then re-rendered and the measured distance is logged via `add_debug_message`.

**Parameters:**
- `point1`
- `point2`

### clear_measurements()

*No description available.*
Removes all active measurement actors from the plotter by iterating over `measurement_objects` and calling `plotter.remove_actor()` on each one. After removal, both the `measurement_objects` and `points` collections are cleared. The plotter is then re-rendered to reflect the updated state.

### export_image()

*No description available.*
Opens a save file dialog prompting the user to specify a destination path for a PNG image. If a path is selected, captures a screenshot of the current plotter view at a fixed resolution of 300 DPI with dimensions of 15×10 cm (1772×1181 pixels), preserving and restoring the camera position after capture. On success, displays an informational message box; on failure, logs the error via `add_debug_message` and displays a warning dialog.

### get_visible_faces(plotter, mesh)

*No description available.*
Determines which faces of an axis-aligned box mesh are visible from the current camera position. It computes the direction vector from the mesh center to the camera, then tests each of the six cardinal face normals (`±X`, `±Y`, `±Z`) against that direction using a dot product. Returns a list of face indices (0–5) for which the dot product with the camera direction is positive, indicating the face is oriented toward the camera.

**Parameters:**
- `plotter`
- `mesh`

### edge_visibility(edge, visible_faces)

*No description available.*
Determines whether a given edge of a cuboid is visible based on the set of currently visible faces. The function uses a hardcoded mapping (`edge_to_faces`) that associates each edge, identified by a tuple of two vertex indices, with the list of face indices it borders. Returns `True` if at least one of the edge's adjacent faces is present in `visible_faces`, otherwise returns `False`.

**Parameters:**
- `edge`
- `visible_faces`

### calculate_label_position(p1, p2, offset_factor)

Computes the 3D position for a label to be placed alongside a line segment defined by two endpoints `p1` and `p2`. The position is calculated by finding the midpoint of the segment, then offsetting it along a perpendicular direction by a distance proportional to the segment length scaled by `offset_factor` (default `0.1`). If the perpendicular vector computed via cross product with `[0, 0, 1]` is degenerate, a fallback cross product with `[0, 1, 0]` is used instead.

**Parameters:**
- `p1`
- `p2`
- `offset_factor`

### create_oriented_label(plotter, position, text, direction, is_vertical)

*No description available.*
Creates and adds a billboard text label to a VTK plotter at a specified 3D position, rendered with a white semi-transparent background and black text at font size 6. The label is oriented in 3D space by computing a rotation angle around the Z-axis: if `is_vertical` is `True`, the angle is fixed at 90 degrees; otherwise, it is derived from the `direction` vector using `arctan2`. The constructed `vtkBillboardTextActor3D` is added to the provided `plotter` and returned.

**Parameters:**
- `plotter`
- `position`
- `text`
- `direction`
- `is_vertical`

### show_measures()

*No description available.*
Renders dimensional measurement annotations for a mesh's bounding box in the plotter, but only when `bounding_box_visible` is `True` and the elapsed time since the last update exceeds `update_interval` (0.5 seconds). On each valid update, it removes all existing measurement actors, recomputes the mesh bounds, and draws three edges representing width (X), depth (Y), and height (Z) from the minimum corner of the bounding box. Each edge is rendered as a line actor and annotated with a distance label in centimeters, positioned via `calculate_label_position` and oriented via `create_oriented_label`, after which the plotter is re-rendered.

### toggle_bounding_box_measures()

*No description available.*
Toggles the visibility state of bounding box measurements by inverting the `bounding_box_visible` flag. When activated, it calls `show_measures()` to display the measurement objects and logs a debug message indicating they have been enabled. When deactivated, it removes all current measurement actors from the plotter, clears the `measurement_objects` list, triggers a render update, and logs a debug message indicating they have been disabled.

### camera_changed(obj, event)

*No description available.*
A callback function triggered by `InteractionEvent` observer events on the plotter's interactor. When invoked, it checks whether the bounding box is currently visible and, if so, calls `show_measures()` to refresh the displayed measurements. This ensures that bounding box measurements remain accurate and up to date whenever the camera view is modified through user interaction.

**Parameters:**
- `obj`
- `event`

### reset_view()

*No description available.*
Resets the camera to its default position by calling `plotter.reset_camera()`. This function serves as a convenience wrapper to restore the plotter's camera view to a state that fits all visible actors within the viewport.

### change_view(direction)

*No description available.*
Changes the plotter's camera to a predefined view orientation by dynamically calling the corresponding `view_<direction>` method on the `plotter` object. The `direction` parameter is used to construct the method name via string formatting and `getattr`, allowing any valid view direction supported by the plotter to be selected. No return value is produced.

**Parameters:**
- `direction`

### process_file_path(file_path)

*No description available.*
Accepts a single `file_path` string parameter and returns the URL-decoded equivalent by calling `urllib.parse.unquote` on it. This converts any percent-encoded characters in the file path (e.g., `%20`) back to their original Unicode representation.

**Parameters:**
- `file_path`

### show_image(file_path)

*No description available.*
Creates an `ImageViewer` dialog instance parented to the current object, displays the image located at the specified `file_path`, and opens the dialog in a modal (blocking) execution loop via `exec()`. The function does not return a value and relies on the `ImageViewer` class to handle the actual image rendering logic.

**Parameters:**
- `file_path`

### show_video(file_path)

*No description available.*
Displays a video file in a `VideoPlayerWindow` instance. If no video player window currently exists, one is instantiated with the parent object, `db_manager`, `icon_list_widget`, and `main_class` references. The specified file is then loaded into the player via `set_video` and the window is made visible.

**Parameters:**
- `file_path`

### show_media(file_path, media_type)

Resolves the full file path for a given media file by detecting whether the provided `file_path` is already an absolute path (identified by a known protocol prefix or leading slash) or requires combination with a base path from `thumb_resize_str`. Once the full path is determined, it dispatches to the appropriate handler based on `media_type`: `show_video` for video files, `show_image` for images, or `self.show_3d_model` for 3D models. If the `media_type` is not one of these recognized values, a warning dialog is displayed to the user indicating an unsupported media type.

**Parameters:**
- `file_path`
- `media_type`

### query_media(search_dict, table)

*No description available.*
Queries the database for media records matching the provided search criteria. It accepts a dictionary of search parameters and an optional table name (defaulting to `"MEDIA_THUMB"`), removes empty entries from the dictionary via `Utility.remove_empty_items_fr_dict`, then delegates to `self.DB_MANAGER.query_bool` to execute the boolean query. If the query raises an exception, a warning dialog is displayed and `None` is returned; otherwise, the query result is returned directly.

**Parameters:**
- `search_dict`
- `table`

