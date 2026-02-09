# -*- coding: utf-8 -*-
"""
PyArchInit Futuristic Splash Screen.

A dynamic, always-in-motion splash screen featuring:
- Particle field with depth parallax
- Orbiting rings with glowing trails
- Pulsing central logo with energy halo
- Animated scanning grid
- Flowing status text with typewriter effect
"""

import os
import math
import time
import random
from qgis.PyQt.QtCore import Qt, QTimer, QRectF, QPointF
from qgis.PyQt.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QPixmap,
    QPainterPath,
    QRadialGradient,
    QLinearGradient,
    QConicalGradient,
    QFont,
    QFontMetrics,
)
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialog, QApplication


class Particle:
    """A single particle in the field."""
    __slots__ = ('x', 'y', 'z', 'vx', 'vy', 'size', 'alpha', 'color_idx', 'life', 'max_life')

    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.z = random.uniform(0.2, 1.0)
        speed = random.uniform(0.3, 1.5) * self.z
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(1.0, 3.5) * self.z
        self.alpha = random.uniform(0.3, 0.9)
        self.color_idx = random.randint(0, 2)
        self.life = 0.0
        self.max_life = random.uniform(3.0, 8.0)


class OrbitalRing:
    """An orbiting ring around the logo."""
    __slots__ = ('radius', 'angle', 'speed', 'tilt', 'width', 'color_phase', 'dot_count')

    def __init__(self, radius, speed, tilt, width=1.5, dot_count=0):
        self.radius = radius
        self.angle = random.uniform(0, 360)
        self.speed = speed
        self.tilt = tilt
        self.width = width
        self.color_phase = random.uniform(0, math.pi * 2)
        self.dot_count = dot_count


class FuturisticSplashWidget(QWidget):
    """Widget rendering the futuristic animated splash content."""

    # Pre-computed color palette
    CYAN = QColor(0, 255, 255)
    ELECTRIC_BLUE = QColor(30, 144, 255)
    DEEP_BLUE = QColor(10, 15, 40)
    ORANGE_ACCENT = QColor(255, 140, 0)
    MAGENTA = QColor(180, 0, 255)
    WHITE = QColor(255, 255, 255)

    PALETTE = [CYAN, ELECTRIC_BLUE, ORANGE_ACCENT]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(700, 500)

        # Time tracking
        self._t0 = time.perf_counter()
        self._last_t = self._t0
        self._elapsed = 0.0

        # Particles
        self._particles = []
        self._max_particles = 90
        self._spawn_accum = 0.0

        # Orbital rings
        self._rings = [
            OrbitalRing(radius=95, speed=45, tilt=75, width=1.8, dot_count=6),
            OrbitalRing(radius=120, speed=-30, tilt=60, width=1.2, dot_count=8),
            OrbitalRing(radius=145, speed=20, tilt=85, width=0.9, dot_count=10),
            OrbitalRing(radius=70, speed=-55, tilt=50, width=1.5, dot_count=4),
        ]

        # Scanning grid
        self._grid_offset = 0.0

        # Logo pulse
        self._logo_pulse = 0.0

        # Energy nodes (small glowing points that orbit in patterns)
        self._nodes = []
        for i in range(5):
            self._nodes.append({
                'angle': random.uniform(0, 360),
                'radius': random.uniform(160, 200),
                'speed': random.uniform(15, 35) * (1 if random.random() > 0.5 else -1),
                'size': random.uniform(2.5, 5.0),
                'phase': random.uniform(0, math.pi * 2),
            })

        # Hexagonal wave
        self._hex_phase = 0.0

        # Load logos
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  "resources", "icons")

        logo_path = os.path.join(icons_dir, "logo_pyarchinit.png")
        if os.path.exists(logo_path):
            self.logo = QPixmap(logo_path)
        else:
            logo_path = os.path.join(icons_dir, "IconPAI.png")
            self.logo = QPixmap(logo_path) if os.path.exists(logo_path) else None

        # Partner logos (CNR ISPC + Horizon StratiGraph)
        cnr_path = os.path.join(icons_dir, "logo_cnr_ispc.png")
        self.logo_cnr = QPixmap(cnr_path) if os.path.exists(cnr_path) else None

        horizon_path = os.path.join(icons_dir, "logo_horizon_stratigraph.png")
        self.logo_horizon = QPixmap(horizon_path) if os.path.exists(horizon_path) else None

        # Status text
        self._status_text = ""
        self._displayed_text = ""
        self._char_timer = 0.0

        # Animation timer
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._tick)

    def start_animation(self):
        self._t0 = time.perf_counter()
        self._last_t = self._t0
        self.timer.start(16)  # ~60 FPS

    def stop_animation(self):
        self.timer.stop()

    def set_status(self, text):
        if text != self._status_text:
            self._status_text = text
            self._displayed_text = ""
            self._char_timer = 0.0

    def _tick(self):
        now = time.perf_counter()
        dt = min(now - self._last_t, 0.05)
        if dt < 0:
            dt = 0.0
        self._last_t = now
        self._elapsed += dt

        w, h = self.width(), self.height()
        cx, cy = w * 0.5, h * 0.5

        # Spawn particles
        self._spawn_accum += dt * 12.0
        while self._spawn_accum >= 1.0 and len(self._particles) < self._max_particles:
            self._spawn_accum -= 1.0
            self._particles.append(Particle(w, h))

        # Update particles
        alive = []
        for p in self._particles:
            p.life += dt
            if p.life > p.max_life:
                continue
            # Gentle drift toward center with orbital tendency
            dx = cx - p.x
            dy = cy - p.y
            dist = math.sqrt(dx * dx + dy * dy) + 0.01
            # Slight gravitational pull + orbital perpendicular
            pull = 0.15 * p.z
            p.vx += (dx / dist * pull - dy / dist * 0.08) * dt
            p.vy += (dy / dist * pull + dx / dist * 0.08) * dt
            # Damping
            p.vx *= 0.998
            p.vy *= 0.998
            p.x += p.vx * 60 * dt
            p.y += p.vy * 60 * dt
            # Wrap around
            if p.x < -20: p.x = w + 20
            elif p.x > w + 20: p.x = -20
            if p.y < -20: p.y = h + 20
            elif p.y > h + 20: p.y = -20
            alive.append(p)
        self._particles = alive

        # Update rings
        for ring in self._rings:
            ring.angle = (ring.angle + ring.speed * dt) % 360.0

        # Update nodes
        for node in self._nodes:
            node['angle'] = (node['angle'] + node['speed'] * dt) % 360.0

        # Grid scanning
        self._grid_offset = (self._grid_offset + dt * 40) % 60.0

        # Logo pulse
        self._logo_pulse = (self._logo_pulse + dt * 2.5) % (2 * math.pi)

        # Hex wave
        self._hex_phase += dt * 1.2

        # Typewriter effect
        if len(self._displayed_text) < len(self._status_text):
            self._char_timer += dt
            chars_to_add = int(self._char_timer * 30)
            if chars_to_add > 0:
                self._char_timer = 0.0
                end = min(len(self._displayed_text) + chars_to_add, len(self._status_text))
                self._displayed_text = self._status_text[:end]

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )

        w, h = self.width(), self.height()
        cx, cy = w * 0.5, h * 0.40  # Logo in upper portion to leave room for partner logos
        t = self._elapsed

        # === BACKGROUND: deep space gradient ===
        bg_grad = QRadialGradient(QPointF(cx, cy), max(w, h) * 0.7)
        bg_grad.setColorAt(0.0, QColor(15, 25, 60))
        bg_grad.setColorAt(0.4, QColor(8, 14, 38))
        bg_grad.setColorAt(1.0, QColor(3, 5, 15))
        painter.fillRect(0, 0, w, h, QBrush(bg_grad))

        # === SUBTLE GRID ===
        self._draw_grid(painter, w, h, t)

        # === PARTICLE FIELD ===
        self._draw_particles(painter, t)

        # === ENERGY WAVE RINGS (behind logo) ===
        self._draw_energy_waves(painter, cx, cy, t)

        # === ORBITAL RINGS ===
        self._draw_orbital_rings(painter, cx, cy, t)

        # === ENERGY NODES ===
        self._draw_energy_nodes(painter, cx, cy, t)

        # === CENTRAL LOGO with glow ===
        self._draw_logo(painter, cx, cy, t)

        # === TITLE ===
        self._draw_title(painter, cx, w, h, t)

        # === STATUS TEXT ===
        self._draw_status(painter, cx, w, h, t)

        # === BOTTOM INFO ===
        self._draw_bottom_info(painter, cx, w, h, t)

        # === PARTNER LOGOS ===
        self._draw_partner_logos(painter, cx, w, h, t)

        # === CORNER ACCENTS ===
        self._draw_corner_accents(painter, w, h, t)

        painter.end()

    def _draw_grid(self, painter, w, h, t):
        """Draw animated scanning grid."""
        spacing = 60
        offset = self._grid_offset

        painter.save()
        # Vertical lines
        alpha_base = 12
        x = offset
        while x < w:
            a = alpha_base + int(6 * math.sin(x * 0.02 + t * 0.5))
            painter.setPen(QPen(QColor(0, 200, 255, max(0, a)), 0.5))
            painter.drawLine(QPointF(x, 0), QPointF(x, h))
            x += spacing

        # Horizontal lines
        y = offset
        while y < h:
            a = alpha_base + int(6 * math.sin(y * 0.02 + t * 0.7))
            painter.setPen(QPen(QColor(0, 200, 255, max(0, a)), 0.5))
            painter.drawLine(QPointF(0, y), QPointF(w, y))
            y += spacing

        # Scanning line (horizontal sweep)
        scan_y = (t * 50) % (h + 40) - 20
        scan_grad = QLinearGradient(QPointF(0, scan_y - 15), QPointF(0, scan_y + 15))
        scan_grad.setColorAt(0.0, QColor(0, 255, 255, 0))
        scan_grad.setColorAt(0.5, QColor(0, 255, 255, 35))
        scan_grad.setColorAt(1.0, QColor(0, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(scan_grad))
        painter.drawRect(QRectF(0, scan_y - 15, w, 30))

        painter.restore()

    def _draw_particles(self, painter, t):
        """Draw particle field with glow."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        for p in self._particles:
            life_ratio = p.life / p.max_life
            # Fade in and out
            if life_ratio < 0.1:
                fade = life_ratio / 0.1
            elif life_ratio > 0.8:
                fade = (1.0 - life_ratio) / 0.2
            else:
                fade = 1.0

            flicker = 0.7 + 0.3 * math.sin(t * 3.0 + p.x * 0.1)
            alpha = int(p.alpha * fade * flicker * 255)
            alpha = max(0, min(255, alpha))

            color = QColor(self.PALETTE[p.color_idx])
            # Outer glow
            glow_size = p.size * 3.0
            glow_color = QColor(color)
            glow_color.setAlpha(max(0, alpha // 4))
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(QPointF(p.x, p.y), glow_size, glow_size)

            # Core
            color.setAlpha(alpha)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)

        painter.restore()

    def _draw_energy_waves(self, painter, cx, cy, t):
        """Draw expanding energy wave rings from center."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(3):
            phase = (t * 0.4 + i * 0.33) % 1.0
            radius = 60 + phase * 180
            alpha = int(40 * (1.0 - phase))
            if alpha <= 0:
                continue
            color = QColor(0, 255, 255, alpha)
            painter.setPen(QPen(color, 1.5 - phase * 0.8))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

        painter.restore()

    def _draw_orbital_rings(self, painter, cx, cy, t):
        """Draw 3D-projected orbital rings with glowing dots."""
        painter.save()

        for ring in self._rings:
            tilt_rad = math.radians(ring.tilt)
            cos_tilt = math.cos(tilt_rad)

            # Color cycling
            hue_shift = math.sin(t * 0.5 + ring.color_phase)
            if hue_shift > 0:
                color = QColor(
                    int(0 + hue_shift * 30),
                    int(200 + hue_shift * 55),
                    255
                )
            else:
                color = QColor(
                    int(255 + hue_shift * 75),
                    int(140 + hue_shift * 60),
                    int(0 - hue_shift * 100)
                )

            # Draw ring as series of segments
            segments = 72
            points = []
            for i in range(segments + 1):
                a = math.radians(ring.angle + i * (360.0 / segments))
                px = cx + ring.radius * math.cos(a)
                py = cy + ring.radius * math.sin(a) * cos_tilt
                points.append(QPointF(px, py))

            # Ring stroke with variable alpha (simulating 3D depth)
            for i in range(len(points) - 1):
                seg_angle = ring.angle + i * (360.0 / segments)
                depth = math.sin(math.radians(seg_angle))
                seg_alpha = int(100 + 80 * depth)
                seg_alpha = max(20, min(200, seg_alpha))
                c = QColor(color)
                c.setAlpha(seg_alpha)
                painter.setPen(QPen(c, ring.width))
                painter.drawLine(points[i], points[i + 1])

            # Glowing dots on the ring
            if ring.dot_count > 0:
                for j in range(ring.dot_count):
                    dot_angle = math.radians(ring.angle + j * (360.0 / ring.dot_count))
                    dx = cx + ring.radius * math.cos(dot_angle)
                    dy = cy + ring.radius * math.sin(dot_angle) * cos_tilt
                    depth = math.sin(math.radians(ring.angle + j * (360.0 / ring.dot_count)))

                    dot_size = 2.5 + 1.5 * (0.5 + 0.5 * depth)
                    dot_alpha = int(150 + 105 * depth)

                    # Glow
                    glow = QColor(color)
                    glow.setAlpha(max(0, dot_alpha // 3))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(glow))
                    painter.drawEllipse(QPointF(dx, dy), dot_size * 3, dot_size * 3)

                    # Core
                    core = QColor(255, 255, 255, max(0, dot_alpha))
                    painter.setBrush(QBrush(core))
                    painter.drawEllipse(QPointF(dx, dy), dot_size, dot_size)

        painter.restore()

    def _draw_energy_nodes(self, painter, cx, cy, t):
        """Draw orbiting energy nodes with trails."""
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        for node in self._nodes:
            a_rad = math.radians(node['angle'])
            r = node['radius'] + 10 * math.sin(t * 1.5 + node['phase'])
            nx = cx + r * math.cos(a_rad)
            ny = cy + r * math.sin(a_rad) * 0.6  # Flatten for 3D feel

            pulse = 0.7 + 0.3 * math.sin(t * 4.0 + node['phase'])
            sz = node['size'] * pulse

            # Trail (3 ghost positions)
            for ti in range(3):
                trail_a = math.radians(node['angle'] - (ti + 1) * 4 * (1 if node['speed'] > 0 else -1))
                trail_r = node['radius'] + 10 * math.sin(t * 1.5 + node['phase'] - (ti + 1) * 0.1)
                tx = cx + trail_r * math.cos(trail_a)
                ty = cy + trail_r * math.sin(trail_a) * 0.6
                trail_alpha = int(60 - ti * 18)
                if trail_alpha > 0:
                    tc = QColor(0, 255, 255, trail_alpha)
                    painter.setBrush(QBrush(tc))
                    trail_size = sz * (0.7 - ti * 0.15)
                    painter.drawEllipse(QPointF(tx, ty), trail_size, trail_size)

            # Outer glow
            glow = QColor(0, 255, 255, 40)
            painter.setBrush(QBrush(glow))
            painter.drawEllipse(QPointF(nx, ny), sz * 4, sz * 4)

            # Core bright
            core = QColor(200, 255, 255, 220)
            painter.setBrush(QBrush(core))
            painter.drawEllipse(QPointF(nx, ny), sz, sz)

        painter.restore()

    def _draw_logo(self, painter, cx, cy, t):
        """Draw central logo with pulsing energy halo."""
        pulse = 0.85 + 0.15 * math.sin(self._logo_pulse)

        # Energy halo (multi-layer glow)
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(4):
            radius = 55 + i * 12
            alpha = int((30 - i * 6) * pulse)
            if alpha <= 0:
                continue
            halo_grad = QRadialGradient(QPointF(cx, cy), radius)
            c1 = QColor(0, 220, 255, alpha)
            c2 = QColor(0, 180, 255, alpha // 2)
            c3 = QColor(0, 100, 200, 0)
            halo_grad.setColorAt(0.0, c1)
            halo_grad.setColorAt(0.6, c2)
            halo_grad.setColorAt(1.0, c3)
            painter.setBrush(QBrush(halo_grad))
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # Dark circle background for logo
        bg_grad = QRadialGradient(QPointF(cx, cy), 52)
        bg_grad.setColorAt(0.0, QColor(15, 25, 55, 240))
        bg_grad.setColorAt(0.8, QColor(8, 15, 40, 250))
        bg_grad.setColorAt(1.0, QColor(0, 10, 30, 200))
        painter.setBrush(QBrush(bg_grad))
        painter.setPen(QPen(QColor(0, 200, 255, int(100 * pulse)), 1.5))
        painter.drawEllipse(QPointF(cx, cy), 52, 52)

        painter.restore()

        # Logo image
        if self.logo:
            logo_size = int(72 * pulse)
            scaled = self.logo.scaled(
                logo_size, logo_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(
                int(cx - scaled.width() * 0.5),
                int(cy - scaled.height() * 0.5),
                scaled
            )

    def _draw_title(self, painter, cx, w, h, t):
        """Draw title with glow effect."""
        painter.save()

        title = "pyArchInit 5"
        font = QFont("Segoe UI", 26)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3.0)
        painter.setFont(font)

        title_y = h * 0.68
        metrics = QFontMetrics(font)
        title_rect = metrics.boundingRect(title)
        tx = cx - title_rect.width() * 0.5
        ty = title_y

        # Glow behind text
        glow_color = QColor(0, 200, 255, int(40 + 15 * math.sin(t * 2.0)))
        painter.setPen(QPen(glow_color, 4))
        painter.drawText(QPointF(tx, ty), title)

        # Main text - gradient from cyan to white
        painter.setPen(QPen(QColor(220, 245, 255, 240), 1))
        painter.drawText(QPointF(tx, ty), title)

        painter.restore()

    def _draw_status(self, painter, cx, w, h, t):
        """Draw status text with typewriter effect and cursor blink."""
        painter.save()

        font = QFont("Consolas", 11)
        painter.setFont(font)

        text = self._displayed_text
        cursor = "|" if int(t * 3) % 2 == 0 and len(self._displayed_text) < len(self._status_text) else ""
        display = text + cursor

        metrics = QFontMetrics(font)
        text_rect = metrics.boundingRect(display)
        tx = cx - text_rect.width() * 0.5
        ty = h * 0.76

        # Glow
        painter.setPen(QPen(QColor(0, 255, 200, 60), 3))
        painter.drawText(QPointF(tx, ty), display)

        # Main
        painter.setPen(QPen(QColor(0, 255, 200, 200), 1))
        painter.drawText(QPointF(tx, ty), display)

        painter.restore()

    def _draw_bottom_info(self, painter, cx, w, h, t):
        """Draw bottom info labels."""
        painter.save()

        # Version
        font_small = QFont("Segoe UI", 9)
        painter.setFont(font_small)
        alpha = int(120 + 30 * math.sin(t * 1.5))
        painter.setPen(QPen(QColor(100, 160, 200, alpha)))

        ver_text = "Archaeological Data Management System"
        metrics = QFontMetrics(font_small)
        vr = metrics.boundingRect(ver_text)
        painter.drawText(QPointF(cx - vr.width() * 0.5, h * 0.81), ver_text)

        # Authors
        font_xs = QFont("Segoe UI", 8)
        font_xs.setItalic(True)
        painter.setFont(font_xs)
        painter.setPen(QPen(QColor(80, 130, 180, alpha)))

        auth_text = "built by Luca Mandolesi & Enzo Cocca"
        metrics2 = QFontMetrics(font_xs)
        ar = metrics2.boundingRect(auth_text)
        painter.drawText(QPointF(cx - ar.width() * 0.5, h * 0.85), auth_text)

        painter.restore()

    def _draw_partner_logos(self, painter, cx, w, h, t):
        """Draw partner logos (CNR ISPC and Horizon StratiGraph) at the bottom center."""
        painter.save()

        logo_y = h * 0.89
        logo_height = 36
        spacing = 30  # space between logos
        pulse = 0.85 + 0.15 * math.sin(t * 1.8)

        logos = []
        if self.logo_cnr:
            logos.append(self.logo_cnr)
        if self.logo_horizon:
            logos.append(self.logo_horizon)

        if not logos:
            painter.restore()
            return

        # Scale logos to uniform height
        scaled_logos = []
        total_width = 0
        for logo in logos:
            scaled = logo.scaled(
                int(logo.width() * logo_height / logo.height()), logo_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            scaled_logos.append(scaled)
            total_width += scaled.width()
        total_width += spacing * (len(scaled_logos) - 1)

        # Draw separator line above logos
        line_y = logo_y - 14
        line_alpha = int(40 * pulse)
        line_grad = QLinearGradient(QPointF(cx - 120, line_y), QPointF(cx + 120, line_y))
        line_grad.setColorAt(0.0, QColor(0, 200, 255, 0))
        line_grad.setColorAt(0.3, QColor(0, 200, 255, line_alpha))
        line_grad.setColorAt(0.7, QColor(0, 200, 255, line_alpha))
        line_grad.setColorAt(1.0, QColor(0, 200, 255, 0))
        painter.setPen(QPen(QBrush(line_grad), 0.8))
        painter.drawLine(QPointF(cx - 120, line_y), QPointF(cx + 120, line_y))

        # "In collaboration with" label
        font_label = QFont("Segoe UI", 7)
        font_label.setItalic(True)
        painter.setFont(font_label)
        label_alpha = int(80 * pulse)
        painter.setPen(QPen(QColor(100, 170, 220, label_alpha)))
        label_text = "in collaboration with"
        metrics = QFontMetrics(font_label)
        lr = metrics.boundingRect(label_text)
        painter.drawText(QPointF(cx - lr.width() * 0.5, logo_y - 4), label_text)

        # Draw logos side by side centered
        x_start = cx - total_width * 0.5
        logo_top = int(logo_y)

        for i, scaled in enumerate(scaled_logos):
            x = int(x_start)

            # Subtle glow behind each logo
            glow_alpha = int(25 * pulse)
            glow_rect = QRectF(x - 4, logo_top - 4, scaled.width() + 8, scaled.height() + 8)
            glow_grad = QRadialGradient(glow_rect.center(), max(scaled.width(), scaled.height()) * 0.6)
            glow_grad.setColorAt(0.0, QColor(0, 180, 255, glow_alpha))
            glow_grad.setColorAt(1.0, QColor(0, 100, 200, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(glow_grad))
            painter.drawRoundedRect(glow_rect, 6, 6)

            # Draw the logo
            painter.setOpacity(0.75 + 0.2 * pulse)
            painter.drawPixmap(x, logo_top, scaled)
            painter.setOpacity(1.0)

            x_start += scaled.width() + spacing

        painter.restore()

    def _draw_corner_accents(self, painter, w, h, t):
        """Draw animated corner brackets."""
        painter.save()

        length = 30
        inset = 12
        alpha = int(100 + 50 * math.sin(t * 2.0))
        color = QColor(0, 200, 255, alpha)
        pen = QPen(color, 1.5)
        painter.setPen(pen)

        # Top-left
        painter.drawLine(QPointF(inset, inset), QPointF(inset + length, inset))
        painter.drawLine(QPointF(inset, inset), QPointF(inset, inset + length))

        # Top-right
        painter.drawLine(QPointF(w - inset, inset), QPointF(w - inset - length, inset))
        painter.drawLine(QPointF(w - inset, inset), QPointF(w - inset, inset + length))

        # Bottom-left
        painter.drawLine(QPointF(inset, h - inset), QPointF(inset + length, h - inset))
        painter.drawLine(QPointF(inset, h - inset), QPointF(inset, h - inset - length))

        # Bottom-right
        painter.drawLine(QPointF(w - inset, h - inset), QPointF(w - inset - length, h - inset))
        painter.drawLine(QPointF(w - inset, h - inset), QPointF(w - inset, h - inset - length))

        # Animated data ticks on edges
        tick_alpha = int(50 + 30 * math.sin(t * 3.0))
        tick_color = QColor(0, 180, 255, tick_alpha)
        painter.setPen(QPen(tick_color, 0.8))

        # Top edge - moving ticks
        for i in range(8):
            tx = ((t * 60 + i * 90) % (w + 40)) - 20
            painter.drawLine(QPointF(tx, 4), QPointF(tx, 10))

        # Bottom edge - moving ticks (opposite direction)
        for i in range(8):
            tx = w - ((t * 45 + i * 85) % (w + 40)) + 20
            painter.drawLine(QPointF(tx, h - 4), QPointF(tx, h - 10))

        painter.restore()


class PyArchInitSplash(QDialog):
    """
    Splash screen dialog for PyArchInit.

    Displays a futuristic, always-in-motion splash with particle effects,
    orbital rings, and dynamic animations.
    """

    def __init__(self, parent=None, message="Loading PyArchInit...", modal=False):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(modal)
        self.init_ui(message)

    def init_ui(self, message):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.splash_widget = FuturisticSplashWidget()
        self.splash_widget.set_status(message)
        layout.addWidget(self.splash_widget)

        self.setFixedSize(700, 500)
        self.center_on_screen()

    def center_on_screen(self):
        """Center the splash screen on the primary screen."""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(x, y)

    def set_message(self, message):
        """Update the status message."""
        self.splash_widget.set_status(message)
        QApplication.processEvents()

    def showEvent(self, event):
        super().showEvent(event)
        self.splash_widget.start_animation()

    def hideEvent(self, event):
        self.splash_widget.stop_animation()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.splash_widget.stop_animation()
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

    splash = PyArchInitSplash(message="Initializing quantum core...")
    splash.show()

    # Simulate progress
    def update_message():
        messages = [
            "Scanning archaeological databases...",
            "Loading stratigraphic modules...",
            "Calibrating GIS projections...",
            "Synchronizing data layers...",
            "PyArchInit ready!"
        ]
        for i, msg in enumerate(messages):
            QTimer.singleShot(i * 2000, lambda m=msg: splash.set_message(m))
        QTimer.singleShot(len(messages) * 2000, splash.close)

    update_message()

    sys.exit(app.exec())
