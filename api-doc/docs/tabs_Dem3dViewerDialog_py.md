# tabs/Dem3dViewerDialog.py

## Overview

This file contains 3 documented elements.

## Classes

### Dem3dViewerDialog

Stand-alone 3D viewer window.

Parameters
----------
parent : QWidget or None
terrain_layer : QgsRasterLayer
    DEM used as terrain source (typically the pre-excavation DEM).
drape_layer : QgsRasterLayer, optional
    DEM-difference raster draped over the terrain.
mesh_pre_layer : QgsMeshLayer, optional
mesh_post_layer : QgsMeshLayer, optional
lang : str
    2-letter language code for UI strings.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, terrain_layer, drape_layer, mesh_pre_layer, mesh_post_layer, lang)

Initializes the dialog by calling the parent constructor and storing the provided layer references (`terrain_layer`, `drape_layer`, `mesh_pre_layer`, `mesh_post_layer`) and language code as instance attributes. The language is validated against the `_I18N` dictionary and falls back to `'en'` if the supplied code is not found; the corresponding translation mapping is stored in `self._t`. The window title and size are then set, the UI is built via `_build_ui()`, and either a 3D canvas is configured through `_setup_3d_canvas()` (when `_HAS_3D` is true and `terrain_layer` is not `None`) or a fallback view is displayed via `_show_not_available()`.

