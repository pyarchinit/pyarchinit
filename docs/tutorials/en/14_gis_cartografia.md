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

Since 5.13.19-alpha **Load existing style** opens the **Existing style** window ("Choose the style to use as a template:") listing the available styles: the styles saved in the database (*Database: name*), the QML styles shipped with pyArchInit (`us_*.qml`, listed as *pyArchInit: …*) and **Other QML file…**, to pick any `.qml` file. The chosen style is loaded on the layer (transparency and blending come with it; the labels do not: on the polygon SU and USM views they are, since 5.13.110-alpha, those of the **Labels** paragraph below, the circled unit number, whatever the template style says) and acts as a **template**: after you choose the categorization field, the values the style already has keep its color and symbol, the others get a copy of its symbol with their own color. If you cancel the choice, it works like **Use temporary style**. Previously it only looked among the styles in the database and, finding none, went straight to the categorization window.

With **Save new style**, **Load existing style** and **Use temporary style** you then choose the categorization field (**Select Categorization Field** window): **Stratigraphic Definition**, **SU Type**, **Interpretive Definition** or **Period/Phase (cont_per)** (since 5.13.19-alpha); each value of the field gets its own color, which since 5.13.19-alpha stays the same every time the layer is loaded. With **Period/Phase (cont_per)** the legend entry of each code also shows the dating of the period/phase taken from the periodization. Only the fields present in the layer are listed.

**Drawing order.** Since 5.13.19-alpha the units are drawn in the order used by the Time Manager: first those without a period, then by period chronology (from the periodization of the SU's initial period/phase, or from `cont_per`), then by `order_layer` (0 = oldest), and finally the cut over its fill, so the most recent units are on top. This applies to every style option, including **Single symbol (outline only)**. When the layers are loaded period by period, the style is asked only once and used for all periods.

**Labels.** Since 5.13.110-alpha, with the chosen style the SU (and USM) view also receives its **labels**: the unit number in **bold inside a white circle with a dark red border**, **one per unit**, on its largest drawing if that one shows (not entirely covered by one of a higher level), with the same recipe as the Time Manager atlas sheets (tutorial 25). When two numbers would overlap, one is moved and a leader line links it to its drawing. This applies to SUs and USMs, with SQLite and PostgreSQL, and to every style option, including **Single symbol (outline only)**; if the style loaded with **Load existing style** already had labels, the circled number takes their place. Point layers, such as the elevations, get no labels from here.

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

**SAM (Segment Anything Model)** is Meta's artificial intelligence model that splits an image into its objects. In pyArchInit the SAM window turns an image into **polygons**, starting from:

- an **orthophoto** (a raster file: GeoTIFF, georeferenced JPEG…);
- or a **tile layer or service** loaded in QGIS: XYZ such as ESRI World Imagery or Google, WMS, ArcGIS REST.

Not only stones: also **buildings, roads, fields, rivers, walls**. The models come in two families:

- **SAM 2.1** (Meta) finds the outlines of objects — all of them, or the ones you point at with points, a box or a polygon — but does not say what they are;
- **text classes** (YOLOE-26 locally, SAM 3 in the cloud) look for the things you type («building, road, river, field») and every polygon carries its label.

The polygons go into the layer you choose: pyArchInit's SU layers, any polygon layer of the project, or a new temporary layer.

### Accessing the Function

1. From the pyArchInit toolbar: the **Analysis Tools** dropdown button → «SAM - Segmentation (stones, buildings, roads, fields…)». It is the button's default action: clicking the icon opens the window straight away.
2. Or from the **pyArchInit** menu → «SAM - Segmentation (stones, buildings, roads, fields…)».

The window is titled «SAM — Segmentation (stones, buildings, roads, fields, rivers…)». Its labels are in Italian when QGIS is in Italian and in English with every other language.

### SAM Interface

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Five groups, to be filled in from top to bottom: «Local environment», «Image», «What to segment», «Model», «Target». Below them come the status line («Ready»), where the messages of the running job also appear, and the buttons «Start», «Cancel» (visible only while working) and «Close». Some rows appear only when needed: «API key:» in place of the weights status for cloud models; «Site:», «Area:», «Stratigraphic index:» and «US type:» for SU layers; «Field for the label:» for other layers. The window remembers the last SU area, the classes, the max side, the chosen model and the API keys.

The entries of the model list are always written in Italian («Locale» = local), and so are a few service messages quoted below.

#### Local environment

The local models (SAM 2.1 and YOLOE) do not run in QGIS's Python but in a **separate Python**, which the window creates and checks by itself. When the window opens the group reads «checking…», then:

- in green «ready — ultralytics …, torch …, mps»: the environment is there; the last word is the compute device (`mps`, `cuda` or `cpu`);
- in orange «not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.».

«Install / update» creates the environment or updates its packages (see «Local SAM Installation» below); «Show log» opens and closes the installation log, with pip's output line by line. Cloud models do not need the environment.

#### Image

- «Raster layer:» the image to segment, chosen among the project's rasters: an orthophoto (file) or a tile/service layer. Underneath, in grey, it says which of the two it is: file name and size in pixels (`orthophoto.tif — 12000 × 9000 px`) or the kind of service, rendered from the view (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)`: this line is in Italian, *reso dalla vista* = rendered from the view).
- «Area:» «current view» (what you see in the map) or «whole raster». «whole raster» is available only for files: a tile service has no edge, so you always work on the view (or on a box or a polygon).
- «Resolution (map units/px):» tiles only: how many map units (metres, or degrees if the map is in geographic coordinates) per pixel of the rendered image. The proposed value is the view's when you open the window or choose the layer: if you zoom afterwards, correct it by hand. Smaller means more detail.
- «Max side (px):» the longest side of the image passed to the model: 2048 by default, from 512 to 8192. Above it the image is downscaled; SAM works at 1024 px internally anyway.

### Segmentation Modes

The «What to segment» group offers six modes. Choosing a mode changes the list of models (see «Available Models») and shows underneath, in blue, the instruction for that mode.

#### 1. Everything (automatic)

«Everything (automatic)»: SAM 2.1 segments every object it finds in the chosen «Area:» («current view» or «whole raster»). The polygons have no class: in the temporary layer they get the label «segment». Run it with «Start».

#### 2. Points

«Points: click the objects on the map»: press «Start selection»; the window hides and the QGIS message bar recalls the commands. Click the objects one by one: each click is one object. Right-click or Enter to finish, Backspace removes the last point, Esc cancels. The window comes back and the segmentation runs on the chosen «Area:», one object per point; points outside the image are ignored.

#### 3. Box

«Box: draw a rectangle»: press «Start selection» and drag a rectangle on the map (Esc or right-click cancels). The image is cut to the rectangle and everything inside it is segmented.

#### 4. Polygon

«Polygon: draw the area»: press «Start selection» and click the vertices; right-click, Enter or double-click close the polygon (at least three vertices are needed), Backspace removes the last vertex, Esc cancels. Only the inside of the polygon is segmented.

#### 5. Polygon from layer

«Polygon from layer:» choose a polygon layer in the drop-down next to it. The selected feature of the layer is used, or all of them if none is selected (several features are merged into one). As with a drawn polygon, only the inside is segmented: handy for working inside a trench, an excavation area or a boundary already drawn. Run it with «Start».

#### 6. Text classes

«Text classes:» type what to look for in the field next to it: **English** words separated by commas (default «building, road, river, field»; other examples: stone, wall). Each class becomes a label on the polygons. It works with YOLOE-26 locally or with Roboflow's SAM 3 in the cloud, on the chosen «Area:». Run it with «Start».

**«Threshold:»** (0.30 by default, from 0.05 to 0.95) is the minimum confidence for a result to be kept: lower gives more polygons, uncertain ones included; higher gives fewer but surer ones. The Replicate cloud model does not use it.

### Available Models

The «Model» group has a «Model:» drop-down whose content depends on the chosen mode:

| Model | Type | Requirements | Modes |
|-------|------|--------------|-------|
| SAM 2.1 Tiny | Local | local environment + ~78 MB weights | all but text classes; the lightest and fastest |
| SAM 2.1 Small | Local | local environment + ~92 MB weights | all but text classes |
| SAM 2.1 Base+ | Local | local environment + ~162 MB weights | all but text classes |
| SAM 2.1 Large | Local | local environment + ~449 MB weights | all but text classes; the most accurate and the slowest |
| Cloud: Replicate SAM-2 | Cloud | Replicate API key | automatic segmentation only (in «Points» mode the clicks are ignored, with a warning) |
| YOLOE-26 S | Local | local environment + ~31 MB weights + MobileCLIP2 254 MB (once) | text classes |
| YOLOE-26 M | Local | local environment + ~70 MB weights + MobileCLIP2 254 MB (once) | text classes |
| YOLOE-26 L | Local | local environment + ~79 MB weights + MobileCLIP2 254 MB (once) | text classes |
| Cloud: Roboflow SAM 3 | Cloud | Roboflow API key | text classes |

In the drop-down the entries read: «Locale: SAM 2.1 Tiny — ~78 MB», «Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB», «Cloud: Replicate SAM-2 (solo automatico, chiave API)», «Cloud: Roboflow SAM 3 (classi a testo, chiave API)» (*locale* = local, *classi a testo* = text classes, *solo automatico* = automatic only, *chiave* = key).

**Weights.** For a local model the weights status sits under the drop-down: «weights present ✓» (green) or «weights missing (~N MB)» (orange), with the «Download weights» button. The download, with a progress bar, takes the files from ultralytics' public assets on GitHub (no account needed). For YOLOE the MobileCLIP2 text encoder (254 MB) is downloaded too, only once for S, M and L. The weights live in `~/pyarchinit_5/bin/models/sam/`.

**API key.** For a cloud model the «API key:» field and the link to get the key replace the weights status (see «API Configuration»).

### SAM-3 with Text Prompt

With the «Text classes» mode you do not ask "split everything" but "find these things":

- type one or more classes in English, separated by commas: `building, road, river, field`, or `stone, wall`…;
- **YOLOE-26** (local, S/M/L) understands the words through the MobileCLIP2 text encoder; Roboflow's **SAM 3** (cloud) receives the same classes as text prompts (16 at most);
- each polygon carries the class that found it: in the temporary layer in the `label` field, in your own layer in the «Field for the label:». In pyArchInit's SU layers the class is not written.

SAM 2.1 in «Everything (automatic)», on the other hand, assigns no classes: it finds outlines, not names.

### API Configuration

Keys are needed only for cloud models. Choose the cloud model in the drop-down, paste the key into the «API key:» field (the text stays hidden) and press «Start»: the key is saved in the QGIS settings and offered again next time. With cloud models the prepared image is sent to the service.

#### Replicate API (SAM-2)
1. Create an account on [replicate.com](https://replicate.com)
2. Create a token at [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) (the «Replicate key» link next to the field opens the same page)
3. Paste it into «API key:» with the «Cloud: Replicate SAM-2» model

#### Roboflow API (SAM-3)
1. Create an account on [roboflow.com](https://roboflow.com)
2. Copy the key from [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) (the «Roboflow key» link next to the field)
3. Paste it into «API key:» with the «Cloud: Roboflow SAM 3» model

### Local SAM Installation

No terminal commands are needed: the environment for the local models is installed from the window.

1. You need a **system Python 3.10–3.13**: the packages are not installed into QGIS's Python, so as not to risk breaking it. The window finds it by itself: on **macOS** Python from [python.org](https://www.python.org/downloads/) or Homebrew, on **Windows** the `py` launcher of the python.org Python, on **Linux** the system's `python3.10`…`python3.13` or `python3`.
2. Press «Install / update» in the «Local environment» group: the virtual environment `~/pyarchinit_5/bin/sam_venv` is created and `ultralytics` (which brings torch, torchvision, OpenCV, numpy) and `requests` are installed into it: about **1.5 GB** of packages, only once. On Linux without an NVIDIA card the CPU build of torch is installed, much lighter.
3. «Show log» shows pip at work. At the end the status turns green: «ready — ultralytics …, torch …, mps».
4. Download the weights of the model you want to use with «Download weights» («Model» group).

Pressing «Install / update» again updates the packages. The compute device is chosen automatically: **MPS** on Macs with Apple Silicon, **CUDA** with an NVIDIA card, otherwise **CPU** (it works, but it is slower). If MPS or CUDA fail, the job starts again on the CPU by itself.

| What | Where |
|------|-------|
| Python environment | `~/pyarchinit_5/bin/sam_venv` |
| Model weights | `~/pyarchinit_5/bin/models/sam/` |
| API keys | QGIS settings |

`~/pyarchinit_5` is pyArchInit's data folder (or the one set by the `PYARCHINIT_HOME` variable).

### Target and Attributes

The «Target» group decides where the polygons go. The «Layer:» drop-down lists the project's polygon layers plus «— new temporary layer —»; if `pyunitastratigrafiche` is loaded, it is proposed.

| Target | What is written |
|--------|-----------------|
| «— new temporary layer —» | a memory layer `SAM_<raster>_<date_time>`, in the image CRS, with the fields `label` (the class, or «segment»), `score` (confidence), `area`, `source` (the model) and `created` (date and time) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = «Site:» (from the configuration, read-only), `area_s` = «Area:» (required), `stratigraph_index_us` = «Stratigraphic index:» (1 = stones/objects, 2 = layer/area), `tipo_us_s` = «US type:» (pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <model>` (e.g. `SAM sam2.1_t.pt`), `data` = today; `us_s` stays empty |
| any other polygon layer | the class in the «Field for the label:», a text field (`label`, `etichetta`, `classe`, `class`, `tipo` or `nome` is proposed if it exists; empty = do not write); if the layer has `score`, `area`, `source` or `created` fields, those are filled too |

- In SU layers the SU number is assigned afterwards in the attribute table: the final message reminds you («Then assign the US numbers in the attribute table.»).
- The polygons are reprojected to the CRS of the target layer and saved into it right away (if the layer was already in edit mode, its pending edits are saved too).
- The temporary layer lives only until QGIS is closed: to keep it, export it to a file (right-click on the layer → Export).

### How It Works

1. **The image.** For a file, the area is cropped and, if needed, downscaled with GDAL: the pixels are the file's real ones, not those drawn on the map (the layer style does not matter; rasters that are not 8-bit are stretched to 0–255). Tiles and services have no file: QGIS renders the view with its own drawing engine at the chosen resolution — that layer only, without the other layers of the map — and the render is segmented.
2. **The area.** With a polygon (drawn or from a layer) the rectangle containing it is taken, everything outside it is painted white, and at the end the results are clipped to the polygon.
3. **The model.** The work is done by `scripts/sam_worker.py`, which runs outside QGIS with the Python of `sam_venv` (or calls the cloud service): QGIS does not freeze. Its progress messages (the worker's `[sam] …` lines, in Italian) appear in the status line: model and device, then how many polygons in how many seconds. Polygons under 20 pixels are discarded and outlines are simplified.
4. **Back to the map.** The worker returns the polygons in pixels; pyArchInit turns them back into coordinates with the image's georeference, repairs invalid geometries and reprojects them to the CRS of the target layer.

### SAM Workflow

**1. Preparation**
- Load the orthophoto, or a tile layer (e.g. ESRI World Imagery as XYZ Tiles)
- Check the project's reference system
- To write into the SUs: load `pyunitastratigrafiche` (or `pyunitastratigrafiche_usm`) and check the site in the configuration
- The first time, for local models: «Install / update», then «Download weights»

**2. Configuration**
- «Image»: raster layer, area, resolution (for tiles) and max side
- «What to segment»: the mode, the threshold and, for text classes, the classes
- «Model»: a local model with its weights present, or a cloud model with its key
- «Target»: the layer and its attributes

**3. Execution**
- «Start», or «Start selection» followed by points, box or polygon on the map
- Follow the status line; «Cancel» stops the job
- At the end: `Done: N polygons added to “layer” (model).`

**4. Post-processing**
- Check the polygons; any warnings appear in the QGIS message bar
- SU layers: assign the SU numbers (`us_s`) in the attribute table
- Fix, merge or delete wrong polygons with the QGIS editing tools
- Temporary layer: export it if you want to keep it

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

- Good quality orthophoto, uniform lighting, good contrast between objects and background
- **Large orthophotos**: work by view or by box, not on «whole raster». SAM works at 1024 px internally and above «Max side (px):» the image is downscaled: over too large an area small objects get lost
- **Tiles**: choose a zoom level at which the objects can be recognised by eye (e.g. 0.3–0.6 m/px for buildings and roads). «Resolution (map units/px):» proposes the view's; if the area is large, the image is reduced to the max side and the real resolution gets worse
- **Text classes**: simple English nouns (building, road, river, field, stone, wall)
- Classes come only from YOLOE or SAM 3: SAM 2.1 in «Everything (automatic)» finds outlines but assigns no classes
- **Hardware**: Macs with Apple Silicon use MPS, an NVIDIA card uses CUDA, otherwise the CPU, which is slower (then prefer SAM 2.1 Tiny or Small, YOLOE-26 S and small areas)
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

| Message or symptom | What to do |
|--------------------|------------|
| «Local environment» in orange: «not installed…», or `The local environment is not installed: press “Install / update” (or choose a cloud model).` | Press «Install / update». A system Python 3.10–3.13 is needed; if there is none, `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` appears (no Python 3.10–3.13 found: install Python from python.org or Homebrew). If pip fails, the error is in «Show log». On Linux without an NVIDIA card the CPU build of torch is installed |
| «weights missing (~N MB)», or `The model weights are missing: press “Download weights”.` | Press «Download weights» (an internet connection is needed) |
| `The service API key is needed.` | With a cloud model, paste the key into «API key:» (see «API Configuration») |
| `No polygon found: try a smaller area, a lower threshold or another model.` | Smaller area, lower «Threshold:», another model (a larger SAM 2.1, or text classes); for tiles, a finer resolution |
| `l'area scelta non copre il raster` (the chosen area does not cover the raster; the message is in Italian) | The view, box or polygon falls outside the raster: zoom to the raster and try again |
| `Fill in the area for the US layer.` | Type the «Area:» in the «Target» group |
| `raster ruotato: non supportato (riproiettalo prima)` (rotated raster not supported: reproject it first) | Reproject the raster with gdalwarp (QGIS Raster menu) and use the new file |
| «Segmentation failed» with the worker's last lines | Read the lines in the message; try again with a smaller area or «Max side (px):», or with a smaller model |

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
- `tabs/Sam_Segmentation_Dialog.py` - SAM window: groups, modes, target
- `modules/utility/sam_environment.py` - Separate Python environment, packages and weights
- `modules/gis/sam_raster_source.py` - Image to segment (GDAL crop or view render) and georeference
- `modules/gis/sam_map_tools.py` - Map tools for points, box and polygon
- `scripts/sam_worker.py` - Worker outside QGIS: SAM 2.1, YOLOE, Replicate, Roboflow

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
