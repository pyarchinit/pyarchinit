# Tutorial 07: Individual Form

## Introduction

The **Individual Form** is the PyArchInit module dedicated to anthropological documentation of human remains found during excavation. This form records information on sex, age, body position, and skeletal conservation status.

### Basic Concepts

**Individual in PyArchInit:**
- An individual is a set of bone remains attributable to a single person
- It is linked to the Grave Form (burial context)
- It is linked to the Structure Form (physical structure)
- It can be linked to Archaeozoology for specific analyses

**Anthropological Data:**
- Biological sex estimation
- Age at death estimation
- Body position and orientation
- Conservation status and completeness

---

## Accessing the Form

### Via Menu
1. **PyArchInit** menu in the QGIS menu bar
2. Select **Individual Form**

![Menu access](images/07_scheda_individui/02_menu_accesso.png)

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Individual** icon (human figure)

![Toolbar access](images/07_scheda_individui/03_toolbar_accesso.png)

---

## Interface Overview

The form presents a layout organized into functional sections:

![Complete interface](images/07_scheda_individui/04_interfaccia_completa.png)

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | DB Info | Record status, sorting, counter |
| 3 | Identification Fields | Site, Area, SU, Individual No. |
| 4 | Structure Link | Code and structure number |
| 5 | Tab Area | Thematic tabs for specific data |

---

## DBMS Toolbar

The main toolbar provides tools for record management.

![DBMS Toolbar](images/07_scheda_individui/05_toolbar_dbms.png)

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
| ![New](../../resources/icons/newrec.png) | New record | Create a new individual record |
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
| ![PDF](../../resources/icons/pdf-icon.png) | PDF export | Export to PDF |
| ![Directory](../../resources/icons/directoryExp.png) | Open directory | Open export folder |

---

## Identification Fields

The identification fields uniquely define the individual in the database.

![Identification fields](images/07_scheda_individui/06_campi_identificativi.png)

### Site

**Field**: `comboBox_sito`
**Database**: `sito`

Select the archaeological site of belonging.

### Area

**Field**: `comboBox_area`
**Database**: `area`

Excavation area within the site. Values are populated from thesaurus.

### SU

**Field**: `comboBox_us`
**Database**: `us`

Reference Stratigraphic Unit.

### Individual Number

**Field**: `lineEdit_individuo`
**Database**: `nr_individuo`

Progressive individual number. The next available number is automatically proposed.

**Notes:**
- The combination Site + Area + SU + Individual No. must be unique
- Number is automatically assigned at creation

### Structure Link

| Field | Database | Description |
|-------|----------|-------------|
| Structure code | `sigla_struttura` | Structure code (e.g., TM) |
| Structure no. | `nr_struttura` | Structure number |

These fields link the individual to the funerary structure.

---

## Filing Data

![Filing data](images/07_scheda_individui/07_dati_schedatura.png)

### Filing Date

**Field**: `dateEdit_schedatura`
**Database**: `data_schedatura`

Form compilation date.

### Recorder

**Field**: `comboBox_schedatore`
**Database**: `schedatore`

Name of operator compiling the form.

---

## Descriptive Data Tab

The first tab contains fundamental anthropological data.

![Descriptive Data Tab](images/07_scheda_individui/08_tab_descrittivi.png)

### Sex Estimation

**Field**: `comboBox_sesso`
**Database**: `sesso`

Biological sex estimation based on morphological characters.

**Values:**
| Value | Description |
|-------|-------------|
| Male | Clear male characters |
| Female | Clear female characters |
| Probable male | Predominantly male characters |
| Probable female | Predominantly female characters |
| Undetermined | Not determinable |

**Determination criteria:**
- Pelvis morphology
- Skull morphology
- General skeletal robustness
- Bone dimensions

### Age at Death Estimation

| Field | Database | Description |
|-------|----------|-------------|
| Minimum age | `eta_min` | Lower limit of estimate |
| Maximum age | `eta_max` | Upper limit of estimate |

**Estimation methods:**
- Pubic symphysis
- Auricular surface
- Cranial sutures
- Dental development (for subadults)
- Bone epiphyses (for subadults)

### Age Classes

**Field**: `comboBox_classi_eta`
**Database**: `classi_eta`

Age group classification.

**Typical values:**
| Class | Approximate age |
|-------|-----------------|
| Infans I | 0-6 years |
| Infans II | 7-12 years |
| Juvenis | 13-20 years |
| Adultus | 21-40 years |
| Maturus | 41-60 years |
| Senilis | >60 years |

### Observations

**Field**: `textEdit_osservazioni`
**Database**: `osservazioni`

Text field for specific anthropological notes.

**Recommended content:**
- Observed pathologies
- Traumas
- Occupational markers
- Skeletal anomalies
- Notes on sex and age determination

---

## Orientation and Position Tab

This tab documents body position and orientation.

![Orientation Tab](images/07_scheda_individui/09_tab_orientamento.png)

### Conservation Status

| Field | Database | Values |
|-------|----------|--------|
| Complete | `completo_si_no` | Yes / No |
| Disturbed | `disturbato_si_no` | Yes / No |
| In articulation | `in_connessione_si_no` | Yes / No |

**Definitions:**
- **Complete**: all anatomical districts are represented
- **Disturbed**: evidence of post-depositional disturbance
- **In articulation**: articulations are preserved

### Skeleton Length

**Field**: `lineEdit_lunghezza`
**Database**: `lunghezza_scheletro`

Measured skeleton length in situ (in cm or m).

### Skeleton Position

**Field**: `comboBox_posizione_scheletro`
**Database**: `posizione_scheletro`

General body position.

**Values:**
- Supine (on back)
- Prone (face down)
- Right lateral
- Left lateral
- Crouched
- Irregular

### Skull Position

**Field**: `comboBox_posizione_cranio`
**Database**: `posizione_cranio`

Head orientation.

**Values:**
- Facing right
- Facing left
- Facing up
- Facing down
- Not determinable

### Upper Limbs Position

**Field**: `comboBox_arti_superiori`
**Database**: `posizione_arti_superiori`

Arm position.

**Values:**
- Extended along sides
- On pelvis
- On chest
- Crossed on chest
- Mixed
- Not determinable

### Lower Limbs Position

**Field**: `comboBox_arti_inferiori`
**Database**: `posizione_arti_inferiori`

Leg position.

**Values:**
- Extended
- Flexed
- Crossed
- Spread
- Not determinable

### Axis Orientation

**Field**: `comboBox_orientamento_asse`
**Database**: `orientamento_asse`

Body longitudinal axis orientation.

**Values:**
- N-S (head to North)
- S-N (head to South)
- E-W (head to East)
- W-E (head to West)
- NE-SW, NW-SE, etc.

### Azimuth Orientation

**Field**: `lineEdit_azimut`
**Database**: `orientamento_azimut`

Numeric azimuth value in degrees (0-360).

---

## Osteological Remains Tab

This tab is dedicated to documenting anatomical districts.

![Osteological Remains Tab](images/07_scheda_individui/10_tab_osteologici.png)

### District Documentation

Allows recording:
- Presence/absence of individual bone elements
- Conservation status by district
- Side (right/left) for paired elements

**Main districts:**
| District | Elements |
|----------|----------|
| Skull | Calvaria, mandible, teeth |
| Spine | Cervical, thoracic, lumbar vertebrae, sacrum |
| Thorax | Ribs, sternum |
| Upper limbs | Clavicles, scapulae, humeri, radius, ulna, hands |
| Pelvis | Coxae |
| Lower limbs | Femora, tibia, fibula, feet |

---

## Other Characteristics Tab

This tab contains additional information.

![Other Characteristics Tab](images/07_scheda_individui/11_tab_altre.png)

### Contents

- Specific metric characteristics
- Anthropometric indices
- Detailed pathologies
- Relationships with other individuals

---

## Export and Print

### PDF Export

The PDF button opens a panel with options:

| Option | Description |
|--------|-------------|
| Individual List | Synthetic list |
| Individual Forms | Complete detailed forms |
| Print | Generate PDF |

### PDF Form Content

The PDF form includes:
- Identification data
- Anthropological data (sex, age)
- Position and orientation
- Conservation status
- Observations

---

## Operational Workflow

### Creating a New Individual

1. **Open form**
   - Via menu or toolbar

2. **New record**
   - Click "New Record"
   - Individual number is automatically proposed

3. **Identification data**
   ```
   Site: Isola Sacra Necropolis
   Area: 1
   SU: 150
   Individual No.: 1
   Structure code: TM
   Structure no.: 45
   ```

4. **Filing data**
   ```
   Date: 15/03/2024
   Recorder: M. Rossi
   ```

5. **Anthropological data** (Tab 1)
   ```
   Sex: Male
   Min age: 35
   Max age: 45
   Age class: Adultus

   Observations: Estimated stature 170 cm.
   Lumbar arthritis. Multiple caries.
   ```

6. **Orientation and Position** (Tab 2)
   ```
   Complete: Yes
   Disturbed: No
   In articulation: Yes
   Length: 165 cm
   Position: Supine
   Skull: Facing right
   Upper limbs: Extended along sides
   Lower limbs: Extended
   Orientation: E-W
   Azimuth: 90
   ```

7. **Osteological remains** (Tab 3)
   - Document present districts

8. **Save**
   - Click "Save"

### Searching Individuals

1. Click "New Search"
2. Fill in criteria:
   - Site
   - Sex
   - Age class
   - Position
3. Click "Search"
4. Navigate through results

---

## Relationships with Other Forms

| Form | Relationship |
|------|--------------|
| **Site Form** | Site contains individuals |
| **Structure Form** | Structure contains individual |
| **Grave Form** | Grave documents context |
| **Archaeozoology** | For specific osteological analyses |

### Recommended Workflow

1. Create **Structure Form** for the grave
2. Create **Grave Form**
3. Create **Individual Form** for each skeleton
4. Link individual to grave and structure

---

## Best Practices

### Sex Determination

- Use multiple morphological indicators
- Indicate reliability level
- Specify criteria used in observations

### Age Estimation

- Always provide a range (min-max)
- Indicate methods used
- For subadults, specify dental and epiphyseal development

### Position and Orientation

- Document with photos before removal
- Use cardinal references
- Measure azimuth with compass

### Conservation

- Distinguish taphonomic losses from ancient removals
- Document post-depositional disturbances
- Record recovery conditions

---

## Troubleshooting

### Problem: Duplicate individual number

**Cause**: An individual with the same number already exists.

**Solution**:
1. Verify existing numbering
2. Use automatically proposed number
3. Check area and SU

### Problem: Structure not found

**Cause**: Structure doesn't exist or has different code.

**Solution**:
1. Verify Structure Form exists
2. Check code and number
3. Create structure first if necessary

### Problem: Age classes not available

**Cause**: Thesaurus not configured.

**Solution**:
1. Verify thesaurus configuration
2. Check language setting
3. Contact administrator

---

## References

### Database

- **Table**: `individui_table`
- **Mapper class**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### Source Files

- **UI**: `gui/ui/Schedaind.ui`
- **Controller**: `tabs/Schedaind.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Video Tutorial

### Individual Form Overview
**Duration**: 5-6 minutes
- Interface presentation
- Main fields
- Tab navigation

[Video placeholder: video_panoramica_individui.mp4]

### Complete Anthropological Documentation
**Duration**: 12-15 minutes
- New record creation
- Sex and age determination
- Position documentation
- Osteological remains recording

[Video placeholder: video_schedatura_individui.mp4]

### Grave-Individual Link
**Duration**: 5-6 minutes
- Form relationships
- Correct workflow
- Best practices

[Video placeholder: video_collegamento_tomba_individuo.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*
