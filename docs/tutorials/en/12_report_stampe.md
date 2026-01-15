# Tutorial 12: Reports and PDF Prints

## Introduction

PyArchInit offers a comprehensive **PDF report** generation system for all archaeological forms. This feature allows exporting documentation in printable format, compliant with ministerial standards and ready for archiving.

### Available Report Types

| Type | Description | Source Form |
|------|-------------|-------------|
| SU Forms | Complete SU/WSU reports | SU Form |
| SU Index | Synthetic SU list | SU Form |
| Periodization Forms | Period/phase reports | Periodization Form |
| Structure Forms | Structure reports | Structure Form |
| Finds Forms | Materials inventory reports | Inventory Form |
| Grave Forms | Burial reports | Grave Form |
| Sample Forms | Sample reports | Sample Form |
| Individual Forms | Anthropological reports | Individual Form |

## Accessing the Function

### From Main Menu
1. **PyArchInit** in menu bar
2. Select **Export PDF**

### From Toolbar
Click on the **PDF** icon in the PyArchInit toolbar

## Export Interface

### Window Overview

The PDF export window presents:

```
+------------------------------------------+
|        PyArchInit - Export PDF            |
+------------------------------------------+
| Site: [Site selection ComboBox]    [v]   |
+------------------------------------------+
| Forms to export:                          |
| [x] SU Forms                              |
| [x] Periodization Forms                   |
| [x] Structure Forms                       |
| [x] Finds Forms                           |
| [x] Grave Forms                           |
| [x] Sample Forms                          |
| [x] Individual Forms                      |
+------------------------------------------+
| [Open Folder]  [Export PDF]  [Cancel]    |
+------------------------------------------+
```

### Site Selection

| Field | Description |
|-------|-------------|
| Site ComboBox | List of all sites in database |

**Note**: Export is per single site. To export multiple sites, repeat the operation.

### Form Checkboxes

Each checkbox enables export of a specific type:

| Checkbox | Generates |
|----------|-----------|
| SU Forms | Complete forms + SU Index |
| Periodization Forms | Period forms + Index |
| Structure Forms | Structure forms + Index |
| Finds Forms | Material forms + Index |
| Grave Forms | Burial forms + Index |
| Sample Forms | Sample forms + Index |
| Individual Forms | Anthropological forms + Index |

## Export Process

### Step 1: Data Selection

```python
# System executes for each selected type:
1. Database query for selected site
2. Data sorting (by number, area, etc.)
3. List preparation for generation
```

### Step 2: PDF Generation

For each form type:
1. **Single form**: Detailed PDF for each record
2. **Index**: Summary PDF with all records

### Step 3: Saving

Output to folder:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Report Contents

### SU Form

Information included:
- **Identification data**: Site, Area, SU Number, Unit type
- **Definitions**: Stratigraphic, Interpretive
- **Description**: Complete descriptive text
- **Interpretation**: Interpretive analysis
- **Periodization**: Initial/Final Period/Phase
- **Physical characteristics**: Color, consistency, formation
- **Measurements**: Min/max elevations, dimensions
- **Relationships**: Stratigraphic relationships list
- **Documentation**: Graphic and photographic references
- **WSU data**: (if applicable) Building technique, materials

### SU Index

Summary table with columns:
| Site | Area | SU | Stratigraphic Def. | Interpretive Def. | Period |

### Periodization Form

- Site
- Period Number
- Phase Number
- Initial/final chronology
- Extended dating
- Period description

### Structure Form

- Identification data (Site, Code, Number)
- Category, Type, Definition
- Description and Interpretation
- Periodization
- Materials used
- Structural elements
- Structure relationships
- Measurements and elevations

### Finds Form

- Site, Inventory number
- Find type, Definition
- Description
- Provenance (Area, SU)
- Conservation status
- Dating
- Elements and measurements
- Bibliography

### Grave Form

- Identification data
- Rite (inhumation/cremation)
- Burial and deposition type
- Description and interpretation
- Grave goods (presence, type, description)
- Periodization
- Structure and individual elevations
- Associated SU

### Sample Form

- Site, Sample number
- Sample type
- Description
- Provenance (Area, SU)
- Storage location
- Box number

### Individual Form

- Identification data
- Sex, Age (min/max), Age classes
- Skeleton position
- Orientation (axis, azimuth)
- Conservation status
- Observations

## Supported Languages

System generates reports based on system language:

| Language | Code | Template |
|----------|------|----------|
| Italian | IT | `build_*_sheets()` |
| German | DE | `build_*_sheets_de()` |
| English | EN | `build_*_sheets_en()` |

Language is automatically detected from QGIS settings.

## Output Folder

### Standard Path
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Generated File Structure

```
pyarchinit_PDF_folder/
├── US_[site]_forms.pdf           # Complete SU forms
├── US_[site]_index.pdf           # SU index
├── Periodization_[site].pdf      # Periodization forms
├── Structure_[site]_forms.pdf    # Structure forms
├── Structure_[site]_index.pdf    # Structure index
├── Finds_[site]_forms.pdf        # Finds forms
├── Finds_[site]_index.pdf        # Finds index
├── Grave_[site]_forms.pdf        # Grave forms
├── Sample_[site]_forms.pdf       # Sample forms
├── Individual_[site]_forms.pdf   # Individual forms
└── ...
```

### Open Folder

The **"Open Folder"** button directly opens the output directory in the system file manager.

## Report Customization

### PDF Templates

Templates are defined in modules:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Library Used

PDFs are generated with **ReportLab**, which allows:
- Customizable layouts
- Image insertion
- Formatted tables
- Headers/footers

### Required Fonts

System uses specific fonts:
- **Cambria** (main font)
- Automatic installation at first plugin startup

## Recommended Workflow

### 1. Data Preparation

```
1. Complete all site forms
2. Verify data completeness
3. Check periodization
4. Verify stratigraphic relationships
```

### 2. Export

```
1. Open Export PDF
2. Select site
3. Select form types
4. Click "Export PDF"
5. Wait for completion
```

### 3. Verification

```
1. Open output folder
2. Check generated PDFs
3. Verify formatting
4. Print or archive
```

## Troubleshooting

### Error: "No form to print"

**Cause**: No records found for selected type

**Solution**:
- Verify data exists for selected site
- Check database

### Empty or Incomplete PDFs

**Possible causes**:
1. Required fields not filled
2. Character encoding problems
3. Missing fonts

**Solutions**:
- Complete required fields
- Verify Cambria font installation

### Font Error

**Cause**: Cambria font not installed

**Solution**:
- Plugin attempts automatic installation
- If problems, install manually

### Slow Export

**Cause**: Many records to export

**Solution**:
- Export by type separately
- Wait for completion

## Best Practices

### 1. Organization

- Export regularly during excavation
- Create backups of generated PDFs
- Organize by campaign/year

### 2. Data Completeness

- Fill all fields before export
- Verify elevations from GIS measurements
- Check stratigraphic relationships

### 3. Archiving

- Save PDFs on secure storage
- Include in final documentation
- Attach to excavation report

### 4. Printing

- Use acid-free paper for archiving
- Print in A4 format
- Bind by campaign

## Integration with Other Functions

### Elevations from GIS

System automatically retrieves:
- Minimum and maximum elevations from geometries
- References to GIS plans

### Photographic Documentation

Reports can include references to:
- Linked photographs
- Drawings and surveys

### Periodization

SU reports automatically include:
- Extended dating from assigned period/phase
- Chronological references

## References

### Source Files
- `tabs/Pdf_export.py` - Export interface
- `modules/utility/pyarchinit_exp_*_pdf.py` - PDF generators

### Dependencies
- ReportLab (PDF generation)
- Cambria font

---

## Video Tutorial

### Complete PDF Export
`[Placeholder: video_export_pdf.mp4]`

**Contents**:
- Site and form selection
- Export process
- Output verification
- Archive organization

**Expected duration**: 10-12 minutes

---

*Last updated: January 2026*
