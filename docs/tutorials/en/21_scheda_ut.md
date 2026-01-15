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
2. Select **TU Form** (or **TU form**)

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **TU** icon

---

## Interface Overview

The form is rich in fields to document all aspects of the survey.

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | Identification Fields | Project, TU No. |
| 3 | Location | Geographic and administrative data |
| 4 | Description | Definition, description, interpretation |
| 5 | Survey Data | Conditions, methodology |
| 6 | Chronology | Periods and dates |

---

## Identification Fields

### Project

**Field**: `lineEdit_progetto`
**Database**: `progetto`

Survey project name.

### TU Number

**Field**: `lineEdit_nr_ut`
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
| GPS method | `gps_method` | Survey type |

---

## Descriptive Fields

### TU Definition

**Field**: `comboBox_def_ut`
**Database**: `def_ut`

Typological classification of the TU.

**Values:**
- Material concentration
- Fragment area
- Terrain anomaly
- Emerging structure
- Archaeological site

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

## Environmental Data

### Terrain Slope

**Field**: `comboBox_terreno`
**Database**: `andamento_terreno_pendenza`

Morphology and slope.

**Values:**
- Flat
- Slight slope
- Medium slope
- Steep slope
- Terraced

### Land Use

**Field**: `comboBox_suolo`
**Database**: `utilizzo_suolo_vegetazione`

Land use at time of survey.

**Values:**
- Arable
- Meadow/pasture
- Vineyard
- Olive grove
- Uncultivated
- Forest
- Urban

### Soil Description

**Field**: `textEdit_suolo`
**Database**: `descrizione_empirica_suolo`

Observed pedological characteristics.

### Place Description

**Field**: `textEdit_luogo`
**Database**: `descrizione_luogo`

Landscape context.

---

## Survey Data

### Survey Method

**Field**: `comboBox_metodo`
**Database**: `metodo_rilievo_e_ricognizione`

Methodology adopted.

**Values:**
- Systematic survey
- Extensive survey
- Targeted survey
- Verification of report

### Survey Type

**Field**: `comboBox_survey_type`
**Database**: `survey_type`

Type of prospection.

### Visibility

**Field**: `spinBox_visibility`
**Database**: `visibility_percent`

Soil visibility percentage (0-100%).

### Vegetation Coverage

**Field**: `comboBox_vegetation`
**Database**: `vegetation_coverage`

Degree of vegetation coverage.

### Surface Condition

**Field**: `comboBox_surface`
**Database**: `surface_condition`

Surface status.

**Values:**
- Freshly plowed
- Plowed not harrowed
- Low grass
- High grass
- Stubble

### Accessibility

**Field**: `comboBox_accessibility`
**Database**: `accessibility`

Ease of access to the area.

### Date

**Field**: `dateEdit_data`
**Database**: `data`

Survey date.

### Time/Weather

**Field**: `lineEdit_meteo`
**Database**: `ora_meteo`

Weather conditions and time.

### Responsible

**Field**: `comboBox_responsabile`
**Database**: `responsabile`

Survey responsible.

### Team

**Field**: `textEdit_team`
**Database**: `team_members`

Team members.

---

## Materials Data

### TU Dimensions

**Field**: `lineEdit_dimensioni`
**Database**: `dimensioni_ut`

Area extent in sqm.

### Finds per sqm

**Field**: `lineEdit_rep_mq`
**Database**: `rep_per_mq`

Material density.

### Dating Finds

**Field**: `textEdit_rep_datanti`
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

## Other Fields

### Geometry

**Field**: `comboBox_geometria`
**Database**: `geometria`

TU shape.

### Bibliography

**Field**: `textEdit_bibliografia`
**Database**: `bibliografia`

Bibliographic references.

### Documentation

**Field**: `textEdit_documentazione`
**Database**: `documentazione`

Documentation produced (photos, drawings).

### Photo Documentation

**Field**: `textEdit_photo_doc`
**Database**: `photo_documentation`

Photographic documentation list.

### Protection Authorities/Constraints

**Field**: `textEdit_vincoli`
**Database**: `enti_tutela_vincoli`

Constraints and protection authorities.

### Preliminary Investigations

**Field**: `textEdit_indagini`
**Database**: `indagini_preliminari`

Previous investigations if any.

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

5. **Description**
   ```
   Definition: Material concentration
   Description: Elliptical area of ca. 50x30 m
   with concentration of ceramic fragments
   and bricks on south-facing hillside...
   ```

6. **Survey data**
   ```
   Method: Systematic survey
   Visibility: 80%
   Condition: Freshly plowed
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

8. **Save**
   - Click on "Save"

---

## GIS Integration

The TU form is closely integrated with QGIS:

- **TU Layer**: geometry visualization
- **Linked attributes**: data from form
- **Map selection**: click on geometry opens form

---

## PDF Export

The form supports PDF export for:
- Single TU forms
- Project lists
- Survey reports

---

## Best Practices

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

### Materials

- Collect diagnostic samples
- Estimate density per area
- Document spatial distribution

---

## Troubleshooting

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

---

## Video Tutorial

### Survey Documentation
**Duration**: 15-18 minutes
- TU recording
- Survey data
- Geolocation

[Video placeholder: video_ut_survey.mp4]

### GIS Survey Integration
**Duration**: 10-12 minutes
- Layers and attributes
- Results visualization
- Spatial analysis

[Video placeholder: video_ut_gis.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
