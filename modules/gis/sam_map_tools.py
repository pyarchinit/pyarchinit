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

    def __init__(self, canvas, raster_layer=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.raster_layer = raster_layer
        self.points = []  # Collected points in pixel coordinates
        self.markers = []  # Visual markers on map

        # Set cursor
        self.setCursor(Qt.CrossCursor)
        print(f"DEBUG SamPointMapTool: Initialized with canvas={canvas}, raster_layer={raster_layer}")

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
        print(f"DEBUG SamPointMapTool: Emitting pointsCollected signal with {len(points_to_emit)} points")
        self.pointsCollected.emit(points_to_emit)

    def _cancel(self):
        """Cancel point collection"""
        print("DEBUG SamPointMapTool: _cancel called")
        self._cleanup()
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

    def __init__(self, canvas, raster_layer=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.raster_layer = raster_layer
        self.rubber_band = None
        self.start_point = None
        self.is_drawing = False

        # Set cursor
        self.setCursor(Qt.CrossCursor)
        print(f"DEBUG SamBoxMapTool: Initialized with canvas={canvas}, raster_layer={raster_layer}")

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

        # Always emit signal (dialog will handle empty case)
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
