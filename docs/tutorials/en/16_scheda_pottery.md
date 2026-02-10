# Tutorial 16: Pottery Form (Specialized Ceramics)

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [Main Fields](#main-fields)
5. [Form Tabs](#form-tabs)
6. [Pottery Tools](#pottery-tools)
7. [Visual Similarity Search](#visual-similarity-search)
8. [Quantifications](#quantifications)
9. [Media Management](#media-management)
10. [Export and Reports](#export-and-reports)
11. [Operational Workflow](#operational-workflow)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Pottery Form** is a specialized tool for detailed cataloging of archaeological ceramics. Unlike the Materials Inventory form (more generalist), this form is specifically designed for in-depth ceramic analysis, with dedicated fields for fabric, ware, decorations, and vessel-specific measurements.

### Differences from Materials Inventory Form

| Aspect | Materials Inventory | Pottery |
|--------|---------------------|---------|
| **Purpose** | All find types | Ceramics only |
| **Detail** | General | Specialized |
| **Fabric fields** | Ceramic body (generic) | Detailed fabric |
| **Decorations** | Single field | Internal/External separate |
| **Measurements** | Generic | Vessel-specific |
| **AI Tools** | SketchGPT | PotteryInk, YOLO, Similarity Search |

### Advanced Features

The Pottery form includes cutting-edge AI features:
- **PotteryInk**: Automatic generation of archaeological drawings from photos
- **YOLO Detection**: Automatic ceramic form recognition
- **Visual Similarity Search**: Search for similar ceramics via visual embeddings
- **Layout Generator**: Automatic ceramic plate generation

---

## Accessing the Form

### From Menu

1. Open QGIS with the PyArchInit plugin active
2. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery**

### From Toolbar

1. Locate the PyArchInit toolbar
2. Click on the **Pottery** icon (ceramic vase/amphora icon)

---

## User Interface

The interface is organized efficiently for ceramic cataloging:

### Main Areas

| Area | Description |
|------|-------------|
| **1. Header** | DBMS Toolbar, status indicators, filters |
| **2. Identification** | Site, Area, SU, ID Number, Box, Bag |
| **3. Classification** | Form, Ware, Fabric, Material |
| **4. Detail Tabs** | Description, Technical Data, Supplements |
| **5. Media Panel** | Image viewer, preview |

### Available Tabs

| Tab | Content |
|-----|---------|
| **Description data** | Description, decorations, notes |
| **Technical Data** | Measurements, surface treatment, Munsell |
| **Supplements** | Bibliography, Statistics |

---

## Main Fields

### Identification Fields

#### ID Number
- **Type**: Integer
- **Required**: Yes
- **Description**: Unique identification number of the ceramic fragment
- **Constraint**: Unique per site

#### Site
- **Type**: ComboBox
- **Required**: Yes
- **Description**: Archaeological site of origin

#### Area
- **Type**: Editable ComboBox
- **Description**: Excavation area

#### SU (Stratigraphic Unit)
- **Type**: Integer
- **Description**: SU number of discovery

#### Sector
- **Type**: Text
- **Description**: Specific discovery sector

### Storage Fields

#### Box
- **Type**: Integer
- **Description**: Storage box number

#### Bag
- **Type**: Integer
- **Description**: Bag number

#### Year
- **Type**: Integer
- **Description**: Year of discovery/cataloging

### Ceramic Classification Fields

#### Form
- **Type**: Editable ComboBox
- **Recommended**: Yes
- **Typical values**: Bowl, Jar, Jug, Plate, Cup, Amphora, Lid, etc.
- **Description**: General vessel form

#### Specific Form
- **Type**: Editable ComboBox
- **Description**: Specific typology (e.g., Hayes 50, Dressel 1)

#### Specific Shape
- **Type**: Text
- **Description**: Detailed morphological variant

#### Ware
- **Type**: Editable ComboBox
- **Description**: Ceramic class
- **Examples**:
  - African Red Slip
  - Italian Sigillata
  - Thin Walled Ware
  - Coarse Ware
  - Amphora
  - Cooking Ware

#### Material
- **Type**: Editable ComboBox
- **Description**: Base material
- **Values**: Ceramic, Terracotta, Porcelain, etc.

#### Fabric
- **Type**: Editable ComboBox
- **Description**: Ceramic paste type
- **Characteristics to consider**:
  - Paste color
  - Inclusion granulometry
  - Hardness
  - Porosity

### Conservation Fields

#### Percent
- **Type**: Editable ComboBox
- **Description**: Preserved percentage of vessel
- **Typical values**: <10%, 10-25%, 25-50%, 50-75%, >75%, Complete

#### QTY (Quantity)
- **Type**: Integer
- **Description**: Number of fragments

### Documentation Fields

#### Photo
- **Type**: Text
- **Description**: Photographic reference

#### Drawing
- **Type**: Text
- **Description**: Drawing reference

---

## Form Tabs

### Tab 1: Description Data

Main tab for fragment description.

#### Decorations

| Field | Description |
|-------|-------------|
| **External Decoration** | External decoration type |
| **Internal Decoration** | Internal decoration type |
| **Description External Deco** | Detailed description of external decoration |
| **Description Internal Deco** | Detailed description of internal decoration |
| **Decoration Type** | Decorative typology (Painted, Incised, Applique, etc.) |
| **Decoration Motif** | Decorative motif (Geometric, Vegetal, Figurative) |
| **Decoration Position** | Decoration position (Rim, Body, Base, Handle) |

#### Wheel Made
- **Type**: ComboBox
- **Values**: Yes, No, Unknown
- **Description**: Indicates if the vessel was wheel-made

#### Note
- **Type**: Multiline TextEdit
- **Description**: Additional notes and observations

#### Media Viewer
Area for viewing associated images:
- Drag & drop to associate images
- Double-click to open full viewer
- Buttons for tag management

### Tab 2: Technical Data

Technical data and measurements.

#### Munsell Color
- **Type**: Editable ComboBox
- **Description**: Munsell color code of the paste
- **Format**: e.g., "10YR 7/4", "5YR 6/6"
- **Note**: Refer to the Munsell Soil Color Chart

#### Surface Treatment
- **Type**: Editable ComboBox
- **Description**: Surface treatment
- **Typical values**:
  - Slip
  - Burnished
  - Glazed
  - Painted
  - Plain

#### Measurements (in cm)

| Field | Description |
|-------|-------------|
| **Diameter Max** | Maximum vessel diameter |
| **Diameter Rim** | Rim diameter |
| **Diameter Bottom** | Base diameter |
| **Total Height** | Total height (if reconstructable) |
| **Preserved Height** | Preserved height |

#### Dating
- **Type**: Editable ComboBox
- **Description**: Chronological framework
- **Format**: Text (e.g., "1st-2nd century AD")

### Tab 3: Supplements

Tab with sub-sections for supplementary data.

#### Sub-Tab: Bibliography
Management of bibliographic references for typological comparisons.

| Column | Description |
|--------|-------------|
| Author | Author(s) |
| Year | Publication year |
| Title | Abbreviated title |
| Page | Page reference |
| Figure | Figure/Plate |

#### Sub-Tab: Statistic
Access to quantification features and statistical charts.

---

## Pottery Tools

The Pottery form includes a powerful set of AI tools for ceramic image processing.

### Accessing Pottery Tools

1. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery Tools**

Or from the dedicated button in the Pottery form.

### PotteryInk - Drawing Generation

Automatically transforms ceramic photos into stylized archaeological drawings.

#### Usage

1. Select a ceramic image
2. Click on "Generate Drawing"
3. The system processes the image with AI
4. The drawing is generated in archaeological style

#### Requirements
- Dedicated virtual environment (automatically created)
- Pre-trained AI models
- GPU recommended for optimal performance

### YOLO Pottery Detection

Automatic recognition of ceramic forms in images.

#### Features

- Automatically identifies vessel form
- Suggests classification
- Detects anatomical parts (rim, wall, base, handle)

### Layout Generator

Automatically generates ceramic plates for publication.

#### Output

- Plates in standard archaeological format
- Automatic metric scale
- Optimized layout
- Export to PDF or image

### PDF Extractor

Extracts ceramic images from PDF publications for comparisons.

---

## Visual Similarity Search

Advanced feature to find visually similar ceramics in the database.

### How It Works

The system uses **visual embeddings** generated by deep learning models to represent each ceramic image as a numerical vector. The search finds ceramics with the most similar vectors.

### Usage

1. Select a reference image
2. Click on "Find Similar"
3. The system searches the database
4. Most similar ceramics are shown sorted by similarity

### Available Models

- **ResNet50**: Good speed/precision balance
- **EfficientNet**: Optimal performance
- **CLIP**: Multimodal search (text + image)

### Embedding Update

Embeddings are automatically generated when new images are added. It's possible to force the update from the Pottery Tools menu.

---

## Quantifications

### Access

1. Click on the **Quant** button in the toolbar
2. Select the quantification parameter
3. View the chart

### Available Parameters

| Parameter | Description |
|-----------|-------------|
| **Fabric** | Distribution by paste type |
| **US** | Distribution by stratigraphic unit |
| **Area** | Distribution by excavation area |
| **Material** | Distribution by material |
| **Percent** | Distribution by preserved percentage |
| **Shape/Form** | Distribution by form |
| **Specific form** | Distribution by specific form |
| **Ware** | Distribution by ceramic class |
| **Munsell color** | Distribution by color |
| **Surface treatment** | Distribution by surface treatment |
| **External decoration** | Distribution by external decoration |
| **Internal decoration** | Distribution by internal decoration |
| **Wheel made** | Wheel yes/no distribution |

### Quantification Export

Data is exported to:
- CSV file in `pyarchinit_Quantificazioni_folder`
- Chart displayed on screen

---

## Media Management

### Image Association

#### Methods

1. **Drag & Drop**: Drag images into the list
2. **All Images button**: Load all associated images
3. **Search Images**: Search for specific images

### Video Player

For ceramics with video documentation, an integrated player is available.

### Cloudinary Integration

Support for remote images on Cloudinary:
- Automatic thumbnail loading
- Local cache for performance
- Cloud synchronization

---

## Export and Reports

### PDF Form Export

Generates a complete PDF form with:
- Identification data
- Classification
- Measurements
- Associated images
- Notes

### List Export

Generates PDF list of all displayed records.

### Data Export

Button for export in tabular format (CSV/Excel).

---

## Operational Workflow

### Recording New Ceramic Fragment

#### Step 1: Open and New Record
1. Open the Pottery Form
2. Click **New record**

#### Step 2: Identification Data
1. Verify/select **Site**
2. Enter **ID Number** (progressive)
3. Enter **Area**, **SU**, **Sector**
4. Enter **Box** and **Bag**

#### Step 3: Classification
1. Select **Form** (Bowl, Jar, etc.)
2. Select **Ware** (ceramic class)
3. Select **Fabric** (paste type)
4. Indicate **Material** and **Percent**

#### Step 4: Technical Data
1. Open **Technical Data** tab
2. Enter **Munsell color**
3. Select **Surface treatment**
4. Enter **measurements** (diameters, heights)
5. Indicate **Wheel made**

#### Step 5: Decorations (if present)
1. Return to **Description data** tab
2. Select **External/Internal decoration** type
3. Fill in detailed descriptions
4. Indicate **Decoration type**, **motif**, **position**

#### Step 6: Documentation
1. Associate photos (drag & drop)
2. Enter **Photo** and **Drawing** reference
3. Fill in **Note** with observations

#### Step 7: Dating and Comparisons
1. Enter **Dating**
2. Open **Supplements** tab → **Bibliography**
3. Add bibliographic references

#### Step 8: Save
1. Click **Save**
2. Verify confirmation

---

## Best Practices

### Consistent Classification

- Use standardized vocabularies for Form, Ware, Fabric
- Maintain consistency in nomenclature
- Update thesaurus when necessary

### Photographic Documentation

- Photograph each fragment with scale
- Include internal and external view
- Document decorative details

### Measurements

- Use calipers for accurate measurements
- Always indicate unit of measurement (cm)
- For fragments, measure only preserved parts

### Munsell Color

- Always use the Munsell Soil Color Chart
- Measure on fresh fracture
- Indicate lighting conditions

### AI Tools Usage

- Always verify automatic results
- PotteryInk works better with good quality photos
- Similarity search is useful for comparisons, not a substitute for analysis

---

## Troubleshooting

### Common Problems

#### Duplicate ID Number
- **Error**: "A record with this ID already exists"
- **Solution**: Verify the next available number

#### Pottery Tools won't start
- **Cause**: Virtual environment not configured
- **Solution**:
  1. Verify internet connection
  2. Wait for automatic configuration
  3. Check log in `pyarchinit/bin/pottery_venv`

#### PotteryInk slow
- **Cause**: CPU processing instead of GPU
- **Solution**:
  1. Install CUDA drivers (NVIDIA)
  2. Verify PyTorch is using GPU

#### Empty Similarity Search
- **Cause**: Embeddings not generated
- **Solution**:
  1. Open Pottery Tools
  2. Click "Update Embeddings"
  3. Wait for completion

#### Images not loaded
- **Cause**: Incorrect path or Cloudinary not configured
- **Solution**:
  1. Verify path configuration in Settings
  2. For Cloudinary: verify credentials

---

## Video Tutorial

### Video 1: Pottery Form Overview
*Duration: 5-6 minutes*

[Video placeholder]

### Video 2: Complete Ceramic Recording
*Duration: 8-10 minutes*

[Video placeholder]

### Video 3: Pottery Tools and AI
*Duration: 10-12 minutes*

[Video placeholder]

### Video 4: Similarity Search
*Duration: 5-6 minutes*

[Video placeholder]

---

## Database Fields Summary

| Field | Type | Database | Required |
|-------|------|----------|----------|
| ID Number | Integer | id_number | Yes |
| Site | Text | sito | Yes |
| Area | Text | area | No |
| US | Integer | us | No |
| Box | Integer | box | No |
| Bag | Integer | bag | No |
| Sector | Text | sector | No |
| Photo | Text | photo | No |
| Drawing | Text | drawing | No |
| Year | Integer | anno | No |
| Fabric | Text | fabric | No |
| Percent | Text | percent | No |
| Material | Text | material | No |
| Form | Text | form | No |
| Specific Form | Text | specific_form | No |
| Specific Shape | Text | specific_shape | No |
| Ware | Text | ware | No |
| Munsell Color | Text | munsell | No |
| Surface Treatment | Text | surf_trat | No |
| External Decoration | Text | exdeco | No |
| Internal Decoration | Text | intdeco | No |
| Wheel Made | Text | wheel_made | No |
| Descrip. External Deco | Text | descrip_ex_deco | No |
| Descrip. Internal Deco | Text | descrip_in_deco | No |
| Note | Text | note | No |
| Diameter Max | Numeric | diametro_max | No |
| QTY | Integer | qty | No |
| Diameter Rim | Numeric | diametro_rim | No |
| Diameter Bottom | Numeric | diametro_bottom | No |
| Total Height | Numeric | diametro_height | No |
| Preserved Height | Numeric | diametro_preserved | No |
| Decoration Type | Text | decoration_type | No |
| Decoration Motif | Text | decoration_motif | No |
| Decoration Position | Text | decoration_position | No |
| Dating | Text | datazione | No |

---

*Last updated: January 2026*
*PyArchInit - Archaeological Pottery Analysis*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/pyarchinit_pottery_tools_animation.html)
