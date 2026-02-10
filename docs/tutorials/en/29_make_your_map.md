# Tutorial 29: Make Your Map

## Introduction

**Make Your Map** is PyArchInit's function for generating professional maps and print layouts directly from the current QGIS view. It uses predefined layout templates to create standardized cartographic outputs.

### Features

- Rapid map generation from current view
- Predefined templates for various formats
- Header and legend customization
- Export to PDF, PNG, SVG

## Access

### From Toolbar
**"Make your Map"** icon (printer) in PyArchInit toolbar

### From Menu
**PyArchInit** → **Make your Map**

## Basic Usage

### Quick Generation

1. Configure desired map view in QGIS
2. Set correct zoom and extent
3. Click **"Make your Map"**
4. Select desired template
5. Enter title and information
6. Generate map

## Available Templates

### Standard Formats

| Template | Format | Orientation | Usage |
|----------|--------|-------------|-------|
| A4 Portrait | A4 | Portrait | Standard documentation |
| A4 Landscape | A4 | Landscape | Extended views |
| A3 Portrait | A3 | Portrait | Detailed plates |
| A3 Landscape | A3 | Landscape | Planimetries |

### Template Elements

Each template includes:
- **Map area** - Main view
- **Header** - Title and project information
- **Scale** - Graphic scale bar
- **North** - North arrow
- **Legend** - Layer symbols
- **Title block** - Technical information

## Customization

### Editable Information

| Field | Description |
|-------|-------------|
| Title | Map name |
| Subtitle | Additional description |
| Site | Archaeological site name |
| Area | Area number |
| Date | Creation date |
| Author | Author name |
| Scale | Representation scale |

### Map Style

Before generating:
1. Configure layer styles in QGIS
2. Enable/disable desired layers
3. Set labels
4. Verify legend

## Export

### Available Formats

| Format | Usage | Quality |
|--------|-------|---------|
| PDF | Print, archive | Vector |
| PNG | Web, presentations | Raster |
| SVG | Editing, publication | Vector |
| JPG | Web, preview | Compressed raster |

### Resolution

| DPI | Usage |
|-----|-------|
| 96 | Screen/preview |
| 150 | Web publishing |
| 300 | Standard print |
| 600 | High quality print |

## Time Manager Integration

### Sequence Generation

In combination with Time Manager:
1. Configure Time Manager
2. For each stratigraphic level:
   - Set level
   - Generate map
   - Save with progressive name

### Animation Output

Series of maps for:
- Presentations
- Time-lapse videos
- Progressive documentation

## Typical Workflow

### 1. Preparation

```
1. Load necessary layers
2. Configure appropriate styles
3. Set coordinate reference system
4. Define map extent
```

### 2. View Configuration

```
1. Zoom to area of interest
2. Enable/disable layers
3. Verify labels
4. Check legend
```

### 3. Generation

```
1. Click Make your Map
2. Select template
3. Fill in information
4. Choose export format
5. Save
```

## Best Practices

### 1. Before Generation

- Verify data completeness
- Check layer styles
- Set appropriate scale

### 2. Templates

- Use consistent templates in project
- Customize headers for institution
- Maintain cartographic standards

### 3. Output

- Save in high resolution for print
- Maintain PDF copy for archive
- Use descriptive naming

## Template Customization

### Template Modification

QGIS templates can be modified:
1. Open Layout Manager in QGIS
2. Modify existing template
3. Save as new template
4. Available in Make your Map

### Template Creation

1. Create new layout in QGIS
2. Add necessary elements
3. Configure variables for dynamic fields
4. Save in templates folder

## Troubleshooting

### Empty Map

**Causes**:
- No active layer
- Wrong extent

**Solutions**:
- Enable visible layers
- Zoom to area with data

### Incomplete Legend

**Cause**: Layers not correctly configured

**Solution**: Verify layer properties in QGIS

### Export Failed

**Causes**:
- Path not writable
- Unsupported format

**Solutions**:
- Verify folder permissions
- Choose different format

## References

### Source Files
- `pyarchinitPlugin.py` - runPrint function
- Templates in `resources/templates/` folder

### QGIS
- Layout Manager
- Print Composer

---

## Video Tutorial

### Make Your Map
`[Placeholder: video_make_map.mp4]`

**Contents**:
- View preparation
- Template usage
- Customization
- Export formats

**Expected duration**: 10-12 minutes

---

*Last updated: January 2026*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../animations/pyarchinit_create_map_animation.html)
