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
from qgis.PyQt.QtCore import QUrl, Qt
from qgis.PyQt.QtWidgets import (QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
                                  QTextBrowser, QSplitter, QComboBox, QLabel, QWidget)
from qgis.gui import QgsDockWidget
from qgis.core import QgsSettings

# Try to import QWebEngineView for better web rendering
try:
    from qgis.PyQt.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

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
            self.web_engine_pyarchinit = QWebEngineView()
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

        # Content browser
        if HAS_WEBENGINE:
            self.tutorial_content = QWebEngineView()
        else:
            self.tutorial_content = QTextBrowser()
            self.tutorial_content.setOpenExternalLinks(True)
        self.tutorial_splitter.addWidget(self.tutorial_content)

        # Set splitter sizes
        self.tutorial_splitter.setSizes([150, 400])

        tutorial_layout.addWidget(self.tutorial_splitter)

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
            filepath = os.path.join(self.tutorials_base_path, 'it', filename)

        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                html = self.markdown_to_html(content)
                if HAS_WEBENGINE:
                    self.tutorial_content.setHtml(html, QUrl.fromLocalFile(tutorials_path + '/'))
                else:
                    self.tutorial_content.setHtml(html)
            except Exception as e:
                self.show_tutorial_error(str(e))
        else:
            self.show_tutorial_placeholder()

    def markdown_to_html(self, md_content):
        """Convert markdown to styled HTML"""
        import re

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

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Images
        html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1" style="max-width:100%">', html)

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
                img {{ border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0; }}
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
        if HAS_WEBENGINE:
            self.tutorial_content.setHtml(html)
        else:
            self.tutorial_content.setHtml(html)

    def show_tutorial_error(self, error):
        """Show error message"""
        html = f"<html><body><p style='color:red;'>Error: {error}</p></body></html>"
        if HAS_WEBENGINE:
            self.tutorial_content.setHtml(html)
        else:
            self.tutorial_content.setHtml(html)

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

        # Add workflow diagram to services tab
        self.add_workflow_to_services_tab()

    def add_workflow_to_services_tab(self):
        """Add a visual workflow diagram header to the services tab"""
        # Find the services tab (Scavo archeologico)
        services_tab = self.services
        if services_tab:
            # Get the existing layout
            existing_layout = services_tab.layout()
            if existing_layout:
                # Create workflow browser
                workflow_browser = QTextBrowser()
                workflow_browser.setMaximumHeight(180)
                workflow_browser.setOpenExternalLinks(False)
                workflow_browser.setStyleSheet("""
                    QTextBrowser {
                        border: none;
                        background: transparent;
                    }
                """)
                workflow_browser.setHtml(self.get_excavation_workflow_html())

                # Insert at the top of the layout
                existing_layout.insertWidget(0, workflow_browser)

        # Add workflow to Ricognizione tab
        ricognizione_tab = self.tab
        if ricognizione_tab:
            existing_layout = ricognizione_tab.layout()
            if existing_layout:
                workflow_browser = QTextBrowser()
                workflow_browser.setMaximumHeight(150)
                workflow_browser.setStyleSheet("QTextBrowser { border: none; background: transparent; }")
                workflow_browser.setHtml(self.get_survey_workflow_html())
                existing_layout.insertWidget(0, workflow_browser)

        # Add workflow to Media tab
        media_tab = self.tab_2
        if media_tab:
            layout = media_tab.layout()
            if not layout:
                layout = QVBoxLayout(media_tab)
            workflow_browser = QTextBrowser()
            workflow_browser.setMaximumHeight(120)
            workflow_browser.setStyleSheet("QTextBrowser { border: none; background: transparent; }")
            workflow_browser.setHtml(self.get_media_workflow_html())
            layout.insertWidget(0, workflow_browser)

    def get_excavation_workflow_html(self):
        """Generate HTML workflow diagram for excavation"""
        labels = {
            'it': {'title': 'Flusso di Lavoro - Scavo', 'site': 'Sito', 'us': 'US/USM', 'period': 'Periodo',
                   'struct': 'Struttura', 'tomb': 'Tomba', 'finds': 'Reperti', 'samples': 'Campioni',
                   'indiv': 'Individui', 'doc': 'Documentazione'},
            'en': {'title': 'Excavation Workflow', 'site': 'Site', 'us': 'SU/WSU', 'period': 'Period',
                   'struct': 'Structure', 'tomb': 'Burial', 'finds': 'Finds', 'samples': 'Samples',
                   'indiv': 'Individuals', 'doc': 'Documentation'},
            'de': {'title': 'Grabungs-Workflow', 'site': 'Fundstelle', 'us': 'SE/MSE', 'period': 'Periode',
                   'struct': 'Struktur', 'tomb': 'Grab', 'finds': 'Funde', 'samples': 'Proben',
                   'indiv': 'Individuen', 'doc': 'Dokumentation'}
        }
        l = labels.get(self.current_lang, labels['it'])

        return f"""
        <html>
        <head><style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 8px; background: transparent; }}
            .workflow {{ display: flex; flex-direction: column; gap: 8px; }}
            .row {{ display: flex; align-items: center; justify-content: center; gap: 5px; flex-wrap: wrap; }}
            .node {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 6px 12px; border-radius: 20px; font-size: 10px;
                font-weight: 500; text-align: center; white-space: nowrap;
                box-shadow: 0 2px 8px rgba(102,126,234,0.3);
            }}
            .node.main {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
            .node.secondary {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
            .node.tertiary {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }}
            .arrow {{ color: #667eea; font-size: 14px; font-weight: bold; }}
            .rel {{ font-size: 8px; color: #764ba2; background: rgba(102,126,234,0.1);
                    padding: 2px 5px; border-radius: 8px; }}
            .title {{ font-size: 11px; font-weight: 600; color: #333; margin-bottom: 8px; text-align: center; }}
        </style></head>
        <body>
            <div class="title">{l['title']}</div>
            <div class="workflow">
                <div class="row">
                    <span class="node main">🏛️ {l['site']}</span>
                </div>
                <div class="row">
                    <span class="arrow">↓</span><span class="rel">1:N</span>
                </div>
                <div class="row">
                    <span class="node">📋 {l['period']}</span>
                    <span class="arrow">←</span>
                    <span class="node secondary">🔲 {l['us']}</span>
                    <span class="arrow">→</span>
                    <span class="node">🏗️ {l['struct']}</span>
                </div>
                <div class="row">
                    <span class="rel">1:N</span>
                    <span style="width:40px"></span>
                    <span class="arrow">↓</span><span class="rel">1:N</span>
                    <span style="width:40px"></span>
                    <span class="rel">N:N</span>
                </div>
                <div class="row">
                    <span class="node tertiary">⚱️ {l['finds']}</span>
                    <span class="node tertiary">🧪 {l['samples']}</span>
                    <span class="node tertiary">⚰️ {l['tomb']}</span>
                    <span class="node tertiary">👤 {l['indiv']}</span>
                </div>
                <div class="row">
                    <span class="arrow">↓</span>
                </div>
                <div class="row">
                    <span class="node" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333;">📸 {l['doc']}</span>
                </div>
            </div>
        </body>
        </html>
        """

    def get_survey_workflow_html(self):
        """Generate HTML workflow diagram for survey/reconnaissance"""
        labels = {
            'it': {'title': 'Flusso - Ricognizione', 'site': 'Sito', 'ut': 'UT', 'finds': 'Reperti'},
            'en': {'title': 'Survey Workflow', 'site': 'Site', 'ut': 'TU', 'finds': 'Finds'},
            'de': {'title': 'Survey-Workflow', 'site': 'Fundstelle', 'ut': 'TE', 'finds': 'Funde'}
        }
        l = labels.get(self.current_lang, labels['it'])

        return f"""
        <html>
        <head><style>
            body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 8px; background: transparent; }}
            .workflow {{ display: flex; flex-direction: column; align-items: center; gap: 6px; }}
            .node {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 6px 14px; border-radius: 20px; font-size: 10px;
                font-weight: 500; box-shadow: 0 2px 8px rgba(102,126,234,0.3);
            }}
            .arrow {{ color: #667eea; font-size: 12px; }}
            .rel {{ font-size: 8px; color: #764ba2; background: rgba(102,126,234,0.1); padding: 2px 5px; border-radius: 8px; }}
            .title {{ font-size: 11px; font-weight: 600; color: #333; margin-bottom: 6px; }}
        </style></head>
        <body>
            <div class="title">{l['title']}</div>
            <div class="workflow">
                <span class="node">🏛️ {l['site']}</span>
                <span class="arrow">↓</span><span class="rel">1:N</span>
                <span class="node">📍 {l['ut']}</span>
                <span class="arrow">↓</span><span class="rel">1:N</span>
                <span class="node">⚱️ {l['finds']}</span>
            </div>
        </body>
        </html>
        """

    def get_media_workflow_html(self):
        """Generate HTML workflow diagram for media management"""
        labels = {
            'it': {'title': 'Gestione Media', 'us': 'US/USM', 'finds': 'Reperti', 'media': 'Media'},
            'en': {'title': 'Media Management', 'us': 'SU/WSU', 'finds': 'Finds', 'media': 'Media'},
            'de': {'title': 'Medien-Verwaltung', 'us': 'SE/MSE', 'finds': 'Funde', 'media': 'Medien'}
        }
        l = labels.get(self.current_lang, labels['it'])

        return f"""
        <html>
        <head><style>
            body {{ font-family: -apple-system, sans-serif; margin: 0; padding: 8px; background: transparent; }}
            .row {{ display: flex; align-items: center; justify-content: center; gap: 8px; }}
            .node {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 5px 12px; border-radius: 15px; font-size: 10px;
                box-shadow: 0 2px 6px rgba(102,126,234,0.3);
            }}
            .arrow {{ color: #667eea; font-size: 12px; }}
            .rel {{ font-size: 8px; color: #764ba2; background: rgba(102,126,234,0.1); padding: 2px 5px; border-radius: 8px; }}
            .title {{ font-size: 11px; font-weight: 600; color: #333; margin-bottom: 8px; text-align: center; }}
        </style></head>
        <body>
            <div class="title">{l['title']}</div>
            <div class="row">
                <span class="node">🔲 {l['us']}</span>
                <span class="arrow">↔</span><span class="rel">N:N</span>
                <span class="node" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">📸 {l['media']}</span>
                <span class="arrow">↔</span><span class="rel">N:N</span>
                <span class="node">⚱️ {l['finds']}</span>
            </div>
        </body>
        </html>
        """

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
