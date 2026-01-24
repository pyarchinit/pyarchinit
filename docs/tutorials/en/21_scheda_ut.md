# Tutorial 21: TU Form - Topographic Units

## Introduction

The **TU Form** (Topographic Units) is the PyArchInit module dedicated to documenting archaeological surface surveys. It allows recording data related to material concentrations, terrain anomalies, and sites identified during field surveys.

### Basic Concepts

**Topographic Unit (TU):**
- Delimited area with homogeneous archaeological characteristics
- Identified during surface survey
- Defined by material concentration or visible anomalies

**Survey:**
- Systematic prospection of the territory
- Collection of data on ancient human presence
- Documentation without excavation

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **TU Form**

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **TU** icon

---

## Interface Overview

The form is organized into multiple tabs to document all aspects of the survey.

### Main Tabs

| # | Tab | Description |
|---|-----|-------------|
| 1 | Identification | Project, TU No., Location |
| 2 | Description | Definition, description, interpretation |
| 3 | TU Data | Conditions, methodology, dates |
| 4 | Analysis | Archaeological potential and risk |

### Main Toolbar

| Button | Function |
|--------|----------|
| ⏮ First | Go to first record |
| ◀ Prev | Previous record |
| ▶ Next | Next record |
| ⏭ Last | Go to last record |
| 🔍 Search | Advanced search |
| 💾 Save | Save record |
| 🗑 Delete | Delete record |
| 📄 PDF | Export PDF sheet |
| 📋 **PDF List** | Export TU list to PDF |
| 📦 **GNA Export** | Export to GNA format |
| 🗺 Show Layer | Display layer on map |

---

## Identification Fields

### Project

**Field**: `comboBox_progetto`
**Database**: `progetto`

Survey project name.

### TU Number

**Field**: `comboBox_nr_ut`
**Database**: `nr_ut`

Progressive Topographic Unit number.

### TU Letter

**Field**: `lineEdit_ut_letterale`
**Database**: `ut_letterale`

Optional alphabetic suffix (e.g., TU 15a, 15b).

---

## Location Fields

### Administrative Data

| Field | Database | Description |
|-------|----------|-------------|
| Nation | `nazione` | Country |
| Region | `regione` | Administrative region |
| Province | `provincia` | Province |
| Municipality | `comune` | Municipality |
| Fraction | `frazione` | Fraction/locality |
| Locality | `localita` | Local toponym |
| Address | `indirizzo` | Street/road |
| No. | `nr_civico` | Street number |

### Cartographic Data

| Field | Database | Description |
|-------|----------|-------------|
| IGM Map | `carta_topo_igm` | IGM sheet |
| CTR Map | `carta_ctr` | CTR element |
| Cadastral sheet | `foglio_catastale` | Cadastre reference |

### Coordinates

| Field | Database | Description |
|-------|----------|-------------|
| Geographic coord. | `coord_geografiche` | Lat/Long (format: lat, lon) |
| Plane coord. | `coord_piane` | UTM/local projection (format: x, y) |
| Altitude | `quota` | Elevation above sea level |
| Coord. precision | `coordinate_precision` | GPS accuracy in meters |

**⚠️ IMPORTANT**: Coordinates are used for heatmap generation. At least one of `coord_geografiche` or `coord_piane` must be filled for each TU.

---

## Descriptive Fields

### TU Definition

**Field**: `comboBox_def_ut`
**Database**: `def_ut`
**Thesaurus**: Code 12.7

Typological classification of the TU. Values are loaded from the thesaurus and automatically translated to the current language.

**Standard values:**
| Code | English | Italian |
|------|---------|---------|
| scatter | Material scatter | Area di dispersione materiali |
| site | Archaeological site | Sito archeologico |
| anomaly | Terrain anomaly | Anomalia del terreno |
| structure | Outcropping structure | Struttura affiorante |
| concentration | Finds concentration | Concentrazione reperti |
| traces | Anthropic traces | Tracce antropiche |
| findspot | Sporadic find | Rinvenimento sporadico |
| negative | Negative result | Esito negativo |

### TU Description

**Field**: `textEdit_descrizione`
**Database**: `descrizione_ut`

Detailed description of the Topographic Unit.

**Contents:**
- Extension and shape of the area
- Material density
- Terrain characteristics
- Visibility and conditions

### TU Interpretation

**Field**: `textEdit_interpretazione`
**Database**: `interpretazione_ut`

Functional/historical interpretation.

---

## Survey Fields with Thesaurus

The following fields use the thesaurus system to ensure standardized terminology translated into 7 languages (IT, EN, DE, ES, FR, AR, CA).

### Survey Type (12.1)

**Field**: `comboBox_survey_type`
**Database**: `survey_type`

| Code | English | Description |
|------|---------|-------------|
| intensive | Intensive survey | Systematic intensive survey |
| extensive | Extensive survey | Sampling survey |
| targeted | Targeted survey | Investigation of specific areas |
| random | Random sampling | Random methodology |

### Vegetation Coverage (12.2)

**Field**: `comboBox_vegetation_coverage`
**Database**: `vegetation_coverage`

| Code | English | Description |
|------|---------|-------------|
| none | Absent | Bare ground |
| sparse | Sparse | Coverage < 25% |
| moderate | Moderate | Coverage 25-50% |
| dense | Dense | Coverage 50-75% |
| very_dense | Very dense | Coverage > 75% |

### GPS Method (12.3)

**Field**: `comboBox_gps_method`
**Database**: `gps_method`

| Code | English | Description |
|------|---------|-------------|
| handheld | Handheld GPS | Portable GPS device |
| dgps | Differential GPS | DGPS with base station |
| rtk | RTK GPS | Real-time kinematic |
| total_station | Total station | Survey with total station |

### Surface Condition (12.4)

**Field**: `comboBox_surface_condition`
**Database**: `surface_condition`

| Code | English | Description |
|------|---------|-------------|
| ploughed | Ploughed | Recently ploughed field |
| stubble | Stubble | Presence of stubble |
| pasture | Pasture | Pasture/meadow land |
| woodland | Woodland | Wooded area |
| urban | Urban | Urban/built area |

### Accessibility (12.5)

**Field**: `comboBox_accessibility`
**Database**: `accessibility`

| Code | English | Description |
|------|---------|-------------|
| easy | Easy access | No restrictions |
| moderate_access | Moderate access | Some difficulties |
| difficult | Difficult access | Significant problems |
| restricted | Restricted access | Authorization only |

### Weather Conditions (12.6)

**Field**: `comboBox_weather_conditions`
**Database**: `weather_conditions`

| Code | English | Description |
|------|---------|-------------|
| sunny | Sunny | Clear weather |
| cloudy | Cloudy | Cloudy conditions |
| rainy | Rainy | Rain during survey |
| windy | Windy | Strong wind |

---

## Environmental Data

### Visibility Percentage

**Field**: `spinBox_visibility_percent`
**Database**: `visibility_percent`

Ground visibility percentage (0-100%). Numeric value important for archaeological potential calculation.

### Terrain Slope

**Field**: `lineEdit_andamento_terreno_pendenza`
**Database**: `andamento_terreno_pendenza`

Terrain morphology and slope.

### Land Use

**Field**: `lineEdit_utilizzo_suolo_vegetazione`
**Database**: `utilizzo_suolo_vegetazione`

Land use at the time of survey.

---

## Material Data

### TU Dimensions

**Field**: `lineEdit_dimensioni_ut`
**Database**: `dimensioni_ut`

Extension in square meters.

### Finds per sqm

**Field**: `lineEdit_rep_per_mq`
**Database**: `rep_per_mq`

Material density per square meter. Critical value for potential calculation.

### Dating Finds

**Field**: `lineEdit_rep_datanti`
**Database**: `rep_datanti`

Description of diagnostic materials.

---

## Chronology

### Period I

| Field | Database |
|-------|----------|
| Period I | `periodo_I` |
| Dating I | `datazione_I` |
| Interpretation I | `interpretazione_I` |

### Period II

| Field | Database |
|-------|----------|
| Period II | `periodo_II` |
| Dating II | `datazione_II` |
| Interpretation II | `interpretazione_II` |

---

## Analysis Tab - Archaeological Potential and Risk

The **Analysis** tab provides advanced tools for automatic calculation of archaeological potential and risk.

### Archaeological Potential

The system calculates a score from 0 to 100 based on weighted factors:

| Factor | Weight | Description | How it's calculated |
|--------|--------|-------------|---------------------|
| TU Definition | 30% | Type of archaeological evidence | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, etc. |
| Historical period | 25% | Material chronology | Older periods weigh more (Prehistoric = 90, Roman = 85, Medieval = 70, etc.) |
| Find density | 20% | Materials per sqm | >10/sqm = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Surface condition | 15% | Visibility and accessibility | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentation | 10% | Documentation quality | Photo presence = +20, bibliography = +30, investigations = +50 |

**Score Classification:**

| Score | Level | Color | Meaning |
|-------|-------|-------|---------|
| 80-100 | High | 🟢 Green | High probability of significant deposits |
| 60-79 | Medium-High | 🟡 Yellow-Green | Good probability, verification recommended |
| 40-59 | Medium | 🟠 Orange | Moderate probability |
| 20-39 | Low | 🔴 Red | Low probability |
| 0-19 | Not assessable | ⚫ Gray | Insufficient data |

### Archaeological Risk

Evaluates the risk of heritage impact/loss:

| Factor | Weight | Description | How it's calculated |
|--------|--------|-------------|---------------------|
| Accessibility | 25% | Ease of area access | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Land use | 25% | Agricultural/building activities | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Existing constraints | 20% | Legal protections | No constraints = 80, landscape protection = 40, archaeological protection = 10 |
| Previous investigations | 15% | Knowledge status | No investigation = 60, survey = 40, excavation = 20 |
| Potential | 15% | Inversely proportional to potential | High potential = high loss risk |

**Risk Classification:**

| Score | Level | Color | Recommended Action |
|-------|-------|-------|-------------------|
| 75-100 | High | 🔴 Red | Urgent intervention, immediate protection measures |
| 50-74 | Medium | 🟠 Orange | Active monitoring, evaluate protection |
| 25-49 | Low | 🟡 Yellow | Periodic monitoring |
| 0-24 | None | 🟢 Green | No immediate intervention needed |

### Database Fields for Analysis

| Field | Database | Description |
|-------|----------|-------------|
| Potential Score | `potential_score` | Calculated value 0-100 |
| Risk Score | `risk_score` | Calculated value 0-100 |
| Potential Factors | `potential_factors` | JSON with factor details |
| Risk Factors | `risk_factors` | JSON with factor details |
| Analysis Date | `analysis_date` | Calculation timestamp |
| Analysis Method | `analysis_method` | Algorithm used |

---

## TU Geometry Layers

PyArchInit manages three types of geometries for Topographic Units:

### Geometry Tables

| Layer | Table | Geometry Type | Use |
|-------|-------|---------------|-----|
| TU Points | `pyarchinit_ut_point` | Point | Point location |
| TU Lines | `pyarchinit_ut_line` | LineString | Traces, paths |
| TU Polygons | `pyarchinit_ut_polygon` | Polygon | Scatter areas |

### Creating TU Layers

1. **Via QGIS Browser:**
   - Open the database in Browser
   - Locate the table `pyarchinit_ut_point/line/polygon`
   - Drag onto the map

2. **Via PyArchInit Menu:**
   - Menu **PyArchInit** > **GIS Tools** > **Load TU Layers**
   - Select geometry type

### TU-Geometry Connection

Each geometry record is linked to the TU form through:

| Field | Description |
|-------|-------------|
| `progetto` | Project name (must match) |
| `nr_ut` | TU number (must match) |

### Geometry Creation Workflow

1. **Enable editing** on the desired TU layer
2. **Draw** the geometry on the map
3. **Fill in** the `progetto` and `nr_ut` attributes
4. **Save** the layer
5. **Verify** the connection from the TU form

---

## Heatmap Generation

The heatmap generation module allows visualizing the spatial distribution of archaeological potential and risk.

### Minimum Requirements

- **At least 2 TUs** with valid coordinates (`coord_geografiche` OR `coord_piane`)
- **Calculated scores** for potential and/or risk
- **CRS defined** in QGIS project

### Interpolation Methods

| Method | Description | When to use |
|--------|-------------|-------------|
| **KDE** (Kernel Density) | Gaussian kernel density estimation | Continuous distribution, many points |
| **IDW** (Inverse Distance) | Inverse distance weighting | Sparse data, point values important |
| **Grid** | Regular grid interpolation | Systematic analysis |

### Heatmap Parameters

| Parameter | Default Value | Description |
|-----------|---------------|-------------|
| Cell Size | 50 m | Grid resolution |
| Bandwidth (KDE) | Auto | Influence radius |
| Power (IDW) | 2 | Weighting exponent |

### Generation Procedure

1. **From TU form:**
   - Go to **Analysis** tab
   - Verify scores are calculated
   - Click **Generate Heatmap**

2. **Select parameters:**
   - Type: Potential or Risk
   - Method: KDE, IDW, or Grid
   - Cell size: typically 25-100 m

3. **Output:**
   - Raster layer added to QGIS
   - Saved in `pyarchinit_Raster_folder`
   - Symbology automatically applied

### Heatmap with Polygon Mask (GNA)

To generate heatmaps **within a project area** (e.g., study perimeter):

1. **Prepare the polygon** for the project area
2. **Use GNA Export** (see next section)
3. The system **automatically masks** the heatmap to the polygon

---

## GNA Export - National Geoportal for Archaeology

### What is GNA?

The **National Geoportal for Archaeology** (GNA) is the information system of the Italian Ministry of Culture for managing territorial archaeological data. PyArchInit supports export to the standard GNA GeoPackage format.

### GNA GeoPackage Structure

| Layer | Type | Description |
|-------|------|-------------|
| **MOPR** | Polygon | Project area/perimeter |
| **MOSI** | Point/Polygon | Archaeological sites (TUs) |
| **VRP** | MultiPolygon | Archaeological Potential Map |
| **VRD** | MultiPolygon | Archaeological Risk Map |

### TU → MOSI GNA Field Mapping

| GNA Field | PyArchInit TU Field | Notes |
|-----------|---------------------|-------|
| ID | `{progetto}_{nr_ut}` | Composite identifier |
| AMA | `def_ut` | GNA controlled vocabulary |
| OGD | `interpretazione_ut` | Object definition |
| OGT | `geometria` | Geometry type |
| DES | `descrizione_ut` | Description (max 10000 char) |
| OGM | `metodo_rilievo_e_ricognizione` | Identification method |
| DTSI | `periodo_I` → date | Start date (negative for BC) |
| DTSF | `periodo_II` → date | End date |
| PRVN | `nazione` | Nation |
| PVCR | `regione` | Region |
| PVCP | `provincia` | Province |
| PVCC | `comune` | Municipality |
| LCDQ | `quota` | Elevation |

### VRP Classification (Potential)

| Range | GNA Code | Label | Color |
|-------|----------|-------|-------|
| 0-20 | NV | Not assessable | Gray |
| 20-40 | NU | None | Green |
| 40-60 | BA | Low | Yellow |
| 60-80 | ME | Medium | Orange |
| 80-100 | AL | High | Red |

### VRD Classification (Risk)

| Range | GNA Code | Label | Color |
|-------|----------|-------|-------|
| 0-25 | NU | None | Green |
| 25-50 | BA | Low | Yellow |
| 50-75 | ME | Medium | Orange |
| 75-100 | AL | High | Red |

### GNA Export Procedure

1. **Data preparation:**
   - Verify all TUs have coordinates
   - Calculate potential/risk scores
   - Prepare project area polygon (MOPR)

2. **Start export:**
   - From TU form, click **GNA Export**
   - Or menu **PyArchInit** > **GNA** > **Export**

3. **Configuration:**
   ```
   Project: [select project]
   Project area: [select MOPR polygon layer]
   Output: [.gpkg file path]

   ☑ Export MOSI (sites)
   ☑ Generate VRP (potential)
   ☑ Generate VRD (risk)

   Heatmap method: KDE
   Cell size: 50 m
   ```

4. **Execution:**
   - Click **Export**
   - Wait for generation (may take several minutes)
   - GeoPackage is saved to specified path

5. **Verify output:**
   - Open GeoPackage in QGIS
   - Verify MOPR, MOSI, VRP, VRD layers
   - Check that VRP/VRD geometries are clipped to MOPR

### GNA Validation

To validate output against GNA specifications:

1. Load GeoPackage into the **official GNA template**
2. Verify layers are recognized
3. Check controlled vocabularies
4. Verify geometric relationships (MOSI inside MOPR)

---

## PDF Export

### Single TU Sheet

Exports the complete TU sheet in professional PDF format.

**Content:**
- Header with project and TU number
- Identification Section
- Location Section
- Terrain Section
- Survey Data Section
- Chronology Section
- Analysis Section (potential/risk with colored bars)
- Documentation Section

**Procedure:**
1. Select the TU record
2. Click the **PDF** button in the toolbar
3. PDF is saved to `pyarchinit_PDF_folder`

### TU List (PDF List)

Exports a tabular list of all TUs in landscape format.

**Columns:**
- TU, Project, Definition, Interpretation
- Municipality, Coordinates, Period I, Period II
- Finds/sqm, Visibility, Potential, Risk

**Procedure:**
1. Load TUs to export (search or view all)
2. Click the **PDF List** button in the toolbar
3. PDF is saved as `UT_List.pdf`

### TU Analysis Report

Generates a detailed potential/risk analysis report.

**Content:**
1. TU identification data
2. Archaeological Potential Section
   - Score with graphical indicator
   - Descriptive narrative text
   - Factor table with contributions
3. Archaeological Risk Section
   - Score with graphical indicator
   - Narrative text with recommendations
   - Factor table with contributions
4. Methodology Section

---

## Complete Operational Workflow

### Phase 1: Project Setup

1. **Create new project** in PyArchInit or use existing one
2. **Define study area** (MOPR polygon)
3. **Configure CRS** of QGIS project

### Phase 2: Field TU Registration

1. **Open TU form**
2. **New record** (click "New Record")
3. **Fill identification data:**
   ```
   Project: Tiber Valley Survey 2024
   TU No.: 25
   ```

4. **Fill location:**
   ```
   Region: Lazio
   Province: Rome
   Municipality: Fiano Romano
   Locality: Colle Alto
   Geographic coord.: 42.1234, 12.5678
   Altitude: 125 m
   GPS precision: 3 m
   ```

5. **Fill description** (using thesaurus):
   ```
   Definition: Finds concentration
   Description: Elliptical area of approx. 50x30 m
   with concentration of ceramic fragments
   and tiles on south-facing hillside...
   ```

6. **Fill survey data** (using thesaurus):
   ```
   Survey Type: Intensive survey
   Vegetation Coverage: Sparse
   GPS Method: Differential GPS
   Surface Condition: Ploughed
   Accessibility: Easy access
   Weather Conditions: Sunny
   Visibility: 80%
   Date: 15/04/2024
   Responsible: Team A
   ```

7. **Fill materials and chronology:**
   ```
   Dimensions: 1500 sqm
   Finds/sqm: 5-8
   Dating finds: Common ware,
   Italian sigillata, tiles

   Period I: Roman
   Dating I: 1st-2nd c. AD
   Interpretation I: Rural villa
   ```

8. **Save** (click "Save")

### Phase 3: Geometry Creation

1. **Load layer** `pyarchinit_ut_polygon`
2. **Enable editing**
3. **Draw** the TU perimeter on the map
4. **Fill attributes**: progetto, nr_ut
5. **Save** the layer

### Phase 4: Analysis

1. **Open Analysis tab** in TU form
2. **Verify** automatically calculated scores
3. **Generate heatmap** if needed
4. **Export PDF report** of analysis

### Phase 5: GNA Export (if required)

1. **Verify data completeness** for all TUs
2. **Prepare MOPR polygon** of project area
3. **Execute GNA Export**
4. **Validate output** against GNA specifications

---

## Tips & Tricks

### Workflow Optimization

1. **Pre-populate thesauri** before starting surveys
2. **Use project templates** with common data preset
3. **Sync coordinates** from GPS to `coord_geografiche` field
4. **Save frequently** during data entry

### Improving Data Quality

1. **Fill ALL relevant fields** for each TU
2. **Always use thesauri** instead of free text
3. **Verify coordinates** on map before saving
4. **Photographically document** each TU

### Heatmap Optimization

1. **Appropriate cell size**: use 25-50m for small areas, 100-200m for extensive areas
2. **KDE method** for continuous and homogeneous distributions
3. **IDW method** when point values are critical
4. **Always verify** coordinates are correct before generating

### Efficient GNA Export

1. **Prepare MOPR polygon** in advance as separate layer
2. **Verify all TUs** have valid coordinates
3. **Calculate scores** before export
4. **Use descriptive filenames** for GeoPackages

### Multi-User Management

1. **Define shared naming conventions** for TU numbering
2. **Use PostgreSQL database** for concurrent access
3. **Periodically synchronize** data
4. **Document changes** in note fields

---

## Troubleshooting

### Problem: Empty Thesaurus Comboboxes

**Symptoms:** Dropdowns for survey_type, vegetation, etc. are empty.

**Causes:**
- Thesaurus entries not present in database
- Wrong language code
- Thesaurus table not updated

**Solutions:**
1. Menu **PyArchInit** > **Database** > **Update database**
2. Verify table `pyarchinit_thesaurus_sigle` for `ut_table` entries
3. Check language settings
4. If needed, reimport thesauri from template

### Problem: Invalid Coordinates

**Symptoms:** Error saving or coordinates displayed in wrong position.

**Causes:**
- Wrong format (comma vs decimal point)
- Mismatched coordinate system
- Lat/lon order reversed

**Solutions:**
1. Correct format for `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Correct format for `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Always use period as decimal separator
4. Verify QGIS project CRS

### Problem: TU Not Visible on Map

**Symptoms:** After saving, TU doesn't appear on map.

**Causes:**
- Geometry not created in layer
- `progetto`/`nr_ut` attributes not matching
- Layer not loaded or hidden
- Different CRS between layer and project

**Solutions:**
1. Verify `pyarchinit_ut_point/polygon` layer exists
2. Check that attributes are correctly filled
3. Enable layer visibility in Layer panel
4. Use "Zoom to Layer" to verify extent

### Problem: Heatmap Not Generated

**Symptoms:** Error "At least 2 points with valid coordinates required".

**Causes:**
- Less than 2 TUs with coordinates
- Coordinates in wrong format
- Empty coordinate fields

**Solutions:**
1. Verify at least 2 TUs have `coord_geografiche` OR `coord_piane` filled
2. Check coordinate format (decimal point, correct order)
3. Recalculate scores before generating heatmap
4. Verify fields don't contain special characters

### Problem: Potential/Risk Score Not Calculated

**Symptoms:** potential_score and risk_score fields are empty or zero.

**Causes:**
- Required fields not filled
- Thesaurus values not recognized
- Calculation error

**Solutions:**
1. Fill at least: `def_ut`, `periodo_I`, `visibility_percent`
2. Use values from thesaurus (not free text)
3. Save record and reopen
4. Check QGIS logs for errors

### Problem: GNA Export Failed

**Symptoms:** GeoPackage not created or incomplete.

**Causes:**
- GNA module not available
- Incomplete TU data
- Invalid MOPR polygon
- Insufficient write permissions

**Solutions:**
1. Verify `modules/gna` module is installed
2. Check all TUs have valid coordinates
3. Verify MOPR polygon is valid (no self-intersections)
4. Check permissions on output folder
5. Verify sufficient disk space

### Problem: PDF Export with Missing Fields

**Symptoms:** Generated PDF doesn't show some fields or shows wrong values.

**Causes:**
- Database fields not updated
- Obsolete database schema version
- Data not saved before export

**Solutions:**
1. Save record before exporting
2. Update database if needed
3. Verify new fields (v4.9.67+) exist in table

### Problem: Qt6/QGIS 4.x Error

**Symptoms:** Plugin won't load on QGIS 4.x with `AllDockWidgetFeatures` error.

**Causes:**
- Qt5/Qt6 incompatibility
- UI file not updated

**Solutions:**
1. Update PyArchInit to latest version
2. `UT_ui.ui` file must use explicit flags instead of `AllDockWidgetFeatures`

---

## References

### Database

- **Table**: `ut_table`
- **Mapper class**: `UT`
- **ID**: `id_ut`

### Geometry Tables

- **Points**: `pyarchinit_ut_point`
- **Lines**: `pyarchinit_ut_line`
- **Polygons**: `pyarchinit_ut_polygon`

### Source Files

| File | Description |
|------|-------------|
| `gui/ui/UT_ui.ui` | Qt user interface |
| `tabs/UT.py` | Main controller |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | PDF sheet export |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | PDF analysis export |
| `modules/analysis/ut_potential.py` | Potential calculation |
| `modules/analysis/ut_risk.py` | Risk calculation |
| `modules/analysis/ut_heatmap_generator.py` | Heatmap generation |
| `modules/gna/gna_exporter.py` | GNA export |
| `modules/gna/gna_vocabulary_mapper.py` | GNA vocabulary mapping |

### TU Thesaurus Codes

| Code | Field | Description |
|------|-------|-------------|
| 12.1 | survey_type | Survey type |
| 12.2 | vegetation_coverage | Vegetation coverage |
| 12.3 | gps_method | GPS method |
| 12.4 | surface_condition | Surface condition |
| 12.5 | accessibility | Accessibility |
| 12.6 | weather_conditions | Weather conditions |
| 12.7 | def_ut | TU definition |

---

## Video Tutorials

### Survey Documentation
**Duration**: 15-18 minutes
- TU registration
- Survey data with thesaurus
- Geolocation

### Potential and Risk Analysis
**Duration**: 10-12 minutes
- Automatic score calculation
- Result interpretation
- Heatmap generation

### GNA Export
**Duration**: 12-15 minutes
- Data preparation
- Export configuration
- Output validation

### PDF Report Export
**Duration**: 8-10 minutes
- Standard TU sheet
- TU list
- Analysis report with maps

---

*Last updated: January 2026*
*PyArchInit v4.9.68 - Archaeological Data Management System*
