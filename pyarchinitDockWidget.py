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
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QVBoxLayout
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
    SUPPORTED_LANGUAGES = ['it', 'en', 'de', 'fr', 'es', 'ar', 'ca']

    def __init__(self, iface):
        super(PyarchinitPluginDialog, self).__init__()
        self.setupUi(self)

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # Detect current language
        self.current_lang = self.detect_language()

        # Initialize web views
        self.setup_webviews()

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

        # Setup tooltips for relationship diagram buttons
        self.setup_button_tooltips()

    def runSite(self):
        pluginGui = pyarchinit_Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPer(self):
        pluginGui = pyarchinit_Periodizzazione(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runStruttura(self):
        pluginGui = pyarchinit_Struttura(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runUS(self):
        pluginGui = pyarchinit_US(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runInr(self):
        pluginGui = pyarchinit_Inventario_reperti(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runGisTimeController(self):
        pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runUpd(self):
        pluginGui = pyarchinit_Upd_Values(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runConf(self):
        pluginConfGui = pyArchInitDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save

    def runInfo(self):
        pluginInfoGui = pyArchInitDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui  # save

    def runImageViewer(self):
        pluginImageView = Main()
        pluginImageView.show()
        self.pluginGui = pluginImageView  # save

    def runImages_directory_export(self):
        pluginImage_directory_export = pyarchinit_Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export  # save

    def runTomba(self):
        pluginTomba = pyarchinit_Tomba(self.iface)
        pluginTomba.show()
        self.pluginGui = pluginTomba  # save

    def runSchedaind(self):
        pluginIndividui = pyarchinit_Schedaind(self.iface)
        pluginIndividui.show()
        self.pluginGui = pluginIndividui  # save

    def runDetsesso(self):
        pluginSesso = pyarchinit_Detsesso(self.iface)
        pluginSesso.show()
        self.pluginGui = pluginSesso  # save

    def runDeteta(self):
        pluginEta = pyarchinit_Deteta(self.iface)
        pluginEta.show()
        self.pluginGui = pluginEta  # save

    # def runArcheozoology(self):
        # pluginArchezoology = pyarchinit_Archeozoology(self.iface)
        # pluginArchezoology.show()
        # self.pluginGui = pluginArchezoology  # save

    def runUT(self):
        pluginUT = pyarchinit_UT(self.iface)
        pluginUT.show()
        self.pluginGui = pluginUT  # save

    def runPDFadministrator(self):
        pluginPDFadmin = pyarchinit_pdf_export(self.iface)
        pluginPDFadmin.show()
        self.pluginGui = pluginPDFadmin  # save

    def detect_language(self):
        """Detect QGIS locale and return language code"""
        locale = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if locale in self.SUPPORTED_LANGUAGES:
            return locale
        return 'it'  # Default to Italian

    def setup_button_tooltips(self):
        """Setup descriptive tooltips for relationship diagram buttons"""
        tooltips = {
            'it': {
                'site': 'Scheda Sito\n━━━━━━━━━━━\nTabella principale del sito archeologico\n\nRelazioni:\n• 1:N → US/USM (Unità Stratigrafiche)\n• 1:N → Periodizzazione\n• 1:N → UT (Unità Topografiche)',
                'us': 'Scheda US/USM\n━━━━━━━━━━━━\nUnità Stratigrafiche e Murarie\n\nRelazioni:\n• N:1 ← Sito\n• 1:N → Reperti\n• N:N ↔ Struttura\n• 1:N → Campioni\n• N:1 ← Periodizzazione',
                'periodo': 'Periodizzazione\n━━━━━━━━━━━━\nFasi e periodi cronologici\n\nRelazioni:\n• N:1 ← Sito\n• 1:N → US/USM',
                'struttura': 'Scheda Struttura\n━━━━━━━━━━━━━━\nStrutture archeologiche\n\nRelazioni:\n• N:N ↔ US/USM\n• N:1 ← Sito',
                'reperti': 'Inventario Materiali\n━━━━━━━━━━━━━━━━\nReperti e materiali archeologici\n\nRelazioni:\n• N:1 ← US/USM\n• N:N ↔ Media',
                'ut': 'Scheda UT\n━━━━━━━━━\nUnità Topografiche (Survey)\n\nRelazioni:\n• N:1 ← Sito\n• 1:N → Reperti',
                'media': 'Media Manager\n━━━━━━━━━━━━\nGestione foto e documenti\n\nRelazioni:\n• N:N ↔ US/USM\n• N:N ↔ Reperti',
                'export': 'Export Immagini\n━━━━━━━━━━━━━━\nEsporta immagini per cartella',
                'pdf': 'PDF Export\n━━━━━━━━━━\nGenera documentazione PDF'
            },
            'en': {
                'site': 'Site Form\n━━━━━━━━━\nMain archaeological site table\n\nRelationships:\n• 1:N → SU/WSU (Stratigraphic Units)\n• 1:N → Periodization\n• 1:N → TU (Topographic Units)',
                'us': 'SU/WSU Form\n━━━━━━━━━━━\nStratigraphic and Wall Units\n\nRelationships:\n• N:1 ← Site\n• 1:N → Finds\n• N:N ↔ Structure\n• 1:N → Samples\n• N:1 ← Periodization',
                'periodo': 'Periodization\n━━━━━━━━━━━━\nChronological phases and periods\n\nRelationships:\n• N:1 ← Site\n• 1:N → SU/WSU',
                'struttura': 'Structure Form\n━━━━━━━━━━━━━\nArchaeological structures\n\nRelationships:\n• N:N ↔ SU/WSU\n• N:1 ← Site',
                'reperti': 'Finds Inventory\n━━━━━━━━━━━━━━\nArtefacts and materials\n\nRelationships:\n• N:1 ← SU/WSU\n• N:N ↔ Media',
                'ut': 'TU Form\n━━━━━━━━\nTopographic Units (Survey)\n\nRelationships:\n• N:1 ← Site\n• 1:N → Finds',
                'media': 'Media Manager\n━━━━━━━━━━━━\nPhoto and document management\n\nRelationships:\n• N:N ↔ SU/WSU\n• N:N ↔ Finds',
                'export': 'Image Export\n━━━━━━━━━━━━\nExport images by folder',
                'pdf': 'PDF Export\n━━━━━━━━━━\nGenerate PDF documentation'
            },
            'de': {
                'site': 'Fundstelle\n━━━━━━━━━━\nHaupttabelle archäologische Fundstelle\n\nBeziehungen:\n• 1:N → SE/MSE (Stratigraphische Einheiten)\n• 1:N → Periodisierung\n• 1:N → TE (Topographische Einheiten)',
                'us': 'SE/MSE Formular\n━━━━━━━━━━━━━━\nStratigraphische und Mauereinheiten\n\nBeziehungen:\n• N:1 ← Fundstelle\n• 1:N → Funde\n• N:N ↔ Struktur\n• 1:N → Proben\n• N:1 ← Periodisierung',
                'periodo': 'Periodisierung\n━━━━━━━━━━━━\nChronologische Phasen\n\nBeziehungen:\n• N:1 ← Fundstelle\n• 1:N → SE/MSE',
                'struttura': 'Struktur Formular\n━━━━━━━━━━━━━━━\nArchäologische Strukturen\n\nBeziehungen:\n• N:N ↔ SE/MSE\n• N:1 ← Fundstelle',
                'reperti': 'Fundinventar\n━━━━━━━━━━━━\nArtefakte und Materialien\n\nBeziehungen:\n• N:1 ← SE/MSE\n• N:N ↔ Medien',
                'ut': 'TE Formular\n━━━━━━━━━━━\nTopographische Einheiten\n\nBeziehungen:\n• N:1 ← Fundstelle\n• 1:N → Funde',
                'media': 'Medien-Manager\n━━━━━━━━━━━━━━\nFoto- und Dokumentenverwaltung\n\nBeziehungen:\n• N:N ↔ SE/MSE\n• N:N ↔ Funde',
                'export': 'Bildexport\n━━━━━━━━━━\nBilder nach Ordner exportieren',
                'pdf': 'PDF-Export\n━━━━━━━━━━\nPDF-Dokumentation erstellen'
            }
        }

        # Get tooltips for current language, fallback to Italian
        tips = tooltips.get(self.current_lang, tooltips['it'])

        # Apply tooltips to buttons
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
        """Setup web views for pyarchinit and tutorial tabs"""
        # Setup pyarchinit.org in tab_5 (webView_adarte)
        if HAS_WEBENGINE:
            # Replace QTextBrowser with QWebEngineView for better web rendering
            # Get the parent layout
            parent_widget = self.webView_adarte.parentWidget()
            layout = parent_widget.layout()

            # Create new QWebEngineView
            self.web_engine_pyarchinit = QWebEngineView()
            self.web_engine_pyarchinit.setUrl(QUrl("https://www.pyarchinit.org"))

            # Replace the old widget
            layout.replaceWidget(self.webView_adarte, self.web_engine_pyarchinit)
            self.webView_adarte.deleteLater()
            self.webView_adarte = self.web_engine_pyarchinit
        else:
            # Fallback: show a message with link
            self.webView_adarte.setHtml(self.get_pyarchinit_fallback_html())
            self.webView_adarte.setOpenExternalLinks(True)

        # Setup tutorial in tab_4 (webView)
        self.load_tutorial_content()

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
                    background-color: #f5f5f5;
                    text-align: center;
                }
                .container {
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 30px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #2c5282; }
                a {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 15px 30px;
                    background-color: #4299e1;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 18px;
                }
                a:hover { background-color: #3182ce; }
                .logo { font-size: 48px; margin-bottom: 20px; }
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

    def load_tutorial_content(self):
        """Load tutorial content based on current language"""
        # Path to tutorial HTML files
        tutorial_html_path = os.path.join(
            self.plugin_dir, 'tabs', f'tutorial_{self.current_lang}.html'
        )

        # Fallback to Italian if language file doesn't exist
        if not os.path.exists(tutorial_html_path):
            tutorial_html_path = os.path.join(
                self.plugin_dir, 'tabs', 'tutorial_it.html'
            )

        # If tutorial HTML exists, load it
        if os.path.exists(tutorial_html_path):
            if HAS_WEBENGINE:
                # Replace QTextBrowser with QWebEngineView
                parent_widget = self.webView.parentWidget()
                layout = parent_widget.layout()

                self.web_engine_tutorial = QWebEngineView()
                self.web_engine_tutorial.setUrl(QUrl.fromLocalFile(tutorial_html_path))

                layout.replaceWidget(self.webView, self.web_engine_tutorial)
                self.webView.deleteLater()
                self.webView = self.web_engine_tutorial
            else:
                with open(tutorial_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.webView.setHtml(html_content)
                self.webView.setOpenExternalLinks(True)
        else:
            # Show tutorial overview with links to documentation
            self.webView.setHtml(self.get_tutorial_html())
            self.webView.setOpenExternalLinks(True)

    def get_tutorial_html(self):
        """Generate tutorial HTML content based on current language"""
        tutorials_info = {
            'it': {
                'title': 'Tutorial pyArchInit',
                'subtitle': 'Guida all\'uso del plugin',
                'description': 'Seleziona un argomento per visualizzare il tutorial:',
                'open_viewer': 'Apri Tutorial Viewer',
                'docs_link': 'Documentazione Online'
            },
            'en': {
                'title': 'pyArchInit Tutorial',
                'subtitle': 'Plugin User Guide',
                'description': 'Select a topic to view the tutorial:',
                'open_viewer': 'Open Tutorial Viewer',
                'docs_link': 'Online Documentation'
            },
            'de': {
                'title': 'pyArchInit Tutorial',
                'subtitle': 'Plugin-Benutzerhandbuch',
                'description': 'Wählen Sie ein Thema aus, um das Tutorial anzuzeigen:',
                'open_viewer': 'Tutorial-Viewer öffnen',
                'docs_link': 'Online-Dokumentation'
            },
            'fr': {
                'title': 'Tutoriel pyArchInit',
                'subtitle': 'Guide d\'utilisation du plugin',
                'description': 'Sélectionnez un sujet pour afficher le tutoriel:',
                'open_viewer': 'Ouvrir le visualiseur de tutoriels',
                'docs_link': 'Documentation en ligne'
            },
            'es': {
                'title': 'Tutorial pyArchInit',
                'subtitle': 'Guía de uso del plugin',
                'description': 'Seleccione un tema para ver el tutorial:',
                'open_viewer': 'Abrir visor de tutoriales',
                'docs_link': 'Documentación en línea'
            },
            'ar': {
                'title': 'دليل pyArchInit',
                'subtitle': 'دليل استخدام الإضافة',
                'description': 'اختر موضوعًا لعرض الدليل:',
                'open_viewer': 'فتح عارض الدليل',
                'docs_link': 'التوثيق عبر الإنترنت'
            },
            'ca': {
                'title': 'Tutorial pyArchInit',
                'subtitle': 'Guia d\'ús del plugin',
                'description': 'Seleccioneu un tema per veure el tutorial:',
                'open_viewer': 'Obrir visualitzador de tutorials',
                'docs_link': 'Documentació en línia'
            }
        }

        info = tutorials_info.get(self.current_lang, tutorials_info['it'])
        direction = 'rtl' if self.current_lang == 'ar' else 'ltr'

        return f"""
        <!DOCTYPE html>
        <html dir="{direction}">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    margin: 0;
                    direction: {direction};
                }}
                .container {{
                    max-width: 600px;
                    margin: 30px auto;
                    padding: 30px;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}
                h1 {{
                    color: #4a5568;
                    margin-bottom: 5px;
                    font-size: 28px;
                }}
                h2 {{
                    color: #718096;
                    font-weight: normal;
                    margin-top: 0;
                    font-size: 16px;
                }}
                p {{ color: #4a5568; line-height: 1.6; }}
                .btn {{
                    display: inline-block;
                    margin: 10px 5px;
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: transform 0.2s, box-shadow 0.2s;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
                }}
                .icon {{ font-size: 48px; margin-bottom: 15px; }}
                .note {{
                    background: #f7fafc;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 20px;
                    font-size: 13px;
                    color: #718096;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">📚</div>
                <h1>{info['title']}</h1>
                <h2>{info['subtitle']}</h2>
                <p>{info['description']}</p>
                <a href="https://pyarchinitdoc.readthedocs.io/{self.current_lang}/latest/" class="btn" target="_blank">
                    {info['docs_link']}
                </a>
                <div class="note">
                    💡 Use the <strong>Tutorial Viewer</strong> from the PyArchInit menu for comprehensive tutorials.
                </div>
            </div>
        </body>
        </html>
        """
