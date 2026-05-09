# modules/gis/pyarchinit_pyqgis_archeozoo.py

## Overview

This file contains 22 documented elements.

## Classes

### Pyarchinit_pyqgis

`Pyarchinit_pyqgis` is a QGIS dialog class that manages the loading and registration of vector layers from either a SpatiaLite or PostgreSQL database into the QGIS map canvas, based on the connection settings read from a `config.cfg` file. It provides methods to charge stratigraphic unit (US) and elevation (quote) views filtered by record identifiers or chronological period, applying named QML styles where applicable. The class also exposes utility methods for interacting with the QGIS interface, including retrieving data provider fields, selected features, and attribute map values from the currently active map layer.

**Inherits from**: QDialog

#### Methods

##### __init__(self, iface)

*No description available.*
Initializes the instance by calling the parent class constructor via `super().__init__()` and storing the provided `iface` argument as an instance attribute. The `iface` parameter is assigned to `self.iface` for later use by the class.

##### remove_USlayer_from_registry(self)

*No description available.*
Removes the US (Unità Stratigrafica) map layer identified by `self.USLayerId` from the current QGIS project's map layer registry by calling `QgsProject.instance().removeMapLayer()`. Returns `0` upon completion.

##### charge_individui_us(self, data)

Loads spatial vector layers for stratigraphic unit (US) records into the QGIS map registry based on a list of record identifiers provided in `data`. The method reads database connection settings from a `config.cfg` file and branches its behavior depending on whether the configured server is `sqlite` or `postgres`: for SQLite, it constructs a `spatialite`-backed `QgsVectorLayer` from `pyarchinit_us_view` and `pyarchinit_quote_view` filtered by `id_us`; for PostgreSQL, it connects using host/port/credentials and loads `pyarchinit_archeozoo_view` and `pyarchinit_quote_view` filtered by `id_archzoo`, applying named styles where applicable. Valid layers are added to the current `QgsProject` instance.

##### charge_vector_layers(self, data)

Loads vector layers from either a SQLite/SpatiaLite or PostgreSQL database into the current QGIS project based on the server type specified in the configuration file. For each backend, it constructs a filtered data source URI using record identifiers from the provided `data` list, then creates and validates `QgsVectorLayer` instances for archaeological unit and elevation/quote views. Valid layers have a named style applied and are added to the QGIS project; invalid layers trigger a warning dialog.

##### charge_vector_layers_periodo(self, cont_per)

*No description available.*
Loads vector layers filtered by a given chronological period (`cont_per`) into the QGIS map canvas, supporting both SQLite/SpatiaLite and PostgreSQL/PostGIS database backends as determined by the application configuration. The filter expression matches records where `cont_per` equals the specified value exactly or contains it as a path-delimited segment. Depending on the backend, it attempts to add a stratigraphic unit view layer (`pyarchinit_us_view` or `pyarchinit_archeozoo_view`) and a elevation/quote view layer (`pyarchinit_quote_view`), applying named QML styles and registering valid layers with the current QGIS project.

##### loadMapPreview(self, gidstr)

if has geometry column load to map canvas 

##### dataProviderFields(self)

*No description available.*
Retrieves the fields from the data provider of the currently active layer on the map canvas. It accesses the current layer via `iface.mapCanvas().currentLayer()`, calls `dataProvider().fields()` on it, and returns the resulting fields object.

##### selectedFeatures(self)

*No description available.*
Retrieves the currently selected features from the active layer on the map canvas. It accesses the current layer via `self.iface.mapCanvas().currentLayer()` and calls `selectedFeatures()` on it, returning the resulting collection of selected features.

##### findFieldFrDict(self, fn)

*No description available.*
Searches the fields dictionary returned by `dataProviderFields()` for a field whose `.name()` matches the provided field name argument `fn`. Iterates over all keys in the dictionary and assigns the matching key to `res` upon a name match. Returns the key corresponding to the field with the given name.

##### findItemInAttributeMap(self, fp, fl)

*No description available.*
Accepts a field position `fp` and a features list `fl`, assigning them to the instance attributes `self.field_position` and `self.features_list` respectively. Iterates over the currently selected features of the active map canvas layer, retrieving the attribute value at the specified field position from each feature's attribute map and converting it to a string. Returns a list of those string values collected from all selected features.

### Order_layers

*No description available.*
A stratigraphic ordering engine that processes a list of stratigraphic relationship tuples and computes a sequential ordering of stratigraphic units (US). It implements an iterative algorithm that identifies units appearing only at the top of the stratigraphic sequence, assigns them progressive order levels in `DIZ_ORDER_LAYERS`, and removes their associated relationships from `LISTA_RAPPORTI` until all units have been assigned a level. The class includes paradox detection via `check_status` and `stop_while` controls, and writes diagnostic output files to the path defined by `REPORT_PATH`.

**Inherits from**: object

#### Methods

##### __init__(self, lr)

*No description available.*
Initializes the instance by accepting a list of stratigraphic relationship tuples (`lr`) and assigning it to the instance attribute `LISTA_RAPPORTI`. The list is immediately sorted in place, and the instance attribute `status` is set to the current length of `LISTA_RAPPORTI` to serve as a baseline for detecting changes during subsequent processing loops.

##### main(self)

*No description available.*
Serves as the primary entry point for the layer-ordering process by first invoking `add_values_to_lista_us()` to populate the US (stratigraphic unit) value list from the stratigraphic relationships list. It then iterates via `loop_on_lista_us()` in a `while` loop for as long as `LISTA_RAPPORTI` is non-empty and `stop_while` remains unset. Upon exhaustion of `LISTA_RAPPORTI`, any remaining entries in `LISTA_US` are individually registered via `add_key_value_to_diz()`, and the completed `DIZ_ORDER_LAYERS` dictionary is returned.

##### add_values_to_lista_us(self)

*No description available.*
Populates `self.LISTA_US` by iterating over `self.LISTA_RAPPORTI` and extracting unique stratigraphic unit (US) values from each relationship pair. If both elements of a pair are identical, the pair is written as an error message to `errori_in_add_value.txt` in `self.REPORT_PATH`; otherwise, each element is appended to `self.LISTA_US` if not already present. After processing all relationships, `self.LISTA_US` is sorted and its contents are written to `test_lista_us.txt` in the same report path.

##### loop_on_lista_us(self)

*No description available.*
Iterates over `LISTA_US` and evaluates each stratigraphic unit (US) by calling `check_position`. If `check_position` returns `1`, the unit is removed from `LISTA_US`; if it returns `0`, the current `TUPLE_TO_REMOVING` list is cleared and iteration continues to the next unit. A stall-detection mechanism tracks how many consecutive iterations produce no change in `status` relative to `LISTA_RAPPORTI`, and sets `stop_while` if the threshold of 10 is exceeded, signalling a potential stratigraphic paradox.

##### check_position(self, n)

*No description available.*
Checks whether a given stratigraphic unit (US) number occupies the top position in the stratigraphic relationship list (`LISTA_RAPPORTI`). It iterates over all relationship tuples: if the US appears in the second position of any tuple, it is not at the top and the method takes no further action; if it appears only in the first position, the corresponding tuples are collected in `TUPLE_TO_REMOVING`, written to a diagnostic file (`check_tuple.txt`), and then removed from `LISTA_RAPPORTI` after calling `add_key_value_to_diz`. Returns `1` if the US was found at the top of the stratigraphic sequence and processed; otherwise returns `None` implicitly.

##### add_key_value_to_diz(self, n)

*No description available.*
Adds a new key-value pair to the `DIZ_ORDER_LAYERS` dictionary using the provided value `n`. Before inserting, it increments `MAX_VALUE_KEYS` by one, which serves as the new dictionary key, then assigns `n` as the corresponding value. The parameter `n` represents the US (Stratigraphic Unit) number to be stored in the dictionary.

### MyError

*No description available.*
A custom exception class that extends the built-in `Exception` class. It accepts a single `value` parameter upon instantiation, which is stored as an instance attribute. The `__str__` method returns the `repr()` representation of the stored `value`.

**Inherits from**: Exception

#### Methods

##### __init__(self, value)

*No description available.*
Initializes a new instance of the `MyError` exception class. Accepts a single argument `value` and assigns it to the instance attribute `self.value`.

##### __str__(self)

*No description available.*
Returns the string representation of the exception instance. Specifically, it returns `repr(self.value)`, producing a printable representation of the `value` attribute set during initialization. This method is invoked when the object is converted to a string, such as via `str()` or `print()`.

