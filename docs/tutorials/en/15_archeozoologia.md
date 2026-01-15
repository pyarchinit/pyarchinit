# Tutorial 15: Archaeozoology Form (Fauna)

## Introduction

The **Archaeozoology/Fauna Form** (FAUNA RECORD - FR) is the PyArchInit module dedicated to the analysis and documentation of faunal remains. It allows recording detailed archaeozoological data for the study of ancient subsistence economies.

### Basic Concepts

**Archaeozoology:**
- Study of animal remains from archaeological contexts
- Analysis of human-animal relationships in the past
- Reconstruction of diets, husbandry, hunting

**Recorded data:**
- Taxonomic identification (species)
- Skeletal parts present
- MNI (Minimum Number of Individuals)
- Conservation status
- Taphonomic traces
- Butchery marks

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **Fauna Form** (or **Fauna form**)

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Fauna** icon (stylized bone)

---

## Interface Overview

The form is organized in thematic tabs:

### Main Tabs

| # | Tab | Content |
|---|-----|---------|
| 1 | Identification Data | Site, Area, SU, Context |
| 2 | Archaeozoological Data | Species, MNI, Skeletal parts |
| 3 | Taphonomic Data | Conservation, Fragmentation, Traces |
| 4 | Contextual Data | Depositional context, Associations |
| 5 | Statistics | Charts and quantifications |

---

## Toolbar

The toolbar provides standard functions:

| Icon | Function |
|------|----------|
| First/Prev/Next/Last | Record navigation |
| New | New record |
| Save | Save |
| Delete | Delete |
| Search | Search |
| View All | View all |
| PDF | PDF Export |

---

## Identification Data Tab

### SU Selection

**Field**: `comboBox_us_select`

Selects the source SU. Shows available SUs in "Site - Area - SU" format.

### Site

**Field**: `comboBox_sito`
**Database**: `sito`

Archaeological site.

### Area

**Field**: `comboBox_area`
**Database**: `area`

Excavation area.

### Trench

**Field**: `comboBox_saggio`
**Database**: `saggio`

Source trench/sondage.

### SU

**Field**: `comboBox_us`
**Database**: `us`

Stratigraphic Unit.

### SU Dating

**Field**: `lineEdit_datazione`
**Database**: `datazione_us`

Chronological framework of the SU.

### Responsible

**Field**: `comboBox_responsabile`
**Database**: `responsabile_scheda`

Form author.

### Compilation Date

**Field**: `dateEdit_data`
**Database**: `data_compilazione`

Form compilation date.

---

## Archaeozoological Data Tab

### Context

**Field**: `comboBox_contesto`
**Database**: `contesto`

Type of depositional context.

**Values:**
- Settlement
- Dump/Waste
- Fill
- Living floor
- Burial
- Ritual

### Species

**Field**: `comboBox_specie`
**Database**: `specie`

Taxonomic identification.

**Common archaeozoological species:**
| Species | Scientific name |
|---------|-----------------|
| Cattle | Bos taurus |
| Sheep | Ovis aries |
| Goat | Capra hircus |
| Pig | Sus domesticus |
| Horse | Equus caballus |
| Red deer | Cervus elaphus |
| Wild boar | Sus scrofa |
| Hare | Lepus europaeus |
| Dog | Canis familiaris |
| Cat | Felis catus |
| Chicken | Gallus gallus |

### Minimum Number of Individuals (MNI)

**Field**: `spinBox_nmi`
**Database**: `numero_minimo_individui`

Estimate of minimum number of individuals represented.

### Skeletal Parts

**Field**: `tableWidget_parti`
**Database**: `parti_scheletriche`

Table for recording present anatomical parts.

**Columns:**
| Column | Description |
|--------|-------------|
| Element | Bone/anatomical part |
| Side | Right/Left/Axial |
| Quantity | Number of fragments |
| MNI | Contribution to MNI |

### Bone Measurements

**Field**: `tableWidget_misure`
**Database**: `misure_ossa`

Standard osteometric measurements.

---

## Taphonomic Data Tab

### Fragmentation Status

**Field**: `comboBox_frammentazione`
**Database**: `stato_frammentazione`

Degree of fragmentation of remains.

**Values:**
- Complete
- Slightly fragmented
- Fragmented
- Highly fragmented

### Conservation Status

**Field**: `comboBox_conservazione`
**Database**: `stato_conservazione`

General conservation conditions.

**Values:**
- Excellent
- Good
- Fair
- Poor
- Very poor

### Combustion Traces

**Field**: `comboBox_combustione`
**Database**: `tracce_combustione`

Presence of fire traces.

**Values:**
- Absent
- Blackening
- Carbonization
- Calcination

### Taphonomic Signs

**Field**: `comboBox_segni_tafo`
**Database**: `segni_tafonomici_evidenti`

Traces of post-depositional alteration.

**Types:**
- Weathering (atmospheric agents)
- Root marks
- Gnawing
- Trampling

### Morphological Alterations

**Field**: `textEdit_alterazioni`
**Database**: `alterazioni_morfologiche`

Detailed description of observed alterations.

---

## Contextual Data Tab

### Recovery Methodology

**Field**: `comboBox_metodologia`
**Database**: `metodologia_recupero`

Method of remains collection.

**Values:**
- Hand-picked
- Dry sieving
- Flotation
- Wet sieving

### Remains in Anatomical Connection

**Field**: `checkBox_connessione`
**Database**: `resti_connessione_anatomica`

Presence of connected parts.

### Associated Find Classes

**Field**: `textEdit_associazioni`
**Database**: `classi_reperti_associazione`

Other materials associated with faunal remains.

### Observations

**Field**: `textEdit_osservazioni`
**Database**: `osservazioni`

General notes.

### Interpretation

**Field**: `textEdit_interpretazione`
**Database**: `interpretazione`

Interpretation of the faunal context.

---

## Statistics Tab

Provides tools for:
- Distribution charts by species
- Total MNI calculation
- Comparisons between SUs/phases
- Statistical data export

---

## Operational Workflow

### Recording Faunal Remains

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click on "New Record"

3. **Identification data**
   ```
   Site: Roman Villa
   Area: 1000
   SU: 150
   Responsible: G. Verdi
   Date: 20/07/2024
   ```

4. **Archaeozoological data** (Tab 2)
   ```
   Context: Dump/Waste
   Species: Bos taurus
   MNI: 3

   Skeletal parts:
   - Humerus / Right / 2 / 1
   - Tibia / Left / 3 / 2
   - Metapodial / - / 5 / 1
   ```

5. **Taphonomic data** (Tab 3)
   ```
   Fragmentation: Fragmented
   Conservation: Good
   Combustion: Absent
   Taphonomic signs: Root marks
   ```

6. **Interpretation**
   ```
   Food waste dump.
   Presence of butchery marks
   on some long bones.
   ```

7. **Save**
   - Click on "Save"

---

## Best Practices

### Identification

- Use reference collections
- Indicate certainty level of ID
- Record unidentifiable remains as well

### MNI

- Calculate for each species separately
- Consider side and age of finds
- Document calculation method

### Taphonomy

- Systematically observe each specimen
- Document traces before washing
- Photograph significant cases

### Context

- Always link to source SU
- Record recovery method
- Note significant associations

---

## PDF Export

The form allows generating:
- Detailed single forms
- Lists by SU or phase
- Statistical reports

---

## Troubleshooting

### Problem: Species not available

**Cause**: Incomplete species list.

**Solution**:
1. Check fauna thesaurus
2. Add missing species
3. Contact administrator

### Problem: MNI not calculated

**Cause**: Skeletal parts not recorded.

**Solution**:
1. Fill in skeletal parts table
2. Indicate side and quantity
3. System will calculate automatically

---

## References

### Database

- **Table**: `fauna_table`
- **Mapper class**: `FAUNA`
- **ID**: `id_fauna`

### Source Files

- **Controller**: `tabs/Fauna.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Video Tutorial

### Archaeozoological Recording
**Duration**: 12-15 minutes
- Taxonomic identification
- Skeletal parts recording
- Taphonomic analysis

[Video placeholder: video_archeozoologia.mp4]

### Faunal Statistics
**Duration**: 8-10 minutes
- MNI calculation
- Distribution charts
- Data export

[Video placeholder: video_fauna_statistiche.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
