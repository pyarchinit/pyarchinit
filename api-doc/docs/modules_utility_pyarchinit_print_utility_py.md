# modules/utility/pyarchinit_print_utility.py

## Overview

This file contains 13 documented elements.

## Classes

### Print_utility

*No description available.*
A `QObject`-derived utility class responsible for batch-generating map printouts of archaeological stratigraphic units (US) within the pyarchinit QGIS plugin. It loads vector layers from either a PostGIS or SpatiaLite database, computes bounding-box dimensions to select an appropriate paper format, and exports each map as a PNG image to the `pyarchinit_MAPS_folder` directory. Progress is reported through the `progressBarUpdated` pyqtSignal, which emits the current and total item counts during batch processing.

**Inherits from**: QObject

#### Methods

##### __init__(self, iface, data)

Initializes the instance by calling the parent class constructor via `super().__init__()` and assigns the provided `iface` and `data` arguments to their respective instance attributes. Retrieves and stores the map canvas from `iface` by calling `self.iface.mapCanvas()`, assigning the result to `self.canvas`.

##### first_batch_try(self, server)

*No description available.*
Iterates over all entries in `self.data` and processes each record by loading the corresponding spatial layer from either a PostGIS (`'postgres'`) or SQLite (`'sqlite'`) backend, as determined by the `server` parameter. For each entry, if the layer loads successfully and contains features, it executes a bounding-box test, prints the map, and emits a `progressBarUpdated` signal to reflect the current progress; if the layer is empty, it is removed. If the layer fails to load (return value of `0`), an error report is written to `report_errori.txt` under `self.REPORT_PATH`.

##### converter_1_20(self, n)

*No description available.*
Converts a value from a 1:1 scale to a 1:20 scale by first multiplying the input `n` by 100 and then dividing the result by 20. Returns the computed floating-point quotient as the scaled output value.

**Signature:** `converter_1_20(self, n)`

**Parameters:** `n` — the numeric value to be converted.

**Returns:** The result of `(n * 100) / 20`.

##### test_bbox(self)

*No description available.*
Retrieves the first feature from `self.layerUS` and computes the bounding box of its geometry. The bounding box's height and width are then converted from centimetres to millimetres using `converter_1_20`, and the results are stored in `self.height` and `self.width` respectively. The method also initialises `dizionario_id_contains` and `lista_quote` as local data structures, though they are not populated within this method.

##### getMapExtentFromMapCanvas(self, mapWidth, mapHeight, scale)

*No description available.*
Calculates and returns a map extent rectangle centered on the current map canvas extent, adjusted to fit the specified map dimensions and scale. The method derives the center point from the canvas's current bounding box, then scales the provided `mapWidth` and `mapHeight` values (converted from points by multiplying by `scale / 1000`) to compute the new bounding coordinates. Returns a `QgsRectangle` representing the resulting extent, symmetrically expanded around the center point.

##### print_map(self, tav_num)

*No description available.*
Generates and exports a QGIS map layout for a specified table number (`tav_num`) and the associated stratigraphic unit (`us`). The method initialises a `QgsLayout` with a page size automatically selected from standard ISO formats (A4, A3, A0, landscape or portrait) based on the computed map dimensions, then adds a map item, a title label, a scale label, and a numeric scale bar to the layout. The resulting layout is exported as a PNG image at 100 DPI to the `pyarchinit_MAPS_folder` directory, with the filename derived from the table number and stratigraphic unit identifier.

##### open_connection_postgis(self)

Opens a PostGIS database connection by reading configuration settings from the `config.cfg` file located in the `pyarchinit_DB_folder` directory under the home path. It parses the configuration content using a `Settings` object and applies the configuration before initializing `self.uri` as a `QgsDataSourceUri` instance. The connection parameters — `HOST`, `PORT`, `DATABASE`, `USER`, and `PASSWORD` — are sourced from the parsed settings and passed to `self.uri.setConnection`.

##### open_connection_sqlite(self)

*No description available.*
Reads the database configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg`, parses its contents using a `Settings` object, and applies the configuration via `set_configuration()`. It then initialises `self.uri` as a `QgsDataSourceUri` instance and establishes a connection using only the `DATABASE` setting, as required for SQLite data sources.

##### remove_layer(self)

Removes the US and Quote map layers from the current QGIS project instance if they are loaded. For each layer, it calls `QgsProject.instance().removeMapLayer()` using the corresponding layer ID (`USLayerId` or `QuoteLayerId`), then resets that ID to an empty string. This ensures both layer references are cleared after removal.

##### charge_layer_sqlite(self, sito, area, us)

Loads two SpatiaLite vector layers — `pyarchinit_us_view` and `pyarchinit_quote_view` — from a SQLite database whose path is resolved by reading the application configuration file (`config.cfg`) located in the `pyarchinit_DB_folder` directory. Both layers are filtered using the provided `sito`, `area`, and `us` parameters as spatial query constraints, and each is assigned a named QML style before being added to the current QGIS project. If the `pyarchinit_us_view` layer fails validation, a warning dialog is displayed and the method returns `0`; if the layer is valid, the map canvas extent is updated to match it.

##### charge_layer_postgis(self, sito, area, us)

*No description available.*
Establishes a PostGIS database connection and loads two spatial vector layers — `"US"` (from the `pyarchinit_us_view` view) and `"Quote"` (from the `pyarchinit_quote` table) — filtered by the provided site (`sito`), area (`area`), and stratigraphic unit (`us`) identifiers. Both layers are assigned the coordinate reference system defined by `self.SRS` and added to the current QGIS project; if the `"US"` layer fails validation, the method returns `0` and does not proceed to load the `"Quote"` layer. If the `"US"` layer is valid, the map canvas extent is adjusted to match its extent before both layers are registered.

