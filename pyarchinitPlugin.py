#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
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
from __future__ import absolute_import
import os
import sqlite3
from datetime import datetime

from qgis.PyQt.QtCore import Qt, QFileInfo, QTranslator, QVariant, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QToolButton, QMenu, QMessageBox
from qgis.core import QgsApplication, QgsSettings, QgsMessageLog, Qgis

from qgis.PyQt.QtCore import QLocale

from .pyarchinitDockWidget import PyarchinitPluginDialog
# Tab/dialog imports are deferred to run*() methods for faster plugin startup

# Register Qt resources early so :/icons/ paths work in all .ui files.
# MUST use relative import — bare "import resources_rc" picks up geodb's copy.
try:
    from . import resources_rc  # noqa: F401  — triggers qInitResources()
except Exception:
    pass


filepath = os.path.dirname(__file__)

class PyArchInitPlugin(object):
    HOME = os.environ['PYARCHINIT_HOME']
    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
                   'THUMB_RESIZE': '',
                   'EXPERIMENTAL': '',
                   'SITE_SET': ''
                  }
    # Positive values for EXPERIMENTAL setting in all supported languages
    EXPERIMENTAL_YES_VALUES = ('Si', 'Yes', 'Ja', 'Oui', 'Sí', 'نعم', 'Sì')

    def is_experimental_enabled(self):
        """Check if experimental features are enabled, regardless of language setting."""
        return self.PARAMS_DICT.get('EXPERIMENTAL', '').strip() in self.EXPERIMENTAL_YES_VALUES

    _cantiere_permission_cache = None  # Cache result for session

    def _check_cantiere_permission(self, table_name='cantiere_table'):
        """
        Check if the current user has permission to access cantiere management forms.
        Returns True if user has admin or responsabile role, or if the permission system
        is not available (backward compatibility).

        This is a soft gate: any error defaults to allowing access.
        Result is cached for the session to avoid repeated DB queries.
        """
        if self._cantiere_permission_cache is not None:
            return self._cantiere_permission_cache

        try:
            from .modules.db.pyarchinit_conn_strings import Connection
            from .modules.db.pyarchinit_db_manager import get_db_manager
            import getpass

            conn = Connection()
            conn_str = conn.conn_str()

            # For SQLite databases, always allow access
            if 'sqlite' in conn_str.lower():
                self._cantiere_permission_cache = True
                return True

            db_manager = get_db_manager(conn_str, use_singleton=True)

            # Check if pyarchinit_users table exists
            check_table = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'pyarchinit_users'
                )
            """
            table_exists = db_manager.execute_sql(check_table)
            if not table_exists or not table_exists[0][0]:
                # Permission system not installed - allow access for backward compatibility
                self._cantiere_permission_cache = True
                return True

            # Get current username from settings or OS
            s = QgsSettings()
            current_user = s.value('pyArchInit/current_user', '', type=str)
            db_username = s.value('pyArchInit/db_username', '', type=str)

            # Try to get DB username from connection if not in settings
            if not db_username:
                try:
                    result = db_manager.execute_sql("SELECT current_user")
                    if result and result[0][0]:
                        db_username = result[0][0]
                except Exception:
                    pass

            if not current_user:
                current_user = getpass.getuser()

            # Check if database superuser (postgres)
            if db_username:
                db_user_lower = db_username.lower()
                if db_user_lower == 'postgres' or db_user_lower.startswith('postgres.'):
                    self._cantiere_permission_cache = True
                    return True

            # Check user role in pyarchinit_users
            usernames_to_check = [u for u in [current_user, db_username] if u]
            for username in usernames_to_check:
                query = """
                    SELECT role FROM pyarchinit_users
                    WHERE LOWER(username) = LOWER(%s) AND is_active = TRUE
                """
                # Try both parameterized and formatted queries for compatibility
                try:
                    result = db_manager.execute_sql(query, (username,))
                except Exception:
                    try:
                        query_fmt = f"""
                            SELECT role FROM pyarchinit_users
                            WHERE LOWER(username) = LOWER('{username}') AND is_active = TRUE
                        """
                        result = db_manager.execute_sql(query_fmt)
                    except Exception:
                        return True  # On query failure, allow access

                if result and len(result) > 0:
                    role = result[0][0]
                    if role in ('admin', 'responsabile'):
                        self._cantiere_permission_cache = True
                        return True
                    else:
                        self._cantiere_permission_cache = False
                        return False

            # User not found in the table - allow access for backward compatibility
            self._cantiere_permission_cache = True
            return True

        except Exception as e:
            # Any error during permission check: default to allowing access
            QgsMessageLog.logMessage(
                f"Cantiere permission check failed (defaulting to allow): {str(e)}",
                "PyArchInit", Qgis.Info
            )
            self._cantiere_permission_cache = True
            return True

    def _show_cantiere_permission_denied(self):
        """Show a permission denied message for cantiere forms."""
        l = QgsSettings().value("locale/userLocale", "it", type=str)[:2]

        _titles = {
            'it': "Accesso Negato",
            'en': "Access Denied",
            'de': "Zugriff verweigert",
            'es': "Acceso Denegado",
            'fr': "Acces Refuse",
            'ar': "الوصول مرفوض",
            'ca': "Acces Denegat",
            'ro': "Acces Refuzat",
            'pt': "Acesso Negado",
            'el': "Apagoreusi Prosvaseos",
        }

        _msgs = {
            'it': ("Non hai i permessi necessari per accedere alla gestione cantiere.\n\n"
                   "Solo gli utenti con ruolo 'admin' o 'responsabile' possono accedere "
                   "a questa funzionalita'.\n\n"
                   "Contatta l'amministratore del sistema per richiedere l'accesso."),
            'en': ("You do not have the necessary permissions to access site management.\n\n"
                   "Only users with 'admin' or 'responsabile' role can access "
                   "this functionality.\n\n"
                   "Contact the system administrator to request access."),
            'de': ("Sie haben nicht die erforderlichen Berechtigungen fuer die Baustellen-Verwaltung.\n\n"
                   "Nur Benutzer mit der Rolle 'admin' oder 'responsabile' koennen auf "
                   "diese Funktion zugreifen.\n\n"
                   "Wenden Sie sich an den Systemadministrator, um Zugriff anzufordern."),
            'es': ("No tiene los permisos necesarios para acceder a la gestion de obra.\n\n"
                   "Solo los usuarios con rol 'admin' o 'responsabile' pueden acceder "
                   "a esta funcionalidad.\n\n"
                   "Contacte al administrador del sistema para solicitar acceso."),
            'fr': ("Vous n'avez pas les autorisations necessaires pour acceder a la gestion du chantier.\n\n"
                   "Seuls les utilisateurs ayant le role 'admin' ou 'responsabile' peuvent acceder "
                   "a cette fonctionnalite.\n\n"
                   "Contactez l'administrateur du systeme pour demander l'acces."),
            'ar': ("ليس لديك الصلاحيات اللازمة للوصول الى ادارة الموقع.\n\n"
                   "فقط المستخدمون بدور 'admin' او 'responsabile' يمكنهم الوصول "
                   "الى هذه الوظيفة.\n\n"
                   "اتصل بمسؤول النظام لطلب الوصول."),
            'ca': ("No teniu els permisos necessaris per accedir a la gestio del cantiere.\n\n"
                   "Nomes els usuaris amb el rol 'admin' o 'responsabile' poden accedir "
                   "a aquesta funcionalitat.\n\n"
                   "Contacteu amb l'administrador del sistema per sol·licitar l'acces."),
            'ro': ("Nu aveti permisiunile necesare pentru a accesa gestionarea santierului.\n\n"
                   "Doar utilizatorii cu rolul 'admin' sau 'responsabile' pot accesa "
                   "aceasta functionalitate.\n\n"
                   "Contactati administratorul de sistem pentru a solicita acces."),
            'pt': ("Nao tem as permissoes necessarias para aceder a gestao do estaleiro.\n\n"
                   "Apenas os utilizadores com o papel 'admin' ou 'responsabile' podem aceder "
                   "a esta funcionalidade.\n\n"
                   "Contacte o administrador do sistema para solicitar acesso."),
            'el': ("Den echete ta aparaitita dikaiomata gia prosvasi sti diacheirisi ergotaxiou.\n\n"
                   "Mono oi christes me rolo 'admin' i 'responsabile' mporoun na prosvasoun "
                   "se afti ti leitourgia.\n\n"
                   "Epikoinoniste me ton diacheiristi systimatos gia na zitisete prosvasi."),
        }

        title = _titles.get(l, _titles['en'])
        msg = _msgs.get(l, _msgs['en'])
        QMessageBox.warning(self.iface.mainWindow(), title, msg, QMessageBox.Ok)

    def load_config(self):
        """Load configuration from config.cfg file into PARAMS_DICT."""
        try:
            cfg_rel_path = os.path.join(os.sep, 'pyarchinit_DB_folder', 'config.cfg')
            file_path = '{}{}'.format(self.HOME, cfg_rel_path)
            if os.path.exists(file_path):
                with open(file_path, "r") as conf:
                    data = conf.read()
                    loaded_params = eval(data)
                    self.PARAMS_DICT.update(loaded_params)
        except Exception as e:
            QgsMessageLog.logMessage(f"PyArchInit - Error loading config: {str(e)}", "PyArchInit", Qgis.Warning)
    # Mapping from short locale codes to full locale names used in translation files
    LOCALE_MAPPING = {
        'it': 'it_IT',
        'en': 'en_US',
        'fr': 'fr_FR',
        'de': 'de_DE',
        'es': 'es_ES',
        'ar': 'ar_LB',
        'ca': 'ca_ES',  # Catalan
        'ro': 'ro_RO',  # Romanian
        'pt': 'pt_PT',  # Portuguese
        'el': 'el_GR',  # Greek
    }

    def __init__(self, iface):
        self.iface = iface
        self.plugin_window = None

        try:
            userPluginPath = os.path.dirname(__file__)
            systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/pyarchinit"

            # Get locale settings with proper type handling
            overrideLocale = QgsSettings().value("locale/overrideFlag", False, type=bool)

            if not overrideLocale:
                localeFullName = QLocale.system().name()
            else:
                localeFullName = QgsSettings().value("locale/userLocale", "", type=str)

            # Ensure localeFullName is a valid string
            if localeFullName and isinstance(localeFullName, str) and len(localeFullName) >= 2:
                localeShort = localeFullName[:2].lower()
                # Try to map short locale to full locale name
                if localeShort in self.LOCALE_MAPPING:
                    localeFullName = self.LOCALE_MAPPING[localeShort]
            else:
                # Default to Italian if no valid locale
                localeFullName = "it_IT"

            # Determine translation file path
            if QFileInfo(userPluginPath).exists():
                translationPath = userPluginPath + "/i18n/pyarchinit_plugin_" + str(localeFullName) + ".qm"
            else:
                translationPath = systemPluginPath + "/i18n/pyarchinit_plugin_" + str(localeFullName) + ".qm"

            self.localePath = translationPath
            if QFileInfo(self.localePath).exists():
                self.translator = QTranslator()
                self.translator.load(self.localePath)
                QCoreApplication.installTranslator(self.translator)

        except Exception as e:
            QgsMessageLog.logMessage(f"PyArchInit - Translation loading error: {str(e)}", "PyArchInit", Qgis.Warning)

        # Check and fix SQLite databases on startup
        self.check_and_fix_sqlite_databases()

    def check_and_fix_sqlite_databases(self):
        """Check and fix macc field in all SQLite databases in the pyarchinit folder"""
        try:
            QgsMessageLog.logMessage("PyArchInit - Starting SQLite database check on plugin startup", "PyArchInit", Qgis.Info)

            # Get the pyarchinit database folder
            db_folder = os.path.join(self.HOME, "pyarchinit_DB_folder")

            if not os.path.exists(db_folder):
                QgsMessageLog.logMessage(f"PyArchInit - Database folder does not exist: {db_folder}", "PyArchInit", Qgis.Info)
                return

            # Check all .sqlite files in the folder
            for filename in os.listdir(db_folder):
                if filename.endswith('.sqlite'):
                    db_path = os.path.join(db_folder, filename)
                    self.fix_single_sqlite_database(db_path)

        except Exception as e:
            QgsMessageLog.logMessage(f"PyArchInit - Error in check_and_fix_sqlite_databases: {str(e)}", "PyArchInit", Qgis.Critical)

    def fix_single_sqlite_database(self, db_path):
        """Fix macc field in a single SQLite database"""
        try:
            db_name = os.path.basename(db_path)
            QgsMessageLog.logMessage(f"PyArchInit - Checking database: {db_name}", "PyArchInit", Qgis.Info)

            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tma_materiali_ripetibili'"
            )
            if not cursor.fetchone():
                QgsMessageLog.logMessage(f"PyArchInit - Table tma_materiali_ripetibili does not exist in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            # Check macc field properties
            cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
            columns = cursor.fetchall()

            macc_info = None
            for col in columns:
                if col[1] == 'macc':  # col[1] is the column name
                    macc_info = col
                    break

            if not macc_info:
                QgsMessageLog.logMessage(f"PyArchInit - Column 'macc' not found in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            # Check if macc is NOT NULL (col[3] is the notnull flag)
            if macc_info[3] == 0:
                QgsMessageLog.logMessage(f"PyArchInit - Column 'macc' is already nullable in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            QgsMessageLog.logMessage(f"PyArchInit - Column 'macc' is NOT NULL in {db_name}. Starting fix...", "PyArchInit", Qgis.Warning)

            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")

            try:
                # Check and drop the view if it exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='view' AND name='pyarchinit_uscaratterizzazioni_view'"
                )
                if cursor.fetchone():
                    cursor.execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view")
                    QgsMessageLog.logMessage(f"PyArchInit - Dropped view pyarchinit_uscaratterizzazioni_view in {db_name}", "PyArchInit", Qgis.Info)

                # Create temporary table with correct schema
                cursor.execute("""
                    CREATE TABLE tma_materiali_ripetibili_temp (
                        id             INTEGER PRIMARY KEY,
                        id_tma         INTEGER NOT NULL
                                       REFERENCES tma_materiali_archeologici(id)
                                       ON UPDATE NO ACTION
                                       ON DELETE NO ACTION,
                        madi           TEXT,
                        macc           TEXT,  -- Now nullable
                        macl           TEXT,
                        macp           TEXT,
                        macd           TEXT,
                        cronologia_mac TEXT,
                        macq           TEXT,
                        peso           FLOAT,
                        created_at     TEXT,
                        updated_at     TEXT,
                        created_by     TEXT,
                        updated_by     TEXT
                    )
                """)

                # Copy data from original table
                cursor.execute("""
                    INSERT INTO tma_materiali_ripetibili_temp
                    SELECT * FROM tma_materiali_ripetibili
                """)

                # Drop original table
                cursor.execute("DROP TABLE tma_materiali_ripetibili")

                # Rename temp table to original name
                cursor.execute(
                    "ALTER TABLE tma_materiali_ripetibili_temp RENAME TO tma_materiali_ripetibili"
                )

                # Commit transaction
                cursor.execute("COMMIT")
                QgsMessageLog.logMessage(f"PyArchInit - Successfully fixed 'macc' field in {db_name}", "PyArchInit", Qgis.Success)

            except Exception as e:
                cursor.execute("ROLLBACK")
                QgsMessageLog.logMessage(f"PyArchInit - Error during migration in {db_name}, rolled back: {str(e)}", "PyArchInit", Qgis.Critical)

            finally:
                conn.close()

        except Exception as e:
            QgsMessageLog.logMessage(f"PyArchInit - Error in fix_single_sqlite_database for {db_name}: {str(e)}", "PyArchInit", Qgis.Critical)

    def initGui(self):
        # Load configuration from config.cfg FIRST to get EXPERIMENTAL setting
        self.load_config()

        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if l == 'it':
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)

            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)

            # Tutorial button - before SAM Segmentation
            icon_tutorials = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tutorials.png'))
            self.actionTutorials = QAction(QIcon(icon_tutorials), "Tutorial e Documentazione", self.iface.mainWindow())
            self.actionTutorials.setWhatsThis("Apri la documentazione e i tutorial di PyArchInit")
            self.actionTutorials.setToolTip("Tutorial e Documentazione - Guide complete per l'utilizzo di PyArchInit")
            self.actionTutorials.triggered.connect(self.runTutorials)
            self.toolBar.addAction(self.actionTutorials)

            # SAM Stone Segmentation action (grouped in analysis tools below)
            icon_sam = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'sam_stones.png'))
            self.actionSamSegmentation = QAction(QIcon(icon_sam), "SAM Stone Segmentation", self.iface.mainWindow())
            self.actionSamSegmentation.setWhatsThis("Automatic stone segmentation using SAM AI model")
            self.actionSamSegmentation.setToolTip("SAM Stone Segmentation - Automatically detect and digitize stones from orthophotos")
            self.actionSamSegmentation.triggered.connect(self.runSamSegmentation)

            # AI Query Database button - standalone before data entry section
            icon_ai_query = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpt.png'))
            self.actionAIQuery = QAction(QIcon(icon_ai_query), "AI Query Database", self.iface.mainWindow())
            self.actionAIQuery.setWhatsThis("Interroga il database con linguaggio naturale usando AI")
            self.actionAIQuery.setToolTip("Query AI Database - Interroga il database archeologico con linguaggio naturale")
            self.actionAIQuery.triggered.connect(self.runAIQuery)
            self.toolBar.addAction(self.actionAIQuery)
            self.toolBar.addSeparator()

            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data

            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Siti", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Siti")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"US", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"US")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Reperti", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Reperti")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Campioni", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Campioni")
            self.actionCampioni.triggered.connect(self.runCampioni)
            icon_tma = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tma.png'))
            self.actionTma = QAction(QIcon(icon_tma), "TMA", self.iface.mainWindow())
            self.actionTma.setWhatsThis("TMA")
            self.actionTma.triggered.connect(self.runTma)
            icon_Pottery = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery.png'))
            self.actionPottery = QAction(QIcon(icon_Pottery), "Pottery", self.iface.mainWindow())
            self.actionPottery.setWhatsThis("Pottery")
            self.actionPottery.triggered.connect(self.runPottery)

            icon_PotteryTools = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery_tools.png'))
            self.actionPotteryTools = QAction(QIcon(icon_PotteryTools), "Pottery Tools", self.iface.mainWindow())
            self.actionPotteryTools.setWhatsThis("Pottery Tools")
            self.actionPotteryTools.triggered.connect(self.runPotteryTools)

            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodizzazione", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodizzazione")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Strutture", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Strutture")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individui", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individui")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Tomba", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Tomba")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.is_experimental_enabled():
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Determinazione Sesso", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Determinazione del sesso")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Determinazione dell'età", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"Determinazione dell'età")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.is_experimental_enabled():
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            #if self.is_experimental_enabled():
            self.topoToolButton = QToolButton(self.toolBar)
            #self.topoToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
            self.actionUT = QAction(QIcon(icon_UT), u"Unità Topografiche", self.iface.mainWindow())
            self.actionUT.setWhatsThis(u"Unità Topografiche")
            self.actionUT.triggered.connect(self.runUT)
            self.topoToolButton.addActions([self.actionUT])
            self.topoToolButton.setDefaultAction(self.actionUT)
            self.toolBar.addWidget(self.topoToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Scheda Documentazione",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Documentazione")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Gestione immagini", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Gestione immagini")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Esportazione immagini",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Esportazione immagini")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Esportazione PDF", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Esportazione PDF")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
            self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                   self.iface.mainWindow())
            self.actionGisTimeController.setWhatsThis("Time Manager")
            self.actionGisTimeController.triggered.connect(self.runGisTimeController)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionimageViewer,self.actionImages_Directory_export,self.actionpdfExp, self.actionExcel,self.actionGisTimeController])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to Fauna (non-experimental)
            self.faunaToolButton = QToolButton(self.toolBar)
            icon_Fauna = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconZoo.png'))
            self.actionFauna = QAction(QIcon(icon_Fauna), "Scheda Fauna", self.iface.mainWindow())
            self.actionFauna.setWhatsThis("Scheda Fauna - SCHEDA FR")
            self.actionFauna.triggered.connect(self.runFauna)
            self.faunaToolButton.addActions([self.actionFauna])
            self.faunaToolButton.setDefaultAction(self.actionFauna)
            self.toolBar.addWidget(self.faunaToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations (experimental)
            if self.is_experimental_enabled():
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
                # add Actions elaboration

                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Comparazione immagini", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Comparazione immagini")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionComparision)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            ######  Section dedicated to analysis tools
            self.analysisToolButton = QToolButton(self.toolBar)
            self.analysisToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Importa dati da TOPS", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Importa dati da TOPS")
            self.actionTops.triggered.connect(self.runTops)

            icon_imageSearch = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'search.png'))
            self.actionImageSearch = QAction(QIcon(icon_imageSearch), "Ricerca Immagini", self.iface.mainWindow())
            self.actionImageSearch.setWhatsThis("Ricerca Immagini")
            self.actionImageSearch.triggered.connect(self.runImageSearch)

            icon_geoarchaeo = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'geoarchaeo.png'))
            self.actionGeoArchaeo = QAction(QIcon(icon_geoarchaeo), "GeoArchaeo - Analisi Geostatistica", self.iface.mainWindow())
            self.actionGeoArchaeo.setWhatsThis("GeoArchaeo - Analisi Geostatistica per la Ricerca Archeologica")
            self.actionGeoArchaeo.triggered.connect(self.runGeoArchaeo)

            icon_movecost = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'movecost.png'))
            self.actionMovecost = QAction(QIcon(icon_movecost), "MoveCost - Analisi Costi di Percorso", self.iface.mainWindow())
            self.actionMovecost.setWhatsThis("MoveCost - Analisi dei costi di percorso basata su pendenza")
            self.actionMovecost.triggered.connect(self.runMovecost)

            self.analysisToolButton.addActions(
                [self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo, self.actionMovecost])
            self.analysisToolButton.setDefaultAction(self.actionSamSegmentation)
            self.toolBar.addWidget(self.analysisToolButton)
            self.toolBar.addSeparator()
            ####################################################################
            self.manageToolButton = QToolButton(self.toolBar)
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Crea la tua Mappa", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Crea la tua Mappa")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Impacchetta per geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Impacchetta per geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus sigle", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus sigle")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Configurazione plugin", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Configurazione plugin")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "Gestione database", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("Gestione database")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            # Database Update action
            icon_DbUpdate = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbUpdate = QAction(QIcon(icon_DbUpdate), "Aggiorna struttura database", self.iface.mainWindow())
            self.actionDbUpdate.setWhatsThis("Aggiorna la struttura del database (migrazione campi US, area, etc.)")
            self.actionDbUpdate.triggered.connect(self.runDbUpdate)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionDbUpdate, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export,self.actionExcel,self.actionGisTimeController])
            self.menu.addSeparator()
            self.menu.addActions([self.actionFauna])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionComparision])
            self.menu.addSeparator()
            self.menu.addActions([self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)

            # === Gestione Cantiere toolbar ===
            self.toolBarCantiere = self.iface.addToolBar("pyArchInit - Gestione Cantiere")
            self.toolBarCantiere.setObjectName("pyArchInitCantiere")

            icon_cantiere = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconCantiere.png'))
            icon_personale = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPersonale.png'))
            icon_presenze = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPresenze.png'))
            icon_attrezzature = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAttrezzature.png'))
            icon_budget = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconBudget.png'))

            self.actionCantiere = QAction(QIcon(icon_cantiere), "Dashboard Cantiere", self.iface.mainWindow())
            self.actionPersonale = QAction(QIcon(icon_personale), "Personale", self.iface.mainWindow())
            self.actionPresenze = QAction(QIcon(icon_presenze), "Presenze", self.iface.mainWindow())
            self.actionAttrezzature = QAction(QIcon(icon_attrezzature), "Attrezzature", self.iface.mainWindow())
            self.actionBudget = QAction(QIcon(icon_budget), "Budget", self.iface.mainWindow())

            # Connect signals
            self.actionCantiere.triggered.connect(self.runCantiere)
            self.actionPersonale.triggered.connect(self.runPersonale)
            self.actionPresenze.triggered.connect(self.runPresenze)
            self.actionAttrezzature.triggered.connect(self.runAttrezzature)
            self.actionBudget.triggered.connect(self.runBudget)

            # Add to toolbar
            self.toolBarCantiere.addAction(self.actionCantiere)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionPersonale)
            self.toolBarCantiere.addAction(self.actionPresenze)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionAttrezzature)
            self.toolBarCantiere.addAction(self.actionBudget)

            # Add to menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)

            self._init_stratigraph_sync()
        elif l == 'en':
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)
            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)

            # Tutorial button - before SAM Segmentation
            icon_tutorials = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tutorials.png'))
            self.actionTutorials = QAction(QIcon(icon_tutorials), "Tutorials & Documentation", self.iface.mainWindow())
            self.actionTutorials.setWhatsThis("Open PyArchInit documentation and tutorials")
            self.actionTutorials.setToolTip("Tutorials & Documentation - Complete guides for using PyArchInit")
            self.actionTutorials.triggered.connect(self.runTutorials)
            self.toolBar.addAction(self.actionTutorials)

            # SAM Stone Segmentation action (grouped in analysis tools below)
            icon_sam = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'sam_stones.png'))
            self.actionSamSegmentation = QAction(QIcon(icon_sam), "SAM Stone Segmentation", self.iface.mainWindow())
            self.actionSamSegmentation.setWhatsThis("Automatic stone segmentation using SAM AI model")
            self.actionSamSegmentation.setToolTip("SAM Stone Segmentation - Automatically detect and digitize stones from orthophotos")
            self.actionSamSegmentation.triggered.connect(self.runSamSegmentation)

            # AI Query Database button - standalone before data entry section
            icon_ai_query = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpt.png'))
            self.actionAIQuery = QAction(QIcon(icon_ai_query), "AI Query Database", self.iface.mainWindow())
            self.actionAIQuery.setWhatsThis("Query the database with natural language using AI")
            self.actionAIQuery.setToolTip("AI Query Database - Query the archaeological database with natural language")
            self.actionAIQuery.triggered.connect(self.runAIQuery)
            self.toolBar.addAction(self.actionAIQuery)
            self.toolBar.addSeparator()

            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data
            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Site", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Site")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"SU", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"SU")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Artefact", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Artefact")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Samples", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Samples")
            self.actionCampioni.triggered.connect(self.runCampioni)
            icon_Pottery = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery.png'))
            self.actionPottery = QAction(QIcon(icon_Pottery), "Pottery", self.iface.mainWindow())
            self.actionPottery.setWhatsThis("Pottery")
            self.actionPottery.triggered.connect(self.runPottery)

            icon_PotteryTools = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery_tools.png'))
            self.actionPotteryTools = QAction(QIcon(icon_PotteryTools), "Pottery Tools", self.iface.mainWindow())
            self.actionPotteryTools.setWhatsThis("Pottery Tools")
            self.actionPotteryTools.triggered.connect(self.runPotteryTools)

            icon_Tma = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tma.png'))
            self.actionTma = QAction(QIcon(icon_Tma), "Tma", self.iface.mainWindow())
            self.actionTma.setWhatsThis("Tma")
            self.actionTma.triggered.connect(self.runTma)

            # icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAlma.png'))
            # self.actionLapidei = QAction(QIcon(icon_Lapidei), "Stone", self.iface.mainWindow())
            # self.actionLapidei.setWhatsThis("Stone")
            # self.actionLapidei.triggered.connect(self.runLapidei)
            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodization", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodization")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Structure", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Structure")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individual", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individual")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Taphonomy", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Taphonomy")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.is_experimental_enabled():
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Sex determination", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Sex determination")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Age determination", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"Age determination")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.is_experimental_enabled():
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            self.topoToolButton = QToolButton(self.toolBar)
            icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
            self.actionUT = QAction(QIcon(icon_UT), u"Topographic Unit", self.iface.mainWindow())
            self.actionUT.setWhatsThis(u"Topographic Unit")
            self.actionUT.triggered.connect(self.runUT)
            self.topoToolButton.addActions([self.actionUT])
            self.topoToolButton.setDefaultAction(self.actionUT)
            self.toolBar.addWidget(self.topoToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Documentation",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Documentation")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)    
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Media manager", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Media menager")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Image exportation",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Image exportation")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Pdf exportation", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Pdf exportation")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
            self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                   self.iface.mainWindow())
            self.actionGisTimeController.setWhatsThis("Time Manager")
            self.actionGisTimeController.triggered.connect(self.runGisTimeController)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionimageViewer,self.actionImages_Directory_export,self.actionpdfExp, self.actionExcel,self.actionGisTimeController])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to Fauna (non-experimental)
            self.faunaToolButton = QToolButton(self.toolBar)
            icon_Fauna = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconZoo.png'))
            self.actionFauna = QAction(QIcon(icon_Fauna), "Fauna Record Sheet", self.iface.mainWindow())
            self.actionFauna.setWhatsThis("Fauna Record Sheet - FR")
            self.actionFauna.triggered.connect(self.runFauna)
            self.faunaToolButton.addActions([self.actionFauna])
            self.faunaToolButton.setDefaultAction(self.actionFauna)
            self.toolBar.addWidget(self.faunaToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations (experimental)
            if self.is_experimental_enabled():
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
                # add Actions elaboration
                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Image comparison", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Image comparison")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionComparision)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            ######  Section dedicated to analysis tools
            self.analysisToolButton = QToolButton(self.toolBar)
            self.analysisToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Import data from TOPS", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Import data from TOPS")
            self.actionTops.triggered.connect(self.runTops)

            icon_imageSearch = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'search.png'))
            self.actionImageSearch = QAction(QIcon(icon_imageSearch), "Image Search", self.iface.mainWindow())
            self.actionImageSearch.setWhatsThis("Image Search")
            self.actionImageSearch.triggered.connect(self.runImageSearch)

            icon_geoarchaeo = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'geoarchaeo.png'))
            self.actionGeoArchaeo = QAction(QIcon(icon_geoarchaeo), "GeoArchaeo - Geostatistical Analysis", self.iface.mainWindow())
            self.actionGeoArchaeo.setWhatsThis("GeoArchaeo - Geostatistical Analysis for Archaeological Research")
            self.actionGeoArchaeo.triggered.connect(self.runGeoArchaeo)

            icon_movecost = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'movecost.png'))
            self.actionMovecost = QAction(QIcon(icon_movecost), "MoveCost - Least-Cost Path Analysis", self.iface.mainWindow())
            self.actionMovecost.setWhatsThis("MoveCost - Slope-dependent cost of movement analysis")
            self.actionMovecost.triggered.connect(self.runMovecost)

            self.analysisToolButton.addActions(
                [self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo, self.actionMovecost])
            self.analysisToolButton.setDefaultAction(self.actionSamSegmentation)
            self.toolBar.addWidget(self.analysisToolButton)
            self.toolBar.addSeparator()

            self.manageToolButton = QToolButton(self.toolBar)
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Make your Map", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Make your Map")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Import into Geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Import into Geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus code", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus code")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Plugin settings", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Plugin settings")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "DB manager", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("DB manager")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            # Database Update action
            icon_DbUpdate = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbUpdate = QAction(QIcon(icon_DbUpdate), "Update database structure", self.iface.mainWindow())
            self.actionDbUpdate.setWhatsThis("Update database structure (US, area fields migration, etc.)")
            self.actionDbUpdate.triggered.connect(self.runDbUpdate)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionDbUpdate, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            # self.pyarchinitSite = pyarchinit_Site(self.iface)
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel, self.actionGisTimeController])
            self.menu.addSeparator()
            self.menu.addActions([self.actionFauna])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionComparision])
            self.menu.addSeparator()
            self.menu.addActions([self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)

            # === Site Management toolbar ===
            self.toolBarCantiere = self.iface.addToolBar("pyArchInit - Gestione Cantiere")
            self.toolBarCantiere.setObjectName("pyArchInitCantiere")

            icon_cantiere = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconCantiere.png'))
            icon_personale = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPersonale.png'))
            icon_presenze = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPresenze.png'))
            icon_attrezzature = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAttrezzature.png'))
            icon_budget = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconBudget.png'))

            self.actionCantiere = QAction(QIcon(icon_cantiere), "Site Dashboard", self.iface.mainWindow())
            self.actionPersonale = QAction(QIcon(icon_personale), "Personnel", self.iface.mainWindow())
            self.actionPresenze = QAction(QIcon(icon_presenze), "Attendance", self.iface.mainWindow())
            self.actionAttrezzature = QAction(QIcon(icon_attrezzature), "Equipment", self.iface.mainWindow())
            self.actionBudget = QAction(QIcon(icon_budget), "Budget", self.iface.mainWindow())

            # Connect signals
            self.actionCantiere.triggered.connect(self.runCantiere)
            self.actionPersonale.triggered.connect(self.runPersonale)
            self.actionPresenze.triggered.connect(self.runPresenze)
            self.actionAttrezzature.triggered.connect(self.runAttrezzature)
            self.actionBudget.triggered.connect(self.runBudget)

            # Add to toolbar
            self.toolBarCantiere.addAction(self.actionCantiere)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionPersonale)
            self.toolBarCantiere.addAction(self.actionPresenze)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionAttrezzature)
            self.toolBarCantiere.addAction(self.actionBudget)

            # Add to menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)

            self._init_stratigraph_sync()
        elif l=='de':
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)
            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)

            # Tutorial button - before SAM Segmentation
            icon_tutorials = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tutorials.png'))
            self.actionTutorials = QAction(QIcon(icon_tutorials), "Tutorials & Dokumentation", self.iface.mainWindow())
            self.actionTutorials.setWhatsThis("PyArchInit Dokumentation und Tutorials öffnen")
            self.actionTutorials.setToolTip("Tutorials & Dokumentation - Vollständige Anleitungen für PyArchInit")
            self.actionTutorials.triggered.connect(self.runTutorials)
            self.toolBar.addAction(self.actionTutorials)

            # SAM Stone Segmentation button - before AI Query
            icon_sam = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'sam_stones.png'))
            self.actionSamSegmentation = QAction(QIcon(icon_sam), "SAM Stein-Segmentierung", self.iface.mainWindow())
            self.actionSamSegmentation.setWhatsThis("Automatische Steinsegmentierung mit SAM AI-Modell")
            self.actionSamSegmentation.setToolTip("SAM Stein-Segmentierung - Steine automatisch aus Orthofotos erkennen")
            self.actionSamSegmentation.triggered.connect(self.runSamSegmentation)

            # AI Query Database button - standalone before data entry section
            icon_ai_query = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpt.png'))
            self.actionAIQuery = QAction(QIcon(icon_ai_query), "AI Query Database", self.iface.mainWindow())
            self.actionAIQuery.setWhatsThis("Datenbank mit natürlicher Sprache abfragen")
            self.actionAIQuery.setToolTip("AI Query Database - Archäologische Datenbank mit natürlicher Sprache abfragen")
            self.actionAIQuery.triggered.connect(self.runAIQuery)
            self.toolBar.addAction(self.actionAIQuery)
            self.toolBar.addSeparator()

            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data
            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Ausgrabungsstätte", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Ausgrabungsstätte")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"SE", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"SE")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Artefakts", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Artefakts")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Proben", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Proben")
            self.actionCampioni.triggered.connect(self.runCampioni)
            icon_Pottery = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery.png'))
            self.actionPottery = QAction(QIcon(icon_Pottery), "Pottery", self.iface.mainWindow())
            self.actionPottery.setWhatsThis("Pottery")
            self.actionPottery.triggered.connect(self.runPottery)

            icon_PotteryTools = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery_tools.png'))
            self.actionPotteryTools = QAction(QIcon(icon_PotteryTools), "Pottery Tools", self.iface.mainWindow())
            self.actionPotteryTools.setWhatsThis("Pottery Tools")
            self.actionPotteryTools.triggered.connect(self.runPotteryTools)

            icon_Tma = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tma.png'))
            self.actionTma = QAction(QIcon(icon_Tma), "Tma", self.iface.mainWindow())
            self.actionTma.setWhatsThis("Tma")
            self.actionTma.triggered.connect(self.runTma)
            # icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAlma.png'))
            # self.actionLapidei = QAction(QIcon(icon_Lapidei), "Steinartefakt", self.iface.mainWindow())
            # self.actionLapidei.setWhatsThis("Steinartefakt")
            # self.actionLapidei.triggered.connect(self.runLapidei)
            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodizierung", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodizierung")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Strukturen", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Strukturen")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individuen", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individuen")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Taphonomie", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Taphonomie")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.is_experimental_enabled():
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Geschlechtsbestimmung", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Geschlechtsbestimmung")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Altersbestimmung", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"DAltersbestimmung")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.is_experimental_enabled():
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            self.topoToolButton = QToolButton(self.toolBar)
            icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
            self.actionUT = QAction(QIcon(icon_UT), u"Topographische Einheit", self.iface.mainWindow())
            self.actionUT.setWhatsThis(u"Topographische Einheit")
            self.actionUT.triggered.connect(self.runUT)
            self.topoToolButton.addActions([self.actionUT])
            self.topoToolButton.setDefaultAction(self.actionUT)
            self.toolBar.addWidget(self.topoToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Formular dokumentation",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Formular dokumentation")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Media manager", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Media manager")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Exportation Bilder",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Exportation Bilder")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Exportation PDF", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Exportation PDF")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            if self.is_experimental_enabled():
                self.actionImages_Directory_export.setCheckable(True)
                self.actionpdfExp.setCheckable(True)
                self.actionimageViewer.setCheckable(True)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to Fauna (non-experimental)
            self.faunaToolButton = QToolButton(self.toolBar)
            icon_Fauna = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconZoo.png'))
            self.actionFauna = QAction(QIcon(icon_Fauna), "Fauna-Formular", self.iface.mainWindow())
            self.actionFauna.setWhatsThis("Fauna-Formular - FR")
            self.actionFauna.triggered.connect(self.runFauna)
            self.faunaToolButton.addActions([self.actionFauna])
            self.faunaToolButton.setDefaultAction(self.actionFauna)
            self.toolBar.addWidget(self.faunaToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations (experimental)
            if self.is_experimental_enabled():
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
                # add Actions elaboration
                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Bildvergleich", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Bildvergleich")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionComparision)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            # Analysis Tools group
            self.analysisToolButton = QToolButton(self.toolBar)
            self.analysisToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Daten von TOPS importieren", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Daten von TOPS importieren")
            self.actionTops.triggered.connect(self.runTops)

            icon_imageSearch = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'search_image.png'))
            self.actionImageSearch = QAction(QIcon(icon_imageSearch), "Bildersuche", self.iface.mainWindow())
            self.actionImageSearch.setWhatsThis("Bildersuche")
            self.actionImageSearch.triggered.connect(self.runImageSearch)

            icon_geoarchaeo = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'geoarchaeo.png'))
            self.actionGeoArchaeo = QAction(QIcon(icon_geoarchaeo), "GeoArchaeo - Geostatistische Analyse", self.iface.mainWindow())
            self.actionGeoArchaeo.setWhatsThis("GeoArchaeo - Geostatistische Analyse für die Archäologische Forschung")
            self.actionGeoArchaeo.triggered.connect(self.runGeoArchaeo)

            icon_movecost = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'movecost.png'))
            self.actionMovecost = QAction(QIcon(icon_movecost), "MoveCost - Wegkostenanalyse", self.iface.mainWindow())
            self.actionMovecost.setWhatsThis("MoveCost - Hangneigungsabhängige Wegkostenanalyse")
            self.actionMovecost.triggered.connect(self.runMovecost)

            self.analysisToolButton.addActions(
                [self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo, self.actionMovecost])
            self.analysisToolButton.setDefaultAction(self.actionSamSegmentation)
            self.toolBar.addWidget(self.analysisToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Make your Map", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Make your Map")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            #self.manageToolButton.setPopupMode(QToolButton.MenuButtonPopup)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Importiert ain geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Importiert ain geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Plugin settings", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Plugin settings")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "DB manager", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("DB manager")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            # Database Update action
            icon_DbUpdate = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbUpdate = QAction(QIcon(icon_DbUpdate), "Update database structure", self.iface.mainWindow())
            self.actionDbUpdate.setWhatsThis("Update database structure (US, area fields migration, etc.)")
            self.actionDbUpdate.triggered.connect(self.runDbUpdate)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionDbUpdate, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            # self.pyarchinitSite = pyarchinit_Site(self.iface)
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel, self.actionGisTimeController])
            self.menu.addSeparator()
            self.menu.addActions([self.actionFauna])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionComparision])
            self.menu.addSeparator()
            self.menu.addActions([self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)

            # === Baustellen-Verwaltung toolbar ===
            self.toolBarCantiere = self.iface.addToolBar("pyArchInit - Gestione Cantiere")
            self.toolBarCantiere.setObjectName("pyArchInitCantiere")

            icon_cantiere = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconCantiere.png'))
            icon_personale = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPersonale.png'))
            icon_presenze = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPresenze.png'))
            icon_attrezzature = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAttrezzature.png'))
            icon_budget = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconBudget.png'))

            self.actionCantiere = QAction(QIcon(icon_cantiere), "Baustellen-Dashboard", self.iface.mainWindow())
            self.actionPersonale = QAction(QIcon(icon_personale), "Personal", self.iface.mainWindow())
            self.actionPresenze = QAction(QIcon(icon_presenze), "Anwesenheit", self.iface.mainWindow())
            self.actionAttrezzature = QAction(QIcon(icon_attrezzature), "Ausrüstung", self.iface.mainWindow())
            self.actionBudget = QAction(QIcon(icon_budget), "Budget", self.iface.mainWindow())

            # Connect signals
            self.actionCantiere.triggered.connect(self.runCantiere)
            self.actionPersonale.triggered.connect(self.runPersonale)
            self.actionPresenze.triggered.connect(self.runPresenze)
            self.actionAttrezzature.triggered.connect(self.runAttrezzature)
            self.actionBudget.triggered.connect(self.runBudget)

            # Add to toolbar
            self.toolBarCantiere.addAction(self.actionCantiere)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionPersonale)
            self.toolBarCantiere.addAction(self.actionPresenze)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionAttrezzature)
            self.toolBarCantiere.addAction(self.actionBudget)

            # Add to menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)

            self._init_stratigraph_sync()
        else:
            settings = QgsSettings()
            icon_paius = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pai_us.png'))
            self.action = QAction(QIcon(icon_paius), "pyArchInit Main Panel",
                                  self.iface.mainWindow())
            self.action.triggered.connect(self.showHideDockWidget)
            # dock widget
            self.dockWidget = PyarchinitPluginDialog(self.iface)
            self.iface.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
            # TOOLBAR
            self.toolBar = self.iface.addToolBar("pyArchInit")
            self.toolBar.setObjectName("pyArchInit")
            self.toolBar.addAction(self.action)

            # Tutorial button - before SAM Segmentation
            icon_tutorials = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tutorials.png'))
            self.actionTutorials = QAction(QIcon(icon_tutorials), "Tutorials & Documentation", self.iface.mainWindow())
            self.actionTutorials.setWhatsThis("Open PyArchInit documentation and tutorials")
            self.actionTutorials.setToolTip("Tutorials & Documentation - Complete guides for using PyArchInit")
            self.actionTutorials.triggered.connect(self.runTutorials)
            self.toolBar.addAction(self.actionTutorials)

            # SAM Stone Segmentation action (grouped in analysis tools below)
            icon_sam = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'sam_stones.png'))
            self.actionSamSegmentation = QAction(QIcon(icon_sam), "SAM Stone Segmentation", self.iface.mainWindow())
            self.actionSamSegmentation.setWhatsThis("Automatic stone segmentation using SAM AI model")
            self.actionSamSegmentation.setToolTip("SAM Stone Segmentation - Automatically detect and digitize stones from orthophotos")
            self.actionSamSegmentation.triggered.connect(self.runSamSegmentation)

            # AI Query Database button - standalone before data entry section
            icon_ai_query = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpt.png'))
            self.actionAIQuery = QAction(QIcon(icon_ai_query), "AI Query Database", self.iface.mainWindow())
            self.actionAIQuery.setWhatsThis("Query the database with natural language using AI")
            self.actionAIQuery.setToolTip("AI Query Database - Query the archaeological database with natural language")
            self.actionAIQuery.triggered.connect(self.runAIQuery)
            self.toolBar.addAction(self.actionAIQuery)
            self.toolBar.addSeparator()

            self.dataToolButton = QToolButton(self.toolBar)
            self.dataToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            ######  Section dedicated to the basic data entry
            # add Actions data
            icon_site = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSite.png'))
            self.actionSite = QAction(QIcon(icon_site), "Site", self.iface.mainWindow())
            self.actionSite.setWhatsThis("Site")
            self.actionSite.triggered.connect(self.runSite)
            icon_US = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSus.png'))
            self.actionUS = QAction(QIcon((icon_US)), u"SU", self.iface.mainWindow())
            self.actionUS.setWhatsThis(u"SU")
            self.actionUS.triggered.connect(self.runUS)
            icon_Finds = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconFinds.png'))
            self.actionInr = QAction(QIcon(icon_Finds), "Artefact", self.iface.mainWindow())
            self.actionInr.setWhatsThis("Artefact")
            self.actionInr.triggered.connect(self.runInr)
            icon_camp_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'champion.png'))
            self.actionCampioni = QAction(QIcon(icon_camp_exp), "Samples", self.iface.mainWindow())
            self.actionCampioni.setWhatsThis("Samples")
            self.actionCampioni.triggered.connect(self.runCampioni)
            icon_Pottery = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery.png'))
            self.actionPottery = QAction(QIcon(icon_Pottery), "Pottery", self.iface.mainWindow())
            self.actionPottery.setWhatsThis("Pottery")
            self.actionPottery.triggered.connect(self.runPottery)

            icon_PotteryTools = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pottery_tools.png'))
            self.actionPotteryTools = QAction(QIcon(icon_PotteryTools), "Pottery Tools", self.iface.mainWindow())
            self.actionPotteryTools.setWhatsThis("Pottery Tools")
            self.actionPotteryTools.triggered.connect(self.runPotteryTools)

            icon_Tma = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tma.png'))
            self.actionTma = QAction(QIcon(icon_Tma), "Tma", self.iface.mainWindow())
            self.actionTma.setWhatsThis("Tma")
            self.actionTma.triggered.connect(self.runTma)

            # icon_Lapidei = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAlma.png'))
            # self.actionLapidei = QAction(QIcon(icon_Lapidei), "Stone", self.iface.mainWindow())
            # self.actionLapidei.setWhatsThis("Stone")
            # self.actionLapidei.triggered.connect(self.runLapidei)
            self.dataToolButton.addActions(
                [self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.dataToolButton.setDefaultAction(self.actionSite)
            self.toolBar.addWidget(self.dataToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the interpretations
            # add Actions interpretation
            self.interprToolButton = QToolButton(self.toolBar)
            self.interprToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_per = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPer.png'))
            self.actionPer = QAction(QIcon(icon_per), "Periodization", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Periodization")
            self.actionPer.triggered.connect(self.runPer)
            icon_Struttura = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconStrutt.png'))
            self.actionStruttura = QAction(QIcon(icon_Struttura), "Structure", self.iface.mainWindow())
            self.actionPer.setWhatsThis("Structure")
            self.actionStruttura.triggered.connect(self.runStruttura)
            self.interprToolButton.addActions([self.actionStruttura, self.actionPer])
            self.interprToolButton.setDefaultAction(self.actionStruttura)
            self.toolBar.addWidget(self.interprToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the funerary archaeology
            # add Actions funerary archaeology
            self.funeraryToolButton = QToolButton(self.toolBar)
            self.funeraryToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_Schedaind = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconIND.png'))
            self.actionSchedaind = QAction(QIcon(icon_Schedaind), "Individual", self.iface.mainWindow())
            self.actionSchedaind.setWhatsThis("Individual")
            self.actionSchedaind.triggered.connect(self.runSchedaind)
            icon_Tomba = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconGrave.png'))
            self.actionTomba = QAction(QIcon(icon_Tomba), "Taphonomy", self.iface.mainWindow())
            self.actionTomba.setWhatsThis("Taphonomy")
            self.actionTomba.triggered.connect(self.runTomba)
            if self.is_experimental_enabled():
                icon_Detsesso = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconSesso.png'))
                self.actionDetsesso = QAction(QIcon(icon_Detsesso), "Sex determination", self.iface.mainWindow())
                self.actionDetsesso.setWhatsThis("Sex determination")
                self.actionDetsesso.triggered.connect(self.runDetsesso)
                icon_Deteta = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconEta.png'))
                self.actionDeteta = QAction(QIcon(icon_Deteta), u"Age determination", self.iface.mainWindow())
                self.actionSchedaind.setWhatsThis(u"Age determination")
                self.actionDeteta.triggered.connect(self.runDeteta)
            self.funeraryToolButton.addActions([self.actionSchedaind, self.actionTomba])
            self.funeraryToolButton.setDefaultAction(self.actionSchedaind)
            if self.is_experimental_enabled():
                self.funeraryToolButton.addActions([self.actionDetsesso, self.actionDeteta])
            self.toolBar.addWidget(self.funeraryToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the topographical research
            self.topoToolButton = QToolButton(self.toolBar)
            icon_UT = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconUT.png'))
            self.actionUT = QAction(QIcon(icon_UT), u"Topographic Unit", self.iface.mainWindow())
            self.actionUT.setWhatsThis(u"Topographic Unit")
            self.actionUT.triggered.connect(self.runUT)
            self.topoToolButton.addActions([self.actionUT])
            self.topoToolButton.setDefaultAction(self.actionUT)
            self.toolBar.addWidget(self.topoToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the documentation
            # add Actions documentation
            self.docToolButton = QToolButton(self.toolBar)
            self.docToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_documentazione = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'icondoc.png'))
            self.actionDocumentazione = QAction(QIcon(icon_documentazione), "Documentation",
                                                self.iface.mainWindow())
            self.actionDocumentazione.setWhatsThis("Documentation")
            self.actionDocumentazione.triggered.connect(self.runDocumentazione)
            icon_excel_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'excel-export.png'))            
            self.actionExcel = QAction(QIcon(icon_excel_exp), "Download EXCEL", self.iface.mainWindow())
            self.actionExcel.setWhatsThis("Download EXCEL")
            self.actionExcel.triggered.connect(self.runExcel)    
            icon_imageViewer = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'photo.png'))
            self.actionimageViewer = QAction(QIcon(icon_imageViewer), "Media manager", self.iface.mainWindow())
            self.actionimageViewer.setWhatsThis("Media menager")
            self.actionimageViewer.triggered.connect(self.runImageViewer)
            icon_Directory_export = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'directoryExp.png'))
            self.actionImages_Directory_export = QAction(QIcon(icon_Directory_export), "Image exportation",
                                                         self.iface.mainWindow())
            self.actionImages_Directory_export.setWhatsThis("Image exportation")
            self.actionImages_Directory_export.triggered.connect(self.runImages_directory_export)
            icon_pdf_exp = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'pdf-icon.png'))
            self.actionpdfExp = QAction(QIcon(icon_pdf_exp), "Pdf exportation", self.iface.mainWindow())
            self.actionpdfExp.setWhatsThis("Pdf exportation")
            self.actionpdfExp.triggered.connect(self.runPdfexp)
            icon_GisTimeController = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconTimeControll.png'))
            self.actionGisTimeController = QAction(QIcon(icon_GisTimeController), "Time Manager",
                                                   self.iface.mainWindow())
            self.actionGisTimeController.setWhatsThis("Time Manager")
            self.actionGisTimeController.triggered.connect(self.runGisTimeController)
            self.docToolButton.addActions([self.actionDocumentazione,self.actionimageViewer,self.actionImages_Directory_export,self.actionpdfExp, self.actionExcel,self.actionGisTimeController])
            self.docToolButton.setDefaultAction(self.actionDocumentazione)
            self.toolBar.addWidget(self.docToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to Fauna (non-experimental)
            self.faunaToolButton = QToolButton(self.toolBar)
            icon_Fauna = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconZoo.png'))
            self.actionFauna = QAction(QIcon(icon_Fauna), "Fauna Record Sheet", self.iface.mainWindow())
            self.actionFauna.setWhatsThis("Fauna Record Sheet - FR")
            self.actionFauna.triggered.connect(self.runFauna)
            self.faunaToolButton.addActions([self.actionFauna])
            self.faunaToolButton.setDefaultAction(self.actionFauna)
            self.toolBar.addWidget(self.faunaToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to elaborations (experimental)
            if self.is_experimental_enabled():
                self.elabToolButton = QToolButton(self.toolBar)
                self.elabToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
                # add Actions elaboration
                icon_Comparision = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'comparision.png'))
                self.actionComparision = QAction(QIcon(icon_Comparision), "Image comparison", self.iface.mainWindow())
                self.actionComparision.setWhatsThis("Image comparison")
                self.actionComparision.triggered.connect(self.runComparision)
                self.elabToolButton.addActions(
                    [self.actionComparision, self.actionGisTimeController])
                self.elabToolButton.setDefaultAction(self.actionComparision)
                self.toolBar.addWidget(self.elabToolButton)
                self.toolBar.addSeparator()
            ######  Section dedicated to analysis tools
            self.analysisToolButton = QToolButton(self.toolBar)
            self.analysisToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

            icon_tops = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'tops.png'))
            self.actionTops = QAction(QIcon(icon_tops), "Import data from TOPS", self.iface.mainWindow())
            self.actionTops.setWhatsThis("Import data from TOPS")
            self.actionTops.triggered.connect(self.runTops)

            icon_imageSearch = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'search.png'))
            self.actionImageSearch = QAction(QIcon(icon_imageSearch), "Image Search", self.iface.mainWindow())
            self.actionImageSearch.setWhatsThis("Image Search")
            self.actionImageSearch.triggered.connect(self.runImageSearch)

            icon_geoarchaeo = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'geoarchaeo.png'))
            self.actionGeoArchaeo = QAction(QIcon(icon_geoarchaeo), "GeoArchaeo - Geostatistical Analysis", self.iface.mainWindow())
            self.actionGeoArchaeo.setWhatsThis("GeoArchaeo - Geostatistical Analysis for Archaeological Research")
            self.actionGeoArchaeo.triggered.connect(self.runGeoArchaeo)

            icon_movecost = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'movecost.png'))
            self.actionMovecost = QAction(QIcon(icon_movecost), "MoveCost - Least-Cost Path Analysis", self.iface.mainWindow())
            self.actionMovecost.setWhatsThis("MoveCost - Slope-dependent cost of movement analysis")
            self.actionMovecost.triggered.connect(self.runMovecost)

            self.analysisToolButton.addActions(
                [self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo, self.actionMovecost])
            self.analysisToolButton.setDefaultAction(self.actionSamSegmentation)
            self.toolBar.addWidget(self.analysisToolButton)
            self.toolBar.addSeparator()

            self.manageToolButton = QToolButton(self.toolBar)
            icon_print = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'print_map.png'))
            self.actionPrint = QAction(QIcon(icon_print), "Make your Map", self.iface.mainWindow())
            self.actionPrint.setWhatsThis("Make your Map")
            self.actionPrint.triggered.connect(self.runPrint)
            self.manageToolButton.addActions(
                [self.actionPrint])
            self.manageToolButton.setDefaultAction(self.actionPrint)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            self.manageToolButton = QToolButton(self.toolBar)
            icon_gpkg = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'gpkg.png'))
            self.actionGpkg = QAction(QIcon(icon_gpkg), "Import into Geopackage", self.iface.mainWindow())
            self.actionGpkg.setWhatsThis("Import into Geopackage")
            self.actionGpkg.triggered.connect(self.runGpkg)
            self.manageToolButton.addActions(
                [self.actionGpkg])
            self.manageToolButton.setDefaultAction(self.actionGpkg)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            ######  Section dedicated to the plugin management
            self.manageToolButton = QToolButton(self.toolBar)
            self.manageToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            icon_thesaurus = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'thesaurusicon.png'))
            self.actionThesaurus = QAction(QIcon(icon_thesaurus), "Thesaurus code", self.iface.mainWindow())
            self.actionThesaurus.setWhatsThis("Thesaurus code")
            self.actionThesaurus.triggered.connect(self.runThesaurus)
            icon_Con = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconConn.png'))
            self.actionConf = QAction(QIcon(icon_Con), "Plugin settings", self.iface.mainWindow())
            self.actionConf.setWhatsThis("Plugin settings")
            self.actionConf.triggered.connect(self.runConf)
            icon_Dbmanagment = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbmanagment = QAction(QIcon(icon_Dbmanagment), "DB manager", self.iface.mainWindow())
            self.actionDbmanagment.setWhatsThis("DB manager")
            self.actionDbmanagment.triggered.connect(self.runDbmanagment)
            # Database Update action
            icon_DbUpdate = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'backup.png'))
            self.actionDbUpdate = QAction(QIcon(icon_DbUpdate), "Update database structure", self.iface.mainWindow())
            self.actionDbUpdate.setWhatsThis("Update database structure (US, area fields migration, etc.)")
            self.actionDbUpdate.triggered.connect(self.runDbUpdate)
            icon_Info = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconInfo.png'))
            self.actionInfo = QAction(QIcon(icon_Info), "Plugin info", self.iface.mainWindow())
            self.actionInfo.setWhatsThis("Plugin info")
            self.actionInfo.triggered.connect(self.runInfo)
            self.manageToolButton.addActions(
                [self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionDbUpdate, self.actionInfo])
            self.manageToolButton.setDefaultAction(self.actionConf)
            self.toolBar.addWidget(self.manageToolButton)
            self.toolBar.addSeparator()
            # menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            #self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
            if self.is_experimental_enabled():
                self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            # MENU
            self.menu = QMenu("pyArchInit")
            # self.pyarchinitSite = pyarchinit_Site(self.iface)
            self.menu.addActions([self.actionSite, self.actionUS, self.actionInr, self.actionCampioni, self.actionPottery, self.actionTma])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPer, self.actionStruttura])
            self.menu.addSeparator()
            self.menu.addActions([self.actionTomba, self.actionSchedaind])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionDetsesso, self.actionDeteta])
            self.menu.addSeparator()
            self.menu.addActions([self.actionUT])
            self.menu.addActions([self.actionDocumentazione,self.actionimageViewer, self.actionpdfExp, self.actionImages_Directory_export, self.actionExcel, self.actionGisTimeController])
            self.menu.addSeparator()
            self.menu.addActions([self.actionFauna])
            if self.is_experimental_enabled():
                self.menu.addActions([self.actionComparision])
            self.menu.addSeparator()
            self.menu.addActions([self.actionSamSegmentation, self.actionPotteryTools, self.actionTops, self.actionImageSearch, self.actionGeoArchaeo])
            self.menu.addSeparator()
            self.menu.addActions([self.actionPrint])
            self.menu.addSeparator()
            self.menu.addActions([self.actionGpkg])
            self.menu.addSeparator()
            self.menu.addActions([self.actionConf, self.actionThesaurus, self.actionDbmanagment, self.actionInfo])
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.addMenu(self.menu)

            # === Site Management toolbar (fallback) ===
            self.toolBarCantiere = self.iface.addToolBar("pyArchInit - Gestione Cantiere")
            self.toolBarCantiere.setObjectName("pyArchInitCantiere")

            icon_cantiere = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconCantiere.png'))
            icon_personale = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPersonale.png'))
            icon_presenze = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconPresenze.png'))
            icon_attrezzature = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconAttrezzature.png'))
            icon_budget = '{}{}'.format(filepath, os.path.join(os.sep, 'resources', 'icons', 'iconBudget.png'))

            self.actionCantiere = QAction(QIcon(icon_cantiere), "Site Dashboard", self.iface.mainWindow())
            self.actionPersonale = QAction(QIcon(icon_personale), "Personnel", self.iface.mainWindow())
            self.actionPresenze = QAction(QIcon(icon_presenze), "Attendance", self.iface.mainWindow())
            self.actionAttrezzature = QAction(QIcon(icon_attrezzature), "Equipment", self.iface.mainWindow())
            self.actionBudget = QAction(QIcon(icon_budget), "Budget", self.iface.mainWindow())

            # Connect signals
            self.actionCantiere.triggered.connect(self.runCantiere)
            self.actionPersonale.triggered.connect(self.runPersonale)
            self.actionPresenze.triggered.connect(self.runPresenze)
            self.actionAttrezzature.triggered.connect(self.runAttrezzature)
            self.actionBudget.triggered.connect(self.runBudget)

            # Add to toolbar
            self.toolBarCantiere.addAction(self.actionCantiere)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionPersonale)
            self.toolBarCantiere.addAction(self.actionPresenze)
            self.toolBarCantiere.addSeparator()
            self.toolBarCantiere.addAction(self.actionAttrezzature)
            self.toolBarCantiere.addAction(self.actionBudget)

            # Add to menu
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.addPluginToMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)

            self._init_stratigraph_sync()

        # Log Rust acceleration status (after all UI is initialized)
        self._log_rust_status()

    def runSite(self):
        from .tabs.Site import pyarchinit_Site
        pluginGui = pyarchinit_Site(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runPer(self):
        from .tabs.Periodizzazione import pyarchinit_Periodizzazione
        pluginGui = pyarchinit_Periodizzazione(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runStruttura(self):
        from .tabs.Struttura import pyarchinit_Struttura
        pluginGui = pyarchinit_Struttura(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runUS(self):
        from .tabs.US_USM import pyarchinit_US
        pluginGui = pyarchinit_US(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runAIQuery(self):
        """Open the AI Query Database dialog for natural language database queries"""
        try:
            from .tabs.US_USM import RAGQueryDialog
            from .modules.db.pyarchinit_conn_strings import Connection
            from .modules.db.pyarchinit_db_manager import get_db_manager

            conn = Connection()
            conn_str = conn.conn_str()
            db_manager = get_db_manager(conn_str, use_singleton=True)

            dialog = RAGQueryDialog(db_manager, parent=None)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                f"Errore nell'apertura del dialogo AI Query:\n{str(e)}"
            )

    def runTutorials(self):
        """Open the Tutorials and Documentation viewer dialog"""
        try:
            from .tabs.Tutorial_viewer import TutorialViewerDialog
            dialog = TutorialViewerDialog(parent=self.iface.mainWindow())
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                f"Error opening Tutorials dialog:\n{str(e)}"
            )

    def runSamSegmentation(self):
        """Open the SAM Stone Segmentation dialog"""
        try:
            from .tabs.Sam_Segmentation_Dialog import SamSegmentationDialog
            from .modules.db.pyarchinit_conn_strings import Connection
            from .modules.db.pyarchinit_db_manager import get_db_manager

            conn = Connection()
            conn_str = conn.conn_str()
            db_manager = get_db_manager(conn_str, use_singleton=True)

            dialog = SamSegmentationDialog(db_manager, parent=self.iface.mainWindow())
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                f"Error opening SAM Segmentation dialog:\n{str(e)}"
            )

    def runInr(self):
        from .tabs.Inv_Materiali import pyarchinit_Inventario_reperti
        pluginGui = pyarchinit_Inventario_reperti(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runTma(self):
        from .tabs.Tma import pyarchinit_Tma
        pluginGui = pyarchinit_Tma(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runCampioni(self):
        from .tabs.Campioni import pyarchinit_Campioni
        pluginGui = pyarchinit_Campioni(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPottery(self):
        from .tabs.pyarchinit_Pottery_mainapp import pyarchinit_Pottery
        pluginGui = pyarchinit_Pottery(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    def runPotteryTools(self):
        from .tabs.Pottery_tools import PotteryToolsDialog
        pluginGui = PotteryToolsDialog(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save

    # def runLapidei(self):
        # pluginGui = pyarchinit_Inventario_Lapidei(self.iface)
        # pluginGui.show()
        # self.pluginGui = pluginGui  # save
    def runGisTimeController(self):
        from .tabs.Gis_Time_controller import pyarchinit_Gis_Time_Controller
        pluginGui = pyarchinit_Gis_Time_Controller(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui  # save
    def runTops(self):
        from .tabs.tops_pyarchinit import pyarchinit_TOPS
        pluginTops = pyarchinit_TOPS(self.iface)
        pluginTops.show()
        self.pluginGui = pluginTops  # save
    def runPrint(self):
        from .tabs.PRINTMAP import pyarchinit_PRINTMAP
        pluginPrint = pyarchinit_PRINTMAP(self.iface)
        pluginPrint.show()
        self.pluginGui = pluginPrint  # save
    def runGpkg(self):
        from .tabs.gpkg_export import pyarchinit_GPKG
        pluginGpkg = pyarchinit_GPKG(self.iface)
        pluginGpkg.show()
        self.pluginGui = pluginGpkg  # save
    def runConf(self):
        from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
        pluginConfGui = pyArchInitDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save
    def runDbUpdate(self):
        """Open config dialog and trigger database schema update."""
        from .gui.pyarchinitConfigDialog import pyArchInitDialog_Config
        pluginConfGui = pyArchInitDialog_Config()
        pluginConfGui.show()
        self.pluginGui = pluginConfGui  # save
        # Trigger the database update
        pluginConfGui.update_database_schema()
    def runInfo(self):
        from .gui.pyarchinitInfoDialog import pyArchInitDialog_Info
        pluginInfoGui = pyArchInitDialog_Info()
        pluginInfoGui.show()
        self.pluginGui = pluginInfoGui  # save
    def runImageViewer(self):
        from .tabs.Image_viewer import Main
        pluginImageView = Main()
        pluginImageView.show()
        self.pluginGui = pluginImageView  # save
    def runImageSearch(self):
        from .tabs.Image_search import pyarchinit_Image_Search
        pluginImageSearch = pyarchinit_Image_Search(self.iface)
        pluginImageSearch.show()
        self.pluginGui = pluginImageSearch  # save
    def runGeoArchaeo(self):
        """Open the GeoArchaeo geostatistical analysis panel."""
        try:
            from .modules.geoarchaeo.gui.main_dock import GeoArchaeoDockWidget
            if not hasattr(self, '_geoarchaeo_dock') or self._geoarchaeo_dock is None:
                self._geoarchaeo_dock = GeoArchaeoDockWidget(self.iface.mainWindow())
                self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._geoarchaeo_dock)
            self._geoarchaeo_dock.show()
            self._geoarchaeo_dock.raise_()
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "GeoArchaeo",
                f"Error opening GeoArchaeo panel:\n{str(e)}"
            )

    def runMovecost(self):
        """Open the MoveCost least-cost path analysis dialog."""
        try:
            from .tabs.Movecost import pyarchinit_Movecost
            pluginMovecost = pyarchinit_Movecost(self.iface)
            pluginMovecost.show()
            self.pluginGui = pluginMovecost
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "MoveCost",
                f"Error opening MoveCost dialog:\n{str(e)}"
            )

    def runTomba(self):
        from .tabs.Tomba import pyarchinit_Tomba
        pluginTomba = pyarchinit_Tomba(self.iface)
        pluginTomba.show()
        self.pluginGui = pluginTomba  # save
    def runSchedaind(self):
        from .tabs.Schedaind import pyarchinit_Schedaind
        pluginIndividui = pyarchinit_Schedaind(self.iface)
        pluginIndividui.show()
        self.pluginGui = pluginIndividui  # save
    def runDetsesso(self):
        from .tabs.Detsesso import pyarchinit_Detsesso
        pluginSesso = pyarchinit_Detsesso(self.iface)
        pluginSesso.show()
        self.pluginGui = pluginSesso  # save
    def runDeteta(self):
        from .tabs.Deteta import pyarchinit_Deteta
        pluginEta = pyarchinit_Deteta(self.iface)
        pluginEta.show()
        self.pluginGui = pluginEta  # save
    def runFauna(self):
        from .tabs.Fauna import pyarchinit_Fauna
        pluginFauna = pyarchinit_Fauna(self.iface)
        pluginFauna.show()
        self.pluginGui = pluginFauna  # save
    def runUT(self):
        from .tabs.UT import pyarchinit_UT
        pluginUT = pyarchinit_UT(self.iface)
        pluginUT.show()
        self.pluginGui = pluginUT  # save
    def runImages_directory_export(self):
        from .tabs.Images_directory_export import pyarchinit_Images_directory_export
        pluginImage_directory_export = pyarchinit_Images_directory_export()
        pluginImage_directory_export.show()
        self.pluginGui = pluginImage_directory_export  # save
    def runComparision(self):
        from .tabs.Images_comparison import Comparision
        pluginComparision = Comparision()
        pluginComparision.show()
        self.pluginGui = pluginComparision  # save
    def runDbmanagment(self):
        from .gui.dbmanagment import pyarchinit_dbmanagment
        pluginDbmanagment = pyarchinit_dbmanagment(self.iface)
        pluginDbmanagment.show()
        self.pluginGui = pluginDbmanagment  # save
    def runPdfexp(self):
        from .tabs.Pdf_export import pyarchinit_pdf_export
        pluginPdfexp = pyarchinit_pdf_export(self.iface)
        pluginPdfexp.show()
        self.pluginGui = pluginPdfexp  # save
    def runThesaurus(self):
        from .tabs.Thesaurus import pyarchinit_Thesaurus
        pluginThesaurus = pyarchinit_Thesaurus(self.iface)
        pluginThesaurus.show()
        self.pluginGui = pluginThesaurus  # save
    def runDocumentazione(self):
        from .tabs.Documentazione import pyarchinit_Documentazione
        pluginDocumentazione = pyarchinit_Documentazione(self.iface)
        pluginDocumentazione.show()
        self.pluginGui = pluginDocumentazione  # save
    def runExcel(self):
        from .tabs.Excel_export import pyarchinit_excel_export
        pluginExcel = pyarchinit_excel_export(self.iface)
        pluginExcel.show()
        self.pluginGui = pluginExcel  # save

    def runCantiere(self):
        if not self._check_cantiere_permission('cantiere_table'):
            self._show_cantiere_permission_denied()
            return
        from .tabs.Cantiere import pyarchinit_Cantiere
        pluginGui = pyarchinit_Cantiere(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runPersonale(self):
        if not self._check_cantiere_permission('cantiere_personale_table'):
            self._show_cantiere_permission_denied()
            return
        from .tabs.Personale import pyarchinit_Personale
        pluginGui = pyarchinit_Personale(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runPresenze(self):
        if not self._check_cantiere_permission('cantiere_presenze_table'):
            self._show_cantiere_permission_denied()
            return
        from .tabs.Presenze import pyarchinit_Presenze
        pluginGui = pyarchinit_Presenze(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runAttrezzature(self):
        if not self._check_cantiere_permission('cantiere_attrezzature_table'):
            self._show_cantiere_permission_denied()
            return
        from .tabs.Attrezzature import pyarchinit_Attrezzature
        pluginGui = pyarchinit_Attrezzature(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def runBudget(self):
        if not self._check_cantiere_permission('cantiere_budget_table'):
            self._show_cantiere_permission_denied()
            return
        from .tabs.Budget import pyarchinit_Budget
        pluginGui = pyarchinit_Budget(self.iface)
        pluginGui.show()
        self.pluginGui = pluginGui

    def unload(self):
        # StratiGraph sync cleanup (locale-independent)
        self._unload_stratigraph_sync()
        # GeoArchaeo dock cleanup (locale-independent)
        if hasattr(self, '_geoarchaeo_dock') and self._geoarchaeo_dock is not None:
            self.iface.removeDockWidget(self._geoarchaeo_dock)
            self._geoarchaeo_dock = None
        # Remove the plugin
        l=QgsSettings().value("locale/userLocale", "it", type=str)[:2]
        if l == 'it':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)

                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            self.iface.removeToolBarIcon(self.actionPottery)
            self.iface.removeToolBarIcon(self.actionPotteryTools)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionFauna)

                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionUT)
            self.iface.removeToolBarIcon(self.actionTops)
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self._unload_main_dockwidget()

            if self.plugin_window:
                self.plugin_window.close()
                self.plugin_window = None

            # Gestione Cantiere cleanup
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)
            self.iface.removeToolBarIcon(self.actionCantiere)
            self.iface.removeToolBarIcon(self.actionPersonale)
            self.iface.removeToolBarIcon(self.actionPresenze)
            self.iface.removeToolBarIcon(self.actionAttrezzature)
            self.iface.removeToolBarIcon(self.actionBudget)
            del self.toolBarCantiere

            # remove tool bar
            del self.toolBar

        elif l== 'en':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            self.iface.removeToolBarIcon(self.actionPottery)
            self.iface.removeToolBarIcon(self.actionPotteryTools)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionFauna)
                self.iface.removeToolBarIcon(self.actionUT)
                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionTops)
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self._unload_main_dockwidget()
            # Gestione Cantiere cleanup
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)
            self.iface.removeToolBarIcon(self.actionCantiere)
            self.iface.removeToolBarIcon(self.actionPersonale)
            self.iface.removeToolBarIcon(self.actionPresenze)
            self.iface.removeToolBarIcon(self.actionAttrezzature)
            self.iface.removeToolBarIcon(self.actionBudget)
            del self.toolBarCantiere

            # remove tool bar
            del self.toolBar
        elif l== 'de':
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            self.iface.removeToolBarIcon(self.actionPottery)
            self.iface.removeToolBarIcon(self.actionPotteryTools)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionFauna)
                self.iface.removeToolBarIcon(self.actionUT)
                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionTops)
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self._unload_main_dockwidget()

            # Gestione Cantiere cleanup
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)
            self.iface.removeToolBarIcon(self.actionCantiere)
            self.iface.removeToolBarIcon(self.actionPersonale)
            self.iface.removeToolBarIcon(self.actionPresenze)
            self.iface.removeToolBarIcon(self.actionAttrezzature)
            self.iface.removeToolBarIcon(self.actionBudget)
            del self.toolBarCantiere

            # remove tool bar
            del self.toolBar
        else:
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSite)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPer)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionStruttura)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUS)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInr)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTma)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCampioni)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPottery)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPotteryTools)
            #self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionLapidei)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionSchedaind)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDocumentazione)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDetsesso)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDeteta)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTomba)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionFauna)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionUT)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionimageViewer)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImages_Directory_export)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionpdfExp)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionComparision)
                self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGisTimeController)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionTops)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionImageSearch)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGeoArchaeo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionMovecost)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPrint)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionGpkg)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionConf)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionThesaurus)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionInfo)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionDbmanagment)
            self.iface.removeToolBarIcon(self.actionSite)
            self.iface.removeToolBarIcon(self.actionPer)
            self.iface.removeToolBarIcon(self.actionStruttura)
            self.iface.removeToolBarIcon(self.actionUS)
            self.iface.removeToolBarIcon(self.actionInr)
            self.iface.removeToolBarIcon(self.actionCampioni)
            self.iface.removeToolBarIcon(self.actionPottery)
            self.iface.removeToolBarIcon(self.actionPotteryTools)
            #self.iface.removeToolBarIcon(self.actionLapidei)
            self.iface.removeToolBarIcon(self.actionTomba)
            self.iface.removeToolBarIcon(self.actionSchedaind)
            self.iface.removeToolBarIcon(self.actionDocumentazione)
            self.iface.removeToolBarIcon(self.actionExcel)
            if self.is_experimental_enabled():
                self.iface.removeToolBarIcon(self.actionDetsesso)
                self.iface.removeToolBarIcon(self.actionDeteta)
                self.iface.removeToolBarIcon(self.actionFauna)
                self.iface.removeToolBarIcon(self.actionUT)
                # self.iface.removeToolBarIcon(self.actionUpd)
                self.iface.removeToolBarIcon(self.actionimageViewer)
                self.iface.removeToolBarIcon(self.actionImages_Directory_export)
                self.iface.removeToolBarIcon(self.actionpdfExp)
                self.iface.removeToolBarIcon(self.actionComparision)
                self.iface.removeToolBarIcon(self.actionGisTimeController)
            self.iface.removeToolBarIcon(self.actionTops)
            self.iface.removeToolBarIcon(self.actionPrint)
            self.iface.removeToolBarIcon(self.actionGpkg)
            self.iface.removeToolBarIcon(self.actionConf)
            self.iface.removeToolBarIcon(self.actionThesaurus)
            self.iface.removeToolBarIcon(self.actionInfo)
            self.iface.removeToolBarIcon(self.actionDbmanagment)
            self._unload_main_dockwidget()

            # Gestione Cantiere cleanup
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionCantiere)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPersonale)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionPresenze)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionAttrezzature)
            self.iface.removePluginMenu("&pyArchInit - Archaeological GIS Tools", self.actionBudget)
            self.iface.removeToolBarIcon(self.actionCantiere)
            self.iface.removeToolBarIcon(self.actionPersonale)
            self.iface.removeToolBarIcon(self.actionPresenze)
            self.iface.removeToolBarIcon(self.actionAttrezzature)
            self.iface.removeToolBarIcon(self.actionBudget)
            del self.toolBarCantiere

            # remove tool bar
            del self.toolBar
    def showHideDockWidget(self):
        if self.dockWidget.isVisible():
            self.dockWidget.hide()
        else:
            self.dockWidget.show()

    # ── Rust Acceleration Status ───────────────────────────────────────
    def _log_rust_status(self):
        """Log the Rust acceleration module status at plugin startup."""
        try:
            s = QgsSettings()
            enabled = s.value(
                'pyArchInit/rust_acceleration_enabled', True, type=bool)
            if not enabled:
                QgsMessageLog.logMessage(
                    "Rust acceleration: disabled by user",
                    "PyArchInit", Qgis.MessageLevel.Info)
                return

            from .scripts.rust_installer import check_rust_available
            available, version = check_rust_available()
            if available:
                QgsMessageLog.logMessage(
                    f"Rust acceleration: active (v{version})",
                    "PyArchInit", Qgis.MessageLevel.Info)
            else:
                QgsMessageLog.logMessage(
                    "Rust acceleration: not installed "
                    "(optional - install via Settings > Rust Acceleration)",
                    "PyArchInit", Qgis.MessageLevel.Info)
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Rust acceleration: status check failed ({e})",
                "PyArchInit", Qgis.MessageLevel.Warning)

    # ── StratiGraph Sync ────────────────────────────────────────────────
    def _init_stratigraph_sync(self):
        """Initialise the StratiGraph offline-first sync subsystem."""
        try:
            from .modules.stratigraph.sync_orchestrator import SyncOrchestrator
            from .gui.stratigraph_sync_panel import StratiGraphSyncPanel

            self.sync_orchestrator = SyncOrchestrator()
            self.sync_panel = StratiGraphSyncPanel(self.sync_orchestrator)
            self.iface.addDockWidget(
                Qt.DockWidgetArea.LeftDockWidgetArea, self.sync_panel)
            self.sync_panel.hide()  # hidden by default

            # Toolbar toggle action
            icon_sync = '{}{}'.format(
                filepath,
                os.path.join(os.sep, 'resources', 'icons', 'stratigraph_sync.png'))
            self.actionStratiGraphSync = QAction(
                QIcon(icon_sync), "StratiGraph Sync",
                self.iface.mainWindow())
            self.actionStratiGraphSync.setCheckable(True)
            self.actionStratiGraphSync.setToolTip(
                "Show / hide the StratiGraph sync panel")
            self.actionStratiGraphSync.toggled.connect(
                self._toggle_sync_panel)
            self.toolBar.addAction(self.actionStratiGraphSync)

            self.sync_orchestrator.start()
        except Exception as e:
            QgsMessageLog.logMessage(
                f"StratiGraph sync init failed: {e}",
                "PyArchInit", Qgis.MessageLevel.Warning)
            self.sync_orchestrator = None
            self.sync_panel = None

        # Phase 1 migrations menu (spec §4.4 / §4.5)
        self._init_migrations_menu()

    # ── Phase 1 migrations menu ─────────────────────────────────────────
    def _init_migrations_menu(self):
        """Wire the one-shot migration entries into the plugin menu.

        Invoked from `_init_stratigraph_sync()` so it runs exactly once per
        language branch in `initGui()`. Idempotent against re-init via the
        ``_migrations_menu_wired`` guard.
        """
        if getattr(self, "_migrations_menu_wired", False):
            return
        try:
            self.actionVocabAlign = QAction(
                "Migrazioni → Allinea vocabolario US "
                "(USVA/USVB→USVs, USVC→USVn)",
                self.iface.mainWindow())
            self.actionVocabAlign.triggered.connect(
                self._run_vocab_alignment_migration)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionVocabAlign)

            self.actionUuidBackfill = QAction(
                "Migrazioni → Backfill node_uuid (UUID v7 per record)",
                self.iface.mainWindow())
            self.actionUuidBackfill.triggered.connect(
                self._run_uuid_backfill_migration)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionUuidBackfill)

            # yE-F other_locations column migration (yed-f-multifolder-5.9.0-alpha):
            # add us_table.other_locations TEXT column on legacy DBs.
            self.actionYefOtherLocations = QAction(
                "Migrazioni → Aggiungi colonna other_locations (yE-F)",
                self.iface.mainWindow())
            self.actionYefOtherLocations.triggered.connect(
                self._run_yef_migration)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionYefOtherLocations)

            # media-fk-migration 5.7.9.3-alpha: drop the legacy killer
            # triggers on media_thumb_table and replace them with proper
            # FK ON DELETE CASCADE. PG-only (SQLite templates were
            # already cleaned in-place by this milestone).
            self.actionMediaFkMigration = QAction(
                "Migrazioni → Fix trigger media (cascade pericoloso)",
                self.iface.mainWindow())
            self.actionMediaFkMigration.triggered.connect(
                self._run_media_fk_migration)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionMediaFkMigration)

            # inventario_materiali schedatore fields (post-5.9.0.1-alpha):
            # add 5 TEXT columns missing on DBs whose auto-migration in
            # pyarchinit_db_update.py:446-459 silently skipped (typical
            # of DBs imported from backups or older plugin installs).
            self.actionSchedatoreFields = QAction(
                "Migrazioni → Aggiungi colonne schedatore "
                "(inventario_materiali)",
                self.iface.mainWindow())
            self.actionSchedatoreFields.triggered.connect(
                self._run_schedatore_fields_migration)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionSchedatoreFields)

            # Schema repair (post-5.9.0.1-alpha): full audit + fix.
            # Use this when the "Update DB" button in the config dialog
            # fails to migrate everything (typical symptom: "no such
            # table" or "no such column" errors after opening a legacy
            # DB). Idempotent: safe to re-run.
            self.actionSchemaRepair = QAction(
                "Migrazioni → Schema repair (tabelle + colonne mancanti)",
                self.iface.mainWindow())
            self.actionSchemaRepair.triggered.connect(
                self._run_schema_repair_migration)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionSchemaRepair)

            self._migrations_menu_wired = True
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Migrations menu wiring failed: {e}",
                "PyArchInit", Qgis.MessageLevel.Warning)

    def _run_vocab_alignment_migration(self):
        """File-picker + dry-run preview + confirmation + apply (with backup)."""
        from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
        from pathlib import Path
        try:
            from .scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
                apply_changes,
                plan_changes,
            )
            from .scripts.migrations._common import auto_backup_sqlite
        except Exception:
            # Fall back to absolute import (when not running under the QGIS
            # plugin loader that registers the package).
            from scripts.migrations._2026_05_us_vocabulary_alignment_lib import (
                apply_changes,
                plan_changes,
            )
            from scripts.migrations._common import auto_backup_sqlite

        db_path, _ = QFileDialog.getOpenFileName(
            self.iface.mainWindow(),
            "Seleziona il database pyarchinit (.sqlite)",
            "",
            "SQLite databases (*.sqlite)",
        )
        if not db_path:
            return
        db = Path(db_path)
        try:
            plan = plan_changes(db)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore lettura database",
                f"Impossibile leggere il piano dalla DB:\n{e}",
            )
            return

        msg = "Piano:\n" + "\n".join(f"  {k}: {v}" for k, v in plan.items())
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma migrazione vocabolario US",
            msg + "\n\nProcedere con --apply (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        try:
            backup = auto_backup_sqlite(db, tag="us_vocab_alignment")
            applied = apply_changes(db)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore migrazione",
                f"La migrazione è fallita:\n{e}",
            )
            return
        QMessageBox.information(
            self.iface.mainWindow(),
            "Migrazione completata",
            f"Backup: {backup}\n\nAggiornamenti: {applied}",
        )

    def _run_uuid_backfill_migration(self):
        """Backfill node_uuid on the currently-connected pyarchinit DB.

        PG-A (5.7.0-alpha): no file picker — uses the conn-str from the
        plugin's Connection() helper. Backup helper dispatches per backend.
        """
        from qgis.PyQt.QtWidgets import QMessageBox
        from pathlib import Path
        try:
            from .modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from .modules.db.pyarchinit_conn_strings import Connection
            from .scripts.migrations._2026_05_node_uuid_backfill_lib import (
                TABLES, add_columns, backfill_uuids,
            )
            from .scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )
        except Exception:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from modules.db.pyarchinit_conn_strings import Connection
            from scripts.migrations._2026_05_node_uuid_backfill_lib import (
                TABLES, add_columns, backfill_uuids,
            )
            from scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )

        conn_str = Connection().conn_str()
        if not conn_str:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Connessione non configurata",
                "Connetti prima un DB pyarchinit dalle Settings (menu "
                "Database → Configurazione)."
            )
            return

        try:
            handle = _resolve_db_handle(conn_str)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore di connessione",
                f"Impossibile aprire la connessione al DB:\n{e}",
            )
            return

        backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                         + "/" + str(handle.engine.url.database or "")
                         if handle.is_postgres
                         else f"SQLite: {handle.sqlite_path}")
        tables_list = "\n".join(f"  - {t}" for t in TABLES)
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma backfill node_uuid",
            f"Backend: {backend_label}\n\n"
            "Verrà aggiunta la colonna node_uuid (TEXT) e assegnato un "
            "UUID v7 a ogni record nelle tabelle:\n"
            f"{tables_list}\n\n"
            "Procedere con --apply (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        backup_path = None
        try:
            if handle.is_postgres:
                dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                            / "_pga_backups")
                try:
                    backup_path = auto_backup_postgres(
                        handle.engine, tag="node_uuid_backfill",
                        dest_dir=dest_dir,
                    )
                except BackupSkipped as e:
                    skip = QMessageBox.question(
                        self.iface.mainWindow(),
                        "Backup non disponibile",
                        f"{e}\n\nProcedere SENZA backup automatico "
                        "(sconsigliato)?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if skip != QMessageBox.Yes:
                        return
                    backup_path = None
            else:
                backup_path = auto_backup_sqlite(
                    handle.sqlite_path, tag="node_uuid_backfill",
                )
            add_columns(handle)
            counts = backfill_uuids(handle)
        except Exception as e:
            msg = (f"La migrazione è fallita:\n{e}\n\n"
                   f"Backup creato: {backup_path}") if backup_path \
                else f"La migrazione è fallita:\n{e}\n\nNessun backup creato."
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore migrazione",
                msg,
            )
            return

        counts_msg = "\n".join(
            f"  {table}: {n} row(s)" for table, n in counts.items())
        QMessageBox.information(
            self.iface.mainWindow(),
            "Backfill completato",
            f"Backup: {backup_path}\n\nUUID v7 assegnati:\n{counts_msg}",
        )

    def _run_yef_migration(self):
        """yE-F other_locations column migration (yed-f-multifolder-5.9.0-alpha).

        Adds the ``other_locations`` TEXT column to ``us_table`` so the
        multi-folder paradata feature can persist secondary location
        memberships per US record.

        Pattern mirrors ``_run_uuid_backfill_migration``: resolve handle
        from the configured Connection (no file picker), confirm,
        auto-backup, apply via the migration lib, summarize.
        """
        from qgis.PyQt.QtWidgets import QMessageBox
        from pathlib import Path
        try:
            from .modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from .modules.db.pyarchinit_conn_strings import Connection
            from .scripts.migrations._2026_05_yef_other_locations_lib import (
                add_other_locations_column,
            )
            from .scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )
        except Exception:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from modules.db.pyarchinit_conn_strings import Connection
            from scripts.migrations._2026_05_yef_other_locations_lib import (
                add_other_locations_column,
            )
            from scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )

        conn_str = Connection().conn_str()
        if not conn_str:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Connessione non configurata",
                "Connetti prima un DB pyarchinit dalle Settings (menu "
                "Database → Configurazione).",
            )
            return

        try:
            handle = _resolve_db_handle(conn_str)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore di connessione",
                f"Impossibile aprire la connessione al DB:\n{e}",
            )
            return

        backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                         + "/" + str(handle.engine.url.database or "")
                         if handle.is_postgres
                         else f"SQLite: {handle.sqlite_path}")
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma migrazione yE-F",
            f"Backend: {backend_label}\n\n"
            "Verrà aggiunta la colonna TEXT ``other_locations`` a "
            "us_table (idempotente: salta la tabella se già presente).\n\n"
            "Procedere con --apply (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        backup_path = None
        try:
            if handle.is_postgres:
                dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                            / "_pga_backups")
                try:
                    backup_path = auto_backup_postgres(
                        handle.engine, tag="yef_other_locations",
                        dest_dir=dest_dir,
                    )
                except BackupSkipped as e:
                    skip = QMessageBox.question(
                        self.iface.mainWindow(),
                        "Backup non disponibile",
                        f"{e}\n\nProcedere SENZA backup automatico "
                        "(sconsigliato)?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if skip != QMessageBox.Yes:
                        return
                    backup_path = None
            else:
                backup_path = auto_backup_sqlite(
                    handle.sqlite_path, tag="yef_other_locations",
                )
            added = add_other_locations_column(handle)
        except Exception as e:
            msg = (f"La migrazione è fallita:\n{e}\n\n"
                   f"Backup creato: {backup_path}") if backup_path \
                else f"La migrazione è fallita:\n{e}\n\nNessun backup creato."
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore migrazione",
                msg,
            )
            return

        QMessageBox.information(
            self.iface.mainWindow(),
            "Migrazione yE-F completata",
            f"Backup: {backup_path}\n\n"
            f"Colonna other_locations: {added} (1=aggiunta, 0=già presente)",
        )

    def _run_schedatore_fields_migration(self):
        """Add 5 missing TEXT columns to inventario_materiali_table
        (schedatore, date_scheda, punto_rinv, negativo_photo, diapositiva).

        Pattern mirrors ``_run_yef_migration``: resolve handle from the
        configured Connection, confirm, auto-backup, apply via the
        migration lib, summarize.
        """
        from qgis.PyQt.QtWidgets import QMessageBox
        from pathlib import Path
        try:
            from .modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from .modules.db.pyarchinit_conn_strings import Connection
            from .scripts.migrations._2026_05_inventario_materiali_schedatore_fields_lib import (
                SCHEDATORE_COLUMNS,
                add_schedatore_columns,
            )
            from .scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )
        except Exception:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from modules.db.pyarchinit_conn_strings import Connection
            from scripts.migrations._2026_05_inventario_materiali_schedatore_fields_lib import (
                SCHEDATORE_COLUMNS,
                add_schedatore_columns,
            )
            from scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )

        conn_str = Connection().conn_str()
        if not conn_str:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Connessione non configurata",
                "Connetti prima un DB pyarchinit dalle Settings (menu "
                "Database → Configurazione).",
            )
            return

        try:
            handle = _resolve_db_handle(conn_str)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore di connessione",
                f"Impossibile aprire la connessione al DB:\n{e}",
            )
            return

        backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                         + "/" + str(handle.engine.url.database or "")
                         if handle.is_postgres
                         else f"SQLite: {handle.sqlite_path}")
        cols_str = ", ".join(SCHEDATORE_COLUMNS)
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma migrazione schedatore",
            f"Backend: {backend_label}\n\n"
            f"Verranno aggiunte le 5 colonne TEXT a "
            f"inventario_materiali_table (idempotente: salta quelle "
            f"già presenti):\n  {cols_str}\n\n"
            "Procedere con --apply (con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        backup_path = None
        try:
            if handle.is_postgres:
                dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                            / "_pga_backups")
                try:
                    backup_path = auto_backup_postgres(
                        handle.engine, tag="schedatore_fields",
                        dest_dir=dest_dir,
                    )
                except BackupSkipped as e:
                    skip = QMessageBox.question(
                        self.iface.mainWindow(),
                        "Backup non disponibile",
                        f"{e}\n\nProcedere SENZA backup automatico "
                        "(sconsigliato)?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if skip != QMessageBox.Yes:
                        return
                    backup_path = None
            else:
                backup_path = auto_backup_sqlite(
                    handle.sqlite_path, tag="schedatore_fields",
                )
            result = add_schedatore_columns(handle)
        except Exception as e:
            msg = (f"La migrazione è fallita:\n{e}\n\n"
                   f"Backup creato: {backup_path}") if backup_path \
                else f"La migrazione è fallita:\n{e}\n\nNessun backup creato."
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore migrazione",
                msg,
            )
            return

        added = sum(result.values())
        details = "\n".join(f"  {c}: {'added' if v else 'already present'}"
                            for c, v in result.items())
        QMessageBox.information(
            self.iface.mainWindow(),
            "Migrazione schedatore completata",
            f"Backup: {backup_path}\n\n"
            f"Colonne aggiunte: {added}/{len(result)}\n\n{details}",
        )

    def _run_schema_repair_migration(self):
        """Full schema repair: create missing tables + add known
        missing columns. Use when the regular "Update DB" button has
        failed to migrate everything (typical for DBs imported from
        backups or created by very old plugin versions). Idempotent.
        """
        from qgis.PyQt.QtWidgets import QMessageBox
        from pathlib import Path
        try:
            from .modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from .modules.db.pyarchinit_conn_strings import Connection
            from .scripts.migrations._2026_05_schema_repair_lib import (
                _collect_canonical_tables,
                _existing_table_names,
                repair_schema,
            )
            from .scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )
        except Exception:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from modules.db.pyarchinit_conn_strings import Connection
            from scripts.migrations._2026_05_schema_repair_lib import (
                _collect_canonical_tables,
                _existing_table_names,
                repair_schema,
            )
            from scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
                auto_backup_sqlite,
            )

        conn_str = Connection().conn_str()
        if not conn_str:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Connessione non configurata",
                "Connetti prima un DB pyarchinit dalle Settings (menu "
                "Database → Configurazione).",
            )
            return

        try:
            handle = _resolve_db_handle(conn_str)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore di connessione",
                f"Impossibile aprire la connessione al DB:\n{e}",
            )
            return

        # Dry-run preview before asking for confirmation.
        canonical, failed_imports = _collect_canonical_tables()
        present = _existing_table_names(handle.engine)
        missing_tables = sorted(set(canonical) - present)
        backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                         + "/" + str(handle.engine.url.database or "")
                         if handle.is_postgres
                         else f"SQLite: {handle.sqlite_path}")
        missing_text = (
            "\n  ".join(missing_tables) if missing_tables
            else "(nessuna)"
        )
        warning_text = ""
        if failed_imports:
            warning_text = (
                f"\n\n⚠️  ATTENZIONE: {len(failed_imports)} moduli "
                f"structure non sono importabili — l'audit è parziale. "
                f"Vedi log QGIS per i dettagli."
            )
            for name, reason in failed_imports:
                QgsMessageLog.logMessage(
                    f"schema_repair: import failed for {name}: {reason}",
                    "PyArchInit", Qgis.MessageLevel.Warning,
                )
        confirm = QMessageBox.question(
            self.iface.mainWindow(),
            "Conferma schema repair",
            f"Backend: {backend_label}\n\n"
            f"Tabelle nel DB: {len(present)} / canoniche: {len(canonical)}\n\n"
            f"Tabelle mancanti da creare:\n  {missing_text}{warning_text}\n\n"
            "Saranno anche aggiunte le colonne mancanti note "
            "(inventario_materiali_table.schedatore e affini, "
            "us_table.other_locations).\n\n"
            "L'operazione è idempotente. Procedere con --apply "
            "(con backup automatico)?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        backup_path = None
        try:
            if handle.is_postgres:
                dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                            / "_pga_backups")
                try:
                    backup_path = auto_backup_postgres(
                        handle.engine, tag="schema_repair",
                        dest_dir=dest_dir,
                    )
                except BackupSkipped as e:
                    skip = QMessageBox.question(
                        self.iface.mainWindow(),
                        "Backup non disponibile",
                        f"{e}\n\nProcedere SENZA backup automatico "
                        "(sconsigliato)?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if skip != QMessageBox.Yes:
                        return
                    backup_path = None
            else:
                backup_path = auto_backup_sqlite(
                    handle.sqlite_path, tag="schema_repair",
                )
            report = repair_schema(handle)
        except Exception as e:
            msg = (f"Lo schema repair è fallito:\n{e}\n\n"
                   f"Backup creato: {backup_path}") if backup_path \
                else f"Lo schema repair è fallito:\n{e}\n\nNessun backup creato."
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore schema repair",
                msg,
            )
            return

        created = report["tables_created"]
        cols = report["columns_added"]
        details = []
        if created:
            details.append("Tabelle create:")
            details.extend(f"  + {t}" for t in created)
        else:
            details.append("Nessuna tabella da creare.")
        if cols:
            details.append("\nColonne aggiunte:")
            for table_name, col_map in cols.items():
                for c, added in col_map.items():
                    details.append(f"  + {table_name}.{c}")
        else:
            details.append("\nNessuna colonna da aggiungere.")
        QMessageBox.information(
            self.iface.mainWindow(),
            "Schema repair completato",
            f"Backup: {backup_path}\n\n" + "\n".join(details),
        )

    def _run_media_fk_migration(self):
        """media-fk-migration 5.7.9.3-alpha: drop the killer triggers on
        media_thumb_table, clean orphans, install FK ON DELETE CASCADE.

        PG-only. SQLite installs receive the cleaned template binary as
        part of this milestone (no runtime migration needed there).

        Pattern mirrors ``_run_uuid_backfill_migration``: resolve handle
        from the configured Connection, detect, count, confirm,
        auto-backup, apply, verify, summarize.
        """
        from qgis.PyQt.QtWidgets import QMessageBox
        from pathlib import Path
        try:
            from .modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from .modules.db.pyarchinit_conn_strings import Connection
            from .scripts.migrations._2026_05_media_fk_cascade_lib import (
                apply_migration,
                count_orphans,
                detect_killer_triggers,
                verify_post_migration,
            )
            from .scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
            )
        except Exception:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            from modules.db.pyarchinit_conn_strings import Connection
            from scripts.migrations._2026_05_media_fk_cascade_lib import (
                apply_migration,
                count_orphans,
                detect_killer_triggers,
                verify_post_migration,
            )
            from scripts.migrations._common import (
                BackupSkipped,
                auto_backup_postgres,
            )

        # Step 1: resolve the active DB connection (same path as
        # _run_uuid_backfill_migration).
        conn_str = Connection().conn_str()
        if not conn_str:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Connessione non configurata",
                "Connetti prima un DB pyarchinit dalle Settings (menu "
                "Database → Configurazione).",
            )
            return

        try:
            handle = _resolve_db_handle(conn_str)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore di connessione",
                f"Impossibile aprire la connessione al DB:\n{e}",
            )
            return

        # Step 2: PG-only gate. SQLite installs already received the
        # cleaned template — there is nothing to do at runtime.
        if not handle.is_postgres:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Fix trigger media",
                "Migrazione PG-only. I database SQLite ricevono "
                "il template già bonificato da questa release.",
            )
            return

        # Step 3: detect killer triggers; bail out cleanly on no-op.
        try:
            det = detect_killer_triggers(handle)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore rilevamento trigger",
                f"Impossibile interrogare information_schema:\n{e}",
            )
            return
        if not det["has_triggers"]:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Fix trigger media",
                "Database già pulito — nessun trigger killer rilevato.",
            )
            return

        # Step 4: count orphans + build preview dialog text.
        try:
            orph = count_orphans(handle)
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore conteggio orfani",
                f"Impossibile contare gli orfani:\n{e}",
            )
            return

        backend_label = ("PostgreSQL: " + str(handle.engine.url.host or "")
                         + "/" + str(handle.engine.url.database or ""))
        names_block = "\n  ".join(det["trigger_names"])
        msg = (
            f"Backend: {backend_label}\n\n"
            f"Rilevati {len(det['trigger_names'])} trigger killer da "
            f"rimuovere:\n  {names_block}\n\n"
            f"Orfani in media_thumb_table: {orph['thumb_orphans']}\n"
            f"Orfani in media_to_entity_table: {orph['mte_orphans']}\n\n"
            "Verrà eseguito un pg_dump di backup prima della migrazione.\n"
            "Procedere?"
        )
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "Fix trigger media",
            msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        # Step 5: auto-backup (same dest_dir convention as PG-A).
        backup_path = None
        dest_dir = (Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
                    / "_pga_backups")
        try:
            backup_path = auto_backup_postgres(
                handle.engine, tag="media_fk_migration",
                dest_dir=dest_dir,
            )
        except BackupSkipped as e:
            skip = QMessageBox.question(
                self.iface.mainWindow(),
                "Backup non disponibile",
                f"{e}\n\nProcedere SENZA backup automatico "
                "(sconsigliato)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if skip != QMessageBox.Yes:
                return
            backup_path = None
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Backup fallito",
                f"pg_dump è fallito:\n{e}\n\nMigrazione annullata.",
            )
            return

        # Step 6: apply (single transaction, rollback on error).
        try:
            res = apply_migration(handle, dry_run=False)
        except Exception as e:
            msg = (f"La migrazione è fallita (rollback automatico):\n{e}\n\n"
                   f"Backup creato: {backup_path}") if backup_path \
                else (f"La migrazione è fallita "
                      f"(rollback automatico):\n{e}\n\n"
                      "Nessun backup creato.")
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Errore migrazione",
                msg,
            )
            return

        # Step 7: verify post-migration is clean.
        try:
            v = verify_post_migration(handle)
        except Exception as e:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Verifica post-migrazione fallita",
                f"Migrazione applicata ma la verifica finale è fallita:"
                f"\n{e}",
            )
            return
        if not v["is_clean"]:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Verifica post-migrazione non pulita",
                f"Migrazione applicata ma stato finale non pulito: {v}",
            )
            return

        # Step 8: summary dialog.
        summary = (
            "Migrazione completata.\n\n"
            f"Trigger droppati: {res['triggers_dropped']}\n"
            f"Orfani thumb cancellati: {res['thumb_orphans_deleted']}\n"
            f"Orfani MTE cancellati: {res['mte_orphans_deleted']}\n"
            f"FK installate: {res['fks_installed']}\n\n"
            f"Backup: {backup_path or '(non eseguito)'}"
        )
        QMessageBox.information(
            self.iface.mainWindow(),
            "Fix trigger media",
            summary,
        )

    def _unload_stratigraph_sync(self):
        """Tear down the StratiGraph sync subsystem.

        Calls ``deleteLater()`` on the dock widget and nulls the
        attribute — without this, QGIS on plugin reload reports
        "removing duplicated widget(s) not cleaned up by the plugin
        during unload: StratiGraphSyncPan" because ``removeDockWidget``
        detaches from the layout but does NOT destroy the QObject.
        """
        if getattr(self, 'sync_orchestrator', None) is not None:
            self.sync_orchestrator.stop()
        if getattr(self, 'sync_panel', None) is not None:
            self.sync_panel.setVisible(False)
            self.iface.removeDockWidget(self.sync_panel)
            self.sync_panel.deleteLater()
            self.sync_panel = None
        if getattr(self, 'actionStratiGraphSync', None) is not None:
            self.iface.removeToolBarIcon(self.actionStratiGraphSync)
            self.actionStratiGraphSync = None

    def _unload_main_dockwidget(self):
        """Idempotently tear down the main ``self.dockWidget``.

        Called once per locale branch in ``unload()`` (4 branches:
        it/en/de/fr). The ``deleteLater()`` + ``None`` assignment is
        required to avoid the "removing duplicated widget(s) not cleaned
        up by the plugin during unload: PyarchinitPlugin" warning on
        plugin reload — ``iface.removeDockWidget`` only detaches from
        layout, the QObject survives until the Qt event loop disposes
        of it (which it never does without ``deleteLater``).
        """
        if getattr(self, 'dockWidget', None) is not None:
            self.dockWidget.setVisible(False)
            self.iface.removeDockWidget(self.dockWidget)
            self.dockWidget.deleteLater()
            self.dockWidget = None

    def _toggle_sync_panel(self, checked):
        if self.sync_panel is not None:
            self.sync_panel.setVisible(checked)
