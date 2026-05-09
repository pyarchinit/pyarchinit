# tabs/Tomba.py

## Overview

This file contains 100 documented elements.

## Classes

### pyarchinit_Tomba

`pyarchinit_Tomba` is a QDialog subclass that implements the tomb/burial record form (`tomba_table`) within the PyArchInit QGIS plugin. It provides a full data-entry, browsing, searching, sorting, and deletion interface for taphonomic burial records, covering fields such as site, structure, individual, burial rite, covering type, grave goods, skeletal position, and chronological phasing. The class supports multiple interface languages (Italian, German, English, French, Spanish, Portuguese, Arabic, Catalan, Romanian, Greek, and others) and integrates media management, GIS layer preview, and PDF report generation for the associated records.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the form widget by setting up the UI, applying the active theme, and configuring the initial state of interface components including hidden dock widgets, drag-and-drop support, and an `OrderedDict`-based image cache with a limit of 100 entries. Attempts a database connection via `on_pushButton_connect_pressed`, displaying a warning dialog if the connection fails, then populates and configures combo boxes and line edits with their initial values. Establishes all signal-slot connections for form fields related to site, structure, individual, object, and chronological period data, and finalizes initialization by calling `fill_fields`, `customize_GUI`, `set_sito`, `msg_sito`, `numero_invetario`, `update_dating`, and `init_remote_loader`.

##### numero_invetario(self)

*No description available.*
Populates the `lineEdit_nr_scheda` field with an inventory number derived from the existing data list (`DATA_LIST`). If the field is currently empty, it initializes it to `'1'`, then iterates over all records in `DATA_LIST`, collecting each entry's `nr_scheda_taf` value into a list, incrementing the last appended value by one, and sorting the list in ascending order. After processing, the field is updated to display the final value in the sorted list.

##### loadCorredolist(self)

*No description available.*
Initialises and populates the `tableWidget_corredo_tipo` table widget by clearing its existing contents and setting localised column headers based on the current language setting (`'it'`, `'de'`, or default English). It queries the database for inventory material records (`INVENTARIO_MATERIALI`) and individual records (`SCHEDAIND`) associated with the current site and structure, extracting artefact identifiers, materials, and individual numbers. The retrieved values are applied as read-only `ComboBoxDelegate` instances to columns 0, 1, and 2 of the table widget respectively; any exceptions encountered during the database operations are silently suppressed.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of multiple UI push buttons by passing the value `n` to each button's `setEnabled` method. The buttons affected are: `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_new_search`, `pushButton_search_go`, and `pushButton_sort`. Note that `pushButton_connect` is present in the source but commented out and therefore not affected by this method.

##### enable_button_search(self, n)

*No description available.*
Sets the enabled state of multiple UI buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are: `pushButton_new_rec`, `pushButton_view_all`, `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_delete`, `pushButton_save`, and `pushButton_sort`. The `pushButton_connect` button is excluded from this operation, as its corresponding call is commented out.

##### on_pushButton_connect_pressed(self)

*No description available.*
Slot triggered when the connect button is pressed. It establishes a database connection using a `Connection` instance, detects whether the backend is SQLite, and initialises the database manager via `get_db_manager`. If the connection succeeds, it loads existing records and updates the UI state accordingly; if the database is empty, it displays a localised welcome message (Italian, German, or English based on `self.L`) and opens a new record form. Any exception during the process is caught and reported as a localised warning message in the QGIS message bar.

##### customize_GUI(self)

Sets up the initial visual configuration of the GUI by applying fixed column widths to `tableWidget_corredo_tipo`, enabling `lineEdit_nr_scheda`, and initializing a `QgsMapCanvas` instance added as a "Piante" tab. Configures `iconListWidget` display properties including line widths, icon size, uniform item sizes, extended selection mode, and connects the double-click signal to `openWide_image`. Also updates media button visibility and sets several combo boxes to editable mode.

##### loadMapPreview(self, mode)

*No description available.*
Loads or clears a map preview in the `mapPreview` widget based on the specified `mode`. When `mode=0`, it constructs a filter expression using the current record's ID, loads the corresponding map layers via `self.pyQGIS.loadMapPreview`, displays a warning dialog listing the layer names, sets those layers on the preview widget, and zooms to the full extent. When `mode=1`, it clears all layers from the preview widget and zooms to the full extent.

##### dropEvent(self, event)

*No description available.*
Handles drop events by extracting file URLs from the event's MIME data and validating each dropped file against a list of accepted formats (`jpg`, `jpeg`, `png`, `tiff`, `tif`, `bmp`, `mp4`, `avi`, `mov`, `mkv`, `flv`). If a dropped file matches an accepted format, `load_and_process_image` is called with the file's local path; otherwise, a warning dialog is displayed indicating the unsupported file type. Any exception raised during file processing is caught and reported via a `QMessageBox` warning, after which the base class `dropEvent` is called.

##### dragEnterEvent(self, event)

*No description available.*
Handles the drag-enter event by inspecting the MIME data of the incoming drag action. If the event's MIME data contains URLs, the proposed action is accepted; otherwise, the event is ignored. This method controls whether a drag operation is permitted to proceed over the widget based solely on the presence of URL data.

##### dragMoveEvent(self, event)

*No description available.*
Handles the drag move event triggered when a dragged object is moved within the widget's boundaries. Unconditionally accepts the proposed drop action by calling `event.acceptProposedAction()`, allowing the drag operation to continue without restriction.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database by assigning the provided `mediatype`, `filename`, `filetype`, and `filepath` values along with a auto-incremented ID, a default description of `'Insert description'`, and a default tag of `"['imagine']"`. The method delegates record construction to `DB_MANAGER.insert_media_values()` and persists the result via `DB_MANAGER.insert_data_session()`.

Returns `1` on successful insertion, or `0` on failure; integrity constraint violations (e.g., duplicate entries) are handled silently with a descriptive message, while other session errors display a warning dialog via `QMessageBox`.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
Inserts a media thumbnail record into the `MEDIA_THUMB` database table by assigning the provided metadata to instance attributes and delegating the actual record construction to `DB_MANAGER.insert_mediathumb_values`, using an auto-incremented primary key derived from the current maximum `id_media_thumb` value. The constructed record is then persisted via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if the operation fails — silently suppressing integrity constraint violations (such as duplicate thumbnail entries) and displaying a warning dialog for all other exceptions.

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
Queries the database for a `TOMBA` record matching the current site (`comboBox_sito`) and card number (`lineEdit_nr_scheda`) values from the UI. It constructs a search dictionary with the `sito` and `nr_scheda_taf` fields and executes a boolean query via `DB_MANAGER`. Returns a list containing a single entry with the matched record's `id_tomba`, the string `'TOMBA'`, and the string `'tomba_table'`.

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
Loads a media file from the given `filepath`, determines its type (image or video) based on the file extension, and processes it for storage. If the file is not already registered in the database, the method inserts a media record, generates thumbnail and resized versions using the appropriate utility classes, and optionally uploads the original file to a configured remote storage backend. The resulting media item is then added to the UI list widget and tagged via `assignTags_reperti`; if the thumbnail path is not configured, an informational message is displayed to the user in the appropriate language.

##### db_search_check(self, table_class, field, value)

*No description available.*
Performs a boolean database query against a specified table class using a single field-value pair as the search criterion. The method constructs a search dictionary from the provided field and value, removes any empty entries via the `Utility.remove_empty_items_fr_dict` helper, and delegates the query to `DB_MANAGER.query_bool`. Returns the result of the database query.

##### on_pushButton_search_images_pressed(self)

Open the Image Search dialog with pre-filled filters for current Tomba record.

##### on_pushButton_removetags_pressed(self)

*No description available.*
Handles the press event of the "remove tags" button by first verifying that at least one item is selected in `iconListWidget`, displaying a localized warning if no selection exists. If items are selected, it prompts the user with a language-appropriate confirmation dialog (supporting Italian, German, and English via `self.L`) before proceeding with the irreversible operation. Upon confirmation, it resolves the current record's database ID by querying the `TOMBA` table using the current site (`comboBox_sito`) and record number (`lineEdit_nr_scheda`), then calls `DB_MANAGER.remove_tags_from_db_sql_scheda` for each selected item and removes those items from `iconListWidget`.

##### on_pushButton_all_images_pressed(self)

*No description available.*
Handles the press event of the "all images" button by querying the database for media thumbnails and entity-to-media relationships, displaying an informational message and returning early if no records are found. If records exist, it constructs and displays a paginated, searchable `QListWidget` interface containing media images, with navigation controls (previous/next page buttons and numbered page labels), a search input field, and a conditional "TAG" button that becomes visible only when an item is selected. Finally, it calls `load_images()` to populate the list and connects the search field's `returnPressed` signal to the `filter_items` method.

##### load_images(self, filter_text)

*No description available.*
Loads and displays thumbnail images from the database into `new_list_widget`, separating tagged and untagged images and applying optional filename-based filtering via `filter_text`. When the total image count exceeds 100, only untagged images are displayed with pagination applied directly to the untagged set; otherwise, images associated with `TOMBA` entity types are also resolved and their linked tomb record numbers appended to each list item's label. Untagged images are highlighted with a yellow background, while tagged images are displayed with a white background; thumbnail icons are managed through an LRU-style cache bounded by `cache_limit`.

##### update_page_labels(self)

*No description available.*
Updates the visual state of all pagination controls to reflect the current page. Enables or disables the previous and next navigation buttons based on whether `current_page` is at the first or last page respectively, and updates each page number label by disabling the one corresponding to the current page. Additionally refreshes the `current_page_label` and `total_pages_label` text to display the current page number and total page count.

##### go_to_previous_page(self)

Navigates to the previous page by decrementing `current_page` by one, provided the current page is greater than 1. After updating the page counter, it reloads the image set by calling `load_images` with the current filter text (`self.current_filter_text`). If the current page is already 1, no action is taken.

##### go_to_next_page(self)

*No description available.*
Advances to the next page of images if the current page is less than the total number of pages. Increments `current_page` by one and reloads the image set by calling `load_images` with the current filter text. No action is taken if the current page is already the last page.

##### on_page_label_clicked(self, page, _)

*No description available.*
Handles a page label click event by navigating to the specified page. If the requested `page` differs from `self.current_page`, it updates `self.current_page` to the new value and reloads the image set by calling `self.load_images` with the current filter text. The second parameter is ignored and defaults to `None`.

##### filter_items(self)

*No description available.*
Retrieves the current text from the search field, converts it to lowercase, and stores it in `self.current_filter_text`. It then calls `self.load_images` with the updated filter text to refresh the displayed images based on the search input.

##### on_done_selecting_all(self)

Handles the completion of a bulk selection operation by associating all selected media items in `new_list_widget` with a TOMBA record identified by the current values of `comboBox_sito` and `lineEdit_nr_scheda`. For each selected item, it queries the database for matching MEDIA records and, if found and not already linked, inserts a new MEDIATOENTITY relationship via `insert_mediaToEntity_rec`. After processing all selected items, it refreshes the icon list widget and updates the last processed list widget item.

##### update_list_widget_item(self, item)

Queries the database for a `MEDIATOENTITY` record matching the text of the provided `QListWidgetItem`, then updates the item's appearance and label based on the result. If a matching record is found, the item's background is set to white and its text is appended with the associated `TOMBA` record's `nr_scheda_taf` value (or `" - US: Not found"` if no corresponding `TOMBA` record exists). If no `MEDIATOENTITY` record is found, the item's background is set to yellow to indicate it is untagged.

##### fill_iconListWidget(self)

Populates `iconListWidget` with icon-based list items derived from the currently selected items in `new_list_widget`. For each selected item, it queries the `MEDIA_THUMB` database table using the item's filename, retrieves the corresponding thumbnail path via a `Connection` instance, and constructs a `QListWidgetItem` with an icon loaded from the resolved file path. Each item stores the media filename as both its display text and custom `UserRole` data before being added to `iconListWidget`.

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

##### openWide_image(self)

*No description available.*
Opens the selected items from `iconListWidget` for full viewing based on their media type. For each selected item, it queries the `MEDIA_THUMB` database table to determine whether the file is a video or an image; if the item is a video, it opens the file directly using `os.startfile`, and if it is an image, it displays it using an `ImageViewer` dialog. The resolved file path is constructed by combining the configured thumbnail resize path (`thumb_resize_str`) with the stored `path_resize` value retrieved from the database.

##### charge_list(self)

*No description available.*
Populates all combo box widgets in the form by loading values from the database and the thesaurus, resolving the current user interface language via `QgsSettings` locale settings. Site values are retrieved directly from the `site_table` database table, while all other field values — including area, rite (`rito`), markers (`segnacoli`), libation channel (`canale_libatorio`), burial preservation (`conservazione_taf`), cover type (`copertura_tipo`), remains container type (`tipo_contenitore_resti`), grave goods presence (`corredo_presenza`), deposition (`deposizione`), and burial type (`sepoltura`) — are queried from the `PYARCHINIT_THESAURUS_SIGLE` thesaurus table using language-specific and typology-specific search criteria. Each retrieved list is sorted alphabetically before being inserted into its corresponding combo box; errors encountered during empty-string removal are reported via localized `QMessageBox` warnings in Italian, English, or German.

##### msg_sito(self)

*No description available.*
Validates the currently selected site in `comboBox_sito` against the configured site retrieved from the `Connection` object. If the selected site matches the configured site, an informational message confirming the active connection is displayed in the appropriate language (`it`, `de`, or default English). If no site has been configured (`sito_set_str` is empty), a warning message is shown prompting the user to set one, and if the user confirms, the configuration dialog `pyArchInitDialog_Config` is opened.

##### set_sito(self)

*No description available.*
Retrieves the configured site setting from the `Connection` object and queries the database for all records matching that site value. If matching records are found, it populates `DATA_LIST`, updates the record counter, fills the form fields, sets the browse status, and disables the site combobox. If no matching records exist, a localized warning message is displayed (in Italian, German, or English) informing the user that the specified site does not exist in the current tab.

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

##### update_dating(self)

This function updates the 'Dating' field for all US records in the database.

##### charge_struttura_nr(self)

*No description available.*
Queries the database for `STRUTTURA` records matching the currently selected site (`comboBox_sito`) and structure code (`comboBox_sigla_struttura`), then extracts and deduplicates the corresponding structure numbers into a sorted list. The method clears and repopulates `comboBox_nr_struttura` with the resulting values after removing any empty entries. Depending on the current browse status, it either clears the combo box edit text (in "Find" mode) or attempts to restore the structure number from the current record in `DATA_LIST` (in "Current" mode).

##### charge_struttura_list(self)

*No description available.*
Queries the database for all `SCHEDAIND` records matching the currently selected site (`comboBox_sito`), then extracts and deduplicates the `sigla_struttura` values from the results. The resulting list is sorted, stripped of empty entries, and used to populate `comboBox_sigla_struttura`. Depending on the current browse status, the combo box edit text is either cleared (in "Find/Trova/Finden" mode) or set to the `sigla_struttura` value of the current record in the data list.

##### charge_individuo_list(self)

*No description available.*
Queries the database for individual records (`SCHEDAIND`) matching the currently selected site (`sito`), structure abbreviation (`sigla_struttura`), and structure number (`nr_struttura`). The resulting individual numbers are deduplicated and loaded into the `comboBox_nr_individuo` combo box, with empty entries removed. Depending on the current browse status, the combo box edit text is either cleared (search/find mode) or populated with the individual number from the current record in `DATA_LIST`.

##### charge_oggetti_esterno_list(self)

Populates the `comboBox_oggetti_esterno` combo box with a deduplicated list of find numbers (`n_reperto`) retrieved from the `INVENTARIO_MATERIALI` table, filtered by the current site (`sito`) and the structure identifier composed from the current record's `sigla_struttura` and `nr_struttura` fields. The query is built using a dictionary passed to `DB_MANAGER.query_bool`, and duplicate entries are removed via `UTILITY.remove_dup_from_list` before the items are added to the combo box. Depending on the current browse status, the combo box edit text is either cleared (search/find mode) or set to the `oggetti_esterno` value of the current record (current/use mode).

##### on_toolButtonPan_toggled(self)

*No description available.*
Slot triggered when the pan tool button is toggled. Instantiates a `QgsMapToolPan` object bound to the `mapPreview` canvas and sets it as the active map tool, enabling pan interaction on the map preview.

##### on_pushButton_showSelectedFeatures_pressed(self)

*No description available.*
Handles the press event of the "Show Selected Features" button by retrieving the currently selected map features and resolving their IDs using the field position derived from `ID_TABLE`. It queries the database manager to fetch and sort the corresponding records, then repopulates `DATA_LIST` with the results and refreshes the form fields. Finally, it updates the browse status, record counter, and internal record pointers to reflect the newly loaded selection.

##### on_pushButton_sort_pressed(self)

*No description available.*
Handles the sort button press event by opening a `SortPanelMain` dialog populated with the available sort items, allowing the user to select sort fields and order type. If the record state check passes, the selected items are converted using `CONVERSION_DICT`, and the current dataset is re-queried and reordered via `DB_MANAGER.query_sort` using the converted sort fields and specified sort mode. Upon completion, the data list, browse status, sort status, record counters, and displayed fields are all updated to reflect the newly sorted results.

##### on_toolButtonGis_toggled(self)

*No description available.*
Handles the toggle event of `toolButtonGis`, displaying a localized informational message box to notify the user whether GIS mode has been activated or deactivated. The message content is determined by the current language setting (`self.L`), with distinct messages provided for Italian (`'it'`), German (`'de'`), and a default English fallback. When the button is checked, a message indicates that search results will be displayed on the GIS; when unchecked, a message indicates that GIS display has been disabled.

##### on_pushButton_new_rec_pressed(self)

*No description available.*
Handles the "New Record" button press event by initiating the creation of a new record entry. It first performs data validation and equality checks on the current data list when in browse mode (`"b"`), then transitions the interface to new-record mode (`"n"`) by clearing fields, resetting sort and status labels, and configuring combo box editability and availability. The exact field-clearing behavior and combo box signal wiring depend on whether the currently selected site (`comboBox_sito`) matches the configured site set retrieved from the `Connection` object.

##### on_pushButton_save_pressed(self)

Handles the save button press event by branching logic based on the current browse status (`self.BROWSE_STATUS`). In browse mode (`"b"`), it performs a data validation check and, if the record has been modified, prompts the user with a localized confirmation dialog (Italian, German, or English) before saving the changes via `update_if`; if no changes are detected, a localized warning is displayed. In insert mode, it validates the data and attempts to insert a new record via `insert_new_rec`, then updates the UI state, resets sort status, refreshes the record list, and re-enables controls upon success, or displays a localized error message on failure.

##### data_error_check(self)

*No description available.*
Validates the required "Site" (`comboBox_sito`) input field by checking whether it is empty using an `Error_check` instance. If the field is empty, a language-specific warning dialog is displayed via `QMessageBox.warning` — in Italian (`'it'`), German (`'de'`), or English (default) — and an internal error flag `test` is set to `1`. Returns `0` if validation passes or `1` if a validation error is detected.

##### insert_new_rec(self)

*No description available.*
Collects form field values from the UI (combo boxes, line edits, and text edits) along with the corredo tipo table data, and attempts to insert a new tomb record into the database via `DB_MANAGER.insert_values_tomba`, assigning the next available ID automatically.

Returns `1` on successful insertion, or `0` if an error occurs. In the event of an `IntegrityError` (duplicate record), a localized warning dialog is displayed in Italian, German, or English depending on the value of `self.L`; all other exceptions trigger a generic error dialog.

##### on_pushButton_insert_row_corredo_pressed(self)

*No description available.*
Event handler triggered when the "insert row" push button for the corredo section is pressed. It delegates to `insert_new_row`, passing `'self.tableWidget_corredo_tipo'` as the target table widget identifier. This results in a new row being added to the `tableWidget_corredo_tipo` table widget.

##### on_pushButton_remove_row_corredo_pressed(self)

*No description available.*
Slot method triggered when the "remove row" button for the corredo section is pressed. It delegates execution to `self.remove_row()`, passing `'self.tableWidget_corredo_tipo'` as the target table identifier to remove a row from that widget.

##### check_record_state(self)

*No description available.*
Validates the current record's state by first performing a data error check via `data_error_check()`, returning `1` immediately if input errors are detected. If no input errors exist and the record has been modified (as determined by `records_equal_check()`), it displays a localized warning dialog — in Italian, German, or English depending on `self.L` — prompting the user to save the changes, and delegates the response to `update_if()`. Returns `0` when no input errors are present.

##### on_pushButton_view_all_pressed(self)

*No description available.*
Handles the press event of the "View All" button. If `check_record_state()` returns `1`, no action is taken; otherwise, the method clears the current fields, reloads all records via `charge_records()`, and populates the fields with the first record in `DATA_LIST`. It then sets the browse status to `"b"`, updates the status label, resets the record counters, and clears the sort label to reflect an unsorted state.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Handles the press event of the "first record" navigation button. If `check_record_state()` returns `1`, no action is taken; otherwise, it clears the current fields, resets the record counters to reflect the total number of records in `DATA_LIST` and sets the current position to `0`, then populates the fields with the first record via `fill_fields(0)` and updates the record counter display accordingly. Any exception raised during this process is caught and displayed to the user as a warning dialog via `QMessageBox`.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Navigates to the last record in `DATA_LIST` by setting `REC_CORR` to the final index and `REC_TOT` to the total number of records. It clears the current form fields via `empty_fields()`, then repopulates them with the last record's data using `fill_fields()`, and updates the record counter display accordingly. If `check_record_state()` returns `1`, the operation is skipped; any other exception raised during execution is caught and displayed as a warning dialog.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous record" button press event by decrementing the current record index (`REC_CORR`) by one. If the index reaches `-1`, it is reset to `0` and a localised warning message is displayed (Italian, German, or English) informing the user that they are already at the first record. Otherwise, the form fields are cleared via `empty_fields()`, repopulated with the previous record's data via `fill_fields()`, and the record counter is updated via `set_rec_counter()`; if the record state check returns `1`, no action is taken.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Advances navigation to the next record by incrementing `REC_CORR`. If the incremented value meets or exceeds `REC_TOT`, it reverts the counter and displays a localized warning message (Italian, German, or English) indicating that the last record has been reached. Otherwise, it clears the current fields, populates them with the next record's data via `fill_fields`, and updates the record counter display using `set_rec_counter`.

##### on_pushButton_delete_pressed(self)

*No description available.*
Handles the delete button press event by presenting a language-appropriate confirmation dialog (Italian, German, or English, based on `self.L`) before permanently deleting the currently selected record from the database via `self.DB_MANAGER.delete_one_record`. If the user confirms, the record identified by `self.ID_TABLE` at `self.DATA_LIST[self.REC_CORR]` is deleted, and the data list is reloaded; if the database becomes empty afterward, all internal data structures and UI counters are reset, otherwise the UI is updated to display the first remaining record in browse mode.

##### on_pushButton_new_search_pressed(self)

*No description available.*
Handles the press event of the "New Search" button by transitioning the form into search mode (`BROWSE_STATUS = "f"`), provided the current record state does not block the action. Depending on whether the current site (`comboBox_sito`) matches the configured site set retrieved via `Connection`, it selectively enables and sets the editability of relevant combo boxes (notably `comboBox_nr_individuo`) and resets the status label, record counter, and sort label accordingly. If the site does not match the configured set, it additionally reloads the combo box lists via `charge_list()` and clears all fields via `empty_fields()`; otherwise, it clears only the non-site fields via `empty_fields_nosite()`.

##### on_pushButton_showLayer_pressed(self)

Handles the press event of the `pushButton_showLayer` button. Retrieves the current record from `DATA_LIST` using the `REC_CORR` index, wraps it in a single-element list, and passes it to `self.pyQGIS.charge_tomba_layers` to load the corresponding layer in the QGIS environment.

##### on_pushButton_search_go_pressed(self)

*No description available.*
Handles the search button press event for the tomb (tomba) record form. If the browse status is not in search mode (`"f"`), a localized warning message is displayed instructing the user to initiate a new search first; otherwise, field values are collected from the form controls — including area, record number, structure number, individual identifiers, chronological period/phase ranges, and various burial attributes — assembled into a search dictionary, and empty entries are removed before executing a boolean database query via `self.DB_MANAGER.query_bool`. Depending on the query result, the data list and record counters are updated, form fields are populated, and — if the GIS toolbar button is active — the matching records are loaded into the QGIS layer via `self.pyQGIS.charge_tomba_layers`; localized result messages are displayed throughout, and the search button is re-enabled upon completion.

##### generate_list_pdf(self)

Iterates over `self.DATA_LIST` and constructs a structured list of records for PDF generation, where each record contains up to 30 fields of burial/individual data. For each entry, the method queries the database via `self.DB_MANAGER` to retrieve associated stratigraphic unit (US) records and elevation (quota) data for both the individual and the related structure, sorting and formatting the quota values accordingly. If no elevation data is found in GIS, placeholder strings are assigned based on the active language (`self.L`), supporting Italian (`'it'`), German (`'de'`), and a default English fallback. The compiled `data_list` is returned for use in PDF rendering.

##### update_if(self, msg)

*No description available.*
Conditionally executes a record update based on the user's response to a confirmation dialog. If `msg` equals `QMessageBox.StandardButton.Ok`, the method calls `update_record()` and, on success, rebuilds `DATA_LIST` by re-querying the database using either a default ascending sort on `ID_TABLE` or the current sort configuration defined by `SORT_ITEMS_CONVERTED` and `SORT_MODE`. Returns `1` if the update succeeds, `0` if it fails, and implicitly `None` if the user did not confirm.

##### update_record(self)

*No description available.*
Attempts to update the current record in the database by calling `self.DB_MANAGER.update` with the mapped table class, ID field, current record identifier, table fields, and the prepared update values returned by `self.rec_toupdate()`. Returns `1` on success or `0` on failure. If an exception occurs, the error details are appended to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user based on the language setting `self.L` (`'it'`, `'de'`, or a fallback).

##### rec_toupdate(self)

*No description available.*
Retrieves the record designated for updating by delegating to the `UTILITY` object's `pos_none_in_list` method, passing `DATA_LIST_REC_TEMP` as the argument. Returns the resulting value, which represents the processed record with `None` values handled according to the utility's implementation. This method serves as a thin wrapper to prepare temporary record data prior to a database update operation.

##### charge_records(self)

*No description available.*
Retrieves all records from the database for the current mapper table class, ordered by the table's ID column in ascending order. The results are stored directly in the instance's `DATA_LIST` attribute via a single ordered query, replacing a previously used double-query pattern for improved performance.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded, separated by hyphens). The formatted date string is returned to the caller.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves the corresponding table widget attribute on the instance, and iterates over all rows and columns to extract cell text values. Non-empty rows are collected as sublists of string values and appended to a list. Returns the resulting list of sublists representing the table's non-empty row data.

##### tableInsertData(self, t, d)

Set the value into alls Grid

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

insert new row into a table based on table_name

##### empty_fields_nosite(self)

Resets all form fields and widgets to their default empty state, excluding the site field. The method first removes all rows from `tableWidget_corredo_tipo` and inserts a single new empty row, then clears or resets all associated UI controls including combo boxes, line edits, text edits, and the icon list widget. All checkable items in `comboBox_nr_individuo` are explicitly unchecked, while the remaining combo boxes and text fields are cleared of any user-entered values.

##### empty_fields(self)

Resets all input fields in the form to their default empty state. It first removes all existing rows from `tableWidget_corredo_tipo` and inserts a single new empty row, then clears all combo boxes, line edits, text edits, and the icon list widget. All checkable items in `comboBox_nr_individuo` are explicitly unchecked.

##### fill_fields(self, n)

Populates all form fields with data from the record at index `n` within `DATA_LIST`, setting the current record number via `self.rec_num`. It updates combo boxes, line edits, text edits, and a checkable combo box (`comboBox_nr_individuo`) for fields including site, area, card number, structure, individual number, rite, description, interpretation, and chronological data, as well as inserting tabular data for burial goods type. After populating the fields, it conditionally triggers a map preview and loads media either automatically for local paths or on demand for remote paths; any exceptions raised during the process are silently suppressed.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the total and current record counters by assigning `t` to `self.rec_tot` and `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

*No description available.*
Collects and validates the current values from all form widgets — including combo boxes, line edits, text edits, and a table widget — and assembles them into `DATA_LIST_REC_TEMP`, a list representing a temporary record of burial/tomb data. Fields such as `area`, `nr_scheda`, and `nr_struttura` are conditionally read as empty strings or cast to integers, while `nr_individuo` is built by iterating over the checkable combo box model and joining all checked items into a comma-separated string. The corredo type data is retrieved via `table2dict` on `tableWidget_corredo_tipo` and included alongside site, structure, rite, taphonomy, grave goods, and chronological phase fields.

##### set_LIST_REC_CORR(self)

*No description available.*
Populates `DATA_LIST_REC_CORR` by iterating over `TABLE_FIELDS` and retrieving the corresponding attribute values from the current record (`DATA_LIST[REC_CORR]`) via `getattr`. Each retrieved value is converted to a string and appended to the `DATA_LIST_REC_CORR` list, which is reset to an empty list at the start of each call. This method is used in conjunction with `set_LIST_REC_TEMP` within `records_equal_check` to prepare the current record's data for comparison.

##### records_equal_check(self)

*No description available.*
Compares the current record in its temporary state against the corresponding saved record by invoking `set_LIST_REC_TEMP()` and `set_LIST_REC_CORR()` to populate the respective data lists. Returns `0` if `DATA_LIST_REC_CORR` and `DATA_LIST_REC_TEMP` are equal, or `1` if they differ.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### testing(self, name_file, message)

*No description available.*
Opens a file at the path specified by `name_file` in write mode (`'w'`), writes the string representation of `message` to it, then closes the file. This method overwrites any existing content at the given file path.

##### on_pushButton_print_pressed(self)

Handles the press event of the print button by generating and exporting PDF documents based on the current interface language (`self.L`) and the state of the checkboxes `checkBox_s_us` and `checkBox_e_us`. When `checkBox_s_us` is checked, it instantiates `generate_tomba_pdf`, retrieves data via `generate_list_pdf`, and calls the appropriate language-specific sheet-building method (e.g., `build_Tomba_sheets`, `build_Tomba_sheets_de`, `build_Tomba_sheets_en`, etc.), then displays a success message. For Italian (`'it'`), if `checkBox_e_us` is also checked, it additionally attempts to build a tomb index PDF via `build_index_Tomba`, displaying a warning if the data list is empty or an exception occurs.

##### setPathpdf(self)

*No description available.*
Opens a file dialog prompting the user to select an existing PDF file, using `PDFFOLDER` as the initial directory and filtering for `.pdf` files. If a valid path is selected, it updates `lineEdit_pdf_path` with the chosen file path and stores the value in `QgsSettings`.

##### openpdfDir(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path using the operating system's default file manager. On Windows, it uses `os.startfile`; on macOS (`Darwin`), it invokes the `open` command via `subprocess.Popen`; on all other platforms, it uses `xdg-open`.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_PDF_folder` directory located under the `PYARCHINIT_HOME` environment variable path. The method determines the current operating system and uses the appropriate platform-specific mechanism to launch the directory in the default file manager: `os.startfile` on Windows, `open` on macOS (Darwin), and `xdg-open` on other systems (typically Linux).

##### check_for_updates(self)

Check if current record has been modified by others

## Functions

### r_id()

*No description available.*
A nested helper function defined within `on_pushButton_removetags_pressed` that retrieves the database ID of a tomb record (`id_tomba`) matching the current site (`comboBox_sito`) and card number (`lineEdit_nr_scheda`) values from the UI. It constructs a search dictionary using those two fields and queries the `TOMBA` table via `DB_MANAGER.query_bool`, then iterates over the results to extract the `id_tomba` value. Returns the `id_tomba` of the last matched record.

### update_done_button()

*No description available.*
A callback function connected to the `itemSelectionChanged` signal of `new_list_widget`. It hides the "TAG" button (`done_button`) when no items are selected in the list widget, and shows it when at least one item is selected. When the button becomes visible, it also connects its `clicked` signal to the `on_done_selecting_all` handler.

### r_list()

*No description available.*
An inner function defined within `on_done_selecting_all` that queries the database for a `TOMBA` record matching the current values of `comboBox_sito` and `lineEdit_nr_scheda`. It constructs a search dictionary using the site name and card number (`nr_scheda_taf`), executes a boolean query against the `TOMBA` table via `DB_MANAGER.query_bool`, and returns a list of tuples containing each matching record's `id_tomba`, the string `'TOMBA'`, and the string `'tomba_table'`.

