# Tutorial 10: Documentation Form

## Introduction

The **Documentation Form** is the PyArchInit module for managing excavation graphic documentation: plans, sections, elevations, surveys, and any other graphic output produced during archaeological activities.

### Documentation Types

- **Plans**: layer plans, phase plans, general plans
- **Sections**: stratigraphic sections
- **Elevations**: wall elevations, excavation fronts
- **Surveys**: topographic, photogrammetric surveys
- **Orthophotos**: drone/photogrammetry outputs
- **Find drawings**: ceramics, metals, etc.

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **Documentation Form**

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Documentation** icon

---

## Interface Overview

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | DB Info | Record status, sorting, counter |
| 3 | Identification Fields | Site, Name, Date |
| 4 | Typological Fields | Type, Source, Scale |
| 5 | Descriptive Fields | Drawer, Notes |

---

## DBMS Toolbar

### Standard Buttons

| Function | Description |
|----------|-------------|
| First/Prev/Next/Last rec | Navigation between records |
| New record | Create new record |
| Save | Save changes |
| Delete | Delete record |
| New search / Search | Search functions |
| Order by | Sort results |
| View all | View all records |

---

## Form Fields

### Site

**Field**: `comboBox_sito_doc`
**Database**: `sito`

Reference archaeological site.

### Documentation Name

**Field**: `lineEdit_nome_doc`
**Database**: `nome_doc`

Document identification name.

**Naming conventions:**
- `P` = Plan (e.g., P001)
- `S` = Section (e.g., S001)
- `E` = Elevation (e.g., E001)
- `R` = Survey (e.g., R001)

### Date

**Field**: `dateEdit_data`
**Database**: `data`

Drawing/survey execution date.

### Documentation Type

**Field**: `comboBox_tipo_doc`
**Database**: `tipo_documentazione`

Document type.

**Typical values:**
| Type | Description |
|------|-------------|
| Layer plan | Single SU |
| Phase plan | Multiple coeval SU |
| General plan | Overview |
| Stratigraphic section | Vertical profile |
| Elevation | Wall upstanding |
| Topographic survey | General planimetry |
| Orthophoto | From photogrammetry |
| Find drawing | Ceramics, metal, etc. |

### Source

**Field**: `comboBox_sorgente`
**Database**: `sorgente`

Production source/method.

**Values:**
- Direct survey
- Photogrammetry
- Laser scanner
- GPS/Total station
- CAD digitization
- Drone orthophoto

### Scale

**Field**: `comboBox_scala`
**Database**: `scala`

Representation scale.

**Common scales:**
| Scale | Typical use |
|-------|-------------|
| 1:1 | Find drawings |
| 1:5 | Details |
| 1:10 | Sections, details |
| 1:20 | Layer plans |
| 1:50 | General plans |
| 1:100 | Planimetries |
| 1:200+ | Topographic maps |

### Drawer

**Field**: `comboBox_disegnatore`
**Database**: `disegnatore`

Drawing/survey author.

### Notes

**Field**: `textEdit_note`
**Database**: `note`

Additional notes about the document.

---

## Operational Workflow

### Registering New Documentation

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click "New Record"

3. **Identification data**
   ```
   Site: Roman Villa of Settefinestre
   Name: P025
   Date: 15/06/2024
   ```

4. **Classification**
   ```
   Type: Layer plan
   Source: Direct survey
   Scale: 1:20
   ```

5. **Author and notes**
   ```
   Drawer: M. Rossi
   Notes: SU 150 plan. Highlights
   floor surface boundaries.
   ```

6. **Save**
   - Click "Save"

### Searching Documentation

1. Click "New Search"
2. Fill in criteria:
   - Site
   - Documentation type
   - Scale
   - Drawer
3. Click "Search"
4. Navigate through results

---

## PDF Export

The form supports PDF export for:
- Documentation list
- Detailed forms

---

## Best Practices

### Naming

- Use consistent codes throughout project
- Progressive numbering by type
- Document conventions adopted

### Organization

- Always link to reference site
- Indicate actual scale
- Record date and author

### Archiving

- Link digital files via media management
- Maintain backup copies
- Use standard formats (PDF, TIFF)

---

## Troubleshooting

### Problem: Documentation type not available

**Cause**: Thesaurus not configured.

**Solution**:
1. Open Thesaurus Form
2. Add missing types for `documentazione_table`

### Problem: File not displayed

**Cause**: Incorrect path or missing file.

**Solution**:
1. Verify file exists
2. Check path in media configuration

---

## References

### Database

- **Table**: `documentazione_table`
- **Mapper class**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### Source Files

- **UI**: `gui/ui/Documentazione.ui`
- **Controller**: `tabs/Documentazione.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Video Tutorial

### Graphic Documentation Management
**Duration**: 6-8 minutes
- New documentation registration
- Classification and metadata
- Search and consultation

[Video placeholder: video_documentazione.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
