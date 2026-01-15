# Tutorial 09: Samples Form

## Introduction

The **Samples Form** is the PyArchInit module dedicated to managing archaeological samples. It allows you to record and track all types of samples taken during excavation: earth, charcoal, seeds, bones, mortars, metals, and other material destined for specialist analyses.

### Sample Types

Archaeological samples include:
- **Sediments**: for sedimentological, granulometric analyses
- **Charcoal**: for radiocarbon dating (C14)
- **Seeds/Pollen**: for archaeobotanical analyses
- **Bones**: for archaeozoological, isotopic, DNA analyses
- **Mortars/Plasters**: for archaeometric analyses
- **Metals/Slags**: for metallurgical analyses
- **Ceramics**: for fabric and provenance analyses

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **Samples Form**

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Samples** icon

---

## Interface Overview

The form presents a simplified layout for rapid sample management.

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | DB Info | Record status, sorting, counter |
| 3 | Identification Fields | Site, Sample No., Type |
| 4 | Descriptive Fields | Description, notes |
| 5 | Storage Fields | Box, Location |

---

## DBMS Toolbar

### Navigation Buttons

| Icon | Function | Description |
|------|----------|-------------|
| First rec | Go to first record |
| Prev rec | Go to previous record |
| Next rec | Go to next record |
| Last rec | Go to last record |

### CRUD Buttons

| Icon | Function | Description |
|------|----------|-------------|
| New record | Create a new sample record |
| Save | Save changes |
| Delete | Delete current record |

### Search Buttons

| Icon | Function | Description |
|------|----------|-------------|
| New search | Start new search |
| Search!!! | Execute search |
| Order by | Sort results |
| View all | View all records |

---

## Form Fields

### Site

**Field**: `comboBox_sito`
**Database**: `sito`

Select the archaeological site of belonging.

### Sample Number

**Field**: `lineEdit_nr_campione`
**Database**: `nr_campione`

Progressive sample identification number.

### Sample Type

**Field**: `comboBox_tipo_campione`
**Database**: `tipo_campione`

Typological classification of the sample. Values come from thesaurus.

**Common types:**
| Type | Description |
|------|-------------|
| Sediment | Soil sample |
| Charcoal | For C14 dating |
| Seeds | Carpological remains |
| Bones | Faunal remains |
| Mortar | Building binders |
| Ceramic | For fabric analysis |
| Metal | For metallurgical analysis |
| Pollen | For palynological analysis |

### Description

**Field**: `textEdit_descrizione`
**Database**: `descrizione`

Detailed description of the sample.

**Recommended content:**
- Physical characteristics of sample
- Quantity taken
- Collection method
- Reason for sampling
- Planned analyses

### Area

**Field**: `comboBox_area`
**Database**: `area`

Source excavation area.

### SU

**Field**: `comboBox_us`
**Database**: `us`

Source Stratigraphic Unit.

### Material Inventory Number

**Field**: `lineEdit_nr_inv_mat`
**Database**: `numero_inventario_materiale`

If sample is linked to an inventoried find, indicate inventory number.

### Box Number

**Field**: `lineEdit_nr_cassa`
**Database**: `nr_cassa`

Storage box or container.

### Storage Location

**Field**: `comboBox_luogo_conservazione`
**Database**: `luogo_conservazione`

Where the sample is stored.

**Examples:**
- Excavation laboratory
- Museum depot
- External analysis laboratory
- University

---

## Operational Workflow

### Creating a New Sample

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click "New Record"

3. **Identification data**
   ```
   Site: Roman Villa of Settefinestre
   Sample No.: C-2024-001
   Sample type: Charcoal
   ```

4. **Provenance**
   ```
   Area: 1000
   SU: 150
   ```

5. **Description**
   ```
   Charcoal sample taken from
   SU 150 burnt surface.
   Quantity: approx. 50 gr.
   Collected for C14 dating.
   ```

6. **Storage**
   ```
   Box No.: Samp-1
   Location: Excavation laboratory
   ```

7. **Save**
   - Click "Save"

### Searching Samples

1. Click "New Search"
2. Fill in criteria:
   - Site
   - Sample type
   - SU
3. Click "Search"
4. Navigate through results

---

## PDF Export

The form supports PDF export for:
- Sample list
- Individual detailed forms

---

## Best Practices

### Naming

- Use unique and meaningful codes
- Recommended format: `SITE-YEAR-PROGRESSIVE`
- Example: `VRS-2024-C001`

### Collection

- Always document collection coordinates
- Photograph the collection point
- Note depth and context

### Storage

- Use containers appropriate to type
- Clearly label each sample
- Maintain suitable conditions

### Documentation

- Always link to source SU
- Indicate planned analyses
- Record shipment to external laboratories

---

## Troubleshooting

### Problem: Sample type not available

**Cause**: Thesaurus not configured.

**Solution**:
1. Open Thesaurus Form
2. Add missing type for `campioni_table`
3. Save and reopen Samples Form

### Problem: SU not displayed

**Cause**: SU not registered for selected site.

**Solution**:
1. Verify SU exists in SU Form
2. Check it belongs to same site

---

## References

### Database

- **Table**: `campioni_table`
- **Mapper class**: `CAMPIONI`
- **ID**: `id_campione`

### Source Files

- **UI**: `gui/ui/Campioni.ui`
- **Controller**: `tabs/Campioni.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Video Tutorial

### Sample Management
**Duration**: 5-6 minutes
- New sample creation
- Field completion
- Search and export

[Video placeholder: video_campioni.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
