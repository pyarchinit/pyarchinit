# -*- coding: utf-8 -*-
"""
PyArchInit Splash Screen with animated rotating gears.

This module provides a splash screen widget that displays the PyArchInit logo
with two animated rotating circles/gears that spin in opposite directions.
"""

import os
import math
from qgis.PyQt.QtCore import Qt, QTimer, QRectF, QPointF
from qgis.PyQt.QtGui import (QPainter, QColor, QPen, QBrush, QPixmap,
                              QLinearGradient, QPainterPath, QFont)
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QApplication


class AnimatedGearWidget(QWidget):
    """Widget that displays animated rotating gears around a central logo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle1 = 0  # Angle for outer gear (clockwise)
        self.angle2 = 0  # Angle for inner gear (counter-clockwise)
        self.setMinimumSize(300, 300)

        # Load the PyArchInit logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "resources", "icons", "IconPAI.png")
        if os.path.exists(logo_path):
            self.logo = QPixmap(logo_path)
        else:
            # Fallback to main logo
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      "logo_pyarchinit.png")
            if os.path.exists(logo_path):
                self.logo = QPixmap(logo_path)
            else:
                self.logo = None

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)

        # Colors
        self.color1 = QColor("#3F51B5")  # Indigo
        self.color2 = QColor("#FF7043")  # Deep Orange
        self.color3 = QColor("#4CAF50")  # Green

    def start_animation(self):
        """Start the gear animation."""
        self.timer.start(30)  # ~33 FPS

    def stop_animation(self):
        """Stop the gear animation."""
        self.timer.stop()

    def update_animation(self):
        """Update the rotation angles."""
        self.angle1 = (self.angle1 + 2) % 360  # Clockwise
        self.angle2 = (self.angle2 - 3) % 360  # Counter-clockwise (faster)
        self.update()

    def paintEvent(self, event):
        """Paint the gears and logo."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get center point
        center_x = self.width() // 2
        center_y = self.height() // 2

        # Draw outer rotating gear/circle with dots
        self.draw_rotating_circle(painter, center_x, center_y,
                                   min(self.width(), self.height()) // 2 - 20,
                                   self.angle1, self.color1, 12, clockwise=True)

        # Draw inner rotating gear/circle with dots
        self.draw_rotating_circle(painter, center_x, center_y,
                                   min(self.width(), self.height()) // 2 - 50,
                                   self.angle2, self.color2, 8, clockwise=False)

        # Draw the logo in the center
        if self.logo:
            logo_size = min(self.width(), self.height()) // 2 - 60
            scaled_logo = self.logo.scaled(logo_size, logo_size,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            logo_x = center_x - scaled_logo.width() // 2
            logo_y = center_y - scaled_logo.height() // 2
            painter.drawPixmap(logo_x, logo_y, scaled_logo)

    def draw_rotating_circle(self, painter, cx, cy, radius, angle, color, num_dots, clockwise=True):
        """Draw a rotating circle with dots around it."""
        # Draw the main circle (arc segments)
        pen = QPen(color)
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Draw dashed arc
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)

        # Draw rotating dots
        dot_radius = 8
        for i in range(num_dots):
            dot_angle = angle + (i * 360 / num_dots)
            rad = math.radians(dot_angle)

            dot_x = cx + radius * math.cos(rad)
            dot_y = cy + radius * math.sin(rad)

            # Gradient effect - dots fade based on position
            alpha = int(255 * (0.3 + 0.7 * ((i + 1) / num_dots)))
            dot_color = QColor(color)
            dot_color.setAlpha(alpha)

            painter.setBrush(QBrush(dot_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(dot_x, dot_y), dot_radius, dot_radius)

        # Draw arc segments
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw partial arcs for gear effect
        for i in range(6):
            start_angle = int((angle + i * 60) * 16)
            span_angle = 40 * 16
            painter.drawArc(rect, start_angle, span_angle)


class PyArchInitSplash(QDialog):
    """
    Splash screen dialog for PyArchInit.

    Displays the PyArchInit logo with animated rotating gears
    and a status message.
    """

    def __init__(self, parent=None, message="Loading PyArchInit..."):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        self.init_ui(message)

    def init_ui(self, message):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create a container widget with background
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 20px;
                border: 2px solid #3F51B5;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("PyArchInit")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #3F51B5;
                background: transparent;
                border: none;
            }
        """)
        container_layout.addWidget(title)

        # Animated gear widget
        self.gear_widget = AnimatedGearWidget()
        self.gear_widget.setMinimumSize(250, 250)
        container_layout.addWidget(self.gear_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Status message
        self.status_label = QLabel(message)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                background: transparent;
                border: none;
                padding: 10px;
            }
        """)
        container_layout.addWidget(self.status_label)

        # Version info
        version_label = QLabel("Archaeological Data Management System")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #999999;
                background: transparent;
                border: none;
            }
        """)
        container_layout.addWidget(version_label)

        layout.addWidget(container)

        self.setFixedSize(350, 420)
        self.center_on_screen()

    def center_on_screen(self):
        """Center the splash screen on the screen."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def set_message(self, message):
        """Update the status message."""
        self.status_label.setText(message)
        QApplication.processEvents()

    def showEvent(self, event):
        """Start animation when shown."""
        super().showEvent(event)
        self.gear_widget.start_animation()

    def hideEvent(self, event):
        """Stop animation when hidden."""
        self.gear_widget.stop_animation()
        super().hideEvent(event)

    def closeEvent(self, event):
        """Stop animation when closed."""
        self.gear_widget.stop_animation()
        super().closeEvent(event)


# Convenience function to show splash during an operation
def show_splash_during_operation(operation_func, message="Loading...", parent=None):
    """
    Show the splash screen while executing an operation.

    Args:
        operation_func: Function to execute while showing splash
        message: Initial message to display
        parent: Parent widget

    Returns:
        The result of operation_func
    """
    splash = PyArchInitSplash(parent, message)
    splash.show()
    QApplication.processEvents()

    try:
        result = operation_func()
    finally:
        splash.close()

    return result


if __name__ == "__main__":
    # Test the splash screen
    import sys
    app = QApplication(sys.argv)

    splash = PyArchInitSplash(message="Installing dependencies...")
    splash.show()

    # Simulate progress
    def update_message():
        messages = [
            "Installing numpy...",
            "Installing pandas...",
            "Installing sqlalchemy...",
            "Installing reportlab...",
            "Finalizing installation..."
        ]
        for i, msg in enumerate(messages):
            QTimer.singleShot(i * 1500, lambda m=msg: splash.set_message(m))
        QTimer.singleShot(len(messages) * 1500, splash.close)

    update_message()

    sys.exit(app.exec())
