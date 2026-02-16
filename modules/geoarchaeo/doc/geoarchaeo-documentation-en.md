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
- **Predictive analysis** for site location

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
pip install rasterio  # optional, for advanced GeoTIFF export
```

#### Linux/Ubuntu
```bash
# Install SpatiaLite
sudo apt-get update
sudo apt-get install libspatialite-dev spatialite-bin

# Install Python dependencies
pip3 install numpy scipy pandas scikit-learn plotly
```

#### macOS
```bash
# With Homebrew
brew install spatialite-tools
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
| Raster | GeoTIFF, ASC, IMG | DEM, gridded geophysics |
| Database | SpatiaLite, PostGIS | For large projects |
| Tabular | CSV, XLSX | With X, Y columns |

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

The plugin provides a dock widget with 6 tabs:

1. **Data Tab**: Layer and field selection, descriptive statistics
2. **Variogram Tab**: Variogram calculation and model fitting
3. **Kriging Tab**: Spatial interpolation with multiple methods
4. **ML Tab**: Machine Learning pattern recognition
5. **Sampling Tab**: Optimal sampling design
6. **Report Tab**: Report generation in HTML/PDF

### 4.2 Toolbar Actions

- **GeoArchaeo Panel**: Show/hide main dock
- **Quick Variogram**: Jump to variogram analysis
- **Quick Kriging**: Jump to kriging interpolation
- **Pattern Recognition**: Jump to ML analysis
- **Generate Report**: Create full analysis report
- **Load Test Layers**: Load sample data for testing

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
2. **Select the layer** in the Data tab
3. **Choose the numeric field** to analyze
4. **Calculate statistics** to understand your data distribution
5. **Calculate variogram** to understand spatial correlation
6. **Run kriging** to create interpolated surface
7. **Validate results** using cross-validation metrics
8. **Export** as GeoTIFF or generate report

### 6.2 Variogram Analysis

The variogram measures how spatial correlation varies with distance:

- **Nugget**: Microscale variation + measurement error
- **Sill**: Total variance at which correlation plateaus
- **Range**: Distance at which observations become uncorrelated

### 6.3 Kriging Interpolation

Available methods:
- **Ordinary Kriging**: Standard method, assumes stationary mean
- **Co-Kriging**: Uses secondary variables for improved estimates
- **Spatio-Temporal**: Includes time dimension for phased excavations

---

## 7. Algorithms and Parameters

### 7.1 Variogram Models

| Model | Equation | Best For |
|-------|----------|----------|
| Spherical | γ(h) = c₀ + c[1.5(h/a) - 0.5(h/a)³] | Most archaeological data |
| Exponential | γ(h) = c₀ + c[1 - exp(-3h/a)] | Gradual transitions |
| Gaussian | γ(h) = c₀ + c[1 - exp(-3(h/a)²)] | Smooth surfaces |
| Matérn | Complex | Flexible, general-purpose |

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

**Q: Kriging produces NaN values**
A: Ensure enough points near prediction locations. Increase search radius.

**Q: Interactive plots don't show in QGIS**
A: QtWebEngine may not be available. Plots will open in your browser instead.

### 8.2 Performance Tips

- For datasets > 10,000 points, use Batch Kriging with tiling
- Reduce grid resolution for initial exploration
- Use SpatiaLite for very large datasets

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
- `villa_ceramica.csv`: 500 ceramic density points
- `necropoli.csv`: 150 tombs with attributes
- `geofisica_grid.csv`: 0.5m GPR+MAG grid

Load via: **Toolbar → Load Test Layers**

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
