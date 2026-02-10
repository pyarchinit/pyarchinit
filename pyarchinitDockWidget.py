#! /usr/bin/env python
# -*- coding: utf 8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""
from __future__ import absolute_import

import os

from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtCore import QUrl, Qt, QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
                                  QTextBrowser, QSplitter, QComboBox, QLabel, QWidget,
                                  QPushButton, QFrame, QGridLayout, QScrollArea, QSizePolicy,
                                  QStackedWidget)
from qgis.gui import QgsDockWidget
from qgis.core import QgsSettings, QgsMessageLog, Qgis

def _dock_log(msg):
    QgsMessageLog.logMessage(str(msg), 'DockWidget', Qgis.MessageLevel.Info)

# Web view import for animation playback — prefer QtWebKit (bundled with QGIS),
# fall back to QtWebEngine, then graceful degradation to system browser.
HAS_WEBENGINE = False
_DockWebViewClass = None

# Try QtWebKit first (available in most QGIS installations via qgis.PyQt)
try:
    from qgis.PyQt.QtWebKitWidgets import QWebView as _DockWebViewClass
    HAS_WEBENGINE = True
    _dock_log("QWebView (QtWebKit) available — animation embedding enabled")
except (ImportError, AttributeError, RuntimeError):
    pass

# Fall back to QtWebEngine if QtWebKit not available
if not HAS_WEBENGINE:
    try:
        from qgis.PyQt.QtWebEngineWidgets import QWebEngineView as _DockWebViewClass
        HAS_WEBENGINE = True
        _dock_log("QWebEngineView available — animation embedding enabled")
    except (ImportError, AttributeError, RuntimeError):
        pass

if not HAS_WEBENGINE:
    _dock_log("No web view available (QtWebKit/QtWebEngine) — animations will open in system browser")

#from .tabs.Archeozoology import pyarchinit_Archeozoology
from .tabs.Deteta import pyarchinit_Deteta
from .tabs.Detsesso import pyarchinit_Detsesso
from .tabs.Gis_Time_controller import pyarchinit_Gis_Time_Controller
from .tabs.Image_viewer import Main
from .tabs.Images_directory_export import pyarchinit_Images_directory_export
from .tabs.Inv_Materiali import pyarchinit_Inventario_reperti
from .tabs.Pdf_export import pyarchinit_pdf_export
from .tabs.Periodizzazione import pyarchinit_Periodizzazione
from .tabs.Schedaind import pyarchinit_Schedaind
from .tabs.Site import pyarchinit_Site
from .tabs.Struttura import pyarchinit_Struttura
from .tabs.Tomba import pyarchinit_Tomba
from .tabs.US_USM import pyarchinit_US
from .tabs.UT import pyarchinit_UT
from .tabs.Upd import pyarchinit_Upd_Values
from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
from .gui.pyarchinitInfoDialog import pyArchInitDialog_Info

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'gui', 'ui', 'pyarchinit_plugin.ui')))


class PyarchinitPluginDialog(QgsDockWidget, MAIN_DIALOG_CLASS):

    # Supported languages
    SUPPORTED_LANGUAGES = {
        'it': 'Italiano',
        'en': 'English',
        'de': 'Deutsch',
        'fr': 'Français',
        'es': 'Español',
        'ar': 'العربية',
        'ca': 'Català'
    }

    # Tutorial metadata per language - Complete list of all 30 tutorials
    TUTORIALS_METADATA = {
        'it': [
            ("01_configurazione.md", "Configurazione", "Setup iniziale e database"),
            ("02_scheda_sito.md", "Scheda Sito", "Gestione siti archeologici"),
            ("03_scheda_us.md", "Scheda US/USM", "Unità Stratigrafiche e Murarie"),
            ("04_scheda_periodizzazione.md", "Periodizzazione", "Fasi e periodi cronologici"),
            ("05_scheda_struttura.md", "Scheda Struttura", "Documentazione strutture"),
            ("06_scheda_tomba.md", "Scheda Tomba", "Sepolture e corredi"),
            ("07_scheda_individui.md", "Scheda Individui", "Antropologia fisica"),
            ("08_scheda_inventario_materiali.md", "Inventario Materiali", "Gestione reperti"),
            ("09_scheda_campioni.md", "Scheda Campioni", "Campionature"),
            ("10_scheda_documentazione.md", "Documentazione", "Foto, disegni, rilievi"),
            ("11_matrix_harris.md", "Matrix Harris", "Diagrammi stratigrafici"),
            ("12_report_stampe.md", "Report e Stampe", "Generazione PDF"),
            ("13_thesaurus.md", "Thesaurus", "Vocabolari controllati"),
            ("14_gis_cartografia.md", "GIS e Cartografia", "Integrazione QGIS"),
            ("15_archeozoologia.md", "Archeozoologia", "Analisi faunistiche"),
            ("16_scheda_pottery.md", "Scheda Pottery", "Ceramica specialistica"),
            ("17_tma.md", "TMA", "Tabelle Materiali Archeologici"),
            ("18_backup.md", "Backup e Restore", "Gestione backup"),
            ("19_multiutente.md", "Multi-utente", "Lavoro collaborativo"),
            ("20_pubblicazione_web.md", "Pubblicazione Web", "Export e Lizmap"),
            ("21_scheda_ut.md", "Scheda UT", "Unità Topografiche"),
            ("22_media_manager.md", "Media Manager", "Gestione multimedia"),
            ("23_ricerca_immagini.md", "Ricerca Immagini", "Ricerca globale"),
            ("24_esporta_immagini.md", "Esporta Immagini", "Export per US/Fase"),
            ("25_time_manager.md", "Time Manager", "Navigazione temporale"),
            ("26_pottery_tools.md", "Pottery Tools", "Strumenti ceramica"),
            ("27_tops.md", "TOPS", "Total Open Station"),
            ("28_geopackage_export.md", "GeoPackage Export", "Export GeoPackage"),
            ("29_make_your_map.md", "Make Your Map", "Generazione mappe"),
            ("30_ai_query_database.md", "AI Query", "Query con AI"),
        ],
        'en': [
            ("01_configurazione.md", "Configuration", "Initial setup and database"),
            ("02_scheda_sito.md", "Site Form", "Archaeological site management"),
            ("03_scheda_us.md", "SU/WSU Form", "Stratigraphic and Wall Units"),
            ("04_scheda_periodizzazione.md", "Periodization", "Phases and periods"),
            ("05_scheda_struttura.md", "Structure Form", "Structure documentation"),
            ("06_scheda_tomba.md", "Burial Form", "Burials and grave goods"),
            ("07_scheda_individui.md", "Individuals Form", "Physical anthropology"),
            ("08_scheda_inventario_materiali.md", "Finds Inventory", "Artefact management"),
            ("09_scheda_campioni.md", "Samples Form", "Sampling"),
            ("10_scheda_documentazione.md", "Documentation", "Photos, drawings"),
            ("11_matrix_harris.md", "Harris Matrix", "Stratigraphic diagrams"),
            ("12_report_stampe.md", "Reports & Print", "PDF generation"),
            ("13_thesaurus.md", "Thesaurus", "Controlled vocabularies"),
            ("14_gis_cartografia.md", "GIS & Cartography", "QGIS integration"),
            ("15_archeozoologia.md", "Archaeozoology", "Faunal analysis"),
            ("16_scheda_pottery.md", "Pottery Form", "Specialist ceramics"),
            ("17_tma.md", "TMA", "Archaeological Materials Tables"),
            ("18_backup.md", "Backup & Restore", "Backup management"),
            ("19_multiutente.md", "Multi-user", "Collaborative work"),
            ("20_pubblicazione_web.md", "Web Publishing", "Export and Lizmap"),
            ("21_scheda_ut.md", "TU Form", "Topographic Units"),
            ("22_media_manager.md", "Media Manager", "Multimedia management"),
            ("23_ricerca_immagini.md", "Image Search", "Global search"),
            ("24_esporta_immagini.md", "Export Images", "Export by SU/Phase"),
            ("25_time_manager.md", "Time Manager", "Temporal navigation"),
            ("26_pottery_tools.md", "Pottery Tools", "Ceramic tools"),
            ("27_tops.md", "TOPS", "Total Open Station"),
            ("28_geopackage_export.md", "GeoPackage Export", "GeoPackage export"),
            ("29_make_your_map.md", "Make Your Map", "Map generation"),
            ("30_ai_query_database.md", "AI Query", "AI database query"),
        ],
        'de': [
            ("01_konfiguration.md", "Konfiguration", "Ersteinrichtung und Datenbank"),
            ("02_fundort_formular.md", "Fundstelle", "Archäologische Fundstellen"),
            ("03_se_formular.md", "SE/MSE Formular", "Stratigraphische Einheiten"),
            ("04_periodisierung.md", "Periodisierung", "Phasen und Perioden"),
            ("05_struktur_formular.md", "Struktur Formular", "Strukturdokumentation"),
            ("06_grab_formular.md", "Grab Formular", "Bestattungen"),
            ("07_individuen_formular.md", "Individuen", "Physische Anthropologie"),
            ("08_fundinventar_formular.md", "Fundinventar", "Artefaktverwaltung"),
            ("09_proben_formular.md", "Proben Formular", "Probenentnahme"),
            ("10_dokumentation_formular.md", "Dokumentation", "Fotos, Zeichnungen"),
            ("11_harris_matrix.md", "Harris-Matrix", "Stratigraphische Diagramme"),
            ("12_berichte_pdf.md", "Berichte & Druck", "PDF-Erstellung"),
            ("13_thesaurus.md", "Thesaurus", "Kontrollierte Vokabulare"),
            ("14_gis_kartographie.md", "GIS & Kartographie", "QGIS-Integration"),
            ("15_archaeozoologie.md", "Archäozoologie", "Faunistische Analyse"),
            ("16_keramik_formular.md", "Keramik Formular", "Spezialisierte Keramik"),
            ("17_tma.md", "TMA", "Archäologische Materialtabellen"),
            ("18_backup.md", "Backup & Restore", "Backup-Verwaltung"),
            ("19_mehrbenutzerbetrieb.md", "Mehrbenutzerbetrieb", "Kollaboratives Arbeiten"),
            ("20_webveroeffentlichung.md", "Web-Veröffentlichung", "Export und Lizmap"),
            ("21_ut_formular.md", "TE Formular", "Topographische Einheiten"),
            ("22_medien_manager.md", "Medien-Manager", "Multimedia-Verwaltung"),
            ("23_bildersuche.md", "Bildsuche", "Globale Suche"),
            ("24_bilder_exportieren.md", "Bilder exportieren", "Export nach SE/Phase"),
            ("25_time_manager.md", "Zeit-Manager", "Zeitliche Navigation"),
            ("26_keramik_werkzeuge.md", "Keramik-Werkzeuge", "Keramikwerkzeuge"),
            ("27_tops.md", "TOPS", "Total Open Station"),
            ("28_geopackage_export.md", "GeoPackage-Export", "GeoPackage-Export"),
            ("29_karte_erstellen.md", "Karte erstellen", "Kartenerstellung"),
            ("30_ki_datenbankabfrage.md", "KI-Abfrage", "KI-Datenbankabfrage"),
        ]
    }

    def __init__(self, iface):
        super(PyarchinitPluginDialog, self).__init__()
        self.setupUi(self)

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.tutorials_base_path = os.path.join(self.plugin_dir, "docs", "tutorials")

        # Detect current language
        self.current_lang = self.detect_language()

        # Initialize web views and UI enhancements
        self.setup_webviews()
        self.setup_tutorial_tab()
        self.remove_old_tabs()  # Remove old tabs before adding new workflow tabs
        self.setup_workflow_tabs()
        self.setup_modern_diagrams()

        # Connect buttons
        self.btnUStable.clicked.connect(self.runUS)
        self.btnUStable_2.clicked.connect(self.runUS)

        self.btnStrutturatable.clicked.connect(self.runStruttura)
        self.btnPeriodotable.clicked.connect(self.runPer)

        self.btnSitotable.clicked.connect(self.runSite)
        self.btnSitotable_2.clicked.connect(self.runSite)

        self.btnReptable.clicked.connect(self.runInr)
        self.btnReptable_2.clicked.connect(self.runInr)
        self.btnReptable_3.clicked.connect(self.runInr)

        self.btnMedtable.clicked.connect(self.runImageViewer)
        self.btnExptable.clicked.connect(self.runImages_directory_export)

        self.btnPDFmen.clicked.connect(self.runPDFadministrator)
        self.btnUTtable.clicked.connect(self.runUT)

        # Setup tooltips
        self.setup_button_tooltips()

    def runSite(self):
        pluginGui = pyarchinit_Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runPer(self):
        pluginGui = pyarchinit_Periodizzazione(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runStruttura(self):
        pluginGui = pyarchinit_Struttura(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runUS(self):
        pluginGui = pyarchinit_US(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runInr(self):
        pluginGui = pyarchinit_Inventario_reperti(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runGisTimeController(self):
        pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runUpd(self):
        pluginGui = pyarchinit_Upd_Values(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runConf(self):
        pluginConfGui = pyArchInitDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui

    def runInfo(self):
        pluginInfoGui = pyArchInitDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui

    def runImageViewer(self):
        pluginImageView = Main()
        pluginImageView.show()
        self.pluginGui = pluginImageView

    def runImages_directory_export(self):
        pluginImage_directory_export = pyarchinit_Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export

    def runTomba(self):
        pluginTomba = pyarchinit_Tomba(self.iface)
        pluginTomba.show()
        self.pluginGui = pluginTomba

    def runSchedaind(self):
        pluginIndividui = pyarchinit_Schedaind(self.iface)
        pluginIndividui.show()
        self.pluginGui = pluginIndividui

    def runDetsesso(self):
        pluginSesso = pyarchinit_Detsesso(self.iface)
        pluginSesso.show()
        self.pluginGui = pluginSesso

    def runDeteta(self):
        pluginEta = pyarchinit_Deteta(self.iface)
        pluginEta.show()
        self.pluginGui = pluginEta

    def runUT(self):
        pluginUT = pyarchinit_UT(self.iface)
        pluginUT.show()
        self.pluginGui = pluginUT

    def runPDFadministrator(self):
        pluginPDFadmin = pyarchinit_pdf_export(self.iface)
        pluginPDFadmin.show()
        self.pluginGui = pluginPDFadmin

    def detect_language(self):
        """Detect QGIS locale and return language code"""
        locale = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if locale in self.SUPPORTED_LANGUAGES:
            return locale
        return 'it'

    def get_icon(self, icon_name):
        """Get QIcon from resources/icons folder"""
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icons', icon_name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def remove_old_tabs(self):
        """Remove old tabs that are replaced by workflow tabs"""
        # Find and remove tabs by their object names
        tabs_to_remove = ['services', 'tab', 'tab_2', 'tab_3', 'account']

        # We need to remove tabs by index, so we'll find them first
        indices_to_remove = []
        for i in range(self.tabWidget.count()):
            widget = self.tabWidget.widget(i)
            if widget and widget.objectName() in tabs_to_remove:
                indices_to_remove.append(i)

        # Remove in reverse order to maintain correct indices
        for index in sorted(indices_to_remove, reverse=True):
            self.tabWidget.removeTab(index)

    def setup_button_tooltips(self):
        """Setup descriptive tooltips for relationship diagram buttons"""
        tooltips = {
            'it': {
                'site': 'Scheda Sito\n━━━━━━━━━━━\nTabella principale del sito archeologico\n\nRelazioni:\n• 1:N → US/USM\n• 1:N → Periodizzazione\n• 1:N → UT',
                'us': 'Scheda US/USM\n━━━━━━━━━━━━\nUnità Stratigrafiche e Murarie\n\nRelazioni:\n• N:1 ← Sito\n• 1:N → Reperti\n• N:N ↔ Struttura',
                'periodo': 'Periodizzazione\n━━━━━━━━━━━━\nFasi e periodi cronologici\n\nRelazioni:\n• N:1 ← Sito\n• 1:N → US/USM',
                'struttura': 'Scheda Struttura\n━━━━━━━━━━━━━━\nStrutture archeologiche\n\nRelazioni:\n• N:N ↔ US/USM',
                'reperti': 'Inventario Materiali\n━━━━━━━━━━━━━━━━\nReperti archeologici\n\nRelazioni:\n• N:1 ← US/USM\n• N:N ↔ Media',
                'ut': 'Scheda UT\n━━━━━━━━━\nUnità Topografiche\n\nRelazioni:\n• N:1 ← Sito\n• 1:N → Reperti',
                'media': 'Media Manager\n━━━━━━━━━━━━\nGestione foto e documenti',
                'export': 'Export Immagini',
                'pdf': 'PDF Export'
            },
            'en': {
                'site': 'Site Form\n━━━━━━━━━\nMain site table\n\nRelationships:\n• 1:N → SU/WSU\n• 1:N → Periodization\n• 1:N → TU',
                'us': 'SU/WSU Form\n━━━━━━━━━━━\nStratigraphic Units\n\nRelationships:\n• N:1 ← Site\n• 1:N → Finds\n• N:N ↔ Structure',
                'periodo': 'Periodization\n━━━━━━━━━━━━\nChronological phases\n\nRelationships:\n• N:1 ← Site\n• 1:N → SU/WSU',
                'struttura': 'Structure Form\n━━━━━━━━━━━━━\nArchaeological structures\n\nRelationships:\n• N:N ↔ SU/WSU',
                'reperti': 'Finds Inventory\n━━━━━━━━━━━━━━\nArtefacts\n\nRelationships:\n• N:1 ← SU/WSU\n• N:N ↔ Media',
                'ut': 'TU Form\n━━━━━━━━\nTopographic Units\n\nRelationships:\n• N:1 ← Site\n• 1:N → Finds',
                'media': 'Media Manager\n━━━━━━━━━━━━\nPhoto management',
                'export': 'Image Export',
                'pdf': 'PDF Export'
            }
        }

        tips = tooltips.get(self.current_lang, tooltips['it'])

        self.btnSitotable.setToolTip(tips['site'])
        self.btnSitotable_2.setToolTip(tips['site'])
        self.btnUStable.setToolTip(tips['us'])
        self.btnUStable_2.setToolTip(tips['us'])
        self.btnPeriodotable.setToolTip(tips['periodo'])
        self.btnStrutturatable.setToolTip(tips['struttura'])
        self.btnReptable.setToolTip(tips['reperti'])
        self.btnReptable_2.setToolTip(tips['reperti'])
        self.btnReptable_3.setToolTip(tips['reperti'])
        self.btnUTtable.setToolTip(tips['ut'])
        self.btnMedtable.setToolTip(tips['media'])
        self.btnExptable.setToolTip(tips['export'])
        self.btnPDFmen.setToolTip(tips['pdf'])

    def setup_webviews(self):
        """Setup pyarchinit.org in the main tab"""
        if HAS_WEBENGINE:
            parent_widget = self.webView_adarte.parentWidget()
            layout = parent_widget.layout()
            self.web_engine_pyarchinit = _DockWebViewClass()
            self.web_engine_pyarchinit.setUrl(QUrl("https://www.pyarchinit.org"))
            layout.replaceWidget(self.webView_adarte, self.web_engine_pyarchinit)
            self.webView_adarte.deleteLater()
            self.webView_adarte = self.web_engine_pyarchinit
        else:
            self.webView_adarte.setHtml(self.get_pyarchinit_fallback_html())
            self.webView_adarte.setOpenExternalLinks(True)

    def setup_tutorial_tab(self):
        """Setup embedded tutorial viewer in tutorial tab"""
        # Get the tutorial tab (tab_4) and its layout
        parent_widget = self.webView.parentWidget()
        layout = parent_widget.layout()

        # Create new container widget for tutorial viewer
        tutorial_container = QWidget()
        tutorial_layout = QVBoxLayout(tutorial_container)
        tutorial_layout.setContentsMargins(5, 5, 5, 5)
        tutorial_layout.setSpacing(5)

        # Language selector
        lang_layout = QHBoxLayout()
        lang_label = QLabel("🌍")
        self.tutorial_lang_combo = QComboBox()
        self.tutorial_lang_combo.setMaximumWidth(120)
        for code, name in self.SUPPORTED_LANGUAGES.items():
            self.tutorial_lang_combo.addItem(name, code)
        index = self.tutorial_lang_combo.findData(self.current_lang)
        if index >= 0:
            self.tutorial_lang_combo.setCurrentIndex(index)
        self.tutorial_lang_combo.currentIndexChanged.connect(self.on_tutorial_language_changed)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.tutorial_lang_combo)
        lang_layout.addStretch()
        tutorial_layout.addLayout(lang_layout)

        # Splitter for list and content
        self.tutorial_splitter = QSplitter(Qt.Orientation.Vertical)

        # Tutorial list
        self.tutorial_list = QListWidget()
        self.tutorial_list.setMaximumHeight(250)
        self.tutorial_list.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-size: 11px;
                color: #333333;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #e9ecef;
                color: #333333;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
            QListWidget::item:hover:!selected {
                background: #e9ecef;
                color: #333333;
            }
        """)
        self.tutorial_list.currentItemChanged.connect(self.on_tutorial_selected)
        self.tutorial_splitter.addWidget(self.tutorial_list)

        # Content: QStackedWidget with QTextBrowser (page 0) + QWebEngineView (page 1)
        self.tutorial_content_stack = QStackedWidget()

        # Page 0: QTextBrowser — always used for markdown
        self.tutorial_content = QTextBrowser()
        self.tutorial_content.setOpenExternalLinks(False)
        self.tutorial_content.setOpenLinks(False)
        self.tutorial_content.anchorClicked.connect(self._on_tutorial_link_clicked)
        self.tutorial_content_stack.addWidget(self.tutorial_content)  # index 0

        # Page 1: QWebEngineView — for HTML5 animations (if available)
        self.tutorial_animation = None
        if HAS_WEBENGINE:
            self.tutorial_animation = _DockWebViewClass()
            self.tutorial_content_stack.addWidget(self.tutorial_animation)  # index 1
            _dock_log("Tutorial animation viewer (QWebEngineView) ready as stack page 1")

        self.tutorial_content_stack.setCurrentIndex(0)
        self.tutorial_splitter.addWidget(self.tutorial_content_stack)

        # Set splitter sizes
        self.tutorial_splitter.setSizes([150, 400])

        tutorial_layout.addWidget(self.tutorial_splitter)

        # Back button (hidden by default, shown when viewing an animation)
        self.tutorial_back_button = QPushButton("← Indietro")
        self.tutorial_back_button.setVisible(False)
        self.tutorial_back_button.setStyleSheet(
            "QPushButton { background: #667eea; color: white; border: none; "
            "padding: 6px 14px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background: #764ba2; }")
        self.tutorial_back_button.clicked.connect(self._on_tutorial_back)
        tutorial_layout.addWidget(self.tutorial_back_button)

        # Replace old webView with new container
        layout.replaceWidget(self.webView, tutorial_container)
        self.webView.deleteLater()
        self.webView = tutorial_container

        # Load tutorial list
        self.load_tutorial_list()

    def load_tutorial_list(self):
        """Load tutorials for current language"""
        self.tutorial_list.clear()
        tutorials = self.TUTORIALS_METADATA.get(self.current_lang, self.TUTORIALS_METADATA['it'])

        for filename, title, description in tutorials:
            item = QListWidgetItem(f"📖 {title}")
            item.setToolTip(description)
            item.setData(Qt.ItemDataRole.UserRole, filename)
            self.tutorial_list.addItem(item)

        # Select first item
        if self.tutorial_list.count() > 0:
            self.tutorial_list.setCurrentRow(0)

    def on_tutorial_language_changed(self, index):
        """Handle tutorial language change"""
        self.current_lang = self.tutorial_lang_combo.itemData(index)
        self.load_tutorial_list()

    def on_tutorial_selected(self, current, previous):
        """Load selected tutorial content"""
        if current is None:
            return

        filename = current.data(Qt.ItemDataRole.UserRole)
        tutorials_path = os.path.join(self.tutorials_base_path, self.current_lang)
        filepath = os.path.join(tutorials_path, filename)

        # Fallback to Italian
        if not os.path.exists(filepath):
            tutorials_path = os.path.join(self.tutorials_base_path, 'it')
            filepath = os.path.join(tutorials_path, filename)

        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Store the tutorial directory for image path resolution
                self.current_tutorial_dir = tutorials_path
                html = self.markdown_to_html(content, tutorials_path)
                # Ensure we're showing the markdown page (not animation)
                self.tutorial_content_stack.setCurrentIndex(0)
                self.tutorial_back_button.setVisible(False)
                self.tutorial_content.setHtml(html)
            except Exception as e:
                self.show_tutorial_error(str(e))
        else:
            self.show_tutorial_placeholder()

    def markdown_to_html(self, md_content, base_path=None):
        """Convert markdown to styled HTML with proper image handling"""
        import re
        import base64

        # Basic markdown conversion
        html = md_content

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Code blocks
        html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\n)+', r'<ul>\g<0></ul>', html)

        # Images - handle before links to avoid conflicts
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)

            # Convert images to base64 for QTextBrowser rendering
            if base_path:
                # Resolve relative path
                if not os.path.isabs(img_path):
                    abs_path = os.path.normpath(os.path.join(base_path, img_path))
                else:
                    abs_path = img_path

                if os.path.exists(abs_path):
                    try:
                        # Determine mime type
                        ext = os.path.splitext(abs_path)[1].lower()
                        mime_types = {
                            '.png': 'image/png',
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.gif': 'image/gif',
                            '.webp': 'image/webp'
                        }
                        mime_type = mime_types.get(ext, 'image/png')

                        # Read and encode image
                        with open(abs_path, 'rb') as f:
                            img_data = base64.b64encode(f.read()).decode('utf-8')

                        return f'<div style="text-align:center; margin: 15px 0;"><img src="data:{mime_type};base64,{img_data}" alt="{alt_text}" style="max-width:100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"><p style="color:#666; font-size:12px; margin-top:5px;"><em>{alt_text}</em></p></div>'
                    except Exception:
                        pass

            # Fallback: use relative path (won't display in QTextBrowser but harmless)
            return f'<div style="text-align:center; margin: 15px 0;"><img src="{img_path}" alt="{alt_text}" style="max-width:100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"><p style="color:#666; font-size:12px; margin-top:5px;"><em>{alt_text}</em></p></div>'

        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, html)

        # Links (after images to avoid capturing image syntax)
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)

        direction = 'rtl' if self.current_lang == 'ar' else 'ltr'

        return f"""
        <!DOCTYPE html>
        <html dir="{direction}">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 13px;
                    line-height: 1.6;
                    padding: 15px;
                    background: #fff;
                    color: #333;
                    direction: {direction};
                }}
                h1 {{ color: #667eea; font-size: 20px; border-bottom: 2px solid #667eea; padding-bottom: 8px; }}
                h2 {{ color: #764ba2; font-size: 16px; margin-top: 20px; }}
                h3 {{ color: #555; font-size: 14px; }}
                code {{ background: #f1f3f4; padding: 2px 6px; border-radius: 4px; font-family: 'Consolas', monospace; }}
                pre {{ background: #282c34; color: #abb2bf; padding: 12px; border-radius: 8px; overflow-x: auto; }}
                pre code {{ background: none; color: inherit; }}
                a {{ color: #667eea; }}
                ul {{ padding-left: 20px; }}
                li {{ margin: 5px 0; }}
                img {{ max-width: 100%; }}
            </style>
        </head>
        <body><p>{html}</p></body>
        </html>
        """

    def show_tutorial_placeholder(self):
        """Show placeholder when tutorial not found"""
        html = """
        <html>
        <body style="font-family: sans-serif; padding: 20px; text-align: center; color: #666;">
            <p style="font-size: 40px;">📚</p>
            <p>Tutorial not available yet.</p>
            <p><a href="https://pyarchinitdoc.readthedocs.io/" target="_blank">View online documentation</a></p>
        </body>
        </html>
        """
        self.tutorial_content.setHtml(html)

    def show_tutorial_error(self, error):
        """Show error message"""
        html = f"<html><body><p style='color:red;'>Error: {error}</p></body></html>"
        self.tutorial_content.setHtml(html)

    def _on_tutorial_link_clicked(self, url):
        """Handle link clicks in QTextBrowser — load .html animations in embedded viewer."""
        url_str = url.toString()

        # Resolve relative paths using current tutorial directory
        if not url.scheme() or url.scheme() == 'file':
            if hasattr(self, 'current_tutorial_dir') and self.current_tutorial_dir:
                relative_path = url.toLocalFile() or url_str
                abs_path = os.path.normpath(os.path.join(self.current_tutorial_dir, relative_path))
                if os.path.isfile(abs_path):
                    # If it's an HTML file, try to load in embedded animation viewer
                    if abs_path.lower().endswith('.html') and self.tutorial_animation is not None:
                        self._load_animation_in_viewer(abs_path)
                        return
                    # Otherwise open in system browser
                    import webbrowser
                    webbrowser.open(f'file://{abs_path}')
                    return

        # External URLs
        import webbrowser
        webbrowser.open(url_str)

    def _load_animation_in_viewer(self, file_path):
        """Load a local HTML animation file into the embedded QWebEngineView."""
        self.tutorial_back_button.setVisible(True)
        self.tutorial_animation.setUrl(QUrl.fromLocalFile(file_path))
        self.tutorial_content_stack.setCurrentIndex(1)

    def _on_tutorial_back(self):
        """Go back to the current tutorial from an animation view."""
        self.tutorial_back_button.setVisible(False)
        self.tutorial_content_stack.setCurrentIndex(0)
        # Stop any ongoing load in the animation viewer
        if self.tutorial_animation is not None:
            self.tutorial_animation.setUrl(QUrl('about:blank'))

    def setup_workflow_tabs(self):
        """Create new tabs with interactive workflow diagrams"""
        # Labels for different languages
        labels = {
            'it': {
                'excavation': 'Scavo',
                'survey': 'Ricognizione',
                'anthropology': 'Antropologia',
                'site': 'Sito', 'us': 'US/USM', 'period': 'Periodizzazione',
                'struct': 'Struttura', 'tomb': 'Tomba', 'finds': 'Reperti',
                'samples': 'Campioni', 'indiv': 'Individui', 'doc': 'Documentazione',
                'ut': 'UT', 'media': 'Media', 'sex': 'Det. Sesso', 'age': 'Det. Età',
                'pdf': 'PDF Export', 'pottery': 'Ceramica', 'fauna': 'Archeozoologia'
            },
            'en': {
                'excavation': 'Excavation',
                'survey': 'Survey',
                'anthropology': 'Anthropology',
                'site': 'Site', 'us': 'SU/WSU', 'period': 'Periodization',
                'struct': 'Structure', 'tomb': 'Burial', 'finds': 'Finds',
                'samples': 'Samples', 'indiv': 'Individuals', 'doc': 'Documentation',
                'ut': 'TU', 'media': 'Media', 'sex': 'Sex Det.', 'age': 'Age Det.',
                'pdf': 'PDF Export', 'pottery': 'Pottery', 'fauna': 'Archaeozoology'
            },
            'de': {
                'excavation': 'Grabung',
                'survey': 'Survey',
                'anthropology': 'Anthropologie',
                'site': 'Fundstelle', 'us': 'SE/MSE', 'period': 'Periodisierung',
                'struct': 'Struktur', 'tomb': 'Grab', 'finds': 'Funde',
                'samples': 'Proben', 'indiv': 'Individuen', 'doc': 'Dokumentation',
                'ut': 'TE', 'media': 'Medien', 'sex': 'Geschlecht', 'age': 'Alter',
                'pdf': 'PDF-Export', 'pottery': 'Keramik', 'fauna': 'Archäozoologie'
            }
        }
        l = labels.get(self.current_lang, labels['it'])

        # Icon mapping
        icons = {
            'site': self.get_icon('iconSite.png'),
            'us': self.get_icon('iconsus.png'),
            'period': self.get_icon('iconPER.png'),
            'struct': self.get_icon('iconStrutt.png'),
            'tomb': self.get_icon('iconGrave.png'),
            'finds': self.get_icon('iconFinds.png'),
            'samples': self.get_icon('champion.png'),
            'indiv': self.get_icon('iconIND.png'),
            'doc': self.get_icon('icondoc.png'),
            'media': self.get_icon('photo.png'),
            'pdf': self.get_icon('pdf-icon.png'),
            'ut': self.get_icon('iconUT.png'),
            'sex': self.get_icon('iconSex.png'),
            'age': self.get_icon('iconEta.png'),
            'pottery': self.get_icon('pottery.png'),
            'fauna': self.get_icon('iconZoo.png'),
            'excavation': self.get_icon('pai_us.png'),
            'anthropology': self.get_icon('iconIND.png'),
            'survey': self.get_icon('site_point.png'),
        }

        icon_size = QSize(24, 24)

        # Common button style
        btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                border: none; border-radius: 8px; padding: 10px 15px;
                color: white; font-weight: bold; font-size: 11px;
                min-width: 100px; min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #5a6fd6, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4e5fc2, stop:1 #5e3780);
            }
        """

        btn_style_main = btn_style.replace('#667eea', '#f093fb').replace('#764ba2', '#f5576c').replace('#5a6fd6', '#e080e8').replace('#6a4190', '#e04a5e').replace('#4e5fc2', '#d070d8').replace('#5e3780', '#d03e50')
        btn_style_secondary = btn_style.replace('#667eea', '#4facfe').replace('#764ba2', '#00f2fe').replace('#5a6fd6', '#3d9ae8').replace('#6a4190', '#00d8e8').replace('#4e5fc2', '#2b88d8').replace('#5e3780', '#00bed8')
        btn_style_tertiary = btn_style.replace('#667eea', '#43e97b').replace('#764ba2', '#38f9d7').replace('#5a6fd6', '#35d56b').replace('#6a4190', '#2ee0c5').replace('#4e5fc2', '#28c15b').replace('#5e3780', '#25c8b3')

        arrow_style = "QLabel { color: #667eea; font-size: 18px; font-weight: bold; background: transparent; }"
        rel_style = "QLabel { background: rgba(102,126,234,0.15); color: #667eea; font-size: 9px; font-weight: bold; padding: 3px 8px; border-radius: 10px; }"
        title_style = "QLabel { color: #333; font-size: 14px; font-weight: bold; background: transparent; padding: 10px; }"

        def create_button(label_key, style, tooltip=""):
            """Helper to create button with icon"""
            btn = QPushButton(l[label_key])
            btn.setIcon(icons.get(label_key, QIcon()))
            btn.setIconSize(icon_size)
            btn.setStyleSheet(style)
            if tooltip:
                btn.setToolTip(tooltip)
            return btn

        # ========== TAB 1: SCAVO (Excavation) ==========
        excavation_tab = QWidget()
        excavation_layout = QVBoxLayout(excavation_tab)
        excavation_layout.setSpacing(8)
        excavation_layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title1 = QLabel(f"{l['excavation']} Workflow")
        title1.setStyleSheet(title_style)
        title1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        excavation_layout.addWidget(title1)

        # Row 1: Site
        row1 = QHBoxLayout()
        row1.addStretch()
        btn_site = create_button('site', btn_style_main, "1:N → US, Periodo, UT")
        btn_site.clicked.connect(self.runSite)
        row1.addWidget(btn_site)
        row1.addStretch()
        excavation_layout.addLayout(row1)

        # Arrow
        arr1 = QLabel("↓")
        arr1.setStyleSheet(arrow_style)
        arr1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        excavation_layout.addWidget(arr1)

        # Row 2: Period, US, Structure
        row2 = QHBoxLayout()
        row2.addStretch()

        btn_period = create_button('period', btn_style)
        btn_period.clicked.connect(self.runPer)
        row2.addWidget(btn_period)

        lbl_rel1 = QLabel("1:N")
        lbl_rel1.setStyleSheet(rel_style)
        row2.addWidget(lbl_rel1)

        btn_us = create_button('us', btn_style_secondary)
        btn_us.clicked.connect(self.runUS)
        row2.addWidget(btn_us)

        lbl_rel2 = QLabel("N:N")
        lbl_rel2.setStyleSheet(rel_style)
        row2.addWidget(lbl_rel2)

        btn_struct = create_button('struct', btn_style)
        btn_struct.clicked.connect(self.runStruttura)
        row2.addWidget(btn_struct)

        row2.addStretch()
        excavation_layout.addLayout(row2)

        # Arrow
        arr2 = QLabel("↓")
        arr2.setStyleSheet(arrow_style)
        arr2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        excavation_layout.addWidget(arr2)

        # Row 3: Finds, Samples, Tomb
        row3 = QHBoxLayout()
        row3.addStretch()

        btn_finds = create_button('finds', btn_style_tertiary)
        btn_finds.clicked.connect(self.runInr)
        row3.addWidget(btn_finds)

        btn_samples = create_button('samples', btn_style_tertiary)
        btn_samples.clicked.connect(self.runInr)  # TODO: connect to samples form
        row3.addWidget(btn_samples)

        btn_tomb = create_button('tomb', btn_style_tertiary)
        btn_tomb.clicked.connect(self.runTomba)
        row3.addWidget(btn_tomb)

        row3.addStretch()
        excavation_layout.addLayout(row3)

        # Arrow
        arr3 = QLabel("↓")
        arr3.setStyleSheet(arrow_style)
        arr3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        excavation_layout.addWidget(arr3)

        # Row 4: Documentation, Media
        row4 = QHBoxLayout()
        row4.addStretch()

        btn_doc = create_button('doc', btn_style)
        btn_doc.clicked.connect(self.runImageViewer)
        row4.addWidget(btn_doc)

        btn_media = create_button('media', btn_style)
        btn_media.clicked.connect(self.runImageViewer)
        row4.addWidget(btn_media)

        btn_pdf = create_button('pdf', btn_style)
        btn_pdf.clicked.connect(self.runPDFadministrator)
        row4.addWidget(btn_pdf)

        row4.addStretch()
        excavation_layout.addLayout(row4)

        excavation_layout.addStretch()
        self.tabWidget.addTab(excavation_tab, icons['excavation'], l['excavation'])

        # ========== TAB 2: ANTROPOLOGIA (Anthropology) ==========
        anthro_tab = QWidget()
        anthro_layout = QVBoxLayout(anthro_tab)
        anthro_layout.setSpacing(8)
        anthro_layout.setContentsMargins(10, 10, 10, 10)

        title2 = QLabel(f"{l['anthropology']} Workflow")
        title2.setStyleSheet(title_style)
        title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anthro_layout.addWidget(title2)

        # Row 1: Site
        arow1 = QHBoxLayout()
        arow1.addStretch()
        abtn_site = create_button('site', btn_style_main)
        abtn_site.clicked.connect(self.runSite)
        arow1.addWidget(abtn_site)
        arow1.addStretch()
        anthro_layout.addLayout(arow1)

        aarr1 = QLabel("↓")
        aarr1.setStyleSheet(arrow_style)
        aarr1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anthro_layout.addWidget(aarr1)

        # Row 2: US -> Tomb
        arow2 = QHBoxLayout()
        arow2.addStretch()

        abtn_us = create_button('us', btn_style_secondary)
        abtn_us.clicked.connect(self.runUS)
        arow2.addWidget(abtn_us)

        albl1 = QLabel("1:N")
        albl1.setStyleSheet(rel_style)
        arow2.addWidget(albl1)

        abtn_tomb = create_button('tomb', btn_style_tertiary)
        abtn_tomb.clicked.connect(self.runTomba)
        arow2.addWidget(abtn_tomb)

        arow2.addStretch()
        anthro_layout.addLayout(arow2)

        aarr2 = QLabel("↓")
        aarr2.setStyleSheet(arrow_style)
        aarr2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anthro_layout.addWidget(aarr2)

        # Row 3: Individuals
        arow3 = QHBoxLayout()
        arow3.addStretch()

        abtn_indiv = create_button('indiv', btn_style_main)
        abtn_indiv.clicked.connect(self.runSchedaind)
        arow3.addWidget(abtn_indiv)

        arow3.addStretch()
        anthro_layout.addLayout(arow3)

        aarr3 = QLabel("↓")
        aarr3.setStyleSheet(arrow_style)
        aarr3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anthro_layout.addWidget(aarr3)

        # Row 4: Sex, Age determination
        arow4 = QHBoxLayout()
        arow4.addStretch()

        abtn_sex = create_button('sex', btn_style)
        abtn_sex.clicked.connect(self.runDetsesso)
        arow4.addWidget(abtn_sex)

        abtn_age = create_button('age', btn_style)
        abtn_age.clicked.connect(self.runDeteta)
        arow4.addWidget(abtn_age)

        arow4.addStretch()
        anthro_layout.addLayout(arow4)

        aarr4 = QLabel("↓")
        aarr4.setStyleSheet(arrow_style)
        aarr4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anthro_layout.addWidget(aarr4)

        # Row 5: Finds (grave goods)
        arow5 = QHBoxLayout()
        arow5.addStretch()

        abtn_finds = create_button('finds', btn_style_tertiary)
        abtn_finds.clicked.connect(self.runInr)
        arow5.addWidget(abtn_finds)

        arow5.addStretch()
        anthro_layout.addLayout(arow5)

        anthro_layout.addStretch()
        self.tabWidget.addTab(anthro_tab, icons['anthropology'], l['anthropology'])

        # ========== TAB 3: RICOGNIZIONE (Survey) ==========
        survey_tab = QWidget()
        survey_layout = QVBoxLayout(survey_tab)
        survey_layout.setSpacing(8)
        survey_layout.setContentsMargins(10, 10, 10, 10)

        title3 = QLabel(f"{l['survey']} Workflow")
        title3.setStyleSheet(title_style)
        title3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        survey_layout.addWidget(title3)

        # Row 1: Site
        srow1 = QHBoxLayout()
        srow1.addStretch()
        sbtn_site = create_button('site', btn_style_main)
        sbtn_site.clicked.connect(self.runSite)
        srow1.addWidget(sbtn_site)
        srow1.addStretch()
        survey_layout.addLayout(srow1)

        sarr1 = QLabel("↓ 1:N")
        sarr1.setStyleSheet(arrow_style)
        sarr1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        survey_layout.addWidget(sarr1)

        # Row 2: UT
        srow2 = QHBoxLayout()
        srow2.addStretch()

        sbtn_ut = create_button('ut', btn_style_secondary)
        sbtn_ut.clicked.connect(self.runUT)
        srow2.addWidget(sbtn_ut)

        srow2.addStretch()
        survey_layout.addLayout(srow2)

        sarr2 = QLabel("↓ 1:N")
        sarr2.setStyleSheet(arrow_style)
        sarr2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        survey_layout.addWidget(sarr2)

        # Row 3: Finds
        srow3 = QHBoxLayout()
        srow3.addStretch()

        sbtn_finds = create_button('finds', btn_style_tertiary)
        sbtn_finds.clicked.connect(self.runInr)
        srow3.addWidget(sbtn_finds)

        srow3.addStretch()
        survey_layout.addLayout(srow3)

        sarr3 = QLabel("↓")
        sarr3.setStyleSheet(arrow_style)
        sarr3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        survey_layout.addWidget(sarr3)

        # Row 4: Documentation
        srow4 = QHBoxLayout()
        srow4.addStretch()

        sbtn_doc = create_button('doc', btn_style)
        sbtn_doc.clicked.connect(self.runImageViewer)
        srow4.addWidget(sbtn_doc)

        sbtn_pdf = create_button('pdf', btn_style)
        sbtn_pdf.clicked.connect(self.runPDFadministrator)
        srow4.addWidget(sbtn_pdf)

        srow4.addStretch()
        survey_layout.addLayout(srow4)

        survey_layout.addStretch()
        self.tabWidget.addTab(survey_tab, icons['survey'], l['survey'])

    def setup_modern_diagrams(self):
        """Setup modern HTML diagrams in service tabs"""
        # Apply modern styling to service tab buttons
        modern_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 8px;
                padding: 8px;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a6fd6, stop:1 #6a4190);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4e5fc2, stop:1 #5e3780);
            }
        """

        # Apply to all main buttons
        for btn in [self.btnSitotable, self.btnSitotable_2, self.btnUStable, self.btnUStable_2,
                    self.btnPeriodotable, self.btnStrutturatable, self.btnReptable,
                    self.btnReptable_2, self.btnReptable_3, self.btnUTtable,
                    self.btnMedtable, self.btnExptable, self.btnPDFmen]:
            btn.setStyleSheet(modern_button_style)

        # Style the relationship labels for better visibility
        label_style = """
            QLabel {
                background: rgba(102, 126, 234, 0.15);
                border-radius: 4px;
                padding: 2px 6px;
                font-weight: bold;
                color: #667eea;
                font-size: 9px;
            }
        """

        # Apply to relationship labels
        for widget in self.findChildren(QLabel):
            text = widget.text()
            if text in ['1:N', 'N:N', 'N:1', '1:1']:
                widget.setStyleSheet(label_style)

        # Style section titles
        title_style = """
            QLabel {
                color: #333333;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                background: transparent;
            }
        """
        for widget in self.findChildren(QLabel):
            text = widget.text()
            if text in ['Scavo Archeologico', 'Ricognizione del territorio', 'Supporto online']:
                widget.setStyleSheet(title_style)

        # Style the tab widget
        tab_style = """
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: #f8f9fa;
            }
            QTabBar::tab {
                background: #e9ecef;
                border: 1px solid #dee2e6;
                padding: 6px 10px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #333333;
                font-size: 10px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #dee2e6;
            }
        """
        self.tabWidget.setStyleSheet(tab_style)

    def get_pyarchinit_fallback_html(self):
        """Return HTML content for when QWebEngine is not available"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    max-width: 400px;
                    padding: 40px;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                }
                h1 { color: #333; margin-bottom: 10px; }
                p { color: #666; }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 15px 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 30px;
                    font-weight: bold;
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                a:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                }
                .logo { font-size: 60px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">🏛️</div>
                <h1>pyArchInit</h1>
                <p>Archaeological Data Management System</p>
                <a href="https://www.pyarchinit.org" target="_blank">
                    Visit pyarchinit.org
                </a>
            </div>
        </body>
        </html>
        """
