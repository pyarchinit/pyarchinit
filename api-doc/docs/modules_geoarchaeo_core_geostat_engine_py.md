# modules/geoarchaeo/core/geostat_engine.py

## Overview

This file contains 34 documented elements.

## Classes

### GeostatEngine

Motore geostatistico avanzato con ML e analisi composizionale

#### Methods

##### __init__(self)

*No description available.*
Initializes a new `GeostatEngine` instance by setting up its core attributes. An empty dictionary `models` and an empty dictionary `cache` are created to store models and cached data respectively. The `ml_available` and `plotly_available` flags are set from the module-level constants `ML_AVAILABLE` and `PLOTLY_AVAILABLE`, indicating the availability of optional ML and Plotly dependencies.

##### calculate_variogram(self, points, values, max_distance, model_type, check_anisotropy)

Calcola variogramma con supporto anisotropia

##### ordinary_kriging(self, points, values, extent, pixel_size, variogram_params)

Ordinary Kriging implementation - optimized and robust version

##### co_kriging(self, primary_points, primary_values, secondary_data, extent, pixel_size)

Co-Kriging multivariabile

##### spatiotemporal_kriging(self, space_time_data, target_time, extent)

Kriging spazio-temporale

##### compositional_analysis(self, points, compositions, transform_type)

Analisi composizionale con trasformazioni log-ratio

##### prepare_ml_features(self, layers)

Prepara features per Machine Learning da layer QGIS

##### extract_labels(self, training_layer)

Estrai etichette da layer di training

##### ml_pattern_recognition(self, layers_data, method)

Pattern recognition con Machine Learning

##### train_ml_model(self, features, labels, method)

Training modello ML supervisionato

##### unsupervised_ml(self, features, method)

Clustering o anomaly detection non supervisionato

##### create_tiles(self, extent, tile_size, overlap_percent)

Crea tiles con overlap per batch processing

##### extract_points_in_tile(self, layer, tile, max_points)

Estrae punti in un tile specifico

##### extract_points_in_tile_with_field(self, layer, tile, field_name, max_points)

Estrae punti in un tile con campo specifico

##### kriging_tile(self, tile_data, tile)

Esegue kriging su un singolo tile

##### merge_tiles(self, tile_results, extent)

Unisce tiles processati in raster finale

##### optimal_sampling_design(self, existing_points, boundary_geom, n_new, method)

Calcola design campionamento ottimale

##### create_interactive_variogram(self, variogram_data)

Crea grafico variogramma interattivo con Plotly

##### create_interactive_kriging_map(self, x, y, predictions, variances, data_points)

Crea mappa kriging interattiva con Plotly

##### create_ml_visualization(self, features, labels, method_name)

Visualizzazione risultati Machine Learning

##### compositional_clr_transform(self, comp_data)

Centered Log-Ratio transformation per dati composizionali

##### compositional_ilr_transform(self, comp_data)

Isometric Log-Ratio transformation per dati composizionali

### DummyBBox

*No description available.*
A locally-defined surrogate bounding box class used as a fallback when no boundary geometry is available. It stores minimum and maximum coordinate values along both axes and exposes them through `xMinimum()`, `xMaximum()`, `yMinimum()`, `yMaximum()`, `width()`, and `height()` methods, mirroring the interface of a standard geometry bounding box object. Instances are initialised with explicit `xmin`, `xmax`, `ymin`, and `ymax` values; `width()` and `height()` are computed as the difference between the respective maximum and minimum values.

#### Methods

##### __init__(self, xmin, xmax, ymin, ymax)

Initializes a stratified sampling instance on a regular grid. If `boundary_geom` is not provided, a `DummyBBox` object is constructed internally using the minimum and maximum coordinate values derived from the data, exposing `xMinimum`, `xMaximum`, `yMinimum`, `yMaximum`, and `width` accessors. The `DummyBBox` serves as a fallback bounding box when no explicit boundary geometry is supplied.

##### xMinimum(self)

*No description available.*
Returns the minimum x-coordinate of the bounding extent. This value corresponds to the `_xmin` field set during initialization. No parameters are accepted and the stored numeric value is returned directly.

##### xMaximum(self)

*No description available.*
Returns the maximum x-coordinate of the bounding rectangle. This value corresponds to the `_xmax` field set during object initialisation. Use this method to retrieve the right-hand boundary of the extent.

##### yMinimum(self)

*No description available.*
Returns the minimum Y-coordinate value of the bounding box. This value corresponds to the `_ymin` instance attribute set during initialization.

##### yMaximum(self)

*No description available.*
Returns the maximum Y-coordinate value of the bounding box. This value is stored in the internal `_ymax` attribute and represents the upper boundary of the bounding box along the Y axis.

##### width(self)

*No description available.*
Returns the width of the bounding box as a numeric value. It is calculated by subtracting `_xmin` from `_xmax`, representing the horizontal extent of the bounding box. No parameters are accepted and no exceptions are documented in the source.

##### height(self)

*No description available.*
Returns the height of the bounding box as a numeric value. It is computed by subtracting the minimum y-coordinate (`_ymin`) from the maximum y-coordinate (`_ymax`). This method provides the vertical extent of the bounding box along the y-axis.

## Functions

### objective(params)

*No description available.*
An inner objective function used for variogram model fitting that computes the sum of squared residuals between observed semivariances and model-predicted values. It accepts a parameter vector `params` containing `nugget`, `sill`, and `range_val`, and returns a penalty value of `1e10` if any parameter violates physical constraints (negative nugget, sill less than nugget, or non-positive range). Otherwise, it evaluates the specified variogram model via `self._evaluate_model` and returns the total squared error, which is minimized by the enclosing `minimize` call using the L-BFGS-B method.

**Parameters:**
- `params`

### log(msg)

*No description available.*
Appends a timestamped message to a log file located at `~/Desktop/geoarchaeo_kriging_log.txt`. Each entry is prefixed with the current time formatted as `HH:MM:SS.ffffff` and followed by a newline, with the file buffer flushed immediately after writing. All exceptions raised during the write operation are silently suppressed.

**Parameters:**
- `msg`

