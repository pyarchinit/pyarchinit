
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
    ------------------------------------------------------------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : pyarchinit at gmail.com
 ***************************************************************************/

/***************************************************************************/
*                                                                           *
*   This program is free software; you can redistribute it and/or modify   *
*   it under the terms of the GNU General Public License as published by    *
*   the Free Software Foundation; either version 2 of the License, or      *
*   (at your option) any later version.                                     *
*                                                                          *
/***************************************************************************/
"""
from __future__ import absolute_import

import os
import sqlite3
import datetime
import traceback


import sqlalchemy as sa


from sqlalchemy.event import listen
import platform
from builtins import range
from builtins import str

from ftplib import FTP

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import *
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import  pyqtSlot, pyqtSignal,QThread,QUrl,QTimer
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog,QLineEdit,QWidget,QCheckBox
from qgis.PyQt.QtSql import *
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsMessageLog, Qgis, QgsSettings, QgsProject, QgsDataSourceUri, QgsVectorLayer
from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.pyarchinit_utility import Utility

from modules.db.db_createdump import CreateDatabase, RestoreSchema, DropDatabase, SchemaDump
from modules.db.media_migration_mapper import MediaMigrationMapper
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility


MAIN_DIALOG_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'pyarchinitConfigDialog.ui'))


class PyArchInitLogger:
    """Simple file-based logger for debugging"""

    def __init__(self):
        # Use system temp directory for log file
        import tempfile
        temp_dir = tempfile.gettempdir()
        self.log_file = os.path.join(temp_dir, 'pyarchinit_debug.log')

    def log(self, message):
        """Write a message to the log file with timestamp"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
                f.flush()
        except Exception as e:
            # If we can't log, at least try to print
            print(f"Failed to log: {e}")

    def log_exception(self, function_name, exception):
        """Log an exception with traceback"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] EXCEPTION in {function_name}: {str(exception)}\n")
                f.write(f"[{timestamp}] Traceback:\n")
                tb = traceback.format_exc()
                for line in tb.split('\n'):
                    if line:
                        f.write(f"[{timestamp}]   {line}\n")
                f.flush()
        except Exception as e:
            print(f"Failed to log exception: {e}")

    def clear_log(self):
        """Clear the log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Log cleared at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.flush()
        except Exception as e:
            print(f"Failed to clear log: {e}")


class pyArchInitDialog_Config(QDialog, MAIN_DIALOG_CLASS):
    progressBarUpdated = pyqtSignal(int,int)
    L=QgsSettings().value("locale/userLocale")[0:2]
    UTILITY=Utility()
    DB_MANAGER=""

    HOME = os.environ['PYARCHINIT_HOME']
    DBFOLDER = '{}{}{}'.format(HOME, os.sep, "pyarchinit_DB_folder")
    PARAMS_DICT = {'SERVER': '',
                   'HOST': '',
                   'DATABASE': '',
                   'PASSWORD': '',
                   'PORT': '',
                   'USER': '',
                   'THUMB_PATH': '',
                   'THUMB_RESIZE': '',
                   'EXPERIMENTAL': '',
                   'SITE_SET': ''}

    # Flag to prevent recursive database creation
    _is_creating_database = False

    def __init__(self, parent=None, db=None):

        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.

        self.setupUi(self)

        # Initialize flag to prevent database creation loop
        self.creating_database = False

        # Initialize logger
        self.logger = PyArchInitLogger()
        self.logger.clear_log()
        self.logger.log("=== PyArchInit Config Dialog Initialized ===")

        s = QgsSettings()
        self.mDockWidget.setHidden(True)

        self.load_dict()
        self.charge_data()
        self.summary()
        self.db_active()
        self.lineEdit_DBname.textChanged.connect(self.db_uncheck)
        self.lineEdit_DBname.textChanged.connect(self.db_name_change)
        # Button enablement is now handled by db_active()
        self.comboBox_sito.setCurrentText(self.sito_active())
        self.comboBox_sito.currentIndexChanged.connect(self.summary)
        self.comboBox_Database.currentIndexChanged.connect(self.db_active)
        self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
        
        # if self.comboBox_server_rd.currentText=='sqlite':
            # self.set_db_import_from_parameter()
        
        self.comboBox_server_rd.currentTextChanged.connect(self.set_db_import_from_parameter)
        self.comboBox_server_wt.currentTextChanged.connect(self.set_db_import_to_parameter)

        self.pushButton_save.clicked.connect(self.summary)
        self.pushButton_save.clicked.connect(self.on_pushButton_save_pressed)

        self.pushButtonGraphviz.clicked.connect(self.setPathGraphviz)
        self.pbnSaveEnvironPath.clicked.connect(self.setEnvironPath)
        self.toolButton_logo.clicked.connect(self.setPathlogo)
        self.toolButton_thumbpath.clicked.connect(self.setPathThumb)
        self.toolButton_resizepath.clicked.connect(self.setPathResize)

        # Add tooltips for remote storage support
        remote_tooltip = (
            "Path can be local or remote:\n"
            "• Local: /path/to/folder/ or C:\\path\\to\\folder\\\n"
            "• Google Drive: gdrive://folder/path/\n"
            "• Dropbox: dropbox://folder/path/\n"
            "• S3: s3://bucket/path/\n"
            "• WebDAV: webdav://server/path/\n"
            "• HTTP: https://server/path/"
        )
        self.lineEdit_Thumb_path.setToolTip(remote_tooltip)
        self.lineEdit_Thumb_resize.setToolTip(remote_tooltip)

        # Add remote storage config button programmatically
        try:
            from qgis.PyQt.QtWidgets import QPushButton
            from qgis.PyQt.QtGui import QIcon
            self.pushButton_remote_storage = QPushButton("Remote Storage Config")
            self.pushButton_remote_storage.setToolTip("Configure credentials for remote storage backends")
            # Add to the Path Settings groupbox layout
            if hasattr(self, 'groupBox_4') and self.groupBox_4.layout():
                self.groupBox_4.layout().addWidget(self.pushButton_remote_storage, 9, 0, 1, 2)
            self.pushButton_remote_storage.clicked.connect(self.openRemoteStorageConfig)
        except Exception as e:
            pass  # Silently fail if button can't be added

        self.toolButton_set_dbsqlite1.clicked.connect(self.setPathDBsqlite1)
        self.toolButton_set_dbsqlite2.clicked.connect(self.setPathDBsqlite2)
        self.pbnOpenthumbDirectory.clicked.connect(self.openthumbDir)
        self.pbnOpenresizeDirectory.clicked.connect(self.openresizeDir)
        
        self.toolButton_db.clicked.connect(self.setPathDB)
        self.pushButtonPostgres.clicked.connect(self.setPathPostgres)
        self.pbnSaveEnvironPathPostgres.clicked.connect(self.setEnvironPathPostgres)
        self.comboBox_server_rd.currentTextChanged.connect(self.geometry_conn)
        self.pushButton_compare.clicked.connect(self.compare)
        self.pushButton_import.clicked.connect(self.on_pushButton_import_pressed)
        self.graphviz_bin = s.value('pyArchInit/graphvizBinPath', None, type=str)
        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)

        if Pyarchinit_OS_Utility.checkgraphvizinstallation():
            self.pushButtonGraphviz.setEnabled(False)
            self.pbnSaveEnvironPath.setEnabled(False)
            self.lineEditGraphviz.setEnabled(False)

        self.postgres_bin = s.value('pyArchInit/postgresBinPath', None, type=str)
        if self.postgres_bin:
            self.lineEditPostgres.setText(self.postgres_bin)

        if Pyarchinit_OS_Utility.checkpostgresinstallation():
            self.pushButtonPostgres.setEnabled(False)
            self.pbnSaveEnvironPathPostgres.setEnabled(False)
            self.lineEditPostgres.setEnabled(False)




        self.selectorCrsWidget.setCrs(QgsProject.instance().crs())
        self.selectorCrsWidget_sl.setCrs(QgsProject.instance().crs())
        if self.checkBox_abort.isChecked():
            self.checkBox_abort.setChecked(True)
            self.checkBox_abort.stateChanged.connect(self.check)
            self.checkBox_abort.stateChanged.connect(self.message)
        elif self.checkBox_ignore.isChecked():
            self.checkBox_ignore.setChecked(True)
            self.checkBox_ignore.stateChanged.connect(self.check)
            self.checkBox_ignore.stateChanged.connect(self.message)
        elif self.checkBox_replace.isChecked():
            self.checkBox_replace.setChecked(True)
            self.checkBox_replace.stateChanged.connect(self.check)
            self.checkBox_replace.stateChanged.connect(self.message)    
        
        self.check()
        #self.upd_individui_table()
        # Always enable the DBname field for both SQLite and PostgreSQL
        # SQLite needs it for the database file name
        # PostgreSQL needs it for the database name
        self.setComboBoxEnable(["self.lineEdit_DBname"], "True")
        self.comboBox_Database.currentIndexChanged.connect(self.customize)
        #self.test()
        self.test2()
        #self.test3()
        self.comboBox_mapper_read.currentIndexChanged.connect(self.check_table)
        self.comboBox_geometry_read.currentIndexChanged.connect(self.check_geometry_table)
        self.mFeature_field_rd.currentTextChanged.connect(self.value_check)
        self.mFeature_field_rd.currentTextChanged.connect(self.value_check_geometry)
        
        self.comboBox_server_rd.currentTextChanged.connect(self.convert_db)
        self.comboBox_server_wt.currentTextChanged.connect(self.convert_db)
        self.pushButton_convert_db_sl.setHidden(True)
        self.pushButton_convert_db_pg.setHidden(True)

        # Admin features will be setup after database connection
        # self.setup_admin_features()

    def setup_admin_features(self):
        """Setup admin-only features like user management"""
        try:
            # First check if admin widget already exists and remove it
            if hasattr(self, 'admin_widget') and self.admin_widget:
                self.admin_widget.deleteLater()
                self.admin_widget = None

            # Create admin panel
            from PyQt5.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QLabel, QGridLayout

            # Check if we're connected and if user is admin
            if hasattr(self, 'DB_MANAGER') and self.DB_MANAGER:
                # Get username from UI field (database connection username)
                username_ui = self.lineEdit_User.text() if hasattr(self, 'lineEdit_User') else ''
                username_ui_lower = username_ui.lower()

                # Default to admin for backward compatibility
                is_admin = True

                # Check admin status
                try:
                    if self.comboBox_Database.currentText() == 'postgres':
                        # First: Check if user is 'postgres' or starts with 'postgres.' (superuser)
                        if username_ui_lower == 'postgres' or username_ui_lower.startswith('postgres.'):
                            is_admin = True
                            print(f"Admin check - User is postgres superuser: {username_ui}")
                        else:
                            # Check if pyarchinit_users table exists
                            check_table = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'pyarchinit_users')"
                            table_exists = self.DB_MANAGER.execute_sql(check_table)

                            if table_exists and table_exists[0][0]:
                                # Table exists - check user's role
                                # Try with the exact username first (case-sensitive)
                                query = f"SELECT role FROM pyarchinit_users WHERE username = '{username_ui}' AND is_active = TRUE"
                                result = self.DB_MANAGER.execute_sql(query)

                                if not result:
                                    # Try case-insensitive
                                    query = f"SELECT role FROM pyarchinit_users WHERE LOWER(username) = LOWER('{username_ui}') AND is_active = TRUE"
                                    result = self.DB_MANAGER.execute_sql(query)

                                if result and len(result) > 0:
                                    role = result[0][0]
                                    is_admin = (role == 'admin')
                                    print(f"Admin check - User '{username_ui}' has role: {role}, is_admin: {is_admin}")
                                else:
                                    # User not found in pyarchinit_users - default to admin for initial setup
                                    is_admin = True
                                    print(f"Admin check - User '{username_ui}' not in pyarchinit_users, defaulting to admin")
                            else:
                                # Table doesn't exist - allow admin for initial setup
                                is_admin = True
                                print("Admin check - pyarchinit_users table doesn't exist, defaulting to admin")
                    else:
                        # SQLite - default to admin for local databases
                        is_admin = True
                        print("Admin check - SQLite database, defaulting to admin")
                except Exception as e:
                    # If any check fails, default to admin for backward compatibility
                    is_admin = True
                    print(f"Admin check - Exception occurred ({e}), defaulting to admin")

                # Debug
                print(f"Admin check FINAL - Username: {username_ui}, Is admin: {is_admin}")

                if is_admin:
                    # Add admin section to the config dialog
                    admin_group = QGroupBox("🛡️ Funzioni Amministratore")
                    admin_layout = QVBoxLayout()

                    # User management button
                    self.user_mgmt_btn = QPushButton("👤 Gestione Utenti e Permessi")

                    # Database update buttons
                    self.update_db_btn = QPushButton("🔄 Aggiorna Schema Database")
                    self.update_db_btn.setToolTip("Applica tutte le modifiche necessarie al database (concorrenza, quota, utenti)")

                    self.apply_concurrency_btn = QPushButton("🔐 Applica Sistema Concorrenza")
                    self.apply_concurrency_btn.setToolTip("Aggiunge il sistema di concorrenza a tutte le tabelle")

                    # Style for database update buttons
                    self.update_db_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            font-weight: bold;
                            padding: 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)

                    self.apply_concurrency_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #9C27B0;
                            color: white;
                            font-weight: bold;
                            padding: 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #7B1FA2;
                        }
                    """)

                    self.user_mgmt_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #FF5722;
                            color: white;
                            font-weight: bold;
                            padding: 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #E64A19;
                        }
                    """)
                    self.user_mgmt_btn.clicked.connect(self.open_user_management)

                    # Monitor button
                    self.monitor_btn = QPushButton("📊 Monitor Attività Real-Time")
                    self.monitor_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            font-weight: bold;
                            padding: 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #1976D2;
                        }
                    """)
                    self.monitor_btn.clicked.connect(self.open_activity_monitor)

                    # Connect new buttons
                    self.update_db_btn.clicked.connect(self.update_database_schema)
                    self.apply_concurrency_btn.clicked.connect(self.apply_concurrency_system)

                    admin_layout.addWidget(self.user_mgmt_btn)
                    admin_layout.addWidget(self.monitor_btn)
                    admin_layout.addWidget(self.update_db_btn)
                    admin_layout.addWidget(self.apply_concurrency_btn)

                    # Info label
                    info_label = QLabel("⚠️ Solo gli amministratori possono accedere a queste funzioni")
                    info_label.setStyleSheet("color: #666; font-style: italic;")
                    admin_layout.addWidget(info_label)

                    admin_group.setLayout(admin_layout)

                    # Store reference to admin widget
                    self.admin_widget = admin_group

                    # Add to main layout - insert at the TOP
                    if hasattr(self, 'tabWidget'):
                        # Get the first tab (Database tab)
                        db_tab = self.tabWidget.widget(0)
                        if db_tab:
                            # Find or create a layout for the tab
                            layout = db_tab.layout()
                            if layout:
                                # Check layout type and add widget appropriately
                                if hasattr(layout, 'insertWidget'):
                                    # QVBoxLayout or QHBoxLayout
                                    layout.insertWidget(0, admin_group)
                                    print("Admin widget added to TOP of Database tab")
                                elif hasattr(layout, 'addWidget'):
                                    if isinstance(layout, QGridLayout):
                                        # For QGridLayout, add at row 0, spanning all columns
                                        # First shift all existing widgets down
                                        for i in range(layout.rowCount() - 1, -1, -1):
                                            for j in range(layout.columnCount()):
                                                item = layout.itemAtPosition(i, j)
                                                if item:
                                                    widget = item.widget()
                                                    if widget and widget != admin_group:
                                                        layout.removeWidget(widget)
                                                        layout.addWidget(widget, i + 1, j)
                                        # Now add admin widget at top
                                        layout.addWidget(admin_group, 0, 0, 1, layout.columnCount())
                                        print("Admin widget added to TOP of Database tab (Grid)")
                                    else:
                                        # Generic add for other layout types
                                        layout.addWidget(admin_group)
                                        print("Admin widget added to Database tab")
                            else:
                                # No layout, create one
                                from PyQt5.QtWidgets import QVBoxLayout
                                new_layout = QVBoxLayout()
                                new_layout.addWidget(admin_group)
                                # Move existing widgets to new layout
                                for child in db_tab.children():
                                    if hasattr(child, 'isWidgetType') and child.isWidgetType():
                                        new_layout.addWidget(child)
                                db_tab.setLayout(new_layout)
                                print("Created new layout and added admin widget")
                    elif hasattr(self, 'gridLayout'):
                        # Fallback: Add at the top of the gridLayout
                        self.gridLayout.addWidget(admin_group, 0, 0, 1, 2)
                        print("Admin widget added to gridLayout")
                    else:
                        print("Could not find suitable layout for admin widget")

        except Exception as e:
            print(f"Error setting up admin features: {e}")

    def check_if_updates_needed(self):
        """Check if database updates are needed"""
        try:
            # Check for concurrency columns
            query = """
                SELECT COUNT(DISTINCT table_name) as tables_with_concurrency
                FROM information_schema.columns
                WHERE column_name IN ('version_number', 'editing_by', 'editing_since', 'audit_trail')
                AND table_schema = 'public'
                AND table_name IN ('us_table', 'tma_materiali_archeologici', 'inventario_materiali_table',
                                   'site_table', 'periodizzazione_table', 'struttura_table', 'tomba_table',
                                   'individui_table', 'campioni_table', 'documentazione_table',
                                   'detsesso_table', 'deteta_table', 'archeozoology_table', 'pottery_table')
            """
            result = self.DB_MANAGER.execute_sql(query)
            tables_with_concurrency = result[0][0] if result else 0

            # Check for quota field
            query2 = """
                SELECT COUNT(*) FROM information_schema.columns
                WHERE table_name = 'inventario_materiali_table'
                AND column_name = 'quota_usm'
            """
            result2 = self.DB_MANAGER.execute_sql(query2)
            has_quota = result2[0][0] if result2 else 0

            # Check for user tables
            query3 = """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name IN ('pyarchinit_users', 'pyarchinit_permissions', 'pyarchinit_activity_log')
                AND table_schema = 'public'
            """
            result3 = self.DB_MANAGER.execute_sql(query3)
            has_user_tables = result3[0][0] if result3 else 0

            # If all updates are already applied
            if tables_with_concurrency >= 14 and has_quota > 0 and has_user_tables >= 3:
                return False  # No updates needed
            return True  # Updates needed

        except Exception as e:
            print(f"Error checking update status: {e}")
            return True  # Assume updates needed if check fails

    def update_database_schema(self):
        """Apply all database schema updates"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            # First check if updates are needed
            if not self.check_if_updates_needed():
                QMessageBox.information(self, 'Database Aggiornato',
                    '✅ Il database è già completamente aggiornato!\n\n'
                    'Tutti i componenti sono già installati:\n'
                    '• Sistema di concorrenza ✓\n'
                    '• Campo quota corretto ✓\n'
                    '• Tabelle gestione utenti ✓\n'
                    '• Protezione duplicati TMA ✓')
                return

            reply = QMessageBox.question(self, 'Conferma',
                'Vuoi applicare tutti gli aggiornamenti al database?\n\n'
                'Questo includerà:\n'
                '• Correzione campo quota (da min/max a singolo)\n'
                '• Sistema di concorrenza su tutte le tabelle\n'
                '• Tabelle gestione utenti\n'
                '• Protezione duplicati TMA\n'
                '• Indici di performance\n\n'
                'Continuare?',
                QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Get the SQL file path
                import os
                sql_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'sql',
                    'update_production_db_safe.sql'
                )

                if os.path.exists(sql_path):
                    # Read SQL file
                    with open(sql_path, 'r') as f:
                        sql_content = f.read()

                    # Execute SQL
                    try:
                        # For database update with functions, use raw psycopg2 connection
                        import psycopg2
                        from urllib.parse import urlparse

                        # Parse connection URL
                        db_url = str(self.DB_MANAGER.engine.url)
                        parsed = urlparse(db_url.replace('postgresql://', 'http://'))

                        # Create direct psycopg2 connection
                        conn = psycopg2.connect(
                            host=parsed.hostname or 'localhost',
                            port=parsed.port or 5432,
                            database=parsed.path.lstrip('/'),
                            user=parsed.username,
                            password=parsed.password
                        )

                        # Execute the entire SQL file as one transaction
                        with conn.cursor() as cursor:
                            cursor.execute(sql_content)
                            conn.commit()

                        conn.close()
                        success_count = 1
                        error_count = 0
                        errors = []

                        if error_count == 0:
                            QMessageBox.information(self, 'Successo',
                                f'Database aggiornato con successo!\n'
                                f'{success_count} statement eseguiti.')
                        else:
                            QMessageBox.warning(self, 'Aggiornamento Parziale',
                                f'Aggiornamento completato con alcuni errori.\n'
                                f'Successi: {success_count}\n'
                                f'Errori: {error_count}\n\n'
                                f'Primi errori: {errors[:3]}')

                    except Exception as e:
                        QMessageBox.critical(self, 'Errore',
                            f'Errore durante l\'aggiornamento del database:\n{str(e)}')
                else:
                    QMessageBox.warning(self, 'File non trovato',
                        'Il file SQL di aggiornamento non è stato trovato.')

        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore: {str(e)}')

    def check_if_concurrency_installed(self):
        """Check if concurrency system is already installed"""
        try:
            query = """
                SELECT COUNT(DISTINCT table_name) as tables_with_concurrency
                FROM information_schema.columns
                WHERE column_name IN ('version_number', 'editing_by', 'editing_since', 'audit_trail')
                AND table_schema = 'public'
                AND table_name IN ('us_table', 'tma_materiali_archeologici', 'inventario_materiali_table',
                                   'site_table', 'periodizzazione_table', 'struttura_table', 'tomba_table',
                                   'individui_table', 'campioni_table', 'documentazione_table',
                                   'detsesso_table', 'deteta_table', 'archeozoology_table', 'pottery_table')
            """
            result = self.DB_MANAGER.execute_sql(query)
            tables_with_concurrency = result[0][0] if result else 0
            return tables_with_concurrency >= 14

        except Exception as e:
            print(f"Error checking concurrency status: {e}")
            return False

    def apply_concurrency_system(self):
        """Apply concurrency system to all tables"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            # First check if concurrency is already installed
            if self.check_if_concurrency_installed():
                QMessageBox.information(self, 'Sistema Già Installato',
                    '✅ Il sistema di concorrenza è già installato!\n\n'
                    'Tutte le tabelle hanno già:\n'
                    '• Campi version_number ✓\n'
                    '• Campi editing_by e editing_since ✓\n'
                    '• Sistema di audit trail ✓\n'
                    '• Viste di monitoraggio attive ✓\n\n'
                    'Non sono necessarie ulteriori modifiche.')
                return

            reply = QMessageBox.question(self, 'Conferma',
                'Vuoi applicare il sistema di concorrenza a tutte le tabelle?\n\n'
                'Questo aggiungerà:\n'
                '• Campi version_number, editing_by, editing_since\n'
                '• Sistema di audit trail\n'
                '• Trigger per gestione conflitti\n\n'
                'Continuare?',
                QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Get the SQL file path
                import os
                sql_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    'sql',
                    'add_concurrency_fixed.sql'
                )

                if os.path.exists(sql_path):
                    # Read SQL file
                    with open(sql_path, 'r') as f:
                        sql_content = f.read()

                    # Execute SQL
                    try:
                        # Use raw psycopg2 connection for complex SQL with functions
                        import psycopg2
                        from urllib.parse import urlparse

                        # Parse connection URL
                        db_url = str(self.DB_MANAGER.engine.url)
                        parsed = urlparse(db_url.replace('postgresql://', 'http://'))

                        # Create direct psycopg2 connection
                        conn = psycopg2.connect(
                            host=parsed.hostname or 'localhost',
                            port=parsed.port or 5432,
                            database=parsed.path.lstrip('/'),
                            user=parsed.username,
                            password=parsed.password
                        )

                        # Execute the entire SQL file as one transaction
                        with conn.cursor() as cursor:
                            cursor.execute(sql_content)
                            conn.commit()

                        conn.close()

                        QMessageBox.information(self, 'Successo',
                            'Sistema di concorrenza applicato con successo!\n\n'
                            'Funzionalità aggiunte:\n'
                            '• Versioning su tutte le tabelle\n'
                            '• Soft locks per editing\n'
                            '• Audit trail completo\n'
                            '• Tracking utente reale')

                    except Exception as e:
                        QMessageBox.critical(self, 'Errore',
                            f'Errore durante l\'applicazione del sistema di concorrenza:\n{str(e)}')
                else:
                    QMessageBox.warning(self, 'File non trovato',
                        'Il file SQL di concorrenza non è stato trovato.')

        except Exception as e:
            QMessageBox.critical(self, 'Errore', f'Errore: {str(e)}')
            import traceback
            traceback.print_exc()

    def open_user_management(self):
        """Open user management dialog"""
        try:
            from .user_management_dialog import UserManagementDialog

            if not hasattr(self, 'DB_MANAGER') or not self.DB_MANAGER:
                QMessageBox.warning(self, "Errore", "Connetti prima al database!")
                return

            dialog = UserManagementDialog(self.DB_MANAGER, self)
            dialog.user_changed.connect(self.on_users_changed)
            dialog.exec_()

        except ImportError:
            QMessageBox.warning(self, "Errore", "Modulo gestione utenti non trovato!")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore apertura gestione utenti: {e}")

    def open_activity_monitor(self):
        """Open real-time activity monitor"""
        try:
            # Open user management dialog on monitor tab
            from .user_management_dialog import UserManagementDialog

            if not hasattr(self, 'DB_MANAGER') or not self.DB_MANAGER:
                QMessageBox.warning(self, "Errore", "Connetti prima al database!")
                return

            dialog = UserManagementDialog(self.DB_MANAGER, self)
            dialog.tabs.setCurrentIndex(2)  # Switch to Monitor tab
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore apertura monitor: {e}")
            import traceback
            traceback.print_exc()

    def on_users_changed(self):
        """Called when users/permissions are changed"""
        QMessageBox.information(self, "Info",
            "Le modifiche agli utenti saranno attive dal prossimo login")

    def convert_db(self):
        if self.comboBox_server_rd.currentText()=='postgres':
            self.pushButton_convert_db_pg.setHidden(True)
            self.pushButton_convert_db_sl.show()
        if self.comboBox_server_rd.currentText()=='sqlite':
            self.pushButton_convert_db_sl.setHidden(True)
            self.pushButton_convert_db_pg.show()
    
        if self.comboBox_server_rd.currentText()=='postgres' and self.comboBox_server_wt.currentText()=='postgres' or self.comboBox_server_rd.currentText()=='':
            self.pushButton_convert_db_sl.setHidden(True)
            self.pushButton_convert_db_pg.setHidden(True)
        if self.comboBox_server_rd.currentText()=='sqlite' and self.comboBox_server_wt.currentText()=='sqlite' or self.comboBox_server_rd.currentText()=='':
            self.pushButton_convert_db_sl.setHidden(True)
            self.pushButton_convert_db_pg.setHidden(True)


    def on_pushButton_convert_db_sl_pressed(self):
        ok=QMessageBox.warning(self, "Attenzione", 'Vuoi sovrascrivere il db.\n clicca ok oppure Annulla per aggiornare', QMessageBox.Ok | QMessageBox.Cancel)
        
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        # if test_conn == 0:
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
        path=sqlite_DB_path+os.sep+self.lineEdit_database_wt.text()
        if ok==QMessageBox.Ok:
            try:
                process= os.system('start cmd /k ogr2ogr --config PG_LIST_ALL_TABLES YES --config PG_SKIP_VIEWS YES -f SQLite '+path+' -progress PG:"dbname='+self.lineEdit_database_rd.text()+' active_schema=public schemas=public host='+self.lineEdit_host_rd.text()+' port='+ self.lineEdit_port_rd.text()+' user='+self.lineEdit_username_rd.text()+' password='+self.lineEdit_pass_rd.text()+'" -lco LAUNDER=yes -dsco SPATIALITE=yes -lco SPATIAL_INDEX=yes -gt 65536 -skipfailures -update -overwrite')
                


            except KeyError as e:
                QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)
        else:
            
            
            process= os.system('start cmd /k ogr2ogr --config PG_LIST_ALL_TABLES YES --config PG_SKIP_VIEWS YES -f SQLite '+path+' -progress PG:"dbname='+self.lineEdit_database_rd.text()+' active_schema=public schemas=public host='+self.lineEdit_host_rd.text()+' port='+ self.lineEdit_port_rd.text()+' user='+self.lineEdit_username_rd.text()+' password='+self.lineEdit_pass_rd.text()+'" -lco LAUNDER=yes -dsco SPATIALITE=yes -lco SPATIAL_INDEX=yes -gt 65536 -skipfailures -update -append')
    
    
    
    def on_pushButton_convert_db_pg_pressed(self):
        ok=QMessageBox.warning(self, "Attenzione", 'Vuoi sovrascrivere il db?\n clicca ok oppure cancell per aggiornare', QMessageBox.Ok | QMessageBox.Cancel)
        
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        # if test_conn == 0:
        sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
        #path=sqlite_DB_path+os.sep+self.lineEdit_database_wt.text()
        path=sqlite_DB_path+os.sep+self.lineEdit_database_rd.text()
        if ok==QMessageBox.Ok:
            try:
                process= os.system('start cmd /k ogr2ogr  --config SQLITE_LIST_ALL_TABLES YES -progress  -f PostgreSQL  PG:"dbname='+self.lineEdit_database_wt.text()+' active_schema=public schemas=public host='+self.lineEdit_host_wt.text()+' port='+self.lineEdit_port_wt.text()+' user='+self.lineEdit_username_wt.text()+' password='+self.lineEdit_pass_wt.text()+'" -lco GEOMETRY_NAME="the_geom" -lco SPATIAL_INDEX=YES '+ path +' -skipfailures -update -overwrite')
                


            except KeyError as e:
                QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)
        else:
            
            process= os.system('start cmd /k ogr2ogr  --config SQLITE_LIST_ALL_TABLES YES -progress  -f PostgreSQL  PG:"dbname='+self.lineEdit_database_wt.text()+' active_schema=public schemas=public host='+self.lineEdit_host_wt.text()+' port='+self.lineEdit_port_wt.text()+' user='+self.lineEdit_username_wt.text()+' password='+self.lineEdit_pass_wt.text()+'" -lco GEOMETRY_NAME="the_geom" -lco SPATIAL_INDEX=YES '+ path +' -skipfailures -update -append')
    
    def sito_active(self):
        conn = Connection()
        conn_str = conn.conn_str()
        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']
        return sito_set_str
    def check_table(self):
        self.comboBox_mapper_read.update()
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            uri = QgsDataSourceUri()
            uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            schema = ''
            if self.comboBox_mapper_read.currentIndex()==1:
                try:
                    table = 'site_table'
                    geom_column = ''
                    uri.setDataSource(schema, table,geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                    pr = vlayer.dataProvider()
                    fi= pr.fields().names()[1:-1]
                    
                    self.mFeature_field_rd.clear()
                    self.mFeature_field_rd.addItems(fi)
                except:
                    pass
            elif self.comboBox_mapper_read.currentIndex()==2:
                
                table = 'us_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_mapper_read.currentIndex()==3:
                
                table = 'periodizzazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_mapper_read.currentIndex()==4:
                
                table = 'inventario_materiali_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)

            elif self.comboBox_mapper_read.currentIndex() == 5:

                table = 'pottery_table'
                geom_column = ''
                uri.setDataSource(schema, table, geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi = pr.fields().names()[1:-1]

                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)

            elif self.comboBox_mapper_read.currentIndex()==6:
                
                table = 'struttura_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)

            elif self.comboBox_mapper_read.currentIndex()==7:
                
                table = 'tomba_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==8:
                
                table = 'pyarchinit_thesaurus_sigle'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)

            elif self.comboBox_mapper_read.currentIndex()==9:
                
                table = 'individui_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==10:
                
                table = 'detsesso_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==11:
                
                table = 'deteta_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==12:
                
                table = 'archeozoology_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==13:
                
                table = 'campioni_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==14:
                
                table = 'documentazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==15:
                
                table = 'media_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==16:
                
                table = 'media_thumb_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==17:
                
                table = 'media_to_entity_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_mapper_read.currentIndex()==18:
                
                table = 'ut_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            try:
                self.mFeature_value_rd.clearEditText()
                self.mFeature_value_rd.update()
                self.value_check(table)
            except:
                pass
        else:
            uri = QgsDataSourceUri()
            uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
            schema = 'public'
            if self.comboBox_mapper_read.currentIndex()==1:
                try:
                    table = 'site_table'
                    geom_column = ''
                    uri.setDataSource(schema, table,geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                    pr = vlayer.dataProvider()
                    fi= pr.fields().names()[1:-1]
                    
                    self.mFeature_field_rd.clear()
                    self.mFeature_field_rd.addItems(fi)
                except:
                    pass
            elif self.comboBox_mapper_read.currentIndex()==2:
                
                table = 'us_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_mapper_read.currentIndex()==3:
                
                table = 'periodizzazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_mapper_read.currentIndex()==4:
                
                table = 'inventario_materiali_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)


            elif self.comboBox_mapper_read.currentIndex() == 5:

                table = 'pottery_table'
                geom_column = ''
                uri.setDataSource(schema, table, geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi = pr.fields().names()[1:-1]

                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)


            elif self.comboBox_mapper_read.currentIndex()==6:
                
                table = 'struttura_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==7:
                
                table = 'tomba_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==8:
                
                table = 'pyarchinit_thesaurus_sigle'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==9:
                
                table = 'individui_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==10:
                
                table = 'detsesso_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==11:
                
                table = 'deteta_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==12:
                
                table = 'archeozoology_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==13:
                
                table = 'campioni_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==14:
                
                table = 'documentazione_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==15:
                
                table = 'media_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==16:
                
                table = 'media_thumb_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_mapper_read.currentIndex()==17:
                
                table = 'media_to_entity_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_mapper_read.currentIndex()==18:
                
                table = 'ut_table'
                geom_column = ''
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
        try:
            self.mFeature_value_rd.clearEditText()
            self.mFeature_value_rd.update()
            self.value_check(table)
        except:
            pass
    def value_check(self,table):
        try:
            self.mFeature_value_rd.clear()
            self.mFeature_value_rd.update()
            if self.mFeature_field_rd.currentTextChanged:
                sito_vl2 = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by(table, self.mFeature_field_rd.currentText(), self.comboBox_mapper_read.currentText()))

            try:
                sito_vl2.remove('')
            except:
                pass
            self.mFeature_value_rd.clear()
            sito_vl2.sort()
            
            self.mFeature_value_rd.addItems(sito_vl2)
            self.mFeature_value_rd.update()
        except :
            pass#QMessageBox.warning(self, "Attenzione", str(e), QMessageBox.Ok)        
    def check_geometry_table(self):
        self.comboBox_geometry_read.update()
        self.comboBox_Database.update()
        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        
        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        self.DB_MANAGER.connection()
        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            uri = QgsDataSourceUri()
            uri.setDatabase(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            schema = ''
            
            ##############################################################################################
            if self.comboBox_geometry_read.currentIndex()==1:
                
                    table = 'pyarchinit_siti_polygonal'
                    geom_column = 'the_geom'
                    uri.setDataSource(schema, table,geom_column)
                    vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                    pr = vlayer.dataProvider()
                    fi= pr.fields().names()[1:-1]
                    
                    self.mFeature_field_rd.clear()
                    self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_geometry_read.currentIndex()==2:
                
                table = 'pyarchinit_siti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_geometry_read.currentIndex()==3:
                
                table = 'pyunitastratigrafiche'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_geometry_read.currentIndex()==4:
                
                table = 'pyunitastratigrafiche_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi) 
            elif self.comboBox_geometry_read.currentIndex()==5:
                
                table = 'pyarchinit_quote'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==6:
                
                table = 'pyarchinit_quote_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==7:
                
                table = 'pyarchinit_us_negative_doc'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==8:
                
                table = 'pyarchinit_strutture_ipotesi'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==9:
                
                table = 'pyarchinit_reperti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==10:
                
                table = 'pyarchinit_individui'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==11:
                
                table = 'pyarchinit_campionature'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==12:
                
                table = 'pyarchinit_tafonomia'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==13:
                
                table = 'pyarchinit_sezioni'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==14:
                
                table = 'pyarchinit_documentazione'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==15:
                
                table = 'pyarchinit_punti_rif'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==16:
                
                table = 'pyarchinit_ripartizioni_spaziali'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'spatialite')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            
            
            try:
                self.mFeature_value_rd.clearEditText()
                self.mFeature_value_rd.update()
                self.value_check_geometry(table)
            except:
                pass
    
        else:
            uri = QgsDataSourceUri()
            uri.setConnection(conn_host["host"], conn_port["port"], conn_sqlite["db_name"], conn_user['user'], conn_password['password'])
            schema='public'
            ##############################################################################################
            if self.comboBox_geometry_read.currentIndex()==1:
                
                table = 'pyarchinit_siti_polygonal'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            elif self.comboBox_geometry_read.currentIndex()==2:
                
                table = 'pyarchinit_siti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)    
            
            elif self.comboBox_geometry_read.currentIndex()==3:
                
                table = 'pyunitastratigrafiche'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[2:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)                        
            elif self.comboBox_geometry_read.currentIndex()==4:
                
                table = 'pyunitastratigrafiche_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi) 
            elif self.comboBox_geometry_read.currentIndex()==5:
                
                table = 'pyarchinit_quote'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==6:
                
                table = 'pyarchinit_quote_usm'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==7:
                
                table = 'pyarchinit_us_negative_doc'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==8:
                
                table = 'pyarchinit_strutture_ipotesi'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==9:
                
                table = 'pyarchinit_reperti'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==10:
                
                table = 'pyarchinit_individui'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==11:
                
                table = 'pyarchinit_campionature'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==12:
                
                table = 'pyarchinit_tafonomia'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==13:
                
                table = 'pyarchinit_sezioni'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==14:
                
                table = 'pyarchinit_documentazione'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==15:
                
                table = 'pyarchinit_punti_rif'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
            elif self.comboBox_geometry_read.currentIndex()==16:
                
                table = 'pyarchinit_ripartizioni_spaziali'
                geom_column = 'the_geom'
                uri.setDataSource(schema, table,geom_column)
                vlayer = QgsVectorLayer(uri.uri(), table, 'postgres')
                pr = vlayer.dataProvider()
                fi= pr.fields().names()[1:-1]
                
                self.mFeature_field_rd.clear()
                self.mFeature_field_rd.addItems(fi)
                
            
            
        try:
            self.mFeature_value_rd.clearEditText()
            self.mFeature_value_rd.update()
            self.value_check_geometry(table)
        except:
            pass
    
    
    def value_check_geometry(self,table):
        try:
            self.mFeature_value_rd.clear()
            self.mFeature_value_rd.update()
            if self.mFeature_field_rd.currentTextChanged:
                sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by(table, self.mFeature_field_rd.currentText(), self.comboBox_geometry_read.currentText()))

                try:
                    sito_vl.remove('')
                except:
                    pass
                self.mFeature_value_rd.clear()
                sito_vl.sort()
                
                self.mFeature_value_rd.addItems(sito_vl)
                self.mFeature_value_rd.update()
        except:
            pass
    
    
    def test3(self):
        
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        conn = Connection()
        db_url = conn.conn_str()
        test_conn = db_url.find('sqlite')
        if test_conn == 0:
            
            
            
            engine = create_engine(db_url, echo=True)

            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
            
            tabl=str('SELECT name FROM sqlite_master WHERE type="table" AND name="pyarchinit_quote_usm";') 
            b=c.execute(tabl).fetchone()
            
            if b==None:
                QMessageBox.warning(self, 'Attenzione','Aggiorna il db per inserire i layer per le unità stratigrafiche verticali',QMessageBox.Ok)
                
                
            try:    
                if Qgis.QGIS_VERSION_INT >=32000:
                    version_sl=str('SELECT CheckSpatialMetaData();')
                    a=c.execute(version_sl).fetchall()
                    for row in a:
                        print(row[0])
                    if str(row[0])=='1':
                        QMessageBox.warning(self, 'Attenzione','Versione DB:'+ str(row[0])+'\n'+' '+ 'La versione spatilalite di questo db dveve essere convertito',QMessageBox.Ok)
                    else:
                       pass
            except:
                pass
                
        
    def test(self):
        try:

            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()

            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")

            con = sqlite3.connect(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            cur = con.cursor()



            delete_tab='''DELETE FROM geometry_columns WHERE f_geometry_column = 'geom';'''
            cur.execute(delete_tab)
            drop_ = '''DROP TABLE IF EXISTS sqlitestudio_temp_table2;'''
            cur.execute(drop_)
            drop_2 = '''DROP TABLE IF EXISTS sqlitestudio_temp_table;'''




            cur.executescript('''
            
            
            PRAGMA foreign_keys = 0;
                
                
                CREATE TABLE sqlitestudio_temp_table2 AS SELECT *
                                                          FROM pyarchinit_us_negative_doc;

                DROP TABLE pyarchinit_us_negative_doc;

                CREATE TABLE pyarchinit_us_negative_doc (
                    gid        "INTEGER"  PRIMARY KEY,
                    sito_n     "TEXT",
                    area_n     "TEXT",
                    us_n       "INTEGER",
                    tipo_doc_n "TEXT",
                    nome_doc_n "TEXT",
                    the_geom   LINESTRING
                );

                INSERT INTO pyarchinit_us_negative_doc (
                                                           gid,
                                                           sito_n,
                                                           area_n,
                                                           us_n,
                                                           tipo_doc_n,
                                                           nome_doc_n,
                                                           the_geom
                                                       )
                                                       SELECT pkuid,
                                                              sito_n,
                                                              area_n,
                                                              us_n,
                                                              tipo_doc_n,
                                                              nome_doc_n,
                                                              the_geom
                                                         FROM sqlitestudio_temp_table2;

                DROP TABLE sqlitestudio_temp_table2;

                
                CREATE TRIGGER ggi_pyarchinit_us_negative_doc_the_geom BEFORE INSERT ON pyarchinit_us_negative_doc FOR EACH ROW BEGIN SELECT RAISE(ROLLBACK, "pyarchinit_us_negative_doc.the_geom violates Geometry constraint [geom-type or SRID not allowed]") WHERE ( SELECT type FROM geometry_columns WHERE f_table_name = 'pyarchinit_us_negative_doc' AND f_geometry_column = 'the_geom' AND GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1 ) IS NULL; END; 
                CREATE TRIGGER ggu_pyarchinit_us_negative_doc_the_geom BEFORE UPDATE ON pyarchinit_us_negative_doc FOR EACH ROW BEGIN SELECT RAISE(ROLLBACK, "pyarchinit_documentazione.the_geom violates Geometry constraint [geom-type or SRID not allowed]") WHERE ( SELECT type FROM geometry_columns WHERE f_table_name = 'pyarchinit_us_negative_doc' AND f_geometry_column = 'the_geom' AND GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1 ) IS NULL; END;
                CREATE TRIGGER "gii_pyarchinit_us_negative_doc_the_geom" AFTER INSERT ON "pyarchinit_us_negative_doc" FOR EACH ROW BEGIN DELETE FROM "idx_pyarchinit_us_negative_doc_the_geom" WHERE pkid=NEW.rowid; SELECT RTreeAlign('idx_pyarchinit_us_negative_doc_the_geom', NEW.rowid, NEW."the_geom"); END; 
                CREATE TRIGGER "giu_pyarchinit_us_negative_doc_the_geom" AFTER UPDATE ON "pyarchinit_us_negative_doc" FOR EACH ROW BEGIN DELETE FROM "idx_pyarchinit_us_negative_doc_the_geom" WHERE pkid=NEW.rowid; SELECT RTreeAlign('idx_pyarchinit_us_negative_doc_the_geom', NEW.rowid, NEW."the_geom"); END; 
                CREATE TRIGGER "gid_pyarchinit_us_negative_doc_the_geom" AFTER DELETE ON "pyarchinit_us_negative_doc" FOR EACH ROW BEGIN DELETE FROM "idx_pyarchinit_us_negative_doc_the_geom" WHERE pkid=OLD.rowid; END; 


                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_strutture_ipotesi;

                DROP TABLE pyarchinit_strutture_ipotesi;

                CREATE TABLE pyarchinit_strutture_ipotesi (
                    gid         INTEGER                  PRIMARY KEY AUTOINCREMENT
                                                         NOT NULL,
                    sito        [CHARACTER VARYING] (80),
                    id_strutt   [CHARACTER VARYING] (80),
                    per_iniz    INTEGER,
                    per_fin     INTEGER,
                    dataz_ext   [CHARACTER VARYING] (80),
                    fase_iniz   INTEGER,
                    fase_fin    INTEGER,
                    descrizione [CHARACTER VARYING],
                    the_geom    POLYGON,
                    sigla_strut VARCHAR (3),
                    nr_strut    INTEGER                  DEFAULT 0
                );

                INSERT INTO pyarchinit_strutture_ipotesi (
                                                             gid,
                                                             sito,
                                                             id_strutt,
                                                             per_iniz,
                                                             per_fin,
                                                             dataz_ext,
                                                             fase_iniz,
                                                             fase_fin,
                                                             descrizione,
                                                             the_geom,
                                                             sigla_strut,
                                                             nr_strut
                                                         )
                                                         SELECT id,
                                                                sito,
                                                                id_strutt,
                                                                per_iniz,
                                                                per_fin,
                                                                dataz_ext,
                                                                fase_iniz,
                                                                fase_fin,
                                                                descrizione,
                                                                the_geom,
                                                                sigla_strut,
                                                                nr_strut
                                                           FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_strutture_ipotesi_the_geom
                        BEFORE INSERT
                            ON pyarchinit_strutture_ipotesi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_strutture_ipotesi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_strutture_ipotesi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_strutture_ipotesi_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_strutture_ipotesi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_strutture_ipotesi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_strutture_ipotesi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_sondaggi;

                DROP TABLE pyarchinit_sondaggi;

                CREATE TABLE pyarchinit_sondaggi (
                    gid          INTEGER                  PRIMARY KEY
                                                          NOT NULL,
                    sito_sond    [CHARACTER VARYING] (80),
                    id_sondaggio [CHARACTER VARYING] (80),
                    the_geom     POLYGON
                );

                INSERT INTO pyarchinit_sondaggi (
                                                    gid,
                                                    sito_sond,
                                                    id_sondaggio,
                                                    the_geom
                                                )
                                                SELECT id,
                                                       sito_sond,
                                                       id_sondaggio,
                                                       the_geom
                                                  FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_sondaggi_the_geom
                        BEFORE INSERT
                            ON pyarchinit_sondaggi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sondaggi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sondaggi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_sondaggi_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_sondaggi
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sondaggi.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sondaggi' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_siti_polygonal;

                DROP TABLE pyarchinit_siti_polygonal;

                CREATE TABLE pyarchinit_siti_polygonal (
                    gid      INTEGER PRIMARY KEY AUTOINCREMENT,
                    sito_id  TEXT,
                    the_geom POLYGON
                );

                INSERT INTO pyarchinit_siti_polygonal (
                                                          gid,
                                                          sito_id,
                                                          the_geom
                                                      )
                                                      SELECT pkuid,
                                                             sito_id,
                                                             the_geom
                                                        FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_siti_polygonal_the_geom
                        BEFORE INSERT
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti_polygonal.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti_polygonal' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_siti_polygonal_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti_polygonal.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti_polygonal' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER gii_pyarchinit_siti_polygonal_the_geom
                         AFTER INSERT
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_siti_polygonal_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER giu_pyarchinit_siti_polygonal_the_geom
                         AFTER UPDATE
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_siti_polygonal_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER gid_pyarchinit_siti_polygonal_the_geom
                         AFTER DELETE
                            ON pyarchinit_siti_polygonal
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_siti_polygonal_the_geom
                          WHERE pkid = OLD.rowid;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_siti;

                DROP TABLE pyarchinit_siti;

                CREATE TABLE pyarchinit_siti (
                    gid        INTEGER                  NOT NULL
                                                        PRIMARY KEY AUTOINCREMENT,
                    id_sito    [CHARACTER VARYING] (80),
                    sito_nome  [CHARACTER VARYING] (80),
                    descr_sito [CHARACTER VARYING],
                    the_geom   POINT
                );

                INSERT INTO pyarchinit_siti (
                                                gid,
                                                id_sito,
                                                sito_nome,
                                                descr_sito,
                                                the_geom
                                            )
                                            SELECT id,
                                                   id_sito,
                                                   sito_nome,
                                                   descr_sito,
                                                   the_geom
                                              FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_siti_the_geom
                        BEFORE INSERT
                            ON pyarchinit_siti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_siti_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_siti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_siti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_siti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_ripartizioni_spaziali;

                DROP TABLE pyarchinit_ripartizioni_spaziali;

                CREATE TABLE pyarchinit_ripartizioni_spaziali (
                    gid      INTEGER                  NOT NULL
                                                      PRIMARY KEY AUTOINCREMENT,
                    id_rs    [CHARACTER VARYING] (80),
                    sito_rs  [CHARACTER VARYING] (80),
                    tip_rip  [CHARACTER VARYING],
                    descr_rs [CHARACTER VARYING],
                    the_geom POLYGON
                );

                INSERT INTO pyarchinit_ripartizioni_spaziali (
                                                                 gid,
                                                                 id_rs,
                                                                 sito_rs,
                                                                 tip_rip,
                                                                 descr_rs,
                                                                 the_geom
                                                             )
                                                             SELECT id,
                                                                    id_rs,
                                                                    sito_rs,
                                                                    tip_rip,
                                                                    descr_rs,
                                                                    the_geom
                                                               FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_ripartizioni_spaziali_the_geom
                        BEFORE INSERT
                            ON pyarchinit_ripartizioni_spaziali
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_ripartizioni_spaziali.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_ripartizioni_spaziali' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_ripartizioni_spaziali_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_ripartizioni_spaziali
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_ripartizioni_spaziali.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_ripartizioni_spaziali' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_reperti;

                DROP TABLE pyarchinit_reperti;

                CREATE TABLE pyarchinit_reperti (
                    gid      INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_rep   INTEGER,
                    siti     TEXT,
                    link     TEXT,
                    the_geom POINT,
                    quota    REAL
                );

                INSERT INTO pyarchinit_reperti (
                                                   gid,
                                                   id_rep,
                                                   siti,
                                                   link,
                                                   the_geom,
                                                   quota
                                               )
                                               SELECT ROWIND,
                                                      id_rep,
                                                      siti,
                                                      link,
                                                      the_geom,
                                                      NULL as quota
                                                 FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_reperti_the_geom
                        BEFORE INSERT
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_reperti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_reperti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_reperti_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_reperti.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_reperti' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER gii_pyarchinit_reperti_the_geom
                         AFTER INSERT
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_reperti_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER giu_pyarchinit_reperti_the_geom
                         AFTER UPDATE
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_reperti_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER gid_pyarchinit_reperti_the_geom
                         AFTER DELETE
                            ON pyarchinit_reperti
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_reperti_the_geom
                          WHERE pkid = OLD.rowid;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_quote;

                DROP TABLE pyarchinit_quote;

                CREATE TABLE pyarchinit_quote (
                    gid               INTEGER                  NOT NULL
                                                               PRIMARY KEY AUTOINCREMENT,
                    sito_q            [CHARACTER VARYING] (80),
                    area_q            INTEGER,
                    us_q              INTEGER,
                    unita_misu_q      [CHARACTER VARYING] (80),
                    quota_q           [DOUBLE PRECISION],
                    data              [CHARACTER VARYING],
                    disegnatore       [CHARACTER VARYING],
                    rilievo_originale [CHARACTER VARYING],
                    the_geom          POINT
                );

                INSERT INTO pyarchinit_quote (
                                                 gid,
                                                 sito_q,
                                                 area_q,
                                                 us_q,
                                                 unita_misu_q,
                                                 quota_q,
                                                 data,
                                                 disegnatore,
                                                 rilievo_originale,
                                                 the_geom
                                             )
                                             SELECT id,
                                                    sito_q,
                                                    area_q,
                                                    us_q,
                                                    unita_misu_q,
                                                    quota_q,
                                                    data,
                                                    disegnatore,
                                                    rilievo_originale,
                                                    the_geom
                                               FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_quote_the_geom
                        BEFORE INSERT
                            ON pyarchinit_quote
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_quote.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_quote' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_quote_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_quote
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_quote.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_quote' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_punti_rif;

                DROP TABLE pyarchinit_punti_rif;

                CREATE TABLE pyarchinit_punti_rif (
                    gid                INTEGER                  NOT NULL
                                                                PRIMARY KEY AUTOINCREMENT,
                    sito               [CHARACTER VARYING] (80),
                    def_punto          [CHARACTER VARYING] (80),
                    id_punto           [CHARACTER VARYING] (80),
                    quota              [DOUBLE PRECISION],
                    unita_misura_quota [CHARACTER VARYING],
                    area               INTEGER,
                    the_geom           POINT
                );

                INSERT INTO pyarchinit_punti_rif (
                                                     gid,
                                                     sito,
                                                     def_punto,
                                                     id_punto,
                                                     quota,
                                                     unita_misura_quota,
                                                     area,
                                                     the_geom
                                                 )
                                                 SELECT id,
                                                        sito,
                                                        def_punto,
                                                        id_punto,
                                                        quota,
                                                        unita_misura_quota,
                                                        area,
                                                        the_geom
                                                   FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_punti_rif_the_geom
                        BEFORE INSERT
                            ON pyarchinit_punti_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_punti_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_punti_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_punti_rif_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_punti_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_punti_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_punti_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_linee_rif;

                DROP TABLE pyarchinit_linee_rif;

                CREATE TABLE pyarchinit_linee_rif (
                    gid        INTEGER                   NOT NULL
                                                         PRIMARY KEY AUTOINCREMENT,
                    sito       [CHARACTER VARYING] (300),
                    definizion [CHARACTER VARYING] (80),
                    descrizion [CHARACTER VARYING] (80),
                    the_geom   LINESTRING
                );

                INSERT INTO pyarchinit_linee_rif (
                                                     gid,
                                                     sito,
                                                     definizion,
                                                     descrizion,
                                                     the_geom
                                                 )
                                                 SELECT id,
                                                        sito,
                                                        definizion,
                                                        descrizion,
                                                        the_geom
                                                   FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_linee_rif_the_geom
                        BEFORE INSERT
                            ON pyarchinit_linee_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_linee_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_linee_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_linee_rif_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_linee_rif
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_linee_rif.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_linee_rif' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_individui;

                DROP TABLE pyarchinit_individui;

                CREATE TABLE pyarchinit_individui (
                    gid             INTEGER                   NOT NULL
                                                              PRIMARY KEY AUTOINCREMENT,
                    sito            [CHARACTER VARYING] (255),
                    sigla_struttura [CHARACTER VARYING] (255),
                    note            [CHARACTER VARYING] (255),
                    id_individuo    INTEGER,
                    the_geom        POINT
                );

                INSERT INTO pyarchinit_individui (
                                                     gid,
                                                     sito,
                                                     sigla_struttura,
                                                     note,
                                                     id_individuo,
                                                     the_geom
                                                 )
                                                 SELECT id,
                                                        sito,
                                                        sigla_struttura,
                                                        note,
                                                        id_individuo,
                                                        the_geom
                                                   FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_individui_the_geom
                        BEFORE INSERT
                            ON pyarchinit_individui
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_individui.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_individui' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_individui_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_individui
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_individui.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_individui' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_documentazione;

                DROP TABLE pyarchinit_documentazione;

                CREATE TABLE pyarchinit_documentazione (
                    gid          INTEGER    PRIMARY KEY AUTOINCREMENT,
                    sito         TEXT,
                    nome_doc     TEXT,
                    tipo_doc     TEXT,
                    path_qgis_pj TEXT,
                    the_geom     LINESTRING
                );

                INSERT INTO pyarchinit_documentazione (
                                                          gid,
                                                          sito,
                                                          nome_doc,
                                                          tipo_doc,
                                                          path_qgis_pj,
                                                          the_geom
                                                      )
                                                      SELECT pkuid,
                                                             sito,
                                                             nome_doc,
                                                             tipo_doc,
                                                             path_qgis_pj,
                                                             the_geom
                                                        FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_documentazione_the_geom
                        BEFORE INSERT
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_documentazione.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_documentazione' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_documentazione_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_documentazione.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_documentazione' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER gii_pyarchinit_documentazione_the_geom
                         AFTER INSERT
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_documentazione_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER giu_pyarchinit_documentazione_the_geom
                         AFTER UPDATE
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_documentazione_the_geom
                          WHERE pkid = NEW.rowid;
                END;

                CREATE TRIGGER gid_pyarchinit_documentazione_the_geom
                         AFTER DELETE
                            ON pyarchinit_documentazione
                      FOR EACH ROW
                BEGIN
                    DELETE FROM idx_pyarchinit_documentazione_the_geom
                          WHERE pkid = OLD.rowid;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_campionature;

                DROP TABLE pyarchinit_campionature;

                CREATE TABLE pyarchinit_campionature (
                    gid        INTEGER                   NOT NULL
                                                         PRIMARY KEY AUTOINCREMENT,
                    id_campion INTEGER,
                    sito       [CHARACTER VARYING] (200),
                    tipo_camp  [CHARACTER VARYING] (200),
                    dataz      [CHARACTER VARYING] (200),
                    cronologia INTEGER,
                    link_immag [CHARACTER VARYING] (500),
                    sigla_camp [CHARACTER VARYING],
                    the_geom   POINT
                );

                INSERT INTO pyarchinit_campionature (
                                                        gid,
                                                        id_campion,
                                                        sito,
                                                        tipo_camp,
                                                        dataz,
                                                        cronologia,
                                                        link_immag,
                                                        sigla_camp,
                                                        the_geom
                                                    )
                                                    SELECT id,
                                                           id_campion,
                                                           sito,
                                                           tipo_camp,
                                                           dataz,
                                                           cronologia,
                                                           link_immag,
                                                           sigla_camp,
                                                           the_geom
                                                      FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_campionature_the_geom
                        BEFORE INSERT
                            ON pyarchinit_campionature
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_campionature.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_campionature' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_campionature_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_campionature
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_campionature.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_campionature' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                PRAGMA foreign_keys = 0;

                CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                                          FROM pyarchinit_sezioni;

                DROP TABLE pyarchinit_sezioni;

                CREATE TABLE pyarchinit_sezioni (
                    gid        INTEGER                  NOT NULL
                                                        PRIMARY KEY AUTOINCREMENT,
                    id_sezione [CHARACTER VARYING] (80),
                    sito       [CHARACTER VARYING] (80),
                    area       INTEGER,
                    descr      [CHARACTER VARYING] (80),
                    the_geom   LINESTRING,
                    tipo_doc   TEXT,
                    nome_doc   TEXT
                );

                INSERT INTO pyarchinit_sezioni (
                                                   gid,
                                                   id_sezione,
                                                   sito,
                                                   area,
                                                   descr,
                                                   the_geom,
                                                   tipo_doc,
                                                   nome_doc
                                               )
                                               SELECT id,
                                                      id_sezione,
                                                      sito,
                                                      area,
                                                      descr,
                                                      the_geom,
                                                      tipo_doc,
                                                      nome_doc
                                                 FROM sqlitestudio_temp_table;

                DROP TABLE sqlitestudio_temp_table;

                CREATE TRIGGER ggi_pyarchinit_sezioni_the_geom
                        BEFORE INSERT
                            ON pyarchinit_sezioni
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sezioni.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sezioni' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                CREATE TRIGGER ggu_pyarchinit_sezioni_the_geom
                        BEFORE UPDATE
                            ON pyarchinit_sezioni
                      FOR EACH ROW
                BEGIN
                    SELECT RAISE(ROLLBACK, "pyarchinit_sezioni.the_geom violates Geometry constraint [geom-type or SRID not allowed]") 
                     WHERE (
                               SELECT type
                                 FROM geometry_columns
                                WHERE f_table_name = 'pyarchinit_sezioni' AND 
                                      f_geometry_column = 'the_geom' AND 
                                      GeometryConstraints(NEW.the_geom, type, srid, 'XY') = 1
                           )
                           IS NULL;
                END;

                PRAGMA foreign_keys = 1;
                 
                
                
                
                        ''')

        except Exception as e:
            pass#QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
    
    
    def test2(self):
        try:
            
            conn = Connection()
            conn_str = conn.conn_str()
            conn_sqlite = conn.databasename()
            
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            
            con = sqlite3.connect(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            cur = con.cursor()

            cur.executescript('''
                PRAGMA foreign_keys = 0;
            
                
                    DROP VIEW IF EXISTS pyarchinit_reperti_view;
                    CREATE VIEW pyarchinit_reperti_view AS
                        SELECT a.rowid AS rowid,
                        a.the_geom AS the_geom,
                        a.id_rep AS id_rep,
                        a.siti AS siti,
                        a.link AS link,
                        b.rowid AS rowid_1,
                        b.id_invmat AS id_invmat,
                        b.sito AS sito,
                        b.numero_inventario AS numero_inventario,
                        b.tipo_reperto AS tipo_reperto,
                        b.criterio_schedatura AS criterio_schedatura,
                        b.definizione AS definizione,
                        b.descrizione AS descrizione,
                        b.area AS area,
                        b.us AS us,
                        b.lavato AS lavato,
                        b.nr_cassa AS nr_cassa,
                        b.luogo_conservazione AS luogo_conservazione,
                        b.stato_conservazione AS stato_conservazione,
                        b.datazione_reperto AS datazione_reperto,
                        b.elementi_reperto AS elementi_reperto,
                        b.misurazioni AS misurazioni,
                        b.rif_biblio AS rif_biblio,
                        b.tecnologie AS tecnologie,
                        b.forme_minime AS forme_minime,
                        b.forme_massime AS forme_massime,
                        b.totale_frammenti AS totale_frammenti,
                        b.corpo_ceramico AS corpo_ceramico,
                        b.rivestimento AS rivestimento,
                        b.n_reperto as n_reperto
                        FROM pyarchinit_reperti AS a
                        JOIN
                        inventario_materiali_table AS b ON (a.siti = b.sito AND 
                        a.id_rep = b.numero_inventario);
                        
                        PRAGMA foreign_keys = 1;
                        PRAGMA foreign_keys = 0;
                        CREATE TABLE IF NOT EXISTS pottery_table (
                            id_rep             INTEGER        NOT NULL,
                            id_number          INTEGER,
                            sito               TEXT,
                            area               TEXT,
                            us                 INTEGER,
                            box                INTEGER,
                            photo              TEXT,
                            drawing            TEXT,
                            anno               INTEGER,
                            fabric             TEXT,
                            percent            TEXT,
                            material           TEXT,
                            form               TEXT,
                            specific_form      TEXT,
                            ware               TEXT,
                            munsell            TEXT,
                            surf_trat          TEXT,
                            exdeco             TEXT,
                            intdeco            TEXT,
                            wheel_made         TEXT,
                            descrip_ex_deco    TEXT,
                            descrip_in_deco    TEXT,
                            note               TEXT,
                            diametro_max       NUMERIC (7, 3),
                            qty                INTEGER,
                            diametro_rim       NUMERIC (7, 3),
                            diametro_bottom    NUMERIC (7, 3),
                            diametro_height    NUMERIC (7, 3),
                            diametro_preserved NUMERIC (7, 3),
                            specific_shape     TEXT,
                            bag                INTEGER,
                            sector             TEXT,
                            PRIMARY KEY (
                                id_rep
                            ),
                            CONSTRAINT ID_rep_unico UNIQUE (
                                sito,
                                id_number
                            )
                        );
                    
                PRAGMA foreign_keys = 1;   
            ''')
            #c.close()
        except KeyError as e:
            pass#QMessageBox.warning(self, "ok", str(e), QMessageBox.Ok)
    def setComboBoxEnable(self, f, v):
        field_names = f
        value = v
        for fn in field_names:
            cmd = '{}{}{}{}'.format(fn, '.setEnabled(', v, ')')
            eval(cmd)
    
    def customize(self):
        # Prevent recursive calls
        if getattr(self, '_customizing', False):
            return
        self._customizing = True

        try:
            # Enable DBname field for both SQLite and PostgreSQL
            # SQLite needs it for the database file name
            # PostgreSQL needs it for the database name
            self.setComboBoxEnable(["self.lineEdit_DBname"], "True")

            # Log the current state for debugging
            if hasattr(self, 'logger'):
                self.logger.log(f"customize() called - DB type: {self.comboBox_Database.currentText()}")
                self.logger.log(f"DBname field enabled: True")
        finally:
            self._customizing = False
    def db_uncheck(self):
        self.toolButton_active.setChecked(False)
    def upd_individui_table(self):
        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        conn = Connection()
        db_url = conn.conn_str()
        test_conn = db_url.find('sqlite')
        if test_conn == 0:
            try:
                engine = create_engine(db_url, echo=True)

                listen(engine, 'connect', self.load_spatialite)
                c = engine.connect()
                sql_upd=("""
                        CREATE TABLE sqlitestudio_temp_table_ AS SELECT *
                                                                  FROM individui_table;""")

                        
                        
                sql_upd1=("""DROP TABLE individui_table;""")

                sql_upd2=(""" CREATE TABLE individui_table (
                            id_scheda_ind            INTEGER        NOT NULL,
                            sito                     TEXT,
                            area                     TEXT,
                            us                       TEXT,
                            nr_individuo             INTEGER,
                            data_schedatura          VARCHAR (100),
                            schedatore               VARCHAR (100),
                            sesso                    VARCHAR (100),
                            eta_min                  TEXT,
                            eta_max                  TEXT,
                            classi_eta               VARCHAR (100),
                            osservazioni             TEXT,
                            sigla_struttura          TEXT,
                            nr_struttura             TEXT,
                            completo_si_no           TEXT,
                            disturbato_si_no         TEXT,
                            in_connessione_si_no     TEXT,
                            lunghezza_scheletro      NUMERIC (6, 2),
                            posizione_scheletro      TEXT,
                            posizione_cranio         TEXT,
                            posizione_arti_superiori TEXT,
                            posizione_arti_inferiori TEXT,
                            orientamento_asse        TEXT,
                            orientamento_azimut      TEXT,
                            PRIMARY KEY (
                                id_scheda_ind
                            ),
                            CONSTRAINT ID_individuo_unico UNIQUE (
                                sito,
                                nr_individuo
                            )
                        );""")

                sql_upd3=("""INSERT INTO individui_table (
                                                    id_scheda_ind,
                                                    sito,
                                                    area,
                                                    us,
                                                    nr_individuo,
                                                    data_schedatura,
                                                    schedatore,
                                                    sesso,
                                                    eta_min,
                                                    eta_max,
                                                    classi_eta,
                                                    osservazioni,
                                                    sigla_struttura,
                                                    nr_struttura,
                                                    completo_si_no,
                                                    disturbato_si_no,
                                                    in_connessione_si_no,
                                                    lunghezza_scheletro,
                                                    posizione_scheletro,
                                                    posizione_cranio,
                                                    posizione_arti_superiori,
                                                    posizione_arti_inferiori,
                                                    orientamento_asse,
                                                    orientamento_azimut
                                                )
                                                SELECT id_scheda_ind,
                                                       sito,
                                                       area,
                                                       us,
                                                       nr_individuo,
                                                       data_schedatura,
                                                       schedatore,
                                                       sesso,
                                                       eta_min,
                                                       eta_max,
                                                       classi_eta,
                                                       osservazioni,
                                                       sigla_struttura,
                                                       nr_struttura,
                                                       completo_si_no,
                                                       disturbato_si_no,
                                                       in_connessione_si_no,
                                                       lunghezza_scheletro,
                                                       posizione_scheletro,
                                                       posizione_cranio,
                                                       posizione_arti_superiori,
                                                       posizione_arti_inferiori,
                                                       orientamento_asse,
                                                       orientamento_azimut
                                                  FROM sqlitestudio_temp_table_;""")

                        
                sql_upd4=("""DROP TABLE sqlitestudio_temp_table_;""")
                        
                c.execute(sql_upd)
                c.execute(sql_upd1)  
                c.execute(sql_upd2)  
                c.execute(sql_upd3)  
                c.execute(sql_upd4)              
                c.close()
                
            
            except Exception as e:
                QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
        else:
            pass
    
    
    
    def geometry_conn(self):
        pass
        # if self.comboBox_server_rd.currentText()!='sqlite':
            # self.pushButton_import_geometry.setEnabled(False)
        # else:
            # self.pushButton_import_geometry.setEnabled(True)

    def message(self):
        if self.checkBox_abort.isChecked():
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Se i ci sono duplicati l'importazione verrà abortita.\n Se vuoi ignorare i duplicati o aggiornare con i dati nuovi spunta una delle opzioni ignora o aggiorna", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Wenn es Duplikate gibt, wird der Import abgebrochen.\n Wenn Sie die Duplikate ignorieren oder mit neuen Daten aktualisieren möchten, aktivieren Sie eine der Optionen ignorieren oder aktualisieren", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "If there are duplicates the import will be aborted.\n If you want to ignore the duplicates or update with new data check one of the options ignore or replace", QMessageBox.Ok)
        
        if self.checkBox_ignore.isChecked():
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", 'Verranno copiati solo i dati nuovi', QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", 'Es werden nur neue Daten kopiert.', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", 'Only new data will be copied', QMessageBox.Ok)
        
        if self.checkBox_replace.isChecked():
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", 'Verranno copiati i dati nuovi e aggiornati quelli esistenti', QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", 'Neue Daten werden kopiert und bestehende Daten werden aktualisiert', QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", 'New data will be copied and existing data will be updated', QMessageBox.Ok)
        
    
    def check(self):
        try:
            if self.checkBox_ignore.isChecked():
                self.message()
                @compiles(Insert)
                def _prefix_insert_with_ignore(insert_srt, compiler, **kw):

                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR IGNORE'), **kw)
                    else:
                        #if the connection is postgresql
                        ck = insert_srt.table.constraints
                        # pk = insert_srt.table.primary_key
                        insert = compiler.visit_insert(insert_srt, **kw)
                        c = next(x for x in ck if isinstance(x, sa.UniqueConstraint))
                        column_names = [col.name for col in c.columns]
                        s= ", ".join(column_names)
                        ondup = f'ON CONFLICT ({s})DO NOTHING'
                    
                        upsert = ' '.join((insert, ondup))
                        return upsert
                       
                        
           
            if self.checkBox_replace.isChecked():
                self.message()
                @compiles(Insert)
                def _prefix_insert_with_replace(insert_srt, compiler, **kw):
                    ##############importo i dati nuovi aggiornando i vecchi dati########################
                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR REPLACE'), **kw)
                    else:
                        #return compiler.visit_insert(insert.prefix_with(''), **kw)
                        
                        ck = insert_srt.table.constraints
                        insert = compiler.visit_insert(insert_srt, **kw)

                        # Try to find UniqueConstraint, if not found use primary key
                        unique_constraint = None
                        for x in ck:
                            if isinstance(x, sa.UniqueConstraint):
                                unique_constraint = x
                                break

                        if unique_constraint:
                            column_names = [col.name for col in unique_constraint.columns]
                        else:
                            # Use primary key columns if no unique constraint
                            pk_cols = [col for col in insert_srt.table.columns if col.primary_key]
                            if pk_cols:
                                column_names = [col.name for col in pk_cols]
                            else:
                                # Fallback to just return the insert without ON CONFLICT
                                return insert

                        s = ", ".join(column_names)
                        
                        
                        ondup = f"ON CONFLICT ({s}) DO UPDATE SET"
                        updates = ", ".join(f'{c.name}=EXCLUDED.{c.name}' for c in insert_srt.table.columns)
                        upsert = " ".join((insert, ondup, updates))
                        return upsert
        
            if self.checkBox_abort.isChecked():
                #self.message()
                @compiles(Insert)
                def _prefix_insert_with_ignore(insert_srt, compiler, **kw):

                    conn = Connection()
                    conn_str = conn.conn_str()
                    test_conn = conn_str.find("sqlite")
                    if test_conn == 0:
                        return compiler.visit_insert(insert_srt.prefix_with('OR ABORT'), **kw)
                    else:
                        #return compiler.visit_insert(insert.prefix_with(''), **kw)
                        pk = insert_srt.table.primary_key
                        insert = compiler.visit_insert(insert_srt, **kw)
                        ondup = f'ON CONFLICT ({",".join(c.name for c in pk)}) DO NOTHING'
                        #updates = ', '.join(f"{c.name}=EXCLUDED.{c.name}" for c in insert_srt.table.columns)
                        upsert = ' '.join((insert, ondup))
                        return insert
        
        
        except:
            pass
    def summary(self):
        # Skip update if we're in the middle of database creation
        if not hasattr(self, 'skip_combo_update'):
            self.comboBox_Database.update()

        conn = Connection()
        conn_str = conn.conn_str()
        conn_sqlite = conn.databasename()
        conn_user = conn.datauser()
        conn_host = conn.datahost()
        conn_port = conn.dataport()
        port_int  = conn_port["port"]
        port_int.replace("'", "")
        #QMessageBox.warning(self, "Attenzione", port_int, QMessageBox.Ok)
        conn_password = conn.datapassword()


        sito_set= conn.sito_set()
        sito_set_str = sito_set['sito_set']

        test_conn = conn_str.find('sqlite')
        if test_conn == 0:
            sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                           "pyarchinit_DB_folder")
            db = QSqlDatabase("QSQLITE")
            db.setDatabaseName(sqlite_DB_path +os.sep+ conn_sqlite["db_name"])
            db.open()
            #self.table = QTableView()
            self.model_a = QSqlQueryModel()

            self.tableView_summary.setModel(self.model_a)

            sito_filter = str(self.comboBox_sito.currentText()) if bool(self.comboBox_sito.currentText()) else None

            if sito_filter:
                # Use subqueries instead of JOINs (more efficient, avoids cartesian product)
                query = QSqlQuery("select '{}' as Sito,"
                                  "(select count(distinct us) from us_table where sito = '{}') as US,"
                                  "(select count(distinct numero_inventario) from inventario_materiali_table where sito = '{}') as Materiali,"
                                  "(select count(distinct id_struttura) from struttura_table where sito = '{}') as Strutture,"
                                  "(select count(distinct id_tomba) from tomba_table where sito = '{}') as Tombe,"
                                  "(select count(distinct id_rep) from pottery_table where sito = '{}') as Pottery,"
                                  "(select count(*) from media_thumb_table) as Media".format(
                                      sito_filter, sito_filter, sito_filter, sito_filter, sito_filter, sito_filter), db=db)
                self.model_a.setQuery(query)
            else:
                query1 = QSqlQuery("select s.sito as Sito,"
                                   "(select count(distinct us) from us_table ad where s.sito=ad.sito) as US,"
                                   "(select count(distinct numero_inventario) from inventario_materiali_table m where s.sito = m.sito) as Materiali,"
                                   "(select count(distinct id_struttura) from struttura_table st where s.sito = st.sito) as Strutture,"
                                   "(select count(distinct id_tomba) from tomba_table t where s.sito = t.sito) as Tombe,"
                                   "(select count(distinct id_rep) from pottery_table p where s.sito = p.sito) as Pottery,"
                                   "(select count(*) from media_thumb_table) as Media "
                                   "from (select sito, count(distinct us) from us_table group by sito) as s "
                                   "order by s.sito;", db=db)
                self.model_a.setQuery(query1)



            # self.model_a.setTable("us_table")
            # self.model_a.setEditStrategy(QSqlTableModel.OnManualSubmit)

            # if bool (sito_set_str):
                # filter_str = "sito = '{}'".format(str(self.comboBox_sito.currentText()))
                # self.model_a.setFilter(filter_str)
                # self.model_a.select()
            # else:

                # self.model_a.select()
            self.tableView_summary.clearSpans()
        else:
            # Use unique connection name to avoid conflicts
            conn_name = "pyarchinit_summary_conn"
            if QSqlDatabase.contains(conn_name):
                db = QSqlDatabase.database(conn_name)
            else:
                db = QSqlDatabase.addDatabase("QPSQL", conn_name)

            db.setHostName(conn_host["host"])
            db.setDatabaseName(conn_sqlite["db_name"])
            db.setPort(int(port_int))
            db.setUserName(conn_user['user'])
            db.setPassword(conn_password['password'])
            # Add SSL option for Supabase
            db.setConnectOptions("sslmode=require")

            if not db.open():
                # Try without SSL if it fails
                db.setConnectOptions("")
                db.open()

            self.model_a = QSqlQueryModel()

            self.tableView_summary.setModel(self.model_a)

            sito_filter = str(self.comboBox_sito.currentText()) if bool(self.comboBox_sito.currentText()) else None

            if sito_filter:
                # Use subqueries instead of JOINs (more efficient, avoids cartesian product)
                query = QSqlQuery("select '{}' as Sito,"
                                  "(select count(distinct id_us) from us_table where sito = '{}') as US,"
                                  "(select count(distinct id_invmat) from inventario_materiali_table where sito = '{}') as Materiali,"
                                  "(select count(distinct id_struttura) from struttura_table where sito = '{}') as Strutture,"
                                  "(select count(distinct id_tomba) from tomba_table where sito = '{}') as Tombe,"
                                  "(select count(distinct id_rep) from pottery_table where sito = '{}') as Pottery,"
                                  "(select count(*) from media_thumb_table) as Media".format(
                                      sito_filter, sito_filter, sito_filter, sito_filter, sito_filter, sito_filter), db=db)
                self.model_a.setQuery(query)
            else:
                query1 = QSqlQuery("select s.sito as Sito,"
                                   "(select count(distinct id_us) from us_table ad where s.sito=ad.sito) as US,"
                                   "(select count(distinct id_invmat) from inventario_materiali_table m where s.sito = m.sito) as Materiali,"
                                   "(select count(distinct id_struttura) from struttura_table st where s.sito = st.sito) as Strutture,"
                                   "(select count(distinct id_tomba) from tomba_table t where s.sito = t.sito) as Tombe,"
                                   "(select count(distinct id_rep) from pottery_table p where s.sito = p.sito) as Pottery,"
                                   "(select count(*) from media_thumb_table) as Media "
                                   "from (select sito, count(distinct id_us) from us_table group by sito) as s "
                                   "order by s.sito;", db=db)
                self.model_a.setQuery(query1)

            self.tableView_summary.clearSpans()

    def check_if_admin(self):
        """Check if current user is admin"""
        try:
            # Get current username from settings or connection
            username = 'admin'  # Default

            if hasattr(self, 'DB_MANAGER') and self.DB_MANAGER:
                # Try to get username from settings
                s = QgsSettings()
                username = s.value('pyArchInit/current_user', 'admin', type=str)

                # Check in database if user is admin
                if self.comboBox_Database.currentText() == 'postgres':
                    try:
                        query = "SELECT role FROM pyarchinit_users WHERE username = :username AND is_active = TRUE"
                        result = self.DB_MANAGER.execute_sql(query, {'username': username})
                        if result and len(result) > 0:
                            return result[0][0] == 'admin'
                    except:
                        # If table doesn't exist or query fails, assume admin
                        return True

            # Default to admin for backward compatibility
            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Error checking admin status: {str(e)}", "PyArchInit", Qgis.Warning)
            return True  # Default to admin if error

    def db_active (self):
        # Prevent recursive calls
        if getattr(self, '_db_active_running', False):
            return
        self._db_active_running = True

        try:
            self.comboBox_Database.update()
            self.comboBox_sito.clear()

            # Check if user is admin
            is_admin = self.check_if_admin()

            # Set tooltip for non-admin users
            admin_msg = "Solo gli amministratori possono eseguire backup/restore" if not is_admin else ""

            if self.comboBox_Database.currentText() == 'sqlite':
                #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                self.toolButton_db.setEnabled(True)
                # Enable SQLite backup button only for admin
                self.pushButton_upd_sqlite.setEnabled(is_admin)
                self.pushButton_upd_sqlite.setToolTip(admin_msg)
                # Disable PostgreSQL buttons
                self.pushButton_upd_postgres.setEnabled(False)
                if hasattr(self, 'pushButton_crea_database'):
                    self.pushButton_crea_database.setEnabled(False)
                if hasattr(self, 'pushButton_restore_postgres'):
                    self.pushButton_restore_postgres.setEnabled(False)

            elif self.comboBox_Database.currentText() == 'postgres':
                #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                self.toolButton_db.setEnabled(False)
                # Enable PostgreSQL buttons only for admin
                self.pushButton_upd_postgres.setEnabled(is_admin)
                self.pushButton_upd_postgres.setToolTip(admin_msg)
                if hasattr(self, 'pushButton_crea_database'):
                    self.pushButton_crea_database.setEnabled(is_admin)
                    self.pushButton_crea_database.setToolTip(admin_msg)
                if hasattr(self, 'pushButton_restore_postgres'):
                    self.pushButton_restore_postgres.setEnabled(is_admin)
                    self.pushButton_restore_postgres.setToolTip(admin_msg)
                # Disable SQLite backup button
                self.pushButton_upd_sqlite.setEnabled(False)

            self.comboBox_sito.clear()
        finally:
            self._db_active_running = False
    def setPathDBsqlite1(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

                self.lineEdit_database_rd.setText(filename)
                s.setValue('',filename)

        #self.comboBox_Database.setCurrentText('sqlite')
        #self.lineEdit_DBname.setText(filename)
        #self.on_pushButton_save_pressed()


    def setPathDBsqlite2(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

            self.lineEdit_database_wt.setText(filename)
            s.setValue('',filename)

    def openthumbDir(self):
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

            self.lineEdit_DBname.setText(filename)
            s.setValue('',filename)
    def openresizeDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_resize.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    def db_name_change(self):
        if str(self.comboBox_Database.currentText()) == 'sqlite':
            self.comboBox_Database.update()
            self.save_and_clear_comboBox_sito()

            # Update toolButton after save operation
            self.tool_ok()

            # Check if DB_MANAGER is connected before using it
            if hasattr(self, 'DB_MANAGER') and self.DB_MANAGER:
                try:
                    # Fetch site_table grouped by 'sito' and 'SITE' and converts it into a list
                    site_values_list = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))

                    if len(site_values_list) > 0:
                        self.comboBox_sito.setCurrentText(site_values_list[0])
                    else:
                        self.comboBox_sito.setCurrentText('')  # or some default value
                except Exception as e:
                    # Log error but don't crash
                    QgsMessageLog.logMessage(f"Error loading site values: {str(e)}", "PyArchInit", Qgis.Warning)
                    self.comboBox_sito.setCurrentText('')

            # Save after comboBox_sito text change
            self.save_p()
        else:
            self.comboBox_Database.update()
            self.save_and_clear_comboBox_sito()
            #self.tool_ok()
            self.save_p()

    def save_and_clear_comboBox_sito(self):
        # Save current state
        self.save_p()
        # Clear comboBox_sito
        self.comboBox_sito.clear()
        # Save after clearing
        self.save_p()

    def save_p(self):

        self.comboBox_Database.update()
        try:
            if not bool(self.lineEdit_Password.text()) and str(self.comboBox_Database.currentText()) == 'postgres':
                print('non dimenticarti di inserire la password')
            else:
                self.PARAMS_DICT['SERVER'] = str(self.comboBox_Database.currentText())
                self.PARAMS_DICT['HOST'] = str(self.lineEdit_Host.text())
                self.PARAMS_DICT['DATABASE'] = str(self.lineEdit_DBname.text())
                self.PARAMS_DICT['PASSWORD'] = str(self.lineEdit_Password.text())
                self.PARAMS_DICT['PORT'] = str(self.lineEdit_Port.text())
                self.PARAMS_DICT['USER'] = str(self.lineEdit_User.text())
                self.PARAMS_DICT['THUMB_PATH'] = str(self.lineEdit_Thumb_path.text())
                self.PARAMS_DICT['THUMB_RESIZE'] = str(self.lineEdit_Thumb_resize.text())
                self.PARAMS_DICT['EXPERIMENTAL'] = str(self.comboBox_experimental.currentText())
                self.PARAMS_DICT['SITE_SET'] = str(self.comboBox_sito.currentText())
                self.PARAMS_DICT['LOGO'] = str(self.lineEdit_logo.text())
                self.save_dict()

                if str(self.comboBox_Database.currentText()) == 'postgres':

                    b = str(self.select_version_sql())

                    a = "90313"

                    if a == b:
                        link = 'https://www.postgresql.org/download/'
                        if self.L == 'it':
                            msg = "Stai utilizzando la versione di Postgres: " + str(
                                b) + ". Tale versione è diventata obsoleta e potresti riscontrare degli errori. Aggiorna PostgreSQL ad una versione più recente. <br><a href='%s'>PostgreSQL</a>" % link
                        if self.L == 'de':
                            msg = "Sie benutzen die Postgres-Version: " + str(
                                b) + ". Diese Version ist veraltet, und Sie werden möglicherweise einige Fehler finden. Aktualisieren Sie PostgreSQL auf eine neuere Version. <br><a href='%s'>PostgreSQL</a>" % link
                        else:
                            msg = "You are using the Postgres version: " + str(
                                b) + ". This version has become obsolete and you may find some errors. Update PostgreSQL to a newer version. <br><a href='%s'>PostgreSQL</a>" % link
                        QMessageBox.information(self, "INFO", msg, QMessageBox.Ok)
                    else:
                        pass
                else:
                    pass

                self.connection_up()

        except Exception as e:
            if self.L == 'it':
                QMessageBox.warning(self, "INFO", "Problema di connessione al db. Controlla i paramatri inseriti",
                                    QMessageBox.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "INFO", "Db-Verbindungsproblem. Überprüfen Sie die eingegebenen Parameter",
                                    QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "INFO", "Db connection problem. Check the parameters inserted",
                                    QMessageBox.Ok)

    def on_pushButton_update_db_pressed(self):
        """
        Handler for the new update button that updates existing databases
        without deleting data using the DB_update class
        """
        try:
            # Import the DB_update class
            from modules.db.pyarchinit_db_update import DB_update
            
            # Get the current connection
            conn = Connection()
            conn_str = conn.conn_str()
            
            # Determine the database type
            db_type = self.comboBox_Database.currentText()
            
            # Create DB_update instance
            db_updater = DB_update(conn_str)
            
            # Show progress message
            if self.L == 'it':
                QMessageBox.information(self, "INFO", "Aggiornamento database in corso...", QMessageBox.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "INFO", "Datenbank-Update läuft...", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "INFO", "Database update in progress...", QMessageBox.Ok)
            
            # Perform the update
            db_updater.update_table()
            
            # Show success message
            if self.L == 'it':
                QMessageBox.information(self, "INFO", "Database aggiornato con successo!", QMessageBox.Ok)
            elif self.L == 'de':
                QMessageBox.information(self, "INFO", "Datenbank erfolgreich aktualisiert!", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "INFO", "Database updated successfully!", QMessageBox.Ok)
                
        except Exception as e:
            # Show error message
            if self.L == 'it':
                QMessageBox.critical(self, "ERRORE", 
                    f"Errore durante l'aggiornamento del database:\n{str(e)}", 
                    QMessageBox.Ok)
            elif self.L == 'de':
                QMessageBox.critical(self, "FEHLER", 
                    f"Fehler beim Aktualisieren der Datenbank:\n{str(e)}", 
                    QMessageBox.Ok)
            else:
                QMessageBox.critical(self, "ERROR", 
                    f"Error updating database:\n{str(e)}", 
                    QMessageBox.Ok)

    def tool_ok(self):

        self.toolButton_active.isChecked()
        if str(self.comboBox_Database.currentText()) == 'sqlite':
            self.charge_list()
        else:
            pass


    def setPathDB(self):

        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            " db sqlite (*.sqlite)"
        )[0]
        filename=dbpath.split("/")[-1]
        if filename:

            self.lineEdit_DBname.setText(filename)
            s.setValue('',filename)

    def setPathThumb(self):
        s = QgsSettings()
        self.thumbpath = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.thumbpath:
            self.lineEdit_Thumb_path.setText(self.thumbpath+"/")
            s.setValue('pyArchInit/thumbpath', self.thumbpath)
    def setPathlogo(self):
        
        s = QgsSettings()
        dbpath = QFileDialog.getOpenFileName(
            self,
            "Set file name",
            self.DBFOLDER,
            "image (*.*)"
        )[0]
        #filename=dbpath.split("/")[-1]
        if dbpath:

            self.lineEdit_logo.setText(dbpath)
            s.setValue('',dbpath)
    def setPathResize(self):
        s = QgsSettings()
        self.resizepath = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )
        if self.resizepath:
            self.lineEdit_Thumb_resize.setText(self.resizepath+"/")
            s.setValue('pyArchInit/risizepath', self.resizepath)

    def openRemoteStorageConfig(self):
        """
        Open the remote storage configuration dialog.

        Allows users to configure credentials for:
        - Google Drive (gdrive://)
        - Dropbox (dropbox://)
        - Amazon S3 / Cloudflare R2 (s3://, r2://)
        - WebDAV (webdav://)
        - HTTP/HTTPS (http://, https://)
        """
        try:
            from .remote_storage_dialog import RemoteStorageDialog
            dialog = RemoteStorageDialog(self)
            dialog.exec_()
        except ImportError as e:
            QMessageBox.warning(
                self, "Remote Storage",
                f"Remote storage module not available: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error opening remote storage configuration: {str(e)}"
            )

    def setPathGraphviz(self):
        s = QgsSettings()
        self.graphviz_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.graphviz_bin:
            self.lineEditGraphviz.setText(self.graphviz_bin)
            s.setValue('pyArchInit/graphvizBinPath', self.graphviz_bin)

    def setPathPostgres(self):
        s = QgsSettings()
        self.postgres_bin = QFileDialog.getExistingDirectory(
            self,
            "Set path directory",
            self.HOME,
            QFileDialog.ShowDirsOnly
        )

        if self.postgres_bin:
            self.lineEditPostgres.setText(self.postgres_bin)
            s.setValue('pyArchInit/postgresBinPath', self.postgres_bin)


    def setEnvironPath(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.graphviz_bin)

        if self.L=='it':
            QMessageBox.warning(self, "Imposta variabile ambientale", "Il percorso è stato impostato con successo", QMessageBox.Ok)

        elif self.L=='de':
            QMessageBox.warning(self, "Umweltvariable setzen", "Der Weg wurde erfolgreich eingeschlagen", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def setEnvironPathPostgres(self):
        os.environ['PATH'] += os.pathsep + os.path.normpath(self.postgres_bin)

        if self.L=='it':
            QMessageBox.warning(self, "Imposta variabile ambientale", "Il percorso è stato impostato con successo", QMessageBox.Ok)

        elif self.L=='de':
            QMessageBox.warning(self, "Umweltvariable setzen", "Der Weg wurde erfolgreich eingeschlagen", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Set Environmental Variable", "The path has been set successful", QMessageBox.Ok)
    def set_db_parameter(self):
        # Prevent recursive calls
        if getattr(self, '_setting_parameters', False):
            return
        self._setting_parameters = True

        try:
            if self.comboBox_Database.currentText() == 'postgres':
                self.lineEdit_DBname.setText("pyarchinit")
                self.lineEdit_Host.setText('127.0.0.1')
                self.lineEdit_Port.setText('5432')
                self.lineEdit_User.setText('postgres')

            if self.comboBox_Database.currentText() == 'sqlite':
                self.lineEdit_DBname.setText("pyarchinit_db.sqlite")
                self.lineEdit_Host.setText('')
                self.lineEdit_Password.setText('')
                self.lineEdit_Port.setText('')
                self.lineEdit_User.setText('')
        finally:
            self._setting_parameters = False



    def set_db_import_from_parameter(self):
        #QMessageBox.warning(self, "ok", "entered in read.", QMessageBox.Ok)

        if self.comboBox_server_rd.currentText() == 'postgres':
            
            self.lineEdit_host_rd.setText('localhost')
            self.lineEdit_username_rd.setText('postgres')
            self.lineEdit_database_rd.setText('pyarchinit')
            self.lineEdit_port_rd.setText('5432')

        if self.comboBox_server_rd.currentText() == 'sqlite':
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)

            self.lineEdit_host_rd.setText('')
            self.lineEdit_username_rd.setText('')
            self.lineEdit_pass_rd.setText('')
            self.lineEdit_database_rd.setText('pyarchinit_db.sqlite')
            self.lineEdit_port_rd.setText('')


    def set_db_import_to_parameter(self):
        #QMessageBox.warning(self, "ok", "entered in write", QMessageBox.Ok)
        #self.comboBox_server_wt.clear()
        if self.comboBox_server_wt.currentText() == 'postgres' and not self.comboBox_Database.currentText()=='postgres':
            QMessageBox.warning(self, "Attenzione", "Devi essere connesso\n prima al db di postgres", QMessageBox.Ok)
            self.comboBox_server_wt.clear()

        if self.comboBox_server_wt.currentText() == 'sqlite' and not self.comboBox_Database.currentText()=='sqlite':
            QMessageBox.warning(self, "Attenzione", "Devi essere connesso\n prima al db di sqlite", QMessageBox.Ok)
            self.comboBox_server_wt.clear()

        if self.comboBox_server_wt.currentText() == 'postgres' and self.comboBox_Database.currentText()=='postgres':
            
            self.lineEdit_host_wt.setText(str(self.lineEdit_Host.text()))
            
            self.lineEdit_database_wt.setText(str(self.lineEdit_DBname.text()))
           
            self.lineEdit_username_wt.setText(str(self.lineEdit_User.text()))
            
            self.lineEdit_port_wt.setText(str(self.lineEdit_Port.text()))
            
            self.lineEdit_pass_wt.setText(str(self.lineEdit_Password.text()))

        
        if self.comboBox_server_wt.currentText() == 'sqlite'and self.comboBox_Database.currentText()=='sqlite':
            #QMessageBox.warning(self, "ok", "entered in if", QMessageBox.Ok)
            #self.self.comboBox_server_wt.clear()
            self.lineEdit_host_wt.setText('')
            self.lineEdit_username_wt.setText('')
            self.lineEdit_pass_wt.setText('')
            self.lineEdit_database_wt.setText(str(self.lineEdit_DBname.text()))
            self.lineEdit_port_wt.setText('')

    def load_dict(self):
        path_rel = os.path.join(os.sep, str(self.HOME), 'pyarchinit_DB_folder', 'config.cfg')
        conf = open(path_rel, "r")
        data = conf.read()
        self.PARAMS_DICT = eval(data)
        conf.close()

    def save_dict(self):
        # save data into config.cfg file
        path_rel = os.path.join(os.sep, str(self.HOME), 'pyarchinit_DB_folder', 'config.cfg')
        f = open(path_rel, "w")
        f.write(str(self.PARAMS_DICT))
        f.close()

    def on_pushButton_save_pressed(self):
        self.logger.log("\n=== on_pushButton_save_pressed called ===")

        # Prevent re-entry
        if getattr(self, '_save_in_progress', False):
            self.logger.log("WARNING: Save already in progress, preventing re-entry")
            return

        self._save_in_progress = True
        self.logger.log("Setting _save_in_progress flag")

        # Skip the update if we're coming from database creation
        if not hasattr(self, 'skip_combo_update'):
            self.logger.log("Updating comboBox_Database")
            self.comboBox_Database.update()
        else:
            # Clean up the flag after using it
            self.logger.log("Skipping combo update (skip_combo_update flag set)")
            delattr(self, 'skip_combo_update')

        try:
            if not bool(self.lineEdit_Password.text()) and str(self.comboBox_Database.currentText())=='postgres':
                QMessageBox.warning(self, "INFO", 'non dimenticarti di inserire la password',QMessageBox.Ok)

            else:
                self.PARAMS_DICT['SERVER'] = str(self.comboBox_Database.currentText())
                self.PARAMS_DICT['HOST'] = str(self.lineEdit_Host.text())
                self.PARAMS_DICT['DATABASE'] = str(self.lineEdit_DBname.text())
                self.PARAMS_DICT['PASSWORD'] = str(self.lineEdit_Password.text())
                self.PARAMS_DICT['PORT'] = str(self.lineEdit_Port.text())
                self.PARAMS_DICT['USER'] = str(self.lineEdit_User.text())
                self.PARAMS_DICT['THUMB_PATH'] = str(self.lineEdit_Thumb_path.text())
                self.PARAMS_DICT['THUMB_RESIZE'] = str(self.lineEdit_Thumb_resize.text())
                self.PARAMS_DICT['EXPERIMENTAL'] = str(self.comboBox_experimental.currentText())
                self.PARAMS_DICT['SITE_SET'] = str(self.comboBox_sito.currentText())
                self.PARAMS_DICT['LOGO'] = str(self.lineEdit_logo.text())
                self.logger.log("Saving parameters to dict")
                self.save_dict()
                self.logger.log("Parameters saved")

                if str(self.comboBox_Database.currentText())=='postgres':


                    b=str(self.select_version_sql())

                    a = "90313"

                    if a == b:
                        link = 'https://www.postgresql.org/download/'
                        if self.L=='it':
                            msg =   "Stai utilizzando la versione di Postgres: " + str(b)+". Tale versione è diventata obsoleta e potresti riscontrare degli errori. Aggiorna PostgreSQL ad una versione più recente. <br><a href='%s'>PostgreSQL</a>" %link
                        if self.L=='de':
                            msg =   "Sie benutzen die Postgres-Version: " + str(b)+". Diese Version ist veraltet, und Sie werden möglicherweise einige Fehler finden. Aktualisieren Sie PostgreSQL auf eine neuere Version. <br><a href='%s'>PostgreSQL</a>" %link
                        else:
                            msg = "You are using the Postgres version: " + str(b)+". This version has become obsolete and you may find some errors. Update PostgreSQL to a newer version. <br><a href='%s'>PostgreSQL</a>" %link
                        QMessageBox.information(self, "INFO", msg,QMessageBox.Ok)
                    else:
                        pass
                else:
                    pass


                self.logger.log("Calling try_connection from on_pushButton_save_pressed")
                self.try_connection()
                self.logger.log("try_connection completed successfully")

        except Exception as e:
            self.logger.log_exception("on_pushButton_save_pressed", e)

            if self.L=='it':
                QMessageBox.warning(self, "INFO", "Problema di connessione al db. Controlla i paramatri inseriti", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "INFO", "Db-Verbindungsproblem. Überprüfen Sie die eingegebenen Parameter", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "INFO", "Db connection problem. Check the parameters inserted", QMessageBox.Ok)
        finally:
            # Always clear the save flag
            self._save_in_progress = False
            self.logger.log("Clearing _save_in_progress flag in finally block")
            self.logger.log("on_pushButton_save_pressed completed")
    def compare(self):
        if self.comboBox_server_wt.currentText() == 'sqlite':

            if platform.system() == "Windows":
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'sqldiff.exe')
            elif platform.system() == "Darwin":
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'sqldiff_osx')
            else:
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'sqldiff_linux')

            db1 = os.path.join(os.sep, self.HOME, 'bin', 'pyarchinit.sqlite')
            db2 = os.path.join(os.sep, self.HOME, 'pyarchinit_DB_folder', self.lineEdit_DBname.text())

            # text_ = cmd, self.comboBox_compare.currentText(), db1 + ' ', db2
            # result = subprocess.check_output([text_], stderr=subprocess.STDOUT)
            os.system("start cmd /k" + cmd + ' ' + self.comboBox_compare.currentText() + ' ' + db1 + ' ' + db2)
            # if result == b'':
            #
            #     pass
            # else:
            #     QMessageBox.warning(self, "Attenzione",
            #                         "Il db non allineato devi aggiornarlo. Chiudi questa finestra e clicca il bottone con l'icona di spatialite in basso a sinistra aggiungendo l'epsg del tuo db",
            #                         QMessageBox.Ok)
            #     # # #break

        else:
            pass

    def on_pushButton_crea_database_pressed(self,):
        # Check if user is admin
        if not self.check_if_admin():
            QMessageBox.warning(self, "Permessi",
                "Solo gli amministratori possono creare database.",
                QMessageBox.Ok)
            return
        self.logger.log("\n=== on_pushButton_crea_database_pressed called ===")

        # Prevent re-entry if we're already creating a database
        if hasattr(self, 'creating_database') and self.creating_database:
            self.logger.log("WARNING: Database creation already in progress, preventing re-entry")
            if self.L == 'it':
                QMessageBox.warning(self, "Attenzione", "Creazione database già in corso...", QMessageBox.Ok)
            elif self.L == 'de':
                QMessageBox.warning(self, "Achtung", "Datenbankerstellung bereits im Gange...", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Warning", "Database creation already in progress...", QMessageBox.Ok)
            return

        self.creating_database = True
        self.logger.log("Setting creating_database flag")

        schema_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit_schema_updated.sql')
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'create_view_updated.sql')
        trigger_file = os.path.join(os.path.dirname(__file__), os.pardir, 'sql',
                                   'create_activity_triggers.sql')

        if not bool(self.lineEdit_db_passwd.text()):
            self.creating_database = False  # Clear flag if password missing
            QMessageBox.warning(self, "INFO", "Non dimenticarti di inserire la password", QMessageBox.Ok)
        else:

            # Temporarily suppress SQLAlchemy URL deprecation warnings
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*Calling URL.*")
                warnings.filterwarnings("ignore", category=DeprecationWarning)

                create_database = CreateDatabase(self.lineEdit_dbname.text(), self.lineEdit_db_host.text(),
                                                 self.lineEdit_port_db.text(), self.lineEdit_db_user.text(),
                                                 self.lineEdit_db_passwd.text())

                ok, db_url = create_database.createdb()


            if ok:
                try:
                    RestoreSchema(db_url, schema_file).restore_schema()
                except Exception as e:
                    # Clear the creating flag on error
                    self.creating_database = False
                    if self.L=='it':
                        QMessageBox.warning(self, "INFO", "Devi essere superutente per creare un db. Vedi l'errore seguente: " + str(e), QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "INFO", "Sie müssen Superuser sein, um eine Db anzulegen. Siehe folgenden Fehler: " + str(e), QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "INFO", "You have to be super user to create a db. See the following error: " + str(e), QMessageBox.Ok)
                    try:
                        DropDatabase(db_url).dropdb()
                    except:
                        pass  # Don't fail if drop doesn't work
                    ok = False
                    return  # Exit the function, don't re-raise

            if ok:
                crsid = self.selectorCrsWidget.crs().authid()
                srid = crsid.split(':')[1]

                res = RestoreSchema(db_url).update_geom_srid('public', srid)

                # create views
                try:
                    RestoreSchema(db_url, view_file).restore_schema()
                except Exception as e:
                    # Log the view creation error but don't fail the entire process
                    if self.L=='it':
                        QMessageBox.warning(self, "ATTENZIONE", "Database creato ma le viste non sono state create. Errore: " + str(e)[:200], QMessageBox.Ok)
                    elif self.L=='de':
                        QMessageBox.warning(self, "ACHTUNG", "Datenbank erstellt, aber Ansichten wurden nicht erstellt. Fehler: " + str(e)[:200], QMessageBox.Ok)
                    else:
                        QMessageBox.warning(self, "WARNING", "Database created but views were not created. Error: " + str(e)[:200], QMessageBox.Ok)
                    # Continue anyway, the database is created

                # create activity tracking triggers
                try:
                    if os.path.exists(trigger_file):
                        RestoreSchema(db_url, trigger_file).restore_schema()
                        self.logger.log("Activity tracking triggers created successfully")
                except Exception as e:
                    # Log the trigger creation error but don't fail the entire process
                    self.logger.log(f"Warning: Activity triggers not created: {str(e)[:200]}")
                    # This is non-critical, don't show a warning to the user

                #set owner
                # Don't change owner if user is a PostgreSQL admin (postgres or postgres.xxx for Supabase)
                db_user = self.lineEdit_db_user.text()
                if not (db_user == 'postgres' or db_user.startswith('postgres.')):
                    try:
                        RestoreSchema(db_url).set_owner(db_user)
                    except:
                        pass  # Non-critical error, continue

            if ok and res:
                if self.L=='it':
                    msg = QMessageBox.warning(self, 'INFO', 'Installazione avvenuta con successo, vuoi connetterti al nuovo DB?',
                                              QMessageBox.Ok | QMessageBox.Cancel)
                elif self.L=='de':
                    msg = QMessageBox.warning(self, 'INFO', 'Erfolgreiche Installation, möchten Sie sich mit der neuen Datenbank verbinden?',
                                              QMessageBox.Ok | QMessageBox.Cancel)
                else:
                    msg = QMessageBox.warning(self, 'INFO', 'Successful installation, do you want to connect to the new DB?',
                                              QMessageBox.Ok | QMessageBox.Cancel)

                if msg == QMessageBox.Ok:
                    # Add a small delay to ensure database is ready
                    from PyQt5.QtCore import QTimer
                    # Temporarily disconnect ALL signals to avoid any interference
                    try:
                        self.comboBox_Database.currentIndexChanged.disconnect()
                    except:
                        pass

                    # Store the new database name before changing combobox
                    new_db_name = self.lineEdit_dbname.text()

                    # Set database type to postgres without triggering signals
                    self.comboBox_Database.setCurrentText('postgres')

                    # Set the connection parameters from the creation dialog
                    # IMPORTANT: Set these BEFORE reconnecting any signals
                    self.lineEdit_Host.setText(self.lineEdit_db_host.text())
                    self.lineEdit_DBname.setText(new_db_name)  # Use stored name to ensure it's not lost
                    self.lineEdit_Port.setText(self.lineEdit_port_db.text())
                    self.lineEdit_User.setText(self.lineEdit_db_user.text())
                    self.lineEdit_Password.setText(self.lineEdit_db_passwd.text())

                    # Reconnect ONLY the essential signals (not set_db_parameter yet)
                    self.comboBox_Database.currentIndexChanged.connect(self.db_active)
                    self.comboBox_Database.currentIndexChanged.connect(self.customize)

                    # Define a function to reconnect set_db_parameter after successful connection
                    def reconnect_set_db_parameter():
                        try:
                            self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                        except:
                            pass

                    # Store the function to call it after successful connection
                    self.reconnect_set_db_param_func = reconnect_set_db_parameter

                    # Set a flag to skip the comboBox update in on_pushButton_save_pressed
                    self.skip_combo_update = True

                    # Clear the creating flag before attempting connection
                    self.creating_database = False

                    # Use QTimer to delay the connection attempt by 1000ms (give more time for DB to be ready)
                    QTimer.singleShot(1000, self.on_pushButton_save_pressed)
                else:
                    # User cancelled, clear the creating flag
                    self.creating_database = False
            else:
                # Database already exists, clear the creating flag
                self.creating_database = False
                if self.L=='it':
                    QMessageBox.warning(self, "INFO", "Database esistente", QMessageBox.Ok)
                elif self.L=='de':
                    QMessageBox.warning(self, "INFO", "die Datenbank existiert", QMessageBox.Ok)
                else:
                    QMessageBox.warning(self, "INFO", "The DB exist already", QMessageBox.Ok)
    def select_version_sql(self):
        conn = Connection()
        db_url = conn.conn_str()
        sql_query_string = "SELECT current_setting('server_version_num')"
        self.engine= create_engine(db_url)
        res = self.engine.execute(sql_query_string)
        rows= res.fetchone()
        vers = ''.join(rows)
        res.close()#QMessageBox.information(self, "INFO", str(vers),QMessageBox.Ok)
        return vers

    def on_pushButton_upd_postgres_pressed(self):
        # Check if user is admin
        if not self.check_if_admin():
            QMessageBox.warning(self, "Permessi",
                "Solo gli amministratori possono eseguire backup del database.",
                QMessageBox.Ok)
            return

        conn = Connection()
        db_url = conn.conn_str()
        view_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                       'pyarchinit_update_postgres.sql')

        b=str(self.select_version_sql())

        a = "90313"
        if self.L== 'it':
            if a == b:
                QMessageBox.information(self, "INFO", " Non puoi aggiornare il db postgres per chè la tua versione è inferiore alla 9.4 "
                                                                                "Aggiorna ad una versione più recente",QMessageBox.Ok)
            else:
                RestoreSchema(db_url,view_file).restore_schema()

                QMessageBox.information(self, "INFO", "il db è stato aggiornato", QMessageBox.Ok)
        elif self.L== 'de':
            if a == b:
                QMessageBox.information(self, "INFO", " Sie können die db postgres nicht aktualisieren, da Ihre Version niedriger als 9.4 ist. "
                                                                                "Upgrade auf eine neuere Version",QMessageBox.Ok)
            else:
                RestoreSchema(db_url,view_file).restore_schema()

                QMessageBox.information(self, "INFO", "die db wurde aktualisiert", QMessageBox.Ok)
        else:
            if a == b:
                QMessageBox.information(self, "INFO", " You cannot update the db postgres because your version is lower than 9.4 "
                                                                                "Upgrade to a newer version",QMessageBox.Ok)
            else:
                RestoreSchema(db_url,view_file).restore_schema()

                QMessageBox.information(self, "INFO", "the db has been updated", QMessageBox.Ok)



    def load_spatialite(self,dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)

        if Pyarchinit_OS_Utility.isWindows()== True:
            dbapi_conn.load_extension('mod_spatialite.dll')

        elif Pyarchinit_OS_Utility.isMac()== True:
            dbapi_conn.load_extension('mod_spatialite.so')
        else:
            dbapi_conn.load_extension('mod_spatialite.so')

    def on_pushButton_upd_sqlite_pressed(self):
        # Check if user is admin
        if not self.check_if_admin():
            QMessageBox.warning(self, "Permessi",
                "Solo gli amministratori possono eseguire backup del database.",
                QMessageBox.Ok)
            return


        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        conn = Connection()
        db_url = conn.conn_str()

        try:
            engine = create_engine(db_url, echo=True)

            listen(engine, 'connect', self.load_spatialite)
            c = engine.connect()
            
            
            py3_usm='''CREATE TABLE IF NOT EXISTS pyarchinit_quote_usm (
                    gid               INTEGER                  NOT NULL
                                                               PRIMARY KEY AUTOINCREMENT,
                    sito_q            TEXT,
                    area_q            INTEGER,
                    us_q              INTEGER,
                    unita_misu_q      TEXT,
                    quota_q           [DOUBLE PRECISION],
                    data              TEXT,
                    disegnatore       TEXT,
                    rilievo_originale TEXT
                );'''
            c.execute(py3_usm)
            
            sql_pyus_geom = """select AddGeometryColumn('pyarchinit_quote_usm', 'the_geom',"""+ self.lineEdit_crs.text()+""" ,'POINT', 'XY');"""
            c.execute(sql_pyus_geom)
            
            sql_pyus_geom_spatial =""" select CreateSpatialIndex('pyarchinit_quote_usm', 'the_geom');"""
            c.execute(sql_pyus_geom_spatial)
                
            
            py8='''DROP VIEW if exists pyarchinit_quote_usm_view;'''
            c.execute(py8)
            py9='''    CREATE VIEW if not exists pyarchinit_quote_usm_view AS
                    SELECT a.rowid AS rowid,
                           a.id_us AS id_us,
                           a.sito AS sito,
                           a.area AS area,
                           a.us AS us,
                           a.d_stratigrafica AS d_stratigrafica,
                           a.d_interpretativa AS d_interpretativa,
                           a.descrizione AS descrizione,
                           a.interpretazione AS interpretazione,
                           a.periodo_iniziale AS periodo_iniziale,
                           a.fase_iniziale AS fase_iniziale,
                           a.periodo_finale AS periodo_finale,
                           a.fase_finale AS fase_finale,
                           a.scavato AS scavato,
                           a.attivita AS attivita,
                           a.anno_scavo AS anno_scavo,
                           a.metodo_di_scavo AS metodo_di_scavo,
                           a.inclusi AS inclusi,
                           a.campioni AS campioni,
                           a.rapporti AS rapporti,
                           a.data_schedatura AS data_schedatura,
                           a.schedatore AS schedatore,
                           a.formazione AS formazione,
                           a.stato_di_conservazione AS stato_di_conservazione,
                           a.colore AS colore,
                           a.consistenza AS consistenza,
                           a.struttura AS struttura,
                           a.cont_per AS cont_per,
                           a.order_layer AS order_layer,
                           a.documentazione AS documentazione,
                           b.rowid AS rowid_1,
                           b.sito_q AS sito_q,
                           b.area_q AS area_q,
                           b.us_q AS us_q,
                           b.unita_misu_q AS unita_misu_q,
                           b.quota_q AS quota_q,
                           b.data AS data,
                           b.disegnatore AS disegnatore,
                           b.rilievo_originale AS rilievo_originale,
                           b.the_geom AS the_geom
                      FROM us_table AS a
                           JOIN
                           pyarchinit_quote_usm AS b ON (a.sito = b.sito_q AND 
                                                     a.area = b.area_q AND 
                                                     a.us = b.us_q) 
                     ORDER BY a.order_layer DESC;'''
            c.execute(py9)
            
            try:
                sql_view_py10= ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('pyarchinit_quote_usm_view', 'the_geom', 'rowid', 'pyarchinit_quote_usm', 'the_geom',0)""")
           
                
                c.execute(sql_view_py10)
            except:
                pass
            
            
            
            py8='''DROP VIEW if exists pyarchinit_quote_view;'''
            c.execute(py8)
            py9='''    CREATE VIEW if not exists pyarchinit_quote_view AS
                    SELECT a.rowid AS rowid,
                           a.id_us AS id_us,
                           a.sito AS sito,
                           a.area AS area,
                           a.us AS us,
                           a.d_stratigrafica AS d_stratigrafica,
                           a.d_interpretativa AS d_interpretativa,
                           a.descrizione AS descrizione,
                           a.interpretazione AS interpretazione,
                           a.periodo_iniziale AS periodo_iniziale,
                           a.fase_iniziale AS fase_iniziale,
                           a.periodo_finale AS periodo_finale,
                           a.fase_finale AS fase_finale,
                           a.scavato AS scavato,
                           a.attivita AS attivita,
                           a.anno_scavo AS anno_scavo,
                           a.metodo_di_scavo AS metodo_di_scavo,
                           a.inclusi AS inclusi,
                           a.campioni AS campioni,
                           a.rapporti AS rapporti,
                           a.data_schedatura AS data_schedatura,
                           a.schedatore AS schedatore,
                           a.formazione AS formazione,
                           a.stato_di_conservazione AS stato_di_conservazione,
                           a.colore AS colore,
                           a.consistenza AS consistenza,
                           a.struttura AS struttura,
                           a.cont_per AS cont_per,
                           a.order_layer AS order_layer,
                           a.documentazione AS documentazione,
                           b.rowid AS rowid_1,
                           b.sito_q AS sito_q,
                           b.area_q AS area_q,
                           b.us_q AS us_q,
                           b.unita_misu_q AS unita_misu_q,
                           b.quota_q AS quota_q,
                           b.data AS data,
                           b.disegnatore AS disegnatore,
                           b.rilievo_originale AS rilievo_originale,
                           b.the_geom AS the_geom
                      FROM us_table AS a
                           JOIN
                           pyarchinit_quote AS b ON (a.sito = b.sito_q AND 
                                                     a.area = b.area_q AND 
                                                     a.us = b.us_q) 
                     ORDER BY a.order_layer DESC;'''
            c.execute(py9)
            
            try:
                sql_view_py10= ("""INSERT OR REPLACE INTO views_geometry_columns
                    (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                    VALUES ('pyarchinit_quote_view', 'the_geom', 'rowid', 'pyarchinit_quote', 'the_geom',0)""")
           
                
                c.execute(sql_view_py10)
            except:
                pass
            
            
            sql_trigger_coord1="""CREATE TRIGGER IF NOT EXISTS create_geom_insert 
                After insert 
                ON pyunitastratigrafiche 

                BEGIN 
                
                update pyunitastratigrafiche set coord = ST_AsText(ST_Centroid(the_geom)) where scavo_s=New.scavo_s and area_s=New.area_s and us_s=New.us_s; 
                
                END;"""
            c.execute(sql_trigger_coord1)
            
            sql_drop_trigger="""Drop trigger if exists create_geom_update"""
            c.execute(sql_drop_trigger)
            
            
            sql_trigger_coord3="""CREATE TRIGGER IF NOT EXISTS create_geom_update 
                After update 
                ON pyunitastratigrafiche 

                BEGIN 
                
                update pyunitastratigrafiche set coord = ST_AsText(ST_Centroid(the_geom)) where gid = New.gid and scavo_s=New.scavo_s and area_s=New.area_s and us_s=New.us_s;
                
                END;"""
            c.execute(sql_trigger_coord3)
            # ################################################################
            sql_alter_table_us=(
            """CREATE TABLE if not exists pyunitastratigrafiche_usm (
            "gid" integer PRIMARY KEY AUTOINCREMENT,
            "area_s" integer,
            "scavo_s" text,
            "us_s" integer,            
            "stratigraph_index_us" integer,
            "tipo_us_s" text,
            "rilievo_originale" text,
            "disegnatore" text,
            "data" date,
            "tipo_doc" text,
            "nome_doc" text,
            "coord" text); """ )
            c.execute(sql_alter_table_us)
            sql_pyus_geom = """ select AddGeometryColumn('pyunitastratigrafiche_usm', 'the_geom',"""+ self.lineEdit_crs.text()+""" ,'MULTIPOLYGON', 'XY'); """
            c.execute(sql_pyus_geom)
            sql_pyus_geom_spatial =""" select CreateSpatialIndex('pyunitastratigrafiche_usm', 'the_geom');"""
            c.execute(sql_pyus_geom_spatial)
        
        
            py8='''DROP VIEW if exists pyarchinit_usm_view;'''
            c.execute(py8)
            sql_view_us=("""CREATE VIEW  IF NOT EXISTS "pyarchinit_usm_view" AS            
            SELECT "a"."rowid" AS "rowid", "a"."gid" AS "gid", "a"."area_s" AS "area_s",
            "a"."scavo_s" AS "scavo_s", "a"."us_s" AS "us_s",
            "a"."stratigraph_index_us" AS "stratigraph_index_us",
            "a"."tipo_us_s" AS "tipo_us_s", "a"."rilievo_originale" AS "rilievo_originale",
            "a"."disegnatore" AS "disegnatore", "a"."data" AS "data",
            "a"."the_geom" AS "the_geom", "a"."tipo_doc" AS "tipo_doc",
            "a"."nome_doc" AS "nome_doc", "b"."id_us" AS "id_us", "b"."sito" AS "sito", "b"."area" AS "area",
            "b"."us" AS "us", "b"."d_stratigrafica" AS "d_stratigrafica",
            "b"."d_interpretativa" AS "d_interpretativa", "b"."descrizione" AS "descrizione",
            "b"."interpretazione" AS "interpretazione", "b"."periodo_iniziale" AS "periodo_iniziale",
            "b"."fase_iniziale" AS "fase_iniziale", "b"."periodo_finale" AS "periodo_finale",
            "b"."fase_finale" AS "fase_finale", "b"."scavato" AS "scavato",
            "b"."attivita" AS "attivita", "b"."anno_scavo" AS "anno_scavo",
            "b"."metodo_di_scavo" AS "metodo_di_scavo", "b"."inclusi" AS "inclusi",
            "b"."campioni" AS "campioni", "b"."rapporti" AS "rapporti",
            "b"."data_schedatura" AS "data_schedatura", "b"."schedatore" AS "schedatore",
            "b"."formazione" AS "formazione", "b"."stato_di_conservazione" AS "stato_di_conservazione",
            "b"."colore" AS "colore", "b"."consistenza" AS "consistenza",
            "b"."struttura" AS "struttura", "b"."cont_per" AS "cont_per",
            "b"."order_layer" AS "order_layer", "b"."documentazione" AS "documentazione",
            "b"."unita_tipo" AS "unita_tipo", "b"."settore" AS "settore",
            "b"."quad_par" AS "quad_par", "b"."ambient" AS "ambient",
            "b"."saggio" AS "saggio", "b"."elem_datanti" AS "elem_datanti",
            "b"."funz_statica" AS "funz_statica", "b"."lavorazione" AS "lavorazione",
            "b"."spess_giunti" AS "spess_giunti", "b"."letti_posa" AS "letti_posa",
            "b"."alt_mod" AS "alt_mod", "b"."un_ed_riass" AS "un_ed_riass",
            "b"."reimp" AS "reimp", "b"."posa_opera" AS "posa_opera",
            "b"."quota_min_usm" AS "quota_min_usm", "b"."quota_max_usm" AS "quota_max_usm",
            "b"."cons_legante" AS "cons_legante", "b"."col_legante" AS "col_legante",
            "b"."aggreg_legante" AS "aggreg_legante", "b"."con_text_mat" AS "con_text_mat",
            "b"."col_materiale" AS "col_materiale", "b"."inclusi_materiali_usm" AS "inclusi_materiali_usm",
            "b"."n_catalogo_generale" AS "n_catalogo_generale",
            "b"."n_catalogo_interno" AS "n_catalogo_interno",
            "b"."n_catalogo_internazionale" AS "n_catalogo_internazionale",
            "b"."soprintendenza" AS "soprintendenza", "b"."quota_relativa" AS "quota_relativa",
            "b"."quota_abs" AS "quota_abs", "b"."ref_tm" AS "ref_tm",
            "b"."ref_ra" AS "ref_ra", "b"."ref_n" AS "ref_n",
            "b"."posizione" AS "posizione", "b"."criteri_distinzione" AS "criteri_distinzione",
            "b"."modo_formazione" AS "modo_formazione", "b"."componenti_organici" AS "componenti_organici",
            "b"."componenti_inorganici" AS "componenti_inorganici",
            "b"."lunghezza_max" AS "lunghezza_max", "b"."altezza_max" AS "altezza_max",
            "b"."altezza_min" AS "altezza_min", "b"."profondita_max" AS "profondita_max",
            "b"."profondita_min" AS "profondita_min", "b"."larghezza_media" AS "larghezza_media",
            "b"."quota_max_abs" AS "quota_max_abs", "b"."quota_max_rel" AS "quota_max_rel",
            "b"."quota_min_abs" AS "quota_min_abs", "b"."quota_min_rel" AS "quota_min_rel",
            "b"."osservazioni" AS "osservazioni", "b"."datazione" AS "datazione",
            "b"."flottazione" AS "flottazione", "b"."setacciatura" AS "setacciatura",
            "b"."affidabilita" AS "affidabilita", "b"."direttore_us" AS "direttore_us",
            "b"."responsabile_us" AS "responsabile_us", "b"."cod_ente_schedatore" AS "cod_ente_schedatore",
            "b"."data_rilevazione" AS "data_rilevazione", "b"."data_rielaborazione" AS "data_rielaborazione",
            "b"."lunghezza_usm" AS "lunghezza_usm", "b"."altezza_usm" AS "altezza_usm",
            "b"."spessore_usm" AS "spessore_usm", "b"."tecnica_muraria_usm" AS "tecnica_muraria_usm",
            "b"."modulo_usm" AS "modulo_usm", "b"."campioni_malta_usm" AS "campioni_malta_usm",
            "b"."campioni_mattone_usm" AS "campioni_mattone_usm",
            "b"."campioni_pietra_usm" AS "campioni_pietra_usm",
            "b"."provenienza_materiali_usm" AS "provenienza_materiali_usm",
            "b"."criteri_distinzione_usm" AS "criteri_distinzione_usm",
            "b"."uso_primario_usm" AS "uso_primario_usm"
            FROM "pyunitastratigrafiche_usm" AS "a"
            JOIN "us_table" AS "b" ON ("a"."area_s" = "b"."area" AND "a"."scavo_s" = "b"."sito"
            AND "a"."us_s" = "b"."us")
            ORDER BY "b"."order_layer" asc ;""")


            c.execute(sql_view_us)
            try:
                sql_view_us_geom= """INSERT OR REPLACE INTO views_geometry_columns
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                        VALUES ('pyarchinit_usm_view', 'the_geom', 'rowid', 'pyunitastratigrafiche_usm', 'the_geom',0)"""
                c.execute(sql_view_us_geom)
            except:
                pass
            py8='''DROP VIEW if exists pyarchinit_us_view;'''
            c.execute(py8)
            sql_view_us=("""CREATE VIEW  IF NOT EXISTS "pyarchinit_us_view" AS
            SELECT 
                a.gid,
                a.the_geom,
                a.tipo_us_s,
                a.scavo_s,
                a.area_s,
                a.us_s,
                a.stratigraph_index_us,
                b.id_us,
                b.sito,
                b.area,
                b.us,
                b.struttura,
                b.d_stratigrafica,
                b.d_interpretativa,
                b.descrizione,
                b.interpretazione,
                b.rapporti,
                b.periodo_iniziale,
                b.fase_iniziale,
                b.periodo_finale,
                b.fase_finale,
                b.anno_scavo
            FROM pyunitastratigrafiche AS a
            JOIN us_table AS b ON (a.area_s = b.area AND a.scavo_s = b.sito AND a.us_s = b.us)
            ORDER BY b.order_layer ASC;""")


            c.execute(sql_view_us)
            try:
                sql_view_us_geom= """INSERT OR REPLACE INTO views_geometry_columns
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column,read_only)
                        VALUES ('pyarchinit_us_view', 'the_geom', 'rowid', 'pyunitastratigrafiche', 'the_geom',0)"""
                c.execute(sql_view_us_geom)
            except:
                pass
            RestoreSchema(db_url,None).update_geom_srid_sl('%d' % int(self.lineEdit_crs.text()))
            c.close()
            QMessageBox.warning(self, "Message", "Update Done", QMessageBox.Ok)



        except Exception as e:
            QMessageBox.warning(self, "Update error", str(e), QMessageBox.Ok)



    def on_pushButton_crea_database_sl_pressed(self):

        self.comboBox_sito.clear()
        db_file = os.path.join(os.path.dirname(__file__), os.pardir, 'resources', 'dbfiles',
                                   'pyarchinit.sqlite')

        home_DB_path = '{}{}{}'.format(self.HOME, os.sep, 'pyarchinit_DB_folder')

        sl_name = '{}.sqlite'.format(self.lineEdit_dbname_sl.text())
        db_path = os.path.join(home_DB_path, sl_name)

        ok = False
        if not os.path.exists(db_path):
            Pyarchinit_OS_Utility().copy_file(db_file, db_path)
            ok = True

        if ok:
            crsid = self.selectorCrsWidget_sl.crs().authid()
            srid = crsid.split(':')[1]

            db_url = 'sqlite:///{}'.format(db_path)
            res = RestoreSchema(db_url).update_geom_srid_sl(srid)

        if ok and res:
            if self.L=='it':
                msg = QMessageBox.warning(self, 'INFO', 'Installazione avvenuta con successo, vuoi connetterti al nuovo DB?', QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Ok:
                    self.comboBox_Database.setCurrentText('sqlite')
                    self.lineEdit_DBname.setText(sl_name)
                    self.on_pushButton_save_pressed()

            elif self.L=='de':
                msg = QMessageBox.warning(self, 'INFO', 'Erfolgreiche Installation, möchten Sie sich mit der neuen Datenbank verbinden?', QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Ok:
                    self.comboBox_Database.setCurrentText('sqlite')
                    self.lineEdit_DBname.setText(sl_name)
                    self.on_pushButton_save_pressed()
            else:
                msg = QMessageBox.warning(self, 'INFO', 'Successful installation, do you want to connect to the new DB?', QMessageBox.Ok | QMessageBox.Cancel)
                if msg == QMessageBox.Ok:
                    self.comboBox_Database.setCurrentText('sqlite')
                    self.lineEdit_DBname.setText(sl_name)
                    self.on_pushButton_save_pressed()
        else:
            if self.L=='it':
                QMessageBox.warning(self, "INFO", "Database esistente", QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "INFO", "die Datenbank existiert", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "INFO", "The Database exsist already", QMessageBox.Ok)





    def try_connection(self):
        # Add file-based logging
        self.logger.log("\n=== try_connection called ===")

        # Log stack trace to understand call hierarchy
        stack = traceback.format_stack()
        for i, frame in enumerate(stack[-5:-1]):
            self.logger.log(f"Stack frame {i}: {frame.strip()}")

        # Check if we're in a loop
        if hasattr(self, '_connection_in_progress') and self._connection_in_progress:
            self.logger.log("WARNING: Connection already in progress, preventing loop")
            # Don't show message box here as it can cause event loops
            return

        self._connection_in_progress = True
        self.logger.log("Setting _connection_in_progress flag to True")

        # Temporarily disconnect all comboBox_Database signals to prevent loops
        self.logger.log("Disconnecting comboBox_Database signals temporarily")
        try:
            self.comboBox_Database.currentIndexChanged.disconnect()
        except:
            self.logger.log("No signals to disconnect")
            pass

        test = False  # Default to failed connection
        try:
            self.logger.log("Calling self.summary()")
            self.summary()

            self.logger.log("Creating Connection object")
            conn = Connection()
            conn_str = conn.conn_str()
            self.logger.log(f"Connection string: {conn_str}")

            self.logger.log("Creating DB_MANAGER")
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)

            self.logger.log("Calling DB_MANAGER.connection()")
            test = self.DB_MANAGER.connection()
            self.logger.log(f"Connection test result: {test}")
        except Exception as e:
            self.logger.log_exception("try_connection", e)
            test = False
        finally:
            # Always reset the flag
            self._connection_in_progress = False
            self.logger.log("Setting _connection_in_progress flag to False in finally block")

            # Reconnect the signals after connection attempt
            self.logger.log("Reconnecting comboBox_Database signals")
            try:
                self.comboBox_Database.currentIndexChanged.connect(self.db_active)
                self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                self.comboBox_Database.currentIndexChanged.connect(self.customize)
                self.logger.log("Signals reconnected successfully")
            except Exception as e:
                self.logger.log(f"Error reconnecting signals: {e}")

        # Apply database fixes for existing databases
        if test and self.comboBox_Database.currentText() == 'postgres':
            try:
                # Fix thesaurus sigla field length if needed
                self.logger.log("Checking and fixing thesaurus sigla field length")
                engine = self.DB_MANAGER.engine
                with engine.connect() as conn:
                    # Check current column type
                    result = conn.execute(text("""
                        SELECT character_maximum_length
                        FROM information_schema.columns
                        WHERE table_name = 'pyarchinit_thesaurus_sigle'
                        AND column_name = 'sigla'
                    """))
                    row = result.fetchone()
                    if row and row[0] and row[0] < 100:
                        self.logger.log(f"Fixing sigla field length from {row[0]} to 255")
                        conn.execute(text("""
                            ALTER TABLE pyarchinit_thesaurus_sigle
                            ALTER COLUMN sigla TYPE character varying(255)
                        """))
                        conn.commit()
                        self.logger.log("Sigla field length fixed successfully")
            except Exception as e:
                self.logger.log(f"Could not apply sigla field fix: {e}")
                # Don't fail connection if fix doesn't apply

        if self.L=='it':
            if test:
                QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
                # Reconnect set_db_parameter after successful connection
                if hasattr(self, 'reconnect_set_db_param_func'):
                    self.reconnect_set_db_param_func()
                    delattr(self, 'reconnect_set_db_param_func')

                # Save current user to settings for admin checks
                self.save_current_user_to_settings()

                # Setup admin features after successful connection
                self.setup_admin_features()

                pass  # Flag already cleared in finally block
            else:
                # Only update combo if not in creation flow
                if not hasattr(self, 'skip_combo_update'):
                    self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)
        elif self.L=='de':
            if test:
                QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
                # Reconnect set_db_parameter after successful connection
                if hasattr(self, 'reconnect_set_db_param_func'):
                    self.reconnect_set_db_param_func()
                    delattr(self, 'reconnect_set_db_param_func')

                # Save current user to settings for admin checks
                self.save_current_user_to_settings()

                # Setup admin features after successful connection
                self.setup_admin_features()

                pass  # Flag already cleared in finally block
            else:
                # Only update combo if not in creation flow
                if not hasattr(self, 'skip_combo_update'):
                    self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)

        else:
            if test:
                QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
                # Reconnect set_db_parameter after successful connection
                if hasattr(self, 'reconnect_set_db_param_func'):
                    self.reconnect_set_db_param_func()
                    delattr(self, 'reconnect_set_db_param_func')

                # Save current user to settings for admin checks
                self.save_current_user_to_settings()

                # Setup admin features after successful connection
                self.setup_admin_features()

                pass  # Flag already cleared in finally block
            else:
                # Only update combo if not in creation flow
                if not hasattr(self, 'skip_combo_update'):
                    self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    #self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    #self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)

    def save_current_user_to_settings(self):
        """Save current database username to settings for admin checks"""
        try:
            s = QgsSettings()
            # Get the username from UI field
            username = self.lineEdit_User.text() if hasattr(self, 'lineEdit_User') else ''

            if username:
                s.setValue('pyArchInit/current_user', username)
                print(f"Saved current user to settings: {username}")

                # Also try to get the database username for reference
                if hasattr(self, 'DB_MANAGER') and self.DB_MANAGER:
                    try:
                        query = "SELECT current_user"
                        result = self.DB_MANAGER.execute_sql(query)
                        if result and result[0][0]:
                            db_username = result[0][0]
                            s.setValue('pyArchInit/db_username', db_username)
                            print(f"Saved DB username to settings: {db_username}")
                    except:
                        pass

                    # Update last_login in pyarchinit_users table
                    try:
                        if self.comboBox_Database.currentText() == 'postgres':
                            update_login = f"UPDATE pyarchinit_users SET last_login = CURRENT_TIMESTAMP WHERE LOWER(username) = LOWER('{username}')"
                            self.DB_MANAGER.execute_sql(update_login)
                            print(f"Updated last_login for user: {username}")
                    except Exception as e:
                        print(f"Could not update last_login: {e}")

        except Exception as e:
            print(f"Error saving current user to settings: {e}")

    def connection_up(self):
        self.summary()

        conn = Connection()
        conn_str = conn.conn_str()

        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        test = self.DB_MANAGER.connection()

        if self.L == 'it':
            if test:
                #QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    # self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    # self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                #self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)
        elif self.L == 'de':
            if test:
                #QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                #self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    # self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    # self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                #self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)

        else:
            if test:
                #QMessageBox.information(self, "Messaggio", "Connessione avvenuta con successo", QMessageBox.Ok)
                self.pushButton_upd_postgres.setEnabled(False)
                self.pushButton_upd_sqlite.setEnabled(True)
            else:
                self.comboBox_Database.update()
                self.comboBox_sito.clear()
                if self.comboBox_Database.currentText() == 'sqlite':
                    # self.comboBox_Database.editTextChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(True)
                    self.pushButton_upd_postgres.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(True)
                elif self.comboBox_Database.currentText() == 'postgres':
                    # self.comboBox_Database.currentIndexChanged.connect(self.set_db_parameter)
                    self.toolButton_db.setEnabled(False)
                    self.pushButton_upd_sqlite.setEnabled(False)
                    self.pushButton_upd_postgres.setEnabled(True)
                #self.comboBox_sito.clear()

                QMessageBox.warning(self, "Alert", "Errore di connessione: <br>" +
                                    "Cambia i parametri e riprova a connetterti. Oppure aggiorna il database con l'apposita funzione che trovi in basso a sinistra",
                                    QMessageBox.Ok)


    def charge_data(self):
        # load data from config.cfg file
        
            
        self.comboBox_Database.setCurrentText(self.PARAMS_DICT['SERVER'])
        self.lineEdit_Host.setText(self.PARAMS_DICT['HOST'])
        self.lineEdit_DBname.setText(self.PARAMS_DICT['DATABASE'])
        self.lineEdit_Password.setText(self.PARAMS_DICT['PASSWORD'])
        self.lineEdit_Port.setText(self.PARAMS_DICT['PORT'])
        self.lineEdit_User.setText(self.PARAMS_DICT['USER'])
        self.lineEdit_Thumb_path.setText(self.PARAMS_DICT['THUMB_PATH'])
        self.lineEdit_Thumb_resize.setText(self.PARAMS_DICT['THUMB_RESIZE'])
        
        try:
            self.comboBox_experimental.setEditText(self.PARAMS_DICT['EXPERIMENTAL'])
        except:
            self.comboBox_experimental.setEditText("No")
        self.comboBox_sito.setCurrentText(self.PARAMS_DICT['SITE_SET'])    ###############
        self.lineEdit_logo.setText(self.PARAMS_DICT['LOGO'])
    def test_def(self):
        pass

    def on_toolButton_active_toggled(self):



        if self.L=='it':
            if self.toolButton_active.isChecked():
                
                QMessageBox.information(self, "Pyarchinit", "Sistema query attivato. Seleziona un sito e clicca su salva parametri", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "Pyarchinit", "Sistema query disattivato", QMessageBox.Ok)
        elif self.L=='de':
            if self.toolButton_active.isChecked():
                QMessageBox.information(self, "Pyarchinit", "Abfragesystem aktiviert. Wählen Sie einen Standort und klicken Sie auf Parameter speichern", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "Pyarchinit", "Abfragesystem deaktiviert", QMessageBox.Ok)

        else:
            if self.toolButton_active.isChecked():
                QMessageBox.information(self, "Pyarchinit", "Query system activated. Select a site and click on save parameters", QMessageBox.Ok)
                self.charge_list()
            else:
                self.comboBox_sito.clear()
                QMessageBox.information(self, "Pyarchinit", "Query system deactivated", QMessageBox.Ok)

    def charge_list(self):
        conn = Connection()
        conn_str = conn.conn_str()

        self.DB_MANAGER = Pyarchinit_db_management(conn_str)
        test = self.DB_MANAGER.connection()
        
        # Check if connection was successful
        if not test:
            QMessageBox.warning(self, "Database Connection", 
                              "Failed to connect to database. Please check your settings.", 
                              QMessageBox.Ok)
            return
            
        # Verifica che self.DB_MANAGER sia un'istanza della classe DBManager
        if not isinstance(self.DB_MANAGER, Pyarchinit_db_management):
            raise TypeError("self.DB_MANAGER is not an instance of DBManager")

        try:
            sito_vl = self.UTILITY.tup_2_list_III(self.DB_MANAGER.group_by('site_table', 'sito', 'SITE'))
            try:
                sito_vl.remove('')
            except Exception as e:
                # if str(e) == "list.remove(x): x not in list":
                pass
        except Exception as e:
            QMessageBox.warning(self, "Database Error", 
                              f"Error loading site list: {str(e)}", 
                              QMessageBox.Ok)
            return

        self.comboBox_sito.clear()
        sito_vl.sort()
        self.comboBox_sito.addItems(sito_vl)

            
    def on_pushButton_import_geometry_pressed(self):
        
        if self.L=='it':

            msg = QMessageBox.warning(self, "Attenzione", "Il sistema aggiornerà le geometrie con i dati importati. Schiaccia Annulla per abortire altrimenti schiaccia Ok per contiunuare." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        elif self.L=='de':

            msg = QMessageBox.warning(self, "Warning", "Das System wird die Geometrien mit den importierten Daten aktualisieren. Drücken Sie Abbrechen, um abzubrechen, oder drücken Sie Ok, um fortzufahren." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        else:

            msg = QMessageBox.warning(self, "Warnung", "The system will update the geometries with the imported data. Press Cancel to abort otherwise press Ok to contiunue." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        if msg == QMessageBox.Cancel:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Azione annullata" ,  QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Aktion abgebrochen" ,  QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Warning", "Action aborted" ,  QMessageBox.Ok)
        else:
            
            id_table_class_mapper_conv_dict = {
                'PYSITO_POINT': 'gid',
                'PYSITO_POLYGON':'gid',
                'PYUS':'gid',
                'PYQUOTE':'gid',
                'PYUSM':'gid',
                'PYQUOTEUSM':'gid',
                'PYUS_NEGATIVE':'gid',
                'PYSTRUTTURE':'gid',
                'PYREPERTI':'gid',
                'PYINDIVIDUI':'gid' ,
                'PYCAMPIONI':'gid',
                'PYTOMBA':'gid',
                'PYDOCUMENTAZIONE':'gid' ,
                'PYLINEERIFERIMENTO':'gid',
                'PYRIPARTIZIONI_SPAZIALI':'gid',
                'PYSEZIONI':'gid'}
           
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_read = {
                "server": str(self.comboBox_server_rd.currentText()),
                "user": str(self.lineEdit_username_rd.text()),
                "password": str(self.lineEdit_pass_rd.text()),
                "host": str(self.lineEdit_host_rd.text()),
                "port": str(self.lineEdit_port_rd.text()),
                "db_name": str(self.lineEdit_database_rd.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_read["server"] == 'postgres':
                try:
                    conn_str_read = "%s://%s:%s@%s:%s/%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])
                except:
                    conn_str_read = "%s://%s:%s@%s:%d/%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])
            elif conn_str_dict_read["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
                conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE
            self.DB_MANAGER_read = Pyarchinit_db_management(conn_str_read)
            test = self.DB_MANAGER_read.connection()
            if test:
                QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Connection error: <br>", QMessageBox.Cancel)

            ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
            search_dict = {
                self.mFeature_field_rd.currentText(): "'" + str(self.mFeature_value_rd.currentText()) + "'"
            }
            mapper_class_read = str(self.comboBox_geometry_read.currentText())
            res_read = self.DB_MANAGER_read.query_bool(search_dict, mapper_class_read)
            ####INSERISCE I DATI DA UPLOADARE DENTRO ALLA LISTA DATA_LIST_TOIMP
            data_list_toimp = []
            for i in res_read:
                data_list_toimp.append(i)
            QMessageBox.warning(self, "Total record to import", str(len(data_list_toimp)), QMessageBox.Ok)
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_write = {
                "server": str(self.comboBox_server_wt.currentText()),
                "user": str(self.lineEdit_username_wt.text()),
                "password": str(self.lineEdit_pass_wt.text()),
                "host": str(self.lineEdit_host_wt.text()),
                "port": str(self.lineEdit_port_wt.text()),
                "db_name": str(self.lineEdit_database_wt.text())
            }
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_write["server"] == 'postgres':
                try:
                    conn_str_write = "%s://%s:%s@%s:%s/%s%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"], conn_str_dict_write["port"], conn_str_dict_write["db_name"],
                        "?sslmode=allow")
                except:
                    print('error')
                else:
                    conn_str_write = "%s://%s:%s@%s:%d/%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"],
                        int(conn_str_dict_write["port"]), conn_str_dict_write["db_name"])
            elif conn_str_dict_write["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
                conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE IN SCRITTURA
            self.DB_MANAGER_write = Pyarchinit_db_management(conn_str_write)
            test = self.DB_MANAGER_write.connection()
            test = str(test)
            mapper_class_write = str(self.comboBox_geometry_read.currentText())
            ####inserisce i dati dentro al database
            ####PYUNITASTRATIGRAFICHE TABLE
            if mapper_class_write == 'PYUS' :
                for sing_rec in range(len(data_list_toimp)):
                    
                    try:
                        data = self.DB_MANAGER_write.insert_pyus(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            
                            
                            data_list_toimp[sing_rec].area_s,
                            data_list_toimp[sing_rec].scavo_s,
                            data_list_toimp[sing_rec].us_s,
                            data_list_toimp[sing_rec].stratigraph_index_us,
                            data_list_toimp[sing_rec].tipo_us_s,
                            data_list_toimp[sing_rec].rilievo_originale,
                            data_list_toimp[sing_rec].disegnatore,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].coord,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_s)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYUSM' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyusm(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].area_s,
                            data_list_toimp[sing_rec].scavo_s,
                            data_list_toimp[sing_rec].us_s,
                            data_list_toimp[sing_rec].stratigraph_index_us,
                            data_list_toimp[sing_rec].tipo_us_s,
                            data_list_toimp[sing_rec].rilievo_originale,
                            data_list_toimp[sing_rec].disegnatore,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].coord,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_s)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            
            elif mapper_class_write == 'PYSITO_POINT' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pysito_point(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_nome,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYSITO_POLYGON' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pysito_polygon(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_id,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYQUOTE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyquote(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_q,
                            data_list_toimp[sing_rec].area_q ,
                            data_list_toimp[sing_rec].us_q ,
                            data_list_toimp[sing_rec].unita_misu_q ,
                            data_list_toimp[sing_rec].quota_q ,
                            data_list_toimp[sing_rec].data ,
                            data_list_toimp[sing_rec].disegnatore ,
                            data_list_toimp[sing_rec].rilievo_originale ,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_q)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYQUOTEUSM' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyquote_usm(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_q,
                            data_list_toimp[sing_rec].area_q ,
                            data_list_toimp[sing_rec].us_q ,
                            data_list_toimp[sing_rec].unita_misu_q ,
                            data_list_toimp[sing_rec].quota_q ,
                            data_list_toimp[sing_rec].data ,
                            data_list_toimp[sing_rec].disegnatore ,
                            data_list_toimp[sing_rec].rilievo_originale ,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].unita_tipo_q)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            
            elif mapper_class_write == 'PYUS_NEGATIVE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyus_negative(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito_n ,
                            data_list_toimp[sing_rec].area_n ,
                            data_list_toimp[sing_rec].us_n ,
                            data_list_toimp[sing_rec].tipo_doc_n ,
                            data_list_toimp[sing_rec].nome_doc_n,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYSTRUTTURE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pystrutture(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito ,
                            data_list_toimp[sing_rec].id_strutt ,
                            data_list_toimp[sing_rec].per_iniz,
                            data_list_toimp[sing_rec].per_fin ,
                            data_list_toimp[sing_rec].dataz_ext ,
                            data_list_toimp[sing_rec].fase_iniz,
                            data_list_toimp[sing_rec].fase_fin ,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].the_geom ,
                            data_list_toimp[sing_rec].sigla_strut,
                            data_list_toimp[sing_rec].nr_strut)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYREPERTI' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyreperti(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_rep ,
                            data_list_toimp[sing_rec].siti ,
                            data_list_toimp[sing_rec].link ,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYINDIVIDUI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyindividui(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].sigla_struttura,
                            data_list_toimp[sing_rec].note,
                            data_list_toimp[sing_rec].id_individuo,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYCAMPIONI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pycampioni(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_campion,
                            data_list_toimp[sing_rec].sito,
                            # data_list_toimp[sing_rec].tipo_camp ,
                            # data_list_toimp[sing_rec].dataz ,
                            # data_list_toimp[sing_rec].cronologia ,
                            # data_list_toimp[sing_rec].link_immag,
                            data_list_toimp[sing_rec].sigla_camp ,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        value = (float(sing_rec)/float(len(data_list_toimp)))*100
                        self.progress_bar.setValue(value)
                        QApplication.processEvents()
                    except Exception as e :
                        QMessageBox.warning(self, "Errore", "Error ! \n"+ str(e),  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYTOMBA':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pytomba(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nr_scheda,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYDOCUMENTAZIONE':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pydocumentazione(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].path_qgis_pj,
                            data_list_toimp[sing_rec].geom,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYLINEERIFERIMENTO':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pylineeriferimento(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].definizion ,
                            data_list_toimp[sing_rec].descrizion,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYRIPARTIZIONI_SPAZIALI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pyripartizioni_spaziali(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_rs,
                            data_list_toimp[sing_rec].sito_rs,
                            data_list_toimp[sing_rec].tip_rip,
                            data_list_toimp[sing_rec].descr_rs,
                            data_list_toimp[sing_rec].the_geom)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PYSEZIONI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_pysezioni(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].id_sezione,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].descr,
                            data_list_toimp[sing_rec].the_geom,
                            data_list_toimp[sing_rec].tipo_doc,
                            data_list_toimp[sing_rec].nome_doc)
                        self.DB_MANAGER_write.insert_data_session(data)
                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")



    def on_pushButton_apply_constraints_pressed(self):
        """Apply unique constraints to thesaurus table."""
        if self.L == 'it':
            msg = QMessageBox.question(self, "Applica Vincoli",
                "Vuoi applicare i vincoli di unicità alla tabella thesaurus?\n"
                "Questo previene duplicati durante l'importazione.\n\n"
                "NOTA: I duplicati esistenti verranno rimossi automaticamente.",
                QMessageBox.Yes | QMessageBox.No)
        else:
            msg = QMessageBox.question(self, "Apply Constraints",
                "Do you want to apply unique constraints to thesaurus table?\n"
                "This prevents duplicates during import.\n\n"
                "NOTE: Existing duplicates will be automatically removed.",
                QMessageBox.Yes | QMessageBox.No)

        if msg == QMessageBox.Yes:
            # Get current database connection settings
            conn_str_dict = {
                "server": str(self.comboBox_server_wt.currentText()),
                "user": str(self.lineEdit_username_wt.text()),
                "password": str(self.lineEdit_pass_wt.text()),
                "host": str(self.lineEdit_host_wt.text()),
                "port": str(self.lineEdit_port_wt.text()),
                "db_name": str(self.lineEdit_database_wt.text())
            }

            try:
                if conn_str_dict["server"] == 'postgres':
                    # Apply PostgreSQL constraints
                    import psycopg2
                    conn = psycopg2.connect(
                        host=conn_str_dict["host"],
                        port=conn_str_dict["port"],
                        dbname=conn_str_dict["db_name"],
                        user=conn_str_dict["user"],
                        password=conn_str_dict["password"]
                    )
                    cursor = conn.cursor()

                    # Ensure n_tipologia and n_sigla columns exist
                    cursor.execute("""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                           WHERE table_schema = 'public'
                                           AND table_name = 'pyarchinit_thesaurus_sigle'
                                           AND column_name = 'n_tipologia') THEN
                                ALTER TABLE public.pyarchinit_thesaurus_sigle
                                ADD COLUMN n_tipologia integer;
                            END IF;

                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                           WHERE table_schema = 'public'
                                           AND table_name = 'pyarchinit_thesaurus_sigle'
                                           AND column_name = 'n_sigla') THEN
                                ALTER TABLE public.pyarchinit_thesaurus_sigle
                                ADD COLUMN n_sigla integer;
                            END IF;
                        END $$;
                    """)

                    # First, clean trailing spaces from all fields
                    cursor.execute("""
                        UPDATE public.pyarchinit_thesaurus_sigle
                        SET lingua = TRIM(lingua),
                            nome_tabella = TRIM(nome_tabella),
                            tipologia_sigla = TRIM(tipologia_sigla),
                            sigla = TRIM(sigla),
                            sigla_estesa = TRIM(sigla_estesa),
                            descrizione = TRIM(descrizione),
                            parent_sigla = TRIM(parent_sigla)
                        WHERE lingua != TRIM(lingua)
                           OR nome_tabella != TRIM(nome_tabella)
                           OR tipologia_sigla != TRIM(tipologia_sigla)
                           OR sigla != TRIM(sigla)
                           OR sigla_estesa != TRIM(sigla_estesa)
                           OR descrizione != TRIM(descrizione)
                           OR parent_sigla != TRIM(parent_sigla)
                    """)

                    trimmed = cursor.rowcount
                    if trimmed > 0:
                        if self.L == 'it':
                            QMessageBox.information(self, "Pulizia Spazi",
                                f"Rimossi spazi in eccesso da {trimmed} record.")
                        else:
                            QMessageBox.information(self, "Trim Spaces",
                                f"Trimmed spaces from {trimmed} records.")

                    # Then find and remove duplicates
                    cursor.execute("""
                        -- Find duplicates based on unique key, handling NULLs and trimmed values
                        WITH duplicates AS (
                            SELECT id_thesaurus_sigle,
                                   ROW_NUMBER() OVER (
                                       PARTITION BY
                                           COALESCE(TRIM(lingua), ''),
                                           COALESCE(TRIM(nome_tabella), ''),
                                           COALESCE(TRIM(tipologia_sigla), ''),
                                           COALESCE(TRIM(sigla_estesa), '')
                                       ORDER BY id_thesaurus_sigle
                                   ) AS row_num
                            FROM public.pyarchinit_thesaurus_sigle
                        )
                        SELECT COUNT(*) FROM duplicates WHERE row_num > 1
                    """)

                    dup_count = cursor.fetchone()[0]

                    if dup_count > 0:
                        if self.L == 'it':
                            remove_msg = QMessageBox.question(self, "Duplicati Trovati",
                                f"Trovati {dup_count} record duplicati.\n"
                                f"Vuoi rimuoverli automaticamente?",
                                QMessageBox.Yes | QMessageBox.No)
                        else:
                            remove_msg = QMessageBox.question(self, "Duplicates Found",
                                f"Found {dup_count} duplicate records.\n"
                                f"Do you want to remove them automatically?",
                                QMessageBox.Yes | QMessageBox.No)

                        if remove_msg == QMessageBox.Yes:
                            # Remove duplicates, keeping only the first occurrence
                            # First check for duplicates based on sigla field as well
                            cursor.execute("""
                                DELETE FROM public.pyarchinit_thesaurus_sigle
                                WHERE id_thesaurus_sigle IN (
                                    SELECT id_thesaurus_sigle
                                    FROM (
                                        SELECT id_thesaurus_sigle,
                                               ROW_NUMBER() OVER (
                                                   PARTITION BY
                                                       COALESCE(TRIM(lingua), ''),
                                                       COALESCE(TRIM(nome_tabella), ''),
                                                       COALESCE(TRIM(tipologia_sigla), ''),
                                                       COALESCE(TRIM(sigla_estesa), '')
                                                   ORDER BY id_thesaurus_sigle
                                               ) AS row_num
                                        FROM public.pyarchinit_thesaurus_sigle
                                    ) t
                                    WHERE t.row_num > 1
                                )
                            """)

                            deleted = cursor.rowcount

                            # Also remove duplicates based on sigla (for the second unique constraint)
                            cursor.execute("""
                                DELETE FROM public.pyarchinit_thesaurus_sigle
                                WHERE id_thesaurus_sigle IN (
                                    SELECT id_thesaurus_sigle
                                    FROM (
                                        SELECT id_thesaurus_sigle,
                                               ROW_NUMBER() OVER (
                                                   PARTITION BY
                                                       COALESCE(TRIM(lingua), ''),
                                                       COALESCE(TRIM(nome_tabella), ''),
                                                       COALESCE(TRIM(tipologia_sigla), ''),
                                                       COALESCE(TRIM(sigla), '')
                                                   ORDER BY id_thesaurus_sigle
                                               ) AS row_num
                                        FROM public.pyarchinit_thesaurus_sigle
                                    ) t
                                    WHERE t.row_num > 1
                                )
                            """)

                            deleted = cursor.rowcount

                            if self.L == 'it':
                                QMessageBox.information(self, "Pulizia Completata",
                                    f"Rimossi {deleted} record duplicati.")
                            else:
                                QMessageBox.information(self, "Cleanup Complete",
                                    f"Removed {deleted} duplicate records.")
                        else:
                            if self.L == 'it':
                                QMessageBox.warning(self, "Operazione Annullata",
                                    "Rimuovi manualmente i duplicati prima di applicare i vincoli.")
                            else:
                                QMessageBox.warning(self, "Operation Cancelled",
                                    "Please remove duplicates manually before applying constraints.")
                            conn.close()
                            return

                    # Add columns if they don't exist
                    cursor.execute("""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                           WHERE table_schema = 'public'
                                           AND table_name = 'pyarchinit_thesaurus_sigle'
                                           AND column_name = 'lingua') THEN
                                ALTER TABLE public.pyarchinit_thesaurus_sigle
                                ADD COLUMN lingua character varying(10) DEFAULT 'it';
                            END IF;
                        END $$;
                    """)

                    # Drop and recreate constraints
                    cursor.execute("""
                        ALTER TABLE public.pyarchinit_thesaurus_sigle
                        DROP CONSTRAINT IF EXISTS thesaurus_unique_key;
                    """)

                    cursor.execute("""
                        ALTER TABLE public.pyarchinit_thesaurus_sigle
                        DROP CONSTRAINT IF EXISTS thesaurus_unique_sigla;
                    """)

                    cursor.execute("""
                        ALTER TABLE public.pyarchinit_thesaurus_sigle
                        ADD CONSTRAINT thesaurus_unique_key
                        UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla_estesa);
                    """)

                    # Secondo vincolo è opzionale - commentalo se hai sigle duplicate con sigla_estesa diversa
                    # cursor.execute("""
                    #     ALTER TABLE public.pyarchinit_thesaurus_sigle
                    #     ADD CONSTRAINT thesaurus_unique_sigla
                    #     UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla);
                    # """)

                    # Create indexes
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_thesaurus_lingua
                        ON public.pyarchinit_thesaurus_sigle(lingua);
                    """)

                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella
                        ON public.pyarchinit_thesaurus_sigle(nome_tabella);
                    """)

                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_thesaurus_composite
                        ON public.pyarchinit_thesaurus_sigle(lingua, nome_tabella, tipologia_sigla);
                    """)

                    conn.commit()
                    conn.close()

                    if self.L == 'it':
                        QMessageBox.information(self, "Successo", "Vincoli applicati con successo!")
                    else:
                        QMessageBox.information(self, "Success", "Constraints applied successfully!")

                elif conn_str_dict["server"] == 'sqlite':
                    # Apply SQLite constraints
                    import sqlite3
                    sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep, "pyarchinit_DB_folder")
                    dbname_abs = sqlite_DB_path + os.sep + conn_str_dict["db_name"]

                    conn = sqlite3.connect(dbname_abs)
                    cursor = conn.cursor()

                    # Check if table exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name='pyarchinit_thesaurus_sigle'
                    """)

                    if cursor.fetchone():
                        # Check and add missing columns if needed
                        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
                        columns = [row[1] for row in cursor.fetchall()]

                        if 'n_tipologia' not in columns:
                            cursor.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN n_tipologia INTEGER")

                        if 'n_sigla' not in columns:
                            cursor.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN n_sigla INTEGER")

                        # First, clean trailing spaces from all fields
                        cursor.execute("""
                            UPDATE pyarchinit_thesaurus_sigle
                            SET lingua = TRIM(lingua),
                                nome_tabella = TRIM(nome_tabella),
                                tipologia_sigla = TRIM(tipologia_sigla),
                                sigla = TRIM(sigla),
                                sigla_estesa = TRIM(sigla_estesa),
                                descrizione = TRIM(descrizione),
                                parent_sigla = TRIM(parent_sigla)
                            WHERE lingua != TRIM(lingua)
                               OR nome_tabella != TRIM(nome_tabella)
                               OR tipologia_sigla != TRIM(tipologia_sigla)
                               OR sigla != TRIM(sigla)
                               OR sigla_estesa != TRIM(sigla_estesa)
                               OR descrizione != TRIM(descrizione)
                               OR parent_sigla != TRIM(parent_sigla)
                        """)

                        trimmed = cursor.rowcount
                        if trimmed > 0:
                            if self.L == 'it':
                                QMessageBox.information(self, "Pulizia Spazi",
                                    f"Rimossi spazi in eccesso da {trimmed} record.")
                            else:
                                QMessageBox.information(self, "Trim Spaces",
                                    f"Trimmed spaces from {trimmed} records.")

                        # Then find and count duplicates
                        cursor.execute("""
                            SELECT COUNT(*) FROM (
                                SELECT COALESCE(TRIM(lingua), '') as lingua,
                                       COALESCE(TRIM(nome_tabella), '') as nome_tabella,
                                       COALESCE(TRIM(tipologia_sigla), '') as tipologia_sigla,
                                       COALESCE(TRIM(sigla_estesa), '') as sigla_estesa,
                                       COUNT(*) as cnt
                                FROM pyarchinit_thesaurus_sigle
                                GROUP BY COALESCE(TRIM(lingua), ''),
                                         COALESCE(TRIM(nome_tabella), ''),
                                         COALESCE(TRIM(tipologia_sigla), ''),
                                         COALESCE(TRIM(sigla_estesa), '')
                                HAVING COUNT(*) > 1
                            )
                        """)

                        dup_groups = cursor.fetchone()[0]

                        if dup_groups > 0:
                            # Count total duplicate records (excluding first occurrence)
                            cursor.execute("""
                                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle t1
                                WHERE EXISTS (
                                    SELECT 1 FROM pyarchinit_thesaurus_sigle t2
                                    WHERE t1.lingua = t2.lingua
                                    AND t1.nome_tabella = t2.nome_tabella
                                    AND t1.tipologia_sigla = t2.tipologia_sigla
                                    AND t1.sigla_estesa = t2.sigla_estesa
                                    AND t1.id_thesaurus_sigle > t2.id_thesaurus_sigle
                                )
                            """)

                            dup_count = cursor.fetchone()[0]

                            if self.L == 'it':
                                remove_msg = QMessageBox.question(self, "Duplicati Trovati",
                                    f"Trovati {dup_count} record duplicati in {dup_groups} gruppi.\n"
                                    f"Vuoi rimuoverli automaticamente?",
                                    QMessageBox.Yes | QMessageBox.No)
                            else:
                                remove_msg = QMessageBox.question(self, "Duplicates Found",
                                    f"Found {dup_count} duplicate records in {dup_groups} groups.\n"
                                    f"Do you want to remove them automatically?",
                                    QMessageBox.Yes | QMessageBox.No)

                            if remove_msg == QMessageBox.Yes:
                                # Remove duplicates, keeping only the first occurrence
                                cursor.execute("""
                                    DELETE FROM pyarchinit_thesaurus_sigle
                                    WHERE id_thesaurus_sigle NOT IN (
                                        SELECT MIN(id_thesaurus_sigle)
                                        FROM pyarchinit_thesaurus_sigle
                                        GROUP BY COALESCE(lingua, ''),
                                                 COALESCE(nome_tabella, ''),
                                                 COALESCE(tipologia_sigla, ''),
                                                 COALESCE(sigla_estesa, '')
                                    )
                                """)

                                deleted = cursor.rowcount

                                if self.L == 'it':
                                    QMessageBox.information(self, "Pulizia Completata",
                                        f"Rimossi {deleted} record duplicati.")
                                else:
                                    QMessageBox.information(self, "Cleanup Complete",
                                        f"Removed {deleted} duplicate records.")
                            else:
                                if self.L == 'it':
                                    QMessageBox.warning(self, "Operazione Annullata",
                                        "Rimuovi manualmente i duplicati prima di applicare i vincoli.")
                                else:
                                    QMessageBox.warning(self, "Operation Cancelled",
                                        "Please remove duplicates manually before applying constraints.")
                                conn.close()
                                return

                        # SQLite requires recreating the table to add constraints
                        # First check current columns
                        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
                        columns = [row[1] for row in cursor.fetchall()]

                        # Build column list for new table
                        column_defs = []
                        if 'id_thesaurus_sigle' in columns:
                            column_defs.append("id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT")
                        if 'nome_tabella' in columns:
                            column_defs.append("nome_tabella TEXT")
                        if 'sigla' in columns:
                            column_defs.append("sigla TEXT")
                        if 'sigla_estesa' in columns:
                            column_defs.append("sigla_estesa TEXT")
                        if 'descrizione' in columns:
                            column_defs.append("descrizione TEXT")
                        if 'tipologia_sigla' in columns:
                            column_defs.append("tipologia_sigla TEXT")

                        # Add lingua if missing
                        if 'lingua' not in columns:
                            column_defs.append("lingua TEXT DEFAULT 'it'")
                        else:
                            column_defs.append("lingua TEXT DEFAULT 'it'")

                        # Add optional columns
                        for col in ['n_tipologia', 'n_sigla', 'order_layer', 'id_parent', 'parent_sigla', 'hierarchy_level']:
                            if col in columns:
                                if col in ['n_tipologia', 'n_sigla', 'order_layer', 'id_parent', 'hierarchy_level']:
                                    column_defs.append(f"{col} INTEGER")
                                else:
                                    column_defs.append(f"{col} TEXT")

                        # Create new table with constraints
                        cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle_new (
                                {', '.join(column_defs)},
                                UNIQUE(lingua, nome_tabella, tipologia_sigla, sigla_estesa),
                                UNIQUE(lingua, nome_tabella, tipologia_sigla, sigla)
                            )
                        """)

                        # Copy data
                        cursor.execute("""
                            INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle_new
                            SELECT * FROM pyarchinit_thesaurus_sigle
                        """)

                        # Replace old table
                        cursor.execute("DROP TABLE pyarchinit_thesaurus_sigle")
                        cursor.execute("ALTER TABLE pyarchinit_thesaurus_sigle_new RENAME TO pyarchinit_thesaurus_sigle")

                        # Create indexes
                        cursor.execute("""
                            CREATE INDEX IF NOT EXISTS idx_thesaurus_composite
                            ON pyarchinit_thesaurus_sigle(lingua, nome_tabella, tipologia_sigla)
                        """)

                        conn.commit()
                        conn.close()

                        if self.L == 'it':
                            QMessageBox.information(self, "Successo", "Vincoli applicati con successo!")
                        else:
                            QMessageBox.information(self, "Success", "Constraints applied successfully!")
                    else:
                        if self.L == 'it':
                            QMessageBox.warning(self, "Avviso", "Tabella thesaurus non trovata")
                        else:
                            QMessageBox.warning(self, "Warning", "Thesaurus table not found")

            except Exception as e:
                if self.L == 'it':
                    QMessageBox.critical(self, "Errore", f"Errore nell'applicare i vincoli:\n{str(e)}")
                else:
                    QMessageBox.critical(self, "Error", f"Error applying constraints:\n{str(e)}")

    def on_pushButton_import_pressed(self):
        if self.L=='it':

            msg = QMessageBox.warning(self, "Attenzione", "Il sistema aggiornerà le tabelle con i dati importati. Schiaccia Annulla per abortire altrimenti schiaccia Ok per contiunuare." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        elif self.L=='de':

            msg = QMessageBox.warning(self, "Warning", "Das System wird die tabellarisch mit den importierten Daten aktualisieren. Drücken Sie Abbrechen, um abzubrechen, oder drücken Sie Ok, um fortzufahren." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        else:

            msg = QMessageBox.warning(self, "Warnung", "The system will update the tables with the imported data. Press Cancel to abort otherwise press Ok to contiunue." ,  QMessageBox.Ok  | QMessageBox.Cancel)

        if msg == QMessageBox.Cancel:
            if self.L=='it':
                QMessageBox.warning(self, "Attenzione", "Azione annullata" ,  QMessageBox.Ok)
            elif self.L=='de':
                QMessageBox.warning(self, "Warnung", "Aktion abgebrochen" ,  QMessageBox.Ok)

            else:
                QMessageBox.warning(self, "Warning", "Action aborted" ,  QMessageBox.Ok)

        else:
            if self.L=='it':
                id_table_class_mapper_conv_dict = {
                    'SITE':'id_sito',
                    'US': 'id_us',
                    'UT': 'id_ut',
                    'PERIODIZZAZIONE': 'id_perfas',
                    'INVENTARIO_MATERIALI': 'id_invmat',
                    'POTTERY':'id_rep',
                    'STRUTTURA': 'id_struttura',
                    'TOMBA': 'id_tomba',
                    'SCHEDAIND': 'id_scheda_ind',
                    'CAMPIONI': 'id_campione',
                    'DOCUMENTAZIONE': 'id_documentazione',
                    'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle',
                    'MEDIA': 'id_media',
                    'MEDIA_THUMB': 'id_media_thumb',
                    'MEDIATOENTITY':'id_mediaToEntity',
                    'TMA': 'id'

                }
            elif self.L=='de':
                id_table_class_mapper_conv_dict = {
                    'SITE':'id_sito',
                    'US': 'id_us',
                    'UT': 'id_ut',
                    'PERIODIZZAZIONE': 'id_perfas',
                    'INVENTARIO_MATERIALI': 'id_invmat',
                    'POTTERY':'id_rep',
                    'STRUTTURA': 'id_struttura',
                    'TOMBA': 'id_tomba',
                    'SCHEDAIND': 'id_scheda_ind',
                    'CAMPIONI': 'id_campione',
                    'DOCUMENTAZIONE': 'id_documentazione',
                    'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle',
                    'MEDIA': 'id_media',
                    'MEDIA_THUMB': 'id_media_thumb',
                    'MEDIATOENTITY':'id_mediaToEntity',
                    'TMA': 'id'
                }
            else:
                id_table_class_mapper_conv_dict = {
                    'SITE':'id_sito',
                    'US': 'id_us',
                    'UT': 'id_ut',
                    'PERIODIZZAZIONE': 'id_perfas',
                    'INVENTARIO_MATERIALI': 'id_invmat',
                    'POTTERY':'id_rep',
                    'STRUTTURA': 'id_struttura',
                    'TOMBA': 'id_tomba',
                    'SCHEDAIND': 'id_scheda_ind',
                    'CAMPIONI': 'id_campione',
                    'DOCUMENTAZIONE': 'id_documentazione',
                    'PYARCHINIT_THESAURUS_SIGLE': 'id_thesaurus_sigle',
                    'MEDIA': 'id_media',
                    'MEDIA_THUMB': 'id_media_thumb',
                    'MEDIATOENTITY':'id_mediaToEntity',
                    'TMA': 'id'
                }
            # creazione del cursore di lettura
            """if os.name == 'posix':
                home = os.environ['HOME']
            elif os.name == 'nt':
                home = os.environ['HOMEPATH']"""
            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_read=''
            conn_str_dict_read = {
                "server": str(self.comboBox_server_rd.currentText()),
                "user": str(self.lineEdit_username_rd.text()),
                "password": str(self.lineEdit_pass_rd.text()),
                "host": str(self.lineEdit_host_rd.text()),
                "port": str(self.lineEdit_port_rd.text()),
                "db_name": str(self.lineEdit_database_rd.text())
            }
            
            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_read["server"] == 'postgres':
                try:
                    conn_str_read = "%s://%s:%s@%s:%s/%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])
                except Exception as e:
                    print(
                        "Error in connection parameter. <br> If they are correct restart QGIS. <br> Error: " + str(e))

                else:
                    conn_str_read = "%s://%s:%s@%s:%s/%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_read["user"], conn_str_dict_read["password"],
                        conn_str_dict_read["host"],
                        conn_str_dict_read["port"], conn_str_dict_read["db_name"])


            elif conn_str_dict_read["server"] == 'sqlite':

                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_read["db_name"]
                conn_str_read = "%s:///%s" % (conn_str_dict_read["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_read["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE
            self.DB_MANAGER_read = Pyarchinit_db_management(conn_str_read)

            test = self.DB_MANAGER_read.connection()

            if test:
                QMessageBox.warning(self, "Message", "Connection ok", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Alert", "Connection error: <br>", QMessageBox.Cancel)
            """elif test.find("create_engine") != -1:
                #QMessageBox.warning(self, "Alert",
                                    "Try connection parameter. <br> If they are correct restart QGIS",
                                    QMessageBox.Ok)"""


            ####LEGGE I RECORD IN BASE AL PARAMETRO CAMPO=VALORE
            search_dict = {
                self.mFeature_field_rd.currentText(): "'" + str(self.mFeature_value_rd.currentText()) + "'"
            }
            mapper_class_read = str(self.comboBox_mapper_read.currentText())
            
            # Handle ALL case separately
            if mapper_class_read == "ALL":
                data_list_toimp = []  # Will be populated later for each table
            else:
                res_read = self.DB_MANAGER_read.query_bool(search_dict, mapper_class_read)
                
                ####INSERISCE I DATI DA UPLOADARE DENTRO ALLA LISTA DATA_LIST_TOIMP
                data_list_toimp = []
                for i in res_read:
                    data_list_toimp.append(i)

            QMessageBox.warning(self, "Total record to import", str(len(data_list_toimp)), QMessageBox.Ok)

            ####RICAVA I DATI IN LETTURA PER LA CONNESSIONE DALLA GUI
            conn_str_dict_write = {
                "server": str(self.comboBox_server_wt.currentText()),
                "user": str(self.lineEdit_username_wt.text()),
                "password": str(self.lineEdit_pass_wt.text()),
                "host": str(self.lineEdit_host_wt.text()),
                "port": str(self.lineEdit_port_wt.text()),
                "db_name": str(self.lineEdit_database_wt.text())
            }

            ####CREA LA STRINGA DI CONNESSIONE IN LETTURA
            if conn_str_dict_write["server"] == 'postgres':
                try:
                    conn_str_write = "%s://%s:%s@%s:%s/%s%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"], conn_str_dict_write["port"], conn_str_dict_write["db_name"],
                        "?sslmode=allow")
                except:
                    print('error')
                else:
                    conn_str_write = "%s://%s:%s@%s:%d/%s?client_encoding=utf8" % (
                        "postgresql", conn_str_dict_write["user"], conn_str_dict_write["password"],
                        conn_str_dict_write["host"],
                        int(conn_str_dict_write["port"]), conn_str_dict_write["db_name"])
            elif conn_str_dict_write["server"] == 'sqlite':
                sqlite_DB_path = '{}{}{}'.format(self.HOME, os.sep,
                                                 "pyarchinit_DB_folder")
                dbname_abs = sqlite_DB_path + os.sep + conn_str_dict_write["db_name"]
                conn_str_write = "%s:///%s" % (conn_str_dict_write["server"], dbname_abs)
                QMessageBox.warning(self, "Alert", str(conn_str_dict_write["db_name"]), QMessageBox.Ok)
            ####SI CONNETTE AL DATABASE IN SCRITTURA

            self.DB_MANAGER_write = Pyarchinit_db_management(conn_str_write)
            test = self.DB_MANAGER_write.connection()
            test = str(test)



            mapper_class_write = str(self.comboBox_mapper_read.currentText())



            ####inserisce i dati dentro al database

            ####SITE TABLE
            if mapper_class_write == 'SITE' :

                for sing_rec in range(len(data_list_toimp)):

                    try:
                        data = self.DB_MANAGER_write.insert_site_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nazione,
                            data_list_toimp[sing_rec].regione,
                            data_list_toimp[sing_rec].comune,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].provincia,
                            data_list_toimp[sing_rec].definizione_sito,
                            data_list_toimp[sing_rec].sito_path,
                            data_list_toimp[sing_rec].find_check)


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            #### US TABLE

            ####SITE TABLE
            if mapper_class_write == 'POTTERY':

                for sing_rec in range(len(data_list_toimp)):

                    try:
                        data = self.DB_MANAGER_write.insert_pottery_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[
                                                                 mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_rep,
                            data_list_toimp[sing_rec].id_number,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].box,
                            data_list_toimp[sing_rec].photo,
                            data_list_toimp[sing_rec].drawing,
                            data_list_toimp[sing_rec].anno,
                            data_list_toimp[sing_rec].fabric,
                            data_list_toimp[sing_rec].percent,
                            data_list_toimp[sing_rec].material,
                            data_list_toimp[sing_rec].form,
                            data_list_toimp[sing_rec].specific_form,
                            data_list_toimp[sing_rec].ware,
                            data_list_toimp[sing_rec].munsell,
                            data_list_toimp[sing_rec].surf_trat,
                            data_list_toimp[sing_rec].exdeco,
                            data_list_toimp[sing_rec].intdeco,
                            data_list_toimp[sing_rec].wheel_made,
                            data_list_toimp[sing_rec].descrip_ex_deco,
                            data_list_toimp[sing_rec].descrip_in_deco,
                            data_list_toimp[sing_rec].note,
                            data_list_toimp[sing_rec].diametro_max,
                            data_list_toimp[sing_rec].qty,
                            data_list_toimp[sing_rec].diametro_rim,
                            data_list_toimp[sing_rec].diametro_bottom,
                            data_list_toimp[sing_rec].diametro_height,
                            data_list_toimp[sing_rec].diametro_preserved,
                            data_list_toimp[sing_rec].specific_shape,
                            data_list_toimp[sing_rec].bag,
                            data_list_toimp[sing_rec].sector)

                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

                #### US TABLE



            if mapper_class_write == 'US':

                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_us,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].d_stratigrafica,
                            data_list_toimp[sing_rec].d_interpretativa,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].interpretazione,
                            data_list_toimp[sing_rec].periodo_iniziale,
                            data_list_toimp[sing_rec].fase_iniziale,
                            data_list_toimp[sing_rec].periodo_finale,
                            data_list_toimp[sing_rec].fase_finale,
                            data_list_toimp[sing_rec].scavato,
                            data_list_toimp[sing_rec].attivita,
                            data_list_toimp[sing_rec].anno_scavo,
                            data_list_toimp[sing_rec].metodo_di_scavo,
                            data_list_toimp[sing_rec].inclusi,
                            data_list_toimp[sing_rec].campioni,
                            data_list_toimp[sing_rec].rapporti,
                            data_list_toimp[sing_rec].data_schedatura,
                            data_list_toimp[sing_rec].schedatore,
                            data_list_toimp[sing_rec].formazione,
                            data_list_toimp[sing_rec].stato_di_conservazione,
                            data_list_toimp[sing_rec].colore,
                            data_list_toimp[sing_rec].consistenza,
                            data_list_toimp[sing_rec].struttura,
                            data_list_toimp[sing_rec].cont_per,
                            data_list_toimp[sing_rec].order_layer,
                            data_list_toimp[sing_rec].documentazione,
                            data_list_toimp[sing_rec].unita_tipo,
                            # campi aggiunti per USM
                            data_list_toimp[sing_rec].settore,
                            data_list_toimp[sing_rec].quad_par,
                            data_list_toimp[sing_rec].ambient,
                            data_list_toimp[sing_rec].saggio,
                            data_list_toimp[sing_rec].elem_datanti,
                            data_list_toimp[sing_rec].funz_statica,
                            data_list_toimp[sing_rec].lavorazione,
                            data_list_toimp[sing_rec].spess_giunti,
                            data_list_toimp[sing_rec].letti_posa,
                            data_list_toimp[sing_rec].alt_mod,
                            data_list_toimp[sing_rec].un_ed_riass,
                            data_list_toimp[sing_rec].reimp,
                            data_list_toimp[sing_rec].posa_opera,
                            data_list_toimp[sing_rec].quota_min_usm,
                            data_list_toimp[sing_rec].quota_max_usm,
                            data_list_toimp[sing_rec].cons_legante,
                            data_list_toimp[sing_rec].col_legante,
                            data_list_toimp[sing_rec].aggreg_legante,
                            data_list_toimp[sing_rec].con_text_mat,
                            data_list_toimp[sing_rec].col_materiale,
                            data_list_toimp[sing_rec].inclusi_materiali_usm,
                            data_list_toimp[sing_rec].n_catalogo_generale,
                            data_list_toimp[sing_rec].n_catalogo_interno,
                            data_list_toimp[sing_rec].n_catalogo_internazionale,
                            data_list_toimp[sing_rec].soprintendenza,
                            data_list_toimp[sing_rec].quota_relativa,
                            data_list_toimp[sing_rec].quota_abs,
                            data_list_toimp[sing_rec].ref_tm,
                            data_list_toimp[sing_rec].ref_ra,
                            data_list_toimp[sing_rec].ref_n,
                            data_list_toimp[sing_rec].posizione,
                            data_list_toimp[sing_rec].criteri_distinzione,
                            data_list_toimp[sing_rec].modo_formazione,
                            data_list_toimp[sing_rec].componenti_organici,
                            data_list_toimp[sing_rec].componenti_inorganici,
                            data_list_toimp[sing_rec].lunghezza_max,
                            data_list_toimp[sing_rec].altezza_max,
                            data_list_toimp[sing_rec].altezza_min,
                            data_list_toimp[sing_rec].profondita_max,
                            data_list_toimp[sing_rec].profondita_min,
                            data_list_toimp[sing_rec].larghezza_media,
                            data_list_toimp[sing_rec].quota_max_abs,
                            data_list_toimp[sing_rec].quota_max_rel,
                            data_list_toimp[sing_rec].quota_min_abs,
                            data_list_toimp[sing_rec].quota_min_rel,
                            data_list_toimp[sing_rec].osservazioni,
                            data_list_toimp[sing_rec].datazione,
                            data_list_toimp[sing_rec].flottazione,
                            data_list_toimp[sing_rec].setacciatura,
                            data_list_toimp[sing_rec].affidabilita,
                            data_list_toimp[sing_rec].direttore_us,
                            data_list_toimp[sing_rec].responsabile_us,
                            data_list_toimp[sing_rec].cod_ente_schedatore,
                            data_list_toimp[sing_rec].data_rilevazione,
                            data_list_toimp[sing_rec].data_rielaborazione,
                            data_list_toimp[sing_rec].lunghezza_usm,
                            data_list_toimp[sing_rec].altezza_usm,
                            data_list_toimp[sing_rec].spessore_usm,
                            data_list_toimp[sing_rec].tecnica_muraria_usm,
                            data_list_toimp[sing_rec].modulo_usm,
                            data_list_toimp[sing_rec].campioni_malta_usm,
                            data_list_toimp[sing_rec].campioni_mattone_usm,
                            data_list_toimp[sing_rec].campioni_pietra_usm,
                            data_list_toimp[sing_rec].provenienza_materiali_usm,
                            data_list_toimp[sing_rec].criteri_distinzione_usm,
                            data_list_toimp[sing_rec].uso_primario_usm,
                            data_list_toimp[sing_rec].tipologia_opera,
                            data_list_toimp[sing_rec].sezione_muraria,
                            data_list_toimp[sing_rec].superficie_analizzata,
                            data_list_toimp[sing_rec].orientamento ,
                            data_list_toimp[sing_rec].materiali_lat ,
                            data_list_toimp[sing_rec].lavorazione_lat,
                            data_list_toimp[sing_rec].consistenza_lat ,
                            data_list_toimp[sing_rec].forma_lat ,
                            data_list_toimp[sing_rec].colore_lat ,
                            data_list_toimp[sing_rec].impasto_lat ,
                            data_list_toimp[sing_rec].forma_p ,
                            data_list_toimp[sing_rec].colore_p ,
                            data_list_toimp[sing_rec].taglio_p ,
                            data_list_toimp[sing_rec].posa_opera_p ,
                            data_list_toimp[sing_rec].inerti_usm ,
                            data_list_toimp[sing_rec].tipo_legante_usm,
                            data_list_toimp[sing_rec].rifinitura_usm,
                            data_list_toimp[sing_rec].materiale_p ,
                            data_list_toimp[sing_rec].consistenza_p,
                            data_list_toimp[sing_rec].rapporti2,
                            data_list_toimp[sing_rec].doc_usv

                        )


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            elif mapper_class_write == 'PERIODIZZAZIONE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_periodizzazione_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].periodo,
                            data_list_toimp[sing_rec].fase,
                            data_list_toimp[sing_rec].cron_iniziale,
                            data_list_toimp[sing_rec].cron_finale,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].datazione_estesa,
                            data_list_toimp[sing_rec].cont_per)


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'INVENTARIO_MATERIALI' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values_reperti(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,

                            #data_list_toimp[sing_rec].id_invmat,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].numero_inventario,
                            data_list_toimp[sing_rec].tipo_reperto,
                            data_list_toimp[sing_rec].criterio_schedatura,
                            data_list_toimp[sing_rec].definizione,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].lavato,
                            data_list_toimp[sing_rec].nr_cassa,
                            data_list_toimp[sing_rec].luogo_conservazione,
                            data_list_toimp[sing_rec].stato_conservazione,
                            data_list_toimp[sing_rec].datazione_reperto,
                            data_list_toimp[sing_rec].elementi_reperto,
                            data_list_toimp[sing_rec].misurazioni,
                            data_list_toimp[sing_rec].rif_biblio,
                            data_list_toimp[sing_rec].tecnologie,
                            data_list_toimp[sing_rec].forme_minime,
                            data_list_toimp[sing_rec].forme_massime,
                            data_list_toimp[sing_rec].totale_frammenti,
                            data_list_toimp[sing_rec].corpo_ceramico,
                            data_list_toimp[sing_rec].rivestimento,
                            data_list_toimp[sing_rec].diametro_orlo,
                            data_list_toimp[sing_rec].peso,
                            data_list_toimp[sing_rec].tipo,
                            data_list_toimp[sing_rec].eve_orlo,
                            data_list_toimp[sing_rec].repertato,
                            data_list_toimp[sing_rec].diagnostico,
                            data_list_toimp[sing_rec].n_reperto,
                            data_list_toimp[sing_rec].tipo_contenitore,
                            data_list_toimp[sing_rec].struttura,
                            data_list_toimp[sing_rec].years,
                        )


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'STRUTTURA' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_struttura_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,

                            #data_list_toimp[sing_rec].id_struttura,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].sigla_struttura,
                            data_list_toimp[sing_rec].numero_struttura,
                            data_list_toimp[sing_rec].categoria_struttura,
                            data_list_toimp[sing_rec].tipologia_struttura,
                            data_list_toimp[sing_rec].definizione_struttura,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].interpretazione,
                            data_list_toimp[sing_rec].periodo_iniziale,
                            data_list_toimp[sing_rec].fase_iniziale,
                            data_list_toimp[sing_rec].periodo_finale,
                            data_list_toimp[sing_rec].fase_finale,
                            data_list_toimp[sing_rec].datazione_estesa,
                            data_list_toimp[sing_rec].materiali_impiegati,
                            data_list_toimp[sing_rec].elementi_strutturali,
                            data_list_toimp[sing_rec].rapporti_struttura,
                            data_list_toimp[sing_rec].misure_struttura
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'TOMBA' :
                for sing_rec in range(len(data_list_toimp)):



                        # blocco periodo_iniziale
                    test_per_iniz = data_list_toimp[sing_rec].periodo_iniziale

                    if test_per_iniz == "" or test_per_iniz == None:
                        per_iniz = ''
                    else:
                        per_iniz = int(data_list_toimp[sing_rec].periodo_iniziale)

                        # blocco fase_iniziale
                    test_fas_iniz = data_list_toimp[sing_rec].fase_iniziale

                    if test_fas_iniz == "" or test_fas_iniz == None:
                        fase_iniz = ''
                    else:
                        fase_iniz = int(data_list_toimp[sing_rec].fase_iniziale)

                        # blocco periodo_finale
                    test_per_fin = data_list_toimp[sing_rec].periodo_finale

                    if test_per_fin == "" or test_per_fin == None:
                        per_fin = ''
                    else:
                        per_fin = int(data_list_toimp[sing_rec].periodo_finale)

                        # blocco fase_finale
                    test_fas_fin = data_list_toimp[sing_rec].fase_finale

                    if test_fas_fin == "" or test_fas_fin == None:
                        fase_fin = ''
                    else:
                        fase_fin = int(data_list_toimp[sing_rec].fase_finale)

                    try:
                        data = self.DB_MANAGER_write.insert_values_tomba(

                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_tomba,
                            str(data_list_toimp[sing_rec].sito),
                            str(data_list_toimp[sing_rec].area),
                            str(data_list_toimp[sing_rec].nr_scheda_taf),
                            str(data_list_toimp[sing_rec].sigla_struttura),
                            str(data_list_toimp[sing_rec].nr_struttura),
                            str(data_list_toimp[sing_rec].nr_individuo),
                            str(data_list_toimp[sing_rec].rito),
                            str(data_list_toimp[sing_rec].descrizione_taf),
                            str(data_list_toimp[sing_rec].interpretazione_taf),
                            str(data_list_toimp[sing_rec].segnacoli),
                            str(data_list_toimp[sing_rec].canale_libatorio_si_no),
                            str(data_list_toimp[sing_rec].oggetti_rinvenuti_esterno),
                            str(data_list_toimp[sing_rec].stato_di_conservazione),
                            str(data_list_toimp[sing_rec].copertura_tipo),
                            str(data_list_toimp[sing_rec].tipo_contenitore_resti),
                            str(data_list_toimp[sing_rec].tipo_deposizione),
                            str(data_list_toimp[sing_rec].tipo_sepoltura),
                            str(data_list_toimp[sing_rec].corredo_presenza),
                            str(data_list_toimp[sing_rec].corredo_tipo),
                            str(data_list_toimp[sing_rec].corredo_descrizione),
                            per_iniz,
                            fase_iniz,
                            per_fin,
                            fase_fin,
                            str(data_list_toimp[sing_rec].datazione_estesa)
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'SCHEDAIND' :
                for sing_rec in range(len(data_list_toimp)):
                    # blocco oritentamento_azimut
                    # test_azimut = data_list_toimp[sing_rec].orientamento_azimut

                    # if test_azimut == "" or test_azimut == None:
                        # orientamento_azimut = None
                    # else:
                        # orientamento_azimut = float(data_list_toimp[sing_rec].orientamento_azimut)
                    ##                  if conn_str_dict_write['server'] == 'postgres':
                    ##                      orientamento_azimut = float(orientamento_azimut)
                    ##

                    # blocco oritentamento_azimut
                    test_lunghezza_scheletro = data_list_toimp[sing_rec].lunghezza_scheletro

                    if test_lunghezza_scheletro == "" or test_lunghezza_scheletro == None:
                        lunghezza_scheletro = None
                    else:
                        lunghezza_scheletro = float(data_list_toimp[sing_rec].lunghezza_scheletro)
                    
                    

                    try:
                        data = self.DB_MANAGER_write.insert_values_ind(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].nr_individuo,
                            data_list_toimp[sing_rec].data_schedatura,
                            data_list_toimp[sing_rec].schedatore,
                            data_list_toimp[sing_rec].sesso,
                            data_list_toimp[sing_rec].eta_min,
                            data_list_toimp[sing_rec].eta_max,
                            data_list_toimp[sing_rec].classi_eta,
                            data_list_toimp[sing_rec].osservazioni,
                            data_list_toimp[sing_rec].sigla_struttura,
                            data_list_toimp[sing_rec].nr_struttura,
                            data_list_toimp[sing_rec].completo_si_no,
                            data_list_toimp[sing_rec].disturbato_si_no,
                            data_list_toimp[sing_rec].in_connessione_si_no,
                            lunghezza_scheletro,
                            data_list_toimp[sing_rec].posizione_scheletro,
                            data_list_toimp[sing_rec].posizione_cranio,
                            data_list_toimp[sing_rec].posizione_arti_superiori,
                            data_list_toimp[sing_rec].posizione_arti_inferiori,
                            data_list_toimp[sing_rec].orientamento_asse,
                            data_list_toimp[sing_rec].orientamento_azimut
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'CAMPIONI':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values_campioni(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nr_campione,
                            data_list_toimp[sing_rec].tipo_campione,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].area,
                            data_list_toimp[sing_rec].us,
                            data_list_toimp[sing_rec].numero_inventario_materiale,
                            data_list_toimp[sing_rec].nr_cassa,
                            data_list_toimp[sing_rec].luogo_conservazione
                        )
                        self.DB_MANAGER_write.insert_data_session(data)
                        for i in range(sing_rec):
                            #time.sleep()
                            self.progress_bar.setValue(((i)/100)*100)

                            QApplication.processEvents()

                    except :

                        QMessageBox.warning(self, "Errore", "Error ! \n"+ "duplicate key",  QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'DOCUMENTAZIONE' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_values_documentazione(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].nome_doc,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].tipo_documentazione,
                            data_list_toimp[sing_rec].sorgente,
                            data_list_toimp[sing_rec].scala,
                            data_list_toimp[sing_rec].disegnatore,
                            data_list_toimp[sing_rec].note
                        )

                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0

                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'UT':
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_ut_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].progetto,
                            data_list_toimp[sing_rec].nr_ut,
                            data_list_toimp[sing_rec].ut_letterale,
                            data_list_toimp[sing_rec].def_ut,
                            data_list_toimp[sing_rec].descrizione_ut,
                            data_list_toimp[sing_rec].interpretazione_ut,
                            data_list_toimp[sing_rec].nazione,
                            data_list_toimp[sing_rec].regione,
                            data_list_toimp[sing_rec].provincia,
                            data_list_toimp[sing_rec].comune,
                            data_list_toimp[sing_rec].frazione,
                            data_list_toimp[sing_rec].localita,
                            data_list_toimp[sing_rec].indirizzo,
                            data_list_toimp[sing_rec].nr_civico,
                            data_list_toimp[sing_rec].carta_topo_igm,
                            data_list_toimp[sing_rec].coord_geografiche,
                            data_list_toimp[sing_rec].coord_piane,
                            data_list_toimp[sing_rec].andamento_terreno_pendenza,
                            data_list_toimp[sing_rec].utilizzo_suolo_vegetazione,
                            data_list_toimp[sing_rec].descrizione_empirica_suolo,
                            data_list_toimp[sing_rec].descrizione_luogo,
                            data_list_toimp[sing_rec].metodo_rilievo_e_ricognizione,
                            data_list_toimp[sing_rec].geometria,
                            data_list_toimp[sing_rec].bibliografia,
                            data_list_toimp[sing_rec].data,
                            data_list_toimp[sing_rec].ora_meteo,
                            data_list_toimp[sing_rec].descrizione_luogo,
                            data_list_toimp[sing_rec].responsabile,
                            data_list_toimp[sing_rec].dimensioni_ut,
                            data_list_toimp[sing_rec].rep_per_mq,
                            data_list_toimp[sing_rec].rep_datanti,
                            data_list_toimp[sing_rec].periodo_I,
                            data_list_toimp[sing_rec].datazione_I,
                            data_list_toimp[sing_rec].responsabile,
                            data_list_toimp[sing_rec].interpretazione_I,
                            data_list_toimp[sing_rec].periodo_II,
                            data_list_toimp[sing_rec].datazione_II,
                            data_list_toimp[sing_rec].interpretazione_II,
                            data_list_toimp[sing_rec].documentazione,
                            data_list_toimp[sing_rec].enti_tutela_vincoli,
                            data_list_toimp[sing_rec].indagini_preliminari
                        )


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")




            elif mapper_class_write == 'PYARCHINIT_THESAURUS_SIGLE' :

                for sing_rec in range(len(data_list_toimp)):

                    try:
                        # Get optional fields with defaults
                        #order_layer = getattr(data_list_toimp[sing_rec], 'order_layer', 0)
                        #id_parent = getattr(data_list_toimp[sing_rec], 'id_parent', None)
                        #parent_sigla = getattr(data_list_toimp[sing_rec], 'parent_sigla', None)
                        #hierarchy_level = getattr(data_list_toimp[sing_rec], 'hierarchy_level', 0)

                        # For thesaurus, use merge to handle conflicts based on unique key
                        # The unique key is: (lingua, nome_tabella, tipologia_sigla, sigla_estesa)
                        # First check if the record already exists
                        search_dict = {
                            'lingua': "'" + str(data_list_toimp[sing_rec].lingua) + "'",
                            'nome_tabella': "'" + str(data_list_toimp[sing_rec].nome_tabella) + "'",
                            'tipologia_sigla': "'" + str(data_list_toimp[sing_rec].tipologia_sigla) + "'",
                            'sigla_estesa': "'" + str(data_list_toimp[sing_rec].sigla_estesa) + "'"
                        }

                        # Check if record exists
                        existing_records = self.DB_MANAGER_write.query_bool(search_dict, 'PYARCHINIT_THESAURUS_SIGLE')

                        if existing_records:
                            # Record exists - skip it (don't update to avoid overwriting good data)
                            continue  # Skip to next record
                        else:
                            # New record - insert it with try/except to handle any constraint violations
                            try:
                                data = self.DB_MANAGER_write.insert_values_thesaurus(
                                    self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                                     id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                                    data_list_toimp[sing_rec].nome_tabella,
                                    data_list_toimp[sing_rec].sigla,
                                    data_list_toimp[sing_rec].sigla_estesa,
                                    data_list_toimp[sing_rec].descrizione,
                                    data_list_toimp[sing_rec].tipologia_sigla,
                                    data_list_toimp[sing_rec].lingua,
                                    data_list_toimp[sing_rec].order_layer,
                                    data_list_toimp[sing_rec].id_parent,
                                    data_list_toimp[sing_rec].parent_sigla,
                                    data_list_toimp[sing_rec].hierarchy_level
                                )
                                self.DB_MANAGER_write.insert_data_session(data)
                            except Exception as e:
                                # Skip duplicates or other constraint violations silently
                                if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                                    continue  # Skip this record
                                else:
                                    raise  # Re-raise other errors

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
            ###########################IMPORTAZIONE MEDIA##############################################    
            elif mapper_class_write == 'MEDIA' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_media_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_media,
                            data_list_toimp[sing_rec].mediatype,
                            data_list_toimp[sing_rec].filename,
                            data_list_toimp[sing_rec].filetype,
                            data_list_toimp[sing_rec].filepath,
                            data_list_toimp[sing_rec].descrizione,
                            data_list_toimp[sing_rec].tags)


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")

            elif mapper_class_write == 'MEDIA_THUMB' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_mediathumb_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_media_thumb,
                            data_list_toimp[sing_rec].id_media,
                            data_list_toimp[sing_rec].mediatype,
                            data_list_toimp[sing_rec].media_filename,
                            data_list_toimp[sing_rec].media_thumb_filename,
                            data_list_toimp[sing_rec].filetype,
                            data_list_toimp[sing_rec].filepath,
                            data_list_toimp[sing_rec].path_resize)


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")


            elif mapper_class_write == 'MEDIATOENTITY' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        data = self.DB_MANAGER_write.insert_media2entity_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            #data_list_toimp[sing_rec].id_mediaToEntity,
                            data_list_toimp[sing_rec].id_entity,
                            data_list_toimp[sing_rec].entity_type,
                            data_list_toimp[sing_rec].table_name,
                            data_list_toimp[sing_rec].id_media,
                            data_list_toimp[sing_rec].filepath,
                            data_list_toimp[sing_rec].media_name)


                        self.DB_MANAGER_write.insert_data_session(data)

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        QMessageBox.warning(self, "Errore", "Error ! \n" + str(e), QMessageBox.Ok)
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
                
            elif mapper_class_write == 'TMA' :
                for sing_rec in range(len(data_list_toimp)):
                    try:
                        # Handle possible dtzs/dtzg field name differences
                        dtzg_value = getattr(data_list_toimp[sing_rec], 'dtzg', None)
                        if dtzg_value is None:
                            dtzg_value = getattr(data_list_toimp[sing_rec], 'dtzs', None)

                        data = self.DB_MANAGER_write.insert_tma_values(
                            self.DB_MANAGER_write.max_num_id(mapper_class_write,
                                                             id_table_class_mapper_conv_dict[mapper_class_write]) + 1,
                            data_list_toimp[sing_rec].sito,
                            data_list_toimp[sing_rec].area,
                            getattr(data_list_toimp[sing_rec], 'localita', ''),
                            getattr(data_list_toimp[sing_rec], 'settore', ''),
                            getattr(data_list_toimp[sing_rec], 'inventario', ''),
                            data_list_toimp[sing_rec].ogtm,
                            data_list_toimp[sing_rec].ldct,
                            data_list_toimp[sing_rec].ldcn,
                            data_list_toimp[sing_rec].vecchia_collocazione,
                            data_list_toimp[sing_rec].cassetta,
                            data_list_toimp[sing_rec].scan,
                            data_list_toimp[sing_rec].saggio,
                            data_list_toimp[sing_rec].vano_locus,
                            data_list_toimp[sing_rec].dscd,
                            data_list_toimp[sing_rec].dscu,
                            data_list_toimp[sing_rec].rcgd,
                            data_list_toimp[sing_rec].rcgz,
                            data_list_toimp[sing_rec].aint,
                            data_list_toimp[sing_rec].aind,
                            dtzg_value,
                            data_list_toimp[sing_rec].deso,
                            getattr(data_list_toimp[sing_rec], 'nsc', ''),
                            data_list_toimp[sing_rec].ftap,
                            data_list_toimp[sing_rec].ftan,
                            data_list_toimp[sing_rec].drat,
                            data_list_toimp[sing_rec].dran,
                            data_list_toimp[sing_rec].draa,
                            getattr(data_list_toimp[sing_rec], 'created_at', ''),
                            getattr(data_list_toimp[sing_rec], 'updated_at', ''),
                            getattr(data_list_toimp[sing_rec], 'created_by', ''),
                            getattr(data_list_toimp[sing_rec], 'updated_by', '')
                        )

                        # First insert the main TMA record
                        self.DB_MANAGER_write.insert_data_session(data)

                        # Now handle tma_materiali_ripetibili if they exist
                        # After inserting main TMA record, check for associated materials

                        try:
                            # Get the ID of the TMA record we just inserted
                            tma_id = self.DB_MANAGER_write.max_num_id('TMA', 'id')
                            self.logger.log(f"TMA record inserted with ID: {tma_id}")

                            # Query for materials associated with this TMA record from source DB
                            if hasattr(data_list_toimp[sing_rec], 'id'):
                                source_tma_id = data_list_toimp[sing_rec].id
                                self.logger.log(f"Looking for materials for source TMA ID: {source_tma_id}")

                                # Query materials from source database (SQLite)
                                try:
                                    self.logger.log(f"Querying TMA_MATERIALI from SOURCE database with id_tma={source_tma_id}")
                                    # CRITICAL: Use DB_MANAGER_read for source database, not DB_MANAGER!
                                    self.logger.log(f"Source DB engine URL: {self.DB_MANAGER_read.engine.url}")

                                    # List all tables in source DB to verify table names
                                    try:
                                        from sqlalchemy import inspect
                                        inspector = inspect(self.DB_MANAGER_read.engine)
                                        tables = inspector.get_table_names()
                                        self.logger.log(f"Tables in source DB: {tables}")

                                        # Check if tma_materiali_ripetibili exists and has data
                                        if 'tma_materiali_ripetibili' in tables:
                                            Session = sessionmaker(bind=self.DB_MANAGER_read.engine)
                                            session = Session()
                                            # Count total materials records
                                            total_result = session.execute(text("SELECT count(*) FROM tma_materiali_ripetibili"))
                                            total_count = total_result.scalar()
                                            self.logger.log(f"Total records in tma_materiali_ripetibili: {total_count}")

                                            # Check specific id_tma
                                            result = session.execute(text("SELECT count(*) FROM tma_materiali_ripetibili WHERE id_tma = :id_tma"), {"id_tma": source_tma_id})
                                            count = result.scalar()
                                            self.logger.log(f"Records for id_tma={source_tma_id}: {count}")

                                            # If there are records, get some samples
                                            if count > 0:
                                                sample = session.execute(text("SELECT * FROM tma_materiali_ripetibili WHERE id_tma = :id_tma LIMIT 2"), {"id_tma": source_tma_id})
                                                for row in sample:
                                                    self.logger.log(f"Sample material: {dict(row)}")
                                            session.close()
                                    except Exception as inspect_err:
                                        self.logger.log(f"Error inspecting source DB: {inspect_err}")

                                    # IMPORTANT: Use source DB_MANAGER (not DB_MANAGER_write) to query SQLite
                                    materials_to_import = self.DB_MANAGER_read.query_bool({'id_tma': int(source_tma_id)}, 'TMA_MATERIALI')
                                    self.logger.log(f"query_bool returned {len(materials_to_import) if materials_to_import else 0} materials")
                                except Exception as mat_query_err:
                                    import traceback
                                    self.logger.log(f"Could not query materials: {mat_query_err}")
                                    self.logger.log(f"Traceback: {traceback.format_exc()}")
                                    materials_to_import = []

                                # Import each material record
                                materials_imported = 0
                                for material in materials_to_import:
                                    try:
                                        material_data = self.DB_MANAGER_write.insert_tma_materiali_values(
                                            self.DB_MANAGER_write.max_num_id('TMA_MATERIALI', 'id') + 1,
                                            tma_id,  # Link to the new TMA record
                                            getattr(material, 'madi', ''),
                                            getattr(material, 'macc', ''),
                                            getattr(material, 'macl', ''),
                                            getattr(material, 'macp', ''),
                                            getattr(material, 'macd', ''),
                                            getattr(material, 'cronologia_mac', ''),
                                            getattr(material, 'macq', ''),
                                            getattr(material, 'peso', None),
                                            getattr(material, 'created_at', ''),
                                            getattr(material, 'updated_at', ''),
                                            getattr(material, 'created_by', ''),
                                            getattr(material, 'updated_by', '')
                                        )
                                        self.DB_MANAGER_write.insert_data_session(material_data)
                                        materials_imported += 1
                                    except Exception as mat_insert_err:
                                        self.logger.log(f"Failed to import material: {mat_insert_err}")

                                if materials_imported > 0:
                                    self.logger.log(f"Successfully imported {materials_imported} materials for TMA ID {tma_id}")
                            else:
                                self.logger.log("Source TMA record has no ID attribute")
                        except Exception as e:
                            import traceback
                            self.logger.log(f"Error in materials import for TMA record {sing_rec + 1}: {e}\n{traceback.format_exc()}")

                        # Calculate the progress as a percentage
                        value = (float(sing_rec) / float(len(data_list_toimp))) * 100
                        # Convert the progress value to an integer
                        int_value = int(value)
                        # Update the progress bar with the integer value
                        self.progress_bar.setValue(int_value)
                        QApplication.processEvents()
                    except Exception as e:
                        import traceback
                        # Log the data that was being inserted
                        self.logger.log(f"TMA record data that failed: sito={data_list_toimp[sing_rec].sito}, area={data_list_toimp[sing_rec].area}")
                        self.logger.log(f"TMA data object: {data}")

                        error_msg = f"Error importing TMA record {sing_rec + 1}/{len(data_list_toimp)}:\n{str(e)}\n\nDetails:\n{traceback.format_exc()}"
                        QMessageBox.warning(self, "TMA Import Error", error_msg, QMessageBox.Ok)
                        self.logger.log(f"TMA Import Error: {error_msg}")
                        return 0
                self.progress_bar.reset()
                QMessageBox.information(self, "Message", "Data Loaded")
                
            elif mapper_class_write == 'ALL' :
                # Initialize media migration mapper
                media_mapper = MediaMigrationMapper()
                
                # Import all tables - we'll process each one individually
                # IMPORTANT: MEDIATOENTITY must be last to use the ID mappings
                tables_to_import = ['SITE', 'US', 'UT', 'PERIODIZZAZIONE', 'INVENTARIO_MATERIALI', 
                                   'POTTERY', 'STRUTTURA', 'TOMBA', 'SCHEDAIND', 'CAMPIONI', 
                                   'DOCUMENTAZIONE', 'PYARCHINIT_THESAURUS_SIGLE', 'TMA',
                                   'MEDIA', 'MEDIA_THUMB', 'MEDIATOENTITY']
                
                total_tables = len(tables_to_import)
                total_records_imported = 0
                tables_imported = []
                failed_tables = []
                
                for table_index, current_table in enumerate(tables_to_import):
                    try:
                        # Update progress for current table
                        table_progress = (float(table_index) / float(total_tables)) * 100
                        self.progress_bar.setValue(int(table_progress))
                        QApplication.processEvents()
                        
                        # Query data for current table
                        try:
                            if current_table in ['DETSESSO', 'DETETA', 'INVENTARIO_LAPIDEI']:
                                # These tables don't exist in the combo box, skip them
                                continue
                                
                            res_read = self.DB_MANAGER_read.query_bool({}, current_table)
                            data_list_toimp_current = []
                            for i in res_read:
                                data_list_toimp_current.append(i)
                            
                            if len(data_list_toimp_current) == 0:
                                continue  # Skip empty tables
                                
                            # Show info about current table
                            if self.L=='it':
                                QMessageBox.information(self, "Info", 
                                    f"Importazione tabella {current_table}: {len(data_list_toimp_current)} record", 
                                    QMessageBox.Ok)
                            elif self.L=='de':
                                QMessageBox.information(self, "Info", 
                                    f"Importiere Tabelle {current_table}: {len(data_list_toimp_current)} Datensätze", 
                                    QMessageBox.Ok)
                            else:
                                QMessageBox.information(self, "Info", 
                                    f"Importing table {current_table}: {len(data_list_toimp_current)} records", 
                                    QMessageBox.Ok)
                            
                            # Now import data for the current table
                            import_success = False
                            
                            # Process each record for the current table
                            for sing_rec in range(len(data_list_toimp_current)):
                                try:
                                    if current_table == 'SITE':
                                        data = self.DB_MANAGER_write.insert_site_values(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_sito') + 1,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].nazione,
                                            data_list_toimp_current[sing_rec].regione,
                                            data_list_toimp_current[sing_rec].comune,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].provincia,
                                            data_list_toimp_current[sing_rec].definizione_sito,
                                            data_list_toimp_current[sing_rec].sito_path,
                                            data_list_toimp_current[sing_rec].find_check
                                        )
                                    elif current_table == 'US':
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id_us
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_us') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('US', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_values(
                                            new_id,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].area,
                                            data_list_toimp_current[sing_rec].us,
                                            data_list_toimp_current[sing_rec].d_stratigrafica,
                                            data_list_toimp_current[sing_rec].d_interpretativa,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].interpretazione,
                                            data_list_toimp_current[sing_rec].periodo_iniziale,
                                            data_list_toimp_current[sing_rec].fase_iniziale,
                                            data_list_toimp_current[sing_rec].periodo_finale,
                                            data_list_toimp_current[sing_rec].fase_finale,
                                            data_list_toimp_current[sing_rec].scavato,
                                            data_list_toimp_current[sing_rec].attivita,
                                            data_list_toimp_current[sing_rec].anno_scavo,
                                            data_list_toimp_current[sing_rec].metodo_di_scavo,
                                            data_list_toimp_current[sing_rec].inclusi,
                                            data_list_toimp_current[sing_rec].campioni,
                                            data_list_toimp_current[sing_rec].rapporti,
                                            data_list_toimp_current[sing_rec].data_schedatura,
                                            data_list_toimp_current[sing_rec].schedatore,
                                            data_list_toimp_current[sing_rec].formazione,
                                            data_list_toimp_current[sing_rec].stato_di_conservazione,
                                            data_list_toimp_current[sing_rec].colore,
                                            data_list_toimp_current[sing_rec].consistenza,
                                            data_list_toimp_current[sing_rec].struttura,
                                            data_list_toimp_current[sing_rec].cont_per,
                                            data_list_toimp_current[sing_rec].order_layer,
                                            data_list_toimp_current[sing_rec].documentazione,
                                            data_list_toimp_current[sing_rec].unita_tipo,
                                            data_list_toimp_current[sing_rec].settore,
                                            data_list_toimp_current[sing_rec].quad_par,
                                            data_list_toimp_current[sing_rec].ambient,
                                            data_list_toimp_current[sing_rec].saggio,
                                            data_list_toimp_current[sing_rec].elem_datanti,
                                            data_list_toimp_current[sing_rec].funz_statica,
                                            data_list_toimp_current[sing_rec].lavorazione,
                                            data_list_toimp_current[sing_rec].spess_giunti,
                                            data_list_toimp_current[sing_rec].letti_posa,
                                            data_list_toimp_current[sing_rec].alt_mod,
                                            data_list_toimp_current[sing_rec].un_ed_riass,
                                            data_list_toimp_current[sing_rec].reimp,
                                            data_list_toimp_current[sing_rec].posa_opera,
                                            data_list_toimp_current[sing_rec].quota_min_usm,
                                            data_list_toimp_current[sing_rec].quota_max_usm,
                                            data_list_toimp_current[sing_rec].cons_legante,
                                            data_list_toimp_current[sing_rec].col_legante,
                                            data_list_toimp_current[sing_rec].aggreg_legante,
                                            data_list_toimp_current[sing_rec].con_text_mat,
                                            data_list_toimp_current[sing_rec].col_materiale,
                                            data_list_toimp_current[sing_rec].inclusi_materiali_usm,
                                            data_list_toimp_current[sing_rec].n_catalogo_generale,
                                            data_list_toimp_current[sing_rec].n_catalogo_interno,
                                            data_list_toimp_current[sing_rec].n_catalogo_internazionale,
                                            data_list_toimp_current[sing_rec].soprintendenza,
                                            data_list_toimp_current[sing_rec].quota_relativa,
                                            data_list_toimp_current[sing_rec].quota_abs,
                                            data_list_toimp_current[sing_rec].ref_tm,
                                            data_list_toimp_current[sing_rec].ref_ra,
                                            data_list_toimp_current[sing_rec].ref_n,
                                            data_list_toimp_current[sing_rec].posizione,
                                            data_list_toimp_current[sing_rec].criteri_distinzione,
                                            data_list_toimp_current[sing_rec].modo_formazione,
                                            data_list_toimp_current[sing_rec].componenti_organici,
                                            data_list_toimp_current[sing_rec].componenti_inorganici,
                                            data_list_toimp_current[sing_rec].lunghezza_max,
                                            data_list_toimp_current[sing_rec].altezza_max,
                                            data_list_toimp_current[sing_rec].altezza_min,
                                            data_list_toimp_current[sing_rec].profondita_max,
                                            data_list_toimp_current[sing_rec].profondita_min,
                                            data_list_toimp_current[sing_rec].larghezza_media,
                                            data_list_toimp_current[sing_rec].quota_max_abs,
                                            data_list_toimp_current[sing_rec].quota_max_rel,
                                            data_list_toimp_current[sing_rec].quota_min_abs,
                                            data_list_toimp_current[sing_rec].quota_min_rel,
                                            data_list_toimp_current[sing_rec].osservazioni,
                                            data_list_toimp_current[sing_rec].datazione,
                                            data_list_toimp_current[sing_rec].flottazione,
                                            data_list_toimp_current[sing_rec].setacciatura,
                                            data_list_toimp_current[sing_rec].affidabilita,
                                            data_list_toimp_current[sing_rec].direttore_us,
                                            data_list_toimp_current[sing_rec].responsabile_us,
                                            data_list_toimp_current[sing_rec].cod_ente_schedatore,
                                            data_list_toimp_current[sing_rec].data_rilevazione,
                                            data_list_toimp_current[sing_rec].data_rielaborazione,
                                            data_list_toimp_current[sing_rec].lunghezza_usm,
                                            data_list_toimp_current[sing_rec].altezza_usm,
                                            data_list_toimp_current[sing_rec].spessore_usm,
                                            data_list_toimp_current[sing_rec].tecnica_muraria_usm,
                                            data_list_toimp_current[sing_rec].modulo_usm,
                                            data_list_toimp_current[sing_rec].campioni_malta_usm,
                                            data_list_toimp_current[sing_rec].campioni_mattone_usm,
                                            data_list_toimp_current[sing_rec].campioni_pietra_usm,
                                            data_list_toimp_current[sing_rec].provenienza_materiali_usm,
                                            data_list_toimp_current[sing_rec].criteri_distinzione_usm,
                                            data_list_toimp_current[sing_rec].uso_primario_usm
                                        )
                                    elif current_table == 'PERIODIZZAZIONE':
                                        data = self.DB_MANAGER_write.insert_periodizzazione_values(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_perfas') + 1,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].periodo,
                                            data_list_toimp_current[sing_rec].fase,
                                            data_list_toimp_current[sing_rec].cron_iniziale,
                                            data_list_toimp_current[sing_rec].cron_finale,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].datazione_estesa,
                                            data_list_toimp_current[sing_rec].cont_per
                                        )
                                    elif current_table == 'INVENTARIO_MATERIALI':
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id_invmat
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_invmat') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('INVENTARIO_MATERIALI', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_values_reperti(
                                            new_id,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].numero_inventario,
                                            data_list_toimp_current[sing_rec].tipo_reperto,
                                            data_list_toimp_current[sing_rec].criterio_schedatura,
                                            data_list_toimp_current[sing_rec].definizione,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].area,
                                            data_list_toimp_current[sing_rec].us,
                                            data_list_toimp_current[sing_rec].lavato,
                                            data_list_toimp_current[sing_rec].nr_cassa,
                                            data_list_toimp_current[sing_rec].luogo_conservazione,
                                            data_list_toimp_current[sing_rec].stato_conservazione,
                                            data_list_toimp_current[sing_rec].datazione_reperto,
                                            data_list_toimp_current[sing_rec].elementi_reperto,
                                            data_list_toimp_current[sing_rec].misurazioni,
                                            data_list_toimp_current[sing_rec].rif_biblio,
                                            data_list_toimp_current[sing_rec].tecnologie,
                                            data_list_toimp_current[sing_rec].forme_minime,
                                            data_list_toimp_current[sing_rec].forme_massime,
                                            data_list_toimp_current[sing_rec].totale_frammenti,
                                            data_list_toimp_current[sing_rec].corpo_ceramico,
                                            data_list_toimp_current[sing_rec].rivestimento,
                                            data_list_toimp_current[sing_rec].diametro_orlo,
                                            data_list_toimp_current[sing_rec].peso,
                                            data_list_toimp_current[sing_rec].tipo,
                                            data_list_toimp_current[sing_rec].eve_orlo,
                                            data_list_toimp_current[sing_rec].repertato,
                                            data_list_toimp_current[sing_rec].diagnostico
                                        )
                                    elif current_table == 'POTTERY':
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id_rep
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_rep') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('POTTERY', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_pottery_values(
                                            new_id,
                                            data_list_toimp_current[sing_rec].id_number,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].area,
                                            data_list_toimp_current[sing_rec].us,
                                            data_list_toimp_current[sing_rec].box,
                                            data_list_toimp_current[sing_rec].photo,
                                            data_list_toimp_current[sing_rec].drawing,
                                            data_list_toimp_current[sing_rec].anno,
                                            data_list_toimp_current[sing_rec].fabric,
                                            data_list_toimp_current[sing_rec].percent,
                                            data_list_toimp_current[sing_rec].material,
                                            data_list_toimp_current[sing_rec].form,
                                            data_list_toimp_current[sing_rec].specific_form,
                                            data_list_toimp_current[sing_rec].ware,
                                            data_list_toimp_current[sing_rec].munsell,
                                            data_list_toimp_current[sing_rec].surf_trat,
                                            data_list_toimp_current[sing_rec].exdeco,
                                            data_list_toimp_current[sing_rec].intdeco,
                                            data_list_toimp_current[sing_rec].wheel_made,
                                            data_list_toimp_current[sing_rec].descrip_ex_deco,
                                            data_list_toimp_current[sing_rec].descrip_in_deco,
                                            data_list_toimp_current[sing_rec].note,
                                            data_list_toimp_current[sing_rec].diametro_max,
                                            data_list_toimp_current[sing_rec].qty,
                                            data_list_toimp_current[sing_rec].diametro_rim,
                                            data_list_toimp_current[sing_rec].diametro_bottom,
                                            data_list_toimp_current[sing_rec].diametro_height,
                                            data_list_toimp_current[sing_rec].diametro_preserved,
                                            data_list_toimp_current[sing_rec].specific_shape,
                                            data_list_toimp_current[sing_rec].bag
                                        )
                                    elif current_table == 'STRUTTURA':
                                        per_iniz = data_list_toimp_current[sing_rec].periodo_iniziale if data_list_toimp_current[sing_rec].periodo_iniziale else ''
                                        per_fin = data_list_toimp_current[sing_rec].periodo_finale if data_list_toimp_current[sing_rec].periodo_finale else ''
                                        fas_iniz = data_list_toimp_current[sing_rec].fase_iniziale if data_list_toimp_current[sing_rec].fase_iniziale else ''
                                        fas_fin = data_list_toimp_current[sing_rec].fase_finale if data_list_toimp_current[sing_rec].fase_finale else ''
                                        
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id_struttura
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_struttura') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('STRUTTURA', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_struttura_values(
                                            new_id,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].sigla_struttura,
                                            data_list_toimp_current[sing_rec].numero_struttura,
                                            data_list_toimp_current[sing_rec].categoria_struttura,
                                            data_list_toimp_current[sing_rec].tipologia_struttura,
                                            data_list_toimp_current[sing_rec].definizione_struttura,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].interpretazione,
                                            per_iniz,
                                            fas_iniz,
                                            per_fin,
                                            fas_fin,
                                            data_list_toimp_current[sing_rec].datazione_estesa,
                                            data_list_toimp_current[sing_rec].materiali_impiegati,
                                            data_list_toimp_current[sing_rec].elementi_strutturali,
                                            data_list_toimp_current[sing_rec].rapporti_struttura,
                                            data_list_toimp_current[sing_rec].misure_struttura
                                        )
                                    elif current_table == 'TOMBA':
                                        per_iniz = '' if not data_list_toimp_current[sing_rec].periodo_iniziale else int(data_list_toimp_current[sing_rec].periodo_iniziale)
                                        fas_iniz = '' if not data_list_toimp_current[sing_rec].fase_iniziale else int(data_list_toimp_current[sing_rec].fase_iniziale)
                                        per_fin = '' if not data_list_toimp_current[sing_rec].periodo_finale else int(data_list_toimp_current[sing_rec].periodo_finale)
                                        fas_fin = '' if not data_list_toimp_current[sing_rec].fase_finale else int(data_list_toimp_current[sing_rec].fase_finale)
                                        
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id_tomba
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_tomba') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('TOMBA', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_values_tomba(
                                            new_id,
                                            str(data_list_toimp_current[sing_rec].sito),
                                            str(data_list_toimp_current[sing_rec].area),
                                            str(data_list_toimp_current[sing_rec].nr_scheda_taf),
                                            str(data_list_toimp_current[sing_rec].sigla_struttura),
                                            str(data_list_toimp_current[sing_rec].nr_struttura),
                                            str(data_list_toimp_current[sing_rec].nr_individuo),
                                            str(data_list_toimp_current[sing_rec].rito),
                                            str(data_list_toimp_current[sing_rec].descrizione_taf),
                                            str(data_list_toimp_current[sing_rec].interpretazione_taf),
                                            str(data_list_toimp_current[sing_rec].segnacoli),
                                            str(data_list_toimp_current[sing_rec].canale_libatorio_si_no),
                                            str(data_list_toimp_current[sing_rec].oggetti_rinvenuti_esterno),
                                            str(data_list_toimp_current[sing_rec].stato_di_conservazione),
                                            str(data_list_toimp_current[sing_rec].copertura_tipo),
                                            str(data_list_toimp_current[sing_rec].tipo_contenitore_resti),
                                            str(data_list_toimp_current[sing_rec].tipo_deposizione),
                                            str(data_list_toimp_current[sing_rec].tipo_sepoltura),
                                            str(data_list_toimp_current[sing_rec].corredo_presenza),
                                            str(data_list_toimp_current[sing_rec].corredo_tipo),
                                            str(data_list_toimp_current[sing_rec].corredo_descrizione),
                                            per_iniz,
                                            fas_iniz,
                                            per_fin,
                                            fas_fin,
                                            str(data_list_toimp_current[sing_rec].datazione_estesa)
                                        )
                                    elif current_table == 'SCHEDAIND':
                                        lunghezza_scheletro = None
                                        if data_list_toimp_current[sing_rec].lunghezza_scheletro:
                                            lunghezza_scheletro = float(data_list_toimp_current[sing_rec].lunghezza_scheletro)
                                            
                                        data = self.DB_MANAGER_write.insert_values_ind(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_scheda_ind') + 1,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].area,
                                            data_list_toimp_current[sing_rec].us,
                                            data_list_toimp_current[sing_rec].nr_individuo,
                                            data_list_toimp_current[sing_rec].data_schedatura,
                                            data_list_toimp_current[sing_rec].schedatore,
                                            data_list_toimp_current[sing_rec].sesso,
                                            data_list_toimp_current[sing_rec].eta_min,
                                            data_list_toimp_current[sing_rec].eta_max,
                                            data_list_toimp_current[sing_rec].classi_eta,
                                            data_list_toimp_current[sing_rec].osservazioni,
                                            data_list_toimp_current[sing_rec].sigla_struttura,
                                            data_list_toimp_current[sing_rec].nr_struttura,
                                            data_list_toimp_current[sing_rec].completo_si_no,
                                            data_list_toimp_current[sing_rec].disturbato_si_no,
                                            data_list_toimp_current[sing_rec].in_connessione_si_no,
                                            lunghezza_scheletro,
                                            data_list_toimp_current[sing_rec].posizione_scheletro,
                                            data_list_toimp_current[sing_rec].posizione_cranio,
                                            data_list_toimp_current[sing_rec].posizione_arti_superiori,
                                            data_list_toimp_current[sing_rec].posizione_arti_inferiori,
                                            data_list_toimp_current[sing_rec].orientamento_asse,
                                            data_list_toimp_current[sing_rec].orientamento_azimut
                                        )
                                    elif current_table == 'CAMPIONI':
                                        data = self.DB_MANAGER_write.insert_values_campioni(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_campione') + 1,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].nr_campione,
                                            data_list_toimp_current[sing_rec].tipo_campione,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].area,
                                            data_list_toimp_current[sing_rec].us,
                                            data_list_toimp_current[sing_rec].numero_inventario_materiale,
                                            data_list_toimp_current[sing_rec].nr_cassa,
                                            data_list_toimp_current[sing_rec].luogo_conservazione
                                        )
                                    elif current_table == 'DOCUMENTAZIONE':
                                        data = self.DB_MANAGER_write.insert_values_documentazione(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_documentazione') + 1,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].nome_doc,
                                            data_list_toimp_current[sing_rec].data,
                                            data_list_toimp_current[sing_rec].tipo_documentazione,
                                            data_list_toimp_current[sing_rec].sorgente,
                                            data_list_toimp_current[sing_rec].scala,
                                            data_list_toimp_current[sing_rec].disegnatore,
                                            data_list_toimp_current[sing_rec].note
                                        )
                                    elif current_table == 'UT':
                                        data = self.DB_MANAGER_write.insert_ut_values(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_ut') + 1,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].progetto,
                                            data_list_toimp_current[sing_rec].nr_ut,
                                            data_list_toimp_current[sing_rec].ut_letterale,
                                            data_list_toimp_current[sing_rec].def_ut,
                                            data_list_toimp_current[sing_rec].descrizione_ut,
                                            data_list_toimp_current[sing_rec].interpretazione_ut,
                                            data_list_toimp_current[sing_rec].nazione,
                                            data_list_toimp_current[sing_rec].regione,
                                            data_list_toimp_current[sing_rec].provincia,
                                            data_list_toimp_current[sing_rec].comune,
                                            data_list_toimp_current[sing_rec].frazione,
                                            data_list_toimp_current[sing_rec].localita,
                                            data_list_toimp_current[sing_rec].indirizzo,
                                            data_list_toimp_current[sing_rec].nr_civico,
                                            data_list_toimp_current[sing_rec].carta_topo_igm,
                                            data_list_toimp_current[sing_rec].coord_geografiche,
                                            data_list_toimp_current[sing_rec].coord_piane,
                                            data_list_toimp_current[sing_rec].andamento_terreno_pendenza,
                                            data_list_toimp_current[sing_rec].utilizzo_suolo_vegetazione,
                                            data_list_toimp_current[sing_rec].descrizione_empirica_suolo,
                                            data_list_toimp_current[sing_rec].descrizione_luogo,
                                            data_list_toimp_current[sing_rec].metodo_rilievo_e_ricognizione,
                                            data_list_toimp_current[sing_rec].geometria,
                                            data_list_toimp_current[sing_rec].bibliografia,
                                            data_list_toimp_current[sing_rec].data,
                                            data_list_toimp_current[sing_rec].ora_meteo,
                                            data_list_toimp_current[sing_rec].descrizione_luogo,
                                            data_list_toimp_current[sing_rec].responsabile,
                                            data_list_toimp_current[sing_rec].dimensioni_ut,
                                            data_list_toimp_current[sing_rec].rep_per_mq,
                                            data_list_toimp_current[sing_rec].rep_datanti,
                                            data_list_toimp_current[sing_rec].periodo_I,
                                            data_list_toimp_current[sing_rec].datazione_I,
                                            data_list_toimp_current[sing_rec].responsabile,
                                            data_list_toimp_current[sing_rec].interpretazione_I,
                                            data_list_toimp_current[sing_rec].periodo_II,
                                            data_list_toimp_current[sing_rec].datazione_II,
                                            data_list_toimp_current[sing_rec].interpretazione_II,
                                            data_list_toimp_current[sing_rec].documentazione,
                                            data_list_toimp_current[sing_rec].enti_tutela_vincoli,
                                            data_list_toimp_current[sing_rec].indagini_preliminari
                                        )
                                    elif current_table == 'PYARCHINIT_THESAURUS_SIGLE':
                                        # For thesaurus, check if record exists based on unique key
                                        search_dict_thes = {
                                            'lingua': "'" + str(data_list_toimp_current[sing_rec].lingua) + "'",
                                            'nome_tabella': "'" + str(data_list_toimp_current[sing_rec].nome_tabella) + "'",
                                            'tipologia_sigla': "'" + str(data_list_toimp_current[sing_rec].tipologia_sigla) + "'",
                                            'sigla_estesa': "'" + str(data_list_toimp_current[sing_rec].sigla_estesa) + "'"
                                        }
                                        existing_thes = self.DB_MANAGER_write.query_bool(search_dict_thes, 'PYARCHINIT_THESAURUS_SIGLE')

                                        if existing_thes:
                                            # Record exists - skip it
                                            continue
                                        else:
                                            # Insert new record with error handling
                                            try:
                                                data = self.DB_MANAGER_write.insert_values_thesaurus(
                                                    self.DB_MANAGER_write.max_num_id(current_table, 'id_thesaurus_sigle') + 1,
                                                    data_list_toimp_current[sing_rec].nome_tabella,
                                                    data_list_toimp_current[sing_rec].sigla,
                                                    data_list_toimp_current[sing_rec].sigla_estesa,
                                                    data_list_toimp_current[sing_rec].descrizione,
                                                    data_list_toimp_current[sing_rec].tipologia_sigla,
                                                    data_list_toimp_current[sing_rec].lingua,
                                                    getattr(data_list_toimp_current[sing_rec], 'order_layer', 0),
                                                    getattr(data_list_toimp_current[sing_rec], 'id_parent', None),
                                                    getattr(data_list_toimp_current[sing_rec], 'parent_sigla', None),
                                                    getattr(data_list_toimp_current[sing_rec], 'hierarchy_level', 0)
                                                )
                                            except:
                                                continue  # Skip on any error
                                    elif current_table == 'TMA':
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_tma') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('TMA', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_tma_values(
                                            new_id,
                                            data_list_toimp_current[sing_rec].sito,
                                            data_list_toimp_current[sing_rec].area,
                                            data_list_toimp_current[sing_rec].ogtm,
                                            data_list_toimp_current[sing_rec].ldct,
                                            data_list_toimp_current[sing_rec].ldcn,
                                            data_list_toimp_current[sing_rec].vecchia_collocazione,
                                            data_list_toimp_current[sing_rec].cassetta,
                                            data_list_toimp_current[sing_rec].localita,
                                            data_list_toimp_current[sing_rec].scan,
                                            data_list_toimp_current[sing_rec].saggio,
                                            data_list_toimp_current[sing_rec].vano_locus,
                                            data_list_toimp_current[sing_rec].dscd,
                                            data_list_toimp_current[sing_rec].dscu,
                                            data_list_toimp_current[sing_rec].rcgd,
                                            data_list_toimp_current[sing_rec].rcgz,
                                            data_list_toimp_current[sing_rec].aint,
                                            data_list_toimp_current[sing_rec].aind,
                                            data_list_toimp_current[sing_rec].dtzg,
                                            data_list_toimp_current[sing_rec].dtzs,
                                            data_list_toimp_current[sing_rec].cronologie,
                                            data_list_toimp_current[sing_rec].n_reperti,
                                            data_list_toimp_current[sing_rec].peso,
                                            data_list_toimp_current[sing_rec].deso,
                                            data_list_toimp_current[sing_rec].madi,
                                            data_list_toimp_current[sing_rec].macc,
                                            data_list_toimp_current[sing_rec].macl,
                                            data_list_toimp_current[sing_rec].macp,
                                            data_list_toimp_current[sing_rec].macd,
                                            data_list_toimp_current[sing_rec].cronologia_mac,
                                            data_list_toimp_current[sing_rec].macq,
                                            data_list_toimp_current[sing_rec].ftap,
                                            data_list_toimp_current[sing_rec].ftan,
                                            data_list_toimp_current[sing_rec].drat,
                                            data_list_toimp_current[sing_rec].dran,
                                            data_list_toimp_current[sing_rec].draa
                                        )
                                    elif current_table == 'MEDIA':
                                        # Get old ID and generate new ID
                                        old_id = data_list_toimp_current[sing_rec].id_media
                                        new_id = self.DB_MANAGER_write.max_num_id(current_table, 'id_media') + 1
                                        # Store mapping
                                        media_mapper.add_id_mapping('MEDIA', old_id, new_id)
                                        
                                        data = self.DB_MANAGER_write.insert_media_values(
                                            new_id,
                                            data_list_toimp_current[sing_rec].mediatype,
                                            data_list_toimp_current[sing_rec].filename,
                                            data_list_toimp_current[sing_rec].filetype,
                                            data_list_toimp_current[sing_rec].filepath,
                                            data_list_toimp_current[sing_rec].descrizione,
                                            data_list_toimp_current[sing_rec].tags
                                        )
                                    elif current_table == 'MEDIA_THUMB':
                                        data = self.DB_MANAGER_write.insert_mediathumb_values(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_media_thumb') + 1,
                                            data_list_toimp_current[sing_rec].id_media,
                                            data_list_toimp_current[sing_rec].mediatype,
                                            data_list_toimp_current[sing_rec].media_filename,
                                            data_list_toimp_current[sing_rec].media_thumb_filename,
                                            data_list_toimp_current[sing_rec].filetype,
                                            data_list_toimp_current[sing_rec].filepath,
                                            data_list_toimp_current[sing_rec].path_resize
                                        )
                                    elif current_table == 'MEDIATOENTITY':
                                        # Usa il mapper per ottenere gli ID aggiornati
                                        updated_data = media_mapper.update_mediatoentity_record(data_list_toimp_current[sing_rec])
                                        
                                        data = self.DB_MANAGER_write.insert_media2entity_values(
                                            self.DB_MANAGER_write.max_num_id(current_table, 'id_mediaToEntity') + 1,
                                            updated_data['id_entity'],
                                            updated_data['entity_type'],
                                            updated_data['table_name'],
                                            updated_data['id_media'],
                                            updated_data['filepath'],
                                            updated_data['media_name']
                                        )
                                    else:
                                        # Skip unknown tables
                                        continue
                                        
                                    # Insert the data
                                    self.DB_MANAGER_write.insert_data_session(data)
                                    
                                except Exception as e:
                                    # Log error but continue with other records
                                    continue
                            
                            # If we get here, import was successful
                            import_success = True
                            tables_imported.append(current_table)
                            total_records_imported += len(data_list_toimp_current)
                            
                        except Exception as e:
                            failed_tables.append(current_table)
                            if self.L=='it':
                                QMessageBox.warning(self, "Errore", 
                                    f"Errore nel leggere la tabella {current_table}: {str(e)}", 
                                    QMessageBox.Ok)
                            elif self.L=='de':
                                QMessageBox.warning(self, "Fehler", 
                                    f"Fehler beim Lesen der Tabelle {current_table}: {str(e)}", 
                                    QMessageBox.Ok)
                            else:
                                QMessageBox.warning(self, "Error", 
                                    f"Error reading table {current_table}: {str(e)}", 
                                    QMessageBox.Ok)
                            continue
                            
                    except Exception as e:
                        failed_tables.append(current_table)
                        continue
                
                # After processing all tables, show summary
                self.progress_bar.reset()
                
                success_count = len(tables_imported)
                fail_count = len(failed_tables)
                
                # Ottieni il riepilogo dei mapping
                mapping_summary = media_mapper.get_mapping_summary()
                
                if self.L=='it':
                    message = f"Importazione completata.\n\nTabelle importate: {success_count}\nTabelle fallite: {fail_count}\nRecord totali importati: {total_records_imported}"
                    if failed_tables:
                        message += f"\n\nTabelle fallite:\n{', '.join(failed_tables)}"
                    if mapping_summary:
                        message += "\n\nMapping ID per media:"
                        for table, info in mapping_summary.items():
                            message += f"\n{table}: {info['count']} record mappati"
                    QMessageBox.information(self, "Riepilogo importazione", message, QMessageBox.Ok)
                elif self.L=='de':
                    message = f"Import abgeschlossen.\n\nTabellen importiert: {success_count}\nFehlgeschlagene Tabellen: {fail_count}\nGesamtzahl importierter Datensätze: {total_records_imported}"
                    if failed_tables:
                        message += f"\n\nFehlgeschlagene Tabellen:\n{', '.join(failed_tables)}"
                    if mapping_summary:
                        message += "\n\nID-Zuordnung für Medien:"
                        for table, info in mapping_summary.items():
                            message += f"\n{table}: {info['count']} Datensätze zugeordnet"
                    QMessageBox.information(self, "Import-Zusammenfassung", message, QMessageBox.Ok)
                else:
                    message = f"Import completed.\n\nTables imported: {success_count}\nTables failed: {fail_count}\nTotal records imported: {total_records_imported}"
                    if failed_tables:
                        message += f"\n\nFailed tables:\n{', '.join(failed_tables)}"
                    if mapping_summary:
                        message += "\n\nID mapping for media:"
                        for table, info in mapping_summary.items():
                            message += f"\n{table}: {info['count']} records mapped"
                    QMessageBox.information(self, "Import Summary", message, QMessageBox.Ok)
                
                return  # Exit after ALL import


            
    def check_sqlite_db_on_init(self):
        """Check and fix macc field when config dialog opens"""
        try:
            conn = Connection()
            conn_str = conn.conn_str()

            # Only check if it's a SQLite connection
            if conn_str.startswith('sqlite'):
                self.fix_macc_field_for_current_db(conn_str)
        except:
            pass  # Silently fail if no connection is configured yet

    def fix_macc_field_for_current_db(self, conn_str):
        """Fix macc field in the current SQLite database"""
        try:
            # Extract database path from connection string
            # Format: sqlite:///path/to/database.sqlite
            db_path = conn_str.replace("sqlite:///", "")
            db_name = os.path.basename(db_path)

            QgsMessageLog.logMessage(f"PyArchInit Config - Checking database: {db_name}", "PyArchInit", Qgis.Info)

            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tma_materiali_ripetibili'"
            )
            if not cursor.fetchone():
                QgsMessageLog.logMessage(f"PyArchInit Config - Table tma_materiali_ripetibili does not exist in {db_name}", "PyArchInit", Qgis.Info)
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
                QgsMessageLog.logMessage(f"PyArchInit Config - Column 'macc' not found in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            # Check if macc is NOT NULL (col[3] is the notnull flag)
            if macc_info[3] == 0:
                QgsMessageLog.logMessage(f"PyArchInit Config - Column 'macc' is already nullable in {db_name}", "PyArchInit", Qgis.Info)
                conn.close()
                return

            QgsMessageLog.logMessage(f"PyArchInit Config - Column 'macc' is NOT NULL in {db_name}. Starting fix...", "PyArchInit", Qgis.Warning)

            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")

            try:
                # Check and drop the view if it exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='view' AND name='pyarchinit_uscaratterizzazioni_view'"
                )
                if cursor.fetchone():
                    cursor.execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view")
                    QgsMessageLog.logMessage(f"PyArchInit Config - Dropped view pyarchinit_uscaratterizzazioni_view in {db_name}", "PyArchInit", Qgis.Info)

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
                QgsMessageLog.logMessage(f"PyArchInit Config - Successfully fixed 'macc' field in {db_name}", "PyArchInit", Qgis.Success)

            except Exception as e:
                cursor.execute("ROLLBACK")
                QgsMessageLog.logMessage(f"PyArchInit Config - Error during migration in {db_name}, rolled back: {str(e)}", "PyArchInit", Qgis.Critical)

            finally:
                conn.close()

        except Exception as e:
            QgsMessageLog.logMessage(f"PyArchInit Config - Error in fix_macc_field_for_current_db: {str(e)}", "PyArchInit", Qgis.Critical)

    def openthumbDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_path.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    def openresizeDir(self):
        s = QgsSettings()
        dir = self.lineEdit_Thumb_resize.text()
        if os.path.exists(dir):
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))
        else:
            QMessageBox.warning(self, "INFO", "Directory not found",
                                QMessageBox.Ok)

    
    def on_pushButton_connect_pressed(self):

        # Defines parameter
        self.ip=str(self.lineEdit_ip.text())


        self.user=str(self.lineEdit_user.text())



        self.pwd=str(self.lineEdit_password.text())



        try:
            ftp = FTP(self.ip)
            a = ftp.login(self.user, self.pwd)
            if bool(a):
                self.lineEdit_2.insert("Connection succesfully stablished ......... ")
                dirlist = ftp.cwd('/')

                self.listWidget.insertItem(0,dirlist)

            else:
                self.lineEdit_2.insert("Errore di connessione ......... ")

        except:
            self.lineEdit_2.insert("Errore di connessione ......... ")





        # #Download the file from the remote server
        # remote_file = 'remote_path/test.qgs'  # Example path

        # with srv.cd('../'):             # still in .
            # srv.chdir('home')    # now in ./static
            # srv.chdir('data')      # now in ./static/here
            # srv.chdir('ftp')
            # srv.chdir('demoliz')

            # srv.chdir('qgis')
            # srv.chdir('rep5')
            # self.listWidget.insertItem(0,"--------------------------------------------")


        # srv.close()
    # def loginServer():
        # # user = ent_login.get()
        # # password = ent_pass.get()
        # try:
            # msg = ftp.login(user,password)
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,msg)
            # displayDir()
            # # lbl_login.place_forget()
            # # ent_login.place_forget()
            # # lbl_pass.place_forget()
            # # ent_pass.place_forget()
            # # btn_login.place_forget()
        # except:
            # text_servermsg.insert(END,"\n")
            # text_servermsg.insert(END,"Unable to login")


    # def displayDir():
        # libox_serverdir.insert(0,"--------------------------------------------")
        # dirlist = []
        # dirlist = ftp.nlst()
        # for item in dirlist:
            # libox_serverdir.insert(0, item)

    # #FTP commands
    # def on_pushButton_change_dir_pressed(self):
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None
        # with pysftp.Connection(host="ftp.adarteifo.it", username="adarteinfo",
        # password="adarteinfo",cnopts =cnopts ) as sftp:

            # try:
                # msg = sftp.cwd('/home') # Switch to a remote directory

                # directory_structure = sftp.listdir_attr()# Obtain structure of the remote directory

                # for attr in directory_structure:
                    # self.listWidget.insertItem(attr.filename, attr)

            # except:
                # self.lineEdit_2.insert("\n")
                # self.lineEdit_2.insert("Unable to change directory")
            # dirlist = []
            # dirlist = sftp.listdir()
            # for item in dirlist:
                # self.listWidget.insertItem(0,item)


    # def on_pushButton_disconnect_pressed(self):

       # cnopts = pysftp.CnOpts()
       # cnopts.hostkeys = None
       # srv = pysftp.Connection(host=self.ip, username=self.user, password=self.pwd,cnopts =cnopts )
       # self.lineEdit_2.insert("Connection Close ............. ")
       # srv.close()
    def on_pushButton_convertdb_pressed(self):
        QMessageBox.warning(self, "Attenzione",
                                     "Assicurati che il nome del db non abbia parentesi o caratteri spaciali, altrimenti la conversione fallisce",
                                     QMessageBox.Ok)
        if self.comboBox_Database.currentText() == 'sqlite':

            if platform.system() == "Windows":
                cmd = os.path.join(os.sep, self.HOME, 'bin', 'spatialite_convert.exe')
                #db1 = os.path.join(os.sep, self.HOME, 'bin', 'pyarchinit.sqlite')
                
            
            else:
                QMessageBox.warning(self, "Attenzione",
                                     "Funzione abilitata solo per windows",
                                     QMessageBox.Ok)

            db1 = os.path.join(os.sep, self.HOME, 'pyarchinit_DB_folder', self.lineEdit_DBname.text())

            # text_ = cmd, self.comboBox_compare.currentText(), db1 + ' ', db2
            # result = subprocess.check_output([text_], stderr=subprocess.STDOUT)
            os.system("start cmd /k" + cmd + ' --db-path ' + ' ' +db1 +' '+ '-tv 4' )
            os.system("start cmd /k" + cmd + ' --db-path ' + ' ' + db1 +' '+ '-tv 5' )
            

        else:
            QMessageBox.warning(self, "Attenzione",
                                     "ops qualcosa è andato storto",
                                     QMessageBox.Ok)
    