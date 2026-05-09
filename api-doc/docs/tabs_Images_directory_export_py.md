# tabs/Images_directory_export.py

## Overview

This file contains 9 documented elements.

## Classes

### pyarchinit_Images_directory_export

*No description available.*
A QDialog subclass that provides a user interface for exporting media images associated with archaeological records — including stratigraphic units (US), finds (INVENTARIO_MATERIALI), pottery (POTTERY), graves (TOMBA), and structures (STRUTTURA) — into organized local directory trees. The export structure varies by the selected `comboBox_export` index, supporting multiple organizational schemes such as flat per-entity folders, hierarchical period/phase/entity folders, and groupings by material definition or specific form. The dialog connects to the configured database on initialization, populates a site selection list, and resolves media paths for both local and remote (HTTP, Cloudinary, etc.) storage via the static `build_media_path` method.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### build_media_path(base_path, path_resize)

Build full media path handling both local and remote paths.
If path_resize is already a full path (unibo://, http://, etc.), use it directly.

##### __init__(self, parent, db)

Initializes the dialog by calling the parent `QDialog.__init__` constructor with the optional `parent` argument, then sets up the UI via `self.setupUi(self)`. Applies the application theme using `ThemeManager.apply_theme` and adds a theme toggle button to the form. Attempts to establish a database connection via `self.connect()`, silently suppressing any exceptions, and then populates the dialog's list by calling `self.charge_list()`.

##### connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object and retrieving its connection string via `conn_str()`, then passing it to `get_db_manager()` with singleton mode enabled. If the connection attempt raises an exception, the method inspects the error message and displays a localized warning dialog via `QMessageBox`: one indicating a failed connection requiring a QGIS restart (when the error references "no such table"), and another prompting the user to report an unexpected bug to the developer for all other errors.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_image_export` directory located under `self.HOME` using the appropriate system command for the current operating system. On Windows, it uses `os.startfile`; on macOS ("Darwin"), it invokes `open` via `subprocess.Popen`; on all other systems, it uses `xdg-open` via `subprocess.Popen`.

##### charge_list(self)

*No description available.*
Populates the site combo box (`comboBox_sito`) with a sorted list of site values retrieved from the `site_table` database table. The raw results are converted from tuples to a plain list via `UTILITY.tup_2_list_III`, and any empty string entries are removed before the list is sorted and loaded into the combo box. The combo box is cleared before new items are added to ensure no stale entries remain.

##### on_pushButton_exp_icons_pressed(self)

Slot handler triggered when the "export icons" push button is pressed. It queries the database for records of entity types US, INVENTARIO_MATERIALI, POTTERY, TOMBA, and STRUTTURA belonging to the site selected in `comboBox_sito` and the year selected in `comboBox_year`, then exports associated media images into a structured directory hierarchy under `pyarchinit_image_export` within `self.HOME`. The specific directory structure and entity types exported are determined by the current index of `comboBox_export`, with folder naming adapted to the active interface language (`self.L`); a localized `QMessageBox` is displayed upon completion or if no images are found, and any exception raised during the process is caught and reported via a localized warning dialog.

##### db_search_DB(self, table_class, field_1, value_1, field_2, value_2, anno)

*No description available.*
Queries the database for records of the specified `table_class` using one or two field/value pairs as search criteria, with an optional `anno` (year) parameter that maps to the appropriate year field depending on the table class (`anno_scavo` for `'US'`, `years` for `'REPERTI'`, or `anno` for `'POTTERY'`). Before executing the query, empty items are removed from the constructed search dictionary via `Utility.remove_empty_items_fr_dict`. Returns the result of `DB_MANAGER.query_bool` applied to the cleaned search dictionary and the target table class.

