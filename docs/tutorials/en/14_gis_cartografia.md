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

### Style Choice (SU and USM)

When the SUs or wall SUs (USM) of the search results are loaded on the map, the **Style Choice** window appears ("How do you want to manage the layer style?"):

| Button | Effect |
|--------|--------|
| **Save new style** | Builds the style from the chosen field and saves it in the database under a name |
| **Load existing style** | Uses a ready-made style, chosen from a list (see below), as a template and builds the style from the chosen field without saving it in the database |
| **Use temporary style** | Builds the style from the chosen field without saving it in the database |
| **Single symbol (outline only)** | Draws only the outline of the geometries, with no fill |

Since 5.13.19-alpha **Load existing style** opens the **Existing style** window ("Choose the style to use as a template:") listing the available styles: the styles saved in the database (*Database: name*), the QML styles shipped with pyArchInit (`us_*.qml`, listed as *pyArchInit: …*) and **Other QML file…**, to pick any `.qml` file. The chosen style is loaded on the layer (labels, transparency and blending come with it) and acts as a **template**: after you choose the categorization field, the values the style already has keep its color and symbol, the others get a copy of its symbol with their own color. If you cancel the choice, it works like **Use temporary style**. Previously it only looked among the styles in the database and, finding none, went straight to the categorization window.

With **Save new style**, **Load existing style** and **Use temporary style** you then choose the categorization field (**Select Categorization Field** window): **Stratigraphic Definition**, **SU Type**, **Interpretive Definition** or **Period/Phase (cont_per)** (since 5.13.19-alpha); each value of the field gets its own color, which since 5.13.19-alpha stays the same every time the layer is loaded. With **Period/Phase (cont_per)** the legend entry of each code also shows the dating of the period/phase taken from the periodization. Only the fields present in the layer are listed.

**Drawing order.** Since 5.13.19-alpha the units are drawn in the order used by the Time Manager: first those without a period, then by period chronology (from the periodization of the SU's initial period/phase, or from `cont_per`), then by `order_layer` (0 = oldest), and finally the cut over its fill, so the most recent units are on top. This applies to every style option, including **Single symbol (outline only)**. When the layers are loaded period by period, the style is asked only once and used for all periods.

Since 5.13.18-alpha the chosen style (and the categorization field) is also respected with SQLite databases, for both SUs and USMs; previously the map always came out with one color per SU.

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

### Layer Loaded but Geometries Not Visible (SQLite)

**Symptom**:
- A pyArchInit layer of a SQLite/SpatiaLite database (e.g. SU `pyunitastratigrafiche`, masonry SU, finds, negative SU) loads and its attribute table shows the records, but nothing is drawn on the map and "Zoom to Layer" does not work

**Cause**:
- The layer's spatial index (R*Tree) was not maintained: its triggers were lost when a table was recreated (e.g. by older schema-update scripts) or data were imported bypassing them
- QGIS picks the features to draw through that index, so they stay invisible
- Databases created from the SQLite template between October 2025 and September 2026 were affected too

**Solution (automatic)**:
- When pyArchInit connects to a SQLite database it checks every spatial index (a few instants; nothing is written if the database is healthy) and automatically rebuilds any broken one
- Since version 5.13.16-alpha the same check also repairs the **spatial views** (`pyarchinit_us_view`, `pyarchinit_quote_view`, structures, finds, the UT views, etc.):
  - each view is keyed on the ROWID of its geometry table
  - registrations of views that no longer exist are removed
  - missing standard views are recreated
  - the UT views are registered as spatial views
  - geometry tables without a spatial index get one: this is needed when the GDAL bundled with QGIS lacks the SpatiaLite functions (e.g. QGIS on macOS), where without an index those layers drew nothing
- Before changing anything it saves ONE backup copy next to the database: `<database>.sqlite.pre_spatial_index_repair_<UTC date-time>`
- The result is written in the QGIS log panel (View → Panels → Log Messages, "PyArchInit" tab)

**What to do**:
- Nothing to start by hand: the check runs automatically at the FIRST connection to each database in every QGIS session (so after updating the plugin or after restarting QGIS)
- If the layers were already loaded, remove and re-add them (or reopen the project) after the repair
- If the "PyArchInit" log reports that an index could NOT be repaired (e.g. SpatiaLite could not be loaded), fix the cause and restart QGIS: the check runs again only in a new session
- The backup file can be deleted once the layers have been verified
- To run the check again (e.g. after restoring a backup), restart QGIS
- Note: in `inventario_materiali_view` the site point is repeated for every find, so "Identify" on that point shows one of the finds

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

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/pyarchinit_image_classification_animation.html)
