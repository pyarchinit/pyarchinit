# tabs/Image_search.py

## Overview

This file contains 23 documented elements.

## Classes

### pyarchinit_Image_Search

Dialog for global image search across all entity types.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface, parent)

Initializes the `Ricerca Immagini` (Image Search) dialog by calling the parent constructor, setting up the UI layout via `setupUi`, and applying the application theme through `ThemeManager`. Establishes a database connection, initializes utility and state attributes (`UTILITY`, `DB_MANAGER`, `DB_SERVER`, `search_results`, `current_selection`), and configures UI connections and the right-click context menu. Completes initialization by loading the initial site data via `load_sites`.

##### connect_to_db(self)

Connect to the database.

##### setup_connections(self)

Setup signal/slot connections.

##### setup_context_menu(self)

Setup context menu for right-click on results list.

##### show_context_menu(self, pos)

Show context menu at the given position.

##### load_sites(self)

Load available sites into combobox.

##### on_sito_changed(self, sito)

Load areas when site changes.

##### on_entity_type_changed(self, entity_type)

Show/hide inventory number field based on entity type.

##### on_untagged_toggled(self, checked)

Enable/disable entity filters when untagged mode is active.

##### clear_filters(self)

Clear all search filters.

##### perform_search(self)

Execute the search based on current filters.

##### display_untagged_results(self, results)

Display untagged search results.

##### display_tagged_results(self, results, entity_type)

Display tagged search results.

##### on_selection_changed(self)

Update details panel when selection changes.

##### clear_details(self)

Clear the details panel.

##### get_original_filepath(self)

Get the original file path for the current selection.

##### get_resize_filepath(self)

Get the resize image path for the current selection.

Pattern: thumb_resize_str (from config) + path_resize (from MEDIA_THUMB table)

##### goto_record(self)

Open the form for the associated record.

##### open_image(self)

Open the selected image in the ImageViewer dialog.

##### export_image(self)

Export the selected image to a user-chosen location.

##### open_media_manager(self)

Open the Media Manager dialog.

