# modules/analysis/ut_heatmap_generator.py

## Overview

This file contains 9 documented elements.

## Classes

### UTHeatmapGenerator

Generates heatmaps for archaeological potential and risk analysis.

Supports three interpolation methods:
- KDE (Kernel Density Estimation): Best for density visualization
- IDW (Inverse Distance Weighting): Best for value interpolation
- Grid: Best for simple aggregation visualization

#### Methods

##### __init__(self, output_dir, crs)

Initialize the heatmap generator.

Args:
    output_dir: Directory for output files (default: temp dir)
    crs: Coordinate Reference System (QgsCoordinateReferenceSystem)

##### log_message(self, message, level)

Log message to QGIS if available.

##### generate_heatmap(self, points, values, method, cell_size, bandwidth, power, search_radius, extent, map_type)

Generate a heatmap using the specified method.

Args:
    points: List of (x, y) coordinate tuples
    values: List of values corresponding to each point
    method: 'kde', 'idw', or 'grid'
    cell_size: Grid cell size in map units
    bandwidth: KDE bandwidth (or 'auto')
    power: IDW power parameter
    search_radius: Maximum search radius for IDW
    extent: (xmin, ymin, xmax, ymax) or QgsRectangle
    map_type: 'potential' or 'risk' (for color styling)

Returns:
    Dictionary with:
        - raster_path: Path to output GeoTIFF
        - layer: QgsRasterLayer (if QGIS available)
        - stats: Statistics dictionary
        - method: Method used
        - timestamp: Generation timestamp

##### generate_vector_grid(self, points, values, cell_size, extent, value_field, map_type)

Generate a vector grid layer with aggregated values per cell.

Args:
    points: List of (x, y) coordinate tuples
    values: List of values corresponding to each point
    cell_size: Grid cell size in map units
    extent: (xmin, ymin, xmax, ymax) or None to auto-calculate
    value_field: Name of the value field
    map_type: 'potential' or 'risk'

Returns:
    Dictionary with:
        - layer: QgsVectorLayer (memory layer)
        - stats: Statistics dictionary
        - cell_count: Number of cells with data

##### generate_masked_heatmap(self, points, values, mask_polygon, method, cell_size, classification_scheme, map_type)

Generate a heatmap masked to an irregular polygon boundary (MOPR).

This method is designed for GNA export, generating heatmaps that are
clipped to the project area polygon and optionally classified into
VRP/VRD categories.

Args:
    points: List of (x, y) coordinate tuples
    values: List of values (potential_score or risk_score)
    mask_polygon: QgsGeometry of the project boundary (MOPR)
    method: 'kde', 'idw', or 'grid'
    cell_size: Grid cell size in map units (default 50m)
    classification_scheme: Dict for VRP/VRD classification:
        {(min, max): {'code': 'XX', 'label': '...', 'color': '#XXXXXX'}}
    map_type: 'potential' or 'risk' for styling

Returns:
    Dictionary with:
        - raster_path: Path to masked GeoTIFF
        - vector_layer: Classified multipolygon layer (if scheme provided)
        - stats: Statistics dictionary
        - method: Method used

##### generate_gna_layers(self, ut_records, mask_polygon, method, cell_size, vrp_scheme, vrd_scheme)

Generate complete GNA VRP and VRD layers from UT records.

Convenience method that generates both potential and risk
heatmaps masked to the project polygon.

Args:
    ut_records: List of UT records with potential_score and risk_score
    mask_polygon: QgsGeometry of project boundary
    method: Interpolation method
    cell_size: Grid cell size
    vrp_scheme: VRP classification scheme (or use default)
    vrd_scheme: VRD classification scheme (or use default)

Returns:
    Dictionary with vrp_layer, vrd_layer, vrp_raster, vrd_raster

## Functions

### get_cell_polygon(iy, ix)

Create polygon for a single cell.

**Parameters:**
- `iy`
- `ix`

