# tabs/Movecost.py

## Overview

This file contains 30 documented elements.

## Classes

### pyarchinit_Movecost

`pyarchinit_Movecost` is a QGIS `QDialog` subclass that provides a graphical interface for executing and managing a suite of R-based least-cost movement analysis algorithms (movecost, movebound, movecorr, movealloc, movecomp, movenetw, and moverank), including their polygon-bounded variants. The dialog handles algorithm execution via QGIS Processing, optional automatic layer organization and styling through `MovecostLayerOrganizer`, and display of analysis results including statistical summaries derived from output vector layers and R-generated plot images. It also provides utilities for exporting results to CSV and HTML, saving plots, adding R scripts to the QGIS Processing environment, accessing localized help documentation, and updating button tooltips based on a selected language.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes a `pyarchinit_Movecost` dialog instance by calling the parent constructor, setting up the UI, and initializing instance attributes including `iface`, `last_algorithm`, and `current_plot_path`. Conditionally instantiates a `MovecostLayerOrganizer` object bound to the dialog if the class is available. Connects the `comboBox_mc_language` widget's `currentIndexChanged` signal to its corresponding handler, suppressing any `AttributeError` if the widget is not present.

##### on_pushButton_movecost_pressed(self)

Handles the press event of the `pushButton_movecost` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movecost'` and the display name `'movecost'`. This triggers execution of the move cost algorithm through the configured algorithm-running workflow.

##### on_pushButton_movecost_p_pressed(self)

Handles the press event of the `pushButton_movecost_p` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movecostbypolygon'` and the display name `'movecost by polygon'`. This triggers execution of the move cost by polygon algorithm within the application's algorithm-running workflow.

##### on_pushButton_movebound_pressed(self)

Handles the press event of the `pushButton_movebound` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movebound'` and the display name `'movebound'`. This method serves as a UI callback that delegates execution to the internal algorithm runner with the specified parameters.

##### on_pushButton_movebound_p_pressed(self)

Handles the press event of the `pushButton_movebound_p` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:moveboundbypolygon'` and the display name `'movebound by polygon'`. This triggers the movebound-by-polygon algorithm within the application's processing workflow.

##### on_pushButton_movecorr_pressed(self)

Handles the press event of the `pushButton_movecorr` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movecorr'` and the display name `'movecorr'`. This method serves as a UI callback that triggers execution of the `movecorr` algorithm through the shared algorithm-running mechanism.

##### on_pushButton_movecorr_p_pressed(self)

Handles the press event of the `pushButton_movecorr_p` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movecorrbypolygon'` and the display name `'movecorr by polygon'`. This triggers execution of the move correlation by polygon algorithm within the application's processing framework.

##### on_pushButton_movealloc_pressed(self)

Handles the press event of the `pushButton_movealloc` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movealloc'` and the display name `'movealloc'`. This method serves as a UI callback that triggers execution of the movealloc algorithm within the processing framework.

##### on_pushButton_movealloc_p_pressed(self)

*No description available.*
Slot method triggered when the corresponding "movealloc by polygon" push button is pressed. It delegates execution to `_mc_run_algorithm`, passing `'r:moveallocbypolygon'` as the algorithm identifier and `'movealloc by polygon'` as the display name.

##### on_pushButton_movecomp_pressed(self)

*No description available.*
Handler method triggered when the `pushButton_movecomp` button is pressed. It delegates execution to `_mc_run_algorithm`, passing the algorithm identifier `'r:movecomp'` and the display name `'movecomp'`. This follows the same pattern used by adjacent button handlers to invoke named algorithms within the processing framework.

##### on_pushButton_movecomp_p_pressed(self)

Handles the press event of the `pushButton_movecomp_p` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movecompbypolygon'` and the display name `'movecomp by polygon'`. This triggers execution of the move-component-by-polygon algorithm within the application's algorithm runner framework.

##### on_pushButton_movenetw_pressed(self)

*No description available.*
Slot method triggered when the `pushButton_movenetw` button is pressed. It delegates execution to `_mc_run_algorithm`, passing the algorithm identifier `'r:movenetw'` and the display name `'movenetw'`.

##### on_pushButton_movenetw_p_pressed(self)

Handles the press event of the `pushButton_movenetw_p` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:movenetwbypolygon'` and the display name `'movenetw by polygon'`. This triggers execution of the move-network-by-polygon algorithm through the shared algorithm runner mechanism.

##### on_pushButton_moverank_p_pressed(self)

Handles the press event of the `pushButton_moverank_p` button by invoking `_mc_run_algorithm` with the algorithm identifier `'r:moverank'` and the display name `'moverank'`. This method serves as a UI callback that triggers execution of the `moverank` algorithm within the application's processing framework.

##### on_pushButton_moverank_polygon_pressed(self)

Handles the press event of the "moverank by polygon" push button in the user interface. Delegates execution to the internal `_mc_run_algorithm` method, passing the algorithm identifier `'r:moverankbypolygon'` and the display name `'moverank by polygon'`. This triggers the move rank by polygon algorithm within the application's processing pipeline.

##### on_pushButton_organize_pressed(self)

Handles the press event of the "organize" push button by invoking `organize_movecost_layers()` if the function is available, then displays an informational `QMessageBox` confirming that layers have been organized and styled. If `organize_movecost_layers` is `None`, a warning `QMessageBox` is shown instead, indicating that the layer organizer module is unavailable and directing the user to install the MoveCost plugin.

##### on_pushButton_refresh_plot_pressed(self)

*No description available.*
Handles the "Refresh Plot" button press event by first checking for active keyboard modifiers. If the Shift key is held, it invokes `_mc_show_search_debug()` and returns early; otherwise, it calls `_mc_load_latest_plot()` to attempt automatic detection of the most recent R plot. If no valid plot path is found, it presents a `QMessageBox` prompt offering the user the option to manually select an image file via `_mc_manual_select_plot()`.

##### on_pushButton_save_plot_pressed(self)

Opens a save file dialog prompting the user to choose a destination path when a valid plot file exists at `current_plot_path`, then copies the plot to the selected location using `shutil.copy2` and displays a success message. Supported save formats are PNG, JPEG, and all file types. If no valid plot is available, a warning dialog is displayed instead.

##### on_pushButton_export_csv_pressed(self)

Handles the CSV export action for cost-related map layers by scanning all loaded layers in the current QGIS project and collecting those of vector type that contain at least one of the fields `cost`, `length_m`, or `time_converted`. If no qualifying layers are found, a warning dialog is displayed and the method returns early; otherwise, the user is prompted via a save dialog to specify a destination CSV file path. Each identified layer is written to the CSV file as a named section containing a header row followed by all feature attribute values, with a blank row separating layers; success or failure is reported to the user via a message dialog.

##### on_pushButton_export_pdf_pressed(self)

*No description available.*
Handles the press event of the PDF export button. Displays an informational `QMessageBox` notifying the user that PDF export requires additional libraries and directing them to use HTML export instead. No PDF export operation is performed.

##### on_pushButton_export_html_pressed(self)

Exports the current analysis report as an HTML file by prompting the user with a save dialog filtered to `.html` files. If a path is selected, the method builds a self-contained HTML document containing a styled summary (retrieved from `textEdit_summary`) and tabular data from all vector layers in the current QGIS project whose fields include `cost`, `length_m`, or `time_converted`. On success, the exported file is opened in the default web browser; on failure, a critical error dialog is displayed.

##### defaultScriptsFolder(self)

*No description available.*
Returns the absolute path to the default R scripts folder located within the user folder, named `rscripts`. If the directory does not already exist, it is created via `mkdir` before the path is returned. The returned value is an absolute, normalized path string produced by `os.path.abspath`.

##### on_pushButton_add_script_pressed(self)

Copies R script files from the movecost plugin's `rscripts` source directory into the QGIS profile's `processing/rscripts` directory, creating the destination directory if it does not exist. The source directory is first looked up within the QGIS settings profile path, then falls back to `self.HOME/bin/rscripts`; if neither location exists, a warning dialog is displayed and the operation is aborted. Upon successful completion, an informational dialog reports the number of files copied.

##### on_pushButton_mc_help_pressed(self)

Opens the MoveCost plugin help documentation in the user's default web browser. It resolves the appropriate language code from `MC_LANGUAGE_CODES` based on the current selection in `comboBox_mc_language` (defaulting to `'en'` on `AttributeError`), then constructs the path to the corresponding `index.html` file within the QGIS profile's plugin help directory. If the language-specific file does not exist, it falls back to the English help file; if that is also absent, it opens the remote wiki at `https://github.com/enzococca/movecost/wiki`.

##### on_comboBox_mc_language_currentIndexChanged(self, index)

Slot method triggered when the current index of the `comboBox_mc_language` combo box changes. It retrieves the language code corresponding to the selected `index` from `MC_LANGUAGE_CODES`, defaulting to `'en'` if the index is not found. It then calls `_mc_update_tooltips` with the resolved language code to refresh the interface tooltips accordingly.

### QgsMapLayerType

*No description available.*
A compatibility shim class that provides access to map layer type constants when `QgsMapLayerType` is not available in the installed version of QGIS. In such cases, the class is defined locally and maps its attributes to the equivalent constants from `Qgis.LayerType` (e.g., `VectorLayer` is mapped to `Qgis.LayerType.Vector`). This ensures consistent access to layer type identifiers across different QGIS versions.

## Functions

### userFolder()

*No description available.*
Returns the path to the user's QGIS Processing settings directory. If the `processing.tools.system` module is available, the implementation is imported directly from it; otherwise, the fallback implementation constructs the path by joining `QgsApplication.qgisSettingsDirPath()` with the subdirectory name `'processing'`. The returned value is a string representing the directory path.

### mkdir(path)

*No description available.*
Creates a directory at the specified `path`, including any necessary intermediate-level directories. If the directory already exists, the function completes silently without raising an error, equivalent to the behaviour of `os.makedirs` with `exist_ok=True`. This implementation serves as a fallback when `mkdir` cannot be imported from `processing.tools.system`.

**Parameters:**
- `path`

