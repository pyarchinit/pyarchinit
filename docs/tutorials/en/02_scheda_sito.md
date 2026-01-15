# PyArchInit - Site Form

## Table of Contents
1. [Introduction](#introduction)
2. [Accessing the Form](#accessing-the-form)
3. [User Interface](#user-interface)
4. [Site Descriptive Data](#site-descriptive-data)
5. [DBMS Toolbar](#dbms-toolbar)
6. [GIS Features](#gis-features)
7. [SU Form Generation](#su-form-generation)
8. [MoveCost - Path Analysis](#movecost---path-analysis)
9. [Report Export](#report-export)
10. [Operational Workflow](#operational-workflow)

---

## Introduction

The **Site Form** is the starting point for documenting an archaeological excavation in PyArchInit. Every archaeological project begins with creating a site, which serves as the main container for all other information (Stratigraphic Units, Structures, Finds, etc.).

An **archaeological site** in PyArchInit represents a defined geographical area where archaeological research activities take place. It can be an excavation, a survey area, a monument, etc.

<!-- VIDEO: Introduction to the Site Form -->
> **Video Tutorial**: [Insert video link for site form introduction]

---

## Accessing the Form

To access the Site Form:

1. Menu **PyArchInit** → **Archaeological record management** → **Site**
2. Or from the PyArchInit toolbar, click on the **Site** icon

<!-- IMAGE: Screenshot of site form access menu -->
![Site Form Access](images/02_scheda_sito/01_menu_scheda_sito.png)
*Figure 1: Accessing the Site Form from the PyArchInit menu*

<!-- IMAGE: Screenshot of toolbar with site icon -->
![Site Toolbar](images/02_scheda_sito/02_toolbar_sito.png)
*Figure 2: Site Form icon in the toolbar*

---

## User Interface

The Site Form is divided into several functional areas:

<!-- IMAGE: Screenshot of complete site form with numbered areas -->
![Site Form Interface](images/02_scheda_sito/03_interfaccia_completa.png)
*Figure 3: Complete Site Form interface*

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | **DBMS Toolbar** | Toolbar for navigation and record management |
| 2 | **Descriptive Data** | Fields for entering site information |
| 3 | **SU Generator** | Tool for batch-creating SU forms |
| 4 | **GIS Viewer** | Controls for cartographic display |
| 5 | **MoveCost** | Advanced spatial analysis tools |
| 6 | **Help** | Documentation and video tutorials |

---

## Site Descriptive Data

### Descriptive Data Tab

<!-- IMAGE: Screenshot of descriptive data tab -->
![Descriptive Data Tab](images/02_scheda_sito/04_tab_dati_descrittivi.png)
*Figure 4: Descriptive Data Tab*

#### Required Fields

| Field | Description | Notes |
|-------|-------------|-------|
| **Site** | Site identification name | Required field, must be unique |

#### Geographic Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Nation** | Country where the site is located | Italy |
| **Region** | Administrative region | Lazio |
| **Province** | Province | Rome |
| **Municipality** | Municipality | Rome |

<!-- IMAGE: Screenshot of completed geographic fields -->
![Geographic Fields](images/02_scheda_sito/05_campi_geografici.png)
*Figure 5: Example of geographic field completion*

#### Descriptive Fields

| Field | Description |
|-------|-------------|
| **Name** | Extended/descriptive name of the site |
| **Definition** | Site type (from thesaurus) |
| **Description** | Free text field for detailed description |
| **Folder** | Path to the local project folder |

<!-- IMAGE: Screenshot of description field -->
![Description Field](images/02_scheda_sito/06_campo_descrizione.png)
*Figure 6: Text description field*

### Site Definition (Thesaurus)

The **Definition** field uses a controlled vocabulary (thesaurus). Available options include:

| Definition | Description |
|------------|-------------|
| Excavation area | Zone subject to stratigraphic investigation |
| Survey area | Surface reconnaissance area |
| Archaeological site | Location with archaeological evidence |
| Monument | Single monumental structure |
| Necropolis | Burial area |
| Settlement | Residential area |
| Sanctuary | Sacred/cult area |
| ... | Other definitions from thesaurus |

<!-- IMAGE: Screenshot of site definition dropdown -->
![Site Definition](images/02_scheda_sito/07_definizione_sito.png)
*Figure 7: Selecting site definition from thesaurus*

### Project Folder

The **Folder** field allows you to associate a local directory with the site to organize project files.

<!-- IMAGE: Screenshot of folder selection -->
![Folder Selection](images/02_scheda_sito/08_selezione_cartella.png)
*Figure 8: Project folder selection*

| Button | Function |
|--------|----------|
| **...** | Browse to select folder |
| **Open** | Opens the folder in file manager |

---

## DBMS Toolbar

The DBMS toolbar provides all controls for record management.

<!-- IMAGE: Screenshot of DBMS toolbar -->
![DBMS Toolbar](images/02_scheda_sito/09_toolbar_dbms.png)
*Figure 9: DBMS Toolbar*

### Status Indicators

| Indicator | Description |
|-----------|-------------|
| **DB Info** | Shows connected database type (SQLite/PostgreSQL) |
| **Status** | Current state: `Use` (browse), `Find` (search), `New Record` |
| **Sorting** | Indicates if records are sorted |
| **record n.** | Current record number |
| **record tot.** | Total records |

<!-- IMAGE: Screenshot of status indicators -->
![Status Indicators](images/02_scheda_sito/10_indicatori_stato.png)
*Figure 10: Status indicators*

### Record Navigation

| Button | Icon | Function | Shortcut |
|--------|------|----------|----------|
| **First rec** | |< | Go to first record | - |
| **Prev rec** | < | Go to previous record | - |
| **Next rec** | > | Go to next record | - |
| **Last rec** | >| | Go to last record | - |

<!-- IMAGE: Screenshot of navigation buttons -->
![Navigation](images/02_scheda_sito/11_navigazione_record.png)
*Figure 11: Navigation buttons*

### Record Management

| Button | Function | Description |
|--------|----------|-------------|
| **New record** | Create new | Prepares the form to enter a new site |
| **Save** | Save | Saves changes or new record |
| **Delete record** | Delete | Deletes current record (with confirmation) |
| **View all records** | View all | Shows all records in database |

<!-- IMAGE: Screenshot of management buttons -->
![Record Management](images/02_scheda_sito/12_gestione_record.png)
*Figure 12: Record management buttons*

### Search and Sorting

| Button | Function | Description |
|--------|----------|-------------|
| **new search** | New search | Starts search mode |
| **search !!!** | Execute search | Executes search with entered criteria |
| **Order by** | Sort | Opens sorting panel |

<!-- IMAGE: Screenshot of search -->
![Search](images/02_scheda_sito/13_ricerca.png)
*Figure 13: Search functions*

#### How to Perform a Search

1. Click **new search** - status changes to "Find"
2. Fill in fields with search criteria
3. Click **search !!!** to execute
4. Results are shown and you can navigate through them

<!-- IMAGE: Screenshot of search example -->
![Search Example](images/02_scheda_sito/14_esempio_ricerca.png)
*Figure 14: Search example by region*

<!-- VIDEO: How to perform searches -->
> **Video Tutorial**: [Insert search video link]

#### Sorting Panel

Clicking **Order by** opens a panel for sorting records:

<!-- IMAGE: Screenshot of sorting panel -->
![Sorting Panel](images/02_scheda_sito/15_pannello_ordinamento.png)
*Figure 15: Sorting panel*

| Option | Description |
|--------|-------------|
| **Field** | Select field for sorting |
| **Ascending** | A-Z, 0-9 order |
| **Descending** | Z-A, 9-0 order |

---

## GIS Features

The Site Form offers various GIS integration features.

<!-- IMAGE: Screenshot of GIS section -->
![GIS Section](images/02_scheda_sito/16_sezione_gis.png)
*Figure 16: GIS features section*

### Layer Loading

| Button | Function |
|--------|----------|
| **GIS viewer** | Load all layers for entering geometries |
| **Load site layer** (globe icon) | Load only current site layers |
| **Load all sites** (multiple globe icon) | Load layers for all sites |

<!-- IMAGE: Screenshot of GIS buttons -->
![GIS Buttons](images/02_scheda_sito/17_bottoni_gis.png)
*Figure 17: GIS layer loading buttons*

### Geocoding - Address Search

The geocoding function allows you to locate an address on the map.

<!-- IMAGE: Screenshot of geocoding -->
![Geocoding](images/02_scheda_sito/18_geocoding.png)
*Figure 18: Address search field*

1. Enter the address in the text field
2. Click **Zoom on**
3. The map centers on the found location

| Field | Description |
|-------|-------------|
| **Address** | Enter street, city, country |
| **Zoom on** | Centers the map on the address |

### Active GIS Mode

The **Enable search loading** toggle activates/deactivates automatic display of search results on the map.

<!-- IMAGE: Screenshot of GIS toggle -->
![GIS Toggle](images/02_scheda_sito/19_toggle_gis.png)
*Figure 19: GIS mode toggle*

- **Active**: Searches are automatically displayed on the map
- **Inactive**: Searches don't modify map display

### WMS Archaeological Constraints

The WMS button loads the archaeological constraints layer from the Italian Ministry of Culture.

<!-- IMAGE: Screenshot of WMS constraints -->
![WMS Constraints](images/02_scheda_sito/20_wms_vincoli.png)
*Figure 20: WMS archaeological constraints layer*

### Base Maps

The Base Maps button allows loading base maps (Google Maps, OpenStreetMap, etc.).

<!-- IMAGE: Screenshot of base maps -->
![Base Maps](images/02_scheda_sito/21_base_maps.png)
*Figure 21: Base maps selection*

---

## SU Form Generation

This feature allows automatically creating an arbitrary number of SU forms for the current site.

<!-- IMAGE: Screenshot of SU generator -->
![SU Generator](images/02_scheda_sito/22_generatore_us.png)
*Figure 22: SU form generation section*

### Parameters

| Field | Description | Example |
|-------|-------------|---------|
| **Area Number** | Excavation area number | 1 |
| **Starting SU form number** | Initial SU number | 1 |
| **Number of forms to create** | How many SU to generate | 100 |
| **Type** | SU or WSU | SU |

### Procedure

1. Make sure you're on the correct site
2. Enter the area number
3. Enter the starting SU number
4. Enter how many forms to create
5. Select the type (SU or WSU)
6. Click **Generate SU**

<!-- IMAGE: Screenshot of generation example -->
![Generation Example](images/02_scheda_sito/23_esempio_generazione.png)
*Figure 23: Example generating 50 SU starting from SU 101*

<!-- VIDEO: How to batch generate SU forms -->
> **Video Tutorial**: [Insert SU generation video link]

---

## MoveCost - Path Analysis

The **MovecostToPyarchinit** section integrates R functions for least cost path analysis.

<!-- IMAGE: Screenshot of MoveCost section -->
![MoveCost](images/02_scheda_sito/24_movecost_sezione.png)
*Figure 24: MoveCost section*

### Prerequisites

- **R** installed on the system
- R package **movecost** installed
- **Processing R Provider** plugin active in QGIS

### Available Functions

| Function | Description |
|----------|-------------|
| **movecost** | Calculates movement cost and least cost paths from an origin point |
| **movecost by polygon** | Same as above, using a polygon to download DTM |
| **movebound** | Calculates walking cost boundaries around points |
| **movebound by polygon** | Same as above, using a polygon |
| **movcorr** | Calculates least cost corridors between points |
| **movecorr by polygon** | Same as above, using a polygon |
| **movalloc** | Territory allocation based on costs |
| **movealloc by polygon** | Same as above, using a polygon |

<!-- IMAGE: Screenshot of movecost example -->
![MoveCost Example](images/02_scheda_sito/25_esempio_movecost.png)
*Figure 25: MoveCost analysis output example*

### Add Scripts

The **Add scripts** button automatically installs the necessary R scripts in the QGIS profile.

<!-- VIDEO: MoveCost Analysis -->
> **Video Tutorial**: [Insert MoveCost video link]

---

## Report Export

### Export Excavation Report

The **Export** button generates a PDF with the excavation report for the current site.

<!-- IMAGE: Screenshot of export -->
![Export](images/02_scheda_sito/26_esportazione.png)
*Figure 26: Report export button*

**Note**: This feature is in development version and may contain bugs.

The report includes:
- Site identification data
- List of SU
- Stratigraphic sequence
- Harris Matrix (if available)

<!-- IMAGE: Screenshot of PDF example -->
![PDF Example](images/02_scheda_sito/27_esempio_pdf.png)
*Figure 27: Example of generated PDF report*

---

## Operational Workflow

### Creating a New Site

<!-- VIDEO: New site creation workflow -->
> **Video Tutorial**: [Insert new site workflow video link]

#### Step 1: Open the Site Form
<!-- IMAGE: Step 1 -->
![Workflow Step 1](images/02_scheda_sito/28_workflow_step1.png)
*Figure 28: Step 1 - Opening the form*

#### Step 2: Click "New record"
The status changes to "New Record" and fields are cleared.

<!-- IMAGE: Step 2 -->
![Workflow Step 2](images/02_scheda_sito/29_workflow_step2.png)
*Figure 29: Step 2 - New record*

#### Step 3: Fill in Required Data
Enter at least the site name (required field).

<!-- IMAGE: Step 3 -->
![Workflow Step 3](images/02_scheda_sito/30_workflow_step3.png)
*Figure 30: Step 3 - Data entry*

#### Step 4: Fill in Geographic Data
Enter nation, region, province, municipality.

<!-- IMAGE: Step 4 -->
![Workflow Step 4](images/02_scheda_sito/31_workflow_step4.png)
*Figure 31: Step 4 - Geographic data*

#### Step 5: Select Definition
Choose the site type from thesaurus.

<!-- IMAGE: Step 5 -->
![Workflow Step 5](images/02_scheda_sito/32_workflow_step5.png)
*Figure 32: Step 5 - Site definition*

#### Step 6: Add Description
Fill in the description field with detailed information.

<!-- IMAGE: Step 6 -->
![Workflow Step 6](images/02_scheda_sito/33_workflow_step6.png)
*Figure 33: Step 6 - Description*

#### Step 7: Save
Click **Save** to save the new site.

<!-- IMAGE: Step 7 -->
![Workflow Step 7](images/02_scheda_sito/34_workflow_step7.png)
*Figure 34: Step 7 - Saving*

#### Step 8: Verify
The site has been created, status returns to "Use".

<!-- IMAGE: Step 8 -->
![Workflow Step 8](images/02_scheda_sito/35_workflow_step8.png)
*Figure 35: Step 8 - Creation verification*

### Modifying an Existing Site

1. Navigate to the site to modify
2. Modify desired fields
3. Click **Save**
4. Confirm the save changes

### Deleting a Site

**Warning**: Deleting a site does NOT automatically delete associated SU, structures, and finds.

1. Navigate to the site to delete
2. Click **Delete record**
3. Confirm deletion

<!-- IMAGE: Screenshot of deletion confirmation -->
![Deletion Confirmation](images/02_scheda_sito/36_conferma_eliminazione.png)
*Figure 36: Deletion confirmation dialog*

---

## Help Tab

The Help tab provides quick access to documentation.

<!-- IMAGE: Screenshot of help tab -->
![Help Tab](images/02_scheda_sito/37_tab_help.png)
*Figure 37: Help Tab*

| Resource | Link |
|----------|------|
| Video Tutorial | YouTube |
| Documentation | pyarchinit.github.io |
| Community | Facebook UnaQuantum |

---

## Concurrency Management (PostgreSQL)

When using PostgreSQL in a multi-user environment, the system automatically manages modification conflicts:

- **Lock indicator**: Shows if the record is being edited by another user
- **Version control**: Detects concurrent modifications
- **Conflict resolution**: Allows choosing which version to keep

<!-- IMAGE: Screenshot of concurrency indicator -->
![Concurrency](images/02_scheda_sito/38_concorrenza.png)
*Figure 38: Locked record indicator*

---

## Troubleshooting

### Site not saved
- Verify that the "Site" field is filled in
- Verify that the name doesn't already exist in the database

### GIS layers not loading
- Verify database connection
- Verify that geometries exist associated with the site

### Geocoding error
- Verify internet connection
- Check that the address is written correctly

### MoveCost not working
- Verify that R is installed
- Verify that Processing R Provider plugin is active
- Install the movecost package in R

---

## Technical Notes

- **Database table**: `site_table`
- **Database fields**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Associated GIS layers**: PYSITO_POLYGON, PYSITO_POINT
- **Thesaurus**: tipologia_sigla = '1.1'

---

*PyArchInit Documentation - Site Form*
*Version: 4.9.x*
*Last updated: January 2026*
