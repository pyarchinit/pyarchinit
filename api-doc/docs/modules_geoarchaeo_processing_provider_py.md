# modules/geoarchaeo/processing_provider.py

## Overview

This file contains 63 documented elements.

## Classes

### GeoArchaeoProvider

Provider Processing per GeoArchaeo

**Inherits from**: QgsProcessingProvider

#### Methods

##### __init__(self, engine)

Initializes a new `GeoArchaeoProvider` instance by calling the parent `QgsProcessingProvider` constructor via `super().__init__()`. Accepts an `engine` parameter and assigns it to the instance attribute `self.engine` for use by the provider and its algorithms.

##### loadAlgorithms(self)

Carica tutti gli algoritmi

##### id(self)

*No description available.*
Returns the unique string identifier for this algorithm provider. This method overrides the base provider `id()` method and returns the fixed string `'geoarchaeo'`, which serves as the canonical identifier for the GeoArchaeo provider within the processing framework.

##### name(self)

*No description available.*
Returns the display name of the provider as the string `'GeoArchaeo'`. This method serves as the human-readable identifier for the provider, complementing the `id()` method which returns the internal identifier `'geoarchaeo'`.

##### icon(self)

Returns the icon associated with the GeoArchaeo algorithm, retrieved from the QGIS theme using the `/mActionShowStatisticalSummary.svg` asset. This method delegates to `QgsApplication.getThemeIcon` to obtain a `QIcon` instance representing the algorithm in the QGIS interface.

### VariogramAlgorithm

Algoritmo per calcolo e fitting variogramma

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes a `VariogramAlgorithm` instance by calling the parent `QgsProcessingAlgorithm` constructor via `super().__init__()`. Accepts an `engine` parameter and assigns it to the instance attribute `self.engine`.

##### name(self)

*No description available.*
Returns the unique string identifier for this processing algorithm. The method returns the fixed string `'variogram'`, which serves as the internal name used to reference the algorithm programmatically.

##### displayName(self)

*No description available.*
Returns the human-readable display name of the algorithm as a string. This method provides the localized Italian label `'Analisi Variogramma'`, which is intended for presentation in user-facing interfaces. It is distinct from `name()`, which returns the internal identifier `'variogram'`.

##### createInstance(self)

*No description available.*
Creates and returns a new instance of `VariogramAlgorithm`, initialized with the current `engine` attribute. This method is used by the processing framework to instantiate a fresh copy of the algorithm. It returns a `VariogramAlgorithm` object.

##### initAlgorithm(self, config)

Initializes the algorithm's parameters by registering all required inputs and outputs via `addParameter`. The method defines six parameters: a point vector layer (`INPUT`), a numeric field (`FIELD`) from that layer, a maximum distance value (`MAX_DISTANCE`) defaulting to `100.0`, a variogram model enumeration (`MODEL`) with options `['Sferico', 'Esponenziale', 'Gaussiano', 'Matérn']` defaulting to index `0`, a boolean anisotropy flag (`ANISOTROPY`) defaulting to `False`, and a JSON file destination (`OUTPUT`). The optional `config` argument is accepted but not used within the method body.

##### processAlgorithm(self, parameters, context, feedback)

Executes the variogram calculation algorithm by extracting the input vector layer, field name, maximum distance, variogram model type, and anisotropy flag from the provided parameters. It iterates over all features in the layer to collect point coordinates and field values, then delegates the variogram computation to `self.engine.calculate_variogram` using the resolved model type (one of `'spherical'`, `'exponential'`, `'gaussian'`, or `'matern'`). The resulting variogram data is serialized as JSON and written to the specified output file path, which is returned as the method's result.

### OrdinaryKrigingAlgorithm

Ordinary Kriging implementation

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes an `OrdinaryKrigingAlgorithm` instance by calling the parent `QgsProcessingAlgorithm` constructor and storing the provided `engine` parameter as an instance attribute. Accepts a single argument, `engine`, which is assigned to `self.engine` for use by the algorithm.

##### name(self)

*No description available.*
Returns the unique programmatic identifier for this algorithm. The method provides the internal string `'ordinarykriging'`, which serves as the canonical machine-readable name used to reference this algorithm within the engine. This identifier is distinct from the human-readable display name returned by `displayName()`.

##### displayName(self)

*No description available.*
Returns the human-readable display name for this algorithm. This method provides the string `'Ordinary Kriging'`, which is intended for presentation in user interfaces as opposed to the internal identifier returned by `name()`.

##### createInstance(self)

*No description available.*
Creates and returns a new instance of `OrdinaryKrigingAlgorithm`, initialized with the current `engine`. This method is used to produce a fresh copy of the algorithm object, passing the existing `engine` attribute to the new instance's constructor.

##### initAlgorithm(self, config)

Initializes the Ordinary Kriging algorithm by registering all required and optional processing parameters. The method adds the following parameters: a point vector layer input (`INPUT`), a numeric field selector (`FIELD`), an output extent (`EXTENT`), a pixel size value (`PIXEL_SIZE`) defaulting to `1.0`, an optional JSON file destination for the variogram (`VARIOGRAM`), and a raster destination for the Kriging output (`OUTPUT`). This method accepts an optional `config` argument in accordance with the QGIS Processing framework interface.

##### processAlgorithm(self, parameters, context, feedback)

Executes the Ordinary Kriging interpolation algorithm by extracting point geometries and field values from the input vector layer, then loading variogram parameters from a file or computing them automatically if no valid file is provided. It performs Ordinary Kriging interpolation over the specified extent and pixel size using the resolved variogram parameters, then writes the resulting prediction grid to a single-band floating-point raster output via `QgsRasterFileWriter`. Returns a dictionary containing the path to the generated output raster layer.

### CoKrigingAlgorithm

Co-Kriging multivariabile per GPR + Magnetometria

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes a `CoKrigingAlgorithm` instance by invoking the parent `QgsProcessingAlgorithm` constructor via `super().__init__()`. Accepts an `engine` parameter and assigns it to the instance attribute `self.engine`.

##### name(self)

*No description available.*
Returns the unique string identifier for this processing algorithm. The method returns the fixed string `'cokriging'`, which serves as the internal name used to reference this algorithm within the engine. This identifier distinguishes the algorithm from others registered in the same processing framework.

##### displayName(self)

*No description available.*
Returns the human-readable display name of the algorithm as a string. Specifically, it returns the fixed string `'Co-Kriging Multivariabile'`, which serves as the user-facing label for the Co-Kriging algorithm. This differs from `name()`, which returns the internal identifier `'cokriging'`.

##### createInstance(self)

*No description available.*
Creates and returns a new instance of `CoKrigingAlgorithm`, initialized with the current `engine` attribute. This method is used to instantiate a fresh copy of the algorithm object, passing `self.engine` as a constructor argument.

##### initAlgorithm(self, config)

Initializes the Co-Kriging algorithm by registering all required input and output parameters. The method adds a primary vector point layer (`PRIMARY`) with its associated numeric field (`PRIMARY_FIELD`), one or more secondary vector point layers (`SECONDARY`) with an optional comma-separated field specification (`SECONDARY_FIELDS`), an output extent (`EXTENT`), a pixel size value (`PIXEL_SIZE`) defaulting to `1.0`, and a raster destination (`OUTPUT`). The optional `config` parameter is accepted but not used within the method body.

##### processAlgorithm(self, parameters, context, feedback)

Executes the Co-Kriging interpolation algorithm by extracting point geometries and field values from a primary vector layer and one or more secondary vector layers, then passing the collected data to the engine's `co_kriging` method along with the specified extent and pixel size. The resulting predictions are written to a single-band floating-point raster output using `QgsRasterFileWriter`, with dimensions derived from the extent and pixel size parameters and a no-data value of `-9999`. Returns a dictionary containing the path to the generated output raster under the key `'OUTPUT'`.

### SpatioTemporalKrigingAlgorithm

Kriging Spazio-Temporale per fasi di scavo

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes a new instance of `SpatioTemporalKrigingAlgorithm` by calling the parent `QgsProcessingAlgorithm` constructor via `super().__init__()`. Accepts a single `engine` parameter and assigns it to the instance attribute `self.engine`.

##### name(self)

*No description available.*
Returns the unique identifier string for this processing algorithm. The method returns the fixed string `'spatiotemporal'`, which serves as the internal programmatic name used to reference this algorithm. This identifier is distinct from the human-readable display name provided by `displayName()`.

##### displayName(self)

*No description available.*
Returns the human-readable display name of the algorithm. This method overrides the base class implementation to provide the localized Italian label `'Kriging Spazio-Temporale'`, which identifies the algorithm in user-facing interfaces. It takes no parameters and returns a string.

##### createInstance(self)

*No description available.*
Creates and returns a new instance of `SpatioTemporalKrigingAlgorithm`, initialized with the current object's `engine` attribute. This method is used to produce a fresh copy of the algorithm, as required by the QGIS Processing framework.

##### initAlgorithm(self, config)

Initializes the algorithm's parameters by registering all required inputs and outputs for spatio-temporal kriging interpolation. The method adds the following parameters: a point vector layer (`INPUT`), a numeric value field (`VALUE_FIELD`), a datetime field (`TIME_FIELD`), a target datetime for interpolation (`TARGET_TIME`), a temporal range in days (`TIME_RANGE`) with a default value of `30.0`, and a raster destination (`OUTPUT`). The optional `config` parameter is accepted but not used within the method body.

##### processAlgorithm(self, parameters, context, feedback)

Executes the spatiotemporal kriging algorithm by extracting features from the input vector layer and filtering them to include only those whose temporal values fall within the specified range (in days) relative to the target datetime. The filtered space-time data points are passed to `self.engine.spatiotemporal_kriging`, and the resulting prediction grid is written to a single-band floating-point raster output using `QgsRasterFileWriter`, with a no-data value of `-9999`. Returns a dictionary containing the path to the generated output raster layer.

### CompositionalAnalysisAlgorithm

Analisi composizionale con trasformazioni CLR/ILR

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes a `CompositionalAnalysisAlgorithm` instance by calling the parent `QgsProcessingAlgorithm` constructor and storing the provided `engine` parameter as an instance attribute. Accepts a single argument, `engine`, which is assigned to `self.engine` for use by the algorithm.

##### name(self)

*No description available.*
Returns the unique identifier string for this processing algorithm. The method returns the fixed string `'compositional'`, which serves as the internal name used to reference this algorithm programmatically. This identifier distinguishes the algorithm from others registered within the processing framework.

##### displayName(self)

*No description available.*
Returns the human-readable display name for this algorithm as a localized string. Specifically, it returns the Italian label `'Analisi Composizionale Terreno'`, which identifies this algorithm in the user interface. This method overrides the base class implementation to provide a descriptive, locale-specific name distinct from the internal identifier returned by `name()`.

##### createInstance(self)

*No description available.*
Creates and returns a new instance of `CompositionalAnalysisAlgorithm`, initialized with the current object's `engine`. This method is used to produce a fresh copy of the algorithm, as required by the QGIS Processing framework.

##### initAlgorithm(self, config)

Initializes the algorithm's parameters by registering four processing inputs and one output with the QGIS Processing framework. The parameters consist of a vector point layer (`INPUT`), one or more numeric compositional fields from that layer (`COMP_FIELDS`), an enumeration for the log-ratio transformation type (`TRANSFORM`) with options CLR, ILR, and ALR (defaulting to CLR), and a raster destination (`OUTPUT`). This method is called automatically by the framework before execution to define the algorithm's interface.

##### processAlgorithm(self, parameters, context, feedback)

Executes the compositional raster analysis algorithm by extracting vector layer features and their associated compositional field values, applying a user-selected log-ratio transformation (`clr`, `ilr`, or `alr`) via the engine's `compositional_analysis` method, and then performing ordinary kriging on each transformed component. The kriging predictions are written to a multi-band floating-point raster output, where each band corresponds to one transformed compositional component interpolated over a grid derived from the input layer's extent. Returns a dictionary containing the file path of the generated output raster under the key `'OUTPUT'`.

### MLPatternRecognitionAlgorithm

Machine Learning per pattern recognition archeologico

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes a new instance of `MLPatternRecognitionAlgorithm` by calling the parent `QgsProcessingAlgorithm` constructor via `super().__init__()`. Accepts an `engine` parameter and assigns it to the instance attribute `self.engine`.

##### name(self)

*No description available.*
Returns the unique string identifier for this processing algorithm. The method returns the fixed string `'mlpattern'`, which serves as the internal name of the algorithm. This identifier is distinct from the human-readable display name provided by `displayName()`.

##### displayName(self)

*No description available.*
Returns the human-readable display name of the algorithm as a string. This method provides the user-facing label `'ML Pattern Recognition'`, which is distinct from the internal identifier returned by `name()`. The returned string is intended for presentation in user interfaces or listings where a descriptive name is required.

##### createInstance(self)

Creates and returns a new instance of `MLPatternRecognitionAlgorithm`, initialized with the current `engine`. This method is used to instantiate a fresh copy of the algorithm, passing the existing engine as a constructor argument.

##### initAlgorithm(self, config)

Initializes the algorithm's parameters by registering the required and optional inputs for the ML pattern recognition processing workflow. It adds a multiple vector layer input (`INPUTS`), an enumeration parameter (`ML_METHOD`) offering six machine learning methods (Random Forest, SVM, Neural Network, Clustering (K-Means), DBSCAN, and Isolation Forest), an optional point vector layer for training data (`TRAINING`), and a raster destination parameter for the output predictions map (`OUTPUT`). This method accepts an optional `config` argument but does not apply it within the visible implementation.

##### processAlgorithm(self, parameters, context, feedback)

Executes the ML-based pattern recognition processing algorithm by retrieving input raster layers, the selected machine learning method, and an optional training vector layer from the provided parameters. Depending on the chosen method (`rf`, `svm`, `nn`, `kmeans`, `dbscan`, or `isolation`) and the presence of a training layer, it performs either supervised learning (training a model and generating predictions) or unsupervised learning (clustering). The resulting predictions are mapped onto a raster grid derived from the combined extent of the input layers and written to the specified output raster file, which is returned as `{'OUTPUT': output_path}`.

### BatchKrigingAlgorithm

Batch processing per dataset grandi con tiling

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes a `BatchKrigingAlgorithm` instance by calling the parent `QgsProcessingAlgorithm` constructor and storing the provided `engine` parameter as an instance attribute. Accepts a single argument, `engine`, which is assigned to `self.engine` for use by the algorithm.

##### name(self)

*No description available.*
Returns the unique string identifier for this processing algorithm. The returned value is `'batchkriging'`, which serves as the internal name used to reference this algorithm programmatically. This identifier is distinct from the human-readable display name provided by `displayName()`.

##### displayName(self)

*No description available.*
Returns the human-readable display name for the algorithm as the string `'Batch Kriging (Dataset Grandi)'`. This name is intended for presentation in user interfaces, distinguishing it from the internal identifier returned by `name()`, which yields `'batchkriging'`.

##### createInstance(self)

*No description available.*
Returns a new instance of `BatchKrigingAlgorithm`, initialized with the current `engine` attribute. This method is used by the processing framework to instantiate a fresh copy of the algorithm.

##### initAlgorithm(self, config)

Initializes the algorithm by registering all required input and output parameters for the batch Kriging process. The method adds a point vector layer input (`INPUT`), a numeric field selector (`FIELD`), a tile size in meters (`TILE_SIZE`), a tile overlap percentage (`OVERLAP`, ranging from 0 to 50), a maximum points-per-tile integer (`MAX_POINTS_PER_TILE`), and a raster destination for the final mosaic output (`OUTPUT`). The optional `config` parameter is accepted but not used within the method body.

##### processAlgorithm(self, parameters, context, feedback)

Executes the tiled kriging interpolation algorithm by retrieving input parameters (vector layer, field name, tile size, overlap, and maximum points per tile), then partitions the layer's extent into overlapping tiles and applies kriging interpolation to each tile containing more than 10 points. Tile results are merged into a final mosaic raster, which is written to the specified output path as a single-band Float32 raster using `QgsRasterFileWriter` and `QgsRasterBlock`. Returns a dictionary mapping `'OUTPUT'` to the output raster file path.

### OptimalSamplingAlgorithm

Design campionamento ottimale

**Inherits from**: QgsProcessingAlgorithm

#### Methods

##### __init__(self, engine)

Initializes an instance of `OptimalSamplingAlgorithm` by calling the parent `QgsProcessingAlgorithm` constructor via `super().__init__()`. Accepts a single `engine` parameter and assigns it to the instance attribute `self.engine`.

##### name(self)

*No description available.*
Returns the unique string identifier for this processing algorithm. The method returns the fixed string `'optimalsampling'`, which serves as the internal programmatic name used to reference and identify the algorithm within the engine. This identifier is distinct from the human-readable display name provided by `displayName()`.

##### displayName(self)

*No description available.*
Returns the human-readable display name of the algorithm as a string. This method provides the localized Italian label `'Design Campionamento Ottimale'`, which is used to identify the algorithm in user-facing interfaces. It serves as the presentational counterpart to the internal identifier returned by `name()`.

##### createInstance(self)

*No description available.*
Returns a new instance of `OptimalSamplingAlgorithm`, initialized with the current `engine` attribute. This method is used by the QGIS processing framework to create a fresh copy of the algorithm.

##### initAlgorithm(self, config)

Initializes the algorithm's parameters by registering the input and output definitions required for the optimal sampling workflow. It adds two vector layer inputs (`EXISTING` for existing point locations and `BOUNDARY` for the study area polygon), an integer parameter (`N_NEW`) specifying the number of new points to generate with a default value of 10, an enumeration parameter (`METHOD`) offering four sampling strategies (`Maximin`, `Riduzione Varianza`, `Stratificato`, `Adattivo`) with a default of index 1, and a vector destination parameter (`OUTPUT`) for the suggested sampling points. This method accepts an optional `config` argument and follows the QGIS Processing framework convention for parameter registration.

##### processAlgorithm(self, parameters, context, feedback)

*No description available.*
Executes the sampling design algorithm by extracting existing point features from a vector layer and a boundary polygon, then computing a set of new optimal sampling points using the selected method (`maximin`, `variance`, `stratified`, or `adaptive`) via `self.engine.optimal_sampling_design`. The resulting points are written to an output Shapefile with fields `id` (integer), `type` (string, fixed to `'suggested'`), and `priority` (double, descending from `1.0`). Returns a dictionary containing the path to the generated output layer under the key `'OUTPUT'`.

