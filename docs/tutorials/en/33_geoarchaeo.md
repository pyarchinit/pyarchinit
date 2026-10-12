# PyArchInit - GeoArchaeo - Geostatistical Analysis

## Index
1. [Introduction](#introduction)
2. [Accessing the Tool](#accessing-the-tool)
3. [User Interface](#user-interface)
4. [Data Tab](#data-tab)
5. [Variogram Tab](#variogram-tab)
6. [Kriging Tab](#kriging-tab)
7. [Patterns (ML) Tab](#patterns-ml-tab)
8. [Sampling Tab](#sampling-tab)
9. [Report Tab](#report-tab)
10. [Operational Workflow](#operational-workflow)
11. [Troubleshooting](#troubleshooting)
12. [Technical Notes](#technical-notes)

---

## Introduction

**GeoArchaeo** is the geostatistical analysis module built into PyArchInit; it corresponds to version **1.3.1** of the GeoArchaeo plugin. It works on any point layer of the QGIS project that has a numeric field (sherd counts, geophysical readings, soil analyses, tomb measurements…) and takes the analysis from descriptive statistics to the variogram, to ordinary kriging interpolation with its uncertainty, to the search for groups and anomalies with machine learning, to the proposal of new sampling locations, and finally to a report.

<!-- VIDEO: Introduction to GeoArchaeo -->
> **Video Tutorial**: [Insert video link GeoArchaeo introduction]

### Why geostatistical analysis in archaeology?

Geostatistical analysis allows you to:

- **Describe** the distribution of the measured values (mean, spread, skewness, outliers)
- **Quantify** spatial correlation, i.e. up to what distance values resemble each other (variogram)
- **Interpolate** values between known points, producing a continuous surface together with its uncertainty (kriging)
- **Recognise** groups of similar points and anomalies (machine learning)
- **Plan** where to sample or excavate in the next campaigns
- **Document** the analyses in a report

### Workflow Overview

```
Input data: point layer + numeric field (chosen at the top, only once)
  │
  ├─ 1 Data ............ descriptive statistics, histogram
  ├─ 2 Variogram ....... nugget, sill, range, anisotropy
  ├─ 3 Kriging ......... estimate and uncertainty rasters, cross-validation
  ├─ 4 Patterns (ML) ... groups and anomalies (point layer)
  ├─ 5 Sampling ........ proposed new points (point layer)
  └─ 6 Report .......... HTML document with interactive charts, or PDF
```

### What's new in version 1.3.1

- Layer and field are chosen **once** at the top and apply to every tab; each tab keeps its own results
- Charts appear in the panel even without QtWebEngine (static preview plus a button to open them in the browser)
- Kriging also produces the **uncertainty raster**, applies the colour ramp and computes a real **leave-one-out cross-validation**
- Anisotropy is checked with real **directional variograms**; nugget, sill and range can be set by hand
- Variogram and kriging are much faster (KD-tree neighbour search): grids up to **500 × 500 cells**
- NULL values no longer break statistics or kriging; the report includes the charts; the example data come from the module folder
- The panel language is stored in the QGIS settings

---

## Accessing the Tool

GeoArchaeo belongs to the PyArchInit group of analysis tools.

### From the Toolbar

1. In the PyArchInit toolbar, find the drop-down button of the **analysis tools** (the same group that contains, among others, SAM, Pottery Tools and MoveCost)
2. Click the arrow next to the button: the visible icon may belong to another tool of the group
3. Choose **GeoArchaeo - Geostatistical Analysis**

<!-- IMAGE: Analysis tools drop-down button in the toolbar -->
> **Fig. 1**: The analysis tools drop-down menu in the PyArchInit toolbar

The same entry is in the **pyArchInit** menu of the QGIS menu bar and in the plugins menu, under **pyArchInit - Archaeological GIS Tools**.

The GeoArchaeo panel opens as a **dock widget** on the right side of the QGIS window: it can be moved, resized or detached like any other QGIS panel. If you close it, the same entry reopens it with the results of the session still there.

<!-- IMAGE: GeoArchaeo panel docked on the right side of QGIS -->
> **Fig. 2**: The GeoArchaeo panel docked on the right side of the QGIS window

### Language Switcher

At the top right, the **«Language:»** drop-down offers **Italiano** and **English**, the only two languages of the GeoArchaeo interface. The change is immediate, without restarting QGIS, and the choice is stored in the QGIS settings. Until you choose, the panel follows the QGIS language: Italian if QGIS is in Italian, English in every other case.

---

## User Interface

From top to bottom the panel contains: the header with its buttons, the **«Input data (used by all tabs)»** group, the **6 analysis tabs** and, while a computation runs, the progress bar with the **«Cancel»** button.

### Header

| Element | Function |
|---------|----------|
| **«Load example data»** | Opens the list of the test datasets shipped with the module (see the Data tab) |
| **«Tutorial»** | Opens the built-in GeoArchaeo guide, in Italian or English, which can also be opened in the browser |
| **«Language:»** | Italiano / English drop-down |

### Input Data

In the **«Input data (used by all tabs)»** group you choose, only once:

- **«Point layer:»**: a vector point layer of the project
- **«Value field (numeric):»**: the field to analyse (the drop-down lists numeric fields only)

Below them a summary shows the valid points out of the total, the CRS and the layer extent, for example «500 valid points of 500 · CRS EPSG:32633 · …». Points without a value (NULL or non-numeric text) are not counted as valid. The summary also warns when the project has no point layers, when the layer has no numeric fields or when the CRS is geographic (degrees).

When you change layer, the panel also proposes the maximum distance of the variogram and the kriging cell size, and preselects the layer in the Patterns (ML) tab if nothing is selected there yet.

### The Six Tabs

| Tab | Function | Result |
|-----|----------|--------|
| **Data** | Descriptive statistics of the field | Statistics table, histogram with box plot |
| **Variogram** | Spatial structure of the values | Nugget, sill, range, anisotropy, chart |
| **Kriging** | Interpolation on a regular grid | Estimate and uncertainty rasters, cross-validation |
| **Patterns (ML)** | Groups and anomalies with machine learning | Point layer with the group label |
| **Sampling** | Proposal of new points to sample | Point layer and coordinate table |
| **Report** | Collection of the session's analyses | HTML file with interactive charts, or PDF |

<!-- IMAGE: Header, Input data group and the six GeoArchaeo tabs -->
> **Fig. 3**: The header, the «Input data» group and the six tabs of the GeoArchaeo panel

### Results and Charts

Each tab shows its results in a **box** below the computation button, which stays visible until you run the analysis again, and the **chart** in the panel:

- if QGIS has QtWebEngine, the Plotly chart is interactive right in the panel (zoom, values on mouse hover)
- otherwise a **static preview** appears with the note «Static preview (QtWebEngine not available in this QGIS installation).»
- in both cases the **«Open interactive chart in browser»** button opens the interactive version in the web browser

The Data, Variogram and Kriging tabs end with a link to the next step, for example **«Next step: Variogram →»**.

### Running Analyses

Variogram, kriging, pattern recognition and sampling are computed in a **separate thread**: QGIS remains usable, and the **progress bar** (as a percentage for kriging) and the **«Cancel»** button appear at the bottom of the panel. One analysis runs at a time: starting another one shows «An analysis is already running: wait for it to finish or cancel it.»

---

## Data Tab

The **Data** tab («1. Exploratory analysis») describes the distribution of the values before interpolating them.

### Computing the Statistics

1. In the «Input data» group, choose the point layer and the numeric field
2. Open the **Data** tab
3. Click **«Calculate statistics»**

<!-- IMAGE: Data tab with statistics and histogram -->
> **Fig. 4**: The Data tab with the statistics table and the histogram of the chosen field

### Statistics and Interpretation

| Statistic | Description |
|-----------|-------------|
| **Number of values**, **Missing values** | Points with a valid value and excluded points (NULL or non-numeric text) |
| **Minimum**, **Maximum**, **Mean**, **Median** | Range and location of the values |
| **Std. deviation**, **Coeff. of variation** | Absolute and relative spread |
| **First quartile (Q1)**, **Third quartile (Q3)** | Limits of the central 50% of the values |
| **Skewness**, **Kurtosis** | Shape of the distribution |

Below the table the panel adds a reading in words:

- skewness above 1: right-skewed distribution (few very high values); consider a log transform before kriging, for example by creating a new field with the Field Calculator
- skewness below -1: left-skewed distribution (few very low values)
- otherwise: roughly symmetric distribution, suitable for kriging
- the number of possible outliers, i.e. beyond 3 standard deviations from the mean

The chart shows the **histogram** of the values with a **box plot** (only the histogram in the static preview).

### Example Data

The **«Load example data»** button opens the «GeoArchaeo example data» window with the datasets in the module's `test_layers` folder; the path is shown in **«Folder:»** and can be changed with **«Browse…»**. GeoPackages and GeoJSON files are already ticked. CSV files are listed only when no GeoPackage or GeoJSON with the same name exists; they must be ticked by hand and are loaded as delimited text (`x` and `y` fields, EPSG:32633). With **OK** the layers are added to the project and the first point layer loaded becomes the panel's input layer.

| Dataset | Points | Main numeric fields | Suggested use |
|---------|--------|---------------------|---------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Statistics, variogram, kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Same as `villa_ceramica` | Trying out all tabs |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, test on a large dataset |
| `necropoli` (GeoPackage) | 120 tombs | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN or K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging of soil properties |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Density kriging, sampling |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variogram and kriging with few points |
| `area_studio` (GeoJSON) | 1 polygon | — | Study area for sampling |

Among the CSV files, `magnetometria_grid` (2500 points, field `mag_nT`) contains simulated magnetic anomalies (two walls, a pit, a kiln). All data are simulated and in EPSG:32633 (UTM 33N, metres). The `area_studio` polygon covers the area of `ricognizione_survey`, `unita_scavo_ceramica` and `magnetometria_grid`, not that of the other datasets.

### Data Requirements

- The layer must be a vector **point** layer (for multipoints the first point is used)
- The field must be **numeric**: a text field containing numbers must be converted with the Field Calculator
- NULL or non-numeric values are excluded automatically and counted as missing
- At least **5 points** with a valid value are needed for variogram and kriging (1 for statistics); a reliable variogram usually needs a few dozen points
- A **projected CRS** in metres (for example UTM) is recommended: with a geographic CRS the summary warns you and variogram and kriging ask for confirmation

---

## Variogram Tab

The **Variogram** tab («2. Variogram») measures how the difference between values grows with distance: it describes the spatial structure of the data and drives the kriging.

### What is a Variogram?

The variogram relates the **semivariance** of point pairs to the **distance** separating them. The model parameters are:

| Parameter | Description |
|-----------|-------------|
| **Nugget** | Variability at almost zero distance: measurement error and small-scale variability |
| **Sill** | Total variance reached by the model (the "plateau") |
| **Range** | Distance beyond which values are no longer correlated; in GeoArchaeo it is the practical range (95% of the sill) |

### Computing the Variogram

1. Open the **Variogram** tab
2. In the **«Parameters»** group check **«Maximum distance:»**: the **«Auto»** button proposes about 1/3 of the diagonal of the area covered by the points (the same value is proposed when you change layer)
3. Choose the **«Theoretical model:»**
4. If needed, tick **«Check anisotropy (directional variograms)»**
5. Click **«Calculate variogram»**

Point pairs are grouped into **15 distance classes** (lags) between zero and the maximum distance; the number of classes cannot be changed from the panel. Above **3000 points** the variogram is computed on a random subsample of 3000 points, because the number of pairs grows with the square of the points. The model is fitted by least squares weighted by the number of pairs in each class.

<!-- IMAGE: Variogram tab with parameters and results -->
> **Fig. 5**: The Variogram tab with the parameters, the theoretical model and the results box

### Theoretical Models

| Model | Behaviour | When to use it |
|-------|-----------|----------------|
| **«Spherical (recommended)»** | Rises up to the range, then stays constant | The most common: artefact densities, distributions with sharp limits |
| **«Exponential»** | Rises quickly near the origin and reaches the sill gradually | Continuously decaying phenomena, for example chemical elements in the soil |
| **«Gaussian»** | Very smooth near the origin | Very "smooth" phenomena (surfaces); use with caution |
| **«Matérn»** | Between exponential and Gaussian (ν = 1.5) | Flexible alternative |

Rule of thumb: start with the spherical model and compare its fit RMSE with that of the other models. Kriging uses the **last** variogram calculated: after comparing, recalculate the one you chose.

### Manual Parameters

The **«Manual parameters (optional)»** group, off by default, lets you fix **«Nugget:»**, **«Sill (total variance):»** and **«Range (correlation distance):»**. With the group enabled, non-zero values are kept fixed and those left on «Auto» (zero) are estimated.

### Reading the Results

The results box reports:

- the model with **Nugget**, **Sill**, **Range** (in CRS units) and the fit **RMSE**
- the number of point pairs and distance classes, with the subsample used, if any
- a reading of the range: values are spatially correlated up to that distance and do not influence each other beyond it
- the nugget/sill ratio: below 25% strong small-scale continuity, up to 60% moderate continuity, above 60% high small-scale variability or measurement error (kriging will be weakly informative)

The chart shows the points of the experimental variogram (larger where there are more pairs), the model curve and the nugget, sill and range lines.

<!-- IMAGE: Experimental variogram with the fitted model -->
> **Fig. 6**: Experimental variogram and spherical model with the nugget, sill and range lines

### Directional Variograms (Anisotropy)

With **«Check anisotropy (directional variograms)»** ticked, GeoArchaeo also computes the variograms in the directions **0°, 45°, 90° and 135°** (angles measured from East, counter-clockwise, tolerance ±22.5°). Nugget and sill are those of the overall variogram; the range is estimated for each direction.

- If the ratio between the largest and the smallest range exceeds **2**, the box reports the anisotropy and the major direction (for example along a wall, a road or a slope)
- Otherwise it reports «No relevant anisotropy» with the computed ratio
- With too few pairs per direction it shows «Not enough pairs for directional variograms.»

In the interactive chart the directional variograms are legend entries hidden at first: click 0°, 45°, 90° or 135° to show them (in the static preview they are always drawn). The panel's kriging uses the omnidirectional model: anisotropy is there for interpretation.

---

## Kriging Tab

The **Kriging** tab («3. Ordinary kriging») interpolates the values on a regular grid using the variogram, also produces the uncertainty map and adds the rasters to the project.

### Ordinary Kriging

The panel runs **ordinary kriging** (constant but unknown local mean), suitable for most archaeological data. For each cell it uses the **20 nearest points**, found with a KD-tree; this number cannot be changed from the panel. Co-kriging, spatio-temporal kriging and tiled kriging for very large datasets exist only as Processing algorithms of the standalone GeoArchaeo plugin and are not available in PyArchInit.

### Running Kriging

1. Open the **Kriging** tab and read the variogram status line (see below); the **«← Go to Variogram»** button takes you back to the previous tab
2. Set **«Cell size:»**, the size of a cell in CRS units: the panel proposes about 100 cells on the longer side of the layer and shows the resulting grid below («Grid: … × … = … cells»)
3. Leave **«Use the calculated variogram»** ticked to use the variogram of the previous tab; when it is off, the variogram is estimated automatically
4. Leave **«Also create the uncertainty raster (std. deviation)»** ticked if you need the uncertainty map
5. Click **«Run kriging»**: the progress bar shows the percentage and **«Cancel»** stops the computation

The status line can read:

- «Variogram available: …, range … ✓»: the variogram calculated on the same layer and field is used
- «No variogram calculated: it will be estimated automatically (spherical model).»
- «The variogram was calculated on another layer/field: it will be recalculated.» (again with an automatic estimate)

> **Grid**: the grid covers the extent of the point layer and is limited to **500 cells per side**. If the chosen cell size is too fine, it is increased automatically and the grid line says so («minimum cell size … (max 500 cells per side)»). Above **40,000 cells** the line turns orange and, when you start, the panel asks for confirmation because the computation may take a few minutes.

<!-- IMAGE: Kriging rasters and cross-validation metrics -->
> **Fig. 7**: The estimate and uncertainty rasters on the map, with the results box and the cross-validation

### Kriging Results

Kriging adds two GeoTIFF rasters to the project, in the CRS of the point layer:

| Layer | Content | Style |
|-------|---------|-------|
| `Kriging_<field>` | Estimated value of each cell | Colour ramp from blue to red through yellow; visible |
| `Kriging_<field>_uncertainty` | Standard deviation of the estimate (uncertainty) | Ramp from light yellow to red; added at the top of the layer list but hidden |

With the panel in Italian the second raster is called `Kriging_<field>_incertezza`. The files are written to a **temporary folder**: to keep them, export them from the layer context menu (**Export**).

The results box summarises the points used, the grid size, the cell size, the model and the range; the chart shows the map of the estimated values and the uncertainty map, with the sample points on top.

### Leave-one-out Cross-validation

After kriging, GeoArchaeo runs a **leave-one-out cross-validation**: each point is removed and re-estimated from the others (on at most 200 randomly chosen points for larger datasets). The metrics appear in the results box:

| Metric | Meaning | Desirable value |
|--------|---------|-----------------|
| **RMSE** (root mean squared error) | Typical estimation error | As low as possible, compared with the standard deviation of the data |
| **MAE** (mean absolute error) | Mean error in absolute value | As low as possible |
| **ME** (mean error, bias) | Systematic over- or underestimation | Close to 0 |
| **R²** (explained variance) | Predictive skill | 0.5 or more good, below 0.2 low |
| **MSDR** (standardized error) | How realistic the estimated uncertainty is | About 1; above 1.5 uncertainty underestimated, below 0.5 overestimated |

The panel adds a verdict in words on the predictive skill (good, moderate or low) and, when relevant, on the MSDR.

> **Note**: kriging runs in a **background thread**, so the QGIS interface remains usable during the computation; the progress bar shows the processing status.

---

## Patterns (ML) Tab

The **Patterns (ML)** tab («4. Pattern recognition (machine learning)») groups the points by position and numeric attributes, or detects anomalies, and creates a layer with each point's label.

### Available Methods

| Method (drop-down entry) | What it does | Parameters |
|--------------------------|--------------|------------|
| **«K-Means – groups by similarity»** | Splits the points into K groups similar in position and attributes | **«Number of groups (0 = automatic):»**; with 0 the number is chosen from the number of points (from 2 to 5) |
| **«DBSCAN – groups by density (also finds isolated points)»** | Finds density groups without fixing their number; isolated points form the «Isolated / noise» group | Automatic |
| **«Isolation Forest – anomaly detection»** | Flags as «Anomaly» about 10% of the points that differ most from the others; the rest are «Normal» | Automatic |

### Running the Analysis

1. Open the **Patterns (ML)** tab
2. In the **«Point layers to analyse (one or more):»** list select one or more point layers (if nothing is selected, the input layer is preselected)
3. Choose the **«Method:»**
4. For K-Means only, set **«Number of groups (0 = automatic):»**
5. Click **«Run pattern recognition»**

The variables analysed are the **X and Y coordinates** and **all the numeric fields** of the selected layers, standardised; missing values are replaced with the field mean. Not only the value field chosen at the top is used: every numeric field goes in, including identifiers and running numbers, and if they distort the groups it is better to analyse a copy of the layer with the useful fields only. When analysing several layers together, they should have the same numeric fields in the same order and the same CRS (the new layer uses the CRS of the first selected layer).

<!-- IMAGE: Patterns (ML) tab with the groups layer -->
> **Fig. 8**: The Patterns (ML) tab with the groups chart and the `ML_groups` layer on the map

### Results

- The results box reports the method, the number of groups and how many points fall in each (for example «Group A (n=42)»)
- The chart shows the points on the plane of the first two principal components (PC1, PC2) of the variables, coloured by group
- A temporary point layer is created, `ML_groups` (K-Means, DBSCAN) or `ML_anomalies` (Isolation Forest), with a categorised legend: grey for isolated points, red and larger for anomalies; with the panel in Italian the names are `Gruppi_ML` and `Anomalie_ML`

| Field | Content |
|-------|---------|
| `cluster_id` | Group number (-1 = isolated with DBSCAN; 1 = anomaly and 0 = normal with Isolation Forest) |
| `cluster_name` | Readable name, for example «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Number of points in the group |
| `method` | Method used |
| `x_coord`, `y_coord` | Point coordinates |

### Supervised Classification

Below the method, the panel recalls that supervised classification (Random Forest with a label field) is found in **Processing → GeoArchaeo**. That algorithm belongs to the standalone GeoArchaeo plugin: in PyArchInit the GeoArchaeo Processing provider is not registered, so Random Forest is not available. To use it you need the separate GeoArchaeo plugin.

---

## Sampling Tab

The **Sampling** tab («5. New sampling locations») suggests where to sample or excavate next, starting from the existing points, and creates a layer with the proposed points.

### Sampling Criteria

| Criterion (drop-down entry) | How it chooses the points | When to use it |
|-----------------------------|---------------------------|----------------|
| **«Coverage (maximin)»** | Each new point is as far as possible from all the others | Filling gaps uniformly |
| **«Uncertainty reduction (kriging variance)»** | Each new point goes where the kriging variance is highest | Reducing the kriging error where it is highest |
| **«Stratified grid»** | One location per cell of a regular grid, with a slight random jitter | Regular coverage of a defined area |
| **«Adaptive (sparser areas)»** | Random draw with higher probability where there are few points | Favouring the least sampled zones while keeping a random component |

The «Uncertainty reduction» criterion uses the calculated variogram if it refers to the same layer and field and «Use the calculated variogram» is ticked in the Kriging tab; otherwise it uses a generic model based on the typical distance between points.

### Designing a Sampling Plan

1. Check **«Existing points:»**: it is the layer chosen at the top in the «Input data» group (the numeric field is not needed for sampling)
2. Optional: choose a polygon layer in **«Study area (polygon, optional):»**; all its polygons are merged and reprojected to the CRS of the points, even if the layer is in another CRS
3. Set **«New points to propose:»** (from 1 to 500, default 10)
4. Choose the **«Criterion:»**: its description appears below the drop-down
5. Click **«Calculate new points»**

Without a study area, points are searched for in the rectangle containing the existing points, enlarged by 20% on each side.

<!-- IMAGE: Proposed new sampling points -->
> **Fig. 9**: The new sampling points (yellow stars) proposed inside the study area

### Sampling Results

- The results box states how many points were proposed and with which criterion; below it, the «Coordinates of the proposed points:» table lists number, X and Y
- A temporary point layer `New_sampling_points` is created (`Nuovi_punti_campionamento` with the panel in Italian), with a yellow star symbol and the fields `point_id`, `x_coord`, `y_coord` and `type` (value `suggested`)

---

## Report Tab

The **Report** tab («6. Report») collects the analyses run in this session into a single document: statistics, interactive charts, parameters and validation.

### Report Contents

In the **«Sections to include»** group each section is marked «available» or «not yet calculated»; sections not yet calculated cannot be selected.

| Section | Content |
|---------|---------|
| **Descriptive statistics** | Layer and field, statistics table with the reading in words, histogram |
| **Variogram** | Model, nugget, sill, range, RMSE, maximum distance, interpretation, chart |
| **Kriging and cross-validation** | Method, cell size, grid size, cross-validation metrics, chart |
| **Pattern recognition** | Layers analysed, groups with their number of points, chart |
| **New sampling locations** | Criterion, layer, coordinate table |

Each section contains the **last** analysis of its kind run in the session.

### Generating a Report

1. Run the analyses you need in the other tabs
2. Open the **Report** tab and leave ticked the sections to include (they are ticked by default)
3. Click **«Save HTML report»** or **«Save PDF report»** and choose the file name

When saving, the panel also shows a preview of the report without charts; the note «Preview: the interactive charts are included in the saved HTML file.» reminds you where they are.

<!-- IMAGE: GeoArchaeo HTML report opened in the browser -->
> **Fig. 10**: A GeoArchaeo HTML report with interactive charts, opened in the browser

### Export

| Format | Content | Notes |
|--------|---------|-------|
| **HTML** (`geoarchaeo_report.html`) | Text, tables and **interactive charts** | The file is self-contained (the chart library is embedded, it also works offline) and opens straight away in the browser |
| **PDF** (`geoarchaeo_report.pdf`) | Text and tables, **without charts** | If the PDF cannot be created, save the HTML report and print it to PDF from the browser |

If no analysis has been run, «No analysis available: run at least one analysis first.» appears; if no section is ticked, «Select at least one section».

---

## Operational Workflow

A complete example with the example data shipped with the module.

### Step 1: Data Preparation

1. Open GeoArchaeo from the PyArchInit toolbar
2. Click **«Load example data»** and confirm with **OK** (GeoPackages and GeoJSON files are loaded)
3. In the «Input data» group choose the `villa_ceramica` layer and the `ceramic_count` field
4. Check the summary: 500 valid points of 500, CRS EPSG:32633

### Step 2: Data Exploration

1. **Data** tab → **«Calculate statistics»**
2. Read skewness and outliers; with strong right skewness consider a log transform

### Step 3: Variogram Analysis

1. **Variogram** tab → **«Auto»** for the maximum distance, **«Spherical (recommended)»** model → **«Calculate variogram»**
2. Repeat with **«Exponential»** and compare the fit RMSE
3. Optional: recalculate with **«Check anisotropy (directional variograms)»**
4. Recalculate the chosen model last and note nugget, sill and range

### Step 4: Interpolation

1. **Kriging** tab: check the «Variogram available … ✓» line
2. Keep the proposed cell size or set 1 (metre)
3. **«Run kriging»**
4. Examine the `Kriging_ceramic_count` and `Kriging_ceramic_count_uncertainty` rasters and the R² and MSDR values

### Step 5: Patterns and Sampling (optional)

1. **Patterns (ML)** tab: in the list keep only `necropoli` selected, DBSCAN method → **«Run pattern recognition»**; the `ML_groups` layer shows the groups of tombs and the isolated points
2. At the top choose the `ricognizione_survey` layer (field `densita_mq`); **Sampling** tab: study area `area_studio`, 10 points, criterion «Coverage (maximin)» → **«Calculate new points»**

### Step 6: Report

1. **Report** tab: leave the available sections ticked
2. **«Save HTML report»**: the report opens in the browser with the interactive charts
3. Export the rasters and temporary layers you want to keep

---

## Troubleshooting

### Common Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| «No point layer in the project: load one or use the example data.» | The project has no point layers | Add a point layer or use **«Load example data»** |
| «The layer has no numeric fields…» | The field to analyse is a text field | Convert it to a number with the Field Calculator |
| «At least 5 points with a valid value are required (found …)» | Too many NULL or non-numeric values | Check the attribute table or choose another field |
| «geographic CRS (degrees)» warning | The layer is not in a projected CRS | Reproject the layer, for example to UTM, and repeat the analysis |
| «No point pairs within the maximum distance…» error | Variogram maximum distance too small | Increase **«Maximum distance:»** or use **«Auto»** |
| «Not enough pairs for directional variograms.» | Too few pairs per direction | Increase the maximum distance or skip the anisotropy check |
| Slow kriging, confirmation request or «Out of memory: increase the cell size.» | Grid with too many cells | Increase **«Cell size:»** |
| Low R² in the cross-validation | Little spatial correlation or too much noise | Treat the map as indicative only and look at the uncertainty raster |
| DBSCAN puts almost all points in «Isolated / noise» | Uniform density or too many variables | Try K-Means or reduce the numeric fields |
| «Machine Learning features not available. Please install scikit-learn.» | scikit-learn is missing | Install scikit-learn in the QGIS Python environment |
| «Plotly visualization not available. Please install plotly.» | Plotly is missing | Install plotly in the QGIS Python environment |
| Chart only as a static image | QtWebEngine not available | Use **«Open interactive chart in browser»** |
| «Cannot create the PDF…» | PDF printing error | Save the HTML report and print it from the browser |
| Panel not visible | Panel closed | Reopen it from the toolbar or the pyArchInit menu: the session's results are still there |

### Frequent Errors

- **«An analysis is already running: wait for it to finish or cancel it.»**: wait for the computation to end or press «Cancel»
- **«Analysis cancelled»**: the analysis was stopped with «Cancel» and produced no results
- **«Select at least one layer»** (Patterns tab): select at least one layer in the list
- **«Select the existing points layer (above)»** (Sampling tab): choose the layer in the «Input data» group
- **«Select a point layer and a numeric field (at the top of the panel)»**: complete the choice in the «Input data» group

### Performance

- Analyses run in a **background thread**: QGIS stays usable and the computation can be cancelled
- The variogram uses at most 3000 points (random subsample), the cross-validation at most 200
- Kriging uses the 20 points nearest to each cell: the time depends mainly on the number of cells
- The grid is limited to 500 × 500 cells; above 40,000 cells the panel asks for confirmation
- With large datasets (for example the 4800 points of `geofisica_survey`) increase the cell size

---

## Technical Notes

### Version and Origin

- The `modules/geoarchaeo/` module is aligned with **GeoArchaeo 1.3.1**, the standalone plugin by Enzo Cocca (github.com/enzococca/GeoArchaeo)
- Only the panel is integrated in PyArchInit: the GeoArchaeo Processing provider (co-kriging, spatio-temporal kriging, tiled kriging, compositional analysis, Random Forest) is **not** registered
- The module is compatible with QGIS 3 (Qt5) and QGIS 4 (Qt6)

### Dependencies

| Library | Usage |
|---------|-------|
| **NumPy** | Numerical computation |
| **SciPy** | Variogram model fitting, neighbour search (KD-tree), statistics |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, principal components (required by the Patterns tab) |
| **Plotly** | Interactive charts in the panel and in the HTML report |
| **Matplotlib** | Static chart previews when QtWebEngine is not available |
| **QtWebEngine** (optional) | Interactive charts directly in the panel |
| **threadpoolctl** (optional) | Limits computation threads during background analyses |
| **GDAL** | Writing the GeoTIFF rasters (included in QGIS) |

### Coordinate Reference Systems

- Distances (maximum distance, range, cell size) are expressed in the **units of the point layer's CRS**
- Use a **projected CRS** in metres: with a geographic CRS the summary warns you and variogram and kriging ask for confirmation
- Kriging rasters and created layers use the CRS of the point layer (in the Patterns tab, that of the first selected layer)
- The study area is reprojected automatically to the CRS of the points

### Output Layers and Files

| Output | Type | Location |
|--------|------|----------|
| `Kriging_<field>`, `Kriging_<field>_uncertainty` | GeoTIFF raster (LZW compression) | System temporary folder |
| `ML_groups` / `ML_anomalies` | Temporary (memory) point layer | Only in the open project |
| `New_sampling_points` | Temporary (memory) point layer | Only in the open project |
| Report | HTML or PDF | Path chosen when saving |

Rasters and temporary layers must be exported (layer context menu → **Export**) so they are not lost when the project is closed. Layer names follow the panel language at the time of the computation.

### Settings

- The panel language is stored in the QGIS settings (key `GeoArchaeo/language`)
- Results stay in memory while QGIS is open: closing the panel does not delete them

---

> **Note**: GeoArchaeo is under continuous development. To report bugs or suggest improvements, use the issue tracking system of the PyArchInit project on GitHub.
