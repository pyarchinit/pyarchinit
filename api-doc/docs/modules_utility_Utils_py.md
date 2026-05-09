# modules/utility/Utils.py

## Overview

This file contains 6 documented elements.

## Classes

### ClickTool

*No description available.*
A custom QGIS map tool that extends `QgsMapTool` to capture single mouse-click events on the map canvas. When the mouse button is released, it transforms the clicked screen position into map coordinates and passes the resulting point to a user-supplied callback function. The tool is initialized with a QGIS interface instance and a callback, which is invoked with the map point on each canvas release event.

**Inherits from**: QgsMapTool

#### Methods

##### __init__(self, iface, callback)

*No description available.*
Initializes a `ClickTool` instance by calling the parent `QgsMapTool` constructor with the map canvas obtained from `iface`. Stores references to `iface`, the provided `callback` callable, and the map canvas as instance attributes. Returns `None`.

##### canvasReleaseEvent(self, e)

*No description available.*
Handles a mouse button release event on the map canvas. Transforms the screen coordinates of the release position into map coordinates using the canvas's coordinate transform, then passes the resulting map point to the registered callback function. Returns `None`.

## Functions

### pointToWGS84(point, crs)

crs is the renderer crs

**Parameters:**
- `point`
- `crs`

### pointFromWGS84(point, crs)

*No description available.*
Transforms a point from WGS84 (EPSG:4326) into the specified target coordinate reference system (`crs`). It constructs a `QgsCoordinateTransform` from a source CRS defined by SRID 4326 to the provided target CRS, falling back to a project-instance-aware constructor if the first attempt fails. The transformed point is returned, with an additional fallback that wraps the input in `QgsPointXY` if the initial transform call raises an exception.

**Parameters:**
- `point`
- `crs`

