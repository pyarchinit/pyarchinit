# tabs/gpkg_export.py

## Overview

This file contains 6 documented elements.

## Classes

### pyarchinit_GPKG

*No description available.*
A QGIS `QDialog` subclass that provides a user interface for exporting selected map layers from the QGIS layer tree into GeoPackage (`.gpkg`) files. It supports exporting both vector layers via `QgsVectorFileWriter` and raster layers via `QgsRasterFileWriter`, handling both new file creation and appending to existing GeoPackage files. The dialog is locale-aware, adapting its message strings to Italian, English, or German based on the current QGIS user locale setting, and applies a theme via `ThemeManager`.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the GeoPackage import dialog by calling the parent class constructors and configuring the UI via `setupUi`. Applies the current application theme using `ThemeManager.apply_theme` and attaches a theme toggle button to the form. Connects the `toolButton` clicked signal to the `setPath` slot for file path selection.

##### setPath(self)

Opens a save file dialog prompting the user to specify a file path for a GeoPackage (`.gpkg`) file. If a valid path is selected, it updates the `lineEdit` widget with the chosen path and stores the value in `QgsSettings`.

##### on_pushButton_gpkg_pressed(self)

*No description available.*
Handles the press event of the GPKG export button by retrieving the currently selected layers from the layer tree view and the target GeoPackage file path from the line edit field. For each selected vector layer, it writes the layer to the specified GeoPackage file using `QgsVectorFileWriter.writeAsVectorFormat`, replacing spaces in layer names with underscores; if the target file already exists, layers are added using the `CreateOrOverwriteLayer` action, otherwise the file is created first before subsequent layers are appended. Upon completion, a localized message box is displayed indicating whether the import succeeded or failed, or warning the user if no layers were selected.

##### on_pushButton_gpkg2_pressed(self)

*No description available.*
Handles the press event of the `pushButton_gpkg2` button by appending the first selected layer from the layer tree view as a raster subdataset into an existing GeoPackage file specified by `lineEdit`. It opens the target GeoPackage via GDAL, constructs a `QgsRasterFileWriter` configured with the `gpkg` output format and `APPEND_SUBDATASET=YES`, and writes the raster data through a `QgsRasterPipe` containing a `QgsRasterProjector`. A warning dialog is displayed to indicate whether the import completed successfully or failed.

