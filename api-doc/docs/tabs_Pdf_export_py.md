# tabs/Pdf_export.py

## Overview

This file contains 17 documented elements.

## Classes

### pyarchinit_pdf_export

`pyarchinit_pdf_export` is a QDialog subclass that provides a QGIS plugin dialog for exporting archaeological record sheets to PDF format. It connects to the pyarchinit database, populates a site selection combo box, and — based on user-selected checkboxes — queries and exports PDF sheets and indexes for multiple record types including stratigraphic units (US), periodisation, structures, finds, tombs, samples, and individuals. Export output is locale-aware, supporting Italian, German, and English, and is written to the `pyarchinit_PDF_folder` directory under the `PYARCHINIT_HOME` environment path.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the dialog by invoking the parent constructor and setting up the UI from the Designer-generated layout. Applies the current theme via `ThemeManager` and adds a theme toggle button to the form, then stores the provided `iface` reference. Attempts a database or service connection via `connect()` (silently suppressing any exceptions), and subsequently calls `charge_list()` and `set_home_path()` to populate data and configure the default path.

##### connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object, retrieving its connection string, and initializing `self.DB_MANAGER` via `get_db_manager` with singleton reuse enabled. If the connection attempt raises an exception, a localized warning message is pushed to the QGIS message bar in Italian, German, or English depending on `self.L`. The `else` branch similarly displays a localized bug-report warning message via the QGIS message bar.

##### charge_list(self)

Retrieves a list of site values from the database by querying the `site_table` table, grouped by the `sito` column, and converts the result using `tup_2_list_III`. Empty string entries are removed from the list, and the list is then sorted alphabetically. The method clears the `comboBox_sito` combo box and repopulates it with the processed site values.

##### set_home_path(self)

*No description available.*
Sets the `HOME` instance attribute by reading the `PYARCHINIT_HOME` environment variable. This method retrieves the value of `os.environ['PYARCHINIT_HOME']` and assigns it to `self.HOME` for use by other methods in the class, such as constructing file system paths.

##### on_pushButton_open_dir_pressed(self)

Opens the `pyarchinit_PDF_folder` directory located under the `HOME` path in the system's default file manager. The method constructs the target path by joining `self.HOME` with the folder name using the OS-appropriate separator, then dispatches the open command using `os.startfile` on Windows, `open` on macOS (Darwin), or `xdg-open` on other platforms.

##### messageOnSuccess(self, printed)

Displays a message in the QGIS interface message bar based on the outcome of an export operation. If `printed` is `True`, a success-level message reading `"Exportation ok"` is pushed; otherwise, an info-level message reading `"Exportation falied"` is displayed.

##### on_pushButton_exp_pdf_pressed(self)

Handles the press event of the PDF export button by retrieving the current site value from `comboBox_sito` and conditionally exporting PDF record sheets and index files for each enabled record type based on the state of the corresponding checkboxes (`checkBox_US`, `checkBox_periodo`, `checkBox_struttura`, `checkBox_reperti`, `checkBox_tomba`, `checkBox_campioni`, `checkBox_individui`). For each enabled record type, the method queries the database for records matching the selected site, sorts them, generates the appropriate PDF sheets and index using language-specific builder methods determined by `self.L` (`'it'`, `'de'`, or a fallback). After each export block, `self.DATA_LIST` is cleared and `self.messageOnSuccess` is called to report the result.

##### db_search_DB(self, table_class, field, value)

*No description available.*
Searches the database for records matching a single field-value criterion within the specified table class. It constructs a search dictionary from the provided field and value, removes any empty entries using a `Utility` helper, and then executes a boolean query via `DB_MANAGER`. Returns the query result set produced by `DB_MANAGER.query_bool`.

##### generate_list_US_pdf(self)

Iterates over all records in `self.DATA_LIST` and compiles a structured list of field values for each stratigraphic unit (US), querying the database via `self.DB_MANAGER` to retrieve elevation data (`select_quote_from_db_sql`) and plan drawing information (`select_us_from_db_sql`). For each record, it derives minimum and maximum elevation values from the sorted query results, resolves plan references with language-dependent fallback strings based on `self.L` (`'it'`, `'de'`, or default), and converts optional numeric fields to empty strings when absent. Returns `data_list`, a list of lists where each inner list contains 113 ordered field values per record, intended for use in PDF generation.

##### generate_list_periodizzazione_pdf(self)

*No description available.*
Iterates over `self.DATA_LIST` and builds a formatted list of rows suitable for PDF generation, where each row represents a periodization record. For each entry, the fields `periodo`, `fase`, `cron_iniziale`, and `cron_finale` are safely converted to strings, substituting an empty string when the value is `None`. Each row contains seven fields — site name (with underscores replaced by spaces), period, phase, initial chronology, final chronology, extended dating, and description — and the completed list is returned.

##### generate_list_struttura_pdf(self)

Iterates over `self.DATA_LIST` to build and return a list of records formatted for PDF generation of structural (struttura) data. For each entry, it queries the database to retrieve associated stratigraphic units (US) and their elevation values (quote), determining the minimum and maximum elevations; if no GIS elevation data is found, a localised placeholder string is used based on `self.L` (supporting Italian, German, and a default English fallback). Each record appended to the output list contains 19 fields covering site, structure identifier, category, typology, definition, description, interpretation, chronological phases, extended dating, materials, structural elements, relationships, measurements, and the computed minimum and maximum elevations.

##### generate_list_reperti_pdf(self)

Iterates over all entries in `self.DATA_LIST` and constructs a list of lists, where each inner list contains 25 fields extracted from a single inventory material record (`id_invmat`, `sito`, `numero_inventario`, `tipo_reperto`, `criterio_schedatura`, `definizione`, `descrizione`, `area`, `us`, `lavato`, `nr_cassa`, `luogo_conservazione`, `stato_conservazione`, `datazione_reperto`, `elementi_reperto`, `misurazioni`, `rif_biblio`, `tecnologie`, `tipo`, `corpo_ceramico`, `rivestimento`, `repertato`, `diagnostico`, `n_reperto`, `tipo_contenitore`). All fields are cast to `str`, with the exception of `numero_inventario`, which is cast to `int`; the `sito` field additionally has underscores replaced with spaces. Returns the fully populated `data_list` for use in PDF generation.

##### generate_list_individui_pdf(self)

*No description available.*
Iterates over all records in `self.DATA_LIST` and compiles a list of lists, where each inner list represents a single individual's data formatted as strings for PDF generation. Each entry contains 23 fields extracted from the corresponding data object, including site name (with underscores replaced by spaces), area, stratigraphic unit (`us`), individual number, recording date, recorder, sex, minimum and maximum age, age class, observations, structure reference, completeness, disturbance and connection status, skeleton length and position, skull position, upper and lower limb positions, and orientation data (axis and azimuth). Returns the fully populated `data_list`.

##### generate_list_tomba_pdf(self)

Iterates over `self.DATA_LIST` to compile a structured list of burial record data for PDF generation. For each record, it queries the database via `self.DB_MANAGER` to retrieve associated individual (`SCHEDAIND`) and structure (`US`) stratigraphic unit records, then resolves their minimum and maximum elevation values from GIS data; if no elevation data is found, locale-appropriate placeholder strings are assigned based on `self.L` (`'it'`, `'de'`, or default). Returns a list of 30-element lists, each containing site, burial card, structure, individual, ritual, descriptive, chronological, elevation, and stratigraphic unit fields for a single record.

##### generate_list_campioni_pdf(self)

*No description available.*
Iterates over `self.DATA_LIST` and builds a formatted list of sample (`campioni`) records intended for PDF generation. For each entry, it safely converts the fields `nr_campione`, `us`, `numero_inventario_materiale`, and `nr_cassa` to empty strings if their value is `'None'`, while the remaining fields are converted directly to strings. Returns a list of nine-element lists, each containing: site name (with underscores replaced by spaces), sample number, sample type, description, area, US, material inventory number, storage location, and crate number.

