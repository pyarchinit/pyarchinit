# PyArchInit - GeoArchaeo - Geostatistical Analysis

## Index
1. [Introduction](#introduction)
2. [Accessing the Tool](#accessing-the-tool)
3. [User Interface](#user-interface)
4. [Data Tab](#data-tab)
5. [Variogram Tab](#variogram-tab)
6. [Kriging Tab](#kriging-tab)
7. [Machine Learning Tab](#machine-learning-tab)
8. [Sampling Tab](#sampling-tab)
9. [Report Tab](#report-tab)
10. [Operational Workflow](#operational-workflow)
11. [Troubleshooting](#troubleshooting)
12. [Technical Notes](#technical-notes)

---

## Introduction

**GeoArchaeo** is the geostatistical analysis module integrated into PyArchInit. It provides a comprehensive suite of tools for spatial analysis of archaeological data, from variogram modelling to kriging interpolation, machine learning predictions, and sampling strategy design.

<!-- VIDEO: Introduction to GeoArchaeo -->
> **Video Tutorial**: [Insert video link GeoArchaeo introduction]

### Why geostatistical analysis in archaeology?

Geostatistical analysis allows you to:

- **Interpolate** values between known sampling points, creating continuous surfaces from discrete data
- **Quantify** the spatial correlation in archaeological data (e.g., find density, layer thickness)
- **Predict** spatial distributions in areas not yet excavated
- **Optimise** sampling strategies for future surveys
- **Generate** comprehensive analytical reports for scientific documentation

### Workflow Overview

```
1. Load Data           2. Variogram           3. Kriging/ML
   (Data Tab)             (Variogram Tab)        (Kriging/ML Tab)
        |                      |                      |
   Select layer           Compute and model       Interpolation or
   and fields             variogram               spatial prediction
                               |                      |
                          4. Sampling            5. Report
                             (Sampling Tab)         (Report Tab)
                                  |                      |
                             Design sampling      Generate analysis
                             strategy             report
```

---

## Accessing the Tool

GeoArchaeo is accessible from the PyArchInit toolbar through the Analysis Tools dropdown button.

### From the Toolbar

1. Locate the **Analysis Tools** button (dropdown icon) in the PyArchInit toolbar
2. Click the dropdown arrow
3. Select **GeoArchaeo** from the list

<!-- IMAGE: Analysis Tools button in the toolbar -->
> **Fig. 1**: The Analysis Tools dropdown menu in the PyArchInit toolbar

The GeoArchaeo panel appears as a **dock widget** attached to the QGIS interface. You can drag, resize, or detach it like any other QGIS panel.

<!-- IMAGE: GeoArchaeo panel docked in QGIS -->
> **Fig. 2**: The GeoArchaeo panel docked in the QGIS window

### Language Switcher

The GeoArchaeo panel includes a **language switcher** at the top, allowing you to change the interface language without restarting QGIS. Supported languages include Italian, English, German, French, Spanish, Arabic, Catalan, Romanian, Portuguese, and Greek.

---

## User Interface

The GeoArchaeo panel is organised into **6 main tabs**, each dedicated to a phase of the geostatistical analysis workflow.

| Tab | Icon | Function |
|-----|------|----------|
| **Data** | Table | Load and explore spatial data from QGIS layers |
| **Variogram** | Chart | Compute and model experimental variograms |
| **Kriging** | Grid | Perform kriging interpolation (ordinary, universal) |
| **ML** | Brain | Machine learning spatial predictions |
| **Sampling** | Target | Design sampling strategies for archaeological surveys |
| **Report** | Document | Generate analysis reports |

<!-- IMAGE: Overview of the 6 GeoArchaeo tabs -->
> **Fig. 3**: The six tabs of the GeoArchaeo panel

### Panel Toolbar

At the top of the panel you will find:

- **Language selector**: Dropdown to change the interface language
- **Load example data**: Button to load a test dataset
- **Help**: Button to access the documentation

---

## Data Tab

The **Data** tab is the starting point for any geostatistical analysis. It allows you to load and view spatial data available in QGIS layers.

### Loading Data

1. Open the **Data** tab
2. Select a **vector layer** from the dropdown (all point layers in the QGIS project are listed)
3. Select the **analysis field** (the numeric field to analyse)
4. Click **Load data**

<!-- IMAGE: Data tab with layer and field selected -->
> **Fig. 4**: The Data tab with a layer and analysis field selected

### Example Data

To familiarise yourself with the tool, you can load an **example dataset** by clicking the dedicated button. The example dataset contains simulated archaeological data with coordinates and numeric values suitable for geostatistical analysis.

### Data Exploration

After loading, the tab displays:

| Information | Description |
|-------------|-------------|
| **Number of points** | Total loaded points |
| **Extent** | Bounding box of the dataset (xmin, ymin, xmax, ymax) |
| **Statistics** | Mean, median, standard deviation, min, max |
| **Preview** | Table with the first rows of the dataset |

### Data Requirements

- The layer must be a **point vector layer**
- The analysis field must contain **numeric values**
- Points must have **valid coordinates** in the project's coordinate reference system
- At least **30 points** are recommended for meaningful geostatistical analysis

---

## Variogram Tab

The **Variogram** tab allows you to compute and model experimental variograms, which describe the spatial correlation structure in your data.

### What is a Variogram?

A variogram is a plot showing how the **variance** between pairs of points changes as a function of the **distance** separating them. The key parameters are:

| Parameter | Description |
|-----------|-------------|
| **Nugget** | Variance at zero distance (measurement error + micro-scale variability) |
| **Sill** | Maximum variance reached (variogram plateau) |
| **Range** | Distance beyond which there is no more spatial correlation |

### Computing the Experimental Variogram

1. Ensure you have loaded data in the Data tab
2. Open the **Variogram** tab
3. Set the parameters:
   - **Number of lags**: Number of distance intervals (default: 15)
   - **Maximum distance**: Maximum distance to consider (default: auto)
   - **Angular tolerance**: For directional variograms (default: omnidirectional)
4. Click **Compute variogram**

<!-- IMAGE: Computed experimental variogram -->
> **Fig. 5**: An experimental variogram computed from archaeological data

### Variogram Modelling

After computing the experimental variogram, you can fit a **theoretical model**:

1. Select the **model type**:
   - **Spherical**: The most common model, reaches the sill at a finite distance
   - **Exponential**: Reaches the sill asymptotically
   - **Gaussian**: Gradual transition, suitable for very smooth phenomena
   - **Linear**: Variogram without a defined sill
2. Click **Fit model**
3. Review the estimated parameters (nugget, sill, range) and goodness of fit

<!-- IMAGE: Fitted variogram model -->
> **Fig. 6**: Spherical model fitted to the experimental variogram

### Directional Variograms

To check for **anisotropy** (variation of spatial structure in different directions):

1. Set an **angular tolerance** (e.g., 22.5 degrees)
2. Select the **directions** to analyse (0, 45, 90, 135 degrees)
3. Compare the variograms in different directions

---

## Kriging Tab

The **Kriging** tab allows you to perform kriging interpolation, the gold standard geostatistical method for optimal spatial prediction.

### Available Kriging Types

| Type | Description | When to Use |
|------|-------------|-------------|
| **Ordinary kriging** | Assumes a constant but unknown local mean | Most common case, stationary data |
| **Universal kriging** | Accounts for a spatial trend (drift) | When data shows a directional trend |

### Running Kriging

1. Ensure you have modelled the variogram in the Variogram tab
2. Open the **Kriging** tab
3. Select the **kriging type** (ordinary or universal)
4. Set the output grid parameters:
   - **Resolution**: Grid cell size (in CRS units)
   - **Extent**: Automatic from dataset or custom
5. Set the kriging parameters:
   - **Minimum points**: Minimum number of nearby points to use
   - **Maximum points**: Maximum number of nearby points to use
   - **Search radius**: Maximum distance for nearby points
6. Click **Run kriging**

<!-- IMAGE: Kriging interpolation result -->
> **Fig. 7**: Kriging interpolation map with the prediction grid

### Kriging Results

The analysis produces two raster layers:

- **Prediction**: The interpolated values on the grid
- **Kriging variance**: The prediction uncertainty at each cell

The layers are automatically added to the QGIS project and displayed on the map.

> **Note**: The analysis runs in a **background thread**, so the QGIS interface remains usable during computation. A progress bar indicates the processing status.

---

## Machine Learning Tab

The **ML** tab offers machine learning methods for spatial predictions, as an alternative or complement to kriging.

### Available Algorithms

| Algorithm | Description | Advantages |
|-----------|-------------|------------|
| **Random Forest** | Ensemble of decision trees | Robust, handles non-linear relationships |
| **Gradient Boosting** | Sequential decision trees | High accuracy, suited for complex patterns |
| **SVR** | Support Vector Regression | Good with small datasets, flexible kernels |

### ML Workflow

1. Open the **ML** tab
2. Select the desired **algorithm**
3. Configure the **predictor variables**:
   - Coordinates (X, Y)
   - Additional fields from the layer (e.g., elevation, slope, distance to a river)
4. Set the algorithm **parameters** (or use defaults)
5. Select the **validation** method:
   - K-fold cross-validation (default: 5 folds)
   - Hold-out (test percentage)
6. Click **Train model**

<!-- IMAGE: ML model configuration -->
> **Fig. 8**: Random Forest model configuration in the ML tab

### ML Results

| Result | Description |
|--------|-------------|
| **Prediction map** | Raster layer with predicted values |
| **Variable importance** | Chart of relative importance of predictor variables |
| **Validation metrics** | R-squared, RMSE, MAE from cross-validation |
| **Residual plot** | Scatter plot of observed vs predicted values |

### Kriging vs ML Comparison

To compare results:

1. Run both kriging and ML on the same data
2. Compare validation metrics in the Report tab
3. Visualise difference maps

---

## Sampling Tab

The **Sampling** tab allows you to design optimal sampling strategies for future archaeological surveys.

### Sampling Strategies

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| **Simple random** | Points randomly distributed across the area | When you have no prior information |
| **Stratified random** | Random points within defined strata | When the area has zones with different characteristics |
| **Regular grid** | Points on a regular grid | For uniform area coverage |
| **Optimised** | Points positioned to minimise kriging variance | When you have a variogram |

### Designing a Sampling Plan

1. Open the **Sampling** tab
2. Select the **sampling strategy**
3. Set the desired **number of points**
4. Define the **study area**:
   - From the current layer extent
   - From a polygon layer
   - By drawing manually on the map
5. Set optional **constraints**:
   - Minimum distance between points
   - Exclusion areas
6. Click **Generate sampling**

<!-- IMAGE: Generated sampling points -->
> **Fig. 9**: Optimised sampling points overlaid on the study area map

### Sampling Results

- A **point vector layer** with sampling points is added to the QGIS project
- An **attribute table** with coordinates and point identifiers
- A **report** with strategy statistics (coverage, distances, etc.)

---

## Report Tab

The **Report** tab allows you to generate comprehensive geostatistical analysis reports.

### Report Contents

The report automatically includes all analyses performed during the session:

| Section | Content |
|---------|---------|
| **Summary** | Overview of the dataset and analyses performed |
| **Data** | Descriptive statistics, distribution, point map |
| **Variogram** | Experimental variogram, model, parameters |
| **Interpolation** | Kriging/ML map, validation metrics |
| **Sampling** | Strategy, point map, statistics |
| **Conclusions** | Summary interpretation of results |

### Generating a Report

1. Open the **Report** tab
2. Select the **sections** to include (all by default)
3. Set the **output format**:
   - PDF (recommended for documentation)
   - HTML (for interactive viewing)
   - Markdown (for later editing)
4. Enter any **additional notes** or comments
5. Click **Generate report**

<!-- IMAGE: Generated report preview -->
> **Fig. 10**: Preview of a geostatistical analysis report generated by GeoArchaeo

### Export

The report can be saved locally or exported in the available formats. Images (charts, maps) are embedded directly in the report.

---

## Operational Workflow

Here is a typical workflow for a complete geostatistical analysis in GeoArchaeo:

### Step 1: Data Preparation

1. Load your point vector layer into QGIS
2. Verify that the numeric field to analyse is present and correct
3. Check the coordinate reference system

### Step 2: Data Exploration

1. Open GeoArchaeo from the toolbar
2. In the **Data** tab, select the layer and field
3. Examine the descriptive statistics
4. Check the data distribution (look for outliers or anomalous values)

### Step 3: Variogram Analysis

1. In the **Variogram** tab, compute the experimental variogram
2. Try different models (spherical, exponential, Gaussian)
3. Choose the model with the best fit
4. Note the parameters (nugget, sill, range)

### Step 4: Interpolation

1. In the **Kriging** tab, set the grid parameters
2. Run ordinary kriging
3. Examine the prediction map and variance
4. Optionally, compare with an ML model in the ML tab

### Step 5: Sampling (optional)

1. In the **Sampling** tab, design a strategy for future surveys
2. Use the variogram for optimised sampling

### Step 6: Report

1. In the **Report** tab, generate the final report
2. Export as PDF for documentation

---

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| No layers available | No point layers in the project | Add a point vector layer to the QGIS project |
| No numeric fields | The layer has no numeric fields | Check the layer's attribute table |
| Flat variogram | Data with no spatial correlation | Check the data, increase the maximum distance |
| Kriging fails | Variogram model not fitted | Fit a model first in the Variogram tab |
| Poor ML results | Insufficient data or uninformative variables | Add predictor variables or increase the data |
| Panel not visible | Widget closed accidentally | Reopen from the Analysis Tools menu |

### Common Errors

- **"Insufficient data"**: At least 30 points are needed for reliable analysis
- **"Variogram model not defined"**: Fit a model before running kriging
- **"Incompatible CRS"**: All layers must use the same coordinate reference system

### Performance

- Analysis runs in a **background thread**: the QGIS interface remains usable
- For very large datasets (>10,000 points), processing may take longer
- You can monitor progress via the bar at the bottom of the panel

---

## Technical Notes

### Dependencies

GeoArchaeo uses the following Python libraries:

| Library | Usage |
|---------|-------|
| **NumPy** | Numerical and matrix computations |
| **SciPy** | Optimisation and model fitting |
| **scikit-learn** | Machine learning algorithms |
| **Matplotlib** | Chart generation |

### Coordinate Reference Systems

- GeoArchaeo works in the current QGIS project's coordinate reference system
- A **projected CRS** (in metres) is recommended for geostatistical analysis
- Geographic systems (in degrees) may produce inaccurate results

### Exporting Results

Results can be exported in various formats:

- **Raster layers** (GeoTIFF) for interpolated surfaces
- **Vector layers** (GeoPackage, Shapefile) for sampling points
- **Charts** (PNG, SVG) for variograms and diagnostics
- **Reports** (PDF, HTML, Markdown) for documentation

### QGIS Integration

- Output layers are automatically added to the QGIS **Layers** panel
- Raster layer styling can be customised using QGIS layer properties
- Results are compatible with all QGIS spatial analysis tools

---

> **Note**: GeoArchaeo is under active development. To report bugs or suggest improvements, please use the PyArchInit project's issue tracker on GitHub.
