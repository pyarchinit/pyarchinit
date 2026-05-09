# pyarchinitPlugin.py

## Overview

This file contains 51 documented elements.

## Classes

### PyArchInitPlugin

`PyArchInitPlugin` is the main entry point class for the pyArchInit QGIS plugin, responsible for initializing, registering, and tearing down all plugin UI components — including locale-aware toolbars, menus, dock widgets, and actions — across supported languages (Italian, English, German, and others). It manages plugin-wide configuration via `PARAMS_DICT` loaded from a `config.cfg` file, controls access to site management (cantiere) forms through a role-based permission system, and conditionally exposes experimental features based on the `EXPERIMENTAL` configuration value. On startup it also performs SQLite database integrity checks, initializes the StratiGraph offline sync subsystem, and installs the appropriate Qt translation file for the active locale.

**Inherits from**: object

#### Methods

##### is_experimental_enabled(self)

Check if experimental features are enabled, regardless of language setting.

##### load_config(self)

Load configuration from config.cfg file into PARAMS_DICT.

##### __init__(self, iface)

Initializes the plugin instance by storing the QGIS interface reference, setting `plugin_window` to `None`, and loading the appropriate translation file based on the current locale settings. The locale is resolved by checking whether the QGIS locale override flag is set, then mapping the resulting locale code via `LOCALE_MAPPING` to a full locale name (defaulting to `"it_IT"` if no valid locale is found), and installing the corresponding `.qm` translation file through `QCoreApplication.installTranslator`. Any exception raised during translation loading is logged as a warning via `QgsMessageLog`, after which `check_and_fix_sqlite_databases` is unconditionally called to perform startup database maintenance.

##### check_and_fix_sqlite_databases(self)

Check and fix macc field in all SQLite databases in the pyarchinit folder

##### fix_single_sqlite_database(self, db_path)

Fix macc field in a single SQLite database

##### initGui(self)

Initializes the plugin's graphical user interface by first loading the plugin configuration via `self.load_config()`, then reading the two-letter QGIS user locale from `QgsSettings` to determine which language branch (`'it'`, `'en'`, `'de'`, or a fallback default) to use for action labels. For each supported locale, the method creates and registers the main dock widget (`PyarchinitPluginDialog`), the primary toolbar (`"pyArchInit"`), a secondary site-management toolbar (`"pyArchInitCantiere"`), a `QMenu` added to the QGIS menu bar, and all plugin actions grouped into thematic `QToolButton` drop-downs covering data entry, interpretation, funerary archaeology, topography, documentation, fauna, analysis tools, and plugin management. Experimental actions (such as sex/age determination and image comparison) are conditionally added only when `self.is_experimental_enabled()` returns `True`, and stratigraphic synchronization is initialized via `self._init_stratigraph_sync()` at the end of each locale branch; Rust acceleration status is logged after all UI elements are constructed.

##### runSite(self)

*No description available.*
Instantiates and displays the `pyarchinit_Site` plugin GUI by importing it from the `.tabs.Site` module and invoking its `show()` method. The created instance is passed the current `iface` object during construction and subsequently stored as `self.pluginGui` for later reference.

##### runPer(self)

Opens the `pyarchinit_Periodizzazione` dialog by importing it from `.tabs.Periodizzazione`, instantiating it with the current `iface` reference, and displaying it via `show()`. The resulting GUI instance is stored in `self.pluginGui` for later reference.

##### runStruttura(self)

Instantiates the `pyarchinit_Struttura` dialog from the `tabs.Struttura` module, passing the current QGIS interface (`self.iface`) as a parameter, and displays it by calling `show()`. The resulting plugin GUI instance is stored in `self.pluginGui` for later reference.

##### runUS(self)

Opens the US/USM (Unità Stratigrafica / Unità Stratigrafica Muraria) plugin interface by instantiating `pyarchinit_US` with the current `iface` object and displaying it via `show()`. The resulting dialog instance is stored in `self.pluginGui` for later reference.

##### runAIQuery(self)

Open the AI Query Database dialog for natural language database queries

##### runTutorials(self)

Open the Tutorials and Documentation viewer dialog

##### runSamSegmentation(self)

Open the SAM Stone Segmentation dialog

##### runInr(self)

*No description available.*
Instantiates and displays the `pyarchinit_Inventario_reperti` dialog by importing it from the `.tabs.Inv_Materiali` module and calling its `show()` method with the current `iface` instance. The resulting dialog object is stored in `self.pluginGui` to maintain a reference and prevent premature garbage collection.

##### runTma(self)

*No description available.*
Instantiates the `pyarchinit_Tma` GUI component, imported from `.tabs.Tma`, passing the current `iface` object to its constructor. Calls `show()` on the resulting instance to display the interface, then stores the reference in `self.pluginGui` for later access.

##### runCampioni(self)

*No description available.*
Instantiates the `pyarchinit_Campioni` GUI class from the `tabs.Campioni` module, passing the current `iface` object to its constructor. Calls `show()` to display the resulting dialog or panel, then stores the instance in `self.pluginGui` for later reference.

##### runPottery(self)

*No description available.*
Instantiates and displays the `pyarchinit_Pottery` main application dialog by importing it from `.tabs.pyarchinit_Pottery_mainapp`. The method creates a new instance of `pyarchinit_Pottery`, passing the current `iface` object, and calls `show()` to render the GUI. The resulting dialog instance is stored in `self.pluginGui` for later reference.

##### runPotteryTools(self)

Opens the Pottery Tools dialog by instantiating a `PotteryToolsDialog` object from the `tabs.Pottery_tools` module, passing the current `iface` instance as a parameter. The dialog is displayed by calling its `show()` method, and the resulting instance is stored in `self.pluginGui` for later reference.

##### runGisTimeController(self)

Instantiates and displays the `pyarchinit_Gis_Time_Controller` dialog by importing it from `.tabs.Gis_Time_controller` and passing `self.iface` to its constructor. Calls `show()` on the resulting instance to make the GUI visible, then stores the reference in `self.pluginGui` to prevent it from being garbage-collected.

##### runTops(self)

*No description available.*
Instantiates and displays the `pyarchinit_TOPS` plugin interface by importing it from `.tabs.tops_pyarchinit` and initializing it with the current `iface` instance. Calls `show()` on the created instance to make the interface visible to the user. The resulting plugin instance is saved to `self.pluginGui` for later reference.

##### runPrint(self)

Instantiates a `pyarchinit_PRINTMAP` object by importing it from the `.tabs.PRINTMAP` module, passing `self.iface` as a constructor argument. Calls `show()` on the resulting instance to display the print map interface. The instantiated object is stored in `self.pluginGui` for later reference.

##### runGpkg(self)

Instantiates a `pyarchinit_GPKG` object from the `gpkg_export` module, passing the current `iface` instance as a parameter, and displays the resulting dialog by calling its `show` method. The created instance is retained in `self.pluginGui` to prevent it from being garbage collected. This method provides access to the GeoPackage export interface within the plugin.

##### runConf(self)

Opens the plugin configuration dialog by instantiating `pyArchInitDialog_Config` from `pyarchinitConfigDialog` and displaying it via `show()`. The resulting dialog instance is stored in `self.pluginGui` to maintain a reference to the active GUI component.

##### runDbUpdate(self)

Open config dialog and trigger database schema update.

##### runInfo(self)

*No description available.*
Instantiates and displays the `pyArchInitDialog_Info` dialog by importing it from `.gui.pyarchinitInfoDialog`. The resulting dialog instance is shown via its `show()` method and stored in `self.pluginGui` for later reference.

##### runImageViewer(self)

*No description available.*
Instantiates and displays the `Main` image viewer widget imported from `.tabs.Image_viewer`. The method calls `show()` on the newly created instance to make it visible, then stores a reference to it in `self.pluginGui` to preserve the object from garbage collection.

##### runImageSearch(self)

Opens the image search interface by instantiating `pyarchinit_Image_Search` with the current `iface` object and displaying it via `show()`. The resulting plugin widget is stored in `self.pluginGui` for later reference.

##### runGeoArchaeo(self)

Open the GeoArchaeo geostatistical analysis panel.

##### runMovecost(self)

Open the MoveCost least-cost path analysis dialog.

##### runTomba(self)

*No description available.*
Instantiates the `pyarchinit_Tomba` dialog by importing it from the `.tabs.Tomba` module and initializing it with the current `iface` instance. Calls `show()` to display the dialog to the user. The resulting plugin instance is stored in `self.pluginGui` for later reference.

##### runSchedaind(self)

*No description available.*
Instantiates the `pyarchinit_Schedaind` plugin tab, imported from `.tabs.Schedaind`, passing the current interface (`self.iface`) as a parameter. Calls `show()` on the resulting instance to display the individuals (*Individui*) form to the user. The instantiated plugin is stored in `self.pluginGui` for later reference.

##### runDetsesso(self)

*No description available.*
Instantiates the `pyarchinit_Detsesso` class from the `tabs.Detsesso` module, passing the current `iface` object to its constructor. Calls `show()` on the resulting instance to display the associated interface panel. The instantiated plugin is stored in `self.pluginGui` for later reference.

##### runDeteta(self)

Instantiates the `pyarchinit_Deteta` class from the `tabs.Deteta` module, passing the current interface (`self.iface`) as a parameter, and displays the resulting plugin window by calling its `show()` method. The created instance is stored in `self.pluginGui` for later reference.

##### runFauna(self)

Instantiates the `pyarchinit_Fauna` class from the `tabs.Fauna` module, passing the current interface (`self.iface`) as a parameter. Calls `show()` on the resulting instance to display the Fauna tab interface. The instantiated plugin is stored in `self.pluginGui` for later reference.

##### runUT(self)

*No description available.*
Instantiates the `pyarchinit_UT` plugin component by importing it from the `.tabs.UT` module and initializing it with the current interface (`self.iface`). Calls `show()` on the newly created instance to display its user interface. The instance is then stored in `self.pluginGui` for later reference.

##### runImages_directory_export(self)

*No description available.*
Instantiates the `pyarchinit_Images_directory_export` class imported from the `.tabs.Images_directory_export` module and displays its interface by calling `show()`. The resulting plugin instance is stored in `self.pluginGui` for later reference.

##### runComparision(self)

*No description available.*
Instantiates and displays the `Comparision` dialog by importing it from `.tabs.Images_comparison`. The newly created instance is shown via its `show()` method and stored in `self.pluginGui` to maintain a reference to the active plugin GUI.

##### runDbmanagment(self)

*No description available.*
Instantiates the `pyarchinit_dbmanagment` dialog by importing it from `.gui.dbmanagment`, passing the current `iface` instance to its constructor. Displays the dialog by calling its `show()` method and stores the resulting instance in `self.pluginGui` for later reference.

##### runPdfexp(self)

*No description available.*
Instantiates the `pyarchinit_pdf_export` class from the `Pdf_export` module, passing the current `iface` object to its constructor. Calls `show()` on the resulting instance to display the PDF export interface, then stores the instance in `self.pluginGui` for later reference.

##### runThesaurus(self)

*No description available.*
Instantiates the `pyarchinit_Thesaurus` class from the `.tabs.Thesaurus` module, passing the current `iface` object to its constructor. Calls `show()` on the resulting instance to display the Thesaurus tab interface. The created instance is saved to `self.pluginGui` for later reference.

##### runDocumentazione(self)

*No description available.*
Instantiates the `pyarchinit_Documentazione` plugin component, imported from `.tabs.Documentazione`, passing the current `iface` object to its constructor. Calls `show()` on the newly created instance to display its interface. The instance is then saved to `self.pluginGui` for later reference.

##### runExcel(self)

*No description available.*
Instantiates a `pyarchinit_excel_export` dialog by importing it from the `.tabs.Excel_export` module, passing the current `iface` object to its constructor. The dialog is then displayed by calling its `show()` method, and the resulting instance is saved to `self.pluginGui` for later reference.

##### runCantiere(self)

*No description available.*
Launches the Cantiere module by first verifying that the current user holds the required `'cantiere_table'` permission via `_check_cantiere_permission`. If the permission check fails, it calls `_show_cantiere_permission_denied` and returns without opening the interface. If the check passes, it instantiates and displays the `pyarchinit_Cantiere` dialog, storing the reference in `self.pluginGui`.

##### runPersonale(self)

*No description available.*
Checks whether the current user has permission to access the `cantiere_personale_table` resource by calling `_check_cantiere_permission`; if permission is denied, it invokes `_show_cantiere_permission_denied` and returns early. If the permission check passes, it imports and instantiates the `pyarchinit_Personale` GUI class from the `.tabs.Personale` module, displays it via `show()`, and stores the reference in `self.pluginGui`.

##### runPresenze(self)

*No description available.*
Launches the *Presenze* plugin interface after verifying that the current user has permission to access the `cantiere_presenze_table`. If the permission check fails, a permission-denied message is displayed and execution is halted. Otherwise, an instance of `pyarchinit_Presenze` is created, made visible, and stored as `self.pluginGui`.

##### runAttrezzature(self)

Opens the Attrezzature (equipment) management interface within the plugin. It first verifies that the current user has the required `cantiere_attrezzature_table` permission, displaying a permission-denied message and returning early if the check fails. If authorized, it instantiates and displays the `pyarchinit_Attrezzature` GUI, storing the reference in `self.pluginGui`.

##### runBudget(self)

*No description available.*
Checks whether the current user has permission to access the `cantiere_budget_table` resource; if permission is denied, displays a permission-denied message and returns immediately. If the permission check passes, it instantiates and displays the `pyarchinit_Budget` plugin GUI, passing the current `iface` reference, and stores the resulting instance in `self.pluginGui`.

##### unload(self)

Performs a complete teardown of the pyArchInit plugin by removing all registered menu entries, toolbar icons, dock widgets, and associated UI resources from the QGIS interface. Prior to locale-dependent cleanup, it unconditionally invokes `_unload_stratigraph_sync()` and removes the `_geoarchaeo_dock` widget if present. The set of menu entries and toolbar icons removed varies based on the two-letter user locale retrieved from `QgsSettings` (`'it'`, `'en'`, `'de'`, or a fallback default), and experimental actions are only removed when `is_experimental_enabled()` returns `True`; in all branches, `toolBar` and `toolBarCantiere` are deleted and the main dock widget is hidden and removed.

##### showHideDockWidget(self)

Toggles the visibility of `dockWidget` based on its current state. If the widget is currently visible, it is hidden; otherwise, it is shown.

