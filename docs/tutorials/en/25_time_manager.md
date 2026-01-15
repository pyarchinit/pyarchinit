# Tutorial 25: Time Manager (GIS Time Controller)

## Introduction

The **Time Manager** (GIS Time Controller) is an advanced tool for visualizing stratigraphic sequence over time. It allows "navigating" through stratigraphic levels using a temporal control, progressively displaying SU from most recent to oldest.

### Main Features

- Progressive visualization of stratigraphic levels
- Control via dial/slider
- Cumulative or single level mode
- Automatic image/video generation
- Integration with Harris Matrix

## Access

### From Menu
**PyArchInit** → **Time Manager**

### Prerequisites

- Layer with `order_layer` field (stratigraphic index)
- SU with order_layer filled in
- Layers loaded in QGIS

## Interface

### Main Panel

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Available layers:                                 |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] other_layer                                  |
+--------------------------------------------------+
|              [Circular Dial]                     |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Level: [SpinBox: 1-N]                   |
+--------------------------------------------------+
| [x] Cumulative Mode (show <= level)             |
+--------------------------------------------------+
| [ ] Show Matrix          [Stop] [Generate Video] |
+--------------------------------------------------+
| [Matrix/Image Preview]                           |
+--------------------------------------------------+
```

### Controls

| Control | Function |
|---------|----------|
| Layer Checkbox | Select layers to control |
| Dial | Navigate between levels (rotation) |
| SpinBox | Direct level input |
| Cumulative Mode | Show all levels up to selected |
| Show Matrix | Display synchronized Harris Matrix |

## order_layer Field

### What is order_layer?

The `order_layer` field defines the stratigraphic display order:
- **1** = Most recent level (surface)
- **N** = Oldest level (deep)

### Filling order_layer

In the SU Form, **"Stratigraphic Index"** field:
1. Assign increasing values from surface
2. Contemporary SU can have the same value
3. Follow the Matrix sequence

### Example

| SU | order_layer | Description |
|----|-------------|-------------|
| SU001 | 1 | Surface humus |
| SU002 | 2 | Plowed layer |
| SU003 | 3 | Collapse |
| SU004 | 4 | Use floor |
| SU005 | 5 | Foundation |

## Visualization Modes

### Single Level Mode

Checkbox **NOT** active:
- Shows ONLY SU of selected level
- Useful for isolating single layers
- "Slice" visualization

### Cumulative Mode

Checkbox **ACTIVE**:
- Shows all SU up to selected level
- Simulates progressive excavation
- More realistic visualization

## Matrix Integration

### Synchronized Visualization

With **"Show Matrix"** checkbox active:
- Harris Matrix appears in panel
- Updates in sync with level
- Highlights current level SU

### Image Generation

Time Manager can generate:
- Screenshot for each level
- Image sequence
- Time-lapse video

## Video/Image Generation

### Process

1. Select layers to include
2. Configure level range (min-max)
3. Click **"Generate Video"**
4. Wait for processing
5. Output in designated folder

### Output

- PNG images for each level
- Optional: compiled MP4 video

## Typical Workflow

### 1. Preparation

```
1. Open QGIS project with SU layers
2. Verify order_layer is filled in
3. Open Time Manager
```

### 2. Layer Selection

```
1. Select layers to control
2. Usually: pyunitastratigrafiche and/or _usm
```

### 3. Navigation

```
1. Use dial or spinbox
2. Observe visualization change
3. Enable/disable cumulative mode
```

### 4. Documentation

```
1. Enable "Show Matrix"
2. Generate significant screenshots
3. Optional: generate video
```

## Layout Templates

### Template Loading

Time Manager supports QGIS templates for:
- Custom print layouts
- Headers and legends
- Standard formats

### Available Templates

In `resources/templates/` folder:
- Base template
- Template with Matrix
- Template for video

## Best Practices

### 1. order_layer

- Fill in BEFORE using Time Manager
- Use consecutive values
- Contemporary SU = same value

### 2. Visualization

- Start from level 1 (surface)
- Proceed in ascending order
- Use cumulative mode for presentations

### 3. Documentation

- Capture screenshots at significant levels
- Document phase transitions
- Generate video for reports

## Troubleshooting

### Layers Not Visible in List

**Cause**: Layer without order_layer field

**Solution**:
- Add order_layer field to layer
- Populate with appropriate values

### No Visual Change

**Causes**:
- order_layer not filled in
- Filter not applied

**Solutions**:
- Verify order_layer values in SU
- Check that layer is selected

### Dial Not Responding

**Cause**: No layer selected

**Solution**: Select at least one layer from list

## References

### Source Files
- `tabs/Gis_Time_controller.py` - Main interface
- `gui/ui/Gis_Time_controller.ui` - UI layout

### Database Field
- `us_table.order_layer` - Stratigraphic index

---

## Video Tutorial

### Time Manager
`[Placeholder: video_time_manager.mp4]`

**Contents**:
- order_layer configuration
- Temporal navigation
- Video generation
- Matrix integration

**Expected duration**: 15-18 minutes

---

*Last updated: January 2026*
