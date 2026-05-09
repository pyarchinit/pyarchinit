# tabs/tops_pyarchinit.py

## Overview

This file contains 13 documented elements.

## Classes

### pyarchinit_TOPS

*No description available.*
A QGIS dialog class that integrates the Total Open Station (TOPS) library into the pyarchinit plugin, enabling users to parse raw total station survey files and export the resulting point data to various output formats. It provides UI controls for selecting input and output files, choosing input and output formats via combo boxes, previewing parsed data in a table view, and deleting selected rows. For pyarchinit-specific CSV output formats, the class handles direct integration with QGIS project layers — including `Quote US disegno`, `Punti di riferimento`, and `Punti di campionatura` — by prompting the user for site metadata and copying parsed features with mapped attributes into the corresponding destination layers.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes a `pyarchinit_TOPS` dialog instance by calling the parent class constructor and setting up the UI via `setupUi`. Assigns the provided `iface` object to the instance, initializes a `QStandardItemModel` and binds it to `tableView`. Connects the `toolButton_input` and `toolButton_output` click signals to their respective path-setting handler methods `setPathinput` and `setPathoutput`.

##### setPathinput(self)

Opens a file dialog prompting the user to select an input file of any type (`*.*`). If a valid file path is selected, the method populates `lineEdit_input` with the chosen file path.

##### setPathoutput(self)

*No description available.*
Opens a save file dialog prompting the user to specify an output file path, with the file extension filter derived from the currently selected format in `comboBox_format2`. If the format string contains a space, only the last token is used as the extension; otherwise, the full format string is used. If the user confirms a file path, the result is written to `lineEdit_output`.

##### loadCsv(self, fileName)

Loads a CSV file from the specified `fileName` path into the table view by reading each row and converting its fields into `QStandardItem` objects, which are then appended to the model. Before populating the model, any existing spans in the `tableView` are cleared via `clearSpans()`.

##### delete(self)

*No description available.*
Removes one or more rows from the table model based on the current selection in `tableView`. If a selection exists, each selected row index is first wrapped in a `QPersistentModelIndex` to maintain index validity during sequential deletion, then each corresponding row is removed from `self.model`.

##### convert_csv(self)

*No description available.*
Reads a CSV file from the path specified in `lineEdit_output`, then splits the `point_name` column into two separate columns, `area_q` and `point_name`, using `-` as the delimiter. The modified DataFrame is written back to the same file path with UTF-8 encoding and without the index column. Any exception raised during this process is silently suppressed.

##### on_pushButton_export_pressed(self)

*No description available.*
Handles the export button press event by reading the input file path, output file path, input format, and output format from the corresponding UI controls, then invoking `_parse_and_export` to process and convert the data. If either file path is empty, a warning dialog is displayed and the operation is aborted. For standard output formats, the result is optionally loaded as a CSV layer; for `csv pyarchinit`-specific formats, additional user input dialogs are presented to collect site metadata and optional elevation values before copying features into the appropriate destination layer (`Quote US disegno`, `Punti di riferimento`, or `Punti di campionatura`) via `_copy_features_to_dest`.

##### rmvLyr(lyrname)

*No description available.*
A static method that removes a map layer from the current QGIS project instance by name. It retrieves the project instance via `QgsProject.instance()`, looks up the first layer matching `lyrname` using `mapLayersByName()`, and removes it by its ID using `removeMapLayer()`. No return value is produced.

## Functions

### set_us_attrs(feature)

*No description available.*
A callback function that sets attribute values on a given feature for the "Quote US disegno" layer. It assigns the `sito_q`, `unita_misu_q`, `x`, and `y` attributes from the outer scope variables `Sito`, `Misura`, the current date (in ISO format), and `Disegnatore` respectively. If the coordinate checkbox is checked, it additionally computes and sets the `quota_q` attribute by adding the user-supplied elevation value `q` to the feature's existing attribute at index 5.

**Parameters:**
- `feature`

### set_rif_attrs(feature)

*No description available.*
A callback function that sets attributes on a given feature for the "Punti di riferimento" layer. It unconditionally assigns the `'sito'` attribute to the value of `Sito`, and conditionally sets the `'quota'` attribute to the sum of the user-supplied elevation value `q` and the feature's existing attribute at index `4`, when the coordinate checkbox is checked. This function is passed as a callback to `_copy_features_to_dest` to apply per-feature attribute transformations during the copy operation.

**Parameters:**
- `feature`

### set_sample_attrs(feature)

*No description available.*
A locally defined callback function that sets the `'sito'` attribute of a given feature to the value of the enclosing `Sito` variable. It accepts a single parameter, `feature`, representing a map layer feature, and directly assigns the site name string via `setAttribute`. This function is passed as a callback to `_copy_features_to_dest` to apply the attribute assignment during the feature copy operation.

**Parameters:**
- `feature`

