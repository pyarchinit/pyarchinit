# Tutorial 08: Materials Inventory Form

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [Main Fields](#main-fields)
5. [Form Tabs](#form-tabs)
6. [DBMS Toolbar](#dbms-toolbar)
7. [Media Management](#media-management)
8. [GIS Features](#gis-features)
9. [Quantifications and Statistics](#quantifications-and-statistics)
10. [Export and Reports](#export-and-reports)
11. [AI Integration](#ai-integration)
12. [Operational Workflow](#operational-workflow)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Materials Inventory Form** is the main tool for managing archaeological finds in PyArchInit. It allows you to catalog, describe, and quantify all materials found during excavation, from ceramics to metals, from glass to animal bones.

### Form Purpose

- Inventory all finds recovered
- Associate finds with source SUs
- Manage typological classification
- Document physical and technological characteristics
- Calculate quantifications (minimum vessels, EVE, weight)
- Link photos and drawings to finds
- Generate reports and statistics

### Manageable Material Types

The form supports various material types:
- **Ceramics**: Pottery, terracottas, building materials
- **Metals**: Bronze, iron, lead, gold, silver
- **Glass**: Containers, window glass
- **Bone/Ivory**: Objects in hard animal material
- **Stone**: Lithic tools, sculptures
- **Coins**: Numismatics
- **Organics**: Wood, textiles, leather

---

## Accessing the Form

### From Menu

1. Open QGIS with the PyArchInit plugin active
2. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Artefact form**

### From Toolbar

1. Locate the PyArchInit toolbar
2. Click on the **Finds** icon (amphora/vase icon)

### Keyboard Shortcut

- **Ctrl+G**: Enable/disable GIS visualization of current find

---

## User Interface

The interface is organized into three main areas:

### Main Areas

| Area | Description |
|------|-------------|
| **1. Header** | DBMS Toolbar, status indicators, GIS and export buttons |
| **2. Identification Fields** | Site, Area, SU, Inventory number, RA, Find type |
| **3. Descriptive Fields** | Class, Definition, Conservation status, Dating |
| **4. Detail Tabs** | 6 tabs for specific data |

### Available Tabs

| Tab | Content |
|-----|---------|
| **Description** | Descriptive text, media viewer, dating |
| **Slides** | Slide and negative management |
| **Quantitative Data** | Find elements, forms, ceramic measurements |
| **Technologies** | Production and decorative techniques |
| **Biblio Ref** | Bibliographic references |
| **Quantifications** | Charts and statistics |

---

## Main Fields

### Identification Fields

#### Site
- **Type**: ComboBox (read-only after save)
- **Required**: Yes
- **Description**: Archaeological site of origin

#### Inventory Number
- **Type**: Numeric LineEdit
- **Required**: Yes
- **Description**: Unique progressive find number within site
- **Constraint**: Unique per site

#### Area
- **Type**: Editable ComboBox
- **Required**: No
- **Description**: Source excavation area

#### SU (Stratigraphic Unit)
- **Type**: LineEdit
- **Required**: No (but strongly recommended)
- **Description**: Source SU number
- **Link**: Connects find to corresponding SU form

#### Structure
- **Type**: Editable ComboBox
- **Required**: No
- **Description**: Belonging structure (if applicable)

#### RA (Archaeological Find)
- **Type**: Numeric LineEdit
- **Required**: No
- **Description**: Alternative find number

### Classification Fields

#### Find Type
- **Type**: Editable ComboBox
- **Required**: Yes
- **Typical values**: Ceramic, Metal, Glass, Bone, Stone, Coin, etc.

#### Material Class (Filing Criterion)
- **Type**: Editable ComboBox
- **Required**: No
- **Examples for ceramics**:
  - Common ware
  - Italian sigillata
  - African sigillata
  - Black-gloss ware
  - Thin-walled ware
  - Amphorae
  - Lamps

#### Definition
- **Type**: Editable ComboBox
- **Required**: No
- **Examples**: Plate, Cup, Pot, Jug, Lid, etc.

### Status and Conservation Fields

#### Washed
- **Type**: ComboBox
- **Values**: Yes, No

#### Catalogued
- **Type**: ComboBox
- **Values**: Yes, No

#### Diagnostic
- **Type**: ComboBox
- **Values**: Yes, No

#### Conservation Status
- **Type**: Editable ComboBox
- **Typical values**: Complete, Fragmentary, Lacunose, Restored

---

## Form Tabs

### Tab 1: Description

The main tab contains textual description and media management.

#### Description Field
- **Type**: Multiline TextEdit
- **Suggested content**:
  - General form
  - Preserved parts
  - Technical characteristics
  - Decorations
  - Typological comparisons

#### Find Dating
- **Type**: Editable ComboBox
- **Format**: Text (e.g., "1st century BC", "2nd-3rd century AD")

#### Media Viewer
Area for viewing images associated with the find:
- **View all images**: Load all linked photos
- **Search images**: Search images
- **Remove tag**: Remove image-find association
- **SketchGPT**: Generate AI description from image

### Tab 2: Slides

Management of traditional photographic documentation.

#### Slides Table
| Column | Description |
|--------|-------------|
| Code | Slide identification code |
| No. | Progressive number |

#### Negatives Table
| Column | Description |
|--------|-------------|
| Code | Negative roll code |
| No. | Frame number |

### Tab 3: Quantitative Data

Fundamental tab for quantitative analysis, especially for ceramics.

#### Find Elements Table
Records individual elements composing the find:

| Column | Description | Example |
|--------|-------------|---------|
| Found element | Vessel anatomical part | Rim, Wall, Base, Handle |
| Quantity type | Fragment status | Fragment, Complete |
| Quantity | Number of pieces | 5 |

#### Ceramic Quantification Fields

| Field | Description |
|-------|-------------|
| **Minimum vessels** | Minimum Number of Individuals (MNI) |
| **Maximum vessels** | Maximum Number of Individuals |
| **Total fragments** | Auto-calculated from elements table |
| **Weight** | Weight in grams |
| **Rim diameter** | Rim diameter in cm |
| **Rim EVE** | Estimated Vessel Equivalent (preserved rim percentage) |

### Tab 4: Technologies

Recording of production and decorative techniques.

#### Technologies Table

| Column | Description | Example |
|--------|-------------|---------|
| Technology type | Technical category | Production, Decoration |
| Position | Where located | Interior, Exterior, Body |
| Quantity | If applicable | - |
| Unit | If applicable | - |

#### Ceramic-Specific Fields

| Field | Description |
|-------|-------------|
| **Ceramic body** | Fabric type (Fine, Semi-fine, Coarse) |
| **Coating** | Coating type (Slip, Engobe, Glaze) |

### Tab 5: Bibliographic References

Comparative bibliography management.

#### References Table

| Column | Description |
|--------|-------------|
| Author | Author surname(s) |
| Year | Publication year |
| Title | Abbreviated title |
| Page | Page reference |
| Figure | Figure/plate reference |

### Tab 6: Quantifications

Tab for generating charts and statistics.

#### Available Quantification Types

| Type | Description |
|------|-------------|
| **Minimum vessels** | MNI chart |
| **Maximum vessels** | Maximum number chart |
| **Total fragments** | Fragment count chart |
| **Weight** | Weight chart |
| **Rim EVE** | EVE chart |

#### Grouping Parameters

Charts can be grouped by:
- Find type
- Material class
- Definition
- Ceramic body
- Coating
- Type
- Dating
- RA
- Year

---

## DBMS Toolbar

### Standard Buttons

| Icon | Function | Description |
|------|----------|-------------|
| Connection test | Test connection | Verify database connection |
| First/Prev/Next/Last | Navigation | Navigate between records |
| New record | New | Create new find |
| Save | Save | Save changes |
| Delete | Delete | Delete current find |
| View all | All | View all records |
| New search | Search | Activate search mode |
| Search!!! | Execute | Execute search |
| Order by | Sort | Sort records |

### Specific Buttons

| Icon | Function | Description |
|------|----------|-------------|
| GIS | View GIS | Show find on map |
| PDF | Export PDF | Generate PDF form |
| Sheet | Export list | Generate PDF list |
| Excel | Export Excel | Export to Excel/CSV format |
| A5 | Export A5 | Generate A5 format label |
| Quant | Quantifications | Open quantifications panel |

---

## Media Management

### Image Association

#### Drag & Drop
You can drag images directly into the list to associate them with the find.

#### Media Buttons

| Button | Function |
|--------|----------|
| **All images** | Load all associated images |
| **Search images** | Open image search |
| **Remove tag** | Remove current association |

### Image Viewer

Double-click on an image in the list opens the full viewer with:
- Zoom
- Pan
- Rotation
- EXIF information

---

## GIS Features

### Map Visualization

#### GIS Button (Toggle)
- **Active**: Find is highlighted on QGIS map
- **Inactive**: No visualization
- **Shortcut**: Ctrl+G

#### Requirements
- Find must have source SU specified
- SU must have geometry in GIS layer

---

## Quantifications and Statistics

### Accessing Quantifications

1. Click **Quant** button in toolbar
2. Select quantification type
3. Select grouping parameters
4. Click OK

### Chart Types

#### Bar Chart
Displays distribution by selected category.

### Export Quantifications

Quantification data is automatically exported to:
- CSV file in `pyarchinit_Quantificazioni_folder`
- Chart displayed on screen

---

## Export and Reports

### Single Form PDF Export

Generates a complete PDF form of current find with:
- All identification data
- Description
- Quantitative data
- Bibliographic references
- Associated images (if available)

### List PDF Export

Generates a PDF list of all displayed finds (current search result):
- Summary table
- Essential data for each find

### A5 Export (Labels)

Generates A5 format labels for:
- Box identification
- Find labeling
- Mobile forms

### Excel/CSV Export

Exports data in tabular format for:
- External statistical processing
- Import to other software
- Archiving

---

## AI Integration

### SketchGPT

AI functionality to automatically generate find descriptions from images.

#### Usage

1. Associate an image to the find
2. Click **SketchGPT** button
3. Select image to analyze
4. Select GPT model (gpt-4-vision, gpt-4o)
5. System generates archaeological description

#### Output

Generated description includes:
- Find type identification
- Description of visible characteristics
- Possible typological comparisons
- Dating suggestions

> **Note**: Requires configured OpenAI API Key.

---

## Operational Workflow

### Creating a New Find

#### Step 1: Open Form
1. Open Materials Inventory Form
2. Verify database connection

#### Step 2: New Record
1. Click **New record**
2. Status changes to "New Record"

#### Step 3: Identification Data
1. Verify/select **Site**
2. Enter **Inventory number** (progressive)
3. Enter **Area** and source **SU**

#### Step 4: Classification
1. Select **Find type**
2. Select **Material class**
3. Select/enter **Definition**

#### Step 5: Description
1. Fill in **Description** field in Description tab
2. Select **Dating**
3. Associate any images

#### Step 6: Quantitative Data (if ceramic)
1. Open **Quantitative Data** tab
2. Enter elements in table
3. Fill minimum/maximum vessels
4. Enter weight and measurements

#### Step 7: Storage
1. Enter **Box no.**
2. Select **Storage location**
3. Indicate **Conservation status**

#### Step 8: Save
1. Click **Save**
2. Verify confirmation message
3. Record is now saved to database

### Searching Finds

#### Simple Search
1. Click **New search**
2. Fill in desired search fields
3. Click **Search!!!**

#### Search by SU
1. Activate search
2. Enter only US number in US field
3. Execute search

---

## Best Practices

### Inventory Numbering

- Use progressive numbering without gaps
- One number = one find (or homogeneous group)
- Document inventory criteria

### Classification

- Use controlled vocabularies for classes
- Maintain consistency in type definitions
- Update thesaurus when necessary

### Ceramic Quantification

For correct quantification:
1. **Minimum vessels (MNI)**: Count only diagnostic elements (rims, distinctive bases)
2. **EVE**: Measure preserved circumference percentage
3. **Weight**: Weigh all fragments in group

### Photographic Documentation

- Photograph all diagnostic finds
- Use metric scale in photos
- Associate photos via media manager

### SU Link

- Always verify SU exists before associating
- For cleaning/surface finds, use appropriate SU
- Document out-of-context finds

---

## Troubleshooting

### Common Problems

#### Duplicate inventory number
- **Error**: "A record with this inventory number already exists"
- **Cause**: Number already used for site
- **Solution**: Verify next available number with "View all"

#### Images not displayed
- **Cause**: Incorrect image path
- **Solution**:
  1. Verify path configuration in Settings
  2. Verify images are in correct folder
  3. Reassociate images

#### Empty quantifications
- **Cause**: Quantitative fields not filled
- **Solution**: Fill minimum/maximum vessels or total fragments

#### GIS not working
- **Cause**: SU has no geometry or layer not loaded
- **Solution**:
  1. Verify SU layer is loaded in QGIS
  2. Verify SU has associated geometry

---

## Video Tutorial

### Video 1: Inventory Form Overview
*Duration: 5-6 minutes*

**Contents:**
- General interface
- Tab navigation
- Main features

### Video 2: Complete Ceramic Documentation
*Duration: 8-10 minutes*

**Contents:**
- All field completion
- Ceramic quantification
- Find elements
- Technologies

### Video 3: Media and Photo Management
*Duration: 4-5 minutes*

**Contents:**
- Image association
- Viewer
- SketchGPT

### Video 4: Export and Quantifications
*Duration: 5-6 minutes*

**Contents:**
- PDF export
- Excel export
- Quantification charts

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management*
