# tabs/Image_viewer.py

## Overview

This file contains 101 documented elements.

## Classes

### Main

`Main` is a QDialog subclass that implements the pyArchInit Media Manager, providing a graphical interface for importing, browsing, tagging, and searching archaeological media files (images and videos) within a QGIS plugin environment. It manages database interactions against `media_table` and `media_thumb_table`, supporting entity-type associations (US, pottery, materials, tombs, and structures) through a tagging system linked to corresponding database records. The class supports multilingual display (Italian, German, and English), paginated thumbnail browsing, advanced search with optional partial matching and untagged-media filtering, and lazy-loads the GPTWindow component to avoid PyMuPDF DLL conflicts on Windows.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self)

Initializes an instance of the Media Manager dialog by calling the parent `QDialog.__init__`, establishing a database connection, and setting up the UI via `setupUi`. Applies the application theme, configures widget behaviors (including extended selection mode, signal-slot connections for combo boxes and the image list widget), and populates form fields and data lists. Finalizes initialization by setting the window title, loading remote image loader credentials from QGIS settings, and invoking `setup_advanced_search` to prepare advanced search UI elements.

##### setup_advanced_search(self)

Initialize advanced search UI elements and connections.

##### toggle_inventario_field(self)

Show/hide numero_inventario field based on selected entity type.

##### toggle_entity_selection(self, checked)

Enable/disable entity type selection when untagged mode is active.

##### clear_search_filters(self)

Clear all search filters.

##### perform_advanced_search(self)

Perform advanced search with text filter, untagged mode, and partial matching.

##### remove_all(self)

Resets the row count of five table widgets (`tableWidgetTags_US`, `tableWidgetTags_POT`, `tableWidgetTags_MAT`, `tableWidgetTags_tomba`, and `tableWidgetTags_tomba_2`) to 1, effectively clearing their contents. This method serves as a bulk reset operation for all tag-related table widgets in the interface.

##### on_pushButton_gptsketch_pressed(self)

Open GPT Sketch window with lazy import to avoid DLL conflicts on Windows.

##### split_2(self)

*No description available.*
Processes the currently selected items from `iconListWidget`, parsing each item's text by splitting on underscores and hyphens to decompose compound identifiers into their constituent `Sito`, `Area`, and `US` components. Items whose text does not contain a hyphen are collected as-is and skipped from further processing. The parsed components are then populated row by row into `tableWidgetTags_US`, with error handling via a `QMessageBox` warning if row insertion fails; a trailing row removal is performed via `remove_row` after population.

##### split_1(self)

*No description available.*
Retrieves the currently selected items from `iconListWidget` and processes their text labels to populate `tableWidgetTags_US` with three columns labeled `'Sito'`, `'Area'`, and `'US'`. Items whose names contain a hyphen (`'-'`) are collected into a separate list and skipped; all other item names are split on the underscore character (`'_'`) and their first three segments are written into the corresponding table row. If an error occurs during table population, a warning dialog titled `"Messaggio"` is displayed with the exception details.

##### customize_gui(self)

Sets predefined column widths for multiple table widgets (`tableWidgetTags_US`, `tableWidgetTags_MAT`, `tableWidgetTags_POT`, `tableWidgetTags_tomba`, `tableWidgetTags_tomba_2`, and `tableWidget_tags`) and configures the icon size and line width of `iconListWidget`. Initializes non-editable `ComboBoxDelegate` instances populated with site, area, and sigla US values, then assigns these delegates to specific columns of the relevant table widgets to provide combo box selection behaviour. Concludes by calling `charge_sito_list()` to reload the site list.

##### valuechange(self, value)

*No description available.*
Handles slider value change events by reading the current slider position and dynamically resizing the icons displayed in `iconListWidget`. The icon width is calculated as `80 + value // 40` and the icon height as `180 + value // 80`, scaling proportionally with the provided `value` parameter. The updated size is applied via `QSize` to `iconListWidget.setIconSize()`.

##### charge_list(self)

*No description available.*
Clears and repopulates the `comboBox_sito` combo box with a sorted list of site values retrieved from the database. It queries the `site_table` table via `DB_MANAGER.group_by`, converts the result using `UTILITY.tup_2_list_III`, and removes any empty string entries before adding the sorted items to the combo box. If an unexpected error occurs during the removal of empty entries, a warning dialog is displayed to the user.

##### charge_sigla_list(self)

*No description available.*
Populates the `comboBox_sigla_struttura` combo box with structure abbreviation values (`sigla_struttura`) retrieved from the database for the currently selected site (`comboBox_sito`). The method only executes when the `radioButton_struttura` radio button is checked, querying the `STRUTTURA` table via `DB_MANAGER.query_bool` using the current site as a filter. Duplicate values are removed from the resulting list using `UTILITY.remove_dup_from_list` before the items are added to the combo box; any exceptions encountered during this process are reported via a `QMessageBox` warning dialog.

##### charge_nr_st_list(self)

*No description available.*
Populates the `comboBox_nr_struttura` combo box with structure numbers (`numero_struttura`) retrieved from the database for the currently selected site (`comboBox_sito`). This method executes only when the `radioButton_struttura` radio button is checked, querying the `STRUTTURA` table via `DB_MANAGER.query_bool` using the current site as a filter. Duplicate entries are removed from the resulting list using `UTILITY.remove_dup_from_list` before populating the combo box; any exceptions encountered during the process are reported via a `QMessageBox` warning dialog.

##### charge_us_list(self)

*No description available.*
Populates `comboBox_us` with a deduplicated list of records retrieved from the database, filtered by the currently selected site (`comboBox_sito`). The specific database table queried and the field used to build the list depend on which radio button is active: `radioButton_us` queries the `US` table using the `us` field, `radioButton_materiali` queries the `INVENTARIO_MATERIALI` table using the `us` field, and `radioButton_tomba` queries the `TOMBA` table using the `nr_scheda_taf` field. The `label_8` text is updated accordingly (`'US'` or `'N. Tomba'`), and any exceptions encountered during execution are reported via a `QMessageBox` warning dialog.

##### charge_area_list(self)

Populates `comboBox_area` with a deduplicated list of area values retrieved from the database, based on the currently selected radio button (`radioButton_us`, `radioButton_materiali`, or `radioButton_tomba`). For each active radio button, the method queries the corresponding database table (`US`, `INVENTARIO_MATERIALI`, or `TOMBA`) using the site name from `comboBox_sito` as the filter criterion. If the query returns no results, the method returns early; otherwise, it clears the combo box and repopulates it using `UTILITY.remove_dup_from_list`.

##### connection(self)

*No description available.*
Establishes a database connection using the connection string retrieved from `conn.conn_str()`, then initialises the database manager via `get_db_manager()` with singleton mode enabled. If records are found after loading, it sets the browse status, updates UI counters and labels, populates the site list, and fills the form fields; if the database is empty, it displays a localised welcome message (Italian, German, or English depending on `self.L`) and sets the browse status to `'x'`. Any exception raised during the process is silently caught and converted to a string.

##### enable_button(self, n)

*No description available.*
Sets the enabled state of six navigation and action buttons by passing the value `n` to each button's `setEnabled` method. The affected buttons are `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_sort`, and `pushButton_go`. The parameter `n` is passed directly to `setEnabled`, and is expected to be a boolean or equivalent value controlling whether the buttons are interactive.

##### enable_button_search(self, n)

Sets the enabled state of multiple navigation and search-related buttons based on the boolean value `n`. The affected buttons are `pushButton_first_rec`, `pushButton_last_rec`, `pushButton_prev_rec`, `pushButton_next_rec`, `pushButton_sort`, and `pushButton_go`. Passing `True` enables all listed buttons, while passing `False` disables them.

##### on_pushButton_go_pressed(self)

**`on_pushButton_go_pressed`**

Slot triggered when the "Go" button is pressed; it initiates a media record search based on the current UI state. If advanced search mode is active (i.e., `checkBox_untagged` is checked or `lineEdit_text_search` contains text), it delegates to `perform_advanced_search()` and returns early. Otherwise, it reads the selected site, area, and unit/structure identifiers from the relevant combo boxes according to the active radio button (`radioButton_us`, `radioButton_pottery`, `radioButton_materiali`, `radioButton_tomba`, or `radioButton_struttura`), queries the database via the appropriate `DB_MANAGER` method, updates `DATA_LIST` and the record counter, populates the form fields, and refreshes `iconListWidget` with thumbnail icons for each matched media record; a localized warning or informational message box is displayed if no search criteria are provided or no records are found.

##### getDirectoryVideo(self)

Opens a directory selection dialog that allows the user to import `.mp4` video files in bulk into the database. For each video found, it extracts a frame thumbnail using OpenCV, resizes it, and saves both the thumbnail and a resized video copy to the configured thumbnail path; new records are inserted into the media and media-thumbnail database tables, while videos already present in the database are loaded for display without re-insertion. If the thumbnail/video storage path has not been configured, a localized informational message is displayed (supporting Italian, German, and English), and any filename containing special characters triggers a localized warning.

##### getDirectory(self)

*No description available.*
Opens a directory selection dialog and processes all supported image files (`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff` in both upper and lower case) found within the chosen directory. For each image, it checks whether the file already exists in the database by its filepath; if not, it inserts a new media record, generates a thumbnail and a resized version using `Media_utility` and `Media_utility_resize`, inserts the corresponding thumbnail record, and adds the image as an icon item to `iconListWidget`. If the configured thumbnail path is not set, an informational message is displayed in the active language (`it`, `de`, or default English) prompting the user to configure the path before proceeding.

##### insert_record_media(self, mediatype, filename, filetype, filepath)

*No description available.*
Inserts a new media record into the database by constructing a media values object with the provided `mediatype`, `filename`, `filetype`, and `filepath` parameters, along with a default description of `'Insert description'` and a default tag of `"['imagine']"`. The new record is assigned an ID incremented from the current maximum ID in the mapped table. Returns `1` on successful insertion, or `0` if the operation fails — silently handling integrity constraint violations (e.g., duplicate entries) and displaying a warning dialog for all other unexpected errors.

##### insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)

*No description available.*
```python
def insert_record_mediathumb(self, media_max_num_id, mediatype, filename, filename_thumb, filetype, filepath_thumb, filepath_resize)
```

Inserts a new media thumbnail record into the database by assigning the next available ID and passing the provided metadata to `DB_MANAGER.insert_mediathumb_values`. The resulting data object is then committed to the database session via `DB_MANAGER.insert_data_session`. Returns `1` on successful insertion, or `0` if the operation fails — silently suppressing integrity constraint violations (such as duplicate thumbnail entries) and displaying a warning dialog for all other exceptions.

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

*No description available.*
Searches the database for records matching a specified field-value pair within a given table class. Constructs a search dictionary from the provided `field` and `value`, removes any empty entries using `Utility.remove_empty_items_fr_dict`, then executes a boolean query via `DB_MANAGER.query_bool`. Returns the result of the query.

##### on_pushButton_sort_pressed(self)

*No description available.*
Opens a `SortPanelMain` dialog pre-populated with `self.SORT_ITEMS`, allowing the user to select sort fields and order type. Upon dialog completion, the selected items are converted using `self.CONVERSION_DICT` and used to re-query the current record set via `self.DB_MANAGER.query_sort`, replacing `self.DATA_LIST` with the sorted results. The browse status is set to `"b"`, the sort status is set to `"o"`, record counters are reset, and the fields are refreshed to display the first record in the sorted list.

##### insert_new_row(self, table_name)

insert new row into a table based on table_name

##### remove_row(self, table_name)

remove row into a table based on table_name

##### remove_rowall(self, table_name)

remove row into a table based on table_name

##### openWide_image(self)

*No description available.*
Opens selected items from `iconListWidget` for full viewing based on their media type. For each selected item, the method queries the `MEDIA_THUMB` database table to determine whether the media file is a video, an image, or another type, and constructs the full file path by combining the stored `path_resize` value with the configured thumbnail resize base path, handling both URL-based and local filesystem paths. If the item is identified as a video, it is opened via the operating system's native file handler; if identified as an image, it is displayed in an `ImageViewer` dialog.

##### charge_sito_list(self)

*No description available.*
Retrieves a distinct list of site values from the `site_table` database table by querying the `sito` column via the `DB_MANAGER.group_by` method, then converts the result using `UTILITY.tup_2_list_III`. Any empty string entries are removed from the list, and the remaining values are sorted in ascending order before being returned.

**Returns:** A sorted list of site name strings.

##### charge_area_us_list(self)

*No description available.*
Retrieves a distinct list of area values from the `us_table` database table by delegating to the database manager's `group_by` method and converting the result using the utility's `tup_2_list_III` method. Any empty string entries are silently removed from the list. The resulting list is sorted in ascending order before being returned.

##### charge_us_us_list(self)

Retrieves a sorted list of unique US (Stratigraphic Unit) values from the `us_table` database table by querying the `us` column via a `group_by` operation. The raw result is converted from tuples to a list using `tup_2_list_III`, after which any empty string entries are silently removed. The resulting list is sorted in ascending order before being returned.

##### charge_sigla_us_list(self)

Retrieves a sorted list of unique structure sigla (abbreviation codes) from the `struttura_table` database table by querying the `sigla_struttura` column via a `group_by` operation. The raw result is converted from tuple format using `tup_2_list_III`, and any empty string entries are silently removed before sorting. The method returns the cleaned, sorted list of sigla values.

##### charge_nr_us_list(self)

*No description available.*
Retrieves a sorted list of unique `numero_struttura` values from the `struttura_table` database table by querying via the `DB_MANAGER.group_by` method and converting the result using `UTILITY.tup_2_list_III`. Any empty string entries are removed from the list before sorting. Returns the cleaned, sorted list of structure numbers.

##### generate_US(self)

*No description available.*
Reads tag entries from `tableWidgetTags_US` via `table2dict`, then queries the database for matching US (Stratigraphic Unit) records using each tag's site, area, and US identifiers. If no matching record is found for the first tag entry, the method prompts the user (in Italian, German, or English depending on `self.L`) to either create a new US record via `DB_MANAGER.insert_number_of_us_records` or abort the operation. If matching records are found, the method compiles and returns a list of entries containing each record's `id_us`, the string `'US'`, and the string `'us_table'`.

##### remove_US(self)

*No description available.*
Iterates over a tags list retrieved from `self.tableWidgetTags_US` via `self.table2dict`, and for each entry constructs a search dictionary keyed on `sito`, `area`, and `us` to query the database using `self.DB_MANAGER.query_bool`. Results are removed from `record_us_list`, and the corresponding `[id_us, 'US', 'us_table']` entries are removed from `us_list`. Returns the resulting `us_list`.

> **Note:** The method calls `list.remove()` on both `record_us_list` and `us_list`, which are initialized as empty lists within the method body; the practical effect of these removal operations at runtime is not fully determinable from the provided source alone.

##### generate_Pottery(self)

Reads pottery tag entries from `self.tableWidgetTags_POT` via `self.table2dict`, then queries the database for matching `POTTERY` records using each tag's `id_number`, `sito`, `area`, and `us` fields. If no matching record is found, a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompts the user to create a new pottery record via `self.DB_MANAGER.insert_number_of_pottery_records`; if the user cancels, the operation is aborted. If matching records exist, the method returns a list of entries in the form `[id_rep, 'CERAMICA', 'pottery_table']` for each found record.

##### remove_pottery(self)

*No description available.*
Removes pottery records from the dataset by querying the database for entries matching tag data extracted from the `tableWidgetTags_POT` widget. For each tag entry, a search dictionary is constructed using `id_number` and `sito` fields, and the corresponding `POTTERY` record is removed from the working list via a boolean query against `DB_MANAGER`. Returns a list of remaining records formatted as `[id_rep, 'CERAMICA', 'pottery_table']` tuples.

##### generate_Reperti(self)

Queries the database for material inventory records matching site and inventory number pairs extracted from the `tableWidgetTags_MAT` widget. If no matching record is found, displays a localized warning dialog (Italian, German, or English based on `self.L`) prompting the user to create the missing record; if confirmed, calls `DB_MANAGER.insert_number_of_reperti_records` to insert it and notifies the user of the result. If records are found, constructs and returns a list of tuples containing each record's `id_invmat`, the string `'REPERTO'`, and the string `'inventario_materiali_table'`.

##### remove_reperti(self)

*No description available.*
Iterates over the entries in the `tableWidgetTags_MAT` widget by converting it to a dictionary via `table2dict`, then attempts to remove from `record_mat_list` the results of a boolean database query (using `sito` and `numero_inventario` as search criteria) for each entry. For each remaining record in `record_mat_list`, it constructs a three-element list containing the record's `id_invmat`, the string `'REPERTO'`, and the string `'inventario_materiali_table'`. Returns the resulting list of these constructed entries.

##### generate_Tombe(self)

*No description available.*
Queries the database for tomb records (`TOMBA`) corresponding to each entry in the tags table widget (`tableWidgetTags_tomba`), matching on `sito` and `nr_scheda_taf` fields. If no matching record is found, a localized warning dialog (Italian, German, or English) prompts the user to create the missing record; upon confirmation, `insert_number_of_tomba_records` is called to insert it, or the operation is cancelled with an informational message. If records are found, the method returns a list of entries containing each tomb's `id_tomba`, the string `'TOMBA'`, and the string `'tomba_table'`.

##### remove_Tombe(self)

*No description available.*
Retrieves a list of tag entries from `tableWidgetTags_tomba` and, for each entry, constructs a search dictionary using the `sito` and `nr_scheda_taf` fields to query the database via `DB_MANAGER.query_bool`, removing the matching records from `record_tmb_list`. The method then iterates over the remaining records and builds a result list of three-element lists containing each record's `id_tomba`, the string `'TOMBA'`, and the string `'tomba_table'`. This compiled list is returned as the method's output.

##### generate_Tombe_2(self)

*No description available.*
Reads tag entries from `tableWidgetTags_tomba_2` via `table2dict` and queries the database for matching `STRUTTURA` records using the fields `sito`, `sigla_struttura`, and `numero_struttura`. If no matching record is found, a localized warning dialog (supporting Italian, German, and English based on `self.L`) prompts the user to create the missing `STRUTTURA` record via `DB_MANAGER.insert_struttura_records`; if the user cancels, the operation is aborted and the method returns `None`. On success — either from an existing record or a newly inserted one — the method returns a list of entries containing each record's `id_struttura`, the string `'STRUTTURA'`, and the string `'struttura_table'`.

##### remove_Tombe_2(self)

*No description available.*
Reads tag entries from `tableWidgetTags_tomba_2` by calling `table2dict`, then queries the database for matching `STRUTTURA` records using a search dictionary built from each tag's `sito`, `sigla_struttura`, and `numero_struttura` fields, removing each result from `record_tmb_list`. After processing all tags, it constructs and returns a list of entries, each containing the `id_struttura` value, the string `'STRUTTURA'`, and the string `'struttura_table'` for every remaining record.

##### table2dict(self, n)

*No description available.*
Accepts a table name string `n`, resolves it to the corresponding table attribute on the instance (stripping a leading `"self."` prefix if present), and iterates over all rows and columns of that table widget. For each row, it collects the text content of non-`None` cells into a sub-list, discarding any empty sub-lists. Returns a list of sub-lists, where each sub-list represents the non-empty cell values of a single row.

##### is_media_path_remote(self)

Check if the configured media thumbnail path is remote.

##### charge_data(self)

*No description available.*
Queries the database via `DB_MANAGER` using `MAPPER_TABLE_CLASS_thumb` as the target mapper class, storing the result in `self.DATA`. After retrieving the data, it immediately calls `open_images()` to process and display the loaded records.

##### clear_thumb_images(self)

*No description available.*
Clears all items from the `iconListWidget` widget by invoking its `clear()` method. This method resets the thumbnail image list to an empty state and is called internally by `open_images` prior to loading new thumbnail data.

##### open_images(self)

*No description available.*
Clears the current thumbnail list and loads a paginated subset of media records from `self.DATA` (from index `self.NUM_DATA_BEGIN` to `self.NUM_DATA_END`) into `self.iconListWidget` as icon items. Each item is populated with the media filename as its label, a `UserRole` data value, and an icon loaded from the resolved thumbnail path. When the media path is detected as remote and data is present, a localized `QProgressDialog` is displayed during loading, with support for cancellation; the pagination indices are reset to `0` and `25` respectively if all records have already been displayed.

##### on_pushButton_dir_video_pressed(self)

*No description available.*
Button press event handler that is triggered when the video directory push button is pressed. It delegates execution to `self.getDirectoryVideo()`, which handles the directory selection logic for video files.

##### on_pushButton_chose_dir_pressed(self)

*No description available.*
Button press event handler that is triggered when the user clicks the "choose directory" button. It delegates execution to `self.getDirectory()`, which handles the directory selection logic. This method serves as the UI callback binding between the button widget and the underlying directory retrieval functionality.

##### on_pushButton_addRow_US_pressed(self)

*No description available.*
Event handler triggered when the "Add Row" button for the US section is pressed. It delegates to `insert_new_row`, passing `'self.tableWidgetTags_US'` as the target table identifier, which inserts a new row into the `tableWidgetTags_US` widget.

##### on_pushButton_removeRow_US_pressed(self)

Handles the press event of the "Remove Row" button associated with the US tags table. Delegates to the `remove_row` method, passing `'self.tableWidgetTags_US'` as the target widget identifier to remove a row from `tableWidgetTags_US`.

##### on_pushButton_addRow_POT_pressed(self)

Handles the press event of the "Add Row" button associated with the POT table widget. Calls `self.insert_new_row` with the string identifier `'self.tableWidgetTags_POT'` to insert a new row into the POT tags table. This method follows the same pattern used by analogous add-row handlers for other table widgets in the interface.

##### on_pushButton_removeRow_POT_pressed(self)

Handles the press event of the "Remove Row" button associated with the POT table widget. Calls `self.remove_row('self.tableWidgetTags_POT')` to remove a row from `tableWidgetTags_POT`. This method follows the same pattern as its counterparts for the US and MAT table widgets.

##### on_pushButton_addRow_MAT_pressed(self)

*No description available.*
Slot method triggered when the "Add Row" button for the MAT section is pressed. It delegates execution to `insert_new_row`, passing `'self.tableWidgetTags_MAT'` as the target table widget identifier. This results in a new row being inserted into the `tableWidgetTags_MAT` table widget.

##### on_pushButton_removeRow_MAT_pressed(self)

*No description available.*
Handler triggered when the "Remove Row" button for the MAT section is pressed. It delegates to the `remove_row` method, passing `'self.tableWidgetTags_MAT'` as the target table identifier to remove a row from the `tableWidgetTags_MAT` widget.

##### on_pushButton_addRow_tomba_pressed(self)

*No description available.*
Handler triggered when the `pushButton_addRow_tomba` button is pressed. It calls `self.insert_new_row` with the target `'self.tableWidgetTags_tomba'`, inserting a new row into that table widget.

##### on_pushButton_removeRow_tomba_pressed(self)

*No description available.*
Slot method triggered when the "removeRow_tomba" push button is pressed. It calls `self.remove_row` with the target `'self.tableWidgetTags_tomba'`, removing a row from the corresponding table widget. This method serves as the event handler for row deletion operations on the `tableWidgetTags_tomba` widget.

##### on_pushButton_addRow_tomba_2_pressed(self)

Handles the press event of the `pushButton_addRow_tomba_2` button by invoking `insert_new_row` with the target widget identifier `'self.tableWidgetTags_tomba_2'`. This inserts a new row into the `tableWidgetTags_tomba_2` table widget. It is the counterpart to `on_pushButton_removeRow_tomba__2_pressed`, which removes a row from the same table.

##### on_pushButton_removeRow_tomba__2_pressed(self)

Handles the press event of the `pushButton_removeRow_tomba__2` button. Calls `self.remove_row` with the string `'self.tableWidgetTags_tomba_2'` as the target, removing a row from the `tableWidgetTags_tomba_2` table widget.

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

*No description available.*
Deletes a file from the filesystem by removing the file located at the concatenated path formed by `path` and `img_name`. This method is used to eliminate thumbnail images, as indicated by its surrounding context. It delegates directly to `os.remove()` with no additional error handling or validation.

##### remove_img2(self, path, img_name)

*No description available.*
Removes an image file from the filesystem by concatenating `path` and `img_name` to form the full file path, then passing it to `os.remove()`. This method is part of a set of thumbnail deletion utilities alongside `remove_img1`, which performs the same operation. No return value is produced.

##### on_pushButton_remove_thumb_pressed(self)

*No description available.*
Handles the press event of the "remove thumbnail" button by prompting the user with a language-specific confirmation dialog (Italian, German, or English, based on `self.L`) before proceeding with deletion. If confirmed and items are selected in `iconListWidget`, it iterates over each selected item, removes the corresponding thumbnail record from the database via `delete_thumb_from_db_sql`, and deletes both the full-size thumbnail file and the resized image file from their respective directories using `remove_img1` and `remove_img2`. After deletion, the widget list is cleared and refreshed via `charge_data` and `view_num_rec`; if no items are selected, a warning message is displayed instead.

##### on_pushButton_remove_tags_pressed(self)

*No description available.*
Handles the press event of the "Remove Tags" button by removing one or more selected tags from the database via `DB_MANAGER.remove_tags_from_db_sql()`. If no item is selected in `tableWidget_tags`, a localized warning message is displayed prompting the user to select a tag first. If items are selected, the user is presented with a localized confirmation dialog (supporting Italian, German, and a default language); upon confirmation, the method iterates over the selected items and removes the corresponding tag — identified by the value in cell `(0, 0)` of `tableWidget_tags` — from the database, then notifies the user of the result.

##### on_pushButton_remove_alltag_pressed(self)

*No description available.*
Handles the press event of the "remove all tags" button by retrieving all currently selected items from `iconListWidget` and, if at least one item is selected, presenting a localized confirmation dialog (Italian, German, or English, based on `self.L`) warning that the action is irreversible. Upon confirmation, it iterates over each selected item, retrieves the original filename via `item.text()`, and calls `self.DB_MANAGER.remove_alltags_from_db_sql()` to remove all associated tags from the database, catching and displaying any exceptions that occur. After processing, it clears `iconListWidget`, reloads the data via `charge_data()` and `view_num_rec()`, and notifies the user of success; if no items are selected, a localized warning is displayed prompting the user to select at least one thumbnail.

##### on_pushButton_openMedia_pressed(self)

*No description available.*
Event handler triggered when the "Open Media" push button is pressed. It invokes `charge_data()` to load the data, then calls `view_num_rec()` to update the record count display. This method serves as the entry point for initializing and rendering the media data in the current view.

##### on_pushButton_next_rec_pressed(self)

*No description available.*
Advances the current data view to the next page of records when the "next" button is pressed. If `NUM_DATA_END` has not yet reached the total length of `DATA`, both `NUM_DATA_BEGIN` and `NUM_DATA_END` are incremented by 25 to shift the visible range forward. After updating the range, it refreshes the record counter display via `view_num_rec()` and loads the corresponding images via `open_images()`.

##### on_pushButton_prev_rec_pressed(self)

*No description available.*
Handles the "previous records" button press event by navigating to the preceding set of records. If `NUM_DATA_BEGIN` is greater than 0, it decrements both `NUM_DATA_BEGIN` and `NUM_DATA_END` by 25, then calls `view_num_rec()` and `open_images()` to refresh the display. If `NUM_DATA_BEGIN` is already at 0, no action is taken.

##### on_pushButton_first_rec_pressed(self)

*No description available.*
Resets the record navigation to the beginning of the dataset by setting `NUM_DATA_BEGIN` to `0` and `NUM_DATA_END` to `25`. After updating the pagination bounds, it calls `view_num_rec()` to refresh the record counter display and `open_images()` to load the corresponding images for the first page of records.

##### on_pushButton_last_rec_pressed(self)

*No description available.*
Handles the press event of the "last record" button by navigating to the final page of records in the dataset. Sets `NUM_DATA_BEGIN` to the last 25 records offset (calculated as the total dataset length minus 25) and `NUM_DATA_END` to the total length of `DATA`. After updating the record range boundaries, it calls `view_num_rec()` to refresh the record count display and `open_images()` to load the corresponding images for the new range.

##### update_if(self, msg)

*No description available.*
Conditionally triggers a record update based on the value of the `msg` parameter. If `msg` equals `1`, the method calls `update_record()` and, upon success, rebuilds `DATA_LIST` by querying and re-sorting the updated records using either the default ascending sort or the current sort configuration, then sets the browse status to `"b"`. Returns `1` if the update succeeds, `0` if `update_record()` reports failure, or `None` if `msg` is not `1`.

##### update_record(self)

*No description available.*
Attempts to persist the current record to the database by calling `self.DB_MANAGER.update` with the mapped table class, primary key identifier, table fields, and the result of `self.rec_toupdate()`. Returns `1` on success or `0` on failure. If an exception occurs, the error details are written to `error_encodig_data_recover.txt` in the `pyarchinit_Report_folder` directory, and a localized warning dialog is displayed to the user in Italian (`it`), German (`de`), or English (default).

##### rec_toupdate(self)

*No description available.*
Resets `self.DATA_LIST` to an empty list and repopulates it by querying the database for all records in the table mapped by `self.MAPPER_TABLE_CLASS_thumb`. For SQLite connections, it collects only the IDs from the query result without appending records to `self.DATA_LIST`; for other database servers, it collects the IDs, sorts the results in ascending order by `self.ID_TABLE_THUMB` using `query_sort`, and appends the sorted records to `self.DATA_LIST`.

##### view_num_rec(self)

*No description available.*
Updates the record navigation labels in the UI to reflect the current pagination state of the data set. It calculates the effective end index by clamping `NUM_DATA_END` to the actual length of `DATA` when the former exceeds the latter, then sets `label_num_tot_immagini` to the total number of records and `label_img_visualizzate` to a formatted string indicating the range of currently displayed records (e.g., `"da 1 to 10"`).

##### on_toolButton_tags_on_off_clicked(self)

*No description available.*
Event handler triggered when the `toolButton_tags_on_off` tool button is clicked. It retrieves the currently selected items from `iconListWidget` and, if at least one item is selected, calls `open_tags()`. If no items are selected, the method takes no action.

##### open_tags(self)

*No description available.*
Retrieves and displays entity association data for the currently selected items in `iconListWidget`, but only when `toolButton_tags_on_off` is in a checked state. For each selected media item, the method queries the database for matching `MEDIA` and `MEDIATOENTITY` records, then resolves the linked entity details based on the entity type (`US`, `CERAMICA`, `REPERTO`, `TOMBA`, `STRUTTURA`, `TMA`, or `UT`), building a formatted descriptive string for each association. The resulting list of entity mappings is populated into `tableWidget_tags`; if no items are selected, all existing rows in that table are cleared.

##### charge_records(self)

*No description available.*
Retrieves and loads an ordered list of records from the database into `self.DATA_LIST`. It executes a single ascending query on the mapped table class (`MAPPER_TABLE_CLASS_thumb`), sorted by the `media_filename` field, using `self.DB_MANAGER.query_ordered`. This approach replaces a previously used double-query pattern to improve performance.

##### datestrfdate(self)

*No description available.*
Retrieves the current date and formats it as a string in `DD-MM-YYYY` format. The method uses `date.today()` to obtain today's date and applies `strftime("%d-%m-%Y")` to produce the formatted string. Returns the formatted date string.

##### yearstrfdate(self)

*No description available.*
Retrieves the current date and extracts the four-digit year component from it. The method uses `date.today()` to obtain today's date and formats it using `strftime("%Y")`, returning the year as a string.

##### set_rec_counter(self, t, c)

*No description available.*
Sets the record counter state by assigning the total record count `t` to `self.rec_tot` and the current record index `c` to `self.rec_corr`. Updates the corresponding UI labels `label_rec_tot` and `label_rec_corrente` to display the new values as strings.

##### set_LIST_REC_TEMP(self)

Populates the `DATA_LIST_REC_TEMP` list with the current text values retrieved from five combo box widgets: `comboBox_sito` (Site), `comboBox_area` (Area), `comboBox_us`, `comboBox_sigla_struttura`, and `comboBox_nr_struttura`. Each value is cast to a string before being stored in the list. The resulting list represents a temporary snapshot of the current record's field values as displayed in the UI.

##### empty_fields(self)

*No description available.*
Clears all input fields in the form by setting the editable text of each combo box to an empty string. The method resets the following controls in sequence: `comboBox_sito`, `comboBox_area`, `comboBox_us`, `comboBox_sigla_struttura`, and `comboBox_nr_struttura`. This is typically called to reset the form to a blank state.

##### fill_fields(self, n)

*No description available.*
Populates the form fields with data from the record at position `n` in `DATA_LIST`, storing the index in `self.rec_num`. The method accepts an integer parameter `n` (defaulting to `0`) that identifies which record to display. The active field-population logic targeting `comboBox_sito`, `comboBox_area`, and `comboBox_us` is currently commented out; see implementation for the complete field-filling behavior.

##### setComboBoxEnable(self, f, v)

Set enabled state for widgets - uses getattr instead of eval for security

##### setComboBoxEditable(self, f, n)

Set editable state for widgets - uses getattr instead of eval for security

##### setTableEnable(self, t, v)

Set enabled state for table widgets - uses getattr instead of eval

##### set_LIST_REC_CORR(self)

*No description available.*
Resets `DATA_LIST_REC_CORR` to an empty list and repopulates it by iterating over `TABLE_FIELDS`, extracting the corresponding field values from the current record (`DATA_LIST[REC_CORR]`) as strings. Each field value is retrieved via `eval` and appended to `DATA_LIST_REC_CORR`, producing a list of string representations of the current record's field values.

##### records_equal_check(self)

*No description available.*
Compares the current record's field values (`DATA_LIST_REC_CORR`) against a temporary record snapshot (`DATA_LIST_REC_TEMP`) to determine whether the two are equal. It first calls `set_LIST_REC_CORR()` to populate `DATA_LIST_REC_CORR` with the current record's data, then performs a direct equality comparison between the two lists. Returns `0` if the records are equal, or `1` if they differ.

##### tableInsertData(self, t, d)

Set the value into alls Grid

