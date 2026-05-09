# modules/s3dgraphy/s3dgraphy_dot_bridge.py

## Overview

This file contains 15 documented elements.

## Classes

### S3DGraphyDotBridge

Bridge class that converts between s3dgraphy Extended Matrix format
and PyArchInit DOT/GraphML formats for yEd compatibility

#### Methods

##### __init__(self, db_manager)

Initializes a bridge instance that facilitates conversion between s3dgraphy Extended Matrix format and PyArchInit DOT/GraphML formats. Accepts an optional `db_manager` parameter and uses it to instantiate an `S3DGraphyIntegration` object stored as `self.s3d_integration`. The `self.spatial_groupings` attribute is initialized to `None` and is intended to store spatial or functional groupings at a later stage.

##### s3dgraphy_to_dot(self, site, area)

Convert s3dgraphy Extended Matrix data to DOT format

Args:
    site: Site name
    area: Optional area filter
    
Returns:
    DOT format string

##### export_integrated_matrix(self, site, area, output_dir, formats)

Export Extended Matrix in multiple formats with s3dgraphy integration

Args:
    site: Site name
    area: Optional area filter
    output_dir: Output directory (default: temp)
    formats: List of formats to export ['dot', 'graphml', 'json', 'phased']
    
Returns:
    Dictionary of format: filepath

### S3DGraphyExportDialog

Dialog for configuring integrated s3dgraphy/yEd export

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, db_manager, site, area)

Initializes the dialog for configuring an integrated s3dgraphy/yEd export operation. Accepts an optional parent widget, a `db_manager` instance, and `site` and `area` parameters, storing them as instance attributes alongside an `S3DGraphyDotBridge` instance and an empty `exported_files` dictionary. Sets the window title to `"Export Extended Matrix - Integrated s3dgraphy + yEd"`, enforces a minimum width of 500, and invokes `setupUI()` to build the interface.

##### setupUI(self)

Constructs and arranges all UI components for the export dialog using a `QVBoxLayout`. Adds a title label, description label, an "Export Formats" group box containing checkboxes for DOT, GraphML, JSON, and Phased Matrix formats, and a "Processing Options" group box containing checkboxes for stratigraphic validation, yEd auto-layout hints, period-based coloring, and spatial/functional groupings. Also adds a hidden `QProgressBar` and a button row with "Export" and "Cancel" buttons, wiring the export button to `on_export` and the cancel button to `reject`.

##### on_export(self)

Handle export button click

### S3DGraphyExportDialog

*No description available.*
A dialog class for exporting S3D Graphy data, designed to operate within the QGIS environment. When QGIS is available, the class provides the full export dialog functionality; when QGIS is not present, a dummy implementation is substituted that raises an `ImportError` upon instantiation. The dummy class accepts arbitrary positional and keyword arguments solely to surface a descriptive error message indicating that QGIS is required.

#### Methods

##### __init__(self)

*No description available.*
Dummy initializer for `S3DGraphyExportDialog` used when QGIS is not available in the environment. Unconditionally raises an `ImportError` with the message `"QGIS is required for S3DGraphyExportDialog"`, preventing instantiation of the class. Accepts arbitrary positional and keyword arguments (`*args`, `**kwargs`) but does not process them.

### Options

A temporary configuration container used internally to supply required option parameters to the `dottoxml` conversion utility. It initializes a fixed set of attributes in `__init__` covering output format, encoding, visual styling defaults (colors, arrows, labels), and processing flags. Instances of this class are constructed immediately before invoking `_convert_dot_to_graphml` to satisfy that method's expected options interface.

#### Methods

##### __init__(self)

Initializes an `Options` instance with a fixed set of default configuration values used for DOT-to-GraphML conversion via `dottoxml`. The attributes define output format (`'Graphml'`), display settings (node labels, edge labels, UML nodes, arrows, colors), attribute handling, separator character, arrow styles, default colors for nodes and edges, and input/output encodings. All values are hardcoded and not configurable through constructor parameters.

## Functions

### integrate_with_us_usm(us_usm_instance)

Add integrated export functionality to US_USM interface

Args:
    us_usm_instance: Instance of US_USM class

**Parameters:**
- `us_usm_instance`

### on_integrated_export()

Handler for integrated export button

