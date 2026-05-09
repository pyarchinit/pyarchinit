# tabs/Interactive_matrix.py

## Overview

This file contains 17 documented elements.

## Classes

### pyarchinit_Interactive_Matrix

`pyarchinit_Interactive_Matrix` is a QDialog subclass that provides an interactive interface for generating and exporting Harris Matrix diagrams from stratigraphic unit data within the PyArchInit QGIS plugin. It accepts a list of stratigraphic records and a unit-ID dictionary, establishes a database connection on initialization, and applies the active UI theme. The class exposes two matrix generation methods, `generate_matrix` and `generate_matrix_2`, which process stratigraphic relationships (positive, negative, contemporary, and connection types) alongside periodization data to construct and export a `HarrisMatrix` object.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface, data_list, id_us_dict)

Initializes the dialog instance by calling the parent constructor and setting up core attributes, including the QGIS interface (`iface`), a `Pyarchinit_pyqgis` helper, the provided data list (`data_list`), and the US ID dictionary (`id_us_dict`). Calls `setupUi` to build the UI layout, then applies the current theme via `ThemeManager` and attaches a theme toggle button to the form. Finally, attempts to establish a database connection via `DB_connect`, silently suppressing any exceptions that occur during that process.

##### DB_connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object, retrieving its connection string via `conn_str()`, and passing it to `get_db_manager()` with singleton reuse enabled, storing the result in `self.DB_MANAGER`. If the connection attempt raises an exception, a warning dialog is displayed to the user via `QMessageBox.warning()` containing the error details; the message is shown in Italian (`'it'`) or English depending on the value of `self.L`.

##### urlify(self, s)

*No description available.*
Transforms a string into a URL-friendly format by performing two sequential substitution operations using regular expressions. First, all non-word characters (anything other than alphanumeric characters and underscores) are replaced with spaces; then, all whitespace sequences are replaced with a single underscore. Returns the resulting sanitized string.

##### generate_matrix_2(self)

*No description available.*
Iterates over `self.DATA_LIST` to collect stratigraphic relationship tuples, categorising each record's relationships into five groups: positive (`data`), negative (`negative`), contemporary (`conteporane`), connection (`connection`, operator `>`), and connection-to (`connection_to`, operator `>>`). Each node label is composed of the unit type, US number, stratigraphic interpretation, and period–phase datation. The method then queries the database for periodisation data associated with the site, builds a cluster list grouping stratigraphic units by period and phase, constructs a `HarrisMatrix` instance from all collected data, invokes its `export_matrix_2` property, and returns the result, displaying a localised warning dialog (Italian, German, or English) if required field values are missing or an error occurs during processing.

##### generate_matrix(self)

*No description available.*
Iterates over `self.DATA_LIST` to extract stratigraphic relationships for each record, classifying them into three groups — positive (`data`), negative (`negative`), and contemporary (`conteporane`) — based on membership in `POSITIVE_GROUP`, `NEGATIVE_GROUP`, and `MATRIX_CONTEMPORARY_GROUP` respectively. It then queries the database for periodization data associated with the site, constructing a hierarchical list (`periodi_us_list`) that maps clusters, areas, periods, and phases — including formatted chronological date ranges retrieved from `PERIODIZZAZIONE` records — to their corresponding stratigraphic units. Finally, it instantiates a `HarrisMatrix` object with the collected relationship and periodization data, invokes `export_matrix`, displays a localized completion message via `QMessageBox`, and returns the resulting plot data.

### pyarchinit_view_Matrix

*No description available.*
A QDialog subclass that provides a graphical interface for generating and exporting a Harris stratigraphic matrix within the PyArchInit QGIS plugin. It accepts a data list of stratigraphic unit records and a unit ID dictionary, establishes a database connection on initialisation, and processes stratigraphic relationships — categorised as positive, negative, or contemporary — alongside periodisation data to construct a `ViewHarrisMatrix` export. The locale setting (Italian, German, or other) governs the language of user-facing warning messages and period labels displayed during matrix generation.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface, data_list, id_us_dict)

Initializes the dialog instance by calling the parent constructor and setting up core attributes, including the QGIS interface (`iface`), a `Pyarchinit_pyqgis` instance, the provided data list, and the US ID dictionary. Configures the UI via `setupUi`, applies the current theme using `ThemeManager`, and adds a theme toggle button to the form. Attempts to establish a database connection via `DB_connect`, silently suppressing any exceptions that occur during that process.

##### DB_connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object, retrieving its connection string via `conn_str()`, and passing it to `get_db_manager()` with singleton reuse enabled, storing the result in `self.DB_MANAGER`. If the connection attempt raises an exception, a warning dialog is displayed to the user via `QMessageBox`; the message is shown in Italian (`'it'`) or English depending on the value of `self.L`.

##### urlify(self, s)

*No description available.*
Transforms a given string `s` into a URL-friendly format by performing two sequential substitution operations. First, all non-word characters (anything other than alphanumeric characters and underscores) are replaced with a space using the pattern `[^\w\s]`. Then, all whitespace sequences are replaced with a single underscore, and the resulting string is returned.

##### generate_matrix(self)

*No description available.*
Iterates over `self.DATA_LIST` to classify stratigraphic relationships for each record into three categories — positive (`data`), negative (`negative`), and contemporary (`conteporane`) — by evaluating each record's `rapporti` field against the predefined groups `POSITIVE_GROUP`, `NEGATIVE_GROUP`, and `MATRIX_CONTEMPORARY_GROUP`. It then queries the database for periodization data associated with the site, building a list of period/phase clusters with their corresponding stratigraphic units. Finally, it constructs a `ViewHarrisMatrix` instance from the collected relationship and cluster data and returns its `export_matrix` attribute.

### pyarchinit_view_Matrix_pre

*No description available.*
A `QDialog` subclass that serves as the main dialog for generating and displaying a Harris Matrix within the PyArchInit QGIS plugin. It accepts a data list of stratigraphic unit records and a unit ID dictionary, establishes a database connection via `DB_connect`, and applies the active UI theme on initialization. The primary method, `generate_matrix_3`, processes stratigraphic relationships from the data list — categorizing them into sequential, negative, and contemporary relation groups — and constructs a `ViewHarrisMatrix` export, optionally filtering output to a specified subset of visible stratigraphic units.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface, data_list, id_us_dict)

Initializes the dialog by calling the parent constructor and setting up core instance attributes, including the QGIS interface (`iface`), a `Pyarchinit_pyqgis` instance, the provided `data_list`, and `id_us_dict`. Configures the UI via `setupUi`, applies the current theme using `ThemeManager`, and adds a theme toggle button to the form. Attempts to establish a database connection via `DB_connect`, silently suppressing any exceptions that occur during that process.

##### DB_connect(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object, retrieving its connection string via `conn_str()`, and passing it to `get_db_manager()` with singleton reuse enabled, storing the result in `self.DB_MANAGER`. If an exception occurs during this process, a warning dialog is displayed to the user; the message is shown in Italian (`'it'`) or English depending on the value of `self.L`.

##### urlify(self, s)

*No description available.*
Transforms a string into a URL-friendly format by performing two sequential substitution operations using regular expressions. First, all non-word characters (anything other than alphanumeric characters and underscores) are replaced with spaces; then, all whitespace sequences are replaced with a single underscore. Returns the resulting sanitized string.

##### generate_matrix_3(self)

*No description available.*
Builds the data structures required to render a Harris Matrix by iterating over `self.DATA_LIST` and classifying each stratigraphic relationship into one of three lists: `data` (sequential relationships such as covers, abuts, fills, and same-as groups), `negative` (cut relationships), and `conteporane` (contemporary/support relationships). When `self.visible_us_list` is populated, the method restricts processing to the specified stratigraphic units plus any automatically identified "bridge" units needed to preserve relational continuity. It then queries periodisation and phase data from the database, assembles a nested `periodi_us_list` grouping units by site, area, period, and phase, constructs a `ViewHarrisMatrix` instance from all collected data, and returns its `export_matrix_3` attribute.

