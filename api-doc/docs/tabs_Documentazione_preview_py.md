# tabs/Documentazione_preview.py

## Overview

This file contains 6 documented elements.

## Classes

### pyarchinit_doc_preview

*No description available.*
A QDialog subclass that provides a preview interface for documentation records stored in the `pyarchinit_documentazione` database table. On initialization, it establishes a database connection, applies the active UI theme, and renders a map preview using a `QgsMapCanvas` widget populated via `pyQGIS.loadMapPreviewDoc`. The class holds class-level state for the current record index, data list, and file paths used by the pyArchInit documentation system.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface, docstr)

Initializes the form widget by calling the parent constructor, setting up the UI, and applying the current theme along with a theme toggle button. Configures a `QgsMapCanvas` instance with a white background and integrates it into the layout alongside the document preview widget, then calls `draw_preview()` to render the initial preview. Stores the provided `iface` and `docstr` references, instantiates a `Pyarchinit_pyqgis` object, and attempts a database connection via `DB_connect()`, silently suppressing any exceptions that occur.

##### DB_connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object and retrieving its connection string via `conn_str()`. It then obtains a database manager instance using `get_db_manager()` with the singleton pattern enabled, assigning the result to `self.DB_MANAGER`. If an exception occurs during this process, a warning dialog is displayed to the user containing the error details.

##### draw_preview(self)

*No description available.*
Constructs a GID filter string using the current record's ID from `ID_TABLE` and `DATA_LIST`, then loads the corresponding map preview layers via `self.pyQGIS.loadMapPreviewDoc`. The retrieved layers are displayed in a warning dialog listing their names, applied to `self.mapPreview`, and the view is zoomed to the full extent of the loaded layers.

##### testing(self, name_file, message)

*No description available.*
Opens a file at the path specified by `name_file` in write mode (`'w'`), writes the string representation of `message` to it, then closes the file. Both `name_file` and `message` are explicitly cast to `str` before use. This method does not return a value.

