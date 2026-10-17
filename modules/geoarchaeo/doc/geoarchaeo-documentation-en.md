# GeoArchaeo Plugin - Complete Documentation
## Advanced Geostatistical Analysis System for Archaeology

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation and Configuration](#2-installation-and-configuration)
3. [Data Preparation and Structure](#3-data-preparation-and-structure)
4. [Interface and Components](#4-interface-and-components)
5. [Archaeological Use Cases](#5-archaeological-use-cases)
6. [Step-by-Step Tutorial](#6-step-by-step-tutorial)
7. [Algorithms and Parameters](#7-algorithms-and-parameters)
8. [Troubleshooting and FAQ](#8-troubleshooting-and-faq)
9. [Best Practices](#9-best-practices)
10. [Examples and Datasets](#10-examples-and-datasets)

---

## 1. Introduction

### 1.1 What is GeoArchaeo?

GeoArchaeo is a professional QGIS plugin for advanced geostatistical analysis in archaeology. It integrates kriging techniques, machine learning, and compositional analysis for:

- **Spatial interpolation** of archaeological data
- **Multi-sensor fusion** of geophysical surveys
- **Automatic pattern recognition** of buried structures
- **Optimization** of excavation strategies

### 1.2 Target Audience

- **Archaeologists** with spatial research projects
- **Geoarchaeologists** for sedimentological analysis
- **Excavation directors** for optimal planning
- **Researchers** in computational archaeology
- **Heritage management** authorities

### 1.3 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| QGIS | 3.16 | 3.28+ / 4.x |
| Python | 3.7 | 3.9+ |
| RAM | 8 GB | 16 GB |
| Disk Space | 500 MB | 2 GB |
| OS | Windows 10, Ubuntu 20.04, macOS 10.14 | Latest OS |

---

## 2. Installation and Configuration

### 2.1 Installing Dependencies

#### Windows
```bash
# Open OSGeo4W Shell as administrator
python -m pip install --upgrade pip
pip install numpy scipy pandas scikit-learn plotly
```

#### Linux/Ubuntu
```bash
# Install Python dependencies
pip3 install numpy scipy pandas scikit-learn plotly
```

#### macOS
```bash
pip3 install numpy scipy pandas scikit-learn plotly
```

### 2.2 Plugin Installation

#### Method 1: From ZIP
1. Download `geoarchaeo.zip` from the repository
2. In QGIS: **Plugins → Manage and Install Plugins → Install from ZIP**
3. Select the ZIP file
4. Restart QGIS

#### Method 2: Manual
```bash
# Linux/Mac
cd ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
git clone https://github.com/enzococca/geoarchaeo

# Windows
cd %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
git clone https://github.com/enzococca/geoarchaeo
```

### 2.3 First Configuration

1. **Activate the plugin**: Plugins → Manage → ✓ GeoArchaeo
2. **Verify installation**: toolbar and dock should appear
3. **Quick test**:
   - Load sample data
   - Click on GeoArchaeo icon
   - If the panel opens, installation is OK

---

## 3. Data Preparation and Structure

### 3.1 Supported Data Formats

| Data Type | Formats | Notes |
|-----------|---------|-------|
| Point vectors | SHP, GPKG, CSV, GeoJSON | Projected coordinates (not lat/lon) |
| Polygon vectors | SHP, GPKG | For boundaries and excavation areas |
| Raster | GeoTIFF | Output only (prediction and uncertainty): not an input format, convert DEMs and gridded geophysics to points first |
| Database | SpatiaLite, PostGIS | For large projects |
| Tabular | CSV, XLSX | With X, Y columns: load them as a point layer |

### 3.2 Archaeological Data Structure

#### 3.2.1 Artifact Table (minimum)
```csv
id,x,y,type,material,period,quantity,weight_g,su
1,345678.5,4567890.2,ceramic,terracotta,roman,5,120.5,101
2,345679.1,4567891.7,metal,bronze,roman,1,45.2,101
3,345680.3,4567889.5,ceramic,sigillata,roman,3,67.8,102
```

**Required fields:**
- `x`, `y`: coordinates in projected system
- A numeric value field for interpolation

**Recommended fields:**
- `id`: unique identifier
- `type`: artifact classification
- `su`: stratigraphic unit
- `period`: chronological phase
- `quantity`: for density analysis

#### 3.2.2 Geophysical Survey Table
```csv
id,x,y,gpr_amplitude,mag_nt,res_ohm,depth_m,line_id
1,345670.0,4567880.0,125.3,48950.2,35.6,0.5,L001
2,345670.5,4567880.0,118.7,48948.5,34.2,0.5,L001
3,345671.0,4567880.0,132.1,48952.1,38.9,0.5,L001
```

**Best practices:**
- Regular grid for geophysics (0.5m or 1m)
- Normalize measurement units
- Include `line_id` for line-by-line processing

#### 3.2.3 Geoarchaeological Sample Table
```csv
sample_id,x,y,depth_cm,ph,p_ppm,organic_percent,sand,silt,clay
GA001,345675.5,4567885.3,20,7.2,125,3.5,45,35,20
GA002,345680.5,4567885.3,20,7.5,189,4.2,40,38,22
GA003,345685.5,4567885.3,20,7.1,156,3.8,42,36,22
```

**Compositional notes:**
- `sand + silt + clay = 100%` (compositional data)
- Requires CLR/ILR transformation before kriging

### 3.3 Coordinate Systems

**IMPORTANT**:
- **NEVER** use WGS84 lat/lon (EPSG:4326) for spatial analysis
- Always use **projected** coordinates in meters
- Verify units: `Project → Properties → General → Units`

---

## 4. Interface and Components

### 4.1 Main Dock Widget

**Header (always visible)**: choose the point layer and the numeric field once; every tab uses this selection.
A summary line shows valid points, CRS and extent, and warns when the CRS is geographic (degrees).
The header also holds *Load example data*, *Tutorial* and the language selector (IT/EN, remembered).
Each tab has an info box, the parameters, a persistent **results** box and the **chart** (interactive Plotly
when QtWebEngine is available, otherwise a static preview with an "open in browser" button).
A progress bar with a *Cancel* button sits at the bottom of the panel.

1. **Data**: descriptive statistics (n, missing, min/max, mean, median, std, CV, quartiles, skewness, kurtosis),
   interpretation notes and histogram.
2. **Variogram**: maximum distance (*Auto* = 1/3 of the area diagonal), model (spherical, exponential, Gaussian,
   Matérn), optional manual nugget/sill/range, anisotropy check (directional variograms at 0°, 45°, 90°, 135°).
3. **Kriging**: variogram status, cell size with grid preview (max 500 cells per side), prediction and uncertainty
   rasters, leave-one-out cross-validation (RMSE, MAE, ME, R², MSDR). Co-kriging, spatio-temporal and batch
   kriging live in the Processing Toolbox.
4. **Patterns (ML)**: one or more point layers, K-Means (chosen or automatic number of groups), DBSCAN,
   Isolation Forest; output point layer with labels. Supervised Random Forest is in Processing.
5. **Sampling**: new sampling locations from the selected layer, optional study-area polygon (reprojected
   automatically); criteria: maximin coverage, kriging-variance reduction, stratified grid, adaptive.
6. **Report**: sections flagged *available / not yet calculated*, HTML export with interactive charts, PDF export.

### 4.2 Toolbar Actions

- **GeoArchaeo Panel**: show/hide the dock
- **Help**: open the HTML help
- **Load example data**: open the example-data dialog (plugin `test_layers` folder)
- **Variogram / Kriging / Pattern recognition**: jump to the corresponding tab
- **Report**: save the HTML report

---

## 5. Archaeological Use Cases

### 5.1 Ceramic Density Analysis
Identify functional areas (kitchens, storage) based on fragment distribution.

### 5.2 Geophysical Data Fusion
Combine GPR + Magnetometry for buried structure identification using Co-Kriging.

### 5.3 Compositional Analysis
CLR/ILR transformations for granulometric and chemical soil data.

### 5.4 Excavation Optimization
Calculate optimal positions for new trenches minimizing prediction uncertainty.

---

## 6. Step-by-Step Tutorial

### 6.1 Basic Workflow

1. **Load your point layer** (CSV, SHP, or GeoJSON)
2. **Select the layer** at the top of the panel (used by all tabs)
3. **Choose the numeric field** to analyze
4. **Calculate statistics** to understand your data distribution
5. **Calculate variogram** to understand spatial correlation
6. **Run kriging** to create interpolated surface
7. **Validate results** using cross-validation metrics
8. **Save** the rasters (GeoTIFF files in a temporary folder: use Export → Save As in QGIS) or generate the report

### 6.2 Variogram Analysis

The variogram measures how spatial correlation varies with distance:

- **Nugget**: Microscale variation + measurement error
- **Sill**: Total variance at which correlation plateaus
- **Range**: Distance at which observations become uncorrelated

### 6.3 Kriging Interpolation

Available methods:
- **Ordinary Kriging** (Kriging tab and Processing): Standard method, assumes stationary mean
- **Co-Kriging** (Processing only): Simplified, regression on secondary variables + kriging of the residuals
- **Spatio-Temporal** (Processing only): Includes time dimension for phased excavations
- **Batch Kriging** (Processing only): Tiled ordinary kriging for large datasets

---

## 7. Algorithms and Parameters

### 7.1 Variogram Models

| Model | Equation | Best For |
|-------|----------|----------|
| Spherical | γ(h) = c₀ + c[1.5(h/a) - 0.5(h/a)³] | Most archaeological data |
| Exponential | γ(h) = c₀ + c[1 - exp(-3h/a)] | Gradual transitions |
| Gaussian | γ(h) = c₀ + c[1 - exp(-3(h/a)²)] | Smooth surfaces |
| Matérn (ν = 1.5) | γ(h) = c₀ + c[1 - (1 + t)·exp(-t)], t = 4.744·h/a | Between exponential and Gaussian |

### 7.2 Machine Learning Methods

- **K-Means**: Unsupervised clustering for pattern groups
- **DBSCAN**: Density-based clustering for irregular shapes
- **Random Forest**: Supervised classification with training data
- **Isolation Forest**: Anomaly detection for unusual features

### 7.3 Sampling Design Methods

- **Maximin**: Maximize minimum distance from existing points
- **Variance Reduction**: Minimize predicted kriging variance
- **Stratified**: Regular grid with random perturbation
- **Adaptive**: Based on local density

---

## 8. Troubleshooting and FAQ

### 8.1 Common Issues

**Q: Plugin fails to load with import error**
A: Install missing dependencies using pip in QGIS Python environment.

**Q: Variogram shows no structure**
A: Check that your data has actual spatial correlation. Try increasing max distance.

**Q: Kriging leaves empty (NoData) cells**
A: In Batch Kriging a tile with fewer than 3 points (tile plus margin) is skipped and its cells stay empty: increase the tile size or the overlap.

**Q: Interactive plots don't show in QGIS**
A: QtWebEngine may not be available. The panel then shows a static preview and the "Open interactive chart in browser" button opens the Plotly version.

### 8.2 Performance Tips

- For datasets > 10,000 points, use Batch Kriging with tiling
- Reduce grid resolution for initial exploration

---

## 9. Best Practices

### 9.1 Data Quality
- Minimum 30 points for robust variogram
- Check for outliers before analysis
- Ensure consistent coordinate system

### 9.2 Variogram Fitting
- Start with automatic fitting
- Compare multiple models
- Validate with cross-validation RMSE

### 9.3 Kriging
- Match grid resolution to data density
- Use validation metrics to assess quality
- Consider anisotropy for directional patterns

---

## 10. Examples and Datasets

Test datasets are included in the `test_layers/` directory:
- `villa_ceramica.csv` / `.gpkg`: 500 ceramic density points
- `necropoli.csv` / `.gpkg`: 120 tombs with attributes
- `geofisica_survey.csv` / `.gpkg`: 4800 points of GPR + magnetometry

Load via: **Load example data** (toolbar button or panel header)

---

## License

GNU General Public License v3.0

## Author

Enzo Cocca - enzo.ccc@gmail.com

## Citation

```bibtex
@software{geoarchaeo2024,
  author = {Cocca, Enzo},
  title = {GeoArchaeo: Advanced Geostatistical Analysis for Archaeological Research},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/enzococca/geoarchaeo}
}
```
