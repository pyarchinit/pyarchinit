# -*- coding: utf-8 -*-
"""
SAM Map Tools for PyArchInit

QgsMapTool implementations for interactive SAM segmentation:
- Point click tool for selecting individual stones
- Box/rectangle tool for area selection

Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal, QPointF
from qgis.PyQt.QtGui import QColor, QCursor
from qgis.PyQt.QtWidgets import QApplication

from qgis.core import (
    QgsPointXY, QgsRectangle, QgsGeometry, QgsWkbTypes,
    QgsCoordinateTransform, QgsProject
)
from qgis.gui import (
    QgsMapTool, QgsMapToolEmitPoint, QgsRubberBand,
    QgsMapCanvas, QgsVertexMarker
)


class SamPointMapTool(QgsMapToolEmitPoint):
    """
    Map tool for collecting point clicks for SAM segmentation.

    Users can click on multiple stones to mark them as prompts.
    Right-click or press Enter/Escape to finish collection.
    """

    # Signal emitted when point collection is finished
    # Emits list of points as [[x1,y1], [x2,y2], ...]
    pointsCollected = pyqtSignal(list)

    # Signal emitted when a point is added (for UI feedback)
    pointAdded = pyqtSignal(int)  # number of points collected

    # Signal emitted when cancelled
    cancelled = pyqtSignal()

    def __init__(self, canvas, raster_layer=None, on_points_collected=None, on_point_added=None, on_cancelled=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.raster_layer = raster_layer
        self.points = []  # Collected points in pixel coordinates
        self.markers = []  # Visual markers on map

        # Direct callbacks (bypass signal system)
        self.on_points_collected_callback = on_points_collected
        self.on_point_added_callback = on_point_added
        self.on_cancelled_callback = on_cancelled

        # Set cursor
        self.setCursor(Qt.CrossCursor)
        print(f"DEBUG SamPointMapTool: Initialized with canvas={canvas}, raster_layer={raster_layer}")
        print(f"DEBUG SamPointMapTool: Callbacks - on_points_collected={on_points_collected}")

    def canvasPressEvent(self, event):
        """Handle mouse press events"""
        print(f"DEBUG SamPointMapTool: canvasPressEvent called, button={event.button()}")
        if event.button() == Qt.LeftButton:
            # Get map coordinates
            map_point = self.toMapCoordinates(event.pos())
            print(f"DEBUG SamPointMapTool: Left click at map_point={map_point}")

            # Convert to pixel coordinates if we have a raster
            if self.raster_layer:
                pixel_coords = self._map_to_pixel(map_point)
                print(f"DEBUG SamPointMapTool: Converted to pixel_coords={pixel_coords}")
                if pixel_coords:
                    self.points.append(pixel_coords)
                    self._add_marker(map_point)
                    self.pointAdded.emit(len(self.points))
                    print(f"DEBUG SamPointMapTool: Point added, total={len(self.points)}")
                else:
                    print("DEBUG SamPointMapTool: pixel_coords is None (outside raster bounds?)")
            else:
                # If no raster, store map coordinates directly
                print("DEBUG SamPointMapTool: No raster layer, storing map coordinates")
                self.points.append([map_point.x(), map_point.y()])
                self._add_marker(map_point)
                self.pointAdded.emit(len(self.points))

        elif event.button() == Qt.RightButton:
            # Right-click to finish
            print("DEBUG SamPointMapTool: Right click - finishing collection")
            self._finish_collection()

    def keyPressEvent(self, event):
        """Handle key press events"""
        print(f"DEBUG SamPointMapTool: keyPressEvent called, key={event.key()}")
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            print("DEBUG SamPointMapTool: Enter pressed - finishing collection")
            self._finish_collection()
        elif event.key() == Qt.Key_Escape:
            print("DEBUG SamPointMapTool: Escape pressed - cancelling")
            self._cancel()
        elif event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
            # Remove last point
            print("DEBUG SamPointMapTool: Backspace/Delete pressed - removing last point")
            self._remove_last_point()

    def _map_to_pixel(self, map_point):
        """Convert map coordinates to raster pixel coordinates"""
        if not self.raster_layer:
            return None

        # Get raster extent and size
        extent = self.raster_layer.extent()
        width = self.raster_layer.width()
        height = self.raster_layer.height()

        # Calculate pixel coordinates
        px = int((map_point.x() - extent.xMinimum()) / extent.width() * width)
        py = int((extent.yMaximum() - map_point.y()) / extent.height() * height)

        # Check if within bounds
        if 0 <= px < width and 0 <= py < height:
            return [px, py]
        return None

    def _add_marker(self, point):
        """Add a visual marker at the clicked point"""
        marker = QgsVertexMarker(self.canvas)
        marker.setCenter(point)
        marker.setColor(QColor(255, 0, 0))
        marker.setFillColor(QColor(255, 0, 0, 100))
        marker.setIconSize(12)
        marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
        marker.setPenWidth(2)
        self.markers.append(marker)

    def _remove_last_point(self):
        """Remove the last added point"""
        if self.points:
            self.points.pop()
            if self.markers:
                marker = self.markers.pop()
                self.canvas.scene().removeItem(marker)
            self.pointAdded.emit(len(self.points))

    def _finish_collection(self):
        """Finish point collection and emit signal"""
        # Always emit signal, even if empty (dialog will handle empty case)
        print(f"DEBUG SamPointMapTool: _finish_collection called, points={len(self.points)}")
        points_to_emit = self.points.copy()
        self._cleanup()

        # First try direct callback (more reliable)
        if self.on_points_collected_callback:
            print(f"DEBUG SamPointMapTool: Calling callback with {len(points_to_emit)} points")
            try:
                self.on_points_collected_callback(points_to_emit)
                print("DEBUG SamPointMapTool: Callback executed successfully")
            except Exception as e:
                print(f"DEBUG SamPointMapTool: Callback error: {e}")
                import traceback
                traceback.print_exc()

        print(f"DEBUG SamPointMapTool: Emitting pointsCollected signal with {len(points_to_emit)} points")
        self.pointsCollected.emit(points_to_emit)

    def _cancel(self):
        """Cancel point collection"""
        print("DEBUG SamPointMapTool: _cancel called")
        self._cleanup()

        # First try direct callback (more reliable)
        if self.on_cancelled_callback:
            print("DEBUG SamPointMapTool: Calling cancelled callback")
            try:
                self.on_cancelled_callback()
                print("DEBUG SamPointMapTool: Cancelled callback executed successfully")
            except Exception as e:
                print(f"DEBUG SamPointMapTool: Cancelled callback error: {e}")

        print("DEBUG SamPointMapTool: Emitting cancelled signal")
        self.cancelled.emit()

    def _cleanup(self):
        """Remove all markers"""
        print("DEBUG SamPointMapTool: _cleanup called")
        for marker in self.markers:
            self.canvas.scene().removeItem(marker)
        self.markers = []
        self.points = []

    def deactivate(self):
        """Called when tool is deactivated"""
        print("DEBUG SamPointMapTool: deactivate called")
        self._cleanup()
        super().deactivate()

    def get_points(self):
        """Get collected points"""
        return self.points.copy()

    def clear_points(self):
        """Clear all collected points"""
        self._cleanup()


class SamBoxMapTool(QgsMapTool):
    """
    Map tool for drawing a rectangle/box for SAM segmentation.

    Users can click and drag to define a bounding box.
    The box is passed to SAM for segmentation within that area.
    """

    # Signal emitted when box is drawn
    # Emits box as [x1, y1, x2, y2] in pixel coordinates
    boxDrawn = pyqtSignal(list)

    # Signal emitted when cancelled
    cancelled = pyqtSignal()

    def __init__(self, canvas, raster_layer=None, on_box_drawn=None, on_cancelled=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.raster_layer = raster_layer
        self.rubber_band = None
        self.start_point = None
        self.is_drawing = False

        # Direct callbacks (bypass signal system)
        self.on_box_drawn_callback = on_box_drawn
        self.on_cancelled_callback = on_cancelled

        # Set cursor
        self.setCursor(Qt.CrossCursor)
        print(f"DEBUG SamBoxMapTool: Initialized with canvas={canvas}, raster_layer={raster_layer}")
        print(f"DEBUG SamBoxMapTool: Callbacks - on_box_drawn={on_box_drawn}, on_cancelled={on_cancelled}")

    def canvasPressEvent(self, event):
        """Handle mouse press - start drawing box"""
        print(f"DEBUG SamBoxMapTool: canvasPressEvent called, button={event.button()}")
        if event.button() == Qt.LeftButton:
            self.start_point = self.toMapCoordinates(event.pos())
            self.is_drawing = True
            print(f"DEBUG SamBoxMapTool: Started drawing at {self.start_point}")

            # Create rubber band for visual feedback
            self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            self.rubber_band.setColor(QColor(255, 0, 0, 100))
            self.rubber_band.setFillColor(QColor(255, 0, 0, 50))
            self.rubber_band.setWidth(2)
            print("DEBUG SamBoxMapTool: Rubber band created")

        elif event.button() == Qt.RightButton:
            print("DEBUG SamBoxMapTool: Right click - cancelling")
            self._cancel()

    def canvasMoveEvent(self, event):
        """Handle mouse move - update box preview"""
        if self.is_drawing and self.start_point:
            current_point = self.toMapCoordinates(event.pos())
            self._update_rubber_band(current_point)

    def canvasReleaseEvent(self, event):
        """Handle mouse release - finish drawing box"""
        print(f"DEBUG SamBoxMapTool: canvasReleaseEvent called, button={event.button()}, is_drawing={self.is_drawing}")
        if event.button() == Qt.LeftButton and self.is_drawing:
            end_point = self.toMapCoordinates(event.pos())
            print(f"DEBUG SamBoxMapTool: Finishing box at {end_point}")
            self._finish_box(end_point)

    def keyPressEvent(self, event):
        """Handle key press events"""
        print(f"DEBUG SamBoxMapTool: keyPressEvent called, key={event.key()}")
        if event.key() == Qt.Key_Escape:
            print("DEBUG SamBoxMapTool: Escape pressed - cancelling")
            self._cancel()

    def _update_rubber_band(self, current_point):
        """Update the rubber band rectangle"""
        if not self.rubber_band or not self.start_point:
            return

        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)

        # Create rectangle geometry
        rect = QgsRectangle(self.start_point, current_point)

        # Add points for the rectangle
        self.rubber_band.addPoint(QgsPointXY(rect.xMinimum(), rect.yMinimum()), False)
        self.rubber_band.addPoint(QgsPointXY(rect.xMinimum(), rect.yMaximum()), False)
        self.rubber_band.addPoint(QgsPointXY(rect.xMaximum(), rect.yMaximum()), False)
        self.rubber_band.addPoint(QgsPointXY(rect.xMaximum(), rect.yMinimum()), True)

    def _finish_box(self, end_point):
        """Finish drawing and emit the box coordinates"""
        print(f"DEBUG SamBoxMapTool: _finish_box called with end_point={end_point}")
        if not self.start_point:
            # If no start point, emit empty and cleanup
            print("DEBUG SamBoxMapTool: No start_point, emitting empty")
            self._cleanup()
            self.boxDrawn.emit([])
            return

        box_to_emit = None

        # Calculate box in pixel coordinates
        if self.raster_layer:
            print(f"DEBUG SamBoxMapTool: Converting to pixel coords, raster={self.raster_layer.name()}")
            start_pixel = self._map_to_pixel(self.start_point)
            end_pixel = self._map_to_pixel(end_point)
            print(f"DEBUG SamBoxMapTool: start_pixel={start_pixel}, end_pixel={end_pixel}")

            if start_pixel and end_pixel:
                # Format as [x1, y1, x2, y2]
                x1 = min(start_pixel[0], end_pixel[0])
                y1 = min(start_pixel[1], end_pixel[1])
                x2 = max(start_pixel[0], end_pixel[0])
                y2 = max(start_pixel[1], end_pixel[1])

                box_to_emit = [x1, y1, x2, y2]
                print(f"DEBUG SamBoxMapTool: Box in pixels: {box_to_emit}")
            else:
                print("DEBUG SamBoxMapTool: start_pixel or end_pixel is None")
        else:
            # If no raster, use map coordinates
            print("DEBUG SamBoxMapTool: No raster layer, using map coordinates")
            x1 = min(self.start_point.x(), end_point.x())
            y1 = min(self.start_point.y(), end_point.y())
            x2 = max(self.start_point.x(), end_point.x())
            y2 = max(self.start_point.y(), end_point.y())

            box_to_emit = [x1, y1, x2, y2]

        self._cleanup()

        # Prepare the result
        result = [box_to_emit] if box_to_emit else []

        # First try direct callback (more reliable)
        if self.on_box_drawn_callback:
            print(f"DEBUG SamBoxMapTool: Calling callback with box={result}")
            try:
                self.on_box_drawn_callback(result)
                print("DEBUG SamBoxMapTool: Callback executed successfully")
            except Exception as e:
                print(f"DEBUG SamBoxMapTool: Callback error: {e}")
                import traceback
                traceback.print_exc()

        # Also emit signal for backwards compatibility
        if box_to_emit:
            print(f"DEBUG SamBoxMapTool: Emitting boxDrawn signal with box={box_to_emit}")
            self.boxDrawn.emit([box_to_emit])
        else:
            print("DEBUG SamBoxMapTool: Emitting empty boxDrawn signal")
            self.boxDrawn.emit([])

    def _map_to_pixel(self, map_point):
        """Convert map coordinates to raster pixel coordinates"""
        if not self.raster_layer:
            return None

        extent = self.raster_layer.extent()
        width = self.raster_layer.width()
        height = self.raster_layer.height()

        px = int((map_point.x() - extent.xMinimum()) / extent.width() * width)
        py = int((extent.yMaximum() - map_point.y()) / extent.height() * height)

        # Clamp to valid range
        px = max(0, min(px, width - 1))
        py = max(0, min(py, height - 1))

        return [px, py]

    def _cancel(self):
        """Cancel box drawing"""
        print("DEBUG SamBoxMapTool: _cancel called")
        self._cleanup()

        # First try direct callback (more reliable)
        if self.on_cancelled_callback:
            print("DEBUG SamBoxMapTool: Calling cancelled callback")
            try:
                self.on_cancelled_callback()
                print("DEBUG SamBoxMapTool: Cancelled callback executed successfully")
            except Exception as e:
                print(f"DEBUG SamBoxMapTool: Cancelled callback error: {e}")

        print("DEBUG SamBoxMapTool: Emitting cancelled signal")
        self.cancelled.emit()

    def _cleanup(self):
        """Clean up rubber band and reset state"""
        print("DEBUG SamBoxMapTool: _cleanup called")
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        self.start_point = None
        self.is_drawing = False

    def deactivate(self):
        """Called when tool is deactivated"""
        print("DEBUG SamBoxMapTool: deactivate called")
        self._cleanup()
        super().deactivate()


class SamPolygonMapTool(QgsMapTool):
    """
    Map tool for drawing a freehand polygon for SAM segmentation.

    Users can click to add vertices, double-click or right-click to finish.
    The polygon defines the area to segment.
    """

    # Signal emitted when polygon is drawn
    # Emits polygon as WKT string
    polygonDrawn = pyqtSignal(str)

    # Signal emitted when cancelled
    cancelled = pyqtSignal()

    def __init__(self, canvas, raster_layer=None, on_polygon_drawn=None, on_cancelled=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.raster_layer = raster_layer
        self.rubber_band = None
        self.points = []  # Map coordinates
        self.is_drawing = False

        # Direct callbacks (bypass signal system)
        self.on_polygon_drawn_callback = on_polygon_drawn
        self.on_cancelled_callback = on_cancelled

        # Set cursor
        self.setCursor(Qt.CrossCursor)
        print(f"DEBUG SamPolygonMapTool: Initialized")

    def canvasPressEvent(self, event):
        """Handle mouse press - add vertex"""
        print(f"DEBUG SamPolygonMapTool: canvasPressEvent called, button={event.button()}")

        if event.button() == Qt.LeftButton:
            point = self.toMapCoordinates(event.pos())
            self.points.append(point)
            self.is_drawing = True
            print(f"DEBUG SamPolygonMapTool: Added point {len(self.points)}: {point}")

            # Create rubber band on first click
            if not self.rubber_band:
                self.rubber_band = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
                self.rubber_band.setColor(QColor(255, 0, 0, 100))
                self.rubber_band.setFillColor(QColor(255, 0, 0, 50))
                self.rubber_band.setWidth(2)

            self._update_rubber_band()

        elif event.button() == Qt.RightButton:
            if len(self.points) >= 3:
                # Finish polygon
                print("DEBUG SamPolygonMapTool: Right click - finishing polygon")
                self._finish_polygon()
            else:
                print("DEBUG SamPolygonMapTool: Right click - cancelling (not enough points)")
                self._cancel()

    def canvasDoubleClickEvent(self, event):
        """Handle double click - finish polygon"""
        print(f"DEBUG SamPolygonMapTool: canvasDoubleClickEvent called")
        if event.button() == Qt.LeftButton and len(self.points) >= 3:
            self._finish_polygon()

    def canvasMoveEvent(self, event):
        """Handle mouse move - update rubber band preview"""
        if self.is_drawing and self.rubber_band and self.points:
            current_point = self.toMapCoordinates(event.pos())
            self._update_rubber_band(current_point)

    def keyPressEvent(self, event):
        """Handle key press events"""
        print(f"DEBUG SamPolygonMapTool: keyPressEvent called, key={event.key()}")
        if event.key() == Qt.Key_Escape:
            print("DEBUG SamPolygonMapTool: Escape pressed - cancelling")
            self._cancel()
        elif event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if len(self.points) >= 3:
                print("DEBUG SamPolygonMapTool: Enter pressed - finishing polygon")
                self._finish_polygon()
        elif event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            # Remove last point
            if self.points:
                self.points.pop()
                self._update_rubber_band()
                print(f"DEBUG SamPolygonMapTool: Removed last point, {len(self.points)} remaining")

    def _update_rubber_band(self, preview_point=None):
        """Update the rubber band polygon"""
        if not self.rubber_band:
            return

        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)

        # Add existing points
        for point in self.points:
            self.rubber_band.addPoint(point, False)

        # Add preview point if provided
        if preview_point:
            self.rubber_band.addPoint(preview_point, False)

        # Close the polygon if we have points
        if self.points:
            self.rubber_band.addPoint(self.points[0], True)

    def _finish_polygon(self):
        """Finish drawing and emit the polygon"""
        print(f"DEBUG SamPolygonMapTool: _finish_polygon called with {len(self.points)} points")

        if len(self.points) < 3:
            print("DEBUG SamPolygonMapTool: Not enough points for polygon")
            self._cleanup()
            return

        # Create WKT from points
        coords = [(p.x(), p.y()) for p in self.points]
        # Close the polygon
        coords.append(coords[0])
        coord_str = ", ".join([f"{x} {y}" for x, y in coords])
        polygon_wkt = f"POLYGON(({coord_str}))"

        print(f"DEBUG SamPolygonMapTool: Created polygon WKT")

        self._cleanup()

        # First try direct callback
        if self.on_polygon_drawn_callback:
            print("DEBUG SamPolygonMapTool: Calling callback")
            try:
                self.on_polygon_drawn_callback(polygon_wkt)
                print("DEBUG SamPolygonMapTool: Callback executed successfully")
            except Exception as e:
                print(f"DEBUG SamPolygonMapTool: Callback error: {e}")
                import traceback
                traceback.print_exc()

        # Also emit signal
        print("DEBUG SamPolygonMapTool: Emitting polygonDrawn signal")
        self.polygonDrawn.emit(polygon_wkt)

    def _cancel(self):
        """Cancel polygon drawing"""
        print("DEBUG SamPolygonMapTool: _cancel called")
        self._cleanup()

        if self.on_cancelled_callback:
            print("DEBUG SamPolygonMapTool: Calling cancelled callback")
            try:
                self.on_cancelled_callback()
            except Exception as e:
                print(f"DEBUG SamPolygonMapTool: Cancelled callback error: {e}")

        print("DEBUG SamPolygonMapTool: Emitting cancelled signal")
        self.cancelled.emit()

    def _cleanup(self):
        """Clean up rubber band and reset state"""
        print("DEBUG SamPolygonMapTool: _cleanup called")
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
        self.points = []
        self.is_drawing = False

    def deactivate(self):
        """Called when tool is deactivated"""
        print("DEBUG SamPolygonMapTool: deactivate called")
        self._cleanup()
        super().deactivate()
