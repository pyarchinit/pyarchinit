"""
Interfaccia dock widget principale di GeoArchaeo
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)

Struttura del pannello:
- intestazione sempre visibile: layer di punti + campo numerico (usati da tutte le schede)
- schede nell'ordine di lavoro: Dati -> Variogramma -> Kriging -> Pattern (ML) -> Campionamento -> Report
- ogni scheda mostra i propri risultati in un riquadro persistente e il grafico nel pannello
"""

import gc
import os
import html as html_lib
import tempfile
import traceback
from datetime import datetime

import numpy as np

from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTabWidget, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QLabel, QTextBrowser, QFileDialog, QProgressBar, QGroupBox,
    QCheckBox, QListWidget, QListWidgetItem, QMessageBox, QDialog,
    QDialogButtonBox, QScrollArea, QSizePolicy
)
from qgis.PyQt.QtCore import QThread, pyqtSignal, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QPixmap, QColor
from qgis.core import (
    QgsMessageLog, QgsProject, QgsRasterLayer, QgsVectorLayer, QgsField,
    QgsFeature, QgsGeometry, QgsPointXY, QgsMarkerSymbol, QgsRendererCategory,
    QgsCategorizedSymbolRenderer, QgsCoordinateReferenceSystem, QgsFeatureRequest,
    QgsRectangle, QgsUnitTypes, QgsRasterShader, QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer, QgsCoordinateTransform
)
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox

from ..i18n import tr, tr_format, tr2, get_language, set_language, TRANSLATIONS
from ..compat import (
    Qt_UserRole, Qt_AlignCenter, Qt_SmoothTransformation, Qt_KeepAspectRatio,
    QVariant_Int, QVariant_Double, QVariant_String,
    Qgis_Info, Qgis_Warning, Qgis_Critical, Qgis_Success,
    QListWidget_MultiSelection, QDialogButtonBox_Ok, QDialogButtonBox_Cancel,
    LayerFilter_Point, LayerFilter_Polygon, FieldFilter_Numeric,
    exec_dialog, is_point_layer, attribute_to_float, question_yes_no, polygon_region,
    Qt_RichText, QFrame_NoFrame, ColorRamp_Interpolated, print_document, pdf_printer
)
from ..core.geostat_engine import GeostatEngine, MAX_GRID_SIDE, VARIOGRAM_MODELS, limit_native_threads
from .tutorial_html import get_tutorial_html

# QWebEngineView is optional - fallback to static PNG preview if not available
WEBENGINE_AVAILABLE = False
try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    QWebEngineView = None

LOG_TAG = 'GeoArchaeo'
INFO_STYLE = "QLabel { background-color: #e3f2fd; color: #1a237e; padding: 8px; border-radius: 5px; }"
RESULT_STYLE = "QLabel { background-color: #f1f8e9; color: #1b5e20; padding: 8px; border-radius: 5px; }"
HINT_STYLE = "QLabel { color: #616161; font-size: 11px; }"
WARN_STYLE = "QLabel { color: #e65100; }"

MODEL_LABEL_KEYS = {'spherical': 'model_spherical', 'exponential': 'model_exponential',
                    'gaussian': 'model_gaussian', 'matern': 'model_matern'}
ML_METHODS = [('kmeans', 'ml_kmeans'), ('dbscan', 'ml_dbscan'), ('isolation_forest', 'ml_isolation')]
SAMPLING_METHODS = [('maximin', 'sampling_maximin', 'sampling_maximin_desc'),
                    ('variance', 'sampling_variance', 'sampling_variance_desc'),
                    ('stratified', 'sampling_stratified', 'sampling_stratified_desc'),
                    ('adaptive', 'sampling_adaptive', 'sampling_adaptive_desc')]
REPORT_SECTIONS = [('stats', 'section_stats'), ('variogram', 'section_variogram'),
                   ('kriging', 'section_kriging'), ('ml', 'section_ml'), ('sampling', 'section_sampling')]
LARGE_GRID_CELLS = 40000
MIN_POINTS = 5


def log(message, level=None):
    QgsMessageLog.logMessage(str(message), LOG_TAG, level if level is not None else Qgis_Info)


def boundary_geometry(boundary_layer, target_crs):
    """Unione dei poligoni del layer, riproiettata nel CRS dei punti (None se assente)."""
    if boundary_layer is None:
        return None
    geoms = [f.geometry() for f in boundary_layer.getFeatures()
             if f.geometry() is not None and not f.geometry().isEmpty()]
    if not geoms:
        return None
    geom = QgsGeometry.unaryUnion(geoms) if len(geoms) > 1 else QgsGeometry(geoms[0])
    source_crs = boundary_layer.crs()
    if source_crs.isValid() and target_crs.isValid() and source_crs != target_crs:
        geom.transform(QgsCoordinateTransform(source_crs, target_crs, QgsProject.instance()))
    return polygon_region(geom)


def fmt(value, digits=3):
    """Formatta un numero in modo leggibile (3 cifre significative)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not np.isfinite(value):
        return '-'
    if value == 0:
        return '0'
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    return f"{value:.{digits}g}"


class AnalysisThread(QThread):
    """Esegue un'analisi del motore in un thread separato."""
    result_ready = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, engine, method, params):
        super().__init__()
        self.engine = engine
        self.method = method
        self.params = params
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self):
        return self._cancelled

    def _progress(self, fraction):
        self.progress.emit(int(max(0.0, min(1.0, fraction)) * 100))
        return not self._cancelled

    def _compute(self, p):
        if self.method == 'variogram':
            return self.engine.calculate_variogram(
                p['points'], p['values'], p['max_dist'], p['model_type'],
                check_anisotropy=p.get('check_anisotropy', False),
                fixed_params=p.get('fixed_params'))
        if self.method == 'kriging':
            return self.engine.ordinary_kriging(
                p['points'], p['values'], p['extent'], p['pixel_size'],
                p.get('variogram_params'), progress=self._progress)
        if self.method == 'ml':
            return self.engine.ml_pattern_recognition(
                p['layers_data'], p['method'], n_clusters=p.get('n_clusters'))
        if self.method == 'sampling':
            return self.engine.optimal_sampling_design(
                p['existing_points'], p.get('boundary'), p['n_new'], p['method'],
                variogram_params=p.get('variogram_params'))
        raise ValueError(f"Unknown analysis: {self.method}")

    def run(self):
        p = self.params
        # Il garbage collector ciclico di Python puo' scattare in qualunque thread:
        # se raccogliesse qui un oggetto Qt del thread principale (es. un layer non
        # piu' referenziato) QGIS andrebbe in crash. Lo sospendiamo durante il calcolo.
        gc.disable()
        try:
            with limit_native_threads():
                result = self._compute(p)
            if self._cancelled:
                self.error.emit('cancelled')
                return
            self.result_ready.emit(result)
        except MemoryError:
            self.error.emit(tr2("Memoria insufficiente: aumenta la dimensione della cella.",
                                "Out of memory: increase the cell size."))
        except RuntimeError as e:
            if 'cancelled' in str(e):
                self.error.emit('cancelled')
            else:
                log(traceback.format_exc(), Qgis_Critical)
                self.error.emit(str(e))
        except Exception as e:
            log(traceback.format_exc(), Qgis_Critical)
            self.error.emit(str(e))
        finally:
            gc.enable()


class PlotPanel(QWidget):
    """
    Area grafico: QWebEngineView (Plotly interattivo) se disponibile, altrimenti
    anteprima PNG statica con pulsante per aprire il grafico interattivo nel browser.
    """

    def __init__(self, parent=None, min_height=320):
        super().__init__(parent)
        self._html_path = None
        self._pixmap = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if WEBENGINE_AVAILABLE:
            self.view = QWebEngineView()
            self.view.setMinimumHeight(min_height)
            layout.addWidget(self.view)
            self.image_label = None
        else:
            self.view = None
            self.scroll = QScrollArea()
            self.scroll.setWidgetResizable(True)
            self.scroll.setMinimumHeight(min_height)
            self.image_label = QLabel()
            self.image_label.setAlignment(Qt_AlignCenter)
            self.image_label.setWordWrap(True)
            self.image_label.setStyleSheet("QLabel { background-color: white; color: #616161; }")
            self.scroll.setWidget(self.image_label)
            layout.addWidget(self.scroll)

        row = QHBoxLayout()
        self.hint_label = QLabel()
        self.hint_label.setStyleSheet(HINT_STYLE)
        self.hint_label.setWordWrap(True)
        row.addWidget(self.hint_label, 1)
        self.browser_btn = QPushButton()
        self.browser_btn.setEnabled(False)
        self.browser_btn.clicked.connect(self.open_in_browser)
        row.addWidget(self.browser_btn)
        layout.addLayout(row)
        self.retranslate()
        self.clear()

    def retranslate(self):
        self.browser_btn.setText(tr('open_in_browser'))
        if self._html_path is None:
            self.hint_label.setText(tr('plot_waiting'))
        elif not WEBENGINE_AVAILABLE:
            self.hint_label.setText(tr('plot_static_hint'))

    def clear(self):
        self._html_path = None
        self._pixmap = None
        self.browser_btn.setEnabled(False)
        self.hint_label.setText(tr('plot_waiting'))
        if self.view is not None:
            self.view.setHtml(f"<html><body style='font-family:sans-serif;color:#616161'>"
                              f"<p>{html_lib.escape(tr('plot_waiting'))}</p></body></html>")
        else:
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(tr('plot_waiting'))

    def show_figure(self, fig, png_bytes=None, temp_dir=None):
        """Mostra una figura Plotly (e, senza WebEngine, l'anteprima PNG)."""
        handle = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False,
                                             dir=temp_dir, encoding='utf-8', prefix='geoarchaeo_plot_')
        handle.close()
        fig.write_html(handle.name, include_plotlyjs=True, full_html=True,
                       default_width='100%', default_height='100%')
        self._html_path = handle.name
        self.browser_btn.setEnabled(True)
        if self.view is not None:
            self.view.setUrl(QUrl.fromLocalFile(handle.name))
            self.hint_label.setText('')
        else:
            self.hint_label.setText(tr('plot_static_hint'))
            if png_bytes:
                pix = QPixmap()
                pix.loadFromData(png_bytes)
                self._pixmap = pix
                self.image_label.setText('')
                self._rescale()
            else:
                self._pixmap = None
                self.image_label.setPixmap(QPixmap())
                self.image_label.setText(tr('open_in_browser'))

    def _rescale(self):
        if self._pixmap is None or self.image_label is None:
            return
        width = max(200, self.scroll.viewport().width() - 4)
        if self._pixmap.width() > width:
            self.image_label.setPixmap(self._pixmap.scaledToWidth(width, Qt_SmoothTransformation))
        else:
            self.image_label.setPixmap(self._pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rescale()

    def open_in_browser(self):
        if self._html_path and os.path.exists(self._html_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._html_path))


class GeoArchaeoDockWidget(QDockWidget):
    """Widget principale del plugin"""

    def __init__(self, iface=None, parent=None):
        super().__init__("GeoArchaeo", parent)
        self.setObjectName('GeoArchaeoDock')
        self.iface = iface
        self.plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.example_dir = os.path.join(self.plugin_dir, 'test_layers')
        self.temp_dir = tempfile.mkdtemp(prefix='geoarchaeo_')

        self.engine = GeostatEngine()
        self.analysis_thread = None
        self.current_results = {}
        self.current_figures = {}
        self._tr_widgets = []      # (widget, setter, key)
        self._tr_callbacks = []    # callables eseguiti al cambio lingua
        self._project_connections = []

        main = QWidget()
        self.setWidget(main)
        layout = QVBoxLayout(main)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        self._create_toolbar(layout)
        self._create_input_group(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)
        self._create_data_tab()
        self._create_variogram_tab()
        self._create_kriging_tab()
        self._create_ml_tab()
        self._create_sampling_tab()
        self._create_report_tab()

        # Progress bar + cancel
        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_row.addWidget(self.progress_bar, 1)
        self.cancel_btn = self._reg(QPushButton(), 'cancel')
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._cancel_analysis)
        progress_row.addWidget(self.cancel_btn)
        layout.addLayout(progress_row)

        self._tab_indices = {'data': 0, 'dati': 0, 'variogram': 1, 'variogramma': 1, 'kriging': 2,
                             'ml': 3, 'sampling': 4, 'campionamento': 4, 'report': 5}

        # Connessioni
        self.layer_combo.layerChanged.connect(self._on_layer_changed)
        self.field_combo.fieldChanged.connect(self._on_field_changed)
        project = QgsProject.instance()
        for signal in (project.layersAdded, project.layersRemoved):
            signal.connect(self._update_ml_layers)
            self._project_connections.append(signal)
        self._on_layer_changed(self.layer_combo.currentLayer())

    # ==================================================================
    # Helpers UI
    # ==================================================================
    def _reg(self, widget, key, setter='setText'):
        """Imposta un testo tradotto e registra il widget per il cambio lingua."""
        getattr(widget, setter)(tr(key))
        self._tr_widgets.append((widget, setter, key))
        return widget

    def _info_label(self, title_key, desc_key):
        label = QLabel()
        label.setWordWrap(True)
        label.setStyleSheet(INFO_STYLE)

        def update():
            label.setText(tr(title_key) + "<br>" + tr(desc_key))
        update()
        self._tr_callbacks.append(update)
        return label

    def _result_label(self):
        label = QLabel()
        label.setWordWrap(True)
        label.setStyleSheet(RESULT_STYLE)
        label.setTextFormat(Qt_RichText)
        label.setVisible(False)
        return label

    def _next_button(self, key, tab_name):
        btn = self._reg(QPushButton(), key)
        btn.setFlat(True)
        btn.setStyleSheet("QPushButton { color: #1565C0; text-align: right; }")
        btn.clicked.connect(lambda: self.switch_to_tab(tab_name))
        return btn

    def _make_tab(self, tab_key):
        """Crea una scheda scrollabile e restituisce (layout_contenuto)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(6)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        scroll.setFrameShape(QFrame_NoFrame)
        index = self.tabs.addTab(scroll, tr(tab_key))
        self._tr_callbacks.append(lambda i=index, k=tab_key: self.tabs.setTabText(i, tr(k)))
        return layout

    def switch_to_tab(self, tab_name):
        """Switch to a specific tab by name"""
        name = str(tab_name).lower()
        if name in self._tab_indices:
            self.tabs.setCurrentIndex(self._tab_indices[name])
        else:
            log(f"Unknown tab: {tab_name}", Qgis_Warning)

    def _notify(self, message, level=None, duration=6):
        """Messaggio non bloccante nella barra di QGIS (fallback: log)."""
        level = Qgis_Info if level is None else level
        log(message, level)
        if self.iface is not None:
            try:
                self.iface.messageBar().pushMessage("GeoArchaeo", message, level, duration)
            except (AttributeError, RuntimeError, TypeError) as e:
                log(f"message bar unavailable: {e}", Qgis_Warning)

    def _warn(self, message):
        QMessageBox.warning(self, tr('warning'), message)

    def _error(self, message):
        QMessageBox.critical(self, tr('error'), message)

    # ==================================================================
    # Intestazione
    # ==================================================================
    def _create_toolbar(self, parent_layout):
        row = QHBoxLayout()
        self.load_examples_btn = self._reg(QPushButton(), 'load_examples')
        self.load_examples_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 5px 10px; "
            "border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #45a049; }")
        self.load_examples_btn.clicked.connect(self.show_load_examples_dialog)
        row.addWidget(self.load_examples_btn)

        self.tutorial_btn = self._reg(QPushButton(), 'show_tutorial')
        self.tutorial_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; padding: 5px 10px; "
            "border-radius: 3px; } QPushButton:hover { background-color: #1976D2; }")
        self.tutorial_btn.clicked.connect(self._show_tutorial)
        row.addWidget(self.tutorial_btn)
        row.addStretch()

        self.language_label = QLabel()
        self._tr_callbacks.append(lambda: self.language_label.setText(tr('language') + ":"))
        self.language_label.setText(tr('language') + ":")
        row.addWidget(self.language_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Italiano", "it")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(0 if get_language() == 'it' else 1)
        self.lang_combo.currentIndexChanged.connect(self._change_language)
        row.addWidget(self.lang_combo)
        parent_layout.addLayout(row)

    def _create_input_group(self, parent_layout):
        self.input_group = self._reg(QGroupBox(), 'input_data', 'setTitle')
        form = QFormLayout()
        form.setContentsMargins(8, 4, 8, 4)
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(LayerFilter_Point)
        self.point_layer_label = self._reg(QLabel(), 'point_layer')
        form.addRow(self.point_layer_label, self.layer_combo)
        self.field_combo = QgsFieldComboBox()
        self.field_combo.setFilters(FieldFilter_Numeric)
        self.value_field_label = self._reg(QLabel(), 'value_field')
        form.addRow(self.value_field_label, self.field_combo)
        self.layer_summary_label = QLabel()
        self.layer_summary_label.setWordWrap(True)
        self.layer_summary_label.setStyleSheet(HINT_STYLE)
        form.addRow(self.layer_summary_label)
        self.input_group.setLayout(form)
        parent_layout.addWidget(self.input_group)

    # ==================================================================
    # Schede
    # ==================================================================
    def _create_data_tab(self):
        layout = self._make_tab('tab_data')
        layout.addWidget(self._info_label('data_title', 'data_desc'))
        self.calc_stats_btn = self._reg(QPushButton(), 'calc_statistics')
        self.calc_stats_btn.clicked.connect(self._run_eda)
        layout.addWidget(self.calc_stats_btn)
        self.stats_view = QTextBrowser()
        self.stats_view.setOpenExternalLinks(False)
        self.stats_view.setMinimumHeight(180)
        self.stats_view.setMaximumHeight(320)
        layout.addWidget(self.stats_view)
        self.data_plot = PlotPanel(min_height=260)
        layout.addWidget(self.data_plot)
        layout.addWidget(self._next_button('next_variogram', 'variogram'))
        layout.addStretch()

    def _create_variogram_tab(self):
        layout = self._make_tab('tab_variogram')
        layout.addWidget(self._info_label('variogram_title', 'variogram_desc'))

        self.variogram_params_group = self._reg(QGroupBox(), 'variogram_params', 'setTitle')
        form = QFormLayout()
        dist_row = QHBoxLayout()
        self.max_dist_spin = QDoubleSpinBox()
        self.max_dist_spin.setDecimals(3)
        self.max_dist_spin.setRange(0.001, 1e9)
        self.max_dist_spin.setValue(100)
        dist_row.addWidget(self.max_dist_spin, 1)
        self.max_dist_auto_btn = self._reg(QPushButton(), 'auto')
        self.max_dist_auto_btn.setMaximumWidth(60)
        self.max_dist_auto_btn.clicked.connect(self._auto_max_distance)
        dist_row.addWidget(self.max_dist_auto_btn)
        self.max_dist_label = self._reg(QLabel(), 'max_distance')
        self._tr_callbacks.append(lambda: self.max_dist_spin.setToolTip(tr('max_distance_tip')))
        self.max_dist_spin.setToolTip(tr('max_distance_tip'))
        form.addRow(self.max_dist_label, dist_row)

        self.model_combo = QComboBox()
        self._fill_combo(self.model_combo, [(m, MODEL_LABEL_KEYS[m]) for m in VARIOGRAM_MODELS])
        self.model_label = self._reg(QLabel(), 'theoretical_model')
        form.addRow(self.model_label, self.model_combo)

        self.anisotropy_check = self._reg(QCheckBox(), 'anisotropy_check')
        form.addRow(self.anisotropy_check)
        self.variogram_params_group.setLayout(form)
        layout.addWidget(self.variogram_params_group)

        self.manual_group = self._reg(QGroupBox(), 'manual_params', 'setTitle')
        self.manual_group.setCheckable(True)
        self.manual_group.setChecked(False)
        self._tr_callbacks.append(lambda: self.manual_group.setToolTip(tr('manual_params_tip')))
        self.manual_group.setToolTip(tr('manual_params_tip'))
        manual_form = QFormLayout()
        self.nugget_spin = QDoubleSpinBox()
        self.sill_spin = QDoubleSpinBox()
        self.range_spin = QDoubleSpinBox()
        for spin in (self.nugget_spin, self.sill_spin, self.range_spin):
            spin.setDecimals(4)
            spin.setRange(0, 1e12)
            spin.setValue(0)
            spin.setSpecialValueText(tr('auto'))
            self._tr_callbacks.append(lambda s=spin: s.setSpecialValueText(tr('auto')))
        self.nugget_label = self._reg(QLabel(), 'nugget')
        self.sill_label = self._reg(QLabel(), 'sill')
        self.range_label = self._reg(QLabel(), 'range')
        manual_form.addRow(self.nugget_label, self.nugget_spin)
        manual_form.addRow(self.sill_label, self.sill_spin)
        manual_form.addRow(self.range_label, self.range_spin)
        self.manual_group.setLayout(manual_form)
        layout.addWidget(self.manual_group)

        self.calc_variogram_btn = self._reg(QPushButton(), 'calc_variogram')
        self.calc_variogram_btn.clicked.connect(self._calculate_variogram)
        layout.addWidget(self.calc_variogram_btn)

        self.variogram_result_label = self._result_label()
        layout.addWidget(self.variogram_result_label)
        self.variogram_plot = PlotPanel()
        layout.addWidget(self.variogram_plot)
        layout.addWidget(self._next_button('next_kriging', 'kriging'))
        layout.addStretch()

    def _create_kriging_tab(self):
        layout = self._make_tab('tab_kriging')
        layout.addWidget(self._info_label('kriging_title', 'kriging_desc'))

        status_row = QHBoxLayout()
        self.variogram_status_label = QLabel()
        self.variogram_status_label.setWordWrap(True)
        self.variogram_status_label.setStyleSheet(HINT_STYLE)
        status_row.addWidget(self.variogram_status_label, 1)
        self.goto_variogram_btn = self._reg(QPushButton(), 'goto_variogram')
        self.goto_variogram_btn.setFlat(True)
        self.goto_variogram_btn.setStyleSheet("QPushButton { color: #1565C0; }")
        self.goto_variogram_btn.clicked.connect(lambda: self.switch_to_tab('variogram'))
        status_row.addWidget(self.goto_variogram_btn)
        layout.addLayout(status_row)

        self.kriging_params_group = self._reg(QGroupBox(), 'kriging_params', 'setTitle')
        form = QFormLayout()
        self.resolution_spin = QDoubleSpinBox()
        self.resolution_spin.setDecimals(3)
        self.resolution_spin.setRange(0.0001, 1e9)
        self.resolution_spin.setValue(5)
        self.resolution_spin.valueChanged.connect(self._update_grid_info)
        self.resolution_label = self._reg(QLabel(), 'grid_resolution')
        form.addRow(self.resolution_label, self.resolution_spin)
        self.grid_info_label = QLabel()
        self.grid_info_label.setWordWrap(True)
        self.grid_info_label.setStyleSheet(HINT_STYLE)
        form.addRow(self.grid_info_label)
        self.use_variogram = self._reg(QCheckBox(), 'use_variogram')
        self.use_variogram.setChecked(True)
        self.use_variogram.toggled.connect(self._update_kriging_status)
        form.addRow(self.use_variogram)
        self.create_uncertainty = self._reg(QCheckBox(), 'create_uncertainty')
        self.create_uncertainty.setChecked(True)
        form.addRow(self.create_uncertainty)
        self.kriging_params_group.setLayout(form)
        layout.addWidget(self.kriging_params_group)

        self.run_kriging_btn = self._reg(QPushButton(), 'run_kriging')
        self.run_kriging_btn.clicked.connect(self._run_kriging)
        layout.addWidget(self.run_kriging_btn)

        self.kriging_result_label = self._result_label()
        layout.addWidget(self.kriging_result_label)
        self.kriging_plot = PlotPanel(min_height=420)
        layout.addWidget(self.kriging_plot)
        layout.addWidget(self._next_button('next_report', 'report'))
        layout.addStretch()
        self._update_kriging_status()

    def _create_ml_tab(self):
        layout = self._make_tab('tab_ml')
        layout.addWidget(self._info_label('ml_title', 'ml_desc'))

        self.ml_data_group = self._reg(QGroupBox(), 'ml_data', 'setTitle')
        group_layout = QVBoxLayout()
        self.ml_layers_label = self._reg(QLabel(), 'ml_layers_select')
        group_layout.addWidget(self.ml_layers_label)
        self.ml_layers = QListWidget()
        self.ml_layers.setSelectionMode(QListWidget_MultiSelection)
        self.ml_layers.setMaximumHeight(110)
        group_layout.addWidget(self.ml_layers)
        self._update_ml_layers()

        form = QFormLayout()
        self.ml_method = QComboBox()
        self._fill_combo(self.ml_method, ML_METHODS)
        self.ml_method.currentIndexChanged.connect(
            lambda i: self.ml_clusters_spin.setEnabled(self.ml_method.currentData() == 'kmeans'))
        self.ml_method_label = self._reg(QLabel(), 'ml_method')
        form.addRow(self.ml_method_label, self.ml_method)
        self.ml_clusters_spin = QSpinBox()
        self.ml_clusters_spin.setRange(0, 50)
        self.ml_clusters_spin.setValue(0)
        self.ml_clusters_spin.setSpecialValueText(tr('auto'))
        self._tr_callbacks.append(lambda: self.ml_clusters_spin.setSpecialValueText(tr('auto')))
        self.ml_clusters_label = self._reg(QLabel(), 'ml_n_clusters')
        form.addRow(self.ml_clusters_label, self.ml_clusters_spin)
        group_layout.addLayout(form)
        self.ml_rf_hint = QLabel()
        self.ml_rf_hint.setWordWrap(True)
        self.ml_rf_hint.setStyleSheet(HINT_STYLE)
        self._reg(self.ml_rf_hint, 'ml_rf_hint')
        group_layout.addWidget(self.ml_rf_hint)
        self.ml_data_group.setLayout(group_layout)
        layout.addWidget(self.ml_data_group)

        self.run_ml_btn = self._reg(QPushButton(), 'run_ml')
        self.run_ml_btn.clicked.connect(self._run_ml)
        layout.addWidget(self.run_ml_btn)

        self.ml_result_label = self._result_label()
        layout.addWidget(self.ml_result_label)
        self.ml_plot = PlotPanel()
        layout.addWidget(self.ml_plot)
        layout.addStretch()

    def _create_sampling_tab(self):
        layout = self._make_tab('tab_sampling')
        layout.addWidget(self._info_label('sampling_title', 'sampling_desc'))

        self.sampling_params_group = self._reg(QGroupBox(), 'sampling_params', 'setTitle')
        form = QFormLayout()
        self.existing_points_label = QLabel()
        self.existing_points_label.setWordWrap(True)
        form.addRow(self.existing_points_label)
        self.boundary_combo = QgsMapLayerComboBox()
        self.boundary_combo.setFilters(LayerFilter_Polygon)
        self.boundary_combo.setAllowEmptyLayer(True)
        self.boundary_combo.setCurrentIndex(0)
        self.study_area_label = self._reg(QLabel(), 'study_area')
        form.addRow(self.study_area_label, self.boundary_combo)
        self.n_points_spin = QSpinBox()
        self.n_points_spin.setRange(1, 500)
        self.n_points_spin.setValue(10)
        self.new_points_label = self._reg(QLabel(), 'new_points')
        form.addRow(self.new_points_label, self.n_points_spin)
        self.sampling_combo = QComboBox()
        self._fill_combo(self.sampling_combo, [(k, lk) for k, lk, _ in SAMPLING_METHODS])
        self.sampling_combo.currentIndexChanged.connect(self._update_sampling_desc)
        self.sampling_method_label = self._reg(QLabel(), 'sampling_method')
        form.addRow(self.sampling_method_label, self.sampling_combo)
        self.sampling_desc_label = QLabel()
        self.sampling_desc_label.setWordWrap(True)
        self.sampling_desc_label.setStyleSheet(HINT_STYLE)
        form.addRow(self.sampling_desc_label)
        self._tr_callbacks.append(self._update_sampling_desc)
        self._update_sampling_desc()
        self.sampling_params_group.setLayout(form)
        layout.addWidget(self.sampling_params_group)

        self.calc_optimal_btn = self._reg(QPushButton(), 'calc_optimal')
        self.calc_optimal_btn.clicked.connect(self._run_sampling_design)
        layout.addWidget(self.calc_optimal_btn)

        self.sampling_result_label = self._result_label()
        layout.addWidget(self.sampling_result_label)
        self.sampling_text = QTextBrowser()
        self.sampling_text.setMinimumHeight(160)
        layout.addWidget(self.sampling_text)
        layout.addStretch()

    def _create_report_tab(self):
        layout = self._make_tab('tab_report')
        layout.addWidget(self._info_label('report_title', 'report_desc'))

        self.report_sections_group = self._reg(QGroupBox(), 'report_sections', 'setTitle')
        group_layout = QVBoxLayout()
        self.report_checks = {}
        for key, label_key in REPORT_SECTIONS:
            check = QCheckBox()
            check.setChecked(True)
            self.report_checks[key] = check
            group_layout.addWidget(check)
        self.report_sections_group.setLayout(group_layout)
        layout.addWidget(self.report_sections_group)
        self._tr_callbacks.append(self._update_report_availability)
        self._update_report_availability()

        btn_row = QHBoxLayout()
        self.generate_html_btn = self._reg(QPushButton(), 'generate_report')
        self.generate_html_btn.clicked.connect(lambda: self._generate_report('html'))
        btn_row.addWidget(self.generate_html_btn)
        self.generate_pdf_btn = self._reg(QPushButton(), 'generate_pdf')
        self.generate_pdf_btn.clicked.connect(lambda: self._generate_report('pdf'))
        btn_row.addWidget(self.generate_pdf_btn)
        layout.addLayout(btn_row)

        self.report_hint = QLabel()
        self.report_hint.setWordWrap(True)
        self.report_hint.setStyleSheet(HINT_STYLE)
        self._reg(self.report_hint, 'report_preview_hint')
        layout.addWidget(self.report_hint)
        self.report_view = QTextBrowser()
        self.report_view.setMinimumHeight(300)
        layout.addWidget(self.report_view, 1)

    def _fill_combo(self, combo, items):
        """Riempie una combo con (chiave_dato, chiave_traduzione) e la registra."""
        def refill():
            current = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            for data, label_key in items:
                combo.addItem(tr(label_key), data)
            idx = combo.findData(current)
            combo.setCurrentIndex(idx if idx >= 0 else 0)
            combo.blockSignals(False)
        refill()
        self._tr_callbacks.append(refill)

    # ==================================================================
    # Layer / campo correnti
    # ==================================================================
    def _current_layer_field(self):
        layer = self.layer_combo.currentLayer()
        field = self.field_combo.currentField()
        if layer is None or not field:
            return None, None
        return layer, field

    def _source_key(self):
        layer, field = self._current_layer_field()
        return (layer.id() if layer else None, field)

    def _layer_units(self, layer):
        crs = layer.crs() if layer else None
        if crs is None or not crs.isValid():
            return tr('unit_generic')
        if crs.isGeographic():
            return tr('unit_deg')
        try:
            return QgsUnitTypes.toAbbreviatedString(crs.mapUnits())
        except Exception:
            return tr('unit_m')

    def _extract_points_values(self, layer, field=None):
        """
        Estrae coordinate e valori numerici validi (NULL e testo non numerico esclusi).
        Restituisce (points (n,2), values (n,), n_features, n_missing).
        """
        points, values = [], []
        n_total = n_missing = 0
        request = QgsFeatureRequest()
        if field:
            request.setSubsetOfAttributes([field], layer.fields())
        else:
            request.setSubsetOfAttributes([])
        for feature in layer.getFeatures(request):
            n_total += 1
            geom = feature.geometry()
            if geom is None or geom.isEmpty():
                continue
            if field:
                value = attribute_to_float(feature[field])
                if value is None:
                    n_missing += 1
                    continue
            else:
                value = 0.0
            point = geom.asMultiPoint()[0] if geom.isMultipart() else geom.asPoint()
            points.append([point.x(), point.y()])
            values.append(value)
        return (np.array(points, dtype=float).reshape(-1, 2), np.array(values, dtype=float),
                n_total, n_missing)

    def _on_layer_changed(self, layer):
        self.field_combo.setLayer(layer)
        if layer is not None and is_point_layer(layer):
            if layer.featureCount() > 0:
                points, _, _, _ = self._extract_points_values(layer, None)
                if len(points) >= 2:
                    self.max_dist_spin.setValue(self.engine.suggest_max_distance(points))
            self.resolution_spin.setValue(self.engine.suggest_pixel_size(layer.extent()))
        self._on_field_changed(self.field_combo.currentField())
        self._preselect_ml_layer(layer)

    def _on_field_changed(self, field):
        self._update_layer_summary()
        self._update_grid_info()
        self._update_kriging_status()
        self._update_sampling_desc()

    def _update_layer_summary(self):
        layer, field = self._current_layer_field()
        if layer is None:
            if self.layer_combo.currentLayer() is None:
                self.layer_summary_label.setText(tr('no_layer_selected'))
            else:
                self.layer_summary_label.setText(tr('no_numeric_field'))
            self.layer_summary_label.setStyleSheet(WARN_STYLE)
            self.existing_points_label.setText(tr_format('existing_points', layer='-'))
            return
        points, values, n_total, n_missing = self._extract_points_values(layer, field)
        extent = layer.extent()
        unit = self._layer_units(layer)
        text = tr_format('layer_summary', n=len(values), total=n_total, crs=layer.crs().authid() or '-',
                         w=fmt(extent.width()), h=fmt(extent.height()), unit=unit)
        style = HINT_STYLE
        if layer.crs().isGeographic():
            text += "<br>" + tr('geographic_crs_warning')
            style = WARN_STYLE
        self.layer_summary_label.setStyleSheet(style)
        self.layer_summary_label.setText(text)
        self.existing_points_label.setText(tr_format('existing_points', layer=layer.name()))

    def _update_grid_info(self):
        layer = self.layer_combo.currentLayer()
        if layer is None:
            self.grid_info_label.setText('')
            return
        try:
            nx, ny, ps, capped = self.engine.grid_shape(layer.extent(), self.resolution_spin.value())
        except ValueError:
            self.grid_info_label.setText('')
            return
        text = tr_format('grid_info', nx=nx, ny=ny, cells=f"{nx * ny:,}")
        if capped:
            text += tr_format('grid_capped', ps=fmt(ps), side=MAX_GRID_SIDE)
        self.grid_info_label.setText(text)
        self.grid_info_label.setStyleSheet(WARN_STYLE if (capped or nx * ny > LARGE_GRID_CELLS) else HINT_STYLE)

    def _usable_variogram(self):
        """Variogramma corrente se calcolato sullo stesso layer/campo, altrimenti None."""
        vg = self.current_results.get('variogram')
        if not vg or not self.use_variogram.isChecked():
            return None
        if tuple(vg.get('source', (None, None))) != self._source_key():
            return None
        return vg

    def _update_kriging_status(self):
        vg = self.current_results.get('variogram')
        layer = self.layer_combo.currentLayer()
        unit = self._layer_units(layer) if layer else ''
        if vg and tuple(vg.get('source', (None, None))) == self._source_key():
            params = vg['model_params']
            self.variogram_status_label.setText(tr_format(
                'variogram_status_ok', model=tr(MODEL_LABEL_KEYS[vg['model_type']]).split(' (')[0],
                range=fmt(params['range']), unit=unit))
            self.use_variogram.setEnabled(True)
        elif vg:
            self.variogram_status_label.setText(tr('variogram_status_stale'))
            self.use_variogram.setEnabled(False)
        else:
            self.variogram_status_label.setText(tr('variogram_status_none'))
            self.use_variogram.setEnabled(False)

    def _update_sampling_desc(self, *_):
        key = self.sampling_combo.currentData()
        for data, _, desc_key in SAMPLING_METHODS:
            if data == key:
                self.sampling_desc_label.setText(tr(desc_key))
        layer = self.layer_combo.currentLayer()
        self.existing_points_label.setText(tr_format('existing_points', layer=layer.name() if layer else '-'))

    def _update_report_availability(self):
        for key, label_key in REPORT_SECTIONS:
            check = self.report_checks[key]
            available = key in self.current_results
            status = tr('available') if available else tr('not_available')
            check.setText(f"{tr(label_key)} ({status})")
            check.setEnabled(available)

    def _check_crs(self, layer):
        if layer.crs().isValid() and layer.crs().isGeographic():
            return question_yes_no(self, tr('warning'), tr('geographic_crs_question'))
        return True

    def _require_data(self, min_points=MIN_POINTS):
        """Layer, campo, punti e valori correnti; None se mancano."""
        layer, field = self._current_layer_field()
        if layer is None:
            self._warn(tr('select_layer_field'))
            return None
        points, values, _, _ = self._extract_points_values(layer, field)
        if len(points) < min_points:
            self._warn(tr_format('min_points', n=min_points, found=len(points)))
            return None
        return layer, field, points, values

    # ==================================================================
    # Thread
    # ==================================================================
    def _is_busy(self):
        if self.analysis_thread is not None and self.analysis_thread.isRunning():
            self._warn(tr('analysis_running'))
            return True
        return False

    def _start_analysis(self, method, params, on_done, determinate=False):
        self.progress_bar.setRange(0, 100 if determinate else 0)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.cancel_btn.setVisible(True)
        self._set_buttons_enabled(False)
        gc.collect()   # raccolta nel thread principale prima di avviare il worker
        self.analysis_thread = AnalysisThread(self.engine, method, params)
        self.analysis_thread.result_ready.connect(lambda result: self._finish_analysis(on_done, result))
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.progress.connect(self.progress_bar.setValue)
        self.analysis_thread.start()

    def _finish_analysis(self, on_done, result):
        self._hide_progress()
        try:
            on_done(result)
        except Exception as e:
            log(traceback.format_exc(), Qgis_Critical)
            self._error(tr_format('error_visualization', msg=str(e)))

    def _hide_progress(self):
        self.progress_bar.setVisible(False)
        self.cancel_btn.setVisible(False)
        self._set_buttons_enabled(True)

    def _set_buttons_enabled(self, enabled):
        for btn in (self.calc_variogram_btn, self.run_kriging_btn, self.run_ml_btn, self.calc_optimal_btn):
            btn.setEnabled(enabled)

    def _cancel_analysis(self):
        if self.analysis_thread is not None:
            self.analysis_thread.cancel()
            self.cancel_btn.setEnabled(False)

    def _on_analysis_error(self, error_msg):
        self._hide_progress()
        self.cancel_btn.setEnabled(True)
        if error_msg == 'cancelled':
            self._notify(tr('analysis_cancelled'), Qgis_Warning)
            return
        self._error(tr_format('error_analysis', msg=error_msg))

    # ==================================================================
    # 1. Dati
    # ==================================================================
    def _run_eda(self):
        data = self._require_data(min_points=1)
        if data is None:
            return
        layer, field, points, values = data
        _, _, n_total, n_missing = self._extract_points_values(layer, field)
        from scipy import stats as scipy_stats
        std = float(np.std(values))
        mean = float(np.mean(values))
        skew = float(scipy_stats.skew(values)) if len(values) > 2 else 0.0
        kurt = float(scipy_stats.kurtosis(values)) if len(values) > 3 else 0.0
        outliers = int(np.sum(np.abs(values - mean) > 3 * std)) if std > 0 else 0
        stats = {
            'n': int(len(values)), 'missing': int(n_missing), 'min': float(values.min()), 'max': float(values.max()),
            'mean': mean, 'median': float(np.median(values)), 'std': std,
            'cv': (std / abs(mean)) if mean != 0 else float('nan'),
            'q1': float(np.percentile(values, 25)), 'q3': float(np.percentile(values, 75)),
            'skewness': skew, 'kurtosis': kurt, 'outliers': outliers,
        }
        self.current_results['stats'] = {
            'layer': layer.name(), 'field': field, 'source': self._source_key(), 'stats': stats}
        self.stats_view.setHtml(self._render_stats_html(stats))
        try:
            fig = self.engine.create_histogram(values, field)
            self.current_figures['histogram'] = fig
            png = None if WEBENGINE_AVAILABLE else self.engine.render_histogram_png(values, field)
            self.data_plot.show_figure(fig, png, self.temp_dir)
        except Exception as e:
            log(f"Histogram error: {e}", Qgis_Warning)
        self._update_report_availability()
        self._notify(f"{tr('statistics')}: {layer.name()} / {field}", Qgis_Success, 3)

    def _render_stats_html(self, stats):
        rows = [('stat_n', stats['n']), ('stat_nulls', stats['missing']), ('stat_min', fmt(stats['min'])),
                ('stat_max', fmt(stats['max'])), ('stat_mean', fmt(stats['mean'])),
                ('stat_median', fmt(stats['median'])), ('stat_std', fmt(stats['std'])),
                ('stat_cv', fmt(stats['cv'])), ('stat_q1', fmt(stats['q1'])), ('stat_q3', fmt(stats['q3'])),
                ('stat_skew', fmt(stats['skewness'])), ('stat_kurt', fmt(stats['kurtosis']))]
        table = "".join(f"<tr><td>{tr(k)}</td><td align='right'><b>{v}</b></td></tr>" for k, v in rows)
        notes = []
        if stats['skewness'] > 1:
            notes.append(tr('interp_skew_right'))
        elif stats['skewness'] < -1:
            notes.append(tr('interp_skew_left'))
        else:
            notes.append(tr('interp_symmetric'))
        if stats['outliers'] > 0:
            notes.append(tr_format('interp_outliers', n=stats['outliers']))
        notes_html = "".join(f"<li>{n}</li>" for n in notes)
        return (f"<table cellpadding='3' style='border-collapse:collapse'>{table}</table>"
                f"<ul>{notes_html}</ul>")

    # ==================================================================
    # 2. Variogramma
    # ==================================================================
    def _auto_max_distance(self):
        layer = self.layer_combo.currentLayer()
        if layer is None:
            return
        points, _, _, _ = self._extract_points_values(layer, None)
        if len(points) >= 2:
            self.max_dist_spin.setValue(self.engine.suggest_max_distance(points))

    def _calculate_variogram(self):
        if self._is_busy():
            return
        data = self._require_data()
        if data is None:
            return
        layer, field, points, values = data
        if not self._check_crs(layer):
            return
        fixed = {}
        if self.manual_group.isChecked():
            for key, spin in (('nugget', self.nugget_spin), ('sill', self.sill_spin), ('range', self.range_spin)):
                if spin.value() > 0:
                    fixed[key] = spin.value()
        params = {
            'points': points, 'values': values,
            'max_dist': self.max_dist_spin.value(),
            'model_type': self.model_combo.currentData(),
            'check_anisotropy': self.anisotropy_check.isChecked(),
            'fixed_params': fixed or None,
            'source': self._source_key(), 'layer_name': layer.name(), 'field': field,
            'unit': self._layer_units(layer),
        }
        self._start_analysis('variogram', params, self._on_variogram_complete)

    def _on_variogram_complete(self, result):
        p = self.analysis_thread.params
        result['source'] = p['source']
        result['layer_name'] = p['layer_name']
        result['field'] = p['field']
        result['unit'] = p['unit']
        self.current_results['variogram'] = result
        self.variogram_result_label.setText(self._render_variogram_summary(result))
        self.variogram_result_label.setVisible(True)

        fig = self.engine.create_interactive_variogram(result)
        self.current_figures['variogram'] = fig
        png = None if WEBENGINE_AVAILABLE else self.engine.render_variogram_png(result)
        self.variogram_plot.show_figure(fig, png, self.temp_dir)

        self._update_kriging_status()
        self._update_report_availability()
        self._notify(tr2("Variogramma calcolato", "Variogram calculated"), Qgis_Success, 3)

    def _render_variogram_summary(self, result):
        params = result['model_params']
        unit = result.get('unit', '')
        model = tr(MODEL_LABEL_KEYS[result['model_type']]).split(' (')[0]
        lines = [tr_format('variogram_results', model=model, nugget=fmt(params['nugget']),
                           sill=fmt(params['sill']), range=fmt(params['range']), unit=unit,
                           rmse=fmt(params['rmse']))]
        pairs = tr_format('variogram_pairs', pairs=f"{sum(result['n_pairs']):,}", lags=len(result['n_pairs']))
        if result.get('n_points_used', 0) < result.get('n_points', 0):
            pairs += tr_format('variogram_subsampled', used=result['n_points_used'], n=result['n_points'])
        lines.append(pairs)
        lines.append(tr_format('interp_range', range=fmt(params['range']), unit=unit))
        pct = 100.0 * params['nugget'] / params['sill'] if params['sill'] > 0 else 0.0
        key = 'interp_nugget_low' if pct < 25 else ('interp_nugget_mid' if pct < 60 else 'interp_nugget_high')
        lines.append(tr_format(key, pct=f"{pct:.0f}"))
        aniso = result.get('anisotropy')
        if aniso:
            if aniso.get('note'):
                lines.append(tr('anisotropy_insufficient'))
            elif aniso.get('is_anisotropic'):
                lines.append(tr_format('anisotropy_result', ratio=f"{aniso['ratio']:.2f}", dir=aniso['major_direction']))
            else:
                lines.append(tr_format('anisotropy_none', ratio=f"{aniso['ratio']:.2f}"))
        return "<br>".join(lines)

    # ==================================================================
    # 3. Kriging
    # ==================================================================
    def _run_kriging(self):
        if self._is_busy():
            return
        data = self._require_data()
        if data is None:
            return
        layer, field, points, values = data
        if not self._check_crs(layer):
            return
        extent = QgsRectangle(layer.extent())
        pixel_size = self.resolution_spin.value()
        nx, ny, ps, capped = self.engine.grid_shape(extent, pixel_size)
        if nx * ny > LARGE_GRID_CELLS:
            if not question_yes_no(self, tr('warning'), tr_format('grid_large_question', cells=f"{nx * ny:,}")):
                return
        params = {
            'points': points, 'values': values, 'extent': extent, 'pixel_size': pixel_size,
            'variogram_params': self._usable_variogram(),
            'source': self._source_key(), 'layer_name': layer.name(), 'field': field,
            'crs': layer.crs(), 'unit': self._layer_units(layer),
        }
        self._start_analysis('kriging', params, self._on_kriging_complete, determinate=True)

    def _on_kriging_complete(self, result):
        p = self.analysis_thread.params
        for key in ('source', 'layer_name', 'field', 'unit'):
            result[key] = p[key]
        result['points'] = p['points']
        self.current_results['kriging'] = result

        try:
            fig = self.engine.create_interactive_kriging_map(
                result['x_grid'], result['y_grid'], result['predictions'], result['variances'], p['points'])
            self.current_figures['kriging'] = fig
            png = None
            if not WEBENGINE_AVAILABLE:
                png = self.engine.render_kriging_png(result['x_grid'], result['y_grid'],
                                                     result['predictions'], result['variances'], p['points'])
            self.kriging_plot.show_figure(fig, png, self.temp_dir)
        except Exception as e:
            log(f"Kriging visualization error: {traceback.format_exc()}", Qgis_Warning)

        names = self._create_kriging_rasters(result, p['crs'], p['field'])
        self.kriging_result_label.setText(self._render_kriging_summary(result))
        self.kriging_result_label.setVisible(True)
        self._update_report_availability()
        if names:
            self._notify(tr_format('kriging_layers_added', names=", ".join(names)), Qgis_Success, 6)

    def _render_kriging_summary(self, result):
        ny, nx = result['predictions'].shape
        vg = result['variogram']
        unit = result.get('unit', '')
        model = tr(MODEL_LABEL_KEYS.get(vg['model_type'], 'model_spherical')).split(' (')[0]
        lines = [tr_format('kriging_results', n=result['n_points'], nx=nx, ny=ny, ps=fmt(result['pixel_size']),
                           unit=unit, model=model, range=fmt(vg['model_params']['range']))]
        if result.get('grid_capped'):
            lines.append(tr_format('grid_capped', ps=fmt(result['pixel_size']), side=MAX_GRID_SIDE).strip(' ·'))
        cv = result.get('cv_results')
        if cv:
            lines.append(f"<b>{tr_format('cv_title', n=cv['n_valid'])}</b>")
            lines.append(f"{tr('cv_rmse')}: <b>{fmt(cv['rmse'])}</b> · {tr('cv_mae')}: <b>{fmt(cv['mae'])}</b>")
            lines.append(f"{tr('cv_me')}: <b>{fmt(cv['me'])}</b> · {tr('cv_r2')}: <b>{fmt(cv['r2'])}</b>"
                         + (f" · {tr('cv_msdr')}: <b>{fmt(cv['msdr'])}</b>" if cv.get('msdr') is not None else ''))
            r2 = cv['r2']
            lines.append(tr('interp_r2_good') if r2 >= 0.5 else (tr('interp_r2_mid') if r2 >= 0.2 else tr('interp_r2_low')))
            if cv.get('msdr') is not None:
                if cv['msdr'] > 1.5:
                    lines.append(tr('interp_msdr_over'))
                elif cv['msdr'] < 0.5:
                    lines.append(tr('interp_msdr_under'))
        else:
            lines.append(tr('cv_none'))
        return "<br>".join(lines)

    def _create_kriging_rasters(self, result, crs, field):
        """Crea i raster (predizione + incertezza) e li aggiunge al progetto."""
        names = []
        stamp = datetime.now().strftime('%H%M%S')
        safe_field = "".join(c if c.isalnum() else '_' for c in str(field))
        try:
            name = tr_format('kriging_result_layer', field=safe_field)
            path = os.path.join(self.temp_dir, f"kriging_{safe_field}_{stamp}.tif")
            layer = self._write_raster(path, result['predictions'], result['x_grid'], result['y_grid'], crs, name)
            if layer is not None:
                self._apply_color_ramp(layer, result['predictions'],
                                       [(49, 54, 149), (116, 173, 209), (255, 255, 191), (244, 109, 67), (165, 0, 38)])
                QgsProject.instance().addMapLayer(layer)
                names.append(name)
            if self.create_uncertainty.isChecked() and result.get('variances') is not None:
                std = np.sqrt(np.where(result['variances'] >= 0, result['variances'], np.nan))
                name = tr_format('kriging_std_layer', field=safe_field)
                path = os.path.join(self.temp_dir, f"kriging_{safe_field}_std_{stamp}.tif")
                std_layer = self._write_raster(path, std, result['x_grid'], result['y_grid'], crs, name)
                if std_layer is not None:
                    self._apply_color_ramp(std_layer, std,
                                           [(255, 255, 229), (254, 217, 118), (253, 141, 60), (189, 0, 38)])
                    QgsProject.instance().addMapLayer(std_layer, False)
                    root = QgsProject.instance().layerTreeRoot()
                    node = root.insertLayer(0, std_layer)
                    if node is not None:
                        node.setItemVisibilityChecked(False)
                    names.append(name)
        except Exception as e:
            log(f"Raster creation error: {traceback.format_exc()}", Qgis_Critical)
            self._error(tr_format('error_visualization', msg=str(e)))
        return names

    def _write_raster(self, path, array, x_grid, y_grid, crs, name, nodata=-9999.0):
        from osgeo import gdal, osr
        array = np.asarray(array, dtype=float)
        ny, nx = array.shape
        psx = float(x_grid[1] - x_grid[0]) if len(x_grid) > 1 else 1.0
        psy = float(y_grid[1] - y_grid[0]) if len(y_grid) > 1 else 1.0
        data = np.flipud(np.where(np.isfinite(array), array, nodata)).astype(np.float32)
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(path, nx, ny, 1, gdal.GDT_Float32, options=['COMPRESS=LZW'])
        if dataset is None:
            raise RuntimeError(f"Cannot create raster {path}")
        dataset.SetGeoTransform([float(x_grid[0]) - psx / 2, psx, 0, float(y_grid[-1]) + psy / 2, 0, -psy])
        if crs is not None and crs.isValid():
            srs = osr.SpatialReference()
            srs.ImportFromWkt(crs.toWkt())
            dataset.SetProjection(srs.ExportToWkt())
        band = dataset.GetRasterBand(1)
        band.WriteArray(data)
        band.SetNoDataValue(nodata)
        band.FlushCache()
        band = None
        dataset = None
        layer = QgsRasterLayer(path, name, 'gdal')
        if not layer.isValid():
            log(f"Invalid raster layer: {path}", Qgis_Critical)
            return None
        return layer

    def _apply_color_ramp(self, raster_layer, array, rgb_stops):
        try:
            valid = np.asarray(array, dtype=float)
            valid = valid[np.isfinite(valid)]
            if len(valid) == 0:
                return
            vmin, vmax = float(valid.min()), float(valid.max())
            if vmax <= vmin:
                vmax = vmin + 1e-9
            items = []
            for i, rgb in enumerate(rgb_stops):
                value = vmin + (vmax - vmin) * i / (len(rgb_stops) - 1)
                items.append(QgsColorRampShader.ColorRampItem(value, QColor(*rgb), fmt(value)))
            ramp = QgsColorRampShader()
            ramp.setColorRampType(ColorRamp_Interpolated)
            ramp.setColorRampItemList(items)
            shader = QgsRasterShader()
            shader.setRasterShaderFunction(ramp)
            renderer = QgsSingleBandPseudoColorRenderer(raster_layer.dataProvider(), 1, shader)
            raster_layer.setRenderer(renderer)
            raster_layer.triggerRepaint()
        except Exception as e:
            log(f"Color style error: {e}", Qgis_Warning)

    # ==================================================================
    # 4. Machine learning
    # ==================================================================
    def _update_ml_layers(self, *_):
        selected = {self.ml_layers.item(i).data(Qt_UserRole)
                    for i in range(self.ml_layers.count()) if self.ml_layers.item(i).isSelected()}
        self.ml_layers.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if is_point_layer(layer):
                item = QListWidgetItem(layer.name())
                item.setData(Qt_UserRole, layer.id())
                self.ml_layers.addItem(item)
                if layer.id() in selected:
                    item.setSelected(True)

    def _preselect_ml_layer(self, layer):
        if layer is None:
            return
        any_selected = any(self.ml_layers.item(i).isSelected() for i in range(self.ml_layers.count()))
        if any_selected:
            return
        for i in range(self.ml_layers.count()):
            if self.ml_layers.item(i).data(Qt_UserRole) == layer.id():
                self.ml_layers.item(i).setSelected(True)

    def _selected_ml_layers(self):
        layers = []
        for i in range(self.ml_layers.count()):
            item = self.ml_layers.item(i)
            if item.isSelected():
                layer = QgsProject.instance().mapLayer(item.data(Qt_UserRole))
                if layer is not None:
                    layers.append(layer)
        return layers

    def _run_ml(self):
        if self._is_busy():
            return
        selected_layers = self._selected_ml_layers()
        if not selected_layers:
            self._warn(tr('select_at_least_one_layer'))
            return
        layers_data = []
        for layer in selected_layers:
            numeric_fields = [f.name() for f in layer.fields() if f.isNumeric()]
            data = {'name': layer.name(), 'points': [], 'features': []}
            for feature in layer.getFeatures():
                geom = feature.geometry()
                if geom is None or geom.isEmpty():
                    continue
                point = geom.asMultiPoint()[0] if geom.isMultipart() else geom.asPoint()
                data['points'].append([point.x(), point.y()])
                data['features'].append([attribute_to_float(feature[name]) for name in numeric_fields])
            if data['points']:
                layers_data.append(data)
        if not layers_data:
            self._warn(tr('no_valid_data'))
            return
        params = {
            'layers_data': layers_data,
            'method': self.ml_method.currentData(),
            'n_clusters': self.ml_clusters_spin.value() or None,
            'method_label': self.ml_method.currentText(),
            'crs': selected_layers[0].crs(),
            'layer_names': [l.name() for l in selected_layers],
        }
        self._start_analysis('ml', params, self._on_ml_complete)

    def _on_ml_complete(self, result):
        p = self.analysis_thread.params
        result['method_label'] = p['method_label']
        result['layer_names'] = p['layer_names']
        self.current_results['ml'] = result

        fig = self.engine.create_ml_visualization(result['features'], result['labels'], p['method_label'],
                                                  result.get('class_names'))
        self.current_figures['ml'] = fig
        png = None if WEBENGINE_AVAILABLE else self.engine.render_ml_png(
            result['features'], result['labels'], p['method_label'], result.get('class_names'))
        self.ml_plot.show_figure(fig, png, self.temp_dir)

        name = self._create_ml_layer(result, p['crs'])
        self.ml_result_label.setText(self._render_ml_summary(result))
        self.ml_result_label.setVisible(True)
        self._update_report_availability()
        if name:
            self._notify(tr_format('layer_created', name=name), Qgis_Success, 5)

    def _cluster_names(self, result):
        """Nome leggibile per ogni etichetta (gruppo / anomalia / isolati)."""
        labels = np.asarray(result['labels'])
        method = result.get('method', 'kmeans')
        names = {}
        for label in np.unique(labels):
            label = int(label)
            count = int(np.sum(labels == label))
            if method == 'isolation_forest':
                base = tr('anomaly_outlier') if label == 1 else tr('anomaly_normal')
                names[label] = f"{base} (n={count})"
            elif method == 'dbscan' and label == -1:
                names[label] = f"{tr('noise_points')} (n={count})"
            elif result.get('class_names') and label in result['class_names']:
                names[label] = f"{result['class_names'][label]} (n={count})"
            else:
                names[label] = tr_format('cluster_with_count', letter=chr(ord('A') + label % 26), count=count)
        return names

    def _render_ml_summary(self, result):
        names = self._cluster_names(result)
        lines = [tr_format('ml_results', method=result['method_label'], n=len(names),
                           points=len(result['labels']))]
        for label in sorted(names):
            lines.append(names[label])
        return "<br>".join(lines)

    def _create_ml_layer(self, result, crs):
        try:
            method = result.get('method', 'kmeans')
            is_anomaly = method == 'isolation_forest'
            layer_name = tr('ml_anomalies_layer') if is_anomaly else tr('ml_clusters_layer')
            layer = QgsVectorLayer(f'Point?crs={crs.authid()}', layer_name, 'memory')
            provider = layer.dataProvider()
            provider.addAttributes([
                QgsField('cluster_id', QVariant_Int),
                QgsField('cluster_name', QVariant_String),
                QgsField('cluster_size', QVariant_Int),
                QgsField('method', QVariant_String),
                QgsField('x_coord', QVariant_Double),
                QgsField('y_coord', QVariant_Double),
            ])
            layer.updateFields()
            names = self._cluster_names(result)
            labels = np.asarray(result['labels'])
            sizes = {int(l): int(np.sum(labels == l)) for l in np.unique(labels)}
            features = []
            for (x, y), label in zip(result['coordinates'], labels):
                label = int(label)
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x), float(y))))
                feat.setAttributes([label, names[label], sizes[label], result.get('method_label', method),
                                    float(x), float(y)])
                features.append(feat)
            provider.addFeatures(features)
            layer.updateExtents()

            palette = ['#E53935', '#43A047', '#1E88E5', '#FDD835', '#8E24AA',
                       '#00ACC1', '#FB8C00', '#6D4C41', '#546E7A', '#D81B60']
            categories = []
            for i, label in enumerate(sorted(names)):
                if is_anomaly:
                    color = '#E53935' if label == 1 else '#90CAF9'
                elif label == -1:
                    color = '#9E9E9E'
                else:
                    color = palette[i % len(palette)]
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'circle', 'color': color, 'size': '3.5' if not (is_anomaly and label == 1) else '5',
                    'outline_style': 'solid', 'outline_width': '0.4', 'outline_color': 'black'})
                categories.append(QgsRendererCategory(label, symbol, names[label]))
            layer.setRenderer(QgsCategorizedSymbolRenderer('cluster_id', categories))
            QgsProject.instance().addMapLayer(layer)
            return layer_name
        except Exception as e:
            log(f"ML layer error: {traceback.format_exc()}", Qgis_Warning)
            return None

    # ==================================================================
    # 5. Campionamento
    # ==================================================================
    def _run_sampling_design(self):
        if self._is_busy():
            return
        layer = self.layer_combo.currentLayer()
        if layer is None:
            self._warn(tr('select_existing_points'))
            return
        existing_points, _, _, _ = self._extract_points_values(layer, None)
        if len(existing_points) == 0:
            self._warn(tr('no_points_in_layer'))
            return
        boundary = boundary_geometry(self.boundary_combo.currentLayer(), layer.crs())
        params = {
            'existing_points': existing_points, 'boundary': boundary,
            'n_new': self.n_points_spin.value(), 'method': self.sampling_combo.currentData(),
            'method_label': self.sampling_combo.currentText(),
            'variogram_params': self._usable_variogram() if self.sampling_combo.currentData() == 'variance' else None,
            'crs': layer.crs(), 'layer_name': layer.name(),
        }
        self._start_analysis('sampling', params, self._on_sampling_complete)

    def _on_sampling_complete(self, new_points):
        p = self.analysis_thread.params
        new_points = np.asarray(new_points, dtype=float).reshape(-1, 2)
        self.current_results['sampling'] = {
            'points': new_points, 'method': p['method'], 'method_label': p['method_label'],
            'layer_name': p['layer_name'], 'n': int(len(new_points)),
        }
        self.sampling_result_label.setText(tr_format('sampling_results', n=len(new_points), method=p['method_label']))
        self.sampling_result_label.setVisible(True)
        rows = "".join(f"<tr><td>{i + 1}</td><td>{x:.2f}</td><td>{y:.2f}</td></tr>"
                       for i, (x, y) in enumerate(new_points))
        self.sampling_text.setHtml(f"<p>{tr('suggested_points')}</p><table cellpadding='3'>"
                                   f"<tr><th>#</th><th>X</th><th>Y</th></tr>{rows}</table>")
        name = self._create_sampling_layer(new_points, p['crs'])
        self._update_report_availability()
        if name:
            self._notify(tr_format('layer_created', name=name), Qgis_Success, 5)

    def _create_sampling_layer(self, new_points, crs):
        try:
            layer_name = tr('sampling_points_layer')
            layer = QgsVectorLayer(f'Point?crs={crs.authid()}', layer_name, 'memory')
            provider = layer.dataProvider()
            provider.addAttributes([
                QgsField('point_id', QVariant_Int), QgsField('x_coord', QVariant_Double),
                QgsField('y_coord', QVariant_Double), QgsField('type', QVariant_String)])
            layer.updateFields()
            features = []
            for i, (x, y) in enumerate(new_points):
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(x), float(y))))
                feat.setAttributes([i + 1, float(x), float(y), 'suggested'])
                features.append(feat)
            provider.addFeatures(features)
            layer.updateExtents()
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'star', 'color': '#FFD700', 'size': '5',
                'outline_style': 'solid', 'outline_width': '0.6', 'outline_color': '#D32F2F'})
            layer.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(layer)
            return layer_name
        except Exception:
            log(f"Sampling layer error: {traceback.format_exc()}", Qgis_Warning)
            return None

    # ==================================================================
    # 6. Report
    # ==================================================================
    def generate_full_report(self):
        """Called from the plugin toolbar: go to the Report tab and save the HTML report."""
        self.switch_to_tab('report')
        self._generate_report('html')

    def _generate_report(self, format_type):
        sections = [key for key, check in self.report_checks.items()
                    if check.isChecked() and key in self.current_results]
        if not any(key in self.current_results for key, _ in REPORT_SECTIONS):
            self._warn(tr('report_nothing'))
            return
        if not sections:
            self._warn(tr('report_no_sections'))
            return
        self.report_view.setHtml(self.build_report_html(sections, embed_plots=False))
        if format_type == 'html':
            file_path, _ = QFileDialog.getSaveFileName(self, tr('save_report_html'), 'geoarchaeo_report.html',
                                                       "HTML (*.html)")
            if not file_path:
                return
            with open(file_path, 'w', encoding='utf-8') as handle:
                handle.write(self.build_report_html(sections, embed_plots=True))
            self._notify(tr_format('report_saved', path=file_path), Qgis_Success, 8)
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        elif format_type == 'pdf':
            self._export_pdf_report(self.build_report_html(sections, embed_plots=False))

    def _html_table(self, rows, header=None):
        head = ''
        if header:
            head = "<tr>" + "".join(f"<th>{html_lib.escape(str(h))}</th>" for h in header) + "</tr>"
        body = "".join("<tr>" + "".join(f"<td>{html_lib.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows)
        return f"<table>{head}{body}</table>"

    def build_report_html(self, sections, embed_plots=True):
        """Costruisce il report HTML; con embed_plots include i grafici Plotly."""
        parts = [f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>GeoArchaeo Report</title>
<style>
 body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; max-width: 1000px; }}
 h1 {{ color: #2c3e50; }} h2 {{ color: #34495e; margin-top: 32px; border-bottom: 1px solid #ccc; }}
 table {{ border-collapse: collapse; margin: 10px 0; }} th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
 th {{ background-color: #3498db; color: white; }} .meta {{ color: #7f8c8d; font-style: italic; }}
 .note {{ background: #f1f8e9; padding: 8px; border-left: 4px solid #7cb342; }}
 .plot {{ margin: 12px 0; height: 520px; }}
</style></head><body>
<h1>GeoArchaeo – Report</h1>
<p class="meta">{tr('report_generated')}: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"""]
        first_plot = [True]

        def plot_html(key):
            fig = self.current_figures.get(key)
            if fig is None or not embed_plots:
                return ''
            html = fig.to_html(full_html=False, include_plotlyjs=first_plot[0],
                               default_width='100%', default_height='500px')
            first_plot[0] = False
            return f"<div class='plot'>{html}</div>"

        if 'stats' in sections:
            s = self.current_results['stats']
            st = s['stats']
            parts.append(f"<h2>{tr('section_stats')}</h2><p>{tr('report_layer')}: <b>{html_lib.escape(s['layer'])}</b> · "
                         f"{tr('report_field')}: <b>{html_lib.escape(s['field'])}</b></p>")
            parts.append(self._render_stats_html(st).replace("<table cellpadding='3' style='border-collapse:collapse'>", "<table>"))
            parts.append(plot_html('histogram'))

        if 'variogram' in sections:
            v = self.current_results['variogram']
            mp = v['model_params']
            parts.append(f"<h2>{tr('section_variogram')}</h2><p>{tr('report_layer')}: <b>{html_lib.escape(v['layer_name'])}</b> · "
                         f"{tr('report_field')}: <b>{html_lib.escape(v['field'])}</b></p>")
            rows = [(tr('theoretical_model').rstrip(':'), tr(MODEL_LABEL_KEYS[v['model_type']])),
                    ('Nugget', fmt(mp['nugget'])), ('Sill', fmt(mp['sill'])),
                    ('Range', f"{fmt(mp['range'])} {v.get('unit', '')}"), ('RMSE', fmt(mp['rmse'])),
                    (tr('max_distance').rstrip(':'), f"{fmt(v['max_distance'])} {v.get('unit', '')}")]
            parts.append(self._html_table(rows, [tr('report_parameter'), tr('report_value')]))
            parts.append(f"<p class='note'>{self._render_variogram_summary(v)}</p>")
            parts.append(plot_html('variogram'))

        if 'kriging' in sections:
            k = self.current_results['kriging']
            ny, nx = k['predictions'].shape
            parts.append(f"<h2>{tr('section_kriging')}</h2><p>{tr('report_layer')}: <b>{html_lib.escape(k['layer_name'])}</b> · "
                         f"{tr('report_field')}: <b>{html_lib.escape(k['field'])}</b></p>")
            rows = [(tr('report_method'), 'Ordinary Kriging'),
                    (tr('grid_resolution').rstrip(':'), f"{fmt(k['pixel_size'])} {k.get('unit', '')}"),
                    (tr('grid_info').split(':')[0], f"{nx} × {ny}")]
            cv = k.get('cv_results')
            if cv:
                rows += [(tr('cv_rmse'), fmt(cv['rmse'])), (tr('cv_mae'), fmt(cv['mae'])),
                         (tr('cv_me'), fmt(cv['me'])), (tr('cv_r2'), fmt(cv['r2']))]
                if cv.get('msdr') is not None:
                    rows.append((tr('cv_msdr'), fmt(cv['msdr'])))
            parts.append(self._html_table(rows, [tr('report_parameter'), tr('report_value')]))
            parts.append(f"<p class='note'>{self._render_kriging_summary(k)}</p>")
            parts.append(plot_html('kriging'))

        if 'ml' in sections:
            m = self.current_results['ml']
            names = self._cluster_names(m)
            parts.append(f"<h2>{tr('section_ml')}</h2><p>{tr('report_layer')}: <b>"
                         f"{html_lib.escape(', '.join(m.get('layer_names', [])))}</b></p>")
            parts.append(self._html_table([(names[l],) for l in sorted(names)], [m['method_label']]))
            parts.append(plot_html('ml'))

        if 'sampling' in sections:
            s = self.current_results['sampling']
            parts.append(f"<h2>{tr('section_sampling')}</h2><p>{tr('report_method')}: <b>{html_lib.escape(s['method_label'])}</b> · "
                         f"{tr('report_layer')}: <b>{html_lib.escape(s['layer_name'])}</b></p>")
            parts.append(self._html_table([(i + 1, f"{x:.2f}", f"{y:.2f}") for i, (x, y) in enumerate(s['points'])],
                                          ['#', 'X', 'Y']))

        parts.append("</body></html>")
        return "\n".join(parts)

    def _export_pdf_report(self, html_content):
        try:
            from qgis.PyQt.QtGui import QTextDocument
            file_path, _ = QFileDialog.getSaveFileName(self, tr('save_report_pdf'), 'geoarchaeo_report.pdf',
                                                       "PDF (*.pdf)")
            if not file_path:
                return
            doc = QTextDocument()
            doc.setHtml(html_content)
            print_document(doc, pdf_printer(file_path))
            self._notify(tr_format('report_saved', path=file_path), Qgis_Success, 8)
        except Exception as e:
            log(f"PDF export error: {traceback.format_exc()}", Qgis_Critical)
            self._warn(tr_format('report_pdf_error', msg=str(e)))

    # ==================================================================
    # Lingua, esempi, tutorial
    # ==================================================================
    def _change_language(self, index):
        set_language(self.lang_combo.itemData(index))
        self._retranslate()
        self._notify(tr('language_changed'), Qgis_Info, 3)

    def _retranslate(self):
        for widget, setter, key in self._tr_widgets:
            getattr(widget, setter)(tr(key))
        for callback in self._tr_callbacks:
            try:
                callback()
            except Exception as e:
                log(f"retranslate: {e}", Qgis_Warning)
        for panel in (self.data_plot, self.variogram_plot, self.kriging_plot, self.ml_plot):
            panel.retranslate()
        self._update_layer_summary()
        self._update_grid_info()
        self._update_kriging_status()
        if 'stats' in self.current_results:
            self.stats_view.setHtml(self._render_stats_html(self.current_results['stats']['stats']))
        if 'variogram' in self.current_results:
            self.variogram_result_label.setText(self._render_variogram_summary(self.current_results['variogram']))
        if 'kriging' in self.current_results:
            self.kriging_result_label.setText(self._render_kriging_summary(self.current_results['kriging']))
        if 'ml' in self.current_results:
            self.ml_result_label.setText(self._render_ml_summary(self.current_results['ml']))

    def _example_files(self, directory):
        """Dataset di esempio: GeoPackage/GeoJSON e CSV x/y senza versione vettoriale."""
        if not os.path.isdir(directory):
            return []
        names = sorted(os.listdir(directory))
        stems_vector = {os.path.splitext(n)[0] for n in names if n.lower().endswith(('.gpkg', '.geojson'))}
        files = []
        for name in names:
            stem, ext = os.path.splitext(name)
            ext = ext.lower()
            if ext in ('.gpkg', '.geojson') or (ext == '.csv' and stem not in stems_vector):
                files.append(os.path.join(directory, name))
        return files

    def show_load_examples_dialog(self):
        """Dialogo per aggiungere i dataset di esempio inclusi nel plugin."""
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('examples_title'))
        dialog.setMinimumWidth(480)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(tr('examples_desc')))

        checks_box = QVBoxLayout()
        layout.addLayout(checks_box)
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel(tr('examples_path')))
        path_label = QLabel(self.example_dir)
        path_label.setWordWrap(True)
        path_row.addWidget(path_label, 1)
        browse_btn = QPushButton(tr('browse'))
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        checks = []

        def fill(directory):
            for cb in checks:
                checks_box.removeWidget(cb)
                cb.deleteLater()
            checks.clear()
            files = self._example_files(directory)
            if not files:
                cb = QCheckBox(tr_format('examples_none', path=directory))
                cb.setEnabled(False)
                checks_box.addWidget(cb)
                checks.append(cb)
                return
            for path in files:
                stem, ext = os.path.splitext(os.path.basename(path))
                label = tr(stem) if stem in TRANSLATIONS else stem
                cb = QCheckBox(f"{label}  [{ext[1:].upper()}]")
                cb.setChecked(ext.lower() != '.csv')
                cb.setProperty('path', path)
                checks_box.addWidget(cb)
                checks.append(cb)

        def browse():
            directory = QFileDialog.getExistingDirectory(dialog, tr('select_examples_dir'), self.example_dir)
            if directory:
                self.example_dir = directory
                path_label.setText(directory)
                fill(directory)

        browse_btn.clicked.connect(browse)
        fill(self.example_dir)

        buttons = QDialogButtonBox(QDialogButtonBox_Ok | QDialogButtonBox_Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if exec_dialog(dialog):
            paths = [cb.property('path') for cb in checks if cb.isEnabled() and cb.isChecked()]
            self.load_example_files(paths)

    def load_example_files(self, paths):
        loaded, errors = [], []
        for path in paths:
            stem, ext = os.path.splitext(os.path.basename(path))
            try:
                if ext.lower() == '.csv':
                    uri = f"file:///{path}?delimiter=,&xField=x&yField=y&crs=EPSG:32633&detectTypes=yes"
                    layer = QgsVectorLayer(uri, stem, 'delimitedtext')
                else:
                    layer = QgsVectorLayer(path, stem, 'ogr')
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    loaded.append(layer)
                else:
                    errors.append(f"{os.path.basename(path)}: invalid layer")
            except Exception as e:
                errors.append(f"{os.path.basename(path)}: {e}")
        if loaded:
            self._update_ml_layers()
            for layer in loaded:
                if is_point_layer(layer):
                    self.layer_combo.setLayer(layer)
                    break
            self._notify(tr_format('examples_loaded', n=len(loaded)), Qgis_Success, 5)
        if errors:
            self._warn(tr_format('examples_errors', errors="\n".join(errors)))
        return loaded

    def _show_tutorial(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("GeoArchaeo Tutorial")
        dialog.setMinimumSize(760, 560)
        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(get_tutorial_html(get_language()))
        layout.addWidget(browser)
        row = QHBoxLayout()
        open_btn = QPushButton(tr('open_in_browser'))
        open_btn.clicked.connect(lambda: self._open_tutorial_in_browser(get_language()))
        row.addWidget(open_btn)
        close_btn = QPushButton(tr2("Chiudi", "Close"))
        close_btn.clicked.connect(dialog.accept)
        row.addWidget(close_btn)
        layout.addLayout(row)
        exec_dialog(dialog)

    def _open_tutorial_in_browser(self, lang):
        path = os.path.join(self.temp_dir, f'geoarchaeo_tutorial_{lang}.html')
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(get_tutorial_html(lang))
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    # ==================================================================
    # Pulizia
    # ==================================================================
    def cleanup(self):
        """Chiamato dal plugin allo scaricamento."""
        for signal in self._project_connections:
            try:
                signal.disconnect(self._update_ml_layers)
            except (TypeError, RuntimeError):
                continue    # gia' disconnesso
        self._project_connections = []
        if self.analysis_thread is not None and self.analysis_thread.isRunning():
            self.analysis_thread.cancel()
            self.analysis_thread.wait(5000)
