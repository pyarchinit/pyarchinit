# pyarchinitDockWidget.py

## Overview

This file contains 37 documented elements.

## Classes

### PyarchinitPluginDialog

`PyarchinitPluginDialog` is a QGIS dock widget that serves as the main plugin interface for pyArchInit, an archaeological data management system. It provides a tabbed UI loaded from `pyarchinit_plugin.ui` that integrates workflow diagrams for excavation, anthropology, and survey contexts, an embedded multilingual tutorial viewer supporting ten languages, and a web view displaying the pyarchinit.org website. The class also exposes buttons that launch subordinate form dialogs for managing archaeological records such as sites, stratigraphic units, structures, burials, individuals, finds, topographic units, and PDF exports.

**Inherits from**: QgsDockWidget, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes a `PyarchinitPluginDialog` instance by calling the parent constructor, setting up the UI, and configuring core attributes including the interface reference, plugin directory, and tutorials base path. Detects the current language and initializes web views, tutorial tab, workflow tabs, and modern diagrams. Connects all toolbar buttons to their respective handler methods and sets up button tooltips.

##### runSite(self)

*No description available.*
Instantiates the `pyarchinit_Site` plugin GUI component, imported from `.tabs.Site`, passing the current `iface` object to its constructor. Calls `show()` on the resulting instance to display the interface, then stores the reference in `self.pluginGui`.

##### runPer(self)

*No description available.*
Instantiates and displays the `pyarchinit_Periodizzazione` GUI component by importing it from the `.tabs.Periodizzazione` module. The method creates a new instance of `pyarchinit_Periodizzazione`, passing `self.iface` as a parameter, then calls `show()` to make the dialog visible. The resulting instance is stored in `self.pluginGui` for later reference.

##### runStruttura(self)

*No description available.*
Instantiates the `pyarchinit_Struttura` GUI component, imported from `.tabs.Struttura`, passing the current `iface` instance to its constructor. Displays the resulting dialog or panel by calling `show()`, then assigns the created instance to `self.pluginGui` for later reference.

##### runUS(self)

*No description available.*
Instantiates and displays the `pyarchinit_US` plugin GUI, imported from `.tabs.US_USM`. The method creates a new `pyarchinit_US` object using the current `iface` instance, calls `show()` to make the dialog visible, and stores the reference in `self.pluginGui`.

##### runInr(self)

*No description available.*
Instantiates and displays the `pyarchinit_Inventario_reperti` GUI component, imported from the `.tabs.Inv_Materiali` module. The method initializes the plugin interface by passing `self.iface` to the constructor and calls `show()` to make the widget visible. The resulting instance is stored in `self.pluginGui` for later reference.

##### runGisTimeController(self)

*No description available.*
Instantiates and displays the `pyarchinit_Gis_Time_Controller` dialog by importing it from the `.tabs.Gis_Time_controller` module. The dialog is initialized with the current `iface` instance and made visible via its `show()` method. A reference to the active dialog is stored in `self.pluginGui`.

##### runUpd(self)

*No description available.*
Instantiates and displays the `pyarchinit_Upd_Values` graphical user interface, imported from the `.tabs.Upd` module. The method passes the current `iface` object to the GUI constructor, calls `show()` to make the dialog visible, and stores the resulting instance in `self.pluginGui` for later reference.

##### runConf(self)

Opens the plugin configuration dialog by instantiating `pyArchInitDialog_Config` from the `pyarchinitConfigDialog` module and displaying it via its `show()` method. The resulting dialog instance is stored in `self.pluginGui` for later reference.

##### runInfo(self)

*No description available.*
Instantiates and displays the `pyArchInitDialog_Info` dialog by importing it from `.gui.pyarchinitInfoDialog`. The method calls `show()` on the created instance to make the dialog visible, then assigns it to `self.pluginGui` to maintain a reference to the active GUI component.

##### runImageViewer(self)

*No description available.*
Instantiates and displays the `Main` image viewer component imported from the `.tabs.Image_viewer` module. The resulting viewer instance is shown immediately and stored as `self.pluginGui` for later reference.

##### runImages_directory_export(self)

Instantiates and displays the `pyarchinit_Images_directory_export` dialog by importing it from the `.tabs.Images_directory_export` module. Calls `show()` on the newly created instance to make it visible, then assigns it to `self.pluginGui` to maintain a reference to the active plugin GUI component.

##### runTomba(self)

*No description available.*
Instantiates and displays the `pyarchinit_Tomba` plugin interface, imported from the `.tabs.Tomba` module. The method creates a new `pyarchinit_Tomba` object using the current `iface` reference, calls its `show()` method to render it visible, and assigns the instance to `self.pluginGui`.

##### runSchedaind(self)

*No description available.*
Instantiates the `pyarchinit_Schedaind` plugin class from the `tabs.Schedaind` module, passing the current interface (`self.iface`) as a parameter. Calls `show()` on the resulting instance to display the Schedaind panel, then assigns it to `self.pluginGui` as the active plugin GUI component.

##### runDetsesso(self)

*No description available.*
Instantiates the `pyarchinit_Detsesso` plugin dialog, imported from `.tabs.Detsesso`, passing the current `iface` object to its constructor. Calls `show()` to display the dialog and assigns the resulting instance to `self.pluginGui`.

##### runDeteta(self)

*No description available.*
Instantiates the `pyarchinit_Deteta` plugin class, imported from `.tabs.Deteta`, passing the current `iface` object to its constructor. Calls `show()` on the resulting instance to display its interface, then assigns it to `self.pluginGui` as the active plugin GUI reference.

##### runUT(self)

*No description available.*
Instantiates the `pyarchinit_UT` plugin dialog by importing it from `.tabs.UT` and initializing it with the current `iface` instance. Calls `show()` to display the dialog and assigns the resulting instance to `self.pluginGui`.

##### runPDFadministrator(self)

Instantiates a `pyarchinit_pdf_export` object from the `Pdf_export` module, passing the current interface (`self.iface`) as a parameter, and displays the resulting dialog by calling its `show()` method. The active plugin GUI reference (`self.pluginGui`) is then updated to point to the newly created PDF export instance.

##### detect_language(self)

Detect QGIS locale and return language code

##### get_icon(self, icon_name)

Get QIcon from resources/icons folder

##### remove_old_tabs(self)

Remove old tabs that are replaced by workflow tabs

##### setup_button_tooltips(self)

Setup descriptive tooltips for relationship diagram buttons

##### setup_webviews(self)

Setup pyarchinit.org in the main tab

##### setup_tutorial_tab(self)

Setup embedded tutorial viewer in tutorial tab

##### load_tutorial_list(self)

Load tutorials for current language

##### on_tutorial_language_changed(self, index)

Handle tutorial language change

##### on_tutorial_selected(self, current, previous)

Load selected tutorial content

##### markdown_to_html(self, md_content, base_path)

Convert markdown to styled HTML with proper image handling

##### show_tutorial_placeholder(self)

Show placeholder when tutorial not found

##### show_tutorial_error(self, error)

Show error message

##### setup_workflow_tabs(self)

Create new tabs with interactive workflow diagrams

##### setup_modern_diagrams(self)

Setup modern HTML diagrams in service tabs

##### get_pyarchinit_fallback_html(self)

Return HTML content for when QWebEngine is not available

## Functions

### replace_image(match)

Processes a Markdown image match object and converts it to an HTML `<img>` element wrapped in a centered `<div>` with an italic caption. When a `base_path` is provided, the function resolves the image path (relative or absolute), reads the file, and encodes its contents as a base64 data URI using a MIME type derived from the file extension (`.png`, `.jpg`, `.jpeg`, `.gif`, or `.webp`); if the file cannot be read or does not exist, the function falls back to using the original path directly as the `src` attribute. In both cases the returned HTML applies inline styles for centering, max-width, border-radius, and box-shadow, and renders the alt text as a styled caption below the image.

**Parameters:**
- `match`

### create_button(label_key, style, tooltip)

Helper to create button with icon

**Parameters:**
- `label_key`
- `style`
- `tooltip`

