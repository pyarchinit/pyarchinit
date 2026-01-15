# Tutorial 14: GIS and Cartography

## Introduction

PyArchInit is deeply integrated with **QGIS**, leveraging all its GIS functionalities for spatial management of archaeological data. This tutorial covers cartographic integration, predefined layers, and advanced features like **SAM automatic segmentation**.

### Main GIS Features

- SU visualization on map
- Predefined vector layers
- Custom QML styling
- GIS elevations and measurements
- Automatic segmentation (SAM)
- Cartographic export

## Predefined PyArchInit Layers

### Main Vector Layers

| Layer | Geometry | Description |
|-------|----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | Deposit SU |
| `pyunitastratigrafiche_usm` | MultiPolygon | Wall SU |
| `pyarchinit_quote` | Point | Elevation points |
| `pyarchinit_siti` | Point | Site locations |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Excavation areas |
| `pyarchinit_strutture_ipotesi` | Polygon | Hypothetical structures |
| `pyarchinit_documentazione` | Point | Documentation references |

### SU Layer Attributes

| Field | Type | Description |
|-------|------|-------------|
| `gid` | Integer | Unique ID |
| `scavo_s` | Text | Site name |
| `area_s` | Text | Area number |
| `us_s` | Text | SU number |
| `stratigraph_index_us` | Integer | Stratigraphic index |
| `tipo_us_s` | Text | SU type |
| `rilievo_originale` | Text | Original survey |
| `disegnatore` | Text | Survey author |
| `data` | Date | Survey date |

## SU Map Visualization

### From "Map" Tab in SU Form

1. Open an SU form
2. Select the **Map** tab
3. Available functions:

| Button | Function |
|--------|----------|
| View US | Display current SU on map |
| View All | Display all SUs in area |
| New Record | Create new geometry |
| Pan to | Center map on SU |

### Visualization from Search

1. Execute an SU search
2. **"View Record"** button → display single
3. **"View All"** button → display all results

## Layer Styling

### QML Files

PyArchInit includes predefined styles in QML format:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Style Application

1. Select the layer in legend
2. Right-click → **Properties**
3. **Style** tab
4. **Load style** → select QML

### Customization

Styles can be customized for:
- Colors based on SU type
- Labels with SU number
- Transparency
- Borders and fills

## Elevations and Measurements

### Elevation Layer

The `pyarchinit_quote` layer stores:
- X, Y coordinates
- Z elevation (absolute)
- Elevation point type
- Reference SU
- Reference area

### Automatic Elevation Calculation

From the SU Form, min/max elevations are calculated:
1. Query elevation points associated with SU
2. Extract minimum and maximum value
3. Display in report

### Elevation Entry

1. Elevation layer in editing mode
2. Draw point on map
3. Fill in attributes:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## SAM Automatic Segmentation

### What is SAM?

**SAM (Segment Anything Model)** is an artificial intelligence model developed by Meta for automatic image segmentation. PyArchInit integrates it for:
- Automatic digitization of stones/elements
- Orthophoto segmentation
- Survey acceleration

### Accessing the Function

1. **PyArchInit** → **SAM Segmentation**
2. Or from toolbar: **SAM** icon

### SAM Interface

```
+--------------------------------------------------+
|        SAM Stone Segmentation                     |
+--------------------------------------------------+
| Input:                                            |
|   Raster Layer: [ComboBox orthophoto]            |
+--------------------------------------------------+
| Target Layer:                                     |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Default Attributes:                               |
|   Site (sito): [automatic field]                 |
|   Area: [area input]                             |
|   Stratigraphic Index: [1-10]                    |
|   Type US: [stone|layer|accumulation|cut]        |
+--------------------------------------------------+
| Segmentation Mode:                                |
|   [o] Automatic (detect all stones)              |
|   [ ] Click mode (click on each stone)           |
|   [ ] Box mode (draw rectangle)                  |
|   [ ] Polygon mode (draw freehand)               |
|   [ ] From layer (use existing polygon)          |
+--------------------------------------------------+
| Model:                                            |
|   [ComboBox model]                               |
|   API Key: [******]                              |
+--------------------------------------------------+
|        [Start Segmentation]  [Cancel]             |
+--------------------------------------------------+
```

### Segmentation Modes

#### 1. Automatic Mode
- Automatically segments all visible objects
- Ideal for areas with many stones
- Requires good quality orthophoto

#### 2. Click Mode
- Click on each object to segment
- Right-click or Enter to finish
- Escape to cancel
- More precise for specific objects

#### 3. Box Mode
- Draw rectangle on area
- Segments only selected area
- Useful for delimited zones

#### 4. Polygon Mode
- Draw freehand polygon
- Click to add vertices
- Right-click to complete
- For irregular areas

#### 5. From Layer Mode
- Use existing polygon as mask
- Select polygon layer
- Segments only within polygon

### Available Models

| Model | Type | Requirements | Quality |
|-------|------|--------------|---------|
| Replicate SAM-2 | Cloud API | API Key | Excellent |
| Roboflow SAM-3 | Cloud API | API Key | Excellent + Text Prompt |
| SAM vit_b | Local | 375MB VRAM | Good |
| SAM vit_l | Local | 1.2GB VRAM | Very good |
| SAM vit_h | Local | 2.5GB VRAM | Excellent |
| OpenCV | Local | None | Basic |

### SAM-3 with Text Prompt

SAM-3 version (Roboflow) supports **text prompts**:
- "stones" - stones
- "pottery fragments" - pottery fragments
- "bones" - bones
- Any text description

### API Configuration

#### Replicate API (SAM-2)
1. Register at [replicate.com](https://replicate.com)
2. Get API key
3. Enter in configuration

#### Roboflow API (SAM-3)
1. Register at [roboflow.com](https://roboflow.com)
2. Get API key
3. Enter in configuration

### Local SAM Installation

For local use without API:
```bash
# Create virtual environment
cd ~/pyarchinit/bin
python -m venv sam_venv

# Activate environment
source sam_venv/bin/activate

# Install dependencies
pip install segment-anything torch torchvision

# Download models (optional)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### SAM Workflow

1. **Preparation**
   - Load orthophoto as raster layer
   - Verify coordinate reference system
   - Prepare target layer

2. **Configuration**
   - Select input raster
   - Set default attributes
   - Choose mode and model

3. **Execution**
   - Click "Start Segmentation"
   - Wait for processing
   - Verify results

4. **Post-processing**
   - Check generated polygons
   - Assign SU numbers
   - Correct any errors

## Cartographic Integration

### GIS Data Export

From SU Form, Map tab:
- **Export GeoPackage**: Layer as GPKG
- **Export Shapefile**: Layer as SHP
- **Export GeoJSON**: Layer as JSON

### GIS Data Import

Import existing geometries:
1. Load layer in QGIS
2. Select features
3. Use import function

### Geoprocessing

Available spatial operations:
- Buffer
- Intersection
- Union
- Difference
- Centroids

## Best Practices

### 1. Orthophotos

- Minimum resolution: 1-2 cm/pixel
- Format: Georeferenced GeoTIFF
- Reference system: consistent with project

### 2. Digitization

- Use snap for precision
- Verify topology
- Maintain attribute consistency

### 3. SAM Segmentation

- High quality orthophoto
- Uniform lighting
- Adequate object/background contrast
- Post-verification always necessary

### 4. Layer Organization

- Group by type
- Use consistent styles
- Maintain order in legend

## Troubleshooting

### Layers Not Displayed

**Possible causes**:
- Wrong extent
- Different reference system
- Active filter

**Solutions**:
- Zoom to Layer
- Verify CRS
- Remove filters

### SAM Not Working

**Possible causes**:
- Invalid API key
- Raster not georeferenced
- Local model not installed

**Solutions**:
- Verify API key
- Check georeferencing
- Install model

### Corrupted Geometries

**Possible causes**:
- Digitization errors
- Problematic import

**Solutions**:
- Use "Fix Geometries"
- Redraw element

## References

### Source Files
- `modules/gis/pyarchinit_pyqgis.py` - GIS Integration
- `tabs/Sam_Segmentation_Dialog.py` - SAM Dialog
- `modules/gis/sam_map_tools.py` - SAM Map Tools

### Layers
- `pyunitastratigrafiche` - Deposit SU
- `pyunitastratigrafiche_usm` - Wall SU
- `pyarchinit_quote` - Elevations

---

## Video Tutorial

### GIS Integration
`[Placeholder: video_gis_integration.mp4]`

**Contents**:
- Predefined layers
- SU visualization
- Styling and labels
- Cartographic export

**Expected duration**: 15-18 minutes

### SAM Segmentation
`[Placeholder: video_sam_segmentation.mp4]`

**Contents**:
- SAM configuration
- Segmentation modes
- Post-processing
- Best practices

**Expected duration**: 12-15 minutes

---

*Last updated: January 2026*
