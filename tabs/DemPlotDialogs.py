# -*- coding: utf-8 -*-
"""
Matplotlib-based plot dialogs for the PyArchInit Site Dashboard
Computo Metrico feature.

- ``DemSectionViewerDialog``: classical archaeological section view built
  from two DEMs (pre / post) and their difference raster. Shows a 2D
  heat-map of the difference with the intervention polygon overlay,
  a longitudinal and a transverse cross-section (pre in blue, post in
  red, the excavated volume filled in between) and a histogram of the
  cut/fill values.

- ``DemMatplotlib3dDialog``: a matplotlib ``mpl_toolkits.mplot3d`` 3D
  surface view of the pre and post DEMs with adjustable vertical
  exaggeration. Used as the fall-back when ``qgis._3d`` is unavailable.

Both dialogs work with Qt5 and Qt6, use the ``backend_qtagg`` matplotlib
backend (auto-detects the Qt binding) and degrade gracefully when
matplotlib / GDAL are missing.

Author: Enzo Cocca
"""
from __future__ import absolute_import

import os

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QFileDialog, QComboBox, QSizePolicy, QMessageBox,
    QSpinBox,
)


# --------------------------------------------------------------------------- #
#                              Qt5 / Qt6 helpers                              #
# --------------------------------------------------------------------------- #

def _align_center():
    try:
        return Qt.AlignmentFlag.AlignCenter
    except AttributeError:
        return Qt.AlignCenter


def _sp_expanding():
    try:
        return QSizePolicy.Policy.Expanding
    except AttributeError:
        return QSizePolicy.Expanding


def _import_qt_figure_canvas():
    """Import matplotlib's Qt-agnostic canvas + toolbar (Qt5 or Qt6)."""
    try:
        from matplotlib.backends.backend_qtagg import (
            FigureCanvasQTAgg, NavigationToolbar2QT,
        )
        return FigureCanvasQTAgg, NavigationToolbar2QT
    except ImportError:
        from matplotlib.backends.backend_qt5agg import (
            FigureCanvasQTAgg, NavigationToolbar2QT,
        )
        return FigureCanvasQTAgg, NavigationToolbar2QT


# --------------------------------------------------------------------------- #
#                             Raster I/O helpers                              #
# --------------------------------------------------------------------------- #

def _read_raster(layer_or_path):
    """
    Return (array, nodata, geotransform, extent_tuple) for a raster layer
    or path. Uses GDAL for speed and numpy conversion.

    ``extent_tuple`` = (xmin, xmax, ymin, ymax) in map CRS — use directly
    with matplotlib's ``imshow(extent=..., origin='upper')``.
    """
    try:
        from osgeo import gdal
    except ImportError:
        try:
            import gdal  # older layouts
        except ImportError:
            return None, None, None, None

    import numpy as np
    try:
        path = layer_or_path if isinstance(layer_or_path, str) \
            else layer_or_path.source()
    except Exception:
        return None, None, None, None

    ds = gdal.Open(path)
    if ds is None:
        return None, None, None, None

    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray().astype('float64')
    nodata = band.GetNoDataValue()
    if nodata is not None:
        arr = np.where(arr == nodata, np.nan, arr)

    gt = ds.GetGeoTransform()  # (x0, pw, 0, y0, 0, -ph)
    n_cols = ds.RasterXSize
    n_rows = ds.RasterYSize
    x0 = gt[0]
    y0 = gt[3]
    pw = gt[1]
    ph = -gt[5]
    extent = (x0, x0 + pw * n_cols, y0 - ph * n_rows, y0)
    return arr, nodata, gt, extent


# --------------------------------------------------------------------------- #
#                          i18n                                               #
# --------------------------------------------------------------------------- #

_I18N = {
    'it': {
        'section_title': 'Sezioni DEM - Computo Metrico',
        'heat_title': 'Differenza DEM (pre - post)',
        'elev_heat_title': 'Quota DEM (m s.l.m.)',
        'elev_hist_title': 'Distribuzione quote',
        'hist_title': 'Distribuzione cut / fill',
        'long_section': 'Sezione longitudinale (E-W)',
        'trans_section': 'Sezione trasversale (N-S)',
        'axis_dist_m': 'Distanza (m)',
        'axis_z_m': 'Quota (m)',
        'axis_pixel_count': '# pixel',
        'axis_diff': 'Differenza (m)',
        'pre': 'DEM pre',
        'post': 'DEM post',
        'fill_label': 'Volume scavato',
        'legend_cut': 'Scavo',
        'legend_fill': 'Riporto',
        'save_png': 'Salva PNG',
        'close': 'Chiudi',
        'no_mpl': 'matplotlib non disponibile. Installalo per usare le sezioni.',
        'no_gdal': 'GDAL non disponibile. Impossibile leggere i raster.',
        'no_data': 'Nessun raster caricato. Esegui prima "Calcola".',
        'long_pos_lbl': 'Riga (0 = nord):',
        'trans_pos_lbl': 'Colonna (0 = ovest):',
        'exag_lbl': 'Esagerazione Z:',
        'view3d_title': 'Vista 3D DEM - Computo Metrico',
        'view3d_mode': 'Modalit\u00e0:',
        'mode_pre_post': 'Pre + Post',
        'mode_diff': 'Solo differenza',
        'mode_pre': 'Solo DEM pre',
        'rendering': 'Calcolo superficie in corso...',
    },
    'en': {
        'section_title': 'DEM Sections - Quantity Surveying',
        'heat_title': 'DEM difference (pre - post)',
        'elev_heat_title': 'DEM elevation (m a.s.l.)',
        'elev_hist_title': 'Elevation distribution',
        'hist_title': 'Cut / fill distribution',
        'long_section': 'Longitudinal section (E-W)',
        'trans_section': 'Transverse section (N-S)',
        'axis_dist_m': 'Distance (m)',
        'axis_z_m': 'Elevation (m)',
        'axis_pixel_count': '# pixels',
        'axis_diff': 'Difference (m)',
        'pre': 'Pre-DEM',
        'post': 'Post-DEM',
        'fill_label': 'Excavated volume',
        'legend_cut': 'Cut',
        'legend_fill': 'Fill',
        'save_png': 'Save PNG',
        'close': 'Close',
        'no_mpl': 'matplotlib not available. Install it to use the section view.',
        'no_gdal': 'GDAL not available. Cannot read raster data.',
        'no_data': 'No raster loaded. Run "Calcola" first.',
        'long_pos_lbl': 'Row (0 = north):',
        'trans_pos_lbl': 'Column (0 = west):',
        'exag_lbl': 'Vertical exaggeration:',
        'view3d_title': '3D DEM View - Quantity Surveying',
        'view3d_mode': 'Mode:',
        'mode_pre_post': 'Pre + Post',
        'mode_diff': 'Difference only',
        'mode_pre': 'Pre-DEM only',
        'rendering': 'Building surface...',
    },
}


def _t(lang, key):
    return _I18N.get(lang, _I18N['en']).get(key, _I18N['en'].get(key, key))


# --------------------------------------------------------------------------- #
#                    Section viewer (2D) - matplotlib                         #
# --------------------------------------------------------------------------- #

class DemSectionViewerDialog(QDialog):
    """
    Archaeological section viewer built from two DEMs and their
    difference raster. Interactive row/column selector drives the
    longitudinal and transverse sections.
    """

    def __init__(self, parent, dem_pre_layer, dem_post_layer=None,
                 diff_raster_path=None, lang='en'):
        super().__init__(parent)
        self.lang = lang if lang in _I18N else 'en'
        self.setWindowTitle(_t(self.lang, 'section_title'))
        self.resize(1100, 780)

        self.dem_pre_layer = dem_pre_layer
        self.dem_post_layer = dem_post_layer
        self.diff_raster_path = diff_raster_path

        self._pre_arr = None
        self._post_arr = None
        self._diff_arr = None
        self._extent = None
        self._gt = None

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        # Try to import matplotlib up-front
        try:
            from matplotlib.figure import Figure
            FigureCanvas, NavigationToolbar = _import_qt_figure_canvas()
        except Exception:
            err = QLabel(_t(self.lang, 'no_mpl'))
            err.setStyleSheet('color:#c62828; padding:40px;')
            err.setAlignment(_align_center())
            root.addWidget(err)
            self._add_close_button(root)
            return

        # Load rasters
        self._load_rasters()
        if self._pre_arr is None and self._diff_arr is None:
            err = QLabel(_t(self.lang, 'no_data'))
            err.setStyleSheet('color:#c62828; padding:40px;')
            err.setAlignment(_align_center())
            root.addWidget(err)
            self._add_close_button(root)
            return

        # Build figure with 2x2 subplots
        self.fig = Figure(figsize=(11, 7.5), tight_layout=True)
        gs = self.fig.add_gridspec(2, 2, width_ratios=[1.3, 1], height_ratios=[1, 1])
        self.ax_heat = self.fig.add_subplot(gs[0, 0])
        self.ax_hist = self.fig.add_subplot(gs[0, 1])
        self.ax_long = self.fig.add_subplot(gs[1, 0])
        self.ax_trans = self.fig.add_subplot(gs[1, 1])

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(_sp_expanding(), _sp_expanding())

        # Controls row: row / col selectors, save / close buttons
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel(_t(self.lang, 'long_pos_lbl')))
        self.row_spin = QSpinBox()
        self.row_spin.setRange(0, 0)
        self.row_spin.valueChanged.connect(self._update_sections)
        ctrl.addWidget(self.row_spin)
        ctrl.addSpacing(12)
        ctrl.addWidget(QLabel(_t(self.lang, 'trans_pos_lbl')))
        self.col_spin = QSpinBox()
        self.col_spin.setRange(0, 0)
        self.col_spin.valueChanged.connect(self._update_sections)
        ctrl.addWidget(self.col_spin)
        ctrl.addStretch(1)

        btn_save = QPushButton(_t(self.lang, 'save_png'))
        btn_save.clicked.connect(self._save_png)
        ctrl.addWidget(btn_save)
        btn_close = QPushButton(_t(self.lang, 'close'))
        btn_close.clicked.connect(self.accept)
        ctrl.addWidget(btn_close)

        toolbar = NavigationToolbar(self.canvas, self)
        root.addWidget(toolbar)
        root.addWidget(self.canvas, 1)
        root.addLayout(ctrl)

        self._draw_static()
        self._update_sections()

    def _add_close_button(self, root):
        btn = QPushButton(_t(self.lang, 'close'))
        btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn)
        root.addLayout(row)

    # -------------------------------------------------------------- data --

    def _load_rasters(self):
        if self.dem_pre_layer is not None:
            self._pre_arr, _, self._gt, self._extent = _read_raster(
                self.dem_pre_layer)
        if self.dem_post_layer is not None:
            self._post_arr, _, _, _ = _read_raster(self.dem_post_layer)
        if self.diff_raster_path:
            diff_arr, _, diff_gt, diff_extent = _read_raster(self.diff_raster_path)
            self._diff_arr = diff_arr
            # If we do not yet have an extent, take it from the diff raster
            if self._extent is None:
                self._extent = diff_extent
                self._gt = diff_gt

        # If we have pre + post but no diff, compute it on the fly
        if (self._diff_arr is None and self._pre_arr is not None
                and self._post_arr is not None):
            try:
                if self._post_arr.shape == self._pre_arr.shape:
                    self._diff_arr = self._pre_arr - self._post_arr
            except Exception:
                pass

        # Range spin boxes
        ref = self._pre_arr if self._pre_arr is not None else self._diff_arr
        if ref is not None:
            n_rows, n_cols = ref.shape
            self.__n_rows = n_rows
            self.__n_cols = n_cols

    # -------------------------------------------------------------- draw --

    def _draw_static(self):
        """Draw the heat map + histogram once (they do not depend on row/col)."""
        import numpy as np

        # Pre-fill spin ranges
        if hasattr(self, '_DemSectionViewerDialog__n_rows'):
            n_rows = self.__n_rows
            n_cols = self.__n_cols
            self.row_spin.blockSignals(True)
            self.col_spin.blockSignals(True)
            self.row_spin.setRange(0, max(0, n_rows - 1))
            self.col_spin.setRange(0, max(0, n_cols - 1))
            self.row_spin.setValue(n_rows // 2)
            self.col_spin.setValue(n_cols // 2)
            self.row_spin.blockSignals(False)
            self.col_spin.blockSignals(False)

        # Decide which array drives the heatmap + histogram
        # - Diff mode: use the (pre-post) diff array with RdBu_r diverging
        #   colormap and a cut/fill histogram.
        # - Single-DEM mode (polygon mode, no post): fall back to the
        #   pre-DEM array with a terrain colormap and an elevation
        #   histogram. This is what the user sees when running the
        #   "DEM su Poligono" mode.
        single_mode = self._diff_arr is None and self._pre_arr is not None
        self._single_mode = single_mode

        # ----- Heatmap
        self.ax_heat.clear()
        if self._diff_arr is not None:
            arr = self._diff_arr
            max_abs = float(np.nanmax(np.abs(arr))) or 1.0
            im = self.ax_heat.imshow(
                arr,
                cmap='RdBu_r', vmin=-max_abs, vmax=max_abs,
                extent=self._extent if self._extent else None,
                origin='upper', aspect='equal', interpolation='nearest',
            )
            self.fig.colorbar(im, ax=self.ax_heat, fraction=0.035, pad=0.02)
            self.ax_heat.set_title(_t(self.lang, 'heat_title'), fontsize=10)
        elif single_mode:
            arr = self._pre_arr
            vmin = float(np.nanmin(arr))
            vmax = float(np.nanmax(arr))
            im = self.ax_heat.imshow(
                arr,
                cmap='terrain', vmin=vmin, vmax=vmax,
                extent=self._extent if self._extent else None,
                origin='upper', aspect='equal', interpolation='nearest',
            )
            self.fig.colorbar(im, ax=self.ax_heat, fraction=0.035, pad=0.02)
            self.ax_heat.set_title(
                _t(self.lang, 'elev_heat_title'), fontsize=10)
        else:
            self.ax_heat.set_title(_t(self.lang, 'heat_title'), fontsize=10)
        self.ax_heat.grid(True, alpha=0.3, linestyle=':')

        # Rubber-band style guides (redrawn in _update_sections)
        self._hline = None
        self._vline = None

        # ----- Histogram
        self.ax_hist.clear()
        if self._diff_arr is not None:
            flat = self._diff_arr[~np.isnan(self._diff_arr)]
            if flat.size > 0:
                self.ax_hist.hist(
                    flat, bins=50, color='#90a4ae', edgecolor='#455a64',
                    linewidth=0.5,
                )
                self.ax_hist.axvline(0, color='black', linewidth=0.8, linestyle='--')
                self.ax_hist.axvspan(
                    0, float(np.nanmax(flat)),
                    alpha=0.12, color='#b2182b',
                    label=_t(self.lang, 'legend_cut'),
                )
                self.ax_hist.axvspan(
                    float(np.nanmin(flat)), 0,
                    alpha=0.12, color='#2166ac',
                    label=_t(self.lang, 'legend_fill'),
                )
                self.ax_hist.legend(fontsize=7, loc='upper right')
            self.ax_hist.set_title(_t(self.lang, 'hist_title'), fontsize=10)
            self.ax_hist.set_xlabel(_t(self.lang, 'axis_diff'), fontsize=8)
        elif single_mode:
            flat = self._pre_arr[~np.isnan(self._pre_arr)]
            if flat.size > 0:
                self.ax_hist.hist(
                    flat, bins=50, color='#8d6e63', edgecolor='#4e342e',
                    linewidth=0.5,
                )
                mean_v = float(np.mean(flat))
                self.ax_hist.axvline(
                    mean_v, color='#1b5e20', linewidth=1.0, linestyle='--',
                    label=f"mean {mean_v:.2f} m",
                )
                self.ax_hist.legend(fontsize=7, loc='upper right')
            self.ax_hist.set_title(_t(self.lang, 'elev_hist_title'), fontsize=10)
            self.ax_hist.set_xlabel(_t(self.lang, 'axis_z_m'), fontsize=8)
        else:
            self.ax_hist.set_title(_t(self.lang, 'hist_title'), fontsize=10)
            self.ax_hist.set_xlabel(_t(self.lang, 'axis_diff'), fontsize=8)
        self.ax_hist.set_ylabel(_t(self.lang, 'axis_pixel_count'), fontsize=8)
        self.ax_hist.grid(True, alpha=0.3, linestyle=':')

    def _update_sections(self):
        import numpy as np

        row = self.row_spin.value()
        col = self.col_spin.value()

        # Redraw horizontal/vertical guides on the heatmap
        if self._extent is not None and self._diff_arr is not None:
            x_min, x_max, y_min, y_max = self._extent
            n_rows, n_cols = self._diff_arr.shape
            y_pos = y_max - (row + 0.5) * (y_max - y_min) / n_rows
            x_pos = x_min + (col + 0.5) * (x_max - x_min) / n_cols

            if self._hline is not None:
                try:
                    self._hline.remove()
                except Exception:
                    pass
            if self._vline is not None:
                try:
                    self._vline.remove()
                except Exception:
                    pass
            self._hline = self.ax_heat.axhline(
                y_pos, color='#1b5e20', linewidth=1.2, linestyle='-')
            self._vline = self.ax_heat.axvline(
                x_pos, color='#4a148c', linewidth=1.2, linestyle='--')

        # ----- Longitudinal section (row across columns)
        self.ax_long.clear()
        if self._pre_arr is not None:
            xs = self._axis_coords('x')
            pre_row = self._pre_arr[row, :] if row < self._pre_arr.shape[0] else None
            post_row = None
            if self._post_arr is not None and self._post_arr.shape == self._pre_arr.shape:
                post_row = self._post_arr[row, :]
            self._plot_section(self.ax_long, xs, pre_row, post_row,
                               title=_t(self.lang, 'long_section') + f"  (row={row})")
        elif self._diff_arr is not None:
            xs = self._axis_coords('x')
            diff_row = self._diff_arr[row, :] if row < self._diff_arr.shape[0] else None
            self._plot_diff_only(self.ax_long, xs, diff_row,
                                 title=_t(self.lang, 'long_section') + f"  (row={row})")

        # ----- Transverse section (col across rows)
        self.ax_trans.clear()
        if self._pre_arr is not None:
            ys = self._axis_coords('y')
            pre_col = self._pre_arr[:, col] if col < self._pre_arr.shape[1] else None
            post_col = None
            if self._post_arr is not None and self._post_arr.shape == self._pre_arr.shape:
                post_col = self._post_arr[:, col]
            self._plot_section(self.ax_trans, ys, pre_col, post_col,
                               title=_t(self.lang, 'trans_section') + f"  (col={col})")
        elif self._diff_arr is not None:
            ys = self._axis_coords('y')
            diff_col = self._diff_arr[:, col] if col < self._diff_arr.shape[1] else None
            self._plot_diff_only(self.ax_trans, ys, diff_col,
                                 title=_t(self.lang, 'trans_section') + f"  (col={col})")

        self.canvas.draw_idle()

    def _axis_coords(self, direction):
        """Return physical coordinates (m) along the X or Y axis of the raster."""
        import numpy as np
        if self._extent is None:
            return None
        x_min, x_max, y_min, y_max = self._extent
        ref = self._pre_arr if self._pre_arr is not None else self._diff_arr
        if ref is None:
            return None
        if direction == 'x':
            return np.linspace(x_min, x_max, ref.shape[1])
        return np.linspace(y_max, y_min, ref.shape[0])

    def _plot_section(self, ax, axis, pre_row, post_row, title=''):
        import numpy as np
        if pre_row is None:
            return
        ax.plot(axis, pre_row, color='#1565c0', linewidth=1.5,
                label=_t(self.lang, 'pre'))
        if post_row is not None:
            ax.plot(axis, post_row, color='#c62828', linewidth=1.5,
                    label=_t(self.lang, 'post'))
            # Fill between the two curves (volume removed)
            above = np.where(pre_row > post_row, pre_row, post_row)
            below = np.where(pre_row > post_row, post_row, pre_row)
            ax.fill_between(axis, below, above,
                            where=~(np.isnan(above) | np.isnan(below)),
                            facecolor='#ef9a9a', alpha=0.5,
                            edgecolor='#b71c1c', linewidth=0.4,
                            label=_t(self.lang, 'fill_label'))
        ax.set_title(title, fontsize=9)
        ax.set_xlabel(_t(self.lang, 'axis_dist_m'), fontsize=8)
        ax.set_ylabel(_t(self.lang, 'axis_z_m'), fontsize=8)
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(fontsize=7, loc='best')

    def _plot_diff_only(self, ax, axis, diff_row, title=''):
        """When no pre/post pair is available, plot only the diff as a line."""
        import numpy as np
        if diff_row is None:
            return
        ax.plot(axis, diff_row, color='#6a1b9a', linewidth=1.5,
                label=_t(self.lang, 'axis_diff'))
        ax.axhline(0, color='#455a64', linewidth=0.6, linestyle='--')
        ax.fill_between(axis, 0, diff_row, where=diff_row > 0,
                        facecolor='#ef9a9a', alpha=0.5,
                        label=_t(self.lang, 'legend_cut'))
        ax.fill_between(axis, 0, diff_row, where=diff_row < 0,
                        facecolor='#90caf9', alpha=0.5,
                        label=_t(self.lang, 'legend_fill'))
        ax.set_title(title, fontsize=9)
        ax.set_xlabel(_t(self.lang, 'axis_dist_m'), fontsize=8)
        ax.set_ylabel(_t(self.lang, 'axis_diff'), fontsize=8)
        ax.grid(True, alpha=0.3, linestyle=':')
        ax.legend(fontsize=7, loc='best')

    def _save_png(self):
        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        path, _ = QFileDialog.getSaveFileName(
            self, _t(self.lang, 'save_png'),
            os.path.join(home, 'dem_section.png'),
            'PNG (*.png)')
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=200, bbox_inches='tight')
            QMessageBox.information(self, 'OK',
                                    f"Saved: {path}")
        except Exception as ex:
            QMessageBox.warning(self, 'Error', str(ex))


# --------------------------------------------------------------------------- #
#                     PyVista 3D viewer (primary, native VTK)                 #
# --------------------------------------------------------------------------- #

class DemPyVista3dDialog(QDialog):
    """
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
    """

    def __init__(self, parent, dem_pre_layer, dem_post_layer=None,
                 diff_raster_path=None, lang='en'):
        super().__init__(parent)
        self.lang = lang if lang in _I18N else 'en'
        self.setWindowTitle(_t(self.lang, 'view3d_title'))
        self.resize(1100, 780)
        self.dem_pre_layer = dem_pre_layer
        self.dem_post_layer = dem_post_layer
        self.diff_raster_path = diff_raster_path
        self._pre_arr = None
        self._post_arr = None
        self._diff_arr = None
        self._extent = None
        self._plotter = None

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        try:
            import pyvista as pv  # noqa: F401
            from pyvistaqt import QtInteractor
        except Exception as ex:
            self._show_error(root,
                             f'pyvista / pyvistaqt not available: {ex}')
            return

        self._load_rasters()
        if self._pre_arr is None:
            self._show_error(root, _t(self.lang, 'no_data'))
            return

        # --- Controls row ---
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel(_t(self.lang, 'view3d_mode')))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(_t(self.lang, 'mode_pre_post'), 'prepost')
        self.mode_combo.addItem(_t(self.lang, 'mode_diff'), 'diff')
        self.mode_combo.addItem(_t(self.lang, 'mode_pre'), 'pre')
        self.mode_combo.currentIndexChanged.connect(self._rebuild)
        ctrl.addWidget(self.mode_combo)

        ctrl.addSpacing(12)
        ctrl.addWidget(QLabel(_t(self.lang, 'exag_lbl')))
        self.exag_spin = QDoubleSpinBox()
        self.exag_spin.setRange(0.1, 20.0)
        self.exag_spin.setSingleStep(0.5)
        self.exag_spin.setDecimals(1)
        self.exag_spin.setValue(2.0)
        self.exag_spin.valueChanged.connect(self._rebuild)
        ctrl.addWidget(self.exag_spin)

        ctrl.addStretch(1)

        btn_save = QPushButton(_t(self.lang, 'save_png'))
        btn_save.clicked.connect(self._save_png)
        ctrl.addWidget(btn_save)
        btn_close = QPushButton(_t(self.lang, 'close'))
        btn_close.clicked.connect(self.accept)
        ctrl.addWidget(btn_close)
        root.addLayout(ctrl)

        # --- VTK plotter ---
        self._plotter = QtInteractor(self)
        self._plotter.set_background('#1a1a2e')
        try:
            self._plotter.add_axes()
        except Exception:
            pass
        self._plotter.setSizePolicy(_sp_expanding(), _sp_expanding())
        root.addWidget(self._plotter.interactor, 1)

        self._rebuild()

    def _show_error(self, root_layout, msg):
        err = QLabel(msg)
        err.setAlignment(_align_center())
        err.setWordWrap(True)
        err.setStyleSheet('color:#c62828; padding:40px; font-size:13px;')
        root_layout.addWidget(err)
        btn = QPushButton(_t(self.lang, 'close'))
        btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn)
        root_layout.addLayout(row)

    def _load_rasters(self):
        if self.dem_pre_layer is not None:
            self._pre_arr, _, _, self._extent = _read_raster(
                self.dem_pre_layer)
        if self.dem_post_layer is not None:
            self._post_arr, _, _, _ = _read_raster(self.dem_post_layer)
        if self.diff_raster_path:
            diff_arr, _, _, diff_extent = _read_raster(self.diff_raster_path)
            self._diff_arr = diff_arr
            if self._extent is None:
                self._extent = diff_extent

    def _make_structured_grid(self, arr, exag):
        """
        Build a ``pyvista.StructuredGrid`` from a 2D elevation array.
        Cells with NaN are kept in the grid but their elevation values
        are masked so PyVista renders them as transparent.
        """
        import numpy as np
        import pyvista as pv

        n_rows, n_cols = arr.shape
        if self._extent is not None:
            x_min, x_max, y_min, y_max = self._extent
            xs = np.linspace(x_min, x_max, n_cols)
            ys = np.linspace(y_max, y_min, n_rows)
        else:
            xs = np.arange(n_cols, dtype='float64')
            ys = np.arange(n_rows, dtype='float64')

        X, Y = np.meshgrid(xs, ys)
        Z = arr.astype('float64') * exag

        grid = pv.StructuredGrid(X, Y, Z)
        # Add the elevation as a scalar field for coloring + threshold
        flat_z = Z.flatten(order='F')  # PyVista uses Fortran order
        grid['elevation'] = flat_z
        return grid

    def _rebuild(self):
        if self._plotter is None:
            return
        try:
            import numpy as np
            import pyvista as pv  # noqa: F401

            mode = self.mode_combo.currentData()
            exag = float(self.exag_spin.value())

            self._plotter.clear()
            self._plotter.set_background('#1a1a2e')
            try:
                self._plotter.add_axes()
            except Exception:
                pass

            def _add_surface(arr, cmap, opacity, scalar_name, show_bar=True):
                if arr is None:
                    return
                grid = self._make_structured_grid(arr, exag)
                # Threshold to remove cells with NaN elevation
                try:
                    valid = grid.threshold(
                        value=[float(np.nanmin(arr) * exag) - 1e6,
                               float(np.nanmax(arr) * exag) + 1e6],
                        scalars='elevation',
                    )
                    surf = valid.extract_surface()
                except Exception:
                    surf = grid.extract_surface()
                self._plotter.add_mesh(
                    surf,
                    scalars='elevation',
                    cmap=cmap,
                    opacity=opacity,
                    show_scalar_bar=show_bar,
                    scalar_bar_args={'title': scalar_name,
                                     'vertical': True} if show_bar else None,
                    smooth_shading=True,
                    specular=0.3,
                    specular_power=15,
                    ambient=0.4,
                    diffuse=0.8,
                )

            if mode == 'diff' and self._diff_arr is not None:
                _add_surface(self._diff_arr, 'RdBu_r', 1.0, 'Δ (m)')
            elif mode == 'pre' or self._post_arr is None:
                _add_surface(self._pre_arr, 'gist_earth', 1.0,
                             _t(self.lang, 'pre'))
            else:
                # Pre + Post overlay
                _add_surface(self._pre_arr, 'gist_earth', 0.85,
                             _t(self.lang, 'pre'))
                if self._post_arr is not None:
                    _add_surface(self._post_arr, 'autumn', 0.7,
                                 _t(self.lang, 'post'))

            # Lighting
            try:
                self._plotter.enable_eye_dome_lighting()
            except Exception:
                pass
            self._plotter.reset_camera()
            self._plotter.camera_position = 'iso'
        except Exception as ex:
            QMessageBox.warning(self, 'Error',
                                f"3D render failed: {ex}")

    def _save_png(self):
        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        path, _ = QFileDialog.getSaveFileName(
            self, _t(self.lang, 'save_png'),
            os.path.join(home, 'dem_3d.png'),
            'PNG (*.png)')
        if not path:
            return
        try:
            self._plotter.screenshot(path)
            QMessageBox.information(self, 'OK', f"Saved: {path}")
        except Exception as ex:
            QMessageBox.warning(self, 'Error', str(ex))

    def closeEvent(self, event):
        try:
            if self._plotter is not None:
                self._plotter.close()
        except Exception:
            pass
        super().closeEvent(event)


# --------------------------------------------------------------------------- #
#                     Plotly 3D viewer (primary, QWebEngineView)              #
# --------------------------------------------------------------------------- #

def _import_qt_webengine():
    """Return a QWebEngineView class compatible with Qt5 / Qt6, or None."""
    for mod_name in (
        'qgis.PyQt.QtWebEngineWidgets',
        'PyQt5.QtWebEngineWidgets',
        'PyQt6.QtWebEngineWidgets',
    ):
        try:
            mod = __import__(mod_name, fromlist=['QWebEngineView'])
            return getattr(mod, 'QWebEngineView')
        except Exception:
            continue
    return None


class DemPlotly3dDialog(QDialog):
    """
    Plotly-based 3D viewer, rendered inside a ``QWebEngineView``.

    Uses ``plotly.graph_objects.Surface`` which handles NaN cells
    transparently — no more vertical "spike" artefacts at the clip
    polygon edges that the matplotlib ``plot_surface`` path produces.
    The scene has directional lighting, hover tooltips with the real
    elevation values and interactive rotation / pan / zoom.

    If Plotly is not installed the dialog shows a clear message so
    the caller can fall back to :class:`DemMatplotlib3dDialog`.
    """

    def __init__(self, parent, dem_pre_layer, dem_post_layer=None,
                 diff_raster_path=None, lang='en'):
        super().__init__(parent)
        self.lang = lang if lang in _I18N else 'en'
        self.setWindowTitle(_t(self.lang, 'view3d_title'))
        self.resize(1100, 780)
        self.dem_pre_layer = dem_pre_layer
        self.dem_post_layer = dem_post_layer
        self.diff_raster_path = diff_raster_path
        self._pre_arr = None
        self._post_arr = None
        self._diff_arr = None
        self._extent = None
        self._html = None

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        # --- Dependency checks ---
        try:
            import plotly.graph_objects as go  # noqa: F401
        except Exception:
            self._show_error(root,
                             'plotly not installed. Run '
                             '"pip install plotly" or use the '
                             'matplotlib 3D fallback.')
            return

        WebView = _import_qt_webengine()
        if WebView is None:
            self._show_error(root,
                             'QWebEngineView not available. '
                             'Using the matplotlib 3D fallback.')
            return

        self._load_rasters()
        if self._pre_arr is None:
            self._show_error(root, _t(self.lang, 'no_data'))
            return

        # --- Controls row ---
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel(_t(self.lang, 'view3d_mode')))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(_t(self.lang, 'mode_pre_post'), 'prepost')
        self.mode_combo.addItem(_t(self.lang, 'mode_diff'), 'diff')
        self.mode_combo.addItem(_t(self.lang, 'mode_pre'), 'pre')
        self.mode_combo.currentIndexChanged.connect(self._rebuild)
        ctrl.addWidget(self.mode_combo)
        ctrl.addSpacing(12)
        ctrl.addWidget(QLabel(_t(self.lang, 'exag_lbl')))
        self.exag_spin = QDoubleSpinBox()
        self.exag_spin.setRange(0.1, 20.0)
        self.exag_spin.setSingleStep(0.5)
        self.exag_spin.setDecimals(1)
        self.exag_spin.setValue(2.0)
        self.exag_spin.valueChanged.connect(self._rebuild)
        ctrl.addWidget(self.exag_spin)
        ctrl.addStretch(1)
        btn_save = QPushButton(_t(self.lang, 'save_png'))
        btn_save.setText(btn_save.text().replace('PNG', 'HTML'))
        btn_save.clicked.connect(self._save_html)
        ctrl.addWidget(btn_save)
        btn_close = QPushButton(_t(self.lang, 'close'))
        btn_close.clicked.connect(self.accept)
        ctrl.addWidget(btn_close)
        root.addLayout(ctrl)

        # --- Web view ---
        self.web_view = WebView(self)
        self.web_view.setSizePolicy(_sp_expanding(), _sp_expanding())
        self.web_view.setMinimumHeight(580)
        root.addWidget(self.web_view, 1)

        self._rebuild()

    def _show_error(self, root_layout, msg):
        err = QLabel(msg)
        err.setAlignment(_align_center())
        err.setWordWrap(True)
        err.setStyleSheet('color:#c62828; padding:40px; font-size:13px;')
        root_layout.addWidget(err)
        btn = QPushButton(_t(self.lang, 'close'))
        btn.clicked.connect(self.accept)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(btn)
        root_layout.addLayout(row)

    def _load_rasters(self):
        if self.dem_pre_layer is not None:
            self._pre_arr, _, _, self._extent = _read_raster(
                self.dem_pre_layer)
        if self.dem_post_layer is not None:
            self._post_arr, _, _, _ = _read_raster(self.dem_post_layer)
        if self.diff_raster_path:
            diff_arr, _, _, diff_extent = _read_raster(self.diff_raster_path)
            self._diff_arr = diff_arr
            if self._extent is None:
                self._extent = diff_extent

    # ---------- scene construction ----------

    def _meshgrid_axes(self, arr):
        import numpy as np
        n_rows, n_cols = arr.shape
        if self._extent is None:
            return (np.arange(n_cols, dtype='float64'),
                    np.arange(n_rows, dtype='float64'))
        x_min, x_max, y_min, y_max = self._extent
        xs = np.linspace(x_min, x_max, n_cols)
        ys = np.linspace(y_max, y_min, n_rows)
        return xs, ys

    def _downsample(self, arr, max_cells=60000):
        """Return a coarser array if arr exceeds ``max_cells`` cells."""
        import math
        import numpy as np
        if arr is None:
            return None, 1
        n = arr.size
        if n <= max_cells:
            return arr, 1
        factor = int(math.ceil(math.sqrt(n / float(max_cells))))
        return arr[::factor, ::factor], factor

    def _rebuild(self):
        try:
            import numpy as np
            import plotly.graph_objects as go
        except Exception:
            return

        mode = self.mode_combo.currentData()
        exag = float(self.exag_spin.value())

        fig = go.Figure()
        title = ''

        if mode == 'diff' and self._diff_arr is not None:
            arr, factor = self._downsample(self._diff_arr)
            xs, ys = self._meshgrid_axes(arr)
            z = arr * exag
            fig.add_trace(go.Surface(
                x=xs, y=ys, z=z,
                colorscale='RdBu_r',
                cmid=0,
                name=_t(self.lang, 'heat_title'),
                showscale=True,
                lighting=dict(ambient=0.55, diffuse=0.8, specular=0.15,
                              roughness=0.5, fresnel=0.1),
                lightposition=dict(x=100, y=200, z=0),
                connectgaps=False,
                hovertemplate='X %{x:.2f}<br>Y %{y:.2f}<br>'
                              'Δ %{z:.3f} m<extra></extra>',
            ))
            title = _t(self.lang, 'heat_title')
        elif mode == 'pre' or self._post_arr is None:
            arr, factor = self._downsample(self._pre_arr)
            xs, ys = self._meshgrid_axes(arr)
            z = arr * exag
            fig.add_trace(go.Surface(
                x=xs, y=ys, z=z,
                colorscale='Earth',
                name=_t(self.lang, 'pre'),
                showscale=True,
                lighting=dict(ambient=0.55, diffuse=0.85, specular=0.2,
                              roughness=0.5, fresnel=0.15),
                lightposition=dict(x=100, y=200, z=0),
                connectgaps=False,
                hovertemplate='X %{x:.2f}<br>Y %{y:.2f}<br>'
                              'Z %{z:.3f} m<extra></extra>',
            ))
            title = _t(self.lang, 'pre')
        else:
            # Pre + Post overlay — use two Surface traces
            pre, factor = self._downsample(self._pre_arr)
            xs, ys = self._meshgrid_axes(pre)
            fig.add_trace(go.Surface(
                x=xs, y=ys, z=pre * exag,
                colorscale='Earth', opacity=0.85, showscale=True,
                colorbar=dict(title=_t(self.lang, 'pre'), x=1.02, len=0.45,
                              y=0.78),
                name=_t(self.lang, 'pre'),
                lighting=dict(ambient=0.55, diffuse=0.85, specular=0.2,
                              roughness=0.5, fresnel=0.15),
                lightposition=dict(x=100, y=200, z=0),
                connectgaps=False,
                hovertemplate='PRE<br>X %{x:.2f}<br>Y %{y:.2f}<br>'
                              'Z %{z:.3f} m<extra></extra>',
            ))
            if self._post_arr is not None:
                post_small = self._post_arr[::factor, ::factor]
                if post_small.shape == pre.shape:
                    fig.add_trace(go.Surface(
                        x=xs, y=ys, z=post_small * exag,
                        colorscale='YlOrRd', opacity=0.7, showscale=True,
                        colorbar=dict(title=_t(self.lang, 'post'),
                                      x=1.13, len=0.45, y=0.26),
                        name=_t(self.lang, 'post'),
                        lighting=dict(ambient=0.55, diffuse=0.85,
                                      specular=0.2, roughness=0.5,
                                      fresnel=0.15),
                        lightposition=dict(x=100, y=200, z=0),
                        connectgaps=False,
                        hovertemplate='POST<br>X %{x:.2f}<br>Y %{y:.2f}<br>'
                                      'Z %{z:.3f} m<extra></extra>',
                    ))
            title = f"{_t(self.lang, 'pre')} + {_t(self.lang, 'post')}"

        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor='center', font=dict(size=13)),
            margin=dict(l=0, r=0, t=36, b=0),
            paper_bgcolor='#eceff1',
            scene=dict(
                xaxis=dict(title='X (m)', backgroundcolor='#f5f5f5',
                           gridcolor='#bdbdbd', showbackground=True),
                yaxis=dict(title='Y (m)', backgroundcolor='#f5f5f5',
                           gridcolor='#bdbdbd', showbackground=True),
                zaxis=dict(title=_t(self.lang, 'axis_z_m'),
                           backgroundcolor='#f5f5f5',
                           gridcolor='#bdbdbd', showbackground=True),
                aspectmode='data',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    eye=dict(x=1.5, y=-1.5, z=1.2),
                ),
            ),
        )

        self._html = fig.to_html(
            include_plotlyjs='cdn',
            full_html=True,
            config={'displayModeBar': True, 'responsive': True},
        )
        # Inject a viewport meta + body style so the plot fills the widget
        self._html = self._html.replace(
            '<head>',
            '<head><meta name="viewport" '
            'content="width=device-width, initial-scale=1">'
            '<style>html,body{margin:0;padding:0;height:100%;overflow:hidden;}'
            '.plotly-graph-div{width:100%!important;height:100%!important;}'
            '</style>',
        )
        self.web_view.setHtml(self._html)

    def _save_html(self):
        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        path, _ = QFileDialog.getSaveFileName(
            self, _t(self.lang, 'save_png'),
            os.path.join(home, 'dem_3d.html'),
            'HTML (*.html)')
        if not path:
            return
        if not self._html:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self._html)
            QMessageBox.information(self, 'OK', f"Saved: {path}")
        except Exception as ex:
            QMessageBox.warning(self, 'Error', str(ex))


# --------------------------------------------------------------------------- #
#                 Matplotlib 3D surface fallback viewer                       #
# --------------------------------------------------------------------------- #

class DemMatplotlib3dDialog(QDialog):
    """
    Fallback 3D viewer based on ``mpl_toolkits.mplot3d``. Always works
    (matplotlib is bundled with the plugin) but provides a lower-quality
    view than the native Qgs3DMapCanvas.
    """

    def __init__(self, parent, dem_pre_layer, dem_post_layer=None,
                 diff_raster_path=None, lang='en'):
        super().__init__(parent)
        self.lang = lang if lang in _I18N else 'en'
        self.setWindowTitle(_t(self.lang, 'view3d_title'))
        self.resize(1000, 740)
        self.dem_pre_layer = dem_pre_layer
        self.dem_post_layer = dem_post_layer
        self.diff_raster_path = diff_raster_path

        self._pre_arr = None
        self._post_arr = None
        self._diff_arr = None
        self._extent = None

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)

        try:
            from matplotlib.figure import Figure  # noqa: F401
            from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
            FigureCanvas, NavigationToolbar = _import_qt_figure_canvas()
        except Exception:
            err = QLabel(_t(self.lang, 'no_mpl'))
            err.setStyleSheet('color:#c62828; padding:40px;')
            err.setAlignment(_align_center())
            root.addWidget(err)
            return

        self._load_rasters()
        if self._pre_arr is None:
            err = QLabel(_t(self.lang, 'no_data'))
            err.setStyleSheet('color:#c62828; padding:40px;')
            err.setAlignment(_align_center())
            root.addWidget(err)
            return

        from matplotlib.figure import Figure
        self.fig = Figure(figsize=(10, 7), tight_layout=True)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(_sp_expanding(), _sp_expanding())

        # Controls
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel(_t(self.lang, 'view3d_mode')))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(_t(self.lang, 'mode_pre_post'), 'prepost')
        self.mode_combo.addItem(_t(self.lang, 'mode_diff'), 'diff')
        self.mode_combo.addItem(_t(self.lang, 'mode_pre'), 'pre')
        self.mode_combo.currentIndexChanged.connect(self._redraw)
        ctrl.addWidget(self.mode_combo)

        ctrl.addSpacing(12)
        ctrl.addWidget(QLabel(_t(self.lang, 'exag_lbl')))
        self.exag_spin = QDoubleSpinBox()
        self.exag_spin.setRange(0.1, 20.0)
        self.exag_spin.setSingleStep(0.5)
        self.exag_spin.setDecimals(1)
        self.exag_spin.setValue(2.0)
        self.exag_spin.valueChanged.connect(self._redraw)
        ctrl.addWidget(self.exag_spin)
        ctrl.addStretch(1)

        btn_save = QPushButton(_t(self.lang, 'save_png'))
        btn_save.clicked.connect(self._save_png)
        ctrl.addWidget(btn_save)
        btn_close = QPushButton(_t(self.lang, 'close'))
        btn_close.clicked.connect(self.accept)
        ctrl.addWidget(btn_close)

        toolbar = NavigationToolbar(self.canvas, self)
        root.addWidget(toolbar)
        root.addWidget(self.canvas, 1)
        root.addLayout(ctrl)

        self._redraw()

    def _load_rasters(self):
        if self.dem_pre_layer is not None:
            self._pre_arr, _, _, self._extent = _read_raster(self.dem_pre_layer)
        if self.dem_post_layer is not None:
            self._post_arr, _, _, _ = _read_raster(self.dem_post_layer)
        if self.diff_raster_path:
            diff_arr, _, _, diff_extent = _read_raster(self.diff_raster_path)
            self._diff_arr = diff_arr
            if self._extent is None:
                self._extent = diff_extent

    def _downsample(self, arr, max_cells=20000):
        """Return a coarser array keeping at most ``max_cells`` cells."""
        import numpy as np
        if arr is None:
            return None, 1
        n_rows, n_cols = arr.shape
        cells = n_rows * n_cols
        if cells <= max_cells:
            return arr, 1
        import math
        factor = int(math.ceil(math.sqrt(cells / float(max_cells))))
        return arr[::factor, ::factor], factor

    def _meshgrid(self, arr_shape, factor):
        import numpy as np
        if self._extent is None:
            n_rows, n_cols = arr_shape
            return np.meshgrid(np.arange(n_cols), np.arange(n_rows))
        x_min, x_max, y_min, y_max = self._extent
        n_rows, n_cols = arr_shape
        xs = np.linspace(x_min, x_max, n_cols)
        ys = np.linspace(y_max, y_min, n_rows)
        return np.meshgrid(xs, ys)

    def _redraw(self):
        try:
            import numpy as np
            mode = self.mode_combo.currentData()
            exag = float(self.exag_spin.value())
            self.ax.clear()

            def _clean(arr):
                """Return a copy with NaN kept (matplotlib skips NaN in
                plot_surface) and an autoscale-friendly version for
                setting the z axis limits."""
                return np.where(np.isfinite(arr), arr, np.nan)

            def _zlim(arr):
                """Tight z limits so small vertical features (walls,
                trench bottoms) are not visually flattened by the auto
                aspect."""
                valid = arr[np.isfinite(arr)]
                if valid.size == 0:
                    return None
                mn, mx = float(valid.min()), float(valid.max())
                if mx - mn < 0.5:
                    mid = (mn + mx) / 2
                    mn, mx = mid - 0.25, mid + 0.25
                pad = (mx - mn) * 0.05
                return (mn - pad) * exag, (mx + pad) * exag

            if mode == 'diff' and self._diff_arr is not None:
                arr, factor = self._downsample(self._diff_arr)
                arr = _clean(arr)
                X, Y = self._meshgrid(arr.shape, factor)
                Z = arr * exag
                self.ax.plot_surface(
                    X, Y, Z, cmap='RdBu_r', linewidth=0,
                    antialiased=True, rstride=1, cstride=1,
                    vmin=-np.nanmax(np.abs(arr)),
                    vmax=np.nanmax(np.abs(arr)),
                )
                zl = _zlim(arr)
                if zl:
                    self.ax.set_zlim(*zl)
                self.ax.set_title(_t(self.lang, 'heat_title'), fontsize=10)
            elif mode == 'pre' or self._post_arr is None:
                arr, factor = self._downsample(self._pre_arr)
                arr = _clean(arr)
                X, Y = self._meshgrid(arr.shape, factor)
                Z = arr * exag
                self.ax.plot_surface(
                    X, Y, Z, cmap='terrain',
                    linewidth=0, antialiased=True,
                    rstride=1, cstride=1)
                zl = _zlim(arr)
                if zl:
                    self.ax.set_zlim(*zl)
                self.ax.set_title(_t(self.lang, 'pre'), fontsize=10)
            else:
                # Pre + Post overlay
                pre, factor = self._downsample(self._pre_arr)
                pre = _clean(pre)
                X, Y = self._meshgrid(pre.shape, factor)
                self.ax.plot_surface(
                    X, Y, pre * exag, cmap='terrain', alpha=0.70,
                    linewidth=0, antialiased=True, rstride=1, cstride=1)
                post_clean = None
                if self._post_arr is not None:
                    post_small = self._post_arr[::factor, ::factor]
                    if post_small.shape == pre.shape:
                        post_clean = _clean(post_small)
                        self.ax.plot_surface(
                            X, Y, post_clean * exag, cmap='YlOrRd',
                            alpha=0.55,
                            linewidth=0, antialiased=True,
                            rstride=1, cstride=1)
                # Tight z-limits: use union of pre and post
                stacked = pre if post_clean is None else np.vstack(
                    [pre[np.isfinite(pre)],
                     post_clean[np.isfinite(post_clean)]])
                try:
                    zl = _zlim(stacked)
                    if zl:
                        self.ax.set_zlim(*zl)
                except Exception:
                    pass
                self.ax.set_title(
                    f"{_t(self.lang, 'pre')} + {_t(self.lang, 'post')}",
                    fontsize=10)

            self.ax.set_xlabel('X (m)', fontsize=8)
            self.ax.set_ylabel('Y (m)', fontsize=8)
            self.ax.set_zlabel(_t(self.lang, 'axis_z_m'), fontsize=8)
            self.canvas.draw_idle()
        except Exception as ex:
            QMessageBox.warning(self, 'Error', f"3D render failed: {ex}")

    def _save_png(self):
        home = os.environ.get('PYARCHINIT_HOME', os.path.expanduser('~'))
        path, _ = QFileDialog.getSaveFileName(
            self, _t(self.lang, 'save_png'),
            os.path.join(home, 'dem_3d.png'),
            'PNG (*.png)')
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=200, bbox_inches='tight')
            QMessageBox.information(self, 'OK', f"Saved: {path}")
        except Exception as ex:
            QMessageBox.warning(self, 'Error', str(ex))
