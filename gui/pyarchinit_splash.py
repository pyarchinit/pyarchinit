# -*- coding: utf-8 -*-
"""
PyArchInit Splash Screen with animated rotating gears.

This module provides a splash screen widget that displays the PyArchInit logo
with two animated rotating circles/gears that spin in opposite directions.
"""

import os
import math
import time
from qgis.PyQt.QtCore import Qt, QTimer, QRectF, QPointF
from qgis.PyQt.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QPixmap,
    QPainterPath,
    QRadialGradient,
)
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QApplication


class AnimatedGearWidget(QWidget):
    """Widget that displays animated rotating gears around a central logo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(580, 300)

        # Continuous, time-based animation state
        self._t0 = time.perf_counter()
        self._last_t = self._t0
        self._speed_deg_s = 0.0
        self._target_speed_deg_s = 120.0  # degrees/sec for gear 1 (faster rotation)
        self._tau_s = 0.08  # inertia time constant (sec) - faster response

        # Meshing gears (external gears)
        self.teeth1 = 18
        self.teeth2 = 30
        self.angle1 = 0.0
        self.angle2 = 0.0
        self._gear_path_cache = {}

        # Load the PyArchInit Archeoimagineers logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "resources", "icons", "logo_pyarchinit.png")
        if os.path.exists(logo_path):
            self.logo = QPixmap(logo_path)
        else:
            # Fallback to IconPAI
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      "resources", "icons", "IconPAI.png")
            if os.path.exists(logo_path):
                self.logo = QPixmap(logo_path)
            else:
                self.logo = None

        # Animation timer
        self.timer = QTimer(self)
        # More stable cadence on some platforms/QGIS builds
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.update_animation)

        # Colors matching the Archeoimagineers logo
        self.color1 = QColor("#E65100")  # Orange (from logo gradient)
        self.color2 = QColor("#C62828")  # Red (from logo gradient)
        self.color3 = QColor("#8B2500")  # Dark brown-red (logo text)

    def start_animation(self):
        """Start the gear animation."""
        self._last_t = time.perf_counter()
        self._speed_deg_s = self._target_speed_deg_s  # Start at full speed immediately
        self.timer.start(16)  # ~60 FPS

    def stop_animation(self):
        """Stop the gear animation."""
        self.timer.stop()

    def update_animation(self):
        """Update rotation angles (continuous, meshed gears)."""
        now = time.perf_counter()
        dt = now - self._last_t
        self._last_t = now

        # Avoid big jumps if the UI thread stalls
        if dt < 0.0:
            dt = 0.0
        elif dt > 0.05:
            dt = 0.05

        # Inertia: smoothly approach target speed
        tau = max(0.05, float(self._tau_s))
        alpha = 1.0 - math.exp(-dt / tau)
        self._speed_deg_s += (self._target_speed_deg_s - self._speed_deg_s) * alpha

        # Integrate primary gear
        self.angle1 = (self.angle1 + self._speed_deg_s * dt) % 360.0

        # Meshing: opposite direction and tooth ratio
        ratio = float(self.teeth1) / float(self.teeth2)
        # Phase so that teeth are interleaved along the line of centers
        phase = 180.0 / float(self.teeth2)
        self.angle2 = (-self.angle1 * ratio + phase) % 360.0
        self.update()

    def paintEvent(self, event):
        """Paint the gears and logo."""
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )

        # Center point
        cx = self.width() * 0.5
        cy = self.height() * 0.5

        # Compute gear sizes so they mesh and fit the widget (fill the window)
        min_dim = float(min(self.width(), self.height()))
        r_sum = min_dim * 0.65  # sum of pitch radii - double size to fill window
        module = (2.0 * r_sum) / float(self.teeth1 + self.teeth2)  # pitch = m * Z
        r1_pitch = 0.5 * module * float(self.teeth1)
        r2_pitch = 0.5 * module * float(self.teeth2)

        # Tooth height: keep it visible but avoid excessive overlap
        addendum = 0.65 * module
        dedendum = 0.75 * module

        r1_outer = r1_pitch + addendum
        r1_root = max(2.0, r1_pitch - dedendum)
        r2_outer = r2_pitch + addendum
        r2_root = max(2.0, r2_pitch - dedendum)

        # Place gears side-by-side so the pitch circles touch (teeth in presa)
        g1x = cx - r1_pitch
        g2x = cx + r2_pitch
        gy = cy

        # Draw gears with logo inside each gear's hub
        self._draw_gear(painter, g1x, gy, r1_root, r1_outer, self.teeth1, self.angle1, self.color1, self.logo)
        self._draw_gear(painter, g2x, gy, r2_root, r2_outer, self.teeth2, self.angle2, self.color2, self.logo)

    def _gear_path_squared(self, teeth, r_root, r_outer, tooth_fill=0.72, chamfer=0.0):
        """Return a squared-tooth gear profile centered at (0,0) as QPainterPath."""
        key = (int(teeth), float(r_root), float(r_outer), float(tooth_fill), float(chamfer))
        cached = self._gear_path_cache.get(key)
        if cached is not None:
            return cached

        teeth = int(max(6, teeth))
        r_root = float(max(2.0, r_root))
        r_outer = float(max(r_root + 1.0, r_outer))

        pitch = (2.0 * math.pi) / float(teeth)
        tooth = pitch * float(max(0.30, min(0.80, tooth_fill)))
        gap = pitch - tooth
        ch = tooth * float(max(0.0, min(0.20, chamfer)))

        pts = []
        for i in range(teeth):
            a0 = i * pitch
            a1 = a0 + gap * 0.5
            a2 = a1 + tooth

            # root -> outer (two vertical-ish flanks) -> root
            pts.append((r_root, a1))
            pts.append((r_outer, a1 + ch))
            pts.append((r_outer, a2 - ch))
            pts.append((r_root, a2))

        path = QPainterPath()
        r, ang = pts[0]
        path.moveTo(r * math.cos(ang), r * math.sin(ang))
        for r, ang in pts[1:]:
            path.lineTo(r * math.cos(ang), r * math.sin(ang))
        path.closeSubpath()

        self._gear_path_cache[key] = path
        return path

    def _draw_gear(self, painter, cx, cy, r_root, r_outer, teeth, angle_deg, base_color, logo=None):
        """Draw a shaded gear with squared teeth and optional logo in center."""
        gear_path = self._gear_path_squared(teeth, r_root, r_outer)

        # Shadow
        painter.save()
        painter.translate(cx + 2.0, cy + 2.0)
        painter.rotate(angle_deg)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 70)))
        painter.drawPath(gear_path)
        painter.restore()

        # Body
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(angle_deg)

        c = QColor(base_color)
        grad = QRadialGradient(QPointF(-r_outer * 0.20, -r_outer * 0.20), r_outer)
        grad.setColorAt(0.0, QColor(c).lighter(165))
        grad.setColorAt(0.35, QColor(c).lighter(125))
        grad.setColorAt(0.75, QColor(c))
        grad.setColorAt(1.0, QColor(c).darker(165))

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(255, 255, 255, 120), 1.1))
        painter.drawPath(gear_path)

        # Hub (no bore - will put logo instead)
        hub_r = (r_root + r_outer) * 0.42

        hub_grad = QRadialGradient(QPointF(-hub_r * 0.25, -hub_r * 0.25), hub_r)
        hub_grad.setColorAt(0.0, QColor(255, 255, 255, 220))
        hub_grad.setColorAt(0.5, QColor(255, 255, 255, 200))
        hub_grad.setColorAt(1.0, QColor(240, 240, 240, 180))

        painter.setPen(QPen(QColor(0, 0, 0, 60), 1.0))
        painter.setBrush(QBrush(hub_grad))
        painter.drawEllipse(QPointF(0, 0), hub_r, hub_r)

        painter.restore()

        # Draw logo in the center of the gear (not rotating)
        if logo:
            logo_size = int(hub_r * 1.6)
            scaled_logo = logo.scaled(logo_size, logo_size,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
            logo_x = int(cx - scaled_logo.width() * 0.5)
            logo_y = int(cy - scaled_logo.height() * 0.5)
            painter.drawPixmap(logo_x, logo_y, scaled_logo)


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
                border: 2px solid #E65100;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("pyArchInit 5")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #8B2500;
                background: transparent;
                border: none;
            }
        """)
        container_layout.addWidget(title)

        # Animated gear widget (wider to fit both gears)
        self.gear_widget = AnimatedGearWidget()
        self.gear_widget.setMinimumSize(580, 300)
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

        # Authors info
        authors_label = QLabel("built by Luca Mandolesi & Enzo Cocca")
        authors_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        authors_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666666;
                background: transparent;
                border: none;
                font-style: italic;
            }
        """)
        container_layout.addWidget(authors_label)

        layout.addWidget(container)

        self.setFixedSize(650, 520)
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
