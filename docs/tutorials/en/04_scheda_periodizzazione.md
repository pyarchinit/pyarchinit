# Tutorial 04: Periodization Form

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [Fundamental Concepts](#fundamental-concepts)
5. [Form Fields](#form-fields)
6. [DBMS Toolbar](#dbms-toolbar)
7. [GIS Features](#gis-features)
8. [PDF Export](#pdf-export)
9. [AI Integration](#ai-integration)
10. [Operational Workflow](#operational-workflow)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

The **Periodization Form** is a fundamental tool for managing the chronological phases of an archaeological excavation. It allows you to define the periods and phases that characterize the stratigraphic sequence of the site, associating a chronological dating and description with each period/phase pair.

### Purpose of the Form

- Define the chronological sequence of the excavation
- Associate periods and phases with stratigraphic units
- Manage absolute (years) and relative (historical periods) chronology
- Display SUs by period/phase on the GIS map
- Generate PDF reports of periodization

### Relationship with Other Forms

The Periodization Form is closely linked to:
- **SU/WSU Form**: Each SU is assigned to a period and phase
- **Site Form**: Periods are specific to each site
- **Harris Matrix**: Periods color the Matrix by chronological phase

![Periodization Form Overview](images/04_scheda_periodizzazione/01_panoramica.png)
*Figure 1: General view of the Periodization Form*

---

## Accessing the Form

### From Menu

1. Open QGIS with the PyArchInit plugin active
2. Menu **PyArchInit** → **Archaeological record management** → **Excavation - Loss of use calculation** → **Period and Phase**

![Periodization Menu](images/04_scheda_periodizzazione/02_menu_accesso.png)
*Figure 2: Accessing the form from menu*

### From Toolbar

1. Locate the PyArchInit toolbar
2. Click on the **Periodization** icon (site icon with clock)

![Periodization Toolbar](images/04_scheda_periodizzazione/03_toolbar_accesso.png)
*Figure 3: Icon in toolbar*

---

## User Interface

The Periodization Form interface is organized in a simple, linear manner:

![Complete Interface](images/04_scheda_periodizzazione/04_interfaccia_completa.png)
*Figure 4: Complete interface layout*

### Main Areas

| Area | Description |
|------|-------------|
| **1. DBMS Toolbar** | Toolbar for navigation and record management |
| **2. Status Indicators** | DB Info, Status, Sorting |
| **3. Identification Data** | Site, Period, Phase, Period code |
| **4. Descriptive Data** | Textual description of the period |
| **5. Chronology** | Initial and final years |
| **6. Extended Dating** | Selection from historical epochs vocabulary |

---

## Fundamental Concepts

### Period and Phase

The periodization system in PyArchInit is based on a two-level hierarchical structure:

#### Period
The **Period** represents a macro-chronological phase of the excavation. It is identified by an integer (1, 2, 3, ...) and represents the major subdivisions of the stratigraphic sequence.

Period examples:
- Period 1: Contemporary age
- Period 2: Medieval age
- Period 3: Roman Imperial age
- Period 4: Roman Republican age

#### Phase
The **Phase** represents an internal subdivision of the period. It is also identified by an integer and allows further detailing of the sequence.

Phase examples in Period 3 (Roman Imperial age):
- Phase 1: 3rd-4th century AD
- Phase 2: 2nd century AD
- Phase 3: 1st century AD

### Period Code

The **Period Code** is a unique numeric identifier that links the period/phase pair to the SUs. When you assign a period/phase to an SU in the SU Form, this code is used.

> **Important**: The period code must be unique for each site/period/phase combination.

### Conceptual Schema

```
Site
└── Period 1 (Contemporary age)
│   ├── Phase 1 → Code 101
│   └── Phase 2 → Code 102
├── Period 2 (Medieval age)
│   ├── Phase 1 → Code 201
│   ├── Phase 2 → Code 202
│   └── Phase 3 → Code 203
└── Period 3 (Roman age)
    ├── Phase 1 → Code 301
    └── Phase 2 → Code 302
```

---

## Form Fields

### Identification Fields

#### Site
- **Type**: ComboBox (read-only in browse mode)
- **Required**: Yes
- **Description**: Select the archaeological site to which the periodization belongs
- **Notes**: If a default site is set in configuration, this field will be pre-filled and not editable

![Site Field](images/04_scheda_periodizzazione/05_campo_sito.png)
*Figure 5: Site selection field*

#### Period
- **Type**: Editable ComboBox
- **Required**: Yes
- **Values**: Integers from 1 to 15 (predefined) or custom values
- **Description**: Period chronological number
- **Notes**: Lower numbers indicate more recent periods, higher numbers indicate older periods

#### Phase
- **Type**: Editable ComboBox
- **Required**: Yes
- **Values**: Integers from 1 to 15 (predefined) or custom values
- **Description**: Phase number within the period

![Period and Phase Fields](images/04_scheda_periodizzazione/06_campi_periodo_fase.png)
*Figure 6: Period and Phase fields*

#### Period Code
- **Type**: LineEdit (text)
- **Required**: No (but strongly recommended)
- **Description**: Unique numeric code to identify the period/phase pair
- **Suggestion**: Use a convention like `[period][phase]` (e.g., 101, 102, 201, 301)

![Period Code Field](images/04_scheda_periodizzazione/07_codice_periodo.png)
*Figure 7: Period Code field*

### Descriptive Fields

#### Description
- **Type**: TextEdit (multiline)
- **Required**: No
- **Description**: Textual description of the period/phase
- **Suggested content**:
  - General characteristics of the period
  - Related historical events
  - Expected structure/material types
  - Bibliographic references

![Description Field](images/04_scheda_periodizzazione/08_campo_descrizione.png)
*Figure 8: Description field*

### Chronological Fields

#### Initial Chronology
- **Type**: LineEdit (numeric)
- **Required**: No
- **Format**: Numeric year
- **Notes**:
  - Positive values = AD
  - Negative values = BC
  - Example: `-100` for 100 BC, `200` for 200 AD

#### Final Chronology
- **Type**: LineEdit (numeric)
- **Required**: No
- **Format**: Numeric year (same conventions as Initial Chronology)

![Chronology Fields](images/04_scheda_periodizzazione/09_campi_cronologia.png)
*Figure 9: Initial and Final Chronology fields*

#### Extended Dating (Historical Epochs)
- **Type**: Editable ComboBox with preloaded vocabulary
- **Required**: No
- **Description**: Selection from a vocabulary of predefined historical epochs
- **Automatic feature**: When selecting an epoch, the Initial and Final Chronology fields are filled automatically

![Extended Dating](images/04_scheda_periodizzazione/10_datazione_estesa.png)
*Figure 10: Extended Dating ComboBox with preloaded epochs*

### Historical Epochs Vocabulary

The vocabulary includes a wide range of historical periods:

| Category | Examples |
|----------|----------|
| **Contemporary Age** | 21st century, 20th century |
| **Modern Age** | 19th-16th century |
| **Medieval Age** | 15th-8th century |
| **Ancient Age** | 7th-1st century |
| **Roman Empire** | Specific periods (Julio-Claudian, Flavian, etc.) |
| **Byzantine Empire** | Specific periods |
| **Prehistory** | Paleolithic, Mesolithic, Neolithic, Bronze Age, Iron Age |

---

## DBMS Toolbar

The DBMS toolbar allows complete record management:

![DBMS Toolbar](images/04_scheda_periodizzazione/11_toolbar_dbms.png)
*Figure 11: Complete DBMS toolbar*

### Navigation Buttons

| Icon | Name | Function | Shortcut |
|------|------|----------|----------|
| ![First](images/icons/first.png) | First | Go to first record | - |
| ![Prev](images/icons/prev.png) | Prev | Go to previous record | - |
| ![Next](images/icons/next.png) | Next | Go to next record | - |
| ![Last](images/icons/last.png) | Last | Go to last record | - |

### Record Management Buttons

| Icon | Name | Function |
|------|------|----------|
| ![New](images/icons/new.png) | New record | Create a new record |
| ![Save](images/icons/save.png) | Save | Save changes |
| ![Delete](images/icons/delete.png) | Delete | Delete current record |
| ![View All](images/icons/view_all.png) | View all | View all records |

### Search Buttons

| Icon | Name | Function |
|------|------|----------|
| ![New Search](images/icons/new_search.png) | New search | Activate search mode |
| ![Search](images/icons/search.png) | Search!!! | Execute search |
| ![Sort](images/icons/sort.png) | Order by | Sort records |

### Status Indicators

![Status Indicators](images/04_scheda_periodizzazione/12_indicatori_stato.png)
*Figure 12: Status indicators*

| Indicator | Description |
|-----------|-------------|
| **Status** | Current mode: "Use" (browse), "Find" (search), "New Record" |
| **Sorting** | "Unsorted" or "Sorted" |
| **record n.** | Current record number |
| **record tot.** | Total number of records |

---

## GIS Features

The Periodization Form offers powerful GIS visualization features to view SUs associated with each period/phase.

### GIS Buttons

![GIS Buttons](images/04_scheda_periodizzazione/13_pulsanti_gis.png)
*Figure 13: Buttons for GIS visualization*

#### View Single Period (GIS Icon)
- **Function**: Loads all SUs associated with the current period/phase on the QGIS map
- **Requirement**: Period Code field must be filled
- **Layers loaded**: SU and WSU filtered by period code

#### View All Periods - SU (Multiple Layers Icon)
- **Function**: Loads all periods as separate layers on the map (SU only)
- **Result**: One layer for each period/phase combination

#### View All Periods - WSU (GIS3 Icon)
- **Function**: Loads all periods as separate layers on the map (WSU only)
- **Result**: One layer for each period/phase combination for wall units

### Map Visualization

![Map with Periods](images/04_scheda_periodizzazione/14_mappa_periodi.png)
*Figure 14: SUs displayed by period on QGIS map*

When loading layers by period:
- Each period/phase has a distinctive color
- SUs are filtered based on assigned period code
- Individual layers can be activated/deactivated

---

## PDF Export

The form offers two PDF export modes:

### Single Form Export

![PDF Form Button](images/04_scheda_periodizzazione/15_pulsante_pdf_scheda.png)
*Figure 15: PDF form export button*

- **Icon**: PDF
- **Function**: Generates a PDF with current period/phase data
- **Content**:
  - Identification information (Site, Period, Phase)
  - Chronology (initial, final, extended dating)
  - Complete description

### Periodization List Export

![PDF List Button](images/04_scheda_periodizzazione/16_pulsante_pdf_lista.png)
*Figure 16: PDF list export button*

- **Icon**: Sheet
- **Function**: Generates a PDF with list of all periods/phases of the site
- **Content**: Summary table with all periods

### Generated PDF Example

![PDF Example](images/04_scheda_periodizzazione/17_esempio_pdf.png)
*Figure 17: Example of generated PDF*

---

## AI Integration

The Periodization Form includes GPT integration to obtain automatic suggestions for historical period descriptions.

### Suggestions Button

![Suggestions Button](images/04_scheda_periodizzazione/18_pulsante_suggerimenti.png)
*Figure 18: AI Suggestions button*

### How It Works

1. Select a historical epoch from the **Extended Dating** field
2. Click on the **Suggestions** button
3. Select the GPT model to use (gpt-4o or gpt-4)
4. The system automatically generates:
   - A description of the historical period
   - 3 relevant Wikipedia links
5. The generated text can be inserted into the Description field

### API Key Configuration

To use this feature:
1. Obtain an API Key from OpenAI
2. On first use, the system asks for the key
3. The key is saved in `PYARCHINIT_HOME/bin/gpt_api_key.txt`

> **Note**: This feature requires an internet connection and an OpenAI account with available credits.

---

## Operational Workflow

### Creating a New Periodization

#### Step 1: Access the Form
1. Open the Periodization Form from menu or toolbar
2. Verify database connection (Status indicator)

![Workflow Step 1](images/04_scheda_periodizzazione/19_workflow_step1.png)
*Figure 19: Opening form*

#### Step 2: New Record
1. Click on the **New record** button
2. Status changes to "New Record"
3. Fields become editable

![Workflow Step 2](images/04_scheda_periodizzazione/20_workflow_step2.png)
*Figure 20: Click on New record*

#### Step 3: Site Selection
1. If not preset, select the **Site** from the dropdown menu
2. The site must already exist in the Site Form

![Workflow Step 3](images/04_scheda_periodizzazione/21_workflow_step3.png)
*Figure 21: Site selection*

#### Step 4: Period and Phase Definition
1. Select or type the **Period** number
2. Select or type the **Phase** number
3. Enter the unique **Period Code**

![Workflow Step 4](images/04_scheda_periodizzazione/22_workflow_step4.png)
*Figure 22: Period and phase definition*

#### Step 5: Chronology
1. Select the **Extended Dating** from epochs vocabulary
2. Initial and Final Chronology fields are filled automatically
3. Or enter years manually

![Workflow Step 5](images/04_scheda_periodizzazione/23_workflow_step5.png)
*Figure 23: Setting chronology*

#### Step 6: Description
1. Fill in the **Description** field with period information
2. Optional: use the **Suggestions** button to get AI-generated text

![Workflow Step 6](images/04_scheda_periodizzazione/24_workflow_step6.png)
*Figure 24: Filling in description*

#### Step 7: Save
1. Click on the **Save** button
2. The record is saved to the database
3. Status returns to "Use"

![Workflow Step 7](images/04_scheda_periodizzazione/25_workflow_step7.png)
*Figure 25: Saving*

### Recommended Periodization Schema

For a typical excavation, it is recommended to create periodization following this schema:

| Period | Phase | Code | Description |
|--------|-------|------|-------------|
| 1 | 1 | 101 | Contemporary age - Plowing |
| 1 | 2 | 102 | Contemporary age - Abandonment |
| 2 | 1 | 201 | Medieval age - Late phase |
| 2 | 2 | 202 | Medieval age - Central phase |
| 2 | 3 | 203 | Medieval age - Initial phase |
| 3 | 1 | 301 | Roman age - Imperial phase |
| 3 | 2 | 302 | Roman age - Republican phase |
| 4 | 1 | 401 | Pre-Roman age |

---

## Best Practices

### Numbering Conventions

1. **Periods**: Number from most recent (1) to oldest
2. **Phases**: Number from most recent (1) to oldest within period
3. **Codes**: Use formula `[period * 100 + phase]` for unique codes

### Effective Descriptions

A good period description should include:
- Chronological framework
- Main characteristics of the period
- Expected structure/material types
- Comparisons with contemporary sites
- Bibliographic references

### Chronology Management

- Always use numeric years for chronologies
- For BC dates, use negative numbers
- Verify consistency: final chronology must be >= initial (in absolute value for BC)

### Linking with SUs

After creating periodization:
1. Open the SU Form
2. In the **Periodization** tab, assign Initial/Final Period and Initial/Final Phase
3. The system will automatically associate the SU with the periodization

---

## Troubleshooting

### Common Problems

#### "Period code not add"
- **Cause**: Period Code field is empty
- **Solution**: Fill in the Period Code field before using GIS functions

#### Chronology not filling automatically
- **Cause**: Selected epoch has no associated data
- **Solution**: Verify the epoch is present in the historical epochs CSV file

#### Save error: duplicate record
- **Cause**: A record already exists with the same Site/Period/Phase combination
- **Solution**: Verify values and use a unique combination

#### SUs don't appear in GIS visualization
- **Cause**: SUs don't have period code assigned
- **Solution**:
  1. Verify in SU Form that Period/Phase fields are filled
  2. Verify that Period Code corresponds

#### AI suggestions not working
- **Cause**: Missing or invalid API Key
- **Solution**:
  1. Verify internet connection
  2. Check API Key validity
  3. Reinstall libraries: `pip install --upgrade openai pydantic`

---

## Video Tutorial

### Video 1: Periodization Form Overview
*Duration: 3-4 minutes*

[Video tutorial placeholder]

**Contents:**
- Opening the form
- Interface description
- Navigating between records

### Video 2: Creating Complete Periodization
*Duration: 5-6 minutes*

[Video tutorial placeholder]

**Contents:**
- Creating a new periodization
- Filling all fields
- Using epochs vocabulary
- Saving

### Video 3: GIS Visualization by Period
*Duration: 3-4 minutes*

[Video tutorial placeholder]

**Contents:**
- Using GIS buttons
- Viewing SUs by period
- Managing loaded layers

---

## Field Summary

| Field | Type | Required | Database |
|-------|------|----------|----------|
| Site | ComboBox | Yes | sito |
| Period | ComboBox | Yes | periodo |
| Phase | ComboBox | Yes | fase |
| Period Code | LineEdit | No | cont_per |
| Description | TextEdit | No | descrizione |
| Initial Chronology | LineEdit | No | cron_iniziale |
| Final Chronology | LineEdit | No | cron_finale |
| Extended Dating | ComboBox | No | datazione_estesa |

---

*Last updated: January 2026*
*PyArchInit - Sketches of Sketches*
