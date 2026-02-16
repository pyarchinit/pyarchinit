"""
Interfaccia dock widget principale
Compatible with QGIS 3.x (Qt5) and QGIS 4.x (Qt6)
"""

from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QLabel, QTextEdit, QFileDialog,
    QProgressBar, QGroupBox, QCheckBox, QListWidget,
    QMessageBox, QSlider, QListWidgetItem, QTextBrowser,
    QDialog, QDialogButtonBox, QToolBar, QAction, QMenu
)
from qgis.PyQt.QtCore import QThread, pyqtSignal, QTimer, QUrl
from qgis.PyQt.QtGui import QIcon, QDesktopServices

# Import i18n module
from ..i18n import tr, tr_format, get_language, set_language

# QWebEngineView is optional - fallback to QTextBrowser if not available
WEBENGINE_AVAILABLE = False
try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    QWebEngineView = None

from qgis.core import (
    QgsMessageLog, Qgis, QgsMapLayerProxyModel,
    QgsFieldProxyModel, QgsApplication, QgsTask,
    QgsRasterLayer, QgsProject, QgsRasterFileWriter,
    QgsRasterPipe, QgsRasterProjector, QgsPointXY,
    QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
    QgsMarkerSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer,
    QgsCoordinateReferenceSystem
)
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox

from ..compat import (
    Qt_UserRole, QVariant_Int, QVariant_Double, QVariant_String,
    Qgis_Info, Qgis_Warning, Qgis_Critical, Qgis_Success
)
import tempfile
import os
import json
import numpy as np
from datetime import datetime


class AnalysisThread(QThread):
    """Thread per analisi pesanti - versione robusta"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, engine, method, params):
        super().__init__()
        self.engine = engine
        self.method = method
        self.params = params
        self._is_cancelled = False

    def cancel(self):
        """Request thread cancellation"""
        self._is_cancelled = True

    def run(self):
        """Esegue analisi nel thread con protezione massima"""
        import traceback
        import sys
        import os
        from datetime import datetime

        # File logging
        log_file = os.path.expanduser("~/Desktop/geoarchaeo_kriging_log.txt")
        def log(msg):
            try:
                with open(log_file, 'a') as f:
                    f.write(f"[THREAD {datetime.now().strftime('%H:%M:%S.%f')}] {msg}\n")
                    f.flush()
            except:
                pass

        log(f"="*60)
        log(f"THREAD START: method={self.method}")

        result = None
        try:
            # Log start
            QgsMessageLog.logMessage(
                f"Starting analysis: {self.method}",
                'GeoArchaeo', Qgis_Info
            )
            log("QgsMessageLog OK")

            if self._is_cancelled:
                log("Cancelled before start")
                self.error.emit("Analysis cancelled")
                return

            if self.method == 'variogram':
                log("Calling calculate_variogram...")
                result = self.engine.calculate_variogram(
                    self.params['points'],
                    self.params['values'],
                    self.params['max_dist'],
                    self.params['model_type']
                )
                log("calculate_variogram returned OK")
            elif self.method == 'kriging':
                log("Calling ordinary_kriging...")
                log(f"  points shape: {self.params['points'].shape}")
                log(f"  values shape: {self.params['values'].shape}")
                log(f"  pixel_size: {self.params['pixel_size']}")
                result = self.engine.ordinary_kriging(
                    self.params['points'],
                    self.params['values'],
                    self.params['extent'],
                    self.params['pixel_size'],
                    self.params['variogram_params']
                )
                log("ordinary_kriging returned OK")
                log(f"  result keys: {result.keys() if result else 'None'}")
            elif self.method == 'ml':
                log("Calling ml_pattern_recognition...")
                result = self.engine.ml_pattern_recognition(
                    self.params['layers_data'],
                    self.params['method']
                )
                log("ml_pattern_recognition returned OK")
            else:
                raise ValueError(f"Metodo sconosciuto: {self.method}")

            if self._is_cancelled:
                log("Cancelled after computation")
                self.error.emit("Analysis cancelled")
                return

            log("About to emit finished signal...")
            # Log success
            QgsMessageLog.logMessage(
                f"Analysis completed: {self.method}",
                'GeoArchaeo', Qgis_Info
            )

            log("Emitting finished signal now...")
            self.finished.emit(result)
            log("Finished signal emitted OK")

        except MemoryError:
            log("MEMORY ERROR!")
            error_msg = "Memoria insufficiente. Prova con una risoluzione maggiore."
            QgsMessageLog.logMessage(error_msg, 'GeoArchaeo', Qgis_Critical)
            self.error.emit(error_msg)

        except Exception as e:
            log(f"EXCEPTION: {e}")
            error_msg = f"Error: {str(e)}"
            full_traceback = traceback.format_exc()
            log(full_traceback)
            QgsMessageLog.logMessage(
                f"Analysis error: {full_traceback}",
                'GeoArchaeo', Qgis_Critical
            )
            self.error.emit(error_msg)

        except:
            # Catch absolutely everything including SystemExit, KeyboardInterrupt
            error_msg = "Critical unhandled error"
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                error_msg = f"Critical error: {exc_info[1]}"
            QgsMessageLog.logMessage(error_msg, 'GeoArchaeo', Qgis_Critical)
            self.error.emit(error_msg)


class GeoArchaeoDockWidget(QDockWidget):
    """Widget principale del plugin"""

    # Default path for example data
    EXAMPLE_DATA_PATH = os.path.expanduser("~/Desktop/GeoArchaeo_TestData")

    def __init__(self, parent=None):
        super().__init__("GeoArchaeo Analysis", parent)

        # Widget principale
        widget = QWidget()
        self.setWidget(widget)

        # Layout principale
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Toolbar con lingua e dati esempio
        self._create_toolbar(layout)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Crea engine
        from ..core.geostat_engine import GeostatEngine
        self.engine = GeostatEngine()

        # Thread analisi
        self.analysis_thread = None

        # Risultati correnti
        self.current_results = {}

        # Crea tabs
        self._create_data_tab()
        self._create_variogram_tab()
        self._create_kriging_tab()
        self._create_ml_tab()
        self._create_sampling_tab()
        self._create_report_tab()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Tab name to index mapping
        self._tab_indices = {
            'data': 0, 'dati': 0,
            'variogram': 1, 'variogramma': 1,
            'kriging': 2,
            'ml': 3,
            'sampling': 4, 'campionamento': 4,
            'report': 5
        }

    def switch_to_tab(self, tab_name):
        """Switch to a specific tab by name"""
        tab_name_lower = tab_name.lower()
        if tab_name_lower in self._tab_indices:
            self.tabs.setCurrentIndex(self._tab_indices[tab_name_lower])
        else:
            QgsMessageLog.logMessage(
                f"Tab sconosciuto: {tab_name}",
                'GeoArchaeo', Qgis_Warning
            )

    def generate_full_report(self):
        """Generate full report - called from plugin menu"""
        self.switch_to_tab('report')
        # TODO: Could auto-trigger report generation here

    def _create_toolbar(self, parent_layout):
        """Create toolbar with language switcher and example data loader"""
        toolbar_layout = QHBoxLayout()

        # Load Examples button
        self.load_examples_btn = QPushButton(tr('load_examples'))
        self.load_examples_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 5px 10px; "
            "border-radius: 3px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.load_examples_btn.clicked.connect(self._show_load_examples_dialog)
        toolbar_layout.addWidget(self.load_examples_btn)

        # Tutorial button
        self.tutorial_btn = QPushButton(tr('show_tutorial'))
        self.tutorial_btn.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; padding: 5px 10px; "
            "border-radius: 3px; }"
            "QPushButton:hover { background-color: #1976D2; }"
        )
        self.tutorial_btn.clicked.connect(self._show_tutorial)
        toolbar_layout.addWidget(self.tutorial_btn)

        toolbar_layout.addStretch()

        # Language selector
        toolbar_layout.addWidget(QLabel(tr('language') + ":"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Italiano", "it")
        self.lang_combo.addItem("English", "en")
        # Set current language
        current_lang = get_language()
        index = 0 if current_lang == 'it' else 1
        self.lang_combo.setCurrentIndex(index)
        self.lang_combo.currentIndexChanged.connect(self._change_language)
        toolbar_layout.addWidget(self.lang_combo)

        parent_layout.addLayout(toolbar_layout)

    def _create_web_view(self):
        """Create web view widget with fallback for systems without QtWebEngine"""
        if WEBENGINE_AVAILABLE:
            return QWebEngineView()
        else:
            # Fallback to QTextBrowser
            browser = QTextBrowser()
            browser.setOpenExternalLinks(True)
            return browser

    def _set_web_content(self, widget, html_content=None, url=None):
        """Set content on web view widget (works with both QWebEngineView and QTextBrowser)"""
        if WEBENGINE_AVAILABLE and isinstance(widget, QWebEngineView):
            if url:
                widget.setUrl(url)
            elif html_content:
                widget.setHtml(html_content)
        else:
            if html_content:
                widget.setHtml(html_content)
            elif url:
                # QTextBrowser can't load URLs, show message
                widget.setHtml(f"<p>Grafico salvato. <a href='{url.toString()}'>Apri nel browser</a></p>")

    def _create_data_tab(self):
        """Tab gestione dati"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info box
        self.data_info_label = QLabel(tr('data_title') + "<br>" + tr('data_desc'))
        self.data_info_label.setWordWrap(True)
        self.data_info_label.setStyleSheet("QLabel { background-color: #e3f2fd; color: #1a237e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.data_info_label)
        
        # Selezione layer
        self.data_group = QGroupBox(tr('data_selection'))
        group_layout = QVBoxLayout()

        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.point_layer_label = QLabel(tr('point_layer'))
        group_layout.addWidget(self.point_layer_label)
        group_layout.addWidget(self.layer_combo)

        self.field_combo = QgsFieldComboBox()
        self.field_combo.setFilters(QgsFieldProxyModel.Numeric)
        self.value_field_label = QLabel(tr('value_field'))
        group_layout.addWidget(self.value_field_label)
        group_layout.addWidget(self.field_combo)

        self.layer_combo.layerChanged.connect(self.field_combo.setLayer)

        self.data_group.setLayout(group_layout)
        layout.addWidget(self.data_group)

        # Statistiche
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        self.stats_label = QLabel(tr('statistics'))
        layout.addWidget(self.stats_label)
        layout.addWidget(self.stats_text)

        # Pulsante analisi esplorativa
        self.calc_stats_btn = QPushButton(tr('calc_statistics'))
        self.calc_stats_btn.clicked.connect(self._run_eda)
        layout.addWidget(self.calc_stats_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, tr('tab_data'))
        
    def _create_variogram_tab(self):
        """Tab variogramma"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info box
        self.variogram_info_label = QLabel(tr('variogram_title') + "<br>" + tr('variogram_desc'))
        self.variogram_info_label.setWordWrap(True)
        self.variogram_info_label.setStyleSheet("QLabel { background-color: #e3f2fd; color: #1a237e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.variogram_info_label)
        
        # Parametri
        self.variogram_params_group = QGroupBox(tr('variogram_params'))
        params_layout = QVBoxLayout()

        # Distanza massima
        h_layout = QHBoxLayout()
        self.max_dist_label = QLabel(tr('max_distance'))
        h_layout.addWidget(self.max_dist_label)
        self.max_dist_spin = QSpinBox()
        self.max_dist_spin.setRange(10, 10000)
        self.max_dist_spin.setValue(100)
        self.max_dist_spin.setSuffix(" m")
        h_layout.addWidget(self.max_dist_spin)
        params_layout.addLayout(h_layout)

        # Modello
        h_layout = QHBoxLayout()
        self.model_label = QLabel(tr('theoretical_model'))
        h_layout.addWidget(self.model_label)
        self.model_combo = QComboBox()
        self.model_combo.addItems(['spherical', 'exponential', 'gaussian', 'matern'])
        h_layout.addWidget(self.model_combo)
        params_layout.addLayout(h_layout)

        # Parametri avanzati
        self.advanced_group = QGroupBox(tr('advanced_params'))
        advanced_layout = QVBoxLayout()

        # Nugget
        h_layout = QHBoxLayout()
        self.nugget_label = QLabel(tr('nugget'))
        h_layout.addWidget(self.nugget_label)
        self.nugget_spin = QDoubleSpinBox()
        self.nugget_spin.setRange(0, 1000)
        self.nugget_spin.setValue(0)
        self.nugget_spin.setSpecialValueText("Auto")
        h_layout.addWidget(self.nugget_spin)
        advanced_layout.addLayout(h_layout)

        # Sill
        h_layout = QHBoxLayout()
        self.sill_label = QLabel(tr('sill'))
        h_layout.addWidget(self.sill_label)
        self.sill_spin = QDoubleSpinBox()
        self.sill_spin.setRange(0, 10000)
        self.sill_spin.setValue(0)
        self.sill_spin.setSpecialValueText("Auto")
        h_layout.addWidget(self.sill_spin)
        advanced_layout.addLayout(h_layout)

        # Range
        h_layout = QHBoxLayout()
        self.range_label = QLabel(tr('range'))
        h_layout.addWidget(self.range_label)
        self.range_spin = QDoubleSpinBox()
        self.range_spin.setRange(0, 10000)
        self.range_spin.setValue(0)
        self.range_spin.setSpecialValueText("Auto")
        h_layout.addWidget(self.range_spin)
        advanced_layout.addLayout(h_layout)

        self.advanced_group.setLayout(advanced_layout)
        params_layout.addWidget(self.advanced_group)

        # Anisotropia
        self.anisotropy_check = QCheckBox(tr('anisotropy_check'))
        params_layout.addWidget(self.anisotropy_check)
        
        self.variogram_params_group.setLayout(params_layout)
        layout.addWidget(self.variogram_params_group)

        # Pulsante calcolo
        self.calc_variogram_btn = QPushButton(tr('calc_variogram'))
        self.calc_variogram_btn.clicked.connect(self._calculate_variogram)
        layout.addWidget(self.calc_variogram_btn)

        # Visualizzazione Plotly
        self.variogram_view = self._create_web_view()
        self.variogram_view.setMinimumHeight(300)
        self.variogram_view.setHtml("<h3>Variogram - Waiting...</h3>")
        layout.addWidget(self.variogram_view)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, tr('tab_variogram'))
        
    def _create_kriging_tab(self):
        """Tab kriging"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info box
        self.kriging_info_label = QLabel(tr('kriging_title') + "<br>" + tr('kriging_desc'))
        self.kriging_info_label.setWordWrap(True)
        self.kriging_info_label.setStyleSheet("QLabel { background-color: #e3f2fd; color: #1a237e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.kriging_info_label)
        
        # Parametri kriging
        self.kriging_params_group = QGroupBox(tr('kriging_params'))
        params_layout = QVBoxLayout()

        # Tipo kriging
        h_layout = QHBoxLayout()
        self.kriging_type_label = QLabel(tr('kriging_type'))
        h_layout.addWidget(self.kriging_type_label)
        self.kriging_type = QComboBox()
        self.kriging_type.addItems(['Ordinary Kriging', 'Co-Kriging', 'Spatio-Temporal'])
        h_layout.addWidget(self.kriging_type)
        params_layout.addLayout(h_layout)

        # Risoluzione
        h_layout = QHBoxLayout()
        self.resolution_label = QLabel(tr('grid_resolution'))
        h_layout.addWidget(self.resolution_label)
        self.resolution_spin = QDoubleSpinBox()
        self.resolution_spin.setRange(0.1, 100)
        self.resolution_spin.setValue(5)
        self.resolution_spin.setSuffix(" m")
        h_layout.addWidget(self.resolution_spin)
        params_layout.addLayout(h_layout)

        # Usa variogramma calcolato
        self.use_variogram = QCheckBox(tr('use_variogram'))
        self.use_variogram.setChecked(True)
        params_layout.addWidget(self.use_variogram)

        self.kriging_params_group.setLayout(params_layout)
        layout.addWidget(self.kriging_params_group)

        # Pulsante esecuzione
        self.run_kriging_btn = QPushButton(tr('run_kriging'))
        self.run_kriging_btn.clicked.connect(self._run_kriging)
        layout.addWidget(self.run_kriging_btn)

        # Visualizzazione risultati
        self.kriging_view = self._create_web_view()
        self.kriging_view.setMinimumHeight(400)
        self.kriging_view.setHtml("<h3>Kriging - Waiting...</h3>")
        layout.addWidget(self.kriging_view)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, tr('tab_kriging'))
        
    def _create_ml_tab(self):
        """Tab Machine Learning"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info box
        self.ml_info_label = QLabel(tr('ml_title') + "<br>" + tr('ml_desc'))
        self.ml_info_label.setWordWrap(True)
        self.ml_info_label.setStyleSheet("QLabel { background-color: #e3f2fd; color: #1a237e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.ml_info_label)
        
        # Selezione layer
        self.ml_data_group = QGroupBox("ML Data")
        group_layout = QVBoxLayout()

        # Lista layer ML
        self.ml_layers = QListWidget()
        self.ml_layers.setSelectionMode(QListWidget.MultiSelection)
        self._update_ml_layers()
        self.ml_layers_label = QLabel(tr('ml_layers_select'))
        group_layout.addWidget(self.ml_layers_label)
        group_layout.addWidget(self.ml_layers)

        # Aggiorna quando cambiano i layer
        QgsProject.instance().layersAdded.connect(self._update_ml_layers)
        QgsProject.instance().layersRemoved.connect(self._update_ml_layers)

        # Metodo ML
        h_layout = QHBoxLayout()
        self.ml_method_label = QLabel(tr('ml_method'))
        h_layout.addWidget(self.ml_method_label)
        self.ml_method = QComboBox()
        self.ml_method.addItems([
            'K-Means (clustering)',
            'DBSCAN (density)',
            'Random Forest (classification)',
            'Isolation Forest (anomalies)'
        ])
        h_layout.addWidget(self.ml_method)
        group_layout.addLayout(h_layout)

        self.ml_data_group.setLayout(group_layout)
        layout.addWidget(self.ml_data_group)

        # Pulsante analisi
        self.run_ml_btn = QPushButton(tr('run_ml'))
        self.run_ml_btn.clicked.connect(self._run_ml)
        layout.addWidget(self.run_ml_btn)

        # Risultati
        self.ml_view = self._create_web_view()
        self.ml_view.setMinimumHeight(350)
        self.ml_view.setHtml("<h3>Machine Learning - Waiting...</h3>")
        layout.addWidget(self.ml_view)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, tr('tab_ml'))
        
    def _create_sampling_tab(self):
        """Tab design campionamento"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Info box
        self.sampling_info_label = QLabel(tr('sampling_title') + "<br>" + tr('sampling_desc'))
        self.sampling_info_label.setWordWrap(True)
        self.sampling_info_label.setStyleSheet("QLabel { background-color: #e3f2fd; color: #1a237e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.sampling_info_label)
        
        # Parametri
        self.sampling_params_group = QGroupBox(tr('sampling_params'))
        group_layout = QVBoxLayout()

        # Punti esistenti
        h_layout = QHBoxLayout()
        self.existing_points_label = QLabel(tr('existing_points'))
        h_layout.addWidget(self.existing_points_label)
        self.existing_combo = QgsMapLayerComboBox()
        self.existing_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        h_layout.addWidget(self.existing_combo)
        group_layout.addLayout(h_layout)

        # Area studio
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Study area (optional):"))
        self.boundary_combo = QgsMapLayerComboBox()
        self.boundary_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.boundary_combo.setAllowEmptyLayer(True)
        h_layout.addWidget(self.boundary_combo)
        group_layout.addLayout(h_layout)

        # Numero punti
        h_layout = QHBoxLayout()
        self.new_points_label = QLabel(tr('new_points'))
        h_layout.addWidget(self.new_points_label)
        self.n_points_spin = QSpinBox()
        self.n_points_spin.setRange(1, 100)
        self.n_points_spin.setValue(10)
        h_layout.addWidget(self.n_points_spin)
        group_layout.addLayout(h_layout)

        # Metodo
        h_layout = QHBoxLayout()
        self.sampling_method_label = QLabel(tr('sampling_method'))
        h_layout.addWidget(self.sampling_method_label)
        self.sampling_combo = QComboBox()
        self.sampling_combo.addItems([
            'Random',
            'Regular (grid)',
            'Stratified',
            'Maximin',
            'LHS (Latin Hypercube)'
        ])
        h_layout.addWidget(self.sampling_combo)
        group_layout.addLayout(h_layout)

        self.sampling_params_group.setLayout(group_layout)
        layout.addWidget(self.sampling_params_group)

        # Pulsante calcolo
        self.calc_optimal_btn = QPushButton(tr('calc_optimal'))
        self.calc_optimal_btn.clicked.connect(self._run_sampling_design)
        layout.addWidget(self.calc_optimal_btn)

        # Risultati
        self.sampling_text = QTextEdit()
        self.sampling_text.setReadOnly(True)
        layout.addWidget(QLabel("Suggested new points:"))
        layout.addWidget(self.sampling_text)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, tr('tab_sampling'))
        
    def _create_report_tab(self):
        """Tab generazione report"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Info box
        self.report_info_label = QLabel(tr('report_title') + "<br>" + tr('report_desc'))
        self.report_info_label.setWordWrap(True)
        self.report_info_label.setStyleSheet("QLabel { background-color: #e3f2fd; color: #1a237e; padding: 10px; border-radius: 5px; }")
        layout.addWidget(self.report_info_label)
        
        # Opzioni report
        self.report_sections_group = QGroupBox(tr('report_sections'))
        group_layout = QVBoxLayout()

        self.report_checks = {
            'stats': QCheckBox('Descriptive Statistics'),
            'variogram': QCheckBox('Variogram Analysis'),
            'kriging': QCheckBox('Kriging Results'),
            'ml': QCheckBox('ML Patterns'),
            'sampling': QCheckBox('Sampling Recommendations')
        }

        for check in self.report_checks.values():
            check.setChecked(True)
            group_layout.addWidget(check)

        self.report_sections_group.setLayout(group_layout)
        layout.addWidget(self.report_sections_group)

        # Pulsanti export
        btn_layout = QHBoxLayout()

        self.generate_html_btn = QPushButton(tr('generate_report'))
        self.generate_html_btn.clicked.connect(lambda: self._generate_report('html'))
        btn_layout.addWidget(self.generate_html_btn)

        self.generate_pdf_btn = QPushButton("PDF Report")
        self.generate_pdf_btn.clicked.connect(lambda: self._generate_report('pdf'))
        btn_layout.addWidget(self.generate_pdf_btn)

        layout.addLayout(btn_layout)
        
        # Preview
        self.report_view = self._create_web_view()
        layout.addWidget(self.report_view)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, tr('tab_report'))
        
    def _update_ml_layers(self):
        """Aggiorna lista layer per ML"""
        self.ml_layers.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == 0:  # Vector layer
                item = QListWidgetItem(layer.name())
                item.setData(Qt_UserRole, layer)
                self.ml_layers.addItem(item)
                
    def _run_eda(self):
        """Esegue analisi esplorativa"""
        layer = self.layer_combo.currentLayer()
        field = self.field_combo.currentField()
        
        if not layer or not field:
            QMessageBox.warning(self, tr('warning'), tr('select_layer_field'))
            return
        
        # Estrai valori
        values = []
        for feature in layer.getFeatures():
            if feature[field] is not None:
                values.append(float(feature[field]))
        
        if not values:
            QMessageBox.warning(self, tr('warning'), tr('no_values_found'))
            return
        
        values = np.array(values)
        
        # Calcola statistiche
        try:
            from scipy import stats as scipy_stats
            skewness = scipy_stats.skew(values)
            kurtosis = scipy_stats.kurtosis(values)
        except:
            skewness = 0.0
            kurtosis = 0.0
            
        stats_text = f"""
Numero valori: {len(values)}
Min: {np.min(values):.3f}
Max: {np.max(values):.3f}
Media: {np.mean(values):.3f}
Mediana: {np.median(values):.3f}
Dev. Standard: {np.std(values):.3f}
Q1: {np.percentile(values, 25):.3f}
Q3: {np.percentile(values, 75):.3f}
Skewness: {skewness:.3f}
Kurtosis: {kurtosis:.3f}

Interpretazione:
- Skewness > 0: distribuzione asimmetrica a destra
- Skewness < 0: distribuzione asimmetrica a sinistra
- Kurtosis > 0: distribuzione più appuntita del normale
- Kurtosis < 0: distribuzione più piatta del normale
"""
        self.stats_text.setText(stats_text)
        
    def _calculate_variogram(self):
        """Calcola variogramma"""
        layer = self.layer_combo.currentLayer()
        field = self.field_combo.currentField()
        
        if not layer or not field:
            QMessageBox.warning(self, tr('warning'), tr('select_layer_field'))
            return
        
        # Estrai punti e valori
        points = []
        values = []
        
        for feature in layer.getFeatures():
            if feature[field] is not None:
                geom = feature.geometry()
                if geom and not geom.isEmpty():
                    point = geom.asPoint()
                    points.append([point.x(), point.y()])
                    values.append(float(feature[field]))
        
        if len(points) < 5:
            QMessageBox.warning(self, tr('warning'), tr('min_points'))
            return
        
        # Prepara parametri
        params = {
            'points': np.array(points),
            'values': np.array(values),
            'max_dist': self.max_dist_spin.value(),
            'model_type': self.model_combo.currentText()
        }
        
        # Avvia analisi in thread
        self.progress_bar.setVisible(True)
        self.analysis_thread = AnalysisThread(self.engine, 'variogram', params)
        self.analysis_thread.finished.connect(self._on_variogram_complete)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.start()
        
    def _on_variogram_complete(self, result):
        """Gestisce fine calcolo variogramma"""
        self.progress_bar.setVisible(False)
        self.current_results['variogram'] = result
        
        try:
            # Crea visualizzazione
            fig = self.engine.create_interactive_variogram(result)
            
            # Salva HTML temporaneo
            html_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.html', delete=False,
                dir=tempfile.gettempdir()
            )
            fig.write_html(html_file.name)
            html_file.close()
            
            # Assicura che il file sia leggibile
            os.chmod(html_file.name, 0o644)
            
            # Mostra in webview o apri nel browser
            import webbrowser
            if WEBENGINE_AVAILABLE:
                try:
                    url = QUrl.fromLocalFile(html_file.name)
                    self.variogram_view.setUrl(url)
                except Exception as e:
                    with open(html_file.name, 'r') as f:
                        self.variogram_view.setHtml(f.read())
            else:
                # Senza WebEngine, mostra messaggio e apri nel browser
                self.variogram_view.setHtml(
                    "<h3>Variogramma calcolato!</h3>"
                    "<p>Il grafico interattivo è stato aperto nel browser.</p>"
                )

            # Apri sempre nel browser per visualizzazione interattiva
            webbrowser.open(f'file://{html_file.name}')
            
            # Mostra parametri stimati
            model_params = result.get('model_params', {})
            msg = f"Variogramma calcolato con successo!\n\n"
            msg += f"Parametri stimati:\n"
            msg += f"- Nugget: {model_params.get('nugget', 0):.3f}\n"
            msg += f"- Sill: {model_params.get('sill', 0):.3f}\n"
            msg += f"- Range: {model_params.get('range', 0):.1f} m\n"
            msg += f"- RMSE fit: {result.get('rmse', 0):.3f}\n\n"
            msg += f"Il grafico è stato aperto nel browser."
            
            QMessageBox.information(self, tr('completed'), msg)
            
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Variogram visualization error: {str(e)}",
                'GeoArchaeo', Qgis_Critical
            )
            QMessageBox.critical(self, tr('error'), tr_format('error_visualization', msg=str(e)))
        
    def _run_kriging(self):
        """Esegue kriging"""
        layer = self.layer_combo.currentLayer()
        field = self.field_combo.currentField()

        if not layer or not field:
            QMessageBox.warning(self, tr('warning'), tr('select_layer_field'))
            return

        # Estrai punti e valori
        points = []
        values = []

        for feature in layer.getFeatures():
            if feature[field] is not None:
                geom = feature.geometry()
                if geom and not geom.isEmpty():
                    point = geom.asPoint()
                    points.append([point.x(), point.y()])
                    try:
                        values.append(float(feature[field]))
                    except (ValueError, TypeError):
                        continue  # Salta valori non numerici

        if len(points) < 5:
            QMessageBox.warning(self, tr('warning'), tr('min_points'))
            return

        # Verifica dimensione griglia
        extent = layer.extent()
        pixel_size = self.resolution_spin.value()
        nx = int((extent.xMaximum() - extent.xMinimum()) / pixel_size)
        ny = int((extent.yMaximum() - extent.yMinimum()) / pixel_size)
        total_cells = nx * ny

        if total_cells > 10000:
            reply = QMessageBox.question(
                self, "Griglia grande",
                f"La griglia avrà {nx}x{ny} = {total_cells} celle.\n"
                f"Con {len(points)} punti, il calcolo potrebbe richiedere molto tempo.\n\n"
                f"Suggerimento: aumenta la risoluzione (es. 2.0m invece di 1.0m).\n\n"
                f"Vuoi continuare comunque?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Prepara parametri
        params = {
            'points': np.array(points),
            'values': np.array(values),
            'extent': extent,
            'pixel_size': pixel_size,
            'variogram_params': self.current_results.get('variogram') if self.use_variogram.isChecked() else None
        }

        # Avvia analisi
        self.progress_bar.setVisible(True)
        self.analysis_thread = AnalysisThread(self.engine, 'kriging', params)
        self.analysis_thread.finished.connect(self._on_kriging_complete)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.start()
        
    def _on_kriging_complete(self, result):
        """Gestisce fine kriging"""
        import os
        from datetime import datetime

        log_file = os.path.expanduser("~/Desktop/geoarchaeo_kriging_log.txt")
        def log(msg):
            try:
                with open(log_file, 'a') as f:
                    f.write(f"[COMPLETE {datetime.now().strftime('%H:%M:%S.%f')}] {msg}\n")
                    f.flush()
            except:
                pass

        log("_on_kriging_complete CALLED")
        log(f"Result type: {type(result)}")
        log(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

        self.progress_bar.setVisible(False)
        self.current_results['kriging'] = result

        try:
            log("Creating visualization...")
            # Crea visualizzazione
            try:
                log("Calling create_interactive_kriging_map...")
                fig = self.engine.create_interactive_kriging_map(
                    result['x_grid'],
                    result['y_grid'],
                    result['predictions'],
                    result['variances'],
                    self.analysis_thread.params['points']
                )

                # Salva HTML temporaneo
                html_file = tempfile.NamedTemporaryFile(
                    mode='w', suffix='.html', delete=False,
                    dir=tempfile.gettempdir()
                )
                fig.write_html(html_file.name)
                html_file.close()

                # Assicura che il file sia leggibile
                os.chmod(html_file.name, 0o644)

                # Mostra in webview o apri nel browser
                import webbrowser
                if WEBENGINE_AVAILABLE:
                    try:
                        url = QUrl.fromLocalFile(html_file.name)
                        self.kriging_view.setUrl(url)
                    except Exception:
                        self.kriging_view.setHtml(
                            "<h3>Kriging Complete!</h3>"
                            "<p>Interactive graph opened in browser.</p>"
                        )
                else:
                    self.kriging_view.setHtml(
                        "<h3>Kriging Complete!</h3>"
                        "<p>Interactive graph opened in browser.</p>"
                    )

                webbrowser.open(f'file://{html_file.name}')

            except Exception as viz_error:
                QgsMessageLog.logMessage(
                    f"Kriging visualization error: {str(viz_error)}",
                    'GeoArchaeo', Qgis_Warning
                )

            # Crea anche raster QGIS
            self._create_kriging_raster(result)

            # Show cross-validation metrics
            cv_msg = "Kriging completed successfully!\n\n"
            if 'cv_results' in result and result['cv_results']:
                cv = result['cv_results']
                cv_msg += "Cross-Validation Metrics:\n"
                cv_msg += f"- RMSE: {cv.get('rmse', 0):.3f} (root mean squared error)\n"
                cv_msg += f"- MAE: {cv.get('mae', 0):.3f} (mean absolute error)\n"
                cv_msg += f"- ME: {cv.get('me', 0):.3f} (mean error - bias)\n"
                cv_msg += f"- R²: {cv.get('r2', 0):.3f} (coefficiente determinazione)\n"
                cv_msg += f"- Punti validi: {cv.get('n_valid', 0)}\n\n"

            cv_msg += "Il grafico è stato aperto nel browser.\nUn raster è stato aggiunto alla mappa."

            QMessageBox.information(self, tr('completed'), cv_msg)
                
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Kriging visualization error: {str(e)}",
                'GeoArchaeo', Qgis_Critical
            )
            QMessageBox.critical(self, tr('error'), tr_format('error_visualization', msg=str(e)))
        
    def _run_ml(self):
        """Esegue analisi ML"""
        # Raccogli layer selezionati
        selected_layers = []
        for i in range(self.ml_layers.count()):
            item = self.ml_layers.item(i)
            if item.isSelected():
                layer = item.data(Qt_UserRole)
                selected_layers.append(layer)
        
        if not selected_layers:
            QMessageBox.warning(self, tr('warning'), tr('select_at_least_one_layer'))
            return
        
        # Prepara dati
        layers_data = []
        for layer in selected_layers:
            data = {
                'name': layer.name(),
                'points': [],
                'features': []
            }
            
            # Estrai punti e attributi numerici
            numeric_fields = []
            for field in layer.fields():
                if field.isNumeric():
                    numeric_fields.append(field.name())
            
            for feature in layer.getFeatures():
                geom = feature.geometry()
                if geom and not geom.isEmpty():
                    point = geom.asPoint()
                    data['points'].append([point.x(), point.y()])
                    
                    # Valori attributi
                    feat_values = []
                    for field_name in numeric_fields:
                        val = feature[field_name]
                        feat_values.append(float(val) if val is not None else 0)
                    data['features'].append(feat_values)
            
            if data['points']:
                layers_data.append(data)
        
        if not layers_data:
            QMessageBox.warning(self, tr('warning'), tr('no_valid_data'))
            return
        
        # Prepara parametri
        method_map = {
            # English keys
            'K-Means (clustering)': 'kmeans',
            'DBSCAN (density)': 'dbscan',
            'Random Forest (classification)': 'random_forest',
            'Isolation Forest (anomalies)': 'isolation_forest',
            # Italian keys (for compatibility)
            'K-Means (raggruppamento)': 'kmeans',
            'DBSCAN (cluster densità)': 'dbscan',
            'Random Forest (classificazione)': 'random_forest',
            'Isolation Forest (anomalie)': 'isolation_forest'
        }
        
        params = {
            'layers_data': layers_data,
            'method': method_map[self.ml_method.currentText()]
        }
        
        # Avvia analisi
        self.progress_bar.setVisible(True)
        self.analysis_thread = AnalysisThread(self.engine, 'ml', params)
        self.analysis_thread.finished.connect(self._on_ml_complete)
        self.analysis_thread.error.connect(self._on_analysis_error)
        self.analysis_thread.start()
        
    def _on_ml_complete(self, result):
        """Gestisce fine ML"""
        self.progress_bar.setVisible(False)
        self.current_results['ml'] = result
        
        try:
            # Crea visualizzazione
            method_name = self.ml_method.currentText()
            fig = self.engine.create_ml_visualization(
                result['features'],
                result['labels'],
                method_name
            )
            
            # Salva HTML temporaneo
            html_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.html', delete=False,
                dir=tempfile.gettempdir()
            )
            fig.write_html(html_file.name)
            html_file.close()
            
            # Assicura che il file sia leggibile
            os.chmod(html_file.name, 0o644)
            
            # Mostra in webview o apri nel browser
            import webbrowser
            if WEBENGINE_AVAILABLE:
                try:
                    url = QUrl.fromLocalFile(html_file.name)
                    self.ml_view.setUrl(url)
                except Exception as e:
                    with open(html_file.name, 'r') as f:
                        self.ml_view.setHtml(f.read())
            else:
                self.ml_view.setHtml(
                    "<h3>Pattern Recognition Complete!</h3>"
                    "<p>Interactive graph opened in browser.</p>"
                )

            webbrowser.open(f'file://{html_file.name}')

            # Crea layer con i cluster
            self._create_ml_layer(result)
            
            n_patterns = len(np.unique(result['labels']))
            QMessageBox.information(self, tr('completed'),
                f"Pattern recognition complete!\n\n"
                f"{n_patterns} patterns/clusters found.\n"
                f"Graph opened in browser.\n"
                f"Vector layer created with clusters.")
                
        except Exception as e:
            QgsMessageLog.logMessage(
                f"ML visualization error: {str(e)}",
                'GeoArchaeo', Qgis_Critical
            )
            QMessageBox.critical(self, tr('error'), tr_format('error_visualization', msg=str(e)))
        
    def _run_sampling_design(self):
        """Calcola design campionamento ottimale"""
        existing_layer = self.existing_combo.currentLayer()
        boundary_layer = self.boundary_combo.currentLayer()
        
        if not existing_layer:
            QMessageBox.warning(self, tr('warning'), tr('select_existing_points'))
            return
        
        # Estrai punti esistenti
        existing_points = []
        for feature in existing_layer.getFeatures():
            geom = feature.geometry()
            if geom and not geom.isEmpty():
                point = geom.asPoint()
                existing_points.append([point.x(), point.y()])
        
        if not existing_points:
            QMessageBox.warning(self, tr('warning'), tr('no_points_in_layer'))
            return
        
        existing_points = np.array(existing_points)
        
        # Estrai boundary se fornito
        boundary = None
        if boundary_layer:
            for feature in boundary_layer.getFeatures():
                geom = feature.geometry()
                if geom and not geom.isEmpty():
                    boundary = geom
                    break
        
        # Calcola nuovi punti
        try:
            n_points = self.n_points_spin.value()
            method = self.sampling_combo.currentText().split()[0].lower()
            
            new_points = self.engine.optimal_sampling_design(
                existing_points, boundary, n_points, method
            )
            
            # Show results
            text = f"Calculated {len(new_points)} new points with method {method}\n\n"
            text += "Suggested coordinates:\n"
            for i, point in enumerate(new_points):
                text += f"{i+1}. X: {point[0]:.2f}, Y: {point[1]:.2f}\n"
            
            self.sampling_text.setText(text)
            self.current_results['sampling'] = new_points
            
            # Crea layer vettoriale per i nuovi punti
            self._create_sampling_layer(new_points)
            
            QMessageBox.information(self, tr('completed'),
                f"Sampling design complete!\n\n"
                f"{len(new_points)} new points suggested.\n"
                f"Created layer with yellow stars.")

        except Exception as e:
            QMessageBox.critical(self, tr('error'), str(e))

    def _generate_report(self, format_type):
        """Generate report"""
        sections_to_include = []
        for option, check in self.report_checks.items():
            if check.isChecked():
                sections_to_include.append(option)

        if not sections_to_include:
            QMessageBox.warning(self, tr('warning'), "Select at least one section")
            return
        
        # Genera HTML report
        html_content = self._build_report_html(sections_to_include)
        
        # Mostra preview
        self.report_view.setHtml(html_content)
        
        # Salva file se richiesto
        if format_type == 'html':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salva Report HTML", "", "HTML Files (*.html)"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(html_content)
                QMessageBox.information(self, tr('completed'), f"Report saved to {file_path}")
                
        elif format_type == 'pdf':
            self._export_pdf_report(html_content, sections_to_include)
    
    def _build_report_html(self, sections):
        """Costruisce HTML del report"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>GeoArchaeo Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; margin-top: 30px; }
        .section { margin-bottom: 30px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #3498db; color: white; }
        .timestamp { color: #7f8c8d; font-style: italic; }
    </style>
</head>
<body>
    <h1>GeoArchaeo Analysis Report</h1>
    <p class="timestamp">Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
"""
        
        if 'Statistiche descrittive' in sections and 'stats' in self.current_results:
            stats = self.current_results['stats']
            html += f"""
    <div class="section">
        <h2>Statistiche Descrittive</h2>
        <pre>{self.stats_text.toPlainText()}</pre>
    </div>
"""
        
        if 'Analisi variogramma' in sections and 'variogram' in self.current_results:
            var_result = self.current_results['variogram']
            params = var_result.get('model_params', {})
            html += f"""
    <div class="section">
        <h2>Analisi Variogramma</h2>
        <p>Modello: {var_result.get('model_type', 'N/A')}</p>
        <p>Nugget: {params.get('nugget', 0):.3f}</p>
        <p>Sill: {params.get('sill', 0):.3f}</p>
        <p>Range: {params.get('range', 0):.1f} m</p>
    </div>
"""
        
        if 'Risultati kriging' in sections and 'kriging' in self.current_results:
            kr_result = self.current_results['kriging']
            html += f"""
    <div class="section">
        <h2>Risultati Kriging</h2>
        <p>Risoluzione griglia: {self.resolution_spin.value()} m</p>
        <p>Metodo: {self.kriging_type.currentText()}</p>
"""
            if 'cv_results' in kr_result:
                cv = kr_result['cv_results']
                html += f"""
        <h3>Cross-Validation</h3>
        <p>RMSE: {cv['rmse']:.3f}</p>
        <p>MAE: {cv['mae']:.3f}</p>
        <p>R²: {cv['r2']:.3f}</p>
"""
            html += "</div>"
        
        if 'Pattern ML' in sections and 'ml' in self.current_results:
            ml_result = self.current_results['ml']
            n_patterns = len(np.unique(ml_result['labels']))
            html += f"""
    <div class="section">
        <h2>Pattern Recognition ML</h2>
        <p>Metodo: {self.ml_method.currentText()}</p>
        <p>Pattern identificati: {n_patterns}</p>
    </div>
"""
        
        if 'Raccomandazioni campionamento' in sections and 'sampling' in self.current_results:
            n_points = len(self.current_results['sampling'])
            html += f"""
    <div class="section">
        <h2>Raccomandazioni Campionamento</h2>
        <p>Metodo: {self.sampling_combo.currentText()}</p>
        <p>Nuovi punti suggeriti: {n_points}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def _export_pdf_report(self, html_content, sections):
        """Esporta report in PDF"""
        try:
            # Prima prova con ReportLab se disponibile
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                
                # Richiedi path di salvataggio
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Salva Report PDF", "", "PDF Files (*.pdf)"
                )
                
                if not file_path:
                    return
                
                # Crea documento PDF
                doc = SimpleDocTemplate(file_path, pagesize=A4)
                story = []
                styles = getSampleStyleSheet()
                
                # Titolo
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#2c3e50'),
                    spaceAfter=30
                )
                story.append(Paragraph("GeoArchaeo Analysis Report", title_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Data
                story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Italic']))
                story.append(Spacer(1, 0.5*inch))
                
                # Aggiungi sezioni
                if 'Statistiche descrittive' in sections and 'stats' in self.current_results:
                    story.append(Paragraph("Statistiche Descrittive", styles['Heading2']))
                    stats_text = self.stats_text.toPlainText()
                    for line in stats_text.split('\n'):
                        if line.strip():
                            story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 0.3*inch))
                
                if 'Analisi variogramma' in sections and 'variogram' in self.current_results:
                    story.append(Paragraph("Analisi Variogramma", styles['Heading2']))
                    var_result = self.current_results['variogram']
                    params = var_result.get('model_params', {})
                    
                    var_data = [
                        ['Parametro', 'Valore'],
                        ['Modello', var_result.get('model_type', 'N/A')],
                        ['Nugget', f"{params.get('nugget', 0):.3f}"],
                        ['Sill', f"{params.get('sill', 0):.3f}"],
                        ['Range', f"{params.get('range', 0):.1f} m"]
                    ]
                    
                    var_table = Table(var_data)
                    var_table.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,0), 12),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                        ('GRID', (0,0), (-1,-1), 1, colors.black)
                    ]))
                    story.append(var_table)
                    story.append(Spacer(1, 0.3*inch))
                
                if 'Risultati kriging' in sections and 'kriging' in self.current_results:
                    story.append(Paragraph("Risultati Kriging", styles['Heading2']))
                    kr_result = self.current_results['kriging']
                    
                    story.append(Paragraph(f"Risoluzione griglia: {self.resolution_spin.value()} m", styles['Normal']))
                    story.append(Paragraph(f"Metodo: {self.kriging_type.currentText()}", styles['Normal']))
                    
                    if 'cv_results' in kr_result:
                        cv = kr_result['cv_results']
                        story.append(Spacer(1, 0.2*inch))
                        story.append(Paragraph("Cross-Validation", styles['Heading3']))
                        
                        cv_data = [
                            ['Metrica', 'Valore'],
                            ['RMSE', f"{cv['rmse']:.3f}"],
                            ['MAE', f"{cv['mae']:.3f}"],
                            ['R²', f"{cv['r2']:.3f}"]
                        ]
                        
                        cv_table = Table(cv_data)
                        cv_table.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
                            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                            ('GRID', (0,0), (-1,-1), 1, colors.black)
                        ]))
                        story.append(cv_table)
                    story.append(Spacer(1, 0.3*inch))
                
                if 'Pattern ML' in sections and 'ml' in self.current_results:
                    story.append(Paragraph("Pattern Recognition ML", styles['Heading2']))
                    ml_result = self.current_results['ml']
                    n_patterns = len(np.unique(ml_result['labels']))
                    
                    story.append(Paragraph(f"Metodo: {self.ml_method.currentText()}", styles['Normal']))
                    story.append(Paragraph(f"Pattern identificati: {n_patterns}", styles['Normal']))
                    story.append(Spacer(1, 0.3*inch))
                
                if 'Raccomandazioni campionamento' in sections and 'sampling' in self.current_results:
                    story.append(Paragraph("Raccomandazioni Campionamento", styles['Heading2']))
                    n_points = len(self.current_results['sampling'])
                    
                    story.append(Paragraph(f"Metodo: {self.sampling_combo.currentText()}", styles['Normal']))
                    story.append(Paragraph(f"Nuovi punti suggeriti: {n_points}", styles['Normal']))
                    story.append(Spacer(1, 0.3*inch))
                
                # Genera PDF
                doc.build(story)
                QMessageBox.information(self, tr('completed'), f"PDF report saved to:\n{file_path}")
                
            except ImportError:
                # Fallback: usa QPrinter se ReportLab non è disponibile
                self._export_pdf_with_printer(html_content)
                
        except Exception as e:
            QgsMessageLog.logMessage(
                f"PDF export error: {str(e)}",
                'GeoArchaeo', Qgis_Critical
            )
            # Fallback finale
            self._export_pdf_with_printer(html_content)
    
    def _export_pdf_with_printer(self, html_content):
        """Export PDF usando QPrinter come fallback"""
        try:
            from qgis.PyQt.QtPrintSupport import QPrinter
            from qgis.PyQt.QtGui import QTextDocument
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salva Report PDF", "", "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            
            doc = QTextDocument()
            doc.setHtml(html_content)
            doc.print_(printer)
            
            QMessageBox.information(self, tr('completed'), f"PDF report saved to:\n{file_path}")

        except Exception as e:
            QMessageBox.warning(self, tr('warning'),
                f"Cannot create PDF.\n"
                f"Use 'Save as HTML' and print from browser.\n"
                f"Error: {str(e)}")
    
    def _on_analysis_error(self, error_msg):
        """Handle analysis errors"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, tr('error'), tr_format('error_analysis', msg=error_msg))
        
    def _create_kriging_raster(self, result):
        """Crea raster QGIS dal risultato kriging"""
        try:
            # Estrai dati
            predictions = result['predictions'].copy()  # Copia per non modificare originale
            x_grid = result['x_grid']
            y_grid = result['y_grid']

            # Crea file GeoTIFF temporaneo
            from osgeo import gdal, osr

            temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
            temp_file.close()

            # Parametri raster
            ny, nx = predictions.shape
            # x_grid e y_grid sono array 1D, non 2D
            pixel_size_x = float(x_grid[1] - x_grid[0]) if len(x_grid) > 1 else 1.0
            pixel_size_y = float(y_grid[1] - y_grid[0]) if len(y_grid) > 1 else 1.0

            # Sostituisci NaN con nodata value prima di scrivere
            nodata_value = -9999.0
            predictions = np.where(np.isnan(predictions), nodata_value, predictions)

            # Inverti l'array lungo l'asse y (GDAL ha origine in alto a sinistra)
            predictions = np.flipud(predictions)

            # Crea raster GDAL
            driver = gdal.GetDriverByName('GTiff')
            dataset = driver.Create(temp_file.name, nx, ny, 1, gdal.GDT_Float32)

            if dataset is None:
                raise RuntimeError("Impossibile creare il file raster")

            # Imposta georeferenziazione
            geotransform = [
                float(x_grid.min() - pixel_size_x/2),  # x origine
                pixel_size_x,                           # pixel size x
                0,                                      # rotazione x
                float(y_grid.max() + pixel_size_y/2),  # y origine
                0,                                      # rotazione y
                -pixel_size_y                           # pixel size y (negativo)
            ]
            dataset.SetGeoTransform(geotransform)

            # Imposta proiezione dal layer corrente
            layer = self.layer_combo.currentLayer()
            if layer and layer.crs():
                srs = osr.SpatialReference()
                srs.ImportFromWkt(layer.crs().toWkt())
                dataset.SetProjection(srs.ExportToWkt())
            else:
                # Default UTM 33N
                srs = osr.SpatialReference()
                srs.ImportFromEPSG(32633)
                dataset.SetProjection(srs.ExportToWkt())

            # Scrivi dati (assicurati che sia float32)
            band = dataset.GetRasterBand(1)
            band.WriteArray(predictions.astype(np.float32))
            band.SetNoDataValue(nodata_value)
            band.FlushCache()

            # Chiudi dataset esplicitamente
            band = None
            dataset = None

            # Forza garbage collection per rilasciare risorse GDAL
            import gc
            gc.collect()

            # Carica come layer QGIS
            layer_name = tr('kriging_result_layer')
            raster_layer = QgsRasterLayer(temp_file.name, layer_name, "gdal")

            if raster_layer.isValid():
                # Applica stile pseudocolor con rampa di colori
                self._apply_kriging_color_style(raster_layer, result['predictions'])

                QgsProject.instance().addMapLayer(raster_layer)
                QgsMessageLog.logMessage(
                    tr('raster_created'),
                    'GeoArchaeo', Qgis_Info
                )
            else:
                QgsMessageLog.logMessage(
                    "Kriging raster load error",
                    'GeoArchaeo', Qgis_Critical
                )

        except Exception as e:
            import traceback
            QgsMessageLog.logMessage(
                f"Raster creation error: {str(e)}\n{traceback.format_exc()}",
                'GeoArchaeo', Qgis_Critical
            )

    def _apply_kriging_color_style(self, raster_layer, predictions):
        """Applica stile pseudocolor con rampa di colori al raster kriging"""
        try:
            from qgis.core import (QgsRasterShader, QgsColorRampShader,
                                   QgsSingleBandPseudoColorRenderer)

            # Calcola min/max escludendo nodata
            valid_data = predictions[~np.isnan(predictions)]
            if len(valid_data) == 0:
                return

            min_val = float(np.min(valid_data))
            max_val = float(np.max(valid_data))

            # Crea rampa di colori (tipo Spectral - da blu a rosso)
            color_ramp_items = []
            # 5 classi con interpolazione
            colors = [
                (min_val, QColor(49, 54, 149)),                                    # Blu scuro (basso)
                (min_val + (max_val - min_val) * 0.25, QColor(116, 173, 209)),    # Blu chiaro
                (min_val + (max_val - min_val) * 0.50, QColor(255, 255, 191)),    # Giallo (medio)
                (min_val + (max_val - min_val) * 0.75, QColor(244, 109, 67)),     # Arancione
                (max_val, QColor(165, 0, 38))                                      # Rosso scuro (alto)
            ]

            for value, color in colors:
                item = QgsColorRampShader.ColorRampItem(value, color, f'{value:.2f}')
                color_ramp_items.append(item)

            # Crea shader
            shader = QgsRasterShader()
            color_ramp = QgsColorRampShader()
            color_ramp.setColorRampType(QgsColorRampShader.Interpolated)
            color_ramp.setColorRampItemList(color_ramp_items)
            shader.setRasterShaderFunction(color_ramp)

            # Applica renderer
            renderer = QgsSingleBandPseudoColorRenderer(
                raster_layer.dataProvider(),
                1,  # banda 1
                shader
            )
            raster_layer.setRenderer(renderer)

            # Trigger refresh
            raster_layer.triggerRepaint()

        except Exception as e:
            QgsMessageLog.logMessage(
                f"Color style error: {str(e)}",
                'GeoArchaeo', Qgis_Warning
            )

    def _create_sampling_layer(self, new_points):
        """Create vector layer for suggested sampling points"""
        try:
            # Get CRS from current layer
            current_layer = self.existing_combo.currentLayer()
            if current_layer:
                crs = current_layer.crs()
            else:
                crs = QgsCoordinateReferenceSystem('EPSG:4326')

            # Create memory layer with translated name
            layer_name = tr('sampling_points_layer')
            layer = QgsVectorLayer(f'Point?crs={crs.authid()}', layer_name, 'memory')
            provider = layer.dataProvider()

            # Add fields
            provider.addAttributes([
                QgsField('point_id', QVariant_Int),
                QgsField('x_coord', QVariant_Double),
                QgsField('y_coord', QVariant_Double),
                QgsField('type', QVariant_String)
            ])
            layer.updateFields()

            # Add features
            features = []
            for i, point in enumerate(new_points):
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point[0], point[1])))
                feat.setAttributes([i+1, float(point[0]), float(point[1]), 'suggested'])
                features.append(feat)

            provider.addFeatures(features)

            # Style for new points
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'star',
                'color': '#FFD700',
                'size': '5',
                'outline_style': 'solid',
                'outline_width': '1',
                'outline_color': '#FF0000'
            })
            layer.renderer().setSymbol(symbol)

            # Add to project
            QgsProject.instance().addMapLayer(layer)

            QgsMessageLog.logMessage(
                tr('layer_created'),
                'GeoArchaeo', Qgis_Info
            )
            
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Sampling layer error: {str(e)}",
                'GeoArchaeo', Qgis_Warning
            )
    
    def _create_ml_layer(self, result):
        """Crea layer vettoriale con i risultati ML - con attributi significativi"""
        try:
            # Ottieni il CRS dal primo layer selezionato
            selected_layers = []
            for i in range(self.ml_layers.count()):
                item = self.ml_layers.item(i)
                if item.isSelected():
                    layer = item.data(Qt_UserRole)
                    selected_layers.append(layer)
                    break

            if selected_layers and selected_layers[0]:
                crs = selected_layers[0].crs()
            else:
                crs = QgsCoordinateReferenceSystem('EPSG:4326')

            # Ottieni metodo ML usato
            ml_method = self.ml_method.currentText().lower()
            is_anomaly_detection = 'isolation' in ml_method or 'anomal' in ml_method
            is_dbscan = 'dbscan' in ml_method

            # Nome layer tradotto
            layer_name = tr('ml_clusters_layer')

            # Crea layer temporaneo
            layer = QgsVectorLayer(f'Point?crs={crs.authid()}', layer_name, 'memory')
            provider = layer.dataProvider()

            # Aggiungi campi con nomi significativi
            provider.addAttributes([
                QgsField('cluster_id', QVariant_Int),
                QgsField('cluster_name', QVariant_String),
                QgsField('cluster_size', QVariant_Int),
                QgsField('description', QVariant_String),
                QgsField('x_coord', QVariant_Double),
                QgsField('y_coord', QVariant_Double)
            ])
            layer.updateFields()

            coords = result['coordinates']
            labels = result['labels']
            unique_labels = np.unique(labels)

            # Calcola statistiche per ogni cluster
            cluster_info = {}
            for label in unique_labels:
                mask = labels == label
                count = np.sum(mask)

                # Genera nome e descrizione significativi
                if is_anomaly_detection:
                    if label == 0:
                        name = tr('anomaly_normal')
                        desc = tr('isolation_desc')
                    else:
                        name = tr('anomaly_outlier')
                        desc = tr('isolation_desc')
                elif is_dbscan and label == -1:
                    name = tr('noise_points')
                    desc = tr('dbscan_desc')
                else:
                    # Assegna lettera alfabetica (A, B, C, ...)
                    letter_idx = label if label >= 0 else len(unique_labels) - 1
                    letter = chr(ord('A') + (letter_idx % 26))
                    name = tr_format('cluster_with_count', letter=letter, count=count)
                    if is_dbscan:
                        desc = tr('dbscan_desc')
                    else:
                        desc = tr('kmeans_desc')

                cluster_info[label] = {
                    'name': name,
                    'count': count,
                    'description': desc
                }

            # Aggiungi features con attributi completi
            features = []
            for i, (x, y) in enumerate(coords):
                label = int(labels[i])
                info = cluster_info[label]

                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
                feat.setAttributes([
                    label,
                    info['name'],
                    int(info['count']),
                    info['description'],
                    float(x),
                    float(y)
                ])
                features.append(feat)

            provider.addFeatures(features)

            # Stile categorizzato con colori migliori e nomi significativi
            categories = []
            # Palette colori più professionale
            colors = ['#E53935', '#43A047', '#1E88E5', '#FDD835', '#8E24AA',
                     '#00ACC1', '#FB8C00', '#6D4C41', '#546E7A', '#D81B60']

            for i, label in enumerate(unique_labels):
                info = cluster_info[label]

                # Colore speciale per rumore/anomalie
                if is_anomaly_detection and label == 1:
                    color = '#E53935'  # Rosso per anomalie
                elif is_dbscan and label == -1:
                    color = '#9E9E9E'  # Grigio per rumore
                else:
                    color = colors[i % len(colors)]

                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'circle',
                    'color': color,
                    'size': '4',
                    'outline_style': 'solid',
                    'outline_width': '0.5',
                    'outline_color': 'black'
                })

                # Usa il nome descrittivo nella legenda
                category = QgsRendererCategory(label, symbol, info['name'])
                categories.append(category)

            renderer = QgsCategorizedSymbolRenderer('cluster_id', categories)
            layer.setRenderer(renderer)

            # Aggiungi al progetto
            QgsProject.instance().addMapLayer(layer)

            QgsMessageLog.logMessage(
                tr('layer_created'),
                'GeoArchaeo', Qgis_Info
            )

        except Exception as e:
            QgsMessageLog.logMessage(
                f"ML layer error: {str(e)}",
                'GeoArchaeo', Qgis_Warning
            )

    # ==================== Language and Examples Methods ====================

    def _change_language(self, index):
        """Change the interface language"""
        lang = self.lang_combo.itemData(index)
        set_language(lang)

        # Update toolbar button texts
        self.load_examples_btn.setText(tr('load_examples'))
        self.tutorial_btn.setText(tr('show_tutorial'))

        # Update tab titles
        self.tabs.setTabText(0, tr('tab_data'))
        self.tabs.setTabText(1, tr('tab_variogram'))
        self.tabs.setTabText(2, tr('tab_kriging'))
        self.tabs.setTabText(3, tr('tab_ml'))
        self.tabs.setTabText(4, tr('tab_sampling'))
        self.tabs.setTabText(5, tr('tab_report'))

        # Update info labels
        if hasattr(self, 'data_info_label'):
            self.data_info_label.setText(tr('data_title') + "<br>" + tr('data_desc'))
        if hasattr(self, 'variogram_info_label'):
            self.variogram_info_label.setText(tr('variogram_title') + "<br>" + tr('variogram_desc'))
        if hasattr(self, 'kriging_info_label'):
            self.kriging_info_label.setText(tr('kriging_title') + "<br>" + tr('kriging_desc'))
        if hasattr(self, 'ml_info_label'):
            self.ml_info_label.setText(tr('ml_title') + "<br>" + tr('ml_desc'))
        if hasattr(self, 'sampling_info_label'):
            self.sampling_info_label.setText(tr('sampling_title') + "<br>" + tr('sampling_desc'))
        if hasattr(self, 'report_info_label'):
            self.report_info_label.setText(tr('report_title') + "<br>" + tr('report_desc'))

        # Update Data tab labels
        if hasattr(self, 'data_group'):
            self.data_group.setTitle(tr('data_selection'))
        if hasattr(self, 'point_layer_label'):
            self.point_layer_label.setText(tr('point_layer'))
        if hasattr(self, 'value_field_label'):
            self.value_field_label.setText(tr('value_field'))
        if hasattr(self, 'stats_label'):
            self.stats_label.setText(tr('statistics'))
        if hasattr(self, 'calc_stats_btn'):
            self.calc_stats_btn.setText(tr('calc_statistics'))

        # Update Variogram tab labels
        if hasattr(self, 'variogram_params_group'):
            self.variogram_params_group.setTitle(tr('variogram_params'))
        if hasattr(self, 'max_dist_label'):
            self.max_dist_label.setText(tr('max_distance'))
        if hasattr(self, 'model_label'):
            self.model_label.setText(tr('theoretical_model'))
        if hasattr(self, 'advanced_group'):
            self.advanced_group.setTitle(tr('advanced_params'))
        if hasattr(self, 'nugget_label'):
            self.nugget_label.setText(tr('nugget'))
        if hasattr(self, 'sill_label'):
            self.sill_label.setText(tr('sill'))
        if hasattr(self, 'range_label'):
            self.range_label.setText(tr('range'))
        if hasattr(self, 'anisotropy_check'):
            self.anisotropy_check.setText(tr('anisotropy_check'))
        if hasattr(self, 'calc_variogram_btn'):
            self.calc_variogram_btn.setText(tr('calc_variogram'))

        # Update Kriging tab labels
        if hasattr(self, 'kriging_params_group'):
            self.kriging_params_group.setTitle(tr('kriging_params'))
        if hasattr(self, 'kriging_type_label'):
            self.kriging_type_label.setText(tr('kriging_type'))
        if hasattr(self, 'resolution_label'):
            self.resolution_label.setText(tr('grid_resolution'))
        if hasattr(self, 'use_variogram'):
            self.use_variogram.setText(tr('use_variogram'))
        if hasattr(self, 'run_kriging_btn'):
            self.run_kriging_btn.setText(tr('run_kriging'))

        # Update ML tab labels
        if hasattr(self, 'ml_layers_label'):
            self.ml_layers_label.setText(tr('ml_layers_select'))
        if hasattr(self, 'ml_method_label'):
            self.ml_method_label.setText(tr('ml_method'))
        if hasattr(self, 'run_ml_btn'):
            self.run_ml_btn.setText(tr('run_ml'))

        # Update Sampling tab labels
        if hasattr(self, 'sampling_params_group'):
            self.sampling_params_group.setTitle(tr('sampling_params'))
        if hasattr(self, 'existing_points_label'):
            self.existing_points_label.setText(tr('existing_points'))
        if hasattr(self, 'new_points_label'):
            self.new_points_label.setText(tr('new_points'))
        if hasattr(self, 'sampling_method_label'):
            self.sampling_method_label.setText(tr('sampling_method'))
        if hasattr(self, 'calc_optimal_btn'):
            self.calc_optimal_btn.setText(tr('calc_optimal'))

        # Update Report tab labels
        if hasattr(self, 'report_sections_group'):
            self.report_sections_group.setTitle(tr('report_sections'))
        if hasattr(self, 'generate_html_btn'):
            self.generate_html_btn.setText(tr('generate_report'))

        # Show confirmation
        if lang == 'en':
            QMessageBox.information(self, "Language Changed", "Interface language changed to English.")
        else:
            QMessageBox.information(self, "Lingua Cambiata", "Lingua dell'interfaccia cambiata in Italiano.")

    def _show_load_examples_dialog(self):
        """Show dialog to load example datasets"""
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('examples_title'))
        dialog.setMinimumWidth(450)

        layout = QVBoxLayout()

        # Description
        desc_label = QLabel(tr('examples_desc'))
        desc_label.setStyleSheet("QLabel { color: #333; padding: 5px; }")
        layout.addWidget(desc_label)

        # Checkboxes for each dataset
        self.example_checks = {}

        datasets = [
            ('villa_ceramica', 'villa_ceramica.gpkg', tr('villa_ceramica')),
            ('geofisica', 'geofisica_survey.gpkg', tr('geofisica')),
            ('soil_samples', 'soil_samples.gpkg', tr('soil_samples')),
            ('necropoli', 'necropoli.gpkg', tr('necropoli')),
        ]

        for key, filename, label in datasets:
            cb = QCheckBox(label)
            cb.setChecked(True)
            cb.setProperty('filename', filename)
            self.example_checks[key] = cb
            layout.addWidget(cb)

        # Path selector
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path:"))
        self.example_path_edit = QLabel(self.EXAMPLE_DATA_PATH)
        self.example_path_edit.setStyleSheet(
            "QLabel { background-color: #f5f5f5; color: #333; padding: 5px; border: 1px solid #ccc; }"
        )
        path_layout.addWidget(self.example_path_edit, 1)

        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(40)
        browse_btn.clicked.connect(self._browse_example_path)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(lambda: self._load_selected_examples(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec_()

    def _browse_example_path(self):
        """Browse for example data directory"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Example Data Directory",
            self.EXAMPLE_DATA_PATH
        )
        if path:
            self.EXAMPLE_DATA_PATH = path
            self.example_path_edit.setText(path)

    def _load_selected_examples(self, dialog):
        """Load selected example datasets"""
        loaded_count = 0
        errors = []

        for key, checkbox in self.example_checks.items():
            if checkbox.isChecked():
                filename = checkbox.property('filename')
                filepath = os.path.join(self.EXAMPLE_DATA_PATH, filename)

                if os.path.exists(filepath):
                    try:
                        # Load the layer
                        layer_name = os.path.splitext(filename)[0]
                        layer = QgsVectorLayer(filepath, layer_name, "ogr")

                        if layer.isValid():
                            QgsProject.instance().addMapLayer(layer)
                            loaded_count += 1
                            QgsMessageLog.logMessage(
                                f"Loaded: {filename}",
                                'GeoArchaeo', Qgis_Info
                            )
                        else:
                            errors.append(f"{filename}: invalid layer")
                    except Exception as e:
                        errors.append(f"{filename}: {str(e)}")
                else:
                    errors.append(f"{filename}: file not found")

        dialog.accept()

        # Show result
        if loaded_count > 0:
            msg = f"Loaded {loaded_count} layer(s) successfully."
            if errors:
                msg += f"\n\nErrors:\n" + "\n".join(errors)
            QMessageBox.information(self, tr('completed'), msg)
        elif errors:
            QMessageBox.warning(self, tr('error'), "\n".join(errors))

    def _show_tutorial(self):
        """Show the tutorial in a dialog or browser"""
        lang = get_language()

        # Tutorial content
        tutorial_html = self._get_tutorial_html(lang)

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("GeoArchaeo Tutorial")
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout()

        # Use QTextBrowser for the tutorial
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(tutorial_html)
        layout.addWidget(browser)

        # Open in browser button
        btn_layout = QHBoxLayout()
        open_browser_btn = QPushButton("Open in Browser / Apri nel Browser")
        open_browser_btn.clicked.connect(lambda: self._open_tutorial_in_browser(lang))
        btn_layout.addWidget(open_browser_btn)

        close_btn = QPushButton("Close / Chiudi")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def _open_tutorial_in_browser(self, lang):
        """Open tutorial in web browser"""
        tutorial_html = self._get_tutorial_html(lang)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.html', delete=False,
            dir=tempfile.gettempdir(), encoding='utf-8'
        )
        temp_file.write(tutorial_html)
        temp_file.close()

        import webbrowser
        webbrowser.open(f'file://{temp_file.name}')

    def _get_tutorial_html(self, lang='it'):
        """Get tutorial HTML content"""
        if lang == 'en':
            return self._get_tutorial_html_en()
        else:
            return self._get_tutorial_html_it()

    def _get_tutorial_html_it(self):
        """Tutorial in Italian - Comprehensive version"""
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tutorial GeoArchaeo - Guida Completa</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 950px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333333; background-color: #ffffff; }
        h1 { color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 10px; }
        h2 { color: #388E3C; margin-top: 30px; border-bottom: 1px solid #388E3C; padding-bottom: 5px; }
        h3 { color: #F57C00; }
        h4 { color: #7B1FA2; }
        p, li, td { color: #333333; }
        a { color: #1976D2; }
        code { background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; color: #c7254e; }
        pre { background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; color: #333333; }
        .tip { background-color: #E3F2FD; border-left: 4px solid #1976D2; padding: 10px; margin: 10px 0; color: #1a237e; }
        .warning { background-color: #FFF3E0; border-left: 4px solid #F57C00; padding: 10px; margin: 10px 0; color: #e65100; }
        .theory { background-color: #F3E5F5; border-left: 4px solid #7B1FA2; padding: 10px; margin: 10px 0; color: #4a148c; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #1976D2; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .formula { font-family: serif; font-style: italic; background-color: #fff9c4; padding: 5px 10px; display: inline-block; margin: 5px 0; color: #333333; }
    </style>
</head>
<body>
    <h1>🏛️ Tutorial GeoArchaeo - Guida Completa</h1>
    <p><em>Analisi Geostatistica per la Ricerca Archeologica</em></p>

    <h2>📚 Indice</h2>
    <ol>
        <li><a href="#teoria">Fondamenti Teorici</a></li>
        <li><a href="#variogramma">Il Variogramma</a></li>
        <li><a href="#kriging">Tipi di Kriging</a></li>
        <li><a href="#ml">Machine Learning</a></li>
        <li><a href="#esercizi">Esercizi Pratici</a></li>
    </ol>

    <h2 id="teoria">1. Fondamenti Teorici</h2>

    <h3>Cos'è la Geostatistica?</h3>
    <p>La geostatistica è una branca della statistica che si occupa di fenomeni spazialmente correlati.
    Il principio fondamentale è la <strong>Prima Legge della Geografia di Tobler</strong>:</p>
    <div class="theory">
        <em>"Tutto è correlato con tutto, ma le cose vicine sono più correlate delle cose lontane."</em>
    </div>

    <h3>Perché usarla in Archeologia?</h3>
    <ul>
        <li><strong>Distribuzione manufatti</strong>: I frammenti ceramici non sono distribuiti casualmente</li>
        <li><strong>Anomalie geofisiche</strong>: Strutture sepolte creano pattern spaziali</li>
        <li><strong>Composizione suoli</strong>: Attività antropiche lasciano firme chimiche spazialmente correlate</li>
    </ul>

    <h2 id="variogramma">2. Il Variogramma</h2>

    <h3>Cos'è il Variogramma?</h3>
    <p>Il variogramma (o semivariogramma) misura come la <strong>variabilità</strong> tra coppie di punti
    cambia al crescere della <strong>distanza</strong>. È lo strumento fondamentale per capire
    la struttura spaziale dei dati.</p>

    <div class="formula">γ(h) = ½ × E[(Z(x) - Z(x+h))²]</div>

    <h3>Parametri del Variogramma</h3>
    <table>
        <tr>
            <th>Parametro</th>
            <th>Significato</th>
            <th>Interpretazione Archeologica</th>
        </tr>
        <tr>
            <td><strong>Nugget (C₀)</strong></td>
            <td>Variabilità a distanza zero</td>
            <td>Errore di misura + variabilità micro-scala (es. disturbo post-deposizionale)</td>
        </tr>
        <tr>
            <td><strong>Sill (C + C₀)</strong></td>
            <td>Varianza totale asintotica</td>
            <td>Massima variabilità raggiunta</td>
        </tr>
        <tr>
            <td><strong>Range (a)</strong></td>
            <td>Distanza di correlazione</td>
            <td>Dimensione tipica delle "unità funzionali" (es. stanze, aree attività)</td>
        </tr>
    </table>

    <h3>Modelli Teorici di Variogramma</h3>

    <h4>🔵 Modello Sferico (Spherical)</h4>
    <p><strong>Quando usarlo:</strong> È il modello più comune in archeologia. Ideale quando la correlazione
    spaziale diminuisce gradualmente fino a un punto (range) oltre il quale i dati sono indipendenti.</p>
    <ul>
        <li>✅ Distribuzione ceramica in aree di scavo</li>
        <li>✅ Densità di manufatti</li>
        <li>✅ Dati con confini spaziali ben definiti</li>
    </ul>

    <h4>🟢 Modello Esponenziale (Exponential)</h4>
    <p><strong>Quando usarlo:</strong> Quando la correlazione diminuisce rapidamente vicino all'origine
    e poi più lentamente. Il range effettivo è raggiunto asintoticamente (mai completamente).</p>
    <ul>
        <li>✅ Diffusione di elementi chimici nel suolo</li>
        <li>✅ Processi con decadimento continuo</li>
        <li>✅ Quando non c'è un limite netto di correlazione</li>
    </ul>

    <h4>🟡 Modello Gaussiano (Gaussian)</h4>
    <p><strong>Quando usarlo:</strong> Per fenomeni molto "lisci" con transizioni graduali.
    La curva è parabolica all'origine (derivata zero).</p>
    <ul>
        <li>✅ Superfici topografiche</li>
        <li>✅ Dati molto regolari senza variabilità locale</li>
        <li>⚠️ Può causare instabilità numerica - usare con cautela</li>
    </ul>

    <h4>🟣 Modello Matérn</h4>
    <p><strong>Quando usarlo:</strong> Modello flessibile che include sferico, esponenziale e gaussiano
    come casi speciali. Ha un parametro (ν) che controlla la "rugosità".</p>
    <ul>
        <li>✅ Quando altri modelli non fittano bene</li>
        <li>✅ Per analisi avanzate con controllo fine della smoothness</li>
    </ul>

    <div class="tip">
        <strong>💡 Regola pratica:</strong> Inizia sempre con il modello <code>spherical</code>.
        Se il fit non è buono, prova <code>exponential</code>. Usa <code>gaussian</code> solo per dati molto regolari.
    </div>

    <h2 id="kriging">3. Tipi di Kriging</h2>

    <h3>Cos'è il Kriging?</h3>
    <p>Il Kriging è un metodo di interpolazione che produce la <strong>Best Linear Unbiased Prediction (BLUP)</strong>.
    A differenza di altri interpolatori, il kriging:</p>
    <ul>
        <li>Usa la struttura spaziale (variogramma) per pesare i punti vicini</li>
        <li>Fornisce una stima dell'<strong>incertezza</strong> per ogni predizione</li>
        <li>È ottimale nel senso dei minimi quadrati</li>
    </ul>

    <h3>Ordinary Kriging (Kriging Ordinario)</h3>
    <p><strong>Il più usato.</strong> Assume che la media sia costante ma sconosciuta nell'area di studio.</p>

    <table>
        <tr><th>Pro</th><th>Contro</th></tr>
        <tr>
            <td>Semplice da usare</td>
            <td>Assume stazionarietà (media costante)</td>
        </tr>
        <tr>
            <td>Robusto</td>
            <td>Non può includere variabili ausiliarie</td>
        </tr>
        <tr>
            <td>Ben compreso teoricamente</td>
            <td>Può avere problemi ai bordi</td>
        </tr>
    </table>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ Distribuzione manufatti in aree omogenee</li>
        <li>✅ Prima analisi esplorativa</li>
        <li>✅ Quando hai solo una variabile da interpolare</li>
    </ul>

    <h3>Co-Kriging</h3>
    <p>Usa <strong>variabili ausiliarie correlate</strong> per migliorare la stima della variabile principale.</p>

    <p><strong>Esempio archeologico:</strong> Interpolare la densità di ceramica usando anche
    i dati di suscettività magnetica (correlata con attività di combustione).</p>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ Hai variabili correlate (es. GPR + magnetometria)</li>
        <li>✅ La variabile ausiliaria ha più punti di campionamento</li>
        <li>✅ Vuoi migliorare la precisione delle stime</li>
    </ul>

    <h3>Kriging Spazio-Temporale</h3>
    <p>Estende il kriging alla dimensione temporale, permettendo di modellare
    come i pattern spaziali cambiano nel tempo.</p>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ Dati da più fasi cronologiche</li>
        <li>✅ Monitoraggio di siti nel tempo</li>
        <li>✅ Analisi di processi deposizionali</li>
    </ul>

    <h2 id="ml">4. Machine Learning per Pattern Recognition</h2>

    <h3>K-Means Clustering</h3>
    <p>Raggruppa i dati in <strong>K cluster</strong> basandosi sulla distanza dal centroide.</p>

    <table>
        <tr><th>Pro</th><th>Contro</th></tr>
        <tr>
            <td>Semplice e veloce</td>
            <td>Devi specificare K a priori</td>
        </tr>
        <tr>
            <td>Funziona bene con cluster sferici</td>
            <td>Sensibile agli outlier</td>
        </tr>
        <tr>
            <td>Scalabile</td>
            <td>Assume cluster di dimensioni simili</td>
        </tr>
    </table>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ Classificazione di aree funzionali</li>
        <li>✅ Quando sai quanti gruppi aspettarti</li>
        <li>✅ Dati con cluster ben separati</li>
    </ul>

    <h3>DBSCAN (Density-Based Spatial Clustering)</h3>
    <p>Trova cluster basati sulla <strong>densità</strong> dei punti. Non richiede di specificare
    il numero di cluster.</p>

    <table>
        <tr><th>Pro</th><th>Contro</th></tr>
        <tr>
            <td>Trova automaticamente il numero di cluster</td>
            <td>Sensibile ai parametri eps e min_samples</td>
        </tr>
        <tr>
            <td>Può trovare cluster di forma arbitraria</td>
            <td>Difficile con densità variabile</td>
        </tr>
        <tr>
            <td>Identifica outlier (noise = -1)</td>
            <td>Non funziona bene in alta dimensionalità</td>
        </tr>
    </table>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ <strong>Necropoli</strong>: gruppi familiari con sepolture ravvicinate</li>
        <li>✅ Pattern spaziali con forma irregolare</li>
        <li>✅ Quando vuoi identificare anche gli outlier</li>
    </ul>

    <h3>Isolation Forest (Anomaly Detection)</h3>
    <p>Identifica <strong>anomalie</strong> isolando i punti che sono "diversi" dalla maggioranza.</p>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ <strong>Geofisica</strong>: trovare anomalie (muri, fosse, forni)</li>
        <li>✅ Identificare punti con valori insoliti</li>
        <li>✅ Quality control dei dati</li>
    </ul>

    <h3>Random Forest</h3>
    <p>Ensemble di alberi decisionali per <strong>classificazione</strong> e <strong>regressione</strong>.</p>

    <p><strong>Quando usarlo:</strong></p>
    <ul>
        <li>✅ Classificare tipi di depositi</li>
        <li>✅ Predire categorie da variabili multiple</li>
        <li>✅ Quando hai dati di training etichettati</li>
    </ul>

    <h2 id="esercizi">5. Esercizi Pratici</h2>

    <h3>Esercizio 1: Distribuzione Ceramica (Kriging)</h3>
    <ol>
        <li>Carica <code>villa_ceramica.gpkg</code></li>
        <li>Tab Dati → Seleziona <code>ceramic_count</code> → Calcola Statistiche</li>
        <li>Tab Variogramma → Distanza 25m, Modello <code>spherical</code></li>
        <li>Tab Kriging → Risoluzione 2.0m → Esegui</li>
    </ol>

    <h3>Esercizio 2: Anomalie Geofisiche (Isolation Forest)</h3>
    <ol>
        <li>Carica <code>geofisica_survey.gpkg</code></li>
        <li>Tab ML → Seleziona il layer → Metodo <code>Isolation Forest</code></li>
        <li>Le anomalie (strutture) saranno evidenziate</li>
    </ol>

    <h3>Esercizio 3: Gruppi Familiari Necropoli (DBSCAN)</h3>
    <ol>
        <li>Carica <code>necropoli.gpkg</code></li>
        <li>Tab ML → Metodo <code>DBSCAN</code></li>
        <li>I cluster rappresentano probabili gruppi familiari</li>
    </ol>

    <h2>Tabella Riassuntiva: Quale Metodo Usare?</h2>
    <table>
        <tr>
            <th>Obiettivo</th>
            <th>Metodo</th>
            <th>Esempio</th>
        </tr>
        <tr>
            <td>Creare mappa continua da punti</td>
            <td>Ordinary Kriging</td>
            <td>Densità ceramica</td>
        </tr>
        <tr>
            <td>Migliorare stima con dati ausiliari</td>
            <td>Co-Kriging</td>
            <td>Ceramica + magnetometria</td>
        </tr>
        <tr>
            <td>Trovare anomalie</td>
            <td>Isolation Forest</td>
            <td>Strutture in dati geofisici</td>
        </tr>
        <tr>
            <td>Raggruppare per densità</td>
            <td>DBSCAN</td>
            <td>Gruppi familiari in necropoli</td>
        </tr>
        <tr>
            <td>Classificare in N gruppi</td>
            <td>K-Means</td>
            <td>Aree funzionali</td>
        </tr>
    </table>

    <div class="warning">
        <strong>⚠️ Risoluzione Problemi:</strong><br>
        • <strong>Kriging lento?</strong> Aumenta la risoluzione (es. 2-5m)<br>
        • <strong>DBSCAN tutto -1?</strong> I parametri eps sono auto-calcolati, ma prova K-Means<br>
        • <strong>R² basso?</strong> I dati potrebbero non avere correlazione spaziale
    </div>

    <hr>
    <p><strong>Autore:</strong> Enzo Cocca | <strong>Email:</strong> enzo.ccc@gmail.com</p>
    <p><strong>Repository:</strong> <a href="https://github.com/enzococca/geoarchaeo">github.com/enzococca/geoarchaeo</a></p>
</body>
</html>'''

    def _get_tutorial_html_en(self):
        """Tutorial in English - Comprehensive version"""
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GeoArchaeo Tutorial - Complete Guide</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 950px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333333; background-color: #ffffff; }
        h1 { color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 10px; }
        h2 { color: #388E3C; margin-top: 30px; border-bottom: 1px solid #388E3C; padding-bottom: 5px; }
        h3 { color: #F57C00; }
        h4 { color: #7B1FA2; }
        p, li, td { color: #333333; }
        a { color: #1976D2; }
        code { background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; color: #c7254e; }
        pre { background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; color: #333333; }
        .tip { background-color: #E3F2FD; border-left: 4px solid #1976D2; padding: 10px; margin: 10px 0; color: #1a237e; }
        .warning { background-color: #FFF3E0; border-left: 4px solid #F57C00; padding: 10px; margin: 10px 0; color: #e65100; }
        .theory { background-color: #F3E5F5; border-left: 4px solid #7B1FA2; padding: 10px; margin: 10px 0; color: #4a148c; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #1976D2; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .formula { font-family: serif; font-style: italic; background-color: #fff9c4; padding: 5px 10px; display: inline-block; margin: 5px 0; color: #333333; }
    </style>
</head>
<body>
    <h1>🏛️ GeoArchaeo Tutorial - Complete Guide</h1>
    <p><em>Geostatistical Analysis for Archaeological Research</em></p>

    <h2>📚 Table of Contents</h2>
    <ol>
        <li><a href="#theory">Theoretical Foundations</a></li>
        <li><a href="#variogram">The Variogram</a></li>
        <li><a href="#kriging">Kriging Types</a></li>
        <li><a href="#ml">Machine Learning</a></li>
        <li><a href="#exercises">Practical Exercises</a></li>
    </ol>

    <h2 id="theory">1. Theoretical Foundations</h2>

    <h3>What is Geostatistics?</h3>
    <p>Geostatistics is a branch of statistics dealing with spatially correlated phenomena.
    The fundamental principle is <strong>Tobler's First Law of Geography</strong>:</p>
    <div class="theory">
        <em>"Everything is related to everything else, but near things are more related than distant things."</em>
    </div>

    <h3>Why Use It in Archaeology?</h3>
    <ul>
        <li><strong>Artifact distribution</strong>: Ceramic fragments are not randomly distributed</li>
        <li><strong>Geophysical anomalies</strong>: Buried structures create spatial patterns</li>
        <li><strong>Soil composition</strong>: Anthropic activities leave spatially correlated chemical signatures</li>
    </ul>

    <h2 id="variogram">2. The Variogram</h2>

    <h3>What is a Variogram?</h3>
    <p>The variogram (or semivariogram) measures how <strong>variability</strong> between pairs of points
    changes as <strong>distance</strong> increases. It is the fundamental tool for understanding
    the spatial structure of data.</p>

    <div class="formula">γ(h) = ½ × E[(Z(x) - Z(x+h))²]</div>

    <h3>Variogram Parameters</h3>
    <table>
        <tr>
            <th>Parameter</th>
            <th>Meaning</th>
            <th>Archaeological Interpretation</th>
        </tr>
        <tr>
            <td><strong>Nugget (C₀)</strong></td>
            <td>Variability at zero distance</td>
            <td>Measurement error + micro-scale variability (e.g., post-depositional disturbance)</td>
        </tr>
        <tr>
            <td><strong>Sill (C + C₀)</strong></td>
            <td>Asymptotic total variance</td>
            <td>Maximum variability reached</td>
        </tr>
        <tr>
            <td><strong>Range (a)</strong></td>
            <td>Correlation distance</td>
            <td>Typical size of "functional units" (e.g., rooms, activity areas)</td>
        </tr>
    </table>

    <h3>Theoretical Variogram Models</h3>

    <h4>🔵 Spherical Model</h4>
    <p><strong>When to use:</strong> The most common model in archaeology. Ideal when spatial correlation
    gradually decreases to a point (range) beyond which data are independent.</p>
    <ul>
        <li>✅ Ceramic distribution in excavation areas</li>
        <li>✅ Artifact density</li>
        <li>✅ Data with well-defined spatial boundaries</li>
    </ul>

    <h4>🟢 Exponential Model</h4>
    <p><strong>When to use:</strong> When correlation decreases rapidly near the origin
    and then more slowly. The effective range is reached asymptotically (never completely).</p>
    <ul>
        <li>✅ Diffusion of chemical elements in soil</li>
        <li>✅ Processes with continuous decay</li>
        <li>✅ When there is no sharp correlation limit</li>
    </ul>

    <h4>🟡 Gaussian Model</h4>
    <p><strong>When to use:</strong> For very "smooth" phenomena with gradual transitions.
    The curve is parabolic at the origin (zero derivative).</p>
    <ul>
        <li>✅ Topographic surfaces</li>
        <li>✅ Very regular data without local variability</li>
        <li>⚠️ Can cause numerical instability - use with caution</li>
    </ul>

    <h4>🟣 Matérn Model</h4>
    <p><strong>When to use:</strong> Flexible model that includes spherical, exponential, and Gaussian
    as special cases. Has a parameter (ν) that controls "roughness".</p>
    <ul>
        <li>✅ When other models don't fit well</li>
        <li>✅ For advanced analyses with fine smoothness control</li>
    </ul>

    <div class="tip">
        <strong>💡 Rule of thumb:</strong> Always start with the <code>spherical</code> model.
        If the fit is poor, try <code>exponential</code>. Use <code>gaussian</code> only for very regular data.
    </div>

    <h2 id="kriging">3. Kriging Types</h2>

    <h3>What is Kriging?</h3>
    <p>Kriging is an interpolation method that produces the <strong>Best Linear Unbiased Prediction (BLUP)</strong>.
    Unlike other interpolators, kriging:</p>
    <ul>
        <li>Uses spatial structure (variogram) to weight nearby points</li>
        <li>Provides an <strong>uncertainty</strong> estimate for each prediction</li>
        <li>Is optimal in the least squares sense</li>
    </ul>

    <h3>Ordinary Kriging</h3>
    <p><strong>Most commonly used.</strong> Assumes the mean is constant but unknown in the study area.</p>

    <table>
        <tr><th>Pros</th><th>Cons</th></tr>
        <tr>
            <td>Simple to use</td>
            <td>Assumes stationarity (constant mean)</td>
        </tr>
        <tr>
            <td>Robust</td>
            <td>Cannot include auxiliary variables</td>
        </tr>
        <tr>
            <td>Well understood theoretically</td>
            <td>May have edge effects</td>
        </tr>
    </table>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ Artifact distribution in homogeneous areas</li>
        <li>✅ First exploratory analysis</li>
        <li>✅ When you only have one variable to interpolate</li>
    </ul>

    <h3>Co-Kriging</h3>
    <p>Uses <strong>correlated auxiliary variables</strong> to improve estimation of the primary variable.</p>

    <p><strong>Archaeological example:</strong> Interpolating ceramic density using also
    magnetic susceptibility data (correlated with combustion activities).</p>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ You have correlated variables (e.g., GPR + magnetometry)</li>
        <li>✅ The auxiliary variable has more sampling points</li>
        <li>✅ You want to improve estimate precision</li>
    </ul>

    <h3>Spatio-Temporal Kriging</h3>
    <p>Extends kriging to the temporal dimension, allowing modeling of
    how spatial patterns change over time.</p>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ Data from multiple chronological phases</li>
        <li>✅ Site monitoring over time</li>
        <li>✅ Analysis of depositional processes</li>
    </ul>

    <h2 id="ml">4. Machine Learning for Pattern Recognition</h2>

    <h3>K-Means Clustering</h3>
    <p>Groups data into <strong>K clusters</strong> based on distance from centroid.</p>

    <table>
        <tr><th>Pros</th><th>Cons</th></tr>
        <tr>
            <td>Simple and fast</td>
            <td>Must specify K beforehand</td>
        </tr>
        <tr>
            <td>Works well with spherical clusters</td>
            <td>Sensitive to outliers</td>
        </tr>
        <tr>
            <td>Scalable</td>
            <td>Assumes similar-sized clusters</td>
        </tr>
    </table>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ Classification of functional areas</li>
        <li>✅ When you know how many groups to expect</li>
        <li>✅ Data with well-separated clusters</li>
    </ul>

    <h3>DBSCAN (Density-Based Spatial Clustering)</h3>
    <p>Finds clusters based on point <strong>density</strong>. Does not require specifying
    the number of clusters.</p>

    <table>
        <tr><th>Pros</th><th>Cons</th></tr>
        <tr>
            <td>Automatically finds number of clusters</td>
            <td>Sensitive to eps and min_samples parameters</td>
        </tr>
        <tr>
            <td>Can find arbitrarily shaped clusters</td>
            <td>Difficult with variable density</td>
        </tr>
        <tr>
            <td>Identifies outliers (noise = -1)</td>
            <td>Doesn't work well in high dimensionality</td>
        </tr>
    </table>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ <strong>Necropolises</strong>: family groups with nearby burials</li>
        <li>✅ Spatial patterns with irregular shape</li>
        <li>✅ When you also want to identify outliers</li>
    </ul>

    <h3>Isolation Forest (Anomaly Detection)</h3>
    <p>Identifies <strong>anomalies</strong> by isolating points that are "different" from the majority.</p>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ <strong>Geophysics</strong>: finding anomalies (walls, pits, kilns)</li>
        <li>✅ Identifying points with unusual values</li>
        <li>✅ Data quality control</li>
    </ul>

    <h3>Random Forest</h3>
    <p>Ensemble of decision trees for <strong>classification</strong> and <strong>regression</strong>.</p>

    <p><strong>When to use:</strong></p>
    <ul>
        <li>✅ Classifying deposit types</li>
        <li>✅ Predicting categories from multiple variables</li>
        <li>✅ When you have labeled training data</li>
    </ul>

    <h2 id="exercises">5. Practical Exercises</h2>

    <h3>Exercise 1: Ceramic Distribution (Kriging)</h3>
    <ol>
        <li>Load <code>villa_ceramica.gpkg</code></li>
        <li>Data Tab → Select <code>ceramic_count</code> → Calculate Statistics</li>
        <li>Variogram Tab → Distance 25m, Model <code>spherical</code></li>
        <li>Kriging Tab → Resolution 2.0m → Run</li>
    </ol>

    <h3>Exercise 2: Geophysical Anomalies (Isolation Forest)</h3>
    <ol>
        <li>Load <code>geofisica_survey.gpkg</code></li>
        <li>ML Tab → Select the layer → Method <code>Isolation Forest</code></li>
        <li>Anomalies (structures) will be highlighted</li>
    </ol>

    <h3>Exercise 3: Necropolis Family Groups (DBSCAN)</h3>
    <ol>
        <li>Load <code>necropoli.gpkg</code></li>
        <li>ML Tab → Method <code>DBSCAN</code></li>
        <li>Clusters represent probable family groups</li>
    </ol>

    <h2>Summary Table: Which Method to Use?</h2>
    <table>
        <tr>
            <th>Goal</th>
            <th>Method</th>
            <th>Example</th>
        </tr>
        <tr>
            <td>Create continuous map from points</td>
            <td>Ordinary Kriging</td>
            <td>Ceramic density</td>
        </tr>
        <tr>
            <td>Improve estimate with auxiliary data</td>
            <td>Co-Kriging</td>
            <td>Ceramics + magnetometry</td>
        </tr>
        <tr>
            <td>Find anomalies</td>
            <td>Isolation Forest</td>
            <td>Structures in geophysical data</td>
        </tr>
        <tr>
            <td>Group by density</td>
            <td>DBSCAN</td>
            <td>Family groups in necropolis</td>
        </tr>
        <tr>
            <td>Classify into N groups</td>
            <td>K-Means</td>
            <td>Functional areas</td>
        </tr>
    </table>

    <div class="warning">
        <strong>⚠️ Troubleshooting:</strong><br>
        • <strong>Kriging slow?</strong> Increase resolution (e.g., 2-5m)<br>
        • <strong>DBSCAN all -1?</strong> Parameters are auto-calculated, but try K-Means<br>
        • <strong>Low R²?</strong> Data may not have spatial correlation
    </div>

    <hr>
    <p><strong>Author:</strong> Enzo Cocca | <strong>Email:</strong> enzo.ccc@gmail.com</p>
    <p><strong>Repository:</strong> <a href="https://github.com/enzococca/geoarchaeo">github.com/enzococca/geoarchaeo</a></p>
</body>
</html>'''