# Tutorial 27: TOPS - Total Open Station

## Introduction

**TOPS** (Total Open Station) is PyArchInit's integration with open source software for downloading and converting data from total stations. It allows direct import of topographic surveys into the PyArchInit system.

### What is Total Open Station?

Total Open Station is free software for:
- Downloading data from total stations
- Format conversion
- Export to GIS-compatible formats

PyArchInit integrates TOPS to simplify excavation data import.

## Access

### From Menu
**PyArchInit** → **TOPS (Total Open Station)**

## Interface

### Main Panel

```
+--------------------------------------------------+
|         Total Open Station to PyArchInit          |
+--------------------------------------------------+
| Input:                                            |
|   File: [___________________] [Browse]           |
|   Input format: [ComboBox formats]               |
+--------------------------------------------------+
| Output:                                           |
|   File: [___________________] [Browse]           |
|   Output format: [csv | dxf | ...]               |
+--------------------------------------------------+
| [ ] Convert coordinates                          |
+--------------------------------------------------+
| [Data Preview - TableView]                       |
+--------------------------------------------------+
|              [Export]                             |
+--------------------------------------------------+
```

## Supported Formats

### Input Formats (Total Stations)

| Format | Manufacturer | Extension |
|--------|--------------|-----------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| Generic CSV | - | .csv |

### Output Formats

| Format | Usage |
|--------|-------|
| CSV | Import to PyArchInit Elevations |
| DXF | Import to CAD/GIS |
| GeoJSON | Direct GIS import |
| Shapefile | GIS standard |

## Workflow

### 1. Import Data from Total Station

```
1. Connect total station to PC
2. Download data file (native format)
3. Save in working folder
```

### 2. Conversion with TOPS

```
1. Open TOPS in PyArchInit
2. Select input file (Browse)
3. Choose correct input format
4. Set output file
5. Choose output format (CSV recommended)
6. Click Export
```

### 3. Import to PyArchInit

After CSV export:
1. The system automatically asks for:
   - Archaeological **site name**
   - **Unit of measurement** (meters)
   - **Surveyor name**
2. Points are loaded as QGIS layer
3. Optional: copy to SU Elevations layer

### 4. Coordinate Conversion (Optional)

If **"Convert coordinates"** checkbox active:
- Enter X, Y, Z offset
- Apply coordinate translation
- Useful for local reference systems

## Data Preview

### TableView

Shows preview of imported data:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Data Editing

- Select rows to delete
- **Delete** button removes selected rows
- Useful for filtering unnecessary points

## SU Elevations Integration

### Automatic Copy

After import, TOPS can copy points to **"SU Elevation Drawing"** layer:
1. Site name is requested
2. Unit of measurement is requested
3. Surveyor is requested
4. Points are copied with correct attributes

### Filled Attributes

| Attribute | Value |
|-----------|-------|
| sito_q | Entered site name |
| area_q | Extracted from point_name |
| unita_misu_q | Entered unit (meters) |
| disegnatore | Entered name |
| data | Current date |

## Naming Conventions

### point_name Format

For automatic area extraction:
```
[AREA]-[POINT_NAME]
Example: 1000-P001
```

The system automatically separates:
- `area_q` = 1000
- `point_name` = P001

## Best Practices

### 1. In the Field

- Use consistent naming for points
- Include area code in point name
- Note reference system used

### 2. Import

- Verify correct input format
- Check preview before export
- Delete erroneous/duplicate points

### 3. Post-Import

- Verify coordinates in QGIS
- Check SU Elevations layer
- Link points to correct SU

## Troubleshooting

### Format Not Recognized

**Cause**: Station format not supported

**Solution**:
- Export from station in generic format (CSV)
- Check station documentation

### Wrong Coordinates

**Causes**:
- Different reference system
- Offset not applied

**Solutions**:
- Verify project reference system
- Apply coordinate conversion

### Layer Not Created

**Cause**: Error during import

**Solution**:
- Check error log
- Verify output file format
- Repeat conversion

## References

### Source Files
- `tabs/tops_pyarchinit.py` - Main interface
- `gui/ui/Tops2pyarchinit.ui` - UI layout

### External Software
- [Total Open Station](https://tops.iosa.it/) - Main software
- Station format documentation

---

## Video Tutorial

### TOPS Import
`[Placeholder: video_tops.mp4]`

**Contents**:
- Download from total station
- Format conversion
- Import to PyArchInit
- SU Elevations integration

**Expected duration**: 12-15 minutes

---

*Last updated: January 2026*
