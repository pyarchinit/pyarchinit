# Tutorial 28: GeoPackage Export

## Introduction

The **GeoPackage Export** function allows packaging PyArchInit vector and raster layers into a single GeoPackage file (.gpkg). This format is ideal for sharing, archiving, and data portability.

### GeoPackage Advantages

| Aspect | Advantage |
|--------|-----------|
| Single file | All data in one file |
| Portability | Easy sharing |
| OGC standard | Universal compatibility |
| Multi-layer | Vectors and rasters together |
| SQLite-based | Lightweight and fast |

## Access

### From Menu
**PyArchInit** → **Package for GeoPackage**

## Interface

### Export Panel

```
+--------------------------------------------------+
|        Import to GeoPackage                       |
+--------------------------------------------------+
| Destination:                                      |
|   [____________________________] [Browse]        |
+--------------------------------------------------+
| [Export Vector Layers]                           |
| [Export Raster Layers]                           |
+--------------------------------------------------+
```

## Procedure

### Vector Layer Export

1. Select layers to export in QGIS Layer panel
2. Open GeoPackage Export tool
3. Specify destination path and file name
4. Click **"Export Vector Layers"**

### Raster Layer Export

1. Select raster layers in Layer panel
2. Specify destination (same file or new)
3. Click **"Export Raster Layers"**

### Combined Export

To include vectors and rasters in the same GeoPackage:
1. First export vectors
2. Then export rasters to same file
3. System adds layers to existing GeoPackage

## Layer Selection

### Method

1. In QGIS Layer panel, select desired layers
   - Ctrl+click for multiple selection
   - Shift+click for range
2. Open GeoPackage Export
3. Selected layers will be exported

### Recommended Layers

| Layer | Type | Notes |
|-------|------|-------|
| pyunitastratigrafiche | Vector | Deposit SU |
| pyunitastratigrafiche_usm | Vector | Wall SU |
| pyarchinit_quote | Vector | Elevation points |
| pyarchinit_siti | Vector | Sites |
| Orthophoto | Raster | Excavation orthophoto |

## Output

### GeoPackage Structure

```
output.gpkg
├── pyunitastratigrafiche (vector)
├── pyunitastratigrafiche_usm (vector)
├── pyarchinit_quote (vector)
└── ortofoto (raster)
```

### Default Path

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Export Options

### Vector Layers

- Maintains original geometries
- Preserves all attributes
- Automatically converts names with spaces (uses underscore)

### Raster Layers

- Supports common formats (GeoTIFF, etc.)
- Maintains georeferencing
- Preserves coordinate reference system

## Typical Uses

### Project Sharing

```
1. Select all project layers
2. Export to GeoPackage
3. Share the .gpkg file
4. Recipient opens directly in QGIS
```

### Campaign Archiving

```
1. At campaign end, select final layers
2. Export to dated GeoPackage
3. Archive with documentation
```

### GIS Backup

```
1. Periodically export current state
2. Maintain dated versions
3. Use for disaster recovery
```

## Best Practices

### 1. Before Export

- Verify layer completeness
- Check coordinate reference system
- Save QGIS project

### 2. Naming

- Use descriptive file names
- Include date in name
- Avoid special characters

### 3. Verification

- Open created GeoPackage
- Verify all layers present
- Check attributes

## Troubleshooting

### Export Failed

**Causes**:
- Invalid layer
- Path not writable
- Insufficient disk space

**Solutions**:
- Verify layer validity
- Check folder permissions
- Free disk space

### Missing Layers

**Cause**: Layer not selected

**Solution**: Verify selection in Layer panel

### Raster Not Exported

**Causes**:
- Unsupported format
- Source file not accessible

**Solutions**:
- Convert raster to GeoTIFF
- Verify source file path

## References

### Source Files
- `tabs/gpkg_export.py` - Export interface
- `gui/ui/gpkg_export.ui` - UI layout

### Documentation
- [GeoPackage Standard](https://www.geopackage.org/)
- [QGIS GeoPackage Support](https://docs.qgis.org/)

---

## Video Tutorial

### GeoPackage Export
`[Placeholder: video_geopackage.mp4]`

**Contents**:
- Layer selection
- Vector and raster export
- Output verification
- Best practices

**Expected duration**: 8-10 minutes

---

*Last updated: January 2026*
