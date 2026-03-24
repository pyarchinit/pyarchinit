#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtWidgets import QApplication, QDialog, QVBoxLayout, QTabWidget, QWidget, QTextBrowser, QLabel
from qgis.PyQt.uic import loadUiType
from qgis.PyQt.QtCore import QUrl, Qt
from qgis.PyQt.QtGui import QDesktopServices

import os
import sys
import platform
import configparser

MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'pyarchinitInfoDialog.ui'))


class pyArchInitDialog_Info(QDialog, MAIN_DIALOG_CLASS):

    # i18n labels for 10 languages
    I18N = {
        'it': {
            'window_title': 'pyArchInit - Informazioni',
            'tab_about': 'Informazioni',
            'tab_system': 'Sistema',
            'tab_deps': 'Dipendenze',
            'tab_links': 'Link e Supporto',
            'version': 'Versione',
            'description': 'Strumenti GIS per l\'archeologia - PyArchInit gestisce dataset archeologici con alta portabilita sulle principali piattaforme',
            'developers': 'Sviluppatori',
            'thanks': 'Ringraziamenti speciali per il testing',
            'support': 'e supporto a',
            'system_info': 'Informazioni di Sistema',
            'plugin_version': 'Versione Plugin',
            'python_version': 'Versione Python',
            'qgis_version': 'Versione QGIS',
            'qt_version': 'Versione Qt',
            'os_info': 'Sistema Operativo',
            'db_status': 'Stato Connessione DB',
            'connected': 'Connesso',
            'not_connected': 'Non connesso',
            'db_type': 'Tipo Database',
            'dependencies': 'Dipendenze Installate',
            'dep_available': 'Disponibile',
            'dep_missing': 'Mancante',
            'documentation': 'Documentazione',
            'website': 'Sito Web',
            'github': 'Repository GitHub',
            'help_group': 'Gruppo di Supporto',
            'email_support': 'Email di Supporto',
            'donations': 'Donazioni',
            'donation_text': 'Supporta lo sviluppo di pyArchInit',
            'license': 'Licenza',
        },
        'en': {
            'window_title': 'pyArchInit - Information',
            'tab_about': 'About',
            'tab_system': 'System',
            'tab_deps': 'Dependencies',
            'tab_links': 'Links & Support',
            'version': 'Version',
            'description': 'Archaeological GIS Tools - PyArchInit manages archaeological datasets with high portability across major platforms',
            'developers': 'Developers',
            'thanks': 'Special thanks for testing to',
            'support': 'and support from',
            'system_info': 'System Information',
            'plugin_version': 'Plugin Version',
            'python_version': 'Python Version',
            'qgis_version': 'QGIS Version',
            'qt_version': 'Qt Version',
            'os_info': 'Operating System',
            'db_status': 'DB Connection Status',
            'connected': 'Connected',
            'not_connected': 'Not connected',
            'db_type': 'Database Type',
            'dependencies': 'Installed Dependencies',
            'dep_available': 'Available',
            'dep_missing': 'Missing',
            'documentation': 'Documentation',
            'website': 'Website',
            'github': 'GitHub Repository',
            'help_group': 'Support Group',
            'email_support': 'Support Email',
            'donations': 'Donations',
            'donation_text': 'Support pyArchInit development',
            'license': 'License',
        },
        'de': {
            'window_title': 'pyArchInit - Informationen',
            'tab_about': 'Info',
            'tab_system': 'System',
            'tab_deps': 'Abhangigkeiten',
            'tab_links': 'Links & Support',
            'version': 'Version',
            'description': 'Archaologische GIS-Werkzeuge - PyArchInit verwaltet archaologische Datensatze mit hoher Portabilitat auf den wichtigsten Plattformen',
            'developers': 'Entwickler',
            'thanks': 'Besonderer Dank fur das Testen an',
            'support': 'und Unterstutzung von',
            'system_info': 'Systeminformationen',
            'plugin_version': 'Plugin-Version',
            'python_version': 'Python-Version',
            'qgis_version': 'QGIS-Version',
            'qt_version': 'Qt-Version',
            'os_info': 'Betriebssystem',
            'db_status': 'DB-Verbindungsstatus',
            'connected': 'Verbunden',
            'not_connected': 'Nicht verbunden',
            'db_type': 'Datenbanktyp',
            'dependencies': 'Installierte Abhangigkeiten',
            'dep_available': 'Verfugbar',
            'dep_missing': 'Fehlend',
            'documentation': 'Dokumentation',
            'website': 'Webseite',
            'github': 'GitHub-Repository',
            'help_group': 'Support-Gruppe',
            'email_support': 'Support-E-Mail',
            'donations': 'Spenden',
            'donation_text': 'Unterstutzen Sie die Entwicklung von pyArchInit',
            'license': 'Lizenz',
        },
        'es': {
            'window_title': 'pyArchInit - Informacion',
            'tab_about': 'Acerca de',
            'tab_system': 'Sistema',
            'tab_deps': 'Dependencias',
            'tab_links': 'Enlaces y Soporte',
            'version': 'Version',
            'description': 'Herramientas GIS arqueologicas - PyArchInit gestiona conjuntos de datos arqueologicos con alta portabilidad en las principales plataformas',
            'developers': 'Desarrolladores',
            'thanks': 'Agradecimientos especiales por las pruebas a',
            'support': 'y apoyo de',
            'system_info': 'Informacion del Sistema',
            'plugin_version': 'Version del Plugin',
            'python_version': 'Version de Python',
            'qgis_version': 'Version de QGIS',
            'qt_version': 'Version de Qt',
            'os_info': 'Sistema Operativo',
            'db_status': 'Estado de Conexion DB',
            'connected': 'Conectado',
            'not_connected': 'No conectado',
            'db_type': 'Tipo de Base de Datos',
            'dependencies': 'Dependencias Instaladas',
            'dep_available': 'Disponible',
            'dep_missing': 'Faltante',
            'documentation': 'Documentacion',
            'website': 'Sitio Web',
            'github': 'Repositorio GitHub',
            'help_group': 'Grupo de Soporte',
            'email_support': 'Email de Soporte',
            'donations': 'Donaciones',
            'donation_text': 'Apoya el desarrollo de pyArchInit',
            'license': 'Licencia',
        },
        'fr': {
            'window_title': 'pyArchInit - Informations',
            'tab_about': 'A propos',
            'tab_system': 'Systeme',
            'tab_deps': 'Dependances',
            'tab_links': 'Liens et Support',
            'version': 'Version',
            'description': 'Outils SIG archeologiques - PyArchInit gere les ensembles de donnees archeologiques avec une haute portabilite sur les principales plateformes',
            'developers': 'Developpeurs',
            'thanks': 'Remerciements speciaux pour les tests a',
            'support': 'et soutien de',
            'system_info': 'Informations Systeme',
            'plugin_version': 'Version du Plugin',
            'python_version': 'Version Python',
            'qgis_version': 'Version QGIS',
            'qt_version': 'Version Qt',
            'os_info': 'Systeme d\'exploitation',
            'db_status': 'Statut Connexion BD',
            'connected': 'Connecte',
            'not_connected': 'Non connecte',
            'db_type': 'Type de Base de Donnees',
            'dependencies': 'Dependances Installees',
            'dep_available': 'Disponible',
            'dep_missing': 'Manquant',
            'documentation': 'Documentation',
            'website': 'Site Web',
            'github': 'Depot GitHub',
            'help_group': 'Groupe de Support',
            'email_support': 'Email de Support',
            'donations': 'Dons',
            'donation_text': 'Soutenez le developpement de pyArchInit',
            'license': 'Licence',
        },
        'ar': {
            'window_title': 'pyArchInit - معلومات',
            'tab_about': 'حول',
            'tab_system': 'النظام',
            'tab_deps': 'التبعيات',
            'tab_links': 'روابط ودعم',
            'version': 'الإصدار',
            'description': 'أدوات نظم المعلومات الجغرافية الأثرية - يدير PyArchInit مجموعات البيانات الأثرية مع قابلية نقل عالية عبر المنصات الرئيسية',
            'developers': 'المطورون',
            'thanks': 'شكر خاص للاختبار إلى',
            'support': 'والدعم من',
            'system_info': 'معلومات النظام',
            'plugin_version': 'إصدار البرنامج المساعد',
            'python_version': 'إصدار بايثون',
            'qgis_version': 'إصدار QGIS',
            'qt_version': 'إصدار Qt',
            'os_info': 'نظام التشغيل',
            'db_status': 'حالة اتصال قاعدة البيانات',
            'connected': 'متصل',
            'not_connected': 'غير متصل',
            'db_type': 'نوع قاعدة البيانات',
            'dependencies': 'التبعيات المثبتة',
            'dep_available': 'متاح',
            'dep_missing': 'مفقود',
            'documentation': 'التوثيق',
            'website': 'الموقع الإلكتروني',
            'github': 'مستودع GitHub',
            'help_group': 'مجموعة الدعم',
            'email_support': 'بريد الدعم',
            'donations': 'تبرعات',
            'donation_text': 'ادعم تطوير pyArchInit',
            'license': 'الرخصة',
        },
        'ca': {
            'window_title': 'pyArchInit - Informacio',
            'tab_about': 'Sobre',
            'tab_system': 'Sistema',
            'tab_deps': 'Dependencies',
            'tab_links': 'Enllacos i Suport',
            'version': 'Versio',
            'description': 'Eines GIS arqueologiques - PyArchInit gestiona conjunts de dades arqueologiques amb alta portabilitat a les principals plataformes',
            'developers': 'Desenvolupadors',
            'thanks': 'Agraiments especials per les proves a',
            'support': 'i suport de',
            'system_info': 'Informacio del Sistema',
            'plugin_version': 'Versio del Plugin',
            'python_version': 'Versio de Python',
            'qgis_version': 'Versio de QGIS',
            'qt_version': 'Versio de Qt',
            'os_info': 'Sistema Operatiu',
            'db_status': 'Estat Connexio BD',
            'connected': 'Connectat',
            'not_connected': 'No connectat',
            'db_type': 'Tipus de Base de Dades',
            'dependencies': 'Dependencies Instal-lades',
            'dep_available': 'Disponible',
            'dep_missing': 'Absent',
            'documentation': 'Documentacio',
            'website': 'Lloc Web',
            'github': 'Repositori GitHub',
            'help_group': 'Grup de Suport',
            'email_support': 'Email de Suport',
            'donations': 'Donacions',
            'donation_text': 'Dona suport al desenvolupament de pyArchInit',
            'license': 'Llicencia',
        },
        'ro': {
            'window_title': 'pyArchInit - Informatii',
            'tab_about': 'Despre',
            'tab_system': 'Sistem',
            'tab_deps': 'Dependente',
            'tab_links': 'Linkuri si Suport',
            'version': 'Versiune',
            'description': 'Instrumente GIS arheologice - PyArchInit gestioneaza seturi de date arheologice cu portabilitate ridicata pe platformele principale',
            'developers': 'Dezvoltatori',
            'thanks': 'Multumiri speciale pentru testare catre',
            'support': 'si sprijin de la',
            'system_info': 'Informatii Sistem',
            'plugin_version': 'Versiune Plugin',
            'python_version': 'Versiune Python',
            'qgis_version': 'Versiune QGIS',
            'qt_version': 'Versiune Qt',
            'os_info': 'Sistem de Operare',
            'db_status': 'Stare Conexiune BD',
            'connected': 'Conectat',
            'not_connected': 'Neconectat',
            'db_type': 'Tip Baza de Date',
            'dependencies': 'Dependente Instalate',
            'dep_available': 'Disponibil',
            'dep_missing': 'Lipsa',
            'documentation': 'Documentatie',
            'website': 'Site Web',
            'github': 'Depozit GitHub',
            'help_group': 'Grup de Suport',
            'email_support': 'Email Suport',
            'donations': 'Donatii',
            'donation_text': 'Sprijina dezvoltarea pyArchInit',
            'license': 'Licenta',
        },
        'pt': {
            'window_title': 'pyArchInit - Informacoes',
            'tab_about': 'Sobre',
            'tab_system': 'Sistema',
            'tab_deps': 'Dependencias',
            'tab_links': 'Links e Suporte',
            'version': 'Versao',
            'description': 'Ferramentas GIS arqueologicas - PyArchInit gerencia conjuntos de dados arqueologicos com alta portabilidade nas principais plataformas',
            'developers': 'Desenvolvedores',
            'thanks': 'Agradecimentos especiais pelos testes a',
            'support': 'e apoio de',
            'system_info': 'Informacoes do Sistema',
            'plugin_version': 'Versao do Plugin',
            'python_version': 'Versao do Python',
            'qgis_version': 'Versao do QGIS',
            'qt_version': 'Versao do Qt',
            'os_info': 'Sistema Operacional',
            'db_status': 'Status Conexao BD',
            'connected': 'Conectado',
            'not_connected': 'Nao conectado',
            'db_type': 'Tipo de Banco de Dados',
            'dependencies': 'Dependencias Instaladas',
            'dep_available': 'Disponivel',
            'dep_missing': 'Ausente',
            'documentation': 'Documentacao',
            'website': 'Site',
            'github': 'Repositorio GitHub',
            'help_group': 'Grupo de Suporte',
            'email_support': 'Email de Suporte',
            'donations': 'Doacoes',
            'donation_text': 'Apoie o desenvolvimento do pyArchInit',
            'license': 'Licenca',
        },
        'el': {
            'window_title': 'pyArchInit - Plirofories',
            'tab_about': 'Sxetika',
            'tab_system': 'Systima',
            'tab_deps': 'Exartiseis',
            'tab_links': 'Syndesmoi kai Ypostirixi',
            'version': 'Ekdosi',
            'description': 'Archaiologika ergaleia GIS - To PyArchInit diachirizetai archaiologika dedomena me ypsili metafersimatita stis kyries platformes',
            'developers': 'Programmatistes',
            'thanks': 'Eidikes efcharisties gia tis dokimes se',
            'support': 'kai ypostirixi apo',
            'system_info': 'Plirofories Systimatos',
            'plugin_version': 'Ekdosi Plugin',
            'python_version': 'Ekdosi Python',
            'qgis_version': 'Ekdosi QGIS',
            'qt_version': 'Ekdosi Qt',
            'os_info': 'Leitourgiko Systima',
            'db_status': 'Katastasi Syndesis BD',
            'connected': 'Syndedemeno',
            'not_connected': 'Mi syndedemeno',
            'db_type': 'Typos Vasis Dedomenon',
            'dependencies': 'Egkatestimenes Exartiseis',
            'dep_available': 'Diathesimo',
            'dep_missing': 'Leipei',
            'documentation': 'Tekmiriosi',
            'website': 'Istotopos',
            'github': 'Apothitirio GitHub',
            'help_group': 'Omada Ypostirixis',
            'email_support': 'Email Ypostirixis',
            'donations': 'Dorees',
            'donation_text': 'Ypostirixte tin anaptyxi tou pyArchInit',
            'license': 'Adeia',
        },
    }

    # Dependencies to check
    DEPENDENCIES = [
        ('sqlalchemy', 'SQLAlchemy'),
        ('reportlab', 'ReportLab'),
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('networkx', 'NetworkX'),
        ('matplotlib', 'Matplotlib'),
        ('graphviz', 'Graphviz (Python)'),
        ('langchain', 'LangChain'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
    ]

    def __init__(self, parent=None, db=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.db = db

        # Get locale
        from qgis.core import QgsSettings
        self.lang = QgsSettings().value("locale/userLocale", "en", type=str)[:2]
        if self.lang not in self.I18N:
            self.lang = 'en'
        self.tr_dict = self.I18N[self.lang]

        # Apply theme
        try:
            from modules.utility.pyarchinit_theme_manager import ThemeManager
            ThemeManager.apply_theme(self)
            self.theme_toggle_btn = ThemeManager.add_theme_toggle_to_form(self)
        except Exception:
            pass

        # Read metadata
        self.config = configparser.ConfigParser()
        metadata_file = os.path.join(os.path.dirname(__file__), os.pardir, 'metadata.txt')
        self.config.read(metadata_file)
        self.plugin_version = self.config.get('general', 'version', fallback='unknown')

        # Set window title
        self.setWindowTitle(self.tr_dict['window_title'])

        # Build the tabbed interface inside the existing textBrowser's parent
        self._build_ui()

    def _t(self, key):
        """Get translated string for key."""
        return self.tr_dict.get(key, self.I18N['en'].get(key, key))

    def _build_ui(self):
        """Build the modernized info dialog UI."""
        # Hide the original textBrowser and replace with tabbed layout
        self.textBrowser.setVisible(False)

        # Get the main layout
        main_layout = self.layout()

        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)

        # Tab 1: About
        tab_widget.addTab(self._build_about_tab(), self._t('tab_about'))

        # Tab 2: System Info
        tab_widget.addTab(self._build_system_tab(), self._t('tab_system'))

        # Tab 3: Dependencies
        tab_widget.addTab(self._build_deps_tab(), self._t('tab_deps'))

        # Tab 4: Links & Support
        tab_widget.addTab(self._build_links_tab(), self._t('tab_links'))

        main_layout.addWidget(tab_widget)

    def _create_text_browser(self):
        """Create a configured QTextBrowser."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setOpenLinks(False)
        browser.anchorClicked.connect(self.open_link)
        return browser

    def _build_about_tab(self):
        """Build the About tab content."""
        browser = self._create_text_browser()

        home = os.environ.get('PYARCHINIT_HOME', '')
        home_DB_path = os.path.join(home, 'pyarchinit_DB_folder')
        logo_path = os.path.join(home_DB_path, 'logo_2.png')

        html = '<div style="font-family: Segoe UI, Arial, sans-serif; padding: 10px;">'

        # Logo
        if os.path.exists(logo_path):
            html += '<div style="text-align: center; margin-bottom: 15px;">'
            html += '<img src="{}">'.format(logo_path)
            html += '</div>'

        # Version badge
        html += '<div style="text-align: center; margin-bottom: 20px;">'
        html += ('<span style="background-color: #1976D2; color: white; padding: 4px 12px; '
                 'border-radius: 12px; font-size: 13px; font-weight: bold;">'
                 '{}: {}</span>').format(self._t('version'), self.plugin_version)
        html += '</div>'

        # Description
        html += '<p style="text-align: center; color: #555; font-style: italic; margin-bottom: 20px;">'
        html += self._t('description')
        html += '</p>'

        # Developers section
        html += '<h3 style="color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 5px;">{}</h3>'.format(
            self._t('developers'))
        html += '<p>Luca Mandolesi<br>Enzo Cocca<br>adArte srl - Rimini - www.adarteinfo.it</p>'

        # Thanks section
        html += '<h3 style="color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 5px;">{}</h3>'.format(
            self._t('thanks'))
        testers = [
            'Tutti i soci e collaboratori di adArte srl',
            'Roberto Montagnetti', 'Paolo Rosati', 'Michele Fait',
            'UNAQUANTUM', 'Giovanni Manghi', 'Jerzy Sikora',
            'Michele Zappitelli', 'Chiara Cesaretti', 'Chiara Di Fronzo',
            'Valeria Casicci', 'Fabio Alboni', 'Yuri Godino',
            'Manuela Battaglia', 'Simona Gugnali', 'Tommaso Gallo',
        ]
        html += '<p>' + '<br>'.join(testers) + '</p>'

        # Supporters section
        html += '<h3 style="color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 5px;">{}</h3>'.format(
            self._t('support'))
        supporters = ['Stefano Costa', 'Francesco de Virgilio', 'Giuseppe Naponiello']
        html += '<p>' + '<br>'.join(supporters) + '</p>'

        # License
        html += '<h3 style="color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 5px;">{}</h3>'.format(
            self._t('license'))
        html += '<p>GNU General Public License v2 (GPLv2)</p>'

        html += '</div>'
        browser.setHtml(html)
        return browser

    def _build_system_tab(self):
        """Build the System Information tab."""
        browser = self._create_text_browser()

        # Gather system info
        python_ver = '{}.{}.{}'.format(*sys.version_info[:3])
        try:
            from qgis.core import Qgis
            qgis_ver = Qgis.version()
        except Exception:
            qgis_ver = 'N/A'

        try:
            from qgis.PyQt.QtCore import QT_VERSION_STR
            qt_ver = QT_VERSION_STR
        except Exception:
            qt_ver = 'N/A'

        os_info = '{} {} ({})'.format(platform.system(), platform.release(), platform.machine())

        # DB connection status
        db_connected = False
        db_type = 'N/A'
        try:
            from modules.db.pyarchinit_conn_strings import Connection
            conn = Connection()
            conn_str = conn.conn_str()
            if conn_str:
                db_type = 'PostgreSQL' if 'postgres' in str(conn_str) else 'SQLite'
                from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
                mgr = Pyarchinit_db_management(conn_str)
                db_connected = mgr.connection()
        except Exception:
            pass

        html = '<div style="font-family: Segoe UI, Arial, sans-serif; padding: 10px;">'
        html += '<h2 style="color: #1976D2;">{}</h2>'.format(self._t('system_info'))

        # System info table
        connected_color = '#4CAF50' if db_connected else '#f44336'
        connected_text = self._t('connected') if db_connected else self._t('not_connected')

        rows = [
            (self._t('plugin_version'), '<b>{}</b>'.format(self.plugin_version)),
            (self._t('python_version'), python_ver),
            (self._t('qgis_version'), qgis_ver),
            (self._t('qt_version'), qt_ver),
            (self._t('os_info'), os_info),
            (self._t('db_type'), db_type),
            (self._t('db_status'),
             '<span style="color: {}; font-weight: bold;">{}</span>'.format(
                 connected_color, connected_text)),
        ]

        html += '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        for label, value in rows:
            html += ('<tr style="border-bottom: 1px solid #e0e0e0;">'
                     '<td style="padding: 8px 12px; color: #555; width: 40%;">{}</td>'
                     '<td style="padding: 8px 12px;">{}</td>'
                     '</tr>').format(label, value)
        html += '</table>'
        html += '</div>'

        browser.setHtml(html)
        return browser

    def _build_deps_tab(self):
        """Build the Dependencies tab."""
        browser = self._create_text_browser()

        html = '<div style="font-family: Segoe UI, Arial, sans-serif; padding: 10px;">'
        html += '<h2 style="color: #1976D2;">{}</h2>'.format(self._t('dependencies'))

        html += '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
        html += ('<tr style="background-color: #E3F2FD; font-weight: bold;">'
                 '<td style="padding: 8px 12px;">Package</td>'
                 '<td style="padding: 8px 12px;">Status</td>'
                 '<td style="padding: 8px 12px;">{}</td>'
                 '</tr>').format(self._t('version'))

        for module_name, display_name in self.DEPENDENCIES:
            try:
                mod = __import__(module_name)
                version = getattr(mod, '__version__', getattr(mod, 'VERSION', ''))
                status_html = '<span style="color: #4CAF50; font-weight: bold;">{}</span>'.format(
                    self._t('dep_available'))
                ver_html = str(version) if version else '-'
            except ImportError:
                status_html = '<span style="color: #f44336; font-weight: bold;">{}</span>'.format(
                    self._t('dep_missing'))
                ver_html = '-'

            html += ('<tr style="border-bottom: 1px solid #e0e0e0;">'
                     '<td style="padding: 6px 12px;">{}</td>'
                     '<td style="padding: 6px 12px;">{}</td>'
                     '<td style="padding: 6px 12px;">{}</td>'
                     '</tr>').format(display_name, status_html, ver_html)

        html += '</table></div>'
        browser.setHtml(html)
        return browser

    def _build_links_tab(self):
        """Build the Links & Support tab."""
        browser = self._create_text_browser()

        html = '<div style="font-family: Segoe UI, Arial, sans-serif; padding: 10px;">'

        # Links section
        links = [
            (self._t('website'),
             'https://pyarchinit.org',
             'https://pyarchinit.org'),
            (self._t('github'),
             'https://github.com/pyarchinit/pyarchinit',
             'https://github.com/pyarchinit/pyarchinit'),
            (self._t('documentation'),
             'https://pyarchinit.org/documentation',
             'https://pyarchinit.org/documentation'),
            (self._t('help_group'),
             'https://groups.google.com/g/pyarchinit-users',
             'Google Groups - pyarchinit-users'),
            (self._t('email_support'),
             'mailto:pyarchinit@gmail.com',
             'pyarchinit@gmail.com'),
        ]

        for label, url, display in links:
            html += ('<div style="margin-bottom: 12px; padding: 10px; '
                     'background-color: #F5F5F5; border-radius: 6px; '
                     'border-left: 4px solid #1976D2;">')
            html += '<b style="color: #333;">{}</b><br>'.format(label)
            html += '<a href="{}" style="color: #1976D2; text-decoration: none;">{}</a>'.format(url, display)
            html += '</div>'

        # Donations section
        html += '<div style="margin-top: 20px; padding: 15px; background-color: #FFF8E1; '
        html += 'border-radius: 6px; border-left: 4px solid #FFC107; text-align: center;">'
        html += '<b style="color: #F57F17; font-size: 14px;">{}</b><br><br>'.format(self._t('donations'))
        html += '<p>{}</p>'.format(self._t('donation_text'))
        html += ('<a href="https://www.paypal.com/donate/?business=3MAT9YSJN7G98&no_recurring=0'
                 '&item_name=Sviluppo+e+implementazione+di+pyarchinit&currency_code=EUR" '
                 'style="display: inline-block; background-color: #FFC107; color: #333; '
                 'padding: 8px 20px; border-radius: 4px; text-decoration: none; '
                 'font-weight: bold;">PayPal</a>')
        html += '</div>'

        html += '</div>'
        browser.setHtml(html)
        return browser

    def open_link(self, url):
        """Open a link in the system browser."""
        QDesktopServices.openUrl(QUrl(url.toString()))
