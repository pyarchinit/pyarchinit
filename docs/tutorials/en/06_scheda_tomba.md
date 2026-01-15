# Tutorial 06: Grave Form

## Introduction

The **Grave Form** is the PyArchInit module dedicated to documenting archaeological burials. This tool allows you to record all aspects of a tomb: from the funerary structure to the rite, from the grave goods to the buried individuals.

### Basic Concepts

**Grave in PyArchInit:**
- A grave is a funerary structure containing one or more individuals
- It is linked to the Structure Form (the physical structure of the burial)
- It is linked to the Individual Form (for anthropological data)
- It documents rite, grave goods, and deposition characteristics

**Relationships:**
```
Grave → Structure (physical container)
     → Individual(s) (human remains)
     → Grave goods (accompanying objects)
     → Materials Inventory (associated finds)
```

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **Grave Form**

![Menu access](images/06_scheda_tomba/02_menu_accesso.png)

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Grave** icon (burial symbol)

![Toolbar access](images/06_scheda_tomba/03_toolbar_accesso.png)

---

## Interface Overview

The form presents a layout organized into functional sections:

![Complete interface](images/06_scheda_tomba/04_interfaccia_completa.png)

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | DB Info | Record status, sorting, counter |
| 3 | Identification Fields | Site, Area, Form No., Structure |
| 4 | Individual Fields | Link to individual |
| 5 | Tab Area | Thematic tabs for specific data |

---

## DBMS Toolbar

The main toolbar provides tools for record management.

![DBMS Toolbar](images/06_scheda_tomba/05_toolbar_dbms.png)

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
| ![New](../../resources/icons/newrec.png) | New record | Create a new grave record |
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
| ![GIS](../../resources/icons/GIS.png) | GIS | Load grave to map |
| ![PDF](../../resources/icons/pdf-icon.png) | PDF export | Export to PDF |
| ![Directory](../../resources/icons/directoryExp.png) | Open directory | Open export folder |

---

## Identification Fields

The identification fields uniquely define the grave in the database.

![Identification fields](images/06_scheda_tomba/06_campi_identificativi.png)

### Site

**Field**: `comboBox_sito`
**Database**: `sito`

Select the archaeological site of belonging.

### Area

**Field**: `comboBox_area`
**Database**: `area`

Excavation area within the site.

### Form Number

**Field**: `lineEdit_nr_scheda`
**Database**: `nr_scheda_taf`

Progressive grave form number. The next available number is automatically proposed.

### Structure Code and Number

| Field | Database | Description |
|-------|----------|-------------|
| Structure code | `sigla_struttura` | Structure code (e.g., TM, TB) |
| Structure no. | `nr_struttura` | Structure number |

These fields link the grave to the corresponding Structure Form.

### Individual Number

**Field**: `comboBox_nr_individuo`
**Database**: `nr_individuo`

Number of the buried individual. Links the grave to the Individual Form.

**Notes:**
- A grave can contain multiple individuals (multiple burial)
- The menu shows available individuals for the selected structure

---

## Descriptive Data Tab

The first tab contains fundamental fields for describing the burial.

![Descriptive Data Tab](images/06_scheda_tomba/07_tab_descrittivi.png)

### Rite

**Field**: `comboBox_rito`
**Database**: `rito`

Type of funerary ritual practiced.

**Typical values:**
| Rite | Description |
|------|-------------|
| Inhumation | Deposition of whole body |
| Cremation | Incineration of remains |
| Primary cremation | On-site cremation |
| Secondary cremation | Cremation elsewhere and deposition |
| Mixed | Combination of rites |
| Undetermined | Not determinable |

### Burial Type

**Field**: `comboBox_tipo_sepoltura`
**Database**: `tipo_sepoltura`

Typological classification of the burial.

**Examples:**
- Simple pit grave
- Cist grave
- Chamber tomb
- Cappuccina tomb
- Enchytrismos tomb
- Sarcophagus
- Ossuary

### Deposition Type

**Field**: `comboBox_tipo_deposizione`
**Database**: `tipo_deposizione`

Body deposition method.

**Values:**
- Primary (direct deposition)
- Secondary (reduction/displacement)
- Simultaneous multiple
- Successive multiple

### Conservation Status

**Field**: `comboBox_stato_conservazione`
**Database**: `stato_di_conservazione`

Conservation status assessment.

**Scale:**
- Excellent
- Good
- Fair
- Poor
- Very poor

### Description

**Field**: `textEdit_descrizione`
**Database**: `descrizione_taf`

Detailed description of the grave.

**Recommended content:**
- Pit shape and dimensions
- Orientation
- Depth
- Fill characteristics
- Condition at time of excavation

### Interpretation

**Field**: `textEdit_interpretazione`
**Database**: `interpretazione_taf`

Historical-archaeological interpretation of the burial.

---

## Grave Characteristics

### Grave Markers

**Field**: `comboBox_segnacoli`
**Database**: `segnacoli`

Presence and type of grave markers.

**Values:**
- Absent
- Stele
- Cippus
- Tumulus
- Enclosure
- Other

### Libation Channel

**Field**: `comboBox_canale_libatorio`
**Database**: `canale_libatorio_si_no`

Presence of channel for ritual libations.

**Values:** Yes / No

### Cover

**Field**: `comboBox_copertura_tipo`
**Database**: `copertura_tipo`

Type of grave cover.

**Examples:**
- Tiles
- Stone slabs
- Wooden planks
- Earth
- Absent

### Remains Container

**Field**: `comboBox_tipo_contenitore`
**Database**: `tipo_contenitore_resti`

Container type for remains.

**Examples:**
- Earth pit
- Wooden box
- Stone box
- Amphora
- Urn
- Sarcophagus

### External Objects

**Field**: `comboBox_oggetti_esterno`
**Database**: `oggetti_rinvenuti_esterno`

Objects found outside the grave but associated with it.

---

## Grave Goods Tab

This tab manages documentation of grave goods.

![Grave Goods Tab](images/06_scheda_tomba/08_tab_corredo.png)

### Grave Goods Presence

**Field**: `comboBox_corredo_presenza`
**Database**: `corredo_presenza`

Indicates whether the grave contained grave goods.

**Values:**
- Yes
- No
- Probable
- Removed

### Grave Goods Type

**Field**: `comboBox_corredo_tipo`
**Database**: `corredo_tipo`

General classification of grave goods.

**Categories:**
- Personal (jewelry, fibulae)
- Ritual (vases, lamps)
- Symbolic (coins, amulets)
- Instrumental (tools)
- Mixed

### Grave Goods Description

**Field**: `textEdit_corredo_descrizione`
**Database**: `corredo_descrizione`

Detailed description of grave goods objects.

### Grave Goods Table

**Widget**: `tableWidget_corredo_tipo`

Table for recording individual grave goods elements.

**Columns:**
| Column | Description |
|--------|-------------|
| Find ID | Find inventory number |
| Indv. ID | Associated individual |
| Material | Material type |
| Position in grave | Where it was located in the tomb |
| Position relative to body | Position relative to the body |

**Notes:**
- Elements are linked to the Materials Inventory Form
- The table is automatically populated with finds from the structure

---

## Other Characteristics Tab

This tab contains additional information about the burial.

![Other Characteristics Tab](images/06_scheda_tomba/09_tab_altre.png)

### Periodization

| Field | Database | Description |
|-------|----------|-------------|
| Initial period | `periodo_iniziale` | Period of start of use |
| Initial phase | `fase_iniziale` | Phase in period |
| Final period | `periodo_finale` | Period of end of use |
| Final phase | `fase_finale` | Phase in period |
| Extended dating | `datazione_estesa` | Literal dating |

Values are populated based on the Periodization Form for the site.

---

## Tools Tab

The Tools tab contains additional features.

![Tools Tab](images/06_scheda_tomba/10_tab_tools.png)

### Media Management

Allows you to:
- View associated images
- Add new photos via drag & drop
- Search media in database

### Export

Export options:
- Grave List (synthetic list)
- Grave Forms (complete forms)
- PDF to Word conversion

---

## GIS Integration

### Map Visualization

| Button | Function |
|--------|----------|
| GIS Toggle | Enable/disable automatic loading |
| Load to GIS | Load grave to map |

### GIS Layers

The form uses specific layers for graves:
- **pyarchinit_tomba**: grave geometry
- Link with structure and SU layers

---

## Export and Print

### PDF Export

The PDF button opens a panel with options:

| Option | Description |
|--------|-------------|
| Grave List | Synthetic list of graves |
| Grave Forms | Complete detailed forms |
| Print | Generate PDF |

### PDF Form Content

The PDF form includes:
- Identification data
- Rite and burial type
- Description and interpretation
- Grave goods data
- Periodization
- Associated images

---

## Operational Workflow

### Creating a New Grave

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click "New Record"
   - Form number is automatically proposed

3. **Identification data**
   ```
   Site: Isola Sacra Necropolis
   Area: 1
   Form No.: 45
   Structure code: TM
   Structure no.: 45
   ```

4. **Individual link**
   ```
   Individual No.: 1
   ```

5. **Descriptive data** (Tab 1)
   ```
   Rite: Inhumation
   Burial type: Simple pit grave
   Deposition type: Primary
   Conservation status: Good

   Description: Rectangular pit with
   rounded corners, oriented E-W...

   Markers: Cippus
   Cover: Cappuccina tiles
   ```

6. **Grave goods** (Tab 2)
   ```
   Presence: Yes
   Type: Personal
   Description: Bronze fibula near right
   shoulder, coin near mouth...
   ```

7. **Periodization**
   ```
   Initial period: II - Phase A
   Final period: II - Phase A
   Dating: 2nd century AD
   ```

8. **Save**
   - Click "Save"

### Searching Graves

1. Click "New Search"
2. Fill in criteria:
   - Site
   - Rite
   - Burial type
   - Period
3. Click "Search"
4. Navigate through results

---

## Relationships with Other Forms

| Form | Relationship |
|------|--------------|
| **Site Form** | Site contains graves |
| **Structure Form** | Physical structure of the grave |
| **Individual Form** | Human remains in the grave |
| **Materials Inventory Form** | Grave goods finds |
| **Periodization Form** | Chronology |

### Recommended Workflow

1. Create **Site Form** (if not existing)
2. Create **Structure Form** for the grave
3. Create **Grave Form** linking to structure
4. Create **Individual Form** for each individual
5. Record grave goods in **Materials Inventory Form**

---

## Best Practices

### Naming

- Use consistent codes (TM, TB, SEP)
- Progressive numbering within site
- Document conventions adopted

### Description

- Systematically describe shape, dimensions, orientation
- Document condition at time of excavation
- Separate objective observations from interpretations

### Grave Goods

- Record exact position of each object
- Link each element to Materials Inventory
- Document significant associations

### Periodization

- Base dating on diagnostic elements
- Indicate reliability level
- Compare with similar burials

---

## Troubleshooting

### Problem: Individual not available in menu

**Cause**: Individual not yet created or not associated with structure.

**Solution**:
1. Verify Individual Form exists
2. Check individual is associated with the same structure

### Problem: Grave goods not displayed in table

**Cause**: Finds not linked to structure.

**Solution**:
1. Open Materials Inventory Form
2. Verify finds have correct structure
3. Refresh Grave Form

### Problem: Grave not visible on map

**Cause**: Geometry not associated.

**Solution**:
1. Verify grave layer exists
2. Check structure has geometry
3. Verify coordinate reference system

---

## References

### Database

- **Table**: `tomba_table`
- **Mapper class**: `TOMBA`
- **ID**: `id_tomba`

### Source Files

- **UI**: `gui/ui/Tomba.ui`
- **Controller**: `tabs/Tomba.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Video Tutorial

### Grave Form Overview
**Duration**: 5-6 minutes
- Interface presentation
- Main fields
- Tab navigation

[Video placeholder: video_panoramica_tomba.mp4]

### Complete Grave Documentation
**Duration**: 10-12 minutes
- New record creation
- All field completion
- Individual and grave goods linking

[Video placeholder: video_schedatura_tomba.mp4]

### Grave Goods Management
**Duration**: 6-8 minutes
- Recording grave goods elements
- Linking with Materials Inventory
- Position documentation

[Video placeholder: video_corredo_tomba.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
