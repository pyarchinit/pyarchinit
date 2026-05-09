# modules/utility/pyarchinit_dem_visualizer.py

## Overview

This file contains 14 documented elements.

## Functions

### ensure_output_dir(sito)

Return the absolute directory where per-site dashboard artifacts are saved.

``${PYARCHINIT_HOME}/site_dashboard/<sanitized-sito>`` — created as needed.
Falls back to ``~/pyarchinit/site_dashboard/<sito>`` when PYARCHINIT_HOME
is not set.

**Parameters:**
- `sito`

### timestamped_name(prefix, ext)

Return ``<prefix>_YYYYMMDD_HHMMSS.<ext>``.

**Parameters:**
- `prefix`
- `ext`

### compute_dem_difference(layer_pre, layer_post, out_path)

Run QgsRasterCalculator ``pre@1 - post@1`` using the pre-DEM's extent
and pixel grid. Returns ``0`` on success (QGIS convention).

**Parameters:**
- `layer_pre`
- `layer_post`
- `out_path`

### compute_volume_stats(diff_layer, cut_threshold)

Iterate the raster block once and return a dictionary of stats:

``{'total_area_m2', 'total_volume_m3', 'cut_volume_m3',
   'fill_volume_m3', 'max_abs', 'min_value', 'max_value'}``

- ``cut_volume`` = volume removed (diff > threshold, pre higher than post)
- ``fill_volume`` = volume added (diff < -threshold)
- ``total_area`` = area where |diff| > threshold
- ``total_volume`` = sum(|diff|) * pixel_area (gross earth movement)

**Parameters:**
- `diff_layer`
- `cut_threshold`

### style_diff_raster(layer, max_abs)

Apply a diverging color ramp centered on zero to a DEM difference raster.

Positive values (cut / removed material) are rendered in red,
negative values (fill / added material) in blue.

**Parameters:**
- `layer`
- `max_abs`

### style_cut_polygon(layer)

Semi-transparent red hatched fill for the intervention polygon.

**Parameters:**
- `layer`

### polygonize_cut_area(diff_raster_path, out_vector_path, threshold)

Vectorize the area where ``|diff| > threshold`` into a polygon layer.

Uses ``gdal:rastercalculator`` + ``gdal:polygonize`` via QGIS processing.
Returns the path on success, ``None`` on failure.

**Parameters:**
- `diff_raster_path`
- `out_vector_path`
- `threshold`

### add_layer_to_group(layer, group_name, expanded)

Insert ``layer`` into ``QgsProject`` under a dedicated layer-tree group.

**Parameters:**
- `layer`
- `group_name`
- `expanded`

### zoom_canvas_to(iface, rect)

Zoom the main map canvas to the given QgsRectangle + refresh.

**Parameters:**
- `iface`
- `rect`

### clip_raster_by_polygon(raster_path, poly_layer, out_path, dst_nodata, target_x_res, target_y_res, target_bounds)

Clip a raster to a polygon layer using ``gdal.Warp`` with a
temporary cutline shapefile.

Returns ``(out_path, None)`` on success, ``(None, error_message)``
on failure. Safe in all QGIS profiles: does not rely on the
``processing`` framework.

Handles:
  - layer source URIs with ``|layername=...`` suffixes (GPKG, ...)
  - polygon layers in a different CRS than the raster (passes
    ``cutlineSRS``)
  - memory vector layers (exported via
    ``QgsVectorFileWriter`` to a temp shapefile)

The optional ``target_x_res`` / ``target_y_res`` / ``target_bounds``
parameters force the output raster onto a specific pixel grid —
pass the same values to both the pre and post DEM clips so the two
outputs are perfectly aligned and can be subtracted by
``QgsRasterCalculator`` without resampling artefacts.

**Parameters:**
- `raster_path`
- `poly_layer`
- `out_path`
- `dst_nodata`
- `target_x_res`
- `target_y_res`
- `target_bounds`

### exclude_polygons_from_raster(raster_path, poly_layer, nodata_value)

Burn the features of ``poly_layer`` into ``raster_path`` using
``nodata_value``, effectively removing those areas from any
downstream volume calculation. Modifies the raster in place.

Used by the Computo Metrico workflow to subtract walls / built
structures from the excavation volume: the wall polygons are
rasterised onto the (already-clipped) DEM-difference raster, and
the burned cells become NODATA so ``compute_volume_stats`` skips
them.

Returns ``(True, None)`` on success, ``(False, error)`` otherwise.

**Parameters:**
- `raster_path`
- `poly_layer`
- `nodata_value`

### create_tin_mesh_from_dem(dem_layer, out_mesh_path, max_cells, clip_poly_layer)

Convert a DEM raster into a regular-grid 2DM mesh using a pure
Python writer.

Earlier versions of this function invoked ``native:pixelstopoints``
+ ``native:tinmeshcreation`` via the QGIS Processing framework,
which crashed QGIS on some builds. The new implementation:

  1. Reads the DEM directly with GDAL (no Processing).
  2. Downsamples in-memory with NumPy if the grid exceeds ``max_cells``.
  3. Writes a 2DM mesh file manually: one quad (``E4Q``) per valid
     DEM cell, nodes at pixel centres.

Because no processing algorithm is invoked, this is safe across
all QGIS versions and never triggers a segfault.

If ``clip_poly_layer`` is set, only cells whose centre lies inside
the polygon (via a pre-clipped GDAL warp) are kept — the mesh then
represents the excavation area only.

**Parameters:**
- `dem_layer`
- `out_mesh_path`
- `max_cells`
- `clip_poly_layer`

### load_mesh_layer(mesh_path, name)

Load a 2DM mesh file as a ``QgsMeshLayer``.

Historical note: previous versions also applied an automatic scalar
renderer via ``_style_mesh_terrain``. That path was dropped because
calling ``QgsMeshRendererScalarSettings`` APIs from Python triggers
a segfault on several QGIS builds (the signatures are unstable
across minor versions). The caller is responsible for styling the
mesh, or — preferably — for visualising the DEM directly via the
matplotlib 3D fallback without ever creating a mesh layer.

**Parameters:**
- `mesh_path`
- `name`

