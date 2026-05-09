# modules/gis/sam_map_tools.py

## Overview

This file contains 22 documented elements.

## Classes

### SamPointMapTool

Map tool for collecting point clicks for SAM segmentation.

Users can click on multiple stones to mark them as prompts.
Right-click or press Enter/Escape to finish collection.

**Inherits from**: QgsMapToolEmitPoint

#### Methods

##### __init__(self, canvas, raster_layer, on_points_collected, on_point_added, on_cancelled)

Initializes a `SamPointMapTool` instance by calling the parent class constructor with the provided `canvas` and setting up the tool's core state, including an empty list for collected points in pixel coordinates and an empty list for visual map markers. Accepts optional references to a `raster_layer` and three direct callback functions — `on_points_collected`, `on_point_added`, and `on_cancelled` — which are stored as instance attributes to bypass the signal system. Sets the map cursor to `Qt.CrossCursor` upon initialization.

##### canvasPressEvent(self, event)

Handle mouse press events

##### keyPressEvent(self, event)

Handle key press events

##### deactivate(self)

Called when tool is deactivated

##### get_points(self)

Get collected points

##### clear_points(self)

Clear all collected points

### SamBoxMapTool

Map tool for drawing a rectangle/box for SAM segmentation.

Users can click and drag to define a bounding box.
The box is passed to SAM for segmentation within that area.

**Inherits from**: QgsMapTool

#### Methods

##### __init__(self, canvas, raster_layer, on_box_drawn, on_cancelled)

Initializes a `SamBoxMapTool` instance by calling the parent class constructor with the provided `canvas` and setting up the tool's internal state, including `raster_layer`, `rubber_band`, `start_point`, and `is_drawing`. Stores optional direct callback functions `on_box_drawn` and `on_cancelled`, which bypass the signal system, as instance attributes. Sets the map tool cursor to `Qt.CrossCursor` upon initialization.

##### canvasPressEvent(self, event)

Handle mouse press - start drawing box

##### canvasMoveEvent(self, event)

Handle mouse move - update box preview

##### canvasReleaseEvent(self, event)

Handle mouse release - finish drawing box

##### keyPressEvent(self, event)

Handle key press events

##### deactivate(self)

Called when tool is deactivated

### SamPolygonMapTool

Map tool for drawing a freehand polygon for SAM segmentation.

Users can click to add vertices, double-click or right-click to finish.
The polygon defines the area to segment.

**Inherits from**: QgsMapTool

#### Methods

##### __init__(self, canvas, raster_layer, on_polygon_drawn, on_cancelled)

Initializes a `SamPolygonMapTool` instance by calling the parent class constructor with the provided `canvas` and setting up the tool's internal state, including `raster_layer`, `rubber_band` (set to `None`), an empty `points` list, and an `is_drawing` flag set to `False`. Stores optional direct callback functions `on_polygon_drawn` and `on_cancelled` as instance attributes, bypassing the signal system. Sets the map tool cursor to `Qt.CrossCursor`.

##### canvasPressEvent(self, event)

Handle mouse press - add vertex

##### canvasDoubleClickEvent(self, event)

Handle double click - finish polygon

##### canvasMoveEvent(self, event)

Handle mouse move - update rubber band preview

##### keyPressEvent(self, event)

Handle key press events

##### deactivate(self)

Called when tool is deactivated

