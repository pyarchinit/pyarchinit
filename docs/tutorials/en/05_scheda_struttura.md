# Tutorial 05: Structure Form

## Introduction

The **Structure Form** is the PyArchInit module dedicated to documenting archaeological structures. A structure is an organized set of Stratigraphic Units (SU/WSU) that form a recognizable constructive or functional entity, such as a wall, a floor, a tomb, a kiln, or any other built element.

### Basic Concepts

**Structure vs Stratigraphic Unit:**
- An **SU** is the single unit (layer, cut, fill)
- A **Structure** groups multiple functionally related SUs
- Example: a wall (structure) is composed of foundation, elevation, mortar (different SUs)

**Hierarchies:**
- Structures can have relationships with each other
- Each structure belongs to one or more chronological periods/phases
- Structures are linked to the SUs that compose them

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **Structure Management** (or **Structure form**)

![Menu access](images/05_scheda_struttura/02_menu_accesso.png)

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Structure** icon (stylized building)

![Toolbar access](images/05_scheda_struttura/03_toolbar_accesso.png)

---

## Interface Overview

The form presents a layout organized into functional sections:

![Complete interface](images/05_scheda_struttura/04_interfaccia_completa.png)

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | DB Info | Record status, sorting, counter |
| 3 | Identification Fields | Site, Code, Structure number |
| 4 | Classification Fields | Category, Type, Definition |
| 5 | Tab Area | Thematic tabs for specific data |

---

## DBMS Toolbar

The main toolbar provides all tools for record management.

![DBMS Toolbar](images/05_scheda_struttura/05_toolbar_dbms.png)

### Navigation Buttons

| Icon | Function | Description |
|------|----------|-------------|
| ![First](../../resources/icons/5_leftArrows.png) | First rec | Go to first record |
| ![Prev](../../resources/icons/4_leftArrow.png) | Prev rec | Go to previous record |
| ![Next](../../resources/icons/6_rightArrow.png) | Next rec | Go to next record |
| ![Last](../../resources/icons/7_rightArrows.png) | Last rec | Go to last record |

### CRUD Buttons

| Icon | Function | Description |
|------|----------|-------------|
| ![New](../../resources/icons/newrec.png) | New record | Create a new structure record |
| ![Save](../../resources/icons/b_save.png) | Save | Save changes |
| ![Delete](../../resources/icons/delete.png) | Delete | Delete current record |

### Search Buttons

| Icon | Function | Description |
|------|----------|-------------|
| ![New Search](../../resources/icons/new_search.png) | New search | Start new search |
| ![Search](../../resources/icons/search.png) | Search!!! | Execute search |
| ![Sort](../../resources/icons/sort.png) | Order by | Sort results |
| ![View All](../../resources/icons/view_all.png) | View all | View all records |

### Special Buttons

| Icon | Function | Description |
|------|----------|-------------|
| ![Map Preview](map_preview.png) | Map preview | Enable/disable map preview |
| ![Media Preview](../../resources/icons/photo.png) | Media preview | Enable/disable media preview |
| ![Draw Structure](../../resources/icons/iconStrutt.png) | Draw structure | Draw structure on map |
| ![GIS](../../resources/icons/GIS.png) | Load to GIS | Load structure to map |
| ![Layers](../../resources/icons/layers-icon.png) | Load all | Load all structures |
| ![PDF](../../resources/icons/pdf-icon.png) | PDF export | Export to PDF |
| ![Directory](../../resources/icons/directoryExp.png) | Open directory | Open export folder |

---

## Identification Fields

The identification fields uniquely define the structure in the database.

![Identification fields](images/05_scheda_struttura/06_campi_identificativi.png)

### Site

**Field**: `comboBox_sito`
**Database**: `sito`

Select the archaeological site of belonging. The dropdown menu shows all sites registered in the database.

**Notes:**
- Required field
- Site + Code + Number combination must be unique
- Locked after record creation

### Structure Code

**Field**: `comboBox_sigla_struttura`
**Database**: `sigla_struttura`

Alphanumeric code identifying the structure type. Common conventions:

| Code | Meaning | Example |
|------|---------|---------|
| WL | Wall | WL 1 |
| ST | Structure | ST 5 |
| FL | Floor | FL 2 |
| KN | Kiln | KN 1 |
| TK | Tank | TK 3 |
| TB | Tomb | TB 10 |
| WE | Well | WE 2 |
| CN | Channel | CN 1 |

**Notes:**
- Editable with free input
- Locked after creation

### Structure Number

**Field**: `numero_struttura`
**Database**: `numero_struttura`

Progressive structure number within the code.

**Notes:**
- Numeric field
- Must be unique for Site + Code combination
- Locked after creation

---

## Synchronization with SU Form

Structures created in this form automatically appear in the **Structure** field of the **SU Form** for the same site.

### How the link works

1. **Create the structure** filling in at least:
   - **Site**: the archaeological site (e.g., "Rome_Forum")
   - **Code**: the structure code (e.g., "MUR")
   - **Number**: the progressive number (e.g., 1)
   - Save the record

2. **In the SU Form** for the same site:
   - The **Structure** field will show the structure in format `CODE-NUMBER`
   - Example: "MUR-1", "PV-2", "ST-3"

### Display format

Structures appear in the SU Form in the format:
```
STRUCTURE_CODE - STRUCTURE_NUMBER
```

**Examples:**
| Structure Form | Displayed in SU Form |
|----------------|----------------------|
| Site=Rome, Code=MUR, Number=1 | MUR-1 |
| Site=Rome, Code=PV, Number=2 | PV-2 |
| Site=Rome, Code=ST, Number=10 | ST-10 |

### Important notes

- The structure must be **saved** before appearing in the SU Form
- Only structures from the **same site** are visible
- In the SU Form you can **select multiple structures** (multi-selection with checkboxes)
- To **remove** a structure from the SU: open the dropdown menu and uncheck the box
- To **clear** all structures: right-click → "Clear Structure field"

---

## Classification Fields

Classification fields define the nature of the structure.

![Classification fields](images/05_scheda_struttura/07_campi_classificazione.png)

### Structure Category

**Field**: `comboBox_categoria_struttura`
**Database**: `categoria_struttura`

Functional macro-category of the structure.

**Typical values:**
- Residential
- Productive
- Funerary
- Religious
- Defensive
- Hydraulic
- Road
- Artisanal

### Structure Type

**Field**: `comboBox_tipologia_struttura`
**Database**: `tipologia_struttura`

Specific type within the category.

**Examples by category:**
| Category | Types |
|----------|-------|
| Residential | House, Villa, Palace, Hut |
| Productive | Kiln, Mill, Olive press |
| Funerary | Pit tomb, Chamber tomb, Sarcophagus |
| Hydraulic | Well, Cistern, Aqueduct, Channel |

### Structure Definition

**Field**: `comboBox_definizione_struttura`
**Database**: `definizione_struttura`

Synthetic and specific definition of the structural element.

**Examples:**
- Perimeter wall
- Cocciopesto floor
- Stone threshold
- Stairway
- Column base

---

## Descriptive Data Tab

The first tab contains text fields for detailed description.

![Descriptive Data Tab](images/05_scheda_struttura/08_tab_descrittivi.png)

### Description

**Field**: `textEdit_descrizione_struttura`
**Database**: `descrizione`

Free text field for physical description of the structure.

**Recommended content:**
- Construction technique
- Materials used
- Conservation status
- General dimensions
- Orientation
- Peculiar characteristics

**Example:**
```
Wall in opus incertum built with local limestone blocks
of variable size (15-30 cm). Whitish lime mortar binder.
Preserved to a maximum height of 1.20 m.
Average width 50 cm. NE-SW orientation. Shows traces
of plaster on the internal side.
```

### Interpretation

**Field**: `textEdit_interpretazione_struttura`
**Database**: `interpretazione`

Functional and historical interpretation of the structure.

**Recommended content:**
- Hypothesized original function
- Phases of use/reuse
- Typological comparisons
- Chronological framework
- Relationships with other structures

**Example:**
```
North perimeter wall of a residential building from Roman
Imperial age. Construction technique and materials suggest
dating to the 2nd century AD. In a later phase (3rd-4th century)
the wall was partially spoliated and incorporated into a
productive structure.
```

---

## Periodization Tab

This tab manages the chronological framework of the structure.

![Periodization Tab](images/05_scheda_struttura/09_tab_periodizzazione.png)

### Initial Period and Phase

| Field | Database | Description |
|-------|----------|-------------|
| Initial Period | `periodo_iniziale` | Construction/start of use period |
| Initial Phase | `fase_iniziale` | Phase within the period |

Values are automatically populated based on periods defined in the Periodization Form for the selected site.

### Final Period and Phase

| Field | Database | Description |
|-------|----------|-------------|
| Final Period | `periodo_finale` | Abandonment/dismissal period |
| Final Phase | `fase_finale` | Phase within the period |

### Extended Dating

**Field**: `comboBox_datazione_estesa`
**Database**: `datazione_estesa`

Literal dating calculated automatically or entered manually.

**Formats:**
- "1st century BC - 2nd century AD"
- "100 BC - 200 AD"
- "Roman Imperial age"

**Notes:**
- Automatically proposed based on period/phase
- Manually editable for special cases

---

## Relationships Tab

This tab manages relationships between structures.

![Relationships Tab](images/05_scheda_struttura/10_tab_rapporti.png)

### Structure Relationships Table

**Widget**: `tableWidget_rapporti`
**Database**: `rapporti_struttura`

Records relationships between current structure and other structures.

**Columns:**
| Column | Description |
|--------|-------------|
| Relationship type | Stratigraphic/functional relationship |
| Site | Related structure site |
| Code | Related structure code |
| Number | Related structure number |

**Relationship types:**

| Relationship | Inverse | Description |
|--------------|---------|-------------|
| Bonds with | Bonds with | Contemporary physical connection |
| Covers | Covered by | Overlapping relationship |
| Cuts | Cut by | Cutting relationship |
| Fills | Filled by | Filling relationship |
| Abuts | Supports | Abutment relationship |
| Same as | Same as | Same structure with different name |

### Row Management

| Button | Function |
|--------|----------|
| + | Add new row |
| - | Remove selected row |

---

## Construction Elements Tab

This tab documents materials and elements composing the structure.

![Construction Elements Tab](images/05_scheda_struttura/11_tab_elementi.png)

### Materials Used

**Widget**: `tableWidget_materiali_impiegati`
**Database**: `materiali_impiegati`

List of materials used in construction.

**Column:**
- Materials: material description

**Material examples:**
- Limestone blocks
- Bricks
- Lime mortar
- River pebbles
- Tiles
- Marble
- Tuff

### Structural Elements

**Widget**: `tableWidget_elementi_strutturali`
**Database**: `elementi_strutturali`

List of construction elements with quantities.

**Columns:**
| Column | Description |
|--------|-------------|
| Element type | Type of element |
| Quantity | Number of elements |

**Element examples:**
| Element | Quantity |
|---------|----------|
| Column base | 4 |
| Capital | 2 |
| Threshold | 1 |
| Squared block | 45 |

### Row Management

For both tables:
| Button | Function |
|--------|----------|
| + | Add new row |
| - | Remove selected row |

---

## Measurements Tab

This tab records structure dimensions.

![Measurements Tab](images/05_scheda_struttura/12_tab_misure.png)

### Measurements Table

**Widget**: `tableWidget_misurazioni`
**Database**: `misure_struttura`

**Columns:**
| Column | Description |
|--------|-------------|
| Measurement type | Type of dimension |
| Unit of measure | m, cm, sq m, etc. |
| Value | Numeric value |

### Common Measurement Types

| Type | Description |
|------|-------------|
| Length | Larger dimension |
| Width | Smaller dimension |
| Preserved height | Preserved elevation |
| Original height | Estimated original elevation |
| Depth | For sunken structures |
| Diameter | For circular structures |
| Thickness | For walls, floors |
| Surface area | Area in sq m |

### Compilation Example

| Measurement type | Unit of measure | Value |
|------------------|-----------------|-------|
| Length | m | 8.50 |
| Width | cm | 55 |
| Preserved height | m | 1.20 |
| Surface area | sq m | 4.68 |

---

## Media Tab

Management of images, videos, and 3D models associated with the structure.

![Media Tab](images/05_scheda_struttura/13_tab_media.png)

### Features

**Widget**: `iconListWidget`

Displays thumbnails of associated media.

### Buttons

| Icon | Function | Description |
|------|----------|-------------|
| ![All Images](../../resources/icons/photo2.png) | All images | Show all images |
| ![Remove Tags](../../resources/icons/remove_tag.png) | Remove tags | Remove media association |
| ![Search](../../resources/icons/search.png) | Search images | Search images in database |

### Drag & Drop

You can drag files directly onto the form:

**Supported formats:**
- Images: JPG, JPEG, PNG, TIFF, TIF, BMP
- Video: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Viewing

- **Double click** on thumbnail: opens viewer
- For video: opens integrated video player
- For 3D: opens PyVista 3D viewer

---

## Map Tab

Preview of structure position on map.

![Map Tab](images/05_scheda_struttura/14_tab_map.png)

### Features

- Displays structure geometry
- Automatic zoom on element
- Integration with project GIS layers

---

## GIS Integration

### Map Visualization

| Button | Function |
|--------|----------|
| Map Preview | Toggle preview in Map tab |
| Draw Structure | Highlight structure on QGIS map |
| Load to GIS | Load structures layer |
| Load All | Load all site structures |

### GIS Layers

The form uses **pyarchinit_strutture** layer for visualization:
- Geometry: polygon or multipolygon
- Attributes linked to form fields

---

## Export and Print

### PDF Export

![Export Panel](images/05_scheda_struttura/15_export_panel.png)

The PDF button opens a panel with export options:

| Option | Description |
|--------|-------------|
| Structure List | Synthetic list of structures |
| Structure Forms | Complete detailed forms |
| Print | Generate PDF |
| Convert to Word | Convert PDF to Word format |

### PDF to Word Conversion

Advanced feature to convert generated PDFs to editable Word documents:

1. Select PDF file to convert
2. Specify page range (optional)
3. Click "Convert"
4. Word file is saved in the same folder

---

## Operational Workflow

### Creating a New Structure

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click "New Record" button
   - Identification fields become editable

3. **Identification data**
   ```
   Site: Roman Villa of Settefinestre
   Code: WL
   Number: 15
   ```

4. **Classification**
   ```
   Category: Residential
   Type: Perimeter wall
   Definition: Opus incertum wall
   ```

5. **Descriptive data** (Tab 1)
   ```
   Description: Wall built in opus incertum with
   local limestone blocks...

   Interpretation: North boundary of the domus, phase I
   of the residential complex...
   ```

6. **Periodization** (Tab 2)
   ```
   Initial period: I - Phase: A
   Final period: II - Phase: B
   Dating: 1st century BC - 2nd century AD
   ```

7. **Relationships** (Tab 3)
   ```
   Bonds with: WL 16, WL 17
   Cut by: ST 5
   ```

8. **Construction elements** (Tab 4)
   ```
   Materials: Limestone blocks, Lime mortar
   Elements: Squared blocks (52), Threshold (1)
   ```

9. **Measurements** (Tab 5)
   ```
   Length: 12.50 m
   Width: 0.55 m
   Preserved height: 1.80 m
   ```

10. **Save**
    - Click "Save"
    - Verify save confirmation

### Searching Structures

1. Click "New Search"
2. Fill in one or more filter fields:
   - Site
   - Structure code
   - Category
   - Period
3. Click "Search"
4. Navigate through results

### Modifying Existing Structure

1. Navigate to desired record
2. Modify necessary fields
3. Click "Save"

---

## Best Practices

### Naming

- Use consistent codes throughout the project
- Document conventions used
- Avoid duplicate numbering

### Description

- Be systematic in description
- Follow a schema: technique > materials > dimensions > status
- Separate objective description from interpretation

### Periodization

- Always link to periods defined in Periodization Form
- Indicate both initial and final phase
- Use extended dating for synthesis

### Relationships

- Record all significant relationships
- Verify relationship reciprocity
- Link to SUs composing the structure

### Media

- Associate representative photos
- Include construction detail photos
- Document excavation phases

---

## Troubleshooting

### Problem: Structure not visible on map

**Cause**: Geometry not associated or layer not loaded.

**Solution**:
1. Verify `pyarchinit_strutture` layer exists
2. Check structure has associated geometry
3. Verify coordinate reference system

### Problem: Periods not available

**Cause**: Periods not defined for the site.

**Solution**:
1. Open Periodization Form
2. Define periods for current site
3. Return to Structure Form

### Problem: Save error "existing record"

**Cause**: Site + Code + Number combination already exists.

**Solution**:
1. Verify existing numbering
2. Use a free progressive number
3. Check for duplicates

### Problem: Media not displayed

**Cause**: Image path incorrect.

**Solution**:
1. Verify path in configuration
2. Check files exist
3. Regenerate thumbnails if necessary

---

## Relationships with Other Forms

| Form | Relationship |
|------|--------------|
| **Site Form** | Site contains structures |
| **SU Form** | SUs compose structures |
| **Periodization Form** | Provides chronology |
| **Materials Inventory Form** | Finds associated with structures |
| **Tomb Form** | Tombs as special type of structure |

---

## References

### Database

- **Table**: `struttura_table`
- **Mapper class**: `STRUTTURA`
- **ID**: `id_struttura`

### Source Files

- **UI**: `gui/ui/Struttura.ui`
- **Controller**: `tabs/Struttura.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Video Tutorial

### Structure Form Overview
**Duration**: 5-6 minutes
- General interface presentation
- Tab navigation
- Main features

[Video placeholder: video_panoramica_struttura.mp4]

### Complete Structure Documentation
**Duration**: 10-12 minutes
- New record creation
- Filling all fields
- Managing relationships and measurements

[Video placeholder: video_schedatura_struttura.mp4]

### GIS Integration and Export
**Duration**: 6-8 minutes
- Map visualization
- Layer loading
- PDF and Word export

[Video placeholder: video_gis_export_struttura.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
