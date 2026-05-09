# tabs/DemPlotDialogs.py

## Overview

This file contains 10 documented elements.

## Classes

### DemSectionViewerDialog

Archaeological section viewer built from two DEMs and their
difference raster. Interactive row/column selector drives the
longitudinal and transverse sections.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)

Initializes the dialog window for visualizing DEM section analysis, accepting a parent widget, pre- and optional post-event DEM layers, an optional difference raster path, and a language code. Sets up a 2×2 matplotlib figure layout containing heatmap, histogram, longitudinal, and transverse section subplots, along with row/column spinbox controls that drive interactive section updates. If matplotlib is unavailable or no raster data can be loaded, the constructor renders an error label and a close button in place of the visualization widgets.

### DemPyVista3dDialog

Native VTK-based 3D viewer using ``pyvista`` and ``pyvistaqt``.

This is the highest-quality option of the four 3D backends in the
plugin (PyVista > Plotly > Qgs3DMapCanvas > matplotlib). PyVista
uses VTK directly, so:

  - **NaN handling is perfect** — clipped polygon edges are crisp,
    no spike artefacts
  - **Real shading / lighting** with directional + ambient lights
  - **Interactive rotation / pan / zoom** in a native Qt widget
  - **Fast** — VTK is GPU-accelerated where available
  - **Walls visible** — small vertical features are clearly
    rendered against the trench floor

Both ``pyvista`` and ``pyvistaqt`` are listed in PyArchInit's
``requirements.txt`` and shipped via ``ext_libs/`` so the dialog
is normally available out of the box.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)

Initializes the 3D viewer dialog by setting up the window title, dimensions (1100×780), and storing references to the provided DEM pre- and post-event layers, optional difference raster path, and resolved language code. It attempts to import `pyvista` and `pyvistaqt`, displaying an error label in the layout if either dependency is unavailable, then loads the raster arrays and aborts with an error if no data is found. On success, it constructs the control row (mode combo box, vertical exaggeration spin box, save and close buttons) and a `QtInteractor` VTK plotter widget, then triggers an initial scene build via `_rebuild`.

##### closeEvent(self, event)

Overrides the Qt `closeEvent` handler to perform cleanup before the widget closes. If `_plotter` is not `None`, it attempts to call `_plotter.close()`, silently suppressing any exceptions that occur during that call. The base class `closeEvent` is then invoked unconditionally to ensure standard close behaviour is preserved.

### DemPlotly3dDialog

Plotly-based 3D viewer, rendered inside a ``QWebEngineView``.

Uses ``plotly.graph_objects.Surface`` which handles NaN cells
transparently — no more vertical "spike" artefacts at the clip
polygon edges that the matplotlib ``plot_surface`` path produces.
The scene has directional lighting, hover tooltips with the real
elevation values and interactive rotation / pan / zoom.

If Plotly is not installed the dialog shows a clear message so
the caller can fall back to :class:`DemMatplotlib3dDialog`.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)

Initializes the Plotly-based 3D DEM viewer dialog, accepting a parent widget, a mandatory pre-event DEM layer, an optional post-event DEM layer, an optional difference raster path, and a language code (defaulting to `'en'`). The constructor sets up the window title and size, performs dependency checks for both `plotly` and `QWebEngineView` (displaying an informative error message and returning early if either is unavailable), then loads the raster data and builds the UI controls — including a mode selector (`QComboBox`), a vertical exaggeration spinner (`QDoubleSpinBox`), an HTML save button, and a close button — before embedding a `QWebEngineView` and triggering an initial render via `_rebuild`. If `plotly` is not installed or `QWebEngineView` is unavailable, the dialog renders only an error label, allowing the caller to fall back to an alternative renderer.

### DemMatplotlib3dDialog

Fallback 3D viewer based on ``mpl_toolkits.mplot3d``. Always works
(matplotlib is bundled with the plugin) but provides a lower-quality
view than the native Qgs3DMapCanvas.

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, dem_pre_layer, dem_post_layer, diff_raster_path, lang)

Initializes the 3D map dialog by setting up the window title, dimensions (1000×740), and storing references to the provided DEM layers and optional difference raster path. It attempts to import matplotlib and its 3D toolkit, displaying a localized error label and returning early if the import fails or if no raster data can be loaded. On success, it constructs the full UI including a matplotlib `Figure` with a 3D subplot, a mode selection combo box (`prepost`, `diff`, `pre`), a vertical exaggeration spin box, save and close buttons, and a navigation toolbar, then triggers an initial render via `_redraw()`.

