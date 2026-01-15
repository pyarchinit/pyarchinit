# Tutorial 17: TMA - Archaeological Materials Table

## Introduction

The **TMA Form** (Archaeological Materials Table) is the advanced PyArchInit module for managing excavation materials according to Italian ministerial standards. It allows detailed cataloging compliant with ICCD (Central Institute for Catalog and Documentation) regulations.

### Main Features

- ICCD-compliant cataloging
- Materials management by box/container
- Detailed chronological fields
- Associated materials table
- Integrated media management
- Label and PDF form export

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **TMA Form**

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **TMA** icon

---

## Interface Overview

The form presents a complex interface with many fields.

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | Identification Fields | Site, Area, SU, Box |
| 3 | Location Fields | Location, Room, Trench |
| 4 | Chronological Fields | Period, Fraction, Chronologies |
| 5 | Materials Table | Associated materials detail |
| 6 | Media Tab | Images and documents |

---

## Identification Fields

### Site

**Field**: `comboBox_sito`
**Database**: `sito`

Archaeological site (SCAN - ICCD Excavation Denomination).

### Area

**Field**: `comboBox_area`
**Database**: `area`

Excavation area.

### SU (DSCU)

**Field**: `comboBox_us`
**Database**: `dscu`

Source Stratigraphic Unit (DSCU = Description Excavation Unit).

### Sector

**Field**: `comboBox_settore`
**Database**: `settore`

Excavation sector.

### Inventory

**Field**: `lineEdit_inventario`
**Database**: `inventario`

Inventory number.

### Box

**Field**: `lineEdit_cassetta`
**Database**: `cassetta`

Box/container number.

---

## ICCD Location Fields

### LDCT - Location Type

**Field**: `comboBox_ldct`
**Database**: `ldct`

Type of storage location.

**ICCD Values:**
- museum
- superintendency
- deposit
- laboratory
- other

### LDCN - Location Name

**Field**: `lineEdit_ldcn`
**Database**: `ldcn`

Specific name of storage location.

### Previous Location

**Field**: `lineEdit_vecchia_coll`
**Database**: `vecchia_collocazione`

Previous location if applicable.

### SCAN - Excavation Name

**Field**: `lineEdit_scan`
**Database**: `scan`

Official name of excavation/research.

### Trench

**Field**: `comboBox_saggio`
**Database**: `saggio`

Reference trench/sondage.

### Room/Locus

**Field**: `lineEdit_vano`
**Database**: `vano_locus`

Room or locus of origin.

---

## Chronological Fields

### DTZG - Chronological Period

**Field**: `comboBox_dtzg`
**Database**: `dtzg`

General chronological period.

**ICCD Examples:**
- Bronze Age
- Iron Age
- Roman Age
- Medieval Age

### DTZS - Chronological Fraction

**Field**: `comboBox_dtzs`
**Database**: `dtzs`

Period subdivision.

**Examples:**
- early
- middle
- late
- final

### Chronologies

**Field**: `tableWidget_cronologie`
**Database**: `cronologie`

Table for multiple or detailed chronologies.

---

## Acquisition Fields

### AINT - Acquisition Type

**Field**: `comboBox_aint`
**Database**: `aint`

Method of materials acquisition.

**ICCD Values:**
- excavation
- survey
- purchase
- donation
- seizure

### AIND - Acquisition Date

**Field**: `dateEdit_aind`
**Database**: `aind`

Date of acquisition.

### RCGD - Survey Date

**Field**: `dateEdit_rcgd`
**Database**: `rcgd`

Survey date (if applicable).

### RCGZ - Survey Details

**Field**: `textEdit_rcgz`
**Database**: `rcgz`

Survey notes.

---

## Materials Fields

### OGTM - Material

**Field**: `comboBox_ogtm`
**Database**: `ogtm`

Main material (Object Type Material).

**ICCD Values:**
- ceramic
- glass
- metal
- bone
- stone
- brick/tile

### No. of Finds

**Field**: `spinBox_n_reperti`
**Database**: `n_reperti`

Total number of finds.

### Weight

**Field**: `doubleSpinBox_peso`
**Database**: `peso`

Total weight in grams.

### DESO - Object Description

**Field**: `textEdit_deso`
**Database**: `deso`

Brief description of objects.

---

## Materials Detail Table

**Widget**: `tableWidget_materiali`
**Associated table**: `tma_materiali`

Allows recording individual materials contained in the box.

### Columns

| ICCD Field | Description |
|------------|-------------|
| MADI | Material inventory |
| MACC | Category |
| MACL | Class |
| MACP | Typological specification |
| MACD | Definition |
| Chronology | Specific dating |
| MACQ | Quantity |

### Row Management

| Button | Function |
|--------|----------|
| + | Add material |
| - | Remove material |

---

## Documentation Fields

### FTAP - Photo Type

**Field**: `comboBox_ftap`
**Database**: `ftap`

Type of photographic documentation.

### FTAN - Photo Code

**Field**: `lineEdit_ftan`
**Database**: `ftan`

Photo identification code.

### DRAT - Drawing Type

**Field**: `comboBox_drat`
**Database**: `drat`

Type of graphic documentation.

### DRAN - Drawing Code

**Field**: `lineEdit_dran`
**Database**: `dran`

Drawing identification code.

### DRAA - Drawing Author

**Field**: `lineEdit_draa`
**Database**: `draa`

Drawing author.

---

## Media Tab

Management of images associated with the box/TMA.

### Features

- Thumbnail viewing
- Drag & drop to add images
- Double-click to view
- Link to media database

---

## Table View Tab

Table view of all TMA records for quick consultation.

### Features

- Grid view
- Column sorting
- Quick filters
- Multiple selection

---

## Export and Print

### PDF Export

| Option | Description |
|--------|-------------|
| TMA Form | Complete form |
| Labels | Box labels |

### Box Labels

Automatic label generation for:
- Box identification
- Brief contents
- Provenance data
- Barcode (optional)

---

## Operational Workflow

### Registering New TMA

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click on "New Record"

3. **Identification data**
   ```
   Site: Roman Villa
   Area: 1000
   SU: 150
   Box: C-001
   ```

4. **Location**
   ```
   LDCT: deposit
   LDCN: Rome Superintendency Deposit
   SCAN: Roman Villa Excavations 2024
   ```

5. **Chronology**
   ```
   DTZG: Roman Age
   DTZS: Imperial
   ```

6. **Materials** (table)
   ```
   | Inv | Cat | Class | Def | Qty |
   |-----|-----|-------|-----|-----|
   | 001 | ceramic | common | jar | 5 |
   | 002 | ceramic | sigillata | plate | 3 |
   | 003 | glass | - | unguentarium | 1 |
   ```

7. **Save**
   - Click on "Save"

---

## Best Practices

### ICCD Standards

- Use ICCD controlled vocabularies
- Follow official abbreviations
- Maintain terminological consistency

### Box Organization

- Unique progressive numbering
- One TMA per physical box
- Separate by SU when possible

### Documentation

- Always link photos and drawings
- Use unique codes for media
- Record author and date

---

## Troubleshooting

### Problem: ICCD vocabularies not available

**Cause**: Thesaurus not configured.

**Solution**:
1. Import standard ICCD vocabularies
2. Verify thesaurus configuration

### Problem: Materials not saved

**Cause**: Materials table not synchronized.

**Solution**:
1. Verify all required fields are filled
2. Save the main form before adding materials

---

## References

### Database

- **Main table**: `tma_materiali_archeologici`
- **Detail table**: `tma_materiali`
- **Mapper class**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### Source Files

- **UI**: `gui/ui/Tma.ui`
- **Controller**: `tabs/Tma.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Labels**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Video Tutorial

### TMA Cataloging
**Duration**: 15-18 minutes
- ICCD standards
- Complete compilation
- Materials management

[Video placeholder: video_tma_catalogazione.mp4]

### Label Generation
**Duration**: 5-6 minutes
- Label configuration
- Batch printing
- Customization

[Video placeholder: video_tma_etichette.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
