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
| Geographic coord. | `coord_geografiche` | Lat/Long |
| Planar coord. | `coord_piane` | UTM/Gauss-Boaga |
| Elevation | `quota` | Altitude a.s.l. |
| Coord. precision | `coordinate_precision` | GPS accuracy |

---

## Descriptive Fields

### TU Definition ⭐ NEW

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
- Area extent and shape
- Material density
- Terrain characteristics
- Visibility and conditions

### TU Interpretation

**Field**: `textEdit_interpretazione`
**Database**: `interpretazione_ut`

Functional/historical interpretation.

---

## Thesaurus Survey Fields ⭐ NEW

The following fields use the thesaurus system to ensure standardized terminology translated into 7 languages (IT, EN, DE, ES, FR, AR, CA).

### Survey Type (12.1)

**Field**: `comboBox_survey_type`
**Database**: `survey_type`

| Code | English | Description |
|------|---------|-------------|
| intensive | Intensive Survey | Intensive systematic field walking |
| extensive | Extensive Survey | Extensive reconnaissance survey |
| targeted | Targeted Survey | Investigation of specific areas |
| random | Random Sampling | Random sampling methodology |

### Vegetation Coverage (12.2)

**Field**: `comboBox_vegetation_coverage`
**Database**: `vegetation_coverage`

| Code | English | Description |
|------|---------|-------------|
| none | No vegetation | Bare ground |
| sparse | Sparse vegetation | Coverage < 25% |
| moderate | Moderate vegetation | Coverage 25-50% |
| dense | Dense vegetation | Coverage 50-75% |
| very_dense | Very dense vegetation | Coverage > 75% |

### GPS Method (12.3)

**Field**: `comboBox_gps_method`
**Database**: `gps_method`

| Code | English | Description |
|------|---------|-------------|
| handheld | Handheld GPS | Handheld GPS device |
| dgps | Differential GPS | DGPS with base station |
| rtk | RTK GPS | Real-time kinematic |
| total_station | Total Station | Total station survey |

### Surface Condition (12.4)

**Field**: `comboBox_surface_condition`
**Database**: `surface_condition`

| Code | English | Description |
|------|---------|-------------|
| ploughed | Ploughed | Recently ploughed field |
| stubble | Stubble | Crop stubble present |
| pasture | Pasture | Grassland/pasture |
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
| restricted | Restricted access | Permission only |

### Weather Conditions (12.6)

**Field**: `comboBox_weather_conditions`
**Database**: `weather_conditions`

| Code | English | Description |
|------|---------|-------------|
| sunny | Sunny | Clear and sunny |
| cloudy | Cloudy | Overcast conditions |
| rainy | Rainy | Rain during survey |
| windy | Windy | Strong winds |

---

## Environmental Data

### Visibility Percentage

**Field**: `spinBox_visibility_percent`
**Database**: `visibility_percent`

Soil visibility percentage (0-100%). Numeric value.

### Terrain Slope

**Field**: `lineEdit_andamento_terreno_pendenza`
**Database**: `andamento_terreno_pendenza`

Terrain morphology and slope.

### Land Use

**Field**: `lineEdit_utilizzo_suolo_vegetazione`
**Database**: `utilizzo_suolo_vegetazione`

Land use at time of survey.

---

## Materials Data

### TU Dimensions

**Field**: `lineEdit_dimensioni_ut`
**Database**: `dimensioni_ut`

Area extent in sqm.

### Finds per sqm

**Field**: `lineEdit_rep_per_mq`
**Database**: `rep_per_mq`

Material density per square meter.

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

## Analysis Tab ⭐ NEW

The **Analysis** tab provides advanced tools for automatic calculation of archaeological potential and risk.

### Archaeological Potential

The system calculates a score from 0 to 100 based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| TU Definition | 30% | Type of archaeological evidence |
| Historical Period | 25% | Material chronology |
| Finds Density | 20% | Materials per sqm |
| Surface Condition | 15% | Visibility and accessibility |
| Documentation | 10% | Documentation quality |

**Display:**
- Colored progress bar (green = high, yellow = medium, red = low)
- Detailed factors table with individual scores
- Automatic narrative text with interpretation

### Archaeological Risk

Evaluates the risk of impact/loss to heritage:

| Factor | Weight | Description |
|--------|--------|-------------|
| Accessibility | 25% | Ease of access to the area |
| Land Use | 25% | Agricultural/building activities |
| Existing Constraints | 20% | Legal protections |
| Previous Investigations | 15% | State of knowledge |
| Visibility | 15% | Site exposure |

### Heatmap Generation

The **Generate Heatmap** button creates raster layers displaying:
- **Potential Heatmap**: spatial distribution of archaeological potential
- **Risk Heatmap**: impact risk map

**Available methods:**
- Kernel Density Estimation (KDE)
- Inverse Distance Weighting (IDW)
- Natural Neighbor

---

## PDF Export ⭐ IMPROVED

### Standard TU Form

Exports the complete TU form with all filled fields.

### TU Analysis Report

Generates a PDF report including:

1. **TU identification data**
2. **Archaeological Potential Section**
   - Score with graphic indicator
   - Descriptive narrative text
   - Factors table with contributions
   - Potential heatmap image (if generated)
3. **Archaeological Risk Section**
   - Score with graphic indicator
   - Narrative text with recommendations
   - Factors table with contributions
   - Risk heatmap image (if generated)
4. **Methodology Section**
   - Description of algorithms used
   - Notes on factor weights

The report is available in all 7 supported languages.

---

## Operational Workflow

### Registering New TU

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click on "New Record"

3. **Identification data**
   ```
   Project: Tiber Valley Survey 2024
   TU No.: 25
   ```

4. **Location**
   ```
   Region: Lazio
   Province: Rome
   Municipality: Fiano Romano
   Locality: Colle Alto
   Coord.: 42.1234 N, 12.5678 E
   Elevation: 125 m
   ```

5. **Description** (using thesaurus)
   ```
   Definition: Finds concentration (from thesaurus)
   Description: Elliptical area of ca. 50x30 m
   with concentration of ceramic fragments
   and bricks on south-facing hillside...
   ```

6. **Survey data** (using thesaurus)
   ```
   Survey Type: Intensive Survey
   Vegetation Coverage: Sparse
   GPS Method: Differential GPS
   Surface Condition: Ploughed
   Accessibility: Easy access
   Weather Conditions: Sunny
   Visibility: 80%
   Date: 15/04/2024
   Responsible: Team A
   ```

7. **Materials and chronology**
   ```
   Dimensions: 1500 sqm
   Finds/sqm: 5-8
   Dating finds: Common ware,
   Italian sigillata, bricks

   Period I: Roman
   Dating I: 1st-2nd century AD
   Interpretation I: Rustic villa
   ```

8. **Analysis** (Analysis tab)
   - Check Potential score
   - Check Risk score
   - Generate Heatmap if needed

9. **Save**
   - Click on "Save"

---

## GIS Integration

The TU form is closely integrated with QGIS:

- **TU Layer**: geometry visualization
- **Linked attributes**: data from form
- **Map selection**: click on geometry opens form
- **Heatmap as layer**: generated maps are saved as raster layers

---

## Best Practices

### Thesaurus Usage

- Always prefer thesaurus values for consistency
- Values are automatically translated to user's language
- For new values, add them to the thesaurus first

### Nomenclature

- Progressive numbering per project
- Use suffixes for subdivisions
- Document conventions

### Geolocation

- Use differential GPS when possible
- Always indicate method and precision
- Verify coordinates on map

### Documentation

- Photograph every TU
- Produce planimetric sketches
- Record visibility conditions

### Analysis

- Always verify calculated scores
- Generate heatmaps for complete projects
- Export reports for documentation

---

## UT Thesaurus Codes

| Code | Field | Description |
|------|-------|-------------|
| 12.1 | survey_type | Survey type |
| 12.2 | vegetation_coverage | Vegetation coverage |
| 12.3 | gps_method | GPS method |
| 12.4 | surface_condition | Surface condition |
| 12.5 | accessibility | Accessibility |
| 12.6 | weather_conditions | Weather conditions |
| 12.7 | def_ut | TU Definition |

---

## Troubleshooting

### Problem: Empty comboboxes

**Cause**: Thesaurus entries not present in database.

**Solution**:
1. Update database via "Update database"
2. Verify that `pyarchinit_thesaurus_sigle` table contains entries for `ut_table`
3. Check language code in settings

### Problem: Invalid coordinates

**Cause**: Wrong format or reference system.

**Solution**:
1. Verify format (DD or DMS)
2. Check reference system
3. Use QGIS conversion tool

### Problem: TU not visible on map

**Cause**: Geometry not associated.

**Solution**:
1. Verify TU layer exists
2. Check that record has geometry
3. Verify layer projection

### Problem: Heatmap not generated

**Cause**: Insufficient data or calculation error.

**Solution**:
1. Verify at least 3 TUs with complete data exist
2. Check that geometries are valid
3. Verify available disk space

---

## References

### Database

- **Table**: `ut_table`
- **Mapper class**: `UT`
- **ID**: `id_ut`

### Source Files

- **UI**: `gui/ui/UT_ui.ui`
- **Controller**: `tabs/UT.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_UTsheet_pdf.py`
- **Analysis PDF**: `modules/utility/pyarchinit_exp_UT_analysis_pdf.py`
- **Potential Calculator**: `modules/analysis/ut_potential.py`
- **Risk Calculator**: `modules/analysis/ut_risk.py`
- **Heatmap Generator**: `modules/analysis/ut_heatmap_generator.py`

---

## Video Tutorial

### Survey Documentation
**Duration**: 15-18 minutes
- TU recording
- Survey data with thesaurus
- Geolocation

[Video placeholder: video_ut_survey.mp4]

### Potential and Risk Analysis
**Duration**: 10-12 minutes
- Automatic score calculation
- Results interpretation
- Heatmap generation

[Video placeholder: video_ut_analysis.mp4]

### PDF Report Export
**Duration**: 8-10 minutes
- Standard TU form
- Analysis report with maps
- Output customization

[Video placeholder: video_ut_pdf.mp4]

---

*Last updated: January 2026*
*PyArchInit v4.9.68 - Archaeological Data Management System*
