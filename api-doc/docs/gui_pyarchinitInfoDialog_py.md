# gui/pyarchinitInfoDialog.py

## Overview

This file contains 4 documented elements.

## Classes

### pyArchInitDialog_Info

*No description available.*
A `QDialog` subclass that displays a multi-tabbed information dialog for the pyArchInit QGIS plugin, loaded from the `pyarchinitInfoDialog.ui` UI file. The dialog presents four tabs — About, System, Dependencies, and Links & Support — covering plugin metadata, runtime environment details, availability of required Python packages, and external resource links. UI labels are rendered in one of ten supported languages (`it`, `en`, `de`, `es`, `fr`, `ar`, `ca`, `ro`, `pt`, `el`) determined at construction time from the QGIS locale setting, falling back to English if the locale is not recognized.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

Initializes the `QDialog`-based instance by setting up the UI, storing the database reference, and determining the user locale from `QgsSettings` to load the appropriate translation dictionary from `I18N`. Applies the application theme via `ThemeManager` (silently ignoring any exceptions), reads the plugin version from `metadata.txt` using `configparser`, and sets the window title from the resolved translation dictionary. Finally, calls `_build_ui()` to construct the tabbed interface within the dialog.

##### open_link(self, url)

Open a link in the system browser.

