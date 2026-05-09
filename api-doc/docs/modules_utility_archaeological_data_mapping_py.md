# modules/utility/archaeological_data_mapping.py

## Overview

This file contains 12 documented elements.

## Classes

### ArchaeologicalDataMapper

*No description available.*
A `QWidget`-based GUI component that facilitates the mapping and export of archaeological materials data from pyArchInit-formatted Excel files to the ICA (Inventario Comune Archeologico) template format. The widget provides a three-step interface allowing the user to select an input Excel file, specify an output file path, and trigger a data processing pipeline that collects additional metadata via interactive dialogs, transforms the source data, and writes the result into a pre-existing Excel template with logo, borders, and column formatting applied. The window is configured to remain always on top of other windows via `Qt.WindowStaysOnTopHint`.

**Inherits from**: QWidget

#### Methods

##### __init__(self, iface, parent)

Initializes an instance of `ArchaeologicalDataMapper`, a `QWidget` subclass, by calling the parent class constructor with the optional `parent` argument. Stores the provided `iface` reference as an instance attribute and invokes `self.initUI()` to set up the user interface. Applies the `Qt.WindowStaysOnTopHint` window flag to ensure the widget remains on top of other windows.

##### initUI(self)

*No description available.*
Initialises and assembles the main user interface of the widget using a `QVBoxLayout`. It creates and adds the following widgets to the layout: an instructional `QLabel`, a `QPushButton` for selecting the input Excel file (connected to `get_input_file`), a `QPushButton` for specifying the output file path (connected to `get_output_file`), a `QPushButton` for triggering data processing (connected to `process_data`), and an output `QLabel` with external link support connected to `open_file`. Finally, it applies the layout to the widget, sets the window geometry to `(300, 300, 300, 150)`, sets the window title to `'Mapper Materiali da pyArchInit a ICA'`, and calls `show()` to display the window.

##### open_file(self, link)

*No description available.*
Opens a URL or file path using the system's default application by delegating to `QDesktopServices.openUrl`. The provided `link` argument is wrapped in a `QUrl` object before being passed to the open call. This method does not return a value.

##### get_input_file(self)

*No description available.*
Opens a file selection dialog prompting the user to select an Excel file (`.xlsx` or `.xls`), with the dialog title `'Seleziona file excel dei materiali esportato da pyArchInit'`. The selected file path is stored in `self.input_file`. If a file is selected, `self.label` is updated to display the text `'File di input: '` followed by the chosen file path.

##### get_output_file(self)

Opens a save file dialog prompting the user to specify a destination path and filename for the output Excel file (`.xlsx` or `.xls`). If a valid path is selected, updates the `label` widget to display the chosen output file path.

##### process_data(self)

*No description available.*
Validates that both `input_file` and `output_file` attributes are present on the instance before attempting to generate an Excel file by calling `create_archaeological_excel` with those paths. On success, displays an informational dialog confirming the file was created and updates `output_label` with a clickable hyperlink to the output file. If either attribute is missing, a warning dialog is shown prompting the user to select both files first; if an exception occurs during processing, a critical error dialog is displayed with the exception message.

##### load_input_data(self, input_file)

*No description available.*
Reads an Excel file specified by `input_file` into a pandas DataFrame using the `openpyxl` engine. For each column containing object-type data, any string values that begin with `'['` are parsed using `ast.literal_eval` to convert them into their corresponding Python objects (e.g., lists). Returns the resulting DataFrame with the converted column values.

##### map_data_to_template(self, input_df)

Maps rows from an input DataFrame to a predefined archaeological inventory template structure defined by `template_columns`. Before processing, it prompts the user via `QInputDialog` to manually enter several fields (such as institution name, responsible parties, investigation method, and storage location details) that are applied uniformly to all rows, while per-row fields are extracted from the input DataFrame using `row.get()`. Measurement data from `misurazioni` and `elementi_reperto` columns is parsed and concatenated with `/` separators into the corresponding template fields; the method returns a `pd.DataFrame` aligned to the template columns, or `None` if the resulting DataFrame is empty.

##### create_archaeological_excel(self, input_file, output_file)

*No description available.*
Loads archaeological data from `input_file`, maps it to a predefined template structure, and writes the result to `output_file` as a formatted Excel workbook. The method uses a fixed template (`template_materiali.xlsx`) and inserts a logo image (`resized_logo.jpeg`) into cell `A1`, applies uniform row heights and column widths derived from the template's first row and column dimensions, and writes the mapped data starting from row 3 with thin black borders applied to all data cells. Returns `True` on success or `False` if the data is empty, a required file is not found, or any other exception occurs, displaying appropriate `QMessageBox` dialogs in each case.

## Functions

### process_quantity(q)

*No description available.*
Processes a list of measurement entries, where each entry is expected to be a three-element list, and unpacks them into three separate parallel lists (`t`, `u`, `v`) representing the first, second, and third components of each measurement respectively.

If the input `q` is empty or falsy, the function returns three empty values: two empty lists and an empty string. After iterating over all valid measurements, it consolidates the unit values (`u`) into a single string — using the first unit if all units are identical, or joining them with `", "` if they differ — then returns the values list, the consolidated unit string, and the third-component list.

**Parameters:**
- `q`

### process_measurements(measurements)

*No description available.*
Processes a list of measurement entries, each expected to be a three-element list containing a type, a unit, and a value. Returns a tuple of three elements: a list of type strings, a consolidated unit string, and a list of value strings. If all units are identical, the unit string contains only the single shared unit; otherwise, all units are joined with `", "`. If the input is empty or `None`, the function returns two empty lists and an empty string.

**Parameters:**
- `measurements`

