# tabs/Excel_export.py

## Overview

This file contains 10 documented elements.

## Classes

### pyarchinit_excel_export

*No description available.*
A QDialog subclass that provides a graphical interface for exporting archaeological database records to Excel (`.xlsx`) files. It connects to either a PostgreSQL or SQLite database, populates a site selection combo box, and exports data from selected tables — including `site_table`, `us_table`, `inventario_materiali_table`, `struttura_table`, and `tomba_table` — into timestamped Excel files written to the `pyarchinit_EXCEL_folder` directory. The dialog applies theme management via `ThemeManager` and displays localized warning messages in Italian, German, or English based on the current QGIS locale setting.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the dialog by setting up the UI from the Designer file and applying the current theme, including adding a theme toggle button to the form. Stores the provided `iface` reference, then attempts a database connection via `connect()`, suppressing any exceptions that may occur. Completes initialization by calling `charge_list()` and `set_home_path()`.

##### connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object, retrieving the connection string via `conn_str()`, and passing it to `get_db_manager()` to initialize `self.DB_MANAGER`. If the connection attempt raises an exception, a localized warning message is pushed to the QGIS message bar in Italian, German, or English depending on `self.L`, advising the user to restart QGIS or report the error to the developer. The `else` branch similarly displays a localized bug-warning message via the QGIS message bar.

##### charge_list(self)

Populates the `comboBox_sito` combo box with a sorted list of site values retrieved from the `site_table` database table, grouped by the `sito` column. The raw query results are converted from tuples to a list via `UTILITY.tup_2_list_III`, and any empty string entries are removed before the items are sorted and added to the combo box.

##### set_home_path(self)

Sets the `HOME` instance attribute by reading the `PYARCHINIT_HOME` environment variable via `os.environ`. This value is subsequently used as the base path for constructing directory references within the class.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_EXCEL_folder` directory located under the application's home path (`self.HOME`) in the operating system's default file manager. The method constructs the target path by joining `self.HOME` with the folder name, then dispatches the appropriate system call based on the current platform: `os.startfile` on Windows, `open` via subprocess on macOS (Darwin), and `xdg-open` via subprocess on all other systems.

##### messageOnSuccess(self, printed)

Displays a message in the QGIS interface message bar based on the outcome of an export operation. If `printed` is `True`, a success message reading `"Exportation ok"` is pushed with `Qgis.Success` severity; otherwise, a message reading `"Exportation falied"` is pushed with `Qgis.Info` severity.

##### db_search_DB(self, table_class, field, value)

*No description available.*
Searches the database for records matching a specified field-value pair within a given table class. It constructs a search dictionary mapping the field to the provided value, removes any empty entries using `Utility.remove_empty_items_fr_dict`, and then executes a boolean query via `DB_MANAGER.query_bool`. Returns the result of the query.

##### on_pushButton_exp_pdf_pressed(self)

Handles the export of site-specific database records to Excel (`.xlsx`) files when the corresponding export button is pressed. Reads database connection settings from `config.cfg`, connects to either a PostgreSQL or SQLite database depending on the configured server type, and exports data from one or more tables (`site_table`, `us_table`, `inventario_materiali_table`, `struttura_table`, `tomba_table`) based on the currently selected site and the state of the associated checkboxes (`checkBox_site`, `checkBox_uw`, `checkBox_art`, `checkBox_pottery`, `checkBox_anchor`). Output files are written to the `pyarchinit_EXCEL_folder` directory using `xlsxwriter` via pandas, with filenames incorporating the site name and the current date.

