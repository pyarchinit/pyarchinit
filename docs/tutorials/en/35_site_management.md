# PyArchInit - Site Management (Gestione Cantiere)

## Table of Contents

1. [Introduction](#introduction)
2. [Accessing the Module](#accessing-the-module)
3. [Site Dashboard](#site-dashboard)
   - [Site and Year Selector](#site-and-year-selector)
   - [Budget Summary](#budget-summary)
   - [Personnel Summary](#personnel-summary)
   - [Equipment Summary](#equipment-summary)
   - [Quantity Surveying (Computo Metrico)](#quantity-surveying-computo-metrico)
   - [Calculation History](#calculation-history)
4. [Personnel Form](#personnel-form)
5. [Attendance Form](#attendance-form)
6. [Equipment Form](#equipment-form)
7. [Budget Form](#budget-form)
8. [Operational Workflow](#operational-workflow)
9. [FAQ](#faq)
10. [Technical Notes](#technical-notes)

---

## Introduction

The **Site Management** module (Italian: *Gestione Cantiere*) is a comprehensive suite of tools for managing the operational and administrative aspects of an archaeological excavation site. While PyArchInit has always excelled at recording archaeological data -- stratigraphic units, finds, structures, and spatial information -- the day-to-day logistics of running a field project require their own dedicated management tools.

This module addresses that need by providing five interconnected components:

- **Site Dashboard**: A central overview that aggregates budget, personnel, equipment, and volumetric data into a single, at-a-glance view
- **Personnel Form**: Registration and management of team members, their roles, contracts, and rates
- **Attendance Form**: Daily tracking of working hours, absences, overtime, and associated costs
- **Equipment Form**: Inventory and lifecycle management for all site equipment
- **Budget Form**: Financial planning and expense tracking by category and year

All five components share data through the PyArchInit database and are linked by the site name, ensuring consistent filtering and reporting across the module.

<!-- IMAGE: Overview of the five Site Management icons in the toolbar -->
> **Fig. 1**: The five Site Management toolbar icons providing access to Dashboard, Personnel, Attendance, Equipment, and Budget forms

---

## Accessing the Module

The Site Management module is accessed from a dedicated **Site Management** toolbar in PyArchInit. The toolbar contains five icons, one for each component:

| Icon | Component | Description |
|------|-----------|-------------|
| 1 | **Dashboard** | Opens the central Site Dashboard |
| 2 | **Personnel** | Opens the Personnel CRUD form |
| 3 | **Attendance** | Opens the Attendance CRUD form |
| 4 | **Equipment** | Opens the Equipment CRUD form |
| 5 | **Budget** | Opens the Budget CRUD form |

To open any component, simply click its icon in the toolbar. Each component opens as an independent dialog window, so you can have multiple forms open simultaneously.

<!-- IMAGE: Close-up of the Site Management toolbar with all five icons labelled -->
> **Fig. 2**: The Site Management toolbar with all five component icons

---

## Site Dashboard

The **Site Dashboard** (`Cantiere.py`) is the central hub of the module. It provides a real-time overview of your excavation site's operational status by aggregating data from the Personnel, Attendance, Equipment, and Budget tables.

<!-- IMAGE: Full screenshot of the Site Dashboard with all sections visible -->
> **Fig. 3**: The Site Dashboard showing all summary sections -- budget, personnel, equipment, and quantity surveying

### Site and Year Selector

At the top of the dashboard, two dropdown menus allow you to filter all displayed data:

| Control | Description |
|---------|-------------|
| **Site** (comboBox_sito) | Select the archaeological site to display. If you have configured a default site in PyArchInit settings, it is automatically pre-selected on opening. |
| **Year** (comboBox_anno) | Select the fiscal year. Defaults to the current year and lists the last 10 years in descending order. |
| **Refresh** | Manually refreshes all dashboard sections with the latest data from the database. |

Changing either the site or year selector automatically triggers a full dashboard refresh.

<!-- IMAGE: Site and year selector dropdowns at the top of the dashboard -->
> **Fig. 4**: The site and year selector controls with auto-selection of the configured site

### Budget Summary

The budget section provides a financial overview for the selected site and year:

| Element | Description |
|---------|-------------|
| **Estimated Total** | Sum of all `importo_previsto` values from the Budget table, displayed in euros |
| **Actual Spending** | Sum of all `importo_effettivo` values from the Budget table, displayed in euros |
| **Progress Bar** | Visual indicator showing the percentage of budget consumed (actual / estimated x 100) |
| **Pie Chart** | A matplotlib-rendered pie chart breaking down actual spending by budget category |

The pie chart is embedded directly in the dashboard using `matplotlib`'s Qt5 backend. Each slice represents a budget category (e.g., Personnel, Materials, Transport) with percentage labels. The chart updates automatically when you change the site or year.

<!-- IMAGE: Budget summary section showing estimated vs actual totals, progress bar, and pie chart -->
> **Fig. 5**: Budget summary with progress bar at 62% and pie chart showing spending distribution across categories

### Personnel Summary

The personnel section shows a snapshot of today's workforce status, queried from the Attendance table:

| Metric | Description |
|--------|-------------|
| **Present Today** | Count of attendance records for today where `tipo_giornata` = "lavorativa" (working) |
| **On Vacation** | Count of records for today where `tipo_giornata` = "ferie" (vacation) |
| **Sick Leave** | Count of records for today where `tipo_giornata` = "malattia" (sick) |
| **Monthly Hours** | Total regular + overtime hours accumulated in the current calendar month |
| **Monthly Cost** | Total daily cost accumulated in the current calendar month, displayed in euros |

This section gives the site director an immediate understanding of available human resources on any given day.

<!-- IMAGE: Personnel summary showing present/vacation/sick counts and monthly totals -->
> **Fig. 6**: Personnel summary indicating 8 present, 1 on vacation, 0 sick, with 342.5 monthly hours

### Equipment Summary

The equipment section aggregates data from the Equipment table:

| Metric | Description |
|--------|-------------|
| **Total** | Total number of equipment records for the selected site |
| **In Use** | Count of equipment with `stato` = "in_uso" |
| **Maintenance** | Count of equipment with `stato` = "manutenzione" |
| **Maintenance Alerts** | If any equipment has a `data_prossima_manutenzione` that is past today's date and is not decommissioned, a red warning is displayed showing the count of overdue items |

The maintenance alert system is designed to prevent equipment failures in the field. When overdue maintenance is detected, the label turns **red and bold** to attract attention.

<!-- IMAGE: Equipment summary with a red overdue maintenance alert visible -->
> **Fig. 7**: Equipment summary showing 2 items with overdue maintenance highlighted in red

### Quantity Surveying (Computo Metrico)

The Quantity Surveying section provides GIS-integrated volumetric calculations directly from the dashboard. This is particularly useful for tracking excavation progress in terms of area and volume of soil removed.

Two calculation modes are available:

#### DEM Difference Calculation

Select the **DEM Difference** radio button to compute the volume of material removed between two DEM (Digital Elevation Model) surveys taken at different times.

| Control | Description |
|---------|-------------|
| **DEM Pre** | Select the pre-excavation (or earlier) DEM raster layer from the QGIS project |
| **DEM Post** | Select the post-excavation (or later) DEM raster layer from the QGIS project |
| **Calculate** | Runs the QGIS Raster Calculator to compute pixel-by-pixel differences, then sums absolute values multiplied by pixel area |

The result is displayed as:
- **Area** (m2): Total area where elevation change exceeds 0.01 m
- **Volume** (m3): Absolute total volume of material displaced

#### DEM + Polygon Zonal Statistics

Select the **DEM + Polygon** radio button to compute zonal statistics for a DEM within one or more polygon boundaries.

| Control | Description |
|---------|-------------|
| **DEM** | Select the DEM raster layer (uses the DEM Pre combobox) |
| **Polygon Layer** | Select a vector polygon layer defining the zones of interest |
| **Calculate** | Runs `QgsZonalStatistics` to compute sum, count, min, and max within each polygon |

This mode is useful for calculating volumes within specific excavation areas or trenches defined by polygon features.

<!-- IMAGE: Quantity Surveying section with DEM layer selectors and result labels -->
> **Fig. 8**: Quantity Surveying controls showing DEM Difference mode with results: 124.50 m2 area and 38.72 m3 volume

#### Saving Results

After a calculation completes, click **Save Computo** to persist the results to the `computo_metrico_table` in the database. The saved record includes:

- Site name
- Calculation description (auto-generated with timestamp)
- Calculation type (`differenza_dem` or `dem_poligono`)
- Layer names used
- Area and volume values
- Date of calculation

### Calculation History

Below the Quantity Surveying controls, a table widget displays all previously saved calculations for the selected site. Each row shows:

| Column | Description |
|--------|-------------|
| **Date** | When the calculation was performed |
| **Type** | `differenza_dem` or `dem_poligono` |
| **Area (m2)** | Calculated area |
| **Volume (m3)** | Calculated volume |
| **Notes** | Any additional notes |

This history allows you to track excavation progress over time and compare volumes removed across different campaign phases.

<!-- IMAGE: Calculation history table with multiple rows of saved computo metrico results -->
> **Fig. 9**: Calculation history showing three saved calculations from different dates

---

## Personnel Form

The **Personnel Form** (`Personale.py`) is a standard PyArchInit CRUD form for managing the team members assigned to an archaeological site. It follows the familiar DBMS toolbar pattern used throughout the plugin.

<!-- IMAGE: Full screenshot of the Personnel form -->
> **Fig. 10**: The Personnel form with all fields visible

### Fields

| Field | DB Column | Description |
|-------|-----------|-------------|
| **Site** | `sito` | Archaeological site the person is assigned to |
| **First Name** | `nome` | Person's first name |
| **Last Name** | `cognome` | Person's last name |
| **Qualification** | `qualifica` | Professional qualification (e.g., Archaeologist, Topographer) |
| **Role** | `ruolo` | Role on site (e.g., Director, Field Supervisor, Excavator) |
| **Tax Code** | `codice_fiscale` | Fiscal code or national ID number |
| **Email** | `email` | Contact email address |
| **Phone** | `telefono` | Contact phone number |
| **Date of Birth** | `data_nascita` | Date of birth |
| **Address** | `indirizzo` | Home address |
| **Contract Type** | `tipo_contratto` | Type of employment contract |
| **Contract Start** | `data_inizio_contratto` | Contract start date |
| **Contract End** | `data_fine_contratto` | Contract end date |
| **Hourly Rate** | `tariffa_oraria` | Hourly pay rate |
| **Daily Rate** | `tariffa_giornaliera` | Daily pay rate |
| **IBAN** | `iban` | Bank account IBAN for payments |
| **Notes** | `note` | Free-text notes |
| **Active** | `attivo` | Whether the person is currently active on site |

### DBMS Toolbar

The Personnel form includes the standard PyArchInit DBMS toolbar with:

- **Record navigation**: First, Previous, Next, Last
- **Record management**: New Record, Save, Delete
- **Search**: New Search, Execute Search
- **Sorting**: Order By (sortable by ID, Site, First Name, Last Name, Role, Contract Type, Active)

### Workflow

1. Click **New Record** to enter a new team member
2. Select the **Site** from the dropdown
3. Fill in at least the first name, last name, and role
4. Set the daily or hourly rate (used for cost calculations in the Attendance form)
5. Click **Save**

<!-- IMAGE: Personnel form in New Record mode with fields being filled -->
> **Fig. 11**: Adding a new team member with role and daily rate configured

---

## Attendance Form

The **Attendance Form** (`Presenze.py`) tracks daily attendance, working hours, and costs for each team member. It is the data source for the dashboard's personnel summary.

<!-- IMAGE: Full screenshot of the Attendance form -->
> **Fig. 12**: The Attendance form showing a daily attendance record

### Fields

| Field | DB Column | Description |
|-------|-----------|-------------|
| **Site** | `sito` | Archaeological site |
| **Personnel ID** | `id_personale` | Reference to the person (links to Personnel table) |
| **Date** | `data` | Date of the attendance record (format: YYYY-MM-DD) |
| **Clock In** | `ora_ingresso` | Time of arrival |
| **Clock Out** | `ora_uscita` | Time of departure |
| **Regular Hours** | `ore_ordinarie` | Number of regular working hours |
| **Overtime Hours** | `ore_straordinario` | Number of overtime hours |
| **Day Type** | `tipo_giornata` | Type of day: `lavorativa` (working), `ferie` (vacation), `malattia` (sick), `permesso` (leave) |
| **Shift** | `turno` | Shift designation (e.g., morning, afternoon) |
| **Work Area** | `area_lavoro` | Excavation area where the person worked |
| **Day Cost** | `costo_giornata` | Total cost for the day (can be auto-calculated from Personnel rates) |
| **Notes** | `note` | Free-text notes |

### Day Types

| Value | English | Description |
|-------|---------|-------------|
| `lavorativa` | Working | Normal working day -- counted as "present" in the dashboard |
| `ferie` | Vacation | Planned vacation day |
| `malattia` | Sick | Sick leave |
| `permesso` | Leave | Other authorized absence |

### DBMS Toolbar

Standard PyArchInit navigation and management buttons. Records can be sorted by ID, Site, Personnel ID, Date, Day Type, Shift, or Work Area.

### Workflow

1. Click **New Record**
2. Select the **Site** and **Personnel ID**
3. Enter today's **Date**
4. Set the **Day Type** (working, vacation, sick, or leave)
5. If working: enter clock in/out times, regular and overtime hours
6. Enter the **Day Cost** or let it calculate from the personnel's daily rate
7. Click **Save**

<!-- IMAGE: Attendance form showing a working day record with hours filled in -->
> **Fig. 13**: Recording a working day with 8 regular hours and 1.5 overtime hours

---

## Equipment Form

The **Equipment Form** (`Attrezzature.py`) manages the inventory of tools, machinery, and instruments used on the archaeological site.

<!-- IMAGE: Full screenshot of the Equipment form -->
> **Fig. 14**: The Equipment form showing details of a total station

### Fields

| Field | DB Column | Description |
|-------|-----------|-------------|
| **Site** | `sito` | Archaeological site where the equipment is deployed |
| **Inventory Code** | `codice_inventario` | Unique inventory identifier |
| **Name** | `nome` | Equipment name (e.g., "Total Station", "Drone", "Sieve") |
| **Category** | `categoria` | Equipment category (e.g., Survey, Excavation, Photography) |
| **Brand** | `marca` | Manufacturer brand |
| **Model** | `modello` | Model designation |
| **Serial Number** | `numero_serie` | Manufacturer serial number |
| **Ownership** | `proprieta` | Whether owned, rented, or on loan |
| **Purchase Date** | `data_acquisto` | Date of acquisition |
| **Purchase Cost** | `costo_acquisto` | Acquisition cost |
| **Rental Cost/Day** | `costo_noleggio_giorno` | Daily rental cost (if applicable) |
| **Status** | `stato` | Current status: `in_uso` (in use), `manutenzione` (maintenance), `fuori_uso` (decommissioned) |
| **Assigned To** | `assegnato_a` | Person or team currently using the equipment |
| **Last Maintenance** | `data_ultima_manutenzione` | Date of the most recent maintenance |
| **Next Maintenance** | `data_prossima_manutenzione` | Date of the next scheduled maintenance (monitored by dashboard alerts) |
| **Notes** | `note` | Free-text notes |

### Equipment Status Values

| Value | English | Dashboard Effect |
|-------|---------|-----------------|
| `in_uso` | In use | Counted in the "In Use" metric |
| `manutenzione` | Maintenance | Counted in the "Maintenance" metric |
| `fuori_uso` | Decommissioned | Excluded from overdue maintenance alerts |

### Maintenance Alerts

The dashboard monitors the **Next Maintenance** date. If any active equipment (status not `fuori_uso`) has a `data_prossima_manutenzione` that has passed, the dashboard displays a red alert. To resolve the alert:

1. Open the Equipment form
2. Navigate to the flagged equipment
3. Update the **Last Maintenance** date to today
4. Set a new **Next Maintenance** date
5. Save the record
6. Refresh the dashboard

<!-- IMAGE: Equipment form showing a record with overdue maintenance date highlighted -->
> **Fig. 15**: An equipment record where the Next Maintenance date has passed, triggering a dashboard alert

---

## Budget Form

The **Budget Form** (`Budget.py`) manages financial planning and expense tracking for the excavation. Budget records are organized by site, year, and category.

<!-- IMAGE: Full screenshot of the Budget form -->
> **Fig. 16**: The Budget form showing a planned vs actual expense entry

### Fields

| Field | DB Column | Description |
|-------|-----------|-------------|
| **Site** | `sito` | Archaeological site |
| **Year** | `anno` | Budget year |
| **Category** | `categoria` | Spending category (e.g., Personnel, Materials, Transport, Equipment, Services) |
| **Description** | `descrizione` | Description of the budget line item |
| **Estimated Amount** | `importo_previsto` | Planned/budgeted amount in euros |
| **Actual Amount** | `importo_effettivo` | Actual amount spent in euros |
| **Registration Date** | `data_registrazione` | Date the record was created |
| **Expense Date** | `data_spesa` | Date the expense was incurred |
| **Supplier** | `fornitore` | Supplier or vendor name |
| **Invoice Number** | `numero_fattura` | Invoice or receipt reference number |
| **Notes** | `note` | Free-text notes |

### Budget Categories

Budget records should use consistent category names, as these are used to generate the dashboard pie chart. Recommended categories include:

| Category | Description |
|----------|-------------|
| Personale | Personnel costs (salaries, per diem) |
| Materiali | Consumable materials |
| Attrezzature | Equipment purchase or rental |
| Trasporti | Travel and transport costs |
| Servizi | External services (lab analysis, consultants) |
| Varie | Miscellaneous expenses |

### DBMS Toolbar

Standard PyArchInit navigation and management. Records can be sorted by ID, Site, Year, Category, Supplier, or Expense Date.

### Workflow

1. Click **New Record**
2. Select the **Site** and **Year**
3. Choose or type a **Category**
4. Enter a **Description** for the budget line
5. Enter the **Estimated Amount** (budget plan)
6. When the expense is incurred, update the **Actual Amount**
7. Optionally fill in the supplier and invoice details
8. Click **Save**

The dashboard will immediately reflect any changes to the budget totals and pie chart on the next refresh.

<!-- IMAGE: Budget form in Browse mode showing a saved record with both estimated and actual amounts -->
> **Fig. 17**: A budget record showing a planned amount of 5,000.00 and actual spending of 4,230.50

---

## Operational Workflow

### Setting Up a New Excavation Site

This workflow shows how to configure the Site Management module for a new excavation campaign.

#### Step 1: Create the Site

Before using any Site Management feature, ensure that the archaeological site exists in the PyArchInit Site Form (see [Site Form Tutorial](02_scheda_sito.md)). The site name is the key linking field across all module components.

#### Step 2: Register Personnel

1. Open the **Personnel Form** from the toolbar
2. Create a new record for each team member
3. Fill in their name, role, qualification, and daily rate
4. Set the contract start/end dates
5. Save each record

#### Step 3: Register Equipment

1. Open the **Equipment Form**
2. Create records for all site equipment
3. Set the status to `in_uso` for active equipment
4. Enter maintenance schedules (last and next maintenance dates)
5. Save each record

#### Step 4: Create the Budget Plan

1. Open the **Budget Form**
2. Create one record per budget category
3. Enter the **Estimated Amount** for each category
4. Leave the **Actual Amount** at zero initially
5. Save all records

#### Step 5: Monitor via Dashboard

1. Open the **Site Dashboard**
2. Verify that the correct site is selected
3. Check that all summary sections display the expected data
4. Use this view daily to monitor the site's operational status

<!-- IMAGE: Dashboard fully populated after completing the setup workflow -->
> **Fig. 18**: A fully configured dashboard showing budget, personnel, and equipment data for an active site

### Daily Operations

Each working day, the typical workflow includes:

1. **Morning**: Open the Attendance form and create records for all team members, setting the day type and clock-in time
2. **End of day**: Update attendance records with clock-out times and hours worked
3. **As needed**: Update budget records when expenses are incurred
4. **As needed**: Update equipment status when items go to/from maintenance
5. **Periodically**: Run Quantity Surveying calculations from the dashboard when new DEM data is available

### DEM Volume Tracking Workflow

1. Perform a drone or total station survey at the start of excavation to produce the **pre-excavation DEM**
2. Load the DEM raster into the QGIS project
3. After a period of excavation, produce a **post-excavation DEM**
4. Load the second DEM into the QGIS project
5. Open the **Site Dashboard**
6. In the Quantity Surveying section, select **DEM Difference** mode
7. Choose the pre-excavation DEM and post-excavation DEM
8. Click **Calculate**
9. Review the area and volume results
10. Click **Save Computo** to record the results in the database
11. Repeat for subsequent survey phases to track cumulative excavation volume

<!-- IMAGE: Before and after DEM layers loaded in QGIS alongside the dashboard calculation results -->
> **Fig. 19**: DEM difference workflow showing pre/post rasters in QGIS and the computed volume in the dashboard

---

## FAQ

### General

**Q: Do I need to create the database tables manually?**
A: No. The Site Management tables (`personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico_table`) are created automatically when PyArchInit initializes the database. They work with both PostgreSQL and SQLite.

**Q: Can I use the module with multiple sites?**
A: Yes. All records are linked to a site name. Simply change the site selector in the dashboard or filter by site in the CRUD forms to switch between sites.

**Q: Is the module available in languages other than English?**
A: Yes. The module supports 10 languages (Italian, English, German, Spanish, French, Arabic, Catalan, Romanian, Portuguese, Greek). The interface language follows your QGIS locale setting.

### Dashboard

**Q: The pie chart is not displayed. What should I do?**
A: The pie chart requires `matplotlib` to be installed. If it is not available, the chart area will remain empty. Install matplotlib via: `pip install matplotlib`.

**Q: The dashboard shows zeros everywhere even though I have data.**
A: Verify that:
1. The correct site is selected in the dropdown
2. The correct year is selected (budget data is year-filtered)
3. The database connection is active (check the QGIS log for connection errors)

**Q: How is the budget progress bar calculated?**
A: The progress bar shows `(total actual spending / total estimated budget) x 100`, capped at 100%. If the estimated budget is zero, the bar stays at 0%.

### Personnel and Attendance

**Q: How do I link an attendance record to a person?**
A: Use the **Personnel ID** field in the Attendance form. This should match the `id_personale` value from the Personnel table.

**Q: Can I track multiple shifts per day for the same person?**
A: Yes. You can create multiple attendance records for the same person on the same date with different shift values.

### Equipment

**Q: What triggers the overdue maintenance alert?**
A: The dashboard checks all equipment for the selected site where `stato` is not `fuori_uso` (decommissioned). If any record has a `data_prossima_manutenzione` that is earlier than today's date, the alert is triggered.

**Q: How do I dismiss a maintenance alert?**
A: Update the equipment record's **Next Maintenance** date to a future date, then refresh the dashboard.

### Quantity Surveying

**Q: What coordinate reference system should the DEMs use?**
A: Both DEM layers must share the same CRS and should use a projected (metric) coordinate system (e.g., UTM). The area and volume calculations assume metric units.

**Q: Can I use the polygon zonal statistics with multiple polygons?**
A: Yes. The zonal statistics calculation iterates over all features in the selected polygon layer and aggregates the results.

**Q: Where are the calculation results stored?**
A: In the `computo_metrico_table` in your PyArchInit database. They are displayed in the calculation history table on the dashboard.

---

## Technical Notes

### Source Files

| File | Description |
|------|-------------|
| `tabs/Cantiere.py` | Site Dashboard dialog and logic |
| `tabs/Personale.py` | Personnel CRUD form controller |
| `tabs/Presenze.py` | Attendance CRUD form controller |
| `tabs/Attrezzature.py` | Equipment CRUD form controller |
| `tabs/Budget.py` | Budget CRUD form controller |
| `gui/ui/Cantiere.ui` | Dashboard Qt Designer layout |
| `gui/ui/Personale.ui` | Personnel form Qt Designer layout |
| `gui/ui/Presenze.ui` | Attendance form Qt Designer layout |
| `gui/ui/Attrezzature.ui` | Equipment form Qt Designer layout |
| `gui/ui/Budget.ui` | Budget form Qt Designer layout |

### Database Tables

| Table | Primary Key | Description |
|-------|-------------|-------------|
| `personale_table` | `id_personale` | Personnel records |
| `presenze_table` | `id_presenza` | Attendance records |
| `attrezzature_table` | `id_attrezzatura` | Equipment inventory |
| `budget_table` | `id_budget` | Budget line items |
| `computo_metrico_table` | `id_computo` | Quantity surveying calculations |

### Dependencies

| Component | Required |
|-----------|----------|
| PyArchInit | >= 5.0.x |
| QGIS | >= 3.22 |
| matplotlib | Optional (required for budget pie chart) |
| Database | PostgreSQL/PostGIS or SQLite/SpatiaLite |

### Theme Support

All five forms support PyArchInit's theme system via `ThemeManager`. The dashboard and CRUD forms automatically adapt to light and dark themes, and each form includes a theme toggle button.

---

*PyArchInit Documentation - Site Management*
*Version: 5.0.x*
*Last updated: February 2026*
