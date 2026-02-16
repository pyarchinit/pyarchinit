# PyArchInit - MoveCost - Least-Cost Path Analysis

## Index

1. [Introduction](#introduction)
2. [Accessing the Tool](#accessing-the-tool)
3. [Prerequisites](#prerequisites)
4. [User Interface](#user-interface)
5. [Algorithms Tab](#algorithms-tab)
6. [Results Tab](#results-tab)
7. [Export Tab](#export-tab)
8. [Settings Tab](#settings-tab)
9. [Operational Workflow](#operational-workflow)
10. [Troubleshooting](#troubleshooting)
11. [Technical Notes](#technical-notes)

---

## Introduction

**MoveCost** is a standalone PyArchInit tool for least-cost path analysis (LCPA) based on R scripts. Least-cost path analysis is a fundamental methodology in landscape archaeology that enables modelling the most probable routes between locations, taking into account terrain topography and the energetic cost of movement.

### History

Previously, the MoveCost functionality was embedded directly within the Site form of PyArchInit. Starting from the current version, MoveCost has been extracted as an **independent analysis tool**, accessible through a dedicated QDialog. This separation offers several advantages:

- **Dedicated interface**: A dialog with 4 tabs organized by function
- **Better organization**: Algorithms, results, export, and settings clearly separated
- **Quick access**: Available from the toolbar without opening the Site form
- **Extensibility**: Modular structure that facilitates adding new algorithms

### What is Least-Cost Path Analysis?

Least-cost path analysis calculates the optimal path between two or more points on a cost surface derived from a digital terrain model (DTM). The cost of movement depends on terrain slope and is calculated using anisotropic cost functions that account for the direction of movement (uphill vs downhill).

<!-- IMAGE: Example of least-cost path on DTM -->
> **Fig. 1**: Example of a least-cost path calculated on a digital terrain model

---

## Accessing the Tool

### From the Toolbar

1. Locate the **Analysis Tools** dropdown button in the PyArchInit toolbar -- it has a chart/analysis icon
2. Click the dropdown arrow
3. Select **MoveCost** from the menu

<!-- IMAGE: Analysis Tools button in toolbar -->
> **Fig. 2**: The Analysis Tools button in the PyArchInit toolbar with the dropdown menu open

### Dialog Window

On click, a **modal QDialog** opens with four tabs:

```
+-----------------------------------------------------------+
|  MoveCost - Least-Cost Path Analysis                       |
+-----------------------------------------------------------+
| [Algorithms] | [Results] | [Export] | [Settings]          |
+-----------------------------------------------------------+
|                                                           |
|              (Active tab content)                          |
|                                                           |
+-----------------------------------------------------------+
|                              [Close]                       |
+-----------------------------------------------------------+
```

---

## Prerequisites

Before using MoveCost, ensure the following components are installed and configured:

### 1. R (Statistical Language)

| Requirement | Detail |
|-------------|--------|
| **Software** | R (version >= 4.0 recommended) |
| **Download** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verification** | Open a terminal and type `R --version` |

### 2. R Package `movecost`

Install the package from within R:

```r
install.packages("movecost")
```

Main dependencies installed automatically: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Requirement | Detail |
|-------------|--------|
| **Plugin** | Processing R Provider |
| **Installation** | QGIS > Plugins > Manage and Install Plugins > Search "Processing R Provider" |
| **Configuration** | Processing Settings > Providers > R > R folder path |

### 4. Input Data

- **DTM/DEM**: A digital terrain model raster for the study area
- **Point layer**: Origin and destination points for the analysis
- **Polygon layer**: (Optional) For the "by polygon" algorithm variants

### Quick Prerequisites Checklist

```
+-------------------------------------------+
| Prerequisites Checklist                    |
+-------------------------------------------+
| [x] R installed and in PATH              |
| [x] movecost package installed in R      |
| [x] Processing R Provider active in QGIS |
| [x] DTM loaded in QGIS project           |
| [x] Point layer with origins/destinations |
+-------------------------------------------+
```

---

## User Interface

The MoveCost dialog is organized into **4 tabs**, each with a specific function.

### Tab Overview

| Tab | Icon | Function |
|-----|------|----------|
| **Algorithms** | Gear | Select and launch the 14 analysis algorithms |
| **Results** | Chart | View cost statistics and R plots |
| **Export** | Disk | Export results to CSV, PDF, or HTML |
| **Settings** | Wrench | Configure R scripts, language, layer organization |

<!-- IMAGE: MoveCost dialog overview with 4 tabs -->
> **Fig. 3**: The MoveCost dialog with all four tabs visible

---

## Algorithms Tab

The **Algorithms** tab is the core of the MoveCost tool. It contains **14 algorithms** based on R scripts, organized into **3 functional groups**.

### Group 1: Cost Surface & Paths

Algorithms for calculating accumulated cost surfaces and least-cost paths.

| Algorithm | Description |
|-----------|-------------|
| **movecost** | Calculate accumulated anisotropic slope-dependent cost of movement and least-cost paths from a point origin |
| **movecost by polygon** | Same but using a polygon area to define the DTM extent |
| **movebound** | Calculate slope-dependent walking cost boundaries around point locations |
| **movebound by polygon** | Same but using a polygon to define the extent |

### Group 2: Corridor & Network Analysis

Algorithms for cost corridor analysis and optimal path networks.

| Algorithm | Description |
|-----------|-------------|
| **movecorr** | Calculate least-cost corridor between point locations |
| **movecorr by polygon** | Same but using a polygon |
| **movealloc** | Calculate slope-dependent walking-cost allocation to origins |
| **movealloc by polygon** | Same but using a polygon |
| **movenetw** | Calculate least-cost path network between multiple points |
| **movenetw by polygon** | Same but using a polygon |

### Group 3: Comparison & Ranking

Algorithms for comparing cost functions and ranking destinations.

| Algorithm | Description |
|-----------|-------------|
| **movecomp** | Compare least-cost paths generated using different cost functions |
| **movecomp by polygon** | Same but using a polygon |
| **moverank** | Rank destinations by walking cost from an origin |
| **moverank by polygon** | Same but using a polygon |

### How to Launch an Algorithm

1. Select the desired algorithm from the list
2. The QGIS Processing interface opens with algorithm-specific parameters
3. Configure the input parameters:
   - **DTM/DEM**: Select the terrain raster
   - **Origin point(s)**: Select the point layer
   - **Polygon** (if "by polygon" variant): Select the study area
   - **Cost function**: Choose among available functions (Tobler, Minetti, etc.)
4. Click **Run**
5. Results are automatically added to the QGIS project

<!-- IMAGE: Algorithms tab with 3 groups -->
> **Fig. 4**: The Algorithms tab with the three algorithm groups highlighted

<!-- IMAGE: Processing interface for a movecost algorithm -->
> **Fig. 5**: The QGIS Processing interface for the movecost algorithm with parameters configured

### "By Polygon" Variants

The "by polygon" variants of each algorithm allow you to:
- **Limit the analysis area** to a specific region
- **Reduce computation time** by working on a clipped DTM
- **Focus the analysis** on an area of archaeological interest

---

## Results Tab

The **Results** tab allows you to view the results of executed analyses.

### Cost Summary

A text area (QTextEdit) displays summary statistics from generated cost layers:

| Statistic | Description |
|-----------|-------------|
| **Minimum** | Minimum cost value in the surface |
| **Maximum** | Maximum cost value in the surface |
| **Mean** | Average cost value |
| **Std. Deviation** | Standard deviation of cost values |

```
+---------------------------------------------------+
| Cost Summary                                       |
+---------------------------------------------------+
| Layer: movecost_accumulated_cost                   |
| Minimum: 0.00                                      |
| Maximum: 15234.56                                  |
| Mean: 4521.89                                      |
| Std. Deviation: 2103.45                            |
|                                                    |
| Layer: movecost_back_link                          |
| Minimum: 0.00                                      |
| Maximum: 8.00                                      |
| Mean: 4.12                                         |
+---------------------------------------------------+
```

### R Plot Viewer

The R Plot Viewer displays the latest plot generated by R scripts:

| Function | Description |
|----------|-------------|
| **Auto-display** | Shows the latest R plot from the temp directory |
| **Refresh** | Reloads the latest available plot |
| **Save** | Saves the current plot to an image file (PNG, JPG) |
| **Manual select** | Allows opening a specific R plot from any location |

<!-- IMAGE: Results tab with cost summary and R plot -->
> **Fig. 6**: The Results tab showing cost summary statistics and an R plot

### R Plot Locations

R plots are saved to QGIS/R temporary directories. The viewer automatically searches the following locations:

- QGIS Processing temporary directory
- R temporary directory (`tempdir()`)
- User-specified output folder

---

## Export Tab

The **Export** tab offers three options for exporting analysis results.

### Export Cost Table (CSV)

Exports cost layer statistics to a CSV file:

1. Click **Export Cost Table**
2. Select the file location and name
3. The CSV file contains: layer name, minimum, maximum, mean, standard deviation

| Column | Description |
|--------|-------------|
| `layer_name` | Name of the cost layer |
| `min_value` | Minimum value |
| `max_value` | Maximum value |
| `mean_value` | Mean value |
| `std_dev` | Standard deviation |

### Export Report (PDF)

> **Note**: This feature is currently under development (stub). It will be available in a future version.

### Export Report (HTML)

Generates a complete, styled HTML report that includes:

- **Header** with project title and date
- **Analysis parameters** used
- **Layer statistics** in tabular format
- **R plots** embedded as images
- **Integrated CSS styling** for professional presentation

1. Click **Export Report (HTML)**
2. Select the file location and name
3. The report opens automatically in the default browser

<!-- IMAGE: Example of exported HTML report -->
> **Fig. 7**: An example HTML report generated by MoveCost with statistics and plots

---

## Settings Tab

The **Settings** tab allows you to configure the MoveCost tool.

### Install R Scripts

| Function | Description |
|----------|-------------|
| **Install R Scripts** | Copies movecost R scripts to the QGIS processing directory |

This operation is required on **first setup** or after a plugin update. Scripts are copied to the Processing R scripts folder:

```
{QGIS_HOME}/processing/rscripts/
```

### Language Selection

MoveCost supports **5 languages** for the interface:

| Language | Code |
|----------|------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

The selected language applies to:
- Dialog interface labels
- Status and error messages
- Result table headers

### Layer Organization

| Function | Description |
|----------|-------------|
| **Organize Layers** | Auto-organize and style movecost output layers |

This function:
1. Groups output layers into logical groups in the QGIS Layers panel
2. Applies predefined colour styles (colour ramps for cost surfaces)
3. Renames layers with descriptive names

### Documentation

| Function | Description |
|----------|-------------|
| **Help** | Opens the inline tool documentation |

<!-- IMAGE: Settings tab with all options -->
> **Fig. 8**: The MoveCost Settings tab with configuration options

---

## Operational Workflow

### Step-by-Step Example: Calculating a Least-Cost Path

This example shows how to calculate a least-cost path between a settlement and a water source.

### Step 1: Data Preparation

```
1. Load the study area DTM into the QGIS project
2. Create a point layer with:
   - Origin point (settlement)
   - Destination point(s) (water source)
3. Verify that the coordinate reference system is consistent
```

### Step 2: Prerequisites Check

```
1. Open MoveCost from the toolbar
2. Go to the Settings tab
3. Click "Install R Scripts" (if first time)
4. Verify that no errors are reported
```

### Step 3: Run the Analysis

```
1. Switch to the Algorithms tab
2. Select "movecost" from Group 1
3. In the Processing window:
   - DTM: select the terrain raster
   - Origin: select the settlement point
   - Destination: select the water source point
   - Cost function: Tobler (recommended default)
4. Click Run
5. Wait for processing to complete
```

### Step 4: Analyse the Results

```
1. Switch to the Results tab
2. Review the Cost Summary for statistics
3. Examine the R plot for visualization
4. In the QGIS canvas, observe:
   - The accumulated cost surface (coloured raster)
   - The least-cost path (vector line)
```

### Step 5: Export

```
1. Switch to the Export tab
2. Export the cost table to CSV for further analysis
3. Generate the HTML report for documentation
4. Save the R plot from the Results tab
```

### Step 6: Organization

```
1. Return to the Settings tab
2. Click "Organize Layers" to sort the results
3. Layers are grouped and styled automatically
```

<!-- IMAGE: Complete workflow with annotated screenshots -->
> **Fig. 9**: The complete workflow from data preparation to final results

---

## Troubleshooting

### R Not Found

**Symptom**: Error message "R not found" or "R is not installed"

**Solutions**:
1. Verify that R is installed: open a terminal and type `R --version`
2. Check the R path in Processing settings:
   - **QGIS** > **Settings** > **Options** > **Processing** > **Providers** > **R**
   - Set the **R folder path** correctly
3. On macOS, R may be located at `/Library/Frameworks/R.framework/Resources/`
4. On Windows, typically at `C:\Program Files\R\R-4.x.x\`
5. On Linux, verify with `which R`

### R Scripts Missing

**Symptom**: Algorithms do not appear in the Processing toolbox

**Solutions**:
1. Open MoveCost > Settings > click **Install R Scripts**
2. Restart QGIS after installing the scripts
3. Verify that the Processing R Provider is active:
   - **QGIS** > **Plugins** > **Manage and Install Plugins** > Check "Processing R Provider"
4. Check the R scripts folder: `{QGIS_HOME}/processing/rscripts/`

### R Plots Not Showing

**Symptom**: The Results tab does not display any plot

**Solutions**:
1. Click **Refresh** in the Results tab
2. Use **Manual select** to navigate to the plots folder
3. Verify that the analysis completed successfully
4. Check the temporary directories:
   - macOS/Linux: `/tmp/` or `$TMPDIR`
   - Windows: `%TEMP%`
5. Some algorithms may not generate plots

### movecost Package Not Installed in R

**Symptom**: Error "there is no package called 'movecost'"

**Solutions**:
1. Open R or RStudio
2. Run: `install.packages("movecost")`
3. Verify: `library(movecost)` -- should produce no errors
4. If there are dependency issues: `install.packages("movecost", dependencies = TRUE)`

### Analysis Very Slow

**Symptom**: Processing takes a very long time

**Solutions**:
1. Use the **"by polygon"** variants to limit the computation area
2. Reduce the DTM resolution (resampling)
3. Check the DTM dimensions:
   - Very large DTMs (>10000x10000 pixels) require significant time
   - Clip the DTM to the area of interest before analysis
4. Close other applications to free RAM

### Projection / CRS Error

**Symptom**: Inconsistent results or coordinate reference system error

**Solutions**:
1. Verify that DTM and point layers have the **same CRS**
2. Use a **projected CRS** (metric), not geographic
3. Recommended CRS: UTM (e.g., EPSG:32632 for central Italy)
4. Reproject layers if necessary before analysis

---

## Technical Notes

### Tool Architecture

MoveCost is implemented as a standalone **QDialog** (`MoveCostDialog`) that:
- Interfaces with the QGIS Processing Framework for executing R algorithms
- Reads results from layers loaded in the project
- Manages R plot visualization through QLabel/QPixmap
- Generates HTML reports using predefined templates

### Source Files

| File | Description |
|------|-------------|
| `tabs/MoveCost.py` | Main dialog and interface logic |
| `gui/ui/MoveCost.ui` | Qt Designer interface layout |
| `resources/r_scripts/` | R scripts for movecost algorithms |

### Supported Cost Functions

The R `movecost` package supports several anisotropic cost functions:

| Function | Author | Description |
|----------|--------|-------------|
| **Tobler** | Tobler (1993) | Classic hiking cost function |
| **Minetti** | Minetti et al. (2002) | Based on metabolic cost |
| **Herzog** | Herzog (2010) | Modified variant |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Energetic model |
| **Others** | Various | See R package documentation |

### Bibliographic References

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibility

| Component | Minimum Version |
|-----------|-----------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| movecost R package | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Video Tutorial

### MoveCost - Least-Cost Path Analysis
`[Placeholder: video_movecost.mp4]`

**Contents**:
- Configuring R and the movecost package
- Installing R scripts in QGIS
- Running the basic movecost algorithm
- Viewing results and R plots
- Exporting reports

**Expected duration**: 20-25 minutes

---

*PyArchInit Documentation - MoveCost*
*Version: 5.0.x*
*Last updated: February 2026*
