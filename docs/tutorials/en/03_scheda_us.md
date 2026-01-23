# PyArchInit - SU/WSU Form (Stratigraphic Unit)

## Table of Contents
1. [Introduction](#introduction)
2. [Fundamental Concepts](#fundamental-concepts)
3. [Accessing the Form](#accessing-the-form)
4. [General Interface](#general-interface)
5. [Identification Fields](#identification-fields)
6. [Location Tab](#location-tab)
7. [Descriptive Data Tab](#descriptive-data-tab)
8. [Periodization Tab](#periodization-tab)
9. [Stratigraphic Relationships Tab](#stratigraphic-relationships-tab)
10. [Physical Data Tab](#physical-data-tab)
11. [Filing Data Tab](#filing-data-tab)
12. [SU Measurements Tab](#su-measurements-tab)
13. [Documentation Tab](#documentation-tab)
14. [WSU Building Technique Tab](#wsu-building-technique-tab)
15. [WSU Binders Tab](#wsu-binders-tab)
16. [Media Tab](#media-tab)
17. [Help - Tool Box Tab](#help---tool-box-tab)
18. [Harris Matrix](#harris-matrix)
19. [GIS Features](#gis-features)
20. [Exports](#exports)
21. [Operational Workflow](#operational-workflow)
22. [Troubleshooting](#troubleshooting)

---

## Introduction

The **SU/WSU Form** (Stratigraphic Unit / Wall Stratigraphic Unit) is the heart of archaeological documentation in PyArchInit. It represents the main tool for recording all information related to stratigraphic units identified during excavation.

This form implements the principles of the **stratigraphic method** developed by Edward C. Harris, allowing documentation of:
- Physical characteristics of each layer
- Stratigraphic relationships between units
- Relative and absolute chronology
- Associated graphic and photographic documentation

<!-- VIDEO: Introduction to SU Form -->
> **Video Tutorial**: [Insert SU form introduction video link]

---

## Fundamental Concepts

### What is a Stratigraphic Unit (SU)

A **Stratigraphic Unit** is the smallest excavation unit that can be identified and distinguished from others. It can be:
- **Layer**: earth deposit with homogeneous characteristics
- **Interface**: contact surface between layers (e.g., pit cut)
- **Structural element**: part of a construction

### Unit Types

| Type | Code | Description |
|------|------|-------------|
| SU | Stratigraphic Unit | Generic layer |
| WSU | Wall Stratigraphic Unit | Wall construction element |
| VSUA | Vertical Stratigraphic Unit A | Vertical elevation type A |
| VSUB | Vertical Stratigraphic Unit B | Vertical elevation type B |
| VSUC | Vertical Stratigraphic Unit C | Vertical elevation type C |
| DSU | Demolition Stratigraphic Unit | Collapse/demolition layer |
| ASH | Ashlars | Architectural blocks |
| VSF | Virtual Stratigraphic Feature | Virtual element |
| SF | Stratigraphic Feature | Stratigraphic feature |
| SSU | Sub-Stratigraphic Unit | Subdivision of SU |
| DOC | Documentation | Documentary element |

### Stratigraphic Relationships

Stratigraphic relationships define temporal relations between SUs:

| Relationship | Inverse | Meaning |
|--------------|---------|---------|
| **Covers** | Covered by | The SU physically overlies |
| **Cuts** | Cut by | The SU interrupts/crosses |
| **Fills** | Filled by | The SU fills a cavity |
| **Abuts** | Supports | Support relationship |

<!-- IMAGE: Stratigraphic relationships diagram -->
![Stratigraphic Relationships](images/03_scheda_us/01_schema_rapporti.png)
*Figure 1: Stratigraphic relationships diagram*

---

## Accessing the Form

To access the SU Form:

1. Menu **PyArchInit** → **Archaeological record management** → **SU/WSU**
2. Or from the PyArchInit toolbar, click on the **SU/WSU** icon

<!-- IMAGE: Screenshot of access menu -->
![SU Form Access](images/03_scheda_us/02_menu_scheda_us.png)
*Figure 2: Accessing the SU Form from menu*

<!-- IMAGE: Screenshot of toolbar -->
![SU Toolbar](images/03_scheda_us/03_toolbar_us.png)
*Figure 3: SU Form icon in toolbar*

---

## General Interface

The SU Form is organized into several functional areas:

<!-- IMAGE: Screenshot of complete interface with numbered areas -->
![SU Interface](images/03_scheda_us/04_interfaccia_completa.png)
*Figure 4: Complete SU Form interface*

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | **Identification Fields** | Site, Area, SU, Type, Definitions |
| 2 | **DBMS Toolbar** | Navigation, saving, search |
| 3 | **Data Tabs** | Thematic tabs for data |
| 4 | **GIS Toolbar** | Map display tools |
| 5 | **Tool Box Tab** | Advanced tools and Matrix |

### DBMS Toolbar

The DBMS toolbar is identical to the Site Form with some additional features:

<!-- IMAGE: Screenshot of SU DBMS toolbar -->
![DBMS Toolbar](images/03_scheda_us/05_toolbar_dbms.png)
*Figure 5: SU Form DBMS Toolbar*

| Button | Function | Description |
|--------|----------|-------------|
| **New record** | New | Creates a new SU form |
| **Save** | Save | Saves changes |
| **Delete** | Delete | Deletes current form |
| **View all** | View all | Shows all records |
| **First/Prev/Next/Last** | Navigation | Navigate between records |
| **new search** | Search | Starts search mode |
| **search !!!** | Execute | Executes search |
| **Order by** | Sort | Sorts records |
| **Report** | Print | Generates PDF report |
| **SU/Photo list** | List | Generates lists |

---

## Identification Fields

The identification fields are always visible at the top of the form.

<!-- IMAGE: Screenshot of identification fields -->
![Identification Fields](images/03_scheda_us/06_campi_identificativi.png)
*Figure 6: Identification fields*

### Required Fields

| Field | Description | Format |
|-------|-------------|--------|
| **Site** | Archaeological site name | Text (from combobox) |
| **Area** | Excavation area number | Integer (1-20) |
| **SU/WSU** | Stratigraphic unit number | Integer |
| **Unit type** | Type of unit (SU, WSU, etc.) | Selection |

### Descriptive Fields

| Field | Description |
|-------|-------------|
| **Stratigraphic definition** | Stratigraphic classification (from thesaurus) |
| **Interpretive definition** | Functional interpretation (from thesaurus) |

### Stratigraphic Definitions (Examples)

| Definition | Description |
|------------|-------------|
| Layer | Generic deposit |
| Fill | Filling material |
| Cut | Negative interface |
| Floor surface | Walking surface |
| Collapse | Collapse material |
| Beaten earth | Beaten earth flooring |

### Interpretive Definitions (Examples)

| Definition | Description |
|------------|-------------|
| Construction activity | Construction phase |
| Abandonment | Abandonment phase |
| Flooring | Floor surface |
| Wall | Wall structure |
| Pit | Intentional excavation |
| Leveling | Preparation layer |

---

## Location Tab

Contains positioning data within the excavation.

<!-- IMAGE: Screenshot of location tab -->
![Location Tab](images/03_scheda_us/07_tab_localizzazione.png)
*Figure 7: Location Tab*

### Location Fields

| Field | Description | Notes |
|-------|-------------|-------|
| **Sector** | Excavation sector | Letters A-H or numbers 1-20 |
| **Square/Wall** | Spatial reference | For grid excavations |
| **Room** | Room number | For buildings/structures |
| **Trench** | Trench number | For test trenches |

### Catalog Numbers

| Field | Description |
|-------|-------------|
| **General Cat. Nr.** | General catalog number |
| **Internal Cat. Nr.** | Internal catalog number |
| **International Cat. Nr.** | International code |

---

## Descriptive Data Tab

Contains the textual description of the stratigraphic unit.

<!-- IMAGE: Screenshot of descriptive data tab -->
![Descriptive Data Tab](images/03_scheda_us/08_tab_dati_descrittivi.png)
*Figure 8: Descriptive Data Tab*

### Descriptive Fields

| Field | Description | Suggestions |
|-------|-------------|-------------|
| **Description** | Physical description of SU | Color, consistency, composition, boundaries |
| **Interpretation** | Functional interpretation | Function, formation, meaning |
| **Dating elements** | Materials for dating | Ceramics, coins, dating objects |
| **Observations** | Additional notes | Doubts, hypotheses, comparisons |

### How to Describe an SU

**Physical description:**
```
Layer of clayey soil, dark brown color (10YR 3/3),
compact consistency, with inclusions of brick fragments (2-5 cm),
limestone pebbles (1-3 cm) and charcoal. Sharp boundaries above,
diffuse below. Variable thickness 15-25 cm.
```

**Interpretation:**
```
Abandonment layer formed following cessation of
activities in the room. The presence of fragmented building
material suggests partial collapse of structures.
```

---

## Periodization Tab

Manages the chronology of the stratigraphic unit.

<!-- IMAGE: Screenshot of periodization tab -->
![Periodization Tab](images/03_scheda_us/09_tab_periodizzazione.png)
*Figure 9: Periodization Tab*

### Relative Periodization

| Field | Description |
|-------|-------------|
| **Initial Period** | Formation period |
| **Initial Phase** | Formation phase |
| **Final Period** | Obliteration period |
| **Final Phase** | Obliteration phase |

**Note**: Periods and phases must first be created in the **Periodization Form**.

### Absolute Chronology

| Field | Description |
|-------|-------------|
| **Dating** | Absolute date or range |
| **Year** | Excavation year |

### Other Fields

| Field | Description | Values |
|-------|-------------|--------|
| **Activity** | Activity type | Free text |
| **Structure** | Associated structure code | From Structure Form |
| **Excavated** | Excavation status | Yes / No |
| **Excavation method** | Excavation mode | Mechanical / Stratigraphic |

### Structure Field - Link with Structure Form

The **Structure** field allows you to associate one or more structures with the current stratigraphic unit. It is a multi-selection field (checkboxes).

#### How synchronization works

1. **First** create structures in the **Structure Form**
2. In the Structure Form fill in: **Site** (same as SU), **Code** (e.g., "MUR"), **Number** (e.g., 1)
3. In the SU Form, the Structure field will show available structures in format `CODE-NUMBER`

#### Selecting structures

1. Click on the **Structure** field to open the dropdown menu
2. Check the boxes of structures to associate
3. You can select **multiple structures** at once
4. Save the record

#### Removing a single structure

1. Click on the **Structure** field to open the dropdown menu
2. **Uncheck** the box of the structure to remove
3. Save the record

#### Removing all structures (Clear field)

1. **Right-click** on the Structure field
2. Select "**Clear Structure field**" from the context menu
3. Save the record to confirm the change

> **Note**: The "Clear field" function removes ALL associated structures. To remove only one, use the checkboxes.

---

## Stratigraphic Relationships Tab

**This is the most important tab in the SU form.** It defines stratigraphic relations with other units.

<!-- IMAGE: Screenshot of stratigraphic relationships tab -->
![Relationships Tab](images/03_scheda_us/10_tab_rapporti.png)
*Figure 10: Stratigraphic Relationships Tab*

<!-- VIDEO: How to enter stratigraphic relationships -->
> **Video Tutorial**: [Insert stratigraphic relationships video link]

### Relationships Table Structure

| Column | Description |
|--------|-------------|
| **Site** | Related SU site |
| **Area** | Related SU area |
| **SU** | Related SU number |
| **Relationship type** | Type of relationship |

### Available Relationship Types

| Italian | English | German |
|---------|---------|--------|
| Copre | Covers | Liegt über |
| Coperto da | Covered by | Liegt unter |
| Taglia | Cuts | Schneidet |
| Tagliato da | Cut by | Geschnitten von |
| Riempie | Fills | Verfüllt |
| Riempito da | Filled by | Verfüllt von |
| Si appoggia a | Abuts | Stützt sich auf |
| Gli si appoggia | Supports | Wird gestützt von |
| Uguale a (=) | Same as | Gleich |
| Anteriore (>>) | Earlier | Früher |
| Posteriore (<<) | Later | Später |

### Entering Relationships

1. Click **+** to add a row
2. Enter Site, Area, SU of related SU
3. Select relationship type
4. Save

<!-- IMAGE: Screenshot of relationship entry -->
![Relationship Entry](images/03_scheda_us/11_inserimento_rapporto.png)
*Figure 11: Entering a stratigraphic relationship*

### Relationships Buttons

| Button | Function |
|--------|----------|
| **+** | Add row |
| **-** | Remove row |
| **Insert or update inverse relat.** | Automatically create inverse relationship |
| **Go to SU** | Navigate to selected SU |
| **Display matrix** | Show Harris Matrix |
| **Fix** | Fix relationship errors |

### Automatic Inverse Relationships

When you enter a relationship, you can automatically create the inverse:

| If you enter | Will be created |
|--------------|-----------------|
| SU 1 **covers** SU 2 | SU 2 **covered by** SU 1 |
| SU 1 **cuts** SU 2 | SU 2 **cut by** SU 1 |
| SU 1 **fills** SU 2 | SU 2 **filled by** SU 1 |

### Relationship Check

The **Check relationships** button verifies relationship consistency:
- Detects missing relationships
- Finds inconsistencies
- Flags logical errors

<!-- IMAGE: Screenshot of relationship check -->
![Relationship Check](images/03_scheda_us/12_controllo_rapporti.png)
*Figure 12: Relationship check result*

---

## Extended Matrix Relationships Tab

Tab dedicated to advanced relationship management for Extended Matrix.

<!-- IMAGE: Screenshot of EM tab -->
![EM Tab](images/03_scheda_us/13_tab_em.png)
*Figure 13: Extended Matrix Relationships Tab*

This tab allows adding supplementary information for each relationship:
- Unit type
- Interpretive definition
- Periodization

---

## Physical Data Tab

Describes the physical characteristics of the stratigraphic unit.

<!-- IMAGE: Screenshot of physical data tab -->
![Physical Data Tab](images/03_scheda_us/14_tab_dati_fisici.png)
*Figure 14: Physical Data Tab*

### General Characteristics

| Field | Values |
|-------|--------|
| **Color** | Brown, Yellow, Gray, Black, etc. |
| **Consistency** | Clayey, Compact, Friable, Sandy |
| **Formation** | Artificial, Natural |
| **Position** | - |
| **Formation mode** | Input, Subtraction, Accumulation, Landslide |
| **Distinction criteria** | Free text |

### Component Tables

| Table | Content |
|-------|---------|
| **Organic comp.** | Bones, wood, charcoal, seeds, etc. |
| **Inorganic comp.** | Stones, bricks, ceramics, etc. |
| **Artificial Inclusions** | Anthropic materials included |

For each table:
- **+** Add row
- **-** Remove row

### Sampling

| Field | Values |
|-------|--------|
| **Flotation** | Yes / No |
| **Sieving** | Yes / No |
| **Reliability** | Poor, Good, Fair, Excellent |
| **Conservation status** | Insufficient, Poor, Good, Fair, Excellent |

---

## Filing Data Tab

Information about form compilation.

<!-- IMAGE: Screenshot of filing data tab -->
![Filing Data Tab](images/03_scheda_us/15_tab_schedatura.png)
*Figure 15: Filing Data Tab*

### Entity and Managers

| Field | Description |
|-------|-------------|
| **Responsible Entity** | Entity managing the excavation |
| **Superintendence** | Competent SABAP |
| **Scientific Director** | Excavation director |
| **Compilation Manager** | Who compiled the field form |
| **Reworking Manager** | Who reworked the data |

### References

| Field | Description |
|-------|-------------|
| **TM Ref.** | TM sheet reference (Materials Table) |
| **RA Ref.** | RA sheet reference (Archaeological Finds) |
| **Pottery Ref.** | Pottery sheet reference |

### Dates

| Field | Format |
|-------|--------|
| **Survey date** | DD/MM/YYYY |
| **Filing date** | DD/MM/YYYY |
| **Reworking date** | DD/MM/YYYY |

---

## SU Measurements Tab

Contains all stratigraphic unit measurements.

<!-- IMAGE: Screenshot of measurements tab -->
![Measurements Tab](images/03_scheda_us/16_tab_misure.png)
*Figure 16: SU Measurements Tab*

### Elevations

| Field | Description | Unit |
|-------|-------------|------|
| **Absolute elevation** | Elevation above sea level | meters |
| **Relative elevation** | Elevation relative to reference point | meters |
| **Max absolute elevation** | Maximum absolute elevation | meters |
| **Max relative elevation** | Maximum relative elevation | meters |
| **Min absolute elevation** | Minimum absolute elevation | meters |
| **Min relative elevation** | Minimum relative elevation | meters |

### Dimensions

| Field | Description | Unit |
|-------|-------------|------|
| **Max length** | Maximum length | meters |
| **Average width** | Average width | meters |
| **Max height** | Maximum height | meters |
| **Min height** | Minimum height | meters |
| **Thickness** | Layer thickness | meters |
| **Max depth** | Maximum depth | meters |
| **Min depth** | Minimum depth | meters |

---

## Documentation Tab

Manages references to graphic and photographic documentation.

<!-- IMAGE: Screenshot of documentation tab -->
![Documentation Tab](images/03_scheda_us/17_tab_documentazione.png)
*Figure 17: Documentation Tab*

### Documentation Table

| Column | Description |
|--------|-------------|
| **Documentation type** | Photo, Plan, Section, Elevation, etc. |
| **References** | Document number/code |

### Documentation Types

| Type | Description |
|------|-------------|
| Photo | Photographic documentation |
| Plan | Excavation plan |
| Section | Stratigraphic section |
| Elevation | Wall elevation |
| Survey | Graphic survey |
| 3D | Three-dimensional model |

### Buttons

| Button | Function |
|--------|----------|
| **insert row** | Adds reference |
| **remove row** | Removes reference |
| **Update doc** | Updates from documentation table |
| **View documentation** | Shows associated documents |

---

## WSU Building Technique Tab

Specific tab for Wall Stratigraphic Units (WSU).

<!-- IMAGE: Screenshot of building technique tab -->
![Building Technique Tab](images/03_scheda_us/18_tab_tecnica_usm.png)
*Figure 18: WSU Building Technique Tab*

### WSU Specific Data

| Field | Description |
|-------|-------------|
| **WSU Length** | Wall length (meters) |
| **WSU Height** | Wall height (meters) |
| **Analyzed surface** | Percentage analyzed |
| **Wall section** | Section type |
| **Module** | Construction module |
| **Work typology** | Wall type |
| **Orientation** | Structure orientation |
| **Reuse** | Yes / No |

### Materials and Techniques

| Section | Fields |
|---------|--------|
| **Bricks** | Materials, Processing, Consistency, Shape, Color, Mixture, Laying |
| **Stone Elements** | Materials, Processing, Consistency, Shape, Color, Cut, Laying |

### Samples

| Field | Description |
|-------|-------------|
| **Mortar samples** | Mortar sample references |
| **Brick samples** | Brick sample references |
| **Stone samples** | Stone sample references |

---

## WSU Binders Tab

Describes binder (mortar) characteristics in wall structures.

<!-- IMAGE: Screenshot of binders tab -->
![Binders Tab](images/03_scheda_us/19_tab_leganti.png)
*Figure 19: WSU Binders Tab*

### Binder Characteristics

| Field | Description |
|-------|-------------|
| **Binder type** | Mortar, Mud, Absent, etc. |
| **Consistency** | Tenacious, Friable, etc. |
| **Color** | Binder color |
| **Finish** | Finish type |
| **Binder thickness** | Thickness in cm |

### Composition

| Section | Description |
|---------|-------------|
| **Aggregates** | Coarse components |
| **Inerts** | Fine components |
| **Inclusions** | Included materials |

---

## Media Tab

Displays images associated with the stratigraphic unit.

<!-- IMAGE: Screenshot of media tab -->
![Media Tab](images/03_scheda_us/20_tab_media.png)
*Figure 20: Media Tab*

### SU List

The table shows all SUs with associated images:
- Go to form
- Checkbox for multiple selection
- Thumbnail preview

### Buttons

| Button | Function |
|--------|----------|
| **Search images** | Search for associated images |
| **Save** | Save associations |
| **Revert** | Undo changes |

---

## Help - Tool Box Tab

Contains advanced tools for checking and exporting.

<!-- IMAGE: Screenshot of toolbox tab -->
![Tool Box Tab](images/03_scheda_us/21_tab_toolbox.png)
*Figure 21: Tool Box Tab*

### Check Systems

| Tool | Description |
|------|-------------|
| **Check stratigraphic relationships** | Verify relationship consistency |
| **Check, go!!!!** | Execute check |

### Matrix Export

| Button | Output |
|--------|--------|
| **Export Matrix** | DOT file for Graphviz |
| **Export Graphml** | GraphML file for yEd |
| **Export to Extended Matrix** | S3DGraphy format |
| **Interactive Matrix** | Interactive visualization |

### Additional Tools

| Tool | Description |
|------|-------------|
| **Stratigraphic order** | Calculate stratigraphic sequence |
| **Create Period Code** | Generate period codes |
| **csv2us** | Import SU from CSV |
| **Graphml2csv** | Export GraphML to CSV |

---

## Stratigraphic Ordering (Order Layer)

The **Stratigraphic Ordering** system automatically calculates the SU sequence based on the entered stratigraphic relationships. It is an automatic calculation that assigns a progressive numeric value to each SU according to its position in the stratigraphic sequence.

### How it works

The system analyzes stratigraphic relationships (covers/covered by, cuts/cut by, etc.) and builds a directed graph. Then it calculates the topological order, assigning:
- **Level 0**: Oldest SUs (at the base of stratigraphy)
- **Level 1, 2, 3...**: Progressively more recent SUs
- **Level N**: Most recent SUs (at the top of stratigraphy)

### Requirements for ordering

1. **Complete relationships**: All SUs must have stratigraphic relationships entered
2. **No paradoxes**: No cycles must exist in relationships (e.g., SU1 covers SU2 and SU2 covers SU1)
3. **Inverse relationships**: All relationships must have their inverse

### How to execute ordering

1. Perform a **search** by Site and Area (the system works on single site/area)
2. Go to **Help Tab** → **Tool Box**
3. Click **Stratigraphic order**
4. Confirm the operation
5. Wait for completion

### Ordering format

The ordering is **always sequential numeric**:
```
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13...
```

**Rules:**
- Numbers are **always consecutive** (never 1, 2, 5, 8 - always 1, 2, 3, 4)
- No gaps in the sequence
- SUs at the same stratigraphic level have the same number
- Order can be **reversed** (checkbox "Order: Ancient → Recent"):
  - **Active**: 0 = oldest, N = most recent
  - **Inactive**: 0 = most recent, N = oldest

### Order Layer Field

The result is saved in the **Order Layer** field (lineEditOrderLayer) of each SU. This field:
- Is **automatically calculated** by the system
- Can be **manually modified** if necessary
- Is used to sort SUs in the view

### Common errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Stratigraphic paradox" | Cycle in relationships | Verify and correct relationships |
| "Missing SUs" | Referenced SUs don't exist | Create missing SUs |
| "Missing relationship" | Relationship without type or number | Complete relationships |

### Visualization

Once the order is calculated, you can:
- **Sort** records by Order Layer
- **Filter** by specific levels
- **Export** Matrix with levels

---

### GIS Functions

| Button | Function |
|--------|----------|
| **Draw SU** | Load layer for drawing |
| **Preview SU plan** | Preview on map |
| **Open SU forms** | Opens selected forms |
| **Pan** | Pan tool |
| **Show images** | Display photos |

### Plate Exports

| Button | Output |
|--------|--------|
| **Plate Export** | Excavation plates |
| **symbology** | Symbology management |
| **Open folder** | Opens output folder |

---

## Harris Matrix

The Harris Matrix is a graphical representation of stratigraphic relationships.

<!-- IMAGE: Screenshot of harris matrix -->
![Harris Matrix](images/03_scheda_us/22_matrix_harris.png)
*Figure 22: Harris Matrix example*

<!-- VIDEO: Harris Matrix generation -->
> **Video Tutorial**: [Insert Harris Matrix video link]

### Matrix Generation

1. Select site and area
2. Verify relationships are correct
3. Go to **Help Tab** → **Tool Box**
4. Click **Export Matrix**

### Export Formats

| Format | Software | Use |
|--------|----------|-----|
| DOT | Graphviz | Basic visualization |
| GraphML | yEd, Gephi | Advanced editing |
| Extended Matrix | S3DGraphy | 3D visualization |
| CSV | Excel | Data analysis |

### Extended Matrix

The Extended Matrix adds supplementary information:
- Periodization
- Interpretive definitions
- Chronological data
- CIDOC-CRM compatibility

<!-- IMAGE: Screenshot of extended matrix -->
![Extended Matrix](images/03_scheda_us/23_extended_matrix.png)
*Figure 23: Extended Matrix dialog*

### Interactive Matrix

Interactive Matrix visualization:
- Zoom and pan
- Node selection
- Navigation to forms

---

## GIS Features

The SU Form is closely integrated with QGIS.

<!-- IMAGE: Screenshot of GIS integration -->
![GIS Integration](images/03_scheda_us/24_gis_integration.png)
*Figure 24: GIS Integration*

### GIS Toolbar

| Button | Function | Shortcut |
|--------|----------|----------|
| **GIS Viewer** | Load SU layers | Ctrl+G |
| **Preview SU plan** | Preview geometry | Ctrl+G |
| **Draw SU** | Activate drawing | - |

### Associated GIS Layers

| Layer | Geometry | Description |
|-------|----------|-------------|
| PYUS | Polygon | Stratigraphic units |
| PYUSM | Polygon | Wall units |
| PYQUOTE | Point | Elevations |
| PYQUOTEUSM | Point | WSU elevations |
| PYUS_NEGATIVE | Polygon | Negative SU |

### Search Results Visualization

When GIS mode is active:
- Searches are displayed on the map
- Results are highlighted
- You can navigate between results

---

## Exports

### PDF SU Forms

1. Click **Report** in toolbar
2. Choose format (PDF, Word)
3. Select forms to export

<!-- IMAGE: Screenshot of PDF export -->
![PDF Export](images/03_scheda_us/25_esportazione_pdf.png)
*Figure 25: PDF export options*

### Lists

| Type | Content |
|------|---------|
| **SU List** | List of all SU |
| **Photo List with Thumbnail** | List with previews |
| **Photo List without Thumbnail** | Simple list |
| **SU Forms** | Complete forms |

### Word Conversion

The **Convert to Word** button allows:
1. Selecting a PDF
2. Converting to DOCX format
3. Editing in Word

---

## Operational Workflow

### Creating a New SU

<!-- VIDEO: SU creation workflow -->
> **Video Tutorial**: [Insert SU creation video link]

#### Step 1: Open the Form
<!-- IMAGE: Step 1 -->
![Step 1](images/03_scheda_us/26_workflow_step1.png)

#### Step 2: Click New Record
<!-- IMAGE: Step 2 -->
![Step 2](images/03_scheda_us/27_workflow_step2.png)

#### Step 3: Enter Identification
- Select Site
- Enter Area
- Enter SU number
- Select Type

<!-- IMAGE: Step 3 -->
![Step 3](images/03_scheda_us/28_workflow_step3.png)

#### Step 4: Definitions
- Select stratigraphic definition
- Select interpretive definition

<!-- IMAGE: Step 4 -->
![Step 4](images/03_scheda_us/29_workflow_step4.png)

#### Step 5: Description
- Fill in physical description
- Fill in interpretation

<!-- IMAGE: Step 5 -->
![Step 5](images/03_scheda_us/30_workflow_step5.png)

#### Step 6: Stratigraphic Relationships
- Enter relationships with other SUs
- Create inverse relationships

<!-- IMAGE: Step 6 -->
![Step 6](images/03_scheda_us/31_workflow_step6.png)

#### Step 7: Physical Data and Measurements
- Fill in physical characteristics
- Enter measurements

<!-- IMAGE: Step 7 -->
![Step 7](images/03_scheda_us/32_workflow_step7.png)

#### Step 8: Save
- Click Save
- Verify save

<!-- IMAGE: Step 8 -->
![Step 8](images/03_scheda_us/33_workflow_step8.png)

### Generating the Harris Matrix

1. Verify all relationships are entered
2. Execute relationship check
3. Correct any errors
4. Export Matrix

### Linking Documentation

1. First create forms in Documentation table
2. In SU form, Documentation tab
3. Add references
4. Verify with "View documentation"

---

## Troubleshooting

### Save error
- Verify that Site, Area and SU are filled in
- Verify that the combination is unique

### Inconsistent relationships
- Use relationship check
- Verify inverse relationships
- Fix with Fix button

### Matrix not generating
- Verify Graphviz is installed
- Check path in configuration
- Verify relationships exist

### GIS layers not loading
- Verify database connection
- Check that geometries exist
- Verify coordinate reference system

### Images not displayed
- Verify thumbnail paths
- Check media associations
- Verify folder permissions

---

## Technical Notes

### Database

- **Main table**: `us_table`
- **Main fields**: over 80 fields
- **Primary key**: `id_us`
- **Composite key**: site + area + us

### Thesaurus

Fields with thesaurus (definitions) use table `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' for stratigraphic definition
- tipologia_sigla = '1.2' for interpretive definition

### GIS Layers

| Layer | Table | Type |
|-------|-------|------|
| PYUS | pyarchinit_us_view | Polygon |
| PYUSM | pyarchinit_usm_view | Polygon |
| PYQUOTE | pyarchinit_quote_view | Point |

---

*PyArchInit Documentation - SU/WSU Form*
*Version: 4.9.x*
*Last updated: January 2026*
