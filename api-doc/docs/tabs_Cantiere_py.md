# tabs/Cantiere.py

## Overview

This file contains 24 documented elements.

## Classes

### pyarchinit_Cantiere

`pyarchinit_Cantiere` is a QGIS `QDialog` subclass that implements a multi-section site management dashboard for the pyArchInit archaeological data management plugin. It provides an interface for viewing and exporting budget summaries, personnel records, equipment inventories, and quantity surveying (computo metrico) data for a selected archaeological site and year. The dashboard also integrates DEM-difference volume calculations with optional polygon clipping and wall exclusion, 2D/3D visualization of results, per-site cost analysis, and export to PDF and CSV formats, with full localization across ten languages.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the Site Dashboard dialog by calling the parent constructor, storing the QGIS interface reference, and applying the UI setup and theme configuration including a theme toggle button.

Establishes a `_last_calc` state dictionary to track results from the most recent calculation run, with fields for raster paths, layers, statistics, and site metadata. Completes initialization by programmatically injecting visualization buttons, a walls combo box, and a cost panel into the existing UI layout, then wires calculation-mode radio buttons into an explicit `QButtonGroup` and reorganizes the top-level layout into a `QTabWidget` for backward-compatible UI enhancement.

##### on_pushButton_connect_pressed(self)

Connect to database using singleton pattern

##### charge_list(self)

Populate site and year dropdowns

##### apply_sito_set(self)

Pre-select the configured site if set

##### populate_raster_combos(self)

Refresh DEM combos from the current QGIS project while preserving
the user's current selection (so calling this right before Calcola
does not reset the chosen layers).

##### populate_vector_combos(self)

Refresh the polygon combo from the current QGIS project while
preserving the selection (see ``populate_raster_combos``).

##### retranslate_ui(self)

Translate all dashboard labels based on current locale.

##### refresh_dashboard(self)

Refresh all dashboard sections

##### refresh_budget_summary(self, sito, anno)

Query budget_table, calculate totals, update progress bar

##### refresh_personnel_summary(self, sito)

Query presenze_table - show all-time stats if no records today

##### refresh_equipment_summary(self, sito)

Query attrezzature_table

##### refresh_computo_history(self, sito)

Load computo metrico history into table widget

##### on_pushButton_calcola_pressed(self)

Run the DEM-difference workflow. The previous polygon-only mode
is no longer exposed by the UI (see ``_wire_calc_mode_radios``)
— when the user picks a polygon in "Layer Poligono" it is used
as a clip mask, not as a selector for a different calculation.

##### calculate_dem_difference(self)

Compute the volume/area from the difference of two DEMs AND
build the 2D visualization (persistent raster + polygon) in the
map canvas. Enables the 3D visualization button on success.

If a polygon layer is also selected in ``comboBox_layer_poligono``,
both DEMs are clipped to that polygon first (via ``gdal.Warp``)
so that the calculation, the 2D section viewer, the 3D view and
the mesh all operate on the intervention area only.

##### calculate_dem_polygon(self)

Polygon mode: clip a single DEM to a polygon layer, compute
area + volume (zonal stats) and feed the clipped DEM to the
2D section / 3D viewers so the visualisations show only the
intervention area.

##### on_pushButton_salva_computo_pressed(self)

Save computo metrico result to database

##### draw_budget_chart(self, records)

Draw an interactive Plotly pie chart in QWebEngineView, with matplotlib fallback.

##### on_pushButton_export_pdf_pressed(self)

Export a professional dashboard PDF with budget, personnel,
equipment and computo metrico sections.

Uses DejaVu Sans (bundled with matplotlib) for full Unicode
support - correctly renders Romanian (ă, ț, ș), Greek, Arabic, etc.

##### on_pushButton_export_excel_pressed(self)

Export dashboard data to CSV including the Computo Metrico section.

- UTF-8 with BOM ("utf-8-sig") so that Microsoft Excel and LibreOffice
  on any locale correctly decode Unicode characters (Romanian,
  Greek, Arabic, ...).
- Semicolon separator (European Excel default, avoids confusion with
  decimal commas).
- A top metadata block with site, year and generation timestamp.
- Dedicated sections for Budget, Personnel, Equipment and
  Computo Metrico plus an aggregated summary.

## Functions

### fmt_num(x, decimals)

*No description available.*
Formats a numeric value as a fixed-point decimal string with a configurable number of decimal places. The input `x` is coerced to `float`, treating `None` or other falsy values as `0`; the `decimals` parameter controls the number of digits after the decimal point, defaulting to `2`. Returns an empty string if the conversion raises a `TypeError` or `ValueError`.

**Parameters:**
- `x`
- `decimals`

### make_table_style()

Return standard professional table style commands.

### header_footer(canvas, doc)

*No description available.*
A page callback function applied to every page of the generated PDF document. It draws a styled header bar at the top of the page containing the application name (`"pyArchInit"`), site and year metadata, and a right-aligned generation timestamp; it also draws a footer bar at the bottom displaying a footer label and the current page number. The canvas graphics state is preserved and restored via `saveState()`/`restoreState()` to avoid side effects on subsequent drawing operations.

**Parameters:**
- `canvas`
- `doc`

